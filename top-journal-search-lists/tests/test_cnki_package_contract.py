import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap


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


LAYOUTS = {
    "skill": Path("scripts"),
    "mcpb": Path("mcpb/src"),
}


def _run_layout_contract(layout_root: Path) -> dict[str, object]:
    program = textwrap.dedent(
        """
        import json

        from cnki_search.browser import BrowserFactory
        from cnki_search.models import SearchRequest
        from cnki_search.rate_limit import SerialSearchGate
        from cnki_search.session import CNKI_HOME_URL, PublicCnkiSession

        class Page:
            def __init__(self):
                self.url = ""
                self.wait_until = ""

            def goto(self, url, *, wait_until):
                self.url = url
                self.wait_until = wait_until
                return None

            def close(self):
                pass

        class Context:
            def __init__(self):
                self.page = Page()

            def new_page(self):
                return self.page

            def close(self):
                pass

        class Browser:
            def __init__(self):
                self.context_kwargs = None
                self.context = Context()

            def new_context(self, **kwargs):
                self.context_kwargs = kwargs
                return self.context

            def close(self):
                pass

        class SessionFactory:
            def __init__(self):
                self.browser = Browser()

            def launch_ephemeral(self):
                return self.browser

        class BrowserType:
            def __init__(self):
                self.kwargs = None

            def launch(self, **kwargs):
                self.kwargs = kwargs
                return object()

        class Playwright:
            def __init__(self):
                self.chromium = BrowserType()

        factory = SessionFactory()
        with PublicCnkiSession(browser_factory=factory):
            page = factory.browser.context.page
            session_state = {
                "home_url": CNKI_HOME_URL,
                "navigated_url": page.url,
                "wait_until": page.wait_until,
                "context_kwargs": factory.browser.context_kwargs,
            }

        invalid_limits = []
        interval_nan_rejected = False
        for limit in (0, 21):
            try:
                SearchRequest("topic", limit)
            except ValueError:
                invalid_limits.append(limit)
        try:
            SearchRequest("topic", float("nan"))
        except ValueError:
            interval_nan_rejected = True

        try:
            SerialSearchGate(minimum_interval=5.99)
        except ValueError:
            interval_floor_enforced = True
        else:
            interval_floor_enforced = False

        playwright = Playwright()
        BrowserFactory(playwright).launch_ephemeral()
        print(json.dumps({
            "session": session_state,
            "invalid_limits": invalid_limits,
            "interval_nan_rejected": interval_nan_rejected,
            "interval_floor_enforced": interval_floor_enforced,
            "launch_kwargs": playwright.chromium.kwargs,
        }))
        """
    )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(layout_root)
    result = subprocess.run(
        [sys.executable, "-c", program],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    return json.loads(result.stdout)


def test_skill_and_mcpb_layouts_independently_meet_public_runtime_contract(skill_root: Path) -> None:
    for layout_name, relative_root in LAYOUTS.items():
        state = _run_layout_contract(skill_root / relative_root)
        session = state["session"]
        assert session["home_url"] == "https://www.cnki.net/", layout_name
        assert session["navigated_url"] == "https://www.cnki.net/", layout_name
        assert session["wait_until"] == "domcontentloaded", layout_name
        assert session["context_kwargs"] == {"locale": "zh-CN", "accept_downloads": False}, layout_name
        assert state["invalid_limits"] == [0, 21], layout_name
        assert state["interval_nan_rejected"] is True, layout_name
        assert state["interval_floor_enforced"] is True, layout_name
        assert state["launch_kwargs"]["headless"] is True, layout_name
        assert state["launch_kwargs"]["args"] == ["--no-proxy-server"], layout_name
        assert "proxy" not in state["launch_kwargs"], layout_name


def test_skill_and_mcpb_layouts_exclude_legacy_login_and_download_modules(skill_root: Path) -> None:
    for layout_name, relative_root in LAYOUTS.items():
        names = {path.name for path in (skill_root / relative_root / "cnki_search").glob("*.py")}
        assert not names & LEGACY_MODULES, layout_name


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
