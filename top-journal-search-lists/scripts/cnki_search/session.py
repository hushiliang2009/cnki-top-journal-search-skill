from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlparse

from .browser import BrowserFactory, start_playwright
from .models import SessionStatus


HHU_LOGIN_URL = "https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421f1e2559434357a467b1ac7a490406d301894467e2b/authserver/login?service=https%3A%2F%2Fwebvpn.hhu.edu.cn%2Flogin%3Fcas_login%3Dtrue"
HHU_CNKI_URL = "https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421e7e056d2243e635930068cb8/"
DIRECT_CNKI_OLD_SEARCH_URL = "https://kns.cnki.net/kns/advsearch?dbcode=CJZK"
HHU_CNKI_OLD_SEARCH_URL = (
    "https://webvpn.hhu.edu.cn/https/"
    "77726476706e69737468656265737421fbf952d2243e635930068cb8/"
    "kns/advsearch?dbcode=CJZK"
)

_OLD_SEARCH_REQUIRED_SELECTORS = (
    'li[name="gradeSearch"]',
    'li[name="majorSearch"]',
)
_PUZZLE_PROMPTS = ("拖动下方拼图完成验证", "请完成拼图验证")

def resolve_old_search_url(current_url: str) -> str | None:
    hostname = (urlparse(current_url).hostname or "").casefold()
    if hostname == "webvpn.hhu.edu.cn":
        return HHU_CNKI_OLD_SEARCH_URL
    if hostname == "cnki.net" or hostname.endswith(".cnki.net"):
        return DIRECT_CNKI_OLD_SEARCH_URL
    return None


def classify_public_state(*, url: str, title: str, visible_text: str) -> SessionStatus:
    haystack = f"{url}\n{title}\n{visible_text}".casefold()
    if any(
        token in haystack
        for token in ("http 429", "429 too many requests", "访问过于频繁", "操作频繁", "too many requests")
    ):
        return SessionStatus.RATE_LIMITED
    if any(
        token in haystack
        for token in ("http 403", "403 forbidden", "无权访问", "权限不足", "permission denied")
    ):
        return SessionStatus.PERMISSION_DENIED
    if "authserver/login" in haystack or "统一身份认证" in haystack or "type=\"password\"" in haystack:
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
            "拖动下方拼图完成验证",
            "请完成拼图验证",
        )
    )
    ready_signal = any(
        token in haystack for token in ("中国知网", "高级检索", "专业检索", "kns.cnki")
    )
    residual_captcha_id = (
        path.endswith("/kns/advsearch")
        and verification_query_keys == {"captchaid"}
        and ready_signal
    )
    if (
        verification_url
        or explicit_verification
        or (verification_query_keys and not residual_captcha_id)
    ):
        return SessionStatus.CAPTCHA
    if ready_signal:
        return SessionStatus.READY
    if any(token in haystack for token in ("验证码", "安全验证", "captcha")):
        return SessionStatus.CAPTCHA
    if "webvpn.hhu.edu.cn" in haystack:
        return SessionStatus.SESSION_EXPIRED
    return SessionStatus.LOGIN_REQUIRED


def is_old_search_page_contract(
    *,
    page: Any,
    url: str,
    title: str,
    visible_text: str,
) -> bool:
    parsed_url = urlparse(url)
    if not parsed_url.path.casefold().endswith("/kns/advsearch"):
        return False
    query_keys = {
        key.casefold()
        for key, _value in parse_qsl(parsed_url.query, keep_blank_values=True)
    }
    verification_query_keys = {
        key for key in query_keys if "captcha" in key or "verify" in key
    }
    if verification_query_keys and verification_query_keys != {"captchaid"}:
        return False
    title_text = title.casefold()
    if "中国知网" not in title_text or "检索" not in title_text or "安全验证" in title_text:
        return False
    if any(prompt in visible_text for prompt in _PUZZLE_PROMPTS):
        return False
    try:
        return all(page.locator(selector).count() > 0 for selector in _OLD_SEARCH_REQUIRED_SELECTORS)
    except Exception:
        return False


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
            raise RuntimeError("会话已关闭")
        if self._browser_factory is None:
            self._playwright = start_playwright()
            self._browser_factory = BrowserFactory(self._playwright)
        if self.browser is None:
            self.browser = self._browser_factory.launch_visible()
            self.context = self.browser.new_context(accept_downloads=True)
            self.page = self.context.new_page()
        self.page.goto(HHU_LOGIN_URL, wait_until="domcontentloaded")
        return SessionStatus.WAITING_FOR_USER

    def open_cnki(self) -> SessionStatus:
        if self.page is None:
            return SessionStatus.LOGIN_REQUIRED
        self.page.goto(HHU_CNKI_URL, wait_until="domcontentloaded")
        return self.status()

    def open_old_search(self) -> SessionStatus:
        if self._closed:
            return SessionStatus.CLOSED
        if self.page is None:
            return SessionStatus.LOGIN_REQUIRED
        target = resolve_old_search_url(self.page.url)
        if target is None:
            return SessionStatus.SESSION_EXPIRED
        self.page.goto(target, wait_until="domcontentloaded")
        status = self.status()
        if status is not SessionStatus.READY:
            return status
        if "/kns/advsearch" not in self.page.url.casefold():
            return SessionStatus.SESSION_EXPIRED
        return SessionStatus.READY

    def status(self) -> SessionStatus:
        if self._closed:
            return SessionStatus.CLOSED
        if self.page is None:
            return SessionStatus.LOGIN_REQUIRED
        title = self.page.title()
        visible_text = self.page.locator("body").inner_text(timeout=5_000)
        status = classify_public_state(url=self.page.url, title=title, visible_text=visible_text)
        if status is SessionStatus.CAPTCHA and is_old_search_page_contract(
            page=self.page,
            url=self.page.url,
            title=title,
            visible_text=visible_text,
        ):
            return SessionStatus.READY
        return status

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
