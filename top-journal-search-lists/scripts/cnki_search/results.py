from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser

from .models import PaperRecord


@dataclass(slots=True)
class ParsedResultPage:
    records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    total_rows: int
    excluded_non_journal_rows: int


def extract_publication_year(value: str) -> int | None:
    match = re.fullmatch(
        r"\s*((?:19|20)\d{2})(?:-(\d{2})(?:-(\d{2}))?)?"
        r"(?:\s+(\d{1,2}):(\d{2}))?\s*",
        value,
    )
    if not match:
        return None
    year, month, day, hour, minute = int(match[1]), match[2], match[3], match[4], match[5]
    try:
        date(year, int(month or 1), int(day or 1))
        if hour is not None and not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
            return None
    except ValueError:
        return None
    return year


@dataclass(slots=True)
class _RawRow:
    title: str = ""
    authors: str = ""
    journal: str = ""
    publication_date: str = ""
    document_type: str = ""
    citations: str = ""
    downloads: str = ""
    result_rank: str = ""
    is_online_first: bool = False


class _PublicTableParser(HTMLParser):
    _MAP = {
        "seq": "result_rank",
        "name": "title",
        "author": "authors",
        "source": "journal",
        "date": "publication_date",
        "data": "document_type",
        "quote": "citations",
        "download": "downloads",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.current: _RawRow | None = None
        self.cell: str | None = None
        self.buffer: list[str] = []
        self.rows: list[_RawRow] = []
        self.in_primary_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())
        if tag == "table" and "result-table-list" in classes:
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.current = _RawRow()
        elif self.current is not None and tag == "td":
            self.cell = next((name for name in self._MAP if name in classes), None)
            self.buffer = []
        elif self.current is not None and tag == "a" and self.cell in {"name", "source"}:
            self.in_primary_link = True

    def handle_data(self, data: str) -> None:
        text = data.strip()
        capture = self.cell not in {"name", "source"} or self.in_primary_link
        if self.current is not None and self.cell and text and capture:
            self.buffer.append(text)
        if self.current is not None and self.cell == "name" and text == "网络首发":
            self.current.is_online_first = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.in_primary_link = False
        elif tag == "td" and self.current is not None and self.cell:
            value = "".join(text for text in self.buffer if text != "网络首发").strip()
            setattr(self.current, self._MAP[self.cell], value)
            self.cell, self.buffer = None, []
        elif tag == "tr" and self.current is not None:
            if any((self.current.title, self.current.journal, self.current.document_type)):
                self.rows.append(self.current)
            self.current = None
        elif tag == "table" and self.in_table:
            self.in_table = False


def _to_int(value: str) -> int | None:
    return int(value) if re.fullmatch(r"\d+", value.strip()) else None


def _to_record(raw: _RawRow, *, query: str) -> PaperRecord:
    authors = [item.strip() for item in re.split(r"[;；,，]", raw.authors) if item.strip()]
    return PaperRecord(
        title=raw.title.strip(),
        authors=authors,
        journal_raw=raw.journal.strip(),
        publication_date=raw.publication_date.strip(),
        publication_year=extract_publication_year(raw.publication_date),
        document_type=raw.document_type.strip(),
        citations=_to_int(raw.citations),
        downloads=_to_int(raw.downloads),
        is_online_first=raw.is_online_first,
        result_rank=_to_int(raw.result_rank) or 0,
        source_database="CNKI",
        search_query=query,
    )


def parse_public_result_page(html: str, *, query: str, limit: int) -> ParsedResultPage:
    if not 1 <= limit <= 20:
        raise ValueError("返回数量必须为 1 到 20")
    parser = _PublicTableParser()
    parser.feed(html)
    records: list[PaperRecord] = []
    incomplete: list[PaperRecord] = []
    excluded = 0
    for raw in parser.rows:
        if raw.document_type != "期刊":
            excluded += 1
            continue
        record = _to_record(raw, query=query)
        if not record.title or not record.journal_raw or record.publication_year is None:
            incomplete.append(record)
        elif len(records) < limit:
            records.append(record)
    return ParsedResultPage(records, incomplete, len(parser.rows), excluded)
