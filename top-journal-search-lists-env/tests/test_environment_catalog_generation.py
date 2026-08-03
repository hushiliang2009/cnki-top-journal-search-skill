from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"
BASELINE = REFERENCES / "环境科学与工程学科顶尖期刊目录_v4.0.md"
SCRIPT = ROOT / "scripts" / "environment_catalog_v4.py"


def _load_catalog_module():
    assert SCRIPT.is_file(), "环境 v4.0 来源解析器尚未实现"
    spec = importlib.util.spec_from_file_location("environment_catalog_v4", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip()[1:-1].split("|")]


def _write_generated_baseline(
    tmp_path: Path,
    *,
    include_baseline_title: bool = True,
) -> Path:
    """写入字段已重排的生成目录，以验证重跑不会重新定义基线身份。"""
    lines = BASELINE.read_text(encoding="utf-8").splitlines()
    rendered: list[str] = []
    ordinal = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        if (
            line_index + 1 < len(lines)
            and line.startswith("| 序号 |")
            and lines[line_index + 1].startswith("|---")
        ):
            headers = _table_cells(line)
            reordered_headers = ["正式题名", "期刊ID"]
            if include_baseline_title:
                reordered_headers.append("基线题名")
            reordered_headers.extend(
                header for header in headers if header not in {"期刊名称"}
            )
            rendered.append("| " + " | ".join(reordered_headers) + " |")
            rendered.append("|" + "|".join("---" for _ in reordered_headers) + "|")
            line_index += 2
            while line_index < len(lines) and lines[line_index].startswith("|"):
                values = dict(zip(headers, _table_cells(lines[line_index]), strict=True))
                ordinal += 1
                baseline_title = values["期刊名称"]
                formal_title = (
                    "Cell normalized title" if ordinal == 1 else baseline_title
                )
                row = [formal_title, f"ENVJ-LOCKED-{ordinal:06d}"]
                if include_baseline_title:
                    row.append(baseline_title)
                row.extend(values[header] for header in headers if header != "期刊名称")
                rendered.append("| " + " | ".join(row) + " |")
                line_index += 1
            continue
        rendered.append(line)
        line_index += 1

    generated = tmp_path / "generated-v4-baseline.md"
    generated.write_text("\n".join(rendered) + "\n", encoding="utf-8")
    return generated


def test_source_parsers_preserve_approved_counts_and_original_titles() -> None:
    """删除解析或按逗号拆分北大核心原刊名时，此测试应失败。"""
    catalog = _load_catalog_module()
    paths = catalog.SourcePaths.from_references(REFERENCES)
    ssci = catalog.parse_wos_csv(
        paths.ssci_csv,
        "SSCI",
        display_titles=catalog.parse_wos_markdown(paths.ssci_markdown),
    )
    scie = catalog.parse_wos_csv(
        paths.scie_csv,
        "SCIE",
        display_titles=catalog.parse_wos_markdown(paths.scie_markdown),
    )
    cssci = catalog.parse_cssci_markdown(paths.cssci_markdown)
    natural = catalog.parse_pku_markdown(paths.pku_natural, "natural_sciences")
    non_natural = catalog.parse_pku_markdown(
        paths.pku_non_natural, "non_natural_sciences"
    )

    assert [len(items) for items in (ssci, scie, cssci, natural, non_natural)] == [
        3538,
        9430,
        674,
        1247,
        740,
    ]
    renamed = next(item for item in natural if item.formal_title == "低碳化学与化工")
    assert renamed.aliases == ("天然气化工.C1,化学与化工",)


def test_v4_baseline_has_stable_ids_levels_and_priority_signature() -> None:
    """删除十二级解析、改变顺序或改写稳定编号时，此测试应失败。"""
    catalog = _load_catalog_module()
    records = catalog.parse_v4_baseline(BASELINE)

    assert len(records) == 3764
    assert [sum(record.priority_level == level for record in records) for level in range(1, 13)] == [
        4,
        17,
        5,
        45,
        17,
        6,
        134,
        324,
        241,
        1229,
        1181,
        561,
    ]
    assert records[0].journal_id == "ENVJ-000001"
    assert records[-1].journal_id == "ENVJ-003764"
    assert len({record.formal_title for record in records}) == 3764
    assert len(catalog.priority_signature(records)) == 3764
    assert catalog.PRIORITY_GROUPS == (
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
        "pku_core_natural_sciences",
        "pku_core_non_natural_sciences",
    )


def test_v4_generated_baseline_reuses_ids_and_original_baseline_titles(
    tmp_path: Path,
) -> None:
    """若重跑改写期刊ID、误用正式题名或改变签名，此测试应失败。"""
    catalog = _load_catalog_module()
    generated = _write_generated_baseline(tmp_path)

    records = catalog.parse_v4_baseline(generated)
    replayed = catalog.parse_v4_baseline(generated)

    assert records[0].journal_id == "ENVJ-LOCKED-000001"
    assert records[0].formal_title == "Cell normalized title"
    assert records[0].priority_decision["baseline_title"] == "Cell"
    assert catalog.priority_signature(records) == catalog.priority_signature(replayed)
    assert catalog.priority_signature(records)[0] == (
        "ENVJ-LOCKED-000001",
        1,
        "comprehensive_super_journals",
        None,
    )
    assert catalog.priority_signature(records)[4] == (
        "ENVJ-LOCKED-000005",
        2,
        "ncs_pnas_environment_flagships",
        1,
    )
    assert catalog.priority_signature(records)[-1] == (
        "ENVJ-LOCKED-003764",
        12,
        "pku_core_non_natural_sciences",
        None,
    )


def test_v4_generated_baseline_requires_explicit_baseline_title(tmp_path: Path) -> None:
    """若生成目录缺少基线题名仍被接受，此测试应失败。"""
    catalog = _load_catalog_module()
    generated = _write_generated_baseline(tmp_path, include_baseline_title=False)

    with pytest.raises(ValueError, match="生成目录缺少基线题名列"):
        catalog.parse_v4_baseline(generated)


def test_v4_baseline_excludes_appendix_only_titles() -> None:
    """若附录一的期刊进入十二级签名，此测试应失败。"""
    catalog = _load_catalog_module()
    records = catalog.parse_v4_baseline(BASELINE)

    assert "Innovation" not in {record.formal_title for record in records}


def test_v4_baseline_reads_columns_by_header_after_reordering(tmp_path: Path) -> None:
    """若解析器按列位置而非表头读取生成目录，此测试应失败。"""
    catalog = _load_catalog_module()
    generated = _write_generated_baseline(tmp_path)

    records = catalog.parse_v4_baseline(generated)

    assert records[0].environment_subfields == ["环境科学与工程综合"]
    assert records[0].formal_evidence == [
        "上海交通大学环境科学与工程学院 AAAAA+（U5）"
    ]


def test_approved_source_counts_intersections_and_aliases() -> None:
    """删除受控匹配或来源审计时，此测试应失败。"""
    catalog = _load_catalog_module()

    bundle = catalog.build_catalog_bundle(
        BASELINE,
        catalog.SourcePaths.from_references(REFERENCES),
    )

    assert bundle.match_counts == {
        "CSSCI": (674, 592, 82),
        "PKU_CORE_NATURAL": (1247, 1247, 0),
        "PKU_CORE_NON_NATURAL": (740, 740, 0),
        "SSCI": (3538, 348, 3190),
        "SCIE": (9430, 1499, 7931),
    }
    assert bundle.intersections == {
        "CSSCI&PKU_CORE_NATURAL": 22,
        "CSSCI&PKU_CORE_NON_NATURAL": 520,
        "SSCI&SCIE": 149,
    }
    assert bundle.zero_intersections == {
        "CSSCI&SSCI": 0,
        "CSSCI&SCIE": 0,
        "PKU_CORE_NATURAL&PKU_CORE_NON_NATURAL": 0,
        "PKU_CORE_NATURAL&SSCI": 0,
        "PKU_CORE_NATURAL&SCIE": 0,
        "PKU_CORE_NON_NATURAL&SSCI": 0,
        "PKU_CORE_NON_NATURAL&SCIE": 0,
    }
    assert bundle.controlled_alias_count == 26
    assert bundle.expected_but_unmatched_count == 0
    assert bundle.ambiguous_count == 0

    by_title = {record.formal_title: record for record in bundle.records}
    expected_records = {
        "Nature Climate Change": (
            "ENVJ-000006", 2, 1, {"SSCI", "SCIE"}, {"SSCI:02604", "SCIE:07057"}
        ),
        "Environmental Science & Technology": (
            "ENVJ-000024", 3, None, {"SCIE"}, {"SCIE:02891"}
        ),
        "中国人口·资源与环境": (
            "ENVJ-000169", 7, None, {"CSSCI", "PKU_CORE"},
            {"CSSCI:0620", "PKU_CORE:natural_sciences:0012"},
        ),
        "WIREs Climate Change": (
            "ENVJ-000549", 8, None, {"SSCI", "SCIE"}, {"SSCI:03485", "SCIE:09329"}
        ),
        "城市规划": (
            "ENVJ-000652", 9, None, {"CSSCI", "PKU_CORE"},
            {"CSSCI:0035", "PKU_CORE:natural_sciences:0007"},
        ),
        "WIREs Energy and Environment": (
            "ENVJ-002018", 10, None, {"SCIE"}, {"SCIE:09333"}
        ),
        "Zeitschrift für Geomorphologie": (
            "ENVJ-002022", 10, None, {"SCIE"}, {"SCIE:09394"}
        ),
        "陆军军医大学学报": (
            "ENVJ-002335", 11, None, {"PKU_CORE"},
            {"PKU_CORE:natural_sciences:0005"},
        ),
        "中国社会科学": (
            "ENVJ-003204", 12, None, {"CSSCI", "PKU_CORE"},
            {"CSSCI:0627", "PKU_CORE:non_natural_sciences:0001"},
        ),
    }
    for title, (journal_id, level, rank, memberships, source_ids) in expected_records.items():
        record = by_title[title]
        assert (record.journal_id, record.priority_level, record.ncs_internal_rank) == (
            journal_id,
            level,
            rank,
        )
        assert set(record.index_memberships) == memberships
        assert {item["index_name"] for item in record.source_memberships} == memberships
        assert {item["source_record_id"] for item in record.source_memberships} == source_ids
    assert by_title["Zeitschrift für Geomorphologie"].source_memberships[0][
        "match_method"
    ] == "controlled_alias"
    assert "第三军医大学学报" in by_title["陆军军医大学学报"].aliases

    assert all(record.priority_decision["unchanged"] is True for record in bundle.records)


def test_match_source_records_marks_expected_catalog_membership_unmatched() -> None:
    """删除预期索引回连审计时，此测试应失败。"""
    catalog = _load_catalog_module()
    record = next(
        item for item in catalog.parse_v4_baseline(BASELINE) if item.priority_level == 8
    )

    audit = catalog.match_source_records([record], [], controlled_aliases={})

    assert len(audit) == 1
    expected = audit[0]
    assert expected.status == "expected_but_unmatched"
    assert expected.journal_id == record.journal_id
    assert expected.match_method == "expected_index_membership"
    assert expected.manual_review_required is True
    assert expected.review_reasons == ("SSCI",)


def test_catalog_json_is_canonical_and_cnki_scopes_are_explicit() -> None:
    """Changing the canonical payload or fixed CNKI policies must fail here."""
    catalog = _load_catalog_module()
    bundle = catalog.build_catalog_bundle(
        BASELINE,
        catalog.SourcePaths.from_references(REFERENCES),
    )

    payload = bundle.catalog_payload
    assert set(payload) == {
        "schema_version",
        "catalog_version",
        "catalog_date",
        "revision_date",
        "data_sha256",
        "level_counts",
        "priority_groups",
        "journals",
        "cnki_scopes",
    }
    assert len(payload["journals"]) == 3764
    assert payload["data_sha256"] == catalog.compute_data_sha256(payload)
    assert catalog.canonical_json_bytes({"z": "last", "a": "first"}) == (
        b'{"a":"first","z":"last"}\n'
    )
    with pytest.raises(TypeError):
        catalog.canonical_json_bytes({"value": 1.0})

    journals = payload["journals"]
    pku_members = [record for record in journals if "PKU_CORE" in record["index_memberships"]]
    assert len(pku_members) == 1987
    assert sum(record["priority_level"] <= 10 for record in pku_members) == 245
    assert sum(record["priority_level"] >= 11 for record in pku_members) == 1742
    cssci_members = [record for record in journals if "CSSCI" in record["index_memberships"]]
    assert len(cssci_members) == 592
    assert sum(record["priority_group"] == "environment_cssci" for record in cssci_members) == 241
    assert sum(record["priority_group"] != "environment_cssci" for record in cssci_members) == 351

    scopes = payload["cnki_scopes"]
    assert len(scopes["chinese_environment_top"]["eligible_journal_ids"]) == 6
    assert len(scopes["other_formally_recognized_chinese"]["eligible_journal_ids"]) == 60
    assert len(scopes["environment_cssci"]["eligible_journal_ids"]) == 241
    assert len(scopes["pku_core"]["eligible_journal_ids"]) == 1987
    assert scopes["environment_cssci"]["source_category"] == {
        "code": "P0209",
        "label": "CSSCI",
    }
    assert scopes["pku_core"]["journal_selector"] == "topic_only"
    assert scopes["pku_core"]["source_category"] == {
        "code": "P01",
        "label": "北大核心",
    }


def test_source_registry_has_seven_verified_artifacts_and_resolves_evidence_ids() -> None:
    """Removing an approved snapshot or orphaning evidence IDs must fail here."""
    catalog = _load_catalog_module()
    bundle = catalog.build_catalog_bundle(
        BASELINE,
        catalog.SourcePaths.from_references(REFERENCES),
    )

    registry = bundle.source_registry
    artifacts = registry["artifacts"]
    assert len(artifacts) == 7
    assert {item["filename"] for item in artifacts} == {
        "CSSCI_2025_2026.md",
        "北大中文核心期刊目录_2023_自然科学版.md",
        "北大中文核心期刊目录_2023_.md",
        "Social Sciences Citation Index_20260715.md",
        "Social Sciences Citation Index (SSCI).csv",
        "Science Citation Index Expanded_20260715.md",
        "Science Citation Index Expanded (SCIE).csv",
    }
    assert all(item["bytes"] > 0 and len(item["sha256"]) == 64 for item in artifacts)

    evidence_ids = [item["evidence_id"] for item in registry["evidence_registry"]]
    assert len(evidence_ids) == len(set(evidence_ids))
    registered = set(evidence_ids)
    referenced = {
        evidence_id
        for record in bundle.catalog_payload["journals"]
        for evidence_id in record["evidence_ids"]
        + record["formal_title_evidence_ids"]
    }
    assert referenced <= registered
