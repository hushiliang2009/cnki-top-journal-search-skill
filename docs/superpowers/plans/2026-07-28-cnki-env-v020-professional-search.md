# CNKI 环境版 v0.2.0 专业检索实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在保持环境领域十级期刊目录和公开主题检索的基础上，为 `top-journal-search-lists-env` 增加可生产使用的 WebVPN 人工值守专业检索，并发布独立版本 v0.2.0。

**Architecture:** 环境版独立包含专业表达式、WebVPN 页面驱动、运行时和 MCP 接口，不导入通用版 Python 包。环境目录提供 6 种中文环境顶级期刊和 241 种环境 CSSCI 期刊；执行计划按目录动态生成，环境 CSSCI 每批同时采用精确期刊条件和 CSSCI 来源类别。

**Tech Stack:** Python 3.11+、asyncio、Playwright async API、FastMCP、Pydantic、pytest、ruff、mypy、PowerShell、POSIX Shell、GitHub Actions。

## Global Constraints

- 本计划在通用版 v0.4.1 完成并通过自动化测试后执行。
- 环境版版本从 `0.1.0` 提升为 `0.2.0`，目录版本继续固定为 `3.0`，目录日期继续固定为 `2026-07-26`。
- 公开工具保持 `cnki_search_env(query, limit=20)`。
- 新工具为 `cnki_professional_search_env(topic, group, limit=50, year_from=None, year_to=None)`。
- 专业分组只允许 `chinese_environment_top` 和 `environment_cssci`。
- `chinese_environment_top` 必须来自目录第六级 6 种期刊。
- `environment_cssci` 必须来自目录第九级 241 种期刊，并对每个批次设置 CSSCI 来源类别。
- 表达式长度上限为 3000 字符，批次数由构建器动态计算。
- 正常专业检索请求之间至少间隔 30 秒；浏览器任务串行执行。
- 使用可见、非持久化浏览器上下文，禁止下载，不保存登录状态。
- 环境变量固定为 `CNKI_ENV_WEBVPN_HOME`，不得读取或覆盖 `CNKI_WEBVPN_HOME`。
- CI 不访问 CNKI；正式发布产物仅由 Ubuntu Python 3.11 的环境版任务构建。
- 真实 WebVPN 端到端验证未通过前，不创建 `top-journal-search-lists-env-v0.2.0` 标签和 Release。

---

## File Structure

### 新建文件

- `top-journal-search-lists-env/scripts/cnki_search_env/professional.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_service.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/professional_runtime.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_runtime.py`
- `top-journal-search-lists-env/tests/test_cnki_professional.py`
- `top-journal-search-lists-env/tests/test_cnki_professional_service.py`
- `top-journal-search-lists-env/tests/test_cnki_professional_mcp.py`
- `top-journal-search-lists-env/tests/test_cnki_professional_runtime.py`
- `top-journal-search-lists-env/tests/test_cnki_webvpn.py`
- `top-journal-search-lists-env/tests/test_cnki_webvpn_page.py`
- `top-journal-search-lists-env/tests/test_cnki_webvpn_outcome.py`
- `top-journal-search-lists-env/tests/test_cnki_source_category.py`
- `top-journal-search-lists-env/tests/_webvpn_e2e.py`

### 修改文件

- `top-journal-search-lists-env/scripts/catalog_lookup.py`
- `top-journal-search-lists-env/mcpb/src/catalog_lookup.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/models.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/search.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/search.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/session.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/session.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/mcp_server.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/mcp_server.py`
- `top-journal-search-lists-env/scripts/cnki_search_env/__init__.py`
- `top-journal-search-lists-env/mcpb/src/cnki_search_env/__init__.py`
- `top-journal-search-lists-env/scripts/build_release.py`
- `top-journal-search-lists-env/mcpb/manifest.json`
- `top-journal-search-lists-env/mcpb/pyproject.toml`
- `top-journal-search-lists-env/mcpb/uv.lock`
- `top-journal-search-lists-env/tests/test_catalog_lookup.py`
- `top-journal-search-lists-env/tests/test_cnki_models.py`
- `top-journal-search-lists-env/tests/test_cnki_search_env.py`
- `top-journal-search-lists-env/tests/test_cnki_session.py`
- `top-journal-search-lists-env/tests/test_cnki_mcp.py`
- `top-journal-search-lists-env/tests/test_cnki_package_contract.py`
- `top-journal-search-lists-env/tests/test_mcpb_manifest.py`
- `top-journal-search-lists-env/tests/test_installers.py`
- `top-journal-search-lists-env/tests/_mcp_handshake.py`
- `top-journal-search-lists-env/tests/_mcpb_handshake.py`
- `top-journal-search-lists-env/tests/_mcpb_raw_handshake.py`
- `top-journal-search-lists-env/README.md`
- `top-journal-search-lists-env/SKILL.md`
- `top-journal-search-lists-env/references/cnki-search-env-reference.md`
- `top-journal-search-lists-env/agents/openai.yaml`
- `.github/workflows/ci.yml`

## Task 1: 同步公开检索的页面状态修正

**Files:**
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/models.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/search.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/search.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/session.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/session.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_models.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_search_env.py`
- Test: `top-journal-search-lists-env/tests/test_cnki_session.py`

**Interfaces:**
- Produces: `MAX_RESULTS_PER_PAGE = 50`
- Produces: `SearchStatus.NO_DATA_RETRY_LATER`
- Produces: `PUBLIC_SEARCH_BUTTON_SELECTOR = ".search-btn"`
- Keeps: public MCP limit 1 to 20

- [ ] **Step 1: Add failing public-page regression tests**

```python
def test_public_button_falls_back_to_current_cnki_selector() -> None:
    page = RecordingPage(role_count=0, selector_count=1)
    button = asyncio.run(public_theme_search_button(page))
    assert button is page.selector_button


def test_post_submit_challenge_is_not_reported_as_contract_change() -> None:
    snapshot = asyncio.run(session.search("环境规制"))
    assert classify_public_search_state(**snapshot.state_arguments()) is SearchStatus.CHALLENGE_DETECTED


def test_no_data_retry_later_is_a_distinct_status() -> None:
    assert SearchStatus.NO_DATA_RETRY_LATER.value == "no_data_retry_later"
```

- [ ] **Step 2: Run the tests and verify RED**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_search_env.py top-journal-search-lists-env/tests/test_cnki_session.py -q
```

Expected: FAIL because the selector fallback, post-submit blocking snapshot and new status are absent.

- [ ] **Step 3: Add the shared page-size constant without widening the public MCP**

Add `MAX_RESULTS_PER_PAGE = 50` for professional result parsing and page controls. Keep `SearchRequest` validation at 1 to 20 and keep `mcp_server.MAX_LIMIT = 20`.

- [ ] **Step 4: Add the button fallback**

```python
PUBLIC_SEARCH_BUTTON_SELECTOR = ".search-btn"

async def public_theme_search_button(page: Any) -> Any:
    button = page.get_by_role("button", name=PUBLIC_SEARCH_BUTTON_NAME)
    if await await_maybe(button.count()) != 1:
        button = page.locator(PUBLIC_SEARCH_BUTTON_SELECTOR)
    if await await_maybe(button.count()) != 1:
        raise PageContractChanged("知网公开首页主题检索按钮结构已变化")
    return button
```

- [ ] **Step 5: Classify blocking pages after submission**

When `PublicThemeSearchRunner.run()` raises `PageContractChanged`, capture the current page and return it only if classification is one of:

```python
frozenset({
    SearchStatus.CHALLENGE_DETECTED,
    SearchStatus.LOGIN_REQUIRED,
    SearchStatus.FORBIDDEN,
    SearchStatus.RATE_LIMITED,
    SearchStatus.NETWORK_ERROR,
})
```

Unknown pages must still raise `PageContractChanged`.

- [ ] **Step 6: Run focused tests and verify GREEN**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_search_env.py top-journal-search-lists-env/tests/test_cnki_session.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add top-journal-search-lists-env/scripts/cnki_search_env/models.py top-journal-search-lists-env/mcpb/src/cnki_search_env/models.py top-journal-search-lists-env/scripts/cnki_search_env/search.py top-journal-search-lists-env/mcpb/src/cnki_search_env/search.py top-journal-search-lists-env/scripts/cnki_search_env/session.py top-journal-search-lists-env/mcpb/src/cnki_search_env/session.py top-journal-search-lists-env/tests/test_cnki_models.py top-journal-search-lists-env/tests/test_cnki_search_env.py top-journal-search-lists-env/tests/test_cnki_session.py
git commit -m "fix: update environmental public search contracts"
```

## Task 2: 从环境目录生成专业检索计划

**Files:**
- Modify: `top-journal-search-lists-env/scripts/catalog_lookup.py`
- Modify: `top-journal-search-lists-env/mcpb/src/catalog_lookup.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py`
- Create: `top-journal-search-lists-env/scripts/cnki_search_env/professional.py`
- Create: `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional.py`
- Create: `top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py`
- Create: `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_service.py`
- Test: `top-journal-search-lists-env/tests/test_catalog_lookup.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_professional.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_professional_service.py`

**Interfaces:**
- Produces: `journals_by_group(group: str, path: Path = DEFAULT_CATALOG) -> list[str]`
- Produces: `ExpressionBatch(index: int, total: int, journals: tuple[str, ...], expression: str, page_size: int = 50, source_category: str | None = None)`
- Produces: `build_group_plans(topic: str, group: str, *, catalog: Path, max_chars: int, year_from: int | None, year_to: int | None) -> list[ExpressionBatch]`
- Produces: `CnkiProfessionalSearchService.search_group(topic: str, group: str, *, limit: int, year_from: int | None, year_to: int | None) -> Awaitable[dict[str, Any]]`

- [ ] **Step 1: Write failing catalog group tests**

```python
def test_professional_groups_come_from_the_environment_catalog() -> None:
    assert len(module.journals_by_group("chinese_environment_top", CATALOG)) == 6
    assert len(module.journals_by_group("environment_cssci", CATALOG)) == 241
    assert "中国环境科学" in module.journals_by_group(
        "chinese_environment_top", CATALOG
    )
```

- [ ] **Step 2: Run catalog tests and verify RED**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_catalog_lookup.py -q
```

Expected: FAIL because `journals_by_group` does not exist.

- [ ] **Step 3: Expose directory-backed group enumeration**

Implement:

```python
def journals_by_group(group: str, path: Path = DEFAULT_CATALOG) -> list[str]:
    if group not in EXPECTED_GROUPS:
        raise ValueError(f"未知环境期刊层级：{group}")
    records, _ = _parse_records(_read_catalog(path))
    return [
        record["matched_title"]
        for record in records
        if record["priority_group"] == group
    ]
```

Export it through `catalog_adapter.py`.

- [ ] **Step 4: Write failing expression-plan tests**

```python
def test_environment_top_is_one_exact_batch() -> None:
    plans = preview_plans("环境规制", CHINESE_ENVIRONMENT_TOP_GROUP)
    assert len(plans) == 1
    assert sum(len(plan.journals) for plan in plans) == 6
    assert all(plan.source_category is None for plan in plans)


def test_environment_cssci_is_dynamically_batched_and_faceted() -> None:
    plans = preview_plans("环境规制", ENVIRONMENT_CSSCI_GROUP)
    assert len(plans) >= 2
    assert sum(len(plan.journals) for plan in plans) == 241
    assert all(len(plan.expression) <= 3000 for plan in plans)
    assert all(plan.source_category == "CSSCI" for plan in plans)
    assert len({journal for plan in plans for journal in plan.journals}) == 241
```

- [ ] **Step 5: Implement expression construction**

Create `professional.py` with:

- official fields `SU`, `LY`, `YE`;
- NFKC normalization and full-width or half-width title variants;
- safe single-quote rejection;
- `year_clause`;
- `build_expression`;
- `ExpressionBatch`;
- `build_batches` using the 3000-character limit.

Use this exact dataclass:

```python
@dataclass(frozen=True, slots=True)
class ExpressionBatch:
    index: int
    total: int
    journals: tuple[str, ...]
    expression: str
    page_size: int = MAX_RESULTS_PER_PAGE
    source_category: str | None = None
```

- [ ] **Step 6: Implement environment group plans**

```python
CHINESE_ENVIRONMENT_TOP_GROUP = "chinese_environment_top"
ENVIRONMENT_CSSCI_GROUP = "environment_cssci"
SUPPORTED_GROUPS = (
    CHINESE_ENVIRONMENT_TOP_GROUP,
    ENVIRONMENT_CSSCI_GROUP,
)

def build_group_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    journals = journals_by_group(group, catalog)
    plans = build_batches(
        topic,
        journals,
        year_from=year_from,
        year_to=year_to,
        max_chars=max_chars,
    )
    if group == ENVIRONMENT_CSSCI_GROUP:
        plans = [replace(plan, source_category="CSSCI") for plan in plans]
    return plans


def preview_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    return build_group_plans(
        topic,
        group,
        catalog=catalog,
        max_chars=max_chars,
        year_from=year_from,
        year_to=year_to,
    )
```

- [ ] **Step 7: Implement service parsing, ranking, stopping and deduplication**

The executor signature is:

```python
ExpressionExecutor = Callable[
    [ExpressionBatch],
    Awaitable[tuple[str, str, str]],
]
```

The service must:

- serialize batches through `run_batches`;
- parse only periodical rows;
- stop once unique complete records reach `limit`;
- retain the more complete duplicate;
- annotate with the environment catalog;
- remove result URLs from external output;
- expose `group`, `journal_count`, `batches_completed`, `batches_total`, `limit_reached`, `complete` and `human_intervention_required`.

- [ ] **Step 8: Run planner and service tests**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_catalog_lookup.py top-journal-search-lists-env/tests/test_cnki_professional.py top-journal-search-lists-env/tests/test_cnki_professional_service.py -q
```

Expected: PASS, with group counts 6 and 241.

- [ ] **Step 9: Commit**

```powershell
git add top-journal-search-lists-env/scripts/catalog_lookup.py top-journal-search-lists-env/mcpb/src/catalog_lookup.py top-journal-search-lists-env/scripts/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/mcpb/src/cnki_search_env/catalog_adapter.py top-journal-search-lists-env/scripts/cnki_search_env/professional.py top-journal-search-lists-env/mcpb/src/cnki_search_env/professional.py top-journal-search-lists-env/scripts/cnki_search_env/professional_service.py top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_service.py top-journal-search-lists-env/tests/test_catalog_lookup.py top-journal-search-lists-env/tests/test_cnki_professional.py top-journal-search-lists-env/tests/test_cnki_professional_service.py
git commit -m "feat: build environmental professional search plans"
```

## Task 3: 增加环境版 WebVPN 会话和生产运行时

**Files:**
- Create: `top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py`
- Create: `top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py`
- Create: `top-journal-search-lists-env/scripts/cnki_search_env/professional_runtime.py`
- Create: `top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_runtime.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_webvpn.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_webvpn_page.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_webvpn_outcome.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_source_category.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_professional_runtime.py`

**Interfaces:**
- Produces: `WebVpnConfig(home_url: str, login_timeout_seconds: float = 600.0, poll_interval_seconds: float = 3.0)`
- Produces: `Throttle`, `BatchCheckpoint`, `run_batches`
- Produces: `ProfessionalSearchPage.execute_plan(plan)`
- Produces: `ProfessionalSearchRuntime`
- Produces: `build_professional_runtime_from_env()`

- [ ] **Step 1: Write failing WebVPN contract tests**

Require:

- minimum request interval 30 seconds;
- visible browser launch;
- `browser.new_context(locale="zh-CN", accept_downloads=False)`;
- no `launch_persistent_context`;
- login timeout 600 seconds;
- advanced search reached from the home-page link, never by deep link;
- exact professional textarea selector;
- visible button fallback order;
- CSSCI facet value `P0209`;
- page-size option 50;
- visible CAPTCHA detection only;
- `no_data_retry_later` distinct from no results.

- [ ] **Step 2: Run the new tests and verify RED**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_webvpn.py top-journal-search-lists-env/tests/test_cnki_webvpn_page.py top-journal-search-lists-env/tests/test_cnki_webvpn_outcome.py top-journal-search-lists-env/tests/test_cnki_source_category.py -q
```

Expected: collection errors because the WebVPN module does not yet exist.

- [ ] **Step 3: Implement the non-persistent session**

Use:

```python
browser = await playwright.chromium.launch(headless=False)
context = await browser.new_context(
    locale="zh-CN",
    accept_downloads=False,
)
```

Track and close page, context, browser and Playwright. Do not define a profile path.

- [ ] **Step 4: Implement the batch scheduler**

Provide:

```python
async def run_batches(
    batches: Sequence[ExpressionBatch],
    execute: BatchExecutor,
    *,
    on_challenge: ChallengeHandler | None = None,
    checkpoint: BatchCheckpoint | None = None,
    throttle: Throttle | None = None,
    max_challenge_retries: int = 3,
    should_stop: Callable[[list[dict[str, Any]]], bool] | None = None,
) -> dict[str, Any]:
```

Use SHA256 checkpoint identity and safe serialized records only. Never persist raw expressions, URLs or HTML.

Retry `network_error` at most once and call `Throttle.wait()` before the retry. Challenge recovery remains limited to three user-completed attempts. All other failure statuses stop or return without automatic retry.

Continue after `no_results` because a later journal batch may contain records. Stop on `no_data_retry_later`, `page_contract_changed`, `forbidden`, `rate_limited`, exhausted `network_error` or unresolved `challenge_detected`, and expose that value as `terminal_status`. Preserve the terminal status when no prior records exist; otherwise return `partial`.

- [ ] **Step 5: Implement the professional page driver**

The driver must execute:

```text
open_from_home
→ switch_to_professional
→ fill_expression
→ submit
→ classify_outcome
→ optional apply_source_category
→ set_page_size(50)
→ classify_outcome
→ content
```

Return a structured status when any page contract is missing.

After submission, poll for an outcome for up to 30 seconds. A temporary `page_contract_changed` classification while the result table is rendering is not final; return it only after the polling deadline. Repeat the wait after applying the source category and after changing page size.

- [ ] **Step 6: Implement the environment runtime**

Use:

```python
WEBVPN_HOME_ENV = "CNKI_ENV_WEBVPN_HOME"

class ProfessionalSearchRuntime:
    def __init__(self, session: WebVpnSession,
                 service: CnkiProfessionalSearchService) -> None:
        self.session = session
        self.service = service
        self._lock = asyncio.Lock()
        self._closed = False

    async def search_group(
        self,
        topic: str,
        group: str,
        *,
        limit: int,
        year_from: int | None,
        year_to: int | None,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("环境版 WebVPN 专业检索运行时已关闭")
        async with self._lock:
            self.session.ensure_open()
            return await self.service.search_group(
                topic,
                group,
                limit=limit,
                year_from=year_from,
                year_to=year_to,
            )

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            await self.session.close()

async def build_professional_runtime_from_env() -> ProfessionalSearchRuntime:
    home_url = (os.environ.get(WEBVPN_HOME_ENV) or "").strip()
    if not home_url:
        raise ValueError(f"请设置 {WEBVPN_HOME_ENV}")
    session = WebVpnSession(WebVpnConfig(home_url))
    try:
        await session.__aenter__()
        await session.wait_until_ready()
        executor = ProfessionalBatchExecutor(session)
        service = CnkiProfessionalSearchService(
            executor,
            throttle=Throttle(default_state_dir() / "throttle"),
            checkpoint=BatchCheckpoint(default_state_dir() / "checkpoint.json"),
            on_challenge=executor.wait_for_manual_challenge,
        )
        return ProfessionalSearchRuntime(session, service)
    except BaseException:
        await session.close()
        raise
```

The throttle and sanitized checkpoint state may use `~/.cnki-search-env/`; no browser state may be stored there.

`ProfessionalBatchExecutor` retains a result tab only when `challenge_detected` is visible. Its `wait_for_manual_challenge()` polls for at most 600 seconds and never clicks, drags, reloads or modifies the page. After the user completes verification, close that tab and let the scheduler retry the current expression after the required backoff.

- [ ] **Step 7: Test cancellation and resource release**

Cover:

- login timeout;
- user closes the window;
- cancellation during throttle sleep;
- cancellation during page search;
- runtime close with queued request;
- cleanup after factory construction fails.

- [ ] **Step 8: Run all new runtime tests**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_webvpn.py top-journal-search-lists-env/tests/test_cnki_webvpn_page.py top-journal-search-lists-env/tests/test_cnki_webvpn_outcome.py top-journal-search-lists-env/tests/test_cnki_source_category.py top-journal-search-lists-env/tests/test_cnki_professional_runtime.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

```powershell
git add top-journal-search-lists-env/scripts/cnki_search_env/webvpn.py top-journal-search-lists-env/mcpb/src/cnki_search_env/webvpn.py top-journal-search-lists-env/scripts/cnki_search_env/professional_runtime.py top-journal-search-lists-env/mcpb/src/cnki_search_env/professional_runtime.py top-journal-search-lists-env/tests/test_cnki_webvpn.py top-journal-search-lists-env/tests/test_cnki_webvpn_page.py top-journal-search-lists-env/tests/test_cnki_webvpn_outcome.py top-journal-search-lists-env/tests/test_cnki_source_category.py top-journal-search-lists-env/tests/test_cnki_professional_runtime.py
git commit -m "feat: add environmental WebVPN runtime"
```

## Task 4: 注册环境版专业检索 MCP 工具

**Files:**
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/mcp_server.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/mcp_server.py`
- Modify: `top-journal-search-lists-env/tests/test_cnki_mcp.py`
- Create: `top-journal-search-lists-env/tests/test_cnki_professional_mcp.py`
- Modify: `top-journal-search-lists-env/tests/test_cnki_async.py`
- Modify: `top-journal-search-lists-env/tests/_mcp_handshake.py`
- Modify: `top-journal-search-lists-env/tests/_mcpb_handshake.py`
- Modify: `top-journal-search-lists-env/tests/_mcpb_raw_handshake.py`

**Interfaces:**
- Produces: `REQUIRED_TOOLS = ["cnki_search_env", "cnki_professional_search_env"]`
- Produces: professional MCP limit 1 to 50
- Consumes: `build_professional_runtime_from_env`

- [ ] **Step 1: Write failing MCP schema tests**

```python
def test_environment_server_registers_both_tools() -> None:
    mcp = CnkiMcpServer().build_fastmcp(RecordingMcp)
    assert set(mcp.tools) == {
        "cnki_search_env",
        "cnki_professional_search_env",
    }


def test_professional_schema_is_environment_specific() -> None:
    schema = tool_schema("cnki_professional_search_env")
    assert schema["properties"]["group"]["pattern"] == (
        "^(chinese_environment_top|environment_cssci)$"
    )
    assert schema["properties"]["limit"]["maximum"] == 50
```

- [ ] **Step 2: Run MCP tests and verify RED**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_mcp.py top-journal-search-lists-env/tests/test_cnki_professional_mcp.py -q
```

Expected: FAIL because only `cnki_search_env` is registered.

- [ ] **Step 3: Add the professional method**

```python
async def cnki_professional_search_env(
    self,
    topic: str,
    group: str = CHINESE_ENVIRONMENT_TOP_GROUP,
    limit: int = MAX_PROFESSIONAL_LIMIT,
    year_from: int | None = None,
    year_to: int | None = None,
) -> dict[str, Any]:
```

Use the default runtime factory when `CNKI_ENV_WEBVPN_HOME` is configured. Reject unsupported groups before creating the browser session.

- [ ] **Step 4: Register the FastMCP tool**

Use Pydantic constraints:

```python
topic: Annotated[str, Field(min_length=1, pattern=r".*\S.*")]
group: Annotated[
    str,
    Field(pattern=r"^(chinese_environment_top|environment_cssci)$"),
]
limit: Annotated[int, Field(ge=1, le=50)] = 50
```

The description must state that login and continuous human attendance are required and scheduled tasks are unsupported.

- [ ] **Step 5: Add asynchronous close and exception mapping**

Keep `shutdown()` non-blocking and add `aclose()` that cancels active tasks and awaits runtime closure. Construct the real FastMCP instance with an `asynccontextmanager` lifespan whose `finally` block awaits `self.aclose()` on the same event loop. Fake FastMCP classes used by schema tests retain their current name-only constructor. Map configuration, login, page-contract and network failures to structured statuses; re-raise cancellation.

Constrain optional `year_from` and `year_to` to `1900` through `date.today().year + 1` in the MCP schema. Reject a missing endpoint and `year_from > year_to` before starting the browser.

- [ ] **Step 6: Update all handshake expectations**

Require exact sorted tools:

```python
["cnki_professional_search_env", "cnki_search_env"]
```

Do this for Skill, installed MCPB and raw MCPB handshakes.

- [ ] **Step 7: Run MCP and async tests**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_mcp.py top-journal-search-lists-env/tests/test_cnki_professional_mcp.py top-journal-search-lists-env/tests/test_cnki_async.py -q
python top-journal-search-lists-env/tests/_mcp_handshake.py
python top-journal-search-lists-env/tests/_mcpb_handshake.py
python top-journal-search-lists-env/tests/_mcpb_raw_handshake.py
```

Expected: PASS and both tools are present.

- [ ] **Step 8: Commit**

```powershell
git add top-journal-search-lists-env/scripts/cnki_search_env/mcp_server.py top-journal-search-lists-env/mcpb/src/cnki_search_env/mcp_server.py top-journal-search-lists-env/tests/test_cnki_mcp.py top-journal-search-lists-env/tests/test_cnki_professional_mcp.py top-journal-search-lists-env/tests/test_cnki_async.py top-journal-search-lists-env/tests/_mcp_handshake.py top-journal-search-lists-env/tests/_mcpb_handshake.py top-journal-search-lists-env/tests/_mcpb_raw_handshake.py
git commit -m "feat: expose environmental professional search MCP"
```

## Task 5: 更新环境版版本、文档和发布契约

**Files:**
- Create: `top-journal-search-lists-env/tests/_webvpn_e2e.py`
- Modify: `top-journal-search-lists-env/scripts/cnki_search_env/__init__.py`
- Modify: `top-journal-search-lists-env/mcpb/src/cnki_search_env/__init__.py`
- Modify: `top-journal-search-lists-env/scripts/build_release.py`
- Modify: `top-journal-search-lists-env/mcpb/manifest.json`
- Modify: `top-journal-search-lists-env/mcpb/pyproject.toml`
- Modify: `top-journal-search-lists-env/mcpb/uv.lock`
- Modify: `top-journal-search-lists-env/tests/test_cnki_package_contract.py`
- Modify: `top-journal-search-lists-env/tests/test_mcpb_manifest.py`
- Modify: `top-journal-search-lists-env/tests/test_installers.py`
- Modify: `top-journal-search-lists-env/README.md`
- Modify: `top-journal-search-lists-env/SKILL.md`
- Modify: `top-journal-search-lists-env/references/cnki-search-env-reference.md`
- Modify: `top-journal-search-lists-env/agents/openai.yaml`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: version `0.2.0`
- Produces: Skill ZIP and `cnki-search-env.mcpb` containing four professional modules
- Produces: environment-only E2E helper

- [ ] **Step 1: Change version and manifest expectations to 0.2.0**

Update tests first and run:

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_mcp.py top-journal-search-lists-env/tests/test_mcpb_manifest.py -q
```

Expected: FAIL on current `0.1.0`.

- [ ] **Step 2: Update version sources and lock**

Change both `__init__.py`, manifest and pyproject to `0.2.0`, then:

```powershell
uv lock --project top-journal-search-lists-env/mcpb
```

Assert package, manifest, serverInfo and lock entry all report `0.2.0`.

- [ ] **Step 3: Extend release allowlists**

Add:

```text
professional.py
professional_service.py
professional_runtime.py
webvpn.py
```

to `CNKI_MODULES`, and add all new `test_cnki_professional_*`, `test_cnki_webvpn*` and `test_cnki_source_category.py` files to `TEST_ALLOWLIST`. Keep `_webvpn_e2e.py` repository-only.

- [ ] **Step 4: Replace the public-only package boundary**

`test_cnki_package_contract.py` must:

- keep public modules free of WebVPN, login and download code;
- classify the four professional files as isolated WebVPN modules;
- require human-attendance declarations;
- forbid proxy rotation, User-Agent modification, stealth code, `storage_state` and persistent contexts;
- test both tools in both source layouts.

- [ ] **Step 5: Update the manifest and client descriptions**

The manifest must list both tools. README, SKILL.md, reference and `agents/openai.yaml` must distinguish:

- public theme search, max 20;
- environmental professional search, max 50;
- 6 exact environment top journals;
- 241 exact environment CSSCI journals plus CSSCI facet;
- `CNKI_ENV_WEBVPN_HOME`;
- non-persistent login and restart requirement;
- no login automation, no download and no scheduled execution.

- [ ] **Step 6: Add the sanitized environment E2E helper**

Accept the two environment groups only. Print title, journal, year, environmental priority level and batch counts. Recursively reject URL, Cookie, HTML, storage state, profile and absolute path fields.

- [ ] **Step 7: Strengthen CI coexistence checks**

In the existing environment jobs:

- keep Python 3.11 to 3.14 on Ubuntu;
- keep Python 3.11 on Windows and macOS;
- run both environment handshakes;
- build environment artifacts only;
- upload only from Ubuntu Python 3.11.

Add an installer test that installs both products into the same isolated `CODEX_HOME` and confirms `[mcp_servers.cnki-search]` and `[mcp_servers.cnki-search-env]` both remain intact.

- [ ] **Step 8: Run package, installer and workflow tests**

```powershell
python -m pytest top-journal-search-lists-env/tests/test_cnki_package_contract.py top-journal-search-lists-env/tests/test_mcpb_manifest.py top-journal-search-lists-env/tests/test_installers.py top-journal-search-lists-env/tests/test_release_baseline.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

```powershell
git add top-journal-search-lists-env .github/workflows/ci.yml
git commit -m "chore: prepare environmental search v0.2.0"
```

## Task 6: 完成环境版自动化验证和共存复核

**Files:**
- Modify only if a failing check identifies a defect in files already listed above.

**Interfaces:**
- Consumes: completed generic v0.4.1 and environment v0.2.0 code
- Produces: evidence for the environment release PR

- [ ] **Step 1: Run static analysis**

```powershell
ruff check .
mypy top-journal-search-lists-env/scripts/
```

Expected: exit 0.

- [ ] **Step 2: Run the complete environment suite**

```powershell
python -m pytest top-journal-search-lists-env -q -p no:cacheprovider
python top-journal-search-lists-env/scripts/catalog_lookup.py validate
python top-journal-search-lists-env/tests/_mcp_handshake.py
python top-journal-search-lists-env/tests/_mcpb_handshake.py
python top-journal-search-lists-env/tests/_mcpb_raw_handshake.py
```

Expected: zero failures, catalog counts unchanged, both tools exposed.

- [ ] **Step 3: Re-run the complete generic suite**

```powershell
python -m pytest top-journal-search-lists -q -p no:cacheprovider
```

Expected: zero failures. Environment changes must not regress the generic product.

- [ ] **Step 4: Build the environment artifacts twice**

```powershell
python top-journal-search-lists-env/scripts/build_release.py --output work/env-release-a
python top-journal-search-lists-env/scripts/build_release.py --output work/env-release-b
Get-FileHash work/env-release-a/* -Algorithm SHA256
Get-FileHash work/env-release-b/* -Algorithm SHA256
```

Expected: byte-identical Skill ZIP, MCPB and checksum file.

- [ ] **Step 5: Inspect package boundaries**

Both environment archives must contain all four professional modules and no caches, repository metadata, browser profiles, login state, HTML or downloads.

- [ ] **Step 6: Install both products into one isolated Windows home**

Run the generic v0.4.1 installer, then the environment v0.2.0 installer. Confirm:

- both Skill directories exist;
- both runtimes exist;
- both MCP configuration tables exist;
- each server announces its own version;
- generic tools and environment tools do not share names;
- reinstalling either product preserves the other.

- [ ] **Step 7: Review the environment production path**

Trace:

```text
cnki_professional_search_env
→ build_professional_runtime_from_env
→ environment WebVpnSession
→ environment ProfessionalBatchExecutor
→ 6-journal or 241-journal group plan
→ CSSCI facet when required
→ environment catalog ranking
```

Confirm every group list originates from the environment catalog and no generic catalog is imported.

- [ ] **Step 8: Commit any review fixes**

If review identifies a defect, reproduce it with a failing focused test, fix it and commit:

```powershell
git add top-journal-search-lists-env .github/workflows/ci.yml
git commit -m "fix: address environmental v0.2.0 verification findings"
```

Do not create an empty commit.

## Task 7: 人工验证、环境版发布和 ChatGPT Desktop 升级

**Files:**
- No source changes unless live verification identifies a reproducible defect.
- Release attachments: `top-journal-search-lists-env_Skill.zip`, `cnki-search-env.mcpb`, `checksums.sha256`

**Interfaces:**
- Consumes: reviewed v0.2.0 branch and user-supplied `CNKI_ENV_WEBVPN_HOME`
- Produces: tag `top-journal-search-lists-env-v0.2.0`, independent GitHub Release and verified local installation

- [ ] **Step 1: Run the 6-journal E2E**

```powershell
$env:CNKI_ENV_WEBVPN_HOME='<用户提供的 WebVPN 知网首页>'
C:\Python314\python.exe top-journal-search-lists-env\tests\_webvpn_e2e.py --topic '环境' --group chinese_environment_top --limit 5
```

Verify exact-journal scope, page size 50, bibliographic fields and environmental level 6.

- [ ] **Step 2: Run the 241-journal CSSCI E2E**

```powershell
C:\Python314\python.exe top-journal-search-lists-env\tests\_webvpn_e2e.py --topic '环境规制' --group environment_cssci --limit 5
```

Verify previewed dynamic batch count, CSSCI facet on every submitted batch, environment level 9 and sanitized output.

- [ ] **Step 3: Stop on a failed live gate**

If either E2E cannot complete, retain the branch without a release. Record only structured status and sanitized diagnostics. Add a failing automated regression test before changing code.

- [ ] **Step 4: Push and create the environment PR**

```powershell
git push -u origin HEAD
gh pr create --base main --title "feat: environmental professional search v0.2.0" --body-file work/env-v020-pr.md
gh pr checks --watch
```

- [ ] **Step 5: Merge after review and CI**

```powershell
gh pr merge --squash --delete-branch
git -C G:\Claude_Code\SCIE_SSCI_CSSCI目录\cnki-top-journal-search-skill checkout main
git -C G:\Claude_Code\SCIE_SSCI_CSSCI目录\cnki-top-journal-search-skill pull --ff-only
```

- [ ] **Step 6: Create the independent environment tag**

Only after live verification and main CI pass:

```powershell
git tag -a top-journal-search-lists-env-v0.2.0 -m "Top Journal Search Lists Environment v0.2.0"
git push origin top-journal-search-lists-env-v0.2.0
```

- [ ] **Step 7: Publish canonical environment artifacts**

Download only `release-environment-ubuntu-py3.11`, then:

```powershell
gh release create top-journal-search-lists-env-v0.2.0 .\release\top-journal-search-lists-env_Skill.zip .\release\cnki-search-env.mcpb .\release\checksums.sha256 --title "Top Journal Search Lists Environment v0.2.0" --notes-file work\env-v020-release-notes.md
```

- [ ] **Step 8: Re-download and verify**

```powershell
gh release download top-journal-search-lists-env-v0.2.0 --dir work\env-v020-download
Get-FileHash work\env-v020-download\* -Algorithm SHA256
```

Compare all hashes and inspect embedded version `0.2.0`.

- [ ] **Step 9: Install the published environment version alongside generic v0.4.1**

Extract the downloaded environment Skill ZIP and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists-env\installers\install.ps1 -Codex -PythonExe C:\Python314\python.exe
codex mcp get cnki-search
codex mcp get cnki-search-env
```

Confirm generic v0.4.1 still exposes two generic tools and environment v0.2.0 exposes two environment tools. Ask the user to restart ChatGPT Desktop after both installed-runtime handshakes pass.
