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


ENV_DOCS = ("SKILL.md", "README.md", "references/cnki-search-env-reference.md")


def _section_containing(text: str, needle: str) -> str:
    """取包含 needle 的那个段落，避免关键词分散在全文各处也能凑齐断言。"""
    assert needle in text, needle
    blocks = [block for block in text.split("\n\n") if needle in block]
    return "\n".join(blocks)


def test_environment_docs_state_one_pku_scope_and_global_order(
    skill_root: Path,
) -> None:
    # 逐文件校验：拼接后断言会让"任一份写到就全过"，与四组顺序需处处一致的意图不符。
    for relative in ENV_DOCS:
        text = (skill_root / relative).read_text(encoding="utf-8")
        assert "other_formally_recognized_chinese" in text, relative
        assert "pku_core" in text, relative
        assert "P01" in text, relative
        assert "第6级、第7级中文期刊、第9级CSSCI、第11—12级北大核心" in text, relative
        assert "第11级和第12级不得分别重复检索" in text, relative


def test_environment_docs_state_the_pku_core_membership_span(
    skill_root: Path,
) -> None:
    """1987 横跨 1—12 级；写成"只有第11—12级"会让调用方误判组内合格范围。"""
    for relative in ENV_DOCS:
        text = (skill_root / relative).read_text(encoding="utf-8")
        block = _section_containing(text, "1987")
        assert "1742" in block, relative
        assert "245" in block, relative
        assert "横跨" in block, relative
        assert "1—12" in block, relative


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
    # agents/openai.yaml 也在对外描述层级，漏掉它就没人拦得住"十级"回归。
    for relative in (*ENV_DOCS, "agents/openai.yaml"):
        text = (skill_root / relative).read_text(encoding="utf-8")
        assert "v3.0" not in text, relative
        assert "十级" not in text, relative
        assert "ten-level" not in text, relative
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "环境科学与工程学科顶尖期刊目录_v4.0.md" in skill
    assert "pku_core_natural_sciences" in skill
    assert "pku_core_non_natural_sciences" in skill
    assert not (skill_root / "references"
                / "环境科学与工程学科顶尖期刊目录_v3.0.md").exists()


def test_environment_docs_state_the_single_group_diagnostic_boundaries(
    skill_root: Path,
) -> None:
    """光提到字段名不够：语义写反了照样能通过，所以按段落锚定正反两面。"""
    for relative in ("SKILL.md", "references/cnki-search-env-reference.md"):
        text = (skill_root / relative).read_text(encoding="utf-8")

        covered = _section_containing(text, "already_covered_higher_priority_count")
        assert "单组" in covered, relative
        assert "恒为 0" in covered, relative
        assert "不代表" in covered or "不等于" in covered, relative

        excluded = _section_containing(text, "excluded_out_of_scope_records")
        assert "不占限额" in excluded, relative

        applied = _section_containing(text, "source_category_applied")
        assert "合取" in applied, relative
        assert "低报" in applied, relative

        for wrong in ("跨组去重结果", "已扣除重复", "组外记录计入限额", "乐观上报"):
            assert wrong not in text, (relative, wrong)
