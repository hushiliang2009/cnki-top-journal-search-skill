import ast
import asyncio
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

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
    assert (skill_root / "scripts/cnki_search_env/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-env-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


def test_package_exposes_public_home_and_no_legacy_capabilities(skill_root: Path) -> None:
    code_files = [
        *(skill_root / "scripts/cnki_search_env").glob("*.py"),
        *(skill_root / "mcpb/src/cnki_search_env").glob("*.py"),
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
    bundled_names = {path.name for path in (skill_root / "mcpb/src/cnki_search_env").glob("*.py")}
    assert not bundled_names & LEGACY_MODULES


def _run_layout_contract(layout_root: Path) -> dict[str, object]:
    program = textwrap.dedent(
        """
        import json
        from pathlib import Path

        import catalog_lookup
        from cnki_search_env.models import SearchRequest
        from cnki_search_env.session import CNKI_HOME_URL

        invalid_limits = []
        for limit in (0, 21):
            try:
                SearchRequest("topic", limit)
            except ValueError:
                invalid_limits.append(limit)
        request = SearchRequest("  topic   phrase  ", 1)
        print(json.dumps({
            "home_url": CNKI_HOME_URL,
            "normalized_query": request.query,
            "invalid_limits": invalid_limits,
            "catalog_exists": Path(catalog_lookup.DEFAULT_CATALOG).is_file(),
        }))
        """
    )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(layout_root)
    result = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_skill_and_mcpb_layouts_independently_meet_runtime_contract(skill_root: Path) -> None:
    for layout_name, layout_root in {
        "skill": skill_root / "scripts",
        "mcpb": skill_root / "mcpb/src",
    }.items():
        state = _run_layout_contract(layout_root)
        assert state["home_url"] == "https://www.cnki.net/", layout_name
        assert state["normalized_query"] == "topic phrase", layout_name
        assert state["invalid_limits"] == [0, 21], layout_name
        assert state["catalog_exists"] is True, layout_name


def test_helper_scripts_reference_only_existing_runtime_symbols(skill_root: Path) -> None:
    """辅助脚本不随契约测试执行，需显式校验其引用的运行时符号仍然存在。"""
    helpers = sorted((skill_root / "tests").glob("_*.py"))
    assert helpers, "tests/ 下应至少保留一个辅助脚本"
    for helper in helpers:
        tree = ast.parse(helper.read_text(encoding="utf-8"), filename=str(helper))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level:
                continue
            if node.module is None or not node.module.startswith("cnki_search_env"):
                continue
            module = importlib.import_module(node.module)
            for alias in node.names:
                assert hasattr(module, alias.name), (
                    f"{helper.name} 引用了 {node.module}.{alias.name}，该符号已不存在"
                )


def _load_helper_module(skill_root: Path, name: str) -> Any:
    path = skill_root / "tests" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # 先登记再执行：dataclass 解析注解时会回查 sys.modules[cls.__module__]。
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


_SMOKE_RESULT_HTML = """
<table class="result-table-list"><tbody>
  <tr>
    <td class="name"><a>供应链持股与会计信息质量</a></td>
    <td class="author"><a>张三</a><a>李四</a></td>
    <td class="source"><a>经济研究</a></td>
    <td class="date">2024-05-20 14:35:12</td>
    <td class="data">期刊</td>
  </tr>
</tbody></table>
"""


def test_live_smoke_speaks_the_current_async_session_protocol(skill_root: Path) -> None:
    """离线注入假会话端到端跑通实机冒烟脚本。

    该脚本不进 CI（会对知网发真实请求），符号存在性检查也测不出同步/异步
    协议漂移——运行时迁到异步后它曾整体失效而无人察觉。这里以注入方式覆盖。
    """
    if not (skill_root / "tests/_public_cnki_live_smoke.py").is_file():
        pytest.skip("发布包不含实机冒烟脚本，本守卫仅在仓库检出下生效")
    smoke = _load_helper_module(skill_root, "_public_cnki_live_smoke")
    from cnki_search_env.session import SearchSnapshot

    class FakeSession:
        entered = exited = False

        async def __aenter__(self) -> "FakeSession":
            type(self).entered = True
            return self

        async def search(self, query: str) -> SearchSnapshot:
            return SearchSnapshot(
                html=_SMOKE_RESULT_HTML,
                url="https://kns.cnki.net/kns8s/defaultresult/index",
                title="中国知网",
                visible_text="题名 作者 来源 供应链持股与会计信息质量",
                http_status=200,
            )

        async def __aexit__(self, *_exc: object) -> None:
            type(self).exited = True

    result = asyncio.run(smoke.run_smoke("供应链持股", 20, session_factory=FakeSession))

    assert FakeSession.entered and FakeSession.exited, "包装会话未走完异步上下文协议"
    assert result.exit_code == 0, result.message
    assert result.summary == {
        "status": "success",
        "record_count": 1,
        "final_domain": "kns.cnki.net",
    }
    assert result.payload["records"][0]["journal_raw"] == "经济研究"
    assert result.payload["records"][0]["publication_year"] == 2024

    # 证据已过脱敏守卫（否则 run_smoke 内就抛了）；这里正向确认守卫会拦下嵌套的敏感键。
    with pytest.raises(ValueError, match="敏感字段"):
        smoke._assert_no_sensitive_fields({"records": [{"detail_url": "https://example.invalid"}]})


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
    files = ("SKILL.md", "README.md", "references/cnki-search-env-reference.md")
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
    for relative in ("SKILL.md", "README.md", "references/cnki-search-env-reference.md"):
        assert expected in (skill_root / relative).read_text(encoding="utf-8")
