from __future__ import annotations

import asyncio
import inspect
import os
import signal
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable


PLAYWRIGHT_BROWSER_INSTALL_TIMEOUT_SECONDS = 600.0
PROCESS_TERMINATION_TIMEOUT_SECONDS = 5.0


def configure_playwright_browsers_path() -> Path:
    configured = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if configured:
        return Path(configured)
    private_cache = Path(sys.prefix) / "playwright-browsers"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(private_cache)
    return private_cache


def discover_browser_executable() -> str | None:
    configured = os.environ.get("CNKI_ENV_BROWSER_PATH")
    if configured and Path(configured).is_file():
        return configured
    for command in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(command)
        if found:
            return found
    if os.name == "nt":
        roots = [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")]
        relatives = [
            "Google/Chrome/Application/chrome.exe",
            "Microsoft/Edge/Application/msedge.exe",
            "Chromium/Application/chrome.exe",
        ]
        for root in filter(None, roots):
            for relative in relatives:
                candidate = Path(root) / relative
                if candidate.is_file():
                    return str(candidate)
    return None


BROWSER_INSTALL_HINT = (
    "浏览器不可用：请在 MCP 运行环境中执行 "
    "python -m playwright install chromium chromium-headless-shell"
)


class BrowserUnavailableError(RuntimeError):
    """本机没有可用浏览器，重试无意义，需人工安装。"""


async def _terminate_process(process: Any) -> None:
    if process.returncode is not None:
        return
    try:
        if os.name == "nt":
            tree_killer = await asyncio.create_subprocess_exec(
                "taskkill.exe",
                "/PID",
                str(process.pid),
                "/T",
                "/F",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await tree_killer.communicate()
        else:
            getattr(os, "killpg")(process.pid, signal.SIGTERM)
    except (OSError, ProcessLookupError):
        try:
            process.terminate()
        except ProcessLookupError:
            return
    try:
        await asyncio.wait_for(
            process.wait(), timeout=PROCESS_TERMINATION_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        if os.name == "nt":
            process.kill()
        else:
            try:
                getattr(os, "killpg")(
                    process.pid, getattr(signal, "SIGKILL", signal.SIGTERM),
                )
            except ProcessLookupError:
                pass
        await process.wait()


async def _install_playwright_browser_runtime(
    timeout_seconds: float = PLAYWRIGHT_BROWSER_INSTALL_TIMEOUT_SECONDS,
) -> None:
    configure_playwright_browsers_path()
    process_options: dict[str, Any]
    if os.name == "nt":
        process_options = {
            "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP"),
        }
    else:
        process_options = {"start_new_session": True}
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "playwright",
        "install",
        "chromium",
        "chromium-headless-shell",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        **process_options,
    )
    try:
        _stdout, _stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout_seconds,
        )
    except asyncio.CancelledError:
        await _terminate_process(process)
        raise
    except asyncio.TimeoutError as exc:
        await _terminate_process(process)
        raise BrowserUnavailableError(BROWSER_INSTALL_HINT) from exc
    if process.returncode != 0:
        raise BrowserUnavailableError(BROWSER_INSTALL_HINT)


def _is_playwright_timeout_error(error: BaseException) -> bool:
    return any(
        item.__name__ == "TimeoutError" and item.__module__.startswith("playwright.")
        for item in type(error).__mro__
    )


class BrowserFactory:
    def __init__(
        self,
        playwright: Any,
        executable_path: str | None = None,
        browser_installer: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        self.playwright = playwright
        self.executable_path = executable_path
        self.browser_installer = browser_installer or _install_playwright_browser_runtime

    async def ensure_runtime(self) -> str | None:
        executable = self.executable_path or discover_browser_executable()
        if not executable:
            bundled = getattr(self.playwright.chromium, "executable_path", None)
            if bundled and not Path(bundled).is_file():
                try:
                    await self.browser_installer()
                except BrowserUnavailableError:
                    raise
                except Exception as exc:
                    raise BrowserUnavailableError(BROWSER_INSTALL_HINT) from exc
        return executable

    async def launch_ephemeral(self) -> Any:
        kwargs: dict[str, Any] = {
            "headless": True,
            "args": ["--no-proxy-server", "--proxy-bypass-list=*"],
        }
        executable = await self.ensure_runtime()
        if executable:
            kwargs["executable_path"] = executable
        try:
            return await await_maybe(self.playwright.chromium.launch(**kwargs))
        except Exception as exc:
            # playwright 的启动失败异常不是 OSError 子类，不转换就会以原始
            # traceback 穿透 MCP 工具边界。超时另有可重试路径，此处放行。
            if _is_playwright_timeout_error(exc):
                raise
            raise BrowserUnavailableError(BROWSER_INSTALL_HINT) from exc


async def await_maybe(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


async def start_playwright() -> Any:
    configure_playwright_browsers_path()
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise BrowserUnavailableError("缺少 Playwright，请先运行安装器") from exc
    return await async_playwright().start()


async def prepare_browser_runtime() -> None:
    if discover_browser_executable():
        return
    playwright = await start_playwright()
    try:
        await BrowserFactory(playwright).ensure_runtime()
    finally:
        await await_maybe(playwright.stop())
