from __future__ import annotations

from typing import Any


class PageContractChanged(RuntimeError):
    pass


class PublicThemeSearchRunner:
    def run(self, page: Any, query: str) -> int | None:
        field = page.get_by_text("主题", exact=True)
        box = page.get_by_role("textbox", name="中文文献、外文文献")
        if field.count() != 1 or box.count() != 1:
            raise PageContractChanged("知网公开首页主题检索结构已变化")
        box.fill(query)
        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
            box.press("Enter")
        response = navigation.value
        return response.status if response is not None else None
