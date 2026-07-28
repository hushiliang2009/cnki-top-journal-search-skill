from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated, Any

from pydantic import Field

from . import __version__
from .browser import BrowserUnavailableError
from .models import MAX_RESULTS_PER_PAGE
from .professional_runtime import build_professional_runtime_from_env
from .professional_service import CHINESE_TOP_GROUP, SUPPORTED_GROUPS
from .service import CnkiPublicSearchService
from .webvpn import (
    ExpressionTruncated,
    WebVpnLoginTimeout,
    WebVpnNavigationError,
    WebVpnWindowClosed,
)

REQUIRED_TOOLS = ["cnki_search", "cnki_professional_search"]
MIN_LIMIT = 1
#: 公开匿名模式只读结果页默认呈现的一页，从不去点「显示」档位控件，因此实际
#: 永远只有 20 行。把上限写成 50 会让调用方以为结果被截断——上限必须反映
#: 该模式真正能拿到的条数。
MAX_LIMIT = 20
#: 专业检索模式会主动把档位切到 50（2026-07-28 实机验证：切换后确实渲染 50 行）。
#: 50 是站点档位上限，没有更大的选项。
MAX_PROFESSIONAL_LIMIT = MAX_RESULTS_PER_PAGE

#: WebVPN 人工值守模式必须显式启用：设置本环境变量为所在机构 WebVPN 改写后的
#: 知网首页地址。未设置时工具返回配置错误而不是擅自拉起浏览器——该模式会打开
#: 可见窗口并要求人工登录，绝不能在调用方毫无预期时发生。
WEBVPN_HOME_ENV = "CNKI_WEBVPN_HOME"

_WEBVPN_DISABLED_HINT = (
    f"WebVPN 专业检索未启用：请将环境变量 {WEBVPN_HOME_ENV} 设为所在机构 WebVPN "
    "改写后的知网首页地址。该模式需要本人登录并全程保持浏览器窗口打开，"
    "不可用于定时任务。"
)

def webvpn_enabled() -> bool:
    return bool((os.environ.get(WEBVPN_HOME_ENV) or "").strip())


def _configuration_error(message: str) -> dict[str, Any]:
    return _professional_error("configuration_error", message)


def _professional_error(status: str, message: str) -> dict[str, Any]:
    return {"ok": False, "mode": "webvpn", "status": status,
            "human_intervention_required": True, "records": [],
            "incomplete_records": [], "detail": message}


class CnkiMcpServer:
    def __init__(self, service: CnkiPublicSearchService | None = None, *,
                 professional_factory: Any = None) -> None:
        self.service = service or CnkiPublicSearchService()
        # 惰性构造：WebVPN 会话会打开可见浏览器窗口并等待人工登录，
        # 绝不能在 MCP 服务器启动时就发生。
        self._professional_factory = professional_factory
        self._professional: Any = None
        self._tasks: set[asyncio.Task[Any]] = set()
        self._shutdown = False

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    async def cnki_search(self, query: str, limit: int = MAX_LIMIT) -> dict[str, Any]:
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

    async def cnki_professional_search(
        self, topic: str, group: str = CHINESE_TOP_GROUP,
        limit: int = MAX_PROFESSIONAL_LIMIT,
        year_from: int | None = None, year_to: int | None = None,
    ) -> dict[str, Any]:
        if self._shutdown:
            raise RuntimeError("CNKI MCP server has been shut down")
        if self._professional_factory is None and not webvpn_enabled():
            return _configuration_error(_WEBVPN_DISABLED_HINT)
        if group not in SUPPORTED_GROUPS:
            return _configuration_error(
                f"CNKI 专业检索只覆盖中文层级 {SUPPORTED_GROUPS}；{group!r} 应改用 ai4scholar。"
            )
        task = asyncio.current_task()
        if task is not None:
            self._tasks.add(task)
        try:
            service = await self._ensure_professional()
            return await service.search_group(topic, group, limit=limit,
                                              year_from=year_from, year_to=year_to)
        except asyncio.CancelledError:
            raise
        except (BrowserUnavailableError, ValueError) as exc:
            return _configuration_error(str(exc))
        except (WebVpnLoginTimeout, WebVpnWindowClosed) as exc:
            return _professional_error("login_required", str(exc))
        except (WebVpnNavigationError, ExpressionTruncated) as exc:
            return _professional_error("page_contract_changed", str(exc))
        finally:
            if task is not None:
                self._tasks.discard(task)

    async def _ensure_professional(self) -> Any:
        """首次调用时建立 WebVPN 会话，之后复用。

        票据不能跨进程复用，会话必须在同一进程内保持存活，因此这里缓存实例，
        而不是每次调用都重新登录。
        """
        if self._professional is None:
            factory = (
                self._professional_factory or build_professional_runtime_from_env
            )
            self._professional = await factory()
        return self._professional

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

    async def aclose(self) -> None:
        self.shutdown()
        pending = [task for task in self._tasks if not task.done()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        if self._professional is not None:
            await self._professional.aclose()
            self._professional = None

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP

            @asynccontextmanager
            async def lifespan(_app: Any):
                try:
                    yield {}
                finally:
                    await self.aclose()

            mcp = FastMCP("CNKI Public Search", lifespan=lifespan)
        else:
            mcp = fastmcp_class("CNKI Public Search")
        lowlevel = getattr(mcp, "_mcp_server", None)
        if lowlevel is not None:
            lowlevel.version = __version__

        async def cnki_search(
            query: Annotated[str, Field(min_length=1, pattern=r".*\S.*")],
            limit: Annotated[int, Field(ge=MIN_LIMIT, le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> dict[str, Any]:
            return await self.cnki_search(query, limit)

        mcp.tool(name="cnki_search", description="从中国知网公开首页执行固定主题检索，并标注第一页期刊论文。")(cnki_search)

        async def cnki_professional_search(
            topic: Annotated[str, Field(min_length=1, pattern=r".*\S.*")],
            group: Annotated[str, Field(pattern=r"^(chinese_top_journals|cssci)$")] = CHINESE_TOP_GROUP,
            limit: Annotated[int, Field(ge=MIN_LIMIT, le=MAX_PROFESSIONAL_LIMIT)] = MAX_PROFESSIONAL_LIMIT,
            year_from: Annotated[
                int | None, Field(ge=1900, le=date.today().year + 1)
            ] = None,
            year_to: Annotated[
                int | None, Field(ge=1900, le=date.today().year + 1)
            ] = None,
        ) -> dict[str, Any]:
            return await self.cnki_professional_search(topic, group, limit, year_from, year_to)

        mcp.tool(
            name="cnki_professional_search",
            description=(
                "经机构 WebVPN 以专业检索按期刊清单定向检索中文期刊论文，"
                "只覆盖中文顶尖期刊（13 本）与 CSSCI（含扩展版）。"
                "需要本人登录并全程保持浏览器窗口打开，中途可能需人工完成安全验证；"
                "不可用于定时任务。未设置环境变量 CNKI_WEBVPN_HOME 时返回配置错误。"
            ),
        )(cnki_professional_search)
        return mcp

def main() -> None:
    server = CnkiMcpServer()
    try:
        server.build_fastmcp().run(transport="stdio")
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()
