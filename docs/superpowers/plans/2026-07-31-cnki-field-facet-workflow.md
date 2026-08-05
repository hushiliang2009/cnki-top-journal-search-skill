# CNKI 字段累计与来源类别工作流实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使通用版和环境版 CNKI 专业检索严格按 `TI → SU → KY → TKA` 累计合格记录，并在结果页完成受控的 CSSCI 或北大核心来源类别筛选、目录资格过滤、去重、限额和状态报告。

**Architecture:** 两版继续保留相互独立的 Python 包和 WebVPN 运行环境，但采用相同的表达式、分面、字段累计和断点身份契约。目录计划提供环境版 `cnki_scope()` 数据接口；专业检索层将目录范围转换为不可变 `SearchGroupPolicy`，页面层只负责执行表达式和结果页分面，服务层按目录资格过滤后再去重和计算限额。

**Tech Stack:** Python 3.11—3.14、asyncio、Playwright async API、FastMCP、Pydantic、pytest、ruff、mypy、Markdown。

## Global Constraints

- 本计划以 `docs/superpowers/specs/2026-07-31-environment-catalog-v4-cnki-source-category-design.md` 为唯一设计依据。
- 环境目录数据生成、3764种期刊增补、版本号、锁文件、构建白名单、安装器、CI矩阵、标签和Release由其他计划负责，本计划不得重复实现。
- 环境版开始实施前，目录计划必须提供 `cnki_scope(scope_id: str, path: Path = DEFAULT_CATALOG) -> dict[str, Any]`，并由 `cnki_search_env.catalog_adapter` 原样导出；返回值必须含`catalog_version`。
- 两版底层默认字段均为 `TI`；分组检索只允许依次使用 `TI`、`SU`、`KY`、`TKA`，累计唯一合格记录达到请求数量后停止。
- 使用者自备专业表达式继续单次原样执行，不自动替换字段，不自动添加来源类别。
- 来源类别不是专业检索字段，不得出现在表达式或 `LY=` 子句中；CSSCI固定为 `P0209`，北大核心固定为 `P01`，且不得作为MCP自由输入参数。
- 通用版分组仅为 `chinese_top_journals`、`cssci`；环境版分组仅为 `chinese_environment_top`、`other_formally_recognized_chinese`、`environment_cssci`、`pku_core`。
- 通用版 `cssci` 每个字段只提交一个主题与年份计划，再应用 CSSCI 结果页来源类别；不枚举综合目录去重后的661种期刊，也不把661误解为 CNKI 当前 CSSCI 及扩展版的来源总数。
- 环境版四个范围依次为第6级6种、第7级中文60种、第9级241种、v4.0全部1987种北大核心成员；第7级中文集合由目录构建期固化，运行时不得猜测语言。
- `pku_core`只提交主题与年份表达式并勾选北大核心，不生成`LY=`；第11级和第12级不得分别重复发起相同分面检索。
- 专业结果最多读取当前页50条；`first_page_only=true`必须返回。只有累计合格唯一记录达到请求数量且没有终止状态时，`complete`才可为真。
- 单组限额只计算当前策略认可的记录。近似`LY=`命中、目录未匹配、环境CSSCI非第9级记录和索引身份不符记录均进入组外报告，不占限额。
- CNKI页面契约没有可核验DOI，CNKI服务继续禁止返回或持久化`doi`、详情链接和下载字段；服务内按规范篇名、作者和年度去重。同一论文在多个字段命中时保留最先命中的字段，并合并命中字段和分组信息。Skill层合并ai4scholar等跨来源记录时才先按来源明确提供的DOI去重。
- 排序顺序固定为期刊层级、NCS内部顺序、最先命中的字段、原始结果顺序。
- 登录失效、401、403、429、安全验证、浏览器关闭或页面契约变化时立即停止后续批次和字段；来源类别失败不得退回未筛选结果。
- 专业检索继续使用可见、非持久化、人工值守的WebVPN会话；不得下载、保存Cookie或浏览器profile，不得绕过验证码、切换代理或导出登录态。
- 通用版源码与`mcpb/src/cnki_search`镜像、环境版源码与`mcpb/src/cnki_search_env`镜像必须字节一致。
- 通用版与环境版pytest必须分进程运行，避免顶层同名`catalog_lookup`模块互相污染。

---

## File Structure

### 通用版修改文件

- `top-journal-search-lists/scripts/cnki_search/models.py`：增加字段命中和分组命中元数据，继续禁止DOI和链接字段。
- `top-journal-search-lists/scripts/cnki_search/professional.py`：定义受控字段、来源类别、分组策略、执行计划和页面执行结果。
- `top-journal-search-lists/scripts/cnki_search/professional_service.py`：构建通用版策略，累计字段结果，执行资格过滤、去重和限额。
- `top-journal-search-lists/scripts/cnki_search/ranking.py`：加入字段优先级排序。
- `top-journal-search-lists/scripts/cnki_search/webvpn.py`：执行来源类别、筛选后状态复核和完整断点身份。
- `top-journal-search-lists/scripts/cnki_search/mcp_server.py`：锁定工具入参和返回契约。
- `top-journal-search-lists/mcpb/src/cnki_search/{models.py,professional.py,professional_service.py,ranking.py,webvpn.py,mcp_server.py}`：与源码逐字节同步。
- `top-journal-search-lists/tests/{test_cnki_models.py,test_cnki_professional.py,test_cnki_professional_service.py,test_cnki_ranking.py,test_cnki_source_category.py,test_cnki_webvpn_page.py,test_cnki_webvpn.py,test_cnki_professional_mcp.py,test_cnki_package_contract.py,test_mcpb_manifest.py}`：对应TDD和直接文档契约。
- `top-journal-search-lists/tests/_webvpn_e2e.py`：在既有敏感字段守卫下输出发布前人工值守冒烟测试所需的字段和来源类别摘要。
- `top-journal-search-lists/{SKILL.md,README.md,agents/openai.yaml,references/cnki-search-reference.md}`：记录字段累计、CSSCI结果页筛选和限制。

### 环境版修改文件

- `top-journal-search-lists-env/scripts/cnki_search_env/models.py`：保留并消费目录计划已加入的`journal_id`、`aliases`、`index_subject_categories`、`source_memberships`和`revision_date`，仅增加字段及分组命中元数据，继续禁止DOI和链接字段。
- `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`：导出目录计划提供的`cnki_scope()`。
- `top-journal-search-lists-env/scripts/cnki_search_env/professional.py`：定义与通用版同构的受控类型和执行计划。
- `top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py`：消费四个目录范围，累计并过滤合格记录。
- `top-journal-search-lists-env/scripts/cnki_search_env/ranking.py`、`webvpn.py`、`mcp_server.py`：分别处理排序、页面状态和MCP契约。
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/{models.py,catalog_adapter.py,professional.py,professional_service.py,ranking.py,webvpn.py,mcp_server.py}`：与源码逐字节同步。
- `top-journal-search-lists-env/tests/{test_cnki_models.py,test_cnki_professional_env.py,test_cnki_professional_service_env.py,test_cnki_ranking.py,test_cnki_webvpn_page_env.py,test_cnki_webvpn_env.py,test_cnki_professional_mcp_env.py,test_cnki_package_contract.py,test_skill_contract.py,test_mcpb_manifest.py}`：对应TDD和直接文档契约。
- `top-journal-search-lists-env/tests/_webvpn_e2e.py`：与通用版保持同一安全摘要契约，补充环境分组的分面与目录资格证据。
- `top-journal-search-lists-env/{SKILL.md,README.md,agents/openai.yaml,references/cnki-search-env-reference.md}`：记录四组顺序、北大核心分面和跨组总限额。

## Task 1: 固定表达式、策略与记录接口

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/models.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/professional.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/{models.py,professional.py}`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/models.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/professional.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/{models.py,professional.py}`
- Test: `top-journal-search-lists/tests/{test_cnki_models.py,test_cnki_professional.py}`
- Test: `top-journal-search-lists-env/tests/{test_cnki_models.py,test_cnki_professional_env.py}`

**Interfaces:**
- Produces: `TOPIC_FIELD_PRIORITY: tuple[str, ...] = ("TI", "SU", "KY", "TKA")`
- Produces: `SourceCategorySpec(code: Literal["P0209", "P01"], label: Literal["CSSCI", "北大核心"])`
- Produces: `SearchGroupPolicy(scope_id, catalog_version, journal_selector, source_category, journal_titles, eligible_journal_ids, eligible_priority_levels, required_index_membership, result_filter)`
- Produces: `ExpressionBatch(..., scope_id: str, catalog_version: str, topic_field: str | None, source_category: SourceCategorySpec | None)`
- Produces: `PlanExecutionResult(status, html, url, source_category_applied, source_category_total)`
- Produces: `build_topic_expression(..., topic_field="TI")`, `build_expression(..., topic_field="TI")`, `build_batches(..., topic_field="TI", scope_id=..., source_category=...)`

- [ ] **Step 1: Write failing contract tests in both packages**

```python
def test_all_builders_default_to_title_and_reject_unknown_fields() -> None:
    assert build_topic_expression("碳中和").startswith("TI %=")
    assert build_expression("碳中和", ["环境科学"]).startswith("TI %=")
    assert build_batches("碳中和", ["环境科学"])[0].topic_field == "TI"
    with pytest.raises(ValueError, match="TI、SU、KY、TKA"):
        build_topic_expression("碳中和", topic_field="AB")


def test_source_category_is_a_closed_pair_not_free_text() -> None:
    assert SourceCategorySpec("P0209", "CSSCI").code == "P0209"
    assert SourceCategorySpec("P01", "北大核心").label == "北大核心"
    with pytest.raises(ValueError):
        SourceCategorySpec("P01", "CSSCI")


def test_record_exposes_safe_dedup_and_match_metadata() -> None:
    names = {item.name for item in fields(PaperRecord)}
    assert {"topic_match_field", "matched_topic_fields", "matched_search_groups"} <= names
    assert not names & {"doi", "detail_url", "download_url", "pdf_url", "caj_url", "abstract"}
```

- [ ] **Step 2: Run tests to verify RED**

Run separately:

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_models.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_env.py top-journal-search-lists-env/tests/test_cnki_models.py
```

Expected: FAIL because the default is still `SU`, arbitrary fields are accepted, structured source categories and record match metadata do not exist.

- [ ] **Step 3: Implement the closed contracts identically in both packages**

```python
TOPIC_FIELD_PRIORITY = ("TI", "SU", "KY", "TKA")
TOPIC_FIELD = TOPIC_FIELD_PRIORITY[0]


def validate_topic_field(value: str) -> str:
    if value not in TOPIC_FIELD_PRIORITY:
        raise ValueError("检索字段只允许 TI、SU、KY、TKA")
    return value


@dataclass(frozen=True, slots=True)
class SourceCategorySpec:
    code: Literal["P0209", "P01"]
    label: Literal["CSSCI", "北大核心"]

    def __post_init__(self) -> None:
        if (self.code, self.label) not in {
            ("P0209", "CSSCI"), ("P01", "北大核心"),
        }:
            raise ValueError("来源类别代码与名称不匹配")


@dataclass(frozen=True, slots=True)
class SearchGroupPolicy:
    scope_id: str
    catalog_version: str
    journal_selector: Literal["exact_titles", "topic_only"]
    source_category: SourceCategorySpec | None
    journal_titles: tuple[str, ...]
    eligible_journal_ids: frozenset[str]
    eligible_priority_levels: frozenset[int]
    required_index_membership: str | None
    result_filter: Literal["matched_title", "matched_journal_id", "source_category"]


@dataclass(frozen=True, slots=True)
class PlanExecutionResult:
    status: str
    html: str
    url: str
    source_category_applied: bool = False
    source_category_total: int | None = None
```

Add these optional fields to `PaperRecord` after the existing required bibliographic fields:

```python
topic_match_field: str | None = None
matched_topic_fields: list[str] = field(default_factory=list)
matched_search_groups: list[str] = field(default_factory=list)
```

Environment `PaperRecord` consumes the directory plan's existing `journal_id`, `aliases`, `index_subject_categories`, `source_memberships` and `revision_date`; this task must not redefine or duplicate those fields. Keep the existing negative contract that rejects `doi`, detail URLs, download URLs, abstracts and full-text fields.

- [ ] **Step 4: Run tests to verify GREEN and mirror parity**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_models.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_env.py top-journal-search-lists-env/tests/test_cnki_models.py
```

Expected: both commands PASS; existing quote, year, parenthesis and 3000-character-budget tests remain green.

- [ ] **Step 5: Commit the contracts**

```bash
git add top-journal-search-lists/scripts/cnki_search/models.py top-journal-search-lists/scripts/cnki_search/professional.py top-journal-search-lists/mcpb/src/cnki_search/models.py top-journal-search-lists/mcpb/src/cnki_search/professional.py top-journal-search-lists/tests/test_cnki_models.py top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists-env/scripts/cnki_search_env/models.py top-journal-search-lists-env/scripts/cnki_search_env/professional.py top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py top-journal-search-lists-env/mcpb/src/cnki_search_env/professional.py top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_professional_env.py
git commit -m "feat: define controlled CNKI search contracts"
```

## Task 2: 改造通用版字段累计、资格过滤与限额

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/professional_service.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/ranking.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/{professional_service.py,ranking.py}`
- Test: `top-journal-search-lists/tests/{test_cnki_professional_service.py,test_cnki_ranking.py}`

**Interfaces:**
- Consumes: Task 1 `SearchGroupPolicy`, `SourceCategorySpec`, `TOPIC_FIELD_PRIORITY`, `PlanExecutionResult`
- Produces: `build_group_policy(group: str, *, catalog: Path = DEFAULT_CATALOG) -> SearchGroupPolicy`
- Produces: `build_group_plans(topic: str, *, policy: SearchGroupPolicy, topic_field: str, max_chars=3000, year_from=None, year_to=None) -> list[ExpressionBatch]`
- Produces: `_record_identity(record: PaperRecord) -> tuple[object, ...]`
- Produces: `_partition_eligible(records, policy, *, source_category_applied) -> tuple[list[PaperRecord], list[PaperRecord]]`
- Produces: `_run_field(batches, *, policy, remaining_limit) -> FieldOutcome`
- Keeps: `search_group(topic, group, *, limit=20, year_from=None, year_to=None) -> dict[str, Any]`

- [ ] **Step 1: Write failing cumulative and qualification tests**

```python
def test_fields_accumulate_unique_eligible_records_until_limit() -> None:
    service, seen = service_yielding_by_field({"TI": [paper("甲")], "SU": [paper("甲"), paper("乙")]})
    result = asyncio.run(service.search_group("碳中和", CHINESE_TOP_GROUP, limit=2))
    assert [record["title"] for record in result["records"]] == ["甲", "乙"]
    assert result["topic_fields_tried"] == ["TI", "SU"]
    assert [record["topic_match_field"] for record in result["records"]] == ["TI", "SU"]


def test_out_of_scope_rows_do_not_consume_limit() -> None:
    result = asyncio.run(service_with_near_ly_match().search_group(
        "生态", CHINESE_TOP_GROUP, limit=1,
    ))
    assert result["eligible_record_count"] == 1
    assert result["excluded_out_of_scope_count"] == 1
    assert result["records"][0]["journal_matched_title"] == "生态学报"


def test_all_fields_short_return_accumulated_unique_records_not_largest_field() -> None:
    service, seen = service_yielding_by_field({
        "TI": [paper("甲")],
        "SU": [paper("乙")],
        "KY": [paper("甲"), paper("丙")],
        "TKA": [paper("丁")],
    })
    result = asyncio.run(service.search_group("碳中和", CHINESE_TOP_GROUP, limit=10))
    assert [item["title"] for item in result["records"]] == ["甲", "乙", "丙", "丁"]
    assert result["topic_fields_tried"] == ["TI", "SU", "KY", "TKA"]
    assert [field_of(plan.expression) for plan in seen] == ["TI", "SU", "KY", "TKA"]
    assert result["complete"] is False


@pytest.mark.parametrize("terminal_status", [
    SearchStatus.CHALLENGE_DETECTED,
    SearchStatus.LOGIN_REQUIRED,
    SearchStatus.FORBIDDEN,
    SearchStatus.RATE_LIMITED,
    SearchStatus.PAGE_CONTRACT_CHANGED,
])
def test_blocking_field_keeps_qualified_partial_and_stops_later_fields(
    terminal_status: SearchStatus,
) -> None:
    service, seen = service_with_terminal_by_field(
        successful={"TI": [paper("已取得")], "SU": []},
        terminal_field="SU",
        terminal_status=terminal_status,
    )
    result = asyncio.run(service.search_group("环境治理", CHINESE_TOP_GROUP, limit=10))
    assert [item["title"] for item in result["records"]] == ["已取得"]
    assert result["status"] == SearchStatus.PARTIAL.value
    assert result["terminal_status"] == terminal_status.value
    assert result["human_intervention_required"] is True
    assert result["topic_fields_tried"] == ["TI", "SU"]
    assert [field_of(plan.expression) for plan in seen] == ["TI", "SU"]


def test_generic_cssci_uses_topic_only_plus_result_facet() -> None:
    policy = build_group_policy(CSSCI_GROUP)
    plans = build_group_plans("环境治理", policy=policy, topic_field="TI")
    assert len(plans) == 1
    assert plans[0].expression == "TI %= '环境治理'"
    assert "CSSCI" not in plans[0].expression
    assert plans[0].source_category == SourceCategorySpec("P0209", "CSSCI")
```

- [ ] **Step 2: Run the focused service tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional_service.py top-journal-search-lists/tests/test_cnki_ranking.py
```

Expected: FAIL because the service currently chooses one best field, counts unqualified rows, discards earlier fields when all four are short, and does not preserve qualified partial records consistently across every blocking status.

- [ ] **Step 3: Implement policies, qualified accumulation and bibliographic merging**

Use these fixed policies:

```python
def build_group_policy(group: str, *, catalog: Path = DEFAULT_CATALOG) -> SearchGroupPolicy:
    catalog_version = validate_catalog(catalog)["catalog_version"]
    if group == CHINESE_TOP_GROUP:
        titles = tuple(journals_by_group(group, catalog))
        return SearchGroupPolicy(group, catalog_version, "exact_titles", None, titles,
                                 frozenset(), frozenset({6}), None, "matched_title")
    if group == CSSCI_GROUP:
        return SearchGroupPolicy(group, catalog_version, "topic_only", SourceCategorySpec("P0209", "CSSCI"),
                                 (), frozenset(), frozenset(), "CSSCI", "source_category")
    raise ValueError(f"CNKI 专业检索不支持分组 {group!r}")
```

The fallback identity must no longer include the raw journal title:

```python
def _record_identity(record: PaperRecord) -> tuple[object, ...]:
    return (
        "metadata",
        " ".join(record.title.split()).casefold(),
        record.publication_year,
    )
```

Use this internal result type so field accumulation never round-trips through serialized dictionaries:

```python
@dataclass(slots=True)
class FieldOutcome:
    topic_field: str
    eligible_records: list[PaperRecord]
    excluded_records: list[PaperRecord]
    incomplete_records: list[PaperRecord]
    terminal_status: str | None
    human_intervention_required: bool
    source_category_applied: bool
    source_category_total: int | None
```

Within each title-year group, keep the existing normalized-author overlap rule so that normalized title, author and year jointly determine duplicates. When merging a later, more complete duplicate, copy the earliest `topic_match_field`; merge `matched_topic_fields` and `matched_search_groups` in declared order without duplicates.

Refactor the field loop to accumulate instead of selecting one field:

```python
eligible: list[PaperRecord] = []
excluded: list[PaperRecord] = []
tried: list[str] = []
for field in TOPIC_FIELD_PRIORITY:
    tried.append(field)
    outcome = await self._run_field(
        build_group_plans(topic, policy=policy, topic_field=field,
                          year_from=year_from, year_to=year_to),
        policy=policy,
        remaining_limit=limit - len(eligible),
    )
    eligible = _merge_candidate_records([*eligible, *outcome.eligible_records])
    excluded = _merge_candidate_records([*excluded, *outcome.excluded_records])
    if outcome.terminal_status is not None:
        terminal_status = outcome.terminal_status
        human_intervention_required = True
        break
    if len(eligible) >= limit:
        break
```

Never replace the accumulator with the single field having the largest result count. If all four fields are short, return their cumulative unique eligible records. For challenge, login required, forbidden, rate limited or page contract changed, retain prior eligible records, set `status=partial`, `human_intervention_required=true`, preserve the terminal status, and stop before the next field. Always parse up to `MAX_RESULTS_PER_PAGE`, then annotate, qualify and slice. Return `eligible_record_count`, `excluded_out_of_scope_count`, `excluded_out_of_scope_records`, `topic_fields_tried`, `topic_field` as the widest field reached, `first_page_only=true`, and `complete = terminal_status is None and eligible_record_count >= limit`.

Extend the ranking key:

```python
field_rank = {field: index for index, field in enumerate(TOPIC_FIELD_PRIORITY, start=1)}
key=lambda item: (
    item.priority_level is None,
    item.priority_level or 999,
    item.ncs_internal_rank or 999,
    field_rank.get(item.topic_match_field or "", 999),
    item.result_rank,
)
```

- [ ] **Step 4: Run service, ranking and regression tests to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional_service.py top-journal-search-lists/tests/test_cnki_ranking.py top-journal-search-lists/tests/test_cnki_results.py
```

Expected: PASS, including disjoint-author preservation, overlapping-author merge, metadata-completeness selection and eligible-only stopping.

- [ ] **Step 5: Commit the generic service**

```bash
git add top-journal-search-lists/scripts/cnki_search/professional_service.py top-journal-search-lists/scripts/cnki_search/ranking.py top-journal-search-lists/mcpb/src/cnki_search/professional_service.py top-journal-search-lists/mcpb/src/cnki_search/ranking.py top-journal-search-lists/tests/test_cnki_professional_service.py top-journal-search-lists/tests/test_cnki_ranking.py
git commit -m "feat: accumulate qualified CNKI field results"
```

## Task 3: 接入环境版四个目录范围

**Files:**
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/ranking.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/{catalog_adapter.py,professional_service.py,ranking.py}`
- Test: `top-journal-search-lists-env/tests/{test_cnki_professional_service_env.py,test_cnki_ranking.py}`

**Interfaces:**
- Consumes: `cnki_scope(scope_id: str, path: Path = DEFAULT_CATALOG) -> dict[str, Any]`
- Consumes exact payload keys: `scope_id`, `catalog_version`, `journal_selector`, `source_category`, `journal_titles`, `eligible_journal_ids`, `eligible_priority_levels`, `required_index_membership`, `result_filter`
- Produces: `SUPPORTED_GROUPS = ("chinese_environment_top", "other_formally_recognized_chinese", "environment_cssci", "pku_core")`
- Produces: `build_group_policy(group, *, catalog=DEFAULT_CATALOG) -> SearchGroupPolicy`

- [ ] **Step 1: Write failing four-scope and eligibility tests**

```python
@pytest.mark.parametrize(
    ("group", "journal_count", "selector", "facet"),
    [
        ("chinese_environment_top", 6, "exact_titles", None),
        ("other_formally_recognized_chinese", 60, "exact_titles", None),
        ("environment_cssci", 241, "exact_titles", SourceCategorySpec("P0209", "CSSCI")),
        ("pku_core", 1987, "topic_only", SourceCategorySpec("P01", "北大核心")),
    ],
)
def test_environment_policies_come_from_catalog(group, journal_count, selector, facet) -> None:
    policy = build_group_policy(group)
    assert policy.journal_selector == selector
    assert len(policy.eligible_journal_ids) == journal_count
    assert policy.source_category == facet


def test_pku_core_has_no_ly_and_accepts_members_at_levels_1_to_12() -> None:
    policy = build_group_policy("pku_core")
    plan = build_group_plans("气候治理", policy=policy, topic_field="TI")[0]
    assert plan.expression == "TI %= '气候治理'"
    assert "LY=" not in plan.expression
    assert policy.eligible_priority_levels == frozenset(range(1, 13))


def test_every_environment_cssci_batch_keeps_exact_titles_and_cssci_facet() -> None:
    policy = build_group_policy("environment_cssci")
    plans = build_group_plans("环境政策", policy=policy, topic_field="TI")
    assert len(plans) > 1
    assert all("LY=" in plan.expression for plan in plans)
    assert all(
        plan.source_category == SourceCategorySpec("P0209", "CSSCI")
        for plan in plans
    )


def test_pku_core_direct_scope_and_skill_supplement_bases_are_fixed() -> None:
    policy = build_group_policy("pku_core")
    matches = lookup_journals(DEFAULT_CATALOG, list(policy.journal_titles))
    higher = sum(1 for item in matches if 1 <= item["priority_level"] <= 10)
    supplement = sum(1 for item in matches if item["priority_level"] in {11, 12})
    assert len(policy.eligible_journal_ids) == 1987
    assert higher == 245
    assert supplement == 1742
    assert higher + supplement == 1987


def test_environment_cssci_excludes_non_level_nine_before_limit() -> None:
    result = asyncio.run(service_with_level_7_and_level_9().search_group(
        "环境政策", "environment_cssci", limit=1,
    ))
    assert [item["priority_level"] for item in result["records"]] == [9]
    assert result["excluded_out_of_scope_count"] == 1
```

- [ ] **Step 2: Run environment service tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py
```

Expected: FAIL because only two groups exist, `pku_core` is absent, and current field logic replaces earlier records instead of accumulating them.

- [ ] **Step 3: Convert the catalog payload to a closed policy and qualify by journal ID**

```python
def build_group_policy(group: str, *, catalog: Path = DEFAULT_CATALOG) -> SearchGroupPolicy:
    if group not in SUPPORTED_GROUPS:
        raise ValueError(f"CNKI 环境专业检索不支持分组 {group!r}")
    raw = cnki_scope(group, catalog)
    category = raw["source_category"]
    return SearchGroupPolicy(
        scope_id=raw["scope_id"],
        catalog_version=raw["catalog_version"],
        journal_selector=raw["journal_selector"],
        source_category=(None if category is None else
                         SourceCategorySpec(category["code"], category["label"])),
        journal_titles=tuple(raw["journal_titles"]),
        eligible_journal_ids=frozenset(raw["eligible_journal_ids"]),
        eligible_priority_levels=frozenset(raw["eligible_priority_levels"]),
        required_index_membership=raw["required_index_membership"],
        result_filter=raw["result_filter"],
    )
```

For `result_filter="matched_journal_id"`, a record is eligible only when all applicable conditions hold:

```python
eligible = (
    record.journal_id in policy.eligible_journal_ids
    and record.priority_level in policy.eligible_priority_levels
    and (
        policy.required_index_membership is None
        or policy.required_index_membership in record.index_memberships
    )
)
```

Port Task 2 cumulative-field, title-author-year merge, eligible-only limit and ranking behavior without importing the generic package. For direct `pku_core` calls, levels1—12 are valid; set `already_covered_higher_priority_count=0` because prior-group context belongs to the Skill workflow, not the single-group MCP call.

- [ ] **Step 4: Run environment service tests to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py top-journal-search-lists-env/tests/test_catalog_lookup.py
```

Expected: PASS; fixed counts are 6, 60, 241 and 1987, and `pku_core` produces one topic-only plan per field.

- [ ] **Step 5: Commit the environment policies**

```bash
git add top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py top-journal-search-lists-env/scripts/cnki_search_env/ranking.py top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_service.py top-journal-search-lists-env/mcpb/src/cnki_search_env/ranking.py top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py
git commit -m "feat: add catalog-driven environmental CNKI scopes"
```

## Task 4: 强化结果页来源类别与筛选后状态

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py`
- Test: `top-journal-search-lists/tests/{test_cnki_source_category.py,test_cnki_webvpn_page.py}`
- Test: `top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py`

**Interfaces:**
- Consumes: `SourceCategorySpec`, `PlanExecutionResult`
- Produces: `apply_source_category(category: SourceCategorySpec, *, timeout_seconds=20.0) -> SourceCategoryApplication`
- Produces: `execute_plan(plan: ExpressionBatch) -> PlanExecutionResult`

- [ ] **Step 1: Write failing page-state tests in both layouts**

```python
def test_unchanged_total_is_valid_when_checkbox_is_checked_and_page_is_stable() -> None:
    outcome = asyncio.run(_driver(stable_page(total="50")).apply_source_category(
        SourceCategorySpec("P0209", "CSSCI"), timeout_seconds=0.1,
    ))
    assert outcome.applied is True
    assert outcome.total == 50


@pytest.mark.parametrize(
    ("after_status", "expected"),
    [(SearchStatus.NO_RESULTS, "no_results"),
     (SearchStatus.CHALLENGE_DETECTED, "challenge_detected"),
     (SearchStatus.PAGE_CONTRACT_CHANGED, "page_contract_changed")],
)
def test_execute_plan_rechecks_status_after_facet(after_status, expected) -> None:
    result = asyncio.run(driver_after_facet(after_status).execute_plan(cssci_plan()))
    assert result.status == expected
    assert result.html == ""
    assert "set_page_size" not in driver.events


def test_missing_or_unchecked_facet_never_returns_unfiltered_html() -> None:
    result = asyncio.run(driver_with_unusable_facet().execute_plan(pku_plan()))
    assert result.status == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result.source_category_applied is False
    assert result.html == ""
```

- [ ] **Step 2: Run page tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_source_category.py top-journal-search-lists/tests/test_cnki_webvpn_page.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py
```

Expected: FAIL because current success detection relies on total-count change and sets page size before reclassifying the post-facet page.

- [ ] **Step 3: Implement checked-state and stable-page verification**

```python
@dataclass(frozen=True, slots=True)
class SourceCategoryApplication:
    requested: SourceCategorySpec
    applied: bool
    total: int | None
    status: SearchStatus


async def apply_source_category(self, category: SourceCategorySpec, *,
                                timeout_seconds: float = 20.0) -> SourceCategoryApplication:
    box = self.page.locator(
        f"input[type=checkbox][value='{category.code}']"
    ).first
    if await await_maybe(box.count()) != 1:
        raise WebVpnNavigationError(f"结果页未找到来源类别：{category.label}")
    await await_maybe(box.check())
    previous: tuple[object, ...] | None = None
    stable = 0
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        await asyncio.sleep(0.5)
        checked = bool(await await_maybe(box.is_checked()))
        status = await self.classify_outcome()
        total_text = await self.total_results()
        rows = await await_maybe(
            self.page.locator(RESULT_TABLE_SELECTOR + " tbody tr").count()
        )
        snapshot = (checked, status.value, total_text, rows)
        stable = stable + 1 if checked and snapshot == previous else 0
        previous = snapshot
        if stable >= 1 and status is not SearchStatus.PAGE_CONTRACT_CHANGED:
            total = int(total_text.replace(",", "")) if total_text else None
            return SourceCategoryApplication(category, True, total, status)
    raise WebVpnNavigationError(f"来源类别未稳定生效：{category.label}")
```

The exact `execute_plan` order is:

```python
await self.fill_expression(plan.expression)
await self.submit()
status = await self.wait_for_outcome()
application = None
if status is SearchStatus.SUCCESS and plan.source_category is not None:
    try:
        application = await self.apply_source_category(plan.source_category)
        status = application.status
    except WebVpnNavigationError:
        status = SearchStatus.PAGE_CONTRACT_CHANGED
if status is SearchStatus.SUCCESS:
    await self.set_page_size(plan.page_size)
    status = await self.wait_for_outcome()
html = await await_maybe(self.page.content()) if status is SearchStatus.SUCCESS else ""
return PlanExecutionResult(
    status.value, html, str(self.page.url),
    source_category_applied=bool(application and application.applied),
    source_category_total=None if application is None else application.total,
)
```

- [ ] **Step 4: Run both page suites to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_source_category.py top-journal-search-lists/tests/test_cnki_webvpn_page.py top-journal-search-lists/tests/test_cnki_webvpn_outcome.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py top-journal-search-lists-env/tests/test_cnki_webvpn_outcome_env.py
```

Expected: PASS; event order is submit, first status, facet, second status, page size, final status, HTML.

- [ ] **Step 5: Commit the page workflow**

```bash
git add top-journal-search-lists/scripts/cnki_search/webvpn.py top-journal-search-lists/mcpb/src/cnki_search/webvpn.py top-journal-search-lists/tests/test_cnki_source_category.py top-journal-search-lists/tests/test_cnki_webvpn_page.py top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py
git commit -m "fix: verify CNKI result facets before parsing"
```

## Task 5: 将范围、字段和来源类别纳入断点身份

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py`
- Test: `top-journal-search-lists/tests/test_cnki_webvpn.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_webvpn_env.py`

**Interfaces:**
- Produces: `_checkpoint_token(batches: Sequence[ExpressionBatch]) -> str`
- Keeps: checkpoint files sanitized; raw expressions, URLs, HTML, Cookie and browser paths remain absent

- [ ] **Step 1: Write failing checkpoint-isolation tests**

```python
def batch(expression: str, scope_id: str, topic_field: str,
          category: SourceCategorySpec | None, *,
          catalog_version: str = "2026-07-15") -> ExpressionBatch:
    return ExpressionBatch(
        index=1, total=1, journals=(), expression=expression,
        scope_id=scope_id, catalog_version=catalog_version,
        topic_field=topic_field, source_category=category,
    )


def test_same_expression_with_cssci_and_pku_facets_has_distinct_tokens() -> None:
    cssci = batch("TI %= '气候'", "cssci", "TI", SourceCategorySpec("P0209", "CSSCI"))
    pku = batch("TI %= '气候'", "pku_core", "TI", SourceCategorySpec("P01", "北大核心"))
    assert _checkpoint_token([cssci]) != _checkpoint_token([pku])


def test_same_expression_in_different_fields_or_scopes_has_distinct_tokens() -> None:
    assert _checkpoint_token([batch("X", "scope-a", "TI", None)]) != \
           _checkpoint_token([batch("X", "scope-a", "SU", None)])
    assert _checkpoint_token([batch("X", "scope-a", "TI", None)]) != \
           _checkpoint_token([batch("X", "scope-b", "TI", None)])


def test_same_scope_and_expression_in_different_catalog_versions_has_distinct_tokens() -> None:
    assert _checkpoint_token([batch("X", "scope-a", "TI", None, catalog_version="3.0")]) != \
           _checkpoint_token([batch("X", "scope-a", "TI", None, catalog_version="4.0")])
```

- [ ] **Step 2: Run checkpoint tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_webvpn.py -k "checkpoint"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_webvpn_env.py -k "checkpoint"
```

Expected: FAIL because the current token hashes expression text only.

- [ ] **Step 3: Hash the complete in-memory identity without persisting it**

```python
def _checkpoint_token(batches: Sequence[ExpressionBatch]) -> str:
    identity = [
        {
            "expression": batch.expression,
            "scope_id": batch.scope_id,
            "catalog_version": batch.catalog_version,
            "topic_field": batch.topic_field,
            "source_category": (
                None if batch.source_category is None else {
                    "code": batch.source_category.code,
                    "label": batch.source_category.label,
                }
            ),
            "page_size": batch.page_size,
        }
        for batch in batches
    ]
    canonical = json.dumps(identity, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Replace the inline expression-only hash in `run_batches()` with this helper. Add only `topic_match_field`, `matched_topic_fields` and `matched_search_groups` to the safe checkpoint record whitelist, applying the existing length, control-character and sensitive-text guards. Continue rejecting `doi`, URLs, HTML and download fields.

- [ ] **Step 4: Run the complete checkpoint suites to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_webvpn.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_webvpn_env.py
```

Expected: PASS, including malformed checkpoint rejection, fail-closed persistence, resume, clear-after-completion and throttle tests.

- [ ] **Step 5: Commit checkpoint isolation**

```bash
git add top-journal-search-lists/scripts/cnki_search/webvpn.py top-journal-search-lists/mcpb/src/cnki_search/webvpn.py top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py top-journal-search-lists-env/tests/test_cnki_webvpn_env.py
git commit -m "fix: isolate CNKI checkpoints by search scope"
```

## Task 6: 固定MCP分组与返回契约

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/mcp_server.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/mcp_server.py`
- Modify: `top-journal-search-lists/tests/_webvpn_e2e.py`
- Modify: `top-journal-search-lists-env/tests/_webvpn_e2e.py`
- Test: `top-journal-search-lists/tests/test_cnki_professional_mcp.py`
- Test: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_professional_mcp_env.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_package_contract.py`

**Interfaces:**
- Keeps: `cnki_professional_search(topic, group="chinese_top_journals", limit=50, year_from=None, year_to=None)`
- Keeps: `cnki_professional_search_env(topic, group="chinese_environment_top", limit=50, year_from=None, year_to=None)`
- Keeps: `source_category` absent from both public tool schemas
- Produces environment group regex: `^(chinese_environment_top|other_formally_recognized_chinese|environment_cssci|pku_core)$`

- [ ] **Step 1: Write failing MCP schema and response tests**

```python
def test_environment_group_schema_lists_exactly_four_controlled_scopes() -> None:
    schema = professional_tool_schema()
    assert schema["properties"]["group"]["pattern"] == (
        "^(chinese_environment_top|other_formally_recognized_chinese|"
        "environment_cssci|pku_core)$"
    )
    assert "source_category" not in schema["properties"]


def test_professional_result_exposes_field_facet_and_scope_counts() -> None:
    result = asyncio.run(call_professional_tool())
    for key in (
        "source_category_requested", "source_category_applied",
        "source_category_total", "source_category_code", "topic_fields_tried",
        "eligible_record_count", "excluded_out_of_scope_count",
        "excluded_out_of_scope_records", "already_covered_higher_priority_count",
        "already_covered_higher_priority_records", "first_page_only", "complete",
        "human_intervention_required",
    ):
        assert key in result


def test_attended_e2e_summary_keeps_only_safe_release_diagnostics() -> None:
    summary = e2e._summary(professional_result(), "cssci")
    assert summary["topic_fields_tried"] == ["TI", "SU"]
    assert summary["source_category_code"] == "P0209"
    assert summary["source_category_applied"] is True
    assert summary["eligible_record_count"] == 3
    assert summary["first_page_only"] is True
    assert summary["complete"] is True
    assert summary["human_intervention_required"] is False
    serialized = json.dumps(summary, ensure_ascii=False).casefold()
    for forbidden in ("cookie", "token", "html", "url", "password", "download"):
        assert forbidden not in serialized
```

- [ ] **Step 2: Run MCP tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional_mcp.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_mcp_env.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_package_contract.py -k "e2e_summary"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_package_contract.py -k "e2e_summary"
```

Expected: FAIL because environment MCP only accepts two groups, the new diagnostic fields are absent, and the attended E2E summary currently strips the field and facet evidence needed by the release smoke gate.

- [ ] **Step 3: Update only controlled groups and descriptions**

Keep `limit` at `1..50`, year bounds unchanged, and do not expose `topic_field` or `source_category`. Map runtime exceptions to the existing stable statuses. The service result must always include the listed fields; for groups without a facet return `source_category_requested=None`, `source_category_applied=False`, `source_category_total=None`, and `source_category_code=None`. Direct custom-expression execution returns `topic_fields_tried=[]` and does not add a facet.

Update both private `_webvpn_e2e.py` helpers so `_summary()` copies only the following additional, type-checked values from the service result: `topic_fields_tried` as a controlled list of `TI/SU/KY/TKA`, `source_category_code` as `None/P0209/P01`, and the booleans or integers `source_category_applied`, `eligible_record_count`, `first_page_only`, `complete`, `human_intervention_required`. Keep the existing fail-closed sanitizer, fixed error output and prohibition on URLs, HTML, Cookie, credentials, paths and downloads. These helpers remain excluded from both release packages and CI network execution; they exist only for an explicitly authorized attended smoke test against the checked-out source.

- [ ] **Step 4: Run MCP and runtime tests to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_professional_mcp.py top-journal-search-lists/tests/test_cnki_professional_runtime.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_mcp_env.py top-journal-search-lists-env/tests/test_cnki_professional_runtime_env.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_package_contract.py -k "webvpn_e2e"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_package_contract.py -k "webvpn_e2e"
```

Expected: PASS; tools/list schemas contain no caller-controlled facet and both services retain independent environment variables and runtimes.

- [ ] **Step 5: Commit MCP contracts**

```bash
git add top-journal-search-lists/scripts/cnki_search/mcp_server.py top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py top-journal-search-lists/tests/_webvpn_e2e.py top-journal-search-lists/tests/test_cnki_professional_mcp.py top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists-env/scripts/cnki_search_env/mcp_server.py top-journal-search-lists-env/mcpb/src/cnki_search_env/mcp_server.py top-journal-search-lists-env/tests/_webvpn_e2e.py top-journal-search-lists-env/tests/test_cnki_professional_mcp_env.py top-journal-search-lists-env/tests/test_cnki_package_contract.py
git commit -m "feat: expose controlled CNKI scope diagnostics"
```

## Task 7: 直接测试Skill与文档工作流

**Files:**
- Modify: `top-journal-search-lists/{SKILL.md,README.md,agents/openai.yaml,references/cnki-search-reference.md}`
- Modify: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Modify: `top-journal-search-lists-env/{SKILL.md,README.md,agents/openai.yaml,references/cnki-search-env-reference.md}`
- Modify: `top-journal-search-lists-env/tests/{test_cnki_package_contract.py,test_skill_contract.py}`

**Interfaces:**
- Documents: field accumulation rather than best-field replacement
- Documents: CSSCI and 北大核心 are result-page source categories, never professional fields
- Documents: environment cross-group order and one global limit
- Documents: first-page and partial-result boundaries

- [ ] **Step 1: Write failing direct documentation tests**

```python
def test_professional_documentation_states_field_and_facet_contract(skill_root: Path) -> None:
    for relative in ("SKILL.md", "README.md", "references/cnki-search-reference.md"):
        text = (skill_root / relative).read_text(encoding="utf-8")
        assert "TI → SU → KY → TKA" in text
        assert "累计" in text
        assert "来源类别不是专业检索字段" in text
        assert "P0209" in text
        assert "first_page_only" in text


def test_environment_docs_state_one_pku_scope_and_global_order(skill_root: Path) -> None:
    text = "\n".join(
        (skill_root / relative).read_text(encoding="utf-8")
        for relative in ("SKILL.md", "README.md", "references/cnki-search-env-reference.md")
    )
    assert "other_formally_recognized_chinese" in text
    assert "pku_core" in text
    assert "P01" in text
    assert "第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心" in text
    assert "第11级和第12级不得分别重复检索" in text
```

- [ ] **Step 2: Run direct documentation tests to verify RED**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_package_contract.py -k "documentation"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_package_contract.py top-journal-search-lists-env/tests/test_skill_contract.py
```

Expected: FAIL because existing texts still describe `SU` or best-field replacement and environment coverage still has only two groups.

- [ ] **Step 3: Update the four direct documents in each Skill**

State these operational rules verbatim and consistently:

```text
分组检索依次执行 TI、SU、KY、TKA，并累计此前字段尚未取得的合格唯一记录；达到请求数量即停。
CSSCI和北大核心只在首次检索成功后的结果页来源类别中筛选，不写入专业检索表达式。
环境检索依次执行第6级、第7级中文期刊、第9级CSSCI和一个pku_core范围；跨组总量只计算全局去重后的新增论文。
第11级和第12级不得分别重复检索；pku_core结果按目录层级排序后补充。
first_page_only=true表示每条表达式只读取当前页最多50条；complete=false时不得声称检索完整。
```

Also state that `LY=` may近似命中，组外记录不占限额并列入`excluded_out_of_scope_records`；高层级重复项在完整环境工作流中标为`already_covered_higher_priority`，不占后续剩余总限额。

- [ ] **Step 4: Run direct documentation tests to verify GREEN**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_package_contract.py -k "documentation"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_package_contract.py top-journal-search-lists-env/tests/test_skill_contract.py
```

Expected: PASS; no document claims that来源类别 is an expression field or that four fields replace one another.

- [ ] **Step 5: Commit direct documentation**

```bash
git add top-journal-search-lists/SKILL.md top-journal-search-lists/README.md top-journal-search-lists/agents/openai.yaml top-journal-search-lists/references/cnki-search-reference.md top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists-env/SKILL.md top-journal-search-lists-env/README.md top-journal-search-lists-env/agents/openai.yaml top-journal-search-lists-env/references/cnki-search-env-reference.md top-journal-search-lists-env/tests/test_cnki_package_contract.py top-journal-search-lists-env/tests/test_skill_contract.py
git commit -m "docs: explain CNKI field and facet workflow"
```

## Task 8: 锁定镜像并运行分版回归

**Files:**
- Modify: `top-journal-search-lists/tests/test_mcpb_manifest.py`
- Modify: `top-journal-search-lists-env/tests/test_mcpb_manifest.py`
- Verify: all files listed in this plan

**Interfaces:**
- Produces: byte-parity test for every modified runtime module and its MCPB mirror
- Verifies: no version, lockfile, installer, release artifact or directory data file changed in this plan

- [ ] **Step 1: Add failing explicit mirror tests**

```python
@pytest.mark.parametrize(
    "name",
    ("models.py", "professional.py", "professional_service.py",
     "ranking.py", "webvpn.py", "mcp_server.py"),
)
def test_modified_runtime_module_matches_mcpb_mirror(skill_root: Path, name: str) -> None:
    assert (skill_root / "scripts/cnki_search" / name).read_bytes() == \
           (skill_root / "mcpb/src/cnki_search" / name).read_bytes()
```

Use `cnki_search_env` and include `catalog_adapter.py` in the environment parameterization.

- [ ] **Step 2: Run mirror tests to verify RED if any copy drift remains**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_mcpb_manifest.py -k "modified_runtime"
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_mcpb_manifest.py -k "modified_runtime"
```

Expected: FAIL only when a source/mirror pair differs; copy the authoritative source bytes to its mirror, then rerun.

- [ ] **Step 3: Run the complete focused runtime suites separately**

```powershell
python -m pytest -q -p no:cacheprovider top-journal-search-lists/tests/test_cnki_models.py top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_professional_service.py top-journal-search-lists/tests/test_cnki_ranking.py top-journal-search-lists/tests/test_cnki_source_category.py top-journal-search-lists/tests/test_cnki_webvpn_page.py top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_professional_mcp.py top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists/tests/test_mcpb_manifest.py
python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_professional_env.py top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py top-journal-search-lists-env/tests/test_cnki_webvpn_env.py top-journal-search-lists-env/tests/test_cnki_professional_mcp_env.py top-journal-search-lists-env/tests/test_cnki_package_contract.py top-journal-search-lists-env/tests/test_skill_contract.py top-journal-search-lists-env/tests/test_mcpb_manifest.py
```

Expected: both commands PASS with no network access.

- [ ] **Step 4: Run static checks on both independent source trees**

```powershell
python -m ruff check top-journal-search-lists/scripts top-journal-search-lists/tests
python -m mypy top-journal-search-lists/scripts/cnki_search
python -m ruff check top-journal-search-lists-env/scripts top-journal-search-lists-env/tests
python -m mypy top-journal-search-lists-env/scripts/cnki_search_env
```

Expected: all four commands exit 0.

- [ ] **Step 5: Confirm scope and commit the regression gate**

```powershell
git diff --name-only
git diff --check
git status --short
```

Expected: only files listed in this plan are modified; no generated directory, version, lockfile, installer or release artifact appears.

```bash
git add top-journal-search-lists/tests/test_mcpb_manifest.py top-journal-search-lists-env/tests/test_mcpb_manifest.py
git commit -m "test: lock CNKI runtime mirror parity"
```

实施完成后，将上述提交交给版本与发布计划统一更新版本、构建白名单、CI产物、标签和Release；不得在本计划中提前发布。
