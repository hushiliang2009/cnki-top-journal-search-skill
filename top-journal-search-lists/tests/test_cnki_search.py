import pytest

from cnki_search import search


class RecordingLocator:
    def __init__(self, page: "RecordingPage") -> None:
        self.page = page

    def count(self) -> int:
        return 1

    def fill(self, value: str) -> None:
        self.page.actions.append(("fill", value))

    def press(self, value: str) -> None:
        self.page.actions.append(("press", value))


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

    def get_by_text(self, value: str, exact: bool = False) -> RecordingLocator:
        assert (value, exact) == ("主题", True)
        return RecordingLocator(self)

    def get_by_role(self, role: str, name: str) -> RecordingLocator:
        self.actions.append((role, name))
        return RecordingLocator(self)

    def expect_navigation(self, **_kwargs: object) -> Navigation:
        return Navigation()


def test_runner_fills_only_default_theme_box() -> None:
    page = RecordingPage()
    search.PublicThemeSearchRunner().run(page, "数字化转型")
    assert page.actions == [
        ("textbox", "中文文献、外文文献"),
        ("fill", "数字化转型"),
        ("press", "Enter"),
    ]


def test_runner_stops_when_public_home_contract_changes() -> None:
    class MissingFieldPage(RecordingPage):
        def get_by_text(self, value: str, exact: bool = False) -> RecordingLocator:
            locator = super().get_by_text(value, exact)
            locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    with pytest.raises(search.PageContractChanged):
        search.PublicThemeSearchRunner().run(MissingFieldPage(), "主题")
