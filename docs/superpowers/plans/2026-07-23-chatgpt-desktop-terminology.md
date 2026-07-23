# ChatGPT Desktop Terminology Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the obsolete standalone `Codex Desktop` product wording with `ChatGPT Desktop 中的 Codex` while preserving all installer and MCP behavior.

**Architecture:** Update only the README terminology and its contract tests. The test must require the current ChatGPT Desktop wording in each applicable platform section and reject standalone `Codex Desktop` wording before the README is changed.

**Tech Stack:** Markdown, Python 3.11+, pytest, Git.

## Global Constraints

- Use `ChatGPT Desktop 中的 Codex` for the desktop Codex surface.
- Do not describe `Codex Desktop` as a standalone client.
- Windows and macOS support Codex CLI and ChatGPT Desktop 中的 Codex.
- Linux supports Codex CLI and Claude Code; an official Linux ChatGPT Desktop client is not provided.
- WSL installation does not configure ChatGPT Desktop 中的 Codex on Windows.
- `-Codex` and `--codex` behavior, Skill names, MCP names, runtime paths, and backup behavior remain unchanged.
- Do not reintroduce WebVPN, advanced or professional CNKI search, login, or download behavior.

---

### Task 1: Update and verify ChatGPT Desktop terminology

**Files:**
- Modify: `top-journal-search-lists/tests/test_installers.py`
- Modify: `top-journal-search-lists/README.md`

**Interfaces:**
- Consumes: the current README platform sections and existing installer parameters.
- Produces: current product terminology without changing installation behavior.

- [ ] **Step 1: Write the failing terminology contract**

Update the README contract tests so they require:

```python
assert "ChatGPT Desktop 中的 Codex" in readme
assert "Codex Desktop" not in readme
assert "ChatGPT Desktop 中的 Codex" in windows
assert "ChatGPT Desktop 中的 Codex" in macos
assert "官方 Linux 版 ChatGPT Desktop" in linux
assert "Windows 侧 ChatGPT Desktop 中的 Codex" in wsl_text
```

Replace existing positive assertions that require `Codex Desktop`; do not weaken unrelated installation assertions.

- [ ] **Step 2: Run the focused test and verify RED**

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py -q
```

Expected: FAIL because the current README still uses `Codex Desktop` and does not contain `ChatGPT Desktop 中的 Codex`.

- [ ] **Step 3: Update README terminology**

Replace every standalone-product use of `Codex Desktop` with context-appropriate wording:

- Platform table: `Codex CLI、ChatGPT Desktop 中的 Codex、Claude Code、Claude Desktop`.
- Windows/macOS flag explanation: the Codex flag covers `Codex CLI 和 ChatGPT Desktop 中的 Codex` because both use Codex Home and `config.toml`.
- Single-target labels: `仅安装 Codex CLI 或配置 ChatGPT Desktop 中的 Codex`.
- Linux boundary: no official Linux ChatGPT Desktop client; Linux guidance covers Codex CLI and Claude Code.
- WSL boundary: does not configure `Windows 侧 ChatGPT Desktop 中的 Codex`.

Do not rename `Codex CLI`, the `-Codex`/`--codex` parameters, `.codex`, or `config.toml`.

- [ ] **Step 4: Run focused and full verification**

```text
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests/test_installers.py -q
C:\Python314\python.exe -m pytest -p no:cacheprovider top-journal-search-lists/tests -q
C:\Python314\python.exe top-journal-search-lists/scripts/catalog_lookup.py validate
git diff --check
```

Expected: focused and full tests PASS, catalog returns `valid: true`, and `git diff --check` reports no errors. Use a clean short-path copy under `C:\Users\Public\ct` for the full suite if the worktree's generated virtual environments cause Windows path-length failures.

- [ ] **Step 5: Review, commit, and push**

Confirm the README contains no standalone `Codex Desktop` wording and no installer behavior changed. Then commit and push:

```text
git add top-journal-search-lists/README.md top-journal-search-lists/tests/test_installers.py docs/superpowers/plans/2026-07-23-chatgpt-desktop-terminology.md
git commit -m "docs: update Codex desktop terminology"
git push origin agent/cnki-new-entry-only
```
