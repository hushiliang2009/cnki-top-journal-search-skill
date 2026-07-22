from html.parser import HTMLParser
from pathlib import Path

import pytest

from cnki_search.models import SearchMode, SearchRequest
from cnki_search.search import AdvancedSearchRunner, PlaywrightPageDriver, ProfessionalSearchRunner


FIXTURES = Path(__file__).with_name("fixtures")


class TextInputValueParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_prefilled_text_input = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "input" and attributes.get("type", "").casefold() == "text":
            self.has_prefilled_text_input = bool((attributes.get("value") or "").strip())


def test_new_search_fixtures_are_sanitized_and_cover_form_controls() -> None:
    advanced = (FIXTURES / "new_advanced.html").read_text(encoding="utf-8")
    professional = (FIXTURES / "new_professional.html").read_text(encoding="utf-8")

    assert 'data-fixture="sanitized"' in advanced
    assert 'li name="gradeSearch"' in advanced
    assert 'id="gradetxt"' in advanced
    assert 'class="btn-search"' in advanced
    assert 'data-fixture="sanitized"' in professional
    assert 'li name="majorSearch"' in professional
    assert 'textarea class="textarea-major majorSearch"' in professional


def test_new_search_selector_provenance_is_sanitized() -> None:
    provenance = (FIXTURES / "new_search_selector_provenance.md").read_text(
        encoding="utf-8"
    )

    assert "2026-07-21" in provenance
    assert "work/cnki_form_contract.py" in provenance
    assert "work/cnki_advanced_dom.py" in provenance
    assert "work/cnki_live_professional.py" in provenance
    assert 'li[name="gradeSearch"]' in provenance
    assert 'li[name="majorSearch"]' in provenance
    assert "#gradetxt > dd" in provenance
    assert "不含会话状态声明" in provenance


def test_new_search_html_fixtures_exclude_sensitive_or_prefilled_content() -> None:
    fixtures = [
        (FIXTURES / "new_advanced.html").read_text(encoding="utf-8"),
        (FIXTURES / "new_professional.html").read_text(encoding="utf-8"),
    ]
    forbidden_tokens = ("cookie", "token", "账号", "密码", "动态参数", "captcha", "verify")

    for content in fixtures:
        assert not any(token in content.casefold() for token in forbidden_tokens)
        assert "<textarea" not in content.casefold() or "></textarea>" in content.casefold()
        parser = TextInputValueParser()
        parser.feed(content)
        assert not parser.has_prefilled_text_input

    parser = TextInputValueParser()
    parser.feed('<input value="示例检索词" data-fixture="test" type="text">')
    assert parser.has_prefilled_text_input
    assert 'a value="="' in fixtures[0]


class FakePageDriver:
    def __init__(self) -> None:
        self.actions: list[tuple] = []
        self.filled_text = ""

    def select_label(self, label: str, value: str) -> None:
        self.actions.append(("select_label", label, value))

    def fill_label(self, label: str, value: str) -> None:
        self.actions.append(("fill_label", label, value))
        if label == "专业检索表达式":
            self.filled_text = value

    def set_option(self, label: str, value) -> None:
        self.actions.append(("set_option", label, value))

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
    assert page.actions[0] == ("select_label", "检索字段1", "主题")
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

    def inner_text(self, **_kwargs) -> str:
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
    def __init__(self, url: str = "https://kns.cnki.net/kns8s/AdvSearch") -> None:
        self.url = url
        self.actions: list[tuple] = []

    def locator(self, selector: str) -> RecordingLocator:
        return RecordingLocator(selector, self.actions)

    def title(self) -> str:
        return "中国知网高级检索"

    def get_by_label(self, *_args, **_kwargs):
        raise AssertionError("真实知网表单没有可用 label")

    def get_by_role(self, *_args, **_kwargs):
        raise AssertionError("检索按钮应使用真实页面的唯一可见选择器")


def test_playwright_driver_accepts_new_search_contract() -> None:
    page = RecordingPlaywrightPage("https://kns.cnki.net/kns8s/AdvSearch")
    PlaywrightPageDriver(page).assert_new_search_page()


def test_playwright_driver_rejects_non_new_url() -> None:
    page = RecordingPlaywrightPage("https://kns.cnki.net/")
    with pytest.raises(RuntimeError, match="新版检索页面"):
        PlaywrightPageDriver(page).assert_new_search_page()


def test_playwright_driver_rejects_third_party_host_with_new_search_path() -> None:
    page = RecordingPlaywrightPage("https://untrusted.example/kns8s/AdvSearch")
    with pytest.raises(RuntimeError, match="新版检索页面"):
        PlaywrightPageDriver(page).assert_new_search_page()


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


def test_exact_title_search_uses_title_field() -> None:
    page = FakePageDriver()
    title = "数字化转型、企业创新与新质生产力"
    request = SearchRequest(
        mode=SearchMode.ADVANCED,
        query=title,
        pages=1,
        fields=[{"field": "篇名", "value": title, "match": "精确"}],
        filters={},
    )

    AdvancedSearchRunner().run(page, request)

    assert ("select_label", "检索字段1", "题名") in page.actions
    assert ("set_option", "匹配方式1", "精确") in page.actions


def test_professional_expression_is_not_rewritten() -> None:
    page = FakePageDriver()
    expression = "TI='数字化转型' AND KY='企业创新'"

    ProfessionalSearchRunner().run(page, expression)

    assert ("fill_label", "专业检索表达式", expression) in page.actions


def test_playwright_driver_rejects_unknown_advanced_filter() -> None:
    with pytest.raises(ValueError, match="暂不支持的高级检索筛选项"):
        PlaywrightPageDriver(RecordingPlaywrightPage()).set_option("未知筛选", "值")
