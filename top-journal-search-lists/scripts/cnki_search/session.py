from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlparse

from .browser import BrowserFactory, start_playwright
from .models import SessionStatus


HHU_LOGIN_URL = "https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421f1e2559434357a467b1ac7a490406d301894467e2b/authserver/login?service=https%3A%2F%2Fwebvpn.hhu.edu.cn%2Flogin%3Fcas_login%3Dtrue"
DIRECT_CNKI_SEARCH_URL = "https://kns.cnki.net/kns8s/AdvSearch"
HHU_CNKI_SEARCH_URL = "https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch"


def resolve_search_url(current_url: str) -> str | None:
    hostname = (urlparse(current_url).hostname or "").casefold()
    if hostname == "webvpn.hhu.edu.cn":
        return HHU_CNKI_SEARCH_URL
    if hostname == "cnki.net" or hostname.endswith(".cnki.net"):
        return DIRECT_CNKI_SEARCH_URL
    return None


def classify_public_state(*, url: str, title: str, visible_text: str) -> SessionStatus:
    haystack = f"{url}\n{title}\n{visible_text}".casefold()
    if any(
        token in haystack
        for token in (
            "http 429",
            "429 too many requests",
            "\u8bbf\u95ee\u8fc7\u4e8e\u9891\u7e41",
            "\u64cd\u4f5c\u9891\u7e41",
            "too many requests",
        )
    ):
        return SessionStatus.RATE_LIMITED
    if any(
        token in haystack
        for token in (
            "http 403",
            "403 forbidden",
            "\u65e0\u6743\u8bbf\u95ee",
            "\u6743\u9650\u4e0d\u8db3",
            "permission denied",
        )
    ):
        return SessionStatus.PERMISSION_DENIED
    if (
        "authserver/login" in haystack
        or "\u7edf\u4e00\u8eab\u4efd\u8ba4\u8bc1" in haystack
        or 'type="password"' in haystack
    ):
        return SessionStatus.LOGIN_REQUIRED
    parsed_url = urlparse(url)
    path = parsed_url.path.casefold()
    verification_url = any(token in path for token in ("captcha", "verify"))
    verification_query_keys = {
        key.casefold()
        for key, _value in parse_qsl(parsed_url.query, keep_blank_values=True)
        if "captcha" in key.casefold() or "verify" in key.casefold()
    }
    explicit_verification = any(
        token in haystack
        for token in (
            "\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801",
            "\u5b89\u5168\u9a8c\u8bc1",
            "\u6ed1\u52a8\u4e0b\u65b9\u62fc\u56fe\u5b8c\u6210\u9a8c\u8bc1",
            "\u8bf7\u5b8c\u6210\u62fc\u56fe\u9a8c\u8bc1",
        )
    )
    if verification_url or explicit_verification or verification_query_keys:
        return SessionStatus.CAPTCHA
    if any(
        token in haystack
        for token in ("\u4e2d\u56fd\u77e5\u7f51", "\u9ad8\u7ea7\u68c0\u7d22", "\u4e13\u4e1a\u68c0\u7d22", "kns.cnki")
    ):
        return SessionStatus.READY
    if "webvpn.hhu.edu.cn" in haystack:
        return SessionStatus.SESSION_EXPIRED
    return SessionStatus.LOGIN_REQUIRED


def is_new_search_page_contract(*, url: str, title: str, visible_text: str) -> bool:
    parsed_url = urlparse(url)
    try:
        location = (
            parsed_url.scheme.casefold(),
            (parsed_url.hostname or "").casefold(),
            parsed_url.port,
            parsed_url.path,
        )
    except ValueError:
        return False
    allowed_locations = {
        (
            allowed.scheme.casefold(),
            (allowed.hostname or "").casefold(),
            allowed.port,
            allowed.path,
        )
        for allowed in map(urlparse, (DIRECT_CNKI_SEARCH_URL, HHU_CNKI_SEARCH_URL))
    }
    if location not in allowed_locations:
        return False
    visible_identity = f"{title}\n{visible_text}".casefold()
    if "\u9ad8\u7ea7\u68c0\u7d22" not in visible_identity:
        return False
    return classify_public_state(
        url=url,
        title=title,
        visible_text=visible_text,
    ) is SessionStatus.READY


class CnkiSession:
    def __init__(self, browser_factory: BrowserFactory | None = None) -> None:
        self._playwright: Any = None
        self._browser_factory = browser_factory
        self.browser: Any = None
        self.context: Any = None
        self.page: Any = None
        self._closed = False

    def login(self) -> SessionStatus:
        if self._closed:
            raise RuntimeError("\u4f1a\u8bdd\u5df2\u5173\u95ed")
        if self._browser_factory is None:
            self._playwright = start_playwright()
            self._browser_factory = BrowserFactory(self._playwright)
        if self.browser is None:
            self.browser = self._browser_factory.launch_visible()
            self.context = self.browser.new_context(accept_downloads=True)
            self.page = self.context.new_page()
        self.page.goto(HHU_LOGIN_URL, wait_until="domcontentloaded")
        return SessionStatus.WAITING_FOR_USER

    def open_search(self) -> SessionStatus:
        if self._closed:
            return SessionStatus.CLOSED
        if self.page is None:
            return SessionStatus.LOGIN_REQUIRED
        target = resolve_search_url(self.page.url)
        if target is None:
            return SessionStatus.SESSION_EXPIRED
        self.page.goto(target, wait_until="domcontentloaded")
        url = self.page.url
        title = self.page.title()
        visible_text = self.page.locator("body").inner_text(timeout=5_000)
        status = classify_public_state(
            url=url,
            title=title,
            visible_text=visible_text,
        )
        if status is not SessionStatus.READY:
            return status
        if not is_new_search_page_contract(
            url=url,
            title=title,
            visible_text=visible_text,
        ):
            return SessionStatus.SESSION_EXPIRED
        return SessionStatus.READY

    def status(self) -> SessionStatus:
        if self._closed:
            return SessionStatus.CLOSED
        if self.page is None:
            return SessionStatus.LOGIN_REQUIRED
        return classify_public_state(
            url=self.page.url,
            title=self.page.title(),
            visible_text=self.page.locator("body").inner_text(timeout=5_000),
        )

    def close(self) -> SessionStatus:
        if self.context is not None:
            self.context.close()
        if self.browser is not None:
            self.browser.close()
        if self._playwright is not None:
            self._playwright.stop()
        self.context = None
        self.browser = None
        self.page = None
        self._closed = True
        return SessionStatus.CLOSED
