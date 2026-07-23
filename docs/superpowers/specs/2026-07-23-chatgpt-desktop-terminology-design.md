# ChatGPT Desktop 中的 Codex 术语修订设计

## 目标

依据 OpenAI 当前官方产品说明，将安装指南中的 `Codex Desktop` 更新为 `ChatGPT Desktop 中的 Codex`，准确反映 Codex 已整合到新版 ChatGPT 桌面应用的产品关系。

## 修订范围

- 将 README 平台支持表中的 `Codex Desktop` 改为 `ChatGPT Desktop 中的 Codex`。
- 将 Windows 和 macOS 安装说明改为：`-Codex` 或 `--codex` 同时配置 Codex CLI 与 ChatGPT Desktop 中的 Codex，因为二者共用 Codex 主目录和 `config.toml`。
- 将 Linux 边界改为：官方 Linux 版 ChatGPT Desktop 当前未提供，因此 Linux 仅说明 Codex CLI 与 Claude Code。
- 将 WSL 边界改为：WSL 内安装不会配置 Windows 侧 ChatGPT Desktop 中的 Codex。
- 更新 README 契约测试，使其要求新术语并拒绝 README 继续使用独立产品名称 `Codex Desktop`。

## 不变内容

- Skill 显示名、目录名和调用名保持不变。
- `cnki-search` MCP 服务名和 `cnki_search(query, limit)` 工具名保持不变。
- PowerShell 与 Shell 安装器的参数和行为保持不变。
- Claude Code、Claude Desktop、Codex CLI 的名称和安装方式保持不变。
- 不改变支持平台、运行环境位置、配置备份和手工安装边界。

## 验证标准

- README 不再把 `Codex Desktop` 作为独立客户端名称使用。
- Windows 与 macOS 使用 `ChatGPT Desktop 中的 Codex`。
- Linux 和 WSL 边界使用更新后的 ChatGPT Desktop 术语。
- 安装器契约测试先因旧术语失败，修订后通过。
- 完整测试、期刊目录校验和 `git diff --check` 通过。
