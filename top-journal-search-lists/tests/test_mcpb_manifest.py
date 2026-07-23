import hashlib
import json
import importlib.util
import os
from pathlib import Path
import zipfile


CNKI_MODULES = (
    "__init__.py",
    "browser.py",
    "cache.py",
    "install_config.py",
    "mcp_server.py",
    "merge.py",
    "models.py",
    "ranking.py",
    "rate_limit.py",
    "results.py",
    "search.py",
    "service.py",
    "session.py",
)
TEST_RELATIVE = (
    "tests/conftest.py",
    "tests/test_catalog_lookup.py",
    "tests/test_cnki_cache.py",
    "tests/test_cnki_mcp.py",
    "tests/test_cnki_merge.py",
    "tests/test_cnki_models.py",
    "tests/test_cnki_package_contract.py",
    "tests/test_cnki_ranking.py",
    "tests/test_cnki_rate_limit.py",
    "tests/test_cnki_results.py",
    "tests/test_cnki_search.py",
    "tests/test_cnki_service.py",
    "tests/test_cnki_session.py",
    "tests/test_task0_baseline.py",
    "tests/test_installers.py",
    "tests/test_mcpb_manifest.py",
    "tests/fixtures/public_challenge.html",
    "tests/fixtures/public_home.html",
    "tests/fixtures/public_incomplete_results.html",
    "tests/fixtures/public_no_results.html",
    "tests/fixtures/public_results.html",
    "tests/fixtures/representative_public_results_sanitized.html",
    "tests/fixtures/synthetic_malformed_public_results.html",
)
EXPECTED_SKILL_RELATIVE = (
    "README.md",
    "SKILL.md",
    "agents/openai.yaml",
    "installers/install.ps1",
    "installers/install.sh",
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_clean_skill(module, source: Path, target: Path) -> Path:
    module.copy_skill_tree(source, target)
    return target


def test_mcpb_manifest_is_uv_cross_platform_and_safe(skill_root: Path) -> None:
    manifest = json.loads((skill_root / "mcpb/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.4"
    assert manifest["name"] == "cnki-search"
    assert manifest["display_name"] == "CNKI Public Theme Search"
    assert manifest["version"] == "0.2.0"
    assert manifest["description"] == (
        "Public CNKI theme search with master-journal classification; no login or downloads."
    )
    assert manifest["server"]["type"] == "uv"
    assert manifest["server"]["entry_point"] == "src/server.py"
    assert manifest["server"]["mcp_config"]["command"] == "uv"
    assert set(manifest["compatibility"]["platforms"]) == {"win32", "darwin", "linux"}
    assert manifest["tools"] == [
        {
            "name": "cnki_search",
            "description": "Search the public CNKI homepage by topic and rank first-page journal records.",
        }
    ]
    assert manifest["keywords"] == ["CNKI", "literature", "public-search", "journal-ranking"]
    assert manifest["license"] == "Apache-2.0"
    serialized = json.dumps(manifest, ensure_ascii=False).casefold()
    for token in ("password", "cookie", "webvpn", "cnki_download", "cnki_fetch_details"):
        assert token not in serialized
    assert "user_config" not in manifest


def test_mcpb_pyproject_declares_public_runtime_dependencies(skill_root: Path) -> None:
    text = (skill_root / "mcpb/pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.2.0"' in text
    assert 'requires-python = ">=3.11"' in text
    assert '"mcp>=1,<2"' in text
    assert '"playwright>=1.45,<2"' in text
    assert (skill_root / "mcpb/src/server.py").is_file()


def test_release_builder_is_present(skill_root: Path) -> None:
    builder = skill_root / "scripts/build_release.py"
    assert builder.is_file()
    text = builder.read_text(encoding="utf-8")
    assert "TemporaryDirectory" in text
    assert "ALLOWLIST" in text
    assert "checksums.sha256" in text


def test_release_builder_creates_clean_archives(skill_root: Path) -> None:
    module = _load_builder(skill_root)

    artifacts = module.build(skill_root, skill_root.parent / "outputs")

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


def test_release_archives_have_exact_allowlisted_members_and_source_bytes(skill_root: Path) -> None:
    module = _load_builder(skill_root)
    skill_zip, mcpb_zip, _checksums = module.build(skill_root, skill_root.parent / "outputs")

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
    first_root = _copy_clean_skill(module, skill_root, tmp_path / "first-skill")
    second_root = _copy_clean_skill(module, skill_root, tmp_path / "second-skill")
    for path in second_root.rglob("*"):
        if path.is_file():
            os.utime(path, (946684800, 946684800))

    first = module.build(first_root, tmp_path / "first-output")
    second = module.build(second_root, tmp_path / "second-output")

    assert [_sha256(path) for path in first[:2]] == [_sha256(path) for path in second[:2]]


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
    bait_root = _copy_clean_skill(module, skill_root, tmp_path / "bait-skill")
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
