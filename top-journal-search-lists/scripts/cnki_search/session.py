from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from .browser import BrowserFactory, start_playwright
from .models import SearchStatus
from .search import PageContractChanged, PublicThemeSearchRunner, validate_public_theme_search_contract


CNKI_HOME_URL = "https://www.cnki.net/"
CNKI_RESULT_HOST = "kns.cnki.net"
CNKI_RESULT_PATH_PREFIX = "/kns8s/defaultresult/"


class TransientBrowserError(RuntimeError):
    """可安全重试一次的公开浏览器访问失败。"""


def _is_playwright_timeout(error: BaseException) -> bool:
    return any(
        item.__name__ == "TimeoutError" and item.__module__.startswith("playwright.")
        for item in type(error).__mro__
    )


PUBLIC_RESULT_TABLE_MARKER = "result-table-list"


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
        return {
            "url": self.url,
            "title": self.title,
            "visible_text": self.visible_text,
            "http_status": self.http_status,
            "has_result_table": self.has_result_table,
        }


def classify_public_search_state(
    *, url: str, title: str, visible_text: str, http_status: int | None = None,
    has_result_table: bool = False,
) -> SearchStatus:
    """依据结构化信号判定页面状态。

    判定依据必须收窄到 URL、<title>、HTTP 状态码和结果表是否存在——
    visible_text 是整页 body.inner_text()，包含全部结果的**论文标题**。
    若拿它做全文子串匹配，一次成功的检索会因某篇论文标题含"无权访问"
    "访问过于频繁""用户登录"等词而被误判为受限，返回零题录且无任何提示。
    """
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").casefold()
    path_identity = parsed.path.casefold()
    url_identity = f"{hostname}{path_identity}{parsed.query}".casefold()
    title_identity = title.casefold()
    visible_identity = visible_text.casefold()
    # 结果表存在即说明检索已成功返回题录，此时正文里的受限措辞只可能来自
    # 论文标题本身，不得参与判定。
    body_signals_apply = not has_result_table

    if http_status in {401, 403}:
        return SearchStatus.FORBIDDEN
    if http_status == 429:
        return SearchStatus.RATE_LIMITED
    if http_status is not None and 500 <= http_status <= 599:
        return SearchStatus.NETWORK_ERROR
    # 挑战页只认 URL 路径与标题：实测真实挑战页落在 /verify/home、
    # 标题为"安全验证"，且正文可见文本为 0 字符。
    if "captcha" in url_identity or "/verify/" in path_identity or any(
        token in title_identity for token in ("验证码", "安全验证", "拼图验证")
    ):
        return SearchStatus.CHALLENGE_DETECTED
    # 登录判定只看主机名，不看正文
    if hostname in {"login.cnki.net"} or "authserver" in url_identity:
        return SearchStatus.LOGIN_REQUIRED
    if body_signals_apply:
        if any(
            token in visible_identity
            for token in ("401 unauthorized", "403 forbidden", "无权访问", "拒绝访问")
        ):
            return SearchStatus.FORBIDDEN
        if any(
            token in visible_identity
            for token in ("429 too many requests", "访问过于频繁", "操作频繁")
        ):
            return SearchStatus.RATE_LIMITED
        if any(
            token in visible_identity
            for token in ("请完成拼图验证", "请输入验证码", "请完成安全验证", "拖动滑块完成验证")
        ):
            return SearchStatus.CHALLENGE_DETECTED
        if any(token in visible_identity for token in ("用户登录", "统一身份认证")):
            return SearchStatus.LOGIN_REQUIRED
    if "未检索到相关文献" in visible_text:
        return SearchStatus.NO_RESULTS
    if parsed.hostname == CNKI_RESULT_HOST and path_identity.startswith(CNKI_RESULT_PATH_PREFIX):
        if "题名" in visible_text and "来源" in visible_text:
            return SearchStatus.SUCCESS
    # 公开首页不是结果页，绝不能判为 SUCCESS——否则会去解析首页、得到 0 行，
    # 最终把一次未真正执行的检索报成"无结果"。
    return SearchStatus.PAGE_CONTRACT_CHANGED


class PublicCnkiSession:
    def __init__(self, browser_factory: BrowserFactory | None = None) -> None:
        self._playwright: Any = None
        self._browser_factory = browser_factory
        self.browser: Any = None
        self.context: Any = None
        self.page: Any = None
        self._home_response_status: int | None = None

    def __enter__(self) -> "PublicCnkiSession":
        try:
            if self._browser_factory is None:
                self._playwright = start_playwright()
                self._browser_factory = BrowserFactory(self._playwright)
            self.browser = self._browser_factory.launch_ephemeral()
            self.context = self.browser.new_context(locale="zh-CN", accept_downloads=False)
            self.page = self.context.new_page()
            response = self.page.goto(CNKI_HOME_URL, wait_until="domcontentloaded")
            self._home_response_status = getattr(response, "status", None)
            return self
        except Exception as exc:
            self._close_resources()
            if _is_playwright_timeout(exc):
                raise TransientBrowserError("知网公开首页访问超时") from exc
            raise

    def search(self, query: str) -> SearchSnapshot:
        try:
            if self.page is None:
                raise RuntimeError("公开检索会话未启动")
            body = self.page.locator("body").inner_text(timeout=10_000)
            initial = SearchSnapshot(
                self.page.content(), self.page.url, self.page.title(), body, self._home_response_status,
            )
            if classify_public_search_state(**initial.state_arguments()) in {
                SearchStatus.CHALLENGE_DETECTED,
                SearchStatus.LOGIN_REQUIRED,
                SearchStatus.FORBIDDEN,
                SearchStatus.RATE_LIMITED,
                SearchStatus.NETWORK_ERROR,
                SearchStatus.NO_RESULTS,
            }:
                return initial
            if self.page.url != CNKI_HOME_URL:
                raise PageContractChanged("知网公开首页未就绪")
            validate_public_theme_search_contract(self.page)
            http_status = PublicThemeSearchRunner().run(self.page, query)
            body = self.page.locator("body").inner_text(timeout=10_000)
            return SearchSnapshot(self.page.content(), self.page.url, self.page.title(), body, http_status)
        except Exception as exc:
            if _is_playwright_timeout(exc):
                raise TransientBrowserError("知网公开检索超时") from exc
            raise

    def __exit__(self, *_exc: object) -> None:
        self._close_resources()

    def _close_resources(self) -> None:
        for resource, method in (
            (self.page, "close"),
            (self.context, "close"),
            (self.browser, "close"),
            (self._playwright, "stop"),
        ):
            if resource is not None:
                try:
                    getattr(resource, method)()
                except Exception:
                    pass
        self.context = None
        self.browser = None
        self.page = None
        self._home_response_status = None
        self._playwright = None
