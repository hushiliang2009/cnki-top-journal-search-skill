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


PUBLIC_RESULT_TABLE_SELECTOR = ".result-table-list"
PUBLIC_NO_RESULT_TEXT = "未检索到相关文献"
RESULT_RENDER_TIMEOUT_MS = 15_000


class PublicThemeSearchRunner:
    def run(self, page: Any, query: str) -> int | None:
        box = validate_public_theme_search_contract(page)
        box.fill(query)
        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
            box.press("Enter")
        response = navigation.value
        self._wait_for_result_render(page)
        return response.status if response is not None else None

    def _wait_for_result_render(self, page: Any) -> None:
        """等待结果表渲染完毕（规格 §5.2 步骤 5）。

        domcontentloaded 只保证文档解析完成，结果表由脚本渲染。不等就取
        page.content()，会抓到尚未渲染的 HTML，解析出 0 行并被报成"无结果"。

        选择器与解析器使用的是同一个类名：若 CNKI 改名，解析本就会失效，
        此处不引入新的失败面，只是把静默失败变成响亮失败。
        受限页（验证码、登录、429）不会出现结果表，超时后交由状态判定处理。
        """
        waiter = getattr(page, "wait_for_selector", None)
        if waiter is None:
            return
        try:
            waiter(
                f"{PUBLIC_RESULT_TABLE_SELECTOR}, text={PUBLIC_NO_RESULT_TEXT}",
                timeout=RESULT_RENDER_TIMEOUT_MS,
            )
        except Exception:
            # 不在此处判定成败：交给 classify_public_search_state 依据
            # URL、标题、HTTP 状态码给出准确原因。
            return
