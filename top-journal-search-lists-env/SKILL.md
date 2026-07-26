---
name: top-journal-search-lists-env
description: Use when the user asks to search, review, organize, or synthesize literature on environmental science, ecology, environmental chemistry, environmental engineering, climate, oceans, soil, environmental health, environmental economics, environmental management, environmental law, sustainability, pollution control, or related interdisciplinary environmental topics.
---

# Top Environmental Journal Search

## 核心原则

以 ai4scholar 为主要来源，以 `cnki_search_env(query, limit)` 作为近期中文
期刊论文的补充来源。期刊判级只能依据
`references/环境科学与工程学科顶尖期刊目录_v3.0.md`，目录版本为 3.0，
日期为 2026-07-26。

普通检索不得全文加载约 408 KB 的目录。先运行目录脚本，再按查询结果判级：

```text
python scripts/catalog_lookup.py validate
python scripts/catalog_lookup.py lookup "Journal A" "Journal B"
```

仅在目录审计、更新或来源核验任务中读取完整参考文件。非环境主题，例如
公司金融与董事会治理，应改用通用期刊检索 Skill，不触发本 Skill。

## 检索方法

1. 明确主题、年份、语言和数量。未指定时，以近五年为重点，并保留必要的经典
   研究。
2. 校验目录。校验失败时停止判级并报告原因，不得改用通用目录代替。
3. 用 `mcp__ai4scholar__search_google_scholar` 完成综合检索，用
   `mcp__ai4scholar__search_semantic` 补充结构化元数据。对关键论文使用
   `mcp__ai4scholar__get_semantic_references`、
   `mcp__ai4scholar__get_semantic_citations` 和
   `mcp__ai4scholar__get_semantic_recommendations_for_paper` 扩展文献。
4. 环境健康、暴露科学、毒理学和环境医学主题补充
   `mcp__ai4scholar__search_pubmed`。
5. 需要中文论文、近期中国研究或用户明确要求 CNKI 时，调用
   `cnki_search_env(query, limit)`。该工具只执行公开首页主题检索，读取第一页，
   `limit` 为 1 至 20。
6. 正式候选必须具有篇名、期刊和发表年度。先按 DOI 去重；无 DOI 时按规范化
   篇名、作者和年度去重，保留元数据更完整的记录及全部 `sources`。
7. 批量查询正式期刊名，按 `priority_level` 升序排列。第二级内部再按
   `ncs_internal_rank` 升序排列。未匹配或歧义结果保持
   `manual_review_required=true`，不得自行赋级。

## 十级顺序

| 层级 | `priority_group` |
|---:|---|
| 1 | `comprehensive_super_journals` |
| 2 | `ncs_pnas_environment_flagships` |
| 3 | `top_university_highest_consensus` |
| 4 | `top_university_high_level` |
| 5 | `environment_field_top` |
| 6 | `chinese_environment_top` |
| 7 | `other_formally_recognized` |
| 8 | `environment_ssci` |
| 9 | `environment_cssci` |
| 10 | `environment_scie` |

同一期刊只采用最高层级。不得把 SCIE 分类附录或 v2.0 处置记录当作主目录记录。
期刊判级结果须保留 `matched_title`、`priority_level`、`priority_group`、
`environment_subfields`、`subject_categories`、`formal_evidence`、
`index_memberships`、`source_catalogs`、`ncs_internal_rank`、
`catalog_version`、`catalog_date` 和 `manual_review_required`。

## CNKI 公开检索边界

- 固定使用 `https://www.cnki.net/` 公开首页和主题字段，只读取第一页。
- 不登录、不下载、不持久化 Cookie，不持久化缓存，运行期仅24小时内存缓存。
- 不使用用户浏览器配置、代理、替代入口、机构认证或内部接口。
- 遇到 `challenge_detected`、登录页、401、403、429或页面结构变化时立即停止；
  不刷新重试，不切换代理或浏览器状态，不规避安全检测。
- CNKI 受阻不等于没有中文文献。继续使用 ai4scholar，并如实说明中文近期文献
  可能覆盖不足。

## 输出契约

严格按以下顺序报告：

1. 检索范围：主题、检索式、年份、语言、检索日期和 `sources`。
2. 按十级目录整理的论文：篇名、作者、年度、正式期刊名、DOI或稳定链接、
   期刊层级和来源。
3. 环境细分领域及正式证据：列出 `environment_subfields`、
   `formal_evidence`、`index_memberships` 和 `source_catalogs`。
4. 文献综合：只概括题录、摘要或工具结果能够核实的信息。
5. 检索限制与未匹配记录：说明空层级、去重口径、元数据缺失、CNKI状态、
   歧义和未匹配期刊。

不得根据题名推测结论，不得补造 DOI、作者、期刊、年度、引用次数、链接、
数据库收录或正式证据。
