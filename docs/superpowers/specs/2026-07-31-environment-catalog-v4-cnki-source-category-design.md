# 环境期刊目录 v4.0 全面增补与 CNKI 来源类别检索设计

> 设计日期：2026年7月31日
>
> 仓库基线：`main@76651999980bc3f5c9bd283f90002a1efda97851`
>
> 目标版本：通用版 `0.5.0`，环境版 `0.3.0`
>
> 状态：经用户分节确认，等待书面审核

## 一、目标与范围

本次工作包含三个相互配合的部分。

1. 规范整理《环境科学与工程学科顶尖期刊目录 v4.0》，使十二级含义、证据边界、机器字段和统计口径清晰一致。
2. 对 v4.0 现有3764种期刊逐刊补充 SSCI、SCIE、CSSCI、北大中文核心交叉收录、原始学科类别、来源题名和受控别名。
3. 同步升级通用版与环境版的 CNKI 高级检索之专业检索功能。专业表达式按 TI、SU、KY、TKA 顺序逐级放宽；CSSCI 和北大核心仅通过检索结果页的来源类别筛选，不作为专业检索字段。

全面增补只增加元数据，不重新评定期刊层级。v4.0 的3764种期刊、十二级顺序和各级数量是不可变基线。CSSCI 完整目录中未进入现有环境目录的82种期刊不新增到 v4.0。

本次不纳入 CSCD、AMI、WJCI、EI 等逐刊收录关系。虽然这些类别出现在 CNKI 结果页，但当前工作区没有相应完整正式目录，不得根据界面标签或非正式转载反推逐刊身份。

## 二、证据边界

逐刊交叉收录只采用以下本地正式目录快照：

| 来源 | 版本或日期 | 用途 |
|---|---|---|
| `CSSCI_2025_2026.md` | 2025—2026 | CSSCI身份及原始学科类别 |
| `北大中文核心期刊目录_2023_自然科学版.md` | 2023版 | 北大核心自然科学身份、分类和原刊名 |
| `北大中文核心期刊目录_2023_.md` | 2023版 | 北大核心非自然科学身份及分类 |
| `Social Sciences Citation Index_20260715.md` 与 `Social Sciences Citation Index (SSCI).csv` | 2026-07-15 | SSCI身份、WoS学科类别及正式标识符；CSV用于机器匹配，Markdown用于人读审计 |
| `Science Citation Index Expanded_20260715.md` 与 `Science Citation Index Expanded (SCIE).csv` | 2026-07-15 | SCIE身份、WoS学科类别及正式标识符；CSV用于机器匹配，Markdown用于人读审计 |

SSCI、SCIE 对应本地 CSV 中已有 ISSN 或 eISSN 时可以保留这些标识符。CSSCI 和北大核心目录没有提供正式标识符的期刊，不从其他网站或推测性数据补造 ISSN。

第一级至第七级原有高校、学会和顶尖期刊证据继续保留。数据库交叉收录仅说明收录身份，不替代高校或学会分级证据，也不触发层级升降。

## 三、目录层级的含义

十二级分为三类。

| 类别 | 层级 | 含义 |
|---|---|---|
| 正式高水平层 | 第1—7级 | 依据顶尖高校、全国性学会或既有顶尖期刊目录认定 |
| 环境数据库层 | 第8—10级 | 环境相关 SSCI、CSSCI、SCIE 补充范围 |
| 北大核心补充层 | 第11—12级 | 前十级或前十一级未收录的北大核心自然科学及非自然科学期刊 |

U1至U5只用于第一级至第七级正式证据的标准化，不适用于第八级至第十二级。第十一、十二级是环境主题检索的宽范围补充，不表示其中每种期刊均属于环境学科；环境相关性由检索主题和结果审核共同限定。

第十一级排除第一至第十级已有期刊。第十二级排除第一至第十一级已有期刊。交叉收录信息在元数据中完整保留，但主目录只保留最高检索层级。

## 四、目录产物与职责

环境版同时维护以下产物。

### 4.1 人读目录

`top-journal-search-lists-env/references/环境科学与工程学科顶尖期刊目录_v4.0.md`

该文件保留编制说明、十二级主目录、正式证据、交叉收录、附录、统计和内容哈希。表格按表头名称解析，不依赖固定列序。数据日期继续为2026年7月29日，另记录规范修订日期2026年7月31日。

### 4.2 机器目录

`top-journal-search-lists-env/references/environment_journal_catalog_v4.0.json`

JSON 保存3764条规范记录及其证据ID引用，是 Skill 与 MCP 的机器查询基准；证据实体由来源清单统一登记。JSON 的 `data_sha256` 按下段规定的固定占位符计算。Markdown 由 JSON 确定性渲染，记录相同的 `data_sha256`，并按固定的自引用占位符规则计算自身内容哈希。两者不互相嵌入文件哈希，避免递归哈希。正常检索只加载 JSON 并在进程内复用索引，不全文解析 Markdown；`validate` 才执行完整的一致性核验。

规范 JSON 固定采用 UTF-8 无 BOM、LF 换行、文件末尾一个换行、键名按 Unicode 码点升序、`ensure_ascii=false` 和紧凑分隔符。数据模型不使用浮点数。期刊记录按 `journal_id` 排序；集合型数组规范去重后按 NFKC 文本升序排列；具有证据顺序的数组按来源注册表顺序和来源行号排列。计算 `data_sha256` 时，保留该键并把值固定为字符串 `{{DATA_SHA256}}`，对规范序列的 UTF-8 字节计算 SHA-256，再以64位小写十六进制摘要替换占位符；校验时执行同一逆向替换。Markdown 内容哈希同理使用唯一占位符 `{{CONTENT_SHA256}}`。最终 JSON、Markdown、来源清单和发布包的文件级哈希统一写入发布根目录的 `checksums.sha256`。

### 4.3 来源清单

`top-journal-search-lists-env/references/environment_catalog_sources_v4.0.json`

该文件包含两个注册区。`artifacts` 记录五类数据库来源、七份本地快照的名称、版本、范围、文件大小和 SHA-256；`evidence_registry` 记录第一级至第七级使用的高校、学会、NCS、PNAS及既有顶尖期刊证据，至少包含稳定证据ID、发布机构、文件或网页名称、原始等级、发布日期、正式链接、访问日期和本地快照哈希。每个 `evidence_id` 必须能在该注册表中唯一解析。

五份 Markdown 与两份 WoS CSV 快照随 Skill 和 MCPB 发布，使目录在其他电脑上仍可独立复算与审计。两份北大核心目录的链接改为 Skill 内相对路径，不保留盘符或用户目录。只有正式链接而没有本地快照的高校或学会证据保留链接和访问日期，不伪造文件哈希。

### 4.4 逐刊匹配审计

开发仓库保留：

- `docs/audits/environment_journal_match_audit_v4.0.jsonl`
- `docs/audits/environment_journal_match_audit_v4.0.md`

JSONL 覆盖每一条来源记录，记录原始题名、候选、匹配方法、处理结果、增加的收录关系、层级前后值和人工审核状态。处理状态固定区分 `matched`、`out_of_scope`、`ambiguous` 和 `expected_but_unmatched`。完整数据库中不属于3764条主目录的正常记录标为 `out_of_scope`，不得计为匹配失败；只有主目录已声明相应身份却不能回连来源时才标为 `expected_but_unmatched`。

Markdown 汇总统计、受控别名、范围外来源记录、真正未匹配记录、人工决定和代表性样本。仓库摘要位于 `docs/audits/environment_journal_match_audit_v4.0.md`，发布镜像位于 `top-journal-search-lists-env/references/environment_journal_match_audit_v4.0.md` 和 `top-journal-search-lists-env/mcpb/src/references/environment_journal_match_audit_v4.0.md`。完整 JSONL 只由仓库保留并纳入 CI 校验。

### 4.5 镜像要求

Skill 目录和 `mcpb/src` 中的人读目录、机器JSON、来源清单、审计摘要及七份来源快照必须字节一致。构建脚本使用白名单收集文件，不把缓存、Cookie、浏览器配置、临时检索结果或本机路径装入发布包。

## 五、规范记录模型

每种期刊具有稳定的 `journal_id`。初次转换按层级升序、级内现有序号升序分配 `ENVJ-000001` 至 `ENVJ-003764`。后续更名不得重用或改变编号；层级基线不变时，编号顺序也不得重新生成。

```text
journal_id
formal_title
formal_title_evidence_ids[]
aliases[]
issn[]
eissn[]
priority_level
priority_group
priority_decision
ncs_internal_rank
environment_subfields[]
subject_categories[]
formal_evidence[]
evidence_ids[]
index_memberships[]
index_subject_categories{}
source_memberships[]
source_catalogs[]
catalog_version
catalog_date
revision_date
manual_review_required
review_reasons[]
cnki_routing
```

字段含义如下。

- `formal_title` 是当前正式期刊名称，`formal_title_evidence_ids` 指向支持该名称的正式来源。若增补阶段发现有唯一正式证据支持的题名错误，可以在 `journal_id`、层级、分组和数量均不变的前提下审计更正，并将原题名保存为别名；不能唯一确认时保持原题名并标记人工复核。
- `aliases` 只保存有来源证明的原刊名、数据库旧题名或受控显示变体，不自动生成缩写。
- `priority_level`、`priority_group` 和 `ncs_internal_rank` 只由已确认的 v4.0 主目录决定。
- `priority_decision` 记录最高层级规则、候选来源和增补前后层级，增补后必须标记 `unchanged=true`。
- `environment_subfields` 只保存环境学科标签。
- `subject_categories` 是兼容字段，继续与 `environment_subfields` 一致。
- `index_memberships` 只保存 `SSCI`、`SCIE`、`CSSCI`、`PKU_CORE` 等索引身份，不再混入学科名称。
- `index_subject_categories` 按索引分别保存 WoS、CSSCI 和北大核心原始学科类别。
- `source_memberships` 逐项保存索引、版本、来源题名、来源记录、学科类别、匹配方法和来源文件。
- `formal_evidence` 保留兼容展示文本；`evidence_ids` 指向文档级证据注册表。
- `source_catalogs` 从交叉收录和正式证据来源派生，不再用环境目录本身替代全部原始来源。
- `cnki_routing` 记录中文检索可用性、结果页来源类别和精确来源题名，只服务检索，不影响分级。

## 六、逐刊增补与题名匹配

### 6.1 两阶段处理

第一阶段读取现有十二级主目录，生成初始正式题名，并锁定以下身份与分级字段：

- `journal_id`
- `priority_level`
- `priority_group`
- `ncs_internal_rank`
- `environment_subfields`

第二阶段读取五类来源目录。SSCI 与 SCIE 以各自 CSV 作为机器匹配输入，以对应 Markdown 复核正式显示题名和人读结构；其余三类来源直接读取 Markdown。第二阶段增补别名、标识符、索引身份、原始学科类别和来源，也可以按第五节规则审计更正正式题名，但不得改变 `journal_id`、层级、分组或记录数。交叉记录如果不能唯一指向现有3764条主记录，进入人工审核，不得静默新增期刊。

### 6.2 匹配顺序

v4.0 基线本身没有完整 ISSN，因此标识符不是首次绑定的先决条件。每条来源记录按以下顺序执行：

1. 目标记录已经由更早来源绑定 ISSN、eISSN 时，按正式标识符唯一命中；
2. 正式题名完全匹配；
3. 有来源证明的受控别名唯一命中；
4. 保守规范化后唯一命中；
5. 经审计记录的人工映射。

题名或别名首次唯一命中后，将来源中的 ISSN、eISSN 绑定到该 `journal_id`；后续来源可以使用这些标识符合并交叉记录。标识符冲突时不得覆盖，直接转入人工审核。

保守规范化只处理 Unicode NFKC、大小写、首尾空白、`The`、`&/and` 和有限标点差异。禁止使用编辑距离、题名包含关系或宽泛去重音符号自动认定。多候选时保持 `ambiguous`，不赋予匹配层级。

北大核心原刊名不得按逗号拆分。例如 `天然气化工.C1,化学与化工` 是一个完整原刊名。

### 6.3 受控别名

现有17条北大核心原刊名全部转为结构化别名。此外加入九组经来源目录与现刊名证据确认的数据库题名：

- `WIREs Climate Change` 与 `Wiley Interdisciplinary Reviews-Climate Change`
- `WIREs Energy and Environment` 与 `Wiley Interdisciplinary Reviews-Energy and Environment`
- `WIREs Water` 与 `Wiley Interdisciplinary Reviews-Water`
- `地理学报` 与 `地理学报（北京）`
- `Archiv für Molluskenkunde` 与 `ARCHIV FUR MOLLUSKENKUNDE`
- `ArchéoSciences-Revue d Archeometrie` 与 `ARCHEOSCIENCES-REVUE D ARCHEOMETRIE`
- `Journal of Food Safety and Food Quality-Archiv für Lebensmittelhygiene` 与 `JOURNAL OF FOOD SAFETY AND FOOD QUALITY-ARCHIV FUR LEBENSMITTELHYGIENE`
- `Zeitschrift der Deutschen Gesellschaft für Geowissenschaften` 与 `ZEITSCHRIFT DER DEUTSCHEN GESELLSCHAFT FUR GEOWISSENSCHAFTEN`
- `Zeitschrift für Geomorphologie` 与 `ZEITSCHRIFT FUR GEOMORPHOLOGIE`

九组数据库题名映射逐条保存来源证据，不扩展为通用去重音符号规则。17条原刊名与9组数据库题名合计形成26条结构化别名增补，不增加主目录期刊数。查询别名时返回当前正式题名，并标明 `match_method=controlled_alias`。

### 6.4 增补统计基线

接受上述受控别名后，预期命中为：

| 来源 | 来源唯一期刊 | v4.0命中 | 正常范围外 | 关键完整性门槛 |
|---|---:|---:|---:|---|
| CSSCI | 674 | 592 | 82 | 第9级241种全部回连 |
| 北大核心自然科学 | 1247 | 1247 | 0 | 1247种全部回连 |
| 北大核心非自然科学 | 740 | 740 | 0 | 740种全部回连 |
| SSCI | 3538 | 348 | 3190 | 第8级324种全部回连 |
| SCIE | 9430 | 1499 | 7931 | 第10级1229种全部回连 |

交叉统计以 v4.0 的唯一期刊记录为对象，不按来源目录中的重复学科行计数。预期 `CSSCI ∩ 北大核心自然科学=22`、`CSSCI ∩ 北大核心非自然科学=520`、`SSCI ∩ SCIE=149`，其余来源两两交集均为0。完全未被五类数据库来源命中的 v4.0 记录为29种，可以保留，但必须具有原有高校、学会或顶尖期刊正式证据。规范化冲突、一对多歧义和 `expected_but_unmatched` 均应为0。

## 七、目录渲染与校验

Markdown 的机器配置补齐十二个固定分组：

1. `comprehensive_super_journals`
2. `ncs_pnas_environment_flagships`
3. `top_university_highest_consensus`
4. `top_university_high_level`
5. `environment_field_top`
6. `chinese_environment_top`
7. `other_formally_recognized`
8. `environment_ssci`
9. `environment_cssci`
10. `environment_scie`
11. `pku_core_natural_sciences`
12. `pku_core_non_natural_sciences`

各级表格统一表达正式题名、检索别名、环境细分领域、正式证据、索引收录、原始学科类别和来源目录。没有环境细分领域的第十一、十二级使用空值，不把北大核心分类误写为环境领域。

统计区增加：

- 前十级唯一期刊数2022；
- 北大核心原始记录合计1987；
- 北大核心排除重复合计245；
- 第十一、十二级净新增1742；
- 各索引交叉收录命中数；
- 受控别名数；
- 主目录层级签名；
- JSON规范数据哈希、Markdown自引用内容哈希和来源清单哈希。

完整校验必须确认：

- 各级数量为 `[4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561]`；
- 主目录唯一记录为3764；
- 主目录不存在跨层级重复；
- 增补前后 `(journal_id, priority_level, priority_group, ncs_internal_rank)` 签名一致；
- JSON规范数据哈希、Markdown自引用内容哈希和来源快照哈希有效；
- Skill 与 MCPB 镜像字节一致。

## 八、机器查询

`catalog_lookup.py` 默认读取 `environment_journal_catalog_v4.0.json`，首次加载时建立以下进程内索引：

- `by_journal_id`
- `by_issn`
- `by_formal_title`
- `by_alias`
- `by_normalized_title`
- `records_by_priority_group`
- `records_by_cnki_scope`

查询返回现有兼容字段，并增加 `journal_id`、`aliases`、`index_subject_categories`、`source_memberships` 和 `revision_date`。未匹配和歧义结果不得自行赋予层级。`--catalog` 继续支持覆盖路径；同时增加只在审计时使用的完整 Markdown 与来源清单校验。

`journals_by_group()` 仍只依据最高 `priority_group` 返回期刊，交叉收录不得造成跨组重复。另提供显式的 CNKI 检索范围查询，不使用语言猜测替代目录规则。

## 九、CNKI专业检索范围

目录层级与 CNKI 检索范围分开管理。CNKI 采用数据驱动的 `SearchGroupPolicy`，至少包含：

```text
scope_id
journal_selector
source_category
eligible_journal_ids
eligible_priority_levels
result_filter
```

`source_category` 只允许 `null`、`{"code":"P0209","label":"CSSCI"}` 或 `{"code":"P01","label":"北大核心"}`。代码和值由策略表固定，不作为工具的自由输入。结果处理顺序固定为分面生效、目录匹配、索引身份核验、当前组资格过滤、跨结果去重、计算限额。

以CSSCI或北大核心身份定义范围的中文检索必须应用对应结果页来源类别。以具体期刊清单定义的中文顶尖或正式认可期刊范围继续使用 `LY=` 精确限定；其中可能包含并非CSSCI或北大核心的期刊，不能无条件叠加来源类别而造成漏检。

### 9.1 通用版

| 范围 | 专业表达式 | 结果页筛选 |
|---|---|---|
| `chinese_top_journals` | `LY=`限定13种中文顶尖期刊 | 无 |
| `cssci` | 主题和年份 | 来源类别 CSSCI |

通用版 CSSCI 不枚举综合目录去重后剩余的661种期刊。该数字来自CSSCI原始674种扣除已归入更高层级的13种，并不表示CSSCI来源只有661种。来源类别筛选覆盖 CNKI 当前 CSSCI 来源期刊及扩展版，返回记录再按综合目录判级。

### 9.2 环境版

| 范围 | 专业表达式 | 结果页筛选 | 组内判定 |
|---|---|---|---|
| `chinese_environment_top` | `LY=`限定第6级6种期刊 | 无 | 第6级题名集合 |
| `other_formally_recognized_chinese` | `LY=`限定第7级60种中文期刊 | 无 | 第7级中文题名集合 |
| `environment_cssci` | `LY=`限定第9级241种期刊 | 来源类别 CSSCI | 第9级题名集合 |
| `pku_core` | 主题和年份 | 来源类别 北大核心 | v4.0中全部1987种北大核心成员 |

v4.0 中共有592种 CSSCI 身份期刊，但 `environment_cssci` 的目录资格只限第9级241种；其余351种保留CSSCI身份，不能据此改写为第9级。第9级近似来源题名或目录外CSSCI记录标为当前组范围外，不占该组限额。

第十一、十二级共用一个 `pku_core` 范围，避免对完全相同的北大核心分面发起两次检索。该范围直接调用时保留全部1987种北大核心身份期刊并按现有层级排序，其中245种已位于第1—10级，1742种位于第11—12级。完整环境中文检索工作流中，245种高层级记录若已由前序组取得，标记为 `already_covered_higher_priority` 并参与全局去重，不占剩余总限额；不得把它们作为组外记录丢弃。

第7级中文期刊集合由规范目录显式生成并固定测试数量，不在运行时仅凭题名含汉字临时推断。

### 9.3 跨组顺序与限额

通用版依次执行 `chinese_top_journals`、`cssci`。环境版依次执行：

1. `chinese_environment_top`，第6级；
2. `other_formally_recognized_chinese`，第7级中文期刊；
3. `environment_cssci`，第9级；
4. `pku_core`，先保留尚未取得的高层级记录，再按第11级、第12级补充。

MCP 单次工具调用中的 `limit` 保持为当前组限额。Skill 接到一个跨组总量时，以该数量作为全局唯一论文目标，按上述顺序把尚缺数量传给后续组；达到总量后停止。使用者明确要求各层级分别取若干篇时，才把限额分别应用到每个组。

跨组结果优先按 DOI 去重；无 DOI 时按规范化篇名、作者和年度去重。同一论文被多组或多个检索字段命中时，保留期刊目录层级最高的记录；层级相同时保留更早的组和更早的检索字段，同时合并命中来源信息。

## 十、专业检索字段优先序

两版统一采用：

1. `TI`，篇名；
2. `SU`，主题；
3. `KY`，关键词；
4. `TKA`，篇关摘。

底层表达式构造器默认字段也改为 `TI`，防止绕过服务层时回退到旧的 `SU` 行为。`build_topic_expression()`、`build_expression()` 和 `build_batches()` 均接收显式 `topic_field`，只允许上述四种值。

分组检索依次执行字段并累计合并组内有效记录。每篇论文保留最先命中的字段；达到请求数量后停止继续放宽。若四个字段均不足，返回已累计的全部唯一记录，不选择一个较宽字段替换此前结果。

论文最终排序为：

1. 期刊目录层级；
2. NCS内部顺序；
3. 最先命中的检索字段顺序；
4. 原始结果顺序。

同一论文优先按 DOI 去重；没有 DOI 时按规范化篇名、作者和年度去重。直接执行使用者自备表达式的接口保持单次执行，不自动改写字段或添加来源类别。

## 十一、来源类别页面流程

来源类别不是专业检索字段，不得出现在表达式或 `LY` 条件中。固定执行顺序如下：

1. 填写并提交专业检索表达式；
2. 等待首次结果状态；
3. 首次状态为成功时，在结果页勾选 CSSCI 或北大核心；
4. 验证复选框已选中并等待页面稳定；
5. 重新判断成功、无结果、安全验证或页面异常；
6. 仍为成功时切换每页50条；
7. 解析题录并完成目录匹配；
8. 核验CSSCI或北大核心索引身份；
9. 执行当前组资格过滤；
10. 执行字段内、字段间及跨组去重；
11. 按合格唯一记录计算限额。

筛选后总数可能与筛选前相同，因此不能只以总数变化作为成功条件。应结合复选框状态、结果区状态和页面稳定性判断。筛选后为零条时返回 `no_results`；来源类别缺失、复选框未生效或页面结构不符时返回 `page_contract_changed`，不得退回未筛选结果。

断点键必须包含表达式、检索范围、检索字段和来源类别。CSSCI 与北大核心即使主题表达式相同，也不能相互复用断点。

## 十二、结果范围与返回契约

单组调用只以当前策略认定的有效记录计算 `limit`。`LY=` 的近似命中、`environment_cssci` 中不属于第9级的记录以及目录未匹配记录均不占当前组限额，另行报告。`pku_core` 直接调用时，第1—12级的北大核心成员均为有效记录；完整工作流中已经由高层级组取得的记录参与全局去重，标为已由更高层级覆盖，不占后续剩余总限额。

新增或明确返回：

```text
source_category_requested
source_category_applied
source_category_total
source_category_code
topic_fields_tried
topic_match_field
eligible_record_count
excluded_out_of_scope_count
excluded_out_of_scope_records
already_covered_higher_priority_count
already_covered_higher_priority_records
first_page_only
complete
human_intervention_required
```

CNKI 结果页最多读取当前页50条，因此 `first_page_only=true` 必须如实返回。组内记录不足不能解释为该主题没有更多文献，`complete=false` 时 Skill 不得宣称检索完整。

## 十三、异常与人工值守

公开首页检索保持匿名、第一页、最多20条、不登录、不下载、不持久化Cookie的现有边界。

专业检索继续采用人工值守 WebVPN 会话。出现安全验证时停止后续批次和字段切换。只有使用者在当前可见浏览器中手工完成验证后，才能在同一会话恢复当前批次；不得自动破解、切换代理、导出登录态或无人值守重试。若人工验证未完成，返回部分结果及 `human_intervention_required=true`。

登录失效、401、403、429、浏览器关闭或页面契约变化时立即停止。来源类别筛选失败不得降级为普通主题结果。已取得的合格记录可以作为 `partial` 返回，但必须同时报告终止状态。

## 十四、版本、接口与文档

通用版由 `0.4.2` 升至 `0.5.0`，环境版由 `0.2.0` 升至 `0.3.0`。MCP服务名和工具名保持不变：

- `cnki-search`：`cnki_search`、`cnki_professional_search`
- `cnki-search-env`：`cnki_search_env`、`cnki_professional_search_env`

环境专业检索工具的 `group` 增加 `other_formally_recognized_chinese` 和 `pku_core`。通用版仍只允许 `chinese_top_journals` 与 `cssci`。任意 `source_category` 不作为公开输入参数，避免调用者绕过受控范围。

同步修改两版 `SKILL.md`、`README.md`、`agents/openai.yaml`、CNKI参考说明、MCP工具描述、版本文件、manifest、锁文件和确定性构建白名单。历史设计、计划、交接和基线评估文件记录既有事实，不追溯改写。

## 十五、测试设计

实施采用测试先行。通用版和环境版分别运行测试，避免顶层同名 `catalog_lookup` 模块在同一 Python 进程中相互污染。

### 15.1 目录与增补

- v4.0版本、日期、修订日期、十二级名称和分组；
- 3764种期刊及各级固定数量；
- 层级签名增补前后完全一致；
- 五类来源的命中数和交叉收录数；
- 第8、9、10级分别完整回连 SSCI、CSSCI、SCIE；
- 北大核心1987种全部回连；
- 17个原刊名和9组数据库题名别名，共26条结构化别名增补；
- 无规范化冲突和一对多歧义；
- `out_of_scope` 与 `expected_but_unmatched` 状态及固定数量；
- 规范JSON序列化、Markdown自引用哈希、来源清单和镜像哈希；
- 附录记录不得进入主索引；
- 默认目录不得继续引用 v3.0。

代表性记录至少包括：

- `Nature Climate Change`：第2级、内部顺序1、SSCI与SCIE；
- `Environmental Science & Technology`：第3级、SCIE；
- `中国人口·资源与环境`：第7级、CSSCI与北大核心自然科学；
- `WIREs Climate Change`：第8级、SSCI与SCIE、数据库题名别名；
- `城市规划`：第9级、CSSCI与北大核心自然科学；
- `WIREs Energy and Environment`：第10级、SCIE、数据库题名别名；
- `Zeitschrift für Geomorphologie`：第10级、SCIE、含重音符号的受控题名映射；
- `陆军军医大学学报`：第11级，原刊名可查询；
- `中国社会科学`：第12级、CSSCI与北大核心非自然科学，层级不因CSSCI身份改变。

### 15.2 专业检索表达式

- 底层默认字段为 TI；
- TI、SU、KY、TKA 严格顺序；
- 累计唯一记录达到限额后停止；
- 同一论文被多个检索字段命中时按最高字段优先级保留；
- CSSCI、北大核心、分面值和来源类别文字不出现在专业表达式；
- 年份、括号、引号、`LY=`及字符预算维持合法语法。

### 15.3 来源类别页面

- 事件顺序为提交、首次判定、勾选分面、再次判定、每页50条、解析、目录匹配、身份核验、资格过滤、去重和限额计算；
- CSSCI值 `P0209`、北大核心值 `P01`；
- 筛选后总数未变但复选框已生效的正常情况；
- 筛选后零结果、安全验证、分面缺失、异步失败和页面变化；
- 来源类别失败时不解析未筛选HTML；
- 断点键区分 CSSCI 与北大核心。

### 15.4 分组与去重

- 通用 CSSCI 使用一次主题计划和结果页分面；
- 环境第6级6种、第7级60种、第9级241种范围准确；
- 环境跨组顺序固定为第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心补充；
- 第9级每一批均应用 CSSCI；
- `pku_core` 不生成 `LY=`，只应用北大核心；
- `pku_core` 直接调用识别1987种成员，完整工作流将245种已覆盖高层级成员全局去重，并按第11、12级补充1742种；
- MCP单组限额与Skill跨组总限额分别执行；
- 当前组范围外记录和已由高层级覆盖的重复记录不占相应限额；
- DOI优先去重，无DOI时使用题名、作者、年度；
- 期刊层级优先于字段优先级排序。

### 15.5 安装、CI与发布

- Python 3.11—3.14的既有矩阵继续运行；
- Windows、macOS、Linux安装和Python 3.10拒绝测试；
- 通用版与环境版并存、覆盖升级、备份保留和失败恢复；
- 两套MCP握手及原始MCPB握手；
- Ruff、mypy、目录校验和确定性构建；
- 连续构建的ZIP与MCPB字节一致；
- 解压到工作区外仍可校验目录并完成MCP握手。

## 十六、当前基线

设计提交前的 Windows 基线如下：

- 通用版：沙箱内468项通过、91个子测试通过；3项Git Bash安装器测试因沙箱拒绝 `CreateFileMapping` 失败。授权环境运行完整安装器文件为30项全部通过。
- 环境版：沙箱内466项通过；4项同类Git Bash安装器测试受沙箱限制。授权环境运行完整安装器文件为33项全部通过。

因此当前产品基线可视为通过。后续若出现同类沙箱错误，必须在授权环境复现后再判断，不得直接归因于产品代码。

## 十七、分支、合并与发布

开发在独立分支进行，先提交测试，再提交实现和生成数据。完成后创建 Pull Request 合并至 `main`。合并条件为：

- 通用版原有测试全部通过；
- 环境版原有测试全部通过；
- 本设计新增测试全部通过；
- 三平台CI通过；
- 逐刊审计无未决主目录歧义；
- 发布包确定性与哈希验证通过。

合并后分别创建：

- 通用版标签 `v0.5.0`；
- 环境版标签 `top-journal-search-lists-env-v0.3.0`。

继续发布各自的 Skill ZIP、MCPB 和 `checksums.sha256`。发布附件下载后重新核对大小、SHA-256、嵌入版本、目录版本、MCP握手和本机共存安装。正式 Release 创建前不得复用旧版本附件或哈希。

## 十八、完成标准

只有同时满足以下条件，任务才可视为完成：

1. v4.0人读目录分级清晰、字段明确、链接可移植；
2. 3764种期刊完成证据边界内的逐刊交叉增补；
3. 层级与数量完全保持不变；
4. 通用版与环境版严格执行 TI、SU、KY、TKA；
5. CSSCI和北大核心只在结果页来源类别中筛选；
6. 环境版覆盖第6级、第7级中文期刊、第9级CSSCI和第11、12级北大核心；
7. 异常状态、组外记录和第一页限制得到如实报告；
8. 测试、安装、构建、审计、PR、标签和Release均通过相应门槛。
