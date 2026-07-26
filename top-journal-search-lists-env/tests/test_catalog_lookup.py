from __future__ import annotations

import importlib.util
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "catalog_lookup.py"
CATALOG = ROOT / "references" / "环境科学与工程学科顶尖期刊目录_v3.0.md"
MCPB_CATALOG = (
    ROOT / "mcpb" / "src" / "references" / "环境科学与工程学科顶尖期刊目录_v3.0.md"
)
FILE_SHA256 = "a01e40d5e011276d74b8bc277e0585f9c0d47e9e2c16d3082b0959643104dff4"
CONTENT_SHA256 = "681ae8776c3036ef1423a59926a87d44f451627809768065729bdc7377ed3444"


def _load_module():
    assert SCRIPT.is_file(), "环境目录解析器尚未实现"
    spec = importlib.util.spec_from_file_location("environment_catalog_lookup", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_environment_catalog_parser_exists_and_uses_bundled_v3_catalog() -> None:
    module = _load_module()
    assert module.DEFAULT_CATALOG.resolve() == CATALOG.resolve()


def test_catalog_snapshots_are_byte_identical_and_match_approved_sha256() -> None:
    assert CATALOG.read_bytes() == MCPB_CATALOG.read_bytes()
    assert hashlib.sha256(CATALOG.read_bytes()).hexdigest() == FILE_SHA256


def test_catalog_embedded_content_sha256_uses_documented_placeholder_rule() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    assert f"`{CONTENT_SHA256}`" in text
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    placeholder_text, count = re.subn(
        rf"`{CONTENT_SHA256}`",
        "`{{SHA256}}`",
        normalized,
        count=1,
    )
    assert count == 1
    assert hashlib.sha256(placeholder_text.encode("utf-8")).hexdigest() == CONTENT_SHA256


def test_validate_catalog_enforces_environment_v3_contract() -> None:
    module = _load_module()
    result = module.validate_catalog(CATALOG)
    assert result == {
        "valid": True,
        "catalog": str(CATALOG.resolve()),
        "catalog_version": "3.0",
        "catalog_date": "2026-07-26",
        "priority_levels": 10,
        "priority_groups": [
            "comprehensive_super_journals",
            "ncs_pnas_environment_flagships",
            "top_university_highest_consensus",
            "top_university_high_level",
            "environment_field_top",
            "chinese_environment_top",
            "other_formally_recognized",
            "environment_ssci",
            "environment_cssci",
            "environment_scie",
        ],
        "level_counts": [4, 17, 5, 45, 17, 6, 134, 324, 241, 1229],
        "unique_journals": 2022,
    }


def test_representative_journals_match_all_ten_levels_and_required_fields() -> None:
    module = _load_module()
    expected = {
        "Cell": (1, None),
        "Nature Climate Change": (2, 1),
        "Environmental Science & Technology": (3, None),
        "Ecological Economics": (4, None),
        "Ecology Letters": (5, None),
        "中国环境科学": (6, None),
        "ACS ES&T Water": (7, None),
        "Environment and Urbanization": (8, None),
        "上海经济研究": (9, None),
        "AAPG Bulletin": (10, None),
    }
    results = module.lookup_journals(CATALOG, list(expected))
    assert [item["input"] for item in results] == list(expected)
    for item in results:
        expected_level, expected_rank = expected[item["input"]]
        assert item["status"] == "matched"
        assert item["priority_level"] == expected_level
        assert item["ncs_internal_rank"] == expected_rank
        assert item["priority_group"]
        assert item["environment_subfields"]
        assert item["subject_categories"] == item["environment_subfields"]
        assert isinstance(item["formal_evidence"], list)
        assert isinstance(item["index_memberships"], list)
        assert isinstance(item["source_catalogs"], list)
        assert item["catalog_version"] == "3.0"
        assert item["catalog_date"] == "2026-07-26"
        assert item["manual_review_required"] is False


def test_header_driven_parser_preserves_evidence_and_index_fields() -> None:
    module = _load_module()
    level_three, level_eight = module.lookup_journals(
        CATALOG,
        ["Environmental Science & Technology", "Environment and Urbanization"],
    )
    assert "南京大学环境学院 1区A类（U4）" in level_three["formal_evidence"]
    assert "Engineering, Environmental" in level_three["index_memberships"]
    assert level_three["source_catalogs"] == [
        "环境科学与工程学科顶尖期刊目录_v3.0.md"
    ]
    assert "Urban Studies" in level_eight["index_memberships"]
    assert level_eight["source_catalogs"] == [
        "Social Sciences Citation Index_20260715.md"
    ]
    assert level_eight["formal_evidence"] == []


def test_controlled_title_variants_preserve_formal_title() -> None:
    module = _load_module()
    queries = [
        "The Environment and Urbanization",
        "Environmental Science and Technology",
        "经济学(季刊)",
        "Applied Catalysis B-Environment and Energy",
        "环境科学（网络首发）",
    ]
    results = module.lookup_journals(CATALOG, queries)
    assert [item["status"] for item in results] == ["matched"] * len(queries)
    assert results[0]["matched_title"] == "Environment and Urbanization"
    assert results[1]["matched_title"] == "Environmental Science & Technology"
    assert results[2]["matched_title"] == "经济学（季刊）"
    assert results[3]["matched_title"] == "Applied Catalysis B: Environment and Energy"
    assert results[4]["matched_title"] == "环境科学"
    assert results[4]["match_method"] == "controlled_display_suffix"


def test_appendices_are_not_indexed(tmp_path: Path) -> None:
    module = _load_module()
    text = CATALOG.read_text(encoding="utf-8")
    appendix = "## 附录一：环境相关SCIE分类目录"
    text = text.replace(
        appendix,
        appendix
        + "\n\n| 序号 | 期刊名称 | 原始学科类别 | 环境细分领域 | 收录来源 |\n"
        + "|---:|---|---|---|---|\n"
        + "| 1 | Appendix Only Environmental Journal | Ecology | 生态学 | SCIE |\n",
        1,
    )
    placeholder_text = text.replace(f"`{CONTENT_SHA256}`", "`{{SHA256}}`", 1)
    modified_hash = hashlib.sha256(placeholder_text.encode("utf-8")).hexdigest()
    text = text.replace(f"`{CONTENT_SHA256}`", f"`{modified_hash}`", 1)
    modified = tmp_path / "catalog.md"
    modified.write_text(text, encoding="utf-8")
    result = module.lookup_journals(modified, ["Appendix Only Environmental Journal"])[0]
    assert result["status"] == "unmatched"
    assert result["priority_level"] is None


def test_unmatched_and_genuine_normalized_collision_require_manual_review() -> None:
    module = _load_module()
    unmatched = module.lookup_journals(CATALOG, ["Imaginary Environmental Journal XYZ"])[0]
    assert unmatched["status"] == "unmatched"
    assert unmatched["priority_level"] is None
    assert unmatched["priority_group"] is None
    assert unmatched["manual_review_required"] is True

    index: dict[str, list[dict[str, object]]] = {}
    module._add(
        index,
        title="A.B",
        level=8,
        group="environment_ssci",
        environment_subfields=["环境管理"],
        formal_evidence=[],
        index_memberships=["Environmental Studies"],
        source_catalogs=["one.md"],
    )
    module._add(
        index,
        title="AB",
        level=9,
        group="environment_cssci",
        environment_subfields=["环境管理"],
        formal_evidence=[],
        index_memberships=["环境科学"],
        source_catalogs=["two.md"],
    )
    ambiguous = module.lookup_journal(index, "AB")
    assert ambiguous["status"] == "ambiguous"
    assert ambiguous["priority_level"] is None
    assert ambiguous["manual_review_required"] is True
    assert ambiguous["candidates"] == ["A.B", "AB"]


def test_cli_validate_and_batch_lookup_return_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--catalog",
            str(CATALOG),
            "lookup",
            "Cell",
            "Nature Climate Change",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(completed.stdout)
    assert [item["priority_level"] for item in payload] == [1, 2]

    validated = subprocess.run(
        [sys.executable, str(SCRIPT), "validate"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert json.loads(validated.stdout)["unique_journals"] == 2022
