# Task 5 完成报告：确定性生成、镜像与只读检查

## 实施结果

本任务完成 v4.0 人读目录、规范 JSON、来源登记表、匹配审计和双布局镜像的确定性生成。生成器通过同目录临时文件和 `Path.replace()` 原子更新产物；`--check` 只计算并逐字节比较预期内容，不创建目录、不写入或修复失配文件。

`parse_v4_baseline()` 以稳定期刊 ID、基线题名和锁定分级信息为输入，正式题名从基线与批准来源重新生成，上一轮的正式题名、别名、ISSN、索引身份、索引学科类别、来源成员和 CNKI 路由均不参与下一轮匹配。生成目录再次作为基线时，四项发布产物和两项审计产物保持字节一致。

Markdown 现统一渲染十二级表格，包含稳定 ID、基线题名、正式题名、别名、环境细分领域、正式证据、索引收录、原始索引类别和来源目录，并保留结构化 SCIE 分类附录与 v2.0 期刊处置附录。北大核心链接改为同级来源文件。两个 v3.0 Markdown 镜像按计划删除。

Skill 与 MCPB 两个 references 布局中的四项生成产物和七份批准来源快照共 11 个文件均保持字节一致。生成 JSON、Markdown 和审计 Markdown 固定为 LF；七份来源快照设置为不做文本转换。根目录仅为指定审计 JSONL 增加精确忽略例外。

## 继承改动审查

接手时工作树已有未提交的 Task 5 实现和生成产物。经逐项审查，保留了正确的原子写入、镜像复制、规范渲染、派生字段隔离、只读检查、行尾规则、v3.0 删除及既有测试。审查发现原实现丢失了任务要求保留的 SCIE 分类附录和 v2.0 处置附录，因此先恢复批准种子，再补充 bundle 字段、附录解析和渲染，最后重新生成全部产物。

未修改计划文件，也未修改或提交既有未跟踪 handoff 文件 `docs/superpowers/handoffs/2026-07-31-win11-chatgpt-desktop-verification-result.md`。

## TDD 记录

- RED：新增附录保留测试后运行指定测试，因 `CatalogBundle` 缺少 `scie_appendix_markdown` 字段而失败，符合预期。
- 测试提交：`2ca94a9 test: define environment v4 generated artifacts`。
- GREEN：加入两项锁定附录字段、严格提取与渲染后，同一测试通过；随后完整生成测试为 14 passed。
- `--check` 失配测试确认异常退出后失配文件仍保持原字节，来源镜像测试确认七份快照不被换行或内容改写。

## 新鲜验证

- `python scripts/generate_environment_catalog_v4.py`：退出 0。
- `python scripts/generate_environment_catalog_v4.py --check`：退出 0。
- `--check` 前后比较 10 项生成与审计文件的 SHA-256 和 UTC 修改时间：0 项变化。
- `python -m pytest -q -p no:cacheprovider tests/test_environment_catalog_generation.py`：14 passed。
- `python -m compileall -q ...environment_catalog_v4.py ...generate_environment_catalog_v4.py`：退出 0。
- `git diff --check`：退出 0，仅显示 Windows `core.autocrlf` 提示，无空白错误。
- 11 个 Skill/MCPB 文件逐一比较 SHA-256：0 个不一致。
- 使用固定占位符独立反算 Markdown 内容哈希和 JSON 数据哈希：两项均一致。

生成产物 SHA-256 如下：

- 人读 Markdown：`987d5f8561ba0819d9bedd995454ec368566f032f6e5e932761d94f77fcd2cf2`
- 机器目录 JSON：`5bbbe763d36b93f4125c94b8aad35d224b5c3f2b86206a87825a66a6980927c1`
- 来源登记表 JSON：`34f40275af5f50f37b037440a5bb0558bb05a09266b55f548cdf66060d300583`
- 审计摘要 Markdown：`f4cb087d1f82ce45d72cbdd29804a3b3e0674d410b4b1613e49736a9e11652f0`

审计共 15629 条：matched 4426、out_of_scope 11203、ambiguous 0、expected_but_unmatched 0。受控别名为 26 条。

## 风险

当前解释器未安装 Ruff 和 Mypy，本任务未安装额外依赖；已完成编译检查和全部聚焦测试。原子写入使用固定同级临时文件名，设计面向单一生成进程；若未来允许多个生成器并发写同一目录，应另行增加进程互斥或唯一临时文件名。
