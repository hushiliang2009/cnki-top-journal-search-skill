"""WebVPN 人工值守模式的会话与批次调度。

与公开匿名模式（``PublicCnkiSession``）平级、互不影响。启用本模式需要使用者
本人以校园账号经学校官方 WebVPN 完成统一身份认证，并在整个检索期间保持浏览器
窗口打开。

三处人工介入无法自动化，是架构约束而非实现缺陷：

1. **统一身份认证**：需要校园账号密码，程序不接触凭据。
2. **登录态不能跨进程复用**：WebVPN 票据是 session cookie，导出后在新浏览器
   进程里会被服务端直接拒绝（有头/无头皆然，与 User-Agent 无关）。因此登录与
   检索必须在同一进程内完成，且不把票据写入磁盘。
3. **中途安全验证**：连续请求触发风控时需要人工滑动，程序不得自动破解。

因此本模式**不可用于定时任务或任何无人值守场景**。

本模块把「批次调度状态机」与「浏览器生命周期」分开：前者是纯逻辑，可离线测试；
后者才需要 Playwright。
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import time
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .browser import BrowserUnavailableError, await_maybe
from .models import MAX_RESULTS_PER_PAGE, SearchStatus
from .professional import ExpressionBatch

#: 实测：连续 4 次快速请求即触发安全验证，冷却约 75 秒后恢复。30 秒是据此取的
#: 保守值，**不是**二分测试得出的安全阈值，长时间高频使用仍可能触发风控。
MIN_REQUEST_INTERVAL_SECONDS = 30.0
#: 命中风控后在常规间隔之外额外等待，避免把账号推向更严的限制。
CHALLENGE_BACKOFF_SECONDS = 180.0
#: 同一批次因风控最多重试几次；超过则如实上报未完成，交由使用者决定。
MAX_CHALLENGE_RETRIES = 3
PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS = 5.0

LOGIN_READY_TITLE = "中国知网"
DEFAULT_LOGIN_TIMEOUT_SECONDS = 600.0
DEFAULT_POLL_INTERVAL_SECONDS = 3.0


# ── 高级/专业检索页的真实结构（2026-07-28 实测） ──────────────────────────
#: 高级检索页**不能深链**。直接访问 /kns8s/AdvSearch 会被判定为异常访问并跳转
#: 安全验证页；从知网首页点「高级检索」链接则一切正常（在新标签页打开）。
ADV_SEARCH_LINK_TEXT = "高级检索"
PROFESSIONAL_TAB_TEXT = "专业检索"
#: 非活动标签被 CSS 隐藏，Playwright 的可见性判定会认为它不可点，
#: 因此标签切换只能用 JS 直接触发 click。
PROFESSIONAL_TAB_CLICK_JS = """(label) => {
  const text = (node) => (node.textContent || '').replace(/\\s+/g, '');
  const hit = [...document.querySelectorAll('li,a,span,div')]
    .filter((node) => node.children.length === 0 && text(node) === label)
    .sort((a, b) => (b.offsetParent ? 1 : 0) - (a.offsetParent ? 1 : 0))[0];
  if (!hit) return false;
  hit.click();
  return true;
}"""
#: 必须精确定位专业检索的表达式框。页面顶部另有一框式检索输入框，其长度上限
#: 只有 100 字符；误填到那里会把表达式**静默截断成半截语法**再提交，站点直接
#: 返回「访问禁止」，而且现象看起来像风控，极易误判。
EXPRESSION_BOX_SELECTOR = "textarea.textarea-major.majorSearch"
#: 高级检索页的提交按钮是 input.btn-search（实测 161×34 可见）。
#: 页面上同时存在 input.search-btn，但那是知网首页按钮的类名，在这里尺寸为
#: 0×0 且不可点——按 class 取 .first 会拿到它，点击必然超时 30 秒。
#: 因此按候选顺序逐个挑"真正可见可点"的，而不是认定某一个。
SEARCH_BUTTON_SELECTORS = (
    "input.btn-search",
    "input.search-btn",
    "input[type=button][value='检索']",
)
SEARCH_BUTTON_SELECTOR = SEARCH_BUTTON_SELECTORS[0]
RESULT_TABLE_SELECTOR = "table.result-table-list"
#: 「抱歉，暂无数据，请稍后重试。」——服务端临时拒绝的措辞。
NO_DATA_MARKERS = ("暂无数据", "请稍后重试")
#: 结果页左侧「来源类别」分面的取值。
#:
#: 它只出现在**结果页**，高级检索输入页上没有——曾据输入页错判为"来源类别
#: 筛选不存在"，进而以为 CSSCI 只能靠枚举 661 本刊名。实际用分面更好：
#: 一次请求即可，且 CSSCI 分面含来源期刊与扩展版，范围大于目录里的 674 本，
#: 也不受刊名全半角变体的影响。
SOURCE_CATEGORY_VALUES = {
    "CSSCI": "P0209",
    "北大核心": "P01",
    "AMI": "P13",
    "WJCI": "P12",
    "CSCD": "P0210",
}
SOURCE_CATEGORY_SELECTOR = "input[type=checkbox][value='{value}']"
TOTAL_COUNT_JS = (
    r"""() => (document.body.innerText.match(/共找到\s*([\d,]+)\s*条结果/) || [])[1] || null"""
)
#: 每页条数是自定义下拉，不是原生 <select>；列表默认 display:none，需先点开。
#: 实测档位仅 10/20/50。
PAGE_SIZE_CLICK_JS = """(want) => {
  const root = document.querySelector('div.page-show-count');
  if (!root) return false;
  const item = root.querySelector(`li[data-val="${want}"]`);
  if (!item) return false;
  const trigger = root.querySelector('.sort-default');
  if (trigger) trigger.click();
  (item.querySelector('a') || item).click();
  return true;
}"""
#: 安全验证组件**始终存在于 DOM 中**，未触发时被停在 top:-1000430px 的离屏位置，
#: 且 display:block、visibility:visible、offsetParent 非空。因此判断它是否真的
#: 出现，必须检查元素矩形是否落在视口内；用文本出现与否或 offsetParent 判断，
#: 会把每一次"无结果"都误报成安全验证，把排查引向完全错误的方向。
CAPTCHA_TEXT_MARKERS = ("拖动下方拼图", "请完成安全验证")
CAPTCHA_VIEWPORT_JS = """(markers) => {
  const inViewport = (node) => {
    const rect = node.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && rect.bottom > 0 && rect.right > 0 &&
           rect.top < window.innerHeight && rect.left < window.innerWidth;
  };
  return [...document.querySelectorAll('div,span')]
    .filter((node) => markers.some((marker) =>
      (node.textContent || '').replace(/\\s+/g, '').includes(marker)))
    .some(inViewport);
}"""


class ExpressionTruncated(RuntimeError):
    """输入框接受的字符数少于提交的表达式，继续提交会得到错误的检索范围。"""


class WebVpnNavigationError(RuntimeError):
    """页面结构与实测契约不符，重试无意义。"""


class WebVpnLoginTimeout(RuntimeError):
    """在允许的时间内没有检测到已登录的知网首页。"""


class WebVpnWindowClosed(RuntimeError):
    """浏览器窗口被关闭，会话无法继续。关窗等同于登出。"""


async def _finish_cleanup(cleanup: Awaitable[Any]) -> None:
    """等待清理任务完成，期间外层任务的重复取消不得中断资源回收。"""
    task = asyncio.ensure_future(cleanup)
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            continue
    await task


def _clear_current_cancellation() -> None:
    task = asyncio.current_task()
    if task is not None:
        while task.cancelling():
            task.uncancel()


async def _wait_task_bounded(
    task: asyncio.Task[Any],
    timeout_seconds: float,
    *,
    cancel_on_timeout: bool,
) -> tuple[bool, asyncio.CancelledError | None]:
    """有界等待独立任务，并记录等待期间收到的客户端取消。"""
    deadline = asyncio.get_running_loop().time() + max(timeout_seconds, 0.0)
    return await _wait_task_until(
        task,
        deadline,
        cancel_on_timeout=cancel_on_timeout,
    )


async def _wait_task_until(
    task: asyncio.Task[Any],
    deadline: float,
    *,
    cancel_on_timeout: bool,
) -> tuple[bool, asyncio.CancelledError | None]:
    """在同一个单调时钟截止点前等待独立任务。"""
    cancellation: asyncio.CancelledError | None = None
    while not task.done():
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            if cancel_on_timeout:
                task.cancel()
            return False, cancellation
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=remaining)
        except TimeoutError:
            if cancel_on_timeout:
                task.cancel()
            return False, cancellation
        except asyncio.CancelledError as exc:
            current = asyncio.current_task()
            if current is not None and current.cancelling():
                cancellation = cancellation or exc
                _clear_current_cancellation()
                continue
            if task.done():
                break
            raise
        except BaseException:
            if task.done():
                break
            raise
    return True, cancellation


async def _finish_cleanup_bounded(
    cleanup: Awaitable[Any],
    timeout_seconds: float,
) -> tuple[bool, asyncio.CancelledError | None]:
    task = asyncio.ensure_future(cleanup)
    return await _wait_task_bounded(
        task,
        timeout_seconds,
        cancel_on_timeout=True,
    )


async def _finish_cleanup_until(
    cleanup: Awaitable[Any],
    deadline: float,
) -> tuple[bool, asyncio.CancelledError | None]:
    task = asyncio.ensure_future(cleanup)
    return await _wait_task_until(
        task,
        deadline,
        cancel_on_timeout=True,
    )


@dataclass(frozen=True, slots=True)
class WebVpnConfig:
    """WebVPN 入口配置。

    ``home_url`` 是学校 WebVPN 改写后的知网首页地址。WebVPN 对每个后端主机的
    编码不同（首页与结果页的编码主机并不一致），因此只固定首页入口，后续跳转
    交给站点自身处理，不对结果页 URL 做等值断言。
    """

    home_url: str
    login_timeout_seconds: float = DEFAULT_LOGIN_TIMEOUT_SECONDS
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS

    def __post_init__(self) -> None:
        if not self.home_url.startswith("https://"):
            raise ValueError("WebVPN 入口必须是 https 地址")
        if self.login_timeout_seconds <= 0 or self.poll_interval_seconds <= 0:
            raise ValueError("超时与轮询间隔必须为正数")


class Throttle:
    """跨进程持久的请求节流。

    时间戳必须落盘：常驻模式下模块可能被重新加载，放在模块级变量里的状态会丢，
    节流随之失效。
    """

    def __init__(self, state_file: Path, *,
                 min_interval: float = MIN_REQUEST_INTERVAL_SECONDS,
                 challenge_backoff: float = CHALLENGE_BACKOFF_SECONDS,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                 now: Callable[[], float] = time.time) -> None:
        self.state_file = state_file
        self.min_interval = min_interval
        self.challenge_backoff = challenge_backoff
        self._sleep = sleep
        self._now = now

    def _read(self) -> tuple[float, float]:
        try:
            last, backoff = self.state_file.read_text(encoding="utf-8").split()
            return float(last), float(backoff)
        except (OSError, ValueError):
            return 0.0, 0.0

    def record(self, *, challenged: bool = False) -> None:
        backoff = self.challenge_backoff if challenged else 0.0
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(f"{self._now()} {backoff}", encoding="utf-8")
        except OSError:
            pass

    async def wait(self) -> float:
        """按需等待，返回实际等待秒数。"""
        last, backoff = self._read()
        if not last:
            return 0.0
        required = self.min_interval + backoff
        elapsed = self._now() - last
        if elapsed >= required:
            return 0.0
        delay = required - elapsed
        await self._sleep(delay)
        return delay


@dataclass
class BatchCheckpoint:
    """已完成批次的断点记录。

    风控中断后从断点续跑，不重复已完成的批次——重跑既浪费限流预算，也会把
    账号更快推向风控。
    """

    state_file: Path
    completed: dict[int, dict[str, Any]] = field(default_factory=dict)

    def load(self, token: str) -> None:
        try:
            payload = json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if payload.get("token") != token:      # 检索条件变了，旧断点作废
            return
        self.completed = {int(key): value for key, value in payload.get("completed", {}).items()}

    def save(self, token: str) -> None:
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(
                json.dumps({"token": token, "completed": self.completed}, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    def clear(self) -> None:
        self.completed = {}
        self.state_file.unlink(missing_ok=True)


BatchExecutor = Callable[[ExpressionBatch], Awaitable[dict[str, Any]]]
ChallengeHandler = Callable[[ExpressionBatch], Awaitable[bool]]


async def run_batches(
    batches: Sequence[ExpressionBatch],
    execute: BatchExecutor,
    *,
    on_challenge: ChallengeHandler | None = None,
    checkpoint: BatchCheckpoint | None = None,
    throttle: Throttle | None = None,
    max_challenge_retries: int = MAX_CHALLENGE_RETRIES,
) -> dict[str, Any]:
    """依次执行各批次，遇安全验证则暂停等待人工处理后续跑。

    ``on_challenge`` 返回 ``True`` 表示人工已完成验证、可以重试当前批次；
    返回 ``False`` 表示放弃，此时如实上报未完成批次而不是假装成功。
    """
    if not batches:
        raise ValueError("批次列表不能为空")
    token = "|".join(batch.expression for batch in batches)
    if checkpoint is not None:
        checkpoint.load(token)

    results: list[dict[str, Any]] = []
    human_intervention_required = False
    for batch in batches:
        if checkpoint is not None and batch.index in checkpoint.completed:
            results.append(checkpoint.completed[batch.index])
            continue

        attempts = 0
        while True:
            if throttle is not None:
                await throttle.wait()
            result = await execute(batch)
            challenged = result.get("status") == SearchStatus.CHALLENGE_DETECTED.value
            if throttle is not None:
                throttle.record(challenged=challenged)
            if result.get("status") == SearchStatus.PAGE_CONTRACT_CHANGED.value:
                return _summary(
                    results,
                    batches,
                    token,
                    checkpoint,
                    human_intervention_required,
                    stopped_at=batch,
                    stopped_result=result,
                )
            if not challenged:
                break
            human_intervention_required = True
            attempts += 1
            if on_challenge is None or attempts > max_challenge_retries:
                return _summary(results, batches, token, checkpoint,
                                human_intervention_required, stopped_at=batch)
            if not await on_challenge(batch):
                return _summary(results, batches, token, checkpoint,
                                human_intervention_required, stopped_at=batch)

        results.append(result)
        if checkpoint is not None:
            checkpoint.completed[batch.index] = result
            checkpoint.save(token)

    if checkpoint is not None:
        checkpoint.clear()
    return _summary(results, batches, token, checkpoint, human_intervention_required)


def _summary(results: list[dict[str, Any]], batches: Sequence[ExpressionBatch],
             token: str, checkpoint: BatchCheckpoint | None,
             human_intervention_required: bool,
             stopped_at: ExpressionBatch | None = None,
             stopped_result: dict[str, Any] | None = None) -> dict[str, Any]:
    if stopped_at is not None and checkpoint is not None:
        checkpoint.save(token)
    return {
        "batches_completed": len(results),
        "batches_total": len(batches),
        "complete": stopped_at is None,
        "stopped_at_batch": stopped_at.index if stopped_at is not None else None,
        "stopped_result": stopped_result,
        "human_intervention_required": human_intervention_required,
        "results": results,
    }


class WebVpnSession:
    """有头浏览器的非持久化会话，用于承载人工登录并在同一进程完成检索。

    刻意不导出 ``storage_state``：票据跨进程无效，落盘明文认证 cookie 只会平白
    多出一处凭据泄露面。
    """

    def __init__(self, config: WebVpnConfig, *, context_factory: Any = None) -> None:
        self.config = config
        self._context_factory = context_factory
        self._playwright: Any = None
        self.browser: Any = None
        self.context: Any = None
        self.page: Any = None

    async def __aenter__(self) -> "WebVpnSession":
        try:
            if self._context_factory is None:
                self._playwright = await _start_playwright()
                self._context_factory = _EphemeralContextFactory(self._playwright)
            else:
                self._playwright = getattr(self._context_factory, "playwright", None)
            self.browser, self.context = await await_maybe(self._context_factory.launch())
            pages = getattr(self.context, "pages", None) or []
            self.page = pages[0] if pages else await await_maybe(self.context.new_page())
            await await_maybe(self.page.goto(
                self.config.home_url, wait_until="domcontentloaded"))
            return self
        except BaseException:
            await _finish_cleanup(self.close())
            raise

    async def wait_until_ready(self, *, sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                               now: Callable[[], float] = time.monotonic) -> None:
        """轮询等待人工完成认证。

        计时用与页面无关的 sleep：``page.wait_for_timeout`` 依赖页面存活，
        使用者关闭窗口会直接打断整个进程。
        """
        deadline = now() + self.config.login_timeout_seconds
        while now() < deadline:
            if await self._is_ready():
                return
            await sleep(self.config.poll_interval_seconds)
        raise WebVpnLoginTimeout(
            f"{self.config.login_timeout_seconds:.0f} 秒内未检测到已登录的知网首页"
        )

    async def _is_ready(self) -> bool:
        try:
            title = await await_maybe(self.page.title())
        except Exception:
            return False
        return LOGIN_READY_TITLE in (title or "")

    def ensure_open(self) -> None:
        is_closed = getattr(self.page, "is_closed", None)
        if callable(is_closed) and is_closed():
            raise WebVpnWindowClosed("浏览器窗口已关闭，WebVPN 会话结束，请重新登录")

    async def close(self) -> None:
        for resource, method in (
            (self.context, "close"),
            (self.browser, "close"),
            (self._playwright, "stop"),
        ):
            if resource is not None:
                with contextlib.suppress(Exception, asyncio.CancelledError):
                    await await_maybe(getattr(resource, method)())
        self.page = self.context = self.browser = self._playwright = None

    async def __aexit__(self, *_exc: object) -> None:
        await asyncio.shield(self.close())


async def wait_for_professional_page(
    context: Any, *, timeout_seconds: float = 900.0, poll_seconds: float = 2.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    now: Callable[[], float] = time.monotonic,
) -> Any:
    """等待使用者手工导航到专业检索页，返回该页面。

    这是人工值守模式的交接点，也是比自动导航更稳的做法：站点在「首页 →
    高级检索 → 专业检索」这条路径上会开中转标签页、异步渲染标签、并对
    深链施加风控，程序化走这条路既脆弱又容易招来安全验证；而使用者本人
    点几下是可靠的。程序从"表达式框已经可见"这一刻起接管。

    判据是表达式框可见，而不是标题或地址——只有它可见才说明确实停在
    专业检索标签上，高级检索标签下它是隐藏的。
    """
    deadline = now() + timeout_seconds
    while now() < deadline:
        for page in list(getattr(context, "pages", []) or []):
            is_closed = getattr(page, "is_closed", None)
            if callable(is_closed) and is_closed():
                continue
            with contextlib.suppress(Exception):
                box = page.locator(EXPRESSION_BOX_SELECTOR)
                if await await_maybe(box.count()) and await await_maybe(box.first.is_visible()):
                    return page
        await sleep(poll_seconds)
    raise WebVpnLoginTimeout(
        f"{timeout_seconds:.0f} 秒内未检测到已打开的专业检索页面"
        "（需停在「高级检索 → 专业检索」标签，且表达式框可见）"
    )


class ProfessionalSearchPage:
    """驱动「高级检索 → 专业检索」页面提交一条表达式。

    每一步的定位方式都来自实测，不是猜测；偏离任何一条都会以难以归因的方式失败。
    """

    def __init__(self, page: Any) -> None:
        self.page = page

    async def open_from_home(
        self,
        context: Any,
        *,
        timeout_seconds: float = 20.0,
        preserve_home: bool = False,
    ) -> Any:
        """从知网首页点进高级检索。**不要改成直接 goto 高级检索地址。**

        高级检索通常在新标签页打开，且新页面需要时间加载。固定 sleep 是在赌
        网络速度：慢一点就会在 DOM 尚未就绪时去找标签，报出"未找到专业检索"
        这种指向完全错误的错误。这里改为轮询等待新标签页出现并完成加载。

        ``preserve_home`` 用于批次运行时：先在同一浏览器上下文创建批次自有页面，
        打开当前首页地址，再从该页点击高级检索。这样即使站点改为同页跳转，
        保留首页也不会被覆盖。方法只把返回页的所有权交给调用方；识别失败时，
        本次点击产生的所有页面均在抛出异常前关闭。
        """
        retained_home = self.page
        baseline = list(getattr(context, "pages", []) or [])
        owned: list[Any] = []
        popup_listener_pages: list[Any] = []
        popup_cleanup_deadline: float | None = None
        popup_close_tasks: set[asyncio.Task[Any]] = set()
        popup_closing_pages: list[Any] = []
        click_cleanup_task: asyncio.Task[Any] | None = None
        click_cleanup_deadline: float | None = None
        has_popup_boundary = False

        def schedule_popup_close(page: Any) -> None:
            if popup_cleanup_deadline is None:
                return
            if asyncio.get_running_loop().time() >= popup_cleanup_deadline:
                return
            if any(page is closing for closing in popup_closing_pages):
                return
            is_closed = getattr(page, "is_closed", None)
            if callable(is_closed) and is_closed():
                return
            popup_closing_pages.append(page)
            close_task = asyncio.create_task(self._close_pages([page]))
            popup_close_tasks.add(close_task)

            def consume_close_result(task: asyncio.Task[Any]) -> None:
                popup_close_tasks.discard(task)
                for index, closing in enumerate(popup_closing_pages):
                    if closing is page:
                        popup_closing_pages.pop(index)
                        break
                self._consume_task_result(task)

            close_task.add_done_callback(consume_close_result)

        def own_popup(page: Any) -> None:
            if all(page is not existing for existing in owned):
                owned.append(page)
            listen_for_popups(page)
            schedule_popup_close(page)

        def listen_for_popups(page: Any) -> bool:
            on = getattr(page, "on", None)
            if not callable(on):
                return False
            if any(page is existing for existing in popup_listener_pages):
                return True
            on("popup", own_popup)
            popup_listener_pages.append(page)
            return True

        def stop_listening_for_popups() -> None:
            for page in popup_listener_pages:
                remove = getattr(page, "remove_listener", None)
                if callable(remove):
                    with contextlib.suppress(Exception):
                        remove("popup", own_popup)
            popup_listener_pages.clear()

        def own_context_delta() -> None:
            for page in list(getattr(context, "pages", []) or []):
                if (
                    all(page is not existing for existing in baseline)
                    and all(page is not existing for existing in owned)
                ):
                    owned.append(page)

        async def close_owned_pages_until_stable() -> None:
            while True:
                pending = [
                    page
                    for page in owned
                    if not (
                        callable(getattr(page, "is_closed", None))
                        and page.is_closed()
                    )
                ]
                if pending:
                    await self._close_pages(pending)
                    continue
                await asyncio.sleep(0)
                if all(
                    callable(getattr(page, "is_closed", None))
                    and page.is_closed()
                    for page in owned
                ):
                    return

        async def close_cancelled_click_until(deadline: float) -> None:
            nonlocal popup_cleanup_deadline
            popup_cleanup_deadline = deadline
            for page in list(owned):
                schedule_popup_close(page)
            try:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining > 0:
                    await asyncio.sleep(remaining)
            finally:
                popup_cleanup_deadline = None
                if click_cleanup_task is not None and not click_cleanup_task.done():
                    click_cleanup_task.cancel()
                for close_task in list(popup_close_tasks):
                    if not close_task.done():
                        close_task.cancel()

        try:
            if preserve_home:
                creation_task = asyncio.create_task(
                    await_maybe(context.new_page())
                )
                try:
                    origin = await asyncio.shield(creation_task)
                except asyncio.CancelledError:
                    _clear_current_cancellation()
                    completed, _repeat_cancel = await _wait_task_bounded(
                        creation_task,
                        PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS,
                        cancel_on_timeout=True,
                    )
                    if completed and not creation_task.cancelled():
                        with contextlib.suppress(BaseException):
                            owned.append(creation_task.result())
                    else:
                        creation_task.add_done_callback(
                            self._close_page_created_after_cancellation
                        )
                    own_context_delta()
                    raise
                owned.append(origin)
                home_url = str(getattr(retained_home, "url", "") or "")
                if not home_url:
                    raise WebVpnNavigationError("知网首页地址不可用，无法建立批次页面")
                await await_maybe(
                    origin.goto(home_url, wait_until="domcontentloaded")
                )
                self.page = origin
            else:
                origin = retained_home

            has_popup_boundary = listen_for_popups(origin)
            link = self.page.get_by_role("link", name=ADV_SEARCH_LINK_TEXT)
            if await await_maybe(link.count()) < 1:
                raise WebVpnNavigationError("知网首页未找到「高级检索」入口")
            click_task = asyncio.create_task(await_maybe(link.first.click()))
            try:
                await asyncio.shield(click_task)
            except asyncio.CancelledError:
                _clear_current_cancellation()
                click_cleanup_deadline = (
                    asyncio.get_running_loop().time()
                    + PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS
                )
                click_cleanup_task = click_task
                click_task.add_done_callback(self._consume_task_result)
                click_task.cancel()
                if not has_popup_boundary:
                    own_context_delta()
                raise

            # 不能认"第一个新出现的标签页"：站点会短暂开一个中转标签页再关掉，
            # 抓到它就会让驱动指向已关闭页面。只检查本次批次拥有的页面。
            deadline = time.monotonic() + timeout_seconds
            while True:
                if not has_popup_boundary:
                    own_context_delta()
                candidates = [origin, *owned]
                found = await self._locate_advanced_search_page(candidates)
                if found is not None:
                    self.page = found
                    stop_listening_for_popups()
                    completed, cancellation = await _finish_cleanup_bounded(
                        self._close_pages(
                            page for page in owned if page is not found
                        ),
                        PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS,
                    )
                    if cancellation is not None:
                        raise cancellation
                    if not completed:
                        raise WebVpnNavigationError(
                            "批次页面清理超时，已停止本次检索"
                        )
                    return self.page
                if time.monotonic() >= deadline:
                    raise WebVpnNavigationError(
                        "点击「高级检索」后未出现可用的高级检索页面；"
                        "站点可能改版，或中转标签页被关闭"
                    )
                await asyncio.sleep(1)
        except BaseException as exc:
            initial_cancellation = (
                exc if isinstance(exc, asyncio.CancelledError) else None
            )
            if initial_cancellation is not None:
                _clear_current_cancellation()
            try:
                if click_cleanup_deadline is None:
                    _completed, cleanup_cancellation = (
                        await _finish_cleanup_bounded(
                            close_owned_pages_until_stable(),
                            PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS,
                        )
                    )
                else:
                    _completed, cleanup_cancellation = (
                        await _finish_cleanup_until(
                            close_cancelled_click_until(
                                click_cleanup_deadline
                            ),
                            click_cleanup_deadline,
                        )
                    )
            finally:
                stop_listening_for_popups()
            self.page = retained_home
            if cleanup_cancellation is not None:
                raise cleanup_cancellation
            if initial_cancellation is not None:
                raise initial_cancellation
            raise

    async def _locate_advanced_search_page(
        self, candidates: Sequence[Any]
    ) -> Any | None:
        for page in candidates:
            is_closed = getattr(page, "is_closed", None)
            if callable(is_closed) and is_closed():
                continue                       # 跳过已关闭的中转页
            with contextlib.suppress(Exception):
                if await await_maybe(page.locator(EXPRESSION_BOX_SELECTOR).count()):
                    return page                # 表达式框存在即已在高级检索页
                title = await await_maybe(page.title())
                if ADV_SEARCH_LINK_TEXT in (title or ""):
                    return page
        return None

    @staticmethod
    async def _close_pages(pages: Iterable[Any]) -> None:
        for page in list(pages):
            is_closed = getattr(page, "is_closed", None)
            if callable(is_closed) and is_closed():
                continue
            with contextlib.suppress(Exception):
                await await_maybe(page.close())

    @staticmethod
    def _close_page_created_after_cancellation(
        creation_task: asyncio.Task[Any],
    ) -> None:
        if creation_task.cancelled():
            return
        try:
            page = creation_task.result()
        except BaseException:
            return
        cleanup_task = asyncio.create_task(
            _finish_cleanup_bounded(
                ProfessionalSearchPage._close_pages([page]),
                PAGE_OWNERSHIP_CLEANUP_TIMEOUT_SECONDS,
            )
        )
        cleanup_task.add_done_callback(
            ProfessionalSearchPage._consume_task_result
        )

    @staticmethod
    def _consume_task_result(task: asyncio.Task[Any]) -> None:
        with contextlib.suppress(BaseException):
            task.result()

    async def switch_to_professional(self, *, timeout_seconds: float = 20.0) -> None:
        """切到「专业检索」标签。

        非活动标签被 CSS 隐藏，只能用 JS 触发 click；页面为前端渲染，标签可能
        晚于 domcontentloaded 才出现，因此轮询而不是一次定成败。
        """
        deadline = time.monotonic() + timeout_seconds
        while True:
            switched = await await_maybe(
                self.page.evaluate(PROFESSIONAL_TAB_CLICK_JS, PROFESSIONAL_TAB_TEXT)
            )
            if switched:
                break
            if time.monotonic() >= deadline:
                raise WebVpnNavigationError("高级检索页未找到「专业检索」标签")
            await asyncio.sleep(1)
        # 切换后表达式框才会变为可见，等它真正出现再返回
        box_deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < box_deadline:
            await asyncio.sleep(1)
            with contextlib.suppress(Exception):
                if await await_maybe(self.page.locator(EXPRESSION_BOX_SELECTOR).count()):
                    return

    async def fill_expression(self, expression: str) -> None:
        box = self.page.locator(EXPRESSION_BOX_SELECTOR)
        if await await_maybe(box.count()) != 1:
            raise WebVpnNavigationError("未找到专业检索表达式输入框")
        await await_maybe(box.fill(""))
        await await_maybe(box.fill(expression))
        accepted = await await_maybe(box.input_value())
        if len(accepted or "") != len(expression):
            # 半截表达式照样能提交，返回的却是完全不同的检索范围。宁可中止。
            raise ExpressionTruncated(
                f"表达式被截断：提交 {len(expression)} 字符，输入框只接受 "
                f"{len(accepted or '')} 字符"
            )

    async def submit(self) -> None:
        button = await self._visible_search_button()
        if button is None:
            raise WebVpnNavigationError("专业检索页未找到可见的检索按钮")
        await await_maybe(button.click())

    async def _visible_search_button(self) -> Any | None:
        """在候选里挑第一个真正可见可点的按钮。

        隐藏的同名按钮点不动，Playwright 会重试到超时才报错，而错误信息只说
        "元素不可见"，不会提示"你选错了按钮"。
        """
        for selector in SEARCH_BUTTON_SELECTORS:
            locator = self.page.locator(selector)
            with contextlib.suppress(Exception):
                total = await await_maybe(locator.count())
                for index in range(min(total, 8)):
                    item = locator.nth(index)
                    with contextlib.suppress(Exception):
                        if await await_maybe(item.is_visible()) and \
                                await await_maybe(item.is_enabled()):
                            return item
        return None

    async def set_page_size(self, size: int = MAX_RESULTS_PER_PAGE, *,
                            timeout_seconds: float = 20.0) -> int:
        """把结果页每页条数切到指定档位，返回实际渲染的行数。

        档位是自定义下拉（``div.page-show-count`` 内的 ``li[data-val]``），列表
        默认 ``display:none``，因此先点开再选。实测档位只有 10/20/50。

        不设置就只有 20 行——若上层按 50 取数却没切档，就会把"只有 20 条"当成
        检索结果本身，而不是分页设置的产物。
        """
        before = await await_maybe(self.page.locator(RESULT_TABLE_SELECTOR + " tbody tr").count())
        picked = await await_maybe(self.page.evaluate(PAGE_SIZE_CLICK_JS, str(size)))
        if not picked:
            raise WebVpnNavigationError(
                f"结果页没有每页 {size} 条的档位；实测可选 10/20/50"
            )
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            await asyncio.sleep(1)
            rows = await await_maybe(
                self.page.locator(RESULT_TABLE_SELECTOR + " tbody tr").count())
            if rows and rows != before:
                return rows
        return await await_maybe(
            self.page.locator(RESULT_TABLE_SELECTOR + " tbody tr").count())

    async def total_results(self) -> str | None:
        with contextlib.suppress(Exception):
            return await await_maybe(self.page.evaluate(TOTAL_COUNT_JS))
        return None

    async def apply_source_category(self, name: str, *,
                                    timeout_seconds: float = 20.0) -> str | None:
        """在结果页勾选来源类别分面，返回筛选后的结果总数。

        必须先完成一次检索——分面不在高级检索输入页上，只在结果页出现。
        """
        value = SOURCE_CATEGORY_VALUES.get(name)
        if value is None:
            raise ValueError(
                f"未知的来源类别 {name!r}，可选：{sorted(SOURCE_CATEGORY_VALUES)}"
            )
        box = self.page.locator(SOURCE_CATEGORY_SELECTOR.format(value=value))
        if await await_maybe(box.count()) < 1:
            raise WebVpnNavigationError(
                f"结果页未找到「{name}」来源类别分面；需先完成一次检索"
            )
        before = await self.total_results()
        await await_maybe(box.first.check())
        # 分面是异步刷新，等总数变化而不是固定 sleep
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            await asyncio.sleep(1)
            current = await self.total_results()
            if current and current != before:
                return current
        return await self.total_results()

    async def classify_outcome(self) -> SearchStatus:
        """判定提交后的页面状态。顺序很重要：先看结果，再看拒绝，最后才看验证码。"""
        with contextlib.suppress(Exception):
            if await await_maybe(self.page.locator(RESULT_TABLE_SELECTOR).count()):
                return SearchStatus.SUCCESS
        body = ""
        with contextlib.suppress(Exception):
            body = await await_maybe(self.page.locator("body").inner_text(timeout=8_000)) or ""
        flattened = "".join(body.split())
        if "未检索到相关文献" in flattened:
            return SearchStatus.NO_RESULTS
        if all(marker in flattened for marker in NO_DATA_MARKERS):
            return SearchStatus.NO_DATA_RETRY_LATER
        with contextlib.suppress(Exception):
            if await await_maybe(self.page.evaluate(CAPTCHA_VIEWPORT_JS,
                                                    list(CAPTCHA_TEXT_MARKERS))):
                return SearchStatus.CHALLENGE_DETECTED
        return SearchStatus.PAGE_CONTRACT_CHANGED

    async def wait_for_outcome(
        self,
        timeout_seconds: float = 30,
        *,
        poll_seconds: float = 0.5,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        now: Callable[[], float] = time.monotonic,
    ) -> SearchStatus:
        """等待结果页完成渲染，临时结构未就绪不立即判为契约变化。"""
        deadline = now() + timeout_seconds
        while True:
            status = await self.classify_outcome()
            if status is not SearchStatus.PAGE_CONTRACT_CHANGED:
                return status
            if now() >= deadline:
                return status
            await sleep(poll_seconds)

    async def execute_plan(self, plan: ExpressionBatch) -> tuple[str, str, str]:
        await self.fill_expression(plan.expression)
        await self.submit()
        status = await self.wait_for_outcome()
        if status is SearchStatus.SUCCESS:
            if plan.source_category is not None:
                await self.apply_source_category(plan.source_category)
            await self.set_page_size(plan.page_size)
            status = await self.wait_for_outcome()
        html = await await_maybe(self.page.content()) if status is SearchStatus.SUCCESS else ""
        return status.value, html, str(getattr(self.page, "url", ""))


class _EphemeralContextFactory:
    def __init__(self, playwright: Any) -> None:
        self.playwright = playwright

    async def launch(self) -> tuple[Any, Any]:
        browser = None
        try:
            browser = await await_maybe(
                self.playwright.chromium.launch(headless=False)
            )
            context = await await_maybe(browser.new_context(
                locale="zh-CN",
                accept_downloads=False,
            ))
            return browser, context
        except BaseException as exc:
            if browser is not None:
                with contextlib.suppress(Exception, asyncio.CancelledError):
                    await _finish_cleanup(await_maybe(browser.close()))
            if not isinstance(exc, Exception):
                raise
            raise BrowserUnavailableError(
                "无法启动有头浏览器：WebVPN 模式需要图形界面完成人工认证"
            ) from exc


async def _start_playwright() -> Any:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise BrowserUnavailableError("缺少 Playwright，请先运行安装器") from exc
    return await async_playwright().start()
