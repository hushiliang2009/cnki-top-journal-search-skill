# 环境期刊目录 v4.0 数据增补与运行时查询 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将既有3764种环境期刊整理为可审计、可复算的 v4.0 人读目录和规范 JSON，并使环境 Skill 与 MCPB 运行时从 JSON 查询完整元数据。

**Architecture:** 生成层以现有十二级目录为不可变分级基线，导入七份正式来源快照，按标识符、正式题名、受控别名、保守规范化和人工映射的固定顺序增补元数据，同时输出逐条审计记录。运行层只加载规范 JSON，缓存题名、别名、ISSN、层级和 CNKI 范围索引；完整 Markdown、来源注册表和镜像一致性只在生成或 `validate` 时校验。

**Tech Stack:** Python 3.11+ 标准库（`argparse`、`csv`、`dataclasses`、`hashlib`、`json`、`pathlib`、`re`、`unicodedata`）、pytest、ruff、mypy、PowerShell、Git。

## Global Constraints

- 实施起点固定为已批准设计提交 `b6f9dd0`；该设计所审计的产品代码基线为 `main@76651999980bc3f5c9bd283f90002a1efda97851`。
- 本计划只实施环境 v4.0 目录来源导入、生成与审计、JSON 运行时查询、模型字段传播、Skill/MCPB 数据镜像及直接测试。
- 本计划不修改版本号、manifest、锁文件、安装器、发布脚本、CI、README、SKILL.md、agents/openai.yaml、CNKI 页面驱动、专业检索字段顺序或来源类别页面流程。
- 目录版本固定为 `4.0`，数据日期固定为 `2026-07-29`，规范修订日期固定为 `2026-07-31`。
- 3764种期刊、十二级顺序和各级数量 `[4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561]` 不得改变。
- 十二个分组标识依次固定为 `comprehensive_super_journals`、`ncs_pnas_environment_flagships`、`top_university_highest_consensus`、`top_university_high_level`、`environment_field_top`、`chinese_environment_top`、`other_formally_recognized`、`environment_ssci`、`environment_cssci`、`environment_scie`、`pku_core_natural_sciences`、`pku_core_non_natural_sciences`。
- 增补前后 `(journal_id, priority_level, priority_group, ncs_internal_rank)` 签名必须完全一致；数据库交叉收录不得触发升降级。
- 唯一逐刊来源限定为 CSSCI 2025—2026、北大核心2023自然科学、北大核心2023非自然科学、SSCI 2026-07-15 和 SCIE 2026-07-15；不得补入 CSCD、AMI、WJCI、EI 或推测性 ISSN。
- SSCI、SCIE 以 CSV 为机器输入、对应 Markdown 为正式显示题名复核；CSSCI 和两份北大核心直接解析 Markdown。
- 匹配顺序固定为已绑定 ISSN/eISSN、正式题名、受控别名、保守规范化、审计登记的人工映射；歧义不得自动判级或静默新增期刊。
- 保守规范化只处理 Unicode NFKC、大小写、首尾空白、`The`、`&/and` 和有限标点，不使用编辑距离、包含关系或通用去重音符号。
- 17个北大核心原刊名和9组数据库题名构成26条结构化受控别名；北大核心原刊名不得按逗号拆分。
- 规范 JSON 使用 UTF-8 无 BOM、LF、文件末尾一个换行、Unicode 键名升序、`ensure_ascii=false`、紧凑分隔符且不含浮点数。
- `data_sha256` 使用固定值 `{{DATA_SHA256}}` 反算；Markdown 自引用哈希使用唯一值 `{{CONTENT_SHA256}}` 反算。
- Skill 与 `mcpb/src` 中 v4 Markdown、机器 JSON、来源清单、审计摘要及七份来源快照必须字节一致。
- 正常运行只加载 JSON；只有生成器与 `validate` 才解析完整 Markdown、来源清单和审计文件。
- 未匹配、歧义和来源范围外记录分别返回真实状态，不得自行赋予层级。
- 每个任务先提交测试，再提交最小实现；每次提交只包含本任务列出的文件。

八个输入文件必须在导入前同时通过下表的字节数和 SHA-256 门槛；任一项不符即停止生成，不得自动改写、换行规范化或以近似同名文件替代。

| 输入文件 | 字节数 | SHA-256 |
|---|---:|---|
| `环境科学与工程学科顶尖期刊目录_v4.0.md` | 681999 | `5a00fd832c16d28b1fc05137e90c883ada1a07f07f6147a903a53c0e4e568240` |
| `CSSCI_2025_2026.md` | 32269 | `09f48b9c38e6bf9644c0e7bcc1bd82ababb60474e8cba86b2eba93db654c766a` |
| `北大中文核心期刊目录_2023_自然科学版.md` | 64392 | `f2e807aa64acb850872be23d05b4eda411903d3c6efc6ff80d99cff01f3ef8de` |
| `北大中文核心期刊目录_2023_.md` | 37043 | `6ef7d9832844a36dc12e318e586f8942b951c068a2a4ac3f8297824a5be3b891` |
| `Social Sciences Citation Index_20260715.md` | 188504 | `0c1c63386f53ce88f03a75cc4caefb5bb2dd5944573e5b9819948d0545e57c55` |
| `Social Sciences Citation Index (SSCI).csv` | 635202 | `8436b3e9bd90cecba335490199ab917d6eb7732623824692d53e0b3efd1ab986` |
| `Science Citation Index Expanded_20260715.md` | 560466 | `40984893b8f50a6d4f9dd12553fbc33fc933ddabb93d967086b6e0c81e78f273` |
| `Science Citation Index Expanded (SCIE).csv` | 1758382 | `4cb2ff6458bb426c94aaf58e27d7e1291d0169b51b235ab5f6be4bec448b8b36` |

输入门槛采用双状态规则。首次转换时，v4 Markdown 必须是上表 `5a00fd...` 的批准种子；生成器覆盖该文件后，后续 `--check` 不再要求种子文件哈希，而要求规范生成版的 `CONTENT_SHA256`、对应 JSON 的 `data_sha256` 和3764条层级签名全部有效。其余七份来源快照在首次转换和以后每次重建时始终必须符合上表固定字节数与哈希。

---

## File Structure

### 新建文件

- `top-journal-search-lists-env/scripts/environment_catalog_v4.py`：数据模型、来源解析、受控匹配、目录构建、规范序列化、Markdown和审计渲染、完整校验。
- `top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py`：生成与 `--check` 命令行入口，只调用前述纯函数。
- `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`：来源、分级签名、命中统计、别名、哈希、审计和镜像的集中回归测试。
- `docs/audits/environment_journal_match_audit_v4.0.jsonl`：五类来源逐条匹配审计记录。
- `docs/audits/environment_journal_match_audit_v4.0.md`：仓库级审计摘要。
- `top-journal-search-lists-env/references/environment_journal_catalog_v4.0.json`：3764条机器记录和四个环境 CNKI 范围。
- `top-journal-search-lists-env/references/environment_catalog_sources_v4.0.json`：七份来源快照及第1—7级证据注册表。
- `top-journal-search-lists-env/references/environment_journal_match_audit_v4.0.md`：发布用审计摘要。
- `top-journal-search-lists-env/references/环境科学与工程学科顶尖期刊目录_v4.0.md`：规范化人读目录。
- `top-journal-search-lists-env/references/CSSCI_2025_2026.md`
- `top-journal-search-lists-env/references/北大中文核心期刊目录_2023_自然科学版.md`
- `top-journal-search-lists-env/references/北大中文核心期刊目录_2023_.md`
- `top-journal-search-lists-env/references/Social Sciences Citation Index_20260715.md`
- `top-journal-search-lists-env/references/Social Sciences Citation Index (SSCI).csv`
- `top-journal-search-lists-env/references/Science Citation Index Expanded_20260715.md`
- `top-journal-search-lists-env/references/Science Citation Index Expanded (SCIE).csv`
- `top-journal-search-lists-env/mcpb/src/references/` 下与上述11个 references 产物同名的镜像文件。

### 修改文件

- `.gitignore`：为已跟踪的 `docs/audits/environment_journal_match_audit_v4.0.jsonl` 增加精确例外，不放宽其他 JSONL 忽略规则。
- `top-journal-search-lists-env/.gitattributes`：固定规范产物的 LF，并把七份来源快照标为不做文本转换，保证跨平台字节哈希稳定。
- `top-journal-search-lists-env/scripts/catalog_lookup.py`：由 v3 Markdown 解析器改为 v4 JSON 缓存查询器和完整校验入口。
- `top-journal-search-lists-env/mcpb/src/catalog_lookup.py`：运行时镜像。
- `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`：导出 v4 查询和 CNKI 范围接口。
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py`：运行时镜像。
- `top-journal-search-lists-env/scripts/cnki_search_env/models.py`：承载新增目录字段。
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py`：运行时镜像。
- `top-journal-search-lists-env/scripts/cnki_search_env/ranking.py`：传播新增目录字段。
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/ranking.py`：运行时镜像。
- `top-journal-search-lists-env/tests/test_catalog_lookup.py`
- `top-journal-search-lists-env/tests/test_cnki_models.py`
- `top-journal-search-lists-env/tests/test_cnki_ranking.py`
- `top-journal-search-lists-env/tests/test_cnki_package_contract.py`

### 删除文件

- `top-journal-search-lists-env/references/环境科学与工程学科顶尖期刊目录_v3.0.md`
- `top-journal-search-lists-env/mcpb/src/references/环境科学与工程学科顶尖期刊目录_v3.0.md`

## 固定接口

```python
def canonical_json_bytes(value: object) -> bytes: ...
def parse_v4_baseline(path: Path) -> list[CatalogRecord]: ...
def parse_wos_markdown(path: Path) -> dict[str, str]: ...
def parse_wos_csv(
    path: Path,
    index_name: Literal["SSCI", "SCIE"],
    *,
    display_titles: Mapping[str, str],
) -> list[SourceRecord]: ...
def parse_cssci_markdown(path: Path) -> list[SourceRecord]: ...
def parse_pku_markdown(
    path: Path,
    branch: Literal["natural_sciences", "non_natural_sciences"],
) -> list[SourceRecord]: ...
def match_source_records(
    records: list[CatalogRecord],
    source_records: list[SourceRecord],
    *,
    controlled_aliases: Mapping[str, ControlledAlias],
) -> list[AuditRecord]: ...
def build_catalog_bundle(baseline: Path, sources: SourcePaths) -> CatalogBundle: ...
def render_catalog_markdown(bundle: CatalogBundle) -> str: ...
def render_audit_jsonl(audit: Sequence[AuditRecord]) -> str: ...
def render_audit_summary(bundle: CatalogBundle, audit: Sequence[AuditRecord]) -> str: ...
def validate_generated_bundle(
    bundle: CatalogBundle,
    audit: Sequence[AuditRecord],
) -> dict[str, Any]: ...
def generate_outputs(paths: OutputPaths, *, check: bool) -> dict[str, str]: ...

def load_catalog(path: Path = DEFAULT_CATALOG) -> CatalogIndex: ...
def validate_catalog(
    path: Path = DEFAULT_CATALOG,
    *,
    markdown: Path | None = None,
    sources: Path | None = None,
    audit_summary: Path | None = None,
    mirror_references: Path | None = None,
) -> dict[str, Any]: ...
def lookup_journal(index: CatalogIndex, journal: str) -> dict[str, Any]: ...
def lookup_journals(path: Path, journals: list[str]) -> list[dict[str, Any]]: ...
def journals_by_group(group: str, path: Path = DEFAULT_CATALOG) -> list[str]: ...
def cnki_scope(scope_id: str, path: Path = DEFAULT_CATALOG) -> dict[str, Any]: ...
```

`cnki_scope()` 的返回键固定为 `scope_id`、`catalog_version`、`journal_selector`、`source_category`、`journal_titles`、`eligible_journal_ids`、`eligible_priority_levels`、`required_index_membership` 和 `result_filter`。`catalog_version` 固定从目录根对象取得，v4.0 为 `4.0`；`journal_selector` 只允许 `exact_titles` 或 `topic_only`；`result_filter` 固定为 `matched_journal_id`；`source_category` 只允许 `null`、`{"code":"P0209","label":"CSSCI"}` 或 `{"code":"P01","label":"北大核心"}`。

### Task 1: 导入七份来源快照并建立严格解析器

**Files:**
- Create: `top-journal-search-lists-env/scripts/environment_catalog_v4.py`
- Create: `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`
- Create: `top-journal-search-lists-env/references/` 下七份来源快照和 v4.0 基线 Markdown
- Create: `top-journal-search-lists-env/mcpb/src/references/` 下对应镜像

**Interfaces:**
- Produces: `SourceRecord`、`SourcePaths`、`parse_wos_markdown()`、`parse_wos_csv()`、`parse_cssci_markdown()`、`parse_pku_markdown()`。
- Preserves: 北大核心备注中的完整 `原刊名：` 值，包括其中的逗号。

- [ ] **Step 1: Write failing source parser tests**

```python
def test_source_parsers_preserve_approved_counts_and_original_titles() -> None:
    paths = catalog.SourcePaths.from_references(REFERENCES)
    ssci = catalog.parse_wos_csv(
        paths.ssci_csv,
        "SSCI",
        display_titles=catalog.parse_wos_markdown(paths.ssci_markdown),
    )
    scie = catalog.parse_wos_csv(
        paths.scie_csv,
        "SCIE",
        display_titles=catalog.parse_wos_markdown(paths.scie_markdown),
    )
    cssci = catalog.parse_cssci_markdown(paths.cssci_markdown)
    natural = catalog.parse_pku_markdown(paths.pku_natural, "natural_sciences")
    non_natural = catalog.parse_pku_markdown(
        paths.pku_non_natural, "non_natural_sciences"
    )
    assert [len(items) for items in (ssci, scie, cssci, natural, non_natural)] == [
        3538, 9430, 674, 1247, 740
    ]
    renamed = next(item for item in natural if item.formal_title == "低碳化学与化工")
    assert renamed.aliases == ("天然气化工.C1,化学与化工",)
```

- [ ] **Step 2: Run the parser test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py::test_source_parsers_preserve_approved_counts_and_original_titles
```

Expected: FAIL because `environment_catalog_v4.py` and bundled v4 source snapshots do not exist.

- [ ] **Step 3: Copy the approved snapshots without changing bytes**

From the repository root used by this plan:

```powershell
$sourceRoot = Resolve-Path '..\..\..'
$skillRefs = 'top-journal-search-lists-env\references'
$mcpbRefs = 'top-journal-search-lists-env\mcpb\src\references'
$files = @(
  'CSSCI_2025_2026.md',
  '北大中文核心期刊目录_2023_自然科学版.md',
  '北大中文核心期刊目录_2023_.md',
  'Social Sciences Citation Index_20260715.md',
  'Social Sciences Citation Index (SSCI).csv',
  'Science Citation Index Expanded_20260715.md',
  'Science Citation Index Expanded (SCIE).csv'
)
Copy-Item -LiteralPath (Join-Path $sourceRoot 'cnki-top-journal-search-skill\top-journal-search-lists-env\references\环境科学与工程学科顶尖期刊目录_v4.0.md') -Destination $skillRefs
foreach ($name in $files) {
  Copy-Item -LiteralPath (Join-Path $sourceRoot $name) -Destination (Join-Path $skillRefs $name)
}
$mirrorFiles = $files + '环境科学与工程学科顶尖期刊目录_v4.0.md'
foreach ($name in $mirrorFiles) {
  Copy-Item -LiteralPath (Join-Path $skillRefs $name) -Destination (Join-Path $mcpbRefs $name) -Force
}
```

Before copying, verify all eight source paths against the exact byte counts and hashes in Global Constraints. After copying, verify every Skill/MCPB pair with `Get-FileHash`; a mismatch stops implementation before parsing. This is the only stage that accepts the approved v4 seed hash.

- [ ] **Step 4: Implement source records and header-driven parsers**

```python
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
            aliases=(), issn=(), eissn=(),
            subject_categories=(row.values["学科名称"],),
        )
        for row in rows
    ]
```

`parse_wos_csv()` must use `csv.DictReader`, require the seven approved column names, split `Web of Science Categories` only on `|`, retain nonempty ISSN/eISSN, and resolve display title through the corresponding Markdown title map plus the nine explicit database-title mappings. `parse_pku_markdown()` must track the current `###` classification heading and optional `分类代码` while parsing table headers by name; `备注` is split only on the exact prefix `原刊名：` and never on punctuation inside the title.

- [ ] **Step 5: Run parser tests and verify GREEN**

Run the command from Step 2.

Expected: PASS with source counts `3538/9430/674/1247/740` and no lost comma-bearing PKU title.

- [ ] **Step 6: Commit source parser and immutable inputs**

```bash
git add top-journal-search-lists-env/scripts/environment_catalog_v4.py top-journal-search-lists-env/tests/test_environment_catalog_generation.py top-journal-search-lists-env/references top-journal-search-lists-env/mcpb/src/references
git commit -m "test: lock environment v4 source snapshots"
```

### Task 2: 解析十二级基线并锁定稳定记录身份

**Files:**
- Modify: `top-journal-search-lists-env/scripts/environment_catalog_v4.py`
- Modify: `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`

**Interfaces:**
- Produces: `CatalogRecord`、`ControlledAlias`、`parse_v4_baseline()`、`priority_signature()`。
- Guarantees: `ENVJ-000001` 至 `ENVJ-003764` 按层级和级内原序分配；已有 `期刊ID` 时原样复用。

- [ ] **Step 1: Write failing baseline identity tests**

```python
def test_v4_baseline_has_stable_ids_levels_and_priority_signature() -> None:
    records = catalog.parse_v4_baseline(BASELINE)
    assert len(records) == 3764
    assert [sum(r.priority_level == level for r in records) for level in range(1, 13)] == [
        4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561
    ]
    assert records[0].journal_id == "ENVJ-000001"
    assert records[-1].journal_id == "ENVJ-003764"
    assert len({r.formal_title for r in records}) == 3764
    assert len(catalog.priority_signature(records)) == 3764
    assert catalog.PRIORITY_GROUPS == (
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
```

- [ ] **Step 2: Run the identity test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py::test_v4_baseline_has_stable_ids_levels_and_priority_signature
```

Expected: FAIL because `CatalogRecord` and `parse_v4_baseline()` are absent.

- [ ] **Step 3: Implement the complete record model and header-driven baseline parser**

```python
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
```

Parse only from `## 四、十二级主目录` up to `## 附录一` and recognize the twelve exact headings and groups. Locate columns by header text, not position. On the approved seed, use `期刊名称` as `priority_decision.baseline_title`; on a generated catalog, require and reuse the explicit `基线题名` column rather than treating the previously generated formal title as a new seed. Read optional `期刊ID`, `正式题名`, `环境细分领域` and `正式证据`, but discard previously generated aliases, ISSN、eISSN、索引和来源成员 before matching. Assign an ID only when the baseline row has none. Map the 15 distinct level 1—7 evidence display strings to stable document evidence IDs for SJTU, NJU, Fudan, the academic master directory and the Chinese Society for Environmental Sciences.

- [ ] **Step 4: Run identity and appendix-exclusion tests and verify GREEN**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py -k "baseline or appendix"
```

Expected: PASS; appendix-only titles do not enter the 3764-record signature.

- [ ] **Step 5: Commit stable identity conversion**

```bash
git add top-journal-search-lists-env/scripts/environment_catalog_v4.py top-journal-search-lists-env/tests/test_environment_catalog_generation.py
git commit -m "feat: lock environment v4 journal identities"
```

### Task 3: 增补五类交叉收录并生成逐条审计

**Files:**
- Modify: `top-journal-search-lists-env/scripts/environment_catalog_v4.py`
- Modify: `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`

**Interfaces:**
- Produces: `AuditRecord`、`CONTROLLED_ALIASES`、`match_source_records()`。
- Statuses: `matched`、`out_of_scope`、`ambiguous`、`expected_but_unmatched`。

- [ ] **Step 1: Write failing matching, alias and statistics tests**

```python
def test_approved_source_counts_intersections_and_aliases() -> None:
    bundle = catalog.build_catalog_bundle(BASELINE, catalog.SourcePaths.from_references(REFERENCES))
    assert bundle.match_counts == {
        "CSSCI": (674, 592, 82),
        "PKU_CORE_NATURAL": (1247, 1247, 0),
        "PKU_CORE_NON_NATURAL": (740, 740, 0),
        "SSCI": (3538, 348, 3190),
        "SCIE": (9430, 1499, 7931),
    }
    assert bundle.intersections == {
        "CSSCI&PKU_CORE_NATURAL": 22,
        "CSSCI&PKU_CORE_NON_NATURAL": 520,
        "SSCI&SCIE": 149,
    }
    assert bundle.zero_intersections == {
        "CSSCI&SSCI": 0,
        "CSSCI&SCIE": 0,
        "PKU_CORE_NATURAL&PKU_CORE_NON_NATURAL": 0,
        "PKU_CORE_NATURAL&SSCI": 0,
        "PKU_CORE_NATURAL&SCIE": 0,
        "PKU_CORE_NON_NATURAL&SSCI": 0,
        "PKU_CORE_NON_NATURAL&SCIE": 0,
    }
    assert bundle.controlled_alias_count == 26
    assert bundle.expected_but_unmatched_count == 0
    assert bundle.ambiguous_count == 0
```

Add representative assertions for all nine records required by the design: `Nature Climate Change`, `Environmental Science & Technology`, `中国人口·资源与环境`, `WIREs Climate Change`, `城市规划`, `WIREs Energy and Environment`, `Zeitschrift für Geomorphologie`, `陆军军医大学学报`, and `中国社会科学`.

- [ ] **Step 2: Run the matching test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py::test_approved_source_counts_intersections_and_aliases
```

Expected: FAIL because bundle matching and audit records are not implemented.

- [ ] **Step 3: Implement ordered matching without fuzzy fallback**

```python
def _match_one(
    indexes: MatchIndexes,
    source: SourceRecord,
    controlled_aliases: Mapping[str, ControlledAlias],
) -> MatchDecision:
    for identifier in (*source.issn, *source.eissn):
        if len(candidates := indexes.by_identifier.get(identifier, ())) == 1:
            return MatchDecision(candidates[0], "identifier")
        if len(candidates) > 1:
            return MatchDecision(None, "identifier_conflict", candidates)
    if len(candidates := indexes.by_exact_title.get(_exact_key(source.formal_title), ())) == 1:
        return MatchDecision(candidates[0], "formal_title_exact")
    alias = controlled_aliases.get(_exact_key(source.formal_title))
    if alias is not None:
        return MatchDecision(indexes.by_journal_id[alias.journal_id], "controlled_alias")
    candidates = indexes.by_conservative_title.get(_conservative_key(source.formal_title), ())
    if len(candidates) == 1:
        return MatchDecision(candidates[0], "conservative_normalized")
    return MatchDecision(None, "ambiguous" if candidates else "out_of_scope", candidates)
```

After a unique title match, bind nonempty identifiers only if they do not conflict. Add `index_memberships`, per-index `index_subject_categories`, source title, source record ID, source file, line, categories and match method to `source_memberships`. Preserve the original priority signature and set `priority_decision["unchanged"] = True`. Build the 17 PKU original-title aliases from parsed remarks and add exactly the nine approved database-title mappings; do not derive any further accent aliases.

- [ ] **Step 4: Run matching tests and verify GREEN**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py -k "source_counts or representative or alias or intersection"
```

Expected: PASS with 29 catalog records outside all five database memberships, zero ambiguity and zero `expected_but_unmatched`.

- [ ] **Step 5: Commit matching and audit decisions**

```bash
git add top-journal-search-lists-env/scripts/environment_catalog_v4.py top-journal-search-lists-env/tests/test_environment_catalog_generation.py
git commit -m "feat: enrich environment catalog memberships"
```

### Task 4: 构建规范 JSON、来源注册表和环境 CNKI 范围

**Files:**
- Modify: `top-journal-search-lists-env/scripts/environment_catalog_v4.py`
- Modify: `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`

**Interfaces:**
- Produces: `CatalogBundle`、`build_catalog_bundle()`、`canonical_json_bytes()`、`validate_generated_bundle()`。
- Produces root keys: `schema_version`、`catalog_version`、`catalog_date`、`revision_date`、`data_sha256`、`level_counts`、`priority_groups`、`journals`、`cnki_scopes`。

- [ ] **Step 1: Write failing canonical JSON and CNKI scope tests**

```python
def test_catalog_json_is_canonical_and_cnki_scopes_are_explicit() -> None:
    bundle = build_bundle()
    payload = bundle.catalog_payload
    assert len(payload["journals"]) == 3764
    assert payload["data_sha256"] == catalog.compute_data_sha256(payload)
    journals = payload["journals"]
    pku_members = [r for r in journals if "PKU_CORE" in r["index_memberships"]]
    assert len(pku_members) == 1987
    assert sum(r["priority_level"] <= 10 for r in pku_members) == 245
    assert sum(r["priority_level"] >= 11 for r in pku_members) == 1742
    cssci_members = [r for r in journals if "CSSCI" in r["index_memberships"]]
    assert len(cssci_members) == 592
    assert sum(r["priority_group"] == "environment_cssci" for r in cssci_members) == 241
    assert sum(r["priority_group"] != "environment_cssci" for r in cssci_members) == 351
    scopes = payload["cnki_scopes"]
    assert len(scopes["chinese_environment_top"]["eligible_journal_ids"]) == 6
    assert len(scopes["other_formally_recognized_chinese"]["eligible_journal_ids"]) == 60
    assert len(scopes["environment_cssci"]["eligible_journal_ids"]) == 241
    assert len(scopes["pku_core"]["eligible_journal_ids"]) == 1987
    assert scopes["environment_cssci"]["source_category"] == {
        "code": "P0209", "label": "CSSCI"
    }
    assert scopes["pku_core"]["journal_selector"] == "topic_only"
    assert scopes["pku_core"]["source_category"] == {
        "code": "P01", "label": "北大核心"
    }
```

- [ ] **Step 2: Run the JSON test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py::test_catalog_json_is_canonical_and_cnki_scopes_are_explicit
```

Expected: FAIL because canonical serialization, source registry and `cnki_scopes` do not exist.

- [ ] **Step 3: Implement canonical serialization and hash calculation**

```python
def canonical_json_bytes(value: object) -> bytes:
    if _contains_float(value):
        raise TypeError("规范目录不得包含浮点数")
    normalized = _canonicalize(value)
    text = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def compute_data_sha256(payload: Mapping[str, object]) -> str:
    draft = dict(payload)
    draft["data_sha256"] = "{{DATA_SHA256}}"
    return hashlib.sha256(canonical_json_bytes(draft)).hexdigest()
```

Sort journal records by `journal_id`; sort set-like arrays by NFKC text; sort source memberships by source registry order and source line. The source registry records the seven bundled artifact filenames, versions, sizes and SHA-256 values, plus stable document evidence IDs. Every record-level `evidence_id` must resolve exactly once.

- [ ] **Step 4: Build four fixed CNKI scope policies in JSON**

Use these exact policies:

```python
CNKI_SCOPE_RULES = {
    "chinese_environment_top": ("exact_titles", None, [6], None),
    "other_formally_recognized_chinese": ("exact_titles", None, [7], None),
    "environment_cssci": (
        "exact_titles", {"code": "P0209", "label": "CSSCI"}, [9], "CSSCI"
    ),
    "pku_core": (
        "topic_only", {"code": "P01", "label": "北大核心"}, list(range(1, 13)),
        "PKU_CORE"
    ),
}
```

Materialize eligible journal IDs during generation. The level-7 Chinese set is fixed in JSON at 60 records and validated during generation; runtime code must never infer it from Unicode characters.

- [ ] **Step 5: Run JSON and full bundle validation and verify GREEN**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py -k "canonical or cnki_scope or evidence_registry or priority_signature"
```

Expected: PASS; all evidence IDs resolve, all four scope sizes are fixed, and the priority signature remains unchanged.

- [ ] **Step 6: Commit the canonical bundle model**

```bash
git add top-journal-search-lists-env/scripts/environment_catalog_v4.py top-journal-search-lists-env/tests/test_environment_catalog_generation.py
git commit -m "feat: define environment v4 canonical catalog"
```

### Task 5: 确定性生成 Markdown、审计文件和双布局镜像

**Files:**
- Create: `top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py`
- Modify: `.gitignore`
- Modify: `top-journal-search-lists-env/.gitattributes`
- Create: `docs/audits/environment_journal_match_audit_v4.0.jsonl`
- Create: `docs/audits/environment_journal_match_audit_v4.0.md`
- Create: `top-journal-search-lists-env/references/environment_journal_catalog_v4.0.json`
- Create: `top-journal-search-lists-env/references/environment_catalog_sources_v4.0.json`
- Create: `top-journal-search-lists-env/references/environment_journal_match_audit_v4.0.md`
- Modify: `top-journal-search-lists-env/references/环境科学与工程学科顶尖期刊目录_v4.0.md`
- Create/Modify: the same four generated references under `top-journal-search-lists-env/mcpb/src/references/`
- Delete: both v3.0 Markdown references
- Modify: `top-journal-search-lists-env/tests/test_environment_catalog_generation.py`

**Interfaces:**
- Produces: `OutputPaths`、`render_catalog_markdown()`、`render_audit_jsonl()`、`render_audit_summary()`、`generate_outputs()`。
- CLI: `python scripts/generate_environment_catalog_v4.py [--check] [--references PATH] [--mcpb-references PATH]`.

- [ ] **Step 1: Write failing deterministic-output and mirror tests**

```python
def test_generated_outputs_are_deterministic_hashed_and_mirrored(tmp_path: Path) -> None:
    first = catalog.generate_outputs(output_paths(tmp_path / "one"), check=False)
    second = catalog.generate_outputs(output_paths(tmp_path / "two"), check=False)
    assert first == second
    for name in catalog.MIRRORED_REFERENCE_FILES:
        assert (tmp_path / "one/skill" / name).read_bytes() == (
            tmp_path / "one/mcpb" / name
        ).read_bytes()
    markdown = (tmp_path / "one/skill/环境科学与工程学科顶尖期刊目录_v4.0.md").read_text("utf-8")
    assert "revision_date: \"2026-07-31\"" in markdown
    assert "{{CONTENT_SHA256}}" not in markdown
    for statistic in (
        "前十级唯一期刊数：2022",
        "北大核心原始记录：1987",
        "排除前十级重复：245",
        "第十一、十二级净新增：1742",
        "受控别名：26",
    ):
        assert statistic in markdown


def test_generated_markdown_cannot_feed_derived_fields_back_into_matching(tmp_path: Path) -> None:
    first_paths = output_paths(tmp_path / "first", baseline=BASELINE, sources=SOURCES)
    catalog.generate_outputs(first_paths, check=False)
    second_paths = output_paths(
        tmp_path / "second",
        baseline=first_paths.skill_references / "环境科学与工程学科顶尖期刊目录_v4.0.md",
        sources=catalog.SourcePaths.from_references(first_paths.skill_references),
    )
    catalog.generate_outputs(second_paths, check=False)
    for name in catalog.MIRRORED_REFERENCE_FILES:
        assert (first_paths.skill_references / name).read_bytes() == (
            second_paths.skill_references / name
        ).read_bytes()
    assert first_paths.audit_jsonl.read_bytes() == second_paths.audit_jsonl.read_bytes()
    assert first_paths.audit_markdown.read_bytes() == second_paths.audit_markdown.read_bytes()
```

- [ ] **Step 2: Run the output test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_environment_catalog_generation.py::test_generated_outputs_are_deterministic_hashed_and_mirrored
```

Expected: FAIL because renderer, CLI, audit files and machine JSON have not been generated.

- [ ] **Step 3: Implement atomic generation and check mode**

```python
def generate_outputs(paths: OutputPaths, *, check: bool) -> dict[str, str]:
    bundle = build_catalog_bundle(paths.baseline, paths.sources)
    audit = bundle.audit_records
    validate_generated_bundle(bundle, audit)
    outputs = {
        "环境科学与工程学科顶尖期刊目录_v4.0.md": render_catalog_markdown(bundle),
        "environment_journal_catalog_v4.0.json": canonical_json_bytes(
            bundle.catalog_payload
        ).decode("utf-8"),
        "environment_catalog_sources_v4.0.json": canonical_json_bytes(
            bundle.source_registry
        ).decode("utf-8"),
        "environment_journal_match_audit_v4.0.md": render_audit_summary(bundle, audit),
    }
    _verify_or_write_mirrors(paths, outputs, check=check)
    _verify_or_write(paths.audit_jsonl, render_audit_jsonl(audit), check=check)
    _verify_or_write(paths.audit_markdown, outputs["environment_journal_match_audit_v4.0.md"], check=check)
    return {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in outputs.items()}
```

Write through a sibling temporary file followed by `Path.replace()`. `--check` performs byte comparison only and exits nonzero without writing. Render twelve tables with stable ID, immutable baseline title, formal title, aliases, environmental subfields, formal evidence, index memberships, original index categories and source catalogs. Level 11—12 environmental subfields remain empty. Rewrite the two PKU links to bundled relative filenames. Preserve structured SCIE and v2 disposition appendices in the bundle. The statistics section must state 2022 pre-PKU journals, 1987 original PKU members, 245 members already in levels 1—10, 1742 net additions in levels 11—12, all approved source intersections, 26 controlled aliases, the priority signature, JSON data hash, Markdown content hash and source-registry hash; recompute every value and both placeholder hashes rather than copying seed text.

`parse_v4_baseline()`只复用 `期刊ID`、`基线题名` 和五个锁定分级字段。每次运行都从基线题名以及固定的来源题名、人工更正映射重新生成正式题名，并在处理来源前将 ISSN、eISSN、索引身份、索引学科类别、来源成员、CNKI 路由和来源派生别名初始化为空。随后按七份快照的固定顺序重建，上一轮生成字段不得改变标识符优先匹配顺序、匹配方法标签或审计记录。

- [ ] **Step 4: Add exact line-ending rules**

Modify `top-journal-search-lists-env/.gitattributes` so generated JSON and Markdown are `text eol=lf`, while the seven copied source filenames in both references layouts are `-text`; Git must not rewrite source bytes whose hashes are in the registry. In root `.gitignore`, retain the general `*.jsonl` rule and add only these exceptions:

```gitignore
!docs/audits/
!docs/audits/environment_journal_match_audit_v4.0.jsonl
```

- [ ] **Step 5: Generate repository outputs and verify GREEN**

Run from `top-journal-search-lists-env`:

```powershell
python scripts/generate_environment_catalog_v4.py
python scripts/generate_environment_catalog_v4.py --check
python -m pytest -q -p no:cacheprovider tests/test_environment_catalog_generation.py
```

Expected: both generator commands exit 0; the test passes; audit status counts match the approved baseline; the two layouts are byte-identical.

- [ ] **Step 6: Commit generated data and audit artifacts**

Return to the repository root, then run:

```bash
git add .gitignore top-journal-search-lists-env/.gitattributes docs/audits top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py top-journal-search-lists-env/references top-journal-search-lists-env/mcpb/src/references top-journal-search-lists-env/tests/test_environment_catalog_generation.py
git commit -m "feat: generate environment v4 catalog artifacts"
```

### Task 6: 将运行时查询迁移到 v4 规范 JSON

**Files:**
- Modify: `top-journal-search-lists-env/scripts/catalog_lookup.py`
- Modify: `top-journal-search-lists-env/mcpb/src/catalog_lookup.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py`
- Modify: `top-journal-search-lists-env/tests/test_catalog_lookup.py`
- Modify: `top-journal-search-lists-env/tests/test_cnki_package_contract.py`

**Interfaces:**
- Produces: `CatalogIndex` with `by_journal_id`、`by_issn`、`by_formal_title`、`by_alias`、`by_normalized_title`、`records_by_priority_group`、`records_by_cnki_scope`。
- Keeps: `lookup_journals(path, journals)`、`journals_by_group(group, path)` and `--catalog` compatibility.
- Adds: `cnki_scope(scope_id, path)`.

- [ ] **Step 1: Rewrite catalog tests for v4 JSON and new fields**

```python
def test_lookup_returns_v4_identity_memberships_and_alias_method() -> None:
    module = _load_module()
    formal, alias = module.lookup_journals(
        CATALOG_JSON,
        ["WIREs Climate Change", "Wiley Interdisciplinary Reviews-Climate Change"],
    )
    assert formal["journal_id"] == alias["journal_id"]
    assert formal["priority_level"] == 8
    assert set(formal["index_memberships"]) == {"SSCI", "SCIE"}
    assert alias["match_method"] == "controlled_alias"
    for key in ("aliases", "index_subject_categories", "source_memberships", "revision_date"):
        assert key in formal


def test_cnki_scope_returns_explicit_members_not_runtime_language_guesses() -> None:
    scope = module.cnki_scope("other_formally_recognized_chinese", CATALOG_JSON)
    assert scope["catalog_version"] == "4.0"
    assert scope["journal_selector"] == "exact_titles"
    assert scope["source_category"] is None
    assert len(scope["eligible_journal_ids"]) == 60
    assert len(scope["journal_titles"]) == 60


def test_default_validate_auto_discovers_full_companions_and_all_mirrors() -> None:
    result = module.validate_catalog()
    assert result["validation_scope"] == "full"
    assert result["companion_files_verified"] == [
        "环境科学与工程学科顶尖期刊目录_v4.0.md",
        "environment_catalog_sources_v4.0.json",
        "environment_journal_match_audit_v4.0.md",
    ]
    assert result["mirrored_files_verified"] == 11


def test_explicit_standalone_catalog_without_companions_is_json_only(tmp_path: Path) -> None:
    standalone = tmp_path / "custom-environment-catalog.json"
    standalone.write_bytes(CATALOG_JSON.read_bytes())
    result = module.validate_catalog(standalone)
    assert result["validation_scope"] == "json_only"
    assert result["companion_files_verified"] == []
    assert result["mirrored_files_verified"] == 0


def test_cli_validate_reports_default_full_and_explicit_json_only(tmp_path: Path) -> None:
    default_run = subprocess.run(
        [sys.executable, str(SCRIPT), "validate"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    assert json.loads(default_run.stdout)["validation_scope"] == "full"

    standalone = tmp_path / "custom-environment-catalog.json"
    standalone.write_bytes(CATALOG_JSON.read_bytes())
    custom_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(standalone), "validate"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    assert json.loads(custom_run.stdout)["validation_scope"] == "json_only"
```

- [ ] **Step 2: Run lookup tests and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_catalog_lookup.py top-journal-search-lists-env/tests/test_cnki_package_contract.py
```

Expected: FAIL because the default still points to v3 Markdown and the new fields and scopes are absent.

- [ ] **Step 3: Implement cached JSON loading and indexes**

```python
@dataclass(frozen=True, slots=True)
class CatalogIndex:
    payload: dict[str, Any]
    by_journal_id: dict[str, dict[str, Any]]
    by_issn: dict[str, tuple[dict[str, Any], ...]]
    by_formal_title: dict[str, tuple[dict[str, Any], ...]]
    by_alias: dict[str, tuple[dict[str, Any], ...]]
    by_normalized_title: dict[str, tuple[dict[str, Any], ...]]
    records_by_priority_group: dict[str, tuple[dict[str, Any], ...]]
    records_by_cnki_scope: dict[str, tuple[dict[str, Any], ...]]


@lru_cache(maxsize=8)
def _load_catalog_cached(resolved_path: str, size: int, mtime_ns: int) -> CatalogIndex:
    payload = json.loads(Path(resolved_path).read_text(encoding="utf-8"))
    return _build_indexes(payload)
```

`load_catalog()` resolves the path and passes path, size and nanosecond mtime to the cache. Query order is exact formal title, exact alias, conservative normalized title; multiple IDs return `ambiguous`. Matched aliases return the current formal title and `controlled_alias`. Unmatched and ambiguous responses contain the same complete empty-field shape and `manual_review_required=True`.

- [ ] **Step 4: Implement automatic full validation, explicit JSON-only validation and CNKI scopes**

`validate_catalog()` always verifies JSON schema、dates、12 groups、counts、unique IDs/titles、priority signature、canonical data hash and no cross-level duplicate. When `path` resolves to `DEFAULT_CATALOG`, it must automatically discover the same-layout sibling Markdown、`environment_catalog_sources_v4.0.json` and `environment_journal_match_audit_v4.0.md`; absence or invalidity of any companion is a validation error and must never silently fall back to JSON-only validation. In a complete Skill checkout, it must also discover the peer `mcpb/src/references` directory and byte-verify all 11 mirrored reference files. A default successful result therefore returns `validation_scope="full"`, the three companion filenames and `mirrored_files_verified=11`.

Only an explicitly supplied non-default `--catalog` path may run without companions. If no companion arguments are supplied, validate the JSON contract and return `validation_scope="json_only"`, `companion_files_verified=[]` and `mirrored_files_verified=0`. If the caller supplies any of `--markdown`、`--sources`、`--audit-summary` or `--mirror-references`, require the complete three-file companion set, validate every supplied/discovered artifact, and return `validation_scope="full"`; partial companion input is an error. Add these four optional CLI arguments to the root parser and pass them only to the `validate` subcommand.

`cnki_scope()` retrieves the precomputed policy and records from `records_by_cnki_scope`, inserts formal `journal_titles`, and rejects unknown scopes with `ValueError`.

- [ ] **Step 5: Mirror code and run lookup tests GREEN**

```powershell
Copy-Item -LiteralPath top-journal-search-lists-env\scripts\catalog_lookup.py -Destination top-journal-search-lists-env\mcpb\src\catalog_lookup.py -Force
Copy-Item -LiteralPath top-journal-search-lists-env\scripts\cnki_search_env\catalog_adapter.py -Destination top-journal-search-lists-env\mcpb\src\cnki_search_env\catalog_adapter.py -Force
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_catalog_lookup.py top-journal-search-lists-env/tests/test_cnki_package_contract.py
```

Expected: PASS; default catalog is v4 JSON, representative queries cover all 12 levels, and both layouts resolve the same catalog.

- [ ] **Step 6: Commit runtime JSON lookup**

```bash
git add top-journal-search-lists-env/scripts/catalog_lookup.py top-journal-search-lists-env/mcpb/src/catalog_lookup.py top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/tests/test_catalog_lookup.py top-journal-search-lists-env/tests/test_cnki_package_contract.py
git commit -m "feat: query environment v4 JSON catalog"
```

### Task 7: 传播新增目录字段到论文模型与排序结果

**Files:**
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/models.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/ranking.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/ranking.py`
- Modify: `top-journal-search-lists-env/tests/test_cnki_models.py`
- Modify: `top-journal-search-lists-env/tests/test_cnki_ranking.py`

**Interfaces:**
- Adds to `PaperRecord`: `journal_id`、`aliases`、`index_subject_categories`、`source_memberships`、`revision_date`。
- Fixes immutable defaults: `catalog_version="4.0"`、`catalog_date="2026-07-29"`、`revision_date="2026-07-31"`。

- [ ] **Step 1: Write failing model and propagation tests**

```python
def test_annotation_propagates_v4_record_identity_and_source_evidence() -> None:
    ranked = annotate_and_sort_records([record("城市规划", 1)], catalog=CATALOG_JSON)
    item = ranked[0]
    assert item.journal_id and item.journal_id.startswith("ENVJ-")
    assert item.catalog_version == "4.0"
    assert item.catalog_date == "2026-07-29"
    assert item.revision_date == "2026-07-31"
    assert set(item.index_memberships) == {"CSSCI", "PKU_CORE"}
    assert "CSSCI" in item.index_subject_categories
    assert item.source_memberships
```

- [ ] **Step 2: Run model tests and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_ranking.py
```

Expected: FAIL because `PaperRecord` still fixes catalog v3.0 and lacks the new fields.

- [ ] **Step 3: Add fields and propagate exact lookup values**

```python
journal_id: str | None = None
aliases: list[str] = field(default_factory=list)
index_subject_categories: dict[str, list[str]] = field(default_factory=dict)
source_memberships: list[dict[str, Any]] = field(default_factory=list)
catalog_version: str = field(default="4.0", init=False)
catalog_date: str = field(default="2026-07-29", init=False)
revision_date: str = field(default="2026-07-31", init=False)
```

In `annotate_and_sort_records()`, assign the five fields from `lookup_journals()` with defensive list/dict copies. Preserve the existing sort key: matched before unmatched, lower priority level first, lower NCS internal rank first, then original result rank.

- [ ] **Step 4: Mirror runtime code and verify GREEN**

```powershell
Copy-Item -LiteralPath top-journal-search-lists-env\scripts\cnki_search_env\models.py -Destination top-journal-search-lists-env\mcpb\src\cnki_search_env\models.py -Force
Copy-Item -LiteralPath top-journal-search-lists-env\scripts\cnki_search_env\ranking.py -Destination top-journal-search-lists-env\mcpb\src\cnki_search_env\ranking.py -Force
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_ranking.py
```

Expected: PASS; unmatched records retain `None`/empty values and `manual_review_required=True`.

- [ ] **Step 5: Commit model propagation**

```bash
git add top-journal-search-lists-env/scripts/cnki_search_env/models.py top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py top-journal-search-lists-env/scripts/cnki_search_env/ranking.py top-journal-search-lists-env/mcpb/src/cnki_search_env/ranking.py top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_ranking.py
git commit -m "feat: propagate environment v4 journal metadata"
```

### Task 8: 执行数据子系统最终审计

**Files:**
- Verify only: all files listed in Tasks 1—7

**Interfaces:**
- Verifies: generator idempotence, canonical hashes, complete audit, runtime query, model propagation and byte-identical mirrors.
- Excludes: version bump, release build, installer, CI, CNKI page and field workflows.

- [ ] **Step 1: Run generator check and focused tests**

```powershell
Set-Location top-journal-search-lists-env
python scripts/generate_environment_catalog_v4.py --check
python scripts/catalog_lookup.py validate
python scripts/catalog_lookup.py lookup "Nature Climate Change" "WIREs Climate Change" "第三军医大学学报" "中国社会科学"
python -m pytest -q -p no:cacheprovider tests/test_environment_catalog_generation.py tests/test_catalog_lookup.py tests/test_cnki_models.py tests/test_cnki_ranking.py tests/test_cnki_package_contract.py
```

Expected: every command exits 0; lookup returns levels 2, 8, 11 and 12; `第三军医大学学报` resolves by controlled alias to `陆军军医大学学报`.

- [ ] **Step 2: Run static checks for the changed Python files**

From the repository root:

```powershell
ruff check top-journal-search-lists-env/scripts/environment_catalog_v4.py top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py top-journal-search-lists-env/scripts/catalog_lookup.py top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/scripts/cnki_search_env/models.py top-journal-search-lists-env/scripts/cnki_search_env/ranking.py
mypy top-journal-search-lists-env/scripts/
```

Expected: both commands exit 0.

- [ ] **Step 3: Verify mirrors and forbidden stale references**

```powershell
$skill = 'top-journal-search-lists-env\references'
$mcpb = 'top-journal-search-lists-env\mcpb\src\references'
$names = @(
  '环境科学与工程学科顶尖期刊目录_v4.0.md',
  'environment_journal_catalog_v4.0.json',
  'environment_catalog_sources_v4.0.json',
  'environment_journal_match_audit_v4.0.md',
  'CSSCI_2025_2026.md',
  '北大中文核心期刊目录_2023_自然科学版.md',
  '北大中文核心期刊目录_2023_.md',
  'Social Sciences Citation Index_20260715.md',
  'Social Sciences Citation Index (SSCI).csv',
  'Science Citation Index Expanded_20260715.md',
  'Science Citation Index Expanded (SCIE).csv'
)
foreach ($name in $names) {
  if ((Get-FileHash -LiteralPath (Join-Path $skill $name)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $mcpb $name)).Hash) { throw "镜像不一致：$name" }
}
if (rg -n "环境科学与工程学科顶尖期刊目录_v3\.0\.md|catalog_version.*3\.0" top-journal-search-lists-env/scripts top-journal-search-lists-env/mcpb/src top-journal-search-lists-env/tests) { throw '仍引用v3.0目录' }
```

Expected: no exception and no v3.0 runtime reference.

- [ ] **Step 4: Review repository scope and commit audit-only corrections if needed**

```bash
git status --short
git diff --check
```

Expected: only Tasks 1—7 listed paths are changed; no version, release, documentation, CI, installer or CNKI page file appears. If the audit required a direct data-test correction, commit it separately:

```bash
git add top-journal-search-lists-env/tests docs/audits
git commit -m "test: verify environment v4 data contract"
```
