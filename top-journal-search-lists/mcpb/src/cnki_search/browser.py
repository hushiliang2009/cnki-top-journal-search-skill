from __future__ import annotations

import os
import shutil
import inspect
from pathlib import Path
from typing import Any


def discover_browser_executable() -> str | None:
    configured = os.environ.get("CNKI_BROWSER_PATH")
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


def _is_playwright_timeout_error(error: BaseException) -> bool:
    return any(
        item.__name__ == "TimeoutError" and item.__module__.startswith("playwright.")
        for item in type(error).__mro__
    )


class BrowserFactory:
    def __init__(self, playwright: Any, executable_path: str | None = None) -> None:
        self.playwright = playwright
        self.executable_path = executable_path

    async def launch_ephemeral(self) -> Any:
        kwargs: dict[str, Any] = {
            "headless": True,
            "args": ["--no-proxy-server", "--proxy-bypass-list=*"],
        }
        executable = self.executable_path or discover_browser_executable()
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
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise BrowserUnavailableError("缺少 Playwright，请先运行安装器") from exc
    return await async_playwright().start()
