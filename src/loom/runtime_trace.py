"""Structured correlated runtime tracing for LOOM.

Trace output is append-only JSONL. Failure to write diagnostics must never change
simulation, navigation, or campaign behavior.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import threading
import uuid

TRACE_CONTRACT = "LOOM_RUNTIME_TRACE_V1"


class RuntimeTrace:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()

    @staticmethod
    def new_trace_id(prefix: str = "tr") -> str:
        return f"{prefix}-{uuid.uuid4().hex}"

    def emit(self, event_type: str, *, trace_id: str, subsystem: str, parent_event_id: str | None = None, **fields: Any) -> dict[str, Any]:
        row = {
            "contract": TRACE_CONTRACT,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "event_id": "ev-" + uuid.uuid4().hex,
            "trace_id": trace_id,
            "parent_event_id": parent_event_id,
            "subsystem": subsystem,
            "event_type": event_type,
            **fields,
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(row, separators=(",", ":"), default=str) + "\n"
            with self._lock:
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(payload)
        except Exception:
            pass
        return row
