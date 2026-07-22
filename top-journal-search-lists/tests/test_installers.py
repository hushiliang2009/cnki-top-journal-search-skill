from pathlib import Path, PurePosixPath, PureWindowsPath

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
