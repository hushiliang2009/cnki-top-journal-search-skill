"""专业检索页驱动的契约测试。

每条断言都对应 2026-07-28 实测得到的一条结构事实。偏离任一条都会以难以归因的
方式失败，因此固化成测试而不是只写注释。
"""
import asyncio
from types import SimpleNamespace

import pytest

from cnki_search_env import webvpn
from cnki_search_env.models import SearchStatus
from cnki_search_env.professional import ExpressionBatch, PlanExecutionResult, SourceCategorySpec


class FakeLocator:
    def __init__(self, page: "FakePage", selector: str, *, count: int = 1,
                 visible: bool = True) -> None:
        self.page = page
        self.selector = selector
        self._count = count
        self._visible = visible
        self.value = ""

    @property
    def first(self) -> "FakeLocator":
        return self

    def nth(self, _index: int) -> "FakeLocator":
        return self

    async def is_visible(self) -> bool:
        return self._visible

    async def is_enabled(self) -> bool:
        return True

    async def count(self) -> int:
        return self._count

    async def fill(self, value: str) -> None:
        # 一框式检索框只收 100 字符，专业检索框收 18000
        cap = self.page.caps.get(self.selector, 18_000)
        self.value = value[:cap]
        self.page.filled = self.value

    async def input_value(self) -> str:
        return self.value

    async def click(self) -> None:
        self.page.actions.append(("click", self.selector))


class FakePage:
    def __init__(self, *, counts: dict | None = None, caps: dict | None = None,
                 tab_switch: bool = True, page_title: str = "中国知网",
                 closed: bool = False, visibility: dict | None = None,
                 url: str = "https://webvpn.example.edu.cn/cnki-home") -> None:
        self.counts = counts or {}
        self.visibility = visibility or {}
        self.caps = caps or {}
        self.tab_switch = tab_switch
        self.page_title = page_title
        self.closed = closed
        self.url = url
        self.actions: list[tuple[str, str]] = []
        self.filled = ""
        self._locators: dict[str, FakeLocator] = {}

    async def title(self) -> str:
        return self.page_title

    def is_closed(self) -> bool:
        return self.closed

    async def wait_for_load_state(self, _state: str) -> None:
        return None

    async def goto(self, url: str, *, wait_until: str) -> None:
        assert wait_until == "domcontentloaded"
        self.url = url

    async def close(self) -> None:
        self.closed = True

    def locator(self, selector: str) -> FakeLocator:
        if selector not in self._locators:
            self._locators[selector] = FakeLocator(
                self, selector, count=self.counts.get(selector, 1),
                visible=self.visibility.get(selector, True))
        return self._locators[selector]

    def get_by_role(self, role: str, name: str) -> FakeLocator:
        key = f"role:{role}:{name}"
        self.actions.append(("get_by_role", key))
        return FakeLocator(self, key, count=self.counts.get(key, 1))

    async def evaluate(self, script: str, arg=None):
        self.actions.append(("evaluate", arg or ""))
        return self.tab_switch


class FakeContext:
    def __init__(self, pages: list) -> None:
        self.pages = pages

    async def new_page(self) -> FakePage:
        page = _home_without_expression_box()
        self.pages.append(page)
        return page


def test_advanced_search_is_reached_through_the_home_page_link() -> None:
    """深链 /kns8s/AdvSearch 会触发安全验证，必须点首页链接。"""
    home = FakePage()
    driver = webvpn.ProfessionalSearchPage(home)
    context = FakeContext([home])
    asyncio.run(driver.open_from_home(context, timeout_seconds=2))
    assert ("get_by_role", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions
    assert ("click", f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}") in home.actions


def _home_without_expression_box(**kwargs) -> FakePage:
    """真实的知网首页没有专业检索表达式框——判据正是靠这一点区分页面。"""
    return FakePage(counts={webvpn.EXPRESSION_BOX_SELECTOR: 0}, **kwargs)


def test_driver_follows_the_new_tab_opened_by_the_link() -> None:
    home = _home_without_expression_box()
    adv = FakePage(page_title="高级检索-中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class GrowingContext:
        def __init__(self) -> None:
            self.pages = [home]

        def open(self) -> None:
            self.pages.append(adv)

    context = GrowingContext()
    original_click = FakeLocator.click

    async def click_and_open(self) -> None:
        await original_click(self)
        context.open()

    FakeLocator.click = click_and_open
    try:
        result = asyncio.run(driver.open_from_home(context, timeout_seconds=3))
    finally:
        FakeLocator.click = original_click
    assert result is adv and driver.page is adv


def test_transient_tab_that_closes_is_skipped_rather_than_adopted() -> None:
    """站点会短暂开一个中转标签页再关掉。

    抓住它会让驱动指向已关闭的页面，后续报错还指向完全错误的原因
    （表现为"未找到专业检索标签"，实则页面早已不存在）。
    """
    home = _home_without_expression_box()
    transient = FakePage(closed=True)
    adv = FakePage(page_title="高级检索-中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home]

    original_click = FakeLocator.click

    async def click_and_open(self) -> None:
        await original_click(self)
        Context.pages.extend([transient, adv])

    FakeLocator.click = click_and_open
    try:
        result = asyncio.run(driver.open_from_home(Context(), timeout_seconds=3))
    finally:
        FakeLocator.click = original_click
    assert result is adv, "应跳过已关闭的中转页，选中真正的高级检索页"


def test_preserved_home_survives_same_tab_navigation() -> None:
    """批次导航即使同页跳转，也只能改变批次自有页面。"""
    home = _home_without_expression_box(page_title="中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context(FakeContext):
        async def new_page(self) -> FakePage:
            page = _home_without_expression_box(
                page_title="高级检索-中国知网"
            )
            self.pages.append(page)
            return page

    context = Context([home])
    result = asyncio.run(
        driver.open_from_home(
            context, timeout_seconds=3, preserve_home=True
        )
    )

    assert result is not home
    assert home.page_title == "中国知网"
    assert home.closed is False


def test_new_tabs_are_closed_when_advanced_contract_is_not_found() -> None:
    home = _home_without_expression_box(page_title="中国知网")
    orphan = _home_without_expression_box(page_title="陌生页面")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home]

    original_click = FakeLocator.click

    async def click_and_open(self) -> None:
        await original_click(self)
        Context.pages.append(orphan)

    FakeLocator.click = click_and_open
    try:
        with pytest.raises(
            webvpn.WebVpnNavigationError,
            match="未出现可用的高级检索页面",
        ):
            asyncio.run(driver.open_from_home(Context(), timeout_seconds=0))
    finally:
        FakeLocator.click = original_click

    assert orphan.closed is True


def test_cancellation_after_new_page_creation_closes_only_the_owned_page() -> None:
    home = _home_without_expression_box(page_title="中国知网")
    created = asyncio.Event()
    batch_page = _home_without_expression_box(page_title="中国知网")
    unrelated = _home_without_expression_box(page_title="用户打开的其他页面")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home, unrelated]

        async def new_page(self) -> FakePage:
            self.pages.append(batch_page)
            created.set()
            await asyncio.sleep(0)
            return batch_page

    async def scenario() -> None:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await created.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())

    assert batch_page.closed is True
    assert home.closed is False
    assert unrelated.closed is False


def test_cancelled_new_page_registered_before_timeout_is_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        webvpn,
        "PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS",
        0.01,
    )
    home = _home_without_expression_box(page_title="中国知网")
    unrelated = _home_without_expression_box(page_title="用户打开的其他页面")
    batch_page = _home_without_expression_box(page_title="中国知网")
    created = asyncio.Event()
    release_creation = asyncio.Event()
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home, unrelated]

        async def new_page(self) -> FakePage:
            self.pages.append(batch_page)
            created.set()
            await release_creation.wait()
            return batch_page

    async def scenario() -> None:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await created.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=0.2)
        closed_before_creation_returns = batch_page.closed
        release_creation.set()
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        assert closed_before_creation_returns is True

    asyncio.run(scenario())

    assert home.closed is False
    assert unrelated.closed is False


def test_cancellation_during_click_closes_owned_popup_not_retained_home() -> None:
    popup_created = asyncio.Event()
    close_started = asyncio.Event()

    class Page(FakePage):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self._popup_handlers = []

        def on(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.append(callback)

        def remove_listener(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.remove(callback)

        def emit_popup(self, popup) -> None:
            for callback in list(self._popup_handlers):
                callback(popup)

    home = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    batch_page = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    popup = Page(page_title="高级检索-中国知网")
    unrelated = Page(page_title="用户打开的其他页面")
    driver = webvpn.ProfessionalSearchPage(home)

    class ClickLocator(FakeLocator):
        async def click(self) -> None:
            Context.pages.append(unrelated)
            batch_page.emit_popup(popup)
            popup_created.set()
            await asyncio.Event().wait()

    def batch_link(role: str, name: str) -> ClickLocator:
        assert role == "link"
        assert name == webvpn.ADV_SEARCH_LINK_TEXT
        return ClickLocator(batch_page, "advanced-link")

    batch_page.get_by_role = batch_link

    original_close = popup.close

    async def close_popup() -> None:
        close_started.set()
        await original_close()

    popup.close = close_popup

    class Context:
        pages = [home]

        async def new_page(self) -> Page:
            self.pages.append(batch_page)
            return batch_page

    async def scenario() -> None:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await popup_created.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert close_started.is_set()

    asyncio.run(scenario())

    assert batch_page.closed is True
    assert popup.closed is True
    assert home.closed is False
    assert unrelated.closed is False


def test_click_cancel_keeps_listener_until_queued_popup_is_owned() -> None:
    click_started = asyncio.Event()
    popup_queued = False

    class Page(FakePage):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self._popup_handlers = []

        def on(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.append(callback)

        def remove_listener(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.remove(callback)

        def emit_popup(self, popup) -> None:
            if popup not in Context.pages:
                Context.pages.append(popup)
            for callback in list(self._popup_handlers):
                callback(popup)

    home = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    unrelated = Page(page_title="取消前已存在的其他页面")
    batch_page = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    popup = Page(page_title="高级检索-中国知网")
    next_batch_popup = Page(page_title="下一批页面")
    driver = webvpn.ProfessionalSearchPage(home)

    class ClickLocator(FakeLocator):
        async def click(self) -> None:
            nonlocal popup_queued
            click_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                popup_queued = True
                raise

    def batch_link(role: str, name: str) -> ClickLocator:
        assert role == "link"
        assert name == webvpn.ADV_SEARCH_LINK_TEXT
        return ClickLocator(batch_page, "advanced-link")

    batch_page.get_by_role = batch_link
    original_close = batch_page.close

    async def close_batch_page() -> None:
        if popup_queued:
            asyncio.get_running_loop().call_soon(
                batch_page.emit_popup,
                popup,
            )
            await asyncio.sleep(0)
        await original_close()

    batch_page.close = close_batch_page

    class Context:
        pages = [home, unrelated]

        async def new_page(self) -> Page:
            self.pages.append(batch_page)
            return batch_page

    async def scenario() -> None:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await click_started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        await asyncio.sleep(0)
        batch_page.emit_popup(next_batch_popup)
        await asyncio.sleep(0)

    asyncio.run(scenario())

    assert batch_page.closed is True
    assert popup.closed is True
    assert home.closed is False
    assert unrelated.closed is False
    assert batch_page._popup_handlers == []
    assert next_batch_popup.closed is False


def test_click_cancel_closes_popup_arriving_within_remaining_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        webvpn,
        "PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS",
        0.10,
    )
    click_started = asyncio.Event()

    class Page(FakePage):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self._popup_handlers = []

        def on(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.append(callback)

        def remove_listener(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.remove(callback)

        def emit_popup(self, popup) -> None:
            for callback in list(self._popup_handlers):
                callback(popup)

    home = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    unrelated = Page(page_title="取消前已存在的其他页面")
    batch_page = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    popup = Page(page_title="延迟到达的高级检索页")
    next_batch_popup = Page(page_title="下一批页面")
    driver = webvpn.ProfessionalSearchPage(home)

    class ClickLocator(FakeLocator):
        async def click(self) -> None:
            click_started.set()
            await asyncio.Event().wait()

    def batch_link(role: str, name: str) -> ClickLocator:
        assert role == "link"
        assert name == webvpn.ADV_SEARCH_LINK_TEXT
        return ClickLocator(batch_page, "advanced-link")

    batch_page.get_by_role = batch_link

    class Context:
        pages = [home, unrelated]

        async def new_page(self) -> Page:
            self.pages.append(batch_page)
            return batch_page

    async def scenario() -> None:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await click_started.wait()
        task.cancel()

        async def deliver_late_popup() -> None:
            await asyncio.sleep(0.03)
            batch_page.emit_popup(popup)

        delivery_task = asyncio.create_task(deliver_late_popup())
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=0.3)
        await delivery_task

        batch_page.emit_popup(next_batch_popup)
        await asyncio.sleep(0)

    asyncio.run(scenario())

    assert batch_page.closed is True
    assert popup.closed is True
    assert home.closed is False
    assert unrelated.closed is False
    assert batch_page._popup_handlers == []
    assert next_batch_popup.closed is False


def test_click_cancel_uses_one_cleanup_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from time import monotonic

    monkeypatch.setattr(
        webvpn,
        "PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS",
        0.05,
    )
    click_started = asyncio.Event()
    close_started = asyncio.Event()

    class Page(FakePage):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self._popup_handlers = []

        def on(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.append(callback)

        def remove_listener(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.remove(callback)

    home = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    batch_page = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    driver = webvpn.ProfessionalSearchPage(home)

    class ClickLocator(FakeLocator):
        async def click(self) -> None:
            click_started.set()
            while not close_started.is_set():
                try:
                    await close_started.wait()
                except asyncio.CancelledError:
                    continue

    def batch_link(role: str, name: str) -> ClickLocator:
        assert role == "link"
        assert name == webvpn.ADV_SEARCH_LINK_TEXT
        return ClickLocator(batch_page, "advanced-link")

    batch_page.get_by_role = batch_link

    async def close_batch_page() -> None:
        close_started.set()
        await asyncio.sleep(0.04)
        batch_page.closed = True

    batch_page.close = close_batch_page

    class Context:
        pages = [home]

        async def new_page(self) -> Page:
            self.pages.append(batch_page)
            return batch_page

    async def scenario() -> float:
        task = asyncio.create_task(
            driver.open_from_home(
                Context(), timeout_seconds=3, preserve_home=True
            )
        )
        await click_started.wait()
        started = monotonic()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=0.3)
        return monotonic() - started

    elapsed = asyncio.run(scenario())

    assert elapsed < 0.075
    assert batch_page.closed is True
    assert home.closed is False
    assert batch_page._popup_handlers == []


def test_click_cancel_retrieves_late_shield_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gc

    monkeypatch.setattr(
        webvpn,
        "PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS",
        0.05,
    )
    click_started = asyncio.Event()
    click_failed = asyncio.Event()
    exception_contexts: list[dict] = []

    class Page(FakePage):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self._popup_handlers = []

        def on(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.append(callback)

        def remove_listener(self, event: str, callback) -> None:
            assert event == "popup"
            self._popup_handlers.remove(callback)

    home = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    batch_page = Page(
        counts={webvpn.EXPRESSION_BOX_SELECTOR: 0},
        page_title="中国知网",
    )
    driver = webvpn.ProfessionalSearchPage(home)

    class ClickLocator(FakeLocator):
        async def click(self) -> None:
            click_started.set()
            cancellations = 0
            while True:
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    cancellations += 1
                    if cancellations < 2:
                        continue
                    click_failed.set()
                    raise RuntimeError("click-late")

    def batch_link(role: str, name: str) -> ClickLocator:
        assert role == "link"
        assert name == webvpn.ADV_SEARCH_LINK_TEXT
        return ClickLocator(batch_page, "advanced-link")

    batch_page.get_by_role = batch_link

    class Context:
        pages = [home]

        async def new_page(self) -> Page:
            self.pages.append(batch_page)
            return batch_page

    async def scenario() -> None:
        loop = asyncio.get_running_loop()
        previous_handler = loop.get_exception_handler()
        loop.set_exception_handler(
            lambda _loop, context: exception_contexts.append(context)
        )
        try:
            task = asyncio.create_task(
                driver.open_from_home(
                    Context(), timeout_seconds=3, preserve_home=True
                )
            )
            await click_started.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=0.3)
            await click_failed.wait()
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            gc.collect()
            await asyncio.sleep(0)
        finally:
            loop.set_exception_handler(previous_handler)

    asyncio.run(scenario())

    assert exception_contexts == []
    assert batch_page.closed is True
    assert home.closed is False
    assert batch_page._popup_handlers == []


def test_no_usable_advanced_search_page_raises_with_actionable_message() -> None:
    home = _home_without_expression_box(page_title="中国知网")
    driver = webvpn.ProfessionalSearchPage(home)

    class Context:
        pages = [home]

    with pytest.raises(webvpn.WebVpnNavigationError, match="未出现可用的高级检索页面"):
        asyncio.run(driver.open_from_home(Context(), timeout_seconds=2))


def test_missing_home_link_is_reported_rather_than_deep_linking() -> None:
    home = FakePage(counts={f"role:link:{webvpn.ADV_SEARCH_LINK_TEXT}": 0})
    driver = webvpn.ProfessionalSearchPage(home)
    with pytest.raises(webvpn.WebVpnNavigationError, match="高级检索"):
        asyncio.run(driver.open_from_home(FakeContext([home]), timeout_seconds=2))


def test_professional_tab_is_switched_through_javascript_click() -> None:
    """非活动标签被 CSS 隐藏，Playwright 判定其不可见，只能用 JS 触发。

    到达高级检索页时表达式框是"存在但不可见"，此处必须如实建模——旧假页面
    默认它可见，正是这一点让"用 count() 判存在"的缺陷得以通过测试。
    """
    page = TogglingTabPage(starts_professional=False)
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.switch_to_professional(timeout_seconds=2))
    assert ("evaluate", webvpn.PROFESSIONAL_TAB_TEXT) in page.actions


class TogglingTabPage(FakePage):
    """真实站点：表达式框在两个标签下都在 DOM 里，只在专业检索标签下可见；
    再点一次标签会切回去。同一会话第二次进入高级检索页时，站点记住上次的
    标签，本就停在专业检索——此时若无条件再点，反而把它切走。"""

    def __init__(self, *, starts_professional: bool = False) -> None:
        super().__init__(visibility={webvpn.EXPRESSION_BOX_SELECTOR: starts_professional})
        self.tab_clicks = 0

    async def evaluate(self, script: str, arg=None):
        self.tab_clicks += 1
        self.actions.append(("evaluate", arg or ""))
        box = self.locator(webvpn.EXPRESSION_BOX_SELECTOR)
        box._visible = not box._visible          # 标签切换是开关，不是幂等赋值
        return self.tab_switch


def test_switch_confirms_the_box_is_visible_not_merely_present() -> None:
    """判据必须是可见而不是存在。

    表达式框在高级检索标签下同样在 DOM 里，只是被 CSS 隐藏。用 count() 判定
    会在切换根本没生效时也返回成功，随后 fill 在不可见元素上白等 30 秒，
    报出的现象还指向完全错误的方向。
    """
    page = FakePage(visibility={webvpn.EXPRESSION_BOX_SELECTOR: False})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="表达式框"):
        asyncio.run(driver.switch_to_professional(timeout_seconds=2))


def test_switch_is_idempotent_when_already_on_the_professional_tab() -> None:
    """已经停在专业检索标签时不得再点——再点会切回高级检索。"""
    page = TogglingTabPage(starts_professional=True)
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.switch_to_professional(timeout_seconds=2))
    assert page.tab_clicks == 0
    assert asyncio.run(page.locator(webvpn.EXPRESSION_BOX_SELECTOR).is_visible()) is True


def test_second_search_in_one_session_still_reaches_the_professional_tab() -> None:
    """同一会话内连续两次专业检索：第二次站点已停在专业检索标签。

    通用版真实验证是两次独立进程各登录一次，从未走到这条路径；而 MCP 工具
    缓存会话，第二次调用必然走到这里。
    """
    page = TogglingTabPage(starts_professional=False)
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.switch_to_professional(timeout_seconds=2))
    assert page.tab_clicks == 1
    asyncio.run(driver.switch_to_professional(timeout_seconds=2))
    assert asyncio.run(page.locator(webvpn.EXPRESSION_BOX_SELECTOR).is_visible()) is True


def test_missing_professional_tab_raises() -> None:
    driver = webvpn.ProfessionalSearchPage(
        FakePage(tab_switch=False, visibility={webvpn.EXPRESSION_BOX_SELECTOR: False})
    )
    with pytest.raises(webvpn.WebVpnNavigationError, match="专业检索"):
        asyncio.run(driver.switch_to_professional(timeout_seconds=2))


def test_expression_is_typed_into_the_professional_box_only() -> None:
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    expression = "SU %= '数字经济' AND (LY='管理世界')"
    asyncio.run(driver.fill_expression(expression))
    assert page.locator(webvpn.EXPRESSION_BOX_SELECTOR).value == expression


def test_truncated_expression_aborts_instead_of_submitting_half_a_query() -> None:
    """误填到一框式检索框（上限 100 字符）会静默截断，提交后站点返回「访问禁止」。

    截断后的半截语法仍是"合法"提交，返回的却是完全不同的检索范围——必须中止，
    否则会把错误结果当成真实检索结果报出去。
    """
    page = FakePage(caps={webvpn.EXPRESSION_BOX_SELECTOR: 100})
    driver = webvpn.ProfessionalSearchPage(page)
    long_expression = "SU %= '数字经济' AND (" + " OR ".join(
        f"LY='测试期刊{index:03d}'" for index in range(20)) + ")"
    assert len(long_expression) > 100
    with pytest.raises(webvpn.ExpressionTruncated) as raised:
        asyncio.run(driver.fill_expression(long_expression))
    assert "100" in str(raised.value)
    assert ("click", webvpn.SEARCH_BUTTON_SELECTOR) not in page.actions


def test_missing_expression_box_raises() -> None:
    page = FakePage(counts={webvpn.EXPRESSION_BOX_SELECTOR: 0})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="表达式输入框"):
        asyncio.run(driver.fill_expression("SU %= '主题'"))


def test_submit_clicks_the_professional_search_button() -> None:
    page = FakePage()
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.submit())
    clicked = {selector for action, selector in page.actions if action == "click"}
    assert clicked & set(webvpn.SEARCH_BUTTON_SELECTORS)


def test_submit_skips_the_hidden_namesake_button() -> None:
    """input.search-btn 在高级检索页尺寸 0×0；选中它会重试到 30 秒超时。"""
    page = FakePage(visibility={"input.btn-search": False, "input.search-btn": True})
    driver = webvpn.ProfessionalSearchPage(page)
    asyncio.run(driver.submit())
    assert ("click", "input.search-btn") in page.actions


def test_missing_search_button_raises() -> None:
    page = FakePage(counts={selector: 0 for selector in webvpn.SEARCH_BUTTON_SELECTORS})
    driver = webvpn.ProfessionalSearchPage(page)
    with pytest.raises(webvpn.WebVpnNavigationError, match="检索按钮"):
        asyncio.run(driver.submit())


def test_selectors_match_the_observed_page_structure() -> None:
    """选择器一旦被随手改动，失败现象会伪装成风控，因此钉死在测试里。"""
    assert webvpn.EXPRESSION_BOX_SELECTOR == "textarea.textarea-major.majorSearch"
    assert webvpn.SEARCH_BUTTON_SELECTORS[0] == "input.btn-search"
    assert "input.search-btn" in webvpn.SEARCH_BUTTON_SELECTORS
    assert webvpn.RESULT_TABLE_SELECTOR == "table.result-table-list"
    assert webvpn.ADV_SEARCH_LINK_TEXT == "高级检索"
    assert webvpn.PROFESSIONAL_TAB_TEXT == "专业检索"


class PlanPage:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.url = "https://webvpn.example.edu.cn/result"

    async def content(self) -> str:
        self.events.append("content")
        return "<table class='result-table-list'></table>"


class PlanRecorder(webvpn.ProfessionalSearchPage):
    def __init__(self, events: list[str]) -> None:
        super().__init__(PlanPage(events))
        self.events = events

    async def fill_expression(self, expression: str) -> None:
        assert expression == "SU %= '数字经济'"
        self.events.append("fill")

    async def submit(self) -> None:
        self.events.append("submit")

    async def wait_for_outcome(self, timeout_seconds: float = 30) -> SearchStatus:
        self.events.append("classify")
        return SearchStatus.SUCCESS

    async def apply_source_category(self, category: SourceCategorySpec | str, *,
                                    timeout_seconds: float = 20.0) -> str | None:
        label = category.label if isinstance(category, SourceCategorySpec) else category
        self.events.append(f"facet:{label}")
        requested = category if isinstance(category, SourceCategorySpec) else \
            SourceCategorySpec("P0209", category)
        return webvpn.SourceCategoryApplication(
            requested, True, 10, SearchStatus.SUCCESS,
        )

    async def set_page_size(self, size: int = 50, *,
                            timeout_seconds: float = 20.0) -> int:
        self.events.append(f"page_size:{size}")
        return size


def _plan(*, source_category: SourceCategorySpec | str | None) -> ExpressionBatch:
    return ExpressionBatch(
        index=1,
        total=1,
        journals=(),
        expression="SU %= '数字经济'",
        page_size=50,
        source_category=source_category,
    )


class ControlledFacetLocator:
    def __init__(self) -> None:
        self.checked = False

    @property
    def first(self) -> "ControlledFacetLocator":
        return self

    async def count(self) -> int:
        return 1

    async def check(self) -> None:
        self.checked = True

    async def is_checked(self) -> bool:
        return self.checked


class ControlledFacetPlanPage(PlanPage):
    def __init__(self, events: list[str]) -> None:
        super().__init__(events)
        self.facet = ControlledFacetLocator()
        self.facet_selector: str | None = None

    def locator(self, selector: str) -> ControlledFacetLocator:
        if selector.startswith("input[type=checkbox]"):
            self.facet_selector = selector
        return self.facet

    async def evaluate(self, _script: str) -> str:
        return "2,270" if self.facet.checked else "2,378"


class ControlledFacetPlanDriver(webvpn.ProfessionalSearchPage):
    def __init__(self, page: ControlledFacetPlanPage, events: list[str]) -> None:
        super().__init__(page)
        self.events = events

    async def fill_expression(self, expression: str) -> None:
        assert expression == "SU %= '数字经济'"
        self.events.append("fill")

    async def submit(self) -> None:
        self.events.append("submit")

    async def wait_for_outcome(self, timeout_seconds: float = 30) -> SearchStatus:
        self.events.append("classify")
        return SearchStatus.SUCCESS

    async def set_page_size(self, size: int = 50, *,
                            timeout_seconds: float = 20.0) -> int:
        self.events.append(f"page_size:{size}")
        return size


class MissingFacetLocator:
    @property
    def first(self) -> "MissingFacetLocator":
        return self

    async def count(self) -> int:
        return 0


class MissingFacetPlanPage(PlanPage):
    def locator(self, selector: str) -> MissingFacetLocator:
        assert selector == webvpn.SOURCE_CATEGORY_SELECTOR.format(value="P01")
        return MissingFacetLocator()


class MissingFacetPlanDriver(webvpn.ProfessionalSearchPage):
    def __init__(self, page: MissingFacetPlanPage, events: list[str]) -> None:
        super().__init__(page)
        self.events = events

    async def fill_expression(self, expression: str) -> None:
        assert expression == "SU %= '数字经济'"
        self.events.append("fill")

    async def submit(self) -> None:
        self.events.append("submit")

    async def wait_for_outcome(self, timeout_seconds: float = 30) -> SearchStatus:
        self.events.append("classify")
        return SearchStatus.SUCCESS

    async def set_page_size(self, size: int = 50, *,
                            timeout_seconds: float = 20.0) -> int:
        self.events.append(f"page_size:{size}")
        return size


class PostFacetStatusDriver(PlanRecorder):
    def __init__(self, events: list[str], status: SearchStatus, *,
                 applied: bool = True) -> None:
        super().__init__(events)
        self.post_facet_status = status
        self.applied = applied

    async def apply_source_category(self, category: SourceCategorySpec | str, *,
                                    timeout_seconds: float = 20.0):
        label = category.label if isinstance(category, SourceCategorySpec) else category
        self.events.extend((f"facet:{label}", f"classify:{self.post_facet_status.value}"))
        return SimpleNamespace(
            applied=self.applied,
            total=50 if self.applied else None,
            status=self.post_facet_status,
        )


def test_real_execute_plan_uses_controlled_facet_code_and_reports_total(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_wait(_seconds: float) -> None:
        return None

    monkeypatch.setattr(webvpn.asyncio, "sleep", no_wait)
    events: list[str] = []
    page = ControlledFacetPlanPage(events)
    driver = ControlledFacetPlanDriver(page, events)

    result = asyncio.run(
        driver.execute_plan(
            _plan(source_category=SourceCategorySpec("P0209", "CSSCI"))
        )
    )

    assert page.facet_selector == webvpn.SOURCE_CATEGORY_SELECTOR.format(
        value="P0209"
    )
    assert result.source_category_applied is True
    assert result.source_category_total == 2270


def test_real_execute_plan_stops_when_requested_facet_is_missing() -> None:
    """真实分面执行器缺少目标复选框时，不得退回未筛选结果。"""
    events: list[str] = []
    page = MissingFacetPlanPage(events)
    driver = MissingFacetPlanDriver(page, events)

    result = asyncio.run(
        driver.execute_plan(
            _plan(source_category=SourceCategorySpec("P01", "北大核心"))
        )
    )

    assert result == PlanExecutionResult(
        SearchStatus.PAGE_CONTRACT_CHANGED.value,
        "",
        "https://webvpn.example.edu.cn/result",
        False,
        None,
    )
    assert events == ["fill", "submit", "classify"]


def test_execute_plan_applies_post_result_options_before_final_render() -> None:
    events: list[str] = []
    driver = PlanRecorder(events)

    result = asyncio.run(
        driver.execute_plan(_plan(source_category=SourceCategorySpec("P0209", "CSSCI")))
    )

    assert result == PlanExecutionResult(
        "success", "<table class='result-table-list'></table>",
        "https://webvpn.example.edu.cn/result", True, 10,
    )
    assert events == [
        "fill", "submit", "classify",
        "facet:CSSCI", "page_size:50", "classify", "content",
    ]


def test_execute_plan_omits_facet_for_chinese_top_plan() -> None:
    events: list[str] = []
    driver = PlanRecorder(events)

    result = asyncio.run(driver.execute_plan(_plan(source_category=None)))

    assert result.status == SearchStatus.SUCCESS.value
    assert result.source_category_applied is False
    assert result.source_category_total is None
    assert all(not event.startswith("facet:") for event in events)


@pytest.mark.parametrize(
    ("after_status", "expected"),
    [
        (SearchStatus.NO_RESULTS, "no_results"),
        (SearchStatus.CHALLENGE_DETECTED, "challenge_detected"),
        (SearchStatus.PAGE_CONTRACT_CHANGED, "page_contract_changed"),
    ],
)
def test_execute_plan_rechecks_status_after_facet(
    after_status: SearchStatus, expected: str,
) -> None:
    """分面刷新若进入终止状态，严禁再调整页大小或读取未筛选页面。"""
    events: list[str] = []
    result = asyncio.run(
        PostFacetStatusDriver(events, after_status).execute_plan(
            _plan(source_category=SourceCategorySpec("P0209", "CSSCI"))
        )
    )

    assert result.status == expected
    assert result.html == ""
    assert "page_size:50" not in events


def test_missing_or_unchecked_facet_never_returns_unfiltered_html() -> None:
    events: list[str] = []
    result = asyncio.run(
        PostFacetStatusDriver(
            events, SearchStatus.PAGE_CONTRACT_CHANGED, applied=False,
        ).execute_plan(_plan(source_category=SourceCategorySpec("P01", "北大核心")))
    )

    assert result.status == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result.source_category_applied is False
    assert result.html == ""
    assert "page_size:50" not in events


class UnchangedTotalFacetPage(ControlledFacetPlanPage):
    async def evaluate(self, _script: str) -> str:
        return "50"


def test_unchanged_total_is_valid_when_checkbox_is_checked_and_page_is_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """分面命中全部结果时总数可以不变，不能被误判为未生效。"""
    async def no_wait(_seconds: float) -> None:
        return None

    monkeypatch.setattr(webvpn.asyncio, "sleep", no_wait)
    events: list[str] = []
    driver = ControlledFacetPlanDriver(UnchangedTotalFacetPage(events), events)

    application = asyncio.run(
        driver.apply_source_category(
            SourceCategorySpec("P0209", "CSSCI"), timeout_seconds=5.0,
        )
    )

    assert application.applied is True
    assert application.total == 50
    assert application.status is SearchStatus.SUCCESS


class AmbiguousFacetLocator:
    """同一 value 命中多个复选框：结构已变，不能任选其一。"""

    def __init__(self, count: int) -> None:
        self._count = count
        self.checked = False

    @property
    def first(self) -> "AmbiguousFacetLocator":
        return AmbiguousFacetLocator(1)

    async def count(self) -> int:
        return self._count

    async def check(self) -> None:
        self.checked = True

    async def is_checked(self) -> bool:
        return self.checked


class AmbiguousFacetPlanPage(PlanPage):
    def locator(self, selector: str) -> AmbiguousFacetLocator:
        if selector.startswith("input[type=checkbox]"):
            return AmbiguousFacetLocator(2)
        return AmbiguousFacetLocator(1)

    async def evaluate(self, _script: str, _arg=None) -> str:
        return "50"


def test_duplicate_source_category_checkbox_is_a_contract_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`.first` 会掩盖歧义；命中数必须在取 first 之前判定。"""
    async def no_wait(_seconds: float) -> None:
        return None

    monkeypatch.setattr(webvpn.asyncio, "sleep", no_wait)
    events: list[str] = []
    driver = ControlledFacetPlanDriver(AmbiguousFacetPlanPage(events), events)

    result = asyncio.run(
        driver.execute_plan(_plan(source_category=SourceCategorySpec("P0209", "CSSCI")))
    )

    assert result.status == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result.source_category_applied is False
    assert result.html == ""
    assert "page_size:50" not in events


def test_unapplied_facet_blocks_page_size_even_when_status_is_success() -> None:
    """状态仍为 success 但分面未真正生效时，同样不得读取未筛选结果。"""
    events: list[str] = []
    result = asyncio.run(
        PostFacetStatusDriver(
            events, SearchStatus.SUCCESS, applied=False,
        ).execute_plan(_plan(source_category=SourceCategorySpec("P0209", "CSSCI")))
    )

    assert result.status == SearchStatus.PAGE_CONTRACT_CHANGED.value
    assert result.source_category_applied is False
    assert result.source_category_total is None
    assert result.html == ""
    assert "page_size:50" not in events


class DelayedResultLocator:
    def __init__(self, page: "DelayedResultPage", selector: str) -> None:
        self.page = page
        self.selector = selector

    async def count(self) -> int:
        if self.selector == webvpn.RESULT_TABLE_SELECTOR:
            self.page.result_polls += 1
            return int(self.page.result_polls >= 3)
        return 1

    async def inner_text(self, *, timeout: int) -> str:
        return ""


class DelayedResultPage:
    def __init__(self) -> None:
        self.result_polls = 0

    def locator(self, selector: str) -> DelayedResultLocator:
        return DelayedResultLocator(self, selector)

    async def evaluate(self, _script: str, _markers: list[str]) -> bool:
        return False


def test_wait_for_outcome_polls_through_temporary_contract_change() -> None:
    page = DelayedResultPage()
    driver = webvpn.ProfessionalSearchPage(page)

    status = asyncio.run(driver.wait_for_outcome(timeout_seconds=1, poll_seconds=0))

    assert status is SearchStatus.SUCCESS
    assert page.result_polls == 3
