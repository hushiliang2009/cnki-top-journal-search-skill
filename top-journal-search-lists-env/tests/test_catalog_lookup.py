from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "catalog_lookup.py"
CATALOG_JSON = ROOT / "references" / "environment_journal_catalog_v4.0.json"
MCPB_REFERENCES = ROOT / "mcpb" / "src" / "references"


def _load_module():
    spec = importlib.util.spec_from_file_location("environment_catalog_lookup", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_default_catalog_is_v4_json_for_both_runtime_layouts() -> None:
    module = _load_module()
    assert module.DEFAULT_CATALOG.resolve() == CATALOG_JSON.resolve()
    assert module.DEFAULT_CATALOG.suffix == ".json"
    assert (MCPB_REFERENCES / CATALOG_JSON.name).is_file()


def test_lookup_returns_v4_identity_memberships_and_alias_method() -> None:
    module = _load_module()
    formal, alias = module.lookup_journals(
        CATALOG_JSON,
        ["WIREs Climate Change", "Wiley Interdisciplinary Reviews-Climate Change"],
    )
    assert formal["journal_id"] == alias["journal_id"]
    assert formal["priority_level"] == 8
    assert set(formal["index_memberships"]) == {"SSCI", "SCIE"}
    assert alias["match_method"] == "controlled_alias"
    for key in ("aliases", "index_subject_categories", "source_memberships", "revision_date"):
        assert key in formal


def test_lookup_returns_complete_empty_shape_for_unmatched_and_ambiguous() -> None:
    module = _load_module()
    unmatched = module.lookup_journals(CATALOG_JSON, ["Imaginary Environmental Journal XYZ"])[0]
    assert unmatched["status"] == "unmatched"
    assert unmatched["manual_review_required"] is True
    for key in ("journal_id", "matched_title", "priority_level", "priority_group"):
        assert unmatched[key] is None
    for key in ("aliases", "index_memberships", "index_subject_categories", "source_memberships"):
        assert unmatched[key] == [] or unmatched[key] == {}


def test_cnki_scope_returns_explicit_members_not_runtime_language_guesses() -> None:
    module = _load_module()
    scope = module.cnki_scope("other_formally_recognized_chinese", CATALOG_JSON)
    assert scope["catalog_version"] == "4.0"
    assert scope["journal_selector"] == "exact_titles"
    assert scope["source_category"] is None
    assert len(scope["eligible_journal_ids"]) == 60
    assert len(scope["journal_titles"]) == 60
    with pytest.raises(ValueError, match="scope"):
        module.cnki_scope("not-a-scope", CATALOG_JSON)


def test_default_validate_auto_discovers_full_companions_and_all_mirrors() -> None:
    module = _load_module()
    result = module.validate_catalog()
    assert result["validation_scope"] == "full"
    assert result["companion_files_verified"] == [
        "环境科学与工程学科顶尖期刊目录_v4.0.md",
        "environment_catalog_sources_v4.0.json",
        "environment_journal_match_audit_v4.0.md",
    ]
    assert result["mirrored_files_verified"] == 11
    assert result["catalog_version"] == "4.0"
    assert result["unique_journals"] == 3764


def test_explicit_standalone_catalog_without_companions_is_json_only(tmp_path: Path) -> None:
    module = _load_module()
    standalone = tmp_path / "custom-environment-catalog.json"
    standalone.write_bytes(CATALOG_JSON.read_bytes())
    result = module.validate_catalog(standalone)
    assert result["validation_scope"] == "json_only"
    assert result["companion_files_verified"] == []
    assert result["mirrored_files_verified"] == 0


def test_partial_explicit_companion_set_is_rejected(tmp_path: Path) -> None:
    module = _load_module()
    standalone = tmp_path / "custom-environment-catalog.json"
    standalone.write_bytes(CATALOG_JSON.read_bytes())
    with pytest.raises(ValueError, match="完整"):
        module.validate_catalog(standalone, markdown=ROOT / "references" / "环境科学与工程学科顶尖期刊目录_v4.0.md")


def test_cli_validate_reports_default_full_and_explicit_json_only(tmp_path: Path) -> None:
    default_run = subprocess.run(
        [sys.executable, str(SCRIPT), "validate"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert json.loads(default_run.stdout)["validation_scope"] == "full"

    standalone = tmp_path / "custom-environment-catalog.json"
    standalone.write_bytes(CATALOG_JSON.read_bytes())
    custom_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(standalone), "validate"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert json.loads(custom_run.stdout)["validation_scope"] == "json_only"
