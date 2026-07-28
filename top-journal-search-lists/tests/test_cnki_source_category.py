"""来源类别分面的契约测试。

分面只出现在结果页。曾据高级检索输入页错判为"来源类别筛选不存在"，
据此把 CSSCI 设计成枚举 661 本刊名的 5 批请求；实测分面一次请求即可，
且覆盖面更大。把这个事实钉住，避免再退回枚举方案。
"""
import asyncio

import pytest

from cnki_search import webvpn


class FacetLocator:
    def __init__(self, count: int = 1) -> None:
        self._count = count
        self.checked = False

    @property
    def first(self) -> "FacetLocator":
        return self

    async def count(self) -> int:
        return self._count

    async def check(self) -> None:
        self.checked = True


class FacetPage:
    """勾选分面后总数从 before 变成 after。"""

    def __init__(self, *, before: str = "2,378", after: str = "2,270",
                 facet_present: bool = True) -> None:
        self.before = before
        self.after = after
        self.locators: dict[str, FacetLocator] = {}
        self.facet_present = facet_present

    def locator(self, selector: str) -> FacetLocator:
        if selector not in self.locators:
            self.locators[selector] = FacetLocator(1 if self.facet_present else 0)
        return self.locators[selector]

    async def evaluate(self, _script: str, _arg=None):
        checked = any(item.checked for item in self.locators.values())
        return self.after if checked else self.before


def _driver(page) -> webvpn.ProfessionalSearchPage:
    return webvpn.ProfessionalSearchPage(page)


def test_cssci_facet_value_matches_the_observed_page() -> None:
    assert webvpn.SOURCE_CATEGORY_VALUES["CSSCI"] == "P0209"
    for name in ("北大核心", "AMI", "WJCI", "CSCD"):
        assert name in webvpn.SOURCE_CATEGORY_VALUES


def test_applying_the_facet_narrows_the_result_count() -> None:
    page = FacetPage(before="2,378", after="2,270")
    total = asyncio.run(_driver(page).apply_source_category("CSSCI"))
    assert total == "2,270"
    selector = webvpn.SOURCE_CATEGORY_SELECTOR.format(value="P0209")
    assert page.locators[selector].checked is True


def test_unknown_category_is_rejected_with_the_available_options() -> None:
    with pytest.raises(ValueError, match="未知的来源类别"):
        asyncio.run(_driver(FacetPage()).apply_source_category("SSCI"))


def test_missing_facet_points_at_the_real_precondition() -> None:
    """分面不在输入页上；报错要说清"先检索"，否则会被当成站点改版。"""
    with pytest.raises(webvpn.WebVpnNavigationError, match="需先完成一次检索"):
        asyncio.run(_driver(FacetPage(facet_present=False)).apply_source_category("CSSCI"))


def test_total_results_is_read_from_the_page() -> None:
    assert asyncio.run(_driver(FacetPage(before="1,234")).total_results()) == "1,234"
