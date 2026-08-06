from __future__ import annotations

import copy
import argparse
import json
import os
import re
import sys
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


#: 使用者可以自行设置、升级时必须原样留下的 env 键。
#:
#: 这里刻意用白名单而非"凡非安装器所写皆保留"。既有安全约定是整条 cnki 表
#: 被完整替换，好让陈旧值（可能含密钥）不残留；黑名单会把这个性质一并破坏。
#: 白名单只放行文档写明由使用者设置的变量，其余陈旧键照旧清除。
#:
#: CNKI_WEBVPN_HOME 由 WebVPN 人工值守模式要求使用者手工设置。此前每次重装
#: 都会把它抹掉，专业检索退回配置错误，而安装器并不提示自己删了什么。
_PRESERVED_ENV_KEYS = ("CNKI_WEBVPN_HOME",)


def _merged_server_entry(
    existing_entry: object, server_config: Mapping[str, object]
) -> dict[str, object]:
    """以新配置为准，并把 _PRESERVED_ENV_KEYS 中的旧值带过来。"""
    merged = copy.deepcopy(dict(server_config))
    if not isinstance(existing_entry, Mapping):
        return merged

    previous_env = existing_entry.get("env")
    if not isinstance(previous_env, Mapping):
        return merged

    carried = {
        key: copy.deepcopy(previous_env[key])
        for key in _PRESERVED_ENV_KEYS
        if key in previous_env
    }
    if not carried:
        return merged

    new_env = merged.get("env")
    if not isinstance(new_env, dict):
        new_env = {}
        merged["env"] = new_env
    for key, value in carried.items():
        new_env.setdefault(key, value)
    return merged


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
    servers["cnki-search"] = _merged_server_entry(servers.get("cnki-search"), server_config)
    return result


# 必须同时识别普通表 [a.b] 与数组表 [[a.b]]：数组表虽然永远不是 cnki 表，
# 但它**必须**构成删除区间的边界，否则删除范围会越过它一路吃到下一个普通
# 表头，把用户的 [[mcp_servers.custom.headers]]（含 API 密钥）一并删掉。
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


def _inline_table_end(existing_toml: str, start: int) -> tuple[int, int] | None:
    while start < len(existing_toml) and existing_toml[start] in " \t":
        start += 1
    if start >= len(existing_toml) or existing_toml[start] != "{":
        return None
    depth = 0
    quote: str | None = None
    index = start
    while index < len(existing_toml):
        character = existing_toml[index]
        if quote:
            if quote == '"' and character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return start, index
        index += 1
    return None


def _root_inline_mcp_servers_table(
    existing_toml: str, headers: list[tuple[int, tuple[str, ...] | None]],
) -> tuple[int, int] | None:
    header_index = 0
    active_table: tuple[str, ...] | None = None
    for assignment in _TOML_ASSIGNMENT.finditer(existing_toml):
        while header_index < len(headers) and headers[header_index][0] < assignment.start():
            active_table = headers[header_index][1]
            header_index += 1
        if active_table is None and _toml_key_path(assignment.group("key")) == ("mcp_servers",):
            return _inline_table_end(existing_toml, assignment.end())
    return None


def _reject_unsupported_cnki_definitions(
    existing_toml: str,
    headers: list[tuple[int, tuple[str, ...] | None]],
    parsed_config: Mapping[str, object],
    root_inline_table: tuple[int, int] | None,
) -> None:
    if root_inline_table:
        servers = parsed_config.get("mcp_servers")
        if isinstance(servers, Mapping) and "cnki-search" in servers:
            raise ValueError(
                "现有配置以点分键或内联表定义了 mcp_servers.cnki-search，"
                "安装器无法安全替换。请手工删除该条目后重试。"
            )
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
                "现有配置以点分键或内联表定义了 mcp_servers.cnki-search，"
                "安装器无法安全替换。请手工删除该条目后重试。"
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


def _render_codex_server_inline_entry(server_config: Mapping[str, object]) -> str:
    command = _toml_string(server_config["command"])
    args = server_config["args"]
    env = server_config["env"]
    if not isinstance(args, list) or not isinstance(env, Mapping):
        raise ValueError("CNKI MCP 配置格式无效")
    rendered_args = ", ".join(_toml_string(argument) for argument in args)
    rendered_env = ", ".join(
        f"{_toml_string(key)} = {_toml_string(value)}" for key, value in env.items()
    )
    return (
        f'"cnki-search" = {{ command = {command}, args = [{rendered_args}], '
        f"env = {{ {rendered_env} }} }}"
    )


def merge_codex_config(existing_toml: str, server_config: Mapping[str, object]) -> str:
    parsed_config = tomllib.loads(existing_toml) if existing_toml.strip() else {}
    headers = _toml_table_headers(existing_toml)
    root_inline_table = _root_inline_mcp_servers_table(existing_toml, headers)
    _reject_unsupported_cnki_definitions(
        existing_toml, headers, parsed_config, root_inline_table
    )
    # 这条路径靠删表重渲染实现覆盖，使用者自加的 env 键会随旧表一起消失。
    # 先从解析结果里取回，再交给渲染函数。
    previous_entry = parsed_config.get("mcp_servers", {})
    if isinstance(previous_entry, Mapping):
        previous_entry = previous_entry.get("cnki-search")
    else:
        previous_entry = None
    server_config = _merged_server_entry(previous_entry, server_config)
    if root_inline_table:
        _, end = root_inline_table
        separator = ", " if existing_toml[root_inline_table[0] + 1 : end].strip() else ""
        merged = (
            existing_toml[:end]
            + separator
            + _render_codex_server_inline_entry(server_config)
            + existing_toml[end:]
        )
        tomllib.loads(merged)
        return merged
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
    try:
        return _run(build_parser().parse_args(argv))
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        # 不抛裸 traceback：安装器用 set -e / $ErrorActionPreference='Stop'，
        # 需要一个可读的中文原因和非零退出码。
        print(f"配置合并失败：{exc}", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace) -> int:
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
