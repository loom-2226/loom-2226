#!/usr/bin/env python3
"""Build a unified candidate patch without relying on linked-worktree Git metadata."""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def build_candidate_patch(authoritative_root: Path, repaired_root: Path, paths: list[str]) -> str:
    authoritative_root = authoritative_root.resolve()
    repaired_root = repaired_root.resolve()
    chunks: list[str] = []
    for raw in paths:
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe candidate path: {raw}")
        before_path = (authoritative_root / rel).resolve()
        after_path = (repaired_root / rel).resolve()
        if authoritative_root not in before_path.parents or repaired_root not in after_path.parents:
            raise ValueError(f"candidate path escapes root: {raw}")
        before = before_path.read_text(encoding="utf-8").splitlines(keepends=True)
        after = after_path.read_text(encoding="utf-8").splitlines(keepends=True)
        chunks.extend(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"a/{rel.as_posix()}",
                tofile=f"b/{rel.as_posix()}",
                lineterm="\n",
            )
        )
    return "".join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authoritative-root", required=True)
    ap.add_argument("--repaired-root", required=True)
    ap.add_argument("--decision", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    import json

    decision = json.loads(Path(args.decision).read_text(encoding="utf-8"))
    paths = decision.get("applied_paths") or []
    if not paths:
        raise SystemExit("decision contains no applied_paths")
    patch = build_candidate_patch(
        Path(args.authoritative_root),
        Path(args.repaired_root),
        [str(p) for p in paths],
    )
    if not patch:
        raise SystemExit("candidate patch is empty")
    Path(args.output).write_text(patch, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
