# CNKI 新版入口统一实施计划

> 状态：已废止，由 `../specs/2026-07-22-cnki-public-theme-search-design.md` 取代。本计划不得继续执行。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 CNKI 检索实现、测试、文档和安装包统一到新版 `kns8s/AdvSearch` 页面，并删除所有其他入口及其回退能力。

**Architecture:** `session.py` 只依据当前会话主机解析直连或河海大学 WebVPN 的新版入口，并以可见页面合同判断状态。`search.py` 只维护新版高级检索和专业检索控件，`mcp_server.py` 在每次检索前进入新版页面并传播停止状态。结果、详情和下载继续通过可见浏览器串行执行，主源码通过测试后同步到 MCPB 副本。

**Tech Stack:** Python 3.14、pytest 9、Playwright、FastMCP、PowerShell、Git

## Global Constraints

- 直连入口固定为 `https://kns.cnki.net/kns8s/AdvSearch`。
- 河海大学 WebVPN 入口固定为 `https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch`。
- 公开接口不提供入口版本参数，不保留其他入口、适配器或回退分支。
- 只操作可见页面和官方可见控件，不由程序构造或直接调用 CNKI 内部 HTTP 接口。
- 使用临时可见浏览器上下文，不持久化或导出 Cookie、localStorage、Local State 和浏览器 profile。
- 检索默认 1 页、最多 3 页，页间 4 至 7 秒；详情最多 10 篇，篇间 3 至 6 秒；下载最多 5 篇，每次点击前等待 8 至 15 秒。
- 验证码、403、429、权限不足、会话失效和页面合同变化立即停止，不自动重试，不切换代理或检索入口。
- 下载必须具有编号选择、访问权限确认和输出目录，每个文件下载后校验格式、大小和 SHA-256。
- 主源码、MCPB 副本、Skill 文档和安装包必须保持一致。

---

## 文件结构

- `top-journal-search-lists/scripts/cnki_search/session.py`：新版入口解析、临时会话和可见页面状态分类。
- `top-journal-search-lists/scripts/cnki_search/search.py`：新版高级检索与专业检索页面合同和表单操作。
- `top-journal-search-lists/scripts/cnki_search/mcp_server.py`：工具入口、检索调度、停止状态和下载授权参数。
- `top-journal-search-lists/scripts/cnki_search/downloads.py`：每次点击前等待、官方按钮下载和文件校验。
- `top-journal-search-lists/tests/fixtures/new_advanced.html`：脱敏的新版高级检索结构。
- `top-journal-search-lists/tests/fixtures/new_professional.html`：脱敏的新版专业检索结构。
- `top-journal-search-lists/tests/test_cnki_session.py`：新版入口解析和状态分类测试。
- `top-journal-search-lists/tests/test_cnki_search.py`：新版页面合同和两类表单测试。
- `top-journal-search-lists/tests/test_cnki_mcp.py`：MCP 新版导航与停止状态测试。
- `top-journal-search-lists/tests/test_cnki_downloads.py`：下载授权、等待和格式校验测试。
- `top-journal-search-lists/tests/test_cnki_package_contract.py`：源码、文档、包内入口一致性测试。
- `top-journal-search-lists/mcpb/src/cnki_search/`：主源码的发布副本，只在主源码测试通过后同步。
- `top-journal-search-lists/SKILL.md`、`README.md`、`references/cnki-search-reference.md`：新版入口使用说明。

### Task 1: 建立新版入口唯一性测试

**Files:**
- Modify: `top-journal-search-lists/tests/test_cnki_session.py`
- Modify: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Test: `top-journal-search-lists/tests/test_cnki_session.py`
- Test: `top-journal-search-lists/tests/test_cnki_package_contract.py`

**Interfaces:**
- Produces: `DIRECT_CNKI_SEARCH_URL: str`、`HHU_CNKI_SEARCH_URL: str`、`resolve_search_url(current_url: str) -> str | None`
- Consumes: `SessionStatus`

- [ ] **Step 1: 用新版接口替换现有入口测试**

```python
from cnki_search.session import (
    DIRECT_CNKI_SEARCH_URL,
    HHU_CNKI_SEARCH_URL,
    resolve_search_url,
)


def test_resolve_search_url_uses_new_entry_only() -> None:
    assert resolve_search_url("https://kns.cnki.net/") == DIRECT_CNKI_SEARCH_URL
    assert resolve_search_url("https://webvpn.hhu.edu.cn/") == HHU_CNKI_SEARCH_URL
    assert DIRECT_CNKI_SEARCH_URL == "https://kns.cnki.net/kns8s/AdvSearch"
    assert HHU_CNKI_SEARCH_URL.endswith("/kns8s/AdvSearch")
    assert resolve_search_url("https://example.com/") is None
```

- [ ] **Step 2: 增加全项目入口唯一性失败测试**

```python
def test_cnki_package_contains_only_new_search_entry(skill_root: Path) -> None:
    included = [
        skill_root / "scripts" / "cnki_search",
        skill_root / "mcpb" / "src" / "cnki_search",
        skill_root / "SKILL.md",
        skill_root / "README.md",
        skill_root / "references" / "cnki-search-reference.md",
    ]
    text = "\n".join(
        path.read_text(encoding="utf-8")
        if path.is_file()
        else "\n".join(p.read_text(encoding="utf-8") for p in path.rglob("*.py"))
        for path in included
    ).casefold()
    assert "kns8s/advsearch" in text
    assert "kns/advsearch" not in text
    assert "resolve_old_search_url" not in text
    assert "open_old_search" not in text
    assert "assert_old_search_page" not in text
```

- [ ] **Step 3: 运行测试并确认因旧实现而失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_session.py top-journal-search-lists/tests/test_cnki_package_contract.py -q
```

Expected: FAIL，原因包括新版常量和 `resolve_search_url` 尚不存在，且源码仍包含非新版入口。

- [ ] **Step 4: 提交测试**

```powershell
git add top-journal-search-lists/tests/test_cnki_session.py top-journal-search-lists/tests/test_cnki_package_contract.py
git commit -m "test: require CNKI new search entry"
```

### Task 2: 实现新版入口解析与会话导航

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/session.py`
- Test: `top-journal-search-lists/tests/test_cnki_session.py`

**Interfaces:**
- Consumes: 当前 `page.url`
- Produces: `resolve_search_url(current_url: str) -> str | None`、`CnkiSession.open_search() -> SessionStatus`、`is_new_search_page_contract(...) -> bool`

- [ ] **Step 1: 在测试中定义新版导航行为**

```python
def test_session_opens_new_search_for_webvpn() -> None:
    page = RecordingPage("https://webvpn.hhu.edu.cn/")
    session = CnkiSession()
    session.page = page
    assert session.open_search() is SessionStatus.READY
    assert page.visited == [HHU_CNKI_SEARCH_URL]


def test_session_rejects_unrelated_host() -> None:
    page = RecordingPage("https://example.com/")
    session = CnkiSession()
    session.page = page
    assert session.open_search() is SessionStatus.SESSION_EXPIRED
    assert page.visited == []
```

- [ ] **Step 2: 运行新增测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_session.py -q
```

Expected: FAIL，`CnkiSession.open_search` 尚不存在。

- [ ] **Step 3: 删除其他入口实现并加入新版最小实现**

```python
DIRECT_CNKI_SEARCH_URL = "https://kns.cnki.net/kns8s/AdvSearch"
HHU_CNKI_SEARCH_URL = (
    "https://webvpn.hhu.edu.cn/https/"
    "77726476706e69737468656265737421fbf952d2243e635930068cb8/"
    "kns8s/AdvSearch"
)


def resolve_search_url(current_url: str) -> str | None:
    hostname = (urlparse(current_url).hostname or "").casefold()
    if hostname == "webvpn.hhu.edu.cn":
        return HHU_CNKI_SEARCH_URL
    if hostname == "cnki.net" or hostname.endswith(".cnki.net"):
        return DIRECT_CNKI_SEARCH_URL
    return None


def open_search(self) -> SessionStatus:
    if self._closed:
        return SessionStatus.CLOSED
    if self.page is None:
        return SessionStatus.LOGIN_REQUIRED
    target = resolve_search_url(self.page.url)
    if target is None:
        return SessionStatus.SESSION_EXPIRED
    self.page.goto(target, wait_until="domcontentloaded")
    status = self.status()
    if status is not SessionStatus.READY:
        return status
    if "/kns8s/advsearch" not in self.page.url.casefold():
        return SessionStatus.SESSION_EXPIRED
    return SessionStatus.READY
```

删除 `DIRECT_CNKI_OLD_SEARCH_URL`、`HHU_CNKI_OLD_SEARCH_URL`、`resolve_old_search_url`、`open_old_search`、`is_old_search_page_contract` 及其特殊验证码恢复分支。验证码判断只依据可见验证控件、验证 URL 和明确验证提示。

- [ ] **Step 4: 运行会话测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_session.py -q
```

Expected: PASS。

- [ ] **Step 5: 提交入口实现**

```powershell
git add top-journal-search-lists/scripts/cnki_search/session.py top-journal-search-lists/tests/test_cnki_session.py
git commit -m "feat: use CNKI new search entry"
```

### Task 3: 建立新版页面合同和检索表单

**Files:**
- Create: `top-journal-search-lists/tests/fixtures/new_advanced.html`
- Create: `top-journal-search-lists/tests/fixtures/new_professional.html`
- Modify: `top-journal-search-lists/tests/test_cnki_search.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/search.py`

**Interfaces:**
- Consumes: `SearchRequest`、`resolve_field(name: str)`、新版脱敏 DOM
- Produces: `PlaywrightPageDriver.assert_new_search_page() -> None`、`AdvancedSearchRunner.run(...)`、`ProfessionalSearchRunner.run(...)`

- [ ] **Step 1: 从实机页面形成脱敏夹具**

保存新版高级检索和专业检索所需的标签、行容器、字段菜单、输入框和检索按钮。不得保存输入值、账号、Cookie、动态令牌和个人信息。夹具根节点加入 `data-fixture="sanitized"`，便于包合同测试识别。

- [ ] **Step 2: 写入新版页面合同失败测试**

```python
def test_playwright_driver_accepts_new_search_contract() -> None:
    page = RecordingPlaywrightPage("https://kns.cnki.net/kns8s/AdvSearch")
    PlaywrightPageDriver(page).assert_new_search_page()


def test_playwright_driver_rejects_non_new_url() -> None:
    page = RecordingPlaywrightPage("https://kns.cnki.net/")
    with pytest.raises(RuntimeError, match="新版检索页面"):
        PlaywrightPageDriver(page).assert_new_search_page()
```

- [ ] **Step 3: 写入篇名与专业检索行为测试**

```python
def test_exact_title_search_uses_title_field() -> None:
    page = RecordingDriver()
    request = SearchRequest(
        mode=SearchMode.ADVANCED,
        query="数字化转型、企业创新与新质生产力",
        pages=1,
        fields=[{"field": "篇名", "value": "数字化转型、企业创新与新质生产力", "match": "精确"}],
        filters={},
    )
    AdvancedSearchRunner().run(page, request)
    assert ("select_label", "检索字段1", "题名") in page.actions
    assert ("set_option", "匹配方式1", "精确") in page.actions


def test_professional_expression_is_not_rewritten() -> None:
    page = RecordingDriver()
    expression = "TI='数字化转型' AND KY='企业创新'"
    ProfessionalSearchRunner().run(page, expression)
    assert ("fill_label", "专业检索表达式", expression) in page.actions
```

- [ ] **Step 4: 运行检索测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_search.py -q
```

Expected: FAIL，页面驱动仍暴露其他页面合同或新版夹具选择器尚未实现。

- [ ] **Step 5: 实现新版页面合同**

将 `assert_old_search_page` 改为 `assert_new_search_page`，URL 必须包含 `/kns8s/advsearch`。高级检索和专业检索选择器只能取自两份脱敏夹具。默认高级检索字段继续为主题，但显式篇名字段必须由 `resolve_field("篇名")` 解析为标签 `题名`。对未知筛选项保持 `ValueError("暂不支持的高级检索筛选项：...")`。

- [ ] **Step 6: 运行检索测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_search.py top-journal-search-lists/tests/test_cnki_fields.py top-journal-search-lists/tests/test_cnki_syntax.py -q
```

Expected: PASS。

- [ ] **Step 7: 提交新版页面合同**

```powershell
git add top-journal-search-lists/scripts/cnki_search/search.py top-journal-search-lists/tests/test_cnki_search.py top-journal-search-lists/tests/fixtures/new_advanced.html top-journal-search-lists/tests/fixtures/new_professional.html
git commit -m "feat: implement CNKI new search forms"
```

### Task 4: 将 MCP 调度统一到新版入口

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/tests/test_cnki_mcp.py`

**Interfaces:**
- Consumes: `CnkiSession.open_search()`、`PlaywrightPageDriver.assert_new_search_page()`
- Produces: `CnkiMcpServer.cnki_search(...) -> dict[str, Any]`

- [ ] **Step 1: 写入新版导航和停止状态测试**

```python
def test_search_opens_new_page_before_runner(monkeypatch) -> None:
    session = ReadySession()
    server = CnkiMcpServer(session=session)
    response = server.cnki_search("数字化转型", fields=[{"field": "篇名", "value": "数字化转型"}])
    assert session.open_search_calls == 1
    assert response["status"] == "ready"


@pytest.mark.parametrize(
    "status",
    [SessionStatus.CAPTCHA, SessionStatus.RATE_LIMITED, SessionStatus.PERMISSION_DENIED, SessionStatus.SESSION_EXPIRED],
)
def test_search_stops_when_new_page_is_not_ready(status) -> None:
    session = ReadySession(open_search_status=status)
    response = CnkiMcpServer(session=session).cnki_search("数字化转型")
    assert response["ok"] is False
    assert response["status"] == status.value
```

- [ ] **Step 2: 运行 MCP 测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_mcp.py -q
```

Expected: FAIL，服务器仍调用 `open_old_search` 和 `assert_old_search_page`。

- [ ] **Step 3: 改为新版调度**

```python
search_page_status = self.session.open_search()
if search_page_status is not SessionStatus.READY:
    return ToolResponse.failure(
        search_page_status,
        "知网新版检索页面尚未就绪",
        next_action="请在可见浏览器中手工完成登录或验证。",
    ).to_dict()
driver = PlaywrightPageDriver(self.session.page)
driver.assert_new_search_page()
```

删除所有其他入口名称和提示。`cnki_search` 的公开参数保持 `query`、`mode`、`pages`、`fields`、`filters`，不得增加入口版本参数。

- [ ] **Step 4: 运行 MCP 与结果测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_mcp.py top-journal-search-lists/tests/test_cnki_results.py top-journal-search-lists/tests/test_cnki_details.py -q
```

Expected: PASS。

- [ ] **Step 5: 提交 MCP 调度**

```powershell
git add top-journal-search-lists/scripts/cnki_search/mcp_server.py top-journal-search-lists/tests/test_cnki_mcp.py
git commit -m "feat: route CNKI tools through new entry"
```

### Task 5: 强制下载授权与每次点击前等待

**Files:**
- Modify: `top-journal-search-lists/scripts/cnki_search/downloads.py`
- Modify: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Modify: `top-journal-search-lists/tests/test_cnki_downloads.py`
- Modify: `top-journal-search-lists/tests/test_cnki_mcp.py`

**Interfaces:**
- Consumes: `selected_indices: list[int]`、`output_dir: str`、`access_confirmed: bool`
- Produces: `DownloadRunner.download_selected(...) -> list[Path]`，每次驱动点击前调用 `sleeper(random_uniform(8.0, 15.0))`

- [ ] **Step 1: 写入单篇和连续下载等待测试**

```python
def test_each_download_waits_before_click(tmp_path: Path) -> None:
    waits: list[float] = []
    driver = RecordingDownloadDriver(payload=b"%PDF-1.7\n")
    runner = DownloadRunner(driver, sleeper=waits.append, random_uniform=lambda low, high: 9.0)
    runner.download_selected(records(2), selected_indices=[1, 2], output_dir=tmp_path)
    assert waits == [9.0, 9.0]
    assert driver.events == ["download:1", "download:2"]
```

- [ ] **Step 2: 写入访问权限确认测试**

```python
def test_mcp_download_requires_access_confirmation(tmp_path: Path) -> None:
    server = ready_server_with_records()
    response = server.cnki_download([1], str(tmp_path), access_confirmed=False)
    assert response["ok"] is False
    assert "访问权限" in response["message"]
```

- [ ] **Step 3: 运行下载测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_downloads.py top-journal-search-lists/tests/test_cnki_mcp.py -q
```

Expected: FAIL，首个或唯一文件当前不会等待，MCP 也没有权限确认参数。

- [ ] **Step 4: 实现每次点击前等待和权限门槛**

```python
for index in indices:
    self.sleeper(self.random_uniform(8.0, 15.0))
    record = records[index - 1]
    temporary = output_dir / f"{safe_filename(record.title)}.download"
    path = self.driver.download_selected(index, temporary)
```

```python
def cnki_download(
    self,
    selected_indices: list[int],
    output_dir: str,
    access_confirmed: bool = False,
) -> dict[str, Any]:
    if not access_confirmed:
        return ToolResponse.failure(
            SessionStatus.PERMISSION_DENIED,
            "下载前必须由用户确认具有相应访问权限",
        ).to_dict()
```

下载成功数据增加文件大小和 SHA-256；HTML 或未知格式仍立即删除并停止。

- [ ] **Step 5: 运行下载测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_downloads.py top-journal-search-lists/tests/test_cnki_mcp.py -q
```

Expected: PASS。

- [ ] **Step 6: 提交下载门槛**

```powershell
git add top-journal-search-lists/scripts/cnki_search/downloads.py top-journal-search-lists/scripts/cnki_search/mcp_server.py top-journal-search-lists/tests/test_cnki_downloads.py top-journal-search-lists/tests/test_cnki_mcp.py
git commit -m "fix: enforce CNKI download authorization"
```

### Task 6: 更新文档并同步发布副本

**Files:**
- Modify: `top-journal-search-lists/SKILL.md`
- Modify: `top-journal-search-lists/README.md`
- Modify: `top-journal-search-lists/references/cnki-search-reference.md`
- Modify: `top-journal-search-lists/mcpb/src/cnki_search/*.py`
- Test: `top-journal-search-lists/tests/test_cnki_package_contract.py`

**Interfaces:**
- Consumes: 已通过测试的主源码
- Produces: 与主源码逐字节一致的 MCPB Python 副本和只说明新版入口的文档

- [ ] **Step 1: 补充源码副本一致性测试**

```python
def test_mcpb_cnki_source_matches_skill_source(skill_root: Path) -> None:
    source = skill_root / "scripts" / "cnki_search"
    bundled = skill_root / "mcpb" / "src" / "cnki_search"
    for path in source.glob("*.py"):
        assert (bundled / path.name).read_bytes() == path.read_bytes()
```

- [ ] **Step 2: 运行包合同测试并确认失败**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_package_contract.py -q
```

Expected: FAIL，MCPB 仍包含修改前源码。

- [ ] **Step 3: 同步源码并核对文档**

Run:

```powershell
Copy-Item -LiteralPath top-journal-search-lists\scripts\cnki_search\*.py -Destination top-journal-search-lists\mcpb\src\cnki_search -Force
rg -n "kns/advsearch|resolve_old_search_url|open_old_search|assert_old_search_page" top-journal-search-lists
```

Expected: `rg` 无输出。文档只出现两个固定新版 URL，并说明没有其他入口或回退模式。

- [ ] **Step 4: 运行包合同测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests/test_cnki_package_contract.py top-journal-search-lists/tests/test_mcpb_manifest.py -q
```

Expected: PASS。

- [ ] **Step 5: 提交文档和发布副本**

```powershell
git add top-journal-search-lists/SKILL.md top-journal-search-lists/README.md top-journal-search-lists/references/cnki-search-reference.md top-journal-search-lists/mcpb/src/cnki_search top-journal-search-lists/tests/test_cnki_package_contract.py
git commit -m "docs: document CNKI new entry only"
```

### Task 7: 全量测试、独立解压和敏感文件检查

**Files:**
- Modify: `outputs/install.ps1`
- Modify: `outputs/install.sh`
- Produce: `outputs/top-journal-search-lists_Skill.zip`
- Produce: `outputs/cnki-search.mcpb`
- Produce: `outputs/checksums.sha256`

**Interfaces:**
- Consumes: 已测试源码、MCPB 配置和安装脚本
- Produces: 可独立安装的 ZIP、MCPB 和 SHA-256 清单

- [ ] **Step 1: 运行全部自动化测试**

Run:

```powershell
C:\Python314\python.exe -m pytest top-journal-search-lists/tests -q
```

Expected: 全部 PASS，无跳过的 CNKI 入口合同测试。

- [ ] **Step 2: 构建交付包**

使用现有构建流程生成一个顶层目录的 Skill ZIP 和 MCPB。安装脚本只写入用户明确选择的 Codex、Claude Code 或 Claude Desktop 配置目录，不删除未知目录。

- [ ] **Step 3: 检查包内禁止内容**

Run:

```powershell
$extract = Join-Path $env:TEMP 'cnki-new-entry-package-check'
Expand-Archive -LiteralPath outputs\top-journal-search-lists_Skill.zip -DestinationPath $extract -Force
rg -n "kns/advsearch|Cookie|Local State|user-data-dir|C:\\Users\\" $extract
```

Expected: 无非新版入口、会话文件或固定用户路径命中。文档中安全边界对 Cookie 和 Local State 的文字说明允许存在，但包内不得存在同名会话文件。

- [ ] **Step 4: 从独立解压目录运行测试**

Run:

```powershell
C:\Python314\python.exe -m pytest "$extract\top-journal-search-lists\tests" -q
```

Expected: 全部 PASS。

- [ ] **Step 5: 生成校验和并提交构建脚本变更**

Run:

```powershell
Get-FileHash outputs\top-journal-search-lists_Skill.zip,outputs\cnki-search.mcpb -Algorithm SHA256
git add outputs/install.ps1 outputs/install.sh top-journal-search-lists
git commit -m "build: package CNKI new entry release"
```

二进制交付包不纳入普通 Git 历史，后续只上传到私有 GitHub Release 或保留在本地 `outputs` 目录。

### Task 8: 实机验证与跨客户端安装

**Files:**
- Produce: `outputs/live-cnki-validation/new-entry-status.json`
- Produce: `outputs/live-cnki-validation/new-entry-advanced.json`
- Produce: `outputs/live-cnki-validation/new-entry-professional.json`
- Produce: `outputs/live-cnki-validation/new-entry-detail.json`
- Produce: `outputs/live-cnki-validation/new-entry-download.json`

**Interfaces:**
- Consumes: 通过独立解压测试的交付包
- Produces: 脱敏实机证据和三个客户端的安装验证结果

- [ ] **Step 1: 安装到测试位置并检查工具清单**

分别验证 Codex、Claude Code 和 Claude Desktop 能加载 `cnki_status`、`cnki_login`、`cnki_search`、`cnki_fetch_details`、`cnki_export`、`cnki_download`、`cnki_close_session`。

- [ ] **Step 2: 用户手工登录 WebVPN**

调用 `cnki_login`，等待用户在可见浏览器中完成登录。不得读取其他浏览器配置，不得让用户向工具传递账号、密码或验证码。

- [ ] **Step 3: 验证新版高级检索**

以篇名精确检索《数字化转型、企业创新与新质生产力》。确认当前检索 URL 以 WebVPN 代理的 `/kns8s/AdvSearch` 结尾，结果中出现完全一致题名。

- [ ] **Step 4: 验证新版专业检索和详情**

提交经用户确认的专业表达式，解析首屏结果，选择目标记录并进入 `/kcms2/article/abstract` 详情页。遇到验证、限流、权限或结构变化立即停止。

- [ ] **Step 5: 经用户再次授权后验证单篇下载**

向用户展示编号结果，确认访问权限和保存目录。等待 8 至 15 秒后点击官方可见下载按钮，校验文件格式、大小和 SHA-256。没有明确授权时跳过此步骤，不影响检索与详情验收。

- [ ] **Step 6: 关闭会话并检查残留**

调用 `cnki_close_session`，确认运行目录、安装包和客户端配置中没有 Cookie、Local State、浏览器 profile 或固定用户路径。

- [ ] **Step 7: 记录验证结论**

实机证据只保存脱敏状态、规范化查询、题录、文件元数据和错误分类，不保存会话令牌、账号或动态 URL 参数。
