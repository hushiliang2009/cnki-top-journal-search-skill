from __future__ import annotations

import copy
import argparse
import json
from dataclasses import dataclass
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Mapping


@dataclass(frozen=True)
class ClientPaths:
    codex_skill: PurePath
    claude_skill: PurePath
    codex_config: PurePath
    claude_desktop_config: PurePath
    claude_code_config: PurePath


def _path_for(platform: str, value: str) -> PurePath:
    return PureWindowsPath(value) if platform == "win32" else PurePosixPath(value)


def client_paths(home: PurePath, *, platform: str, env: Mapping[str, str]) -> ClientPaths:
    if platform not in {"win32", "darwin", "linux"}:
        raise ValueError(f"不支持的平台：{platform}")
    codex_home = _path_for(platform, env["CODEX_HOME"]) if env.get("CODEX_HOME") else home / ".codex"
    claude_home = (
        _path_for(platform, env["CLAUDE_CONFIG_DIR"])
        if env.get("CLAUDE_CONFIG_DIR")
        else home / ".claude"
    )
    if platform == "win32":
        appdata = _path_for(platform, env.get("APPDATA", str(home / "AppData/Roaming")))
        claude_desktop = appdata / "Claude" / "claude_desktop_config.json"
    elif platform == "darwin":
        claude_desktop = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        claude_desktop = home / ".config" / "Claude" / "claude_desktop_config.json"
    return ClientPaths(
        codex_skill=codex_home / "skills" / "top-journal-search-lists",
        claude_skill=claude_home / "skills" / "top-journal-search-lists",
        codex_config=codex_home / "config.toml",
        claude_desktop_config=claude_desktop,
        claude_code_config=home / ".claude.json",
    )


def cnki_server_config(skill_root: Path, python_executable: Path) -> dict[str, object]:
    return {
        "command": str(python_executable),
        "args": ["-m", "cnki_search.mcp_server"],
        "env": {
            "PYTHONPATH": str(skill_root / "scripts"),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        },
    }


def merge_claude_config(
    existing: Mapping[str, object], server_config: Mapping[str, object]
) -> dict[str, object]:
    result = copy.deepcopy(dict(existing))
    servers = result.get("mcpServers")
    if servers is None:
        result["mcpServers"] = {}
        servers = result["mcpServers"]
    if not isinstance(servers, dict):
        raise ValueError("Claude 配置中的 mcpServers 必须是对象")
    servers["cnki-search"] = copy.deepcopy(dict(server_config))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="增量配置 CNKI MCP")
    commands = parser.add_subparsers(dest="command", required=True)
    merge = commands.add_parser("merge-claude")
    merge.add_argument("--config", type=Path, required=True)
    merge.add_argument("--skill-root", type=Path, required=True)
    merge.add_argument("--python", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path: Path = args.config
    if config_path.is_file():
        existing = json.loads(config_path.read_text(encoding="utf-8-sig"))
    else:
        existing = {}
    merged = merge_claude_config(
        existing, cnki_server_config(args.skill_root, args.python)
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = config_path.with_name(f"{config_path.name}.tmp")
    temporary.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
