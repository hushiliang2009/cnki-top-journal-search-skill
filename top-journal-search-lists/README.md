# Top Journal Search Lists 使用指南

## 功能与边界

本 Skill 以 ai4scholar 为主要来源，检索和整理中英文研究；CNKI 是近期中文论文的补充来源。CNKI MCP 仅从中国知网公开首页执行主题检索，仅读取第一页，最多返回 20 条期刊记录，并依据内置综合期刊目录完成判级。

正式结果包含篇名、期刊、发表年度、期刊层级和 `sources`。程序不登录、不下载、不持久化 Cookie，不读取用户浏览器配置或历史状态，不访问结果详情页面。用户如需全文，应自行通过合法渠道下载。

## 压缩包内容

```text
top-journal-search-lists/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── installers/
├── references/
├── scripts/
└── mcpb/
```

压缩包不包含账户信息、Cookie、Local State、浏览器缓存或检索结果缓存。

## 环境要求

- Windows、macOS 或 Linux；
- Python 3.11 或更高版本；
- CNKI MCP 运行时依赖 `mcp` 与 `playwright`；
- 系统已安装 Chrome、Edge 或 Chromium。没有兼容浏览器时，可安装 Playwright Chromium；
- 文件统一使用 UTF-8。

## 安装

安装器复制完整 Skill、创建独立 Python 环境，并仅向所选客户端增量写入 `cnki-search` MCP 配置。修改已有配置前会生成时间戳备份，不删除 Zotero、ai4scholar 等其他 MCP 服务。

Windows PowerShell：

```text
powershell -ExecutionPolicy Bypass -File installers/install.ps1 -Codex
powershell -ExecutionPolicy Bypass -File installers/install.ps1 -ClaudeCode
powershell -ExecutionPolicy Bypass -File installers/install.ps1 -ClaudeDesktop
```

macOS 或 Linux：

```text
sh installers/install.sh --codex
sh installers/install.sh --claude-code
sh installers/install.sh --claude-desktop
```

可在同一命令中指定多个目标。手工安装时，将 `top-journal-search-lists` 文件夹复制到 Codex 的 `.codex/skills` 或 Claude Code 的 `.claude/skills` 目录，确保 `SKILL.md` 位于该文件夹根目录。

## 验证

在 Skill 根目录运行：

```text
python scripts/catalog_lookup.py validate
python scripts/catalog_lookup.py lookup "American Economic Review" "Nature Human Behaviour" "经济研究"
python -m pytest -p no:cacheprovider tests -q
```

目录示例的预期层级分别为 1、2、6。MCP 只暴露 `cnki_search(query, limit)`；安装后重启相应客户端再验证。

结果按十级期刊层级排序；第二级内部按 `ncs_internal_rank` 升序排列。第七级没有独立记录时，须报告为空层级，不得伪造期刊或以其他层级记录替代。仅在用户明确提供其他目录文件时，才使用 `--catalog path/to/directory.md` 指定目录。

## 使用示例

```text
使用 $top-journal-search-lists 检索人工智能对审计质量影响的中英文文献，优先使用 ai4scholar，并按十级期刊层级整理。
```

```text
使用 $top-journal-search-lists 补充检索数字化转型与企业创新的近期中文论文；CNKI 仅用公开首页主题检索，返回第一页中具有篇名、期刊和发表年度的记录。
```

## 异常处理

CNKI 出现验证码、登录页、401、403、429 或页面结构变化时，立即停止当前检索；不切换入口、代理或网络出口。ai4scholar 不可用时，报告具体工具错误，不以普通网页搜索替代 MCP 结果。目录缺失或校验失败时，停止期刊层级判定。
