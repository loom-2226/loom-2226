#!/usr/bin/env python3
"""LOOM read-only runtime doctor."""
from __future__ import annotations

from pathlib import Path
import argparse
import sys

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loom.runtime import resolve_runtime_roots
from loom.runtime_diagnostics import collect_runtime_manifest, manifest_json, render_runtime_audit


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Inspect LOOM runtime identity without mutating it.")
    ap.add_argument("--app-root", type=Path)
    ap.add_argument("--data-root", type=Path)
    ap.add_argument("--campaign-root", type=Path)
    ap.add_argument("--json", action="store_true", help="print machine-readable manifest")
    args = ap.parse_args(argv)

    roots = resolve_runtime_roots(
        app_root=args.app_root,
        data_root=args.data_root,
        campaign_root=args.campaign_root,
    )
    manifest = collect_runtime_manifest(roots=roots)
    print(manifest_json(manifest) if args.json else render_runtime_audit(manifest), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
