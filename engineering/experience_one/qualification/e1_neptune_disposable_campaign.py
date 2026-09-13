#!/usr/bin/env python3
from __future__ import annotations

"""Experience One — Ceres→Neptune disposable campaign qualification.

This is a qualification harness, not a second flight implementation. It drives the
EXISTING Navigator campaign path against disposable copies of campaign artifacts,
then verifies commit, arrival, restart and replay. The real campaign is hashed
before and after and must remain bit-identical.
"""

import argparse
import builtins
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

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
        "real_campaign_hashes_before": before,
    }

    with tempfile.TemporaryDirectory(prefix="loom_e1_neptune_") as temp_dir:
        temp_root = Path(temp_dir)
        prepare_disposable(real_root, temp_root)

        original_path_ctor = navmod.Path
        original_input = builtins.input
        original_load_core = navmod._load_core
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

        responses = iter(["1", str(args.plan), "y"])

        def scripted_input(prompt=""):
            try:
                value = next(responses)
            except StopIteration:
                raise RuntimeError(f"unexpected interactive prompt: {prompt!r}")
            print(f"{prompt}{value}")
            return value

        def load_core_without_server_hold(internal):
            core = original_load_core(internal)
            core.serve_sequence_d = lambda *a, **k: print("E1 NEPTUNE SERVER HOLD SKIPPED / PRESENTATION OUT OF SCOPE")
            return core

        builtins.input = scripted_input
        navmod._load_core = load_core_without_server_hold
        try:
            navmod._navigator_one_action_main()
        finally:
            builtins.input = original_input
            navmod.Path = original_path_ctor
            navmod._load_core = original_load_core

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

        core = navmod._load_core(temp_root / "LOOM_E1_NEPTUNE_REPLAY")
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
                "committed_plan_sha256": committed.get("details", {}).get("plan_sha256"),
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
