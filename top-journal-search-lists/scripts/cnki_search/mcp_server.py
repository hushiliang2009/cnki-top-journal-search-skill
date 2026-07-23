from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from typing import Annotated, Any, Callable

# 必须是模块级导入：本模块用了 from __future__ import annotations，注解是字符串，
# FastMCP 以 inspect.signature(..., eval_str=True) 解析，Field 需在模块全局可解析。
# pydantic 是 mcp 的硬依赖，安装器装了 mcp 就一定有它。
from pydantic import Field

from . import __version__
from .service import CnkiPublicSearchService


REQUIRED_TOOLS = ["cnki_search"]
MIN_LIMIT = 1
MAX_LIMIT = 20


class CnkiMcpServer:
    def __init__(self, service: CnkiPublicSearchService | None = None) -> None:
        self.service = service or CnkiPublicSearchService()
        self._tool_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="cnki-public")
        self._shutdown = False

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    def cnki_search(self, query: str, limit: int = MAX_LIMIT) -> dict[str, Any]:
        return self.service.search(query, limit).to_dict()

    def _async_tool(self, function: Callable[..., dict[str, Any]]) -> Callable[..., Any]:
        @wraps(function)
        async def invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(self._tool_executor, partial(function, *args, **kwargs))
            try:
                return await asyncio.shield(future)
            except asyncio.CancelledError:
                # 单线程池上的任务无法中途抢占，但至少不要让已取消的调用
                # 继续占着协程；后台任务结束后由 shutdown 回收。
                future.cancel()
                raise

        return invoke

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        # 原实现先 submit 一个空任务并 .result() 等待，若队列里排着一个
        # 6 秒限速的检索，shutdown 会被无谓地阻塞。直接取消未开始的任务。
        self._tool_executor.shutdown(wait=True, cancel_futures=True)

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP

            fastmcp_class = FastMCP
        mcp = fastmcp_class("CNKI Public Search")
        # 通告产品版本：底层 Server.version 为空时会回落到 mcp 包自身的版本，
        # 于是 serverInfo 报的是 SDK 版本而不是本工具版本。
        lowlevel = getattr(mcp, "_mcp_server", None)
        if lowlevel is not None:
            lowlevel.version = __version__

        # limit 的 1–20 范围此前只写在文档里，机器无法执行。用带约束的注解
        # 让 tools/list 的 inputSchema 输出 minimum / maximum。
        async def cnki_search(
            query: Annotated[str, Field(min_length=1, pattern=r".*\S.*")],
            limit: Annotated[int, Field(ge=MIN_LIMIT, le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> dict[str, Any]:
            return await self._async_tool(self.cnki_search)(query, limit)

        mcp.tool(
            name="cnki_search",
            description="从中国知网公开首页执行固定主题检索，并按主期刊目录标注第一页期刊论文。",
        )(cnki_search)
        return mcp


def main() -> None:
    server = CnkiMcpServer()
    try:
        server.build_fastmcp().run(transport="stdio")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
