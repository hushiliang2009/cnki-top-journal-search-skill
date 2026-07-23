from __future__ import annotations

import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from cnki_search.browser import discover_browser_executable
from cnki_search.session import PublicCnkiSession, classify_public_search_state


def main() -> None:
    with PublicCnkiSession() as session:
        snapshot = session.search("public session API smoke")
        print(
            json.dumps(
                {
                    "browser": discover_browser_executable(),
                    "page_status": classify_public_search_state(**snapshot.state_arguments()).value,
                    "url": snapshot.url,
                    "title": snapshot.title,
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
