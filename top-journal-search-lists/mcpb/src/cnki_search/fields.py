from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FieldSpec:
    code: str
    label: str
    aliases: tuple[str, ...] = ()


_FIELDS = (
    FieldSpec("SU", "主题", ("subject",)),
    FieldSpec("TKA", "篇关摘", ("篇名关键词摘要",)),
    FieldSpec("KY", "关键词", ("keyword",)),
    FieldSpec("TI", "题名", ("篇名", "title")),
    FieldSpec("FT", "全文", ("fulltext",)),
    FieldSpec("AU", "作者", ("author",)),
    FieldSpec("FI", "第一作者", ("first_author",)),
    FieldSpec("RP", "通讯作者", ("corresponding_author",)),
    FieldSpec("AF", "作者单位", ("机构", "affiliation")),
    FieldSpec("AB", "摘要", ("abstract",)),
    FieldSpec("FU", "基金", ("fund",)),
    FieldSpec("CO", "来源期刊", ("期刊", "journal")),
    FieldSpec("RF", "参考文献", ("reference",)),
    FieldSpec("CLC", "中图分类号", ("分类号",)),
    FieldSpec("LY", "栏目", ("column",)),
    FieldSpec("SN", "ISSN", ()),
    FieldSpec("CN", "CN号", ("国内刊号",)),
    FieldSpec("DOI", "DOI", ()),
)

_INDEX: dict[str, FieldSpec] = {}
for _field in _FIELDS:
    for _name in (_field.code, _field.label, *_field.aliases):
        _INDEX[_name.casefold()] = _field


def resolve_field(name: str) -> FieldSpec:
    try:
        return _INDEX[name.strip().casefold()]
    except KeyError as exc:
        raise ValueError(f"不支持的 CNKI 检索字段: {name}") from exc


def supported_field_codes() -> frozenset[str]:
    return frozenset(field.code for field in _FIELDS)

