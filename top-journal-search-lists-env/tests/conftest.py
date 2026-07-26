from collections.abc import Generator
from pathlib import Path
import shutil
import sys
import uuid

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def fixtures() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def tmp_path() -> Generator[Path]:
    base = Path(__file__).resolve().parents[2] / ".pytest-runtime"
    path = base / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
