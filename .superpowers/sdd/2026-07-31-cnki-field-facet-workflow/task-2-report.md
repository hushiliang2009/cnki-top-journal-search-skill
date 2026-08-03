# Task 2 实施报告

## 完成内容

- 通用版专业检索按 `TI`、`SU`、`KY`、`TKA` 顺序累计唯一合格记录。
- 中文顶尖期刊仅保留目录精确匹配记录；CSSCI 使用结果页来源类别 `P0209`，不将 CSSCI 写入检索表达式。
- 越界记录不占限额；阻断状态保留前序合格记录并返回部分结果。
- 去重身份改为题名和年份，保留作者交集判断、最早命中字段及合并后的字段元数据。
- 排序在期刊层级和 NCS 顺序之后，按最早命中的主题字段排序。
- 通用源码与 MCPB 镜像中的 `professional_service.py`、`ranking.py` 已逐字节同步。
- 通用版与环境版的真实页面执行器均接收 `SourceCategorySpec`：用 `.code` 定位 CNKI 分面，用 `.label` 生成可读错误；执行结果保留 `source_category_applied` 与 `source_category_total`。
- 两套 `webvpn.py`、`professional_runtime.py` 的脚本版与 MCPB 镜像均已逐字节同步；审查中发现并恢复了通用版 MCPB `webvpn.py` 的不完整镜像。

## TDD 记录

- RED 提交：`45d8ea9 test: specify qualified CNKI field accumulation`。
- GREEN 提交：`de06f50 feat: accumulate qualified CNKI field results`。
- MCPB 镜像提交：`801b16d chore: mirror qualified CNKI field results`。
- 执行器回归 RED：旧字符串查表路径抛出 `ValueError: 未知的来源类别 SourceCategorySpec(code='P0209', label='CSSCI')`。
- 执行器回归 GREEN：通用版和环境版均选择 `P0209`，并返回 `source_category_applied=True`、`source_category_total=2270`。

## 验证

```text
python -m pytest -q -p no:cacheprovider \
  top-journal-search-lists/tests/test_cnki_professional_service.py \
  top-journal-search-lists/tests/test_cnki_ranking.py
36 passed

AST_OK
MIRRORS_IDENTICAL
```

本轮补充验证：

```text
python -m pytest -q -p no:cacheprovider \
  top-journal-search-lists/tests/test_cnki_professional.py \
  top-journal-search-lists/tests/test_cnki_professional_service.py \
  top-journal-search-lists/tests/test_cnki_professional_runtime.py \
  top-journal-search-lists/tests/test_cnki_ranking.py \
  top-journal-search-lists/tests/test_cnki_source_category.py \
  top-journal-search-lists/tests/test_cnki_webvpn_page.py
100 passed

python -m pytest -q -p no:cacheprovider \
  top-journal-search-lists-env/tests/test_cnki_professional_env.py \
  top-journal-search-lists-env/tests/test_cnki_professional_runtime_env.py \
  top-journal-search-lists-env/tests/test_cnki_webvpn_page_env.py
63 passed

SCRIPT_MCPB_SHA256_IDENTICAL=true
```

两套包不能放在同一 pytest 进程中运行：它们都以顶层模块名 `catalog_lookup` 导入不同目录，测试收集顺序会使通用版误用环境版目录。这是测试装载隔离问题，因此按各自运行时分进程验证。

`python -m ruff` 在当前解释器中不可用，错误为 `No module named ruff`；已改用 AST 语法检查。既有未跟踪 Win11 handoff 未纳入任何提交。
