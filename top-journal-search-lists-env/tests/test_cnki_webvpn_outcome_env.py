"""提交后状态判定的契约测试。

每条都对应 2026-07-28 实机得到的一个事实。这些判定曾接连出过两次错，
且错误现象都伪装成别的原因，因此逐条钉死。
"""
import asyncio

import pytest

from cnki_search_env import webvpn
from cnki_search_env.models import SearchStatus


class OutcomeLocator:
    def __init__(self, count: int = 0, text: str = "", visible: bool = True) -> None:
        self._count = count
        self._text = text
        self._visible = visible

    async def count(self) -> int:
        return self._count

    async def inner_text(self, *, timeout: int = 0) -> str:
        return self._text

    async def is_visible(self) -> bool:
        return self._visible

    async def is_enabled(self) -> bool:
        return True

    def nth(self, _index: int) -> "OutcomeLocator":
        return self


class OutcomePage:
    def __init__(self, *, has_table: bool = False, body: str = "",
                 captcha_in_viewport: bool = False,
                 button_visibility: dict | None = None) -> None:
        self.has_table = has_table
        self.body = body
        self.captcha_in_viewport = captcha_in_viewport
        self.button_visibility = button_visibility or {}

    def locator(self, selector: str) -> OutcomeLocator:
        if selector == webvpn.RESULT_TABLE_SELECTOR:
            return OutcomeLocator(count=1 if self.has_table else 0)
        if selector == "body":
            return OutcomeLocator(count=1, text=self.body)
        if selector in self.button_visibility:
            visible = self.button_visibility[selector]
            return OutcomeLocator(count=1, visible=visible)
        return OutcomeLocator(count=0)

    async def evaluate(self, _script: str, _arg=None) -> bool:
        return self.captcha_in_viewport


def _classify(page) -> SearchStatus:
    return asyncio.run(webvpn.ProfessionalSearchPage(page).classify_outcome())


def test_result_table_wins_over_everything_else() -> None:
    """结果出来了就是成功，哪怕离屏验证码组件仍留在 DOM 里。"""
    page = OutcomePage(has_table=True, body="安全验证 拖动下方拼图完成验证",
                       captcha_in_viewport=True)
    assert _classify(page) is SearchStatus.SUCCESS


def test_no_data_message_is_not_reported_as_a_challenge() -> None:
    """「抱歉，暂无数据，请稍后重试。」是服务端临时拒绝，实测由过长表达式触发。

    曾被误报成 challenge_detected，导致排查方向完全跑偏——两者的补救办法
    相反：前者要缩小分批，后者要停手等人工。
    """
    page = OutcomePage(body="抱歉，暂无数据，请稍后重试。")
    assert _classify(page) is SearchStatus.NO_DATA_RETRY_LATER


def test_no_data_takes_precedence_over_offscreen_captcha_markup() -> None:
    page = OutcomePage(body="抱歉，暂无数据，请稍后重试。 拖动下方拼图完成验证",
                       captcha_in_viewport=False)
    assert _classify(page) is SearchStatus.NO_DATA_RETRY_LATER


def test_captcha_counts_only_when_actually_inside_the_viewport() -> None:
    """验证码组件常驻 DOM，未触发时停在 top:-1000430px 的离屏位置。

    它的 display:block、visibility:visible、offsetParent 都非空，只有元素矩形
    落在视口内才说明它真的弹出来了。
    """
    offscreen = OutcomePage(body="拖动下方拼图完成验证", captcha_in_viewport=False)
    assert _classify(offscreen) is SearchStatus.PAGE_CONTRACT_CHANGED

    onscreen = OutcomePage(body="拖动下方拼图完成验证", captcha_in_viewport=True)
    assert _classify(onscreen) is SearchStatus.CHALLENGE_DETECTED


def test_empty_result_message_is_distinguished_from_refusal() -> None:
    page = OutcomePage(body="未检索到相关文献")
    assert _classify(page) is SearchStatus.NO_RESULTS


def test_unknown_page_falls_back_to_contract_change() -> None:
    assert _classify(OutcomePage(body="某个完全陌生的页面")) is SearchStatus.PAGE_CONTRACT_CHANGED


def test_submit_picks_the_visible_button_not_the_hidden_namesake() -> None:
    """input.search-btn 在高级检索页尺寸为 0×0；点它会重试到 30 秒超时。"""
    page = OutcomePage(button_visibility={"input.btn-search": True,
                                          "input.search-btn": False})
    driver = webvpn.ProfessionalSearchPage(page)
    button = asyncio.run(driver._visible_search_button())
    assert button is not None
    assert asyncio.run(button.is_visible()) is True


def test_submit_raises_when_no_candidate_is_visible() -> None:
    page = OutcomePage(button_visibility={"input.btn-search": False,
                                          "input.search-btn": False})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="可见的检索按钮"):
        asyncio.run(driver.submit())


def test_button_candidate_order_prefers_the_advanced_search_button() -> None:
    assert webvpn.SEARCH_BUTTON_SELECTORS[0] == "input.btn-search"
    assert "input.search-btn" in webvpn.SEARCH_BUTTON_SELECTORS
