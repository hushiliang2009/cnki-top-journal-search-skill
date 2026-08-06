import importlib.util
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys

import pytest
import tomllib

import cnki_search_env.install_config as install_config
from cnki_search_env.install_config import (
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
    assert 'python_command=${CNKI_ENV_PYTHON:-python3}' in shell
    assert "assert_python_version" in shell
    assert shell.rindex("assert_python_version") < shell.index("install_skill()")


def test_installers_require_runtime_self_checks_and_transactional_restore(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")

    for script in (powershell, shell):
        assert "playwright install chromium chromium-headless-shell" in script
        assert "PLAYWRIGHT_BROWSERS_PATH" in script
        assert "playwright-browsers" in script
        assert "import mcp, playwright" in script
        assert "import cnki_search_env.mcp_server" in script
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
        "if ($env:CNKI_TEST_RUNTIME_ROOT) {\n"
        "  New-Item -ItemType Directory -Path $env:CNKI_TEST_RUNTIME_ROOT -Force | Out-Null\n"
        "  Set-Content -LiteralPath (Join-Path $env:CNKI_TEST_RUNTIME_ROOT 'partial-update.txt') "
        "-Value 'partial runtime update'\n"
        "}\n"
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
        # 这些用例走替身 runtime，不做真实 pip 解包；而 .pytest-runtime 下的路径
        # 本身就超过长路径预算，会被预检拦下。预检自身由专门的用例验证。
        env=environment | {"CNKI_TEST_SKIP_PATH_BUDGET": "1"},
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
        "if [ -n \"${CNKI_TEST_RUNTIME_ROOT:-}\" ]; then\n"
        "  mkdir -p \"$CNKI_TEST_RUNTIME_ROOT\"\n"
        "  printf '%s\\n' 'partial runtime update' > \"$CNKI_TEST_RUNTIME_ROOT/partial-update.txt\"\n"
        "fi\n"
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
@pytest.mark.parametrize("existing_runtime", [True, False])
def test_powershell_runtime_failure_restores_skill_and_config(
    skill_root: Path, tmp_path: Path, existing_runtime: bool,
) -> None:
    runtime_python = tmp_path / "failing-runtime.ps1"
    _write_recording_powershell_runtime(runtime_python, fail_browser_check=True)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists-env"
    original_skill.mkdir(parents=True)
    (original_skill / "original.txt").write_text("original skill", encoding="utf-8")
    original_runtime = codex_home / "runtimes" / "cnki-search-env"
    if existing_runtime:
        original_runtime.mkdir(parents=True)
        (original_runtime / "original-runtime.txt").write_text("original runtime", encoding="utf-8")
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n", encoding="utf-8")
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(codex_home),
        "CNKI_TEST_REAL_PYTHON": sys.executable,
        "CNKI_TEST_RUNTIME_ROOT": str(original_runtime),
    }

    copied_skill = _prepare_powershell_test_skill(
        skill_root, tmp_path / "skill-copy", runtime_python, "20260723-120002"
    )
    result = _run_powershell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "chromium.launch" in result.stdout
    assert (original_skill / "original.txt").read_text(encoding="utf-8") == "original skill"
    if existing_runtime:
        assert (original_runtime / "original-runtime.txt").read_text(encoding="utf-8") == "original runtime"
        assert not (original_runtime / "partial-update.txt").exists()
    else:
        assert not original_runtime.exists()
    assert config.read_text(encoding="utf-8") == "[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n"


def test_shell_rejects_python_310_before_creating_install_paths(skill_root: Path, tmp_path: Path) -> None:
    fake_python = tmp_path / "python310.sh"
    fake_python.write_text("#!/bin/sh\nprintf 'Python 3.10.9\\n'\n", encoding="utf-8")
    fake_python.chmod(0o755)
    copied_skill = _copy_test_skill(skill_root, tmp_path / "skill-copy")
    codex_home = tmp_path / "codex-home"
    environment = _shell_test_environment(
        tmp_path, codex_home, **{"CNKI_ENV_PYTHON": _shell_path(fake_python)},
    )

    result = _run_shell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "Python 3.10.9" in result.stderr
    assert not (codex_home / "skills").exists()
    assert not (codex_home / "runtimes").exists()


@pytest.mark.parametrize("existing_runtime", [True, False])
def test_shell_runtime_failure_restores_skill_and_config(
    skill_root: Path, tmp_path: Path, existing_runtime: bool,
) -> None:
    runtime_python = tmp_path / "failing-runtime.sh"
    _write_recording_shell_runtime(runtime_python, fail_browser_check=True)
    copied_skill = _prepare_shell_test_skill(
        skill_root, tmp_path / "skill-copy", runtime_python, "20260723-130002"
    )
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists-env"
    original_skill.mkdir(parents=True)
    (original_skill / "original.txt").write_text("original skill", encoding="utf-8")
    original_runtime = codex_home / "runtimes" / "cnki-search-env"
    if existing_runtime:
        original_runtime.mkdir(parents=True)
        (original_runtime / "original-runtime.txt").write_text("original runtime", encoding="utf-8")
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n", encoding="utf-8")
    environment = _shell_test_environment(
        tmp_path,
        codex_home,
        **{
            "CNKI_ENV_PYTHON": _shell_path(Path(sys.executable)),
            "CNKI_TEST_REAL_PYTHON": _shell_path(Path(sys.executable)),
            "CNKI_TEST_RUNTIME_ROOT": _shell_path(original_runtime),
        },
    )

    result = _run_shell_installer(copied_skill, environment)

    assert result.returncode != 0
    assert "chromium.launch" in result.stdout
    assert (original_skill / "original.txt").read_text(encoding="utf-8") == "original skill"
    if existing_runtime:
        assert (original_runtime / "original-runtime.txt").read_text(encoding="utf-8") == "original runtime"
        assert not (original_runtime / "partial-update.txt").exists()
    else:
        assert not original_runtime.exists()
    assert config.read_text(encoding="utf-8") == "[mcp_servers.zotero]\ncommand = 'zotero-mcp'\n"


@requires_windows_powershell
def test_powershell_success_runs_self_checks_and_retains_exactly_three_backups(
    skill_root: Path, tmp_path: Path,
) -> None:
    runtime_python = tmp_path / "recording-runtime.ps1"
    _write_recording_powershell_runtime(runtime_python, fail_browser_check=False)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists-env"
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
    assert "import cnki_search_env.mcp_server" in commands
    assert "chromium.launch" in commands
    assert commands.index("-m pip install") < commands.index("-m playwright install")
    assert commands.index("-m playwright install") < commands.index("import mcp, playwright")
    assert commands.index("import mcp, playwright") < commands.index("import cnki_search_env.mcp_server")
    assert commands.index("import cnki_search_env.mcp_server") < commands.index("chromium.launch")
    skill_backups = codex_home / "backups" / "skills"
    assert len(list(skill_backups.glob("top-journal-search-lists-env.backup-????????-??????"))) == 3
    runtime_backups = codex_home / "backups" / "runtimes"
    assert len(list(runtime_backups.glob("cnki-search-env.backup-????????-??????"))) == 3
    # 备份必须留在 skills 扫描目录之外，否则会被当作同名技能加载
    assert not list(original_skill.parent.glob("top-journal-search-lists-env.backup-*"))
    assert len(list(config.parent.glob("config.toml.backup-????????-??????"))) == 3


@requires_windows_powershell
def test_environment_install_coexists_with_generic_skill_and_mcp(
    skill_root: Path, tmp_path: Path,
) -> None:
    runtime_python = tmp_path / "recording-runtime.ps1"
    _write_recording_powershell_runtime(runtime_python, fail_browser_check=False)
    copied_skill = _prepare_powershell_test_skill(
        skill_root, tmp_path / "skill-copy", runtime_python, "20260726-230001"
    )
    codex_home = tmp_path / "codex-home"
    generic_skill = codex_home / "skills" / "top-journal-search-lists"
    generic_skill.mkdir(parents=True)
    (generic_skill / "generic.txt").write_text("keep generic", encoding="utf-8")
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "[mcp_servers.cnki-search]\n"
        'command = "generic-python"\n'
        'args = ["-m", "cnki_search.mcp_server"]\n',
        encoding="utf-8",
    )
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(codex_home),
        "CNKI_TEST_REAL_PYTHON": sys.executable,
    }

    result = _run_powershell_installer(copied_skill, environment)

    assert result.returncode == 0, result.stderr
    parsed = tomllib.loads(config.read_text(encoding="utf-8"))
    assert parsed["mcp_servers"]["cnki-search"]["command"] == "generic-python"
    assert "cnki-search-env" in parsed["mcp_servers"]
    assert (generic_skill / "generic.txt").read_text(encoding="utf-8") == "keep generic"
    assert (codex_home / "skills" / "top-journal-search-lists-env").is_dir()
    assert (codex_home / "runtimes" / "cnki-search-env").is_dir()
    assert (
        codex_home
        / "skills/top-journal-search-lists-env/references/environment_journal_catalog_v4.0.json"
    ).is_file()


def test_shell_success_runs_self_checks_and_retains_exactly_three_backups(
    skill_root: Path, tmp_path: Path,
) -> None:
    runtime_python = tmp_path / "recording-runtime.sh"
    _write_recording_shell_runtime(runtime_python, fail_browser_check=False)
    codex_home = tmp_path / "codex-home"
    original_skill = codex_home / "skills" / "top-journal-search-lists-env"
    original_skill.mkdir(parents=True)
    config = codex_home / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("[profiles.default]\nmodel = 'gpt-5'\n", encoding="utf-8")
    environment = _shell_test_environment(
        tmp_path,
        codex_home,
        **{
            "CNKI_ENV_PYTHON": _shell_path(Path(sys.executable)),
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
    assert "import cnki_search_env.mcp_server" in commands
    assert "chromium.launch" in commands
    skill_backups = codex_home / "backups" / "skills"
    assert len(list(skill_backups.glob("top-journal-search-lists-env.backup-????????-??????"))) == 3
    runtime_backups = codex_home / "backups" / "runtimes"
    assert len(list(runtime_backups.glob("cnki-search-env.backup-????????-??????"))) == 3
    # 备份必须留在 skills 扫描目录之外，否则会被当作同名技能加载
    assert not list(original_skill.parent.glob("top-journal-search-lists-env.backup-*"))
    assert len(list(config.parent.glob("config.toml.backup-????????-??????"))) == 3


def test_readme_documents_installer_safety_requirements(skill_root: Path) -> None:
    readme = (skill_root / "README.md").read_text(encoding="utf-8")
    for text in (
        "Python 3.11 或更高版本",
        "`-PythonExe`",
        "`CNKI_ENV_PYTHON`",
        "python -m playwright install chromium chromium-headless-shell",
        "导入检查",
        "离线启动",
        "恢复原有 Skill、环境运行时和配置",
        "`backups/runtimes/`",
        "`CNKI_ENV_BROWSER_PATH`",
        "最近 3 份",
    ):
        assert text in readme


def test_allowlisted_install_contains_environment_v4_portable_files(
    skill_root: Path, tmp_path: Path,
) -> None:
    """装好之后目录数据和离线复算脚本都要在本地，否则用户只能相信我们的说法。"""
    installed = _copy_test_skill(skill_root, tmp_path / "installed-env")

    for relative in (
        "references/环境科学与工程学科顶尖期刊目录_v4.0.md",
        "references/environment_journal_catalog_v4.0.json",
        "references/environment_catalog_sources_v4.0.json",
        "scripts/environment_catalog_v4.py",
        "scripts/generate_environment_catalog_v4.py",
    ):
        assert (installed / relative).is_file(), relative
    assert not (installed / "references/环境科学与工程学科顶尖期刊目录_v3.0.md").exists()


def test_allowlisted_install_copy_excludes_workspace_baits(
    skill_root: Path, tmp_path: Path,
) -> None:
    builder_path = skill_root / "scripts/build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_install_copy", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = shutil.copytree(skill_root, tmp_path / "source")
    for relative in ("Cookie", "Local State", "random-extra.txt", "scripts/cnki_search_env/random_extra.py"):
        bait = source / relative
        bait.parent.mkdir(parents=True, exist_ok=True)
        bait.write_text("TASK7-INSTALL-BAIT", encoding="utf-8")

    destination = tmp_path / "installed"
    module.copy_skill_tree(source, destination)

    assert (destination / "SKILL.md").is_file()
    assert (destination / "scripts/cnki_search_env/service.py").is_file()
    for relative in ("Cookie", "Local State", "random-extra.txt", "scripts/cnki_search_env/random_extra.py"):
        assert not (destination / relative).exists()


def test_merge_claude_config_preserves_unrelated_servers() -> None:
    before = {"mcpServers": {"zotero": {"command": "zotero-mcp"}}, "theme": "dark"}
    server = cnki_server_config(Path("C:/skill"), Path("C:/skill/.venv/Scripts/python.exe"))
    after = merge_claude_config(before, server)
    assert after["mcpServers"]["zotero"] == before["mcpServers"]["zotero"]
    assert after["mcpServers"]["cnki-search-env"] == server
    assert server["env"]["PLAYWRIGHT_BROWSERS_PATH"] == str(
        Path("C:/skill/playwright-browsers")
    )
    assert after["theme"] == "dark"
    assert before["mcpServers"].keys() == {"zotero"}


def test_merge_claude_config_keeps_user_env_across_upgrades() -> None:
    """升级不得丢掉使用者自加的环境变量，但受管键必须跟着新运行时走。

    PLAYWRIGHT_BROWSERS_PATH 指向运行时目录，若被误当作使用者变量保留，
    升级后浏览器路径仍指向旧运行时，无头浏览器将无法启动。
    """
    before = {
        "mcpServers": {
            "cnki-search-env": {
                "command": "/old/.venv/bin/python",
                "args": ["-m", "cnki_search_env.mcp_server"],
                "env": {
                    "PYTHONPATH": "/old/skill/scripts",
                    "PYTHONUTF8": "1",
                    "PYTHONIOENCODING": "utf-8",
                    "PLAYWRIGHT_BROWSERS_PATH": "/old/playwright-browsers",
                    "CNKI_ENV_WEBVPN_HOME": "https://webvpn.example.edu.cn/cnki",
                },
            }
        }
    }
    server = cnki_server_config(Path("/new/skill"), Path("/new/runtime/.venv/bin/python"))

    after = merge_claude_config(before, server)
    entry = after["mcpServers"]["cnki-search-env"]

    assert entry["command"] == "/new/runtime/.venv/bin/python"
    assert entry["env"]["PYTHONPATH"] == str(Path("/new/skill") / "scripts")
    # 受管键跟随新运行时，不得沿用旧值
    assert entry["env"]["PLAYWRIGHT_BROWSERS_PATH"] == str(
        Path("/new/runtime/playwright-browsers")
    )
    # 使用者自加的键原样留下
    assert entry["env"]["CNKI_ENV_WEBVPN_HOME"] == "https://webvpn.example.edu.cn/cnki"
    assert before["mcpServers"]["cnki-search-env"]["command"] == "/old/.venv/bin/python"


def test_merge_codex_config_keeps_user_env_across_upgrades() -> None:
    """Codex 侧同样不得丢使用者变量。该路径删表重渲染，更容易漏掉。"""
    existing = "\n".join(
        [
            "[mcp_servers.cnki-search-env]",
            'command = "/old/.venv/bin/python"',
            'args = ["-m", "cnki_search_env.mcp_server"]',
            "",
            "[mcp_servers.cnki-search-env.env]",
            'PYTHONPATH = "/old/skill/scripts"',
            'PYTHONUTF8 = "1"',
            'PYTHONIOENCODING = "utf-8"',
            'PLAYWRIGHT_BROWSERS_PATH = "/old/playwright-browsers"',
            'CNKI_ENV_WEBVPN_HOME = "https://webvpn.example.edu.cn/cnki"',
            "",
        ]
    )
    server = cnki_server_config(Path("/new/skill"), Path("/new/runtime/.venv/bin/python"))

    merged = install_config.merge_codex_config(existing, server)

    entry = tomllib.loads(merged)["mcp_servers"]["cnki-search-env"]
    assert entry["env"]["PLAYWRIGHT_BROWSERS_PATH"] == str(
        Path("/new/runtime/playwright-browsers")
    )
    assert entry["env"]["CNKI_ENV_WEBVPN_HOME"] == "https://webvpn.example.edu.cn/cnki"


def test_windows_client_paths() -> None:
    paths = client_paths(
        PureWindowsPath("C:/CodexTest"),
        platform="win32",
        env={"APPDATA": r"C:\CodexTest\AppData\Roaming"},
    )
    assert str(paths.codex_skill).endswith(r".codex\skills\top-journal-search-lists-env")
    assert str(paths.claude_skill).endswith(r".claude\skills\top-journal-search-lists-env")
    assert str(paths.claude_desktop_config).endswith(r"Claude\claude_desktop_config.json")
    assert str(paths.codex_config).endswith(r".codex\config.toml")


def test_macos_and_linux_client_paths() -> None:
    mac = client_paths(PurePosixPath("/Users/test"), platform="darwin", env={})
    linux = client_paths(PurePosixPath("/home/test"), platform="linux", env={})
    assert str(mac.claude_desktop_config) == "/Users/test/Library/Application Support/Claude/claude_desktop_config.json"
    assert str(linux.claude_desktop_config) == "/home/test/.config/Claude/claude_desktop_config.json"
    assert str(mac.codex_skill) == "/Users/test/.codex/skills/top-journal-search-lists-env"
    assert str(linux.claude_skill) == "/home/test/.claude/skills/top-journal-search-lists-env"


def test_custom_homes_are_respected() -> None:
    paths = client_paths(
        PurePosixPath("/home/test"),
        platform="linux",
        env={"CODEX_HOME": "/opt/codex", "CLAUDE_CONFIG_DIR": "/opt/claude"},
    )
    assert str(paths.codex_skill) == "/opt/codex/skills/top-journal-search-lists-env"
    assert str(paths.claude_skill) == "/opt/claude/skills/top-journal-search-lists-env"


def test_install_config_cli_terms_are_available() -> None:
    from cnki_search_env.install_config import build_parser

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
        Path(r"C:\\学术资料\\top-journal-search-lists-env"),
        Path(r"C:\\运行时\\python.exe"),
    )

    merged = install_config.merge_codex_config("# existing configuration\n", server)

    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["cnki-search-env"] == server


def test_merge_codex_config_replaces_only_cnki_table_and_subtables() -> None:
    existing = """# keep this comment byte-for-byte
[mcp_servers.node_repl]
command = "node"
args = ["--experimental-repl-await"]
startup_timeout_sec = 20

[mcp_servers.cnki-search-env]
command = "old-python"
args = ["-m", "old_server"]

[mcp_servers.cnki-search-env.env]
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
    assert parsed["mcp_servers"]["cnki-search-env"] == server


def test_merge_codex_config_replaces_quoted_and_unquoted_cnki_headers() -> None:
    existing = """[mcp_servers.cnki-search-env]
command = "old-one"

["mcp_servers"."cnki-search-env".env]
PYTHONPATH = "old-one"

[mcp_servers.zotero]
command = "zotero-mcp"
"""
    server = cnki_server_config(Path("/opt/skill"), Path("/opt/python"))

    merged = install_config.merge_codex_config(existing, server)

    assert "old-one" not in merged
    assert "[mcp_servers.zotero]\ncommand = \"zotero-mcp\"\n" in merged
    assert tomllib.loads(merged)["mcp_servers"]["cnki-search-env"] == server


def test_merge_codex_config_preserves_user_array_tables_and_secrets() -> None:
    """数组表必须构成删除边界，否则会连同用户的 API 密钥一起被静默删除。"""
    existing = """[mcp_servers.zotero]
command = "zotero-mcp"

[mcp_servers.cnki-search-env]
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
    assert sorted(parsed["mcp_servers"]) == ["ai4scholar", "cnki-search-env", "custom", "zotero"]
    assert parsed["mcp_servers"]["custom"]["headers"] == [
        {"name": "X-Api-Key", "value": "user-secret-token"},
        {"name": "X-Tenant", "value": "lab-01"},
    ]
    assert "OLD-PYTHON-SHOULD-BE-REPLACED" not in merged
    assert parsed["mcp_servers"]["cnki-search-env"] == server


def test_merge_codex_config_rejects_unreplaceable_inline_cnki_definition() -> None:
    existing = 'mcp_servers.cnki-search-env = { command = "old" }\n'
    server = cnki_server_config(Path("/opt/skill"), Path("/opt/python"))

    with pytest.raises(ValueError, match="无法安全替换"):
        install_config.merge_codex_config(existing, server)


def test_merge_codex_cli_reports_readable_error_instead_of_traceback(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('mcp_servers.cnki-search-env = { command = "old" }\n', encoding="utf-8")

    exit_code = main(
        ["merge-codex", "--config", str(config), "--skill-root", "/opt/skill", "--python", "/opt/py"]
    )

    assert exit_code == 1
    # 失败发生在写盘之前，用户配置不受损
    assert config.read_text(encoding="utf-8") == 'mcp_servers.cnki-search-env = { command = "old" }\n'


def test_installers_gate_python_version_and_install_browser(skill_root: Path) -> None:
    """3.10 can install dependencies but cannot start cnki_search_env, so installers must reject it."""
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
                r"C:\用户\学术资料\top-journal-search-lists-env",
                "--python",
                r"C:\用户\运行时\python.exe",
            ]
        )

        assert exit_code == 0
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        assert parsed["mcp_servers"]["cnki-search-env"]["command"] == r"C:\用户\运行时\python.exe"
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
        "Top Environmental Journal Search",
        "$top-journal-search-lists-env",
        "cnki-search-env",
        "cnki_search_env(query, limit)",
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
    assert "powershell -ExecutionPolicy Bypass -File .\\top-journal-search-lists-env\\installers\\install.ps1 -Codex -ClaudeCode -ClaudeDesktop" in windows
    assert "sh ./top-journal-search-lists-env/installers/install.sh --codex --claude-code --claude-desktop" in macos


def test_readme_documents_installer_runtime_and_platform_boundaries():
    skill_root = Path(__file__).resolve().parents[1]
    readme = (skill_root / "README.md").read_text(encoding="utf-8")

    required_text = (
        "`limit` 最大为 20",
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
    assert "sh ./top-journal-search-lists-env/installers/install.sh --claude-desktop" in linux
    assert (
        "sh ./top-journal-search-lists-env/installers/install.sh "
        "--codex --claude-code --claude-desktop"
    ) in linux
    assert "~/.config/Claude/claude_desktop_config.json" in linux
    wsl_text = linux
    assert "Windows 侧 ChatGPT Desktop 中的 Codex" in wsl_text
    assert "Windows" in verification
    assert "python top-journal-search-lists-env/scripts/catalog_lookup.py validate" in verification
    assert "macOS/Linux" in verification
    assert "python3 top-journal-search-lists-env/scripts/catalog_lookup.py validate" in verification
    assert "pytest" not in verification
    assert "pytest" in developer_checks
    assert "开发环境安装 pytest" in developer_checks
    assert "Windows: python -m pytest" not in developer_checks
    assert "macOS/Linux: python3 -m pytest" not in developer_checks


@requires_windows_powershell
def test_powershell_rejects_a_too_deep_codex_home_before_writing_anything(
    skill_root: Path, tmp_path: Path,
) -> None:
    """playwright 的 driver 目录很深，深 CODEX_HOME 下 pip 解包会超 Windows MAX_PATH。

    失败发生在 pip 阶段，安装器只透传一段英文 pip 报错，用户要读完整段才能定位；
    而此时 Skill 已经复制过、备份已经产生。预检必须在任何写入之前拦下。
    """
    deep_home = tmp_path / ("d" * 120) / "codex-home"
    environment = os.environ | {
        "USERPROFILE": str(tmp_path / "profile"),
        "APPDATA": str(tmp_path / "appdata"),
        "CODEX_HOME": str(deep_home),
    }

    result = subprocess.run(
        [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"& '{skill_root / 'installers' / 'install.ps1'}' -Codex -PythonExe python",
        ],
        cwd=skill_root,
        env=environment,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "too long" in result.stderr.casefold(), result.stderr
    assert not (deep_home / "skills").exists()
    assert not (deep_home / "runtimes").exists()
    assert not (deep_home / "backups").exists()
