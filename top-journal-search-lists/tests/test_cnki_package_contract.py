from pathlib import Path
import re

import pytest


SOURCE_ROOTS = (Path("scripts/cnki_search"), Path("mcpb/src/cnki_search"))
TASK7 = "Task 7 将同步 MCPB 副本并重写公开检索发布合同；本迁移单元不得修改该副本或文档。"


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def test_cnki_runtime_contract(skill_root: Path) -> None:
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


@pytest.mark.xfail(reason=TASK7, strict=True)
def test_task7_documentation_contract(skill_root: Path) -> None:
    files = ("SKILL.md", "README.md", "references/cnki-search-reference.md")
    required = ("公开首页", "主题检索", "第一页", "不登录", "不下载", "不持久化 Cookie")
    for relative in files:
        content = (skill_root / relative).read_text(encoding="utf-8")
        for item in required:
            assert item in content, f"{relative} 缺少 {item}"


@pytest.mark.xfail(reason=TASK7, strict=True)
def test_task7_package_entry_and_copy_contract(skill_root: Path) -> None:
    main_root, mcpb_root = (skill_root / root for root in SOURCE_ROOTS)
    main_files = [path.relative_to(main_root) for path in _python_files(main_root)]
    mcpb_files = [path.relative_to(mcpb_root) for path in _python_files(mcpb_root)]
    assert main_files == mcpb_files
    for relative in main_files:
        assert (main_root / relative).read_bytes() == (mcpb_root / relative).read_bytes()
    for source in (*_python_files(main_root), *_python_files(mcpb_root)):
        content = source.read_text(encoding="utf-8").casefold()
        assert "advsearch" not in content
        assert "webvpn" not in content
        assert "fallback" not in content
        assert not re.search(r"https?://[^\s]+/kns", content)
