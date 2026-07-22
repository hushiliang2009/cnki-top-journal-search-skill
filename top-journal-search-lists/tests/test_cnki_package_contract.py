from pathlib import Path
import re


DIRECT_NEW_SEARCH_URL = "https://kns.cnki.net/kns8s/AdvSearch"
HHU_NEW_SEARCH_URL = (
    "https://webvpn.hhu.edu.cn/https/"
    "77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch"
)
SOURCE_ROOTS = (
    Path("scripts/cnki_search"),
    Path("mcpb/src/cnki_search"),
)
BUILD_INPUTS = (
    Path("SKILL.md"),
    Path("README.md"),
    Path("references/cnki-search-reference.md"),
    Path("mcpb/manifest.json"),
    Path("installers/install.ps1"),
    Path("installers/install.sh"),
)
FORBIDDEN_SEARCH_TOKENS = (
    "kns/advsearch",
    "old_search",
    "legacy_search",
    "resolve_old",
    "open_old",
    "assert_old",
    "is_old_search",
    "fallback",
    "dbcode=",
)


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _scanned_files(skill_root: Path) -> list[Path]:
    files = [
        *(path for root in SOURCE_ROOTS for path in _python_files(skill_root / root)),
        *(skill_root / path for path in BUILD_INPUTS),
    ]
    return sorted(files, key=lambda path: path.relative_to(skill_root).as_posix())


def _relative(skill_root: Path, paths: list[Path]) -> str:
    return ", ".join(path.relative_to(skill_root).as_posix() for path in paths)


def test_cnki_runtime_contract(skill_root: Path) -> None:
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


def test_cnki_documentation_states_safety_and_scope(skill_root: Path) -> None:
    for relative_path in BUILD_INPUTS[:3]:
        content = (skill_root / relative_path).read_text(encoding="utf-8")
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
            assert required in content, f"{relative_path.as_posix()} 缺少 {required}"


def test_cnki_documentation_excludes_evasion_and_password_collection(skill_root: Path) -> None:
    combined = "\n".join(
        (skill_root / name).read_text(encoding="utf-8")
        for name in ("SKILL.md", "README.md")
    ).casefold()
    assert "输入密码参数" not in combined
    assert "自动破解验证码" not in combined
    assert "绕过反爬" not in combined


def test_cnki_package_declares_the_two_exact_new_search_urls(skill_root: Path) -> None:
    for root in SOURCE_ROOTS:
        session_file = skill_root / root / "session.py"
        content = session_file.read_text(encoding="utf-8")
        assert DIRECT_NEW_SEARCH_URL in content, f"{session_file.relative_to(skill_root)} 缺少直接入口"
        assert HHU_NEW_SEARCH_URL in content, f"{session_file.relative_to(skill_root)} 缺少 WebVPN 入口"


def test_cnki_documentation_declares_the_two_exact_new_search_urls(skill_root: Path) -> None:
    for relative_path in BUILD_INPUTS[:3]:
        content = (skill_root / relative_path).read_text(encoding="utf-8")
        assert DIRECT_NEW_SEARCH_URL in content, f"{relative_path.as_posix()} 缺少直接入口"
        assert HHU_NEW_SEARCH_URL in content, f"{relative_path.as_posix()} 缺少 WebVPN 入口"


def test_cnki_package_contains_only_new_search_entry(skill_root: Path) -> None:
    files = _scanned_files(skill_root)
    contents = {path: path.read_text(encoding="utf-8").casefold() for path in files}

    for token in FORBIDDEN_SEARCH_TOKENS:
        offenders = [path for path in files if token in contents[path]]
        assert not offenders, f"禁止标记 {token!r} 出现在: {_relative(skill_root, offenders)}"

    expected_urls = {DIRECT_NEW_SEARCH_URL.casefold(), HHU_NEW_SEARCH_URL.casefold()}
    observed_urls = {
        match.rstrip("`'\".,;:)")
        for content in contents.values()
        for match in re.findall(r"https?://[^\s`'\")]+", content)
        if "/kns" in match
    }
    unexpected_urls = sorted(observed_urls - expected_urls)
    assert not unexpected_urls, f"发现非新版检索入口: {', '.join(unexpected_urls)}"


def test_mcpb_cnki_python_copy_matches_main_source_file_by_file(skill_root: Path) -> None:
    main_root = skill_root / SOURCE_ROOTS[0]
    mcpb_root = skill_root / SOURCE_ROOTS[1]
    main_files = [path.relative_to(main_root) for path in _python_files(main_root)]
    mcpb_files = [path.relative_to(mcpb_root) for path in _python_files(mcpb_root)]
    assert main_files == mcpb_files, (
        "主源码与 MCPB 副本的 Python 文件集合不一致: "
        f"主源码={', '.join(path.as_posix() for path in main_files)}; "
        f"MCPB={', '.join(path.as_posix() for path in mcpb_files)}"
    )
    for relative_path in main_files:
        main_text = (main_root / relative_path).read_text(encoding="utf-8")
        mcpb_text = (mcpb_root / relative_path).read_text(encoding="utf-8")
        assert main_text == mcpb_text, f"Python 副本不一致: {relative_path.as_posix()}"
