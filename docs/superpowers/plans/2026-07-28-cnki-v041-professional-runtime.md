# CNKI 通用版 v0.4.1 专业检索运行时实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 v0.4.0 专业检索仅能通过测试工厂运行的问题，使默认 MCP 生产入口能够以非持久化 WebVPN 会话执行中文顶级期刊和 CSSCI 检索，并发布 v0.4.1。

**Architecture:** 保留公开主题检索不变，在专业检索侧引入分组感知的 `ExpressionBatch` 执行参数和独立 `ProfessionalSearchRuntime`。运行时按需建立可见、非持久化 Playwright 会话，串行执行批次并负责异步关闭；MCP 入口使用默认生产工厂，测试仍可注入伪工厂。

**Tech Stack:** Python 3.11+、asyncio、Playwright async API、FastMCP、Pydantic、pytest、ruff、mypy、PowerShell、POSIX Shell、GitHub Actions。

## Global Constraints

- 基准提交为 `7c858951e407da55980e69dced7c8c3edc1fe859`，目标版本统一为 `0.4.1`。
- 公开工具保持 `cnki_search(query, limit=20)`；专业工具保持 `cnki_professional_search(topic, group, limit=50, year_from=None, year_to=None)`。
- 专业分组只允许 `chinese_top_journals` 和 `cssci`。
- 正常专业检索请求之间至少间隔 30 秒；同一时刻只允许一个浏览器检索任务。
- 浏览器必须可见、禁止下载并使用非持久化上下文；不得调用 `launch_persistent_context()`。
- 不导出 `storage_state`，不保存 Cookie、HTML、完整 URL 或登录状态，不接入用户日常浏览器配置。
- 安全验证只允许用户手动完成；不得自动破解、自动刷新、切换代理或修改浏览器指纹。
- CI 不访问 CNKI；正式发布产物仅由 Ubuntu Python 3.11 构建。
- Skill 布局 `scripts/cnki_search/` 与 MCPB 布局 `mcpb/src/cnki_search/` 必须具有相同行为。
- 真实 WebVPN 端到端验证未通过前，不创建 `v0.4.1` 标签和 Release。

---

## File Structure

### 新建文件

- `top-journal-search-lists/scripts/cnki_search/professional_runtime.py`：生产运行时、页面批次执行器、默认环境变量工厂和资源关闭。
- `top-journal-search-lists/mcpb/src/cnki_search/professional_runtime.py`：MCPB 布局的同等实现。
- `top-journal-search-lists/tests/test_cnki_professional_runtime.py`：默认工厂、页面执行顺序、异常映射、取消和关闭测试。
- `top-journal-search-lists/tests/_webvpn_e2e.py`：只供人工运行的脱敏端到端验证入口，不进入 CI 自动联网。

### 修改文件

- `top-journal-search-lists/scripts/cnki_search/professional.py`
- `top-journal-search-lists/mcpb/src/cnki_search/professional.py`
- `top-journal-search-lists/scripts/cnki_search/professional_service.py`
- `top-journal-search-lists/mcpb/src/cnki_search/professional_service.py`
- `top-journal-search-lists/scripts/cnki_search/webvpn.py`
- `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`
- `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- `top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py`
- `top-journal-search-lists/tests/test_cnki_professional.py`
- `top-journal-search-lists/tests/test_cnki_professional_service.py`
- `top-journal-search-lists/tests/test_cnki_professional_mcp.py`
- `top-journal-search-lists/tests/test_cnki_webvpn.py`
- `top-journal-search-lists/tests/test_cnki_webvpn_page.py`
- `top-journal-search-lists/tests/test_cnki_package_contract.py`
- `top-journal-search-lists/tests/test_cnki_mcp.py`
- `top-journal-search-lists/tests/test_mcpb_manifest.py`
- `top-journal-search-lists/tests/test_installers.py`
- `top-journal-search-lists/scripts/build_release.py`
- `top-journal-search-lists/scripts/cnki_search/__init__.py`
- `top-journal-search-lists/mcpb/src/cnki_search/__init__.py`
- `top-journal-search-lists/mcpb/manifest.json`
- `top-journal-search-lists/mcpb/pyproject.toml`
- `top-journal-search-lists/mcpb/uv.lock`
- `top-journal-search-lists/README.md`
- `top-journal-search-lists/SKILL.md`
- `top-journal-search-lists/references/cnki-search-reference.md`

## Task 1: 建立分组感知的专业检索执行计划

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/professional.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/professional.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/professional_service.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/professional_service.py`
- Test: `top-journal-search-lists/tests/test_cnki_professional.py`
- Test: `top-journal-search-lists/tests/test_cnki_professional_service.py`

**Interfaces:**
- Produces: `build_topic_expression(topic: str, *, year_from: int | None, year_to: int | None) -> str`
- Produces: `ExpressionBatch(index: int, total: int, journals: tuple[str, ...], expression: str, page_size: int = 50, source_category: str | None = None)`
- Produces: `ExpressionExecutor = Callable[[ExpressionBatch], Awaitable[tuple[str, str, str]]]`
- Consumes: `journals_by_group(group, catalog)` and `SearchStatus`

- [ ] **Step 1: Write failing planner tests**

Add tests that fix the two group policies:

```python
def test_chinese_top_plan_uses_exact_journals_without_facet() -> None:
    plans = service_module.preview_plans("数字经济", service_module.CHINESE_TOP_GROUP)
    assert len(plans) == 1
    assert "LY='管理世界'" in plans[0].expression
    assert plans[0].source_category is None
    assert plans[0].page_size == 50


def test_cssci_plan_uses_one_topic_expression_and_result_facet() -> None:
    plans = service_module.preview_plans("数字化转型", service_module.CSSCI_GROUP)
    assert len(plans) == 1
    assert plans[0].expression == "SU %= '数字化转型'"
    assert "LY=" not in plans[0].expression
    assert plans[0].source_category == "CSSCI"
    assert plans[0].page_size == 50
```

- [ ] **Step 2: Run the planner tests and verify RED**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_professional_service.py -q
```

Expected: FAIL because `preview_plans`, `source_category` and `page_size` do not exist and CSSCI still enumerates 661 journals.

- [ ] **Step 3: Add the execution-plan fields and topic-only builder**

Implement the exact public shape:

```python
def build_topic_expression(
    topic: str,
    *,
    year_from: int | None = None,
    year_to: int | None = None,
) -> str:
    clauses = [f"{TOPIC_FIELD} {RELEVANCE_OPERATOR} {quote_value(topic)}"]
    if year_from is not None and year_to is not None:
        clauses.append(year_clause(year_from, year_to))
    elif (year_from is None) != (year_to is None):
        raise ValueError("年份区间必须同时提供起止年份")
    return " AND ".join(clauses)


@dataclass(frozen=True, slots=True)
class ExpressionBatch:
    index: int
    total: int
    journals: tuple[str, ...]
    expression: str
    page_size: int = MAX_RESULTS_PER_PAGE
    source_category: str | None = None
```

Import `MAX_RESULTS_PER_PAGE` from `.models`.

- [ ] **Step 4: Build plans by group and pass the whole plan to the executor**

Add:

```python
def build_group_plans(
    topic: str,
    group: str,
    *,
    catalog: Path = DEFAULT_CATALOG,
    max_chars: int = DEFAULT_MAX_EXPRESSION_CHARS,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[ExpressionBatch]:
    if group == CHINESE_TOP_GROUP:
        return build_batches(
            topic,
            journals_by_group(group, catalog),
            year_from=year_from,
            year_to=year_to,
            max_chars=max_chars,
        )
    if group == CSSCI_GROUP:
        return [ExpressionBatch(
            index=1,
            total=1,
            journals=(),
            expression=build_topic_expression(
                topic, year_from=year_from, year_to=year_to
            ),
            source_category="CSSCI",
        )]
    raise ValueError(f"CNKI 专业检索只覆盖中文层级 {SUPPORTED_GROUPS}，收到 {group!r}")


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

Change `ExpressionExecutor` to accept `ExpressionBatch`, and call `await self.executor(batch)`.
Report `journal_count=13` for `chinese_top_journals`. Report `journal_count=None` and `source_category="CSSCI"` for the facet-based CSSCI scope; do not label the old 661-title directory count as the size of a broader facet.

- [ ] **Step 5: Update service tests to record full plans**

Replace string-only fake executors with:

```python
def _executor(pages, seen=None):
    async def execute(plan: ExpressionBatch) -> tuple[str, str, str]:
        if seen is not None:
            seen.append(plan)
        title, journal = pages.pop(0)
        return SearchStatus.SUCCESS.value, RESULT_TEMPLATE.format(
            title=title, journal=journal
        ), "https://example.invalid/"
    return execute
```

Assert CSSCI is one facet plan, not multiple LY batches. Retain exact-journal batching tests by calling `build_batches()` directly with a reduced character budget.

- [ ] **Step 6: Run the focused tests and verify GREEN**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_professional_service.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add top-journal-search-lists/scripts/cnki_search/professional.py top-journal-search-lists/mcpb/src/cnki_search/professional.py top-journal-search-lists/scripts/cnki_search/professional_service.py top-journal-search-lists/mcpb/src/cnki_search/professional_service.py top-journal-search-lists/tests/test_cnki_professional.py top-journal-search-lists/tests/test_cnki_professional_service.py
git commit -m "fix: make professional search plans group aware"
```

## Task 2: 改为非持久化 WebVPN 浏览器会话

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`
- Test: `top-journal-search-lists/tests/test_cnki_webvpn.py`
- Test: `top-journal-search-lists/tests/test_cnki_webvpn_page.py`
- Test: `top-journal-search-lists/tests/test_cnki_package_contract.py`

**Interfaces:**
- Produces: `WebVpnConfig(home_url: str, login_timeout_seconds: float = 600.0, poll_interval_seconds: float = 3.0)`
- Produces: `_EphemeralContextFactory.launch() -> tuple[Any, Any]`, returning browser and context
- Produces: `WebVpnSession.close() -> Awaitable[None]`
- Consumes: `ExpressionBatch.page_size` and `ExpressionBatch.source_category`

- [ ] **Step 1: Write failing non-persistence and cleanup tests**

Add a fake Playwright recorder and assert:

```python
def test_session_uses_ephemeral_context_and_closes_every_resource() -> None:
    async def scenario() -> None:
        session = WebVpnSession(
            WebVpnConfig("https://webvpn.example.edu.cn/https/abc/"),
            context_factory=factory,
        )
        async with session:
            assert factory.launch_calls == 1
        assert context.closed
        assert browser.closed
        assert playwright.stopped

    asyncio.run(scenario())


def test_webvpn_source_forbids_persistent_context(skill_root: Path) -> None:
    for root in ("scripts/cnki_search", "mcpb/src/cnki_search"):
        source = (skill_root / root / "webvpn.py").read_text(encoding="utf-8")
        assert "launch_persistent_context" not in source
        assert "storage_state=" not in source
```

- [ ] **Step 2: Run lifecycle tests and verify RED**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_package_contract.py -q
```

Expected: FAIL because `WebVpnConfig` requires `profile_dir`, the launcher is persistent, and browser closure is not tracked.

- [ ] **Step 3: Replace the persistent factory**

Use:

```python
class _EphemeralContextFactory:
    def __init__(self, playwright: Any) -> None:
        self.playwright = playwright

    async def launch(self) -> tuple[Any, Any]:
        browser = await await_maybe(
            self.playwright.chromium.launch(headless=False)
        )
        context = await await_maybe(browser.new_context(
            locale="zh-CN",
            accept_downloads=False,
        ))
        return browser, context
```

Remove `profile_dir` from `WebVpnConfig`. Store `browser` separately in `WebVpnSession`.

- [ ] **Step 4: Make close idempotent and cancellation-safe**

Implement:

```python
async def close(self) -> None:
    for resource, method in (
        (self.page, "close"),
        (self.context, "close"),
        (self.browser, "close"),
        (self._playwright, "stop"),
    ):
        if resource is not None:
            with contextlib.suppress(Exception):
                await await_maybe(getattr(resource, method)())
    self.page = self.context = self.browser = self._playwright = None

async def __aexit__(self, *_exc: object) -> None:
    await asyncio.shield(self.close())
```

Do not close the home page twice: either omit the page close when context owns it, or keep idempotent fake and real tests proving double close is harmless.

- [ ] **Step 5: Add a page-level plan executor**

Add:

```python
async def execute_plan(self, plan: ExpressionBatch) -> tuple[str, str, str]:
    await self.fill_expression(plan.expression)
    await self.submit()
    status = await self.wait_for_outcome()
    if status is SearchStatus.SUCCESS:
        if plan.source_category is not None:
            await self.apply_source_category(plan.source_category)
        await self.set_page_size(plan.page_size)
        status = await self.wait_for_outcome()
    html = await await_maybe(self.page.content()) if status is SearchStatus.SUCCESS else ""
    return status.value, html, str(getattr(self.page, "url", ""))
```

The external service must later remove the URL. It is only an internal diagnostic return value.
`wait_for_outcome(timeout_seconds=30)` must poll through the temporary `page_contract_changed` state while the result table is rendering, and return `page_contract_changed` only after the timeout. Add a fake page that exposes the result table on a later poll so this race cannot regress.

- [ ] **Step 6: Test operation order and post-filter rendering**

Use a fake page recorder and assert:

```python
assert events == [
    "fill", "submit", "classify",
    "facet:CSSCI", "page_size:50", "classify", "content",
]
```

Also test a Chinese-top plan produces no facet event.

- [ ] **Step 7: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_webvpn_page.py top-journal-search-lists/tests/test_cnki_package_contract.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```powershell
git add top-journal-search-lists/scripts/cnki_search/webvpn.py top-journal-search-lists/mcpb/src/cnki_search/webvpn.py top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_webvpn_page.py top-journal-search-lists/tests/test_cnki_package_contract.py
git commit -m "fix: use ephemeral WebVPN browser sessions"
```

## Task 3: 建立默认生产运行时并接入 MCP

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/professional_runtime.py`
- Create: `top-journal-search-lists/mcpb/src/cnki_search/professional_runtime.py`
- Create: `top-journal-search-lists/tests/test_cnki_professional_runtime.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/tests/test_cnki_professional_mcp.py`
- Modify: `top-journal-search-lists/tests/test_cnki_async.py`

**Interfaces:**
- Produces: `ProfessionalSearchRuntime.search_group(topic: str, group: str, *, limit: int, year_from: int | None, year_to: int | None) -> Awaitable[dict[str, Any]]`
- Produces: `ProfessionalSearchRuntime.aclose() -> Awaitable[None]`
- Produces: `build_professional_runtime_from_env() -> Awaitable[ProfessionalSearchRuntime]`
- Consumes: `CNKI_WEBVPN_HOME`, `WebVpnSession`, `ProfessionalSearchPage`, `CnkiProfessionalSearchService`

- [ ] **Step 1: Write a failing default-factory regression test**

```python
def test_enabled_default_server_builds_production_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = FakeRuntime()
    created = 0

    async def build():
        nonlocal created
        created += 1
        return runtime

    monkeypatch.setenv("CNKI_WEBVPN_HOME", "https://webvpn.example.edu.cn/https/abc/")
    monkeypatch.setattr(mcp_server, "build_professional_runtime_from_env", build)
    server = CnkiMcpServer()
    result = asyncio.run(server.cnki_professional_search("数字经济"))

    assert result["status"] == "success"
    assert created == 1
```

This test must construct `CnkiMcpServer()` without passing `professional_factory`.

- [ ] **Step 2: Run the regression test and verify RED**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_professional_mcp.py::test_enabled_default_server_builds_production_runtime -q
```

Expected: FAIL with the current disabled-factory configuration error.

- [ ] **Step 3: Implement `ProfessionalSearchRuntime`**

Use this public shape:

```python
class ProfessionalSearchRuntime:
    def __init__(self, session: WebVpnSession, service: CnkiProfessionalSearchService) -> None:
        self.session = session
        self.service = service
        self._lock = asyncio.Lock()
        self._closed = False

    async def search_group(self, topic: str, group: str, *, limit: int,
                           year_from: int | None, year_to: int | None) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("WebVPN 专业检索运行时已关闭")
        async with self._lock:
            self.session.ensure_open()
            return await self.service.search_group(
                topic, group, limit=limit, year_from=year_from, year_to=year_to
            )

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            await self.session.close()
```

- [ ] **Step 4: Implement the real batch executor**

For every batch:

1. Start from the still-open CNKI home page.
2. Create `ProfessionalSearchPage(session.page)`.
3. Call `open_from_home(session.context)`.
4. Call `switch_to_professional()`.
5. Call `execute_plan(plan)`.
6. Close only the result tab in `finally`; keep the home page for the next batch.

Return `(status, html, "")` to the service so full WebVPN URLs never leave the runtime boundary.

If `execute_plan()` returns `challenge_detected`, retain that result tab as `active_challenge_page`. `wait_for_manual_challenge()` polls for at most 600 seconds and returns `True` only after the visible challenge disappears. It must not click, drag, reload or alter the page. Close the challenge tab before the scheduler retries the expression after the required backoff.

- [ ] **Step 5: Implement the environment factory**

```python
async def build_professional_runtime_from_env() -> ProfessionalSearchRuntime:
    home_url = (os.environ.get("CNKI_WEBVPN_HOME") or "").strip()
    if not home_url:
        raise ValueError("请设置 CNKI_WEBVPN_HOME")
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

`default_state_dir()` may keep throttle and sanitized checkpoint files under `~/.cnki-search/`; it must not create a browser profile.

- [ ] **Step 6: Wire the MCP server to the default factory**

Keep an injected factory distinguishable from the default:

```python
self._professional_factory = professional_factory

async def _ensure_professional(self) -> Any:
    if self._professional is None:
        factory = self._professional_factory or build_professional_runtime_from_env
        self._professional = await factory()
    return self._professional
```

Keep the explicit `webvpn_enabled()` guard so an unset environment variable never opens a browser.
Remove `WEBVPN_PROFILE_ENV`, `DEFAULT_WEBVPN_PROFILE` and the now-unused `Path` import from `mcp_server.py`.

Map runtime exceptions:

- `BrowserUnavailableError`, invalid HTTPS URL: `configuration_error`
- `WebVpnLoginTimeout`, `WebVpnWindowClosed`: `login_required`
- `WebVpnNavigationError`, `ExpressionTruncated`: `page_contract_changed`
- `asyncio.CancelledError`: re-raise

Constrain both optional years in the FastMCP schema to `1900` through `date.today().year + 1`. The expression builder must continue rejecting a missing interval endpoint and `year_from > year_to`.

- [ ] **Step 7: Add asynchronous server close and FastMCP lifespan**

Implement:

```python
async def aclose(self) -> None:
    self.shutdown()
    pending = [task for task in self._tasks if not task.done()]
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
    if self._professional is not None:
        await self._professional.aclose()
        self._professional = None
```

When constructing the real FastMCP instance, pass an async lifespan so `aclose()` runs on the same event loop that created the Playwright runtime:

```python
@asynccontextmanager
async def lifespan(_app: Any):
    try:
        yield {}
    finally:
        await self.aclose()

mcp = FastMCP("CNKI Public Search", lifespan=lifespan)
```

When a fake `fastmcp_class` is injected for schema tests, construct it with the existing name-only signature. Retain `shutdown()` as the non-blocking cancellation signal and as the fallback if `mcp.run()` fails before entering lifespan. Do not call `asyncio.run()` to close resources created on FastMCP’s event loop.

- [ ] **Step 8: Test cancellation and close**

Assert:

- runtime constructed once and reused;
- cancellation propagates;
- `aclose()` closes session;
- queued call never enters `service.search_group`;
- `main()` has a tested close path without depending on a live browser.

- [ ] **Step 9: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_professional_runtime.py top-journal-search-lists/tests/test_cnki_professional_mcp.py top-journal-search-lists/tests/test_cnki_async.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit**

```powershell
git add top-journal-search-lists/scripts/cnki_search/professional_runtime.py top-journal-search-lists/mcpb/src/cnki_search/professional_runtime.py top-journal-search-lists/scripts/cnki_search/mcp_server.py top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py top-journal-search-lists/tests/test_cnki_professional_runtime.py top-journal-search-lists/tests/test_cnki_professional_mcp.py top-journal-search-lists/tests/test_cnki_async.py
git commit -m "fix: wire the production professional runtime"
```

## Task 4: 修复断点、提前停止和重复题录选择

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/professional_service.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/professional_service.py`
- Test: `top-journal-search-lists/tests/test_cnki_webvpn.py`
- Test: `top-journal-search-lists/tests/test_cnki_professional_service.py`

**Interfaces:**
- Produces: `run_batches(batches, execute, *, on_challenge=None, checkpoint=None, throttle=None, max_challenge_retries=3, should_stop=None) -> Awaitable[dict[str, Any]]`
- Produces: schedule field `limit_reached: bool`
- Produces: checkpoint token as SHA256, never raw expression text

- [ ] **Step 1: Write failing scheduler and deduplication tests**

```python
def test_limit_stops_before_submitting_remaining_batches() -> None:
    # Three plans, first page already supplies limit records.
    assert result["limit_reached"] is True
    assert result["batches_completed"] == 1
    assert executor_calls == [1]


def test_duplicate_keeps_more_complete_record() -> None:
    # First record lacks authors; second duplicate has authors and citation count.
    assert result["records"][0]["authors"] == ["张三"]


def test_checkpoint_contains_no_expression_url_html_or_cookie(tmp_path: Path) -> None:
    text = checkpoint_path.read_text(encoding="utf-8")
    for forbidden in ("SU %=", "https://", "<table", "cookie"):
        assert forbidden.casefold() not in text.casefold()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_professional_service.py -q
```

Expected: FAIL because all batches run, the first duplicate always wins, and the checkpoint token contains raw expressions.

- [ ] **Step 3: Hash checkpoint identity and serialize only safe data**

Use:

```python
token = hashlib.sha256(
    "\n".join(batch.expression for batch in batches).encode("utf-8")
).hexdigest()
```

Before writing a completed batch, reduce it to status, batch index, counts and sanitized record dictionaries. Exclude `result_url`, HTML, full expression, paths and browser fields. Convert loaded dictionaries back to `PaperRecord` before merging.

- [ ] **Step 4: Add a stop predicate**

After appending a successful result:

```python
if should_stop is not None and should_stop(results):
    return _summary(
        results, batches, token, checkpoint,
        human_intervention_required,
        limit_reached=True,
    )
```

Add `limit_reached=False` to all other summaries.

For `network_error`, retry the current batch at most once. The retry must pass through `Throttle.wait()` again. Other non-challenge failure statuses are returned without retry.

Treat `no_results` as a completed empty batch so later exact-journal batches may still run. Treat `no_data_retry_later`, `page_contract_changed`, `forbidden`, `rate_limited`, exhausted `network_error` and unresolved `challenge_detected` as terminal. Add `terminal_status` to the schedule. If earlier batches produced records, the merged status is `partial`; if none produced records, preserve the terminal status instead of converting it to `no_results`.

- [ ] **Step 5: Count unique formal records against `limit`**

The service stop predicate must normalize:

```python
key = (
    " ".join(record.title.split()).casefold(),
    " ".join(record.journal_raw.split()).casefold(),
    record.publication_year,
)
```

Stop when unique complete records reach `limit`.

- [ ] **Step 6: Replace duplicates only when completeness improves**

Score title, journal, valid year, author count, publication date, citation count and download count. If two records share the key, retain the record with the larger score; preserve the earlier record when scores tie.

- [ ] **Step 7: Remove diagnostic URLs from the external outcome**

Do not include `result_url` in merged output or checkpoint. Keep `expressions` because they are an explicit, reviewable description of the submitted scope.

- [ ] **Step 8: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_professional_service.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

```powershell
git add top-journal-search-lists/scripts/cnki_search/webvpn.py top-journal-search-lists/mcpb/src/cnki_search/webvpn.py top-journal-search-lists/scripts/cnki_search/professional_service.py top-journal-search-lists/mcpb/src/cnki_search/professional_service.py top-journal-search-lists/tests/test_cnki_webvpn.py top-journal-search-lists/tests/test_cnki_professional_service.py
git commit -m "fix: sanitize professional checkpoints and stop at limit"
```

## Task 5: 更新版本、文档和发布清单

**Files:**
- Create: `top-journal-search-lists/tests/_webvpn_e2e.py`
- Modify: `top-journal-search-lists/scripts/build_release.py`
- Modify: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Modify: `top-journal-search-lists/tests/test_cnki_mcp.py`
- Modify: `top-journal-search-lists/tests/test_mcpb_manifest.py`
- Modify: `top-journal-search-lists/tests/test_installers.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/__init__.py`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/__init__.py`
- Modify: `top-journal-search-lists/mcpb/manifest.json`
- Modify: `top-journal-search-lists/mcpb/pyproject.toml`
- Modify: `top-journal-search-lists/mcpb/uv.lock`
- Modify: `top-journal-search-lists/README.md`
- Modify: `top-journal-search-lists/SKILL.md`
- Modify: `top-journal-search-lists/references/cnki-search-reference.md`

**Interfaces:**
- Produces: version `0.4.1` in Python, MCP serverInfo, manifest, pyproject and lock file
- Produces: release packages containing `professional_runtime.py`
- Produces: manual command `python tests/_webvpn_e2e.py --topic 数字化转型 --group chinese_top_journals --limit 5`

- [ ] **Step 1: Change version assertions to 0.4.1 and verify RED**

Update test expectations first:

```python
assert mcp._mcp_server.version == __version__ == "0.4.1"
assert manifest["version"] == "0.4.1"
assert 'version = "0.4.1"' in pyproject_text
```

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_mcp.py top-journal-search-lists/tests/test_mcpb_manifest.py -q
```

Expected: FAIL on current `0.4.0`.

- [ ] **Step 2: Update all version sources**

Change both `__init__.py`, manifest and pyproject to `0.4.1`, then run:

```powershell
uv lock --project top-journal-search-lists/mcpb
```

Confirm the root package entry in `uv.lock` is `0.4.1`.

- [ ] **Step 3: Add the new runtime and tests to release allowlists**

Add `professional_runtime.py` to `CNKI_MODULES`, and add:

```text
tests/test_cnki_professional_runtime.py
```

to `TEST_ALLOWLIST`. Keep `_webvpn_e2e.py` repository-only so CI and release self-tests never access CNKI.

- [ ] **Step 4: Update package boundary tests**

Add `professional_runtime.py` to `WEBVPN_MODULES`. Require both layouts to import it and expose the same MCP schema. Continue forbidding login, download and detection-evasion code from public modules.

- [ ] **Step 5: Update documentation**

Document:

- `CNKI_WEBVPN_HOME` is the only required WebVPN variable;
- `CNKI_WEBVPN_PROFILE` is no longer required;
- sessions are non-persistent and require login after service restart;
- generic top uses 13 exact journals;
- CSSCI uses the result-page source category;
- `no_data_retry_later` is not an empty-result conclusion;
- public mode remains ai4scholar’s Chinese supplement and does not log in or download;
- WebVPN mode requires human attendance and is not suitable for scheduled tasks.

- [ ] **Step 6: Add the sanitized E2E helper**

The helper accepts `--topic`, `--group`, `--limit`, `--year-from`, `--year-to`; reads the WebVPN home only from the environment; calls `build_professional_runtime_from_env()`; prints only:

```json
{
  "status": "success",
  "group": "chinese_top_journals",
  "record_count": 5,
  "batches_completed": 1,
  "batches_total": 1,
  "sample": [
    {"title": "数字化转型与企业创新", "journal_raw": "管理世界", "publication_year": 2025, "priority_level": 6}
  ]
}
```

Before printing, recursively reject keys containing `url`, `cookie`, `html`, `storage_state`, `profile` or absolute paths.

- [ ] **Step 7: Run package and documentation tests**

Run:

```powershell
python -m pytest top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists/tests/test_cnki_mcp.py top-journal-search-lists/tests/test_mcpb_manifest.py top-journal-search-lists/tests/test_installers.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```powershell
git add top-journal-search-lists
git commit -m "chore: prepare CNKI search v0.4.1"
```

## Task 6: 完成自动化验证和独立代码复核

**Files:**
- Modify only if a failing check identifies a defect in files already listed above.

**Interfaces:**
- Consumes: all v0.4.1 implementation tasks
- Produces: review record suitable for PR description

- [ ] **Step 1: Run formatting and static analysis**

```powershell
ruff check .
mypy top-journal-search-lists/scripts/
```

Expected: both commands exit 0.

- [ ] **Step 2: Run the complete generic test suite**

```powershell
python -m pytest top-journal-search-lists -q -p no:cacheprovider
python top-journal-search-lists/scripts/catalog_lookup.py validate
python top-journal-search-lists/tests/_mcp_handshake.py
python top-journal-search-lists/tests/_mcpb_handshake.py
python top-journal-search-lists/tests/_mcpb_raw_handshake.py
```

Expected: zero failures; both handshakes list `cnki_search` and `cnki_professional_search`.

- [ ] **Step 3: Build twice and compare deterministic artifacts**

Build to two different directories:

```powershell
python top-journal-search-lists/scripts/build_release.py --output work/release-a
python top-journal-search-lists/scripts/build_release.py --output work/release-b
Get-FileHash work/release-a/* -Algorithm SHA256
Get-FileHash work/release-b/* -Algorithm SHA256
```

Expected: matching hashes for the Skill ZIP, MCPB and checksum file.

- [ ] **Step 4: Inspect package contents**

Assert both archives contain `professional_runtime.py` and contain none of:

```text
__pycache__/
.pytest_cache/
.git/
storage_state
webvpn-profile
Cookie
Local State
downloads/
```

- [ ] **Step 5: Run the Windows installer in an isolated home**

Use a temporary `USERPROFILE`, `APPDATA` and `CODEX_HOME`; run:

```powershell
& .\top-journal-search-lists\installers\install.ps1 -Codex -PythonExe C:\Python314\python.exe
```

Verify Chromium starts, the MCP imports, both tools appear, and an existing unrelated MCP table remains unchanged.

- [ ] **Step 6: Review the production path manually**

Trace this exact path without test injection:

```text
main()
→ CnkiMcpServer()
→ cnki_professional_search()
→ build_professional_runtime_from_env()
→ WebVpnSession
→ ProfessionalBatchExecutor
→ ProfessionalSearchPage.execute_plan()
→ CnkiProfessionalSearchService
```

Confirm there is no `professional_factory is None` dead end and every resource has one owner and one close path.

- [ ] **Step 7: Commit any review fixes**

If review found changes, run their focused failing test first, then:

```powershell
git add top-journal-search-lists
git commit -m "fix: address v0.4.1 verification findings"
```

If no changes were needed, do not create an empty commit.

## Task 7: 人工 WebVPN 验证、合并、发布和本地安装

**Files:**
- No source changes unless the live test reveals a reproducible defect.
- Release attachments: `top-journal-search-lists_Skill.zip`, `cnki-search.mcpb`, `checksums.sha256`

**Interfaces:**
- Consumes: reviewed v0.4.1 branch and a user-supplied `CNKI_WEBVPN_HOME`
- Produces: tag `v0.4.1`, GitHub Release and verified local ChatGPT Desktop installation

- [ ] **Step 1: Run Chinese-top E2E with a visible browser**

```powershell
$env:CNKI_WEBVPN_HOME='<用户提供的 WebVPN 知网首页>'
C:\Python314\python.exe top-journal-search-lists\tests\_webvpn_e2e.py --topic '数字化转型' --group chinese_top_journals --limit 5
```

The user completes login. Verify the summary contains title, journal, year and level 6, and no sensitive fields.

- [ ] **Step 2: Run CSSCI facet E2E**

```powershell
C:\Python314\python.exe top-journal-search-lists\tests\_webvpn_e2e.py --topic '数字化转型' --group cssci --limit 5
```

Verify one topic expression, CSSCI source category, page size 50 and valid bibliographic fields.

- [ ] **Step 3: Stop on a failed live gate**

If either scenario cannot complete, record the returned structured status and stop. Do not tag, publish or claim production support. Fix only after reproducing the defect with a failing automated test.

- [ ] **Step 4: Push branch and create a ready PR**

```powershell
git push -u origin HEAD
gh pr create --base main --title "fix: wire CNKI professional search v0.4.1" --body-file work/v041-pr.md
```

Include automated test evidence and the sanitized E2E outcome, never the WebVPN URL.

- [ ] **Step 5: Wait for all PR checks and merge**

```powershell
gh pr checks --watch
gh pr merge --squash --delete-branch
git -C G:\Claude_Code\SCIE_SSCI_CSSCI目录\cnki-top-journal-search-skill checkout main
git -C G:\Claude_Code\SCIE_SSCI_CSSCI目录\cnki-top-journal-search-skill pull --ff-only
```

Confirm local and remote `main` point to the merge commit.

- [ ] **Step 6: Create the tag only after the live gate and main CI pass**

```powershell
git tag -a v0.4.1 -m "CNKI Top Journal Search Skill v0.4.1"
git push origin v0.4.1
```

- [ ] **Step 7: Publish only canonical Ubuntu Python 3.11 artifacts**

Download `release-canonical-ubuntu-py3.11`, then:

```powershell
gh release create v0.4.1 .\release\top-journal-search-lists_Skill.zip .\release\cnki-search.mcpb .\release\checksums.sha256 --title "CNKI Top Journal Search Skill v0.4.1" --notes-file work\v041-release-notes.md
```

- [ ] **Step 8: Re-download and verify the release**

```powershell
gh release download v0.4.1 --dir work\v041-download
Get-FileHash work\v041-download\* -Algorithm SHA256
```

Compare against `checksums.sha256`; inspect both archives and confirm embedded version `0.4.1`.

- [ ] **Step 9: Install the published v0.4.1 into ChatGPT Desktop**

Extract the downloaded Skill ZIP and run its installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -Codex -PythonExe C:\Python314\python.exe
```

Verify:

```powershell
codex mcp get cnki-search
```

Then perform an MCP handshake from the installed runtime and confirm both tools are present. Prompt the user to restart ChatGPT Desktop only after these checks pass.
