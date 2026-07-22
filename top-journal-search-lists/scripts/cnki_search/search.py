from __future__ import annotations

import re
from typing import Any, Protocol

from .fields import resolve_field
from .models import SearchRequest
from .syntax import validate_professional_expression


class PageDriver(Protocol):
    def select_label(self, label: str, value: str) -> None: ...
    def fill_label(self, label: str, value: str) -> None: ...
    def set_option(self, label: str, value: Any) -> None: ...
    def click_text(self, text: str) -> None: ...


class PlaywrightPageDriver:
    def __init__(self, page: Any) -> None:
        self.page = page

    def assert_old_search_page(self) -> None:
        if "/kns/advsearch" not in self.page.url.casefold():
            raise RuntimeError("当前页面不是知网旧版检索页面")
        advanced = self.page.locator('li[name="gradeSearch"]')
        professional = self.page.locator('li[name="majorSearch"]')
        if advanced.count() < 1 or professional.count() < 1:
            raise RuntimeError("知网旧版检索页面结构已变化")

    def _condition_row(self, label: str) -> Any:
        match = re.search(r"(\d+)$", label)
        if not match:
            raise ValueError(f"无法识别检索条件序号：{label}")
        return self.page.locator("#gradetxt > dd").nth(int(match.group(1)) - 1)

    @staticmethod
    def _choose(dropdown: Any, option_selector: str, expected_text: str) -> None:
        current = dropdown.locator(".sort-default span").first.inner_text().strip()
        if current == expected_text:
            return
        dropdown.locator(".sort-default").first.click()
        dropdown.locator(option_selector).first.click()

    def select_label(self, label: str, value: str) -> None:
        self.page.locator('li[name="gradeSearch"]').click()
        row = self._condition_row(label)
        dropdown = row.locator(".sort.reopt")
        self._choose(dropdown, f'a[title="{value}"]', value)

    def fill_label(self, label: str, value: str) -> None:
        if label == "专业检索表达式":
            self.page.locator('li[name="majorSearch"]').click()
            self.page.locator("textarea.textarea-major.majorSearch:visible").fill(value)
            return
        row = self._condition_row(label)
        row.locator("input[type=text]").fill(value)

    def set_option(self, label: str, value: Any) -> None:
        if label.startswith("匹配方式"):
            dropdown = self._condition_row(label).locator(".sort.special")
            classes = dropdown.get_attribute("class") or ""
            if "disableclick" in classes:
                return
            symbol = {"精确": "=", "模糊": "%"}.get(str(value), str(value))
            self._choose(dropdown, f'a[value="{symbol}"]', str(value))
            return
        if label.startswith("逻辑关系"):
            dropdown = self._condition_row(label).locator(".sort.logical")
            logic = {"并且": "AND", "或者": "OR", "不含": "NOT"}.get(str(value), str(value))
            self._choose(dropdown, f'a[value="{logic}"]', logic)
            return
        locator = self.page.locator(f'input[name="{label}"]:visible')
        if isinstance(value, bool):
            locator.check() if value else locator.uncheck()
        else:
            raise ValueError(f"暂不支持的高级检索筛选项：{label}")

    def click_text(self, text: str) -> None:
        if text != "检索":
            raise ValueError(f"暂不支持的按钮：{text}")
        self.page.locator("input.btn-search:visible").click()


class AdvancedSearchRunner:
    def run(self, page: PageDriver, request: SearchRequest) -> None:
        fields = request.fields or [{"field": "主题", "value": request.query, "match": "模糊"}]
        for index, item in enumerate(fields, start=1):
            field = resolve_field(str(item["field"]))
            value = str(item.get("value", "")).strip()
            if not value:
                raise ValueError(f"第 {index} 个检索词不能为空")
            page.select_label(f"检索字段{index}", field.label)
            page.fill_label(f"检索词{index}", value)
            page.set_option(f"匹配方式{index}", item.get("match", "模糊"))
            if index > 1:
                page.set_option(f"逻辑关系{index}", item.get("relation", "并且"))
        for label, value in request.filters.items():
            page.set_option(str(label), value)
        page.click_text("检索")


class ProfessionalSearchRunner:
    def run(self, page: PageDriver, expression: str) -> None:
        errors = validate_professional_expression(expression)
        if errors:
            raise ValueError("；".join(errors))
        page.fill_label("专业检索表达式", expression)
        page.click_text("检索")
