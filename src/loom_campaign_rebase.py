#!/usr/bin/env python3
"""Controlled LOOM campaign epoch rebase.

Rewrites campaign JSON/history timestamps by one constant offset while preserving
relative durations and record ordering. Recomputes state IDs/hashes and history
hash-chain values. JSON/history remain canonical authority; shadow SQL is updated
only as a diagnostic mirror.

Default legacy source seed: 2027-06-15T02:00:00Z
Canonical target seed:      2226-06-15T02:00:00Z
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import copy
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile

SOURCE_SEED = "2027-06-15T02:00:00Z"
TARGET_SEED = "2226-06-15T02:00:00Z"
STATE_FILE = "LOOM_STATE_V1.json"
BACKUP_FILE = "LOOM_STATE_V1.bak"
HISTORY_FILE = "LOOM_CAMPAIGN_HISTORY.jsonl.gz"
SHADOW_FILE = "LOOM_CAMPAIGN_DEV.sqlite3"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _state_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in state.items() if k not in ("state_id", "state_sha256")}


def _stamp_state(state: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(state)
    rev = int(out["revision"])
    digest = _sha(_state_payload(out))
    out["state_sha256"] = digest
    out["state_id"] = f"S{rev:06d}-{digest[:12]}"
    return out


def _validate_state(state: dict[str, Any]) -> None:
    digest = _sha(_state_payload(state))
    if state.get("state_sha256") != digest:
        raise RuntimeError("state hash mismatch")
    if state.get("state_id") != f"S{int(state['revision']):06d}-{digest[:12]}":
        raise RuntimeError("state id mismatch")


def _parse_utc(text: str) -> datetime | None:
    if not isinstance(text, str):
        return None
    if not (text.endswith("Z") or text.endswith("+00:00")):
        return None
    try:
        dt = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except ValueError:
        return None
    return dt.astimezone(timezone.utc)


def _fmt_like(original: str, dt: datetime) -> str:
    iso = dt.astimezone(timezone.utc).isoformat()
    if original.endswith("Z"):
        return iso.replace("+00:00", "Z")
    return iso


def _shift_recursive(value: Any, offset) -> Any:
    if isinstance(value, dict):
        return {k: _shift_recursive(v, offset) for k, v in value.items()}
    if isinstance(value, list):
        return [_shift_recursive(v, offset) for v in value]
    if isinstance(value, tuple):
        return tuple(_shift_recursive(v, offset) for v in value)
    if isinstance(value, str):
        dt = _parse_utc(value)
        return _fmt_like(value, dt + offset) if dt is not None else value
    return value


def _replace_refs(value: Any, id_map: dict[str, str], hash_map: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {k: _replace_refs(v, id_map, hash_map) for k, v in value.items()}
    if isinstance(value, list):
        return [_replace_refs(v, id_map, hash_map) for v in value]
    if isinstance(value, tuple):
        return tuple(_replace_refs(v, id_map, hash_map) for v in value)
    if isinstance(value, str):
        return id_map.get(value, hash_map.get(value, value))
    return value


def _read_gzip(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _write_gzip_atomic(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        with open(tmp, "wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as gz:
                for record in records:
                    gz.write((json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8"))
            raw.flush(); os.fsync(raw.fileno())
        if len(_read_gzip(tmp)) != len(records):
            raise RuntimeError("history temp verification failed")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _record_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "record_sha256"}


def _verify_history(records: list[dict[str, Any]]) -> None:
    prev = None
    for number, record in enumerate(records, 1):
        if int(record.get("record_number", -1)) != number:
            raise RuntimeError("history record numbering gap")
        if record.get("previous_record_sha256") != prev:
            raise RuntimeError("history previous hash mismatch")
        want = _sha(_record_payload(record))
        if record.get("record_sha256") != want:
            raise RuntimeError("history record hash mismatch")
        prev = want


def _history_paths(root: Path) -> list[Path]:
    return sorted(root.glob("LOOM_CAMPAIGN_HISTORY_ARCHIVE_*.jsonl.gz")) + [root / HISTORY_FILE]


def _load_history(root: Path) -> tuple[list[dict[str, Any]], list[tuple[Path, int]]]:
    records: list[dict[str, Any]] = []
    spans: list[tuple[Path, int]] = []
    for path in _history_paths(root):
        chunk = _read_gzip(path)
        if chunk or path.name == HISTORY_FILE:
            records.extend(chunk)
            spans.append((path, len(chunk)))
    _verify_history(records)
    return records, spans


def _backup_campaign(root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = root / ".loom_epoch_rebase_backups" / stamp
    dest.mkdir(parents=True, exist_ok=False)
    for path in [root / STATE_FILE, root / BACKUP_FILE, root / SHADOW_FILE, *_history_paths(root)]:
        if path.exists():
            shutil.copy2(path, dest / path.name)
    return dest


def _transform_state(old: dict[str, Any], offset, id_map: dict[str, str], hash_map: dict[str, str]) -> dict[str, Any]:
    shifted = _shift_recursive(old, offset)
    shifted = _replace_refs(shifted, id_map, hash_map)
    stamped = _stamp_state(shifted)
    id_map[str(old.get("state_id"))] = stamped["state_id"]
    hash_map[str(old.get("state_sha256"))] = stamped["state_sha256"]
    return stamped


def _transform_history(records: list[dict[str, Any]], offset):
    id_map: dict[str, str] = {}
    hash_map: dict[str, str] = {}
    new_snapshots: dict[int, dict[str, Any]] = {}

    # Build state mappings in record order so departure_state_id references can
    # resolve to already-transformed predecessor states.
    for record in records:
        snap = record.get("state_after_snapshot")
        if isinstance(snap, dict):
            new_snapshots[int(record["record_number"])] = _transform_state(snap, offset, id_map, hash_map)

    out: list[dict[str, Any]] = []
    prev = None
    record_hash_map: dict[str, str] = {}
    for record in records:
        old_record_sha = str(record.get("record_sha256") or "")
        new = _replace_refs(_shift_recursive(record, offset), id_map, hash_map)
        number = int(record["record_number"])
        if number in new_snapshots:
            new["state_after_snapshot"] = new_snapshots[number]
            new["state_after_sha256"] = new_snapshots[number]["state_sha256"]
        if record.get("state_before_sha256") in hash_map:
            new["state_before_sha256"] = hash_map[record["state_before_sha256"]]
        new["previous_record_sha256"] = prev
        new.pop("record_sha256", None)
        digest = _sha(new)
        new["record_sha256"] = digest
        record_hash_map[old_record_sha] = digest
        prev = digest
        out.append(new)
    _verify_history(out)
    return out, id_map, hash_map, record_hash_map, new_snapshots


def _update_shadow(root: Path, offset, id_map, hash_map, record_hash_map, snapshots_by_record) -> None:
    path = root / SHADOW_FILE
    if not path.exists():
        return
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT flight_id,history_record_number,canonical_commit_json FROM campaign_flight_commits").fetchall()
        for flight_id, record_number, commit_json in rows:
            commit = json.loads(commit_json)
            commit = _replace_refs(_shift_recursive(commit, offset), id_map, hash_map)
            if int(record_number) in snapshots_by_record:
                commit["final_state"] = snapshots_by_record[int(record_number)]
                commit["state_after_id"] = commit["final_state"].get("state_id")
            old_history_sha = str(commit.get("history_record_sha256") or "")
            if old_history_sha in record_hash_map:
                commit["history_record_sha256"] = record_hash_map[old_history_sha]
            final_state = dict(commit.get("final_state") or {})
            conn.execute("""
                UPDATE campaign_flight_commits SET
                  state_before_id=?, state_after_id=?, departure_epoch_utc=?, arrival_epoch_utc=?,
                  history_record_sha256=?, final_state_json=?, canonical_commit_json=?
                WHERE flight_id=?
            """, (
                commit.get("state_before_id"), commit.get("state_after_id"),
                commit.get("departure_epoch_utc"), commit.get("arrival_epoch_utc"),
                commit.get("history_record_sha256"),
                json.dumps(final_state, sort_keys=True, separators=(",", ":"), default=str),
                json.dumps(commit, sort_keys=True, separators=(",", ":"), default=str),
                flight_id,
            ))
        check = conn.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            raise RuntimeError("shadow SQL integrity check failed")


def rebase_campaign(root: Path, source_seed: str = SOURCE_SEED, target_seed: str = TARGET_SEED, *, apply: bool = False) -> dict[str, Any]:
    root = Path(root).expanduser().resolve()
    state_path = root / STATE_FILE
    if not state_path.is_file():
        raise RuntimeError(f"campaign state missing: {state_path}")
    current = json.loads(state_path.read_text(encoding="utf-8"))
    _validate_state(current)
    records, spans = _load_history(root)

    source = _parse_utc(source_seed); target = _parse_utc(target_seed)
    if source is None or target is None:
        raise RuntimeError("source and target seeds must be UTC ISO-8601")
    offset = target - source

    rewritten, id_map, hash_map, record_hash_map, snapshots = _transform_history(records, offset)

    old_current_hash = str(current.get("state_sha256"))
    if old_current_hash in hash_map:
        # latest canonical state should exactly match its rewritten snapshot
        matching = [s for s in snapshots.values() if s["state_sha256"] == hash_map[old_current_hash]]
        new_current = matching[-1] if matching else _transform_state(current, offset, id_map, hash_map)
    else:
        new_current = _transform_state(current, offset, id_map, hash_map)
    _validate_state(new_current)

    result = {
        "status": "DRY_RUN" if not apply else "APPLIED",
        "campaign_root": str(root),
        "source_seed": source_seed,
        "target_seed": target_seed,
        "old_epoch_utc": current.get("epoch_utc"),
        "new_epoch_utc": new_current.get("epoch_utc"),
        "revision": int(new_current["revision"]),
        "history_records": len(rewritten),
        "old_state_id": current.get("state_id"),
        "new_state_id": new_current.get("state_id"),
    }
    if not apply:
        return result

    backup_dir = _backup_campaign(root)
    # Rewrite history files with the same archive/active record partition.
    pos = 0
    for path, count in spans:
        chunk = rewritten[pos:pos + count]
        _write_gzip_atomic(path, chunk)
        pos += count
    state_path.write_text(json.dumps(new_current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _validate_state(json.loads(state_path.read_text(encoding="utf-8")))

    # Rebase state backup too when it is a valid state; otherwise preserve only
    # the byte-for-byte pre-rebase copy in backup_dir.
    bak_path = root / BACKUP_FILE
    if bak_path.exists():
        try:
            old_bak = json.loads(bak_path.read_text(encoding="utf-8")); _validate_state(old_bak)
            new_bak = _transform_state(old_bak, offset, id_map, hash_map)
            bak_path.write_text(json.dumps(new_bak, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception:
            pass

    _update_shadow(root, offset, id_map, hash_map, record_hash_map, snapshots)
    verify_records, _ = _load_history(root)
    if len(verify_records) != len(records):
        raise RuntimeError("post-rebase history count mismatch")
    result["backup_dir"] = str(backup_dir)
    return result


def _default_campaign_root() -> Path:
    env = os.environ.get("LOOM_CAMPAIGN_ROOT")
    if env:
        return Path(env)
    return Path("/storage/emulated/0/Documents/LOOM/campaign") if os.environ.get("ANDROID_ROOT") else Path.cwd()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Rebase LOOM campaign timeline while preserving elapsed durations")
    p.add_argument("--campaign-root", default=str(_default_campaign_root()))
    p.add_argument("--source-seed", default=SOURCE_SEED)
    p.add_argument("--target-seed", default=TARGET_SEED)
    p.add_argument("--apply", action="store_true", help="Apply after validated dry-run; otherwise read-only")
    args = p.parse_args(argv)
    result = rebase_campaign(Path(args.campaign_root), args.source_seed, args.target_seed, apply=args.apply)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
