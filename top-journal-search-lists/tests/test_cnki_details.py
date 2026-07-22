from pathlib import Path

from cnki_search.details import PlaywrightResultNavigator, parse_detail_page
from cnki_search.models import PaperRecord


class FakeNewPage:
    def __init__(self) -> None:
        self.waited = False

    def wait_for_load_state(self, state: str) -> None:
        assert state == "domcontentloaded"
        self.waited = True


class FakePageInfo:
    def __init__(self, page: FakeNewPage) -> None:
        self.value = page


class FakeExpectPage:
    def __init__(self, page: FakeNewPage) -> None:
        self.info = FakePageInfo(page)

    def __enter__(self) -> FakePageInfo:
        return self.info

    def __exit__(self, *_args) -> None:
        return None


class FakeLink:
    def __init__(self, actions: list[tuple]) -> None:
        self.actions = actions

    @property
    def first(self):
        return self

    def click(self) -> None:
        self.actions.append(("click", "official_title_link"))


class FakeRow:
    def __init__(self, actions: list[tuple], index: int) -> None:
        self.actions = actions
        self.index = index

    def locator(self, selector: str) -> FakeLink:
        self.actions.append(("locator", self.index, selector))
        return FakeLink(self.actions)


class FakeRows:
    def __init__(self, actions: list[tuple]) -> None:
        self.actions = actions

    def count(self) -> int:
        return 3

    def nth(self, index: int) -> FakeRow:
        return FakeRow(self.actions, index)


class FakeContext:
    def __init__(self, new_page: FakeNewPage) -> None:
        self.new_page = new_page

    def expect_page(self) -> FakeExpectPage:
        return FakeExpectPage(self.new_page)


class FakeResultPage:
    def __init__(self) -> None:
        self.actions: list[tuple] = []
        self.new_page = FakeNewPage()
        self.context = FakeContext(self.new_page)

    def locator(self, selector: str) -> FakeRows:
        self.actions.append(("locator", selector))
        return FakeRows(self.actions)

    def goto(self, _url: str) -> None:
        raise AssertionError("详情必须从当前结果页点击官方题名链接")


def test_detail_navigation_clicks_selected_result_without_direct_goto() -> None:
    page = FakeResultPage()
    detail = PlaywrightResultNavigator().open_selected(page, 2)
    assert detail is page.new_page
    assert detail.waited is True
    assert ("locator", 1, "td.name a") in page.actions
    assert ("click", "official_title_link") in page.actions


def test_real_cnki_detail_page_enriches_selected_record() -> None:
    html = (Path(__file__).with_name("fixtures") / "detail.html").read_text(
        encoding="utf-8"
    )
    base = PaperRecord(
        title="结果页题名",
        detail_url="https://kns.cnki.net/kcms2/article/abstract?id=1",
        journal_level="9:cssci",
        source_mode="cnki",
    )
    record = parse_detail_page(html, base)
    assert record.title == "数字化转型何以赋能探索式创新"
    assert record.authors == ["方鑫", "陆亮亮", "唐秋雨", "谢佩洪"]
    assert record.first_author == "方鑫"
    assert record.affiliations == [
        "合肥大学管理学院",
        "上海立信会计金融学院金融科技学院",
        "上海财经大学商学院",
        "上海对外经贸大学工商管理学院",
    ]
    assert record.journal == "技术经济与管理研究"
    assert record.year == 2026
    assert record.issue == "07"
    assert record.pages == "85-92"
    assert record.abstract == "数字化转型促进探索式创新。"
    assert record.keywords == ["数字化转型", "探索式创新", "企业吸收能力"]
    assert record.funds == ["安徽省教育厅青年项目", "合肥大学人才科研基金项目"]
    assert record.doi == "10.1234/example.detail"
    assert record.detail_url == base.detail_url
    assert record.journal_level == "9:cssci"
