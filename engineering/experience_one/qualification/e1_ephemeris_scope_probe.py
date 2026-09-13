#!/usr/bin/env python3
from __future__ import annotations

"""Read-only introspection probe for the embedded Sequence H ephemeris seam.

This is diagnostic tooling only. It does not call Horizons, mutate campaign state,
or alter Navigator behavior. It loads the exact embedded core through Navigator's
own loader and prints the implementation/signatures needed to design a bounded
route-scoped acquisition adapter without guessing at the opaque embedded module.
"""

import inspect
import json
import tempfile
from pathlib import Path

import importlib.util


REPO = Path(__file__).resolve().parents[3]
NAV_PATH = REPO / "src" / "loom_navigator_core.py"


def load_navigator():
    spec = importlib.util.spec_from_file_location("loom_e1_ephemeris_probe_nav", NAV_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {NAV_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def show_function(module, name: str) -> None:
    obj = getattr(module, name, None)
    print(f"\n=== {name} ===")
    if obj is None:
        print("MISSING")
        return
    try:
        print("SIGNATURE", inspect.signature(obj))
    except Exception as exc:
        print("SIGNATURE_ERROR", repr(exc))
    try:
        print(inspect.getsource(obj))
    except Exception as exc:
        print("SOURCE_ERROR", repr(exc))


def main() -> int:
    outer = load_navigator()
    with tempfile.TemporaryDirectory(prefix="loom_e1_ephemeris_probe_") as td:
        core = outer._load_core(Path(td))
        print("CORE_FILE", getattr(core, "__file__", None))
        print("CORE_SHA", getattr(outer, "CORE_SHA", None))

        for name in (
            "run_acquisition",
            "build_canonical_dependency_index",
            "fetch_or_cache",
            "validate_and_normalize_mission",
            "_route_rows_from_canonical",
        ):
            show_function(core, name)

        interesting = {}
        for key, value in sorted(vars(core).items()):
            upper = key.upper()
            if any(token in upper for token in ("EPHEM", "TARGET", "OBJECT", "MOON", "ACQUIS")):
                if isinstance(value, (dict, list, tuple, set, str, int, float, bool, type(None))):
                    try:
                        rendered = json.loads(json.dumps(value, default=str))
                    except Exception:
                        rendered = repr(value)
                    interesting[key] = rendered
        print("\n=== INTERESTING_GLOBALS ===")
        print(json.dumps(interesting, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
