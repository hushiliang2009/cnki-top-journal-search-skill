# Top Journal Search Lists 使用指南

## 功能与边界

本 Skill 以 ai4scholar 为主要来源，检索和整理中英文研究；CNKI 是近期中文论文的补充来源。CNKI MCP 仅从中国知网公开首页执行主题检索，仅读取第一页，最多返回 20 条期刊记录，并依据内置综合期刊目录完成判级。

正式结果包含篇名、期刊、发表年度、期刊层级和 `sources`。程序不登录、不下载、不持久化 Cookie，不持久化缓存，运行期仅24小时内存缓存；不读取用户浏览器配置或历史状态，不访问结果详情页面。用户如需全文，应自行通过合法渠道下载。

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

压缩包不包含账户信息、Cookie、Local State、浏览器缓存或检索结果缓存。这里的缓存边界是：不持久化缓存，运行期仅24小时内存缓存。

## 安装后的名称

| 项目 | 安装后的名称 |
| --- | --- |
| Skill 显示名称 | Top Journal and Public CNKI Search |
| Skill 目录 | `top-journal-search-lists` |
| 调用方式 | `$top-journal-search-lists` |
| MCP 服务 | `cnki-search` |
| MCP 工具 | `cnki_search(query, limit)` |

`limit` 最大为 20。

## 平台与客户端支持

| 平台 | 支持的客户端 |
| --- | --- |
| Windows | Codex CLI、Codex Desktop、Claude Code、Claude Desktop |
| macOS | Codex CLI、Codex Desktop、Claude Code、Claude Desktop |
| Linux | Codex CLI、Claude Code |

## 安装前准备

- 安装 Python 3.11 或更高版本，以及 Git；
- 安装 Chrome、Edge 或 Chromium。没有兼容浏览器时，可安装 Playwright Chromium；
- 确保当前账户具有私有仓库访问权限，并已检出本仓库；
- 在 `agent/cnki-new-entry-only` 分支合并前，请检出该分支以取得本安装指南及安装器。

## Windows 安装指南

在仓库根目录的 PowerShell 中执行。`-Codex` 同时覆盖 Codex CLI 和 Codex Desktop，因为两者共用 Codex 主目录及 `config.toml`。Claude Code 和 Claude Desktop 的 MCP 配置文件不同，必须分别使用 `-ClaudeCode` 与 `-ClaudeDesktop`。

仅安装 Codex CLI 或 Codex Desktop：

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -Codex
```

仅安装 Claude Code：

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -ClaudeCode
```

仅安装 Claude Desktop：

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -ClaudeDesktop
```

同时安装四个客户端：

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -Codex -ClaudeCode -ClaudeDesktop
```

## macOS 安装指南

在仓库根目录执行。`--codex` 同时覆盖 Codex CLI 和 Codex Desktop，因为两者共用 Codex 主目录及 `config.toml`。Claude Code 和 Claude Desktop 的 MCP 配置文件不同，必须分别使用 `--claude-code` 与 `--claude-desktop`。

仅安装 Codex CLI 或 Codex Desktop：

```sh
sh ./top-journal-search-lists/installers/install.sh --codex
```

仅安装 Claude Code：

```sh
sh ./top-journal-search-lists/installers/install.sh --claude-code
```

仅安装 Claude Desktop：

```sh
sh ./top-journal-search-lists/installers/install.sh --claude-desktop
```

同时安装四个客户端：

```sh
sh ./top-journal-search-lists/installers/install.sh --codex --claude-code --claude-desktop
```

## Linux 安装指南

Linux 支持 Codex CLI 和 Claude Code。官方 Linux 桌面客户端不提供 Claude Desktop 或 Codex Desktop，因此不要使用 `--claude-desktop` 配置桌面客户端。

安装 Codex CLI：

```sh
sh ./top-journal-search-lists/installers/install.sh --codex
```

安装 Claude Code：

```sh
sh ./top-journal-search-lists/installers/install.sh --claude-code
```

WSL 中的安装属于 Linux 侧安装，只配置 WSL 内的 Codex CLI 或 Claude Code，不会自动配置 Windows 桌面客户端。

## 安装器实际执行的操作

安装器复制完整 Skill，创建独立 Python 运行环境，安装 `mcp` 与 `playwright`，并仅向所选客户端增量写入 `cnki-search` MCP 配置。修改已有配置前会生成带时间戳的备份，不删除 Zotero、ai4scholar 等其他 MCP 服务。

## 安装位置与配置文件

Codex 安装到 `.codex/skills/top-journal-search-lists`，运行环境位于 `.codex/runtimes/cnki-search`，配置文件为 `.codex/config.toml`。Claude 安装到 `.claude/skills/top-journal-search-lists`，运行环境位于 `.claude/runtimes/cnki-search`。Claude Code 配置文件为 `~/.claude.json`，Claude Desktop 使用其平台对应的 `claude_desktop_config.json`。

## 手工安装

手工复制仅可安装 Skill：将 `top-journal-search-lists` 文件夹复制到相应的 Skill 目录，并确保 `SKILL.md` 位于该文件夹根目录。手工复制不会自动配置 `cnki-search` MCP，也不会创建运行环境；如需 MCP，请使用对应安装器。

## 更新与重复安装

更新前先检出所需版本，再重复执行相同安装命令。安装器会备份同名 Skill 目录和已有配置文件，并更新 `cnki-search` 条目。

## 安装后验证

在仓库根目录运行：

```text
python top-journal-search-lists/scripts/catalog_lookup.py validate
python top-journal-search-lists/scripts/catalog_lookup.py lookup "American Economic Review" "Nature Human Behaviour" "经济研究"
python -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
```

目录示例的预期层级分别为 1、2、6。安装后重启相应客户端，再调用 `cnki_search(query, limit)` 验证 MCP 服务。结果按十级期刊层级排序；第二级内部按 `ncs_internal_rank` 升序排列。第七级没有独立记录时，须报告为空层级，不得伪造期刊或以其他层级记录替代。仅在用户明确提供其他目录文件时，才使用 `--catalog path/to/directory.md` 指定目录。

## 使用示例

```text
使用 $top-journal-search-lists 检索人工智能对审计质量影响的中英文文献，优先使用 ai4scholar，并按十级期刊层级整理。
```

```text
使用 $top-journal-search-lists 补充检索数字化转型与企业创新的近期中文论文；CNKI 仅用公开首页主题检索，返回第一页中具有篇名、期刊和发表年度的记录。
```

## 异常处理

CNKI 出现验证码、登录页、401、403、429 或页面结构变化时，立即停止当前检索；不切换入口、代理或网络出口。ai4scholar 不可用时，报告具体工具错误，不以普通网页搜索替代 MCP 结果。目录缺失或校验失败时，停止期刊层级判定。
