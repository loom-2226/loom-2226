#!/usr/bin/env python3
"""Bounded local mechanical-repair helper for LOOM Pixel qualification.

This helper may edit only engineering/pixel Python/shell files in a temporary
worktree. It has no Git commit/push authority and no permission to edit tests,
active qualification config, src/, data/, canon/, schemas, or physics/runtime
state. A successful local repair is a candidate patch, never a governed PASS.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

API_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.6-terra"
MAX_CONTEXT_CHARS = 120_000
MAX_EDITS = 4
MAX_REPLACEMENT_CHARS = 8_000


def is_editable_path(path: str) -> bool:
    p = Path(path)
    if p.is_absolute() or ".." in p.parts:
        return False
    s = p.as_posix()
    if s == "engineering/pixel/active_qualification.txt":
        return False
    return s.startswith("engineering/pixel/") and p.suffix in {".py", ".sh"}


def apply_exact_replacements(root: Path, edits: list[dict[str, str]]) -> list[str]:
    if len(edits) > MAX_EDITS:
        raise ValueError(f"too many edits: {len(edits)} > {MAX_EDITS}")
    applied: list[str] = []
    root = root.resolve()
    for edit in edits:
        path = str(edit.get("path", ""))
        old = str(edit.get("old", ""))
        new = str(edit.get("new", ""))
        if not is_editable_path(path):
            raise ValueError(f"edit path outside mechanical boundary: {path}")
        if not old or old == new:
            raise ValueError(f"invalid exact replacement for {path}")
        if len(new) > MAX_REPLACEMENT_CHARS:
            raise ValueError(f"replacement too large for {path}")
        target = (root / path).resolve()
        if root not in target.parents:
            raise ValueError(f"path escapes worktree: {path}")
        if not target.is_file():
            raise ValueError(f"target file missing: {path}")
        text = target.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            raise ValueError(f"old text must occur exactly once in {path}; found {count}")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        applied.append(path)
    return applied


def _editable_context(root: Path) -> str:
    chunks: list[str] = []
    base = root / "engineering" / "pixel"
    if not base.is_dir():
        return ""
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not is_editable_path(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        chunks.append(f"\n--- FILE {rel} ---\n{text}")
    joined = "".join(chunks)
    return joined[:MAX_CONTEXT_CHARS]


def _response_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "classification": {
                "type": "string",
                "enum": ["MECHANICAL_REPAIRABLE", "ESCALATE"],
            },
            "summary": {"type": "string"},
            "reason": {"type": "string"},
            "edits": {
                "type": "array",
                "maxItems": MAX_EDITS,
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old": {"type": "string"},
                        "new": {"type": "string"},
                    },
                    "required": ["path", "old", "new"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["classification", "summary", "reason", "edits"],
        "additionalProperties": False,
    }


def _extract_output_text(response: dict) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct:
        return direct
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    return text
    raise RuntimeError("Responses API returned no output text")


def request_repair(root: Path, transcript: str, attempt: int) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model = os.environ.get("LOOM_REPAIR_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    context = _editable_context(root)
    prompt = f"""LOOM local mechanical qualification repair, attempt {attempt}.

You are diagnosing a failed Android Termux qualification run. You may propose ONLY
mechanical repairs to files under engineering/pixel/*.py or engineering/pixel/*.sh.
Allowed examples: import/bootstrap path mistakes, Termux path portability, shell
quoting, missing local directories, subprocess/process lifecycle mistakes, command
invocation mistakes, and similar harness/platform failures.

You MUST ESCALATE if the failure would require changing tests, active_qualification.txt,
src/, data/, canon, schemas, expected numerical values, physics, Navigator behavior,
qualification semantics, authority boundaries, or scientific conclusions. Never
weaken a test or change an expected result to make a run pass. Never propose Git
commit/push operations. Prefer the smallest exact string replacement possible.
If no safe mechanical repair is clear, ESCALATE with zero edits.

FAILED TRANSCRIPT:
{transcript[-50000:]}

EDITABLE FILE CONTEXT:
{context}
"""
    payload = {
        "model": model,
        "store": False,
        "reasoning": {"effort": "medium"},
        "input": prompt,
        "text": {
            "verbosity": "low",
            "format": {
                "type": "json_schema",
                "name": "loom_mechanical_repair",
                "strict": True,
                "schema": _response_schema(),
            },
        },
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1200]}") from exc
    decision = json.loads(_extract_output_text(response))
    if decision.get("classification") == "MECHANICAL_REPAIRABLE":
        edits = decision.get("edits") or []
        if not edits:
            raise RuntimeError("repairable classification returned no edits")
        decision["applied_paths"] = apply_exact_replacements(root, edits)
    else:
        decision["edits"] = []
        decision["applied_paths"] = []
    decision["model"] = model
    decision["attempt"] = attempt
    return decision


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--attempt", type=int, required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    transcript = Path(args.transcript).read_text(encoding="utf-8", errors="replace")
    try:
        decision = request_repair(root, transcript, args.attempt)
    except Exception as exc:
        decision = {
            "classification": "ESCALATE",
            "summary": "Local mechanical-repair agent could not produce a safe candidate.",
            "reason": str(exc),
            "edits": [],
            "applied_paths": [],
            "attempt": args.attempt,
            "model": os.environ.get("LOOM_REPAIR_MODEL", DEFAULT_MODEL),
        }
    encoded = json.dumps(decision, indent=2, sort_keys=True)
    print(encoded)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    return 0 if decision.get("classification") == "MECHANICAL_REPAIRABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
