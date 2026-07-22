import pytest

from cnki_search.fields import resolve_field


def test_resolve_field_supports_cnki_codes_and_chinese_names() -> None:
    assert resolve_field("主题").code == "SU"
    assert resolve_field("TKA").label == "篇关摘"
    assert resolve_field("DOI").code == "DOI"


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="不支持"):
        resolve_field("任意字段")
