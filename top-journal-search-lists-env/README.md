# top-journal-search-lists-env

`Top Environmental Journal Search` 是环境科学与工程专用文献检索 Skill。
它以 ai4scholar 为主要来源，按
《环境科学与工程学科顶尖期刊目录 v4.0》的十二级顺序整理文献，并可通过独立的
`cnki-search-env` MCP 补充中国知网公开首页中文期刊结果。调用方式为
`$top-journal-search-lists-env`，MCP 工具为 `cnki_search_env(query, limit)`。
`limit` 最大为 20。

另有一个可选的第二模式：`cnki_professional_search_env`，由使用者本人经所在
机构官方 WebVPN 完成统一身份认证后，用知网专业检索按环境期刊目录定向检索
中文期刊论文。覆盖四个受控范围：`chinese_environment_top`（第6级 6 本，`LY=`
**精确**枚举）、`other_formally_recognized_chinese`（第7级中文 60 本，精确枚举）、
`environment_cssci`（第9级 241 本，精确枚举并逐批在学术期刊条件区勾选来源类别 CSSCI，
代码 `P0209`）与 `pku_core`（1987 本，只提交主题表达式并勾选来源类别北大核心，
代码 `P01`，不生成 `LY=`）。`limit` 为 1 至 50。

1987 是 v4.0 全部北大核心成员数，其中 1742 本位于第11—12级，其余 245 本已在更高
层级出现；该组的合格层级因此是 **1—12 级**，成员横跨全部层级，命中后按目录层级
排序归位。

完整工作流按 **第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心** 的顺序
依次检索，跨组总量只计全局去重后的新增论文。**第11级和第12级不得分别重复检索**——
两级同属一个 `pku_core` 范围，一次来源类别检索即可覆盖。

该模式属**机构授权**的正常访问路径，与检测规避有本质区别：**不伪造**
User-Agent、**不轮换代理**、不抹除自动化标志、**不自动破解**验证码。它
**必须人工值守，不可用于定时任务**——登录、保持浏览器窗口、中途安全验证三处
都需要人。启用时设置 `CNKI_ENV_WEBVPN_HOME` 为所在机构 WebVPN 改写后的知网
首页地址（与通用版的 `CNKI_WEBVPN_HOME` 相互独立）；运行时使用**非持久化**
浏览器上下文，不保存 Cookie、票据或 profile，**服务重启后需要重新登录**。

返回 `no_data_retry_later` 表示知网临时拒绝，**不等于空结果**；其他层级不在
覆盖范围内，应改用 ai4scholar。

分组检索依次执行 **TI → SU → KY → TKA**，并**累计**此前字段尚未取得的合格
唯一记录；达到 `limit` 即停。四个字段互相补充，不是从中挑一个"最好的"。
`topic_fields_tried` 如实列出试过哪些字段。

页面操作顺序固定为：知网首页、高级检索、专业检索、学术期刊、再次确认专业检索、
设置出版年度和来源类别、填写表达式、提交检索。该调整不改变四个受控范围或期刊清单。

**来源类别不是专业检索字段**：CSSCI（`P0209`）与北大核心（`P01`）只在选择
学术期刊后显示的条件区中勾选，且必须在提交前生效；不写入表达式或 `LY=`。
控件异常时返回 `page_contract_changed`，不会提交未筛选检索。

可检索字段为 `SU`、`TKA`、`TI`、`KY`、`AB`、`CO`、`FT`、`AU`、`FI`、`RP`、
`AF`、`LY`、`RF`、`FU`、`CLC`、`SN`、`CN`、`DOI`、`QKLM`、`FAF`、`CF`。
`YE` 不受支持，年份须通过出版年度起止控件设置。

`first_page_only=true` 表示每条表达式只读取当前页最多 50 条；
`complete=false` 时不得声称检索完整。组外记录不占限额，进 `excluded_out_of_scope_records`；
单组调用的 `already_covered_higher_priority_count` 恒为 0（跨组去重属完整
工作流职责）；`source_category_applied` 取全部已执行批次与字段的合取，可能
保守低报。

⚠ 每多试一个字段就是一次真实检索，而批次间强制 ≥30 秒节流。窄主题可能一路
试到 TKA：单组最坏为 4 × 批次数 次请求，`environment_cssci` 两批即 8 次、
约 4 分钟。请求数正是风控最敏感的维度，因此命中安全验证、登录、限流、拒绝
或页面结构变化时**立即停止换字段**——换个字段不会让风控消失。

⚠ **`LY=` 并非严格精确匹配**。2026-07-30 实测：表达式只枚举了 6 本中文环境
顶刊，结果中仍出现 2 条来源为 `Journal of Resources and Ecology` 的记录——
该刊中文名《资源与生态学报》包含清单中的「生态学报」。因此**返回的期刊不保证
全部落在分组清单内**。这类记录不会被误标：判级层如实给出 `priority_level`
为空且 `manual_review_required=true`，但它们会占用 `limit` 名额。调用方应以
判级结果而非「出现在结果里」判断一条记录是否属于该分组。

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

## 自行复算目录（可选）

发布包内附 `scripts/environment_catalog_v4.py` 和
`scripts/generate_environment_catalog_v4.py`，可重新推导 v4.0 派生产物并与随包文件
逐字节比对：

```powershell
python top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py --check
```

`--check` 只读不写：一致时打印四份产物的 SHA-256 并以 0 退出；不一致时报错并以非 0
退出（如 `生成文件不一致`、`各级期刊数错误`）。校验范围覆盖 `references/` 与
`mcpb/src/references/` 两套镜像，因此单改其中一套也会被发现。

### 它校验什么、不校验什么

脚本从 `references/` 下的七份来源快照重算的是**来源匹配、索引收录、交叉收录和审计
摘要**；已有派生字段不回流参与匹配。

**层级、环境细分领域、正式证据、内部顺序和期刊清单本身来自已批准的 v4.0 目录
markdown，不由脚本推导。** 对这些内容，`--check` 只核对每级期刊数（十二级合计 3764）
和与随包产物的字节一致，不核对某本期刊是否应当位于该层级。因此：删掉一行会因每级
计数不符而被查出，但把两本期刊的层级对调后重新生成，`--check` 仍会通过。

七份来源快照另有脚本内置的字节数与 SHA-256 锁定，被替换会直接报
`来源快照未通过字节或 SHA-256 校验`；baseline markdown 没有这种锁定。

这是**自洽性**校验，不是**真实性**校验：它证明随包产物与随包 baseline 相互一致，
不能证明 baseline 本身没被替换。请另按 Release 附带的 `checksums.sha256` 核验压缩包，
以确认下载件与官方 Release 所发布的一致。

发布包不含 `docs/audits/` 下的逐条匹配审计 JSONL（该文件只保留在仓库中），所以在
发布包里运行时会多打印一行 `docs/audits: skipped`，表示这一项未参与校验。在仓库检出
中运行则会一并校验审计输出，不打印该行。两种情况下随包目录与镜像的校验强度相同。

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

## 版本与发布包

当前环境版为 `0.3.3`，使用《`环境科学与工程学科顶尖期刊目录_v4.0.md`》和机器目录 `environment_journal_catalog_v4.0.json`。正式 Release 包含 `top-journal-search-lists-env_Skill.zip`、`cnki-search-env.mcpb` 和 `checksums.sha256`。环境版使用 `top-journal-search-lists-env`、`cnki-search-env` 和 `runtimes/cnki-search-env`；可与通用版 `top-journal-search-lists`、`cnki-search` 并存，二者互不覆盖。

### 校验发布产物

`checksums.sha256` 用于确认下载到的压缩包与官方 Release 发布的是同一份文件。这是同一
文件的比对，在任何平台都成立，也是安装前应当做的检查。

如果你从源码仓库自行重建产物，归档的 SHA-256 可能与官方值不同，这是正常现象：ZIP 的
deflate 压缩流取决于 Python 链接的 zlib 实现（例如 zlib-ng 与标准 zlib 对同一输入会产生
不同但同样合法的压缩流），而官方产物由 Ubuntu CI 构建。归档哈希不同并不意味着内容不同。

跨平台应比对**解压后的内容**。在**仓库根目录**运行：

```text
python scripts/compare_release_content.py <你的构建输出目录> <官方产物目录>
```

该脚本比对成员集合与顺序、每个成员的 CRC 与解压字节，以及打包元数据（固定时间戳与
权限位），不比较归档哈希和压缩后大小。全部一致时退出码为 0。

该脚本属于仓库的构建工具，**不随发布包分发**——解压 Skill ZIP 后在其 `scripts/` 下
找不到它。自行重建本来就需要完整仓库，按上面的路径从仓库根运行即可。
