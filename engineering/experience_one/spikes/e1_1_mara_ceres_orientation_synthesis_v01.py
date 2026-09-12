#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 bounded Mara synthesis over already-qualified Ceres query packets.

This experiment isolates the SYNTHESIS layer. It does not ask the model to select
facts, resolve entities, query SQLite, rank places, infer campaign state, or mutate
anything. Deterministic code first constructs the qualified ORIENT and INTERESTING
packets; the model receives only those packets and turns them into concise prose.

The exact prose is printed and preserved for manual semantic review. Structural
checks can establish grounding/path discipline, but cannot by themselves prove
that natural-language wording is semantically faithful.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
HERE = Path(__file__).resolve().parent
V05 = HERE / "e1_1_mara_grounded_synthesis_v05.py"
DEFAULT_PROJECTION = Path("/storage/emulated/0/Download/E1_1_CERES_CONTEXT_V1.json")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_MARA_CERES_ORIENTATION_SYNTHESIS_V01.json")
DEFAULT_AUDIT = Path("/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


query_mod = _load(SRC / "loom_canon_context_query.py", "loom_canon_context_query")
v05 = _load(V05, "e1_1_mara_grounded_synthesis_v05")
base = v05.base

SYSTEM = """You are Mara in a bounded LOOM engineering experiment.
You have ZERO calculation authority, ZERO state authority, and ZERO canon authority.
Use only the supplied deterministic evidence packet. Do not add lore, causal claims,
events, motives, history, danger, significance, or recommendations that are not in
that packet. If the packet does not establish something, omit it.

Answer the user's question in concise natural language, then cite the exact packet
paths you relied on. Return ONLY a JSON object with exactly these fields:
{
  "answer": "...",
  "assessment": "SUPPORTED",
  "evidence_paths": ["orient....", "interesting...."]
}
The answer should make the place legible to a human, not recite field names.
"""

USER_PROMPT = "What is this place, and what should I notice?"


def path_exists(value: Any, path: str) -> bool:
    current = value
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return False
            current = current[part]
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return False
        else:
            return False
    return True


def build_evidence(projection: dict[str, Any]) -> dict[str, Any]:
    orient = query_mod.query_projection(projection, "ORIENT")
    interesting = query_mod.query_projection(projection, "INTERESTING", max_items=3)
    return {
        "schema": "LOOM_E1_1_MARA_CERES_SYNTHESIS_EVIDENCE_V1",
        "question": USER_PROMPT,
        "orient": orient,
        "interesting": interesting,
        "authority_policy": {
            "model_sqlite_access": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "fact_selection": "DETERMINISTIC_PRECOMPUTED",
            "place_ranking": "DETERMINISTIC_PRECOMPUTED",
            "campaign_mutation": False,
            "canon_mutation": False,
        },
    }


def validate_answer(evidence: dict[str, Any], answer: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if set(answer) != {"answer", "assessment", "evidence_paths"}:
        reasons.append("response_shape_mismatch")
    text = answer.get("answer")
    if not isinstance(text, str) or not text.strip():
        reasons.append("answer_missing")
    if answer.get("assessment") != "SUPPORTED":
        reasons.append("assessment_must_be_supported")
    paths = answer.get("evidence_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
        reasons.append("evidence_paths_invalid")
        paths = []
    bad = [p for p in paths if not path_exists(evidence, p)]
    if bad:
        reasons.append("evidence_path_not_in_packet")
    if not any(p.startswith("orient.") for p in paths):
        reasons.append("orientation_grounding_missing")
    if not any(p.startswith("interesting.") for p in paths):
        reasons.append("interesting_grounding_missing")
    return not reasons, reasons


def parse_json_answer(raw: str) -> dict[str, Any]:
    return base.parse_json_answer(raw)


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projection", type=Path, default=DEFAULT_PROJECTION)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--timeout", type=float, default=90.0)
    args = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    projection = json.loads(args.projection.expanduser().read_text(encoding="utf-8"))
    evidence = build_evidence(projection)
    audit = base.OpenAIDevAudit(args.audit, key, endpoint=base.API_URL)

    payload = {
        "model": args.model,
        "instructions": SYSTEM,
        "input": [
            {"role": "user", "content": USER_PROMPT},
            {"role": "user", "content": "DETERMINISTIC_EVIDENCE_PACKET\n" + json.dumps(evidence, separators=(",", ":"))},
        ],
        "store": False,
    }

    response, latency = base.api_post(
        key,
        payload,
        args.timeout,
        audit,
        stage="ceres_orientation_synthesis_v01",
        metadata={"phase": "DETERMINISTIC_PACKETS_TO_MODEL", "question": USER_PROMPT},
    )
    raw = base.output_text(response)
    parsed = parse_json_answer(raw)
    passed, reasons = validate_answer(evidence, parsed)
    usage = response.get("usage") or {}

    result = {
        "schema": "LOOM_E1_1_MARA_CERES_ORIENTATION_SYNTHESIS_RESULT_V01",
        "question": USER_PROMPT,
        "model": args.model,
        "authority": evidence["authority_policy"],
        "evidence": evidence,
        "model_answer_raw": raw,
        "model_answer_parsed": parsed,
        "structural_pass": passed,
        "structural_fail_reasons": reasons,
        "semantic_review": "EMPIRICAL_MANUAL_REVIEW_REQUIRED",
        "latency_s": round(latency, 3),
        "usage": {
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
        },
        "audit": {
            "path": str(args.audit),
            "session_id": audit.session_id,
            "entries_written_this_session": audit.sequence,
            "last_entry_sha256": audit.previous_hash,
            "raw_key_recorded": False,
        },
    }
    _write(args.out, result)

    print("schema:", result["schema"])
    print("structural_pass:", passed)
    print("structural_fail_reasons:", reasons)
    print("assessment:", parsed.get("assessment"))
    print("evidence_paths:")
    for path in parsed.get("evidence_paths") or []:
        print(" -", path)
    print("answer:")
    print(parsed.get("answer", ""))
    print("semantic_review:", result["semantic_review"])
    print("latency_s:", result["latency_s"])
    print("usage:", result["usage"])
    print("out:", args.out)
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
