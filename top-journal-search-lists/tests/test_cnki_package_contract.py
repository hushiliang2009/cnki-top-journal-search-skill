import ast
import importlib
import subprocess
import sys
from pathlib import Path

import pytest


LEGACY_MODULES = {
    "cli.py",
    "details.py",
    "downloads.py",
    "exporters.py",
    "fields.py",
    "syntax.py",
}


def test_cnki_runtime_contract(skill_root: Path) -> None:
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


def test_package_exposes_public_home_and_no_legacy_capabilities(skill_root: Path) -> None:
    code_files = [
        *(skill_root / "scripts/cnki_search").glob("*.py"),
        *(skill_root / "mcpb/src/cnki_search").glob("*.py"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").casefold() for path in code_files)
    assert "https://www.cnki.net/" in combined
    for token in (
        "webvpn",
        "advsearch",
        "brief/grid",
        "senquery",
        "access_confirmed",
        "detail_url",
        "download_url",
    ):
        assert token not in combined
    bundled_names = {path.name for path in (skill_root / "mcpb/src/cnki_search").glob("*.py")}
    assert not bundled_names & LEGACY_MODULES


def test_main_and_mcpb_sources_and_catalog_are_identical(skill_root: Path) -> None:
    main = skill_root / "scripts/cnki_search"
    bundled = skill_root / "mcpb/src/cnki_search"
    assert [path.name for path in sorted(main.glob("*.py"))] == [
        path.name for path in sorted(bundled.glob("*.py"))
    ]
    for source in main.glob("*.py"):
        assert source.read_bytes() == (bundled / source.name).read_bytes()
    assert (skill_root / "scripts/catalog_lookup.py").read_bytes() == (
        skill_root / "mcpb/src/catalog_lookup.py"
    ).read_bytes()
    assert (skill_root / "references/Academic_Journal_Master_Directory_20260715.md").read_bytes() == (
        skill_root / "mcpb/src/references/Academic_Journal_Master_Directory_20260715.md"
    ).read_bytes()


def test_helper_scripts_reference_only_existing_runtime_symbols(skill_root: Path) -> None:
    """辅助脚本不随契约测试执行，需显式校验其引用的运行时符号仍然存在。"""
    helpers = sorted((skill_root / "tests").glob("_*.py"))
    assert helpers, "tests/ 下应至少保留一个辅助脚本"
    for helper in helpers:
        tree = ast.parse(helper.read_text(encoding="utf-8"), filename=str(helper))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level:
                continue
            if node.module is None or not node.module.startswith("cnki_search"):
                continue
            module = importlib.import_module(node.module)
            for alias in node.names:
                assert hasattr(module, alias.name), (
                    f"{helper.name} 引用了 {node.module}.{alias.name}，该符号已不存在"
                )


@pytest.mark.parametrize(
    ("package_dir", "module_dir"),
    [("", "scripts"), ("mcpb", "src")],
    ids=["skill_layout", "mcpb_layout"],
)
def test_catalog_resolves_under_both_distribution_layouts(
    skill_root: Path, package_dir: str, module_dir: str,
) -> None:
    """Skill 与 MCPB 两种布局的目录深度差一层，固定深度推导会有一种失败。

    必须走子进程：conftest.py 把 sys.path 钉死在 scripts/，同进程测不到 MCPB 布局。
    """
    working_dir = skill_root / package_dir if package_dir else skill_root
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, {module_dir!r});"
            " import catalog_lookup as C;"
            " print(C.DEFAULT_CATALOG.is_file()); print(C.DEFAULT_CATALOG)",
        ],
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    found, resolved = completed.stdout.splitlines()[:2]
    assert found == "True", f"{module_dir} 布局下未能定位综合期刊目录：{resolved}"
    assert Path(resolved).is_file()


def test_skill_uses_ai4scholar_as_primary_and_cnki_as_supplement(skill_root: Path) -> None:
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    for required in ("ai4scholar", "主要来源", "中文论文", "补充", "sources", "篇名", "期刊", "发表年度"):
        assert required in text


def test_public_documentation_contract(skill_root: Path) -> None:
    files = ("SKILL.md", "README.md", "references/cnki-search-reference.md")
    required = ("公开首页", "主题检索", "第一页", "不登录", "不下载", "不持久化 Cookie")
    forbidden = ("WebVPN", "高级检索", "专业检索", "cnki_login", "cnki_fetch_details", "cnki_download")
    for relative in files:
        content = (skill_root / relative).read_text(encoding="utf-8")
        for item in required:
            assert item in content, f"{relative} 缺少 {item}"
        for item in forbidden:
            assert item not in content, f"{relative} 包含旧能力 {item}"


def test_documentation_describes_only_ephemeral_memory_cache(skill_root: Path) -> None:
    expected = "不持久化缓存，运行期仅24小时内存缓存"
    for relative in ("SKILL.md", "README.md", "references/cnki-search-reference.md"):
        assert expected in (skill_root / relative).read_text(encoding="utf-8")
