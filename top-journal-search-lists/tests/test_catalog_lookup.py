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

    def test_catalog_has_no_unresolved_normalized_collisions(self):
        index = self.module.build_index(CATALOG)
        ambiguous = {
            key: [item["matched_title"] for item in entries]
            for key, entries in index.items()
            if len(entries) > 1
        }
        self.assertEqual(ambiguous, {})

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

# 固定依据：2026-07-23_cnki-skill-audit-round1.md 附录 A 的 35 例。
# 这里直接保存输入与预期，禁止通过生产函数反向生成候选。
_EXPLICIT_VARIANT_CASES = (
    (("The Accounting Review", "Accounting Review"), 3),
    (("Journal of Accounting and Economics", "Journal of Accounting & Economics"), 3),
    (("The Journal of Finance", "Journal of Finance"), 3),
    (("The Review of Financial Studies", "Review of Financial Studies"), 3),
    (("Accounting, Organizations and Society", "Accounting Organizations and Society"), 4),
    (("American Economic Journal: Applied Economics", "American Economic Journal-Applied Economics"), 5),
    (("American Economic Journal: Macroeconomics", "American Economic Journal-Macroeconomics"), 5),
    (("American Economic Journal: Microeconomics", "American Economic Journal-Microeconomics"), 5),
    (("American Economic Journal: Economic Policy", "American Economic Journal-Economic Policy"), 5),
    (("American Economic Review: Insights", "American Economic Review-Insights"), 5),
    (("Auditing: A Journal of Practice & Theory", "Auditing-a Journal of Practice & Theory"), 5),
    (("Corporate Governance: An International Review", "Corporate Governance-an International Review"), 5),
    (("Environmental and Resource Economics", "Environmental & Resource Economics"), 5),
    (("Geneva Papers on Risk and Insurance: Issues and Practice", "Geneva Papers on Risk and Insurance-Issues and Practice"), 5),
    (("Insurance: Mathematics and Economics", "Insurance Mathematics & Economics"), 5),
    (("Journal of Economic Dynamics and Control", "Journal of Economic Dynamics & Control"), 5),
    (("Journal of Law and Economics", "Journal of Law & Economics"), 5),
    (("Journal of Law, Economics, and Organization", "Journal of Law Economics & Organization"), 5),
    (("Journal of Money, Credit and Banking", "Journal of Money Credit and Banking"), 5),
    (("R&D Management", "R & d Management"), 5),
    (("Supply Chain Management: An International Journal", "Supply Chain Management-an International Journal"), 5),
    (("Transportation Research Part B: Methodological", "Transportation Research Part B-Methodological"), 5),
    (("Transportation Research Part A: Policy and Practice", "Transportation Research Part A-Policy and Practice"), 5),
    (("Transportation Research Part E: Logistics and Transportation Review", "Transportation Research Part E-Logistics and Transportation Review"), 5),
    (("经济学(季刊)", "经济学（季刊）"), 6),
    (("Humanities and Social Sciences Communications", "Humanities & Social Sciences Communications"), 2),
    (("npj Science of Learning", "Npj Science of Learning"), 2),
    (("npj Urban Sustainability", "Npj Urban Sustainability"), 2),
    (("Cell Stem Cell", "Cell STEM Cell"), 2),
    (("Trends in Endocrinology & Metabolism", "Trends in Endocrinology and Metabolism"), 2),
    (("Transportation Research Part d-Transport and Environment", "Transportation Research Part D-Transport and Environment"), 8),
    (("Journals of Gerontology Series a-Biological Sciences and Medical Sciences", "Journals of Gerontology Series A-Biological Sciences and Medical Sciences"), 8),
    (("Journal of the Royal Statistical Society Series a-Statistics in Society", "Journal of the Royal Statistical Society Series A-Statistics in Society"), 8),
    (("Structural Equation Modeling-a Multidisciplinary Journal", "Structural Equation Modeling-A Multidisciplinary Journal"), 8),
    (("Transportmetrica a-Transport Science", "Transportmetrica A-Transport Science"), 8),
)


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
            "Journal [AJPT] - 中文说明": "Journal",
            "IEEE Transactions on Very Large Scale Integration (VLSI) Systems": "IEEE Transactions on Very Large Scale Integration (VLSI) Systems",
            "Journal (AJPT) - English description": "Journal (AJPT) - English description",
            "Journal 【AJPT】 - English description": "Journal 【AJPT】 - English description",
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

    def test_35_explicit_variant_pairs_preserve_minimum_level(self):
        self.assertEqual(len(_EXPLICIT_VARIANT_CASES), 35)
        for module, label, _path in self.layout_modules:
            index = module.build_index(module.DEFAULT_CATALOG)
            for variants, expected in _EXPLICIT_VARIANT_CASES:
                with self.subTest(layout=label, variants=variants):
                    for title in variants:
                        result = module.lookup_journal(index, title)
                        self.assertEqual(result["status"], "matched")
                        self.assertEqual(result["priority_level"], expected)

    def test_variant_merges_preserve_source_and_subject_unions(self):
        expectations = (
            (
                "经济学（季刊）",
                6,
                {"Top_Academic_Journals_all.md", "CSSCI_2025_2026.md"},
                {"经济学"},
            ),
            (
                "Journal of Accounting & Economics",
                3,
                {"Top_Academic_Journals_all.md", "Social Sciences Citation Index_20260715.md"},
                {"Business, Finance", "Economics"},
            ),
            (
                "Transportation Research Part B-Methodological",
                5,
                {"Top_Academic_Journals_all.md", "Social Sciences Citation Index_20260715.md", "Science Citation Index Expanded_20260715.md"},
                {"Economics", "Transportation", "Engineering, Civil", "Operations Research & Management Science", "Transportation Science & Technology"},
            ),
        )
        for module, label, _path in self.layout_modules:
            for title, level, sources, subjects in expectations:
                with self.subTest(layout=label, title=title):
                    result = module.lookup_journals(module.DEFAULT_CATALOG, [title])[0]
                    self.assertEqual(result["status"], "matched")
                    self.assertEqual(result["priority_level"], level)
                    self.assertTrue(sources.issubset(result["source_catalogs"]))
                    self.assertTrue(subjects.issubset(result["subject_categories"]))

    def test_real_ambiguity_remains_ambiguous(self):
        for module, label, _path in self.layout_modules:
            ambiguous = {}
            module._add(ambiguous, "A.B", 8, "ssci", "one.md")
            module._add(ambiguous, "AB", 9, "cssci", "two.md")
            with self.subTest(layout=label):
                self.assertEqual(module.lookup_journal(ambiguous, "AB")["status"], "ambiguous")

    def test_history_titles_do_not_gain_unlisted_generic_aliases(self):
        for module, label, _path in self.layout_modules:
            index = {}
            module._add(index, "Economic History", 5, "field_top", "catalog-one.md")
            module._add(index, "Business History", 8, "ssci", "catalog-two.md")
            with self.subTest(layout=label):
                result = module.lookup_journal(index, "Economics of History")
                self.assertEqual(result["status"], "unmatched")
