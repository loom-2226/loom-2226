"""Non-authoritative SQLite shadow ledger for campaign transitions.

JSON state and the RC6.1 history ledger remain canonical authority. This module
mirrors only successfully committed campaign transitions for diagnostics,
reconciliation, and later migration work.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping
import json
import sqlite3

SHADOW_LEDGER_CONTRACT = "LOOM_CAMPAIGN_SQL_SHADOW_V1"
SHADOW_DB_NAME = "LOOM_CAMPAIGN_DEV.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS campaign_shadow_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS campaign_flight_commits (
    flight_id TEXT PRIMARY KEY,
    revision_before INTEGER NOT NULL,
    revision_after INTEGER NOT NULL,
    state_before_id TEXT,
    state_after_id TEXT,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_epoch_utc TEXT NOT NULL,
    arrival_epoch_utc TEXT NOT NULL,
    remass_before_t REAL NOT NULL,
    remass_after_t REAL NOT NULL,
    history_record_number INTEGER NOT NULL,
    history_record_sha256 TEXT NOT NULL,
    state_path TEXT NOT NULL,
    history_path TEXT NOT NULL,
    final_state_json TEXT NOT NULL,
    canonical_commit_json TEXT NOT NULL,
    UNIQUE(revision_after),
    UNIQUE(history_record_number),
    UNIQUE(history_record_sha256)
);
"""

class CampaignShadowLedgerError(RuntimeError): pass

def _mapping(value: Any) -> dict[str, Any]:
    if is_dataclass(value): return asdict(value)
    if isinstance(value, Mapping): return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict): return dict(to_dict())
    raise CampaignShadowLedgerError("campaign commit is not serializable")

def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

class CampaignShadowLedger:
    """Best-effort mirror; never a campaign authority boundary."""
    def __init__(self, campaign_root: Path | str, *, db_name: str = SHADOW_DB_NAME):
        self.root = Path(campaign_root).expanduser().resolve()
        self.path = self.root / db_name

    def _connect(self) -> sqlite3.Connection:
        self.root.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(_SCHEMA)
        conn.execute("INSERT OR REPLACE INTO campaign_shadow_meta(key,value) VALUES('contract',?)", (SHADOW_LEDGER_CONTRACT,))
        return conn

    def mirror_commit(self, commit: Any) -> None:
        row = _mapping(commit)
        final_state = dict(row.get("final_state") or {})
        required = ("flight_id","revision_before","revision_after","origin","destination","departure_epoch_utc","arrival_epoch_utc","remass_before_t","remass_after_t","history_record_number","history_record_sha256","state_path","history_path")
        missing = [key for key in required if row.get(key) is None]
        if missing: raise CampaignShadowLedgerError("commit missing fields: " + ", ".join(missing))
        values = (
            str(row["flight_id"]), int(row["revision_before"]), int(row["revision_after"]), row.get("state_before_id"), row.get("state_after_id"), str(row["origin"]), str(row["destination"]), str(row["departure_epoch_utc"]), str(row["arrival_epoch_utc"]), float(row["remass_before_t"]), float(row["remass_after_t"]), int(row["history_record_number"]), str(row["history_record_sha256"]), str(row["state_path"]), str(row["history_path"]), _canonical_json(final_state), _canonical_json(row),
        )
        with self._connect() as conn:
            existing = conn.execute("SELECT canonical_commit_json FROM campaign_flight_commits WHERE flight_id=?", (values[0],)).fetchone()
            if existing:
                if existing[0] != values[-1]: raise CampaignShadowLedgerError("flight_id already mirrored with different canonical commit")
                return
            conn.execute("""INSERT INTO campaign_flight_commits(
                flight_id,revision_before,revision_after,state_before_id,state_after_id,origin,destination,departure_epoch_utc,arrival_epoch_utc,remass_before_t,remass_after_t,history_record_number,history_record_sha256,state_path,history_path,final_state_json,canonical_commit_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", values)

    def reconcile_commit(self, commit: Any) -> dict[str, Any]:
        row = _mapping(commit); flight_id = str(row.get("flight_id") or "")
        if not self.path.is_file(): return {"contract":SHADOW_LEDGER_CONTRACT,"flight_id":flight_id,"status":"MISSING_DB","match":False}
        with sqlite3.connect(self.path) as conn:
            found = conn.execute("SELECT canonical_commit_json FROM campaign_flight_commits WHERE flight_id=?", (flight_id,)).fetchone()
        if not found: return {"contract":SHADOW_LEDGER_CONTRACT,"flight_id":flight_id,"status":"MISSING_COMMIT","match":False}
        match = found[0] == _canonical_json(row)
        return {"contract":SHADOW_LEDGER_CONTRACT,"flight_id":flight_id,"status":"MATCH" if match else "MISMATCH","match":match}
