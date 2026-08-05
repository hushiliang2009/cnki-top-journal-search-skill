---
name: top-journal-search-lists-env
description: Use when the user asks to search, review, organize, or synthesize literature on environmental science, ecology, environmental chemistry, environmental engineering, climate, oceans, soil, environmental health, environmental economics, environmental management, environmental law, sustainability, pollution control, or related interdisciplinary environmental topics.
---

# Top Environmental Journal Search

## 核心原则

以 ai4scholar 为主要来源，以 `cnki_search_env(query, limit)` 作为近期中文
期刊论文的补充来源。期刊判级只能依据
`references/环境科学与工程学科顶尖期刊目录_v4.0.md`，目录版本为 4.0，
日期为 2026-07-29，修订日期为 2026-07-31。

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
6. 用户已启用 WebVPN 人工值守模式，且需要按中文环境顶尖期刊、其他正式认可
   中文期刊、环境 CSSCI 或北大核心定向查证时，才调用
   `cnki_professional_search_env(topic, group, limit,
   year_from, year_to)`。启用前必须告知：需要本人登录、浏览器窗口全程打开、
   中途可能需要人工完成安全验证。返回值中的 `human_intervention_required`
   与 `complete` 必须如实转述；`complete` 为假时不得把结果当作该主题的完整
   中文文献。
7. 正式候选必须具有篇名、期刊和发表年度。先按 DOI 去重；无 DOI 时按规范化
   篇名、作者和年度去重，保留元数据更完整的记录及全部 `sources`。
8. 批量查询正式期刊名，按 `priority_level` 升序排列。第二级内部再按
   `ncs_internal_rank` 升序排列。未匹配或歧义结果保持
   `manual_review_required=true`，不得自行赋级。

## 十二级顺序

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
| 11 | `pku_core_natural_sciences` |
| 12 | `pku_core_non_natural_sciences` |

同一期刊只采用最高层级。不得把 SCIE 分类附录或 v2.0 处置记录当作主目录记录。
期刊判级结果须保留 `matched_title`、`priority_level`、`priority_group`、
`environment_subfields`、`subject_categories`、`formal_evidence`、
`index_memberships`、`source_catalogs`、`ncs_internal_rank`、
`catalog_version`、`catalog_date` 和 `manual_review_required`。

用户质疑某本期刊的层级、或要求核实目录来源时，不要凭记忆解释判级理由。逐刊判级证据
应引用目录记录里的 `formal_evidence` 和 `source_catalogs`。需要核验目录整体未被篡改时，
运行 `python scripts/generate_environment_catalog_v4.py --check`：它据七份来源快照重算
层级与来源匹配，并与随包产物逐字节比对，一致则退出码为 0。该校验覆盖层级与镜像，不构成
对期刊清单本身的独立重建。发布包内不含 `docs/audits/` 的逐条匹配审计，该模式下会打印
`docs/audits: skipped`；仓库检出中则一并校验。

## CNKI 公开检索边界

- 固定使用 `https://www.cnki.net/` 公开首页和主题字段，只读取第一页。
- 不登录、不下载、不持久化 Cookie，不持久化缓存，运行期仅24小时内存缓存。
- 不使用用户浏览器配置、代理、替代入口、机构认证或内部接口。
- 遇到 `challenge_detected`、登录页、401、403、429或页面结构变化时立即停止；
  不刷新重试，不切换代理或浏览器状态，不规避安全检测。
- CNKI 受阻不等于没有中文文献。继续使用 ai4scholar，并如实说明中文近期文献
  可能覆盖不足。

## WebVPN 人工值守专业检索（可选，须显式启用）

由使用者本人以校园账号、经所在机构官方 WebVPN 完成统一身份认证后，使用知网
专业检索按环境期刊目录定向检索中文期刊论文。这属于**机构授权**的正常访问
路径，与检测规避有本质区别。底线不随模式改变：**不伪造** User-Agent、
**不轮换代理**、不抹除自动化标志、**不自动破解**验证码。

启用时只设置 `CNKI_ENV_WEBVPN_HOME`，其值为所在机构 WebVPN 改写后的知网首页
地址。该变量与通用版的 `CNKI_WEBVPN_HOME` 相互独立，设一个不会把另一个产品
一起打开。运行时使用**非持久化**浏览器上下文，不保存 Cookie、登录票据或
浏览器 profile；**服务重启后需要重新登录**。

该模式**必须人工值守，不可用于定时任务**或任何无人参与的场景。三处人工介入
无法自动化：

1. 统一身份认证需要校园账号密码，程序不接触凭据；
2. WebVPN 票据是 session cookie，导出后在新浏览器进程会被服务端拒绝，因此
   登录与检索必须同进程、浏览器窗口全程打开；
3. 中途触发安全验证时需要人工滑动。

请求携带使用者的实名机构身份，所在机构的使用规范与频率限制均适用。默认请求
间隔 30 秒。

覆盖范围是四个受控范围，刊名与刊数一律取自本 Skill 的环境期刊目录：

| `group` | 层级 | 期刊数 | 构造方式 |
|---|---:|---:|---|
| `chinese_environment_top` | 6 | 6 本 | `LY=` **精确**枚举刊名，单批完成 |
| `other_formally_recognized_chinese` | 7（中文） | 60 本 | `LY=` 精确枚举，中文集合由目录构建期固化 |
| `environment_cssci` | 9 | 241 本 | `LY=` 精确枚举 + 按表达式长度分批，每批附结果页「来源类别」= CSSCI（`P0209`） |
| `pku_core` | 11—12（成员横跨 1—12 级） | 1987 本 | 只提交主题与年份表达式，勾选结果页「来源类别」= 北大核心（`P01`），**不生成 `LY=`** |

⚠ 1987 是 v4.0 全部北大核心成员数，其中 1742 本位于第11—12级，其余 245 本已在更高
层级出现。因此 `pku_core` 的合格层级是 **1—12 级**，一条第6级期刊的记录在该组里
同样合格，命中后按目录层级排序归位——不要以为该组只会返回第11—12级的期刊。

完整环境工作流按 **第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心** 的
顺序依次检索；跨组总量只计算全局去重后的新增论文。**第11级和第12级不得分别重复检索**：
两级同属一个 `pku_core` 范围，一次分面检索即可覆盖，结果按目录层级排序后补充。
其他层级不在覆盖范围内，应改用 `ai4scholar`。

环境 CSSCI 只是 CSSCI 的子集，仅靠来源类别分面收不窄到环境学科，因此刊名枚举
与分面两者都不能省。第7级中文集合在目录构建期固化，运行时不猜测语言。

分组检索依次执行 **TI → SU → KY → TKA**，并**累计**此前字段尚未取得的合格唯一
记录；达到请求数量即停。四个字段的结果互相补充，不存在"取有效记录最多的那个
字段"这回事。返回值里的 `topic_fields_tried` 如实列出试过哪些字段，`topic_field`
是达到的最宽字段。

**来源类别不是专业检索字段。** CSSCI 固定为 `P0209`、北大核心固定为 `P01`，只在
首次检索成功后的结果页来源类别中勾选，不写入专业检索表达式，也不出现在 `LY=`
子句里，更不作为 MCP 的自由输入参数。分面未证实稳定生效即返回
`page_contract_changed`，绝不退回未筛选结果。

`first_page_only=true` 表示每条表达式只读取当前页最多 50 条；只有累计合格唯一
记录达到请求数量且无终止状态时 `complete` 才为真，`complete=false` 时不得声称
检索完整。

三个诊断字段的语义边界：

- `excluded_out_of_scope_records` / `excluded_out_of_scope_count`：`LY=` 的近似
  命中、目录未匹配、环境 CSSCI 非第9级、索引身份不符的记录都进这里，**不占限额**。
- `already_covered_higher_priority_count` 在单组 MCP 调用中**恒为 0**——单组调用
  没有"已检索过哪些更高层级分组"的上下文，跨组去重是完整 Skill 工作流的职责。
  它为 0 不代表"没有重复"，只代表"本次未计算"。完整工作流中高层级重复项标记为
  `already_covered_higher_priority`，不占后续剩余总限额。
- `source_category_applied` 是全部已执行批次与字段的**合取**：任一批次未证实分面
  生效，整组即为 `false`。它可能低于逐条记录的实际筛选状态，误差方向是保守低报，
  且必然伴随 `terminal_status` 或 `human_intervention_required=true` 供定位。

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

返回 `no_data_retry_later` 表示知网返回「抱歉，暂无数据，请稍后重试。」，
这是服务端临时拒绝，**不等于空结果**，通常由表达式过长触发，应缩小分批后重试，
不得当作"该主题在这些期刊上没有文献"。

## 输出契约

严格按以下顺序报告：

1. 检索范围：主题、检索式、年份、语言、检索日期和 `sources`。
2. 按十二级目录整理的论文：篇名、作者、年度、正式期刊名、DOI或稳定链接、
   期刊层级和来源。
3. 环境细分领域及正式证据：列出 `environment_subfields`、
   `formal_evidence`、`index_memberships` 和 `source_catalogs`。
4. 文献综合：只概括题录、摘要或工具结果能够核实的信息。
5. 检索限制与未匹配记录：说明空层级、去重口径、元数据缺失、CNKI状态、
   歧义和未匹配期刊。

不得根据题名推测结论，不得补造 DOI、作者、期刊、年度、引用次数、链接、
数据库收录或正式证据。
