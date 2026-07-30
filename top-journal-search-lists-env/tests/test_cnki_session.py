import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest

import cnki_search_env.browser as browser_module
import cnki_search_env.session as session_module
from cnki_search_env.browser import BrowserFactory
from cnki_search_env.models import SearchStatus
from cnki_search_env.session import PublicCnkiSession


ROOT = Path(__file__).resolve().parents[1]


def test_public_session_uses_only_cnki_home() -> None:
    assert session_module.CNKI_HOME_URL == "https://www.cnki.net/"
    source = Path(session_module.__file__).read_text(encoding="utf-8").casefold()
    assert "webvpn" not in source
    assert "advsearch" not in source
    assert "brief/grid" not in source


@pytest.mark.parametrize(
    ("url", "text", "expected"),
    [
        ("https://kns.cnki.net/captcha", "请完成拼图验证", SearchStatus.CHALLENGE_DETECTED),
        ("https://login.cnki.net/", "用户登录", SearchStatus.LOGIN_REQUIRED),
        ("https://kns.cnki.net/kns8s/authserver/login", "普通认证页", SearchStatus.LOGIN_REQUIRED),
        ("https://kns.cnki.net/", "403 Forbidden", SearchStatus.FORBIDDEN),
        ("https://kns.cnki.net/", "访问过于频繁", SearchStatus.RATE_LIMITED),
        ("https://kns.cnki.net/", "未检索到相关文献", SearchStatus.NO_RESULTS),
    ],
)
def test_restrictions_stop_without_fallback(url: str, text: str, expected: SearchStatus) -> None:
    assert session_module.classify_public_search_state(url=url, title="", visible_text=text) is expected


class FakeBrowserType:
    def __init__(self) -> None:
        self.launch_kwargs: dict[str, object] = {}

    def launch(self, **kwargs: object) -> object:
        self.launch_kwargs = kwargs
        return object()


class FakePlaywright:
    def __init__(self) -> None:
        self.chromium = FakeBrowserType()


def test_browser_launch_is_headless_and_has_no_persistent_state() -> None:
    fake = FakePlaywright()
    asyncio.run(BrowserFactory(fake).launch_ephemeral())
    assert fake.chromium.launch_kwargs["headless"] is True
    assert fake.chromium.launch_kwargs["args"] == ["--no-proxy-server", "--proxy-bypass-list=*"]
    assert "user_data_dir" not in fake.chromium.launch_kwargs
    assert "storage_state" not in fake.chromium.launch_kwargs
    assert "proxy" not in fake.chromium.launch_kwargs


def test_environment_browser_path_does_not_reuse_generic_skill_setting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    generic_browser = tmp_path / "generic-browser"
    environment_browser = tmp_path / "environment-browser"
    generic_browser.touch()
    environment_browser.touch()
    monkeypatch.setenv("CNKI_BROWSER_PATH", str(generic_browser))
    monkeypatch.setenv("CNKI_ENV_BROWSER_PATH", str(environment_browser))

    assert browser_module.discover_browser_executable() == str(environment_browser)


def test_default_playwright_cache_is_private_to_current_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    runtime_prefix = tmp_path / "mcpb" / ".venv"
    monkeypatch.delenv("PLAYWRIGHT_BROWSERS_PATH", raising=False)
    monkeypatch.setattr(browser_module.sys, "prefix", str(runtime_prefix))

    configured = browser_module.configure_playwright_browsers_path()

    assert configured == runtime_prefix / "playwright-browsers"
    assert os.environ["PLAYWRIGHT_BROWSERS_PATH"] == str(configured)


def test_missing_browser_triggers_one_local_runtime_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    bundled_browser = tmp_path / "playwright" / "chromium"
    fake = FakePlaywright()
    fake.chromium.executable_path = str(bundled_browser)
    install_calls = 0

    async def install_browser() -> None:
        nonlocal install_calls
        install_calls += 1
        bundled_browser.parent.mkdir(parents=True)
        bundled_browser.touch()

    monkeypatch.setattr(browser_module, "discover_browser_executable", lambda: None)
    asyncio.run(
        BrowserFactory(fake, browser_installer=install_browser).launch_ephemeral()
    )

    assert install_calls == 1


def test_existing_playwright_browser_skips_local_runtime_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    bundled_browser = tmp_path / "playwright" / "chromium"
    bundled_browser.parent.mkdir(parents=True)
    bundled_browser.touch()
    fake = FakePlaywright()
    fake.chromium.executable_path = str(bundled_browser)

    async def unexpected_install() -> None:
        raise AssertionError("existing browser must not be reinstalled")

    monkeypatch.setattr(browser_module, "discover_browser_executable", lambda: None)
    asyncio.run(
        BrowserFactory(fake, browser_installer=unexpected_install).launch_ephemeral()
    )


def test_playwright_runtime_installer_uses_current_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: tuple[object, ...] = ()
    captured_options: dict[str, object] = {}

    class Process:
        returncode = 0

        async def communicate(self) -> tuple[bytes, bytes]:
            return b"", b""

    async def create_process(*args: object, **kwargs: object) -> Process:
        nonlocal captured, captured_options
        captured = args
        captured_options = kwargs
        return Process()

    monkeypatch.setattr(
        browser_module.asyncio, "create_subprocess_exec", create_process,
    )
    asyncio.run(browser_module._install_playwright_browser_runtime())

    assert captured == (
        sys.executable,
        "-m",
        "playwright",
        "install",
        "chromium",
        "chromium-headless-shell",
    )
    if os.name == "nt":
        assert captured_options["creationflags"] == browser_module.subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        assert captured_options["start_new_session"] is True


def test_cancelled_browser_install_terminates_child_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started = asyncio.Event()

    class Process:
        returncode: int | None = None
        terminated = False
        pid = 424242

        async def communicate(self) -> tuple[bytes, bytes]:
            started.set()
            await asyncio.Event().wait()
            return b"", b""

        def terminate(self) -> None:
            self.terminated = True
            self.returncode = 1

        async def wait(self) -> int:
            return self.returncode or 0

    process = Process()
    tree_kill_args: tuple[object, ...] = ()
    process_group_signals: list[tuple[int, int]] = []

    class TreeKiller:
        async def communicate(self) -> tuple[bytes, bytes]:
            return b"", b""

    async def create_process(*args: object, **_kwargs: object) -> Process | TreeKiller:
        nonlocal tree_kill_args
        if args and args[0] == "taskkill.exe":
            tree_kill_args = args
            return TreeKiller()
        return process

    async def scenario() -> None:
        monkeypatch.setattr(
            browser_module.asyncio, "create_subprocess_exec", create_process,
        )
        monkeypatch.setattr(
            browser_module.os,
            "killpg",
            lambda pid, sig: process_group_signals.append((pid, sig)),
            raising=False,
        )
        task = asyncio.create_task(
            browser_module._install_playwright_browser_runtime(),
        )
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    if os.name == "nt":
        assert tree_kill_args == (
            "taskkill.exe", "/PID", str(process.pid), "/T", "/F",
        )
    else:
        assert process_group_signals == [(process.pid, browser_module.signal.SIGTERM)]


def test_timed_out_browser_install_terminates_child_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Process:
        returncode: int | None = None
        terminated = False
        pid = 424242

        async def communicate(self) -> tuple[bytes, bytes]:
            await asyncio.Event().wait()
            return b"", b""

        def terminate(self) -> None:
            self.terminated = True
            self.returncode = 1

        async def wait(self) -> int:
            return self.returncode or 0

    process = Process()
    tree_kill_args: tuple[object, ...] = ()
    process_group_signals: list[tuple[int, int]] = []

    class TreeKiller:
        async def communicate(self) -> tuple[bytes, bytes]:
            return b"", b""

    async def create_process(*args: object, **_kwargs: object) -> Process | TreeKiller:
        nonlocal tree_kill_args
        if args and args[0] == "taskkill.exe":
            tree_kill_args = args
            return TreeKiller()
        return process

    monkeypatch.setattr(
        browser_module.asyncio, "create_subprocess_exec", create_process,
    )
    monkeypatch.setattr(
        browser_module.os,
        "killpg",
        lambda pid, sig: process_group_signals.append((pid, sig)),
        raising=False,
    )
    with pytest.raises(browser_module.BrowserUnavailableError):
        asyncio.run(
            browser_module._install_playwright_browser_runtime(
                timeout_seconds=0.01,
            )
        )

    if os.name == "nt":
        assert tree_kill_args == (
            "taskkill.exe", "/PID", str(process.pid), "/T", "/F",
        )
    else:
        assert process_group_signals == [(process.pid, browser_module.signal.SIGTERM)]


class _Closable:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def stop(self) -> None:
        self.closed = True


PlaywrightTimeoutBase = type(
    "TimeoutError", (RuntimeError,), {"__module__": "playwright._impl._errors"}
)


class DerivedPlaywrightTimeout(PlaywrightTimeoutBase):
    pass


class _GotoTimeoutPage(_Closable):
    def goto(self, _url: str, *, wait_until: str) -> object:
        assert wait_until == "domcontentloaded"
        raise DerivedPlaywrightTimeout("navigation timed out")


def test_session_converts_playwright_style_timeout_and_closes_initialization_resources() -> None:
    page = _GotoTimeoutPage()
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]
    playwright = _Closable()

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    session._playwright = playwright
    with pytest.raises(RuntimeError) as raised:
        asyncio.run(session.__aenter__())
    assert type(raised.value).__name__ == "TransientBrowserError"
    assert page.closed and context.closed and browser.closed and playwright.closed
    assert session.page is None and session.context is None and session.browser is None


def test_challenge_classifier_ignores_ordinary_safety_description() -> None:
    assert session_module.classify_public_search_state(
        url="https://kns.cnki.net/kns8s/defaultresult/", title="", visible_text="安全验证说明"
    ) is SearchStatus.PAGE_CONTRACT_CHANGED


def test_challenge_classifier_accepts_captcha_url_without_generic_text() -> None:
    assert session_module.classify_public_search_state(
        url="https://kns.cnki.net/captcha", title="", visible_text="请稍候"
    ) is SearchStatus.CHALLENGE_DETECTED


@pytest.mark.parametrize(
    ("url", "title", "text", "http_status", "expected"),
    [
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "拒绝访问 用户登录 统一身份认证",
            "题名 来源 访问过于频繁 无权访问 拒绝访问 用户登录 统一身份认证",
            200,
            SearchStatus.SUCCESS,
        ),
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "中国知网",
            "题名 来源",
            403,
            SearchStatus.FORBIDDEN,
        ),
        (
            "https://kns.cnki.net/verify/home",
            "安全验证",
            "",
            200,
            SearchStatus.CHALLENGE_DETECTED,
        ),
        (
            "https://www.cnki.net/",
            "中国知网",
            "中国知网公开首页",
            200,
            SearchStatus.PAGE_CONTRACT_CHANGED,
        ),
        (
            "https://kns.cnki.net/kns8s/defaultresult/index",
            "中国知网",
            "普通页面说明：请完成安全验证后可继续使用服务",
            200,
            SearchStatus.PAGE_CONTRACT_CHANGED,
        ),
    ],
)
def test_public_state_truth_table_prioritizes_status_and_result_structure(
    url: str, title: str, text: str, http_status: int, expected: SearchStatus,
) -> None:
    assert session_module.classify_public_search_state(
        url=url,
        title=title,
        visible_text=text,
        http_status=http_status,
        has_result_table=expected is SearchStatus.SUCCESS,
    ) is expected


def test_state_truth_table_runs_in_both_runtime_layouts() -> None:
    roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
from cnki_search_env.models import SearchStatus
from cnki_search_env.session import classify_public_search_state

result_url = 'https://kns.cnki.net/kns8s/defaultresult/index'
assert classify_public_search_state(
        url=result_url,
        title='拒绝访问 用户登录',
        visible_text='题名 来源 无权访问 访问过于频繁 用户登录',
        http_status=200,
        has_result_table=True,
    ) is SearchStatus.SUCCESS
assert classify_public_search_state(
    url='https://kns.cnki.net/verify/home', title='安全验证', visible_text='', http_status=200,
) is SearchStatus.CHALLENGE_DETECTED
assert classify_public_search_state(
    url=result_url, title='中国知网', visible_text='题名 来源', http_status=403,
) is SearchStatus.FORBIDDEN
assert classify_public_search_state(
    url='https://www.cnki.net/', title='中国知网', visible_text='首页', http_status=200,
) is SearchStatus.PAGE_CONTRACT_CHANGED
"""
    for root in roots:
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=root,
            env=os.environ | {"PYTHONPATH": str(root)},
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr


def test_result_table_structure_controls_success_and_body_restriction_fallback_in_both_layouts() -> None:
    roots = (ROOT / "scripts", ROOT / "mcpb" / "src")
    program = """
from cnki_search_env.models import SearchStatus
from cnki_search_env.session import SearchSnapshot, classify_public_search_state

url = 'https://kns.cnki.net/kns8s/defaultresult/index'
without_table = SearchSnapshot('<main></main>', url, '中国知网', '题名 来源', 200)
assert without_table.has_result_table is False
assert classify_public_search_state(**without_table.state_arguments()) is SearchStatus.PAGE_CONTRACT_CHANGED
with_table = SearchSnapshot(
    '<table class="result-table-list"><tr><td>题名</td></tr></table>',
    url,
    '中国知网',
    '无权访问 访问过于频繁',
    200,
)
assert with_table.has_result_table is True
assert classify_public_search_state(**with_table.state_arguments()) is SearchStatus.SUCCESS
"""
    for root in roots:
        completed = subprocess.run(
            [sys.executable, "-c", program],
            cwd=root,
            env=os.environ | {"PYTHONPATH": str(root)},
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr


class RestrictedPage:
    def __init__(self, text: str, response_status: int | None = None) -> None:
        self.url = "https://www.cnki.net/"
        self.text = text
        self.response_status = response_status
        self.box_accessed = False

    def title(self) -> str:
        return "中国知网"

    def goto(self, url: str, *, wait_until: str) -> object | None:
        assert (url, wait_until) == (session_module.CNKI_HOME_URL, "domcontentloaded")
        if self.response_status is None:
            return None
        return type("Response", (), {"status": self.response_status})()

    def locator(self, selector: str) -> "RestrictedPage":
        assert selector == "body"
        return self

    def inner_text(self, *, timeout: int) -> str:
        assert timeout == 10_000
        return self.text

    def content(self) -> str:
        return "<main>restricted</main>"

    def get_by_role(self, *_args: object, **_kwargs: object) -> object:
        self.box_accessed = True
        raise AssertionError("受限首页不得访问主题框")

    def get_by_text(self, *_args: object, **_kwargs: object) -> object:
        self.box_accessed = True
        raise AssertionError("受限首页不得访问主题框")


async def _search_with_session(session: PublicCnkiSession, query: str):
    async with session:
        return await session.search(query)

class PostSubmitChallengePage(RestrictedPage):
    """首页正常，提交检索后被风控拦到安全验证页。"""

    def __init__(self) -> None:
        super().__init__("请完成安全验证")
        self.searched = False

    def title(self) -> str:
        return "安全验证" if self.searched else "中国知网"


async def _noop_contract(*_args: object, **_kwargs: object) -> None:
    return None


def test_post_submit_challenge_is_not_reported_as_contract_change() -> None:
    """结果契约未出现时，必须先判断是不是站点主动阻断。

    两者补救方式相反：页面结构变化要改解析器，安全验证必须立即停手。
    一律报 page_contract_changed 会把排查引向错误方向。
    """
    page = PostSubmitChallengePage()
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    class ChallengedRunner:
        async def run(self, _page: object, _query: str) -> int | None:
            page.searched = True
            page.url = "https://kns.cnki.net/verify/home?captchaType=blockPuzzle"
            raise session_module.PageContractChanged("知网公开检索结果结构未出现")

    session = PublicCnkiSession(browser_factory=Factory())
    originals = (session_module.validate_public_theme_search_contract,
                 session_module.PublicThemeSearchRunner)
    session_module.validate_public_theme_search_contract = _noop_contract  # type: ignore[assignment]
    session_module.PublicThemeSearchRunner = ChallengedRunner  # type: ignore[assignment]
    try:
        snapshot = asyncio.run(_search_with_session(session, "环境规制"))
    finally:
        (session_module.validate_public_theme_search_contract,
         session_module.PublicThemeSearchRunner) = originals  # type: ignore[assignment]

    assert session_module.classify_public_search_state(
        **snapshot.state_arguments()
    ) is SearchStatus.CHALLENGE_DETECTED
    assert context.closed and browser.closed


def test_session_returns_initial_restriction_before_theme_contract_and_closes_resources() -> None:
    page = RestrictedPage("403 Forbidden")
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    snapshot = asyncio.run(_search_with_session(session, "主题"))
    assert session_module.classify_public_search_state(**snapshot.state_arguments()) is SearchStatus.FORBIDDEN
    assert page.box_accessed is False
    assert context.closed and browser.closed
@pytest.mark.parametrize(
    ("response_status", "expected"),
    [(403, SearchStatus.FORBIDDEN), (429, SearchStatus.RATE_LIMITED)],
)
def test_session_uses_initial_response_status_before_theme_contract(
    response_status: int, expected: SearchStatus,
) -> None:
    page = RestrictedPage("", response_status)
    context = _Closable()
    context.new_page = lambda: page  # type: ignore[attr-defined]
    browser = _Closable()
    browser.new_context = lambda **_kwargs: context  # type: ignore[attr-defined]

    class Factory:
        def launch_ephemeral(self) -> _Closable:
            return browser

    session = PublicCnkiSession(browser_factory=Factory())
    snapshot = asyncio.run(_search_with_session(session, "主题"))
    assert snapshot.http_status == response_status
    assert session_module.classify_public_search_state(**snapshot.state_arguments()) is expected
    assert page.box_accessed is False
    assert context.closed and browser.closed
