from pathlib import Path


def test_browser_launch_smoke_uses_current_public_session_api(skill_root: Path) -> None:
    smoke = (skill_root / "tests/_browser_launch_smoke.py").read_text(encoding="utf-8")
    assert "PublicCnkiSession" in smoke
    assert "import CnkiSession" not in smoke
    assert ".login(" not in smoke


def test_parser_fixtures_have_clear_non_live_provenance(fixtures: Path) -> None:
    representative = fixtures / "representative_public_results_sanitized.html"
    malformed = fixtures / "synthetic_malformed_public_results.html"
    assert representative.is_file()
    assert malformed.is_file()
    assert "sanitized representative fixture" in representative.read_text(encoding="utf-8").casefold()
    assert "synthetic malformed fixture" in malformed.read_text(encoding="utf-8").casefold()
    assert "not a captured cnki page" in representative.read_text(encoding="utf-8").casefold()
    assert "not a captured cnki page" in malformed.read_text(encoding="utf-8").casefold()


def test_ci_runs_cross_platform_non_live_quality_gates(skill_root: Path) -> None:
    workflow = skill_root.parent / ".github/workflows/ci.yml"
    text = workflow.read_text(encoding="utf-8")
    for required in (
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
        'python-version: ["3.11", "3.12", "3.13", "3.14"]',
        "python-version: [\"3.11\"]",
        "python -m pytest -q",
        "scripts/catalog_lookup.py validate",
        "tests/_mcp_handshake.py",
        "tests/_mcpb_handshake.py",
        "scripts/build_release.py --output",
        "zipfile.ZipFile",
    ):
        assert required in text
    for forbidden in ("www.cnki.net", "kns.cnki.net", "webvpn", "CDP", "proxy"):
        assert forbidden.casefold() not in text.casefold()
