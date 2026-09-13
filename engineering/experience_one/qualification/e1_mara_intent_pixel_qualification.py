#!/usr/bin/env python3
from __future__ import annotations

"""Pixel qualification for Mara/OpenAI -> typed E1 flight intent only.

No planning or execution occurs. The live campaign is hashed before/after and must
remain bit-identical. Every provider call is recorded in the append-only OpenAI
development audit.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path

from engineering.experience_one.e1_mara_intent_adapter import OpenAIMaraIntentAdapter

CAMPAIGN_FILES = ("LOOM_STATE_V1.json", "LOOM_STATE_V1.bak", "LOOM_CAMPAIGN_HISTORY.jsonl.gz")
DEFAULT_ROOT = Path("/storage/emulated/0/Download/LOOM_TEST")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_MARA_TYPED_INTENT_QUALIFICATION_RESULT.json")
DEFAULT_AUDIT = Path("/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def campaign_hashes(root: Path) -> dict[str, str | None]:
    return {name: sha256_file(root / name) for name in CAMPAIGN_FILES}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--prompt", default="Take us to Neptune, balanced profile.")
    args = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    before = campaign_hashes(args.root)
    if before["LOOM_STATE_V1.json"] is None or before["LOOM_CAMPAIGN_HISTORY.jsonl.gz"] is None:
        raise RuntimeError("live campaign artifacts missing")

    adapter = OpenAIMaraIntentAdapter(
        api_key=key,
        audit_path=args.audit,
        model=args.model,
    )
    intent = adapter.interpret(args.prompt)
    payload = intent.payload()

    after = campaign_hashes(args.root)
    unchanged = before == after
    intent_pass = bool(
        payload.get("destination") == "NEPTUNE_SYSTEM"
        and payload.get("priority") == "BALANCED"
        and payload.get("origin") == "MARA"
        and payload.get("calculation_authority") == "ZERO"
        and payload.get("state_authority") == "ZERO"
        and payload.get("execution_authority") == "ZERO"
    )
    result = {
        "schema": "LOOM_E1_MARA_TYPED_INTENT_QUALIFICATION_V1",
        "prompt": args.prompt,
        "model": args.model,
        "typed_intent": payload,
        "intent_pass": intent_pass,
        "real_campaign_hashes_before": before,
        "real_campaign_hashes_after": after,
        "real_campaign_unchanged_pass": unchanged,
        "audit": {
            "schema": "LOOM_OPENAI_DEV_AUDIT_V1",
            "path": str(args.audit),
            "session_id": adapter.audit.session_id,
            "entries_written_this_session": adapter.audit.sequence,
            "last_entry_sha256": adapter.audit.previous_hash,
            "raw_key_recorded": False,
        },
        "qualification_pass": bool(intent_pass and unchanged and adapter.audit.sequence == 1),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not unchanged:
        raise RuntimeError("REAL CAMPAIGN MUTATED — HARD FAIL")
    return 0 if result["qualification_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
