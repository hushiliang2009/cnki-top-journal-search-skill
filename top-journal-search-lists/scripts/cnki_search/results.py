from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser

from .models import PaperRecord, is_verifiable_publication_year
from .search import PageContractChanged


@dataclass(slots=True)
class ParsedResultPage:
    records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    total_rows: int
    excluded_non_journal_rows: int


def extract_publication_year(value: str) -> int | None:
    match = re.search(
        r"(?<!\d)(?P<year>(?:19|20)\d{2})"
        r"(?:(?P<separator>[-/])(?P<month>\d{1,2})"
        r"(?:(?P=separator)(?P<day>\d{1,2}))?)?"
        r"(?:\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})(?::(?P<second>\d{2}))?)?"
        r"(?![\d年])",
        value,
    )
    if not match:
        return None
    year = int(match["year"])
    month, day = match["month"], match["day"]
    hour, minute, second = match["hour"], match["minute"], match["second"]
    try:
        date(year, int(month or 1), int(day or 1))
        if hour is not None and not (
            0 <= int(hour) <= 23 and 0 <= int(minute) <= 59 and 0 <= int(second or 0) <= 59
        ):
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
        self.table_depth = 0
        self.current: _RawRow | None = None
        self.cell: str | None = None
        self.buffer: list[str] = []
        self.rows: list[_RawRow] = []
        self.in_primary_link = False
        self.found_public_table = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())
        if tag == "table" and not self.in_table and "result-table-list" in classes:
            self.in_table = True
            self.table_depth = 1
            self.found_public_table = True
            return
        if tag == "table" and self.in_table:
            self.table_depth += 1
            return
        if not self.in_table or self.table_depth != 1:
            return
        if tag == "tr":
            self._finish_row()
            self.current = _RawRow()
        elif tag == "td" and self.current is not None:
            self._finish_cell()
            self.cell = next((name for name in self._MAP if name in classes), None)
            self.buffer = []
        elif self.current is not None and tag == "a" and self.cell in {"name", "source"}:
            self.in_primary_link = True

    def handle_data(self, data: str) -> None:
        if not self.in_table or self.table_depth != 1:
            return
        text = data.strip()
        capture = self.cell not in {"name", "source"} or self.in_primary_link
        if self.current is not None and self.cell and data and capture:
            self.buffer.append(data)
        if self.current is not None and self.cell == "name" and text == "网络首发":
            self.current.is_online_first = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self.in_table:
            self.table_depth -= 1
            if self.table_depth == 0:
                self._finish_row()
                self.in_table = False
            return
        if not self.in_table or self.table_depth != 1:
            return
        if tag == "a":
            if self.cell == "author":
                self.buffer.append(";")
            self.in_primary_link = False
        elif tag == "td":
            self._finish_cell()
        elif tag == "tr":
            self._finish_row()

    def finish(self) -> None:
        self._finish_row()

    def _finish_cell(self) -> None:
        if self.current is not None and self.cell:
            value = _collapse_whitespace("".join(self.buffer))
            setattr(self.current, self._MAP[self.cell], value)
        self.cell, self.buffer, self.in_primary_link = None, [], False

    def _finish_row(self) -> None:
        self._finish_cell()
        if self.current is not None and any(
            (self.current.title, self.current.journal, self.current.document_type)
        ):
            self.rows.append(self.current)
        self.current = None


def _collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _to_int(value: str) -> int | None:
    normalized = re.sub(r"[,，\s]", "", value)
    return int(normalized) if re.fullmatch(r"[0-9]+", normalized) else None


def _to_record(raw: _RawRow, *, query: str) -> PaperRecord:
    authors = [
        _collapse_whitespace(item)
        for item in re.split(r"[;；,，\n]", raw.authors)
        if _collapse_whitespace(item)
    ]
    return PaperRecord(
        title=_collapse_whitespace(raw.title),
        authors=authors,
        journal_raw=_collapse_whitespace(raw.journal),
        publication_date=_collapse_whitespace(raw.publication_date),
        publication_year=extract_publication_year(raw.publication_date),
        document_type=_collapse_whitespace(raw.document_type),
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
    parser.close()
    parser.finish()
    if not parser.found_public_table and "题名" in html and "来源" in html:
        raise PageContractChanged("知网公开结果表结构已变化")
    if parser.found_public_table and not parser.rows:
        raise PageContractChanged("知网公开结果表未解析到题录行")
    records: list[PaperRecord] = []
    incomplete: list[PaperRecord] = []
    excluded = 0
    for raw in parser.rows:
        if raw.document_type != "期刊":
            excluded += 1
            continue
        record = _to_record(raw, query=query)
        if not record.title or not record.journal_raw or not is_verifiable_publication_year(record.publication_year):
            incomplete.append(record)
        elif len(records) < limit:
            records.append(record)
    return ParsedResultPage(records, incomplete, len(parser.rows), excluded)
