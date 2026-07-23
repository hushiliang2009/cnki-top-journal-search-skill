# Linux 桌面客户端支持范围更正设计

## 事实依据

截至当前官方资料，ChatGPT Desktop 仅提供 macOS 和 Windows 版本；Claude Desktop 已正式提供 Linux beta，支持 Ubuntu 22.04 LTS 以上或 Debian 12 以上，并覆盖 x64 和 arm64。

## 修订目标

更正 README 和契约测试中 Claude Desktop 不支持 Linux 的错误表述。Linux 平台应列为支持 Codex CLI、Claude Code 和 Claude Desktop beta，仅 ChatGPT Desktop 中的 Codex 没有官方 Linux 桌面版本。

## README 修订

- Linux 支持表改为 `Codex CLI、Claude Code、Claude Desktop（Linux beta）`。
- Linux 章节明确 ChatGPT Desktop 当前没有官方 Linux 版本。
- Linux 章节提供 Claude Desktop 单独安装命令。
- Linux 联合安装命令改为包含 `--codex --claude-code --claude-desktop`。
- 说明 Linux Claude Desktop MCP 配置写入 `~/.config/Claude/claude_desktop_config.json`。
- WSL 仍视为 Linux 环境；是否配置 Claude Desktop 取决于 WSL 内是否实际运行对应 Linux 桌面环境，不自动配置 Windows 侧 ChatGPT Desktop。

## 契约测试修订

- 删除 `Claude Desktop 也不支持 Linux` 的错误断言。
- 要求 Linux 分段包含 `Claude Desktop（Linux beta）`。
- 要求 Linux 分段包含 `--claude-desktop` 单独安装命令和三客户端联合安装命令。
- 继续要求 Linux 分段明确没有官方 ChatGPT Desktop。
- 继续禁止使用独立产品名称 `Codex Desktop`。

## 不变内容

- 不修改 PowerShell 或 Shell 安装器。
- 不修改 Skill、MCP、运行环境和备份行为。
- 不重新引入 WebVPN、高级或专业检索、登录或下载功能。

## 验证标准

- 新契约测试在旧 README 上按预期失败。
- 修订后聚焦测试和完整测试通过。
- 期刊目录校验返回 `valid: true`。
- `git diff --check` 无错误。
