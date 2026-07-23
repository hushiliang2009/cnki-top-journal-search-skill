# 阶段 0 实施报告：可信测试基线与 CI

实施提交：`9727eac`（`test: establish CNKI audit baseline (BUG-14 BUG-15 BUG-21 BUG-25 BUG-39)`）。

## 范围

本次仅处理 BUG-14、BUG-15、BUG-21、BUG-25 和 BUG-39 的阶段 0 基线工作。未访问 CNKI，自动化测试、MCP 握手和发布检查均为本地离线操作。

## 红灯与绿灯证据

先新增布局独立合约测试、冒烟脚本接口测试、夹具来源测试与 CI 合约测试，再执行：

```powershell
python -m pytest tests/test_cnki_package_contract.py::test_skill_and_mcpb_layouts_independently_meet_public_runtime_contract tests/test_task0_baseline.py -q -p no:cacheprovider --basetemp C:\Users\Public\cnki-audit-pytest
```

红灯结果为 4 failed，原因依次为：小于 6 秒的间隔未被拒绝、`_browser_launch_smoke.py` 仍调用已移除的会话 API、两份带来源说明的夹具不存在、CI 工作流不存在。

实施最小修复后，相关测试执行结果为 `24 passed in 0.20s`。

## 实施内容

- 删除主 Skill 与 MCPB 布局之间逐字节相同的断言，改为两个独立 Python 子进程加载各自布局，验证公开首页、`limit` 边界、最小间隔、无代理启动参数、非持久上下文与 `accept_downloads=False`。
- 两个布局的 `SerialSearchGate` 均拒绝小于 6 秒的间隔；浏览器启动不再注入代理相关参数。
- 更新 `_browser_launch_smoke.py`，使用 `PublicCnkiSession`，不再调用登录接口。
- 新增已说明来源的代表性脱敏 HTML 夹具和合成畸形 HTML 夹具。两者均明确不是实际抓取的 CNKI 页面。
- 发布白名单纳入新增测试和夹具。
- 新增 GitHub Actions：Ubuntu Python 3.11 至 3.14，Windows 和 macOS Python 3.11；各平台执行 pytest、目录校验、两个 MCP 握手、发布构建与 ZIP 产物检查。工作流不含 CNKI 域名访问步骤。

## 文件变更

- `.github/workflows/ci.yml`
- `top-journal-search-lists/scripts/cnki_search/browser.py`
- `top-journal-search-lists/scripts/cnki_search/rate_limit.py`
- `top-journal-search-lists/mcpb/src/cnki_search/browser.py`
- `top-journal-search-lists/mcpb/src/cnki_search/rate_limit.py`
- `top-journal-search-lists/scripts/build_release.py`
- `top-journal-search-lists/tests/_browser_launch_smoke.py`
- `top-journal-search-lists/tests/test_cnki_package_contract.py`
- `top-journal-search-lists/tests/test_cnki_session.py`
- `top-journal-search-lists/tests/test_mcpb_manifest.py`
- `top-journal-search-lists/tests/test_task0_baseline.py`
- `top-journal-search-lists/tests/fixtures/representative_public_results_sanitized.html`
- `top-journal-search-lists/tests/fixtures/synthetic_malformed_public_results.html`

## 验证结果

```text
python -m pytest tests -q -p no:cacheprovider --basetemp C:\Users\Public\cnki-audit-pytest\stage0-tests
113 passed in 4.22s

python scripts/catalog_lookup.py validate
valid: true; catalog_version: 2026-07-15

python tests/_mcp_handshake.py
{'tools': ['cnki_search']}

python tests/_mcpb_handshake.py
{'tools': ['cnki_search']}

python scripts/build_release.py --output C:\Users\Public\cnki-audit-pytest\stage0-release
产物检查：Skill 64 个成员，MCPB 19 个成员，checksums 186 字节。
```

## 疑虑与环境说明

普通沙箱会对工作树遗留的受限临时目录及 Windows 本地子进程管道返回 `PermissionError`。因此完整 pytest 和 MCP 握手在提升权限下、专用目录 `C:\Users\Public\cnki-audit-pytest\stage0-tests` 中复验。测试运行时使用 `pytest tests`，以避免 pytest 收集工作树根目录中不可读取的历史临时目录。代码与测试本身未出现功能性失败。`catalog_lookup.py` 中仅有正则表达式的原始字符串，其写法跨平台正确，本次未作修改。
