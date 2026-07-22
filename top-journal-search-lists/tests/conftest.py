from pathlib import Path
import sys

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
