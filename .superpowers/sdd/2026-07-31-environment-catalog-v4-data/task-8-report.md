# Task 8 报告：环境目录 v4.0 最终质量审计

## 审计修复

- 全量 `mypy top-journal-search-lists-env/scripts/` 首次报告 17 项错误。其中 13 项来自本计划新增的 `environment_catalog_v4.py`，原因是规范 JSON 与来源登记表使用了过宽的 `object` 容器类型。
- 以局部 `cast` 和明确的 `dict[str, int]` 注解收窄这些读取点，不改变生成器的数据、哈希、输出或运行时行为。
- 旧版本引用审计首次失败。四个测试文件仍将实际目录路径指向 v3.0，另一个版本漂移测试使用 v3.0 作为无效样本。测试目录统一迁移至 v4 规范 JSON；无效版本样本改为 `9.9`，保持拒绝错误版本的行为覆盖。

## 验证结果

- RED：全量 mypy 首次为 17 项错误；旧版本引用扫描命中 6 处。
- 环境目录模块的单项检查 `uvx mypy top-journal-search-lists-env/scripts/environment_catalog_v4.py` 通过；相关测试 `59 passed`；旧版本引用扫描为 0。
- 生成器 `--check` 通过，四个规范产物哈希保持为 `987d5f...2cf2`、`5bbbe7...927c1`、`34f402...0583`、`f4cb08...52f0`。
- 默认目录验证通过：3764 条期刊、12 级、11 个镜像文件和 3 个伴随产物均已验证。
- 代表性查询分别得到等级 2、8、11、12；第三军医大学学报通过受控别名解析为陆军军医大学学报。
- Task 8 指定的聚焦测试为 `94 passed`；Ruff 通过；11 个镜像字节一致；未发现 v3.0 运行时或测试引用。

## 全量 mypy 门禁状态

固定可复现命令如下：

```powershell
uvx --with pydantic --with "mcp>=1,<2" mypy==2.3.0 top-journal-search-lists-env/scripts/
```

该命令退出码为 1，在 21 个源文件中报告 2 项错误，均为缺少 `playwright.async_api` 类型实现：

- `cnki_search_env/browser.py:193`
- `cnki_search_env/webvpn.py:1587`

因此，全量 mypy 门禁未全绿，状态为条件性失败。上述两个文件属于 CNKI 浏览器与 WebVPN 范围，本任务未修改它们，也未增加全局忽略规则。

作为环境差异记录，未注入项目运行时依赖的裸命令 `uvx mypy==2.3.0 top-journal-search-lists-env/scripts/` 可复现 4 项错误：除上述两项外，还缺少 `pydantic` 与 `mcp.server.fastmcp`。这不是代码新增类型错误，而是临时类型检查环境未安装项目运行时依赖所致。

除该条件性失败外，本报告所列生成器、运行时查询、聚焦测试、Ruff、镜像与旧版本引用门禁均已通过。

## 提交

- `2b66da8 test: verify environment v4 data contract`
