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
| Skill 显示名称（Claude Code、Codex CLI） | `top-journal-search-lists`，取自 `SKILL.md` 的 `name` 字段 |
| Skill 显示名称（ChatGPT Desktop 中的 Codex） | Top Journal and Public CNKI Search，取自 `agents/openai.yaml` |
| Skill 目录 | `top-journal-search-lists` |
| 调用方式 | `$top-journal-search-lists` |
| MCP 服务 | `cnki-search` |
| MCP 工具 | `cnki_search(query, limit)` |

`limit` 最大为 20。

## 平台与客户端支持

| 平台 | 支持的客户端 |
| --- | --- |
| Windows | Codex CLI、ChatGPT Desktop 中的 Codex、Claude Code、Claude Desktop |
| macOS | Codex CLI、ChatGPT Desktop 中的 Codex、Claude Code、Claude Desktop |
| Linux | Codex CLI、Claude Code、Claude Desktop（Linux beta） |

## 安装前准备

- 安装 Python 3.11 或更高版本，以及 Git。低于 3.11 时安装器会拒绝安装并给出提示；Windows 安装器可用 `-PythonExe` 指定解释器，macOS/Linux 安装器读取 `CNKI_PYTHON`，未指定时分别使用 `python` 和 `python3`；
- 安装 Chrome、Edge 或 Chromium。没有兼容浏览器时安装 Playwright Chromium，安装器会自动执行：

```sh
python -m playwright install chromium chromium-headless-shell
```

  两个包都要装：只装 `chromium` 不会一并落地 headless shell，无头模式仍会启动失败。
- 私有仓库需要先以具有访问权限的账号完成 GitHub 认证；
- 在 Windows、macOS 或 Linux 的终端中克隆并进入仓库：

```sh
git clone https://github.com/hushiliang2009/cnki-top-journal-search-skill.git
cd cnki-top-journal-search-skill
```

## Windows 安装指南

在仓库根目录的 PowerShell 中执行。`-Codex` 同时覆盖 Codex CLI 和 ChatGPT Desktop 中的 Codex，因为两者共用 Codex 主目录及 `config.toml`。Claude Code 和 Claude Desktop 的 MCP 配置文件不同，必须分别使用 `-ClaudeCode` 与 `-ClaudeDesktop`。

仅安装 Codex CLI 或配置 ChatGPT Desktop 中的 Codex：

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

在仓库根目录执行。`--codex` 同时覆盖 Codex CLI 和 ChatGPT Desktop 中的 Codex，因为两者共用 Codex 主目录及 `config.toml`。Claude Code 和 Claude Desktop 的 MCP 配置文件不同，必须分别使用 `--claude-code` 与 `--claude-desktop`。

仅安装 Codex CLI 或配置 ChatGPT Desktop 中的 Codex：

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

目前没有官方 Linux 版 ChatGPT Desktop。Claude Desktop 提供官方 Linux beta，支持 Ubuntu 22.04 LTS 或更高版本、Debian 12 或更高版本，以及 x64 或 arm64 架构。请先按 [Anthropic 官方安装说明](https://support.claude.com/en/articles/10065433-install-claude-desktop) 安装客户端；本节仅说明客户端已安装后的 Skill 和 MCP 配置。

安装 Codex CLI：

```sh
sh ./top-journal-search-lists/installers/install.sh --codex
```

安装 Claude Code：

```sh
sh ./top-journal-search-lists/installers/install.sh --claude-code
```

安装 Claude Desktop（Linux beta）：

```sh
sh ./top-journal-search-lists/installers/install.sh --claude-desktop
```

同时安装 Codex CLI、Claude Code 和 Claude Desktop（Linux beta）：

```sh
sh ./top-journal-search-lists/installers/install.sh --codex --claude-code --claude-desktop
```

Linux 版 Claude Desktop 的 MCP 配置文件为 `~/.config/Claude/claude_desktop_config.json`。

WSL 中的安装属于 Linux 侧安装，绝不会配置 Windows ChatGPT Desktop，即 Windows 侧 ChatGPT Desktop 中的 Codex。仅当兼容的 Linux 桌面环境中实际运行 Claude Desktop（Linux beta）时，才可在 WSL 中使用 `--claude-desktop` 配置该客户端。

## 安装器实际执行的操作

安装器复制完整 Skill，创建独立 Python 运行环境，安装 `mcp` 与 `playwright`，并执行 `python -m playwright install chromium chromium-headless-shell`。依赖安装后，安装器会进行导入检查、临时 Chromium 的离线启动和关闭，以及 MCP 自检；不会打开 CNKI 或其他网址。修改已有内容前会生成带时间戳的备份；安装失败会恢复原有 Skill 和配置，不删除 Zotero、ai4scholar 等其他 MCP 服务。安装完整成功后，每个目标仅保留最近 3 份由安装器生成的时间戳备份。

旧版 Skill 的备份写入 `<Home>/backups/skills/top-journal-search-lists.backup-<时间戳>`，位于 `skills/` 扫描目录之外。客户端按 `<Home>/skills/*/SKILL.md` 发现技能且不过滤目录名，备份若留在 `skills/` 内会被当作一个同名同描述的独立技能加载。配置文件的备份仍与原文件同目录（如 `~/.claude.json.backup-<时间戳>`），那些路径不在扫描范围内。

## 安装位置与配置文件

Codex 安装到 Codex Home 下的 `skills/top-journal-search-lists`，配置文件为 `config.toml`。Claude 安装到 Claude Home 下的 `skills/top-journal-search-lists`。只要选择 Codex，运行环境位于 Codex Home 下的 `runtimes/cnki-search`；仅选择 Claude 目标时，运行环境位于 Claude Home 下的 `runtimes/cnki-search`。Claude Code 配置文件为 `~/.claude.json`，Claude Desktop 使用其平台对应的 `claude_desktop_config.json`。

## 手工安装

手工复制仅可安装 Skill：将 `top-journal-search-lists` 文件夹复制到相应的 Skill 目录，并确保 `SKILL.md` 位于该文件夹根目录。手工复制不会自动配置 `cnki-search` MCP，也不会创建运行环境；如需 MCP，请使用对应安装器。

## 更新与重复安装

更新前先检出所需版本，再重复执行相同安装命令。安装器会备份同名 Skill 目录和已有配置文件，并更新 `cnki-search` 条目。

## 安装后验证

安装器已创建 MCP 运行环境。普通用户在仓库根目录进行目录验证；验证后重启相应客户端，确认 Skill 可调用且 `cnki-search` MCP 服务可用。

### Windows

```text
python top-journal-search-lists/scripts/catalog_lookup.py validate
python top-journal-search-lists/scripts/catalog_lookup.py lookup "American Economic Review" "Nature Human Behaviour" "经济研究"
```

### macOS/Linux

```text
python3 top-journal-search-lists/scripts/catalog_lookup.py validate
python3 top-journal-search-lists/scripts/catalog_lookup.py lookup "American Economic Review" "Nature Human Behaviour" "经济研究"
```

目录示例的预期层级分别为 1、2、6。结果按十级期刊层级排序；第二级内部按 `ncs_internal_rank` 升序排列。第七级没有独立记录时，须报告为空层级，不得伪造期刊或以其他层级记录替代。仅在用户明确提供其他目录文件时，才使用 `--catalog path/to/directory.md` 指定目录。

## 开发者完整测试

完整测试不属于普通用户安装验证。请先在开发环境安装 pytest，或使用已有包含 pytest 的 Python 环境，再在仓库根目录执行：

### Windows

```text
python -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
```

### macOS/Linux

```text
python3 -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
```

## 使用示例

```text
使用 $top-journal-search-lists 检索人工智能对审计质量影响的中英文文献，优先使用 ai4scholar，并按十级期刊层级整理。
```

```text
使用 $top-journal-search-lists 补充检索数字化转型与企业创新的近期中文论文；CNKI 仅用公开首页主题检索，返回第一页中具有篇名、期刊和发表年度的记录。
```

## 异常处理

CNKI 出现验证码、登录页、401、403、429 或页面结构变化时，立即停止当前检索；不切换入口、代理或网络出口。ai4scholar 不可用时，报告具体工具错误，不以普通网页搜索替代 MCP 结果。目录缺失或校验失败时，停止期刊层级判定。

### CNKI 返回 `challenge_detected` 怎么办

这是**知网站点侧的正常安全防护**，不是安装故障：重装 Skill、重试、更换网络都不会改变。

CNKI 检索在本工具中是尽力而为的补充能力。知网对自动化访问有站点级策略，在本工具的边界内（不登录、不使用你的浏览器配置文件、不改 User-Agent、不用代理、不做任何检测规避）可能长期无法取得结果。

遇到时请：

1. 改用 ai4scholar 完成检索（它本就是主要来源）；
2. 需要中文近期文献时，按主题词自行在知网网页端检索，再把篇名交给本工具做期刊判级：

```text
python top-journal-search-lists/scripts/catalog_lookup.py lookup "期刊名A" "期刊名B"
```

3. 在成果里如实写明"CNKI 补充检索未能执行"，不要把它当作"该主题无中文文献"。
