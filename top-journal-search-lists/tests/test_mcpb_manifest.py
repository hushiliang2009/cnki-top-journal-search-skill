import json
from pathlib import Path

from cnki_search.mcp_server import REQUIRED_TOOLS


def test_mcpb_manifest_is_uv_cross_platform_and_safe(skill_root: Path) -> None:
    manifest = json.loads((skill_root / "mcpb/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.4"
    assert manifest["server"]["type"] == "uv"
    assert manifest["server"]["entry_point"] == "src/server.py"
    assert manifest["server"]["mcp_config"]["command"] == "uv"
    assert set(manifest["compatibility"]["platforms"]) == {"win32", "darwin", "linux"}
    assert [tool["name"] for tool in manifest["tools"]] == REQUIRED_TOOLS
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


def test_install_scripts_exist_and_do_not_replace_whole_config(skill_root: Path) -> None:
    powershell = (skill_root / "installers/install.ps1").read_text(encoding="utf-8")
    shell = (skill_root / "installers/install.sh").read_text(encoding="utf-8")
    assert "Backup" in powershell
    assert "backup" in shell.casefold()
    assert "cnki-search" in powershell
    assert "cnki-search" in shell
    assert "claude_desktop_config.json" in powershell
    assert "claude_desktop_config.json" in shell
    assert ".claude.json" in powershell
    assert ".claude.json" in shell
    assert "Backup-File" in powershell
