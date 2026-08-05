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


def test_ci_verifies_environment_release_after_extracting_outside_the_checkout(
    skill_root: Path,
) -> None:
    """环境版还多一条：解压后必须能用随包脚本把 v4.0 目录原样复算出来。"""
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "Verify environment release outside checkout",
        "sha256sum -c checksums.sha256",
        "environment-release-check",
        "CNKI_ENV_MCPB_PROJECT",
        'generate_environment_catalog_v4.py" --check',
    ):
        assert required in workflow


def test_ci_env_installer_job_installs_both_products_side_by_side(
    skill_root: Path,
) -> None:
    """共存只在两版真的一起装过之后才算验证过；单独装环境版证明不了不覆盖通用版。"""
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    env_installer = workflow.split("\n  env-installer:\n", 1)[1].split(
        "\n  env-version-gate:\n", 1
    )[0]
    for required in (
        "top-journal-search-lists/installers/install.sh --codex",
        "top-journal-search-lists-env/installers/install.sh --codex",
        "top-journal-search-lists\\installers\\install.ps1 -Codex -PythonExe python",
        "top-journal-search-lists-env\\installers\\install.ps1 -Codex -PythonExe python",
        "runtimes/cnki-search/.venv/bin/python",
        "runtimes/cnki-search-env/.venv/bin/python",
    ):
        assert required in env_installer


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


def test_ci_compares_environment_release_content_across_platforms(skill_root: Path) -> None:
    """环境版同样需要跨平台内容比对；归档哈希受 zlib 实现影响，不能作为判据。"""
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "Compare release content across platforms" in workflow
    assert "release-environment-ubuntu-py3.11\n          path: ci-ubuntu-release" in workflow
    assert (
        "compare_release_content.py top-journal-search-lists-env/release ci-ubuntu-release"
        in workflow
    )
