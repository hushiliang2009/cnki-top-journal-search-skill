"""WebVPN 专业检索页的结构探针（实机脚本，不进 CI）。

与 ``_public_cnki_live_smoke.py`` 同属实机验证脚本：``_`` 前缀使 pytest 不收集，
CI 也不调用——它需要人工登录且会对知网发真实请求。

用途是在改动 :mod:`cnki_search.webvpn` 的选择器之前，先确认站点结构是否仍与
代码中的契约一致。默认只做**结构探测，不提交检索**，因此不消耗限流预算；
需要提交时用 ``--submit`` 显式开启。

证据经过脱敏：WebVPN 地址内嵌机构编码主机与会话信息，一律不写入输出。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cnki_search.professional import build_expression
from cnki_search.webvpn import (
    EXPRESSION_BOX_SELECTOR,
    PROFESSIONAL_TAB_TEXT,
    RESULT_TABLE_SELECTOR,
    SEARCH_BUTTON_SELECTOR,
    ProfessionalSearchPage,
    WebVpnConfig,
    WebVpnSession,
)

#: 与公开冒烟脚本同一套脱敏口径。WebVPN 地址本身就是敏感信息。
FORBIDDEN_FIELD_TOKENS = ("url", "cookie", "token", "session", "profile", "home")

#: 页面结构探测脚本。只读 DOM，不触发任何请求。
STRUCTURE_PROBE_JS = r"""(selectors) => {
  // 箭头函数没有 arguments 对象，选择器必须作为具名参数传入
  const [boxSelector, buttonSelector, tableSelector] = selectors;
  const text = (node) => (node.textContent || '').replace(/\s+/g, '');
  const sourceCategories = ['SCI', 'EI', '北大核心', 'CSSCI', 'CSCD', 'AMI', 'SSCI'];
  const box = document.querySelector(boxSelector);
  return {
    tabs: [...document.querySelectorAll('li,a,span')]
      .filter((node) => node.children.length === 0 &&
        /^(高级检索|专业检索|作者发文检索|句子检索|一框式检索)$/.test(text(node)))
      .map((node) => text(node)),
    expression_box_found: Boolean(box),
    expression_box_visible: Boolean(box && box.offsetParent),
    expression_box_maxlength: box ? box.getAttribute('maxlength') : null,
    search_button_count: document.querySelectorAll(buttonSelector).length,
    result_table_count: document.querySelectorAll(tableSelector).length,
    source_category_filters: [...document.querySelectorAll('input[type=checkbox]')]
      .map((cb) => { const label = cb.closest('label') || cb.parentElement;
                     return label ? text(label).slice(0, 20) : ''; })
      .filter((label) => sourceCategories.some((name) => label.includes(name))),
    option_checkboxes: [...document.querySelectorAll('input[type=checkbox]')]
      .filter((cb) => Boolean(cb.offsetParent))
      .map((cb) => { const label = cb.closest('label') || cb.parentElement;
                     return label ? text(label).slice(0, 16) : ''; })
      .filter(Boolean),
  };
}"""


def _assert_no_sensitive_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).casefold()
            if any(token in normalized for token in FORBIDDEN_FIELD_TOKENS):
                raise ValueError(f"验证证据含敏感字段：{path}.{key}")
            _assert_no_sensitive_fields(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _assert_no_sensitive_fields(child, f"{path}[{index}]")


@dataclass(frozen=True, slots=True)
class ProbeResult:
    exit_code: int
    payload: dict[str, Any]
    summary: dict[str, Any]
    message: str = ""


_TAB_SCAN_JS = r"""() => {
  const text = (node) => (node.textContent || '').replace(/\s+/g, '');
  return {
    page_title: document.title,
    mentions_professional: document.body ? document.body.innerText.includes('专业检索') : false,
    leaf_matches: [...document.querySelectorAll('li,a,span,div')]
      .filter((node) => node.children.length === 0 && text(node) === '专业检索')
      .map((node) => ({tag: node.tagName, cls: String(node.className || ''),
                       visible: Boolean(node.offsetParent)})),
    tab_texts: [...document.querySelectorAll('li,a,span')]
      .filter((node) => node.children.length === 0 &&
        /^(高级检索|专业检索|作者发文检索|句子检索|一框式检索)$/.test(text(node)))
      .map((node) => text(node)),
  };
}"""


async def _diagnose_tabs(context: Any, current: Any) -> dict[str, Any]:
    """列出全部标签页并逐个扫描「专业检索」，判断驱动是否停在了正确的页面。"""
    tabs = []
    for index, page in enumerate(getattr(context, "pages", []) or []):
        entry: dict[str, Any] = {"index": index, "is_driver_page": page is current}
        try:
            entry.update(await page.evaluate(_TAB_SCAN_JS))
        except Exception as exc:
            entry["scan_error"] = f"{type(exc).__name__}: {exc}"
        tabs.append(entry)
    return {"tab_count": len(tabs), "tabs": tabs}


def evaluate_contract(structure: Mapping[str, Any]) -> dict[str, Any]:
    """把原始探测结果折算成"代码中的契约是否仍成立"。"""
    return {
        "professional_tab_present": PROFESSIONAL_TAB_TEXT in structure.get("tabs", []),
        "expression_box_matches_selector": bool(structure.get("expression_box_found")),
        "expression_box_visible_after_switch": bool(structure.get("expression_box_visible")),
        "declared_maxlength": structure.get("expression_box_maxlength"),
        "search_button_matches_selector": (structure.get("search_button_count") or 0) >= 1,
        # 2026-07-28 实测为空。若某天不再为空，说明知网加回了来源类别筛选，
        # CSSCI 就不必再靠 LY= 枚举 661 本刊。
        "source_category_filters_available": bool(structure.get("source_category_filters")),
        "visible_option_checkboxes": list(structure.get("option_checkboxes", [])),
    }


async def run_probe(config: WebVpnConfig, *, submit_topic: str | None = None,
                    session_factory: Any = WebVpnSession,
                    driver_factory: Any = ProfessionalSearchPage) -> ProbeResult:
    """结构探测；``submit_topic`` 非空时额外提交一次 13 本顶刊的定向检索。"""
    async with session_factory(config) as session:
        await session.wait_until_ready()
        session.ensure_open()

        driver = driver_factory(session.page)
        await driver.open_from_home(session.context)
        try:
            await driver.switch_to_professional()
        except Exception as exc:
            # 失败时把"当时到底停在哪个页面"记下来。缺了这个，
            # "未找到专业检索标签"既可能是站点改版，也可能是驱动停错了页面。
            diagnosis = await _diagnose_tabs(session.context, driver.page)
            payload = {"navigation_error": str(exc), "diagnosis": diagnosis}
            _assert_no_sensitive_fields(payload)
            return ProbeResult(1, payload, {"contract_ok": False, "failed_checks": ["navigation"]},
                               "未能进入专业检索标签；诊断信息见证据文件。")

        structure = await driver.page.evaluate(
            STRUCTURE_PROBE_JS, [EXPRESSION_BOX_SELECTOR, SEARCH_BUTTON_SELECTOR,
                                 RESULT_TABLE_SELECTOR])
        contract = evaluate_contract(structure)

        submission: dict[str, Any] | None = None
        if submit_topic:
            expression = build_expression(submit_topic, _CHINESE_TOP_JOURNALS)
            # fill_expression 内部会校验实际接受长度，被截断即抛 ExpressionTruncated
            await driver.fill_expression(expression)
            await driver.submit()
            await asyncio.sleep(8)
            submission = {
                "expression_chars": len(expression),
                "result_rows": await driver.page.locator(RESULT_TABLE_SELECTOR).count(),
                "page_title": await driver.page.title(),
            }

    payload = {"contract": contract, "structure": dict(structure)}
    if submission is not None:
        payload["submission"] = submission
    _assert_no_sensitive_fields(payload)

    failures = [name for name in (
        "professional_tab_present", "expression_box_matches_selector",
        "expression_box_visible_after_switch", "search_button_matches_selector",
    ) if not contract[name]]
    summary = {
        "contract_ok": not failures,
        "failed_checks": failures,
        "declared_maxlength": contract["declared_maxlength"],
        "source_category_filters_available": contract["source_category_filters_available"],
    }
    if failures:
        return ProbeResult(1, payload, summary,
                           "页面结构与 cnki_search.webvpn 中的契约不一致，需要更新选择器。")
    return ProbeResult(0, payload, summary)


def _load_chinese_top_journals() -> list[str]:
    from catalog_lookup import journals_by_group
    return journals_by_group("chinese_top_journals")


_CHINESE_TOP_JOURNALS = _load_chinese_top_journals()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="WebVPN 专业检索页结构探针（需人工登录，不进 CI）")
    parser.add_argument("--home", required=True,
                        help="所在机构 WebVPN 改写后的知网首页地址")
    parser.add_argument("--output", required=True, type=Path, help="脱敏 JSON 证据输出路径")
    parser.add_argument("--submit", metavar="TOPIC", default=None,
                        help="额外提交一次 13 本中文顶尖期刊的定向检索（会消耗限流预算）")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = WebVpnConfig(home_url=args.home)
    result = asyncio.run(run_probe(config, submit_topic=args.submit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result.payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result.summary, ensure_ascii=False))
    if result.message:
        print(result.message, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
