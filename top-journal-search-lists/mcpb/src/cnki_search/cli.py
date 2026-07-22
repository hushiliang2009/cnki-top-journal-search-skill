from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .mcp_server import CnkiMcpServer


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CNKI 可见浏览器检索工具")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="检查会话状态，不打开浏览器")
    commands.add_parser("login", help="打开 WebVPN 页面并等待手工登录")
    search = commands.add_parser("search", help="执行高级检索或专业检索")
    search.add_argument("query")
    search.add_argument("--mode", choices=("advanced", "professional"), default="advanced")
    search.add_argument("--pages", type=int, default=1)
    commands.add_parser("close", help="关闭并清理内存会话")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    if argv is not None and "--help" in argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    server = CnkiMcpServer()
    if args.command == "status":
        response = server.cnki_status()
    elif args.command == "login":
        response = server.cnki_login()
    elif args.command == "search":
        response = server.cnki_search(args.query, mode=args.mode, pages=args.pages)
    else:
        response = server.cnki_close_session()
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
