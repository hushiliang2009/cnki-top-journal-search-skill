from pathlib import Path


def test_skill_metadata_covers_environment_scope_and_excludes_generic_finance(
    skill_root: Path,
) -> None:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    for trigger in (
        "environmental science",
        "ecology",
        "environmental chemistry",
        "environmental engineering",
        "climate",
        "oceans",
        "soil",
        "environmental health",
        "environmental economics",
        "environmental management",
        "environmental law",
        "sustainability",
    ):
        assert trigger in frontmatter
    assert "公司金融与董事会治理" in text
    assert "不触发本 Skill" in text


def test_skill_requires_script_lookup_ai4scholar_deduplication_and_output_order(
    skill_root: Path,
) -> None:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    for required in (
        "不得全文加载",
        "scripts/catalog_lookup.py validate",
        "scripts/catalog_lookup.py lookup",
        "mcp__ai4scholar__search_google_scholar",
        "mcp__ai4scholar__search_semantic",
        "mcp__ai4scholar__search_pubmed",
        "DOI 去重",
        "规范化",
        "篇名、作者和年度",
    ):
        assert required in text
    headings = (
        "1. 检索范围",
        "2. 按十二级目录整理的论文",
        "3. 环境细分领域及正式证据",
        "4. 文献综合",
        "5. 检索限制与未匹配记录",
    )
    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_skill_and_packaging_texts_use_only_relative_portable_paths(
    skill_root: Path,
) -> None:
    files = [
        skill_root / "SKILL.md",
        skill_root / "README.md",
        skill_root / "agents/openai.yaml",
        *(skill_root / "scripts").rglob("*.py"),
        *(skill_root / "installers").glob("*"),
        *(
            path
            for path in (skill_root / "mcpb").rglob("*.py")
            if ".venv" not in path.parts
        ),
        skill_root / "mcpb/manifest.json",
        skill_root / "mcpb/pyproject.toml",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "G:\\" not in text, path
        assert "C:\\Users\\" not in text, path
        assert "/Users/" not in text, path
        assert "/home/" not in text, path


def test_environment_docs_state_one_pku_scope_and_global_order(
    skill_root: Path,
) -> None:
    text = "\n".join(
        (skill_root / relative).read_text(encoding="utf-8")
        for relative in (
            "SKILL.md", "README.md", "references/cnki-search-env-reference.md",
        )
    )
    assert "other_formally_recognized_chinese" in text
    assert "pku_core" in text
    assert "P01" in text
    assert "第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心" in text
    assert "第11级和第12级不得分别重复检索" in text


def test_environment_docs_state_the_field_and_facet_contract(
    skill_root: Path,
) -> None:
    for relative in (
        "SKILL.md", "README.md", "references/cnki-search-env-reference.md",
    ):
        text = (skill_root / relative).read_text(encoding="utf-8")
        assert "TI → SU → KY → TKA" in text, relative
        assert "累计" in text, relative
        assert "来源类别不是专业检索字段" in text, relative
        assert "first_page_only" in text, relative
        for stale in ("取有效记录最多的那个字段", "逐级替换"):
            assert stale not in text, (relative, stale)


def test_environment_docs_reference_the_v4_twelve_level_catalog(
    skill_root: Path,
) -> None:
    """目录已升到 v4.0 十二级；文档仍写 v3.0 十级会让判级依据对不上。"""
    for relative in ("SKILL.md", "README.md",
                     "references/cnki-search-env-reference.md"):
        text = (skill_root / relative).read_text(encoding="utf-8")
        assert "v3.0" not in text, relative
        assert "十级" not in text, relative
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "环境科学与工程学科顶尖期刊目录_v4.0.md" in skill
    assert "pku_core_natural_sciences" in skill
    assert "pku_core_non_natural_sciences" in skill


def test_environment_docs_state_the_single_group_diagnostic_boundaries(
    skill_root: Path,
) -> None:
    """单组调用的两个语义边界必须写明，否则调用方会误读诊断字段。"""
    text = "\n".join(
        (skill_root / relative).read_text(encoding="utf-8")
        for relative in (
            "SKILL.md", "references/cnki-search-env-reference.md",
        )
    )
    assert "already_covered_higher_priority_count" in text
    assert "excluded_out_of_scope_records" in text
    assert "source_category_applied" in text
