from __future__ import annotations

import asyncio
from typing import Annotated, Any

from pydantic import Field

from . import __version__
from .service import CnkiPublicSearchService

REQUIRED_TOOLS = ["cnki_search_env"]
MIN_LIMIT = 1
MAX_LIMIT = 20

class CnkiMcpServer:
    def __init__(self, service: CnkiPublicSearchService | None = None) -> None:
        self.service = service or CnkiPublicSearchService()
        self._tasks: set[asyncio.Task[Any]] = set()
        self._shutdown = False

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    async def cnki_search_env(self, query: str, limit: int = MAX_LIMIT) -> dict[str, Any]:
        if self._shutdown:
            raise RuntimeError("CNKI MCP server has been shut down")
        task = asyncio.current_task()
        if task is not None:
            self._tasks.add(task)
        try:
            return (await self.service.search(query, limit)).to_dict()
        finally:
            if task is not None:
                self._tasks.discard(task)

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        try:
            current = asyncio.current_task()
        except RuntimeError:
            current = None
        for task in tuple(self._tasks):
            if task is not current and not task.done():
                task.cancel()

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP
            fastmcp_class = FastMCP
        mcp = fastmcp_class("CNKI Environmental Public Search")
        lowlevel = getattr(mcp, "_mcp_server", None)
        if lowlevel is not None:
            lowlevel.version = __version__

        async def cnki_search_env(
            query: Annotated[str, Field(min_length=1, pattern=r".*\S.*")],
            limit: Annotated[int, Field(ge=MIN_LIMIT, le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> dict[str, Any]:
            return await self.cnki_search_env(query, limit)

        mcp.tool(
            name="cnki_search_env",
            description="从中国知网公开首页执行固定主题检索，并按环境期刊目录标注第一页期刊论文。",
        )(cnki_search_env)
        return mcp

def main() -> None:
    server = CnkiMcpServer()
    try:
        server.build_fastmcp().run(transport="stdio")
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()
