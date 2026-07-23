from __future__ import annotations

import os
import shutil
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


class BrowserFactory:
    def __init__(self, playwright: Any, executable_path: str | None = None) -> None:
        self.playwright = playwright
        self.executable_path = executable_path

    def launch_ephemeral(self) -> Any:
        kwargs: dict[str, Any] = {
            "headless": True,
        }
        executable = self.executable_path or discover_browser_executable()
        if executable:
            kwargs["executable_path"] = executable
        return self.playwright.chromium.launch(**kwargs)


def start_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("缺少 Playwright，请先运行安装器") from exc
    return sync_playwright().start()

