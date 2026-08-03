"""环境期刊目录 v4.0 的不可变来源快照解析器。"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Literal, Mapping
import unicodedata


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
