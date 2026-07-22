---
name: top-journal-search-lists
description: Use when the user asks to search, review, organize, or summarize literature with emphasis on top journals, journal rankings, Chinese papers, CNKI, CSSCI, SSCI, SCIE, Google Scholar, Semantic Scholar, PubMed, or ai4scholar MCP.
---

# Top Journal Search Lists

## 核心原则

ai4scholar 是中英文文献检索的主要来源。CNKI 仅作为近期中文论文的补充来源，用于公开首页主题检索。所有期刊判级均以 `references/Academic_Journal_Master_Directory_20260715.md` 为准，目录版本为 2026-07-15。

CNKI 只使用公开首页、固定主题检索和第一页结果。单次 `limit` 为 1 至 20。程序不登录、不下载、不持久化 Cookie，不持久化缓存，运行期仅24小时内存缓存；不使用用户浏览器配置文件，也不访问结果的详情页面。

## 执行方法

1. 明确主题、年份、语言和数量。未指定时，以近五年为重点，并保留必要的经典研究。
2. 在 Skill 根目录校验目录：

```text
python scripts/catalog_lookup.py validate
```

3. 以 ai4scholar 为主要来源，调用 Google Scholar 和 Semantic Scholar；医学、健康和生命科学主题补充 PubMed。对关键论文可根据需要扩展参考文献、被引文献和相似论文。
4. 用户需要中文论文、近期中文研究或明确要求 CNKI 补充时，只调用 `cnki_search(query, limit)`。它从 CNKI 公开首页按主题检索，仅读取第一页，最多返回 20 条期刊记录。
5. 正式结果必须具有篇名、期刊和发表年度；信息不完整的记录只说明缺失项，不作为正式候选。每条记录保留 `sources`，标明 ai4scholar 或 CNKI。
6. 使用目录脚本核验期刊并按十级顺序排列：

```text
python scripts/catalog_lookup.py lookup "Journal A" "Journal B"
```

7. 同一论文优先按 DOI 去重；没有 DOI 时按规范化篇名、作者和年度去重。保留较完整的元数据和全部 `sources`。

## 期刊排序与目录例外

结果按十级期刊层级排序；第二级内部按 `ncs_internal_rank` 升序排列。第七级没有独立记录时，应明确标记为空层级，不得伪造期刊，也不得从其他层级补入记录。用户明确提供其他目录文件时，才在目录命令中使用 `--catalog` 指定该文件。

## CNKI 公开检索边界

- 入口固定为 `https://www.cnki.net/`，字段固定为主题检索。
- 只读取第一页，结果最多 20 条。
- 出现验证码、登录页、401、403、429 或页面结构变化时立即停止，保留已获得的公开信息并报告原因。
- 不使用替代入口、代理、机构认证、内部接口或浏览器历史状态。
- 用户如需全文，应根据篇名、期刊和发表年度自行前往合法渠道下载；本 Skill 不提供下载功能。

## ai4scholar 工具选择

| 检索情形 | 使用工具 |
|---|---|
| 综合学术检索与年份筛选 | `mcp__ai4scholar__search_google_scholar` |
| 结构化补充检索 | `mcp__ai4scholar__search_semantic` |
| 医学、健康和生命科学 | `mcp__ai4scholar__search_pubmed` |
| 扩展关键论文的参考文献和被引文献 | `mcp__ai4scholar__get_semantic_references`、`mcp__ai4scholar__get_semantic_citations` |
| 查找相似研究 | `mcp__ai4scholar__get_semantic_recommendations_for_paper` |

## 输出契约

按以下顺序报告：

1. 检索范围，包括主题、关键词、年份、语言、日期和 `sources`。
2. 分层论文目录。每篇正式记录包含篇名、期刊、发表年度、期刊层级和 `sources`。
3. 文献综合，仅概括可由题录、摘要或工具返回内容核实的信息。
4. 检索说明，包括检索式、去重口径、空层级、未覆盖范围和元数据缺失。

不依据题名推测研究结论，不补造 DOI、作者、期刊、年度、引用次数或链接。未匹配期刊标记为未匹配，不自行指定层级。
