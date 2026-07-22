from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import hashlib
from pathlib import Path
from typing import Any, Callable

from .details import PlaywrightResultNavigator, parse_detail_page
from .downloads import DownloadRunner, PlaywrightDownloadDriver
from .exporters import attach_journal_levels, deduplicate_records, export_records
from .models import SearchMode, SearchRequest, SessionStatus, ToolResponse
from .rate_limit import SerialRateLimiter
from .results import parse_result_page
from .search import AdvancedSearchRunner, PlaywrightPageDriver, ProfessionalSearchRunner
from .session import CnkiSession, classify_public_state


REQUIRED_TOOLS = [
    "cnki_status",
    "cnki_login",
    "cnki_search",
    "cnki_fetch_details",
    "cnki_export",
    "cnki_download",
    "cnki_close_session",
]


class CnkiMcpServer:
    def __init__(
        self,
        session: CnkiSession | None = None,
        detail_navigator: PlaywrightResultNavigator | None = None,
    ) -> None:
        self.session = session or CnkiSession()
        self.detail_navigator = detail_navigator or PlaywrightResultNavigator()
        self.records: list[Any] = []
        self.limiter = SerialRateLimiter()
        self._tool_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="cnki-mcp")

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    def _ready(self) -> ToolResponse | None:
        status = self.session.status()
        if status is SessionStatus.READY:
            return None
        return ToolResponse.failure(
            status,
            "知网会话尚未就绪",
            next_action="请调用 cnki_login，并在可见浏览器中手工完成登录或验证。",
        )

    def cnki_status(self) -> dict[str, Any]:
        status = self.session.status()
        message = "知网会话可用" if status is SessionStatus.READY else "知网会话尚未建立"
        return ToolResponse(ok=True, status=status, message=message).to_dict()

    def cnki_login(self) -> dict[str, Any]:
        status = self.session.login()
        return ToolResponse(
            ok=True,
            status=status,
            message="已打开河海大学 WebVPN 登录页，请在可见浏览器中手工登录。",
            next_action="登录完成后调用 cnki_status；不要向工具传递账号、密码或验证码。",
        ).to_dict()

    def cnki_search(
        self,
        query: str,
        mode: str = "advanced",
        pages: int = 1,
        fields: list[dict[str, Any]] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        blocked = self._ready()
        if blocked:
            return blocked.to_dict()
        try:
            request = SearchRequest(
                mode=SearchMode(mode), query=query, pages=pages,
                fields=fields or [], filters=filters or {},
            )
            search_page_status = self.session.open_search()
            if search_page_status is not SessionStatus.READY:
                return ToolResponse.failure(
                    search_page_status,
                    "知网新版检索页面尚未就绪",
                    next_action="请在可见浏览器中手工完成登录或验证。",
                ).to_dict()
            driver = PlaywrightPageDriver(self.session.page)
            driver.assert_new_search_page()
            if request.mode is SearchMode.PROFESSIONAL:
                ProfessionalSearchRunner().run(driver, query)
            else:
                AdvancedSearchRunner().run(driver, request)
            self.session.page.wait_for_load_state("domcontentloaded")
            result_page_status = self.session.status()
            if result_page_status is not SessionStatus.READY:
                return ToolResponse.failure(
                    result_page_status,
                    "知网检索结果页面尚未就绪",
                    next_action="请在可见浏览器中手工完成登录或验证。",
                ).to_dict()
            found = parse_result_page(self.session.page.content(), base_url=self.session.page.url)
            for _ in range(1, request.pages):
                self.limiter.wait("search_page")
                self.session.page.get_by_text("下一页", exact=True).click()
                self.session.page.wait_for_load_state("domcontentloaded")
                result_page_status = self.session.status()
                if result_page_status is not SessionStatus.READY:
                    return ToolResponse.failure(
                        result_page_status,
                        "知网检索结果页面尚未就绪",
                        next_action="请在可见浏览器中手工完成登录或验证。",
                    ).to_dict()
                found.extend(parse_result_page(self.session.page.content(), base_url=self.session.page.url))
            self.records = attach_journal_levels(deduplicate_records(found))
            return ToolResponse.success(
                SessionStatus.READY, [record.to_dict() for record in self.records]
            ).to_dict()
        except (ValueError, RuntimeError) as exc:
            return ToolResponse.failure(self.session.status(), str(exc)).to_dict()

    def cnki_fetch_details(self, selected_indices: list[int]) -> dict[str, Any]:
        blocked = self._ready()
        if blocked:
            return blocked.to_dict()
        try:
            self.limiter.validate_count("detail", len(selected_indices))
            if any(index < 1 or index > len(self.records) for index in selected_indices):
                raise IndexError("详情序号超出检索结果范围")
            selected = []
            for position, index in enumerate(selected_indices):
                if position:
                    self.limiter.wait("detail")
                detail_page = self.detail_navigator.open_selected(self.session.page, index)
                try:
                    status = classify_public_state(
                        url=detail_page.url,
                        title=detail_page.title(),
                        visible_text=detail_page.locator("body").inner_text(timeout=5_000),
                    )
                    enriched = (
                        parse_detail_page(detail_page.content(), self.records[index - 1])
                        if status is SessionStatus.READY
                        else None
                    )
                finally:
                    detail_page.close()
                if status is not SessionStatus.READY:
                    return ToolResponse.failure(
                        status,
                        "详情页未就绪，已停止后续访问",
                        next_action="请在可见浏览器中手工完成登录或验证。",
                    ).to_dict()
                self.records[index - 1] = enriched
                selected.append(enriched)
            return ToolResponse.success(
                SessionStatus.READY, [record.to_dict() for record in selected]
            ).to_dict()
        except (IndexError, ValueError) as exc:
            return ToolResponse.failure(SessionStatus.READY, str(exc)).to_dict()

    def cnki_export(self, output_dir: str, stem: str = "cnki-results") -> dict[str, Any]:
        paths = export_records(self.records, Path(output_dir), stem=stem)
        return ToolResponse.success(
            self.session.status(), {name: str(path) for name, path in paths.items()}
        ).to_dict()

    def cnki_download(
        self,
        selected_indices: list[int],
        output_dir: str,
        access_confirmed: bool = False,
    ) -> dict[str, Any]:
        if not access_confirmed:
            return ToolResponse.failure(
                SessionStatus.PERMISSION_DENIED,
                "下载前必须由用户确认具有相应访问权限",
            ).to_dict()
        blocked = self._ready()
        if blocked:
            return blocked.to_dict()
        try:
            driver = PlaywrightDownloadDriver(self.session.page)
            paths = DownloadRunner(driver).download_selected(
                self.records, selected_indices=selected_indices, output_dir=Path(output_dir)
            )
            return ToolResponse.success(
                SessionStatus.READY,
                [
                    {
                        "path": str(path),
                        "size_bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                    for path in paths
                ],
            ).to_dict()
        except (IndexError, ValueError, RuntimeError) as exc:
            return ToolResponse.failure(self.session.status(), str(exc)).to_dict()

    def cnki_close_session(self) -> dict[str, Any]:
        status = self.session.close()
        return ToolResponse(ok=True, status=status, message="知网浏览器会话已关闭").to_dict()

    def _async_tool(self, function: Callable[..., dict[str, Any]]) -> Callable[..., Any]:
        async def invoke(*args: Any, **kwargs: Any) -> dict[str, Any]:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._tool_executor, partial(function, *args, **kwargs)
            )

        return invoke

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP

            fastmcp_class = FastMCP
        mcp = fastmcp_class("CNKI Search")
        descriptions = {
            "cnki_status": "检查本地知网浏览器会话，不自动打开网页。",
            "cnki_login": "打开可见的河海大学 WebVPN 登录页，等待用户手工登录。",
            "cnki_search": "在可见页面执行知网高级检索或专业检索。",
            "cnki_fetch_details": "串行访问用户选择的最多十条详情页。",
            "cnki_export": "把当前结果导出为 JSON、CSV、BibTeX、RIS 和 GB/T 7714。",
            "cnki_download": "经用户选择后从知网官方按钮串行下载最多五篇。",
            "cnki_close_session": "关闭浏览器并清除内存会话。",
        }
        for name in REQUIRED_TOOLS:
            function: Callable[..., dict[str, Any]] = getattr(self, name)
            mcp.tool(name=name, description=descriptions[name])(self._async_tool(function))
        return mcp


def main() -> None:
    CnkiMcpServer().build_fastmcp().run(transport="stdio")


if __name__ == "__main__":
    main()
