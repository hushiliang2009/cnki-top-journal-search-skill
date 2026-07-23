from __future__ import annotations

import copy
import argparse
import json
import os
import re
import tempfile
import tomllib
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


_TOML_TABLE_HEADER = re.compile(
    r"(?m)^[\t ]*(?:\[\[(?P<array_path>[^\]\r\n]+)\]\]|\[(?P<table_path>[^\]\r\n]+)\])[\t ]*(?:#.*)?(?:\r?\n|$)"
)
_TOML_ASSIGNMENT = re.compile(r"(?m)^[\t ]*(?P<key>[^#=\r\n]+?)\s*=")


def _toml_key_path(value: str) -> tuple[str, ...] | None:
    keys: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        while index < length and value[index] in " \t":
            index += 1
        if index >= length:
            return None
        if value[index] == '"':
            end = index + 1
            while end < length:
                if value[end] == "\\":
                    end += 2
                    continue
                if value[end] == '"':
                    break
                end += 1
            if end >= length:
                return None
            try:
                key = json.loads(value[index : end + 1])
            except json.JSONDecodeError:
                return None
            index = end + 1
        elif value[index] == "'":
            end = value.find("'", index + 1)
            if end < 0:
                return None
            key = value[index + 1 : end]
            index = end + 1
        else:
            end = index
            while end < length and value[end] not in ". \t":
                end += 1
            key = value[index:end]
            if not key:
                return None
            index = end
        keys.append(key)
        while index < length and value[index] in " \t":
            index += 1
        if index == length:
            return tuple(keys)
        if value[index] != ".":
            return None
        index += 1
    return None


def _is_cnki_table(path: tuple[str, ...] | None) -> bool:
    return bool(
        path
        and len(path) >= 2
        and path[0] == "mcp_servers"
        and path[1] == "cnki-search"
    )


def _toml_table_headers(existing_toml: str) -> list[tuple[int, tuple[str, ...] | None]]:
    return [
        (match.start(), _toml_key_path(match.group("array_path") or match.group("table_path")))
        for match in _TOML_TABLE_HEADER.finditer(existing_toml)
    ]


def _reject_unsupported_cnki_definitions(
    existing_toml: str, headers: list[tuple[int, tuple[str, ...] | None]],
) -> None:
    header_index = 0
    active_table: tuple[str, ...] | None = None
    for assignment in _TOML_ASSIGNMENT.finditer(existing_toml):
        while header_index < len(headers) and headers[header_index][0] < assignment.start():
            active_table = headers[header_index][1]
            header_index += 1
        key_path = _toml_key_path(assignment.group("key"))
        full_path = (*active_table, *key_path) if active_table and key_path else key_path
        if _is_cnki_table(full_path) and not _is_cnki_table(active_table):
            raise ValueError(
                "unsupported dotted or inline mcp_servers.cnki-search definition; "
                "use [mcp_servers.cnki-search] table notation"
            )


def _toml_string(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Codex MCP 配置值必须是字符串")
    return json.dumps(value, ensure_ascii=False)


def _render_codex_server_config(server_config: Mapping[str, object]) -> str:
    command = _toml_string(server_config["command"])
    args = server_config["args"]
    env = server_config["env"]
    if not isinstance(args, list) or not isinstance(env, Mapping):
        raise ValueError("CNKI MCP 配置格式无效")
    rendered_args = ", ".join(_toml_string(argument) for argument in args)
    lines = [
        "[mcp_servers.cnki-search]",
        f"command = {command}",
        f"args = [{rendered_args}]",
        "",
        "[mcp_servers.cnki-search.env]",
    ]
    lines.extend(f"{key} = {_toml_string(value)}" for key, value in env.items())
    return "\n".join(lines) + "\n"


def merge_codex_config(existing_toml: str, server_config: Mapping[str, object]) -> str:
    if existing_toml.strip():
        tomllib.loads(existing_toml)
    headers = _toml_table_headers(existing_toml)
    _reject_unsupported_cnki_definitions(existing_toml, headers)
    retained: list[str] = []
    cursor = 0
    for index, (start, path) in enumerate(headers):
        if not _is_cnki_table(path):
            continue
        end = headers[index + 1][0] if index + 1 < len(headers) else len(existing_toml)
        if start < cursor:
            continue
        retained.append(existing_toml[cursor:start])
        cursor = end
    retained.append(existing_toml[cursor:])
    merged = "".join(retained)
    if merged and not merged.endswith(("\n", "\r")):
        merged += "\n"
    merged += _render_codex_server_config(server_config)
    tomllib.loads(merged)
    return merged


def _atomic_write_text(config_path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{config_path.name}.", suffix=".tmp", dir=config_path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, config_path)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="增量配置 CNKI MCP")
    commands = parser.add_subparsers(dest="command", required=True)
    merge = commands.add_parser("merge-claude")
    merge.add_argument("--config", type=Path, required=True)
    merge.add_argument("--skill-root", type=Path, required=True)
    merge.add_argument("--python", type=Path, required=True)
    codex = commands.add_parser("merge-codex")
    codex.add_argument("--config", type=Path, required=True)
    codex.add_argument("--skill-root", type=Path, required=True)
    codex.add_argument("--python", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path: Path = args.config
    if args.command == "merge-claude" and config_path.is_file():
        existing = json.loads(config_path.read_text(encoding="utf-8-sig"))
    else:
        existing = {}
    server_config = cnki_server_config(args.skill_root, args.python)
    if args.command == "merge-claude":
        merged = json.dumps(
            merge_claude_config(existing, server_config), ensure_ascii=False, indent=2
        ) + "\n"
    else:
        current = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
        merged = merge_codex_config(current, server_config)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(config_path, merged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
