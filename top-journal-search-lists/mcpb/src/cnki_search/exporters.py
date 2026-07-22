from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import fields
from pathlib import Path
from typing import Iterable

from catalog_lookup import DEFAULT_CATALOG, lookup_journals

from .models import PaperRecord


def _normalized_doi(value: str) -> str:
    value = value.strip().casefold()
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)


def _normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value)


def record_identity(record: PaperRecord) -> tuple[str, ...]:
    doi = _normalized_doi(record.doi)
    if doi:
        return ("doi", doi)
    return (
        "metadata",
        _normalized_text(record.title),
        _normalized_text(record.first_author or (record.authors[0] if record.authors else "")),
        str(record.year or ""),
    )


def deduplicate_records(records: Iterable[PaperRecord]) -> list[PaperRecord]:
    unique: list[PaperRecord] = []
    seen: set[tuple[str, ...]] = set()
    for record in records:
        identity = record_identity(record)
        if identity not in seen:
            seen.add(identity)
            unique.append(record)
    return unique


def attach_journal_levels(
    records: Iterable[PaperRecord], catalog: Path = DEFAULT_CATALOG
) -> list[PaperRecord]:
    records = list(records)
    matches = lookup_journals(catalog, [record.journal for record in records])
    for record, match in zip(records, matches, strict=True):
        level = match.get("priority_level")
        group = match.get("priority_group")
        record.journal_level = f"{level}:{group}" if level is not None else "未匹配"
    return records


def _citation_key(record: PaperRecord, index: int) -> str:
    author = _normalized_text(record.first_author or "cnki") or "cnki"
    return f"{author}{record.year or 'nd'}_{index}"


def _bibtex(records: list[PaperRecord]) -> str:
    blocks: list[str] = []
    for index, record in enumerate(records, 1):
        values = {
            "title": record.title,
            "author": " and ".join(record.authors),
            "journal": record.journal,
            "year": str(record.year or ""),
            "volume": record.volume,
            "number": record.issue,
            "pages": record.pages,
            "doi": _normalized_doi(record.doi),
        }
        lines = [f"@article{{{_citation_key(record, index)},"]
        lines.extend(f"  {key} = {{{value}}}," for key, value in values.items() if value)
        lines.append("}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _ris(records: list[PaperRecord]) -> str:
    blocks: list[str] = []
    for record in records:
        lines = ["TY  - JOUR", f"TI  - {record.title}"]
        lines.extend(f"AU  - {author}" for author in record.authors)
        mapping = (("JO", record.journal), ("PY", record.year), ("VL", record.volume),
                   ("IS", record.issue), ("SP", record.pages), ("DO", _normalized_doi(record.doi)))
        lines.extend(f"{tag}  - {value}" for tag, value in mapping if value)
        lines.append("ER  -")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _gbt7714(records: list[PaperRecord]) -> str:
    lines: list[str] = []
    for index, record in enumerate(records, 1):
        authors = ", ".join(record.authors) or "佚名"
        issue = f"({record.issue})" if record.issue else ""
        pages = f": {record.pages}" if record.pages else ""
        doi = f". DOI:{_normalized_doi(record.doi)}" if record.doi else ""
        lines.append(
            f"[{index}] {authors}. {record.title}[J]. {record.journal}, "
            f"{record.year or '日期不详'}, {record.volume}{issue}{pages}{doi}."
        )
    return "\n".join(lines) + "\n"


def export_records(
    records: Iterable[PaperRecord], output_dir: Path, *, stem: str = "cnki-results"
) -> dict[str, Path]:
    records = list(records)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / f"{stem}.json",
        "csv": output_dir / f"{stem}.csv",
        "bibtex": output_dir / f"{stem}.bib",
        "ris": output_dir / f"{stem}.ris",
        "gbt7714": output_dir / f"{stem}.txt",
    }
    paths["json"].write_text(
        json.dumps([record.to_dict() for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    column_names = [field.name for field in fields(PaperRecord)]
    with paths["csv"].open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=column_names)
        writer.writeheader()
        for record in records:
            row = record.to_dict()
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = "; ".join(value)
            writer.writerow(row)
    paths["bibtex"].write_text(_bibtex(records), encoding="utf-8")
    paths["ris"].write_text(_ris(records), encoding="utf-8")
    paths["gbt7714"].write_text(_gbt7714(records), encoding="utf-8")
    return paths
