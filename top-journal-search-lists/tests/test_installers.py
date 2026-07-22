from pathlib import Path, PurePosixPath, PureWindowsPath

from cnki_search.install_config import client_paths, cnki_server_config, merge_claude_config


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
        PureWindowsPath("C:/Users/Test"),
        platform="win32",
        env={"APPDATA": r"C:\Users\Test\AppData\Roaming"},
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
