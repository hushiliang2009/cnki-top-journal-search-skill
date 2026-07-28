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
import json
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .browser import BrowserUnavailableError, await_maybe
from .models import SearchStatus
from .professional import ExpressionBatch

#: 实测：连续 4 次快速请求即触发安全验证，冷却约 75 秒后恢复。30 秒是据此取的
#: 保守值，**不是**二分测试得出的安全阈值，长时间高频使用仍可能触发风控。
MIN_REQUEST_INTERVAL_SECONDS = 30.0
#: 命中风控后在常规间隔之外额外等待，避免把账号推向更严的限制。
CHALLENGE_BACKOFF_SECONDS = 180.0
#: 同一批次因风控最多重试几次；超过则如实上报未完成，交由使用者决定。
MAX_CHALLENGE_RETRIES = 3

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
SEARCH_BUTTON_SELECTOR = "input.search-btn"
RESULT_TABLE_SELECTOR = "table.result-table-list"


class ExpressionTruncated(RuntimeError):
    """输入框接受的字符数少于提交的表达式，继续提交会得到错误的检索范围。"""


class WebVpnNavigationError(RuntimeError):
    """页面结构与实测契约不符，重试无意义。"""


class WebVpnLoginTimeout(RuntimeError):
    """在允许的时间内没有检测到已登录的知网首页。"""


class WebVpnWindowClosed(RuntimeError):
    """浏览器窗口被关闭，会话无法继续。关窗等同于登出。"""


@dataclass(frozen=True, slots=True)
class WebVpnConfig:
    """WebVPN 入口配置。

    ``home_url`` 是学校 WebVPN 改写后的知网首页地址。WebVPN 对每个后端主机的
    编码不同（首页与结果页的编码主机并不一致），因此只固定首页入口，后续跳转
    交给站点自身处理，不对结果页 URL 做等值断言。
    """

    home_url: str
    profile_dir: Path
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
             stopped_at: ExpressionBatch | None = None) -> dict[str, Any]:
    if stopped_at is not None and checkpoint is not None:
        checkpoint.save(token)
    return {
        "batches_completed": len(results),
        "batches_total": len(batches),
        "complete": stopped_at is None,
        "stopped_at_batch": stopped_at.index if stopped_at is not None else None,
        "human_intervention_required": human_intervention_required,
        "results": results,
    }


class WebVpnSession:
    """有头浏览器 + 持久化 profile，用于承载人工登录并复用同一进程完成检索。

    刻意不导出 ``storage_state``：票据跨进程无效，落盘明文认证 cookie 只会平白
    多出一处凭据泄露面。
    """

    def __init__(self, config: WebVpnConfig, *, context_factory: Any = None) -> None:
        self.config = config
        self._context_factory = context_factory
        self._playwright: Any = None
        self.context: Any = None
        self.page: Any = None

    async def __aenter__(self) -> "WebVpnSession":
        if self._context_factory is None:
            self._playwright = await _start_playwright()
            self._context_factory = _PersistentContextFactory(self._playwright, self.config)
        self.context = await await_maybe(self._context_factory.launch())
        pages = getattr(self.context, "pages", None) or []
        self.page = pages[0] if pages else await await_maybe(self.context.new_page())
        await await_maybe(self.page.goto(self.config.home_url, wait_until="domcontentloaded"))
        return self

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

    async def __aexit__(self, *_exc: object) -> None:
        for resource, method in ((self.context, "close"), (self._playwright, "stop")):
            if resource is not None:
                try:
                    await await_maybe(getattr(resource, method)())
                except Exception:
                    pass
        self.context = self.page = self._playwright = None


class ProfessionalSearchPage:
    """驱动「高级检索 → 专业检索」页面提交一条表达式。

    每一步的定位方式都来自实测，不是猜测；偏离任何一条都会以难以归因的方式失败。
    """

    def __init__(self, page: Any) -> None:
        self.page = page

    async def open_from_home(self, context: Any) -> Any:
        """从知网首页点进高级检索。**不要改成直接 goto 高级检索地址。**"""
        before = set(getattr(context, "pages", []) or [])
        link = self.page.get_by_role("link", name=ADV_SEARCH_LINK_TEXT)
        if await await_maybe(link.count()) < 1:
            raise WebVpnNavigationError("知网首页未找到「高级检索」入口")
        await await_maybe(link.first.click())
        await asyncio.sleep(3)
        fresh = [item for item in (getattr(context, "pages", []) or []) if item not in before]
        self.page = fresh[0] if fresh else self.page      # 通常在新标签页打开
        return self.page

    async def switch_to_professional(self) -> None:
        switched = await await_maybe(
            self.page.evaluate(PROFESSIONAL_TAB_CLICK_JS, PROFESSIONAL_TAB_TEXT)
        )
        if not switched:
            raise WebVpnNavigationError("高级检索页未找到「专业检索」标签")
        await asyncio.sleep(2)

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
        button = self.page.locator(SEARCH_BUTTON_SELECTOR)
        if await await_maybe(button.count()) < 1:
            raise WebVpnNavigationError("专业检索页未找到检索按钮")
        await await_maybe(button.first.click())


class _PersistentContextFactory:
    def __init__(self, playwright: Any, config: WebVpnConfig) -> None:
        self.playwright = playwright
        self.config = config

    async def launch(self) -> Any:
        self.config.profile_dir.mkdir(parents=True, exist_ok=True)
        try:
            return await await_maybe(self.playwright.chromium.launch_persistent_context(
                str(self.config.profile_dir),
                headless=False,          # 人工登录与滑动验证都需要可见窗口
                locale="zh-CN",
                accept_downloads=False,
            ))
        except Exception as exc:
            raise BrowserUnavailableError(
                "无法启动有头浏览器：WebVPN 模式需要图形界面完成人工认证"
            ) from exc


async def _start_playwright() -> Any:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise BrowserUnavailableError("缺少 Playwright，请先运行安装器") from exc
    return await async_playwright().start()
