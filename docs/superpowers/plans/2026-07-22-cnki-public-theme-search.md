# CNKI Public Theme Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `top-journal-search-lists` 中的 CNKI 功能收窄为无需登录的公开首页主题检索，返回具备篇名、期刊、发表年度和主目录期刊级别的备选论文清单。

**Architecture:** 使用 Playwright 的全新临时浏览器上下文打开 `https://www.cnki.net/`，只填写首页默认主题检索框并解析第一页公开结果。结果经严格题录校验后，由 `Academic_Journal_Master_Directory_20260715.md` 完成期刊名称匹配、学科分类和十级排序；MCP、Skill、MCPB及三个客户端共用同一份 Python 实现。

**Tech Stack:** Python 3.11+、Python 3.14 本机测试环境、Playwright 1.45+、FastMCP 1.x、pytest、PowerShell、uv、Markdown 综合期刊目录。

## Global Constraints

- CNKI 入口固定为 `https://www.cnki.net/`，检索字段固定为主题。
- 默认只读取第一页，`limit` 只能为 1 至 20。
- 正式备选记录必须同时具有非空篇名、期刊和可核验发表年度。
- 期刊级别只依据 `Academic_Journal_Master_Directory_20260715.md`，目录版本固定为 `2026-07-15`。
- 不使用高级检索、专业检索、WebVPN、机构认证、IP 登录、Cookie、用户浏览器 profile 或内部 HTTP 接口。
- 不访问详情页，不导出题录，不解析或保存详情、PDF、CAJ及下载 URL，不下载全文。
- 遇到验证码、登录跳转、401、403、429或页面合同变化立即停止，不切换入口、代理或出口地址。
- 主源码 `scripts/cnki_search` 与发布副本 `mcpb/src/cnki_search` 必须逐文件、逐字节一致。
- 所有代码修改遵循测试先行；每个任务由独立子代理实施，再进行规范复核和代码质量复核。
- 测试命令统一设置 `PYTHONDONTWRITEBYTECODE=1`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`，并使用 `-p no:cacheprovider`。
- 不复制 `cnki-search-skill-main.zip` 中没有许可证的源码或静态数据；只进行清洁重写。
- 二进制交付包不提交普通 Git 历史，只保存在 `outputs` 或私有 GitHub Release。
- 各任务的pytest命令从 `top-journal-search-lists` 目录运行；Git、构建、安装和推送命令从工作树根目录运行。

## Execution Units

- 原任务1、3、4、5、6共同构成公开检索迁移单元。旧模型被替换后，旧结果解析、会话、检索和MCP模块无法继续导入，因此这五项按测试先行顺序连续实施，完成后统一运行全量测试并接受独立复核。
- 迁移单元内部仍保留各任务的聚焦测试和提交记录，但在原任务6删除旧模块、旧测试之前，不将中间提交视为可独立集成状态。
- 原任务2、7、8继续作为独立实施和复核单元。
- `SearchOutcome` 必须拒绝将篇名、期刊或发表年度不完整的题录放入 `records`；不完整题录只能进入 `incomplete_records`。
- `PaperRecord.catalog_version` 使用不可由构造参数覆盖的固定值 `2026-07-15`。

---

## File Structure

### 保留并重写

- `top-journal-search-lists/scripts/cnki_search/models.py`：公开检索请求、题录、状态和结果模型。
- `top-journal-search-lists/scripts/cnki_search/browser.py`：浏览器发现和无用户状态的临时浏览器创建。
- `top-journal-search-lists/scripts/cnki_search/session.py`：公开首页、结果页合同和临时上下文生命周期。
- `top-journal-search-lists/scripts/cnki_search/search.py`：首页固定主题检索驱动。
- `top-journal-search-lists/scripts/cnki_search/results.py`：公开结果表解析和必需字段校验。
- `top-journal-search-lists/scripts/cnki_search/cache.py`：仅内存、24小时的公开题录缓存。
- `top-journal-search-lists/scripts/cnki_search/rate_limit.py`：单线程公开检索间隔。
- `top-journal-search-lists/scripts/cnki_search/mcp_server.py`：唯一 MCP 工具和单工作线程。
- `top-journal-search-lists/scripts/cnki_search/install_config.py`：跨客户端增量配置，服务名保持 `cnki-search`。
- `top-journal-search-lists/scripts/catalog_lookup.py`：十级目录、学科分类、受控刊名清理和歧义检测。

### 新增

- `top-journal-search-lists/scripts/cnki_search/ranking.py`：题录目录标注与排序。
- `top-journal-search-lists/scripts/cnki_search/merge.py`：ai4scholar与CNKI结果规范化去重并保留来源。
- `top-journal-search-lists/scripts/cnki_search/service.py`：参数校验、缓存、限流、浏览器、解析和判级编排。
- `top-journal-search-lists/scripts/build_release.py`：从干净暂存目录按白名单生成 Skill ZIP、MCPB和校验和。
- `top-journal-search-lists/tests/test_cnki_ranking.py`
- `top-journal-search-lists/tests/test_cnki_merge.py`
- `top-journal-search-lists/tests/test_cnki_service.py`
- `top-journal-search-lists/tests/_public_cnki_live_smoke.py`
- `top-journal-search-lists/tests/fixtures/public_home.html`
- `top-journal-search-lists/tests/fixtures/public_results.html`
- `top-journal-search-lists/tests/fixtures/public_no_results.html`
- `top-journal-search-lists/tests/fixtures/public_incomplete_results.html`
- `top-journal-search-lists/tests/fixtures/public_challenge.html`

### 删除

- `top-journal-search-lists/scripts/cnki_search/details.py`
- `top-journal-search-lists/scripts/cnki_search/downloads.py`
- `top-journal-search-lists/scripts/cnki_search/exporters.py`
- `top-journal-search-lists/scripts/cnki_search/fields.py`
- `top-journal-search-lists/scripts/cnki_search/syntax.py`
- `top-journal-search-lists/scripts/cnki_search/cli.py`
- MCPB中的同名副本。
- `tests/test_cnki_details.py`、`test_cnki_downloads.py`、`test_cnki_exporters.py`、`test_cnki_fields.py`、`test_cnki_syntax.py`、`test_cnki_cli.py`。
- 高级检索、专业检索、登录和详情相关HTML夹具及选择器来源记录。

---

### Task 1: 建立公开检索数据合同

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/models.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_models.py`

**Interfaces:**
- Consumes: 无。
- Produces: `SearchStatus`、`SearchRequest`、`PaperRecord`、`SearchOutcome`，供结果解析、目录标注、服务和MCP使用。

- [ ] **Step 1: 写入失败的数据合同测试**

```python
from dataclasses import fields

import pytest

from cnki_search.models import PaperRecord, SearchOutcome, SearchRequest, SearchStatus


def test_request_accepts_only_nonempty_theme_and_limit_1_to_20() -> None:
    assert SearchRequest("数字化转型", 20).query == "数字化转型"
    for query, limit in (("", 20), ("   ", 20), ("主题", 0), ("主题", 21)):
        with pytest.raises(ValueError):
            SearchRequest(query, limit)


def test_record_contract_has_no_url_or_fulltext_fields() -> None:
    names = {item.name for item in fields(PaperRecord)}
    assert {"title", "journal_raw", "publication_year", "priority_level"} <= names
    assert not names & {
        "detail_url", "download_url", "pdf_url", "caj_url", "doi",
        "abstract", "keywords", "affiliations", "download_status",
    }


def test_search_statuses_match_public_contract() -> None:
    assert {item.value for item in SearchStatus} == {
        "success", "no_results", "partial", "rate_limited",
        "challenge_detected", "login_required", "forbidden",
        "page_contract_changed", "network_error",
    }
```

- [ ] **Step 2: 运行测试并确认旧合同失败**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_models.py -q
```

Expected: FAIL，旧模型仍含 `SearchMode`、详情和下载字段，且没有公开检索状态。

- [ ] **Step 3: 用以下公开合同替换旧模型**

```python
class SearchStatus(StrEnum):
    SUCCESS = "success"
    NO_RESULTS = "no_results"
    PARTIAL = "partial"
    RATE_LIMITED = "rate_limited"
    CHALLENGE_DETECTED = "challenge_detected"
    LOGIN_REQUIRED = "login_required"
    FORBIDDEN = "forbidden"
    PAGE_CONTRACT_CHANGED = "page_contract_changed"
    NETWORK_ERROR = "network_error"


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    limit: int = 20

    def __post_init__(self) -> None:
        normalized = unicodedata.normalize("NFKC", self.query).strip()
        if not normalized:
            raise ValueError("主题检索词不能为空")
        if not 1 <= self.limit <= 20:
            raise ValueError("返回数量必须为 1 到 20")
        object.__setattr__(self, "query", normalized)


@dataclass(slots=True)
class PaperRecord:
    title: str
    authors: list[str]
    journal_raw: str
    publication_date: str
    publication_year: int | None
    document_type: str
    citations: int | None
    downloads: int | None
    is_online_first: bool
    result_rank: int
    source_database: str
    search_query: str
    journal_matched_title: str | None = None
    journal_match_status: str = "unmatched"
    journal_match_method: str | None = None
    priority_level: int | None = None
    priority_group: str | None = None
    source_catalogs: list[str] = field(default_factory=list)
    subject_categories: list[str] = field(default_factory=list)
    ncs_internal_rank: int | None = None
    catalog_version: str = "2026-07-15"
    manual_review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchOutcome:
    status: SearchStatus
    query: str
    records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    excluded_non_journal_rows: int
    warnings: list[str]
    searched_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.status in {SearchStatus.SUCCESS, SearchStatus.NO_RESULTS, SearchStatus.PARTIAL},
            "status": self.status.value,
            "query": self.query,
            "records": [record.to_dict() for record in self.records],
            "incomplete_records": [record.to_dict() for record in self.incomplete_records],
            "excluded_non_journal_rows": self.excluded_non_journal_rows,
            "warnings": list(self.warnings),
            "searched_at": self.searched_at,
        }
```

- [ ] **Step 4: 运行数据合同测试**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_models.py -q`

Expected: PASS。

- [ ] **Step 5: 提交数据合同**

```powershell
git add top-journal-search-lists/scripts/cnki_search/models.py top-journal-search-lists/tests/test_cnki_models.py
git commit -m "refactor: define CNKI public search models"
```

### Task 2: 扩充主期刊目录匹配器

**Files:**
- Modify: `top-journal-search-lists/scripts/catalog_lookup.py`
- Modify: `top-journal-search-lists/tests/test_catalog_lookup.py`
- Test: `top-journal-search-lists/references/Academic_Journal_Master_Directory_20260715.md`

**Interfaces:**
- Consumes: 主目录十级结构和五个来源区块。
- Produces: `CATALOG_VERSION`、`CatalogIndex`、`clean_lookup_title()`、`build_index()`、`lookup_journal()`、`lookup_journals()`。

- [ ] **Step 1: 增加版本、学科分类、受控清理和歧义测试**

```python
def test_validate_reports_exact_catalog_version(self):
    result = self.module.validate_catalog(CATALOG)
    self.assertEqual(result["catalog_version"], "2026-07-15")

def test_controlled_online_first_suffix_matches_without_overwriting_input(self):
    result = self.module.lookup_journals(CATALOG, ["经济研究（网络首发）"])[0]
    self.assertEqual(result["input"], "经济研究（网络首发）")
    self.assertEqual(result["matched_title"], "经济研究")
    self.assertEqual(result["match_method"], "controlled_display_suffix")

def test_cssci_subject_category_and_all_sources_are_preserved(self):
    result = self.module.lookup_journals(CATALOG, ["经济研究"])[0]
    self.assertEqual(result["priority_level"], 6)
    self.assertIn("经济学", result["subject_categories"])
    self.assertIn("CSSCI_2025_2026.md", result["source_catalogs"])

def test_normalized_key_collision_is_ambiguous(self):
    index = {}
    self.module._add(index, "A.B", 8, "ssci", "one.md")
    self.module._add(index, "AB", 9, "cssci", "two.md")
    result = self.module.lookup_journal(index, "AB")
    self.assertEqual(result["status"], "ambiguous")
    self.assertIsNone(result["priority_level"])
    self.assertEqual(result["candidates"], ["A.B", "AB"])
```

- [ ] **Step 2: 运行新增测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_catalog_lookup.py -q
```

Expected: FAIL，缺少目录版本、学科分类、受控后缀和一键多候选能力。

- [ ] **Step 3: 实现锁定的目录接口**

```python
CATALOG_VERSION = "2026-07-15"
CatalogIndex = dict[str, list[dict[str, Any]]]
_DISPLAY_SUFFIX = re.compile(r"\s*(?:[（(\[【]网络首发[）)\]】]|网络首发)\s*$")


def clean_lookup_title(value: str) -> tuple[str, str]:
    normalized = unicodedata.normalize("NFKC", value).strip()
    cleaned = _DISPLAY_SUFFIX.sub("", normalized).strip()
    method = "controlled_display_suffix" if cleaned != normalized else "normalized_exact"
    return cleaned, method


def lookup_journal(index: CatalogIndex, journal: str) -> dict[str, Any]:
    cleaned, method = clean_lookup_title(journal)
    candidates: list[dict[str, Any]] = []
    for key in _keys_for_title(cleaned):
        for candidate in index.get(key, []):
            if candidate not in candidates:
                candidates.append(candidate)
    base = {
        "input": journal,
        "normalized": normalize_title(cleaned),
        "catalog_version": CATALOG_VERSION,
        "manual_review_required": True,
    }
    if not candidates:
        return base | {
            "status": "unmatched", "match_method": None, "candidates": [],
            "matched_title": None, "priority_level": None, "priority_group": None,
            "source_catalogs": [], "subject_categories": [], "ncs_internal_rank": None,
        }
    if len(candidates) > 1:
        return base | {
            "status": "ambiguous", "match_method": None,
            "candidates": [item["matched_title"] for item in candidates],
            "matched_title": None, "priority_level": None, "priority_group": None,
            "source_catalogs": [], "subject_categories": [], "ncs_internal_rank": None,
        }
    return base | {
        "status": "matched", "match_method": method, "candidates": [],
        "manual_review_required": False, **candidates[0],
    }
```

`_add()` 必须把同名期刊的最高级别、全部 `source_catalogs`、全部 `subject_categories` 和最小 `ncs_internal_rank` 合并；规范化键下出现不同清理后刊名时保留为两个候选。`_index_cssci()` 同时读取期刊名称和第三列学科名称；SSCI、SCIE解析器跟踪最近的三级标题；TOP5明确加入“经济学 Top 5”。`validate_catalog()` 必须校验机器配置中的版本等于 `CATALOG_VERSION`。

- [ ] **Step 4: 固定Windows UTF-8输出并运行目录测试**

在 `main()` 输出前执行：

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_catalog_lookup.py -q
C:\Python314\python.exe scripts/catalog_lookup.py lookup "经济研究（网络首发）" "Social Forces"
```

Expected: 全部测试PASS；JSON分别包含第6级中文期刊信息和SSCI学科 `Sociology`。

- [ ] **Step 5: 提交目录匹配器**

```powershell
git add top-journal-search-lists/scripts/catalog_lookup.py top-journal-search-lists/tests/test_catalog_lookup.py
git commit -m "feat: classify CNKI journals with master catalog"
```

### Task 3: 解析公开结果页并严格校验题录

**Files:**
- Rewrite: `top-journal-search-lists/scripts/cnki_search/results.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_results.py`
- Modify: `top-journal-search-lists/tests/conftest.py`
- Create: `top-journal-search-lists/tests/fixtures/public_results.html`
- Create: `top-journal-search-lists/tests/fixtures/public_no_results.html`
- Create: `top-journal-search-lists/tests/fixtures/public_incomplete_results.html`
- Delete: `top-journal-search-lists/tests/fixtures/results.html`
- Delete: `top-journal-search-lists/tests/fixtures/results_table.html`

**Interfaces:**
- Consumes: `PaperRecord`。
- Produces: `ParsedResultPage`、`extract_publication_year()`、`parse_public_result_page()`。

- [ ] **Step 1: 建立不含详情和下载地址的脱敏夹具**

```html
<table class="result-table-list">
  <thead><tr><th>序号</th><th>篇名</th><th>作者</th><th>来源</th><th>日期</th><th>数据库</th><th>被引</th><th>下载</th></tr></thead>
  <tbody>
    <tr><td class="seq">1</td><td class="name"><a>数字化转型与企业创新</a><i>网络首发</i></td><td class="author">张三;李四</td><td class="source"><a>经济研究</a><span>CSSCI</span></td><td class="date">2026-07-20 10:20</td><td class="data">期刊</td><td class="quote">12</td><td class="download">108</td></tr>
    <tr><td class="seq">2</td><td class="name"><a>数字经济研究</a></td><td class="author">王五</td><td class="source">某大学</td><td class="date">2025</td><td class="data">博士</td><td class="quote">3</td><td class="download">20</td></tr>
  </tbody>
</table>
```

`public_incomplete_results.html` 分别放入缺篇名、缺期刊、非法日期 `2026-13-40` 的三行；`public_no_results.html` 只包含“未检索到相关文献”。所有夹具不得包含 `href`、动态令牌、Cookie、账号或个人检索历史。

在 `conftest.py` 增加：

```python
@pytest.fixture
def fixtures() -> Path:
    return Path(__file__).resolve().parent / "fixtures"
```

- [ ] **Step 2: 写入失败的解析测试**

```python
def test_public_result_requires_title_journal_and_valid_year(fixtures: Path) -> None:
    parsed = parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="数字化转型", limit=20,
    )
    assert len(parsed.records) == 1
    record = parsed.records[0]
    assert (record.title, record.journal_raw, record.publication_year) == (
        "数字化转型与企业创新", "经济研究", 2026,
    )
    assert record.document_type == "期刊"
    assert (record.citations, record.downloads, record.is_online_first) == (12, 108, True)
    assert parsed.excluded_non_journal_rows == 1

def test_incomplete_rows_never_enter_formal_records(fixtures: Path) -> None:
    parsed = parse_public_result_page(
        (fixtures / "public_incomplete_results.html").read_text(encoding="utf-8"),
        query="主题", limit=20,
    )
    assert parsed.records == []
    assert len(parsed.incomplete_records) == 3

def test_public_record_serialization_contains_no_url_fields(fixtures: Path) -> None:
    payload = parse_public_result_page(
        (fixtures / "public_results.html").read_text(encoding="utf-8"),
        query="主题", limit=20,
    ).records[0].to_dict()
    assert not any("url" in key.casefold() for key in payload)
```

- [ ] **Step 3: 运行解析测试并确认失败**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_results.py -q`

Expected: FAIL，旧解析器仍输出详情URL且不区分非期刊与不完整记录。

- [ ] **Step 4: 实现严格日期和公开结果解析**

```python
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
        "seq": "result_rank", "name": "title", "author": "authors",
        "source": "journal", "date": "publication_date", "data": "document_type",
        "quote": "citations", "download": "downloads",
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
        title=raw.title.strip(), authors=authors, journal_raw=raw.journal.strip(),
        publication_date=raw.publication_date.strip(),
        publication_year=extract_publication_year(raw.publication_date),
        document_type=raw.document_type.strip(), citations=_to_int(raw.citations),
        downloads=_to_int(raw.downloads), is_online_first=raw.is_online_first,
        result_rank=_to_int(raw.result_rank) or 0, source_database="CNKI",
        search_query=query,
    )


def parse_public_result_page(html: str, *, query: str, limit: int) -> ParsedResultPage:
    if not 1 <= limit <= 20:
        raise ValueError("返回数量必须为 1 到 20")
    parser = _PublicTableParser()
    parser.feed(html)
    rows = parser.rows
    records: list[PaperRecord] = []
    incomplete: list[PaperRecord] = []
    excluded = 0
    for raw in rows:
        if raw.document_type != "期刊":
            excluded += 1
            continue
        record = _to_record(raw, query=query)
        if not record.title or not record.journal_raw or record.publication_year is None:
            incomplete.append(record)
        elif len(records) < limit:
            records.append(record)
    return ParsedResultPage(records, incomplete, len(rows), excluded)
```

解析器不得读取任何 `href` 属性；非数字被引或下载次数返回 `None`。

- [ ] **Step 5: 运行解析测试并提交**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_results.py -q`

Expected: PASS。

```powershell
git add top-journal-search-lists/scripts/cnki_search/results.py top-journal-search-lists/tests/test_cnki_results.py top-journal-search-lists/tests/conftest.py top-journal-search-lists/tests/fixtures/public_*.html
git rm top-journal-search-lists/tests/fixtures/results.html top-journal-search-lists/tests/fixtures/results_table.html
git commit -m "feat: parse CNKI public bibliography results"
```

### Task 4: 实现公开首页临时浏览器和状态识别

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/browser.py`
- Rewrite: `top-journal-search-lists/scripts/cnki_search/session.py`
- Rewrite: `top-journal-search-lists/scripts/cnki_search/search.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_session.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_search.py`
- Create: `top-journal-search-lists/tests/fixtures/public_home.html`
- Create: `top-journal-search-lists/tests/fixtures/public_challenge.html`

**Interfaces:**
- Consumes: `SearchStatus`。
- Produces: `CNKI_HOME_URL`、`classify_public_search_state()`、`PublicCnkiSession`、`PublicThemeSearchRunner`。

- [ ] **Step 1: 写入公开入口和页面驱动失败测试**

```python
class RecordingLocator:
    def __init__(self, page, kind: str = "") -> None:
        self.page, self.kind = page, kind

    def count(self) -> int:
        return 1

    def fill(self, value: str) -> None:
        self.page.actions.append(("fill", value))

    def press(self, value: str) -> None:
        self.page.actions.append(("press", value))


class Navigation:
    def __enter__(self):
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    @property
    def value(self):
        return type("Response", (), {"status": 200})()


class RecordingPage:
    def __init__(self) -> None:
        self.actions = []

    def get_by_text(self, value: str, exact: bool = False):
        return RecordingLocator(self)

    def get_by_role(self, role: str, name: str):
        self.actions.append((role, name))
        return RecordingLocator(self)

    def expect_navigation(self, **_kwargs):
        return Navigation()


def test_public_session_uses_only_cnki_home() -> None:
    assert CNKI_HOME_URL == "https://www.cnki.net/"
    source = Path(session_module.__file__).read_text(encoding="utf-8").casefold()
    assert "webvpn" not in source
    assert "advsearch" not in source
    assert "brief/grid" not in source

def test_runner_fills_only_default_theme_box() -> None:
    page = RecordingPage()
    PublicThemeSearchRunner().run(page, "数字化转型")
    assert page.actions == [
        ("textbox", "中文文献、外文文献"),
        ("fill", "数字化转型"),
        ("press", "Enter"),
    ]

@pytest.mark.parametrize(
    ("url", "text", "expected"),
    [
        ("https://kns.cnki.net/captcha", "请完成拼图验证", SearchStatus.CHALLENGE_DETECTED),
        ("https://login.cnki.net/", "用户登录", SearchStatus.LOGIN_REQUIRED),
        ("https://kns.cnki.net/", "403 Forbidden", SearchStatus.FORBIDDEN),
        ("https://kns.cnki.net/", "访问过于频繁", SearchStatus.RATE_LIMITED),
    ],
)
def test_restrictions_stop_without_fallback(url, text, expected) -> None:
    assert classify_public_search_state(url=url, title="", visible_text=text) is expected
```

- [ ] **Step 2: 运行页面测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_session.py tests/test_cnki_search.py -q
```

Expected: FAIL，旧代码仍要求WebVPN和新版高级检索页面。

- [ ] **Step 3: 收窄浏览器和页面接口**

```python
CNKI_HOME_URL = "https://www.cnki.net/"
CNKI_RESULT_HOST = "kns.cnki.net"
CNKI_RESULT_PATH_PREFIX = "/kns8s/defaultresult/"


class PublicThemeSearchRunner:
    def run(self, page: Any, query: str) -> int | None:
        field = page.get_by_text("主题", exact=True)
        box = page.get_by_role("textbox", name="中文文献、外文文献")
        if field.count() != 1 or box.count() != 1:
            raise PageContractChanged("知网公开首页主题检索结构已变化")
        box.fill(query)
        with page.expect_navigation(wait_until="domcontentloaded") as navigation:
            box.press("Enter")
        response = navigation.value
        return response.status if response is not None else None


class PageContractChanged(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SearchSnapshot:
    html: str
    url: str
    title: str
    visible_text: str
    http_status: int | None = None

    def state_arguments(self) -> dict[str, Any]:
        return {
            "url": self.url, "title": self.title,
            "visible_text": self.visible_text, "http_status": self.http_status,
        }


def classify_public_search_state(
    *, url: str, title: str, visible_text: str, http_status: int | None = None,
) -> SearchStatus:
    identity = f"{url}\n{title}\n{visible_text}".casefold()
    if http_status in {401, 403} or any(token in identity for token in ("401 unauthorized", "403 forbidden", "无权访问", "拒绝访问")):
        return SearchStatus.FORBIDDEN
    if http_status == 429 or any(token in identity for token in ("429 too many requests", "访问过于频繁", "操作频繁")):
        return SearchStatus.RATE_LIMITED
    if http_status is not None and 500 <= http_status <= 599:
        return SearchStatus.NETWORK_ERROR
    if any(token in identity for token in ("captcha", "请完成拼图验证", "请输入验证码", "安全验证")):
        return SearchStatus.CHALLENGE_DETECTED
    if any(token in identity for token in ("login.cnki.net", "authserver", "用户登录", "统一身份认证")):
        return SearchStatus.LOGIN_REQUIRED
    parsed = urlparse(url)
    if "未检索到相关文献" in visible_text:
        return SearchStatus.NO_RESULTS
    if parsed.hostname == "www.cnki.net" and "中国知网" in identity:
        return SearchStatus.SUCCESS
    if parsed.hostname == CNKI_RESULT_HOST and parsed.path.casefold().startswith(CNKI_RESULT_PATH_PREFIX):
        if "题名" in visible_text and "来源" in visible_text:
            return SearchStatus.SUCCESS
    return SearchStatus.PAGE_CONTRACT_CHANGED


class PublicCnkiSession:
    def __enter__(self) -> "PublicCnkiSession":
        self._playwright = start_playwright()
        self.browser = BrowserFactory(self._playwright).launch_ephemeral()
        self.context = self.browser.new_context(locale="zh-CN", accept_downloads=False)
        self.page = self.context.new_page()
        self.page.goto(CNKI_HOME_URL, wait_until="domcontentloaded")
        return self

    def search(self, query: str) -> SearchSnapshot:
        home_box = self.page.get_by_role("textbox", name="中文文献、外文文献")
        theme_field = self.page.get_by_text("主题", exact=True)
        if self.page.url != CNKI_HOME_URL or home_box.count() != 1 or theme_field.count() != 1:
            raise PageContractChanged("知网公开首页未就绪")
        http_status = PublicThemeSearchRunner().run(self.page, query)
        body = self.page.locator("body").inner_text(timeout=10_000)
        return SearchSnapshot(self.page.content(), self.page.url, self.page.title(), body, http_status)

    def __exit__(self, *_exc: object) -> None:
        self.context.close()
        self.browser.close()
        self._playwright.stop()


def launch_ephemeral(self) -> Any:
    kwargs: dict[str, Any] = {"headless": True}
    executable = self.executable_path or discover_browser_executable()
    if executable:
        kwargs["executable_path"] = executable
    return self.playwright.chromium.launch(**kwargs)
```

最后一个方法写入 `BrowserFactory`。它不接受 `user_data_dir`、`storage_state`、代理、扩展或远程调试参数。`PublicCnkiSession.search()` 不点击筛选、翻页、详情或下载控件。

- [ ] **Step 4: 运行页面测试并提交**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_session.py tests/test_cnki_search.py -q`

Expected: PASS。

```powershell
git add top-journal-search-lists/scripts/cnki_search/browser.py top-journal-search-lists/scripts/cnki_search/session.py top-journal-search-lists/scripts/cnki_search/search.py top-journal-search-lists/tests/test_cnki_session.py top-journal-search-lists/tests/test_cnki_search.py top-journal-search-lists/tests/fixtures/public_home.html top-journal-search-lists/tests/fixtures/public_challenge.html
git commit -m "feat: search CNKI public homepage only"
```

### Task 5: 编排目录标注、排序、缓存和低频检索

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/ranking.py`
- Create: `top-journal-search-lists/scripts/cnki_search/merge.py`
- Create: `top-journal-search-lists/scripts/cnki_search/service.py`
- Rewrite: `top-journal-search-lists/scripts/cnki_search/cache.py`
- Rewrite: `top-journal-search-lists/scripts/cnki_search/rate_limit.py`
- Create: `top-journal-search-lists/tests/test_cnki_ranking.py`
- Create: `top-journal-search-lists/tests/test_cnki_merge.py`
- Create: `top-journal-search-lists/tests/test_cnki_service.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_cache.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_rate_limit.py`

**Interfaces:**
- Consumes: `SearchRequest`、`PaperRecord`、`ParsedResultPage`、`lookup_journals()`、`PublicCnkiSession`。
- Produces: `annotate_and_sort_records()`、`merge_literature_results()`、`SearchCache`、`SerialSearchGate`、`CnkiPublicSearchService.search()`。

- [ ] **Step 1: 写入判级和正式清单排序测试**

```python
ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"
FIXTURES = Path(__file__).with_name("fixtures")


def record(
    journal: str, rank: int, *, title: str = "示例论文", year: int | None = 2026,
) -> PaperRecord:
    return PaperRecord(
        title=title, authors=["张三"], journal_raw=journal,
        publication_date=str(year or ""), publication_year=year,
        document_type="期刊", citations=None, downloads=None,
        is_online_first=False, result_rank=rank, source_database="CNKI",
        search_query="主题",
    )


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class FakeSession:
    def __init__(self, html: str) -> None:
        self.html = html

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def search(self, query: str) -> SearchSnapshot:
        return SearchSnapshot(
            self.html, "https://kns.cnki.net/kns8s/defaultresult/index",
            "检索-中国知网", "题名 作者 来源 日期 数据库", 200,
        )


def test_annotation_uses_catalog_and_preserves_unmatched() -> None:
    records = [record("未知期刊", 1), record("经济研究", 2)]
    ranked = annotate_and_sort_records(records, catalog=CATALOG)
    assert [item.journal_raw for item in ranked] == ["经济研究", "未知期刊"]
    assert ranked[0].priority_level == 6
    assert "经济学" in ranked[0].subject_categories
    assert ranked[1].journal_match_status == "unmatched"
    assert ranked[1].manual_review_required is True

def test_cache_expires_after_24_hours() -> None:
    clock = FakeClock()
    cache = SearchCache(ttl_seconds=86400, now=clock)
    outcome = empty_outcome(SearchStatus.SUCCESS, "数字化 转型")
    cache.put("数字化 转型", 20, outcome)
    assert cache.get("数字化　转型", 20).status is SearchStatus.SUCCESS
    clock.advance(86401)
    assert cache.get("数字化 转型", 20) is None

def test_service_returns_partial_when_incomplete_rows_exist() -> None:
    html = (FIXTURES / "public_incomplete_results.html").read_text(encoding="utf-8")
    service = CnkiPublicSearchService(session_factory=lambda: FakeSession(html), catalog=CATALOG)
    outcome = service.search("数字化转型", limit=20)
    assert outcome.status is SearchStatus.PARTIAL
    assert all(item.title and item.journal_raw and item.publication_year for item in outcome.records)
    assert outcome.incomplete_records

def test_merge_keeps_primary_and_cnki_provenance() -> None:
    primary = [{"title": "数字化转型与企业创新", "authors": ["张三"], "year": 2026}]
    cnki = [record("经济研究", 1, title="数字化转型与企业创新", year=2026)]
    merged = merge_literature_results(primary, cnki)
    assert len(merged) == 1
    assert merged[0]["sources"] == ["ai4scholar", "CNKI"]
    assert set(merged[0]["source_records"]) == {"ai4scholar", "CNKI"}
```

- [ ] **Step 2: 运行编排测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_ranking.py tests/test_cnki_merge.py tests/test_cnki_cache.py tests/test_cnki_rate_limit.py tests/test_cnki_service.py -q
```

Expected: FAIL，新模块尚不存在。

- [ ] **Step 3: 实现目录标注和确定性排序**

```python
def annotate_and_sort_records(
    records: Iterable[PaperRecord], *, catalog: Path = DEFAULT_CATALOG,
) -> list[PaperRecord]:
    materialized = list(records)
    matches = lookup_journals(catalog, [item.journal_raw for item in materialized])
    for record, match in zip(materialized, matches, strict=True):
        record.journal_matched_title = match["matched_title"]
        record.journal_match_status = match["status"]
        record.journal_match_method = match["match_method"]
        record.priority_level = match["priority_level"]
        record.priority_group = match["priority_group"]
        record.source_catalogs = list(match["source_catalogs"])
        record.subject_categories = list(match["subject_categories"])
        record.ncs_internal_rank = match["ncs_internal_rank"]
        record.catalog_version = match["catalog_version"]
        record.manual_review_required = bool(match["manual_review_required"])
    return sorted(materialized, key=lambda item: (
        item.priority_level is None,
        item.priority_level or 999,
        item.ncs_internal_rank or 999,
        item.result_rank,
    ))
```

`merge.py` 使用 DOI 精确键；没有 DOI 时使用规范化篇名、第一作者和年度。它保留两侧原始记录：

```python
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
    ai4scholar_records: Iterable[Mapping[str, Any]],
    cnki_records: Iterable[PaperRecord],
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
            entry = merged.setdefault(key, {
                "canonical": record, "sources": [], "source_records": {},
            })
            if source_name not in entry["sources"]:
                entry["sources"].append(source_name)
            entry["source_records"][source_name] = record
    return list(merged.values())
```

- [ ] **Step 4: 实现内存缓存、单线程间隔和服务**

```python
def normalize_cache_query(query: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", query).split()).casefold()


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


class SearchCache:
    def __init__(self, *, ttl_seconds: float = 86400, now=time.time) -> None:
        self.ttl_seconds = ttl_seconds
        self.now = now
        self._items: dict[tuple[str, int], tuple[float, SearchOutcome]] = {}

    def get(self, query: str, limit: int) -> SearchOutcome | None:
        key = (normalize_cache_query(query), limit)
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, outcome = item
        if self.now() >= expires_at:
            self._items.pop(key, None)
            return None
        return copy.deepcopy(outcome)

    def put(self, query: str, limit: int, outcome: SearchOutcome) -> None:
        payload = outcome.to_dict()
        forbidden = {"cookie", "token", "url", "password", "storage_state"}
        if any(any(part in key.casefold() for part in forbidden) for key in _walk_keys(payload)):
            raise ValueError("缓存包含会话或地址字段")
        key = (normalize_cache_query(query), limit)
        self._items[key] = (self.now() + self.ttl_seconds, copy.deepcopy(outcome))


class SerialSearchGate:
    def __init__(self, *, minimum_interval: float = 6.0, clock=time.monotonic, sleep=time.sleep):
        self.minimum_interval = minimum_interval
        self.clock = clock
        self.sleep = sleep
        self._last_started: float | None = None

    def wait(self) -> float:
        now = self.clock()
        delay = 0.0 if self._last_started is None else max(0.0, self.minimum_interval - (now - self._last_started))
        if delay:
            self.sleep(delay)
        self._last_started = self.clock()
        return delay


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_outcome(status: SearchStatus, query: str, warning: str = "") -> SearchOutcome:
    return SearchOutcome(status, query, [], [], 0, [warning] if warning else [], utc_now())


class CnkiPublicSearchService:
    def __init__(
        self, *, session_factory=PublicCnkiSession, catalog: Path = DEFAULT_CATALOG,
        cache: SearchCache | None = None, gate: SerialSearchGate | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.catalog = catalog
        self.cache = cache or SearchCache()
        self.gate = gate or SerialSearchGate()

    def search(self, query: str, limit: int = 20) -> SearchOutcome:
        request = SearchRequest(query, limit)
        cached = self.cache.get(request.query, request.limit)
        if cached is not None:
            return cached
        for attempt in range(2):
            self.gate.wait()
            try:
                with self.session_factory() as session:
                    snapshot = session.search(request.query)
                status = classify_public_search_state(**snapshot.state_arguments())
                if status is SearchStatus.NO_RESULTS:
                    outcome = empty_outcome(status, request.query)
                elif status is SearchStatus.NETWORK_ERROR and attempt == 0:
                    continue
                elif status is not SearchStatus.SUCCESS:
                    return empty_outcome(status, request.query)
                else:
                    parsed = parse_public_result_page(
                        snapshot.html, query=request.query, limit=request.limit,
                    )
                    records = annotate_and_sort_records(parsed.records, catalog=self.catalog)
                    result_status = SearchStatus.PARTIAL if parsed.incomplete_records else (
                        SearchStatus.SUCCESS if records else SearchStatus.NO_RESULTS
                    )
                    outcome = SearchOutcome(
                        result_status, request.query, records, parsed.incomplete_records,
                        parsed.excluded_non_journal_rows, [], utc_now(),
                    )
                self.cache.put(request.query, request.limit, outcome)
                return outcome
            except PageContractChanged as exc:
                return empty_outcome(SearchStatus.PAGE_CONTRACT_CHANGED, request.query, str(exc))
            except (TimeoutError, OSError) as exc:
                if attempt == 1:
                    return empty_outcome(SearchStatus.NETWORK_ERROR, request.query, str(exc))
        raise AssertionError("unreachable")
```

缓存不写磁盘。网络错误只重试一次，其他状态不重试。

- [ ] **Step 5: 运行编排测试并提交**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_ranking.py tests/test_cnki_merge.py tests/test_cnki_cache.py tests/test_cnki_rate_limit.py tests/test_cnki_service.py -q`

Expected: PASS。

```powershell
git add top-journal-search-lists/scripts/cnki_search/ranking.py top-journal-search-lists/scripts/cnki_search/merge.py top-journal-search-lists/scripts/cnki_search/service.py top-journal-search-lists/scripts/cnki_search/cache.py top-journal-search-lists/scripts/cnki_search/rate_limit.py top-journal-search-lists/tests/test_cnki_ranking.py top-journal-search-lists/tests/test_cnki_merge.py top-journal-search-lists/tests/test_cnki_service.py top-journal-search-lists/tests/test_cnki_cache.py top-journal-search-lists/tests/test_cnki_rate_limit.py
git commit -m "feat: rank and cache CNKI public results"
```

### Task 6: 将MCP收窄为唯一公开检索工具

**Files:**
- Rewrite: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/__init__.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_mcp.py`
- Rewrite: `top-journal-search-lists/tests/_mcp_handshake.py`
- Rewrite: `top-journal-search-lists/tests/_mcpb_handshake.py`
- Rewrite: `top-journal-search-lists/tests/_mcpb_raw_handshake.py`
- Delete: legacy modules and tests listed in File Structure.

**Interfaces:**
- Consumes: `CnkiPublicSearchService.search(query, limit)`。
- Produces: 唯一工具 `cnki_search(query: str, limit: int = 20)`。

- [ ] **Step 1: 写入单工具失败测试**

```python
class FakeService:
    def search(self, query: str, limit: int = 20) -> SearchOutcome:
        return SearchOutcome(
            SearchStatus.NO_RESULTS, query, [], [], 0, [],
            "2026-07-22T00:00:00+00:00",
        )


def test_mcp_exposes_exact_public_tool() -> None:
    server = CnkiMcpServer(service=FakeService())
    assert server.tool_names() == REQUIRED_TOOLS == ["cnki_search"]

def test_public_signature_is_query_and_limit_only() -> None:
    parameters = inspect.signature(CnkiMcpServer.cnki_search).parameters
    assert list(parameters) == ["self", "query", "limit"]
    assert parameters["limit"].default == 20

def test_removed_tools_are_not_attributes() -> None:
    server = CnkiMcpServer(service=FakeService())
    for name in ("cnki_status", "cnki_login", "cnki_fetch_details", "cnki_export", "cnki_download", "cnki_close_session"):
        assert not hasattr(server, name)
```

- [ ] **Step 2: 运行MCP测试并确认失败**

Run: `C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_mcp.py -q`

Expected: FAIL，当前仍暴露七项工具。

- [ ] **Step 3: 重写MCP服务器**

```python
REQUIRED_TOOLS = ["cnki_search"]


class CnkiMcpServer:
    def __init__(self, service: CnkiPublicSearchService | None = None) -> None:
        self.service = service or CnkiPublicSearchService()
        self._tool_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="cnki-public")

    def tool_names(self) -> list[str]:
        return list(REQUIRED_TOOLS)

    def cnki_search(self, query: str, limit: int = 20) -> dict[str, Any]:
        return self.service.search(query, limit).to_dict()

    def build_fastmcp(self, fastmcp_class: type | None = None) -> Any:
        if fastmcp_class is None:
            from mcp.server.fastmcp import FastMCP
            fastmcp_class = FastMCP
        mcp = fastmcp_class("CNKI Public Search")
        mcp.tool(
            name="cnki_search",
            description="从中国知网公开首页执行固定主题检索，并按主期刊目录标注第一页期刊论文。",
        )(self._async_tool(self.cnki_search))
        return mcp
```

保留现有单线程异步包装和 `finally` 关闭执行器；不再保存浏览器会话和当前结果。

- [ ] **Step 4: 删除旧模块、旧测试和旧夹具**

```powershell
git rm top-journal-search-lists/scripts/cnki_search/details.py top-journal-search-lists/scripts/cnki_search/downloads.py top-journal-search-lists/scripts/cnki_search/exporters.py top-journal-search-lists/scripts/cnki_search/fields.py top-journal-search-lists/scripts/cnki_search/syntax.py top-journal-search-lists/scripts/cnki_search/cli.py
git rm top-journal-search-lists/tests/test_cnki_details.py top-journal-search-lists/tests/test_cnki_downloads.py top-journal-search-lists/tests/test_cnki_exporters.py top-journal-search-lists/tests/test_cnki_fields.py top-journal-search-lists/tests/test_cnki_syntax.py top-journal-search-lists/tests/test_cnki_cli.py
git rm top-journal-search-lists/tests/fixtures/advanced.html top-journal-search-lists/tests/fixtures/new_advanced.html top-journal-search-lists/tests/fixtures/new_professional.html top-journal-search-lists/tests/fixtures/login.html top-journal-search-lists/tests/fixtures/detail.html top-journal-search-lists/tests/fixtures/new_search_selector_provenance.md
```

- [ ] **Step 5: 将三个握手脚本改为只调用 `tools/list`**

三个脚本均断言返回工具名严格等于 `["cnki_search"]`，不得调用工具，避免握手测试触发真实网络。原始JSON-RPC脚本依次发送 `initialize`、`notifications/initialized`、`tools/list`。

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_mcp.py -q
C:\Python314\python.exe tests/_mcp_handshake.py
```

Expected: 测试PASS；握手输出只含 `cnki_search`。

- [ ] **Step 6: 提交MCP收口**

```powershell
git add -A top-journal-search-lists/scripts/cnki_search top-journal-search-lists/tests
git commit -m "refactor: expose only CNKI public search"
```

### Task 7: 更新Skill、MCPB、安装包合同和干净构建

**Files:**
- Modify: `top-journal-search-lists/SKILL.md`
- Modify: `top-journal-search-lists/README.md`
- Rewrite: `top-journal-search-lists/references/cnki-search-reference.md`
- Modify: `top-journal-search-lists/agents/openai.yaml`
- Modify: `top-journal-search-lists/mcpb/manifest.json`
- Modify: `top-journal-search-lists/mcpb/pyproject.toml`
- Modify: `top-journal-search-lists/mcpb/uv.lock`
- Synchronize: `top-journal-search-lists/mcpb/src/cnki_search/`
- Synchronize: `top-journal-search-lists/mcpb/src/catalog_lookup.py`
- Create: `top-journal-search-lists/scripts/build_release.py`
- Rewrite: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Modify: `top-journal-search-lists/tests/test_mcpb_manifest.py`
- Modify: `top-journal-search-lists/tests/test_installers.py`

**Interfaces:**
- Consumes: 已通过离线测试的主源码。
- Produces: 单工具MCPB、可移植Skill ZIP、SHA-256清单和三个客户端的增量安装配置。

- [ ] **Step 1: 写入公开包合同失败测试**

```python
def test_package_exposes_public_home_and_no_legacy_capabilities(skill_root: Path) -> None:
    code_files = [
        *Path(skill_root / "scripts/cnki_search").glob("*.py"),
        *Path(skill_root / "mcpb/src/cnki_search").glob("*.py"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").casefold() for path in code_files)
    assert "https://www.cnki.net/" in combined
    for token in ("webvpn", "advsearch", "brief/grid", "senquery", "access_confirmed", "detail_url", "download_url"):
        assert token not in combined

def test_main_and_mcpb_sources_and_catalog_are_identical(skill_root: Path) -> None:
    main = skill_root / "scripts/cnki_search"
    bundled = skill_root / "mcpb/src/cnki_search"
    assert [p.name for p in sorted(main.glob("*.py"))] == [p.name for p in sorted(bundled.glob("*.py"))]
    for source in main.glob("*.py"):
        assert source.read_bytes() == (bundled / source.name).read_bytes()
    assert (skill_root / "scripts/catalog_lookup.py").read_bytes() == (skill_root / "mcpb/src/catalog_lookup.py").read_bytes()
    assert (skill_root / "references/Academic_Journal_Master_Directory_20260715.md").read_bytes() == (skill_root / "mcpb/src/references/Academic_Journal_Master_Directory_20260715.md").read_bytes()

def test_skill_uses_ai4scholar_as_primary_and_cnki_as_supplement(skill_root: Path) -> None:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    for required in ("ai4scholar", "主要来源", "中文论文", "补充", "sources", "篇名", "期刊", "发表年度"):
        assert required in text
```

- [ ] **Step 2: 运行包合同并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_package_contract.py tests/test_mcpb_manifest.py tests/test_installers.py -q
```

Expected: FAIL，MCPB副本、manifest和文档仍是旧合同。

- [ ] **Step 3: 重写文档和MCPB元数据**

`SKILL.md`、README和参考文档必须明确 `ai4scholar` 为主源、CNKI为中文近期论文补充源；首页固定主题、第一页最多20条；正式结果必含篇名、期刊、年度；目录判级；用户自行下载。安装示例必须显式传入 `-Codex`、`-ClaudeCode`、`-ClaudeDesktop` 或对应Shell参数。

`manifest.json` 设置：

```json
{
  "name": "cnki-search",
  "display_name": "CNKI Public Theme Search",
  "version": "0.2.0",
  "description": "Public CNKI theme search with master-journal classification; no login or downloads.",
  "tools": [
    {"name": "cnki_search", "description": "Search the public CNKI homepage by topic and rank first-page journal records."}
  ],
  "keywords": ["CNKI", "literature", "public-search", "journal-ranking"]
}
```

保留原 manifest schema、uv入口、作者、跨平台和Apache-2.0字段。`pyproject.toml`版本同步为 `0.2.0`，继续依赖 `mcp>=1,<2` 与 `playwright>=1.45,<2`。

- [ ] **Step 4: 从主源码机械同步MCPB并更新锁文件**

```powershell
$src='top-journal-search-lists\scripts\cnki_search'
$dst='top-journal-search-lists\mcpb\src\cnki_search'
git rm top-journal-search-lists/mcpb/src/cnki_search/details.py top-journal-search-lists/mcpb/src/cnki_search/downloads.py top-journal-search-lists/mcpb/src/cnki_search/exporters.py top-journal-search-lists/mcpb/src/cnki_search/fields.py top-journal-search-lists/mcpb/src/cnki_search/syntax.py top-journal-search-lists/mcpb/src/cnki_search/cli.py
Copy-Item -Path "$src\*.py" -Destination $dst -Force
Copy-Item -LiteralPath top-journal-search-lists\scripts\catalog_lookup.py -Destination top-journal-search-lists\mcpb\src\catalog_lookup.py -Force
uv lock --directory top-journal-search-lists\mcpb
```

上述命令只删除六个明确列出的旧副本，不使用递归删除。

- [ ] **Step 5: 新增白名单构建脚本**

```python
def _zip_tree(source: Path, output: Path, *, prefix: str = "") -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = path.relative_to(source).as_posix()
            if any(part in {"__pycache__", ".pytest_cache", ".venv"} for part in path.parts):
                continue
            if path.suffix == ".pyc":
                continue
            name = f"{prefix}/{relative}" if prefix else relative
            archive.write(path, name)


def build(skill_root: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_zip = output_dir / "top-journal-search-lists_Skill.zip"
    mcpb_zip = output_dir / "cnki-search.mcpb"
    checksums = output_dir / "checksums.sha256"
    for target in (skill_zip, mcpb_zip, checksums):
        target.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="cnki-public-build-") as temporary:
        staging = Path(temporary)
        skill_stage = staging / "top-journal-search-lists"
        shutil.copytree(
            skill_root, skill_stage,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".venv", "*.pyc"),
        )
        mcpb_stage = staging / "mcpb"
        shutil.copytree(skill_root / "mcpb", mcpb_stage)
        _zip_tree(skill_stage, skill_zip, prefix="top-journal-search-lists")
        _zip_tree(mcpb_stage, mcpb_zip)
    artifacts = [skill_zip, mcpb_zip]
    checksums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    return [*artifacts, checksums]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    build(skill_root, args.output.resolve())
    return 0
```

文件头导入 `argparse`、`hashlib`、`shutil`、`tempfile`、`zipfile` 和 `Path`，文件尾调用 `raise SystemExit(main())`。每次构建只删除上述三个精确目标，不清空 `outputs`；ZIP成员统一使用正斜杠并按路径排序。

- [ ] **Step 6: 运行包合同、更新文档并提交**

Run:

```powershell
C:\Python314\python.exe -m pytest -p no:cacheprovider tests/test_cnki_package_contract.py tests/test_mcpb_manifest.py tests/test_installers.py -q
```

Expected: PASS。

```powershell
git add top-journal-search-lists/SKILL.md top-journal-search-lists/README.md top-journal-search-lists/references/cnki-search-reference.md top-journal-search-lists/agents/openai.yaml top-journal-search-lists/mcpb top-journal-search-lists/scripts/build_release.py top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists/tests/test_mcpb_manifest.py top-journal-search-lists/tests/test_installers.py
git commit -m "build: package CNKI public search"
```

### Task 8: 全量回归、独立解压、实机验证、安装和私有推送

**Files:**
- Create: `top-journal-search-lists/tests/_public_cnki_live_smoke.py`
- Produce: `outputs/top-journal-search-lists_Skill.zip`
- Produce: `outputs/cnki-search.mcpb`
- Produce: `outputs/checksums.sha256`
- Produce: `outputs/live-cnki-validation/public-theme-search.json`

**Interfaces:**
- Consumes: 通过包合同测试的源码和构建脚本。
- Produces: 无Cookie公开检索证据、独立解压验证、三客户端单工具安装和GitHub私有分支。

- [ ] **Step 1: 运行全部离线测试**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
```

Expected: 全部PASS，无旧工具测试和旧页面合同测试。

- [ ] **Step 2: 构建交付包并检查内容**

Run:

```powershell
C:\Python314\python.exe top-journal-search-lists/scripts/build_release.py --output outputs
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_mcpb_manifest.py -q
Get-Content outputs\checksums.sha256 -Encoding UTF8
```

Expected: 两个压缩包和校验和存在；包内没有旧模块、固定用户路径、会话文件、浏览器缓存和动态URL字段。

- [ ] **Step 3: 从全新临时目录独立解压验证**

```powershell
$extract=Join-Path $env:TEMP 'cnki-public-theme-search-verify'
$expected=[IO.Path]::GetFullPath((Join-Path $env:TEMP 'cnki-public-theme-search-verify'))
$resolved=[IO.Path]::GetFullPath($extract)
if($resolved -ne $expected){throw "临时验证目录不符合预期：$resolved"}
if(Test-Path -LiteralPath $resolved){Remove-Item -LiteralPath $resolved -Recurse -Force}
New-Item -ItemType Directory -Path $extract | Out-Null
Expand-Archive -LiteralPath outputs\top-journal-search-lists_Skill.zip -DestinationPath $extract
C:\Python314\python.exe -m pytest -p no:cacheprovider "$extract\top-journal-search-lists\tests" -q
C:\Python314\python.exe "$extract\top-journal-search-lists\scripts\catalog_lookup.py" validate
```

删除前必须确认 `$extract` 解析后位于系统临时目录且名称严格为 `cnki-public-theme-search-verify`。

Expected: 解压副本全量测试PASS；目录版本、十级层级和五个来源校验通过。

- [ ] **Step 4: 新增并运行无状态实机冒烟脚本**

`_public_cnki_live_smoke.py` 调用 `CnkiPublicSearchService`，主题词固定由 `--query` 传入，`--limit`限制1至20；输出前递归断言不存在 `detail_url`、`download_url`、`pdf_url`、`caj_url`、`cookie`、`token` 等会话或地址字段，但允许公开统计字段 `downloads`；断言正式记录均有篇名、期刊和年度；无论成功或异常都由上下文管理器关闭浏览器。证据只保存脱敏状态、查询、题录和目录判定。

Run:

```powershell
C:\Python314\python.exe top-journal-search-lists/tests/_public_cnki_live_smoke.py --query "数字化转型、企业创新与新质生产力" --limit 5 --output outputs/live-cnki-validation/public-theme-search.json
```

Expected: 状态为 `success` 或含少量不完整记录时为 `partial`；最终页面属于 `kns.cnki.net/kns8s/defaultresult`；不出现登录、WebVPN、高级或专业检索；返回1至5条正式期刊论文。若网站返回限制状态，本任务保持未完成，记录脱敏状态并停止，不将限制状态视为验收通过。

- [ ] **Step 5: 验证主源码和MCPB握手**

```powershell
C:\Python314\python.exe top-journal-search-lists/tests/_mcp_handshake.py
C:\Python314\python.exe top-journal-search-lists/tests/_mcpb_handshake.py
C:\Python314\python.exe top-journal-search-lists/tests/_mcpb_raw_handshake.py
```

Expected: 三次握手只列出 `cnki_search`，且不触发真实检索。

- [ ] **Step 6: 安装并验证三个客户端配置**

```powershell
powershell.exe -NoProfile -File top-journal-search-lists\installers\install.ps1 -Codex -ClaudeCode -ClaudeDesktop
codex mcp get cnki-search
```

安装器先为既有Skill目录和配置文件创建时间戳备份，再增量更新 `cnki-search` 服务；不得删除其他MCP。由于本机没有Claude CLI，Claude Code与Claude Desktop通过配置文件和stdio握手验证，重启客户端后由用户确认工具列表只有 `cnki_search`。

- [ ] **Step 7: 运行最终敏感内容和工作树检查**

```powershell
rg -n -S "cnki_status|cnki_login|cnki_fetch_details|cnki_export|cnki_download|cnki_close_session|webvpn|AdvSearch|brief/grid|senquery|access_confirmed|detail_url|download_url" top-journal-search-lists\scripts top-journal-search-lists\mcpb
git status --short
```

Expected: 第一条命令无命中；工作树只允许计划明确产生且尚未提交的脱敏证据或忽略的二进制包。

- [ ] **Step 8: 提交验收脚本并推送私有GitHub分支**

```powershell
git add top-journal-search-lists/tests/_public_cnki_live_smoke.py
git commit -m "test: verify CNKI public theme search"
gh repo view hushiliang2009/cnki-top-journal-search-skill --json visibility
git push -u origin agent/cnki-new-entry-only
```

Expected: `visibility` 为 `PRIVATE` 后才执行推送；推送成功；不得创建公开Release或公开仓库。若可见性不是 `PRIVATE`，停止并请求用户处理，不推送代码。

---

## Final Review Checklist

- [ ] 对照设计文档逐项确认公开首页、固定主题、第一页和20条上限均有测试。
- [ ] 确认正式题录的篇名、期刊、发表年度均非空，不完整记录只进入 `incomplete_records`。
- [ ] 确认期刊级别、学科分类、多目录归属、歧义和未匹配状态均来自主目录。
- [ ] 确认MCP、manifest和三个握手脚本只出现 `cnki_search`。
- [ ] 确认旧模块、旧夹具、旧工具和旧参数已从主源码与MCPB同时删除。
- [ ] 确认Skill ZIP和MCPB从干净暂存目录构建，独立解压测试通过。
- [ ] 确认实机验证使用全新临时上下文、空Cookie、无WebVPN且完成后关闭浏览器。
- [ ] 确认安装器保留其他MCP配置，三个客户端共享同一实现。
- [ ] 确认没有复制无许可证源码，没有打包浏览器缓存、会话状态、动态令牌或固定用户路径。
- [ ] 确认所有测试通过、Git工作树清洁、分支已推送至私有GitHub仓库。
