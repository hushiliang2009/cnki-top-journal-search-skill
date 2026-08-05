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
        '"pytest>=8,<10"',
        "scripts/catalog_lookup.py validate",
        "tests/_mcp_handshake.py",
        "tests/_mcpb_handshake.py",
        "tests/_mcpb_raw_handshake.py",
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


def test_ci_verifies_generic_release_after_extracting_outside_the_checkout(
    skill_root: Path,
) -> None:
    """在仓库里跑通不等于用户解压后跑得通：源码树里的相对路径和同名模块都还在。

    真正要验证的是 ZIP 本身——从 RUNNER_TEMP 解压，再校验哈希、目录和两个握手。
    """
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "Verify generic release outside checkout",
        "sha256sum -c checksums.sha256",
        "generic-release-check",
        "CNKI_MCPB_PROJECT",
    ):
        assert required in workflow


def test_ci_uploads_generic_release_only_from_canonical_ubuntu_python311(
    skill_root: Path,
) -> None:
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    ubuntu_job = workflow.split("\n  ubuntu:\n", 1)[1].split("\n  desktop:\n", 1)[0]
    desktop_job = workflow.split("\n  desktop:\n", 1)[1].split("\n  installer:\n", 1)[0]
    environment_job = workflow.split("\n  env-ubuntu:\n", 1)[1].split(
        "\n  env-desktop:\n", 1
    )[0]

    assert workflow.count("actions/upload-artifact@v4") == 2
    assert "actions/upload-artifact@v4" in ubuntu_job
    assert "if: matrix.python-version == '3.11'" in ubuntu_job
    assert "name: release-canonical-ubuntu-py3.11" in ubuntu_job
    assert "actions/upload-artifact@v4" not in desktop_job
    assert "name: release-environment-ubuntu-py3.11" in environment_job


def test_root_ignore_does_not_hide_a_generated_outputs_directory() -> None:
    root_ignore = Path(__file__).resolve().parents[2] / ".gitignore"
    text = root_ignore.read_text(encoding="utf-8")
    assert "outputs/*" in text
    assert "\noutputs/\n" not in text
