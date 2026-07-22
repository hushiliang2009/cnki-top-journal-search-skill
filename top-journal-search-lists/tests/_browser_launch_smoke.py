from __future__ import annotations

import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from cnki_search.browser import discover_browser_executable
from cnki_search.session import CnkiSession


def main() -> None:
    session = CnkiSession()
    try:
        login_status = session.login()
        current_status = session.status()
        print(
            json.dumps(
                {
                    "browser": discover_browser_executable(),
                    "login_call": login_status.value,
                    "page_status": current_status.value,
                    "url": session.page.url,
                    "title": session.page.title(),
                },
                ensure_ascii=False,
            )
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
