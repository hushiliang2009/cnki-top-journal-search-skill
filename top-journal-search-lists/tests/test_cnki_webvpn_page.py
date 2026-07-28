"""专业检索页驱动的契约测试。

每条断言都对应 2026-07-28 实测得到的一条结构事实。偏离任一条都会以难以归因的
方式失败，因此固化成测试而不是只写注释。
"""
import asyncio

import pytest

from cnki_search import webvpn


class FakeLocator:
    def __init__(self, page: "FakePage", selector: str, *, count: int = 1) -> None:
        self.page = page
        self.selector = selector
        self._count = count
        self.value = ""

    @property
    def first(self) -> "FakeLocator":
        return self

    async def count(self) -> int:
        return self._count

    async def fill(self, value: str) -> None:
        # 一框式检索框只收 100 字符，专业检索框收 18000
        cap = self.page.caps.get(self.selector, 18_000)
        self.value = value[:cap]
        self.page.filled = self.value

    async def input_value(self) -> str:
        return self.value

    async def click(self) -> None:
        self.page.actions.append(("click", self.selector))


class FakePage:
    def __init__(self, *, counts: dict | None = None, caps: dict | None = None,
                 tab_switch: bool = True) -> None:
        self.counts = counts or {}
        self.caps = caps or {}
        self.tab_switch = tab_switch
        self.actions: list[tuple[str, str]] = []
        self.filled = ""
        self._locators: dict[str, FakeLocator] = {}

    def locator(self, selector: str) -> FakeLocator:
        if selector not in self._locators:
            self._locators[selector] = FakeLocator(
                self, selector, count=self.counts.get(selector, 1))
        return self._locators[selector]

    def get_by_role(self, role: str, name: str) -> FakeLocator:
        key = f"role:{role}:{name}"
        self.actions.append(("get_by_role", key))
        return FakeLocator(self, key, count=self.counts.get(key, 1))

    async def evaluate(self, script: str, arg=None):
        self.actions.append(("evaluate", arg or ""))
        return self.tab_switch


class FakeContext:
    def __init__(self, pages: list) -> None:
        self.pages = pages


def test_advanced_search_is_reached_through_the_home_page_link() -> None:
    """深链 /kns8s/AdvSearch 会触发安全验证，必须点首页链接。"""
    home = FakePage()
    driver = webvpn.ProfessionalSearchPage(home)
    context = FakeContext([home])
    asyncio.run(driver.open_from_home(context))
    assert ("get_by_role", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions
    assert ("click", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions


def test_driver_follows_the_new_tab_opened_by_the_link() -> None:
    home = FakePage()
    adv = FakePage()
    driver = webvpn.ProfessionalSearchPage(home)

    class GrowingContext:
        def __init__(self) -> None:
            self.pages = [home]

        def open(self) -> None:
            self.pages.append(adv)

    context = GrowingContext()
    original_click = FakeLocator.click

    async def click_and_open(self) -> None:
        await original_click(self)
        context.open()

    FakeLocator.click = click_and_open
    try:
        result = asyncio.run(driver.open_from_home(context))
    finally:
        FakeLocator.click = original_click
    assert result is adv and driver.page is adv


def test_missing_home_link_is_reported_rather_than_deep_linking() -> None:
    home = FakePage(counts={f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}": 0})
    driver = webvpn.ProfessionalSearchPage(home)
    with pytest.raises(webvpn.WebVpnNavigationError, match="高级检索"):
        asyncio.run(driver.open_from_home(FakeContext([home])))


def test_professional_tab_is_switched_through_javascript_click() -> None:
    """非活动标签被 CSS 隐藏，Playwright 判定其不可见，只能用 JS 触发。"""
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.switch_to_professional())
    assert ("evaluate", webvpn.PROFESSIONAL_TAB_TEXT) in page.actions


def test_missing_professional_tab_raises() -> None:
    driver = webvpn.ProfessionalSearchPage(FakePage(tab_switch=False))
    with pytest.raises(webvpn.WebVpnNavigationError, match="专业检索"):
        asyncio.run(driver.switch_to_professional())


def test_expression_is_typed_into_the_professional_box_only() -> None:
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    expression = "SU %= '数字经济' AND (LY='管理世界')"
    asyncio.run(driver.fill_expression(expression))
    assert page.locator(webvpn.EXPRESSION_BOX_SELECTOR).value == expression


def test_truncated_expression_aborts_instead_of_submitting_half_a_query() -> None:
    """误填到一框式检索框（上限 100 字符）会静默截断，提交后站点返回「访问禁止」。

    截断后的半截语法仍是"合法"提交，返回的却是完全不同的检索范围——必须中止，
    否则会把错误结果当成真实检索结果报出去。
    """
    page = FakePage(caps={webvpn.EXPRESSION_BOX_SELECTOR: 100})
    driver = webvpn.ProfessionalSearchPage(page)
    long_expression = "SU %= '数字经济' AND (" + " OR ".join(
        f"LY='测试期刊{index:03d}'" for index in range(20)) + ")"
    assert len(long_expression) > 100
    with pytest.raises(webvpn.ExpressionTruncated) as raised:
        asyncio.run(driver.fill_expression(long_expression))
    assert "100" in str(raised.value)
    assert ("click", webvpn.SEARCH_BUTTON_SELECTOR) not in page.actions


def test_missing_expression_box_raises() -> None:
    page = FakePage(counts={webvpn.EXPRESSION_BOX_SELECTOR: 0})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="表达式输入框"):
        asyncio.run(driver.fill_expression("SU %= '主题'"))


def test_submit_clicks_the_professional_search_button() -> None:
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.submit())
    assert ("click", webvpn.SEARCH_BUTTON_SELECTOR) in page.actions


def test_missing_search_button_raises() -> None:
    page = FakePage(counts={webvpn.SEARCH_BUTTON_SELECTOR: 0})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="检索按钮"):
        asyncio.run(driver.submit())


def test_selectors_match_the_observed_page_structure() -> None:
    """选择器一旦被随手改动，失败现象会伪装成风控，因此钉死在测试里。"""
    assert webvpn.EXPRESSION_BOX_SELECTOR == "textarea.textarea-major.majorSearch"
    assert webvpn.SEARCH_BUTTON_SELECTOR == "input.search-btn"
    assert webvpn.RESULT_TABLE_SELECTOR == "table.result-table-list"
    assert webvpn.ADV_SEARCH_LINK_TEXT == "高级检索"
    assert webvpn.PROFESSIONAL_TAB_TEXT == "专业检索"
