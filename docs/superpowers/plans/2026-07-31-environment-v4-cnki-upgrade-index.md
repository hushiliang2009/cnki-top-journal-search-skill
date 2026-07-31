# 环境期刊目录 v4.0 与 CNKI 检索升级实施索引

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按既定证据边界完成环境期刊目录 v4.0 全量增补、通用版与环境版 CNKI 字段及来源类别流程升级，并产出可验证、可安装、可回滚的发布包。

**Architecture:** 三份实施计划按依赖关系串行交付：先生成并验证唯一目录数据源，再让两个 CNKI 运行时消费稳定的目录接口，最后统一版本、文档、安装器、CI 和发布产物。

**Tech Stack:** Python 3.11+、Markdown、JSON/JSONL、Playwright async API、FastMCP、Pydantic、pytest、ruff、mypy、PowerShell、POSIX Shell、GitHub Actions。

## Global Constraints

- 唯一设计依据为 `docs/superpowers/specs/2026-07-31-environment-catalog-v4-cnki-source-category-design.md`。
- 实施基线为分支 `codex/v4-catalog-source-category-design` 上的设计提交 `b6f9dd0`；不得将既存未跟踪的 Win11 交接文档纳入任何提交。
- 环境目录固定为 12 级、3764 种主目录期刊，各级数量为 `4, 17, 5, 45, 17, 6, 134, 324, 241, 1229, 1181, 561`。
- CNKI 专业检索字段优先序固定为 `TI`, `SU`, `KY`, `TKA`；CSSCI 和北大核心只能作为结果页来源类别筛选，不得写入专业检索表达式。
- 通用版目标版本为 `0.5.0`，环境版目标版本为 `0.3.0`；全部验收门槛通过前不得创建标签或 GitHub Release。
- 自动化测试和 CI 不访问真实 CNKI 页面；页面状态、来源类别和挑战页行为使用可重复的单元测试与本地页面替身验证。发布前的真实 WebVPN 冒烟测试必须由使用者明确授权并全程人工值守，不得写入 CI。

---

## File Structure

- `docs/superpowers/specs/2026-07-31-environment-catalog-v4-cnki-source-category-design.md`：已批准的唯一设计依据。
- `docs/superpowers/plans/2026-07-31-environment-catalog-v4-data.md`：目录来源导入、增补、审计、生成和运行时查询计划。
- `docs/superpowers/plans/2026-07-31-cnki-field-facet-workflow.md`：通用版与环境版字段累计、来源类别、资格过滤和断点计划。
- `docs/superpowers/plans/2026-07-31-v050-env-v030-release.md`：版本、文档、构建、安装、CI、PR、标签和 Release 计划。
- `docs/superpowers/plans/2026-07-31-environment-v4-cnki-upgrade-index.md`：三份计划的依赖、顺序和总验收索引，不直接修改产品文件。

## 规格覆盖

| 设计章节 | 主责计划 | 验收重点 |
|---|---|---|
| 第4至第8节、第15.1节 | 环境目录 v4.0 数据计划 | 3764种期刊、来源登记、逐条审计、哈希、镜像和机器查询 |
| 第9至第13节、第15.2至第15.4节 | CNKI 字段与来源类别计划 | 四字段累计、结果页分面、目录资格、去重限额、异常与断点 |
| 第14节、第15.5节、第16至第18节 | v0.5.0 / v0.3.0 发布计划 | 文档、版本、锁文件、白名单、安装、CI、PR、标签和发布后验证 |

## 重叠文件的继承规则

- 数据计划先修改环境版 `models.py`、`ranking.py`、`catalog_adapter.py` 及对应镜像；CNKI 计划在此基础上只增加检索字段和分组命中元数据，不得删除 v4.0 目录字段。
- CNKI 计划先写入两版 `SKILL.md`、`README.md`、`agents/openai.yaml` 和参考说明的操作契约；发布计划只追加版本、产物和安装信息，不得回退已通过测试的字段及来源类别描述。
- 后续计划每次修改重叠文件后，必须重跑前置计划为该文件建立的回归测试，不以新计划的定向测试替代。

## 执行顺序

### 阶段 1：生成环境期刊目录 v4.0 数据包

执行计划：`docs/superpowers/plans/2026-07-31-environment-catalog-v4-data.md`

该阶段建立可重复生成的 Markdown、JSON、来源清单和匹配审计，并将运行时默认数据源切换为机器目录。

- [ ] 逐任务执行数据生成计划的 RED、GREEN 和重构步骤。
- [ ] 确认两份 Skill/MCPB 参考文件字节一致，所有内容哈希和数据哈希可重算。
- [ ] 确认 3764 条稳定 ID、五类来源增补、26 个受控别名以及全量匹配审计通过。
- [ ] 在进入阶段 2 前，以独立提交保存目录生成器、数据产物和运行时查询变更。

### 阶段 2：升级通用版与环境版 CNKI 工作流

执行计划：`docs/superpowers/plans/2026-07-31-cnki-field-facet-workflow.md`

该阶段实现字段累积检索、结果页来源类别筛选、跨字段去重、扩展后的断点标识和目录重新判级。

- [ ] 仅在阶段 1 的机器目录接口稳定后开始本阶段。
- [ ] 先完成表达式构建器和断点身份的失败测试，再修改浏览器与服务层。
- [ ] 确认通用版 CSSCI、环境版 CSSCI 和北大核心的来源类别均在结果页生效，筛选状态确认前不得解析记录。
- [ ] 确认直接自定义表达式仍只执行一次，不自动改写字段或来源类别。
- [ ] 在进入阶段 3 前，以独立提交保存两版 CNKI 运行时和相应测试变更。

### 阶段 3：版本、文档、安装、CI 与发布

执行计划：`docs/superpowers/plans/2026-07-31-v050-env-v030-release.md`

该阶段对齐公开说明、包内元数据、依赖锁文件、确定性构建、三平台安装验证和发布门槛。

- [ ] 仅在阶段 1 和阶段 2 的聚焦测试全部通过后开始版本升级。
- [ ] 同步通用版 `0.5.0` 和环境版 `0.3.0` 的所有版本声明，通过 `uv lock` 重新生成锁文件，不手工修改锁文件。
- [ ] 验证通用版 manifest 同时声明两个已有工具，环境版发布白名单仅包含 v4.0 目录及审计资产。
- [ ] 运行完整 CI 对等测试、确定性双构建和工作区外解压验证。
- [ ] 将两个版本分别交付，不在同一个 `checksums.sha256` 中混合两组产物。

## 总验收顺序

- [ ] 运行三份实施计划中的全部聚焦测试命令。
- [ ] 运行通用版和环境版全量 pytest、ruff 与 mypy 检查。
- [ ] 构建两组 ZIP/MCPB 产物两次，比对字节级 SHA-256。
- [ ] 在三平台 CI 安装场景中验证通用版与环境版共存、重装和回滚。
- [ ] 审阅 `git diff --check`、未跟踪文件、发布白名单和包内绝对路径扫描。
- [ ] 仅在全部自动化门槛和人工产物审核通过后，按发布计划创建标签与 Release。

## 建议提交边界

1. 目录生成器、机器数据、审计文件与查询运行时。
2. 通用版 CNKI 字段和来源类别流程。
3. 环境版 CNKI 字段、来源类别和目录分组流程。
4. 两版公开文档、版本元数据与锁文件。
5. 构建、安装器、CI 和发布门槛。

每个提交仅纳入当前边界的代码、测试和文档；任一门槛失败时，留在当前阶段修复，不带失败状态进入后续阶段。
