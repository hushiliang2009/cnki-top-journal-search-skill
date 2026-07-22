from __future__ import annotations

import random
import re
import time
from pathlib import Path
from typing import Callable, Protocol, Sequence

from .models import PaperRecord


WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def safe_filename(value: str, *, fallback: str = "cnki-document", limit: int = 120) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip().rstrip(". ")
    value = re.sub(r"_+", "_", value)[:limit].rstrip(". ") or fallback
    if value.upper() in WINDOWS_RESERVED:
        value = f"_{value}"
    return value


def detect_document_format(payload: bytes) -> str:
    head = payload[:512].lstrip().lower()
    if head.startswith(b"%pdf-"):
        return "pdf"
    if b"caj" in head:
        return "caj"
    if head.startswith((b"<!doctype html", b"<html", b"<?xml")):
        return "html"
    return "unknown"


class VisibleDownloadDriver(Protocol):
    def download_selected(self, selected_index: int, target: Path) -> Path: ...


class PlaywrightDownloadDriver:
    """Download only through the official control on the current visible page."""

    def __init__(self, page: object) -> None:
        self.page = page

    def download_selected(self, selected_index: int, target: Path) -> Path:
        page = self.page
        rows = page.locator("table.result-table-list tbody tr")
        if selected_index < 1 or selected_index > rows.count():
            raise IndexError("下载序号超出当前结果页范围")
        row = rows.nth(selected_index - 1)
        with page.expect_download() as download_info:
            row.locator("td.operat a.downloadlink").first.click()
        download = download_info.value
        failure = download.failure()
        if failure:
            raise RuntimeError(f"知网下载失败：{failure}")
        download.save_as(str(target))
        return target


class DownloadRunner:
    def __init__(
        self,
        driver: VisibleDownloadDriver,
        *,
        sleeper: Callable[[float], None] = time.sleep,
        random_uniform: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self.driver = driver
        self.sleeper = sleeper
        self.random_uniform = random_uniform

    def download_selected(
        self,
        records: Sequence[PaperRecord],
        *,
        selected_indices: Sequence[int],
        output_dir: Path,
    ) -> list[Path]:
        indices = list(dict.fromkeys(selected_indices))
        if len(indices) > 5:
            raise ValueError("单次最多下载 5 篇文献")
        if any(index < 1 or index > len(records) for index in indices):
            raise IndexError("下载序号超出检索结果范围")

        output_dir.mkdir(parents=True, exist_ok=True)
        completed: list[Path] = []
        for position, index in enumerate(indices):
            record = records[index - 1]
            temporary = output_dir / f"{safe_filename(record.title)}.download"
            path = self.driver.download_selected(index, temporary)
            payload = path.read_bytes()
            document_format = detect_document_format(payload)
            if document_format in {"html", "unknown"}:
                path.unlink(missing_ok=True)
                record.download_status = f"stopped_{document_format}"
                label = "HTML" if document_format == "html" else "未知格式"
                raise RuntimeError(f"下载返回{label}，可能需要重新登录或确认权限")
            final_path = path.with_suffix(f".{document_format}")
            if final_path.exists():
                final_path = final_path.with_stem(f"{final_path.stem}_{index}")
            path.replace(final_path)
            record.download_status = "downloaded"
            completed.append(final_path)
            if position < len(indices) - 1:
                self.sleeper(self.random_uniform(8.0, 15.0))
        return completed
