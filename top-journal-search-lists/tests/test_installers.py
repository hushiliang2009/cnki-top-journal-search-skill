import importlib.util
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil

import tomllib

import cnki_search.install_config as install_config
from cnki_search.install_config import (
    client_paths,
    cnki_server_config,
    main,
    merge_claude_config,
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
                r"C:\\用户\\学术资料\\top-journal-search-lists",
                "--python",
                r"C:\\用户\\运行时\\python.exe",
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

    assert "git clone --branch agent/cnki-new-entry-only --single-branch https://github.com/hushiliang2009/cnki-top-journal-search-skill.git" in preparation
    assert "cd cnki-top-journal-search-skill" in preparation
    assert "GitHub 认证" in preparation
    assert "默认分支后可省略 `--branch agent/cnki-new-entry-only --single-branch`" in preparation
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
