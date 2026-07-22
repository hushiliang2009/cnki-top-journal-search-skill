from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from .browser import BrowserFactory, start_playwright
from .models import SearchStatus
from .search import PageContractChanged, PublicThemeSearchRunner


CNKI_HOME_URL = "https://www.cnki.net/"
CNKI_RESULT_HOST = "kns.cnki.net"
CNKI_RESULT_PATH_PREFIX = "/kns8s/defaultresult/"


@dataclass(frozen=True, slots=True)
class SearchSnapshot:
    html: str
    url: str
    title: str
    visible_text: str
    http_status: int | None = None

    def state_arguments(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "visible_text": self.visible_text,
            "http_status": self.http_status,
        }


def classify_public_search_state(
    *, url: str, title: str, visible_text: str, http_status: int | None = None,
) -> SearchStatus:
    identity = f"{url}\n{title}\n{visible_text}".casefold()
    if http_status in {401, 403} or any(
        token in identity for token in ("401 unauthorized", "403 forbidden", "无权访问", "拒绝访问")
    ):
        return SearchStatus.FORBIDDEN
    if http_status == 429 or any(
        token in identity for token in ("429 too many requests", "访问过于频繁", "操作频繁")
    ):
        return SearchStatus.RATE_LIMITED
    if http_status is not None and 500 <= http_status <= 599:
        return SearchStatus.NETWORK_ERROR
    if any(token in identity for token in ("captcha", "请完成拼图验证", "请输入验证码", "安全验证")):
        return SearchStatus.CHALLENGE_DETECTED
    if any(token in identity for token in ("login.cnki.net", "authserver", "用户登录", "统一身份认证")):
        return SearchStatus.LOGIN_REQUIRED
    parsed = urlparse(url)
    if "未检索到相关文献" in visible_text:
        return SearchStatus.NO_RESULTS
    if parsed.hostname == "www.cnki.net" and "中国知网" in identity:
        return SearchStatus.SUCCESS
    if parsed.hostname == CNKI_RESULT_HOST and parsed.path.casefold().startswith(CNKI_RESULT_PATH_PREFIX):
        if "题名" in visible_text and "来源" in visible_text:
            return SearchStatus.SUCCESS
    return SearchStatus.PAGE_CONTRACT_CHANGED


class PublicCnkiSession:
    def __init__(self, browser_factory: BrowserFactory | None = None) -> None:
        self._playwright: Any = None
        self._browser_factory = browser_factory
        self.browser: Any = None
        self.context: Any = None
        self.page: Any = None

    def __enter__(self) -> "PublicCnkiSession":
        if self._browser_factory is None:
            self._playwright = start_playwright()
            self._browser_factory = BrowserFactory(self._playwright)
        self.browser = self._browser_factory.launch_ephemeral()
        self.context = self.browser.new_context(locale="zh-CN", accept_downloads=False)
        self.page = self.context.new_page()
        self.page.goto(CNKI_HOME_URL, wait_until="domcontentloaded")
        return self

    def search(self, query: str) -> SearchSnapshot:
        if self.page is None:
            raise RuntimeError("公开检索会话未启动")
        body = self.page.locator("body").inner_text(timeout=10_000)
        initial = SearchSnapshot(self.page.content(), self.page.url, self.page.title(), body)
        if classify_public_search_state(**initial.state_arguments()) in {
            SearchStatus.CHALLENGE_DETECTED,
            SearchStatus.LOGIN_REQUIRED,
            SearchStatus.FORBIDDEN,
            SearchStatus.RATE_LIMITED,
            SearchStatus.NETWORK_ERROR,
            SearchStatus.NO_RESULTS,
        }:
            return initial
        home_box = self.page.get_by_role("textbox", name="中文文献、外文文献")
        theme_field = self.page.get_by_text("主题", exact=True)
        if self.page.url != CNKI_HOME_URL or home_box.count() != 1 or theme_field.count() != 1:
            raise PageContractChanged("知网公开首页未就绪")
        http_status = PublicThemeSearchRunner().run(self.page, query)
        body = self.page.locator("body").inner_text(timeout=10_000)
        return SearchSnapshot(self.page.content(), self.page.url, self.page.title(), body, http_status)

    def __exit__(self, *_exc: object) -> None:
        if self.context is not None:
            self.context.close()
        if self.browser is not None:
            self.browser.close()
        if self._playwright is not None:
            self._playwright.stop()
        self.context = None
        self.browser = None
        self.page = None
