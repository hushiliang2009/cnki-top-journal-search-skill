import pytest

from cnki_search import search


class RecordingLocator:
    def __init__(self, page: "RecordingPage") -> None:
        self.page = page

    def count(self) -> int:
        return 1

    def inner_text(self) -> str:
        return "主题 ▼"

    def fill(self, value: str) -> None:
        self.page.actions.append(("fill", value))

    def press(self, value: str) -> None:
        self.page.actions.append(("press", value))

    def click(self) -> None:
        self.page.actions.append(("click", ""))


class Navigation:
    def __enter__(self) -> "Navigation":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    @property
    def value(self) -> object:
        return type("Response", (), {"status": 200})()


class RecordingPage:
    def __init__(self) -> None:
        self.actions: list[tuple[str, str]] = []
        self.wait_script = ""

    def get_by_text(self, value: str, exact: bool = False) -> RecordingLocator:
        assert (value, exact) == ("主题", True)
        return RecordingLocator(self)

    def get_by_role(self, role: str, name: str) -> RecordingLocator:
        self.actions.append((role, name))
        return RecordingLocator(self)

    def locator(self, selector: str) -> RecordingLocator:
        assert selector == ".sort .sort-default"
        return RecordingLocator(self)

    def expect_navigation(self, **_kwargs: object) -> Navigation:
        return Navigation()

    def wait_for_function(self, script: str, *, timeout: int) -> None:
        assert timeout == 10_000
        self.wait_script = script
        self.actions.append(("wait_for_function", ""))


def test_runner_fills_only_default_theme_box() -> None:
    page = RecordingPage()
    search.PublicThemeSearchRunner().run(page, "数字化转型")
    assert page.actions == [
        ("textbox", "中文文献、外文文献"),
        ("button", "检索"),
        ("fill", "数字化转型"),
        ("click", ""),
        ("wait_for_function", ""),
    ]
    assert 'document.querySelector("table.result-table-list")' in page.wait_script
    assert "未检索到相关文献" in page.wait_script


def test_runner_stops_when_public_home_contract_changes() -> None:
    class MissingFieldPage(RecordingPage):
        def locator(self, selector: str) -> RecordingLocator:
            locator = super().locator(selector)
            locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    with pytest.raises(search.PageContractChanged):
        search.PublicThemeSearchRunner().run(MissingFieldPage(), "主题")


def test_runner_accepts_unique_current_theme_control_with_duplicate_theme_texts() -> None:
    class DuplicateThemeTextPage(RecordingPage):
        def get_by_text(self, value: str, exact: bool = False) -> RecordingLocator:
            assert (value, exact) == ("主题", True)
            locator = RecordingLocator(self)
            locator.count = lambda: 2  # type: ignore[method-assign]
            return locator

        def locator(self, selector: str) -> RecordingLocator:
            control = super().locator(selector)
            control.inner_text = lambda: "主题 ▼"  # type: ignore[method-assign]
            return control

    page = DuplicateThemeTextPage()
    assert search.PublicThemeSearchRunner().run(page, "数字化转型") == 200


def test_runner_rejects_missing_or_ambiguous_search_button() -> None:
    class MissingButtonPage(RecordingPage):
        def get_by_role(self, role: str, name: str) -> RecordingLocator:
            locator = super().get_by_role(role, name)
            if role == "button":
                locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    with pytest.raises(search.PageContractChanged):
        search.PublicThemeSearchRunner().run(MissingButtonPage(), "数字化转型")


def test_runner_turns_missing_result_or_no_result_contract_into_page_change() -> None:
    class MissingResultPage(RecordingPage):
        def wait_for_function(self, _script: str, *, timeout: int) -> None:
            raise TimeoutError(f"no result contract within {timeout}")

    with pytest.raises(search.PageContractChanged):
        search.PublicThemeSearchRunner().run(MissingResultPage(), "数字化转型")
