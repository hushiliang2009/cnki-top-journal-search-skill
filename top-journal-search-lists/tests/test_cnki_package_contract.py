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
    assert (skill_root / "scripts/cnki_search/__init__.py").is_file()
    assert (skill_root / "references/cnki-search-reference.md").is_file()
    assert "CNKI" in (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "中国知网" in (skill_root / "README.md").read_text(encoding="utf-8")


#: 人工值守的 WebVPN 模式独占的模块。公开匿名模式的边界对它们不适用，
#: 但它们各自的边界由 test_webvpn_modules_are_isolated_and_self_documented 单独把守。
WEBVPN_MODULES = {
    "webvpn.py",
    "professional.py",
    "professional_runtime.py",
    "professional_service.py",
}


#: 两种模式共用的注册入口。它必须能命名 WebVPN 模式（工具描述、启用用的环境
#: 变量），但旧能力令牌对它同样禁止。
SHARED_ENTRY_MODULES = {"mcp_server.py"}


def _public_mode_sources(skill_root: Path) -> list[Path]:
    return [
        path
        for directory in ("scripts/cnki_search", "mcpb/src/cnki_search")
        for path in (skill_root / directory).glob("*.py")
        if path.name not in WEBVPN_MODULES | SHARED_ENTRY_MODULES
    ]


def test_package_exposes_public_home_and_no_legacy_capabilities(skill_root: Path) -> None:
    """公开匿名模式的边界不因新增 WebVPN 模式而放松。

    这些令牌当初是随登录/下载/高级检索能力一并移除的，此处防回退。
    WebVPN 模式的代码集中在 WEBVPN_MODULES，不得渗回公开模式的模块。
    """
    combined = "\n".join(
        path.read_text(encoding="utf-8").casefold() for path in _public_mode_sources(skill_root)
    )
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
        assert token not in combined, f"公开匿名模式的模块不得引入 {token}"
    bundled_names = {path.name for path in (skill_root / "mcpb/src/cnki_search").glob("*.py")}
    assert not bundled_names & LEGACY_MODULES


def test_release_manifest_covers_every_runtime_module(skill_root: Path) -> None:
    """新增模块必须同时登记进发布清单。

    漏登记时源码树里一切正常、测试全绿，只有安装到目标机器后才会
    ModuleNotFoundError——本守卫把这个反馈提前到本地。
    """
    import build_release

    source_modules = {path.name for path in (skill_root / "scripts/cnki_search").glob("*.py")}
    missing = source_modules - set(build_release.CNKI_MODULES)
    assert not missing, f"以下模块未登记进 build_release.CNKI_MODULES：{sorted(missing)}"
    stale = set(build_release.CNKI_MODULES) - source_modules
    assert not stale, f"发布清单登记了不存在的模块：{sorted(stale)}"


#: 只在仓库检出下有意义、不随发布包分发的测试。
#: test_release_baseline.py 校验仓库根的 .gitignore 与 CI 工作流，发布包里没有这些文件。
REPO_ONLY_TESTS = {"tests/test_release_baseline.py"}


def test_release_manifest_covers_every_test_module(skill_root: Path) -> None:
    """测试文件同理：漏登记会让发布包的自检覆盖面悄悄缩水。"""
    import build_release

    source_tests = {f"tests/{path.name}" for path in (skill_root / "tests").glob("test_*.py")}
    missing = source_tests - set(build_release.TEST_ALLOWLIST) - REPO_ONLY_TESTS
    assert not missing, f"以下测试未登记进 build_release.TEST_ALLOWLIST：{sorted(missing)}"


def test_shared_entry_may_name_webvpn_but_not_revive_legacy_capabilities(
    skill_root: Path,
) -> None:
    """注册入口可以命名 WebVPN 模式，但旧能力令牌对它同样禁止。"""
    for directory in ("scripts/cnki_search", "mcpb/src/cnki_search"):
        for name in SHARED_ENTRY_MODULES:
            content = (skill_root / directory / name).read_text(encoding="utf-8").casefold()
            for token in ("advsearch", "brief/grid", "senquery",
                          "access_confirmed", "detail_url", "download_url"):
                assert token not in content, f"{directory}/{name} 不得引入 {token}"


def test_webvpn_modules_are_isolated_and_self_documented(skill_root: Path) -> None:
    """WebVPN 模式必须在代码里写明它不可无人值守，且不得夹带检测规避手段。"""
    for directory in ("scripts/cnki_search", "mcpb/src/cnki_search"):
        module = (skill_root / directory / "webvpn.py").read_text(encoding="utf-8")
        for statement in ("人工", "值守", "不得自动破解"):
            assert statement in module, f"{directory}/webvpn.py 缺少人工值守声明：{statement}"
        # 绕过风控的手段一律禁止，这条底线不随模式改变。只查实际用法，
        # 说明文字里提到这些概念（例如解释"与 User-Agent 无关"）不算违规。
        for forbidden in ("user_agent=", "--proxy-server", "--user-agent",
                          "stealth", "navigator.webdriver"):
            assert forbidden not in module.casefold(), f"webvpn.py 不得使用检测规避手段 {forbidden}"
        # 票据跨进程无效，落盘只会平白多一处凭据泄露面。同样只禁实际调用。
        for forbidden in ("launch_persistent_context", "storage_state=", ".storage_state("):
            assert forbidden not in module, f"webvpn.py 不得持久化登录票据（{forbidden}）"


def _run_layout_contract(layout_root: Path) -> dict[str, object]:
    program = textwrap.dedent(
        """
        import json
        from pathlib import Path

        import catalog_lookup
        from cnki_search.mcp_server import CnkiMcpServer
        from cnki_search.models import SearchRequest
        from cnki_search.professional_runtime import build_professional_runtime_from_env
        from cnki_search.session import CNKI_HOME_URL
        from mcp.server.fastmcp import FastMCP

        invalid_limits = []
        for limit in (0, 51):
            try:
                SearchRequest("topic", limit)
            except ValueError:
                invalid_limits.append(limit)
        request = SearchRequest("  topic   phrase  ", 1)
        mcp = CnkiMcpServer().build_fastmcp(FastMCP)
        schemas = {
            tool.name: tool.parameters
            for tool in mcp._tool_manager.list_tools()
        }
        print(json.dumps({
            "home_url": CNKI_HOME_URL,
            "normalized_query": request.query,
            "invalid_limits": invalid_limits,
            "catalog_exists": Path(catalog_lookup.DEFAULT_CATALOG).is_file(),
            "professional_runtime_callable": callable(build_professional_runtime_from_env),
            "schemas": schemas,
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
    states = {}
    for layout_name, layout_root in {
        "skill": skill_root / "scripts",
        "mcpb": skill_root / "mcpb/src",
    }.items():
        state = _run_layout_contract(layout_root)
        states[layout_name] = state
        assert state["home_url"] == "https://www.cnki.net/", layout_name
        assert state["normalized_query"] == "topic phrase", layout_name
        assert state["invalid_limits"] == [0, 51], layout_name
        assert state["catalog_exists"] is True, layout_name
        assert state["professional_runtime_callable"] is True, layout_name
        assert set(state["schemas"]) == {"cnki_search", "cnki_professional_search"}
        professional = state["schemas"]["cnki_professional_search"]["properties"]
        assert professional["group"]["default"] == "chinese_top_journals", layout_name
        assert professional["limit"]["maximum"] == 50, layout_name
    assert states["skill"]["schemas"] == states["mcpb"]["schemas"]


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


def test_webvpn_probe_uses_current_ephemeral_config_contract(
    skill_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    probe = _load_helper_module(skill_root, "_webvpn_probe")
    captured: list[Any] = []

    async def fake_run_probe(config: Any, *, submit_topic: str | None = None) -> Any:
        captured.append((config, submit_topic))
        return probe.ProbeResult(0, {}, {"contract_ok": True})

    monkeypatch.setattr(probe, "run_probe", fake_run_probe)
    output = tmp_path / "webvpn-probe.json"

    exit_code = probe.main([
        "--home", "https://webvpn.example.edu.cn/https/abc/",
        "--output", str(output),
    ])

    assert exit_code == 0
    assert captured == [(
        probe.WebVpnConfig("https://webvpn.example.edu.cn/https/abc/"),
        None,
    )]
    assert output.is_file()


def test_webvpn_e2e_helper_prints_only_the_sanitized_summary(
    skill_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    helper = _load_helper_module(skill_root, "_webvpn_e2e")
    calls: list[tuple[object, ...]] = []

    class Runtime:
        closed = False

        async def search_group(
            self, topic: str, group: str, *, limit: int,
            year_from: int | None, year_to: int | None,
        ) -> dict[str, object]:
            calls.append((topic, group, limit, year_from, year_to))
            return {
                "status": "success",
                "batches_completed": 1,
                "batches_total": 1,
                "records": [{
                    "title": "数字化转型与企业创新",
                    "journal_raw": "管理世界",
                    "publication_year": 2025,
                    "priority_level": 6,
                    "authors": ["张三", "李四"],
                    "unknown_safe_field": "must-not-be-emitted",
                }],
            }

        async def aclose(self) -> None:
            self.closed = True

    runtime = Runtime()

    async def build_runtime() -> Runtime:
        return runtime

    monkeypatch.setenv(
        "CNKI_WEBVPN_HOME", "https://webvpn.example.edu.cn/https/abc/"
    )
    monkeypatch.setattr(
        helper, "build_professional_runtime_from_env", build_runtime
    )

    exit_code = helper.main([
        "--topic", "数字化转型",
        "--group", "chinese_top_journals",
        "--limit", "5",
        "--year-from", "2020",
        "--year-to", "2025",
    ])

    assert exit_code == 0
    assert calls == [
        ("数字化转型", "chinese_top_journals", 5, 2020, 2025)
    ]
    assert runtime.closed is True
    assert json.loads(capsys.readouterr().out) == {
        "status": "success",
        "group": "chinese_top_journals",
        "record_count": 1,
        "batches_completed": 1,
        "batches_total": 1,
        "sample": [{
            "title": "数字化转型与企业创新",
            "journal_raw": "管理世界",
            "publication_year": 2025,
            "priority_level": 6,
            "authors": ["张三", "李四"],
        }],
    }


def _install_e2e_runtime(
    helper: Any,
    monkeypatch: pytest.MonkeyPatch,
    *,
    result: object = None,
    error: BaseException | None = None,
) -> Any:
    class Runtime:
        closed = False

        async def search_group(self, *_args: object, **_kwargs: object) -> object:
            if error is not None:
                raise error
            return result

        async def aclose(self) -> None:
            self.closed = True

    runtime = Runtime()

    async def build_runtime() -> Runtime:
        return runtime

    monkeypatch.setattr(
        helper, "build_professional_runtime_from_env", build_runtime
    )
    return runtime


@pytest.mark.parametrize(
    "unsafe_key",
    [
        "storageState-KEYSECRET",
        "storage-state-KEYSECRET",
        "storage_state_KEYSECRET",
        "ＳＴＯＲＡＧＥ＿ＳＴＡＴＥ＿ＫＥＹＳＥＣＲＥＴ",
        "cookieKEYSECRET",
        "token-KEYSECRET",
        "profile_KEYSECRET",
        "browser.context.KEYSECRET",
        "local-path-KEYSECRET",
    ],
)
def test_webvpn_e2e_helper_normalizes_sensitive_keys_without_echoing_them(
    skill_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    unsafe_key: str,
) -> None:
    helper = _load_helper_module(skill_root, "_webvpn_e2e")
    runtime = _install_e2e_runtime(
        helper,
        monkeypatch,
        result={
            "status": "success",
            "batches_completed": 1,
            "batches_total": 1,
            "records": [{"title": "题名", unsafe_key: "VALUESECRET"}],
        },
    )

    exit_code = helper.main([
        "--topic", "数字化转型",
        "--group", "chinese_top_journals",
        "--limit", "5",
    ])

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert exit_code != 0
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "status": "error",
        "error": "webvpn_e2e_failed",
    }
    assert runtime.closed is True
    for secret in (unsafe_key, "KEYSECRET", "VALUESECRET"):
        assert secret not in combined


@pytest.mark.parametrize(
    "unsafe_value",
    [
        Path(r"C:\Users\person\Cookie"),
        b"BYTESECRET",
        object(),
    ],
)
def test_webvpn_e2e_helper_rejects_non_json_values_with_fixed_error(
    skill_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    unsafe_value: object,
) -> None:
    helper = _load_helper_module(skill_root, "_webvpn_e2e")
    runtime = _install_e2e_runtime(
        helper,
        monkeypatch,
        result={
            "status": "success",
            "batches_completed": 1,
            "batches_total": 1,
            "records": [],
            "unknown": unsafe_value,
        },
    )

    exit_code = helper.main([
        "--topic", "数字化转型",
        "--group", "chinese_top_journals",
    ])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "status": "error",
        "error": "webvpn_e2e_failed",
    }
    assert runtime.closed is True


@pytest.mark.parametrize(
    "malformed_result",
    [
        {
            "status": {"nested": "STATUSSECRET"},
            "batches_completed": 1,
            "batches_total": 1,
            "records": [],
        },
        {
            "status": "success",
            "batches_completed": ["COUNTSECRET"],
            "batches_total": 1,
            "records": [],
        },
        {
            "status": "success",
            "batches_completed": 1,
            "batches_total": 1,
            "records": [{
                "title": {"nested": "TITLESECRET"},
                "journal_raw": "管理世界",
                "publication_year": 2025,
                "priority_level": 6,
            }],
        },
        {
            "status": "success",
            "batches_completed": 1,
            "batches_total": 1,
            "records": [{
                "title": "题名",
                "journal_raw": "管理世界",
                "publication_year": 2025,
                "priority_level": 6,
                "authors": ["张三", {"nested": "AUTHORSECRET"}],
            }],
        },
    ],
)
def test_webvpn_e2e_helper_rejects_nested_summary_scalars_and_invalid_authors(
    skill_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    malformed_result: dict[str, object],
) -> None:
    helper = _load_helper_module(skill_root, "_webvpn_e2e")
    runtime = _install_e2e_runtime(
        helper, monkeypatch, result=malformed_result
    )

    exit_code = helper.main([
        "--topic", "数字化转型",
        "--group", "chinese_top_journals",
    ])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "status": "error",
        "error": "webvpn_e2e_failed",
    }
    assert runtime.closed is True
    for secret in (
        "STATUSSECRET", "COUNTSECRET", "TITLESECRET", "AUTHORSECRET"
    ):
        assert secret not in captured.err


@pytest.mark.parametrize(
    "error",
    [
        RuntimeError(r"RUNTIMESECRET C:\Users\person\Cookie"),
        asyncio.CancelledError("CANCELSECRET"),
        KeyboardInterrupt("KEYBOARDSECRET"),
        SystemExit(0),
    ],
)
def test_webvpn_e2e_cli_returns_fixed_error_and_closes_runtime_on_base_exceptions(
    skill_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: BaseException,
) -> None:
    helper = _load_helper_module(skill_root, "_webvpn_e2e")
    runtime = _install_e2e_runtime(
        helper, monkeypatch, error=error
    )

    exit_code = helper.main([
        "--topic", "数字化转型",
        "--group", "chinese_top_journals",
    ])

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert exit_code != 0
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "status": "error",
        "error": "webvpn_e2e_failed",
    }
    assert runtime.closed is True
    for secret in (
        "RUNTIMESECRET", "CANCELSECRET", "KEYBOARDSECRET",
        r"C:\Users\person\Cookie", "Traceback",
    ):
        assert secret not in combined


def test_webvpn_e2e_subprocess_missing_home_has_only_fixed_safe_error(
    skill_root: Path,
    tmp_path: Path,
) -> None:
    helper = skill_root / "tests" / "_webvpn_e2e.py"
    environment = dict(os.environ)
    environment.pop("CNKI_WEBVPN_HOME", None)
    environment["HOME"] = str(tmp_path / "isolated-home")
    environment["USERPROFILE"] = str(tmp_path / "isolated-home")

    completed = subprocess.run(
        [
            sys.executable,
            str(helper),
            "--topic",
            "数字化转型",
            "--group",
            "chinese_top_journals",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        check=False,
    )

    combined = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert completed.stdout == ""
    assert json.loads(completed.stderr) == {
        "status": "error",
        "error": "webvpn_e2e_failed",
    }
    for forbidden in (
        "Traceback",
        str(skill_root),
        str(Path(sys.executable)),
        "CNKI_WEBVPN_HOME",
    ):
        assert forbidden not in combined


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
    from cnki_search.session import SearchSnapshot

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


DOCUMENTATION_FILES = ("SKILL.md", "README.md", "references/cnki-search-reference.md")


def test_public_documentation_contract(skill_root: Path) -> None:
    """公开匿名模式的边界必须在每份文档里写明，且旧能力一律不得复活。

    WebVPN 人工值守模式是并列的第二种模式，不放松这里的任何一条——它的额外
    约束由 test_webvpn_documentation_states_its_constraints 单独把守。
    """
    required = ("公开首页", "主题检索", "第一页", "不登录", "不下载", "不持久化 Cookie")
    forbidden = ("cnki_login", "cnki_fetch_details", "cnki_download")
    for relative in DOCUMENTATION_FILES:
        content = (skill_root / relative).read_text(encoding="utf-8")
        for item in required:
            assert item in content, f"{relative} 缺少 {item}"
        for item in forbidden:
            assert item not in content, f"{relative} 包含旧能力 {item}"


def test_webvpn_documentation_states_its_constraints(skill_root: Path) -> None:
    """凡是提到 WebVPN 或专业检索的文档，必须同时写明它不可无人值守。

    否则读者会把它当成和公开检索一样可以随手调用的能力，进而安排定时任务，
    而该模式在无人时必然失败（登录与验证码都需要人）。
    """
    for relative in DOCUMENTATION_FILES:
        content = (skill_root / relative).read_text(encoding="utf-8")
        if "WebVPN" not in content and "专业检索" not in content:
            continue
        for statement in ("人工值守", "不可用于定时任务", "机构授权"):
            assert statement in content, f"{relative} 提到 WebVPN/专业检索但缺少：{statement}"
        # 底线不随模式改变：机构合法认证 ≠ 检测规避
        for statement in ("不伪造", "不轮换代理", "不自动破解"):
            assert statement in content, f"{relative} 缺少检测规避禁令：{statement}"


def test_webvpn_documentation_matches_the_ephemeral_runtime_contract(
    skill_root: Path,
) -> None:
    required = (
        "CNKI_WEBVPN_HOME",
        "CNKI_WEBVPN_PROFILE",
        "非持久化",
        "服务重启后需要重新登录",
        "13 本",
        "精确",
        "来源类别",
        "no_data_retry_later",
        "不等于空结果",
        "ai4scholar",
        "不登录",
        "不下载",
        "人工值守",
        "不可用于定时任务",
    )
    for relative in DOCUMENTATION_FILES:
        content = (skill_root / relative).read_text(encoding="utf-8")
        for statement in required:
            assert statement in content, f"{relative} 缺少运行时约束：{statement}"


def test_documentation_describes_only_ephemeral_memory_cache(skill_root: Path) -> None:
    expected = "不持久化缓存，运行期仅24小时内存缓存"
    for relative in ("SKILL.md", "README.md", "references/cnki-search-reference.md"):
        assert expected in (skill_root / relative).read_text(encoding="utf-8")
