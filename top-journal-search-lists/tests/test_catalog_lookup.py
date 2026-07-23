from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "catalog_lookup.py"
CATALOG = ROOT / "references" / "Academic_Journal_Master_Directory_20260715.md"
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"


def load_module():
    spec = importlib.util.spec_from_file_location("catalog_lookup", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载目录解析器：{SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_validate_reads_ten_levels_and_five_sources(self):
        result = self.module.validate_catalog(CATALOG)
        self.assertTrue(result["valid"])
        self.assertEqual(result["priority_levels"], 10)
        self.assertEqual(result["source_blocks"], 5)

    def test_validate_reports_exact_catalog_version(self):
        result = self.module.validate_catalog(CATALOG)
        self.assertEqual(result["catalog_version"], "2026-07-15")

    def test_controlled_online_first_suffix_matches_without_overwriting_input(self):
        result = self.module.lookup_journals(CATALOG, ["经济研究（网络首发）"])[0]
        self.assertEqual(result["input"], "经济研究（网络首发）")
        self.assertEqual(result["matched_title"], "经济研究")
        self.assertEqual(result["match_method"], "controlled_display_suffix")

    def test_malformed_online_first_suffix_is_not_cleaned(self):
        result = self.module.lookup_journals(CATALOG, ["经济研究(网络首发]"])[0]
        self.assertEqual(result["status"], "unmatched")
        self.assertEqual(result["match_method"], None)

    def test_cssci_subject_category_and_all_sources_are_preserved(self):
        result = self.module.lookup_journals(CATALOG, ["经济研究"])[0]
        self.assertEqual(result["priority_level"], 6)
        self.assertIn("经济学", result["subject_categories"])
        self.assertIn("CSSCI_2025_2026.md", result["source_catalogs"])

    def test_normalized_key_collision_is_ambiguous(self):
        index = {}
        self.module._add(index, "A.B", 8, "ssci", "one.md")
        self.module._add(index, "AB", 9, "cssci", "two.md")
        result = self.module.lookup_journal(index, "AB")
        self.assertEqual(result["status"], "ambiguous")
        self.assertIsNone(result["priority_level"])
        self.assertEqual(result["candidates"], ["A.B", "AB"])

    def test_default_catalog_is_bundled_reference(self):
        self.assertEqual(self.module.DEFAULT_CATALOG.resolve(), CATALOG.resolve())

    def _write_catalog_variant(self, transform):
        text = transform(CATALOG.read_text(encoding="utf-8-sig"))
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".md",
            dir=ROOT / "tests",
            delete=False,
        )
        with handle:
            handle.write(text)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def test_validate_rejects_wrong_source_filename(self):
        path = self._write_catalog_variant(
            lambda text: text.replace(
                "Social Sciences Citation Index_20260715.md",
                "Wrong_SSCI_Source.md",
            )
        )
        with self.assertRaisesRegex(ValueError, "来源文件"):
            self.module.validate_catalog(path)

    def test_validate_rejects_extra_priority_group(self):
        path = self._write_catalog_variant(
            lambda text: text.replace(
                '    group: "scie"',
                '    group: "scie"\n    group: "unexpected_extra"',
                1,
            )
        )
        with self.assertRaisesRegex(ValueError, "优先级分组"):
            self.module.validate_catalog(path)

    def test_extract_source_blocks_rejects_duplicate_source_marker(self):
        text = "\n".join(
            [
                "<!-- SOURCE_BEGIN: duplicate.md -->",
                "first",
                "<!-- SOURCE_END: duplicate.md -->",
                "<!-- SOURCE_BEGIN: duplicate.md -->",
                "second",
                "<!-- SOURCE_END: duplicate.md -->",
            ]
        )
        with self.assertRaisesRegex(ValueError, "重复"):
            self.module._extract_source_blocks(text)

    def test_representative_journals_match_requested_levels(self):
        names = [
            "American Economic Review",
            "Nature Human Behaviour",
            "MIS Quarterly",
            "Academy of Management Annals",
            "Review of Economics and Statistics",
            "经济研究",
            "Social Forces",
            "管理科学学报",
            "Nature Communications",
            "北京大学教育评论",
            "ACS Applied Materials & Interfaces",
        ]
        results = self.module.lookup_journals(CATALOG, names)
        levels = {item["input"]: item["priority_level"] for item in results}
        self.assertEqual(levels["American Economic Review"], 1)
        self.assertEqual(levels["Nature Human Behaviour"], 2)
        self.assertEqual(levels["MIS Quarterly"], 3)
        self.assertEqual(levels["Academy of Management Annals"], 4)
        self.assertEqual(levels["Review of Economics and Statistics"], 5)
        self.assertEqual(levels["经济研究"], 6)
        self.assertEqual(levels["Social Forces"], 8)
        self.assertEqual(levels["管理科学学报"], 6)
        self.assertEqual(levels["Nature Communications"], 2)
        self.assertEqual(levels["北京大学教育评论"], 9)
        self.assertEqual(levels["ACS Applied Materials & Interfaces"], 10)

    def test_ncs_internal_social_science_rank_is_preserved(self):
        results = self.module.lookup_journals(
            CATALOG, ["Nature Human Behaviour", "Nature Communications"]
        )
        ranks = {item["input"]: item["ncs_internal_rank"] for item in results}
        self.assertEqual(ranks["Nature Human Behaviour"], 1)
        self.assertEqual(ranks["Nature Communications"], 2)

    def test_ncs_duplicate_lines_use_each_match_position(self):
        heading = "### 🌟 置顶板块：人文、哲学与社会科学（含交叉研究）期刊"
        main_heading = "### 第一部分：Nature"
        duplicate = "* **Repeated Journal**"
        text = "\n".join([heading, duplicate, main_heading, duplicate])
        calls = []
        original_add = self.module._add

        def capture_add(index, title, level, group, source, **kwargs):
            calls.append(kwargs["ncs_internal_rank"])

        self.module._add = capture_add
        try:
            self.module._index_ncs({}, text)
        finally:
            self.module._add = original_add
        self.assertEqual(calls, [1, 2])

    def test_title_matching_normalizes_the_ampersand_and_fullwidth_text(self):
        index = {}
        self.module._add(
            index,
            "The Journal of Law & Economics",
            8,
            "ssci",
            "source.md",
        )
        key = self.module.normalize_title("Ｊｏｕｒｎａｌ ｏｆ Ｌａｗ ＆ Ｅｃｏｎｏｍｉｃｓ")
        self.assertIn(key, index)
        self.assertEqual(index[key][0]["matched_title"], "The Journal of Law & Economics")

    def test_overlap_uses_highest_priority(self):
        result = self.module.lookup_journals(CATALOG, ["Nature"])[0]
        self.assertEqual(result["priority_level"], 2)
        self.assertIn("NCS_PNAS_Directory.md", result["source_catalogs"])

    def test_unknown_journal_is_unmatched(self):
        result = self.module.lookup_journals(CATALOG, ["Imaginary Journal XYZ"])[0]
        self.assertIsNone(result["priority_level"])
        self.assertEqual(result["status"], "unmatched")

    def test_missing_catalog_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.module.validate_catalog(Path("missing-catalog.md"))

    def test_invalid_catalog_raises_value_error(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".md",
            dir=ROOT / "tests",
            delete=False,
        ) as handle:
            handle.write("# invalid\n")
            path = Path(handle.name)
        try:
            with self.assertRaises(ValueError):
                self.module.validate_catalog(path)
        finally:
            path.unlink(missing_ok=True)

    def test_cli_accepts_catalog_and_returns_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--catalog",
                str(CATALOG),
                "lookup",
                "American Economic Review",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload[0]["priority_level"], 1)
        self.assertIn("ncs_internal_rank", payload[0])

    def test_cli_uses_bundled_catalog_without_catalog_argument(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "validate"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["priority_levels"], 10)
        self.assertEqual(payload["source_blocks"], 5)

    def test_docs_require_ncs_rank_sorting_and_honest_empty_level_seven(self):
        for path in (SKILL, README):
            text = path.read_text(encoding="utf-8")
            self.assertIn("ncs_internal_rank", text)
            self.assertIn("--catalog", text)
            self.assertIn("第七级", text)
            self.assertIn("空层级", text)
            self.assertIn("不得伪造期刊", text)

    def test_skill_files_do_not_contain_original_machine_paths(self):
        for path in (SKILL, README, SCRIPT):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?i)\b[A-Z]:\\")
            self.assertNotIn("/Users/", text)
            self.assertNotIn("/home/", text)


if __name__ == "__main__":
    unittest.main()

CATALOG_LAYOUTS = (
    ("scripts", ROOT / "scripts" / "catalog_lookup.py"),
    ("mcpb", ROOT / "mcpb" / "src" / "catalog_lookup.py"),
)

_VARIANT_KEY_EXPECTATIONS = {
    "accountingreview": 3,
    "journalofaccountingandeconomics": 3,
    "journaloffinance": 3,
    "reviewoffinancialstudies": 3,
    "accountingorganizationsandsociety": 4,
    "americaneconomicjournalappliedeconomics": 5,
    "americaneconomicjournalmacroeconomics": 5,
    "americaneconomicjournalmicroeconomics": 5,
    "americaneconomicjournaleconomicpolicy": 5,
    "americaneconomicreviewinsights": 5,
    "auditingajournalofpracticeandtheory": 5,
    "corporategovernanceaninternationalreview": 5,
    "environmentalandresourceeconomics": 5,
    "genevapapersonriskandinsuranceissuesandpractice": 5,
    "insurancemathematicsandeconomics": 5,
    "journalofeconomicdynamicsandcontrol": 5,
    "journaloflawandeconomics": 5,
    "journaloflaweconomicsandorganization": 5,
    "journalofmoneycreditandbanking": 5,
    "randdmanagement": 5,
    "supplychainmanagementaninternationaljournal": 5,
    "transportationresearchpartbmethodological": 5,
    "transportationresearchpartapolicyandpractice": 5,
    "transportationresearchpartelogisticsandtransportationreview": 5,
    "economicsofhistory": 5,
    "humanitiesandsocialsciencescommunications": 2,
    "npjscienceoflearning": 2,
    "npjurbansustainability": 2,
    "cellstemcell": 2,
    "trendsinendocrinologyandmetabolism": 2,
    "transportationresearchpartdtransportandenvironment": 8,
    "journalsofgerontologyseriesabiologicalsciencesandmedicalsciences": 8,
    "journaloftheroyalstatisticalsocietyseriesastatisticsinsociety": 8,
    "structuralequationmodelingamultidisciplinaryjournal": 8,
    "transportmetricaatransportscience": 8,
}


def _load_layout_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"catalog_lookup_{path.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载布局模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_two_variants(module, key: str, index: dict[str, list[dict]]) -> list[str]:
    candidates = []
    seen = set()
    for buckets in index.values():
        for entry in buckets:
            entry_keys = (
                module._keys_for_title(entry["matched_title"])
                if hasattr(module, "_keys_for_title")
                else {module.normalize_title(entry["matched_title"])}
            )
            if key not in entry_keys:
                continue
            title = entry["matched_title"]
            if title in seen:
                continue
            candidates.append(title)
            seen.add(title)
    if not candidates:
        return []
    if len(candidates) >= 2:
        return candidates[:2]
    primary = candidates[0]
    if " and " in primary:
        return [primary, primary.replace(" and ", " & ")]
    if "&" in primary:
        return [primary, primary.replace(" & ", " and ")]
    return [primary, f"The {primary}"]


class CatalogLookupCrossLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout_modules = [(_load_layout_module(path), label, path) for label, path in CATALOG_LAYOUTS]

    def test_default_catalog_is_discoverable_in_both_layouts(self):
        for module, _label, _path in self.layout_modules:
            self.assertTrue(module.DEFAULT_CATALOG.is_file())

    def test_invalid_catalog_path_or_format_is_reported_without_traceback(self):
        for module, _label, path in self.layout_modules:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(path),
                    "--catalog",
                    "missing-catalog.md",
                    "lookup",
                    "American Economic Review",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("FileNotFoundError", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)

    def test_layouts_build_index_and_merge_communications_series_to_level_2(self):
        for module, _label, _path in self.layout_modules:
            index = module.build_index(module.DEFAULT_CATALOG)
            self.assertFalse(hasattr(module, "COMMUNICATIONS_SERIES"))
            for title in ("Communications Biology", "Communications Chemistry"):
                result = module.lookup_journals(
                    module.DEFAULT_CATALOG,
                    [title],
                )[0]
                self.assertEqual(result["status"], "matched")
                self.assertEqual(result["priority_level"], 2)

    def test_display_suffix_pattern_has_no_leading_whitespace_backtracking(self):
        for module, _label, _path in self.layout_modules:
            self.assertTrue(module._DISPLAY_SUFFIX.pattern.startswith("(?:"))

    def test_bilingual_parallel_journal_title_is_not_truncated(self):
        title = (
            "Zeitschrift fur Ethnologie - "
            "Journal of Social and Cultural Anthropology"
        )
        for module, _label, _path in self.layout_modules:
            self.assertEqual(module._clean_title(title), title)

    def test_clean_title_removes_only_ascii_spaced_chinese_description_suffix(self):
        expectations = {
            "Journal - 中文说明": "Journal",
            "Journal (AJPT) - 中文说明": "Journal",
            "Journal [AJPT] - 中文说明": "Journal",
            "Journal 【AJPT】 - 中文说明": "Journal",
            "Journal-中文说明": "Journal-中文说明",
            "Journal – 中文说明": "Journal – 中文说明",
        }
        for module, label, _path in self.layout_modules:
            for title, expected in expectations.items():
                with self.subTest(layout=label, title=title):
                    self.assertEqual(module._clean_title(title), expected)

    def test_design_spec_distinguishes_variants_from_real_ambiguity(self):
        spec = (
            ROOT.parent
            / "docs/superpowers/specs/2026-07-22-cnki-public-theme-search-design.md"
        ).read_text(encoding="utf-8")
        self.assertIn("冠词、连接词、标点、大小写和全半角", spec)
        self.assertIn("保守变体键", spec)
        self.assertIn("采用数值最小的最高优先级", spec)

    def test_variant_grouping_and_min_level_for_expected_keys_in_both_layouts(self):
        for module, _label, _path in self.layout_modules:
            index = module.build_index(module.DEFAULT_CATALOG)
            for key, expected in _VARIANT_KEY_EXPECTATIONS.items():
                variants = _get_two_variants(module, key, index)
                self.assertGreaterEqual(
                    len(variants),
                    1,
                    f"未找到变体：{key}",
                )
                for variant in variants:
                    result = module.lookup_journals(module.DEFAULT_CATALOG, [variant])[0]
                    self.assertEqual(result["status"], "matched", result)
                    self.assertEqual(result["priority_level"], expected)
                if len(variants) > 1:
                    self.assertNotEqual(variants[0], variants[-1])
