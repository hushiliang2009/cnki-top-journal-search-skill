from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "secret",
    "storage_state",
    "token",
}


def _reject_sensitive(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in _SENSITIVE_KEYS:
                raise ValueError(f"缓存包含敏感字段: {key}")
            _reject_sensitive(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive(child)


class MetadataCache:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("缓存根节点必须是对象")
        return data

    def put(self, key: str, value: dict[str, Any]) -> None:
        _reject_sensitive(value)
        data = self._load()
        data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def get(self, key: str) -> dict[str, Any] | None:
        value = self._load().get(key)
        return value if isinstance(value, dict) else None

