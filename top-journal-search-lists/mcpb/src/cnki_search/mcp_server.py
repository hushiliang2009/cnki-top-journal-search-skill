from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from typing import Any, Callable

from . import __version__
from .service import CnkiPublicSearchService


REQUIRED_TOOLS = ["cnki_search"]


class CnkiMcpServer:
    def __init__(self, service: CnkiPublicSearchService | None = None) -> None:
        self.service = service or CnkiPublicSearchService()
        self._tool_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="cnki-public")
        self._shutdown = False

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    def cnki_search(self, query: str, limit: int = 20) -> dict[str, Any]:
        return self.service.search(query, limit).to_dict()

    def _async_tool(self, function: Callable[..., dict[str, Any]]) -> Callable[..., Any]:
        @wraps(function)
        async def invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(self._tool_executor, partial(function, *args, **kwargs))

        return invoke

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        try:
            self._tool_executor.submit(lambda: None).result()
        finally:
            self._tool_executor.shutdown(wait=True)

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP

            fastmcp_class = FastMCP
        mcp = fastmcp_class("CNKI Public Search")
        mcp._mcp_server.version = __version__
        mcp.tool(
            name="cnki_search",
            description="从中国知网公开首页执行固定主题检索，并按主期刊目录标注第一页期刊论文。",
        )(self._async_tool(self.cnki_search))
        return mcp


def main() -> None:
    server = CnkiMcpServer()
    try:
        server.build_fastmcp().run(transport="stdio")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
