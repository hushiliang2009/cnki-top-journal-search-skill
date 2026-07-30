# top-journal-search-lists-env

`Top Environmental Journal Search` 是环境科学与工程专用文献检索 Skill。
它以 ai4scholar 为主要来源，按
《环境科学与工程学科顶尖期刊目录 v3.0》的十级顺序整理文献，并可通过独立的
`cnki-search-env` MCP 补充中国知网公开首页中文期刊结果。调用方式为
`$top-journal-search-lists-env`，MCP 工具为 `cnki_search_env(query, limit)`。
`limit` 最大为 20。

另有一个可选的第二模式：`cnki_professional_search_env`，由使用者本人经所在
机构官方 WebVPN 完成统一身份认证后，用知网专业检索按环境期刊目录定向检索
中文期刊论文。覆盖 `chinese_environment_top`（6 本，`LY=` **精确**枚举）与
`environment_cssci`（241 本，精确枚举并逐批附结果页「来源类别」= CSSCI），
`limit` 为 1 至 50。

该模式属**机构授权**的正常访问路径，与检测规避有本质区别：**不伪造**
User-Agent、**不轮换代理**、不抹除自动化标志、**不自动破解**验证码。它
**必须人工值守，不可用于定时任务**——登录、保持浏览器窗口、中途安全验证三处
都需要人。启用时设置 `CNKI_ENV_WEBVPN_HOME` 为所在机构 WebVPN 改写后的知网
首页地址（与通用版的 `CNKI_WEBVPN_HOME` 相互独立）；运行时使用**非持久化**
浏览器上下文，不保存 Cookie、票据或 profile，**服务重启后需要重新登录**。

返回 `no_data_retry_later` 表示知网临时拒绝，**不等于空结果**；其他层级不在
覆盖范围内，应改用 ai4scholar。

检索字段按 **TI → SU → KY → TKA** 的优先序逐级替换：篇名最准，主题次之，
关键词第三，篇关摘兜底。**有效记录数达到 `limit` 就停止**，都不够用时取有效
记录最多的那个字段。返回值里的 `topic_field` 与 `topic_fields_tried` 如实
说明最终用了哪个、试过哪些。

⚠ 每多试一个字段就是一次真实检索，而批次间强制 ≥30 秒节流。窄主题可能一路
试到 TKA：单组最坏为 4 × 批次数 次请求，`environment_cssci` 两批即 8 次、
约 4 分钟。请求数正是风控最敏感的维度，因此命中安全验证、登录、限流、拒绝
或页面结构变化时**立即停止换字段**——换个字段不会让风控消失。

## 支持范围

- Windows 11 PowerShell；
- macOS 与 Linux；
- Python 3.11 或更高版本；
- Codex CLI、ChatGPT Desktop 中的 Codex、Claude Code 与 Claude Desktop。

ai4scholar 不包含在本仓库和发布包内，请在目标电脑自行配置。环境版使用
`top-journal-search-lists-env`、`cnki-search-env` 和
`runtimes/cnki-search-env`，可与通用版 `top-journal-search-lists`、
`cnki-search` 同时安装，互不替换。

## 安装前准备

私有仓库需要有效的 GitHub 认证。可从仓库检出：

```text
git clone https://github.com/hushiliang2009/cnki-top-journal-search-skill.git
cd cnki-top-journal-search-skill
```

也可解压 `top-journal-search-lists-env_Skill.zip`。安装器会复制完整 Skill，
创建独立 Python 运行环境并安装 `mcp` 与 `playwright`。如需预先准备浏览器，
运行：

```text
python -m playwright install chromium chromium-headless-shell
```

直接安装 `cnki-search-env.mcpb` 时，如果目标电脑既没有系统 Chrome、Edge 或
Chromium，也没有 Playwright 浏览器缓存，首次实际检索会在 MCPB 的 Python
环境中自动执行上述安装命令。浏览器资产保存在当前 MCPB 运行环境的
`playwright-browsers/` 中；浏览器准备完成后才开始计算单次检索超时，取消准备
任务时会终止安装子进程。可用 `CNKI_ENV_BROWSER_PATH` 指向环境版 MCP 专用的
浏览器可执行文件；该配置不读取通用版的 `CNKI_BROWSER_PATH`。

手工复制 Skill 目录不会自动配置 MCP，也不会创建独立运行环境。

## Windows 安装指南

同时安装到 ChatGPT Desktop 中的 Codex、Claude Code 和 Claude Desktop：

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists-env\installers\install.ps1 -Codex -ClaudeCode -ClaudeDesktop
```

可只保留所需开关。使用 `-PythonExe` 指定解释器。

## macOS 安装指南

```sh
sh ./top-journal-search-lists-env/installers/install.sh --codex --claude-code --claude-desktop
```

可只保留所需选项。该命令支持 ChatGPT Desktop 中的 Codex、Claude Code 和
Claude Desktop。

## Linux 安装指南

Linux 可安装到 Codex CLI、Claude Code 和 Claude Desktop（Linux beta）：

```sh
sh ./top-journal-search-lists-env/installers/install.sh --codex --claude-code --claude-desktop
sh ./top-journal-search-lists-env/installers/install.sh --claude-desktop
```

Claude Desktop 配置位于 `~/.config/Claude/claude_desktop_config.json`。
目前没有官方 Linux 版 ChatGPT Desktop。WSL 中的安装属于 Linux 侧安装，
绝不会配置 Windows ChatGPT Desktop；如需 Windows 侧 ChatGPT Desktop 中的 Codex，应在
Windows PowerShell 中运行安装器。

macOS 与 Linux 可用 `CNKI_ENV_PYTHON` 指定解释器。

安装器先核验 Python 版本，再进行事务式复制、运行时安装和配置合并。运行时会
执行 `python -m playwright install chromium chromium-headless-shell`，随后完成
Python 导入检查和 Chromium 离线启动检查。任何阶段失败都会
恢复原有 Skill、环境运行时和配置。旧 Skill 备份保存在客户端主目录的
`backups/skills/`，旧环境运行时备份保存在 `backups/runtimes/`，两者均不放入
`skills/` 扫描目录；安装器生成带时间戳的备份，每类只保留最近 3 份。安装器只新增或
替换环境版内容，不删除 Zotero、ai4scholar 等其他 MCP 服务。

只要选择 Codex，运行环境位于 Codex Home；
仅选择 Claude 目标时，运行环境位于 Claude Home。Playwright 浏览器资产固定
保存在该环境运行时的 `playwright-browsers/` 子目录，因此随运行时一起备份和
回滚，不使用通用 Skill 或用户级 Playwright 的共享缓存。

## 安装后验证

Windows：

```powershell
python top-journal-search-lists-env/scripts/catalog_lookup.py validate
python top-journal-search-lists-env/scripts/catalog_lookup.py lookup "Cell" "Nature Climate Change" "中国环境科学"
```

macOS/Linux：

```sh
python3 top-journal-search-lists-env/scripts/catalog_lookup.py validate
python3 top-journal-search-lists-env/scripts/catalog_lookup.py lookup "Cell" "Nature Climate Change" "中国环境科学"
```

预期层级分别为 1、2、6；`Nature Climate Change` 的
`ncs_internal_rank` 为 1。目录两份快照必须字节一致，文件 SHA-256 为
`A01E40D5E011276D74B8BC277E0585F9C0D47E9E2C16D3082B0959643104DFF4`。

安装后可检查：

```powershell
codex mcp get cnki-search-env
```

## 开发者完整测试

先在开发环境安装 pytest、mcp 和 playwright，再从环境 Skill 目录运行：

```text
python -m pytest -q -p no:cacheprovider
python scripts/catalog_lookup.py validate
python tests/_mcp_handshake.py
python tests/_mcpb_handshake.py
python tests/_mcpb_raw_handshake.py
python scripts/build_release.py --output release
```

## 使用

```text
$top-journal-search-lists-env 请检索 PFAS 水处理与污染控制领域近五年的研究，
优先环境顶尖期刊，并说明环境细分领域和正式判级证据。
```

正常检索通过 `scripts/catalog_lookup.py` 查询目录，不全文加载目录。只有目录
审计或更新任务才读取完整参考文件。

## CNKI 能力边界

CNKI 只使用公开首页主题检索、第一页、最多20条。不登录、不下载、
不持久化 Cookie，不持久化缓存，运行期仅24小时内存缓存。遇到验证码、登录页、401、
403、429、`challenge_detected` 或页面结构变化时立即停止，不刷新重试，不使用
代理或用户浏览器状态。此时继续使用 ai4scholar，并明确说明中文补充检索受限。

## 更新、备份与卸载

目录内容变化时应同时更新两个目录快照、Skill 版本、目录哈希和回归测试。重复
安装只替换环境版 Skill、环境运行时和 `cnki-search-env` 配置，不改动通用版或
ai4scholar。

卸载时删除客户端中的 `skills/top-journal-search-lists-env`、
`runtimes/cnki-search-env`，并从客户端配置中删除 `cnki-search-env` 条目。
操作前备份配置；不要删除 `cnki-search` 或其他 MCP。
