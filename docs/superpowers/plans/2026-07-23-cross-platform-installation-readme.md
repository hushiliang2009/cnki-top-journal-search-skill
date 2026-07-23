# Cross-Platform Installation README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the repository installation guide so users can install the Skill and `cnki-search` MCP correctly on Windows, macOS, and Linux for Claude Code, Claude Desktop, Codex CLI, and Codex Desktop.

**Architecture:** Keep installation behavior unchanged and make the README an exact reference for the existing PowerShell and POSIX Shell installers. Add a small contract test that checks the required client names, platform sections, installer commands, installed names, and the Linux desktop-client boundary.

**Tech Stack:** Markdown, Python 3.11+, pytest, PowerShell, POSIX Shell, Git.

## Global Constraints

- Skill display name is `Top Journal and Public CNKI Search`.
- Skill directory and invocation names are `top-journal-search-lists` and `$top-journal-search-lists`.
- MCP service and tool names are `cnki-search` and `cnki_search(query, limit)`; `limit` is at most 20.
- Windows and macOS guidance covers Claude Code, Claude Desktop, Codex CLI, and Codex Desktop.
- Linux guidance covers Claude Code and Codex CLI and states that official Linux desktop clients are unavailable.
- `-Codex` and `--codex` cover the shared Codex CLI and Codex Desktop configuration.
- `-ClaudeCode` or `--claude-code` and `-ClaudeDesktop` or `--claude-desktop` target separate Claude MCP configuration files.
- Automatic installation includes the Skill, isolated Python runtime, dependencies, and MCP configuration; manual Skill copying does not configure the MCP.
- Existing MCP entries must be preserved, and timestamped backup behavior must be documented.

---

### Task 1: Add and satisfy the cross-platform README contract

**Files:**
- Modify: `top-journal-search-lists/tests/test_installers.py`
- Modify: `top-journal-search-lists/README.md`

**Interfaces:**
- Consumes: existing `installers/install.ps1` parameters `-Codex`, `-ClaudeCode`, `-ClaudeDesktop`; existing `installers/install.sh` parameters `--codex`, `--claude-code`, `--claude-desktop`.
- Produces: a README installation contract that another computer can follow without inspecting installer source code.

- [x] **Step 1: Write the failing README contract test**

Append this test to `top-journal-search-lists/tests/test_installers.py`:

```python
def test_readme_documents_supported_platforms_clients_and_installed_names():
    skill_root = Path(__file__).resolve().parents[1]
    readme = (skill_root / "README.md").read_text(encoding="utf-8")

    required_text = (
        "Top Journal and Public CNKI Search",
        "$top-journal-search-lists",
        "cnki-search",
        "cnki_search(query, limit)",
        "Claude Code",
        "Claude Desktop",
        "Codex CLI",
        "Codex Desktop",
        "## Windows 安装指南",
        "## macOS 安装指南",
        "## Linux 安装指南",
        "-Codex -ClaudeCode -ClaudeDesktop",
        "--codex --claude-code --claude-desktop",
        "手工复制",
        "不会自动配置",
        "官方 Linux 桌面客户端",
    )
    for text in required_text:
        assert text in readme
```

- [x] **Step 2: Run the contract test and verify RED**

Run:

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py::test_readme_documents_supported_platforms_clients_and_installed_names -q
```

Expected: FAIL because the current README lacks the installed-name section, the three exact platform headings, combined commands, and the Linux desktop-client statement.

- [x] **Step 3: Rewrite the README installation section**

In `top-journal-search-lists/README.md`, preserve the current functional boundaries and replace the existing environment and installation sections with these sections in order:

1. `安装后的名称` table covering the Skill display name, directory, invocation, MCP service, and MCP tool.
2. `平台与客户端支持` table covering all three operating systems and four client names.
3. `安装前准备` covering Python 3.11+, Git, browser, private-repository access, and repository checkout of `agent/cnki-new-entry-only` until the branch is merged.
4. `Windows 安装指南` with separate commands for Codex CLI or Codex Desktop, Claude Code, Claude Desktop, and the combined four-client installation.
5. `macOS 安装指南` with the same client distinctions using `install.sh`.
6. `Linux 安装指南` for Codex CLI and Claude Code, plus an explicit statement that there are no official Linux Claude Desktop or Codex Desktop clients.
7. `安装器实际执行的操作`, `安装位置与配置文件`, `手工安装`, `更新与重复安装`, and `安装后验证`.

Use these exact combined commands:

```powershell
powershell -ExecutionPolicy Bypass -File .\top-journal-search-lists\installers\install.ps1 -Codex -ClaudeCode -ClaudeDesktop
```

```sh
sh ./top-journal-search-lists/installers/install.sh --codex --claude-code --claude-desktop
```

State that the Codex flag covers both Codex CLI and Codex Desktop because they share the Codex home and `config.toml`. State that Claude Code and Claude Desktop need separate flags because their MCP configuration files differ. Explain that WSL installation is a Linux-side installation and does not configure Windows desktop clients.

- [x] **Step 4: Run the focused test and verify GREEN**

Run:

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py -q
```

Expected: all `test_installers.py` tests PASS.

- [x] **Step 5: Run repository verification**

Run:

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
python top-journal-search-lists/scripts/catalog_lookup.py validate
git diff --check
```

Expected: all tests PASS, catalog validation succeeds, and `git diff --check` reports no errors.

- [x] **Step 6: Review documentation consistency**

Confirm that README commands exactly match both installers, no client is assigned to an unsupported platform, manual copying is not described as MCP installation, and no advanced/professional CNKI search, WebVPN, login, or download behavior is reintroduced.

- [x] **Step 7: Commit (completed by the primary agent as 9b6dd84; push omitted under the delegated task scope)**

```text
git add top-journal-search-lists/README.md top-journal-search-lists/tests/test_installers.py docs/superpowers/plans/2026-07-23-cross-platform-installation-readme.md
git commit -m "docs: add cross-platform installation guide"
git push origin agent/cnki-new-entry-only
```

Expected: the private GitHub branch contains the updated README, its contract test, and this implementation plan.
