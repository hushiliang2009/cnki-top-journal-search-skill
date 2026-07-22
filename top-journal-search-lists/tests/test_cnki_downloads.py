from pathlib import Path

import pytest

from cnki_search.downloads import (
    DownloadRunner,
    PlaywrightDownloadDriver,
    detect_document_format,
    safe_filename,
)
from cnki_search.models import PaperRecord


class FakeDownloadDriver:
    def __init__(self, payload: bytes = b"%PDF-1.7 test") -> None:
        self.payload = payload
        self.visited: list[str] = []
        self.clicked = 0

    def download_selected(self, selected_index: int, target: Path) -> Path:
        self.visited.append(str(selected_index))
        self.clicked += 1
        target.write_bytes(self.payload)
        return target


class RecordingDownloadDriver(FakeDownloadDriver):
    def __init__(self, events: list[str], payload: bytes = b"%PDF-1.7 test") -> None:
        super().__init__(payload)
        self.events = events

    def download_selected(self, selected_index: int, target: Path) -> Path:
        self.events.append(f"download:{selected_index}")
        return super().download_selected(selected_index, target)


def _record(index: int) -> PaperRecord:
    return PaperRecord(title=f"论文/{index}:测试", detail_url=f"https://kns.cnki.net/detail/{index}")


def test_safe_filename_removes_cross_platform_reserved_characters() -> None:
    assert safe_filename('A/B:C*D?E"F<G>H|I.') == "A_B_C_D_E_F_G_H_I"
    assert safe_filename("CON") == "_CON"


@pytest.mark.parametrize(
    ("payload", "expected"),
    [(b"%PDF-1.7", "pdf"), (b"CAJViewer", "caj"), (b"<!DOCTYPE html>", "html")],
)
def test_detect_document_format(payload: bytes, expected: str) -> None:
    assert detect_document_format(payload) == expected


def test_download_runner_is_serial_and_selected_only(skill_root: Path) -> None:
    driver = FakeDownloadDriver()
    target = skill_root / "tests" / "_download_test"
    target.mkdir(exist_ok=True)
    try:
        records = [_record(1), _record(2), _record(3)]
        output = DownloadRunner(driver, sleeper=lambda _: None).download_selected(
            records, selected_indices=[1, 3], output_dir=target
        )
        assert len(output) == 2
        assert driver.clicked == 2
        assert driver.visited == ["1", "3"]
        assert all(item.download_status == "downloaded" for item in (records[0], records[2]))
        assert records[1].download_status == "not_requested"
    finally:
        for path in target.iterdir():
            path.unlink()
        target.rmdir()


def test_each_download_waits_before_click(skill_root: Path) -> None:
    events: list[str] = []
    driver = RecordingDownloadDriver(events)
    runner = DownloadRunner(
        driver,
        sleeper=lambda seconds: events.append(f"wait:{seconds}"),
        random_uniform=lambda low, high: 9.0,
    )

    target = skill_root / "tests" / "_download_wait_test"
    target.mkdir(exist_ok=True)
    try:
        runner.download_selected(
            [_record(1), _record(2)], selected_indices=[1, 2], output_dir=target
        )

        assert events == ["wait:9.0", "download:1", "wait:9.0", "download:2"]
    finally:
        for path in target.iterdir():
            path.unlink()
        target.rmdir()


def test_download_runner_rejects_more_than_five() -> None:
    with pytest.raises(ValueError, match="5"):
        DownloadRunner(FakeDownloadDriver(), sleeper=lambda _: None).download_selected(
            [_record(i) for i in range(1, 7)],
            selected_indices=[1, 2, 3, 4, 5, 6],
            output_dir=Path("unused"),
        )


def test_html_download_is_stopped_and_removed(skill_root: Path) -> None:
    driver = FakeDownloadDriver(b"<html>login required</html>")
    target = skill_root / "tests" / "_download_html_test"
    target.mkdir(exist_ok=True)
    try:
        with pytest.raises(RuntimeError, match="HTML"):
            DownloadRunner(driver, sleeper=lambda _: None).download_selected(
                [_record(1)], selected_indices=[1], output_dir=target
            )
        assert list(target.iterdir()) == []
    finally:
        target.rmdir()


class FakeBrowserDownload:
    def failure(self):
        return None

    def save_as(self, target: str) -> None:
        Path(target).write_bytes(b"%PDF-1.7")


class FakeDownloadInfo:
    value = FakeBrowserDownload()


class FakeExpectDownload:
    def __enter__(self):
        return FakeDownloadInfo()

    def __exit__(self, *_args) -> None:
        return None


class FakeOfficialLink:
    def __init__(self, actions: list[tuple]) -> None:
        self.actions = actions

    @property
    def first(self):
        return self

    def click(self) -> None:
        self.actions.append(("click", "official_download"))


class FakeDownloadRow:
    def __init__(self, actions: list[tuple], index: int) -> None:
        self.actions = actions
        self.index = index

    def locator(self, selector: str) -> FakeOfficialLink:
        self.actions.append(("locator", self.index, selector))
        return FakeOfficialLink(self.actions)


class FakeDownloadRows:
    def __init__(self, actions: list[tuple]) -> None:
        self.actions = actions

    def count(self) -> int:
        return 3

    def nth(self, index: int) -> FakeDownloadRow:
        return FakeDownloadRow(self.actions, index)


class FakeResultDownloadPage:
    def __init__(self) -> None:
        self.actions: list[tuple] = []

    def locator(self, selector: str) -> FakeDownloadRows:
        self.actions.append(("locator", selector))
        return FakeDownloadRows(self.actions)

    def expect_download(self) -> FakeExpectDownload:
        return FakeExpectDownload()

    def goto(self, _url: str) -> None:
        raise AssertionError("下载必须从当前结果行点击知网官方控件")


def test_playwright_download_clicks_official_selected_row_without_goto(skill_root: Path) -> None:
    page = FakeResultDownloadPage()
    target = skill_root / "tests" / "_official_download_test.download"
    try:
        output = PlaywrightDownloadDriver(page).download_selected(2, target)
        assert output == target
        assert ("locator", 1, "td.operat a.downloadlink") in page.actions
        assert ("click", "official_download") in page.actions
    finally:
        target.unlink(missing_ok=True)
