"""学术期刊专业检索条件区的来源类别契约测试。

来源类别在先选择学术期刊后显示，并须在提交检索前勾选。CSSCI 仍按一次
来源类别检索覆盖，不退回枚举661本刊名的方案。
"""
import asyncio

import pytest

from cnki_search import webvpn
from cnki_search.professional import SourceCategorySpec


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

    async def is_checked(self) -> bool:
        return self.checked


class ResultRowsLocator:
    async def count(self) -> int:
        return 1


class FacetPage:
    """模拟来源类别条件控件，并保留结果总数读取能力。"""

    def __init__(self, *, before: str = "2,378", after: str = "2,270",
                 facet_present: bool = True) -> None:
        self.before = before
        self.after = after
        self.locators: dict[str, FacetLocator] = {}
        self.facet_present = facet_present

    def locator(self, selector: str) -> FacetLocator | ResultRowsLocator:
        if selector.startswith(webvpn.RESULT_TABLE_SELECTOR):
            return ResultRowsLocator()
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


def test_applying_source_category_checks_the_condition_before_submit() -> None:
    page = FacetPage(before="2,378", after="2,270")
    application = asyncio.run(
        _driver(page).apply_source_category(SourceCategorySpec("P0209", "CSSCI"))
    )
    assert application.applied is True
    assert application.total is None
    selector = webvpn.SOURCE_CATEGORY_SELECTOR.format(value="P0209")
    assert page.locators[selector].checked is True


def test_applying_controlled_category_uses_its_cnki_code() -> None:
    page = FacetPage(before="2,378", after="2,270")
    category = SourceCategorySpec("P0209", "CSSCI")

    application = asyncio.run(_driver(page).apply_source_category(category))

    assert application.applied is True
    assert application.total is None
    selector = webvpn.SOURCE_CATEGORY_SELECTOR.format(value="P0209")
    assert page.locators[selector].checked is True


def test_result_total_is_not_required_before_submit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """提交前尚无结果总数，只要唯一复选框已勾选即可。"""
    async def no_wait(_seconds: float) -> None:
        return None

    monkeypatch.setattr(webvpn.asyncio, "sleep", no_wait)
    page = FacetPage(before="50", after="50")

    application = asyncio.run(
        _driver(page).apply_source_category(
            SourceCategorySpec("P0209", "CSSCI"), timeout_seconds=5.0,
        )
    )

    assert application.applied is True
    assert application.total is None
    assert application.status is webvpn.SearchStatus.SUCCESS


def test_source_category_requires_a_closed_code_and_label_pair() -> None:
    with pytest.raises(ValueError):
        SourceCategorySpec("P0209", "SSCI")


def test_missing_source_category_reports_condition_area_failure() -> None:
    with pytest.raises(webvpn.WebVpnNavigationError, match="专业检索条件区"):
        asyncio.run(
            _driver(FacetPage(facet_present=False)).apply_source_category(
                SourceCategorySpec("P0209", "CSSCI")
            )
        )


def test_total_results_is_read_from_the_page() -> None:
    assert asyncio.run(_driver(FacetPage(before="1,234")).total_results()) == "1,234"
