import pytest

from cnki_search.models import SearchMode, SearchRequest
from cnki_search.search import AdvancedSearchRunner, PlaywrightPageDriver, ProfessionalSearchRunner


def test_playwright_driver_exposes_old_page_contract() -> None:
    assert hasattr(PlaywrightPageDriver, "assert_old_search_page")


class FakePageDriver:
    def __init__(self) -> None:
        self.actions: list[tuple] = []
        self.filled_text = ""

    def select_label(self, label: str, value: str) -> None:
        self.actions.append(("select", label, value))

    def fill_label(self, label: str, value: str) -> None:
        self.actions.append(("fill", label, value))
        if label == "专业检索表达式":
            self.filled_text = value

    def set_option(self, label: str, value) -> None:
        self.actions.append(("option", label, value))

    def click_text(self, text: str) -> None:
        self.actions.append(("click", text))


def test_advanced_search_fills_fields_without_direct_http() -> None:
    page = FakePageDriver()
    request = SearchRequest(
        mode=SearchMode.ADVANCED,
        query="数字化转型",
        fields=[{"field": "主题", "value": "数字化转型", "match": "精确"}],
    )
    AdvancedSearchRunner().run(page, request)
    assert page.actions[0] == ("select", "检索字段1", "主题")
    assert not any(action[0] == "request" for action in page.actions)


def test_professional_search_fills_exact_expression() -> None:
    page = FakePageDriver()
    expression = "SU='气候风险' AND KY='企业创新'"
    ProfessionalSearchRunner().run(page, expression)
    assert page.filled_text == expression


def test_professional_search_stops_on_invalid_expression() -> None:
    with pytest.raises(ValueError, match="括号不配对"):
        ProfessionalSearchRunner().run(FakePageDriver(), "SU='创新' AND (")


class RecordingLocator:
    def __init__(self, path: str, actions: list[tuple]) -> None:
        self.path = path
        self.actions = actions

    def locator(self, selector: str) -> "RecordingLocator":
        return RecordingLocator(f"{self.path} >> {selector}", self.actions)

    def nth(self, index: int) -> "RecordingLocator":
        return RecordingLocator(f"{self.path} >> nth={index}", self.actions)

    def count(self) -> int:
        return 1

    @property
    def first(self) -> "RecordingLocator":
        return self

    def inner_text(self) -> str:
        return "其他"

    def get_attribute(self, _name: str):
        return "sort special"

    def click(self) -> None:
        self.actions.append(("click", self.path))

    def fill(self, value: str) -> None:
        self.actions.append(("fill", self.path, value))

    def check(self) -> None:
        self.actions.append(("check", self.path))

    def uncheck(self) -> None:
        self.actions.append(("uncheck", self.path))


class RecordingPlaywrightPage:
    def __init__(self, url: str = "https://kns.cnki.net/kns/advsearch?dbcode=CJZK") -> None:
        self.url = url
        self.actions: list[tuple] = []

    def locator(self, selector: str) -> RecordingLocator:
        return RecordingLocator(selector, self.actions)

    def get_by_label(self, *_args, **_kwargs):
        raise AssertionError("真实知网表单没有可用 label")

    def get_by_role(self, *_args, **_kwargs):
        raise AssertionError("检索按钮应使用真实页面的唯一可见选择器")


def test_playwright_driver_requires_old_search_page() -> None:
    page = RecordingPlaywrightPage("https://kns.cnki.net/kns8s/AdvSearch")
    with pytest.raises(RuntimeError, match="旧版检索页面"):
        PlaywrightPageDriver(page).assert_old_search_page()


def test_playwright_driver_accepts_old_search_tabs() -> None:
    page = RecordingPlaywrightPage()
    PlaywrightPageDriver(page).assert_old_search_page()


def test_playwright_driver_uses_cnki_custom_advanced_dom() -> None:
    page = RecordingPlaywrightPage()
    driver = PlaywrightPageDriver(page)
    driver.select_label("检索字段1", "主题")
    driver.fill_label("检索词1", "数字化转型")
    driver.set_option("匹配方式1", "精确")
    driver.click_text("检索")
    flattened = "\n".join(str(action) for action in page.actions)
    assert "#gradetxt > dd" in flattened
    assert ".sort.reopt" in flattened
    assert "input[type=text]" in flattened
    assert "input.btn-search:visible" in flattened


def test_playwright_driver_activates_professional_tab_and_textarea() -> None:
    page = RecordingPlaywrightPage()
    driver = PlaywrightPageDriver(page)
    driver.fill_label("专业检索表达式", "SU='气候风险'")
    flattened = "\n".join(str(action) for action in page.actions)
    assert 'li[name="majorSearch"]' in flattened
    assert "textarea.textarea-major.majorSearch:visible" in flattened
