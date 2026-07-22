import json
import importlib.util
from pathlib import Path
import zipfile


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
    builder_path = skill_root / "scripts/build_release.py"
    spec = importlib.util.spec_from_file_location("cnki_public_build", builder_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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
