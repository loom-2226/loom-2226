from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

APP_VERSION = "LOOM_SHIPYARD_BUILD_CAMPAIGN_PIXEL_v0.2"
HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]
SRC = APP_ROOT / "src"
SYN = SRC / "qualification" / "synthesis"
ROOT_SYN = APP_ROOT / "qualification" / "synthesis"
for p in (SRC, SYN, ROOT_SYN):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from generative_shipyard_campaign import run_and_persist_wayfarer_campaign
from LOOM_Shipyard_GLB_Library import default_db


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run the bounded LOOM iterative Wayfarer shipbuilding campaign")
    ap.add_argument("--db", help="Shipyard design-ledger SQLite path")
    ap.add_argument("--seed", type=int, default=2226)
    ap.add_argument("--open-library", action="store_true", help="Open visual workspace after successful build")
    args = ap.parse_args(argv)
    db = Path(args.db).expanduser().resolve() if args.db else default_db()
    print("LOOM SHIPYARD BUILD CAMPAIGN")
    print("============================")
    print(APP_VERSION)
    print(f"DB: {db}")
    print(f"SEED: {args.seed}")
    try:
        report = run_and_persist_wayfarer_campaign(db, args.seed)
    except Exception as exc:
        print(f"SHIPBUILD FAILED: {type(exc).__name__}: {exc}")
        return 2
    print(f"CAMPAIGN: {report['campaign_id']}")
    print(f"CANDIDATES: {report['candidate_count']}")
    print(f"SURVIVED: {report['survivor_count']}")
    print(f"REJECTED: {report['rejected_count']}")
    print(f"PARETO: {report['pareto_count']}")
    print(f"GLB ASSETS: {report['visual_asset_count']}")
    print(f"RESULT: {report['interpretation']}")
    print(f"NAV DIFFERENTIATED: {report['dynamics_differentiation']['translational_mission_behavior_differentiated']}")
    readiness = report["dynamics_readiness"]
    print(f"DYNAMICS READINESS: {readiness['status']}")
    print(f"TRANSLATIONAL CORE READY: {readiness['translational_core_ready']}")
    if readiness["missing_required_admissions"]:
        print("MISSING PHYSICAL ADMISSIONS:")
        for gate in readiness["missing_required_admissions"]:
            print(f"  - {gate}")
    feed = readiness["remass_feed_evidence"]
    print(f"REMASS FEED: {feed['phase11_selection_status']}; LIVE INPUTS={feed['phase11_live_engineering_input_admission_count']}")
    if report.get("next_blocker"):
        print(f"NEXT BLOCKER: {report['next_blocker']}")
    if report.get("next_admission_priority"):
        print(f"NEXT ADMISSION PRIORITY: {report['next_admission_priority']}")
    print("AUTHORITY: RESEARCH ONLY; NO FLIGHT/CANON/PRODUCTION PROMOTION")
    if args.open_library:
        workspace = APP_ROOT / "deploy" / "android" / "LOOM_Shipyard_Visual_Workspace.py"
        if not workspace.is_file():
            print(f"Workspace not found: {workspace}")
            return 3
        return subprocess.call([sys.executable, str(workspace), "--db", str(db)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
