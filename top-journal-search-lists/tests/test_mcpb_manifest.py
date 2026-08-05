import hashlib
import json
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from cnki_search import mcp_server


CNKI_MODULES = (
    "__init__.py",
    "browser.py",
    "cache.py",
    "install_config.py",
    "mcp_server.py",
    "models.py",
    "professional.py",
    "professional_runtime.py",
    "professional_service.py",
    "ranking.py",
    "rate_limit.py",
    "results.py",
    "search.py",
    "service.py",
    "session.py",
    "webvpn.py",
)
TEST_RELATIVE = (
    "tests/_mcp_handshake.py",
    "tests/_mcpb_handshake.py",
    "tests/_mcpb_raw_handshake.py",
    "tests/_webvpn_probe.py",
    "tests/conftest.py",
    "tests/test_catalog_groups.py",
    "tests/test_catalog_lookup.py",
    "tests/test_cnki_cache.py",
    "tests/test_cnki_async.py",
    "tests/test_cnki_mcp.py",
    "tests/test_cnki_models.py",
    "tests/test_cnki_package_contract.py",
    "tests/test_cnki_professional.py",
    "tests/test_cnki_professional_mcp.py",
    "tests/test_cnki_professional_runtime.py",
    "tests/test_cnki_professional_service.py",
    "tests/test_cnki_ranking.py",
    "tests/test_cnki_rate_limit.py",
    "tests/test_cnki_results.py",
    "tests/test_cnki_search.py",
    "tests/test_cnki_service.py",
    "tests/test_cnki_session.py",
    "tests/test_cnki_source_category.py",
    "tests/test_cnki_webvpn.py",
    "tests/test_cnki_webvpn_outcome.py",
    "tests/test_cnki_webvpn_page.py",
    "tests/test_installers.py",
    "tests/test_install_config_security.py",
    "tests/test_mcpb_manifest.py",
    "tests/fixtures/public_challenge.html",
    "tests/fixtures/public_home.html",
    "tests/fixtures/public_incomplete_results.html",
    "tests/fixtures/public_no_results.html",
    "tests/fixtures/public_results.html",
    "tests/fixtures/public_results_nested_table.html",
    "tests/fixtures/public_results_stage3b.html",
    "tests/fixtures/public_results_stage3b_missing_td.html",
    "tests/fixtures/public_results_stage3b_missing_tr.html",
    "tests/fixtures/public_results_with_paper_titles.html",
)
EXPECTED_SKILL_RELATIVE = (
    "README.md",
    "SKILL.md",
    "pytest.ini",
    "agents/openai.yaml",
    "installers/install.ps1",
    "installers/install.sh",
    "mcpb/.mcpbignore",
    "mcpb/manifest.json",
    "mcpb/pyproject.toml",
    "mcpb/src/catalog_lookup.py",
    *(f"mcpb/src/cnki_search/{name}" for name in CNKI_MODULES),
    "mcpb/src/references/Academic_Journal_Master_Directory_20260715.md",
    "mcpb/src/server.py",
    "mcpb/uv.lock",
    "references/Academic_Journal_Master_Directory_20260715.md",
    "references/cnki-search-reference.md",
    "scripts/build_release.py",
    "scripts/catalog_lookup.py",
    *(f"scripts/cnki_search/{name}" for name in CNKI_MODULES),
    *TEST_RELATIVE,
)
EXPECTED_MCPB_RELATIVE = tuple(
    relative.removeprefix("mcpb/")
    for relative in EXPECTED_SKILL_RELATIVE
    if relative.startswith("mcpb/")
)


def _load_builder(skill_root: Path):
    builder_path = skill_root / "scripts/build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_public_build", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXPECTED_VERSION = "0.5.0"
EXPECTED_TOOLS = [
    {
        "name": "cnki_search",
        "description": "Search the public CNKI homepage by topic and rank first-page journal records.",
    },
    {
        "name": "cnki_professional_search",
        "description": (
            "Run attended CNKI professional journal search through institutional WebVPN; "
            "the user must sign in, keep the browser open, and complete security checks."
        ),
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_mcpb_manifest_is_uv_cross_platform_and_safe(skill_root: Path) -> None:
    manifest = json.loads((skill_root / "mcpb/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.4"
    assert manifest["name"] == "cnki-search"
    assert manifest["display_name"] == "CNKI Journal Search"
    assert manifest["version"] == EXPECTED_VERSION
    assert manifest["description"] == (
        "Public CNKI topic search and attended institutional-WebVPN professional search "
        "with master-journal classification; no downloads or unattended login."
    )
    assert manifest["server"]["type"] == "uv"
    assert manifest["server"]["entry_point"] == "src/server.py"
    assert manifest["server"]["mcp_config"]["command"] == "uv"
    assert set(manifest["compatibility"]["platforms"]) == {"win32", "darwin", "linux"}
    assert manifest["tools"] == EXPECTED_TOOLS
    # manifest 声明的工具必须就是服务器真正注册的那两个，漏声明会让客户端
    # 以为专业检索不存在。
    assert [tool["name"] for tool in manifest["tools"]] == mcp_server.REQUIRED_TOOLS
    assert manifest["keywords"] == ["CNKI", "literature", "public-search", "journal-ranking"]
    assert manifest["license"] == "Apache-2.0"
    serialized = json.dumps(manifest, ensure_ascii=False).casefold()
    # webvpn 现在是如实描述的能力，不再是禁词；凭据与下载类令牌仍然禁止。
    for token in ("password", "cookie", "cnki_download", "cnki_fetch_details"):
        assert token not in serialized
    assert "user_config" not in manifest


def test_mcpb_pyproject_declares_public_runtime_dependencies(skill_root: Path) -> None:
    text = (skill_root / "mcpb/pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{EXPECTED_VERSION}"' in text
    assert 'description = "Public and attended CNKI journal-search MCP server"' in text
    assert 'requires-python = ">=3.11"' in text
    assert '"mcp>=1,<2"' in text
    assert '"playwright>=1.45,<2"' in text
    assert (skill_root / "mcpb/src/server.py").is_file()


def test_all_runtime_versions_and_release_allowlist_are_consistent(skill_root: Path) -> None:
    for relative in (
        "scripts/cnki_search/__init__.py",
        "mcpb/src/cnki_search/__init__.py",
    ):
        assert f'__version__ = "{EXPECTED_VERSION}"' in (
            skill_root / relative
        ).read_text(encoding="utf-8")
    assert f'name = "cnki-search-mcp"\nversion = "{EXPECTED_VERSION}"' in (
        skill_root / "mcpb/uv.lock"
    ).read_text(encoding="utf-8")
    assert ".mcpbignore" in _load_builder(skill_root).MCPB_ALLOWLIST


def test_release_builder_is_present(skill_root: Path) -> None:
    builder = skill_root / "scripts/build_release.py"
    assert builder.is_file()
    text = builder.read_text(encoding="utf-8")
    assert "tempfile" not in text
    assert "_build_workspace(output_dir)" in text
    assert "ALLOWLIST" in text
    assert "checksums.sha256" in text


def test_release_builder_creates_clean_archives(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)

    artifacts = module.build(skill_root, tmp_path / "outputs")

    assert [artifact.name for artifact in artifacts] == [
        "top-journal-search-lists_Skill.zip",
        "cnki-search.mcpb",
        "checksums.sha256",
    ]
    with zipfile.ZipFile(artifacts[0]) as archive:
        members = archive.namelist()
    assert members == sorted(members)
    assert all("\\" not in member for member in members)
    assert not any(
        token in "\n".join(members).casefold()
        for token in ("__pycache__", ".pytest_cache", ".venv", "local state", "details.py", "downloads.py")
    )
    assert not any(member.endswith("tests/_webvpn_e2e.py") for member in members)


def test_release_build_uses_only_explicit_output_directory(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    output_dir = tmp_path / "release"

    module.build(skill_root, output_dir)

    assert sorted(path.name for path in output_dir.iterdir()) == [
        "checksums.sha256", "cnki-search.mcpb", "top-journal-search-lists_Skill.zip",
    ]
    assert not (output_dir / ".stage").exists()


def test_release_archives_have_exact_allowlisted_members_and_source_bytes(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    skill_zip, mcpb_zip, _checksums = module.build(skill_root, tmp_path / "outputs")

    with zipfile.ZipFile(skill_zip) as archive:
        assert archive.namelist() == [
            f"top-journal-search-lists/{relative}" for relative in sorted(EXPECTED_SKILL_RELATIVE)
        ]
        for relative in EXPECTED_SKILL_RELATIVE:
            assert archive.read(f"top-journal-search-lists/{relative}") == (
                skill_root / relative
            ).read_bytes()
    with zipfile.ZipFile(mcpb_zip) as archive:
        assert archive.namelist() == list(EXPECTED_MCPB_RELATIVE)
        for relative in EXPECTED_MCPB_RELATIVE:
            assert archive.read(relative) == (skill_root / "mcpb" / relative).read_bytes()


def test_release_build_is_reproducible_across_source_mtimes(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    first_root = shutil.copytree(skill_root, tmp_path / "first-skill")
    second_root = shutil.copytree(skill_root, tmp_path / "second-skill")
    for path in second_root.rglob("*"):
        if path.is_file():
            os.utime(path, (946684800, 946684800))

    first = module.build(first_root, tmp_path / "first-output")
    second = module.build(second_root, tmp_path / "second-output")

    assert [_sha256(path) for path in first] == [_sha256(path) for path in second]


def test_repository_does_not_track_generated_root_outputs(skill_root: Path) -> None:
    repository = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=skill_root.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if repository.returncode != 0:
        pytest.skip("requires a Git checkout rather than an extracted release")
    tracked = subprocess.check_output(
        ["git", "ls-files", "outputs"],
        cwd=skill_root.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert tracked == ""


def test_release_allowlists_do_not_restore_removed_merge_module() -> None:
    for members in (CNKI_MODULES, TEST_RELATIVE, EXPECTED_SKILL_RELATIVE, EXPECTED_MCPB_RELATIVE):
        assert not any("merge.py" in member or "test_cnki_merge.py" in member for member in members)


def test_checksums_match_built_artifacts(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    skill_zip, mcpb_zip, checksums = module.build(skill_root, tmp_path / "outputs")

    expected = {
        skill_zip.name: _sha256(skill_zip),
        mcpb_zip.name: _sha256(mcpb_zip),
    }
    actual = {
        line.split()[1]: line.split()[0]
        for line in checksums.read_text(encoding="utf-8").splitlines()
    }
    assert actual == expected


def test_release_build_excludes_unlisted_and_state_baits(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    bait_root = shutil.copytree(skill_root, tmp_path / "bait-skill")
    baits = (
        bait_root / "Cookie",
        bait_root / "Local State",
        bait_root / "random-extra.txt",
        bait_root / "scripts/cnki_search/random_extra.py",
        bait_root / "mcpb/src/cnki_search/random_extra.py",
        bait_root / "scripts/cnki_search/__pycache__/cache.pyc",
    )
    for bait in baits:
        bait.parent.mkdir(parents=True, exist_ok=True)
        bait.write_text("TASK7-BAIT", encoding="utf-8")

    skill_zip, mcpb_zip, _checksums = module.build(bait_root, tmp_path / "outputs")

    with zipfile.ZipFile(skill_zip) as archive:
        assert archive.namelist() == [
            f"top-journal-search-lists/{relative}" for relative in sorted(EXPECTED_SKILL_RELATIVE)
        ]
    with zipfile.ZipFile(mcpb_zip) as archive:
        assert archive.namelist() == list(EXPECTED_MCPB_RELATIVE)


RUNTIME_MODULES = (
    "models.py",
    "professional.py",
    "professional_runtime.py",
    "professional_service.py",
    "ranking.py",
    "webvpn.py",
    "mcp_server.py",
)


@pytest.mark.parametrize("name", RUNTIME_MODULES)
def test_modified_runtime_module_matches_mcpb_mirror(
    skill_root: Path, name: str,
) -> None:
    """镜像漂移不会让任何测试变红，只会让发布包与源码行为不同——只能显式钉住。"""
    source = skill_root / "scripts" / "cnki_search" / name
    mirror = skill_root / "mcpb" / "src" / "cnki_search" / name
    assert source.read_bytes() == mirror.read_bytes(), name


def test_every_runtime_module_matches_mcpb_mirror(skill_root: Path) -> None:
    """手工清单会漏（professional_runtime.py 就漏过一次），再加一道全目录兜底。

    纯外观漂移（改注释、改 docstring）不会被任何行为测试抓到，只会让发布包与
    源码不同；这里对整个包逐字节比对，并禁止镜像里出现源码没有的模块。
    """
    source_dir = skill_root / "scripts" / "cnki_search"
    mirror_dir = skill_root / "mcpb" / "src" / "cnki_search"
    sources = sorted(path.name for path in source_dir.glob("*.py"))
    mirrors = sorted(path.name for path in mirror_dir.glob("*.py"))
    assert sources == mirrors
    assert set(RUNTIME_MODULES) <= set(sources)
    for name in sources:
        assert (source_dir / name).read_bytes() == (mirror_dir / name).read_bytes(), name
