#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 Mara grounded-synthesis empirical harness v0.3.

Changes from v0.2:
- uses the deterministic context-qualified reference resolver;
- records adapter/query failures as case evidence instead of crashing;
- checkpoints the result artifact after every case;
- preserves the same OpenAI audit and authority boundaries.

This remains engineering evidence, not production Mara architecture.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V02 = HERE / "e1_1_mara_grounded_synthesis_v02.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = _load(V02, "e1_1_mara_grounded_synthesis_v02")

DEFAULT_PROJECTION = Path("/storage/emulated/0/Download/E1_1_CERES_CONTEXT_V1.json")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_MARA_SYNTHESIS_RESULT_V03.json")
DEFAULT_AUDIT = Path("/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl")


def _write_checkpoint(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


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
    audit = base.OpenAIDevAudit(args.audit, key, endpoint=base.API_URL)
    result: dict[str, Any] = {
        "schema": "LOOM_E1_1_MARA_GROUNDED_SYNTHESIS_RESULT_V03",
        "model": args.model,
        "authority": {
            "model_sqlite_access": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "tool_read_only": True,
            "target_resolution": "DETERMINISTIC_PROJECTED_ENTITY_REFERENCE_WITH_CONTEXT_ALIAS",
        },
        "audit": {
            "path": str(args.audit),
            "session_id": audit.session_id,
            "credential_fingerprint_sha256_16": audit.credential_fingerprint,
            "raw_key_recorded": False,
        },
        "cases": [],
    }
    total_in = total_out = 0
    _write_checkpoint(args.out, result)

    for case in base.CASES:
        cid = case["id"]
        p1 = {
            "model": args.model,
            "instructions": base.SYSTEM,
            "input": case["prompt"],
            "tools": [base.TOOL],
            "tool_choice": {"type": "function", "name": "query_canon_context"},
            "parallel_tool_calls": False,
            "store": False,
        }

        try:
            r1, t1 = base.api_post(key, p1, args.timeout, audit, stage=f"{cid}.request1_tool_call_v03", metadata={"case": cid, "phase": "MODEL_TO_TYPED_REFERENCE"})
        except Exception as exc:
            entry = {"case": cid, "user_prompt": case["prompt"], "pass": False, "fail_reasons": [f"request1_error:{type(exc).__name__}:{exc}"]}
            result["cases"].append(entry)
            _write_checkpoint(args.out, result)
            print(f"{cid:<28} FAIL  request1_error={type(exc).__name__}")
            continue

        calls = base.function_calls(r1)
        if len(calls) != 1 or calls[0].get("name") != "query_canon_context":
            entry = {"case": cid, "user_prompt": case["prompt"], "pass": False, "fail_reasons": ["expected_exactly_one_query_canon_context_call"], "provider_output": r1.get("output")}
            result["cases"].append(entry)
            _write_checkpoint(args.out, result)
            print(f"{cid:<28} FAIL  bad_tool_call_count={len(calls)}")
            continue

        call = calls[0]
        raw_args = json.loads(call.get("arguments") or "{}")
        raw_args.setdefault("max_items", 3)
        try:
            packet, normalized = base.build_tool_packet(projection, raw_args)
        except Exception as exc:
            entry = {
                "case": cid,
                "user_prompt": case["prompt"],
                "raw_tool_arguments": raw_args,
                "pass": False,
                "fail_reasons": [f"target_or_query_resolution_error:{type(exc).__name__}:{exc}"],
            }
            result["cases"].append(entry)
            _write_checkpoint(args.out, result)
            print(f"{cid:<28} FAIL  ref={raw_args.get('target_reference')!r}  {type(exc).__name__}: {exc}")
            continue

        arg_reasons: list[str] = []
        if normalized["intent"] != case["expected_intent"]:
            arg_reasons.append("intent_mismatch")
        if normalized["target_entity_id"] != case["expected_target"]:
            arg_reasons.append("resolved_target_mismatch")

        continuation = [{"role": "user", "content": case["prompt"]}]
        continuation.extend(r1.get("output", []))
        continuation.append({"type": "function_call_output", "call_id": call["call_id"], "output": json.dumps(packet, separators=(",", ":"))})
        p2 = {"model": args.model, "instructions": base.SYSTEM, "input": continuation, "tools": [base.TOOL], "tool_choice": "none", "store": False}

        try:
            r2, t2 = base.api_post(key, p2, args.timeout, audit, stage=f"{cid}.request2_grounded_synthesis_v03", metadata={"case": cid, "phase": "TYPED_QUERY_TO_MODEL"})
            raw = base.output_text(r2)
            try:
                parsed = base.parse_json_answer(raw)
                answer_pass, reasons = base.validate_answer(case, packet, parsed)
            except Exception as exc:
                parsed = {"answer": raw}
                answer_pass, reasons = False, [f"non_json_or_invalid_answer:{type(exc).__name__}"]
            reasons = arg_reasons + reasons
            passed = not reasons and answer_pass
            u1, u2 = r1.get("usage") or {}, r2.get("usage") or {}
            ins = int(u1.get("input_tokens", 0)) + int(u2.get("input_tokens", 0))
            outs = int(u1.get("output_tokens", 0)) + int(u2.get("output_tokens", 0))
            total_in += ins
            total_out += outs
            entry = {
                "case": cid,
                "user_prompt": case["prompt"],
                "raw_tool_arguments": raw_args,
                "normalized_tool_arguments": normalized,
                "tool_packet": packet,
                "model_answer_raw": raw,
                "model_answer_parsed": parsed,
                "pass": passed,
                "fail_reasons": reasons,
                "latency_s": round(t1 + t2, 3),
                "usage": {"input_tokens": ins, "output_tokens": outs},
            }
            print(f"{cid:<28} {'PASS' if passed else 'FAIL'}  {t1+t2:.2f}s  ref={raw_args.get('target_reference')!r} -> {normalized['target_entity_id']}  reasons={reasons}")
        except Exception as exc:
            entry = {
                "case": cid,
                "user_prompt": case["prompt"],
                "raw_tool_arguments": raw_args,
                "normalized_tool_arguments": normalized,
                "tool_packet": packet,
                "pass": False,
                "fail_reasons": [f"request2_error:{type(exc).__name__}:{exc}"],
            }
            print(f"{cid:<28} FAIL  request2_error={type(exc).__name__}")

        result["cases"].append(entry)
        result["usage_total"] = {"input_tokens": total_in, "output_tokens": total_out}
        result["audit"]["last_entry_sha256"] = audit.previous_hash
        result["audit"]["entries_written_this_session"] = audit.sequence
        _write_checkpoint(args.out, result)

    result["all_cases_pass"] = len(result["cases"]) == len(base.CASES) and all(x.get("pass") for x in result["cases"])
    result["usage_total"] = {"input_tokens": total_in, "output_tokens": total_out}
    result["audit"]["last_entry_sha256"] = audit.previous_hash
    result["audit"]["entries_written_this_session"] = audit.sequence
    _write_checkpoint(args.out, result)
    print(json.dumps({"all_cases_pass": result["all_cases_pass"], "usage_total": result["usage_total"], "audit_entries_written": audit.sequence, "out": str(args.out)}, indent=2))
    return 0 if result["all_cases_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
