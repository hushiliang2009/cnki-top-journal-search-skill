from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any

from .models import PaperRecord


def _split_values(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;；]", value) if part.strip()]


class _DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.title_parts: list[str] = []
        self.top_parts: list[str] = []
        self.abstract_parts: list[str] = []
        self.keyword_parts: list[str] = []
        self.fund_parts: list[str] = []
        self.authors: list[str] = []
        self.affiliations: list[str] = []
        self._brief_depth = 0
        self._top_depth = 0
        self._title_depth = 0
        self._title_aux_depth = 0
        self._abstract_depth = 0
        self._keyword_depth = 0
        self._fund_depth = 0
        self._author_depth = 0
        self._author_block = -1
        self._author_anchor_depth = 0
        self._anchor_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        for name in (
            "_brief_depth",
            "_top_depth",
            "_title_depth",
            "_title_aux_depth",
            "_abstract_depth",
            "_keyword_depth",
            "_fund_depth",
            "_author_depth",
            "_author_anchor_depth",
        ):
            depth = getattr(self, name)
            if depth:
                setattr(self, name, depth + 1)

        if tag == "meta":
            name = (attributes.get("name") or "").casefold()
            content = (attributes.get("content") or "").strip()
            if name.startswith("citation_") and content:
                self.meta.setdefault(name, []).append(content)
        if "brief" in classes and not self._brief_depth:
            self._brief_depth = 1
        if "top-tip" in classes and not self._top_depth:
            self._top_depth = 1
        if tag == "h1" and self._brief_depth and not self._title_depth:
            self._title_depth = 1
        if "type" in classes and self._title_depth and not self._title_aux_depth:
            self._title_aux_depth = 1
        if "abstract-text" in classes and not self._abstract_depth:
            self._abstract_depth = 1
        if "keywords" in classes and not self._keyword_depth:
            self._keyword_depth = 1
        if "funds" in classes and not self._fund_depth:
            self._fund_depth = 1
        if tag == "h3" and "author" in classes and not self._author_depth:
            self._author_block += 1
            self._author_depth = 1
        if tag == "a" and self._author_depth and not self._author_anchor_depth:
            self._author_anchor_depth = 1
            self._anchor_parts = []

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        if self._title_depth and not self._title_aux_depth:
            self.title_parts.append(value)
        if self._top_depth:
            self.top_parts.append(value)
        if self._abstract_depth:
            self.abstract_parts.append(value)
        if self._keyword_depth:
            self.keyword_parts.append(value)
        if self._fund_depth:
            self.fund_parts.append(value)
        if self._author_anchor_depth:
            self._anchor_parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if self._author_anchor_depth:
            self._author_anchor_depth -= 1
            if not self._author_anchor_depth:
                value = "".join(self._anchor_parts).strip()
                if value:
                    if self._author_block == 0:
                        value = re.sub(r"\d+$", "", value).strip()
                        target = self.authors
                    else:
                        value = re.sub(r"^\d+\s*[.．、]\s*", "", value).strip()
                        target = self.affiliations
                    target.append(value)
                self._anchor_parts = []
        for name in (
            "_author_depth",
            "_fund_depth",
            "_keyword_depth",
            "_abstract_depth",
            "_title_aux_depth",
            "_title_depth",
            "_top_depth",
            "_brief_depth",
        ):
            depth = getattr(self, name)
            if depth:
                setattr(self, name, depth - 1)


def parse_detail_page(html: str, base_record: PaperRecord | None = None) -> PaperRecord:
    parser = _DetailParser()
    parser.feed(html)
    data = base_record.to_dict() if base_record is not None else {"title": ""}

    title = "".join(parser.title_parts).strip()
    if not title:
        title = next(iter(parser.meta.get("citation_title", [])), "").strip()
    if title:
        data["title"] = title

    if parser.authors:
        data["authors"] = parser.authors
        data["first_author"] = parser.authors[0]
    elif parser.meta.get("citation_author"):
        data["authors"] = parser.meta["citation_author"]
        data["first_author"] = parser.meta["citation_author"][0]
    if parser.affiliations:
        data["affiliations"] = parser.affiliations

    top_text = " ".join(parser.top_parts)
    publication = re.search(
        r"^\s*(.+?)\s*\.\s*((?:19|20)\d{2})\s*\(([^)]+)\)\s*:\s*([0-9]+\s*[-–—]\s*[0-9]+)",
        top_text,
    )
    if publication:
        data["journal"] = publication.group(1).strip()
        data["year"] = int(publication.group(2))
        data["issue"] = publication.group(3).strip()
        data["pages"] = re.sub(r"\s+", "", publication.group(4))

    abstract = "".join(parser.abstract_parts).strip()
    keywords = "".join(parser.keyword_parts).strip()
    funds = "".join(parser.fund_parts).strip()
    if abstract:
        data["abstract"] = abstract
    if keywords:
        data["keywords"] = _split_values(keywords)
    if funds:
        data["funds"] = _split_values(funds)

    doi = next(iter(parser.meta.get("citation_doi", [])), "").strip()
    if doi:
        data["doi"] = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    return PaperRecord(**data)


class PlaywrightResultNavigator:
    def open_selected(self, result_page: Any, selected_index: int) -> Any:
        rows = result_page.locator("table.result-table-list tbody tr")
        if selected_index < 1 or selected_index > rows.count():
            raise IndexError("详情序号超出当前结果页范围")
        row = rows.nth(selected_index - 1)
        with result_page.context.expect_page() as new_page:
            row.locator("td.name a").first.click()
        detail_page = new_page.value
        detail_page.wait_for_load_state("domcontentloaded")
        return detail_page
