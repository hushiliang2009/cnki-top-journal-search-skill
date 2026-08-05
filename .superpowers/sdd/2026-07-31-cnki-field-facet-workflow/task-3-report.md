# Task 3 实施报告

## 完成内容

- 环境版专业检索分组固定为中文环境顶刊、其他正式认可中文期刊、环境 CSSCI 和北大核心四个目录范围。
- `build_group_policy()` 直接消费 `cnki_scope()` 的封闭载荷，保留目录版本、期刊 ID、层级、索引身份和来源类别要求。
- `pku_core` 仅提交主题表达式并使用北大核心来源类别；不生成 `LY=` 条件。环境 CSSCI 同时保留逐刊 `LY=` 条件与 CSSCI 结果页分面。
- `pku_core` 的单组结果固定返回 `already_covered_higher_priority_count=0`，明确其不携带 Skill 工作流的高层级去重上下文。
- 检索按 `TI`、`SU`、`KY`、`TKA` 累计合格唯一记录；先按目录资格过滤，再去重、排序和计算单组限额。
- 资格判断同时核验期刊 ID、目录层级、必要索引身份和来源类别是否已在结果页生效。组外记录不占限额。
- 排序在期刊层级和目录内部顺序之后，按最先命中的主题字段排序；重复记录合并字段与分组元数据。
- 脚本版与 MCPB 镜像中的 `catalog_adapter.py`、`professional_service.py`、`ranking.py` 的 SHA-256 均一致。

## TDD 记录

- RED 提交：`c1838cd test: specify environmental CNKI catalog scopes`。
- RED 命令：`python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py`。
- RED 结果：新增测试因 `build_group_policy` 缺失失败；旧 CSSCI 路径还将自由字符串传入已受控的来源类别接口。
- GREEN：实现目录驱动策略、字段累计、目录资格过滤、去重元数据与排序后，同一目标测试及目录查找测试通过。
- 审查修复 RED：`pku_core` 单组结果读取该字段时出现 `KeyError`；修复后服务测试、环境运行时和 MCPB 镜像验证通过。

## 验证

```text
python -m compileall -q top-journal-search-lists-env/scripts/cnki_search_env top-journal-search-lists-env/mcpb/src/cnki_search_env
exit 0

python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests/test_cnki_professional_service_env.py top-journal-search-lists-env/tests/test_cnki_ranking.py top-journal-search-lists-env/tests/test_catalog_lookup.py
53 passed

python -m pytest -q -p no:cacheprovider top-journal-search-lists-env/tests
500 passed
```

完整测试初次在受限沙箱中有 4 项 Git Bash 安装器测试因 `CreateFileMapping ... Win32 error 5` 失败；在授权的非沙箱重跑安装器测试后，`33 passed`。该错误属于沙箱进程映射限制，未改动安装器代码。

当前解释器未安装 Ruff，`python -m ruff` 返回 `No module named ruff`；已完成 Python 编译检查。既有未跟踪 Win11 handoff 未纳入本任务任何提交。
