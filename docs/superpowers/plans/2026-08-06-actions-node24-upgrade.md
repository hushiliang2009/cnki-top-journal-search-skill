# GitHub Actions Node.js 24 Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the four GitHub-maintained Actions used by CI to their current Node.js 24 major versions without changing either Skill, either journal catalog, or the CI matrix.

**Architecture:** Keep the workflow structure and every `with`, `if`, `needs`, matrix, artifact name, and command unchanged. Protect the intended versions with the existing release-baseline contract tests, then replace only the four `uses:` version suffixes in `.github/workflows/ci.yml`.

**Tech Stack:** GitHub Actions YAML, Python 3.11+, pytest, ruff, mypy.

## Global Constraints

- Use `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, and `actions/download-artifact@v8`.
- Require GitHub-hosted runners; do not add self-hosted runners below Actions Runner `v2.327.1`.
- Do not change general Skill version `0.5.2` or environment Skill version `0.3.2`.
- Do not change either journal catalog, group membership, journal count, or search-priority order.
- Do not change the CI job matrix, Python versions, step commands, artifact names, or release packaging behavior.

---

### Task 1: Protect and upgrade the workflow Action versions

**Files:**
- Modify: `top-journal-search-lists/tests/test_release_baseline.py`
- Modify: `top-journal-search-lists-env/tests/test_release_baseline.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the complete workflow text loaded by both `test_release_baseline.py` files.
- Produces: a workflow that retains the existing CI behavior while resolving all four official Actions through Node.js 24 major tags.

- [ ] **Step 1: Write failing workflow-contract assertions**

In both release-baseline test files, update the required Action strings to the new majors and add explicit rejection of the old majors:

```python
for required_action in (
    "actions/checkout@v7",
    "actions/setup-python@v7",
    "actions/upload-artifact@v7",
    "actions/download-artifact@v8",
):
    assert required_action in workflow

for obsolete_action in (
    "actions/checkout@v4",
    "actions/setup-python@v5",
    "actions/upload-artifact@v4",
    "actions/download-artifact@v4",
):
    assert obsolete_action not in workflow
```

Update existing count and job-section assertions from `actions/upload-artifact@v4` to `actions/upload-artifact@v7`, and from `actions/download-artifact@v4` to `actions/download-artifact@v8`.

The production change this test catches is a rollback of any official Action to its Node.js 20 major or an incomplete upgrade in one of the repeated jobs.

- [ ] **Step 2: Run the focused tests and verify RED**

Run in separate Python processes:

```powershell
python -m pytest -q top-journal-search-lists/tests/test_release_baseline.py
python -m pytest -q top-journal-search-lists-env/tests/test_release_baseline.py
```

Expected: both commands fail because `.github/workflows/ci.yml` still contains `checkout@v4`, `setup-python@v5`, `upload-artifact@v4`, and `download-artifact@v4`.

- [ ] **Step 3: Apply the minimal workflow change**

Replace only these strings throughout `.github/workflows/ci.yml`:

```text
actions/checkout@v4          -> actions/checkout@v7
actions/setup-python@v5      -> actions/setup-python@v7
actions/upload-artifact@v4   -> actions/upload-artifact@v7
actions/download-artifact@v4 -> actions/download-artifact@v8
```

Do not edit any adjacent inputs or steps.

- [ ] **Step 4: Run focused tests and verify GREEN**

```powershell
python -m pytest -q top-journal-search-lists/tests/test_release_baseline.py
python -m pytest -q top-journal-search-lists-env/tests/test_release_baseline.py
```

Expected: general `8 passed`; environment `7 passed`.

- [ ] **Step 5: Verify exact workflow scope**

```powershell
rg -n "uses:\s*actions/" .github/workflows/ci.yml
git diff -- .github/workflows/ci.yml
git diff --name-only
```

Expected: every official Action reference uses the four approved majors; the workflow diff contains only version suffix changes; changed files are limited to the workflow, two contract tests, this plan, and the approved design document.

- [ ] **Step 6: Run both complete test suites separately**

```powershell
Push-Location top-journal-search-lists
python -m pytest -q -p no:cacheprovider
Pop-Location
Push-Location top-journal-search-lists-env
python -m pytest -q -p no:cacheprovider
Pop-Location
```

Expected: both commands exit `0`. If the restricted Windows environment returns Win32 error 5 while creating Git Bash or subprocess pipes, rerun only those failed tests outside the sandbox and record both results.

- [ ] **Step 7: Run static, catalog, and formatting validation**

```powershell
$env:PYTHONUTF8='1'
python -m ruff check top-journal-search-lists top-journal-search-lists-env
python -m mypy top-journal-search-lists/scripts/cnki_search top-journal-search-lists-env/scripts/cnki_search_env
python top-journal-search-lists/scripts/catalog_lookup.py validate
python top-journal-search-lists-env/scripts/catalog_lookup.py validate
python top-journal-search-lists-env/scripts/generate_environment_catalog_v4.py --check
git diff --check
```

Expected: all commands exit `0`; general catalog reports 10 levels and environment catalog reports 12 levels.

- [ ] **Step 8: Commit the implementation**

```powershell
git add .github/workflows/ci.yml top-journal-search-lists/tests/test_release_baseline.py top-journal-search-lists-env/tests/test_release_baseline.py docs/superpowers/plans/2026-08-06-actions-node24-upgrade.md
git commit -m "ci: upgrade official Actions to Node.js 24"
```

- [ ] **Step 9: Push and verify the independent pull request**

Push branch `codex/actions-node24-upgrade`, create an independent pull request against `main`, and require its full cross-platform CI to pass. Verify that the completed run no longer emits Node.js 20 deprecation annotations before merging.
