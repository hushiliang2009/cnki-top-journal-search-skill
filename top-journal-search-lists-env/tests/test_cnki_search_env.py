import asyncio
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

from cnki_search_env import search


MCPB_SEARCH = Path(__file__).resolve().parents[1] / "mcpb" / "src" / "cnki_search_env" / "search.py"


def _load_mcpb_search():
    sys.modules.pop("cnki_search_env.search", None)
    sys.modules.pop("cnki_search_env", None)
    sys.path.insert(0, str(MCPB_SEARCH.parents[1]))
    return importlib.import_module("cnki_search_env.search")

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
    async def __aenter__(self) -> "Navigation":
        return self

    async def __aexit__(self, *_exc: object) -> None:
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
        assert selector in (".sort .sort-default", search.PUBLIC_SEARCH_BUTTON_SELECTOR)
        return RecordingLocator(self)

    def expect_navigation(self, **_kwargs: object) -> Navigation:
        return Navigation()

    def wait_for_function(self, script: str, *, timeout: int) -> None:
        assert timeout == 10_000
        self.wait_script = script
        self.actions.append(("wait_for_function", ""))


def test_runner_fills_only_default_theme_box() -> None:
    page = RecordingPage()
    asyncio.run(search.PublicThemeSearchRunner().run(page, "数字化转型"))
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
        asyncio.run(search.PublicThemeSearchRunner().run(MissingFieldPage(), "主题"))


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
    assert asyncio.run(search.PublicThemeSearchRunner().run(page, "数字化转型")) == 200


class NoRoleButtonPage(RecordingPage):
    """知网现状：首页检索按钮是不带 role 的 <div class="search-btn">。"""

    def get_by_role(self, role: str, name: str) -> RecordingLocator:
        locator = super().get_by_role(role, name)
        if role == "button":
            locator.count = lambda: 0  # type: ignore[method-assign]
        return locator


def test_public_button_falls_back_to_current_cnki_selector() -> None:
    page = NoRoleButtonPage()
    assert asyncio.run(search.PublicThemeSearchRunner().run(page, "环境规制")) == 200
    assert ("click", "") in page.actions


def test_runner_rejects_missing_or_ambiguous_search_button() -> None:
    class MissingButtonPage(NoRoleButtonPage):
        def locator(self, selector: str) -> RecordingLocator:
            locator = super().locator(selector)
            if selector == search.PUBLIC_SEARCH_BUTTON_SELECTOR:
                locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    with pytest.raises(search.PageContractChanged):
        asyncio.run(search.PublicThemeSearchRunner().run(MissingButtonPage(), "数字化转型"))


def test_runner_turns_missing_result_or_no_result_contract_into_page_change() -> None:
    class MissingResultPage(RecordingPage):
        def wait_for_function(self, _script: str, *, timeout: int) -> None:
            raise TimeoutError(f"no result contract within {timeout}")

    with pytest.raises(search.PageContractChanged):
        asyncio.run(search.PublicThemeSearchRunner().run(MissingResultPage(), "数字化转型"))


PlaywrightWaitTimeout = type(
    "TimeoutError", (RuntimeError,), {"__module__": "playwright._impl._errors"}
)
PlaywrightWaitError = type(
    "Error", (RuntimeError,), {"__module__": "playwright._impl._errors"}
)


@pytest.mark.parametrize(
    ("error_type", "wrap_as_contract_change"),
    [
        (TimeoutError, True),
        (PlaywrightWaitTimeout, True),
        (RuntimeError, False),
        (PlaywrightWaitError, False),
    ],
)
def test_runner_only_converts_timeout_while_waiting_for_result_contract(
    error_type: type[Exception], wrap_as_contract_change: bool,
) -> None:
    class FailingWaitPage(RecordingPage):
        def wait_for_function(self, _script: str, *, timeout: int) -> None:
            raise error_type("等待失败")

    if wrap_as_contract_change:
        with pytest.raises(search.PageContractChanged) as raised:
            asyncio.run(search.PublicThemeSearchRunner().run(FailingWaitPage(), "数字化转型"))
        assert isinstance(raised.value.__cause__, error_type)
    else:
        with pytest.raises(error_type, match="等待失败"):
            asyncio.run(search.PublicThemeSearchRunner().run(FailingWaitPage(), "数字化转型"))


def test_mcpb_runner_independently_checks_button_and_result_contract() -> None:
    module = _load_mcpb_search()
    page = RecordingPage()
    assert asyncio.run(module.PublicThemeSearchRunner().run(page, "数字化转型")) == 200
    assert ("button", "检索") in page.actions and ("click", "") in page.actions

    class NoRolePage(RecordingPage):
        def get_by_role(self, role: str, name: str) -> RecordingLocator:
            locator = super().get_by_role(role, name)
            if role == "button":
                locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    class MissingButtonPage(NoRolePage):
        def locator(self, selector: str) -> RecordingLocator:
            locator = super().locator(selector)
            if selector == module.PUBLIC_SEARCH_BUTTON_SELECTOR:
                locator.count = lambda: 0  # type: ignore[method-assign]
            return locator

    class TimeoutPage(RecordingPage):
        def wait_for_function(self, _script: str, *, timeout: int) -> None:
            raise TimeoutError(f"no result contract within {timeout}")

    class ErrorPage(RecordingPage):
        def wait_for_function(self, _script: str, *, timeout: int) -> None:
            raise RuntimeError("unexpected browser failure")

    # 打包副本必须与 scripts/ 同步带上 .search-btn 回退，否则装出来的那份仍然坏的。
    no_role = NoRolePage()
    assert asyncio.run(module.PublicThemeSearchRunner().run(no_role, "数字化转型")) == 200
    assert ("click", "") in no_role.actions

    with pytest.raises(module.PageContractChanged):
        asyncio.run(module.PublicThemeSearchRunner().run(MissingButtonPage(), "数字化转型"))
    with pytest.raises(module.PageContractChanged):
        asyncio.run(module.PublicThemeSearchRunner().run(TimeoutPage(), "数字化转型"))
    with pytest.raises(RuntimeError, match="unexpected browser failure"):
        asyncio.run(module.PublicThemeSearchRunner().run(ErrorPage(), "数字化转型"))
