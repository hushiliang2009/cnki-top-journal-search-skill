# Claude Desktop 续接说明

## 当前分支

- 仓库：`hushiliang2009/cnki-top-journal-search-skill`
- 当前分支：`codex/v4-catalog-source-category-design`
- 基线：`76651999980bc3f5c9bd283f90002a1efda97851`
- 本次工作均在该分支进行，尚未推送前请先检查远程分支状态。

## 已完成并提交

### 环境目录 v4.0 计划

计划文件：`docs/superpowers/plans/2026-07-31-environment-catalog-v4-data.md`

8 个任务已完成并通过独立审查，最新提交为 `78d65bb`。主要成果：

- v4.0 环境期刊目录、七份来源快照及 Skill/MCPB 镜像；
- 3764 条期刊、12 个层级、稳定 `ENVJ-*` 身份；
- 来源匹配、交叉收录、审计状态、CNKI scope、JSON schema 校验；
- 确定性生成、`--check` 只读校验、发布清单与 v4 归档成员；
- 环境字段传播和旧 v3 引用清理。

### CNKI 字段与来源类别计划

计划文件：`docs/superpowers/plans/2026-07-31-cnki-field-facet-workflow.md`

前 3 个任务已完成并通过独立审查，最新提交为 `8d6a266`：

- 检索字段顺序固定为 `TI`、`SU`、`KY`、`TKA`；
- 来源类别仅作为结果页 facet，不进入专业检索表达式；
- 通用版 CSSCI 累积检索、合格记录过滤、阻断状态和去重；
- 环境版四范围目录策略：中文环境顶尖、其他正式认可中文期刊、环境 CSSCI、北大核心；
- pku_core 单组返回 `already_covered_higher_priority_count=0`；
- WebVPN 的 `SourceCategorySpec`、P0209 CSSCI 分面及 `source_category_applied/total` 已修复；
- 通用版、环境版及 MCPB 镜像均已同步。

## 当前未完成

### CNKI 字段与来源类别计划

- Task 4：页面 facet 状态机。当前 HEAD 为 `559d0f7` 之后的未提交修改，正在实现：提交后检查 facet、分面后重新判定页面状态、只有 facet 成功才设置 page size 50；分面失败必须返回 `page_contract_changed`，不得降级为无分面结果。
- Task 5–8：断点续检与安全 checkpoint、CNKI 诊断字段、Skill 文档与结果排序、通用版/环境版回归和发布契约。

### 发布计划

计划文件：`docs/superpowers/plans/2026-07-31-v050-env-v030-release.md`

尚未执行。需在 CNKI 计划完成后实施：版本号、构建脚本、ZIP/MCPB 确定性构建、安装器白名单、CI 和本地发布验收。

## 续接顺序

1. 检查 `git status`，保留当前 Task 4 未提交修改；不要删除既有 handoff 文件。
2. 继续完成 CNKI 计划 Task 4，并按 SDD 要求生成独立审查包和审查代理。
3. 依次完成 Task 5–8；每个任务必须先 RED、再 GREEN、提交、独立审查，发现 NEEDS_FIX 时修复后复审。
4. 执行发布计划，先运行本地确定性构建和分进程测试；不要自动执行真实 WebVPN、GitHub 合并、标签或当前 Codex 安装，除非用户另行确认。
5. 最后进行全分支审查，检查未跟踪 handoff、v3/v4 引用、镜像 SHA-256、发布成员和测试记录。

## 已知限制

- Windows 沙箱中 Git Bash 偶发 Win32 `CreateFileMapping` 权限错误；这是测试基础设施限制，需在授权 Windows 环境复跑安装器。
- 全量 mypy 可能因 Playwright 等外部依赖缺失而条件性失败；不得把该结果写成全绿。
- 通用版和环境版测试必须分进程执行，避免同名 `catalog_lookup` 模块导入污染。

## 推荐首条命令

```powershell
Set-Location 'G:\Claude_Code\SCIE_SSCI_CSSCI目录\tmp\win11-verification\repo'
git status --short --branch
git log --oneline -12
```
