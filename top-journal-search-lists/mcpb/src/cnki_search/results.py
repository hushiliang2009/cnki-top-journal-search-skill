from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin

from .models import PaperRecord


_FIELDS = {"title", "authors", "journal", "year", "doi", "abstract", "keywords"}


class _ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.field: str | None = None
        self.depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if "result-item" in classes:
            self.current = {}
            self.depth = 1
            return
        if self.current is None:
            return
        self.depth += 1
        selected = next((name for name in _FIELDS if name in classes), None)
        if selected:
            self.field = selected
            if selected == "title" and attributes.get("href"):
                self.current["detail_url"] = attributes["href"] or ""

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.field and data.strip():
            self.current[self.field] = self.current.get(self.field, "") + data.strip()

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        self.depth -= 1
        self.field = None
        if self.depth == 0:
            self.items.append(self.current)
            self.current = None


class _TableResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, str]] = []
        self.table_depth = 0
        self.current: dict[str, str] | None = None
        self.cell: str | None = None
        self.cell_text: list[str] = []
        self.in_title_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "table" and "result-table-list" in classes:
            self.table_depth = 1
            return
        if not self.table_depth:
            return
        self.table_depth += 1
        if tag == "tr":
            self.current = {}
        elif tag == "td" and self.current is not None:
            self.cell = next(iter(classes), "")
            self.cell_text = []
        elif (
            tag == "a"
            and self.current is not None
            and self.cell == "name"
            and attributes.get("href")
        ):
            self.current["detail_url"] = attributes["href"] or ""
            self.in_title_link = True

    def handle_data(self, data: str) -> None:
        if (
            self.current is not None
            and self.cell is not None
            and data.strip()
            and (self.cell != "name" or self.in_title_link)
        ):
            self.cell_text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if not self.table_depth:
            return
        if tag == "a" and self.cell == "name":
            self.in_title_link = False
        if tag == "td" and self.current is not None and self.cell is not None:
            value = "".join(self.cell_text).strip()
            mapping = {
                "name": "title",
                "author": "authors",
                "source": "journal",
                "date": "year",
            }
            target = mapping.get(self.cell)
            if target:
                self.current[target] = value
            self.cell = None
            self.cell_text = []
        elif tag == "tr" and self.current is not None:
            if self.current.get("title"):
                self.items.append(self.current)
            self.current = None
        self.table_depth -= 1


def _split_people(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;；,，]", value) if part.strip()]


def parse_result_page(html: str, *, base_url: str) -> list[PaperRecord]:
    parser = _ResultParser()
    parser.feed(html)
    table_parser = _TableResultParser()
    table_parser.feed(html)
    searched_at = datetime.now(timezone.utc).isoformat()
    records: list[PaperRecord] = []
    for item in [*parser.items, *table_parser.items]:
        title = item.get("title", "").strip()
        if not title:
            continue
        authors = _split_people(item.get("authors", ""))
        year_text = item.get("year", "")
        year_match = re.search(r"(?:19|20)\d{2}", year_text)
        keywords = _split_people(item.get("keywords", ""))
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", item.get("doi", "").strip(), flags=re.I)
        records.append(
            PaperRecord(
                title=title,
                authors=authors,
                first_author=authors[0] if authors else "",
                journal=item.get("journal", "").strip(),
                year=int(year_match.group()) if year_match else None,
                abstract=item.get("abstract", "").strip(),
                keywords=keywords,
                doi=doi,
                detail_url=urljoin(base_url, item.get("detail_url", "")),
                source_mode="cnki",
                searched_at=searched_at,
            )
        )
    return records
