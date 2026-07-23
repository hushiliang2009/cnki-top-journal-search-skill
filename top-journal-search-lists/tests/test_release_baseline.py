from pathlib import Path


def test_pytest_uses_workspace_local_runtime_directory(skill_root: Path) -> None:
    config = skill_root / "pytest.ini"
    assert config.read_text(encoding="utf-8") == "[pytest]\naddopts = -p no:cacheprovider\n"
    conftest = (skill_root / "tests/conftest.py").read_text(encoding="utf-8")
    assert ' / ".pytest-runtime"' in conftest
    assert "def tmp_path()" in conftest


def test_ci_runs_full_non_live_release_matrix(skill_root: Path) -> None:
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
        '"codex/**"',
        'python-version: ["3.11", "3.12", "3.13", "3.14"]',
        'python-version: ["3.11"]',
        "python -m pytest -q -p no:cacheprovider",
        "scripts/catalog_lookup.py validate",
        "tests/_mcp_handshake.py",
        "tests/_mcpb_handshake.py",
        "scripts/build_release.py --output release",
        "zipfile.ZipFile",
        "installer:",
        "version-gate:",
        "installers/install.sh --codex",
        "installers\\install.ps1 -Codex -PythonExe python",
        'python-version: ["3.10"]',
        "CNKI_PYTHON=python",
        "CODEX_HOME",
        "runtimes/cnki-search/.venv/bin/python",
        "runtimes\\cnki-search\\.venv\\Scripts\\python.exe",
    ):
        assert required in workflow
    for forbidden in ("www.cnki.net", "kns.cnki.net", "webvpn", "proxy"):
        assert forbidden not in workflow.casefold()


def test_root_ignore_does_not_hide_a_generated_outputs_directory() -> None:
    root_ignore = Path(__file__).resolve().parents[2] / ".gitignore"
    text = root_ignore.read_text(encoding="utf-8")
    assert "outputs/*" in text
    assert "\noutputs/\n" not in text
