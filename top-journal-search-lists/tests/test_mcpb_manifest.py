import json
import os
from pathlib import Path
import subprocess
from uuid import uuid4
import zipfile

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


def test_install_scripts_require_explicit_and_isolated_client_targets(skill_root: Path) -> None:
    root = skill_root.parent
    powershell_scripts = [skill_root / "installers/install.ps1"]
    shell_scripts = [skill_root / "installers/install.sh"]
    if (root / "outputs/install.ps1").is_file():
        powershell_scripts.append(root / "outputs/install.ps1")
    if (root / "outputs/install.sh").is_file():
        shell_scripts.append(root / "outputs/install.sh")
    for script in powershell_scripts:
        content = script.read_text(encoding="utf-8")
        for required in ("[switch]$Codex", "[switch]$ClaudeCode", "[switch]$ClaudeDesktop", "Usage"):
            assert required in content, f"{script} 缺少显式安装目标约束：{required}"
        assert "SkipCodex" not in content
        assert "SkipClaude" not in content
    for script in shell_scripts:
        content = script.read_text(encoding="utf-8")
        for required in ("--codex", "--claude-code", "--claude-desktop", "Usage"):
            assert required in content, f"{script} 缺少显式安装目标约束：{required}"
        assert "SkipCodex" not in content
        assert "SkipClaude" not in content


def test_release_zip_uses_portable_entries_when_present(skill_root: Path) -> None:
    artifact = skill_root.parent / "outputs" / "top-journal-search-lists_Skill.zip"
    if not artifact.is_file():
        return
    with zipfile.ZipFile(artifact) as archive:
        names = archive.namelist()
    assert names
    assert all("\\" not in name for name in names)
    assert all(name.startswith("top-journal-search-lists/") for name in names)
    assert not any(
        any(part in {"__pycache__", ".pytest_cache", ".venv"} for part in name.split("/"))
        or name.endswith(".pyc")
        or "task7-installer-" in name
        for name in names
    )


def test_install_script_review_contracts(skill_root: Path) -> None:
    root = skill_root.parent
    powershell_scripts = [skill_root / "installers/install.ps1"]
    shell_scripts = [skill_root / "installers/install.sh"]
    if (root / "outputs/install.ps1").is_file():
        powershell_scripts.append(root / "outputs/install.ps1")
    if (root / "outputs/install.sh").is_file():
        shell_scripts.append(root / "outputs/install.sh")
    for script in powershell_scripts:
        content = script.read_text(encoding="utf-8")
        for required in (
            "[switch]$Codex",
            "[switch]$ClaudeCode",
            "[switch]$ClaudeDesktop",
            "ValueFromRemainingArguments",
            "[Console]::Error.WriteLine",
        ):
            assert required in content
        claude_code_block = content.split("if ($ClaudeCode) {", maxsplit=1)[1].split(
            "if ($ClaudeDesktop)", maxsplit=1
        )[0]
        claude_desktop_block = content.split("if ($ClaudeDesktop) {", maxsplit=1)[1]
        assert ".claude.json" in claude_code_block
        assert "claude_desktop_config.json" not in claude_code_block
        assert "claude_desktop_config.json" in claude_desktop_block
        assert ".claude.json" not in claude_desktop_block
        assert (
            "$RuntimeRoot = if ($Codex) { Join-Path $CodexHome 'runtimes\\cnki-search' } else { Join-Path $ClaudeHome 'runtimes\\cnki-search' }"
            in content
        )
    for script in shell_scripts:
        content = script.read_text(encoding="utf-8")
        assert "*) usage; exit 2 ;;" in content


def test_powershell_installers_return_two_for_missing_and_unknown_targets(
    skill_root: Path,
) -> None:
    root = skill_root.parent
    scripts = [skill_root / "installers/install.ps1"]
    if (root / "outputs/install.ps1").is_file():
        scripts.append(root / "outputs/install.ps1")
    isolated_root = skill_root.parent / f"task7-installer-{uuid4().hex}"
    assert not isolated_root.exists()
    env = os.environ | {
        "APPDATA": str(isolated_root / "AppData" / "Roaming"),
        "CODEX_HOME": str(isolated_root / "codex-home"),
        "CLAUDE_CONFIG_DIR": str(isolated_root / "claude-home"),
    }
    for script in scripts:
        for arguments in ([], ["-UnknownTarget"]):
            process = subprocess.run(
                ["powershell.exe", "-NoProfile", "-File", str(script), *arguments],
                cwd=skill_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                timeout=5,
            )
            assert process.returncode == 2
            assert "Usage" in process.stdout
            assert not (isolated_root / "codex-home").exists()
            assert not (isolated_root / "claude-home").exists()
            assert not (
                isolated_root
                / "AppData"
                / "Roaming"
                / "Claude"
                / "claude_desktop_config.json"
            ).exists()


def test_powershell_installer_without_target_fails_before_writing(skill_root: Path) -> None:
    script = skill_root / "installers/install.ps1"
    isolated_home = skill_root.parent / f"task7-installer-{uuid4().hex}"
    assert not isolated_home.exists()
    env = os.environ | {
        "APPDATA": str(isolated_home / "AppData" / "Roaming"),
        "CODEX_HOME": str(isolated_home / "codex-home"),
        "CLAUDE_CONFIG_DIR": str(isolated_home / "claude-home"),
    }
    process = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-File", str(script)],
        cwd=skill_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    try:
        output, _ = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        output, _ = process.communicate(timeout=10)
        raise AssertionError("无目标安装器未在写入前立即失败")
    assert process.returncode != 0
    assert "Usage" in output
    assert not (isolated_home / "codex-home").exists()
    assert not (isolated_home / "claude-home").exists()
    assert not (isolated_home / ".claude.json").exists()
    assert not (
        isolated_home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    ).exists()
