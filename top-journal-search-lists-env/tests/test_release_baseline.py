from pathlib import Path


def test_pytest_uses_workspace_local_runtime_directory(skill_root: Path) -> None:
    config = skill_root / "pytest.ini"
    assert config.read_text(encoding="utf-8") == "[pytest]\naddopts = -p no:cacheprovider\n"
    conftest = (skill_root / "tests/conftest.py").read_text(encoding="utf-8")
    assert ' / ".pytest-runtime"' in conftest
    assert "def tmp_path()" in conftest


def test_ci_adds_environment_matrix_without_removing_generic_jobs(skill_root: Path) -> None:
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for generic in (
        "\n  ubuntu:\n",
        "\n  desktop:\n",
        "\n  installer:\n",
        "\n  version-gate:\n",
        "working-directory: top-journal-search-lists\n",
        "name: release-canonical-ubuntu-py3.11",
    ):
        assert generic in workflow
    for required in (
        "\n  env-ubuntu:\n",
        "\n  env-desktop:\n",
        "\n  env-installer:\n",
        "\n  env-version-gate:\n",
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
        'python-version: ["3.11", "3.12", "3.13", "3.14"]',
        'python-version: ["3.11"]',
        'python-version: ["3.10"]',
        "working-directory: top-journal-search-lists-env",
        "python -m pytest -q -p no:cacheprovider",
        "scripts/catalog_lookup.py validate",
        "tests/_mcp_handshake.py",
        "tests/_mcpb_handshake.py",
        "tests/_mcpb_raw_handshake.py",
        "scripts/build_release.py --output release",
        "installers/install.sh --codex",
        "installers\\install.ps1 -Codex -PythonExe python",
        "CNKI_ENV_PYTHON=python",
        "runtimes/cnki-search-env/.venv/bin/python",
        "runtimes\\cnki-search-env\\.venv\\Scripts\\python.exe",
        "name: release-environment-ubuntu-py3.11",
        "top-journal-search-lists-env/release",
        "mypy top-journal-search-lists-env/scripts/",
    ):
        assert required in workflow
    for forbidden in ("www.cnki.net", "kns.cnki.net", "webvpn", "proxy"):
        assert forbidden not in workflow.casefold()


def test_ci_uploads_separate_generic_and_environment_artifacts(skill_root: Path) -> None:
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert workflow.count("actions/upload-artifact@v4") == 2
    assert "name: release-canonical-ubuntu-py3.11" in workflow
    assert "name: release-environment-ubuntu-py3.11" in workflow


def test_root_ignore_does_not_hide_a_generated_outputs_directory() -> None:
    root_ignore = Path(__file__).resolve().parents[2] / ".gitignore"
    text = root_ignore.read_text(encoding="utf-8")
    assert "outputs/*" in text
    assert "\noutputs/\n" not in text
