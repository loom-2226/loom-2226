#!/usr/bin/env python3
from __future__ import annotations

"""Experience One — Ceres→Neptune disposable campaign qualification.

This is a qualification harness, not a second flight implementation. It drives the
EXISTING Navigator campaign path against disposable copies of campaign artifacts,
then verifies typed review/authorization, commit, arrival, restart and replay. The
real campaign is hashed before and after and must remain bit-identical.
"""

import argparse
import builtins
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from e1_route_scoped_ephemeris import install_route_scoped_acquisition
from e1_flight_runtime_determinism import install_flight_runtime_determinism

CAMPAIGN_FILES = ("LOOM_STATE_V1.json", "LOOM_STATE_V1.bak", "LOOM_CAMPAIGN_HISTORY.jsonl.gz")
READ_INPUTS = ("LOOM_Navigator_Cache_v1", "LOOM_2226_CIVSTATE.sqlite3")
ANDROID_ROOT = Path("/storage/emulated/0/Download")
DEFAULT_ROOT = ANDROID_ROOT if ANDROID_ROOT.exists() else Path.cwd()
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_REPO = SCRIPT_PATH.parents[3]


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


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("loom_e1_neptune_nav", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_or_link(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    try:
        os.symlink(src, dst, target_is_directory=src.is_dir())
        return
    except Exception:
        pass
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def prepare_disposable(real_root: Path, temp_root: Path) -> None:
    if not (real_root / "LOOM_STATE_V1.json").exists() or not (real_root / "LOOM_CAMPAIGN_HISTORY.jsonl.gz").exists():
        raise RuntimeError("existing state and history required; refusing to create or infer a campaign")
    for name in CAMPAIGN_FILES:
        src = real_root / name
        if src.exists():
            shutil.copy2(src, temp_root / name)
    for name in READ_INPUTS:
        copy_or_link(real_root / name, temp_root / name)
    for path in real_root.iterdir():
        if path.name in CAMPAIGN_FILES or path.name in READ_INPUTS:
            continue
        low = path.name.lower()
        if path.is_file() and ("b1" in low or ("navigator" in low and path.suffix.lower() in (".zip", ".json"))):
            copy_or_link(path, temp_root / path.name)


def install_e1_flight_qualification_adapters(core: Any) -> None:
    install_route_scoped_acquisition(core)
    install_flight_runtime_determinism(core)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--destination", default="NEPTUNE_SYSTEM")
    parser.add_argument("--priority", default="BALANCED")
    parser.add_argument("--plan", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_ROOT / "E1_NEPTUNE_QUALIFICATION_RESULT.json")
    args = parser.parse_args()

    real_root = args.root.resolve()
    repo = args.repo.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    from engineering.experience_one.e1_flight_interaction_contract import (
        FlightAuthorization,
        FlightIntent,
        IntentOrigin,
    )
    from engineering.experience_one.e1_navigator_interaction_adapter import (
        authorized_request_for_finalized_navigator_plan,
        review_from_navigator_output,
    )

    before = campaign_hashes(real_root)
    if before["LOOM_STATE_V1.json"] is None or before["LOOM_CAMPAIGN_HISTORY.jsonl.gz"] is None:
        raise RuntimeError("real campaign artifacts missing")

    navmod = load_module(repo / "src" / "loom_navigator_core.py")
    real_state = json.loads((real_root / "LOOM_STATE_V1.json").read_text(encoding="utf-8"))
    origin = str(real_state["location_token"])
    destination = str(args.destination)
    if origin.upper() not in {"CERES", "CERES_SYSTEM"}:
        raise RuntimeError(f"qualification requires Ceres start; observed {origin!r}")
    if destination.upper() == origin.upper():
        raise RuntimeError("destination equals current location")

    result: dict[str, Any] = {
        "schema": "LOOM_E1_NEPTUNE_QUALIFICATION_RESULT_V1",
        "origin": origin,
        "destination": destination,
        "priority": args.priority.upper(),
        "authorized_plan_number": args.plan,
        "authority_path": "EXISTING_NAVIGATOR_CAMPAIGN_FLIGHT_PATH",
        "interaction_contract": "LOOM_E1_FLIGHT_INTENT_V1",
        "ephemeris_scope": "ROUTE_REQUIRED_ONLY",
        "determinism_scope": "AUTHORITATIVE_FLIGHT_RUNTIME_ONLY",
        "presentation_scope": "SEQUENCE_B_C_D_OUT_OF_SCOPE_FOR_FLIGHT_SEAM",
        "real_campaign_hashes_before": before,
    }

    typed: dict[str, Any] = {}
    candidate_snapshot: list[dict[str, Any]] = []
    intent = FlightIntent(
        destination=destination,
        priority=args.priority,
        origin=IntentOrigin.HUMAN,
        requested_by="PIXEL_QUALIFICATION_OPERATOR",
    )

    with tempfile.TemporaryDirectory(prefix="loom_e1_neptune_") as temp_dir:
        temp_root = Path(temp_dir)
        prepare_disposable(real_root, temp_root)

        original_path_ctor = navmod.Path
        original_input = builtins.input
        original_print = builtins.print
        original_load_core = navmod._load_core
        original_candidate_plans = navmod._candidate_plans
        download_literal = "/storage/emulated/0/Download"

        def redirected_path(*parts):
            if len(parts) == 1 and str(parts[0]) == download_literal:
                return temp_root
            return Path(*parts)

        navmod.Path = redirected_path
        navmod._MVP_INJECTED_COMMAND = {
            "BASE_STATE": real_state["state_id"],
            "ELAPSED_HOURS": "0",
            "LOCATION": origin,
            "DESTINATION": destination,
            "PRIORITY": args.priority.upper(),
            "CONSIDER_GRAVITY_ASSISTS": "NO",
            "CONSIDER_PRECISION_COLLAPSE": "NO",
            "CONSIDER_SOLAR_WEATHER": "NO",
            "CONSIDER_EXCHANGE_ASSIST": "NO",
            "NOTES": "Experience One Neptune disposable qualification.",
        }

        def observed_candidate_plans(*call_args, **call_kwargs):
            candidates = original_candidate_plans(*call_args, **call_kwargs)
            candidate_snapshot[:] = [dict(c) for c in candidates[:8]]
            typed["review"] = review_from_navigator_output(
                intent,
                str(real_state["state_id"]),
                candidate_snapshot,
            )
            return candidates

        def observed_print(*objects, **kwargs):
            text = " ".join(str(obj) for obj in objects)
            match = re.search(r"PLAN SHA\s+([0-9a-fA-F]{64})", text)
            if match:
                typed["finalized_plan_sha256"] = match.group(1).lower()
            return original_print(*objects, **kwargs)

        def scripted_input(prompt=""):
            upper = str(prompt).upper()
            if "OPERATIONAL STRATEGY" in upper:
                value = "1"
            elif "SELECT PLAN" in upper:
                if "review" not in typed:
                    raise RuntimeError("typed review was not captured before plan selection")
                value = str(args.plan)
            elif "COMMIT FLIGHT?" in upper:
                review_payload = typed.get("review")
                final_sha = typed.get("finalized_plan_sha256")
                if not review_payload or not final_sha:
                    raise RuntimeError("typed authorization prerequisites missing before commit")
                authorization = FlightAuthorization(
                    review_sha256=str(review_payload["review_sha256"]),
                    selected_plan_number=args.plan,
                    finalized_plan_sha256=str(final_sha),
                    authorized_by="PIXEL_QUALIFICATION_OPERATOR",
                    explicit=True,
                )
                execution_request = authorized_request_for_finalized_navigator_plan(
                    intent,
                    str(real_state["state_id"]),
                    candidate_snapshot,
                    authorization,
                    current_navigator_state_id=str(real_state["state_id"]),
                    current_finalized_plan_sha256=str(final_sha),
                )
                typed["authorization"] = authorization.payload()
                typed["execution_request"] = execution_request
                value = "y"
            else:
                raise RuntimeError(f"unexpected interactive prompt: {prompt!r}")
            original_print(f"{prompt}{value}")
            return value

        def load_core_without_server_hold(internal):
            core = original_load_core(internal)
            install_e1_flight_qualification_adapters(core)
            core.serve_sequence_d = lambda *a, **k: original_print("E1 NEPTUNE SERVER HOLD SKIPPED / PRESENTATION OUT OF SCOPE")
            return core

        builtins.input = scripted_input
        builtins.print = observed_print
        navmod._load_core = load_core_without_server_hold
        navmod._candidate_plans = observed_candidate_plans
        try:
            navmod._navigator_one_action_main()
        finally:
            builtins.input = original_input
            builtins.print = original_print
            navmod.Path = original_path_ctor
            navmod._load_core = original_load_core
            navmod._candidate_plans = original_candidate_plans

        state_path = temp_root / navmod.STATE_FILE
        backup_path = temp_root / navmod.BACKUP_FILE
        restarted, mode = navmod._setup_campaign(state_path, backup_path, temp_root / navmod.HISTORY_FILE)
        ledger = navmod.HistoryLedger(temp_root, restarted)
        restarted = navmod._history_recover_if_needed(ledger, restarted, state_path, backup_path)
        ledger.state = restarted

        arrivals = [r for r in ledger.records if r.get("record_type") == "FLIGHT_ARRIVED"]
        if not arrivals:
            raise RuntimeError("no FLIGHT_ARRIVED record after authorized flight")
        arrival = arrivals[-1]
        flight_id = arrival.get("flight_id")
        rows = ledger.flight_records(flight_id)
        committed = next((r for r in rows if r.get("record_type") == "FLIGHT_COMMITTED"), None)
        if committed is None:
            raise RuntimeError("no FLIGHT_COMMITTED record for arrived flight")

        committed_plan_sha = committed.get("details", {}).get("plan_sha256")
        typed_request = typed.get("execution_request") or {}
        typed_interaction_pass = bool(
            typed.get("review")
            and typed.get("authorization")
            and typed_request
            and typed_request.get("selected_plan_number") == args.plan
            and typed_request.get("finalized_plan_sha256") == committed_plan_sha
            and typed_request.get("execution_authority") == "NAVIGATOR_ONLY"
            and typed_request.get("requires_navigator_revalidation") is True
        )
        if not typed_interaction_pass:
            raise RuntimeError("typed E1 review/authorization did not bind to committed Navigator plan")

        core = navmod._load_core(temp_root / "LOOM_E1_NEPTUNE_REPLAY")
        install_e1_flight_qualification_adapters(core)
        replay_ok = bool(navmod._replay_flight(core, ledger, flight_id, temp_root))
        restart_location = str(restarted.get("location_token"))
        destination_pass = restart_location.upper() in {destination.upper(), "NEPTUNE", "NEPTUNE_SYSTEM"}

        result.update(
            {
                "flight_id": flight_id,
                "flight_record_types": [r.get("record_type") for r in rows],
                "disposable_mode_after_restart": mode,
                "restart_state_id": restarted.get("state_id"),
                "restart_state_sha256": restarted.get("state_sha256"),
                "restart_location": restart_location,
                "restart_epoch_utc": restarted.get("epoch_utc"),
                "restart_remass_t": restarted.get("ship", {}).get("remass_t"),
                "restart_wet_mass_t": restarted.get("ship", {}).get("wet_mass_t"),
                "last_flight": restarted.get("last_flight"),
                "committed_plan_sha256": committed_plan_sha,
                "typed_review_sha256": typed["review"]["review_sha256"],
                "typed_authorization_contract": typed["authorization"]["contract"],
                "typed_execution_request_contract": typed_request["contract"],
                "typed_interaction_pass": typed_interaction_pass,
                "replay_pass": replay_ok,
                "restart_destination_pass": destination_pass,
                "committed_and_arrived_pass": True,
            }
        )

    after = campaign_hashes(real_root)
    result["real_campaign_hashes_after"] = after
    result["real_campaign_unchanged_pass"] = before == after
    result["qualification_pass"] = bool(
        result["real_campaign_unchanged_pass"]
        and result["typed_interaction_pass"]
        and result["replay_pass"]
        and result["restart_destination_pass"]
        and result["committed_and_arrived_pass"]
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if not result["real_campaign_unchanged_pass"]:
        raise RuntimeError("REAL CAMPAIGN MUTATED — HARD FAIL")
    return 0 if result["qualification_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
