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

    def test_writing_variants_of_one_journal_merge_to_best_level(self):
        """同一本刊的书写变体必须归并取最小层级，不得判为 ambiguous。

        这些期刊此前因 The 有无、& / and、副标题分隔符、全半角括号的差异
        生成了两个条目，被判 ambiguous、层级置空，并被排序推到结果末位。
        """
        expected = {
            "The Journal of Finance": 3,
            "The Accounting Review": 3,
            "Journal of Accounting and Economics": 3,
            "Accounting, Organizations and Society": 4,
            "经济学(季刊)": 6,
        }
        results = self.module.lookup_journals(CATALOG, list(expected))
        for journal, result in zip(expected, results, strict=True):
            with self.subTest(journal=journal):
                self.assertEqual(result["status"], "matched")
                self.assertEqual(result["priority_level"], expected[journal])
                self.assertFalse(result["manual_review_required"])

    def test_index_collisions_retain_distinct_conservative_signatures(self):
        index = self.module.build_index(CATALOG)
        ambiguous = {
            key: [item["matched_title"] for item in entries]
            for key, entries in index.items()
            if len(entries) > 1
        }
        self.assertTrue(ambiguous)
        for entries in (index[key] for key in ambiguous):
            signatures = {
                (entry["normalized_signature"], entry["merge_signature"])
                for entry in entries
            }
            self.assertGreater(len(signatures), 1)

    def test_variant_key_keeps_genuinely_different_titles_apart(self):
        # 句点不参与归并，因此 A.B 与 AB 仍是两本不同的刊
        self.assertNotEqual(self.module.variant_key("A.B"), self.module.variant_key("AB"))
        # 冠词、& / and、分隔符、全半角括号只是同一本刊的书写差异
        self.assertEqual(
            self.module.variant_key("The Journal of Finance"),
            self.module.variant_key("Journal of Finance"),
        )
        self.assertEqual(
            self.module.variant_key("Accounting, Organizations & Society"),
            self.module.variant_key("Accounting Organizations and Society"),
        )
        self.assertEqual(
            self.module.variant_key("经济学(季刊)"), self.module.variant_key("经济学（季刊）")
        )

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
    "accountingreview": 3, "journalofaccountingandeconomics": 3, "journaloffinance": 3,
    "reviewoffinancialstudies": 3, "accountingorganizationsandsociety": 4,
    "americaneconomicjournalappliedeconomics": 5, "americaneconomicjournalmacroeconomics": 5,
    "americaneconomicjournalmicroeconomics": 5, "americaneconomicjournaleconomicpolicy": 5,
    "americaneconomicreviewinsights": 5, "auditingajournalofpracticeandtheory": 5,
    "corporategovernanceaninternationalreview": 5, "environmentalandresourceeconomics": 5,
    "genevapapersonriskandinsuranceissuesandpractice": 5, "insurancemathematicsandeconomics": 5,
    "journalofeconomicdynamicsandcontrol": 5, "journaloflawandeconomics": 5,
    "journaloflaweconomicsandorganization": 5, "journalofmoneycreditandbanking": 5,
    "randdmanagement": 5, "supplychainmanagementaninternationaljournal": 5,
    "transportationresearchpartbmethodological": 5, "transportationresearchpartapolicyandpractice": 5,
    "transportationresearchpartelogisticsandtransportationreview": 5, "economicsofhistory": 5,
    "humanitiesandsocialsciencescommunications": 2, "npjscienceoflearning": 2,
    "npjurbansustainability": 2, "cellstemcell": 2, "trendsinendocrinologyandmetabolism": 2,
    "transportationresearchpartdtransportandenvironment": 8,
    "journalsofgerontologyseriesabiologicalsciencesandmedicalsciences": 8,
    "journaloftheroyalstatisticalsocietyseriesastatisticsinsociety": 8,
    "structuralequationmodelingamultidisciplinaryjournal": 8,
    "transportmetricaatransportscience": 8,
}


def _load_layout_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"catalog_lookup_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载布局模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogLookupCrossLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout_modules = [(_load_layout_module(path), label, path) for label, path in CATALOG_LAYOUTS]

    def test_both_layouts_find_own_catalog_and_rank_key_journals(self):
        for module, label, _path in self.layout_modules:
            with self.subTest(layout=label):
                self.assertTrue(module.DEFAULT_CATALOG.is_file())
                results = module.lookup_journals(
                    module.DEFAULT_CATALOG,
                    ["The Journal of Finance", "Communications Biology", "Communications Chemistry"],
                )
                self.assertEqual([item["priority_level"] for item in results], [3, 2, 2])

    def test_catalog_cli_uses_short_errors_without_traceback(self):
        for _module, label, path in self.layout_modules:
            with self.subTest(layout=label):
                completed = subprocess.run(
                    [sys.executable, str(path), "--catalog", "missing-catalog.md", "lookup", "Journal"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("Academic_Journal_Master_Directory_20260715.md", completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_catalog_entries_not_code_special_cases_and_title_cleaning_is_conservative(self):
        bilingual = "Zeitschrift fur Ethnologie - Journal of Social and Cultural Anthropology"
        expectations = {
            "Journal - 中文说明": "Journal",
            "Journal (AJPT) - 中文说明": "Journal",
            "Journal 【AJPT】 - 中文说明": "Journal",
            "Journal-中文说明": "Journal-中文说明",
            "Journal – 中文说明": "Journal – 中文说明",
        }
        for module, label, _path in self.layout_modules:
            with self.subTest(layout=label):
                self.assertFalse(hasattr(module, "COMMUNICATIONS_SERIES"))
                self.assertFalse(hasattr(module, "_NCS_SERIES"))
                self.assertTrue(module._DISPLAY_SUFFIX.pattern.startswith("(?:"))
                self.assertEqual(module._clean_title(bilingual), bilingual)
                for title, expected in expectations.items():
                    self.assertEqual(module._clean_title(title), expected)

    def test_35_variant_groups_preserve_minimum_level_and_real_ambiguity(self):
        self.assertEqual(len(_VARIANT_KEY_EXPECTATIONS), 35)
        for module, label, _path in self.layout_modules:
            index = module.build_index(module.DEFAULT_CATALOG)
            for key, expected in _VARIANT_KEY_EXPECTATIONS.items():
                candidates = []
                seen = set()
                for bucket in index.values():
                    for entry in bucket:
                        if key not in module._keys_for_title(entry["matched_title"]):
                            continue
                        if entry["matched_title"] not in seen:
                            candidates.append(entry["matched_title"])
                            seen.add(entry["matched_title"])
                        if len(candidates) == 2:
                            break
                    if len(candidates) == 2:
                        break
                if len(candidates) == 1:
                    primary = candidates[0]
                    if primary.casefold().startswith("the "):
                        candidates.append(primary[4:])
                    elif " and " in primary:
                        candidates.append(primary.replace(" and ", " & "))
                    elif " & " in primary:
                        candidates.append(primary.replace(" & ", " and "))
                    else:
                        candidates.append(f"The {primary}")
                with self.subTest(layout=label, key=key):
                    self.assertGreaterEqual(len(candidates), 1)
                    for title in candidates:
                        result = module.lookup_journal(index, title)
                        self.assertEqual(result["status"], "matched")
                        self.assertEqual(result["priority_level"], expected)
            ambiguous = {}
            module._add(ambiguous, "A.B", 8, "ssci", "one.md")
            module._add(ambiguous, "AB", 9, "cssci", "two.md")
            self.assertEqual(module.lookup_journal(ambiguous, "AB")["status"], "ambiguous")
