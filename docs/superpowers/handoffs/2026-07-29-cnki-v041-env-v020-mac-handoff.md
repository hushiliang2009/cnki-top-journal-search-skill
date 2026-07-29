# CNKI 通用版 v0.4.1 与环境版 v0.2.0 开发交接说明

日期：2026-07-29
编写环境：Windows 11，ChatGPT Desktop 中的 Codex
接续环境：macOS，Claude Desktop
仓库：`hushiliang2009/cnki-top-journal-search-skill`

## 1. 文档用途

本文档汇总 2026 年 7 月 28 日以来，Windows 11 上 ChatGPT Desktop Codex 针对本项目完成的全部可追溯工作，供另一台 MacBook 上的 Claude Desktop 直接续接。

本文档覆盖：

- 已确认的产品设计与安全边界；
- 通用版 v0.4.1 和环境版 v0.2.0 的实施计划；
- 当前实际进度；
- 已完成的代码、测试和审查修正；
- 尚未完成的独立复核、自动化质量门槛、人工验证和发布工作；
- 2026 年 7 月 28 日以来的提交记录及受影响文件；
- 两个续接分支的用途和建议操作顺序；
- macOS 端开始工作前必须核对的仓库状态。

本文件是进度交接说明，不替代已经批准的设计和逐步实施计划。发生表述差异时，按以下优先级处理：

1. 用户最新明确要求；
2. 已批准设计：`docs/superpowers/specs/2026-07-28-cnki-v041-env-v020-professional-search-design.md`；
3. 通用版计划：`docs/superpowers/plans/2026-07-28-cnki-v041-professional-runtime.md`；
4. 环境版计划：`docs/superpowers/plans/2026-07-28-cnki-env-v020-professional-search.md`；
5. 本交接说明。

## 2. 仓库与分支状态

### 2.1 基准

- 远程 `main` 基准提交：`7c858951e407da55980e69dced7c8c3edc1fe859`
- 基准版本：通用版 v0.4.0
- 当前通用版开发提交：`20fd3c4426f753dc3e1152912b1273166fabc41f`
- 当前开发提交相对 `main`：领先 22 个提交
- 当前工作树在交接文件写入前：干净
- 当前通用版源码声明版本：`0.4.1`
- 当前环境版源码声明版本：`0.1.0`

截至本文档编写时，远程 `main` 尚未包含 v0.4.1 修改，也没有创建 v0.4.1 标签或 Release。

### 2.2 续接分支

本次交接创建两个远程分支：

| 分支 | 用途 | 初始关系 |
|---|---|---|
| `codex/release-0.4.1` | 完成通用版 v0.4.1 的最终复核、自动化验证、人工 WebVPN 验证、PR、合并和发布 | 以当前通用版开发提交及本交接文件为起点 |
| `codex/release-0.2.0` | 完成环境版 v0.2.0 的代码开发、验证和独立发布 | 初始继承同一通用版基础，暂未包含环境版 v0.2.0 实现 |

不要同时在两个分支上独立修改通用版。应先完成 `codex/release-0.4.1`。通用版合并到 `main` 后，环境版分支应先同步最新 `main`，再开始环境版任务 1。

## 3. 已确认的产品定位

### 3.1 通用版

通用版包含两个 MCP 工具：

- `cnki_search(query, limit=20)`：公开知网首页主题检索；
- `cnki_professional_search(topic, group, limit=50, year_from=None, year_to=None)`：WebVPN 人工值守专业检索。

专业检索包含两个分组：

- `chinese_top_journals`：综合目录中的 13 种中文顶级期刊，使用精确刊名条件；
- `cssci`：使用主题表达式，并在结果页设置 CSSCI 来源类别。

公开主题检索的默认值和上限保持 20，不得借 v0.4.1 扩大。

### 3.2 环境版

环境版保持独立安装、独立运行和独立发布，计划包含两个 MCP 工具：

- `cnki_search_env(query, limit=20)`；
- `cnki_professional_search_env(topic, group, limit=50, year_from=None, year_to=None)`。

专业检索包含两个环境领域分组：

- `chinese_environment_top`：环境目录中的 6 种中文顶级期刊；
- `environment_cssci`：环境目录中的 241 种 CSSCI 期刊，按表达式长度动态分批，并设置 CSSCI 来源类别。

环境版不得导入通用版 Python 包，不得覆盖通用版 Skill、运行时、MCP 配置或备份。

### 3.3 ai4scholar 与 CNKI 的关系

- ai4scholar 仍是主要文献检索来源；
- CNKI 主要补充近期中文期刊论文；
- CNKI 检索结果用于形成题录清单和期刊判级；
- 工具不负责论文下载；
- 公开 CNKI 检索和 WebVPN 专业检索均不能取代人工核验。

## 4. 不得改变的安全与合规边界

后续实现和复核必须继续满足以下要求：

- WebVPN 专业检索只用于用户本人在场的人工值守场景；
- 用户自行完成统一身份认证和可能出现的安全验证；
- 程序不读取、填写、保存或输出账号和密码；
- 不保存 Cookie、登录票据、HTML、完整 URL、浏览器 profile 或 storage state；
- 不接入用户日常 Chrome 会话，不使用 CDP；
- 不使用持久化浏览器上下文；
- 不自动破解验证，不模拟拖动，不自动刷新，不切换代理；
- 不修改 User-Agent，不增加浏览器指纹或反检测措施；
- 浏览器上下文必须设置 `accept_downloads=False`；
- 不提供定时、后台无人值守或批量抓取能力；
- 遇到不可恢复的挑战、拒绝、限流或页面合同变化时停止，不得循环重试；
- `network_error` 最多重试一次；
- 正常专业检索批次之间至少间隔 30 秒；
- 真实 WebVPN 验证失败时不得创建正式标签、Release 或声称生产可用。

## 5. 总体进度

进度不能仅按提交数量判断。以下比例只用于交接沟通，不是发布验收结论。

| 工作部分 | 当前状态 | 估算进度 |
|---|---|---:|
| 共同设计和两份实施计划 | 已完成并提交 | 100% |
| 通用版 v0.4.1 功能实现 | 任务 1 至任务 5 已实现 | 100% |
| 通用版最终复核和发布 | 任务 5 最后一轮独立复核待重跑；任务 6、任务 7未开始 | 约 68% 至 72% |
| 环境版 v0.2.0 功能实现 | 只有设计和计划，代码尚未开始 | 0% |
| 两个版本全部交付 | 通用版接近验证阶段，环境版尚未实施 | 约 34% |

通用版最近一次全量 pytest 结果很好，但不能据此声称 v0.4.1 已达到发布状态。尚缺静态检查、目录校验、三类 MCP 握手、重复构建、产物检查、隔离安装器验证、最终独立复核和真实 WebVPN 端到端验证。

## 6. 2026 年 7 月 28 日以来完成的设计工作

### 6.1 共同设计

提交 `9781754` 新增共同设计，主要决定如下：

- 先修复通用版 v0.4.1，再移植到环境版 v0.2.0；
- 两个产品采用相同接口边界，但各自保留完整源码、目录、安装器和 MCPB；
- 专业检索由默认生产运行时按需创建，不依赖测试注入；
- 执行器接收分组感知的完整执行计划，而不是只有表达式字符串；
- WebVPN 使用可见 Chromium 和非持久化上下文；
- 每个 MCP 服务进程内复用内存会话，进程结束后会话消失；
- 题录按规范化篇名、期刊和年度去重，并保留信息更完整的记录；
- 断点只保存安全、必要的查询摘要、批次状态和题录，不保存浏览器状态；
- 两个版本必须分别通过真实人工 WebVPN 验证后才能发布。

### 6.2 两份实施计划

提交 `f319c79` 新增两份测试先行的实施计划。

通用版计划共 7 项任务：

1. 建立分组感知的专业检索执行计划；
2. 改为非持久化 WebVPN 浏览器会话；
3. 建立默认生产运行时并接入 MCP；
4. 修复断点、提前停止和重复题录选择；
5. 更新版本、文档和发布清单；
6. 完成自动化验证和独立代码复核；
7. 人工 WebVPN 验证、合并、发布和本地安装。

环境版计划共 7 项任务：

1. 同步公开检索的页面状态修正；
2. 从环境目录生成专业检索计划；
3. 增加环境版 WebVPN 会话和生产运行时；
4. 注册环境版专业检索 MCP 工具；
5. 更新环境版版本、文档和发布契约；
6. 完成环境版自动化验证和共存复核；
7. 人工验证、环境版发布和 ChatGPT Desktop 升级。

## 7. 通用版 v0.4.1 已完成工作

### 7.1 任务 1：分组感知的执行计划

状态：完成，独立复核通过。
提交：`c002fe2`

已实现：

- `ExpressionBatch` 携带表达式、批次编号、总批次、每页数量、来源类别和目录摘要；
- 中文顶级期刊组生成 13 个精确 `LY=` 条件；
- CSSCI 组只生成主题表达式，并设置 `source_category="CSSCI"`；
- 专业服务把完整计划传入执行器；
- Skill 源码布局与 MCPB 源码布局同步。

任务 1 原有一项测试辅助函数类型标注较旧的轻微问题，已在任务 4 修正过程中一并消除。

### 7.2 任务 2：非持久化 WebVPN 会话

状态：完成，经过两轮审查修正后通过。
提交：`48ceb10`、`9070cc4`、`bab7f9c`

已实现：

- 删除 `profile_dir` 和旧探针的 `--profile` 参数；
- 使用 `chromium.launch(headless=False)`；
- 使用 `browser.new_context(locale="zh-CN", accept_downloads=False)`；
- 不使用 `launch_persistent_context()`；
- `WebVpnSession` 明确持有 Playwright、browser、context 和首页；
- 创建失败、导航失败、取消和重复取消时继续完成资源清理；
- `close()` 幂等；
- 页面执行顺序覆盖表达式填写、提交、结果等待、可选来源类别、每页 50 条和内容读取；
- 临时 `page_contract_changed` 会轮询等待，不立即误判为最终失败。

### 7.3 任务 3：默认生产运行时与 MCP

状态：完成，经过五轮审查修正后通过。
提交：`b49a8f1`、`092fe83`、`5d1ea3c`、`3d77234`、`e26930b`、`3e7273a`

已实现：

- 新增 `professional_runtime.py`；
- `CnkiMcpServer()` 在设置 `CNKI_WEBVPN_HOME` 后可按需创建真实专业检索运行时；
- 首次并发调用使用异步锁，避免重复创建运行时；
- MCP 真实实例通过 FastMCP lifespan 在同一事件循环关闭资源；
- 运行时串行处理浏览器请求；
- 排队请求取消后不进入服务；
- 配置、登录、浏览器、页面合同和网络错误映射为结构化状态；
- 年度参数在 MCP schema 中限制为 1900 至当前年份加一；
- 每批从保留的知网首页打开结果页；
- 结果页、弹窗和挑战页的所有权及关闭责任已明确；
- 人工挑战等待的总时间不超过 600 秒；
- 取消期间出现的晚到弹窗、晚到任务异常和清理时间预算均已处理。

独立审查先后发现并修复：

- 并发惰性初始化泄漏；
- 页面合同状态丢失；
- 结果页所有权泄漏；
- 挑战等待超过 600 秒；
- 取消期间的新页面和弹窗竞争；
- 延迟任务异常未被取回。

### 7.4 任务 4：断点、提前停止和题录去重

状态：完成，经过五轮审查修正后通过。
提交：`5572211`、`b7ef06f`、`2ecfd55`、`cdd3934`、`53af7c1`、`08028ed`

已实现：

- 使用查询计划的 SHA-256 摘要作为断点身份；
- 断点只保存白名单字段；
- 断点采用同目录临时文件和原子替换；
- 断点读取、写入或清理失败时按 `configuration_error` 失败关闭；
- token 不匹配时不复用旧题录；
- 恢复的完成批次只允许符合语义的 `success` 和 `no_results`；
- 严格验证题录、计数、状态和不完整记录；
- 清理控制字符、零宽字符和异常空白；
- 拒绝 URL、HTML、Cookie、绝对路径、Windows 设备路径及 `file` URI；
- 允许真实结果页缺失序号时使用 `result_rank=0`；
- 达到用户 `limit` 后停止提交尚未执行的批次；
- `network_error` 最多重试一次，并继续服从限速；
- `no_results` 可以继续下一期刊批次；
- 终止状态在已有题录时返回 `partial`，无题录时保留原状态；
- 作者感知的题录分组不再因输入顺序错误合并不同论文；
- 重复题录保留信息更完整的记录。

独立审查先后发现并修复：

- 旧断点可能残留不安全字段；
- token 不匹配时复用旧完成数据；
- 缺作者记录可能把作者互斥的论文错误连接；
- 持久化非原子和异常被吞；
- 恢复状态与记录语义不一致；
- 控制字符、零宽字符、路径变体和文件 URI 绕过；
- 缺失结果序号的真实记录无法保存。

### 7.5 任务 5：版本、文档、发布清单和 E2E 辅助脚本

状态：实现已完成，第三轮修正后的独立复核尚未重跑。
提交：`86dd785`、`cf57e70`、`9464354`、`20fd3c4`

已实现：

- Python 包、MCP `serverInfo`、MCPB manifest、pyproject 和锁文件统一为 `0.4.1`；
- 新运行时模块和测试已纳入发布契约；
- README、SKILL.md 和参考文档改为非持久化 WebVPN 会话口径；
- 明确 `CNKI_WEBVPN_HOME` 是唯一 WebVPN 地址变量；
- 明确不再需要 `CNKI_WEBVPN_PROFILE`；
- 明确服务重启后需要重新登录；
- 新增仓库专用 `tests/_webvpn_e2e.py`；
- E2E 辅助脚本不进入 Skill ZIP 或 MCPB；
- E2E 输出只允许固定摘要字段；
- 递归拒绝 URL、Cookie、HTML、storage state、profile、浏览器、路径、凭据和令牌字段；
- 拒绝数字混淆、Unicode 同形字符和非 ASCII 键名；
- 成功输出为单行 JSON，失败输出为固定安全错误；
- 隔离 Python stdout、stderr、操作系统文件描述符 1 和 2，以及继承标准流的子进程输出；
- 异常、取消和部分文件描述符初始化失败后恢复原标准流。

任务 5 的独立审查发现 E2E 输出可能通过嵌套字段、键名变体、运行时直接输出、原生文件描述符和子进程泄漏。三轮修正均已提交。第三轮最终独立复核在开始后被中断，因此 Mac 端必须重新复核 `9464354..20fd3c4`，不能沿用未完成的复核状态。

## 8. 通用版已有测试证据

各阶段保留了测试先行的失败证据和修复后的通过证据。主要结果如下：

| 阶段 | 最近通过结果 |
|---|---|
| 任务 1 聚焦测试 | 23 passed |
| 任务 2 聚焦测试 | 59 passed |
| 任务 3 最终独立复核后全量测试 | 358 passed，91 subtests passed |
| 任务 4 最终复核前后全量测试 | 431 passed，91 subtests passed，连续两次通过 |
| 任务 5 初始实现全量测试 | 435 passed，91 subtests passed |
| 任务 5 第一轮修正 | 454 passed，91 subtests passed |
| 任务 5 第二轮修正 | 464 passed，91 subtests passed |
| 任务 5 第三轮修正聚焦测试 | 35 passed，17 deselected |
| 当前提交授权环境全量测试 | 467 passed，91 subtests passed |

Windows 受限沙箱中，Git for Windows 的 `sh.exe` 曾因无法创建 signal pipe 报 `Win32 error 5`，相关三个安装器测试在授权环境单独重跑通过。这是执行环境权限问题，没有据此修改产品代码。

当前仍缺少以下发布级证据：

- 当前提交的最终独立代码复核；
- `ruff check .`；
- `mypy top-journal-search-lists/scripts/`；
- 目录校验；
- Skill、安装后 MCPB 和原始 MCPB 三类握手；
- 两次发布构建的逐字节一致性；
- 产物成员检查；
- 隔离 HOME 下的 Windows 安装器完整验证；
- 真实 WebVPN 的两个通用版分组验证；
- GitHub PR 和主分支 CI；
- v0.4.1 标签、正式 Release、重新下载和哈希复核；
- 从 Release 附件安装到本地 ChatGPT Desktop。

## 9. 通用版剩余任务

### 9.1 先完成任务 5 最终复核

必须重新独立审查：

```text
9464354..20fd3c4
```

重点检查：

- 文件描述符保存、替换、恢复和关闭是否覆盖所有部分失败；
- `sys.stdout`、`sys.stderr` 和 fd 1、fd 2 是否始终恢复；
- build、search、净化、close 和子进程输出是否均被隔离；
- 最终 JSON 是否只在恢复标准流后输出；
- 固定错误是否不会拼接原异常或敏感字段；
- `_webvpn_e2e.py` 是否继续保持仓库专用，未进入发布白名单。

若发现问题，先增加失败测试，再修复并重新运行聚焦测试和完整测试。若没有问题，记录明确的批准结论，不创建空提交。

### 9.2 执行通用版计划任务 6

按原计划执行：

```bash
ruff check .
mypy top-journal-search-lists/scripts/
python3 -m pytest top-journal-search-lists -q -p no:cacheprovider
python3 top-journal-search-lists/scripts/catalog_lookup.py validate
python3 top-journal-search-lists/tests/_mcp_handshake.py
python3 top-journal-search-lists/tests/_mcpb_handshake.py
python3 top-journal-search-lists/tests/_mcpb_raw_handshake.py
```

随后：

- 将发布产物构建到两个不同目录；
- 比较 Skill ZIP、MCPB 和校验和文件；
- 检查归档包含 `professional_runtime.py`；
- 检查归档不含缓存、Git 元数据、Cookie、浏览器状态、下载目录和 E2E 辅助脚本；
- 在隔离 HOME 中验证安装器；
- 人工追踪真实生产调用路径；
- 仅在发现可复现缺陷时提交修复。

原计划要求 Windows 隔离 HOME 安装验证。Mac 端可以先完成 macOS 安装器回归，但不得用它替代 Windows 验收。Windows 验收需要在本机或等效 Windows 11 环境补跑。

### 9.3 执行通用版计划任务 7

该任务必须由用户参与：

1. 设置用户提供的 `CNKI_WEBVPN_HOME`；
2. 在可见浏览器中运行 `chinese_top_journals`；
3. 用户本人完成 WebVPN 登录和安全验证；
4. 运行 `cssci`；
5. 检查篇名、期刊、发表年度、期刊等级、每页 50 条和 CSSCI 来源类别；
6. 检查输出不含敏感状态；
7. 任一场景失败时停止发布；
8. 两个场景成功后再创建 PR；
9. 等待 CI 全部通过并合并；
10. 创建 `v0.4.1` 标签；
11. 只采用 Ubuntu Python 3.11 正式构建任务生成的附件；
12. 重新下载附件并复核哈希和包内版本；
13. 从 Release 附件安装到 ChatGPT Desktop；
14. 验证 `cnki-search` MCP 和两个工具，再提示用户重启客户端。

不得从本地工作树直接制作正式 Release 附件。

## 10. 环境版 v0.2.0 当前状态

环境版尚未修改生产代码。以下工作均未开始：

| 任务 | 状态 |
|---|---|
| 任务 1：同步公开检索页面状态修正 | 未开始 |
| 任务 2：从环境目录生成专业检索计划 | 未开始 |
| 任务 3：增加环境版 WebVPN 会话和生产运行时 | 未开始 |
| 任务 4：注册环境版专业检索 MCP 工具 | 未开始 |
| 任务 5：更新版本、文档和发布契约 | 未开始 |
| 任务 6：自动化验证和共存复核 | 未开始 |
| 任务 7：人工验证、独立发布和本地安装 | 未开始 |

环境版当前仍为 v0.1.0，只提供既有公开检索能力。不要把设计文件中计划的 v0.2.0 能力当作现有功能。

## 11. 环境版 v0.2.0 后续实施要点

### 11.1 开始条件

开始环境版开发前必须：

- 通用版 v0.4.1 已完成最终复核；
- 通用版相关修复已经合并到远程 `main`；
- `codex/release-0.2.0` 已同步最新 `main`；
- 通用版测试仍全量通过；
- 环境版现有十级目录和期刊数量基线已记录。

### 11.2 任务 1

将通用版已经修复的公开页面状态判断同步到环境版，包括：

- 公开主题检索上限仍为 20；
- 增加检索按钮兼容选择器；
- 提交后优先识别 HTTP、挑战、登录、结果页和明确无结果；
- `no_data_retry_later` 不得误报为 `no_results`；
- 页面结构缺失返回 `page_contract_changed`。

### 11.3 任务 2

从环境版目录生成两组专业计划：

- 6 种中文环境顶级期刊生成精确刊名条件；
- 241 种环境 CSSCI 期刊按表达式长度动态分批；
- CSSCI 每批均设置来源类别；
- 保持环境目录十级判级和既有计数不变；
- 服务完成解析、判级、排序、停止和作者感知去重。

### 11.4 任务 3

移植并独立实现环境版 WebVPN 运行时：

- 环境变量使用 `CNKI_ENV_WEBVPN_HOME`；
- 不导入通用版运行时；
- 使用非持久化可见 Chromium；
- 禁止下载；
- 浏览器操作串行；
- 正常批次间至少 30 秒；
- 网络错误最多重试一次；
- 人工挑战等待不超过 600 秒；
- 断点放在环境版独立状态目录；
- 断点不得含账号、Cookie、URL、HTML、浏览器状态或本机绝对路径。

### 11.5 任务 4

注册 `cnki_professional_search_env`：

- 分组只允许 `chinese_environment_top` 和 `environment_cssci`；
- limit 为 1 至 50；
- 年度范围受 schema 约束；
- 不支持的分组必须在打开浏览器前拒绝；
- FastMCP lifespan 在同一事件循环关闭运行时；
- 三类握手必须精确列出两个环境版工具。

### 11.6 任务 5

更新环境版发布契约：

- 版本统一为 `0.2.0`；
- 更新 Python 包、MCP `serverInfo`、manifest、pyproject 和 uv.lock；
- 更新 README、SKILL.md、参考文档和客户端描述；
- 新增环境版仓库专用 E2E 辅助脚本；
- E2E 脱敏边界不得低于通用版当前实现；
- 发布归档包含四个专业模块，但不包含 E2E 辅助脚本；
- CI 继续覆盖 Ubuntu Python 3.11 至 3.14，以及 Windows、macOS Python 3.11；
- 正式环境版产物只由 Ubuntu Python 3.11 任务上传。

### 11.7 任务 6

完成环境版全量测试、通用版回归、两次可复现构建、包内容检查和双产品共存安装。必须确认：

- 两个 Skill 目录同时存在；
- 两个运行时同时存在；
- `[mcp_servers.cnki-search]` 与 `[mcp_servers.cnki-search-env]` 同时存在；
- 重装任一产品不覆盖另一产品；
- 环境版不导入通用版目录；
- 6 种和 241 种期刊均来自环境目录。

### 11.8 任务 7

真实验证两个环境分组：

- `chinese_environment_top`；
- `environment_cssci`。

环境版使用独立标签：

```text
top-journal-search-lists-env-v0.2.0
```

环境版使用独立 Release 和独立附件：

- `top-journal-search-lists-env_Skill.zip`；
- `cnki-search-env.mcpb`；
- `checksums.sha256`。

不得覆盖、移动或复用通用版 v0.4.1 的标签及附件。

## 12. 2026 年 7 月 28 日以来的提交记录

`7c85895` 是远程 `main` 的 v0.4.0 基准。其后的 22 个开发提交如下：

| 顺序 | 提交 | 说明 |
|---:|---|---|
| 1 | `9781754` | 设计通用版 v0.4.1 和环境版 v0.2.0 |
| 2 | `f319c79` | 编写两份实施计划 |
| 3 | `c002fe2` | 建立分组感知的专业检索计划 |
| 4 | `48ceb10` | 使用非持久化 WebVPN 浏览器会话 |
| 5 | `9070cc4` | 清理 WebVPN 启动失败后的资源 |
| 6 | `bab7f9c` | 完成取消期间的 WebVPN 清理 |
| 7 | `b49a8f1` | 接入默认专业检索生产运行时 |
| 8 | `092fe83` | 加固专业运行时生命周期 |
| 9 | `5d1ea3c` | 修复运行时审查缺口 |
| 10 | `3d77234` | 修复取消时页面所有权竞争 |
| 11 | `e26930b` | 共享弹窗取消清理期限 |
| 12 | `3e7273a` | 取回延迟点击任务异常 |
| 13 | `5572211` | 净化断点并按 limit 提前停止 |
| 14 | `b7ef06f` | 加固断点复用和题录身份 |
| 15 | `2ecfd55` | 原子保存断点并按作者分组 |
| 16 | `cdd3934` | 畸形断点失败关闭 |
| 17 | `53af7c1` | 加固断点 payload 校验 |
| 18 | `08028ed` | 接受未知结果序号并拒绝文件路径 |
| 19 | `86dd785` | 准备通用版 0.4.1 |
| 20 | `cf57e70` | 加固 WebVPN E2E 输出 |
| 21 | `9464354` | 隔离 WebVPN E2E 异步输出 |
| 22 | `20fd3c4` | 隔离 WebVPN E2E 进程级输出 |

这些提交均已在 Windows 11 工作树中提交。交接文件是后续新增的单独提交。

## 13. 受影响文件清单

相对 v0.4.0 基准，当前通用版开发修改 34 个项目文件，共约 10,145 行新增、316 行删除。清单如下。

### 13.1 设计和计划

- `docs/superpowers/specs/2026-07-28-cnki-v041-env-v020-professional-search-design.md`
- `docs/superpowers/plans/2026-07-28-cnki-v041-professional-runtime.md`
- `docs/superpowers/plans/2026-07-28-cnki-env-v020-professional-search.md`

### 13.2 通用版用户文档和元数据

- `top-journal-search-lists/README.md`
- `top-journal-search-lists/SKILL.md`
- `top-journal-search-lists/references/cnki-search-reference.md`
- `top-journal-search-lists/mcpb/manifest.json`
- `top-journal-search-lists/mcpb/pyproject.toml`
- `top-journal-search-lists/mcpb/uv.lock`
- `top-journal-search-lists/scripts/build_release.py`

### 13.3 Skill 源码布局

- `top-journal-search-lists/scripts/cnki_search/__init__.py`
- `top-journal-search-lists/scripts/cnki_search/mcp_server.py`
- `top-journal-search-lists/scripts/cnki_search/professional.py`
- `top-journal-search-lists/scripts/cnki_search/professional_runtime.py`
- `top-journal-search-lists/scripts/cnki_search/professional_service.py`
- `top-journal-search-lists/scripts/cnki_search/webvpn.py`

### 13.4 MCPB 源码布局

- `top-journal-search-lists/mcpb/src/cnki_search/__init__.py`
- `top-journal-search-lists/mcpb/src/cnki_search/mcp_server.py`
- `top-journal-search-lists/mcpb/src/cnki_search/professional.py`
- `top-journal-search-lists/mcpb/src/cnki_search/professional_runtime.py`
- `top-journal-search-lists/mcpb/src/cnki_search/professional_service.py`
- `top-journal-search-lists/mcpb/src/cnki_search/webvpn.py`

### 13.5 测试和人工辅助脚本

- `top-journal-search-lists/tests/_webvpn_e2e.py`
- `top-journal-search-lists/tests/_webvpn_probe.py`
- `top-journal-search-lists/tests/test_cnki_async.py`
- `top-journal-search-lists/tests/test_cnki_mcp.py`
- `top-journal-search-lists/tests/test_cnki_package_contract.py`
- `top-journal-search-lists/tests/test_cnki_professional_mcp.py`
- `top-journal-search-lists/tests/test_cnki_professional_runtime.py`
- `top-journal-search-lists/tests/test_cnki_professional_service.py`
- `top-journal-search-lists/tests/test_cnki_webvpn.py`
- `top-journal-search-lists/tests/test_cnki_webvpn_page.py`
- `top-journal-search-lists/tests/test_installers.py`
- `top-journal-search-lists/tests/test_mcpb_manifest.py`

本交接文件新增后，受影响文件总数相应增加 1。

## 14. 本地未提交审查材料的处理

Windows 工作树的 `.superpowers/sdd/2026-07-28-cnki-v041-professional-runtime/` 下保存了逐任务 brief、实施报告、审查差异和进度台账。这些文件按仓库规则被忽略，没有作为产品文件提交。

本交接文件已经汇总其中的任务状态、提交、测试结果、审查问题和剩余复核事项。Mac 端不应依赖本机的忽略目录，也不应假定可以从 GitHub 读取这些内部文件。

## 15. MacBook 续接步骤

### 15.1 克隆与核对

```bash
git clone https://github.com/hushiliang2009/cnki-top-journal-search-skill.git
cd cnki-top-journal-search-skill
git fetch origin --prune
git log --oneline -1 origin/codex/release-0.4.1
git log --oneline -1 origin/codex/release-0.2.0
```

两个分支初始应指向同一个包含本交接文件的提交。

建议使用独立工作树：

```bash
git worktree add ../cnki-release-0.4.1 -b claude/release-0.4.1 origin/codex/release-0.4.1
git worktree add ../cnki-release-0.2.0 -b claude/release-0.2.0 origin/codex/release-0.2.0
```

不要在同一个工作树来回切换两个版本。

### 15.2 开发环境

最低 Python 版本为 3.11。建议使用独立虚拟环境，并安装：

- pytest；
- ruff；
- mypy；
- `mcp>=1,<2`；
- `playwright>=1.45,<2`；
- uv，用于更新锁文件和发布构建。

安装 Playwright 运行时：

```bash
python3 -m playwright install chromium chromium-headless-shell
```

开始修改前先运行通用版基线：

```bash
python3 -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
```

若基线与本文档记录不同，先区分依赖、平台和代码问题，不要直接修改实现。

### 15.3 推荐工作顺序

1. 阅读共同设计、通用版计划和本交接文件；
2. 在 `codex/release-0.4.1` 的本地续接分支重做任务 5 最终独立复核；
3. 完成通用版任务 6；
4. 与用户协调 Windows 11 可见浏览器的人工 WebVPN 验证；
5. 完成通用版 PR、CI、合并、标签、Release、附件复核和安装；
6. 更新环境版工作树到通用版最新 `main`；
7. 阅读环境版计划；
8. 严格按测试先行方式逐项执行环境版任务 1 至任务 5；
9. 每项任务完成后独立复核，不把全部问题留到最后；
10. 完成环境版任务 6；
11. 与用户完成两个环境分组的人工验证；
12. 创建独立环境版标签和 Release；
13. 验证通用版与环境版在 ChatGPT Desktop 中共存。

## 16. 提交和发布纪律

- 每个任务形成可独立回退的提交；
- 审查修正单独提交；
- 修复缺陷前先补充失败测试；
- Skill 源码和 MCPB 源码必须同步；
- 新模块必须同步进入 manifest、构建白名单和归档测试；
- 不提交 ZIP、MCPB、浏览器状态、缓存、Cookie、HTML 或本地路径；
- 不提交真实 WebVPN 地址；
- 不在真实 E2E 通过前创建正式标签；
- 不从开发机临时构建结果创建正式 Release；
- 通用版和环境版使用不同标签、不同 Release 和不同附件；
- 发布后必须重新下载附件，复核 SHA-256 和包内版本；
- 安装验证必须使用 Release 附件，不使用工作树源码。

## 17. 完成标准

### 17.1 通用版 v0.4.1

只有全部满足以下条件，才能宣布完成：

- 任务 5 第三轮修正通过独立复核；
- ruff、mypy 和全量 pytest 通过；
- 目录校验和三类 MCP 握手通过；
- 两次构建逐字节一致；
- 归档内容符合安全边界；
- Windows 隔离安装器验证通过；
- 两个通用版 WebVPN 分组真实检索通过；
- PR 审查和主分支 CI 通过；
- v0.4.1 标签未覆盖旧标签；
- 正式附件来自 Ubuntu Python 3.11；
- 重新下载、哈希和包内版本复核通过；
- ChatGPT Desktop 从正式附件安装并验证两个工具。

### 17.2 环境版 v0.2.0

只有全部满足以下条件，才能宣布完成：

- 环境版 7 项计划任务全部完成；
- 环境目录数量和十级判级不回归；
- 两个环境分组真实检索通过；
- 通用版与环境版可同时安装和运行；
- 环境版独立 CI、标签、Release 和附件通过；
- 重新下载、哈希和包内版本复核通过；
- ChatGPT Desktop 中两个 MCP 服务和四个工具同时可见。

## 18. 当前明确禁止的完成表述

在剩余门槛完成前，不得表述：

- v0.4.1 已发布；
- v0.4.1 已可用于生产；
- 环境版 v0.2.0 已实现；
- WebVPN 专业检索已经真实验证；
- 两个版本已经在 ChatGPT Desktop 共存；
- 当前测试结果已经等同于完整发布验收。

准确表述应为：

> 通用版 v0.4.1 的任务 1 至任务 5 已完成代码实现和多轮修正，当前提交的全量 pytest 已通过；任务 5 最后一轮独立复核、发布级自动化验证、真实 WebVPN 验证和正式发布尚未完成。环境版 v0.2.0 只有经确认的设计和实施计划，生产代码尚未开始。
