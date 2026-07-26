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
        "2. 按十级目录整理的论文",
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
