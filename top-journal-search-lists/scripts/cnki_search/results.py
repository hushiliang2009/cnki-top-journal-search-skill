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
    """从 CNKI 发表时间提取四位年份。

    仍要求整体是一个合法日期（不放宽为"抓到四位数字就算"），但接受两种此前
    被整条丢弃的真实写法：带秒的时间戳与 `/` 日期分隔符。
    """
    match = re.fullmatch(
        r"\s*((?:19|20)\d{2})(?:[-/](\d{2})(?:[-/](\d{2}))?)?"
        r"(?:[\s]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?\s*",
        value,
    )
    if not match:
        return None
    year, month, day = int(match[1]), match[2], match[3]
    hour, minute, second = match[4], match[5], match[6]
    try:
        date(year, int(month or 1), int(day or 1))
    except ValueError:
        return None
    if hour is not None and not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
        return None
    if second is not None and not 0 <= int(second) <= 59:
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

    # 作者单元格里每个 <a> 是一位作者，闭合时压入分隔标记，否则会被粘连成
    # 单个字符串（"张三李四王五"）。分隔符取 _to_record 的切分字符之一。
    _AUTHOR_SEPARATOR = ";"

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        # 用深度计数而非布尔标志：结果表单元格内可能嵌套 <table>（如脚注、
        # 基金信息），其 </table> 会提前结束结果表，导致其后的全部题录被
        # 静默丢弃，且因 found_public_table 已为 True 而不触发契约异常。
        self.table_depth = 0
        self.current: _RawRow | None = None
        self.cell: str | None = None
        self.buffer: list[str] = []
        self.rows: list[_RawRow] = []
        self.in_primary_link = False
        self.found_public_table = False

    @property
    def in_result_row(self) -> bool:
        """仅结果表最外层（深度 1）的 tr/td 才是题录结构。"""
        return self.table_depth == 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())
        if tag == "table":
            if self.table_depth == 0 and "result-table-list" in classes:
                self.table_depth = 1
                self.found_public_table = True
            elif self.table_depth > 0:
                self.table_depth += 1
            return
        if not self.in_result_row:
            return
        if tag == "tr":
            self.current = _RawRow()
        elif self.current is not None and tag == "td":
            self.cell = next((name for name in self._MAP if name in classes), None)
            self.buffer = []
        elif self.current is not None and tag == "a" and self.cell in {"name", "source"}:
            self.in_primary_link = True

    def handle_data(self, data: str) -> None:
        if not self.in_result_row:
            return
        capture = self.cell not in {"name", "source"} or self.in_primary_link
        # 保留原始文本节点，包括纯空白节点：<em> 关键词高亮会把英文篇名切成
        # 多段，标签之间的空格自成一个文本节点。逐段 strip 会把它整段丢掉，
        # 拼接后就成了 "Supply ChainFinance"。末尾统一折叠空白并 strip。
        if self.current is not None and self.cell and capture:
            self.buffer.append(data)
        if self.current is not None and self.cell == "name" and data.strip() == "网络首发":
            self.current.is_online_first = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            if self.table_depth > 0:
                self.table_depth -= 1
            return
        if not self.in_result_row:
            return
        if tag == "a":
            self.in_primary_link = False
            if self.current is not None and self.cell == "author":
                self.buffer.append(self._AUTHOR_SEPARATOR)
        elif tag == "td" and self.current is not None and self.cell:
            joined = "".join(text for text in self.buffer if text.strip() != "网络首发")
            value = re.sub(r"\s+", " ", joined).strip()
            setattr(self.current, self._MAP[self.cell], value)
            self.cell, self.buffer = None, []
        elif tag == "tr" and self.current is not None:
            if any((self.current.title, self.current.journal, self.current.document_type)):
                self.rows.append(self.current)
            self.current = None


def _to_int(value: str) -> int | None:
    # CNKI 对四位以上的被引/下载量使用千分位分隔符（如 3,204）
    stripped = re.sub(r"[,，]", "", value.strip())
    return int(stripped) if re.fullmatch(r"\d+", stripped) else None


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
    if not parser.found_public_table and "题名" in html and "来源" in html:
        raise PageContractChanged("知网公开结果表结构已变化")
    if parser.found_public_table and not parser.rows:
        # 存在结果表容器却一行都没解析出来，说明标记形态超出预期。
        # 静默返回"无结果"会让一次失败的检索被写成"该主题无文献"。
        raise PageContractChanged("知网公开结果表存在但未解析出任何题录")
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
