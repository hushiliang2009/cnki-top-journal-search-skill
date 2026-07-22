# CNKI 检索 Skill 跨客户端设计

## 1. 目标

在现有 `top-journal-search-lists` Skill 中增加中国知网检索、结果整理、引文导出和授权下载能力，并以同一套 Python 核心服务于 Claude Code、Claude Desktop、Codex CLI 和 Codex Desktop。支持 Windows、Linux 和 macOS；本机只对 Windows 做真实登录与浏览器冒烟测试，其他系统通过安装脚本、路径和浏览器适配测试验证。

核心约束如下：

- 使用 Python 3.11 及以上版本、Playwright 可见浏览器和本地 stdio MCP。
- 用户在河海大学 WebVPN 页面手工输入密码和验证码。
- 不接收、记录或持久化账号、密码、验证码和 cookies。
- 不使用无头浏览器、隐身插件、代理轮换、Tor、Sci-Hub、LibGen 或反检测技术。
- 遇到验证码、HTTP 403、HTTP 429、权限不足或会话失效时立即停止。
- 下载只通过知网页面可见的官方按钮，并且只下载用户明确选择的条目。
- `cnki-search-skill-main.zip` 无开源许可证，仅作为行为和测试参考，不复制其源码、提示词或文档。

## 2. 已核验输入

| 文件 | SHA-256 | 结论 |
|---|---|---|
| `top-journal-search-lists_Skill.zip` | `87D0168D1A81CFEE5943EE631E3CA4337332766D30501426397BE24CFD71436E` | 目录自包含，十个等级，17 项测试通过 |
| `cnki-search-skill-main.zip` | `37857055F4B9B700CB8284C61EC343B6D1EBCFB96D692A533E3614BE77BF0B1B` | 73 项测试通过，无开源许可证 |
| `scansci-pdf-master.zip` | `7C6CD6694DA87D89080F2917065493FC61734C37AB6C3CB1039EC2490247B47B` | Apache-2.0，含河海大学 WebVPN 配置和 stdio MCP 参考 |

本机 ai4scholar 的 Google Scholar 与 Semantic Scholar 工具均完成真实检索并返回结构化结果。中文限定查询可能为空，因此 CNKI 是中文文献检索的必要补充，而不是 ai4scholar 的替代品。

## 3. ScanSci 浏览器状态审计

压缩包共 195 个条目，其中 165 个为文件。浏览器状态相关文件共 28 个，已经逐字节读取和解析。

### 3.1 结构化状态

- `Last Browser` 指向 CloakBrowser Chromium 146 的 Windows 可执行文件。
- `Last Version` 为 `146.0.7680.177`。
- `Local State` 包含浏览器版本、默认空账户资料、匿名度量标识、设备统计快照和 DPAPI 加密密钥封装。
- `Variations` 记录浏览器上次未正常退出，连续崩溃次数为 0。
- 两个 CRX 缓存的 `metadata.json` 均为空哈希表。
- `BrowserMetrics-spare.pma` 为 4 MiB 全零文件。

`Local State` 中的 DPAPI 数据只做 Base64 解码、格式识别和哈希核验，不调用系统解密接口，因为 ZIP 中不存在 Cookie 数据库，也不需要恢复浏览器会话。

### 3.2 GPU 缓存

`GrShaderCache`、`GraphiteDawnCache` 和 `ShaderCache` 均采用 Chromium blockfile 格式：

- block magic 为 `0xC104CAC3`，索引 magic 为 `0xC103CAC3`。
- `GrShaderCache` 有 76 个有效索引项、76 个不同键、76 个数据流，共 928,240 字节。
- 74 个数据流哈希不同，内容为 ANGLE、Skia 生成的 HLSL 源码及 DXBC 字节码。
- GPU 标识为 AMD Radeon 780M，驱动版本为 `32.0.21036.18`。
- 其余两个缓存只有空索引和初始化块，没有有效 shader 记录。
- 全部缓存未发现 URL、邮箱、CNKI、WebVPN、登录、Cookie、DOI 或访问历史。

压缩包不存在 Chromium 的 `Default` 用户目录，也不存在 Cookies、History、Preferences、Login Data、Web Data、Sessions、Local Storage、Session Storage 或 IndexedDB。

因此，这些文件不会复制到最终 Skill、MCPB 或安装目录。

## 4. 体系结构

```text
Claude Code ─┐
Claude Desktop ─┤
Codex CLI ──────┼─ stdio MCP ─ CNKI Core ─ visible Playwright browser ─ HHU WebVPN ─ CNKI
Codex Desktop ──┘                    │
                                     ├─ result normalization and export
                                     └─ top-journal catalog lookup
```

所有客户端调用同一个本地 MCP。MCP 不开放监听端口，也不提供远程 HTTP 服务。浏览器上下文、cookies 和页面对象仅存在于 MCP 进程内存中；关闭会话或进程后全部释放。

## 5. 包结构

```text
top-journal-search-lists/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── Academic_Journal_Master_Directory_20260715.md
│   └── cnki-search-reference.md
├── scripts/
│   ├── catalog_lookup.py
│   └── cnki_search/
│       ├── __init__.py
│       ├── models.py
│       ├── fields.py
│       ├── syntax.py
│       ├── rate_limit.py
│       ├── session.py
│       ├── browser.py
│       ├── search.py
│       ├── results.py
│       ├── details.py
│       ├── exporters.py
│       ├── downloads.py
│       ├── mcp_server.py
│       └── cli.py
├── mcpb/
│   ├── manifest.json
│   └── pyproject.toml
├── installers/
│   ├── install.ps1
│   └── install.sh
└── tests/
```

用户明确要求交付 `README.md`，因此本项目保留用户说明文件。`SKILL.md` 只保留触发条件、操作顺序和必要约束，详细字段、安装和故障说明放入 README 与 reference。

## 6. 会话状态

状态枚举为：

- `login_required`
- `waiting_for_user`
- `ready`
- `captcha`
- `permission_denied`
- `rate_limited`
- `session_expired`
- `closed`

`cnki_login` 打开可见浏览器并进入河海大学 WebVPN 登录入口。工具返回 `waiting_for_user` 后停止操作，由用户完成认证。`cnki_status` 只根据公开 URL、页面标题和非敏感页面元素判断状态，不读取输入框内容。

## 7. 检索

### 7.1 高级检索

支持主题、篇关摘、关键词、题名、全文、作者、第一作者、通讯作者、作者单位、摘要、基金、来源期刊、参考文献、中图分类号、ISSN、CN、DOI 和栏目。支持逻辑关系、精确或模糊匹配、年份、来源类别、基金和附件所示扩展选项。

字段由稳定业务名称映射到当前页面元素。选择器集中维护，采用标签、角色和附近文本优先，CSS 选择器作为回退。页面结构变化时返回 `page_changed` 诊断，不盲目点击。

### 7.2 专业检索

专业表达式原样输入页面。执行前只检查括号配对、引号配对、字段代码和明显空表达式；不改变布尔关系、词语或字段。

### 7.3 作者与句子检索

作者发文和句子检索作为次要模式，复用同一状态、限流、结果和导出模型。首版验收重点仍为高级检索和专业检索。

## 8. 限流与缓存

- 搜索默认读取 1 页，单次最多 3 页，翻页间隔随机 4 至 7 秒。
- 详情串行读取，单次最多 10 条，间隔随机 3 至 6 秒。
- 下载串行执行，单次最多 5 条，间隔随机 8 至 15 秒。
- 同一调用不并发打开搜索页、详情页或下载任务。
- 验证码、403、429 不自动重试。
- 页面结构变化最多重新定位一次；失败后返回诊断。
- 缓存只保存规范化元数据、检索式摘要、检索时间和来源，不保存页面 HTML、cookies、令牌或凭据。

## 9. 结果与导出

统一结果模型包含：题名、作者、第一作者、机构、期刊、年份、卷期、页码、摘要、关键词、基金、DOI、CNKI 详情链接、来源模式、检索时间和下载状态。

导出格式：

- JSON
- CSV UTF-8 BOM
- BibTeX
- RIS
- GB/T 7714 文本

去重优先使用 DOI；缺少 DOI 时使用规范化题名、第一作者和年份。期刊等级必须由 `catalog_lookup.py` 返回，不在目录中的期刊标记为未收录。

## 10. 下载

`cnki_download` 接收用户明确选择的结果标识。浏览器在详情页点击当前可见的官方 PDF 或 CAJ 下载按钮。写入前检查：

- 下载事件确由当前页面触发。
- Content-Type、扩展名和文件头一致。
- PDF 以 `%PDF-` 开头；CAJ 使用已知 CAJ 文件头。
- 文件名经过 Windows、Linux 和 macOS 安全化。
- 目标存在时默认不覆盖，改用递增序号。

登录页、验证码页、HTML 错误页和权限提示不得保存为论文文件。

## 11. MCP 工具

- `cnki_status`
- `cnki_login`
- `cnki_search`
- `cnki_fetch_details`
- `cnki_export`
- `cnki_download`
- `cnki_close_session`

所有工具返回统一结构：`ok`、`status`、`message`、`data`、`warnings` 和 `next_action`。MCP 初始化说明的前 512 个字符明确写入手工登录、低频串行、风控停止和禁止持久化会话的规则。

## 12. 客户端封装

- Claude Code 使用用户级 stdio MCP，并安装合并 Skill 到 `~/.claude/skills/top-journal-search-lists`。
- Claude Desktop 优先安装 `.mcpb`。MCPB 使用 `server.type = uv` 和锁定依赖；macOS 与 Windows 可一键安装。Linux 如客户端未实现 MCPB，则使用同一 stdio 命令配置。
- Codex CLI 将 Skill 安装到 `$CODEX_HOME/skills`，默认 `~/.codex/skills`，并注册 stdio MCP。
- Codex Desktop 与同一主机上的 Codex CLI 共用 MCP 配置。

安装器只做增量配置。修改前备份，遇到同名服务器先比较，不覆盖其他配置。安装后执行 MCP 握手和 `cnki_status`，不自动启动登录。

## 13. 与 top-journal-search-lists 合并

- 现有十级目录继续作为唯一等级依据。
- ai4scholar 继续检索英文论文和开放元数据。
- CNKI 重点补充第 6 级中文顶刊、第 9 级 CSSCI 和其他中文期刊。
- CNKI 不可用时继续交付 ai4scholar 结果，并明确列出中文检索缺口。
- 合并结果保留来源、检索式、检索时间和期刊等级依据。

## 14. 交付与验收

最终交付：

- `top-journal-search-lists_Skill.zip`
- `cnki-search.mcpb`
- `install.ps1`
- `install.sh`
- `checksums.sha256`

验收要求：

1. 原 17 项目录测试继续通过。
2. 新代码严格执行测试先行，每项生产行为先出现预期失败，再写最小实现。
3. 使用本地 HTML 固件验证高级检索、专业检索、结果解析和风控分类。
4. MCP 工具模式、返回结构和初始化说明通过测试。
5. Windows 实机完成手工登录、两种检索、一条详情、五种导出和一次授权下载。
6. Linux 与 macOS 完成路径、安装脚本、浏览器发现和配置生成测试，不冒充实机登录测试。
7. 覆盖目标 ZIP 前先备份并校验原哈希，打包后重新从 ZIP 安装和测试。

## 15. Windows 实施记录

2026 年 7 月 21 日在本机完成以下验证：

- 高级检索以主题精确检索数字化转型 企业创新，单页返回 20 条结果。
- 专业检索原样提交 `SU='数字化转型' AND KY='企业创新'`，单页返回 20 条结果。
- 详情页通过结果题名链接打开，不直接构造详情网址；真实页面可解析题名、作者、机构、期刊、年份、期号、页码、摘要、关键词和基金。页面未提供 DOI 时保留空值。
- 专业检索结果已导出 JSON、CSV、BibTeX、RIS 和 GB/T 7714 文本。
- 完整测试为 74 项，通过独立解压复测；Skill 与 MCPB 清单验证通过，已安装 MCP 握手返回 7 个工具。
- ai4scholar 的 Semantic Scholar 检索仍可返回有效论文与 DOI，CNKI 与 ai4scholar 的分工保持不变。
- 真实论文下载尚未执行。下载必须等待用户明确指定结果序号，不能由程序代选。
