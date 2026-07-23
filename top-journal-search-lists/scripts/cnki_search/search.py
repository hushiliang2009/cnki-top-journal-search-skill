from __future__ import annotations

from typing import Any


class PageContractChanged(RuntimeError):
    pass


PUBLIC_SEARCH_BOX_NAME = "中文文献、外文文献"
PUBLIC_SEARCH_BUTTON_NAME = "检索"
CURRENT_THEME_SELECTOR = ".sort .sort-default"
CURRENT_THEME_TEXT = "主题▼"
RESULT_TABLE_SELECTOR = "table.result-table-list"
NO_RESULTS_TEXT = "未检索到相关文献"


def _normalize_control_text(value: str) -> str:
    return "".join(value.split())


def current_public_theme_control(page: Any) -> Any:
    control = page.locator(CURRENT_THEME_SELECTOR)
    if control.count() != 1 or _normalize_control_text(control.inner_text()) != CURRENT_THEME_TEXT:
        raise PageContractChanged("知网公开首页当前主题控件结构已变化")
    return control


def public_theme_search_button(page: Any) -> Any:
    button = page.get_by_role("button", name=PUBLIC_SEARCH_BUTTON_NAME)
    if button.count() != 1:
        raise PageContractChanged("知网公开首页主题检索按钮结构已变化")
    return button


def validate_public_theme_search_contract(page: Any) -> tuple[Any, Any]:
    current_public_theme_control(page)
    box = page.get_by_role("textbox", name=PUBLIC_SEARCH_BOX_NAME)
    if box.count() != 1:
        raise PageContractChanged("知网公开首页主题检索框结构已变化")
    return box, public_theme_search_button(page)


def _is_result_wait_timeout(error: BaseException) -> bool:
    return isinstance(error, TimeoutError) or any(
        item.__name__ == "TimeoutError" and item.__module__.startswith("playwright.")
        for item in type(error).__mro__
    )


def wait_for_public_search_result_contract(page: Any) -> None:
    try:
        page.wait_for_function(
            f"""
            () => Boolean(
                document.querySelector("{RESULT_TABLE_SELECTOR}")
                || document.body?.innerText?.includes("{NO_RESULTS_TEXT}")
            )
            """,
            timeout=10_000,
        )
    except Exception as exc:
        if _is_result_wait_timeout(exc):
            raise PageContractChanged("知网公开检索结果结构未出现") from exc
        raise


class PublicThemeSearchRunner:
    def run(self, page: Any, query: str) -> int | None:
        box, button = validate_public_theme_search_contract(page)
        box.fill(query)
        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
            button.click()
        wait_for_public_search_result_contract(page)
        response = navigation.value
        return response.status if response is not None else None
