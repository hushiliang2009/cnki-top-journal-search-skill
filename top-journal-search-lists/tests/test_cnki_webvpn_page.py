"""专业检索页驱动的契约测试。

每条断言都对应 2026-07-28 实测得到的一条结构事实。偏离任一条都会以难以归因的
方式失败，因此固化成测试而不是只写注释。
"""
import asyncio

import pytest

from cnki_search import webvpn
from cnki_search.models import SearchStatus
from cnki_search.professional import ExpressionBatch


class FakeLocator:
    def __init__(self, page: "FakePage", selector: str, *, count: int = 1,
                 visible: bool = True) -> None:
        self.page = page
        self.selector = selector
        self._count = count
        self._visible = visible
        self.value = ""

    @property
    def first(self) -> "FakeLocator":
        return self

    def nth(self, _index: int) -> "FakeLocator":
        return self

    async def is_visible(self) -> bool:
        return self._visible

    async def is_enabled(self) -> bool:
        return True

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
                 tab_switch: bool = True, page_title: str = "中国知网",
                 closed: bool = False, visibility: dict | None = None) -> None:
        self.counts = counts or {}
        self.visibility = visibility or {}
        self.caps = caps or {}
        self.tab_switch = tab_switch
        self.page_title = page_title
        self.closed = closed
        self.actions: list[tuple[str, str]] = []
        self.filled = ""
        self._locators: dict[str, FakeLocator] = {}

    async def title(self) -> str:
        return self.page_title

    def is_closed(self) -> bool:
        return self.closed

    async def wait_for_load_state(self, _state: str) -> None:
        return None

    def locator(self, selector: str) -> FakeLocator:
        if selector not in self._locators:
            self._locators[selector] = FakeLocator(
                self, selector, count=self.counts.get(selector, 1),
                visible=self.visibility.get(selector, True))
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
    asyncio.run(driver.open_from_home(context, timeout_seconds=2))
    assert ("get_by_role", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions
    assert ("click", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions


def _home_without_expression_box(**kwargs) -> FakePage:
    """真实的知网首页没有专业检索表达式框——判据正是靠这一点区分页面。"""
    return FakePage(counts={webvpn.EXPRESSION_BOX_SELECTOR: 0}, **kwargs)


def test_driver_follows_the_new_tab_opened_by_the_link() -> None:
    home = _home_without_expression_box()
    adv = FakePage(page_title="高级检索-中国知网")
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
        result = asyncio.run(driver.open_from_home(context, timeout_seconds=3))
    finally:
        FakeLocator.click = original_click
    assert result is adv and driver.page is adv


def test_transient_tab_that_closes_is_skipped_rather_than_adopted() -> None:
    """站点会短暂开一个中转标签页再关掉。

    抓住它会让驱动指向已关闭的页面，后续报错还指向完全错误的原因
    （表现为"未找到专业检索标签"，实则页面早已不存在）。
    """
    home = _home_without_expression_box()
    transient = FakePage(closed=True)
    adv = FakePage(page_title="高级检索-中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home, transient, adv]

    result = asyncio.run(driver.open_from_home(Context(), timeout_seconds=3))
    assert result is adv, "应跳过已关闭的中转页，选中真正的高级检索页"


def test_same_tab_navigation_is_also_supported() -> None:
    """并非总是新开标签页；同页跳转时 origin 自身就是目标。"""
    home = FakePage(page_title="高级检索-中国知网")   # 点击后原页变成高级检索
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home]

    assert asyncio.run(driver.open_from_home(Context(), timeout_seconds=3)) is home


def test_no_usable_advanced_search_page_raises_with_actionable_message() -> None:
    home = _home_without_expression_box(page_title="中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home]

    with pytest.raises(webvpn.WebVpnNavigationError, match="未出现可用的高级检索页面"):
        asyncio.run(driver.open_from_home(Context(), timeout_seconds=2))


def test_missing_home_link_is_reported_rather_than_deep_linking() -> None:
    home = FakePage(counts={f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}": 0})
    driver = webvpn.ProfessionalSearchPage(home)
    with pytest.raises(webvpn.WebVpnNavigationError, match="高级检索"):
        asyncio.run(driver.open_from_home(FakeContext([home]), timeout_seconds=2))


def test_professional_tab_is_switched_through_javascript_click() -> None:
    """非活动标签被 CSS 隐藏，Playwright 判定其不可见，只能用 JS 触发。"""
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.switch_to_professional(timeout_seconds=2))
    assert ("evaluate", webvpn.PROFESSIONAL_TAB_TEXT) in page.actions


def test_missing_professional_tab_raises() -> None:
    driver = webvpn.ProfessionalSearchPage(FakePage(tab_switch=False))
    with pytest.raises(webvpn.WebVpnNavigationError, match="专业检索"):
        asyncio.run(driver.switch_to_professional(timeout_seconds=2))


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
    clicked = {selector for action, selector in page.actions if action == "click"}
    assert clicked & set(webvpn.SEARCH_BUTTON_SELECTORS)


def test_submit_skips_the_hidden_namesake_button() -> None:
    """input.search-btn 在高级检索页尺寸 0×0；选中它会重试到 30 秒超时。"""
    page = FakePage(visibility={"input.btn-search": False, "input.search-btn": True})
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.submit())
    assert ("click", "input.search-btn") in page.actions


def test_missing_search_button_raises() -> None:
    page = FakePage(counts={selector: 0 for selector in webvpn.SEARCH_BUTTON_SELECTORS})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="检索按钮"):
        asyncio.run(driver.submit())


def test_selectors_match_the_observed_page_structure() -> None:
    """选择器一旦被随手改动，失败现象会伪装成风控，因此钉死在测试里。"""
    assert webvpn.EXPRESSION_BOX_SELECTOR == "textarea.textarea-major.majorSearch"
    assert webvpn.SEARCH_BUTTON_SELECTORS[0] == "input.btn-search"
    assert "input.search-btn" in webvpn.SEARCH_BUTTON_SELECTORS
    assert webvpn.RESULT_TABLE_SELECTOR == "table.result-table-list"
    assert webvpn.ADV_SEARCH_LINK_TEXT == "高级检索"
    assert webvpn.PROFESSIONAL_TAB_TEXT == "专业检索"


class PlanPage:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.url = "https://webvpn.example.edu.cn/result"

    async def content(self) -> str:
        self.events.append("content")
        return "<table class='result-table-list'></table>"


class PlanRecorder(webvpn.ProfessionalSearchPage):
    def __init__(self, events: list[str]) -> None:
        super().__init__(PlanPage(events))
        self.events = events

    async def fill_expression(self, expression: str) -> None:
        assert expression == "SU %= '数字经济'"
        self.events.append("fill")

    async def submit(self) -> None:
        self.events.append("submit")

    async def wait_for_outcome(self, timeout_seconds: float = 30) -> SearchStatus:
        self.events.append("classify")
        return SearchStatus.SUCCESS

    async def apply_source_category(self, name: str, *,
                                    timeout_seconds: float = 20.0) -> str | None:
        self.events.append(f"facet:{name}")
        return "10"

    async def set_page_size(self, size: int = 50, *,
                            timeout_seconds: float = 20.0) -> int:
        self.events.append(f"page_size:{size}")
        return size


def _plan(*, source_category: str | None) -> ExpressionBatch:
    return ExpressionBatch(
        index=1,
        total=1,
        journals=(),
        expression="SU %= '数字经济'",
        page_size=50,
        source_category=source_category,
    )


def test_execute_plan_applies_post_result_options_before_final_render() -> None:
    events: list[str] = []
    driver = PlanRecorder(events)

    status, html, url = asyncio.run(driver.execute_plan(_plan(source_category="CSSCI")))

    assert (status, html, url) == (
        "success",
        "<table class='result-table-list'></table>",
        "https://webvpn.example.edu.cn/result",
    )
    assert events == [
        "fill", "submit", "classify",
        "facet:CSSCI", "page_size:50", "classify", "content",
    ]


def test_execute_plan_omits_facet_for_chinese_top_plan() -> None:
    events: list[str] = []
    driver = PlanRecorder(events)

    status, _html, _url = asyncio.run(driver.execute_plan(_plan(source_category=None)))

    assert status == SearchStatus.SUCCESS.value
    assert all(not event.startswith("facet:") for event in events)


class DelayedResultLocator:
    def __init__(self, page: "DelayedResultPage", selector: str) -> None:
        self.page = page
        self.selector = selector

    async def count(self) -> int:
        if self.selector == webvpn.RESULT_TABLE_SELECTOR:
            self.page.result_polls += 1
            return int(self.page.result_polls >= 3)
        return 1

    async def inner_text(self, *, timeout: int) -> str:
        return ""


class DelayedResultPage:
    def __init__(self) -> None:
        self.result_polls = 0

    def locator(self, selector: str) -> DelayedResultLocator:
        return DelayedResultLocator(self, selector)

    async def evaluate(self, _script: str, _markers: list[str]) -> bool:
        return False


def test_wait_for_outcome_polls_through_temporary_contract_change() -> None:
    page = DelayedResultPage()
    driver = webvpn.ProfessionalSearchPage(page)

    status = asyncio.run(driver.wait_for_outcome(timeout_seconds=1, poll_seconds=0))

    assert status is SearchStatus.SUCCESS
    assert page.result_polls == 3
