from __future__ import annotations

from typing import Any


class PageContractChanged(RuntimeError):
    pass


PUBLIC_SEARCH_BOX_NAME = "中文文献、外文文献"
CURRENT_THEME_SELECTOR = ".sort .sort-default"
CURRENT_THEME_TEXT = "主题▼"


def _normalize_control_text(value: str) -> str:
    return "".join(value.split())


def current_public_theme_control(page: Any) -> Any:
    control = page.locator(CURRENT_THEME_SELECTOR)
    if control.count() != 1 or _normalize_control_text(control.inner_text()) != CURRENT_THEME_TEXT:
        raise PageContractChanged("知网公开首页当前主题控件结构已变化")
    return control


def validate_public_theme_search_contract(page: Any) -> Any:
    current_public_theme_control(page)
    box = page.get_by_role("textbox", name=PUBLIC_SEARCH_BOX_NAME)
    if box.count() != 1:
        raise PageContractChanged("知网公开首页主题检索框结构已变化")
    return box


class PublicThemeSearchRunner:
    def run(self, page: Any, query: str) -> int | None:
        box = validate_public_theme_search_contract(page)
        box.fill(query)
        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
            box.press("Enter")
        response = navigation.value
        return response.status if response is not None else None
