# Windows 11 + ChatGPT Desktop 实机验证交接说明

- 交接日期：2026-07-31
- 交出方：macOS + Claude Desktop / Claude Code
- 接手方：Windows 11 + ChatGPT Desktop
- 基准提交：`85afade`（`main`）

## 1. 文档用途

两个产品都**已经发布完毕**，代码工作已结束。本文档交接的**不是开发任务，而是一组只能在 Windows 11 上完成的验证任务**。

接手方需要做的是：在真实 Windows 11 机器上，用已发布的 Release 附件安装，跑通被平台门控的测试，并在 ChatGPT Desktop 里确认工具可见可用，然后把结果回报到仓库。

**不需要**改代码、不需要改版本号、不需要发新版本。若验证中发现缺陷，按第 8 节处理。

## 2. 基准状态

### 2.1 已发布内容

| 产品 | 版本 | 标签 | 指向提交 |
| --- | --- | --- | --- |
| 通用版 | v0.4.2 | `v0.4.2` | `06e656c` |
| 环境版 | v0.2.0 | `top-journal-search-lists-env-v0.2.0` | `85afade` |

仓库：`hushiliang2009/cnki-top-journal-search-skill`（**私有**，需 `gh auth login`，账号 `hushiliang2009`）。

Release 页面：

- 通用版 <https://github.com/hushiliang2009/cnki-top-journal-search-skill/releases/tag/v0.4.2>
- 环境版 <https://github.com/hushiliang2009/cnki-top-journal-search-skill/releases/tag/top-journal-search-lists-env-v0.2.0>

### 2.2 附件校验和（SHA-256）

下载后**必须先校验**再安装。这四个值取自 CI 产物，macOS 侧已重新下载复核过、逐字节一致。

```
d6d69a038700ffe51b3c5e49c9130fbbedb1cf170c5f44692f84a749b2105aa8  top-journal-search-lists_Skill.zip
92b6cc5597cabca874ac6057b2c8e855ce281191b67e29ce1bc5e6ed5263a7ab  cnki-search.mcpb
00aad9c246c61d253259b710b3627b31d96dfe3d6c968650027f2bc1b1f6c915  top-journal-search-lists-env_Skill.zip
173a01498e5481c1825305ce2d53cb68cdcbd55aab27e225e7f12f9c6fa080e4  cnki-search-env.mcpb
```

### 2.3 CI 状态

`main` 最近一次运行 **25/25 全绿**（Ubuntu 3.11–3.14、Windows、macOS、安装器矩阵）。CI 上的 Windows 作业跑的是 Python 与安装器矩阵，**不包含**第 4 节那 8 个 PowerShell 执行用例。

## 3. macOS 侧已完成、不需要重做的部分

以下均在隔离 HOME 下、用**已发布 Release 附件的真实字节**完成，2026-07-31：

1. 两个产品全新安装并共存：两套 Skill、两套运行时、四个配置条目，互不覆盖。
2. **四个工具同时可见**：两个 MCP 服务均握手成功并列出各自工具。
   - `cnki-search` v0.4.2 → `cnki_search`、`cnki_professional_search`
   - `cnki-search-env` v0.2.0 → `cnki_search_env`、`cnki_professional_search_env`
3. `--codex` 目标（即 ChatGPT Desktop / Codex 使用的 `config.toml`）写出合法 TOML，从该安装拉起的两个服务同样正常。
4. 未设 WebVPN 变量时，两个专业检索工具返回 `status=configuration_error`，指引文案在返回体 `detail` 字段，不崩溃、不挂起。
5. 配置合并不影响无关条目（实测 `ai4scholar` 完好保留）；备份轮转确为最近 3 份。
6. 真实 WebVPN 检索（macOS，人工登录）：`chinese_top_journals` 35 条、`cssci` 48 条、`chinese_environment_top`、`environment_cssci` 均 `success`。

**因此 Windows 侧只需覆盖平台差异，不必重复上述功能验证。**

## 4. 待办任务

### 4.1 任务 A：跑通 8 个 PowerShell 门控用例

这 8 个用例带 `@requires_windows_powershell`，条件是 `os.name == "nt"` 且能找到 `powershell`。在 macOS/Linux 上恒被跳过，**只有 Windows 11 能执行**。

通用版 `top-journal-search-lists/tests/test_installers.py`：

1. `test_powershell_51_parses_no_bom_utf8_installer_with_ascii_executable_text`
2. `test_powershell_rejects_python_310_before_creating_install_paths`
3. `test_powershell_runtime_failure_restores_skill_and_config`
4. `test_powershell_success_runs_self_checks_and_retains_exactly_three_backups`

环境版 `top-journal-search-lists-env/tests/test_installers.py`：

5. `test_powershell_51_parses_no_bom_utf8_installer_with_ascii_executable_text`
6. `test_powershell_rejects_python_310_before_creating_install_paths`
7. `test_powershell_success_runs_self_checks_and_retains_exactly_three_backups`
8. `test_environment_install_coexists_with_generic_skill_and_mcp`

**注意用例 8 的性质**：它断言的共存行为，macOS 侧已用隔离 HOME 手工完整验证过（第 3 节第 1、2 条）。Windows 上跑它补的是「在 Windows 路径与 PowerShell 下同样成立」。

**这 8 个用例都已有静态对应项**在其他平台上断言 `install.ps1` 的文本内容（如 `-copy-skill` 参数存在、`Assert-PythonVersion` 在 `try {` 之前调用、含 `Restore-Transaction` 与 `Rotate-Backups`）。所以 Windows 补的是**「脚本真能执行」的证据**，不是新的逻辑覆盖。

执行方式：

```powershell
git clone https://github.com/hushiliang2009/cnki-top-journal-search-skill.git
```

```powershell
python -m pytest top-journal-search-lists/tests/test_installers.py top-journal-search-lists-env/tests/test_installers.py -v -rs
```

验收：这 8 个用例由 `SKIPPED` 变为 `PASSED`，且其余用例不因平台产生新的失败。

### 4.2 任务 B：从 Release 附件安装到 ChatGPT Desktop 并验证四个工具

ChatGPT Desktop 读取 Codex 配置，对应安装器的 `-Codex` 目标。

Windows 路径（已由 `test_windows_client_paths` 固定）：

| 项 | 路径 |
| --- | --- |
| Codex 主目录 | `%CODEX_HOME%`，未设时为 `%USERPROFILE%\.codex` |
| Codex 配置 | `<CodexHome>\config.toml` |
| Codex Skill | `<CodexHome>\skills\top-journal-search-lists` |
| 运行时 | `<CodexHome>\runtimes\cnki-search`（环境版为 `cnki-search-env`） |

步骤：

1. 从两个 Release 下载 `*_Skill.zip`，按 2.2 校验 SHA-256，解压。
2. 分别执行两个安装器的 `-Codex` 目标：

```powershell
.\top-journal-search-lists\installers\install.ps1 -Codex
```

```powershell
.\top-journal-search-lists-env\installers\install.ps1 -Codex
```

参数形式为 PowerShell 开关：`-Codex` / `-ClaudeCode` / `-ClaudeDesktop`，可组合；另有 `-PythonExe <路径>`。**必须显式给出至少一个目标**，否则退出码 2。

3. 重启 ChatGPT Desktop。
4. 确认**两个 MCP 服务、四个工具同时可见**：`cnki_search`、`cnki_professional_search`、`cnki_search_env`、`cnki_professional_search_env`。
5. 调一次不需要 WebVPN 的公开检索（`cnki_search`），确认返回结构正常。公网知网大概率触发滑块验证码而返回 `challenge_detected`——**这属于预期结果，不是缺陷**（见第 7 节）。
6. 调一次 `cnki_professional_search` 且**不设** `CNKI_WEBVPN_HOME`，确认返回 `status=configuration_error` 且 `detail` 含配置指引。

验收：四个工具在 ChatGPT Desktop 中同时列出；第 5、6 步返回结构符合预期。

### 4.3 任务 C（可选，需人工值守）：字段升级路径实机验证

`professional_service.py` 的检索字段按 `TI → SU → KY → TKA` 逐级替换，有效记录数达到 `limit` 即停。macOS 实测中 **TI 一步就取满 50 条，从未走到后续字段**，该路径目前只有单元测试覆盖。

若要实机验证，需人工登录 WebVPN，并**故意选一个窄到 TI 取不满的主题**，观察返回值里的 `topic_field` 与 `topic_fields_tried`。

⚠ 该任务会成倍增加请求量：窄主题最坏为 `4 × 批次数` 次请求（`environment_cssci` 两批即 8 次、约 4 分钟）。**命中风控立即停止，不要换字段重试。**

此任务优先级低于 A 和 B，可不做。

## 5. 环境准备

| 项 | 要求 |
| --- | --- |
| Python | **≥ 3.11**。`Assert-PythonVersion` 会在创建任何安装路径**之前**拒绝 3.10 及以下 |
| gh CLI | 需 `gh auth login`（仓库私有） |
| PowerShell | Windows PowerShell 5.1 即可；安装器为无 BOM UTF-8、正文纯 ASCII，已针对 5.1 解析做过约束 |
| 磁盘 | 见下 |

**磁盘占用需特别注意**：环境版**钉死自己的私有 Chromium 缓存**（`<运行时>\playwright-browsers`，约 549MB），**无视外部 `PLAYWRIGHT_BROWSERS_PATH`**；通用版则沿用共享缓存。因此：

- 环境版**每装一个客户端目标就多下一份 Chromium**。装到 `-Codex` 和 `-ClaudeDesktop` 两个目标 ≈ 1.1GB。
- 请预留 **2GB 以上**空闲空间。

这一不对称已在 macOS 侧确认为**有意设计且有测试背书**（隔离要求），不是缺陷；是否统一另有独立任务跟进，**本次验证不要顺手改它**。

## 6. 不得放松的安全与合规边界

无论在哪个平台、哪个客户端，以下都不得改变：

- WebVPN 模式**必须人工值守，不可用于定时任务**。登录、保持浏览器窗口、中途安全验证三处都需要人。
- 非持久化浏览器上下文，**不保存** Cookie、票据或 profile；服务重启后需重新登录。
- **不伪造** User-Agent、**不轮换**代理、**不自动破解**验证码。遇滑块验证一律停止。
- 批次间隔 ≥ 30 秒。
- 遇 `challenge_detected` 立即停止，不得重试绕过。

## 7. 接手方必须预先知道的既有事实

这些是此前实测踩出来的，**不了解会把正常行为误判为缺陷**：

1. **公网知网自动检索基本不可用**：提交检索后跳转滑块验证码。这是硬墙，返回 `challenge_detected` 属**正确行为**。中文文献走 WebVPN 模式或 ai4scholar。
2. **WebVPN 票据不能跨进程复用**：`wengine_vpn_ticket*` 是 session cookie，`storage_state` 导出后服务端在新浏览器进程里直接拒绝（有头无头皆然）。故登录与检索必须同进程。
3. **`LY=` 并非严格精确匹配**：只枚举 6 本刊的表达式仍可能返回刊名含清单词条的其他期刊（实测出现过来源为 `Journal of Resources and Ecology` 的记录，因其中文名含「生态学报」）。**返回期刊不保证全部落在分组清单内**；不在目录中的记录会被标为空层级与 `manual_review_required=true`，但占用 `limit` 名额。归属以判级结果为准。
4. **返回 `no_data_retry_later` 表示知网临时拒绝，不等于空结果**，也不等于缺陷。
5. **专业检索工具始终出现在工具列表里**，不是按环境变量隐藏；未配置时在**调用**时返回 `configuration_error`。所以「工具可见但用不了」是设计如此。
6. **知网页面上「DOM 里有」不等于「能用」**：`count()`、`display`、`offsetParent` 都会骗人。安全验证组件常驻 DOM（未触发时停在 `top:-1000430px` 但 `display:block`）；表达式框在高级检索与专业检索两个标签下都存在，仅靠 CSS 隐藏。v0.4.2 修的正是后者引发的缺陷。判断可用性**必须看元素矩形是否落在视口内**。
7. **高级检索页不可深链**（会触发验证码），须从知网首页点「高级检索」进入。
8. **30 秒请求间隔是保守取值**，来自单次观察，未做阶梯测试。不要据此断言它是最优值。

## 8. 结果回报方式

在本目录新增 `2026-XX-XX-win11-chatgpt-desktop-verification-result.md`，至少记录：

1. 任务 A 的 pytest 完整输出摘要（8 个用例的最终状态、总计通过/失败数）。
2. 任务 B 的四个工具可见性证据，以及第 5、6 步的实际返回结构。
3. 实际 Python 版本、PowerShell 版本、磁盘占用实测值。
4. 任何与第 3、7 节所述不符的现象。

**若发现缺陷**：不要在验证分支上直接改代码。先记录复现步骤与实际/预期差异，开 issue 或在结果文档中写明，由后续单独的修复任务处理。**验证与修复分开**，避免把「验证结论」和「未经验证的修改」混在同一次提交里。

## 9. 交接时点的未决事项一览

| 事项 | 状态 |
| --- | --- |
| 8 个 PowerShell 执行用例 | **待办（任务 A）** |
| ChatGPT Desktop 四工具实机验证 | **待办（任务 B）** |
| 字段升级 SU/KY/TKA 实机路径 | 未走到，仅单元测试覆盖（任务 C，可选） |
| 30 秒间隔是否最优 | 未做阶梯测试 |
| WebVPN 单会话冲突 | 未复现确认 |
| 两个安装器浏览器缓存策略不统一 | 已确认为有意设计，是否统一另行跟进，**本次不动** |
