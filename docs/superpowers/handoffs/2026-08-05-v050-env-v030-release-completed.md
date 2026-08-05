# 通用版 v0.5.0 与环境版 v0.3.0 发布完成记录

本文件承接 `2026-08-03-codex-continuation.md`。该文件记录的是 2026-08-03 当时的事实
（CNKI 计划 Task 4 未完成、发布计划尚未执行），按既有约定不追溯改写；本文件记录
2026-08-05 的完成状态。

## 结论

两个计划全部完成并已发布。

- 合并提交：`0160cb6`（PR #18 squash 合并进 `main`）
- 标签：`v0.5.0`、`top-journal-search-lists-env-v0.3.0`，均指向 `0160cb6`
- Release：两个独立 Release，各三件附件

| 产物 | SHA-256 |
|---|---|
| `top-journal-search-lists_Skill.zip` | `2f8751fc51c4888ec8aa74d42641a579cf45650e7a6391fad005449733cc18ec` |
| `cnki-search.mcpb` | `00808bade8c5b4916fba8c81231fc5d6e0e5eb7c859ba42402eb2873713debbc` |
| `top-journal-search-lists-env_Skill.zip` | `70eaca5c148924db56954760109a4ce33c4995fab34b91391b8f0fe257b81817` |
| `cnki-search-env.mcpb` | `c09468fc55ce88a8bb9541cb85fc2eae4d585225954fc6b2f630d72a03857558` |

产物取自 `main` 分支 CI run `30982468175` 的 `release-canonical-ubuntu-py3.11` 与
`release-environment-ubuntu-py3.11`，未复用旧附件；Release 建好后重新下载复核，
哈希与规范 artifact 一致。

## 本次会话的提交

| 提交 | 内容 | 独立审查 |
|---|---|---|
| `eb2328f` | 环境版版本、manifest、锁文件升至 0.3.0 | APPROVED |
| `ac691e7` | 把两个离线复算脚本与握手脚本纳入发布白名单 | APPROVED |
| `1b6eeb4` | CI 增加工作区外解压校验；env-installer 实装两版 | NEEDS_FIX → 修复后 APPROVED |
| `264d769` | 修复发布布局下 `--check` 必然失败 | APPROVED |
| `d970926` | 仓库根 `.gitattributes` 固定 `docs/audits/` 为 LF | 随后续审查一并核验 |
| `98041af` | 补充离线复算脚本的使用文档 | NEEDS_FIX |
| `55fd1ec` | 修正文档对校验范围的夸大表述 | APPROVED |
| `99399b4` | 点明来源快照的字节与 SHA-256 锁定，弱化 checksum 表述 | APPROVED |

CNKI 计划 Task 1—3 与环境目录 v4.0 计划 8 项任务在更早的会话完成，见
`2026-08-03-codex-continuation.md`。

## 发布前修掉的两个实质问题

### 1. 打包的离线复算脚本在收件人处必然失败

`generate_environment_catalog_v4.py --check` 把 `docs/audits/` 下的完整审计当作硬性
前提，而该目录按发布约定只留在仓库、不进任何发布包。结果是随 Skill ZIP 发出的复算
脚本在用户那边必报"生成文件不一致"，新增的 CI 解压校验也会稳定失败。

修复：仓库布局（存在 `docs/audits/` 或 `.git/`）照旧校验审计输出；发布布局跳过并在
输出中明说。`.git/` 这一半是必要的——只看 `docs/audits/` 会让仓库中误删审计目录的
情况被静默跳过，而不是报错。

### 2. 文档夸大了 `--check` 的验证保证

初稿写"层级由脚本重新算出""能查出层级被改动"。实测反例：把 `ENVJ-000004` 与
`ENVJ-000005` 的 payload 对调（ID 留原位，每级计数不变）后重新生成，`--check` 退出 0，
而目录里 Nature Cities 已升到第 1 级、The Lancet 降到第 2 级。

层级取自已批准的 v4.0 目录 markdown 的表格分组，脚本不推导它，只核对每级期刊数与
字节一致。文档已改为如实区分「脚本重算的」（来源匹配、索引收录、交叉收录、审计摘要）
与「取自 baseline 的」（层级、细分领域、正式证据、期刊清单），并说明这是自洽性校验
而非真实性校验。

附带发现：连 ENVJ ID 一起对调会被 `目录优先级签名顺序错误` 拦下，即 ID 单调顺序有
保护，但"某 ID 对应哪本刊、哪个层级"没有。

## 真实站点冒烟（发布门槛）

在河海大学 WebVPN、人工值守、可见浏览器下完成，两版均通过：

- 通用版 `--group cssci`：`topic_fields_tried=["TI"]`、`source_category_code=P0209`、
  `source_category_applied=true`、`complete=true`
- 环境版 `--group pku_core`：`source_category_code=P01`、`source_category_applied=true`，
  返回记录判级出现第 6、7 级

这一步验证了单元测试只能用 fixture 模拟的四件事：字段确实以 `TI` 提交、来源类别在真实
结果页上确实勾中并生效、目录判级对真实刊名有效、首页限额与去重正确。

## 发布后审计

从 `main`(`0160cb6`) 本地重建两个产品，与已发布产物逐成员比对：**225 处差异全部是换行，
内容真实差异为 0**，成员集合相同。已发布产物内容与 `main` 完全对应。

但由此发现产物在 Windows 检出下无法复现官方 SHA-256，见 Issue #21。现有确定性测试只验证
"同一环境连续两次构建字节一致"，因此发现不了跨平台差异。

## 已知遗留

- Issue #19：安装器缺 Windows 长路径预检。深 `CODEX_HOME` 下 pip 解包 playwright 会超
  MAX_PATH。默认 `%USERPROFILE%\.codex` 很短，不受影响。
- Issue #20：Playwright 浏览器版本不匹配时，`BrowserUnavailableError` 提示指向"没有图形
  界面"，会把排查引向错误方向；`_webvpn_e2e.py` 的安全守卫把这类无敏感信息的环境问题
  也一并吞成 `webvpn_e2e_failed`。
- Issue #21：发布产物跨平台不可复现（`.gitattributes` 覆盖不全），并附带
  `top-journal-search-lists-env/.gitattributes` 中指向已删除 v3.0 文件的残留配置。
- Issue #22：索引「总验收顺序」要求在三平台 CI 安装场景验证共存、重装和回滚，其中
  共存已由真实安装作业覆盖，重装与回滚只有替身 runtime 的单元测试覆盖。属验收覆盖
  缺口，不是已知缺陷。

## 验收状态

三份计划共 23 项任务全部完成。索引「总验收顺序」六条中五条完全满足，第四条
（三平台 CI 安装场景的共存、重装、回滚）部分满足，差额见 Issue #22。

## 环境注意事项

- Windows 上 `core.autocrlf=true`。仓库根 `.gitattributes` 现已把 `docs/audits/` 固定为
  LF，否则仓库布局下的 `--check` 会因 CRLF 而误报不一致。
- 本机 GBK 代码页：跑 pytest 与实机脚本需要 `PYTHONUTF8=1`，否则个别用例会因
  `UnicodeDecodeError` 失败。PowerShell 5.1 按 ANSI 读取 `.ps1`，自写脚本应保持纯 ASCII。
- 通用版与环境版 pytest 必须分进程运行，避免顶层同名 `catalog_lookup` 互相污染。
- Playwright 升级后需补下对应版本浏览器（`python -m playwright install chromium`），
  否则 WebVPN 专业检索无法启动。
