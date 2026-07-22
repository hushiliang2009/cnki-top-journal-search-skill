from pathlib import Path


def test_cnki_runtime_contract(skill_root: Path) -> None:
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


def test_cnki_documentation_states_safety_and_scope(skill_root: Path) -> None:
    documents = (
        "SKILL.md",
        "README.md",
        "references/cnki-search-reference.md",
    )
    for document in documents:
        content = (skill_root / document).read_text(encoding="utf-8")
        for required in (
            "低频串行",
            "最多 3 页",
            "最多 10",
            "最多 5",
            "4 至 7 秒",
            "3 至 6 秒",
            "8 至 15 秒",
            "用户明确选择",
            "保存目录",
            "确认具有访问权限",
            "知网官方全文按钮",
            "不得构造隐藏下载链接",
            "不持久化 Cookie",
            "账号",
            "密码",
            "验证码",
        ):
            assert required in content, f"{document} 缺少 {required}"


def test_cnki_documentation_excludes_evasion_and_password_collection(skill_root: Path) -> None:
    combined = "\n".join(
        (skill_root / name).read_text(encoding="utf-8")
        for name in ("SKILL.md", "README.md")
    ).casefold()
    assert "输入密码参数" not in combined
    assert "自动破解验证码" not in combined
    assert "绕过反爬" not in combined


def test_cnki_package_contains_only_new_search_entry(skill_root: Path) -> None:
    included = [
        skill_root / "scripts" / "cnki_search",
        skill_root / "mcpb" / "src" / "cnki_search",
        skill_root / "SKILL.md",
        skill_root / "README.md",
        skill_root / "references" / "cnki-search-reference.md",
    ]
    text = "\n".join(
        path.read_text(encoding="utf-8")
        if path.is_file()
        else "\n".join(p.read_text(encoding="utf-8") for p in path.rglob("*.py"))
        for path in included
    ).casefold()
    assert "kns8s/advsearch" in text
    assert "kns/advsearch" not in text
    assert "resolve_old_search_url" not in text
    assert "open_old_search" not in text
    assert "assert_old_search_page" not in text
