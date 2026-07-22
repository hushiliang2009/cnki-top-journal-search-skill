---
name: top-journal-search-lists
description: Use when the user asks to search, review, organize, or summarize literature with emphasis on top journals, journal rankings, CNKI, 中国知网, CSSCI, SSCI, SCIE, NCS, PNAS, UTD24, FT50, Google Scholar, Semantic Scholar, PubMed, or ai4scholar MCP.
---

# Top Journal Search Lists

## 核心原则

读取本 Skill 自带的 `references/Academic_Journal_Master_Directory_20260715.md`，调用 ai4scholar MCP 全面检索；需要中文期刊文献时，按 `references/cnki-search-reference.md` 调用本地 CNKI 浏览器 MCP。检索先后和结果排序必须遵循目录中的十级配置。不得在前几个层级无结果时提前结束，也不得将宽口径搜索结果直接认定为顶刊论文。

## 检索顺序

1. 经济学 Top 5
2. NCS_PNAS，其中人文、哲学与社会科学（含交叉研究）期刊优先
3. UTD24
4. FT50
5. Field Top
6. 中文顶尖期刊
7. Top 目录中的其他顶尖期刊
8. SSCI
9. CSSCI
10. SCIE

同一期刊属于多个层级时采用最高层级。最终结果先按 `priority_level` 升序排列；`priority_level=2` 时，再按 `ncs_internal_rank` 升序排列。NCS_PNAS 期刊同时记录并在输出中展示 `ncs_internal_rank`，数值 1 表示人文社科交叉优先组，数值 2 表示其他 NCS_PNAS 期刊。

## 执行流程

1. 明确主题、年份、语言和数量。用户未指定时，使用中英文关键词，不限定起始年份，重点关注近五年并保留经典文献。
2. 定位当前 `SKILL.md` 所在目录，将其作为 Skill 根目录。使用系统中可用的 Python 3 解释器，在 Skill 根目录运行目录校验：

```text
python scripts/catalog_lookup.py validate
```

若系统使用 `python3` 或 `py -3` 启动 Python，则替换命令中的 `python`。脚本默认读取 Skill 内的综合目录；只有用户明确使用其他目录文件时才通过 `--catalog` 指定路径。校验失败时停止层级判定并报告错误。

3. 构造中文关键词、英文关键词、同义词、理论词和方法词，保留实际使用的检索式。
4. 依次定向检索经济学 Top 5、NCS_PNAS、UTD24、FT50、Field Top、中文顶刊和其他 Top 期刊。根据主题从各组选择相关期刊，并在查询中加入期刊正式名称；返回后再次核验期刊字段。
5. 使用 `mcp__ai4scholar__search_google_scholar` 和 `mcp__ai4scholar__search_semantic` 执行宽口径补充检索。医学、健康和生命科学主题补充 `mcp__ai4scholar__search_pubmed`。
6. 对高相关种子论文按需调用 `mcp__ai4scholar__get_semantic_references`、`mcp__ai4scholar__get_semantic_citations` 和 `mcp__ai4scholar__get_semantic_recommendations_for_paper` 扩展文献网络。
7. 合并元数据，优先依据 DOI 去重；无 DOI 时使用规范化题名、作者和年份。保留信息最完整的记录。
8. 将候选期刊交给目录脚本判定最高层级：

```text
python scripts/catalog_lookup.py lookup "Journal A" "Journal B"
```

9. 按期刊层级、主题相关性、年份和工具返回的引用信息整理。每个无结果层级也必须报告。

## CNKI 执行规则

需要中国知网中文文献、CSSCI 定向检索或用户明确指定 CNKI 时，优先调用本地 CNKI MCP。以高级检索和专业检索为主要方式；作者发文检索和句子检索只作补充。执行前读取 `references/cnki-search-reference.md`。

1. 先调用 `cnki_status`。只有用户要求启动知网会话时才调用 `cnki_login`。
2. 登录完全由用户在可见浏览器的河海大学 WebVPN 页面手工完成。不得接收或记录账号、密码、短信码和验证码。
3. 会话只保存在当前浏览器进程内的临时浏览器会话中，不持久化 Cookie，不读取或复用其他浏览器配置，不创建持久化用户目录。
4. 高级检索和专业检索均只使用新版 `kns8s/AdvSearch` 页面。WebVPN 会话使用河海大学代理入口 `https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch`；知网直接会话使用 `https://kns.cnki.net/kns8s/AdvSearch`。按当前会话主机选择入口，不固定 `wrdrecordvisit`，不提供其他入口或回退模式。
5. 高级检索使用新版字段化表单；专业检索在同一新版页面切换标签，按用户确认的表达式原样填入，提交前校验字段代码、引号和括号。
6. 始终低频串行操作。检索默认 1 页、最多 3 页，每页间隔 4 至 7 秒；详情最多 10 条，每条间隔 3 至 6 秒；下载最多 5 篇，每篇间隔 8 至 15 秒。
7. 遇到验证码、403、429、权限不足或会话失效时立即停止，并要求用户在可见浏览器中处理。不得自动重试或切换代理规避限制。
8. 先返回检索结果并编号。只有用户明确选择具体编号、确认具有访问权限、指定保存目录，并将 `access_confirmed` 设为 `true` 后，才调用 `cnki_download`；只使用当前页面中的知网官方全文按钮，不得构造隐藏下载链接。下载返回的下载元数据包括文件路径、文件大小和 SHA-256，用于核验实际保存结果。
9. 使用 DOI 优先去重，无 DOI 时使用题名、第一作者和年份。随后调用内置综合目录附加最高期刊层级。
10. 按需调用 `cnki_export` 同时生成 JSON、UTF-8 BOM CSV、BibTeX、RIS 和 GB/T 7714 文本。
11. 完成任务后调用 `cnki_close_session`，清除当前内存会话。

CNKI 负责知网授权范围内的中文文献和精确字段检索；ai4scholar 负责 Google Scholar、Semantic Scholar、PubMed 及引文扩展。两类来源分别记录，不以 ai4scholar 的空结果判断 CNKI 无文献，也不把 CNKI 权限失败当作检索结果为空。

### CNKI MCP 工具

| 工具 | 用途 |
|---|---|
| `cnki_status` | 检查会话状态，不自动打开浏览器 |
| `cnki_login` | 打开可见 WebVPN 登录页，等待用户手工登录 |
| `cnki_search` | 执行高级检索或专业检索 |
| `cnki_fetch_details` | 串行读取用户指定的最多 10 条详情 |
| `cnki_export` | 导出五种结构化或引文格式 |
| `cnki_download` | 下载用户明确选择的最多 5 篇全文 |
| `cnki_close_session` | 关闭浏览器并清除内存会话 |

## ai4scholar 工具选择

| 检索情形 | 使用工具 |
|---|---|
| 综合学术检索与年份筛选 | `mcp__ai4scholar__search_google_scholar` |
| 结构化补充检索 | `mcp__ai4scholar__search_semantic` |
| 医学、健康和生命科学 | `mcp__ai4scholar__search_pubmed` |
| 关键论文的参考文献和被引扩展 | `mcp__ai4scholar__get_semantic_references`、`mcp__ai4scholar__get_semantic_citations` |
| 基于种子论文查找相似研究 | `mcp__ai4scholar__get_semantic_recommendations_for_paper` |

只在用户明确要求下载或阅读全文时调用下载和全文读取工具。

## 输出契约

按以下顺序输出：

1. 检索范围：主题、关键词、年份、语言、检索日期和使用的数据库。
2. 主要结论：概括研究共识、分歧和证据缺口。
3. 分层论文目录：按十级顺序列出；第二级内部按 `ncs_internal_rank` 升序排列并展示该字段；无结果层级写明未检出符合条件的论文。
4. 文献综合：归纳理论、数据、方法、作用机制、边界条件和研究不足。
5. 检索说明：列出检索式、去重口径、未覆盖范围和元数据缺失。

每篇论文尽量包含题名、作者、年份、期刊正式名称、检索层级、来源目录、DOI 或稳定链接、主题相关性、研究发现、数据与方法。第二级论文还必须展示 `ncs_internal_rank`。引用次数仅在工具返回时报告。

第七级没有独立记录时，必须明确报告第七级为空层级，不得伪造期刊，也不得从其他层级复制记录填充。

## 证据要求

- 不依据题名推测研究结论；摘要不足时只说明可核实的信息。
- 不补造 DOI、期刊归属、作者、年份、引用次数或稳定链接。
- 搜索结果中的期刊名称必须通过目录脚本复核；未匹配期刊标记为未匹配，不自行指定层级。
- 同一论文在多个来源中出现时只列一次，并保留最高期刊层级和完整来源信息。

## 常见错误

| 错误 | 正确处理 |
|---|---|
| 只检索 Top 5 或 NCS 后结束 | 继续执行剩余层级并报告空层级 |
| 将 CSSCI 排在 SSCI 前 | SSCI 为第八级，CSSCI 为第九级 |
| 将宽口径结果直接视为顶刊论文 | 先运行目录匹配脚本 |
| 按来源重复列出同一论文 | DOI 优先去重并保留最高层级 |
| 工具未返回摘要却概括结论 | 标记摘要缺失，只报告已核实信息 |
| 第七级无独立记录却填入其他期刊 | 明确报告空层级，不得伪造期刊 |

## 异常处理

- Skill 内置综合目录不存在：停止层级判定，报告 `references/Academic_Journal_Master_Directory_20260715.md` 的实际缺失路径。
- 综合目录结构校验失败：报告无效层级或来源区块，不沿用推测顺序。
- ai4scholar MCP 不可用：报告具体工具错误，不以普通网络搜索冒充 MCP 检索。
- CNKI MCP 不可用：报告本地启动或依赖错误，不改用未经用户同意的网页抓取。
- CNKI 出现验证码、403、429、权限不足或会话失效：立即停止当前操作，保留已取得结果，说明需要用户处理的页面状态。
- 某层级无结果：保留空结果说明并继续后续层级。
- 第七级无独立记录：明确报告第七级为空层级，不得伪造期刊或挪用其他层级记录。
- 元数据不完整：标记缺失字段，不自行补造。
