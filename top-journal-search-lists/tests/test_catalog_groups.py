import pytest

import catalog_lookup


def test_chinese_top_journals_group_has_exactly_thirteen_titles() -> None:
    titles = catalog_lookup.journals_by_group("chinese_top_journals")
    assert len(titles) == 13
    for expected in ("管理世界", "经济研究", "中国社会科学", "经济学(季刊)"):
        assert expected in titles


def test_cssci_group_excludes_the_thirteen_promoted_top_journals() -> None:
    """CSSCI 原表 674 行，其中 13 本同时是中文顶尖期刊。

    目录的去重口径是 highest_priority_wins，这 13 本被提升到层级 6，
    因此层级 9 只剩 661 本。分批数量按 661 计算，不是 674。
    """
    cssci = catalog_lookup.journals_by_group("cssci")
    chinese_top = catalog_lookup.journals_by_group("chinese_top_journals")
    assert len(cssci) == 661
    assert not set(cssci) & set(chinese_top)
    assert len(cssci) + len(chinese_top) == 674


def test_groups_are_sorted_and_unique() -> None:
    titles = catalog_lookup.journals_by_group("cssci")
    assert titles == sorted(titles)
    assert len(titles) == len(set(titles))


def test_unknown_group_raises_rather_than_returning_empty() -> None:
    """静默返回空列表会让调用方构造出一条没有 LY= 条件的表达式。"""
    with pytest.raises(ValueError):
        catalog_lookup.journals_by_group("no_such_group")


def test_thirteen_top_journals_fit_in_one_expression() -> None:
    from cnki_search import professional

    titles = catalog_lookup.journals_by_group("chinese_top_journals")
    batches = professional.build_batches("数字经济", titles)
    assert len(batches) == 1, "13 本顶刊必须能放进单条表达式，否则层级 6 检索会被拆批"
