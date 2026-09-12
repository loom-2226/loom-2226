#!/usr/bin/env python3
from __future__ import annotations

"""Append-only audit trail for OpenAI-key-backed LOOM development calls.

Development evidence only. Records the exact request payload and provider
response/error for each API call, plus timing and a hash chain. It MUST NOT
record the API key or Authorization header.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "LOOM_OPENAI_DEV_AUDIT_V1"


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _credential_fingerprint(key: str) -> str:
    # Correlation only: identifies whether two audited calls used the same
    # credential without persisting any recoverable part of the raw key.
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


class OpenAIDevAudit:
    def __init__(self, path: Path, key: str, *, endpoint: str) -> None:
        self.path = path
        self.endpoint = endpoint
        self.session_id = uuid.uuid4().hex
        self.credential_fingerprint = _credential_fingerprint(key)
        self.sequence = 0
        self.previous_hash = self._read_previous_hash()

    def _read_previous_hash(self) -> str | None:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return None
        last_nonempty = None
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last_nonempty = line
        if last_nonempty is None:
            return None
        try:
            record = json.loads(last_nonempty)
            value = record.get("entry_sha256")
            return str(value) if value else None
        except Exception as exc:
            raise RuntimeError(f"audit trail ends with invalid JSON: {self.path}: {exc}") from exc

    def append(
        self,
        *,
        stage: str,
        request_payload: dict[str, Any],
        response_payload: Any = None,
        error: Any = None,
        http_status: int | None = None,
        latency_s: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.sequence += 1
        record: dict[str, Any] = {
            "schema": SCHEMA,
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "session_id": self.session_id,
            "sequence": self.sequence,
            "provider": "OpenAI",
            "endpoint": self.endpoint,
            "credential_source": "OPENAI_API_KEY",
            "credential_fingerprint_sha256_16": self.credential_fingerprint,
            "stage": stage,
            "request_payload": request_payload,
            "response_payload": response_payload,
            "error": error,
            "http_status": http_status,
            "latency_s": round(latency_s, 6) if latency_s is not None else None,
            "metadata": metadata or {},
            "previous_entry_sha256": self.previous_hash,
        }
        record_hash = hashlib.sha256(_canonical_bytes(record)).hexdigest()
        record["entry_sha256"] = record_hash
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous_hash = record_hash
        return record_hash
