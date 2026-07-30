from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from .browser import BrowserFactory, await_maybe, start_playwright
from .models import SearchStatus
from .search import PageContractChanged, PublicThemeSearchRunner, validate_public_theme_search_contract


CNKI_HOME_URL = "https://www.cnki.net/"
CNKI_RESULT_HOST = "kns.cnki.net"
CNKI_RESULT_PATH_PREFIX = "/kns8s/defaultresult/"
PUBLIC_RESULT_TABLE_MARKER = "result-table-list"


class TransientBrowserError(RuntimeError):
    pass


def _is_playwright_timeout(error: BaseException) -> bool:
    return isinstance(error, TimeoutError) or any(
        item.__name__ == "TimeoutError" and item.__module__.startswith("playwright.")
        for item in type(error).__mro__
    )


@dataclass(frozen=True, slots=True)
class SearchSnapshot:
    html: str
    url: str
    title: str
    visible_text: str
    http_status: int | None = None

    @property
    def has_result_table(self) -> bool:
        return PUBLIC_RESULT_TABLE_MARKER in self.html

    def state_arguments(self) -> dict[str, Any]:
        return {"url": self.url, "title": self.title, "visible_text": self.visible_text,
                "http_status": self.http_status, "has_result_table": self.has_result_table}


def classify_public_search_state(*, url: str, title: str, visible_text: str,
                                 http_status: int | None = None,
                                 has_result_table: bool = False) -> SearchStatus:
    parsed = urlparse(url)
    hostname, path = (parsed.hostname or "").casefold(), parsed.path.casefold()
    title_identity, visible_identity = title.casefold(), visible_text.casefold()
    if http_status in {401, 403}:
        return SearchStatus.FORBIDDEN
    if http_status == 429:
        return SearchStatus.RATE_LIMITED
    if http_status is not None and 500 <= http_status <= 599:
        return SearchStatus.NETWORK_ERROR
    if "/verify/" in path or "captcha" in path or any(token in title_identity for token in ("验证码", "安全验证", "拼图验证")):
        return SearchStatus.CHALLENGE_DETECTED
    if hostname == "login.cnki.net" or "authserver" in path:
        return SearchStatus.LOGIN_REQUIRED
    if hostname == CNKI_RESULT_HOST and path.startswith(CNKI_RESULT_PATH_PREFIX) and has_result_table:
        return SearchStatus.SUCCESS
    if not has_result_table:
        if "未检索到相关文献" in visible_text:
            return SearchStatus.NO_RESULTS
        if any(token in visible_identity for token in ("401 unauthorized", "403 forbidden", "无权访问", "拒绝访问")):
            return SearchStatus.FORBIDDEN
        if any(token in visible_identity for token in ("429 too many requests", "访问过于频繁", "操作频繁")):
            return SearchStatus.RATE_LIMITED
        if any(token in visible_identity for token in ("用户登录", "统一身份认证")):
            return SearchStatus.LOGIN_REQUIRED
    return SearchStatus.PAGE_CONTRACT_CHANGED


class PublicCnkiSession:
    def __init__(self, browser_factory: BrowserFactory | None = None) -> None:
        self._playwright: Any = None
        self._browser_factory = browser_factory
        self.browser: Any = None
        self.context: Any = None
        self.page: Any = None
        self._home_response_status: int | None = None

    async def __aenter__(self) -> "PublicCnkiSession":
        try:
            if self._browser_factory is None:
                self._playwright = await start_playwright()
                self._browser_factory = BrowserFactory(self._playwright)
            self.browser = await await_maybe(self._browser_factory.launch_ephemeral())
            self.context = await await_maybe(self.browser.new_context(locale="zh-CN", accept_downloads=False))
            self.page = await await_maybe(self.context.new_page())
            response = await await_maybe(self.page.goto(CNKI_HOME_URL, wait_until="domcontentloaded"))
            self._home_response_status = getattr(response, "status", None)
            return self
        except BaseException as exc:
            await self._close_resources()
            if _is_playwright_timeout(exc):
                raise TransientBrowserError("知网公开首页访问超时") from exc
            raise

    async def search(self, query: str) -> SearchSnapshot:
        try:
            if self.page is None:
                raise RuntimeError("公开检索会话未启动")
            body = await await_maybe(self.page.locator("body").inner_text(timeout=10_000))
            initial = SearchSnapshot(await await_maybe(self.page.content()), self.page.url,
                                     await await_maybe(self.page.title()), body, self._home_response_status)
            if classify_public_search_state(**initial.state_arguments()) in {
                SearchStatus.CHALLENGE_DETECTED, SearchStatus.LOGIN_REQUIRED, SearchStatus.FORBIDDEN,
                SearchStatus.RATE_LIMITED, SearchStatus.NETWORK_ERROR, SearchStatus.NO_RESULTS,
            }:
                return initial
            if self.page.url != CNKI_HOME_URL:
                raise PageContractChanged("知网公开首页未就绪")
            await validate_public_theme_search_contract(self.page)
            try:
                http_status = await PublicThemeSearchRunner().run(self.page, query)
            except PageContractChanged:
                # 结果契约未出现有两种成因，补救方式相反：页面结构变化要改解析器，
                # 而安全验证/登录/限流必须立即停手。此前只对首页快照分类，
                # 检索后的页面从不分类，风控页因此被误报成 page_contract_changed。
                blocked = await self._blocking_snapshot()
                if blocked is not None:
                    return blocked
                raise
            body = await await_maybe(self.page.locator("body").inner_text(timeout=10_000))
            return SearchSnapshot(await await_maybe(self.page.content()), self.page.url,
                                  await await_maybe(self.page.title()), body, http_status)
        except BaseException as exc:
            if _is_playwright_timeout(exc):
                raise TransientBrowserError("知网公开检索超时") from exc
            raise

    #: 检索提交后可据以判定"站点主动阻断"的状态；命中任一项都应如实上报，
    #: 而不是笼统归为页面结构变化。
    BLOCKING_STATES = frozenset({
        SearchStatus.CHALLENGE_DETECTED, SearchStatus.LOGIN_REQUIRED,
        SearchStatus.FORBIDDEN, SearchStatus.RATE_LIMITED, SearchStatus.NETWORK_ERROR,
    })

    async def _blocking_snapshot(self) -> SearchSnapshot | None:
        """对当前页面分类；仅当命中阻断状态时返回快照，否则返回 None。"""
        try:
            body = await await_maybe(self.page.locator("body").inner_text(timeout=10_000))
            snapshot = SearchSnapshot(await await_maybe(self.page.content()), self.page.url,
                                      await await_maybe(self.page.title()), body)
        except Exception:
            return None
        if classify_public_search_state(**snapshot.state_arguments()) in self.BLOCKING_STATES:
            return snapshot
        return None

    async def __aexit__(self, *_exc: object) -> None:
        await self._close_resources()

    async def _close_resources(self) -> None:
        for resource, method in ((self.page, "close"), (self.context, "close"),
                                 (self.browser, "close"), (self._playwright, "stop")):
            if resource is not None:
                try:
                    await await_maybe(getattr(resource, method)())
                except Exception:
                    pass
        self.context = self.browser = self.page = None
        self._home_response_status = None
        self._playwright = None
