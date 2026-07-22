# CNKI Search Cross-Client Implementation Plan

> 状态：已废止，由 `../specs/2026-07-22-cnki-public-theme-search-design.md` 取代。本计划不得继续执行。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `top-journal-search-lists` 中实现经河海大学 WebVPN 使用可见浏览器的低频 CNKI 检索、导出和授权下载，并交付 Claude 与 Codex 跨客户端安装包。

**Architecture:** 以现有 Skill 为外层入口，在 `scripts/cnki_search` 内建立与客户端无关的 Python 核心。Claude Code、Claude Desktop、Codex CLI 和 Codex Desktop 通过同一 stdio MCP 调用；浏览器和认证状态仅驻留进程内存。

**Tech Stack:** Python 3.11+、Playwright、MCP Python SDK、pytest、标准库 csv/json/pathlib、MCPB uv runtime。

## Global Constraints

- 可见浏览器，禁止 headless、stealth、代理轮换、Tor、Sci-Hub 和 LibGen。
- 用户手工输入账号、密码和验证码，工具不得读取、记录或持久化凭据与 cookies。
- 搜索最多 3 页，详情最多 10 条，下载最多 5 条，全部串行。
- 验证码、403、429、权限不足和会话失效立即停止，不自动重试。
- `cnki-search-skill-main` 无许可证，禁止复制其源码、提示词和文档。
- 每项生产代码先运行对应失败测试，再写最小实现。
- 当前工作区的 `.git` 为空目录，不执行提交；每个任务以测试输出和文件哈希作为检查点。

---

### Task 1: 建立可测试的合并 Skill 工作副本

**Files:**
- Create: `top-journal-search-lists/`，内容来自已核验的原 Skill ZIP
- Create: `top-journal-search-lists/tests/test_cnki_package_contract.py`
- Modify: `top-journal-search-lists/SKILL.md`
- Modify: `top-journal-search-lists/README.md`

**Interfaces:**
- Consumes: 原目录结构和 `scripts/catalog_lookup.py`
- Produces: 可直接运行测试的合并 Skill 根目录

- [ ] **Step 1: 写入失败的包契约测试**

```python
def test_cnki_runtime_contract(skill_root):
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")
```

- [ ] **Step 2: 运行并确认因 CNKI 文件不存在而失败**

Run: `python -m pytest top-journal-search-lists/tests/test_cnki_package_contract.py -q`

Expected: `FAIL`，缺少 `scripts/cnki_search/__init__.py`。

- [ ] **Step 3: 复制原 Skill 并创建最小包入口**

```python
"""CNKI browser-search runtime for top-journal-search-lists."""

__all__ = ["__version__"]
__version__ = "0.1.0"
```

- [ ] **Step 4: 在 SKILL 与 README 增加最小 CNKI 入口并运行测试**

Expected: 包契约测试通过，原 17 项目录测试继续通过。

### Task 2: 定义状态、请求和结果模型

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/models.py`
- Create: `top-journal-search-lists/tests/test_cnki_models.py`

**Interfaces:**
- Produces: `SessionStatus`、`SearchMode`、`SearchRequest`、`PaperRecord`、`ToolResponse`

- [ ] **Step 1: 写入状态和值对象失败测试**

```python
def test_tool_response_serializes_stable_shape():
    response = ToolResponse.success(SessionStatus.READY, {"count": 1})
    assert response.to_dict() == {
        "ok": True,
        "status": "ready",
        "message": "",
        "data": {"count": 1},
        "warnings": [],
        "next_action": None,
    }
```

- [ ] **Step 2: 运行并确认导入失败**

Run: `python -m pytest top-journal-search-lists/tests/test_cnki_models.py -q`

Expected: `ModuleNotFoundError` 或缺少 `ToolResponse`。

- [ ] **Step 3: 使用 dataclass 和 StrEnum 写最小实现**

必须包含设计中的八个会话状态，`SearchRequest` 必须拒绝页数大于 3，`PaperRecord` 必须保留来源模式和检索时间。

- [ ] **Step 4: 运行模型测试并确认通过**

Run: `python -m pytest top-journal-search-lists/tests/test_cnki_models.py -q`

### Task 3: 字段映射与专业检索语法检查

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/fields.py`
- Create: `top-journal-search-lists/scripts/cnki_search/syntax.py`
- Create: `top-journal-search-lists/tests/test_cnki_fields.py`
- Create: `top-journal-search-lists/tests/test_cnki_syntax.py`

**Interfaces:**
- Produces: `resolve_field(name: str) -> FieldSpec`
- Produces: `validate_professional_expression(expression: str) -> list[str]`

- [ ] **Step 1: 写字段别名失败测试**

```python
def test_resolve_field_supports_cnki_codes_and_chinese_names():
    assert resolve_field("主题").code == "SU"
    assert resolve_field("TKA").label == "篇关摘"
    assert resolve_field("DOI").code == "DOI"
```

- [ ] **Step 2: 写专业表达式失败测试**

```python
def test_professional_expression_is_not_rewritten():
    text = "SU='数字化转型' AND (KY='创新' OR TI='研发')"
    assert validate_professional_expression(text) == []
    assert normalize_professional_expression(text) == text
```

- [ ] **Step 3: 确认测试因函数缺失而失败**

Run: `python -m pytest top-journal-search-lists/tests/test_cnki_fields.py top-journal-search-lists/tests/test_cnki_syntax.py -q`

- [ ] **Step 4: 写入字段表和只读语法扫描器**

语法扫描器只检查空表达式、括号、引号和字段代码；`normalize_professional_expression` 必须原样返回输入。

- [ ] **Step 5: 运行测试并确认通过**

### Task 4: 限流、调用配额和元数据缓存

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/rate_limit.py`
- Create: `top-journal-search-lists/scripts/cnki_search/cache.py`
- Create: `top-journal-search-lists/tests/test_cnki_rate_limit.py`
- Create: `top-journal-search-lists/tests/test_cnki_cache.py`

**Interfaces:**
- Produces: `RatePolicy`、`SerialRateLimiter.wait(kind)`、`MetadataCache`

- [ ] **Step 1: 写入确定性限流失败测试**

```python
def test_search_delay_uses_four_to_seven_seconds(fake_sleep, fixed_random):
    limiter = SerialRateLimiter(sleep=fake_sleep, uniform=fixed_random(5.5))
    limiter.wait("search_page")
    assert fake_sleep.calls == [5.5]
```

- [ ] **Step 2: 写入缓存拒绝敏感字段测试**

```python
def test_cache_rejects_sensitive_keys(tmp_path):
    cache = MetadataCache(tmp_path / "cache.json")
    with pytest.raises(ValueError, match="sensitive"):
        cache.put("q", {"cookie": "x"})
```

- [ ] **Step 3: 运行并确认失败，再写最小实现**

搜索、详情、下载区间分别固定为 4 至 7、3 至 6、8 至 15 秒；调用配额为 3、10、5。

- [ ] **Step 4: 运行两组测试并确认通过**

### Task 5: 浏览器适配与内存会话

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/browser.py`
- Create: `top-journal-search-lists/scripts/cnki_search/session.py`
- Create: `top-journal-search-lists/tests/fixtures/login.html`
- Create: `top-journal-search-lists/tests/fixtures/captcha.html`
- Create: `top-journal-search-lists/tests/fixtures/advanced.html`
- Create: `top-journal-search-lists/tests/test_cnki_session.py`

**Interfaces:**
- Produces: `BrowserFactory.launch_visible()`
- Produces: `CnkiSession.login()`、`status()`、`close()`

- [ ] **Step 1: 写入可见浏览器和非持久化失败测试**

```python
def test_browser_launch_is_visible_and_ephemeral(fake_playwright):
    BrowserFactory(fake_playwright).launch_visible()
    assert fake_playwright.launch_kwargs["headless"] is False
    assert "user_data_dir" not in fake_playwright.launch_kwargs
    assert "storage_state" not in fake_playwright.launch_kwargs
```

- [ ] **Step 2: 写入页面状态分类失败测试**

```python
@pytest.mark.parametrize(("fixture", "expected"), [
    ("login.html", SessionStatus.LOGIN_REQUIRED),
    ("captcha.html", SessionStatus.CAPTCHA),
    ("advanced.html", SessionStatus.READY),
])
def test_status_from_public_page_state(fixture, expected, fixture_page):
    assert classify_page(fixture_page(fixture)) is expected
```

- [ ] **Step 3: 运行并确认失败，再实现浏览器发现和状态机**

优先发现系统 Chrome、Edge、Chromium，找不到时使用 Playwright Chromium；禁止调用 `launch_persistent_context`。

- [ ] **Step 4: 运行会话测试并确认通过**

### Task 6: 高级检索、专业检索和结果解析

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/search.py`
- Create: `top-journal-search-lists/scripts/cnki_search/results.py`
- Create: `top-journal-search-lists/tests/fixtures/results.html`
- Create: `top-journal-search-lists/tests/test_cnki_search.py`
- Create: `top-journal-search-lists/tests/test_cnki_results.py`

**Interfaces:**
- Produces: `AdvancedSearchRunner.run(page, request)`
- Produces: `ProfessionalSearchRunner.run(page, expression)`
- Produces: `parse_result_page(html: str) -> list[PaperRecord]`

- [ ] **Step 1: 写入高级表单动作失败测试**

```python
def test_advanced_search_fills_fields_without_direct_http(fake_page, request):
    AdvancedSearchRunner().run(fake_page, request)
    assert fake_page.actions[0] == ("select", "主题")
    assert not any(action[0] == "request" for action in fake_page.actions)
```

- [ ] **Step 2: 写入专业表达式原样输入失败测试**

```python
def test_professional_search_fills_exact_expression(fake_page):
    expr = "SU='气候风险' AND KY='企业创新'"
    ProfessionalSearchRunner().run(fake_page, expr)
    assert fake_page.filled_text == expr
```

- [ ] **Step 3: 写入结果字段和翻页上限失败测试**

固定结果必须解析题名、作者、期刊、年份、摘要、关键词、DOI 和详情链接；请求 4 页必须在浏览器动作前失败。

- [ ] **Step 4: 运行失败测试，再写选择器驱动的最小实现**

- [ ] **Step 5: 运行检索与解析测试并确认通过**

### Task 7: 去重、期刊等级和五种导出

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/exporters.py`
- Create: `top-journal-search-lists/tests/test_cnki_exporters.py`
- Modify: `top-journal-search-lists/scripts/catalog_lookup.py`

**Interfaces:**
- Produces: `deduplicate(records)`、`attach_journal_level(records, catalog)`
- Produces: `export_json/csv/bibtex/ris/gbt7714`

- [ ] **Step 1: 写入 DOI 与题名回退去重失败测试**

```python
def test_deduplicate_prefers_doi_then_title_author_year(records):
    result = deduplicate(records)
    assert [item.title for item in result] == ["数字化转型与创新", "气候风险"]
```

- [ ] **Step 2: 写入目录等级和导出编码失败测试**

CSV 必须使用 UTF-8 BOM；未知期刊必须得到 `未收录`；五种导出必须保留题名、作者和来源。

- [ ] **Step 3: 运行失败测试，再实现纯函数导出器**

- [ ] **Step 4: 运行导出测试和原目录 17 项测试**

### Task 8: 授权下载和文件验证

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/downloads.py`
- Create: `top-journal-search-lists/tests/test_cnki_downloads.py`

**Interfaces:**
- Produces: `safe_filename()`、`validate_download()`、`DownloadRunner.download_selected()`

- [ ] **Step 1: 写入 PDF、CAJ 和 HTML 拒绝测试**

```python
def test_validate_download_rejects_html_error_page():
    with pytest.raises(InvalidDownload, match="HTML"):
        validate_download(b"<html>login required</html>", "paper.pdf", "text/html")
```

- [ ] **Step 2: 写入串行和最多五条测试**

六条选择必须在浏览器操作前失败；合法 PDF 以 `%PDF-` 开头；已存在文件不得覆盖。

- [ ] **Step 3: 运行失败测试，再实现最小下载器**

- [ ] **Step 4: 运行下载测试并确认通过**

### Task 9: MCP 与 CLI 入口

**Files:**
- Create: `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- Create: `top-journal-search-lists/scripts/cnki_search/cli.py`
- Create: `top-journal-search-lists/tests/test_cnki_mcp.py`
- Create: `top-journal-search-lists/tests/test_cnki_cli.py`

**Interfaces:**
- Produces: 七个 MCP 工具和 `python -m cnki_search.cli`

- [ ] **Step 1: 写入工具集合和初始化说明失败测试**

```python
def test_mcp_exposes_exact_tool_set(server):
    assert set(server.tool_names()) == {
        "cnki_status", "cnki_login", "cnki_search",
        "cnki_fetch_details", "cnki_export",
        "cnki_download", "cnki_close_session",
    }
```

- [ ] **Step 2: 写入统一返回结构和关闭清理失败测试**

每个工具必须返回 `ok/status/message/data/warnings/next_action`；关闭后状态为 `closed`，浏览器对象为空。

- [ ] **Step 3: 运行失败测试，再以 FastMCP 写 stdio 入口**

- [ ] **Step 4: 运行 MCP 和 CLI 测试并确认通过**

### Task 10: 完成 Skill 指令、README 和参考文档

**Files:**
- Modify: `top-journal-search-lists/SKILL.md`
- Modify: `top-journal-search-lists/README.md`
- Create: `top-journal-search-lists/references/cnki-search-reference.md`
- Modify: `top-journal-search-lists/agents/openai.yaml`
- Modify: `top-journal-search-lists/tests/test_cnki_package_contract.py`

**Interfaces:**
- Produces: Claude 与 Codex 都能发现和正确调用的 Skill 指令

- [ ] **Step 1: 扩充失败契约测试**

测试必须检查手工登录、低频串行、风控停止、禁止 Cookie 持久化、CNKI 与 ai4scholar 分工、用户确认后下载。

- [ ] **Step 2: 运行并确认现有文档未满足全部契约**

- [ ] **Step 3: 写入最小而完整的 Skill 与用户说明**

`SKILL.md` 控制在 500 行以内；详细字段和安装内容放入 reference 与 README。

- [ ] **Step 4: 使用 Skill Creator 的 `quick_validate.py` 校验**

Run: `python C:/Users/胡世亮/.codex/skills/.system/skill-creator/scripts/quick_validate.py top-journal-search-lists`

### Task 11: 跨平台安装器和 MCPB

**Files:**
- Create: `top-journal-search-lists/installers/install.ps1`
- Create: `top-journal-search-lists/installers/install.sh`
- Create: `top-journal-search-lists/mcpb/manifest.json`
- Create: `top-journal-search-lists/mcpb/pyproject.toml`
- Create: `top-journal-search-lists/tests/test_installers.py`
- Create: `top-journal-search-lists/tests/test_mcpb_manifest.py`

**Interfaces:**
- Produces: 增量安装、备份、检测、卸载和 MCPB uv runtime

- [ ] **Step 1: 写入配置不覆盖失败测试**

```python
def test_installer_preserves_unrelated_mcp_servers(tmp_path):
    before = {"mcpServers": {"zotero": {"command": "zotero-mcp"}}}
    after = merge_claude_config(before, cnki_server_config(tmp_path))
    assert after["mcpServers"]["zotero"] == before["mcpServers"]["zotero"]
```

- [ ] **Step 2: 写入 Windows、Linux、macOS 路径矩阵测试**

测试 Claude Skill、Codex Skill、Claude MCP 和 Codex MCP 的目标路径；所有生成文本使用 UTF-8。

- [ ] **Step 3: 写入 MCPB manifest 失败测试**

检查 `manifest_version`、`server.type=uv`、入口文件、工具说明和无敏感配置字段。

- [ ] **Step 4: 运行失败测试，再实现安装器与 manifest**

- [ ] **Step 5: 使用官方 MCPB 工具验证并打包**

Run: `mcpb validate top-journal-search-lists/mcpb/manifest.json`

Expected: manifest 有效；如本机缺少 `mcpb`，先记录版本并安装官方 CLI 后重试。

### Task 12: 集成验证、安装和最终打包

**Files:**
- Create: `outputs/top-journal-search-lists_Skill.zip`
- Create: `outputs/cnki-search.mcpb`
- Create: `outputs/install.ps1`
- Create: `outputs/install.sh`
- Create: `outputs/checksums.sha256`

**Interfaces:**
- Produces: 最终可安装交付物

- [ ] **Step 1: 运行全部测试**

Run: `python -m pytest top-journal-search-lists/tests -q`

Expected: 全部通过，无 ResourceWarning 和未处理异常。

- [ ] **Step 2: 在临时目录从 ZIP 重新安装并复测**

验证压缩包只有一个顶层 `top-journal-search-lists/`，同时包含 `SKILL.md` 与 `README.md`。

- [ ] **Step 3: 在本机安装 Skill 和 MCP**

修改配置前生成带时间戳备份；执行 MCP 握手和 `cnki_status`，不得自动打开登录页。

- [ ] **Step 4: 执行 Windows 真实浏览器冒烟**

由用户手工登录后依次验证高级检索一页、专业检索一页、一个详情、五种导出和一个用户授权下载。任何验证码或权限状态立即停止并记录。

- [ ] **Step 5: 备份并替换目标 ZIP**

先验证目标仍为原 SHA-256，再创建时间戳备份，最后把已验证 ZIP 写入 `G:\Claude_Code\SCIE_SSCI_CSSCI目录\top-journal-search-lists_Skill.zip`。

- [ ] **Step 6: 计算最终 SHA-256 并报告验证边界**

报告 Windows 实测结果；Linux 和 macOS 仅报告自动化兼容性测试，不表述为实机登录验证。

## Execution Record: 2026-07-21

- [x] 完成核心代码、文档、跨平台安装器与 MCPB。
- [x] 完成高级检索、专业检索、结果解析和真实详情页解析验证。
- [x] 完成五种专业检索结果导出。
- [x] 完成 74 项完整测试、独立解压复测、Skill 校验和 MCPB 清单校验。
- [x] 完成 Codex、Claude Skill 更新和已安装 MCP 七工具握手。
- [x] 完成 G 盘目标 ZIP 的备份、替换和 SHA-256 复核。
- [ ] 等待用户指定结果序号后执行一次授权下载，并验证 PDF 或 CAJ 文件头。
