from __future__ import annotations

import copy
import argparse
import json
import re
import sys
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


# 必须同时识别普通表 [a.b] 与数组表 [[a.b]]：数组表虽然永远不是 cnki 表，
# 但它**必须**构成删除区间的边界，否则删除范围会越过它一路吃到下一个普通
# 表头，把用户的 [[mcp_servers.custom.headers]]（含 API 密钥）一并删掉。
_TOML_TABLE_HEADER = re.compile(
    r"(?m)^[\t ]*(?P<array>\[?)\[(?P<path>[^\]\r\n]+)\]\]?[\t ]*(?:#.*)?(?:\r?\n|$)"
)


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


def _existing_cnki_definition_is_replaceable(existing_toml: str) -> None:
    """cnki 配置若以点分键或内联表定义，逐表头替换无法覆盖，必须明确报错。"""
    try:
        parsed = tomllib.loads(existing_toml)
    except tomllib.TOMLDecodeError:
        return  # 原文本身不合法，交由后续 tomllib.loads(merged) 统一报错
    servers = parsed.get("mcp_servers")
    if not isinstance(servers, Mapping) or "cnki-search" not in servers:
        return
    if not _TOML_TABLE_HEADER.search(existing_toml) or not any(
        _is_cnki_table(_toml_key_path(match.group("path")))
        for match in _TOML_TABLE_HEADER.finditer(existing_toml)
    ):
        raise ValueError(
            "现有配置以点分键或内联表定义了 mcp_servers.cnki-search，"
            "安装器无法安全替换。请手工删除该条目后重试。"
        )


def merge_codex_config(existing_toml: str, server_config: Mapping[str, object]) -> str:
    _existing_cnki_definition_is_replaceable(existing_toml)
    headers = [
        (match.start(), _toml_key_path(match.group("path")), bool(match.group("array")))
        for match in _TOML_TABLE_HEADER.finditer(existing_toml)
    ]
    retained: list[str] = []
    cursor = 0
    for index, (start, path, is_array) in enumerate(headers):
        # 数组表永远不是 cnki 表，但上面已让它参与 headers，从而正确充当边界
        if is_array or not _is_cnki_table(path):
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
    temporary = config_path.with_name(f"{config_path.name}.tmp")
    temporary.write_text(merged, encoding="utf-8")
    temporary.replace(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
