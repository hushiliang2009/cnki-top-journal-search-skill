from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from catalog_lookup import normalize_title

from .models import PaperRecord


def _record_key(record: Mapping[str, Any]) -> tuple[str, ...]:
    doi = str(record.get("doi") or "").strip().casefold()
    if doi:
        return ("doi", re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi))
    title = normalize_title(str(record.get("title") or ""))
    authors = record.get("authors") or []
    first_author = normalize_title(str(authors[0])) if authors else ""
    year = str(record.get("year") or record.get("publication_year") or "")
    return ("metadata", title, first_author, year)


def merge_literature_results(
    ai4scholar_records: Iterable[Mapping[str, Any]], cnki_records: Iterable[PaperRecord],
) -> list[dict[str, Any]]:
    merged: dict[tuple[str, ...], dict[str, Any]] = {}
    for source_name, records in (
        ("ai4scholar", [dict(item) for item in ai4scholar_records]),
        ("CNKI", [item.to_dict() for item in cnki_records]),
    ):
        for record in records:
            key = _record_key(record)
            if key[1:] == ("", "", ""):
                key = ("unique", source_name, str(len(merged)))
            entry = merged.setdefault(key, {"canonical": record, "sources": [], "source_records": {}})
            if source_name not in entry["sources"]:
                entry["sources"].append(source_name)
            entry["source_records"][source_name] = record
    return list(merged.values())
