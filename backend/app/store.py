import json
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.config import get_settings
from backend.app.synthetic import write_data


class DataStore:
    def __init__(self, path: str | None = None):
        self.path = Path(path or get_settings().data_path)
        self._lock = Lock()
        if not self.path.exists():
            write_data(self.path)
        self.data: dict[str, list[dict[str, Any]]] = json.loads(self.path.read_text(encoding="utf-8"))

    def all(self, collection: str) -> list[dict[str, Any]]:
        return list(self.data.get(collection, []))

    def find(self, collection: str, key: str, value: Any) -> dict[str, Any] | None:
        return next((item for item in self.data.get(collection, []) if item.get(key) == value), None)

    def filter(self, collection: str, **criteria: Any) -> list[dict[str, Any]]:
        return [item for item in self.data.get(collection, []) if all(item.get(k) == v for k, v in criteria.items())]

    def append_audit(self, record: dict[str, Any]) -> None:
        with self._lock:
            self.data.setdefault("audit_log", []).append(record)


store = DataStore()
