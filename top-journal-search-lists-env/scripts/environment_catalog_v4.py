"""环境期刊目录 v4.0 的不可变来源快照解析器。"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
from typing import Literal, Mapping
import unicodedata


PRIORITY_GROUPS = (
    "comprehensive_super_journals",
    "ncs_pnas_environment_flagships",
    "top_university_highest_consensus",
    "top_university_high_level",
    "environment_field_top",
    "chinese_environment_top",
    "other_formally_recognized",
    "environment_ssci",
    "environment_cssci",
    "environment_scie",
    "pku_core_natural_sciences",
    "pku_core_non_natural_sciences",
)

_LEVEL_HEADINGS = (
    "第一级：综合超一流主刊",
    "第二级：NCS、PNAS及环境旗舰子刊",
    "第三级：国内顶尖高校最高等级共识期刊",
    "第四级：国内顶尖高校高等级期刊",
    "第五级：广义环境学科各细分领域顶尖期刊",
    "第六级：中文顶尖期刊",
    "第七级：其他获得正式认可的高水平期刊",
    "第八级：环境相关SSCI期刊",
    "第九级：环境相关CSSCI期刊",
    "第十级：环境相关SCIE期刊",
    "第十一级：北大中文核心自然科学期刊",
    "第十二级：北大中文核心非自然科学期刊",
)

_EXPECTED_LEVEL_COUNTS = (4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561)

_DOCUMENT_EVIDENCE_IDS = {
    "上海交通大学环境科学与工程学院 AAAAA+（U5）": "sjtu_environment_u5",
    "上海交通大学环境科学与工程学院 AAAA（U4）": "sjtu_environment_u4",
    "上海交通大学环境科学与工程学院 AAA（U3）": "sjtu_environment_u3",
    "上海交通大学环境科学与工程学院 AA（U2）": "sjtu_environment_u2",
    "上海交通大学环境科学与工程学院 指定中文期刊（U1）": "sjtu_environment_u1",
    "南京大学环境学院 1区A类（U4）": "nju_environment_u4",
    "南京大学环境学院 1区B类（U3）": "nju_environment_u3",
    "南京大学环境学院 2区（U2）": "nju_environment_u2",
    "复旦大学环境科学与工程系 专业硕士认可期刊（U1）": "fudan_environment_u1",
    "学术期刊综合目录 内部顺序1": "academic_master_directory_1",
    "学术期刊综合目录 内部顺序2": "academic_master_directory_2",
    "学术期刊综合目录 内部顺序3": "academic_master_directory_3",
    "中国环境科学学会 T1": "csees_t1",
    "中国环境科学学会 T2": "csees_t2",
    "中国环境科学学会 T3": "csees_t3",
}

_SOURCE_ARTIFACTS = (
    (
        "CSSCI_2025_2026.md",
        "CSSCI",
        "2025-2026",
        32269,
        "09f48b9c38e6bf9644c0e7bcc1bd82ababb60474e8cba86b2eba93db654c766a",
    ),
    (
        "北大中文核心期刊目录_2023_自然科学版.md",
        "PKU_CORE_NATURAL",
        "2023",
        64392,
        "f2e807aa64acb850872be23d05b4eda411903d3c6efc6ff80d99cff01f3ef8de",
    ),
    (
        "北大中文核心期刊目录_2023_.md",
        "PKU_CORE_NON_NATURAL",
        "2023",
        37043,
        "6ef7d9832844a36dc12e318e586f8942b951c068a2a4ac3f8297824a5be3b891",
    ),
    (
        "Social Sciences Citation Index_20260715.md",
        "SSCI_DISPLAY",
        "2026-07-15",
        188504,
        "0c1c63386f53ce88f03a75cc4caefb5bb2dd5944573e5b9819948d0545e57c55",
    ),
    (
        "Social Sciences Citation Index (SSCI).csv",
        "SSCI",
        "2026-07-15",
        635202,
        "8436b3e9bd90cecba335490199ab917d6eb7732623824692d53e0b3efd1ab986",
    ),
    (
        "Science Citation Index Expanded_20260715.md",
        "SCIE_DISPLAY",
        "2026-07-15",
        560466,
        "40984893b8f50a6d4f9dd12553fbc33fc933ddabb93d967086b6e0c81e78f273",
    ),
    (
        "Science Citation Index Expanded (SCIE).csv",
        "SCIE",
        "2026-07-15",
        1758382,
        "4cb2ff6458bb426c94aaf58e27d7e1291d0169b51b235ab5f6be4bec448b8b36",
    ),
)

_SOURCE_FILE_ORDER = {artifact[0]: position for position, artifact in enumerate(_SOURCE_ARTIFACTS)}
_INDEX_MEMBERSHIP_ORDER = {"CSSCI": 0, "PKU_CORE": 1, "SSCI": 2, "SCIE": 3}
_LEVEL_SEVEN_CHINESE_IDS = tuple(f"ENVJ-{number:06d}" for number in range(169, 229))

CNKI_SCOPE_RULES = {
    "chinese_environment_top": ("exact_titles", None, [6], None),
    "other_formally_recognized_chinese": ("exact_titles", None, [7], None),
    "environment_cssci": (
        "exact_titles",
        {"code": "P0209", "label": "CSSCI"},
        [9],
        "CSSCI",
    ),
    "pku_core": (
        "topic_only",
        {"code": "P01", "label": "北大核心"},
        list(range(1, 13)),
        "PKU_CORE",
    ),
}


@dataclass(slots=True)
class CatalogRecord:
    journal_id: str
    formal_title: str
    formal_title_evidence_ids: list[str]
    aliases: list[str]
    issn: list[str]
    eissn: list[str]
    priority_level: int
    priority_group: str
    priority_decision: dict[str, object]
    ncs_internal_rank: int | None
    environment_subfields: list[str]
    subject_categories: list[str]
    formal_evidence: list[str]
    evidence_ids: list[str]
    index_memberships: list[str]
    index_subject_categories: dict[str, list[str]]
    source_memberships: list[dict[str, object]]
    source_catalogs: list[str]
    catalog_version: str = "4.0"
    catalog_date: str = "2026-07-29"
    revision_date: str = "2026-07-31"
    manual_review_required: bool = False
    review_reasons: list[str] = field(default_factory=list)
    cnki_routing: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ControlledAlias:
    journal_id: str
    alias: str
    source: str


def _exact_key(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


_WOS_COLUMNS = frozenset(
    {
        "Journal title",
        "ISSN",
        "eISSN",
        "Publisher name",
        "Publisher address",
        "Languages",
        "Web of Science Categories",
    }
)

_DATABASE_TITLE_MAPPINGS = {
    "Wiley Interdisciplinary Reviews-Climate Change": "WIREs Climate Change",
    "Wiley Interdisciplinary Reviews-Energy and Environment": (
        "WIREs Energy and Environment"
    ),
    "Wiley Interdisciplinary Reviews-Water": "WIREs Water",
    "地理学报（北京）": "地理学报",
    "Archiv fur Molluskenkunde": "Archiv für Molluskenkunde",
    "ArcheoSciences-Revue d Archeometrie": "ArchéoSciences-Revue d Archeometrie",
    "Journal of Food Safety and Food Quality-Archiv fur Lebensmittelhygiene": (
        "Journal of Food Safety and Food Quality-Archiv für Lebensmittelhygiene"
    ),
    "Zeitschrift der Deutschen Gesellschaft fur Geowissenschaften": (
        "Zeitschrift der Deutschen Gesellschaft für Geowissenschaften"
    ),
    "Zeitschrift fur Geomorphologie": "Zeitschrift für Geomorphologie",
}


CONTROLLED_ALIASES = {
    _exact_key("Wiley Interdisciplinary Reviews-Climate Change"): ControlledAlias(
        "ENVJ-000549",
        "Wiley Interdisciplinary Reviews-Climate Change",
        "database_title_mapping",
    ),
    _exact_key("Wiley Interdisciplinary Reviews-Energy and Environment"): ControlledAlias(
        "ENVJ-002018",
        "Wiley Interdisciplinary Reviews-Energy and Environment",
        "database_title_mapping",
    ),
    _exact_key("Wiley Interdisciplinary Reviews-Water"): ControlledAlias(
        "ENVJ-000168", "Wiley Interdisciplinary Reviews-Water", "database_title_mapping"
    ),
    _exact_key("地理学报（北京）"): ControlledAlias(
        "ENVJ-000646", "地理学报（北京）", "database_title_mapping"
    ),
    _exact_key("Archiv fur Molluskenkunde"): ControlledAlias(
        "ENVJ-000902", "Archiv fur Molluskenkunde", "database_title_mapping"
    ),
    _exact_key("ArcheoSciences-Revue d Archeometrie"): ControlledAlias(
        "ENVJ-000910", "ArcheoSciences-Revue d Archeometrie", "database_title_mapping"
    ),
    _exact_key("Journal of Food Safety and Food Quality-Archiv fur Lebensmittelhygiene"): ControlledAlias(
        "ENVJ-001510",
        "Journal of Food Safety and Food Quality-Archiv fur Lebensmittelhygiene",
        "database_title_mapping",
    ),
    _exact_key("Zeitschrift der Deutschen Gesellschaft fur Geowissenschaften"): ControlledAlias(
        "ENVJ-002021",
        "Zeitschrift der Deutschen Gesellschaft fur Geowissenschaften",
        "database_title_mapping",
    ),
    _exact_key("Zeitschrift fur Geomorphologie"): ControlledAlias(
        "ENVJ-002022", "Zeitschrift fur Geomorphologie", "database_title_mapping"
    ),
}


@dataclass(frozen=True, slots=True)
class SourceRecord:
    index_name: str
    index_version: str
    source_file: str
    source_line: int
    source_record_id: str
    source_title: str
    formal_title: str
    aliases: tuple[str, ...]
    issn: tuple[str, ...]
    eissn: tuple[str, ...]
    subject_categories: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourcePaths:
    cssci_markdown: Path
    pku_natural: Path
    pku_non_natural: Path
    ssci_markdown: Path
    ssci_csv: Path
    scie_markdown: Path
    scie_csv: Path

    @classmethod
    def from_references(cls, references: Path) -> SourcePaths:
        return cls(
            cssci_markdown=references / "CSSCI_2025_2026.md",
            pku_natural=references / "北大中文核心期刊目录_2023_自然科学版.md",
            pku_non_natural=references / "北大中文核心期刊目录_2023_.md",
            ssci_markdown=references / "Social Sciences Citation Index_20260715.md",
            ssci_csv=references / "Social Sciences Citation Index (SSCI).csv",
            scie_markdown=references / "Science Citation Index Expanded_20260715.md",
            scie_csv=references / "Science Citation Index Expanded (SCIE).csv",
        )


@dataclass(frozen=True, slots=True)
class _MarkdownRow:
    line_number: int
    values: Mapping[str, str]


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        raise ValueError(f"不是 Markdown 表格行：{line!r}")
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_table_separator(line: str) -> bool:
    try:
        cells = _table_cells(line)
    except ValueError:
        return False
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _parse_named_markdown_table(path: Path, *, required: set[str]) -> list[_MarkdownRow]:
    """按表头名称读取一个或多个 Markdown 表格，保留物理行号。"""
    lines = _read_lines(path)
    rows: list[_MarkdownRow] = []
    line_index = 0
    while line_index + 1 < len(lines):
        if not lines[line_index].lstrip().startswith("|") or not _is_table_separator(
            lines[line_index + 1]
        ):
            line_index += 1
            continue

        headers = _table_cells(lines[line_index])
        if len(headers) != len(set(headers)):
            raise ValueError(f"{path} 的表头包含重复列：{headers}")
        if required.issubset(headers):
            row_index = line_index + 2
            while row_index < len(lines) and lines[row_index].lstrip().startswith("|"):
                cells = _table_cells(lines[row_index])
                if len(cells) != len(headers):
                    raise ValueError(
                        f"{path}:{row_index + 1} 的列数与表头不一致"
                    )
                rows.append(
                    _MarkdownRow(
                        line_number=row_index + 1,
                        values=dict(zip(headers, cells, strict=True)),
                    )
                )
                row_index += 1
            line_index = row_index
            continue
        line_index += 1
    if not rows:
        raise ValueError(f"{path} 中没有包含 {sorted(required)} 的 Markdown 表格")
    return rows


def _wos_title_key(title: str) -> str:
    return unicodedata.normalize("NFKC", title).strip().casefold()


def parse_wos_markdown(path: Path) -> dict[str, str]:
    """读取 WoS 人读目录，将数据库题名键映射到正式显示题名。"""
    display_titles: dict[str, str] = {}
    for line_number, line in enumerate(_read_lines(path), start=1):
        matched = re.match(r"^\d+\.\s+(.+?)\s*$", line)
        if matched is None:
            continue
        title = matched.group(1)
        key = _wos_title_key(title)
        previous = display_titles.setdefault(key, title)
        if previous != title:
            raise ValueError(
                f"{path}:{line_number} 的 WoS 显示题名与既有题名冲突：{title}"
            )
    if not display_titles:
        raise ValueError(f"{path} 中没有 WoS 期刊题名")
    return display_titles


def _identifier(value: str | None) -> tuple[str, ...]:
    value = (value or "").strip()
    return (value,) if value else ()


def parse_wos_csv(
    path: Path,
    index_name: Literal["SSCI", "SCIE"],
    *,
    display_titles: Mapping[str, str],
) -> list[SourceRecord]:
    """以 CSV 为机器输入解析 SSCI 或 SCIE，并以 Markdown 复核显示题名。"""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if fieldnames is None or set(fieldnames) != _WOS_COLUMNS:
            raise ValueError(f"{path} 的列名必须严格等于 {sorted(_WOS_COLUMNS)}")

        records: list[SourceRecord] = []
        for ordinal, row in enumerate(reader, start=1):
            source_title = (row["Journal title"] or "").strip()
            if not source_title:
                raise ValueError(f"{path}:{reader.line_num} 缺少 Journal title")
            display_title = display_titles.get(_wos_title_key(source_title), source_title)
            formal_title = _DATABASE_TITLE_MAPPINGS.get(display_title, display_title)
            categories = tuple(
                item.strip()
                for item in (row["Web of Science Categories"] or "").split("|")
                if item.strip()
            )
            records.append(
                SourceRecord(
                    index_name=index_name,
                    index_version="2026-07-15",
                    source_file=path.name,
                    source_line=reader.line_num,
                    source_record_id=f"{index_name}:{ordinal:05d}",
                    source_title=source_title,
                    formal_title=formal_title,
                    aliases=(),
                    issn=_identifier(row["ISSN"]),
                    eissn=_identifier(row["eISSN"]),
                    subject_categories=categories,
                )
            )
    return records


def parse_cssci_markdown(path: Path) -> list[SourceRecord]:
    rows = _parse_named_markdown_table(path, required={"序号", "期刊名称", "学科名称"})
    return [
        SourceRecord(
            index_name="CSSCI",
            index_version="2025-2026",
            source_file=path.name,
            source_line=row.line_number,
            source_record_id=f"CSSCI:{int(row.values['序号']):04d}",
            source_title=row.values["期刊名称"],
            formal_title=row.values["期刊名称"],
            aliases=(),
            issn=(),
            eissn=(),
            subject_categories=(row.values["学科名称"],),
        )
        for row in rows
    ]


def parse_pku_markdown(
    path: Path,
    branch: Literal["natural_sciences", "non_natural_sciences"],
) -> list[SourceRecord]:
    """解析北大核心表格，并将分类标题、代码及完整原刊名附于每条记录。"""
    lines = _read_lines(path)
    records: list[SourceRecord] = []
    classification = ""
    classification_code = ""
    line_index = 0
    while line_index < len(lines):
        heading = re.match(r"^###\s+(.+?)\s*$", lines[line_index])
        if heading is not None:
            classification = heading.group(1)
            classification_code = ""
            line_index += 1
            continue

        code = re.match(r"^分类代码：`(.+)`。\s*$", lines[line_index])
        if code is not None:
            classification_code = code.group(1)
            line_index += 1
            continue

        if (
            line_index + 1 >= len(lines)
            or not lines[line_index].lstrip().startswith("|")
            or not _is_table_separator(lines[line_index + 1])
        ):
            line_index += 1
            continue

        headers = _table_cells(lines[line_index])
        required = {"顺序", "原目录序号", "期刊名称", "备注"}
        if not required.issubset(headers):
            line_index += 1
            continue
        if not classification:
            raise ValueError(f"{path}:{line_index + 1} 的北大核心表格缺少 ### 分类标题")

        row_index = line_index + 2
        while row_index < len(lines) and lines[row_index].lstrip().startswith("|"):
            cells = _table_cells(lines[row_index])
            if len(cells) != len(headers):
                raise ValueError(f"{path}:{row_index + 1} 的列数与表头不一致")
            values = dict(zip(headers, cells, strict=True))
            source_title = values["期刊名称"]
            remark = values["备注"]
            aliases = (
                (remark.removeprefix("原刊名：").strip(),)
                if remark.startswith("原刊名：")
                else ()
            )
            categories = tuple(
                value for value in (classification, classification_code) if value
            )
            ordinal = int(values["原目录序号"])
            records.append(
                SourceRecord(
                    index_name="PKU_CORE",
                    index_version="2023",
                    source_file=path.name,
                    source_line=row_index + 1,
                    source_record_id=f"PKU_CORE:{branch}:{ordinal:04d}",
                    source_title=source_title,
                    formal_title=source_title,
                    aliases=aliases,
                    issn=(),
                    eissn=(),
                    subject_categories=categories,
                )
            )
            row_index += 1
        line_index = row_index
    if not records:
        raise ValueError(f"{path} 中没有北大核心期刊记录")
    return records


def _split_markdown_breaks(value: str) -> list[str]:
    return [item.strip() for item in value.split("<br>") if item.strip() and item.strip() != "—"]


def _baseline_title(value: str) -> tuple[str, int | None]:
    parts = _split_markdown_breaks(value)
    if not parts:
        raise ValueError("期刊名称不能为空")
    rank = None
    for part in parts[1:]:
        matched = re.fullmatch(r"内部顺序：(\d+)", part)
        if matched is not None:
            rank = int(matched.group(1))
    return parts[0], rank


def _baseline_region(path: Path) -> list[tuple[int, str]]:
    lines = _read_lines(path)
    try:
        start = lines.index("## 四、十二级主目录") + 1
    except ValueError as exc:
        raise ValueError(f"{path} 缺少十二级主目录") from exc

    try:
        end = next(
            index
            for index in range(start, len(lines))
            if lines[index].startswith("## 附录一")
        )
    except StopIteration as exc:
        raise ValueError(f"{path} 缺少附录一分界") from exc
    return [(index + 1, line) for index, line in enumerate(lines[start:end], start)]


def _baseline_tables(path: Path) -> list[tuple[int, list[_MarkdownRow]]]:
    region = _baseline_region(path)
    tables: list[tuple[int, list[_MarkdownRow]]] = []
    priority_level: int | None = None
    line_index = 0

    while line_index < len(region):
        line_number, line = region[line_index]
        heading = re.fullmatch(r"###\s+(.+)", line)
        if heading is not None:
            try:
                priority_level = _LEVEL_HEADINGS.index(heading.group(1)) + 1
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number} 的分级标题不受支持") from exc
            line_index += 1
            continue

        if (
            priority_level is None
            or line_index + 1 >= len(region)
            or not line.lstrip().startswith("|")
            or not _is_table_separator(region[line_index + 1][1])
        ):
            line_index += 1
            continue

        headers = _table_cells(line)
        if len(headers) != len(set(headers)):
            raise ValueError(f"{path}:{line_number} 的表头包含重复列：{headers}")
        if "序号" not in headers or not {
            "期刊名称",
            "基线题名",
            "正式题名",
        }.intersection(headers):
            line_index += 1
            continue

        rows: list[_MarkdownRow] = []
        row_index = line_index + 2
        while row_index < len(region) and region[row_index][1].lstrip().startswith("|"):
            row_line_number, row_line = region[row_index]
            cells = _table_cells(row_line)
            if len(cells) != len(headers):
                raise ValueError(f"{path}:{row_line_number} 的列数与表头不一致")
            rows.append(
                _MarkdownRow(
                    line_number=row_line_number,
                    values=dict(zip(headers, cells, strict=True)),
                )
            )
            row_index += 1
        tables.append((priority_level, rows))
        line_index = row_index

    return tables


def parse_v4_baseline(path: Path) -> list[CatalogRecord]:
    """解析批准的十二级目录，保留层级、级内顺序和已有稳定编号。"""
    tables = _baseline_tables(path)
    table_levels = tuple(level for level, _ in tables)
    if table_levels != tuple(range(1, 13)):
        raise ValueError(f"{path} 的十二级表格不完整或顺序错误：{table_levels}")

    records: list[CatalogRecord] = []
    counts: list[int] = []
    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    for priority_level, rows in tables:
        counts.append(len(rows))
        for row in rows:
            values = row.values
            is_generated = "期刊ID" in values or "正式题名" in values
            if is_generated and "基线题名" not in values:
                raise ValueError(
                    f"{path}:{row.line_number} 的生成目录缺少基线题名列"
                )
            baseline_cell = values.get("基线题名", values.get("期刊名称", ""))
            baseline_title, ncs_internal_rank = _baseline_title(baseline_cell)
            formal_title = values.get("正式题名", baseline_title).strip() or baseline_title
            journal_id = values.get("期刊ID", "").strip() or f"ENVJ-{len(records) + 1:06d}"
            if journal_id in seen_ids:
                raise ValueError(f"{path}:{row.line_number} 的期刊ID重复：{journal_id}")
            if formal_title in seen_titles:
                raise ValueError(f"{path}:{row.line_number} 的正式题名重复：{formal_title}")
            seen_ids.add(journal_id)
            seen_titles.add(formal_title)

            subfields = _split_markdown_breaks(values.get("环境细分领域", ""))
            formal_evidence = _split_markdown_breaks(values.get("正式证据", ""))
            evidence_ids = [
                _DOCUMENT_EVIDENCE_IDS[item]
                for item in formal_evidence
                if item in _DOCUMENT_EVIDENCE_IDS
            ]
            records.append(
                CatalogRecord(
                    journal_id=journal_id,
                    formal_title=formal_title,
                    formal_title_evidence_ids=[],
                    aliases=[],
                    issn=[],
                    eissn=[],
                    priority_level=priority_level,
                    priority_group=PRIORITY_GROUPS[priority_level - 1],
                    priority_decision={"baseline_title": baseline_title},
                    ncs_internal_rank=ncs_internal_rank,
                    environment_subfields=subfields,
                    subject_categories=[],
                    formal_evidence=formal_evidence,
                    evidence_ids=evidence_ids,
                    index_memberships=[],
                    index_subject_categories={},
                    source_memberships=[],
                    source_catalogs=[],
                )
            )

    if tuple(counts) != _EXPECTED_LEVEL_COUNTS:
        raise ValueError(f"{path} 的各级期刊数错误：{tuple(counts)}")
    return records


def priority_signature(
    records: list[CatalogRecord],
) -> tuple[tuple[str, int, str, int | None], ...]:
    """返回用于验证目录身份和判级不可变性的稳定签名。"""
    return tuple(
        (
            record.journal_id,
            record.priority_level,
            record.priority_group,
            record.ncs_internal_rank,
        )
        for record in records
    )


@dataclass(frozen=True, slots=True)
class MatchIndexes:
    by_identifier: dict[str, tuple[CatalogRecord, ...]]
    by_exact_title: dict[str, tuple[CatalogRecord, ...]]
    by_conservative_title: dict[str, tuple[CatalogRecord, ...]]
    by_journal_id: dict[str, CatalogRecord]


@dataclass(frozen=True, slots=True)
class MatchDecision:
    record: CatalogRecord | None
    match_method: str
    candidates: tuple[CatalogRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class AuditRecord:
    index_name: str
    index_version: str
    source_file: str
    source_line: int
    source_record_id: str
    source_title: str
    formal_title: str
    candidate_journal_ids: tuple[str, ...]
    match_method: str
    status: Literal[
        "matched", "out_of_scope", "ambiguous", "expected_but_unmatched"
    ]
    journal_id: str | None
    added_index_membership: bool
    priority_before: int | None
    priority_after: int | None
    manual_review_required: bool
    review_reasons: tuple[str, ...]


@dataclass(slots=True)
class CatalogBundle:
    records: list[CatalogRecord]
    audit: list[AuditRecord]
    match_counts: dict[str, tuple[int, int, int]]
    intersections: dict[str, int]
    zero_intersections: dict[str, int]
    controlled_alias_count: int
    expected_but_unmatched_count: int
    ambiguous_count: int
    catalog_payload: dict[str, object]
    source_registry: dict[str, object]


def _nfkc_text_key(value: str) -> tuple[str, str]:
    return (unicodedata.normalize("NFKC", value), value)


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(item) for item in value)
    return False


def _canonicalize(value: object) -> object:
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("规范 JSON 的对象键必须为字符串")
        return {key: _canonicalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"规范 JSON 不支持 {type(value).__name__}")


def canonical_json_bytes(value: object) -> bytes:
    """Return the UTF-8, LF-terminated canonical JSON representation."""
    if _contains_float(value):
        raise TypeError("规范目录不得包含浮点数")
    text = json.dumps(
        _canonicalize(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def compute_data_sha256(payload: Mapping[str, object]) -> str:
    draft = dict(payload)
    draft["data_sha256"] = "{{DATA_SHA256}}"
    return hashlib.sha256(canonical_json_bytes(draft)).hexdigest()


def _sorted_strings(values: list[str]) -> list[str]:
    return sorted(set(values), key=_nfkc_text_key)


def _source_membership_key(value: Mapping[str, object]) -> tuple[int, int, str]:
    filename = str(value["source_file"])
    return (
        _SOURCE_FILE_ORDER[filename],
        int(value["source_line"]),
        str(value["source_record_id"]),
    )


def _record_payload(record: CatalogRecord) -> dict[str, object]:
    source_memberships = sorted(record.source_memberships, key=_source_membership_key)
    index_memberships = sorted(
        record.index_memberships,
        key=lambda value: (_INDEX_MEMBERSHIP_ORDER[value], value),
    )
    return {
        "journal_id": record.journal_id,
        "formal_title": record.formal_title,
        "formal_title_evidence_ids": _sorted_strings(record.formal_title_evidence_ids),
        "aliases": _sorted_strings(record.aliases),
        "issn": _sorted_strings(record.issn),
        "eissn": _sorted_strings(record.eissn),
        "priority_level": record.priority_level,
        "priority_group": record.priority_group,
        "priority_decision": dict(record.priority_decision),
        "ncs_internal_rank": record.ncs_internal_rank,
        "environment_subfields": _sorted_strings(record.environment_subfields),
        "subject_categories": _sorted_strings(record.subject_categories),
        "formal_evidence": _sorted_strings(record.formal_evidence),
        "evidence_ids": _sorted_strings(record.evidence_ids),
        "index_memberships": index_memberships,
        "index_subject_categories": {
            key: _sorted_strings(value)
            for key, value in sorted(record.index_subject_categories.items())
        },
        "source_memberships": [
            {
                **membership,
                "subject_categories": _sorted_strings(
                    list(membership["subject_categories"])
                ),
            }
            for membership in source_memberships
        ],
        "source_catalogs": sorted(
            set(record.source_catalogs),
            key=lambda value: (_INDEX_MEMBERSHIP_ORDER[value], value),
        ),
        "catalog_version": record.catalog_version,
        "catalog_date": record.catalog_date,
        "revision_date": record.revision_date,
        "manual_review_required": record.manual_review_required,
        "review_reasons": _sorted_strings(record.review_reasons),
        "cnki_routing": dict(record.cnki_routing),
    }


def _build_cnki_scopes(records: list[CatalogRecord]) -> dict[str, object]:
    by_id = {record.journal_id: record for record in records}
    scopes: dict[str, object] = {}
    for scope_id, (selector, source_category, levels, membership) in CNKI_SCOPE_RULES.items():
        if scope_id == "other_formally_recognized_chinese":
            selected = [by_id[journal_id] for journal_id in _LEVEL_SEVEN_CHINESE_IDS]
        else:
            selected = [
                record
                for record in records
                if record.priority_level in levels
                and (membership is None or membership in record.index_memberships)
            ]
        selected.sort(key=lambda record: record.journal_id)
        scopes[scope_id] = {
            "scope_id": scope_id,
            "journal_selector": selector,
            "source_category": source_category,
            "journal_titles": [record.formal_title for record in selected],
            "eligible_journal_ids": [record.journal_id for record in selected],
            "eligible_priority_levels": list(levels),
            "required_index_membership": membership,
            "result_filter": "matched_journal_id",
        }
    expected_counts = {
        "chinese_environment_top": 6,
        "other_formally_recognized_chinese": 60,
        "environment_cssci": 241,
        "pku_core": 1987,
    }
    actual_counts = {
        scope_id: len(scope["eligible_journal_ids"])
        for scope_id, scope in scopes.items()
    }
    if actual_counts != expected_counts:
        raise ValueError(f"CNKI 范围数量错误：{actual_counts}")
    return scopes


def _source_registry(paths: SourcePaths) -> dict[str, object]:
    path_by_name = {
        path.name: path
        for path in (
            paths.cssci_markdown,
            paths.pku_natural,
            paths.pku_non_natural,
            paths.ssci_markdown,
            paths.ssci_csv,
            paths.scie_markdown,
            paths.scie_csv,
        )
    }
    artifacts: list[dict[str, object]] = []
    for filename, source_name, version, expected_bytes, expected_sha256 in _SOURCE_ARTIFACTS:
        path = path_by_name.get(filename)
        if path is None:
            raise ValueError(f"缺少批准的来源快照：{filename}")
        content = path.read_bytes()
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if len(content) != expected_bytes or actual_sha256 != expected_sha256:
            raise ValueError(f"来源快照未通过字节或 SHA-256 校验：{filename}")
        artifacts.append(
            {
                "filename": filename,
                "source_name": source_name,
                "version": version,
                "bytes": expected_bytes,
                "sha256": expected_sha256,
            }
        )
    evidence_registry = [
        {"evidence_id": evidence_id, "evidence_text": evidence_text}
        for evidence_text, evidence_id in _DOCUMENT_EVIDENCE_IDS.items()
    ]
    return {"artifacts": artifacts, "evidence_registry": evidence_registry}


def _catalog_payload(records: list[CatalogRecord]) -> dict[str, object]:
    journals = [_record_payload(record) for record in sorted(records, key=lambda item: item.journal_id)]
    return {
        "schema_version": "1.0",
        "catalog_version": "4.0",
        "catalog_date": "2026-07-29",
        "revision_date": "2026-07-31",
        "data_sha256": "{{DATA_SHA256}}",
        "level_counts": list(_EXPECTED_LEVEL_COUNTS),
        "priority_groups": list(PRIORITY_GROUPS),
        "journals": journals,
        "cnki_scopes": _build_cnki_scopes(records),
    }


def validate_generated_bundle(
    bundle: CatalogBundle,
    audit: list[AuditRecord],
) -> dict[str, object]:
    payload = bundle.catalog_payload
    if payload["data_sha256"] != compute_data_sha256(payload):
        raise ValueError("目录 JSON 哈希校验失败")
    if len(payload["journals"]) != 3764:
        raise ValueError("目录 JSON 期刊数量错误")
    if tuple(payload["level_counts"]) != _EXPECTED_LEVEL_COUNTS:
        raise ValueError("目录 JSON 层级数量错误")
    if priority_signature(bundle.records) != priority_signature(
        sorted(bundle.records, key=lambda item: item.journal_id)
    ):
        raise ValueError("目录优先级签名顺序错误")
    registry = bundle.source_registry
    artifacts = registry["artifacts"]
    evidence = registry["evidence_registry"]
    if len(artifacts) != 7 or len({item["filename"] for item in artifacts}) != 7:
        raise ValueError("来源登记表必须包含七份唯一快照")
    evidence_ids = [item["evidence_id"] for item in evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("文档证据 ID 必须唯一")
    referenced = {
        evidence_id
        for record in payload["journals"]
        for evidence_id in record["evidence_ids"] + record["formal_title_evidence_ids"]
    }
    if not referenced <= set(evidence_ids):
        raise ValueError("期刊证据 ID 未在来源登记表中解析")
    if audit != bundle.audit:
        raise ValueError("目录审计记录必须与构建产物一致")
    return {
        "data_sha256": payload["data_sha256"],
        "journal_count": len(payload["journals"]),
        "audit_count": len(audit),
    }


def _conservative_key(value: str) -> str:
    normalized = _exact_key(value)
    if normalized.startswith("the "):
        normalized = normalized[4:]
    normalized = normalized.replace("&", " and ")
    return re.sub(r"[\s.,:;·()\[\]{}'\"/\\-]+", "", normalized)


def _index_records(records: list[CatalogRecord]) -> MatchIndexes:
    by_identifier: dict[str, list[CatalogRecord]] = {}
    by_exact_title: dict[str, list[CatalogRecord]] = {}
    by_conservative_title: dict[str, list[CatalogRecord]] = {}
    by_journal_id = {record.journal_id: record for record in records}
    for record in records:
        by_exact_title.setdefault(_exact_key(record.formal_title), []).append(record)
        by_conservative_title.setdefault(_conservative_key(record.formal_title), []).append(
            record
        )
        for identifier in (*record.issn, *record.eissn):
            by_identifier.setdefault(identifier, []).append(record)
    return MatchIndexes(
        by_identifier={key: tuple(value) for key, value in by_identifier.items()},
        by_exact_title={key: tuple(value) for key, value in by_exact_title.items()},
        by_conservative_title={
            key: tuple(value) for key, value in by_conservative_title.items()
        },
        by_journal_id=by_journal_id,
    )


def _match_one(
    indexes: MatchIndexes,
    source: SourceRecord,
    controlled_aliases: Mapping[str, ControlledAlias],
) -> MatchDecision:
    for identifier in (*source.issn, *source.eissn):
        candidates = indexes.by_identifier.get(identifier, ())
        if len(candidates) == 1:
            return MatchDecision(candidates[0], "identifier")
        if len(candidates) > 1:
            return MatchDecision(None, "identifier_conflict", candidates)
    candidates = indexes.by_exact_title.get(_exact_key(source.formal_title), ())
    if len(candidates) == 1:
        return MatchDecision(candidates[0], "formal_title_exact")
    alias = controlled_aliases.get(_exact_key(source.formal_title))
    if alias is not None:
        return MatchDecision(indexes.by_journal_id[alias.journal_id], "controlled_alias")
    candidates = indexes.by_conservative_title.get(_conservative_key(source.formal_title), ())
    if len(candidates) == 1:
        return MatchDecision(candidates[0], "conservative_normalized")
    return MatchDecision(None, "ambiguous" if candidates else "out_of_scope", candidates)


def _build_controlled_aliases(
    records: list[CatalogRecord], source_records: list[SourceRecord]
) -> dict[str, ControlledAlias]:
    by_title = {_exact_key(record.formal_title): record for record in records}
    aliases = dict(CONTROLLED_ALIASES)
    for source in source_records:
        if source.index_name != "PKU_CORE" or not source.aliases:
            continue
        target = by_title[_exact_key(source.formal_title)]
        for original_title in source.aliases:
            aliases[_exact_key(original_title)] = ControlledAlias(
                target.journal_id, original_title, "pku_original_title"
            )
    if len(aliases) != 26:
        raise ValueError(f"受控别名数应为26，实际为{len(aliases)}")
    for alias in aliases.values():
        target = next(record for record in records if record.journal_id == alias.journal_id)
        if alias.alias not in target.aliases:
            target.aliases.append(alias.alias)
    return aliases


def _bind_source_membership(
    record: CatalogRecord, source: SourceRecord, match_method: str
) -> bool:
    membership = {
        "index_name": source.index_name,
        "index_version": source.index_version,
        "source_title": source.source_title,
        "source_record_id": source.source_record_id,
        "source_file": source.source_file,
        "source_line": source.source_line,
        "subject_categories": list(source.subject_categories),
        "match_method": match_method,
    }
    if membership in record.source_memberships:
        return False
    added_index = source.index_name not in record.index_memberships
    if added_index:
        record.index_memberships.append(source.index_name)
    record.index_subject_categories.setdefault(source.index_name, [])
    for category in source.subject_categories:
        if category not in record.index_subject_categories[source.index_name]:
            record.index_subject_categories[source.index_name].append(category)
    record.source_memberships.append(membership)
    if source.index_name not in record.source_catalogs:
        record.source_catalogs.append(source.index_name)
    for identifier in source.issn:
        if identifier not in record.issn:
            record.issn.append(identifier)
    for identifier in source.eissn:
        if identifier not in record.eissn:
            record.eissn.append(identifier)
    return added_index


def _register_identifiers(
    indexes: MatchIndexes, record: CatalogRecord, source: SourceRecord
) -> None:
    for identifier in (*source.issn, *source.eissn):
        candidates = indexes.by_identifier.get(identifier, ())
        if record not in candidates:
            indexes.by_identifier[identifier] = (*candidates, record)


def match_source_records(
    records: list[CatalogRecord],
    source_records: list[SourceRecord],
    *,
    controlled_aliases: Mapping[str, ControlledAlias],
) -> list[AuditRecord]:
    """按批准顺序匹配来源记录，并只在无标识符冲突时补充元数据。"""
    audit: list[AuditRecord] = []
    indexes = _index_records(records)
    for source in source_records:
        decision = _match_one(indexes, source, controlled_aliases)
        if decision.record is None:
            status: Literal[
                "matched", "out_of_scope", "ambiguous", "expected_but_unmatched"
            ] = "ambiguous" if decision.match_method != "out_of_scope" else "out_of_scope"
            audit.append(
                AuditRecord(
                    source.index_name,
                    source.index_version,
                    source.source_file,
                    source.source_line,
                    source.source_record_id,
                    source.source_title,
                    source.formal_title,
                    tuple(candidate.journal_id for candidate in decision.candidates),
                    decision.match_method,
                    status,
                    None,
                    False,
                    None,
                    None,
                    status == "ambiguous",
                    (decision.match_method,) if status == "ambiguous" else (),
                )
            )
            continue

        record = decision.record
        conflicting = [
            identifier
            for identifier in (*source.issn, *source.eissn)
            if identifier in indexes.by_identifier
            and record not in indexes.by_identifier[identifier]
        ]
        if conflicting:
            audit.append(
                AuditRecord(
                    source.index_name,
                    source.index_version,
                    source.source_file,
                    source.source_line,
                    source.source_record_id,
                    source.source_title,
                    source.formal_title,
                    (record.journal_id,),
                    "identifier_conflict",
                    "ambiguous",
                    None,
                    False,
                    None,
                    None,
                    True,
                    tuple(conflicting),
                )
            )
            continue
        before = record.priority_level
        added_index = _bind_source_membership(record, source, decision.match_method)
        _register_identifiers(indexes, record, source)
        audit.append(
            AuditRecord(
                source.index_name,
                source.index_version,
                source.source_file,
                source.source_line,
                source.source_record_id,
                source.source_title,
                source.formal_title,
                (record.journal_id,),
                decision.match_method,
                "matched",
                record.journal_id,
                added_index,
                before,
                record.priority_level,
                False,
                (),
            )
        )
    expected_index_by_level = {
        8: "SSCI",
        9: "CSSCI",
        10: "SCIE",
        11: "PKU_CORE",
        12: "PKU_CORE",
    }
    for record in records:
        expected_index = expected_index_by_level.get(record.priority_level)
        if expected_index is None or expected_index in record.index_memberships:
            continue
        audit.append(
            AuditRecord(
                expected_index,
                "catalog_expectation",
                "catalog_baseline",
                0,
                f"EXPECTED:{expected_index}:{record.journal_id}",
                record.formal_title,
                record.formal_title,
                (record.journal_id,),
                "expected_index_membership",
                "expected_but_unmatched",
                record.journal_id,
                False,
                record.priority_level,
                record.priority_level,
                True,
                (expected_index,),
            )
        )
    return audit


def _source_groups(paths: SourcePaths) -> list[tuple[str, list[SourceRecord]]]:
    return [
        ("CSSCI", parse_cssci_markdown(paths.cssci_markdown)),
        ("PKU_CORE_NATURAL", parse_pku_markdown(paths.pku_natural, "natural_sciences")),
        (
            "PKU_CORE_NON_NATURAL",
            parse_pku_markdown(paths.pku_non_natural, "non_natural_sciences"),
        ),
        (
            "SSCI",
            parse_wos_csv(
                paths.ssci_csv,
                "SSCI",
                display_titles=parse_wos_markdown(paths.ssci_markdown),
            ),
        ),
        (
            "SCIE",
            parse_wos_csv(
                paths.scie_csv,
                "SCIE",
                display_titles=parse_wos_markdown(paths.scie_markdown),
            ),
        ),
    ]


def _record_source_groups(record: CatalogRecord) -> set[str]:
    groups: set[str] = set()
    for membership in record.source_memberships:
        index_name = membership["index_name"]
        source_id = membership["source_record_id"]
        if index_name == "PKU_CORE":
            groups.add(
                "PKU_CORE_NATURAL"
                if ":natural_sciences:" in source_id
                else "PKU_CORE_NON_NATURAL"
            )
        else:
            groups.add(index_name)
    return groups


def _audit_matches_group(audit_record: AuditRecord, group_name: str) -> bool:
    if group_name == "PKU_CORE_NATURAL":
        return ":natural_sciences:" in audit_record.source_record_id
    if group_name == "PKU_CORE_NON_NATURAL":
        return ":non_natural_sciences:" in audit_record.source_record_id
    return audit_record.index_name == group_name


def build_catalog_bundle(baseline: Path, sources: SourcePaths) -> CatalogBundle:
    records = parse_v4_baseline(baseline)
    signature = priority_signature(records)
    source_groups = _source_groups(sources)
    source_records = [record for _, group in source_groups for record in group]
    controlled_aliases = _build_controlled_aliases(records, source_records)
    audit = match_source_records(
        records,
        source_records,
        controlled_aliases=controlled_aliases,
    )
    if priority_signature(records) != signature:
        raise ValueError("来源增补不得改变期刊身份或层级签名")
    for record in records:
        record.priority_decision["unchanged"] = True

    by_group = {
        group_name: {
            item.journal_id
            for item in records
            if group_name in _record_source_groups(item)
        }
        for group_name, _ in source_groups
    }
    match_counts = {
        group_name: (
            len(source),
            sum(
                item.status == "matched"
                and _audit_matches_group(item, group_name)
                for item in audit
            ),
            sum(
                item.status == "out_of_scope"
                and _audit_matches_group(item, group_name)
                for item in audit
            ),
        )
        for group_name, source in source_groups
    }
    group_names = tuple(by_group)
    all_intersections = {
        f"{left}&{right}": len(by_group[left] & by_group[right])
        for position, left in enumerate(group_names)
        for right in group_names[position + 1 :]
    }
    intersections = {
        key: value for key, value in all_intersections.items() if value
    }
    zero_intersections = {
        key: value for key, value in all_intersections.items() if not value
    }
    source_registry = _source_registry(sources)
    catalog_payload = _catalog_payload(records)
    catalog_payload["data_sha256"] = compute_data_sha256(catalog_payload)
    bundle = CatalogBundle(
        records,
        audit,
        match_counts,
        intersections,
        zero_intersections,
        len(controlled_aliases),
        sum(item.status == "expected_but_unmatched" for item in audit),
        sum(item.status == "ambiguous" for item in audit),
        catalog_payload,
        source_registry,
    )
    validate_generated_bundle(bundle, audit)
    return bundle
