import importlib.util
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys

import pytest
import tomllib

import cnki_search.install_config as install_config
from cnki_search.install_config import (
    client_paths,
    cnki_server_config,
    main,
    merge_claude_config,
)

requires_windows_powershell = pytest.mark.skipif(
    os.name != "nt" or shutil.which("powershell") is None,
    reason="requires Windows PowerShell",
)


def test_installers_require_explicit_client_targets(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")
    for token in ("[switch]$Codex", "[switch]$ClaudeCode", "[switch]$ClaudeDesktop"):
        assert token in powershell
    for token in ("--codex", "--claude-code", "--claude-desktop"):
        assert token in shell


def test_installers_reuse_allowlisted_skill_copy(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")
    assert "--copy-skill" in powershell
    assert "--copy-skill" in shell
    assert "Copy-Item -LiteralPath $SkillSource -Destination $Destination -Recurse" not in powershell
    assert 'cp -R "$skill_source" "$destination"' not in shell


def test_installers_validate_selected_python_before_any_install_write(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")

    assert "[string]$PythonExe = 'python'" in powershell
    assert "function Assert-PythonVersion" in powershell
    assert powershell.rindex("Assert-PythonVersion $Python") < powershell.index("try {")
    assert 'python_command=${CNKI_PYTHON:-python3}' in shell
    assert "assert_python_version" in shell
    assert shell.rindex("assert_python_version") < shell.index("install_skill()")


def test_installers_require_runtime_self_checks_and_transactional_restore(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")

    for script in (powershell, shell):
        assert "playwright install chromium chromium-headless-shell" in script
        assert "import mcp, playwright" in script
        assert "import cnki_search.mcp_server" in script
        assert "sys.argv[1]" in script
        assert "chromium.launch" in script
        assert "https://" not in script
        assert "http://" not in script
        assert "backup-" in script
        assert "3" in script
    assert "Restore-Transaction" in powershell
    assert "Rotate-Backups" in powershell
    assert "rollback_transaction" in shell
    assert "rotate_backups" in shell


def test_powershell_installer_is_no_bom_utf8_with_ascii_only_text(skill_root: Path) -> None:
    """PowerShell 5.1 按本地代码页读取无 BOM 文件，非 ASCII 字符会导致 ParserError。

    这两条断言是纯静态的，必须在所有平台上跑：CI 没有 Windows PowerShell，
    若只留在下面那个门控用例里，引入 BOM 或非 ASCII 字符的回归会一路绿灯。
    """
    payload = (skill_root / "installers/install.ps1").read_bytes()
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert payload.decode("utf-8").isascii()


@requires_windows_powershell
def test_powershell_51_parses_no_bom_utf8_installer_with_ascii_executable_text(skill_root: Path) -> None:
    installer = skill_root / "installers/install.ps1"

    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(installer)],
        cwd=skill_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "ParserError" not in result.stderr


def _load_release_builder(skill_root: Path):
    builder_path = skill_root / "scripts" / "build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_installer_test_copy", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_test_skill(skill_root: Path, destination: Path) -> Path:
    _load_release_builder(skill_root).copy_skill_tree(skill_root, destination)
    return destination


def _write_recording_powershell_runtime(path: Path, *, fail_browser_check: bool) -> None:
    failure = "if ($joined -like '*chromium.launch*') { exit 71 }\n" if fail_browser_check else ""
    path.write_text(
        "param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)\n"
        "$joined = $Arguments -join ' '\n"
        "Write-Output \"RUNTIME:$joined\"\n"
        f"{failure}"
        "if ($Arguments[0] -eq '-m' -or $Arguments[0] -eq '-c') { exit 0 }\n"
        "& $env:CNKI_TEST_REAL_PYTHON @Arguments\n"
        "exit $LASTEXITCODE\n",
        encoding="utf-8",
    )


def _prepare_powershell_test_skill(
    skill_root: Path, destination: Path, runtime_python: Path, timestamp: str,
) -> Path:
    copied_skill = _copy_test_skill(skill_root, destination)
    installer = copied_skill / "installers" / "install.ps1"
    lines = installer.read_text(encoding="utf-8").splitlines()
    timestamp_lines = [
        index for index, line in enumerate(lines)
        if line.strip().startswith("$TimeStamp = Get-Date")
    ]
    runtime_lines = [
        index for index, line in enumerate(lines)
        if line.strip().startswith("$RuntimePython = Join-Path $RuntimeRoot")
    ]
    assert len(timestamp_lines) == 1
    assert len(runtime_lines) == 1
    escaped_runtime = str(runtime_python).replace("'", "''")
    lines[timestamp_lines[0]] = f"$TimeStamp = '{timestamp}'"
    lines[runtime_lines[0]] = f"    $RuntimePython = '{escaped_runtime}'"
    installer.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return copied_skill


def _run_powershell_installer(
    copied_skill: Path, environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    command = f"& '{copied_skill / 'installers' / 'install.ps1'}' -Codex -PythonExe '{sys.executable}'"
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=copied_skill,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _git_sh() -> str:
    if os.name != "nt":
        shell = shutil.which("sh")
        assert shell is not None
        return shell
    shell = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "usr" / "bin" / "sh.exe"
    assert shell.is_file()
    return str(shell)


def _shell_path(path: Path) -> str:
    return path.as_posix() if os.name == "nt" else str(path)


def _shell_test_environment(tmp_path: Path, codex_home: Path, **extra: str) -> dict[str, str]:
    shell_tmp = tmp_path / "shell-tmp"
    shell_tmp.mkdir(exist_ok=True)
    environment = os.environ | {
        "HOME": _shell_path(tmp_path / "home"),
        "CODEX_HOME": _shell_path(codex_home),
        "TMPDIR": _shell_path(shell_tmp),
        **extra,
    }
    if os.name == "nt":
        git_usr_bin = str(Path(_git_sh()).parent)
        environment["PATH"] = f"{git_usr_bin};{environment.get('PATH', '')}"
    return environment


def _write_recording_shell_runtime(path: Path, *, fail_browser_check: bool) -> None:
    failure = "case \"$*\" in *chromium.launch*) exit 71 ;; esac\n" if fail_browser_check else ""
    path.write_text(
        "#!/bin/sh\n"
        "printf 'RUNTIME:%s\\n' \"$*\"\n"
        f"{failure}"
        "if [ \"$1\" = '-m' ] || [ \"$1\" = '-c' ]; then exit 0; fi\n"
        "\"$CNKI_TEST_REAL_PYTHON\" \"$@\"\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _prepare_shell_test_skill(
    skill_root: Path, destination: Path, runtime_python: Path, timestamp: str,
) -> Path:
    copied_skill = _copy_test_skill(skill_root, destination)
    installer = copied_skill / "installers" / "install.sh"
    lines = installer.read_text(encoding="utf-8").splitlines()
    timestamp_lines = [index for index, line in enumerate(lines) if line.strip().startswith("timestamp=$(date")]
    runtime_lines = [
        index for index, line in enumerate(lines)
        if line.strip().startswith('runtime_python="$runtime_root')
    ]
    assert len(timestamp_lines) == 1
    assert len(runtime_lines) == 1
    shell_runtime = _shell_path(runtime_python).replace("'", "'\"'\"'")
    lines[timestamp_lines[0]] = f"timestamp={timestamp}"
    lines[runtime_lines[0]] = f"runtime_python='{shell_runtime}'"
    installer.write_text("\n".join(lines) + "\n", encoding="utf-8")
    installer.chmod(0o755)
    return copied_skill


def _run_shell_installer(copied_skill: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_git_sh(), _shell_path(copied_skill / "installers" / "install.sh"), "--codex"],
        cwd=copied_skill,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


@requires_windows_powershell
def test_powershell_rejects_python_310_before_creating_install_paths(
    skill_root: Path, tmp_path: Path,
) -> None:
    fake_python = tmp_path / "python310.cmd"
    fake_python.write_text("@echo off\necho Python 3.10.9\nexit /b 0\n", encoding="utf-8")
    codex_home = tmp_path / "codex-home"
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(codex_home),
    }

    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"& '{skill_root / 'installers' / 'install.ps1'}' -Codex -PythonExe '{fake_python}'",
        ],
        cwd=skill_root,
        env=environment,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Python 3.10.9" in result.stderr
    assert "Python 3.11 or higher is required" in result.stderr
    assert not (codex_home / "skills").exists()
    assert not (codex_home / "runtimes").exists()


@requires_windows_powershell
def test_powershell_runtime_failure_restores_skill_and_config(skill_root: Path, tmp_path: Path) -> None:
    runtime_python = tmp_path / "failing-runtime.ps1"
    _write_recording_powershell_runtime(runtime_python, fail_browser_check=True)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists"
    original_skill.mkdir(parents=True)
    (original_skill / "original.txt").write_text("original skill", encoding="utf-8")
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n", encoding="utf-8")
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(codex_home),
        "CNKI_TEST_REAL_PYTHON": sys.executable,
    }

    copied_skill = _prepare_powershell_test_skill(
        skill_root, tmp_path / "skill-copy", runtime_python, "20260723-120002"
    )
    result = _run_powershell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "chromium.launch" in result.stdout
    assert (original_skill / "original.txt").read_text(encoding="utf-8") == "original skill"
    assert config.read_text(encoding="utf-8") == "[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n"


def test_generic_install_copy_does_not_contain_environment_product(
    skill_root: Path, tmp_path: Path,
) -> None:
    """两版共存靠的是各自只装自己的东西；通用版一旦夹带环境目录就会产生版本歧义。"""
    installed = _copy_test_skill(skill_root, tmp_path / "installed-generic")

    assert (installed / "SKILL.md").is_file()
    assert not (installed / "references/environment_journal_catalog_v4.0.json").exists()
    assert not (installed / "scripts/cnki_search_env").exists()


def test_shell_rejects_python_310_before_creating_install_paths(skill_root: Path, tmp_path: Path) -> None:
    fake_python = tmp_path / "python310.sh"
    fake_python.write_text("#!/bin/sh\nprintf 'Python 3.10.9\\n'\n", encoding="utf-8")
    fake_python.chmod(0o755)
    copied_skill = _copy_test_skill(skill_root, tmp_path / "skill-copy")
    codex_home = tmp_path / "codex-home"
    environment = _shell_test_environment(
        tmp_path, codex_home, **{"CNKI_PYTHON": _shell_path(fake_python)},
    )

    result = _run_shell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "Python 3.10.9" in result.stderr
    assert not (codex_home / "skills").exists()
    assert not (codex_home / "runtimes").exists()


def test_shell_runtime_failure_restores_skill_and_config(skill_root: Path, tmp_path: Path) -> None:
    runtime_python = tmp_path / "failing-runtime.sh"
    _write_recording_shell_runtime(runtime_python, fail_browser_check=True)
    copied_skill = _prepare_shell_test_skill(
        skill_root, tmp_path / "skill-copy", runtime_python, "20260723-130002"
    )
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists"
    original_skill.mkdir(parents=True)
    (original_skill / "original.txt").write_text("original skill", encoding="utf-8")
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n", encoding="utf-8")
    environment = _shell_test_environment(
        tmp_path,
        codex_home,
        **{
            "CNKI_PYTHON": _shell_path(Path(sys.executable)),
            "CNKI_TEST_REAL_PYTHON": _shell_path(Path(sys.executable)),
        },
    )

    result = _run_shell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "chromium.launch" in result.stdout
    assert (original_skill / "original.txt").read_text(encoding="utf-8") == "original skill"
    assert config.read_text(encoding="utf-8") == "[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n"


@requires_windows_powershell
def test_powershell_success_runs_self_checks_and_retains_exactly_three_backups(
    skill_root: Path, tmp_path: Path,
) -> None:
    runtime_python = tmp_path / "recording-runtime.ps1"
    _write_recording_powershell_runtime(runtime_python, fail_browser_check=False)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists"
    original_skill.mkdir(parents=True)
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[profiles.default]\nmodel = 'gpt-5'\n", encoding="utf-8")
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(codex_home),
        "CNKI_TEST_REAL_PYTHON": sys.executable,
    }

    for timestamp in ("20260723-120101", "20260723-120102", "20260723-120103", "20260723-120104"):
        copied_skill = _prepare_powershell_test_skill(
            skill_root, tmp_path / f"skill-copy-{timestamp}", runtime_python, timestamp
        )
        result = _run_powershell_installer(copied_skill, environment)
        assert result.returncode == 0, result.stderr
    commands = result.stdout
    assert "-m pip install mcp>=1,<2 playwright>=1.45,<2" in commands
    assert "-m playwright install chromium chromium-headless-shell" in commands
    assert "import mcp, playwright" in commands
    assert "import cnki_search.mcp_server" in commands
    assert "chromium.launch" in commands
    assert commands.index("-m pip install") < commands.index("-m playwright install")
    assert commands.index("-m playwright install") < commands.index("import mcp, playwright")
    assert commands.index("import mcp, playwright") < commands.index("import cnki_search.mcp_server")
    assert commands.index("import cnki_search.mcp_server") < commands.index("chromium.launch")
    skill_backups = codex_home / "backups" / "skills"
    assert len(list(skill_backups.glob("top-journal-search-lists.backup-????????-??????"))) == 3
    # 备份必须留在 skills 扫描目录之外，否则会被当作同名技能加载
    assert not list(original_skill.parent.glob("top-journal-search-lists.backup-*"))
    assert len(list(config.parent.glob("config.toml.backup-????????-??????"))) == 3


def test_shell_success_runs_self_checks_and_retains_exactly_three_backups(
    skill_root: Path, tmp_path: Path,
) -> None:
    runtime_python = tmp_path / "recording-runtime.sh"
    _write_recording_shell_runtime(runtime_python, fail_browser_check=False)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists"
    original_skill.mkdir(parents=True)
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[profiles.default]\nmodel = 'gpt-5'\n", encoding="utf-8")
    environment = _shell_test_environment(
        tmp_path,
        codex_home,
        **{
            "CNKI_PYTHON": _shell_path(Path(sys.executable)),
            "CNKI_TEST_REAL_PYTHON": _shell_path(Path(sys.executable)),
        },
    )

    for timestamp in ("20260723-130101", "20260723-130102", "20260723-130103", "20260723-130104"):
        copied_skill = _prepare_shell_test_skill(
            skill_root, tmp_path / f"skill-copy-{timestamp}", runtime_python, timestamp
        )
        result = _run_shell_installer(copied_skill, environment)
        assert result.returncode == 0, result.stderr
    commands = result.stdout
    assert "-m pip install mcp>=1,<2 playwright>=1.45,<2" in commands
    assert "-m playwright install chromium chromium-headless-shell" in commands
    assert "import mcp, playwright" in commands
    assert "import cnki_search.mcp_server" in commands
    assert "chromium.launch" in commands
    skill_backups = codex_home / "backups" / "skills"
    assert len(list(skill_backups.glob("top-journal-search-lists.backup-????????-??????"))) == 3
    # 备份必须留在 skills 扫描目录之外，否则会被当作同名技能加载
    assert not list(original_skill.parent.glob("top-journal-search-lists.backup-*"))
    assert len(list(config.parent.glob("config.toml.backup-????????-??????"))) == 3


def test_readme_documents_installer_safety_requirements(skill_root: Path) -> None:
    readme = (skill_root / "README.md").read_text(encoding="utf-8")
    for text in (
        "Python 3.11 或更高版本",
        "`-PythonExe`",
        "`CNKI_PYTHON`",
        "python -m playwright install chromium chromium-headless-shell",
        "导入检查",
        "离线启动",
        "恢复原有 Skill 和配置",
        "最近 3 份",
        "`CNKI_WEBVPN_HOME`",
        "`CNKI_WEBVPN_PROFILE`",
        "服务重启后需要重新登录",
    ):
        assert text in readme


def test_allowlisted_install_copy_excludes_workspace_baits(
    skill_root: Path, tmp_path: Path,
) -> None:
    builder_path = skill_root / "scripts/build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_install_copy", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = shutil.copytree(skill_root, tmp_path / "source")
    for relative in ("Cookie", "Local State", "random-extra.txt", "scripts/cnki_search/random_extra.py"):
        bait = source / relative
        bait.parent.mkdir(parents=True, exist_ok=True)
        bait.write_text("TASK7-INSTALL-BAIT", encoding="utf-8")

    destination = tmp_path / "installed"
    module.copy_skill_tree(source, destination)

    assert (destination / "SKILL.md").is_file()
    assert (destination / "scripts/cnki_search/service.py").is_file()
    for relative in ("Cookie", "Local State", "random-extra.txt", "scripts/cnki_search/random_extra.py"):
        assert not (destination / relative).exists()


def test_merge_claude_config_preserves_unrelated_servers() -> None:
    before = {"mcpServers": {"zotero": {"command": "zotero-mcp"}}, "theme": "dark"}
    server = cnki_server_config(Path("C:/skill"), Path("C:/skill/.venv/Scripts/python.exe"))
    after = merge_claude_config(before, server)
    assert after["mcpServers"]["zotero"] == before["mcpServers"]["zotero"]
    assert after["mcpServers"]["cnki-search"] == server
    assert after["theme"] == "dark"
    assert before["mcpServers"].keys() == {"zotero"}


def test_windows_client_paths() -> None:
    paths = client_paths(
        PureWindowsPath("C:/CodexTest"),
        platform="win32",
        env={"APPDATA": r"C:\CodexTest\AppData\Roaming"},
    )
    assert str(paths.codex_skill).endswith(r".codex\skills\top-journal-search-lists")
    assert str(paths.claude_skill).endswith(r".claude\skills\top-journal-search-lists")
    assert str(paths.claude_desktop_config).endswith(r"Claude\claude_desktop_config.json")
    assert str(paths.codex_config).endswith(r".codex\config.toml")


def test_macos_and_linux_client_paths() -> None:
    mac = client_paths(PurePosixPath("/Users/test"), platform="darwin", env={})
    linux = client_paths(PurePosixPath("/home/test"), platform="linux", env={})
    assert str(mac.claude_desktop_config) == "/Users/test/Library/Application Support/Claude/claude_desktop_config.json"
    assert str(linux.claude_desktop_config) == "/home/test/.config/Claude/claude_desktop_config.json"
    assert str(mac.codex_skill) == "/Users/test/.codex/skills/top-journal-search-lists"
    assert str(linux.claude_skill) == "/home/test/.claude/skills/top-journal-search-lists"


def test_custom_homes_are_respected() -> None:
    paths = client_paths(
        PurePosixPath("/home/test"),
        platform="linux",
        env={"CODEX_HOME": "/opt/codex", "CLAUDE_CONFIG_DIR": "/opt/claude"},
    )
    assert str(paths.codex_skill) == "/opt/codex/skills/top-journal-search-lists"
    assert str(paths.claude_skill) == "/opt/claude/skills/top-journal-search-lists"


def test_install_config_cli_terms_are_available() -> None:
    from cnki_search.install_config import build_parser

    parser = build_parser()
    args = parser.parse_args(
        [
            "merge-claude",
            "--config",
            "claude.json",
            "--skill-root",
            "skill",
            "--python",
            "python",
        ]
    )
    assert args.command == "merge-claude"


def test_merge_codex_config_adds_a_parseable_server_without_existing_tables() -> None:
    server = cnki_server_config(
        Path(r"C:\\学术资料\\top-journal-search-lists"),
        Path(r"C:\\运行时\\python.exe"),
    )

    merged = install_config.merge_codex_config("# existing configuration\n", server)

    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["cnki-search"] == server


def test_merge_codex_config_replaces_only_cnki_table_and_subtables() -> None:
    existing = """# keep this comment byte-for-byte
[mcp_servers.node_repl]
command = "node"
args = ["--experimental-repl-await"]
startup_timeout_sec = 20

[mcp_servers.cnki-search]
command = "old-python"
args = ["-m", "old_server"]

[mcp_servers.cnki-search.env]
PYTHONPATH = "old"

[profiles.default]
model = "gpt-5"
"""
    server = cnki_server_config(Path(r"C:\\中文路径\\skill"), Path(r"C:\\运行时\\python.exe"))

    merged = install_config.merge_codex_config(existing, server)

    assert "# keep this comment byte-for-byte\n[mcp_servers.node_repl]\ncommand = \"node\"\nargs = [\"--experimental-repl-await\"]\nstartup_timeout_sec = 20\n" in merged
    assert "[profiles.default]\nmodel = \"gpt-5\"\n" in merged
    assert "old-python" not in merged
    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["node_repl"]["args"] == ["--experimental-repl-await"]
    assert parsed["mcp_servers"]["node_repl"]["startup_timeout_sec"] == 20
    assert parsed["mcp_servers"]["cnki-search"] == server


def test_merge_codex_config_replaces_quoted_and_unquoted_cnki_headers() -> None:
    existing = """[mcp_servers.cnki-search]
command = "old-one"

["mcp_servers"."cnki-search".env]
PYTHONPATH = "old-one"

[mcp_servers.zotero]
command = "zotero-mcp"
"""
    server = cnki_server_config(Path("/opt/skill"), Path("/opt/python"))

    merged = install_config.merge_codex_config(existing, server)

    assert "old-one" not in merged
    assert "[mcp_servers.zotero]\ncommand = \"zotero-mcp\"\n" in merged
    assert tomllib.loads(merged)["mcp_servers"]["cnki-search"] == server


def test_merge_codex_config_preserves_user_array_tables_and_secrets() -> None:
    """数组表必须构成删除边界，否则会连同用户的 API 密钥一起被静默删除。"""
    existing = """[mcp_servers.zotero]
command = "zotero-mcp"

[mcp_servers.cnki-search]
command = "OLD-PYTHON-SHOULD-BE-REPLACED"

[[mcp_servers.custom.headers]]
name = "X-Api-Key"
value = "user-secret-token"

[[mcp_servers.custom.headers]]
name = "X-Tenant"
value = "lab-01"

[mcp_servers.ai4scholar]
command = "ai4scholar"
"""
    server = cnki_server_config(Path("/opt/skill"), Path("/opt/python"))

    merged = install_config.merge_codex_config(existing, server)

    parsed = tomllib.loads(merged)
    assert sorted(parsed["mcp_servers"]) == ["ai4scholar", "cnki-search", "custom", "zotero"]
    assert parsed["mcp_servers"]["custom"]["headers"] == [
        {"name": "X-Api-Key", "value": "user-secret-token"},
        {"name": "X-Tenant", "value": "lab-01"},
    ]
    assert "OLD-PYTHON-SHOULD-BE-REPLACED" not in merged
    assert parsed["mcp_servers"]["cnki-search"] == server


def test_merge_codex_config_rejects_unreplaceable_inline_cnki_definition() -> None:
    existing = 'mcp_servers.cnki-search = { command = "old" }\n'
    server = cnki_server_config(Path("/opt/skill"), Path("/opt/python"))

    with pytest.raises(ValueError, match="无法安全替换"):
        install_config.merge_codex_config(existing, server)


def test_merge_codex_cli_reports_readable_error_instead_of_traceback(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('mcp_servers.cnki-search = { command = "old" }\n', encoding="utf-8")

    exit_code = main(
        ["merge-codex", "--config", str(config), "--skill-root", "/opt/skill", "--python", "/opt/py"]
    )

    assert exit_code == 1
    # 失败发生在写盘之前，用户配置不受损
    assert config.read_text(encoding="utf-8") == 'mcp_servers.cnki-search = { command = "old" }\n'


def test_installers_gate_python_version_and_install_browser(skill_root: Path) -> None:
    """3.10 can install dependencies but cannot start cnki_search, so installers must reject it."""
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")
    for content in (powershell, shell):
        assert "Python 3.11 or higher is required" in content
        assert "playwright install chromium chromium-headless-shell" in content


def test_merge_codex_cli_writes_parseable_toml_with_windows_paths() -> None:
    config = Path(__file__).parent / "task8-codex-config.toml"
    if config.exists():
        config.unlink()
    try:
        exit_code = main(
            [
                "merge-codex",
                "--config",
                str(config),
                "--skill-root",
                r"C:\用户\学术资料\top-journal-search-lists",
                "--python",
                r"C:\用户\运行时\python.exe",
            ]
        )

        assert exit_code == 0
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        assert parsed["mcp_servers"]["cnki-search"]["command"] == r"C:\用户\运行时\python.exe"
    finally:
        if config.exists():
            config.unlink()


def test_readme_documents_supported_platforms_clients_and_installed_names():
    skill_root = Path(__file__).resolve().parents[1]
    readme = (skill_root / "README.md").read_text(encoding="utf-8")

    def section(heading: str) -> str:
        start = readme.index(heading)
        end = readme.find("\n## ", start + len(heading))
        return readme[start:] if end == -1 else readme[start:end]

    required_text = (
        "Top Journal and Public CNKI Search",
        "$top-journal-search-lists",
        "cnki-search",
        "cnki_search(query, limit)",
        "Claude Code",
        "Claude Desktop",
        "Codex CLI",
        "ChatGPT Desktop 中的 Codex",
        "## Windows 安装指南",
        "## macOS 安装指南",
        "## Linux 安装指南",
        "手工复制",
        "不会自动配置",
        "目前没有官方 Linux 版 ChatGPT Desktop",
    )
    for text in required_text:
        assert text in readme

    windows = section("## Windows 安装指南")
    macos = section("## macOS 安装指南")
    assert "ChatGPT Desktop 中的 Codex" in readme
    assert "Codex Desktop" not in readme
    assert "ChatGPT Desktop 中的 Codex" in windows
    assert "ChatGPT Desktop 中的 Codex" in macos
    assert "powershell -ExecutionPolicy Bypass -File .\\top-journal-search-lists\\installers\\install.ps1 -Codex -ClaudeCode -ClaudeDesktop" in windows
    assert "sh ./top-journal-search-lists/installers/install.sh --codex --claude-code --claude-desktop" in macos


def test_readme_documents_installer_runtime_and_platform_boundaries():
    skill_root = Path(__file__).resolve().parents[1]
    readme = (skill_root / "README.md").read_text(encoding="utf-8")

    required_text = (
        # 两种模式上限不同，README 必须分别写明各自真正能拿到的条数
        "公开检索最大 20",
        "专业检索最大 50",
        "Claude Desktop（Linux beta）",
        "官方 Linux 版 ChatGPT Desktop",
        "WSL 中的安装属于 Linux 侧安装",
        "绝不会配置 Windows ChatGPT Desktop",
        "复制完整 Skill",
        "创建独立 Python 运行环境",
        "安装 `mcp` 与 `playwright`",
        "不删除 Zotero、ai4scholar 等其他 MCP 服务",
        "带时间戳的备份",
        "只要选择 Codex，运行环境位于 Codex Home",
        "仅选择 Claude 目标时，运行环境位于 Claude Home",
    )
    for text in required_text:
        assert text in readme


def test_readme_documents_cross_computer_installation_and_verification():
    skill_root = Path(__file__).resolve().parents[1]
    readme = (skill_root / "README.md").read_text(encoding="utf-8")

    def section(heading: str) -> str:
        start = readme.index(heading)
        end = readme.find("\n## ", start + len(heading))
        return readme[start:] if end == -1 else readme[start:end]

    preparation = section("## 安装前准备")
    linux = section("## Linux 安装指南")
    verification = section("## 安装后验证")
    developer_checks = section("## 开发者完整测试")

    # agent/cnki-new-entry-only 已与默认分支同点，不再需要 --branch 指引
    assert "git clone https://github.com/hushiliang2009/cnki-top-journal-search-skill.git" in preparation
    assert "cd cnki-top-journal-search-skill" in preparation
    assert "GitHub 认证" in preparation
    assert "agent/cnki-new-entry-only" not in preparation
    assert "python -m playwright install chromium chromium-headless-shell" in preparation
    assert "Claude Desktop（Linux beta）" in linux
    assert "目前没有官方 Linux 版 ChatGPT Desktop" in linux
    assert "Claude Desktop 也不支持 Linux" not in linux
    assert "sh ./top-journal-search-lists/installers/install.sh --claude-desktop" in linux
    assert (
        "sh ./top-journal-search-lists/installers/install.sh "
        "--codex --claude-code --claude-desktop"
    ) in linux
    assert "~/.config/Claude/claude_desktop_config.json" in linux
    wsl_text = linux
    assert "Windows 侧 ChatGPT Desktop 中的 Codex" in wsl_text
    assert "Windows" in verification
    assert "python top-journal-search-lists/scripts/catalog_lookup.py validate" in verification
    assert "macOS/Linux" in verification
    assert "python3 top-journal-search-lists/scripts/catalog_lookup.py validate" in verification
    assert "pytest" not in verification
    assert "pytest" in developer_checks
    assert "开发环境安装 pytest" in developer_checks
    assert "Windows: python -m pytest" not in developer_checks
    assert "macOS/Linux: python3 -m pytest" not in developer_checks
