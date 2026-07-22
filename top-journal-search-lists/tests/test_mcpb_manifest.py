import json
from pathlib import Path
import zipfile

import pytest


TASK7 = "Task 7 将同步 MCPB 源码、manifest 和发布归档；本迁移单元不得提前实施。"


@pytest.mark.xfail(reason=TASK7, strict=True)
def test_mcpb_manifest_is_uv_cross_platform_and_safe(skill_root: Path) -> None:
    manifest = json.loads((skill_root / "mcpb/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.4"
    assert manifest["server"]["type"] == "uv"
    assert manifest["server"]["entry_point"] == "src/server.py"
    assert manifest["server"]["mcp_config"]["command"] == "uv"
    assert set(manifest["compatibility"]["platforms"]) == {"win32", "darwin", "linux"}
    assert [tool["name"] for tool in manifest["tools"]] == ["cnki_search"]
    serialized = json.dumps(manifest, ensure_ascii=False).casefold()
    assert "password" not in serialized
    assert "cookie" not in serialized
    assert "user_config" not in manifest


def test_mcpb_pyproject_declares_runtime_dependencies(skill_root: Path) -> None:
    text = (skill_root / "mcpb/pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in text
    assert '"mcp' in text
    assert '"playwright' in text
    assert (skill_root / "mcpb/src/server.py").is_file()


@pytest.mark.xfail(reason=TASK7, strict=True)
def test_release_archives_match_current_session_sources_when_present(skill_root: Path) -> None:
    outputs = skill_root.parent / "outputs"
    mcpb_artifact = outputs / "cnki-search.mcpb"
    if mcpb_artifact.is_file():
        with zipfile.ZipFile(mcpb_artifact) as archive:
            assert archive.read("src/cnki_search/session.py") == (
                skill_root / "mcpb/src/cnki_search/session.py"
            ).read_bytes()
    skill_artifact = outputs / "top-journal-search-lists_Skill.zip"
    if skill_artifact.is_file():
        with zipfile.ZipFile(skill_artifact) as archive:
            assert archive.read("top-journal-search-lists/scripts/cnki_search/session.py") == (
                skill_root / "scripts/cnki_search/session.py"
            ).read_bytes()
