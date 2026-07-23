# 跨平台安装指南 README 改版设计

## 目标

完善 `top-journal-search-lists/README.md`，使用户能够从私有 GitHub 仓库在另一台电脑上安装 `cnki-top-journal-search-skill`，并准确区分 Skill、MCP、客户端和操作系统之间的关系。

## 文档结构

README 的安装部分采用平台支持矩阵与分平台步骤结合的结构：

1. 先列出安装后的统一名称，包括界面显示名、Skill 目录名、调用名、MCP 服务名和 MCP 工具名。
2. 使用支持矩阵说明 Windows、macOS、Linux 对 Claude Code CLI、Claude Desktop、Codex CLI、Codex Desktop 的适用范围。
3. 分别提供 Windows PowerShell、macOS 终端和 Linux 终端的安装步骤。
4. 每个平台均覆盖仓库克隆、分支检出、单客户端安装、多客户端联合安装、重启和验证。
5. 单独说明更新安装、配置备份、安装位置和手工安装边界。

## 客户端与安装参数

- `-Codex` 或 `--codex` 安装到 Codex 共用目录，同时适用于 Codex CLI 和 Codex Desktop。
- `-ClaudeCode` 或 `--claude-code` 写入 Claude Code CLI 配置。
- `-ClaudeDesktop` 或 `--claude-desktop` 写入 Claude Desktop 配置。
- Claude Code CLI 与 Claude Desktop 共用 Skill 目录，但使用不同 MCP 配置文件。
- 同一命令可以组合多个目标参数。

## 平台边界

- Windows 和 macOS 提供四类客户端的操作说明。
- Linux 提供 Claude Code CLI 和 Codex CLI 的操作说明。
- README 明确说明 Claude Desktop 和 Codex Desktop 当前没有官方 Linux 客户端，不提供虚构的 Linux 桌面端安装步骤。
- Windows 下优先使用 PowerShell 安装器；WSL 属于 Linux 环境，应在 WSL 内使用 Shell 安装器，不能与 Windows 桌面客户端配置混用。

## 安装行为与安全性

自动安装器复制完整 Skill，创建独立 Python 虚拟环境，安装 `mcp` 和 `playwright`，并增量写入 `cnki-search` MCP 配置。安装器在覆盖 Skill 或修改客户端配置前生成时间戳备份，不删除现有 MCP 服务。

README 明确区分两种方式：

- 使用安装器：同时安装 Skill、运行环境和 MCP 配置。
- 手工复制 Skill 文件夹：只安装 Skill，不保证 `cnki-search` MCP 可用。

## 验证标准

文档应使用户能够确认以下结果：

- Skill 显示名为 `Top Journal and Public CNKI Search`。
- Skill 调用名为 `$top-journal-search-lists`。
- MCP 服务名为 `cnki-search`。
- MCP 仅暴露 `cnki_search(query, limit)`，其中 `limit` 最大为 20。
- 客户端重启后可以识别 Skill 和 MCP。

完成编辑后检查 Markdown 结构、命令与现有安装器参数的一致性，并运行仓库现有测试，确保文档修改未引入发布包或配置回归。
