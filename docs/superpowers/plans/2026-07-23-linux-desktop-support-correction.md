# Linux Desktop Support Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the Linux installation guide so it supports Claude Desktop beta while continuing to state that no official ChatGPT Desktop is available for Linux.

**Architecture:** Change only README content and its contract tests. Preserve the existing POSIX installer because it already supports `--claude-desktop` and writes the Linux Claude Desktop MCP configuration path.

**Tech Stack:** Markdown, Python 3.11+, pytest, POSIX Shell, Git.

## Global Constraints

- Linux supports Codex CLI, Claude Code, and Claude Desktop beta.
- Linux does not have an official ChatGPT Desktop release.
- Linux Claude Desktop requires Ubuntu 22.04 LTS+ or Debian 12+, on x64 or arm64, according to Anthropic's current official installation page.
- The Skill installer flag for Linux Claude Desktop is `--claude-desktop`.
- The Linux three-client combined command is `sh ./top-journal-search-lists/installers/install.sh --codex --claude-code --claude-desktop`.
- Linux Claude Desktop MCP configuration is written to `~/.config/Claude/claude_desktop_config.json`.
- WSL is a Linux-side installation and does not configure Windows ChatGPT Desktop; Claude Desktop configuration in WSL is useful only when a compatible Linux desktop environment and Claude Desktop beta are actually present there.
- Do not change installer code, Skill names, MCP names, runtime paths, or backup behavior.
- Do not reintroduce WebVPN, advanced or professional CNKI search, login, or download behavior.

---

### Task 1: Correct README and Linux support contracts

**Files:**
- Modify: `top-journal-search-lists/tests/test_installers.py`
- Modify: `top-journal-search-lists/README.md`

**Interfaces:**
- Consumes: existing `installers/install.sh --claude-desktop` behavior and Linux Claude Desktop configuration path.
- Produces: a Linux guide that accurately distinguishes ChatGPT Desktop from Claude Desktop beta.

- [ ] **Step 1: Write the failing Linux support contract**

Update the Linux README contract to require:

```python
assert "Claude Desktop（Linux beta）" in linux
assert "目前没有官方 Linux 版 ChatGPT Desktop" in linux
assert "Claude Desktop 也不支持 Linux" not in linux
assert "sh ./top-journal-search-lists/installers/install.sh --claude-desktop" in linux
assert (
    "sh ./top-journal-search-lists/installers/install.sh "
    "--codex --claude-code --claude-desktop"
) in linux
assert "~/.config/Claude/claude_desktop_config.json" in linux
```

Keep the existing requirement that the README does not use the standalone product name `Codex Desktop`.

- [ ] **Step 2: Run the focused test and verify RED**

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py -q
```

Expected: FAIL because the README still says Claude Desktop does not support Linux and lacks the Linux beta installation commands.

- [ ] **Step 3: Correct the README**

Apply these changes:

1. Platform table Linux row: `Codex CLI、Claude Code、Claude Desktop（Linux beta）`.
2. Linux introduction: state that ChatGPT Desktop currently has no official Linux release, while Claude Desktop has an official Linux beta.
3. State the Claude Desktop Linux beta requirements: Ubuntu 22.04 LTS+, Debian 12+, x64 or arm64.
4. Link to Anthropic's official install page: `https://support.claude.com/en/articles/10065433-install-claude-desktop`.
5. Add a single-client Skill/MCP installation command using `--claude-desktop`.
6. Replace the two-client combined command with the three-client combined command.
7. State the Linux Claude Desktop MCP configuration path.
8. Clarify WSL: it never configures Windows ChatGPT Desktop; `--claude-desktop` in WSL only targets a Linux Claude Desktop beta installation actually running in a compatible Linux desktop environment.

Do not copy Anthropic's system-level APT commands into this repository installer section. Link to the official client installation page and keep this README focused on installing the Skill and MCP after the client exists.

- [ ] **Step 4: Run focused and full verification**

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py -q
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
C:\Python314\python.exe top-journal-search-lists/scripts/catalog_lookup.py validate
git diff --check
```

Expected: focused and full tests PASS, catalog returns `valid: true`, and `git diff --check` reports no errors. Use a clean short-path copy under `C:\Users\Public\ct` for the full suite if required.

- [ ] **Step 5: Review, commit, and push**

Confirm that only README, tests, and this plan changed, and that no false Linux desktop claim remains. Then:

```text
git add top-journal-search-lists/README.md top-journal-search-lists/tests/test_installers.py docs/superpowers/plans/2026-07-23-linux-desktop-support-correction.md
git commit -m "docs: correct Linux desktop support"
git push origin agent/cnki-new-entry-only
```
