import hashlib
import json
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from cnki_search_env import mcp_server


EXPECTED_VERSION = "0.3.0"
CNKI_MODULES = (
    "__init__.py",
    "browser.py",
    "cache.py",
    "catalog_adapter.py",
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
V4_REFERENCE_FILES = (
    "环境科学与工程学科顶尖期刊目录_v4.0.md",
    "environment_journal_catalog_v4.0.json",
    "environment_catalog_sources_v4.0.json",
    "environment_journal_match_audit_v4.0.md",
    "CSSCI_2025_2026.md",
    "北大中文核心期刊目录_2023_自然科学版.md",
    "北大中文核心期刊目录_2023_.md",
    "Social Sciences Citation Index_20260715.md",
    "Social Sciences Citation Index (SSCI).csv",
    "Science Citation Index Expanded_20260715.md",
    "Science Citation Index Expanded (SCIE).csv",
)
TEST_RELATIVE = (
    "tests/_mcp_handshake.py",
    "tests/_mcpb_handshake.py",
    "tests/_mcpb_raw_handshake.py",
    "tests/conftest.py",
    "tests/_webvpn_probe.py",
    "tests/test_catalog_lookup.py",
    "tests/test_cnki_cache.py",
    "tests/test_cnki_async.py",
    "tests/test_cnki_mcp.py",
    "tests/test_cnki_models.py",
    "tests/test_cnki_package_contract.py",
    "tests/test_cnki_professional_env.py",
    "tests/test_cnki_professional_mcp_env.py",
    "tests/test_cnki_professional_service_env.py",
    "tests/test_cnki_professional_runtime_env.py",
    "tests/test_cnki_webvpn_outcome_env.py",
    "tests/test_cnki_webvpn_page_env.py",
    "tests/test_cnki_webvpn_env.py",
    "tests/test_cnki_ranking.py",
    "tests/test_cnki_rate_limit.py",
    "tests/test_cnki_results.py",
    "tests/test_cnki_search_env.py",
    "tests/test_cnki_service.py",
    "tests/test_cnki_session.py",
    "tests/test_environment_catalog_generation.py",
    "tests/test_skill_contract.py",
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
    ".gitattributes",
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
    *(f"mcpb/src/cnki_search_env/{name}" for name in CNKI_MODULES),
    *(f"mcpb/src/references/{name}" for name in V4_REFERENCE_FILES),
    "mcpb/src/server.py",
    "mcpb/uv.lock",
    *(f"references/{name}" for name in V4_REFERENCE_FILES),
    "references/cnki-search-env-reference.md",
    "scripts/build_release.py",
    "scripts/catalog_lookup.py",
    "scripts/environment_catalog_v4.py",
    "scripts/generate_environment_catalog_v4.py",
    *(f"scripts/cnki_search_env/{name}" for name in CNKI_MODULES),
    *TEST_RELATIVE,
)
EXPECTED_MCPB_RELATIVE = tuple(sorted(
    relative.removeprefix("mcpb/")
    for relative in EXPECTED_SKILL_RELATIVE
    if relative.startswith("mcpb/")
))


def _load_builder(skill_root: Path):
    builder_path = skill_root / "scripts/build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_public_build", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_mcpb_manifest_is_uv_cross_platform_and_safe(skill_root: Path) -> None:
    manifest = json.loads((skill_root / "mcpb/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.4"
    assert manifest["name"] == "cnki-search-env"
    assert manifest["display_name"] == "CNKI Environmental Journal Search"
    assert manifest["version"] == EXPECTED_VERSION
    assert manifest["description"] == (
        "Public CNKI topic search and attended institutional-WebVPN professional search "
        "with environmental v4.0 journal classification; no downloads or unattended login."
    )
    assert manifest["author"]["name"] == "Top Environmental Journal Search"
    assert manifest["server"]["type"] == "uv"
    assert manifest["server"]["entry_point"] == "src/server.py"
    assert manifest["server"]["mcp_config"]["command"] == "uv"
    assert set(manifest["compatibility"]["platforms"]) == {"win32", "darwin", "linux"}
    # manifest 的 tools 是客户端可见的能力声明，必须与实际注册的工具一致；
    # 少声明一个会让安装者看不到它，多声明则等于承诺了不存在的能力。
    assert manifest["tools"] == [
        {
            "name": "cnki_search_env",
            "description": "Search the public CNKI homepage and rank first-page records by the environmental v4.0 journal catalog.",
        },
        {
            "name": "cnki_professional_search_env",
            "description": (
                "Run attended CNKI professional search over controlled environmental journal "
                "groups through institutional WebVPN; the user must sign in and complete "
                "security checks."
            ),
        },
    ]
    assert [tool["name"] for tool in manifest["tools"]] == mcp_server.REQUIRED_TOOLS
    assert manifest["keywords"] == [
        "CNKI",
        "environmental-science",
        "literature",
        "public-search",
        "journal-ranking",
    ]
    assert manifest["license"] == "Apache-2.0"
    serialized = json.dumps(manifest, ensure_ascii=False).casefold()
    # manifest 可以命名 WebVPN 这一模式（第二个工具正是靠它工作），但凭据类
    # 字段与旧能力令牌照禁——与代码侧 SHARED_ENTRY_MODULES 的口径一致。
    for token in ("password", "cookie", "cnki_download", "cnki_fetch_details"):
        assert token not in serialized
    assert "webvpn" in serialized, "第二个工具必须在 manifest 里如实说明它经 WebVPN 工作"
    assert "user_config" not in manifest


def test_mcpb_pyproject_declares_public_runtime_dependencies(skill_root: Path) -> None:
    text = (skill_root / "mcpb/pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{EXPECTED_VERSION}"' in text
    assert (
        'description = "Public and attended CNKI environmental journal-search MCP server"'
        in text
    )
    assert 'requires-python = ">=3.11"' in text
    assert '"mcp>=1,<2"' in text
    assert '"playwright>=1.45,<2"' in text
    assert (skill_root / "mcpb/src/server.py").is_file()


def test_all_runtime_versions_and_release_allowlist_are_consistent(skill_root: Path) -> None:
    for relative in (
        "scripts/cnki_search_env/__init__.py",
        "mcpb/src/cnki_search_env/__init__.py",
    ):
        assert f'__version__ = "{EXPECTED_VERSION}"' in (
            skill_root / relative
        ).read_text(encoding="utf-8")
    assert f'name = "cnki-search-env-mcp"\nversion = "{EXPECTED_VERSION}"' in (
        skill_root / "mcpb/uv.lock"
    ).read_text(encoding="utf-8")
    assert ".mcpbignore" in _load_builder(skill_root).MCPB_ALLOWLIST


def test_environment_release_has_portable_v4_inputs_without_v3_or_full_jsonl() -> None:
    """离线复算脚本必须随 Skill 发布，否则收件人无法自行核验 v4.0 目录是怎么来的。

    但生成脚本不进 MCPB（运行时不需要重算），完整审计 JSONL 不进任何发布包。
    """
    assert not any("v3.0" in path for path in EXPECTED_SKILL_RELATIVE)
    assert "scripts/environment_catalog_v4.py" in EXPECTED_SKILL_RELATIVE
    assert "scripts/generate_environment_catalog_v4.py" in EXPECTED_SKILL_RELATIVE
    assert "tests/test_environment_catalog_generation.py" in EXPECTED_SKILL_RELATIVE
    assert not any(
        path.endswith("environment_journal_match_audit_v4.0.jsonl")
        for path in EXPECTED_SKILL_RELATIVE
    )
    assert not any(
        "generate_environment_catalog_v4.py" in path for path in EXPECTED_MCPB_RELATIVE
    )
    assert not any(
        "environment_catalog_v4.py" in path for path in EXPECTED_MCPB_RELATIVE
    )


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
        "top-journal-search-lists-env_Skill.zip",
        "cnki-search-env.mcpb",
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
    # 人工实机验证脚本只在仓库检出下有意义：它会打开可见浏览器并等待人工登录，
    # 混进发布包只会给安装者一个看起来能跑、实际必须有人值守的入口。
    assert not any(member.endswith("tests/_webvpn_e2e.py") for member in members)


def test_release_build_uses_only_explicit_output_directory(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    output_dir = tmp_path / "release"

    module.build(skill_root, output_dir)

    assert sorted(path.name for path in output_dir.iterdir()) == [
        "checksums.sha256", "cnki-search-env.mcpb", "top-journal-search-lists-env_Skill.zip",
    ]
    assert not (output_dir / ".stage").exists()


def test_release_archives_have_exact_allowlisted_members_and_source_bytes(skill_root: Path, tmp_path: Path) -> None:
    module = _load_builder(skill_root)
    skill_zip, mcpb_zip, _checksums = module.build(skill_root, tmp_path / "outputs")

    with zipfile.ZipFile(skill_zip) as archive:
        assert archive.namelist() == [
            f"top-journal-search-lists-env/{relative}" for relative in sorted(EXPECTED_SKILL_RELATIVE)
        ]
        for relative in EXPECTED_SKILL_RELATIVE:
            assert archive.read(f"top-journal-search-lists-env/{relative}") == (
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
        bait_root / "scripts/cnki_search_env/random_extra.py",
        bait_root / "mcpb/src/cnki_search_env/random_extra.py",
        bait_root / "scripts/cnki_search_env/__pycache__/cache.pyc",
    )
    for bait in baits:
        bait.parent.mkdir(parents=True, exist_ok=True)
        bait.write_text("TASK7-BAIT", encoding="utf-8")

    skill_zip, mcpb_zip, _checksums = module.build(bait_root, tmp_path / "outputs")

    with zipfile.ZipFile(skill_zip) as archive:
        assert archive.namelist() == [
            f"top-journal-search-lists-env/{relative}" for relative in sorted(EXPECTED_SKILL_RELATIVE)
        ]
    with zipfile.ZipFile(mcpb_zip) as archive:
        assert archive.namelist() == list(EXPECTED_MCPB_RELATIVE)


RUNTIME_MODULES = (
    "models.py",
    "catalog_adapter.py",
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
    source = skill_root / "scripts" / "cnki_search_env" / name
    mirror = skill_root / "mcpb" / "src" / "cnki_search_env" / name
    assert source.read_bytes() == mirror.read_bytes(), name


def test_every_runtime_module_matches_mcpb_mirror(skill_root: Path) -> None:
    """手工清单会漏（professional_runtime.py 就漏过一次），再加一道全目录兜底。

    纯外观漂移（改注释、改 docstring）不会被任何行为测试抓到，只会让发布包与
    源码不同；这里对整个包逐字节比对，并禁止镜像里出现源码没有的模块。
    """
    source_dir = skill_root / "scripts" / "cnki_search_env"
    mirror_dir = skill_root / "mcpb" / "src" / "cnki_search_env"
    sources = sorted(path.name for path in source_dir.glob("*.py"))
    mirrors = sorted(path.name for path in mirror_dir.glob("*.py"))
    assert sources == mirrors
    assert set(RUNTIME_MODULES) <= set(sources)
    for name in sources:
        assert (source_dir / name).read_bytes() == (mirror_dir / name).read_bytes(), name


def test_runtime_docstrings_do_not_claim_a_ten_level_catalog(
    skill_root: Path,
) -> None:
    """环境目录已是十二级；运行时 docstring 仍写十级会误导后续维护者。"""
    for base in ("scripts/cnki_search_env", "mcpb/src/cnki_search_env"):
        for path in sorted((skill_root / base).glob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert "十级期刊目录" not in text, path.name


# 七份来源快照标记为 -text，逐字节保留上游原样，换行不由本仓库决定。
UPSTREAM_SNAPSHOTS = frozenset({
    "CSSCI_2025_2026.md",
    "北大中文核心期刊目录_2023_自然科学版.md",
    "北大中文核心期刊目录_2023_.md",
    "Social Sciences Citation Index_20260715.md",
    "Social Sciences Citation Index (SSCI).csv",
    "Science Citation Index Expanded_20260715.md",
    "Science Citation Index Expanded (SCIE).csv",
})


def test_packaged_text_members_use_lf_on_every_platform(
    skill_root: Path, tmp_path: Path,
) -> None:
    """同通用版：Windows 检出会让产物哈希偏离官方值，使用者无法自证。

    七份上游来源快照除外——它们按约定逐字节保留，含 CRLF 是正确的。
    """
    module = _load_builder(skill_root)
    skill_zip, mcpb_zip, _checksums = module.build(skill_root, tmp_path / "outputs")

    offenders = []
    for archive in (skill_zip, mcpb_zip):
        with zipfile.ZipFile(archive) as bundle:
            for name in bundle.namelist():
                if name.rsplit("/", 1)[-1] in UPSTREAM_SNAPSHOTS:
                    continue
                if b"\r\n" in bundle.read(name):
                    offenders.append(f"{archive.name}:{name}")

    assert offenders == [], f"这些成员含 CRLF：{offenders[:8]}（共 {len(offenders)} 个）"
