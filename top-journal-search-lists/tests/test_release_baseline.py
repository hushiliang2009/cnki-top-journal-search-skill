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


def test_ci_compares_release_content_across_platforms(skill_root: Path) -> None:
    """归档 SHA-256 跨平台本就不同（zlib 实现差异），因此只能比对解压后内容。

    没有这条，Windows 与 Ubuntu 构建出内容不一致的产物也不会被发现——既有的
    确定性测试只比较同一环境连续两次构建。
    """
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "Compare release content across platforms",
        "compare_release_content.py",
        "actions/download-artifact@v4",
    ):
        assert required in workflow, required


def test_compare_release_content_survives_legacy_console_encoding(
    skill_root: Path, tmp_path: Path,
) -> None:
    """Windows 控制台默认 charmap 编码打不出中文，脚本会在打印成功消息时崩溃。

    后果最坏：比对其实通过了，CI 却因输出异常报失败——排查方向会被引到
    "跨平台内容不一致"上，而真实原因只是终端编码。
    """
    import os
    import subprocess
    import sys
    import zipfile

    script = skill_root.parent / "scripts/compare_release_content.py"
    left, right = tmp_path / "a", tmp_path / "b"
    for directory in (left, right):
        directory.mkdir()
        archive = directory / "sample.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            info = zipfile.ZipInfo("payload.txt", date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, "content\n")
        (directory / "checksums.sha256").write_text(
            "0" * 64 + "  sample.zip\n", encoding="utf-8"
        )

    completed = subprocess.run(
        [sys.executable, str(script), str(left), str(right)],
        capture_output=True,
        env=os.environ | {"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"},
    )

    assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")


def test_ci_installer_job_covers_reinstall_and_rollback(skill_root: Path) -> None:
    """索引的总验收要求在三平台 CI 安装场景验证共存、重装和回滚。

    重装与回滚此前只有替身 runtime 的单元测试覆盖——那里被回滚的是替身造的空壳
    目录，而真实安装含 references 与 venv，规模与失败点都不同。
    """
    workflow = (skill_root.parent / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    installer = workflow.split("\n  installer:\n", 1)[1].split("\n  version-gate:\n", 1)[0]
    for required in (
        "Reinstall over an existing installation",
        "Roll back a failing reinstall",
    ):
        assert required in installer, required
    # 回滚场景必须注入真实失败，而不是跳过安装
    assert "fake-python" in installer
