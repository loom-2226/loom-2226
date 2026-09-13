from __future__ import annotations

"""Governed E1 execution seam. Navigator alone may mutate campaign state."""

import builtins
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable, Mapping

QUAL_DIR = Path(__file__).resolve().parent / "qualification"
if str(QUAL_DIR) not in sys.path:
    sys.path.insert(0, str(QUAL_DIR))

from engineering.experience_one.e1_flight_interaction_contract import FlightAuthorization, FlightIntent
from engineering.experience_one.e1_navigator_interaction_adapter import authorized_request_for_finalized_navigator_plan, review_from_navigator_output
from engineering.experience_one.qualification import e1_neptune_disposable_campaign as harness

ExecutionSource = Callable[[Path, FlightIntent, Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]


def _preflight(review_bundle: Mapping[str, Any], finalization: Mapping[str, Any], authorization: Mapping[str, Any]) -> None:
    review = review_bundle.get("review") or {}
    if authorization.get("explicit") is not True:
        raise ValueError("execution requires explicit human authorization")
    if str(authorization.get("execution_authority")) != "REQUEST_ONLY_NAVIGATOR_MUST_REVALIDATE":
        raise ValueError("authorization is not a Navigator execution request")
    if str(authorization.get("review_sha256")) != str(review.get("review_sha256")) or str(finalization.get("review_sha256")) != str(review.get("review_sha256")):
        raise ValueError("authorization/review binding changed")
    if int(authorization.get("selected_plan_number", -1)) != int(finalization.get("selected_plan_number", -2)):
        raise ValueError("authorized selected plan changed")
    if str(authorization.get("finalized_plan_sha256")) != str(finalization.get("finalized_plan_sha256")):
        raise ValueError("authorized final plan hash changed")
    if str(finalization.get("navigator_state_id")) != str(review.get("navigator_state_id")):
        raise ValueError("finalized Navigator state changed")


def _navigator_execution_source(root: Path, intent: FlightIntent, review_bundle: Mapping[str, Any], finalization: Mapping[str, Any], authorization_raw: Mapping[str, Any]) -> Mapping[str, Any]:
    repo = harness.DEFAULT_REPO.resolve()
    navmod = harness.load_module(repo / "src" / "loom_navigator_core.py")
    state_before = json.loads((root / "LOOM_STATE_V1.json").read_text(encoding="utf-8"))
    reviewed = review_bundle.get("review") or {}
    selected = int(finalization["selected_plan_number"])
    candidate_snapshot: list[dict[str, Any]] = []
    observed: dict[str, Any] = {}

    authorization = FlightAuthorization(
        review_sha256=str(authorization_raw["review_sha256"]), selected_plan_number=selected,
        finalized_plan_sha256=str(authorization_raw["finalized_plan_sha256"]),
        authorized_by=str(authorization_raw["authorized_by"]), explicit=True,
    )

    original_path = navmod.Path; original_input = builtins.input; original_print = builtins.print
    original_load_core = navmod._load_core; original_candidates = navmod._candidate_plans
    download_literal = "/storage/emulated/0/Download"

    def redirected_path(*parts):
        if len(parts) == 1 and str(parts[0]) == download_literal: return root
        return Path(*parts)

    def observed_candidates(*args, **kwargs):
        rows = original_candidates(*args, **kwargs)
        candidate_snapshot[:] = [dict(c) for c in rows[:8]]
        fresh = review_from_navigator_output(intent, str(state_before["state_id"]), candidate_snapshot)
        if str(fresh["review_sha256"]) != str(reviewed.get("review_sha256")):
            raise RuntimeError("Navigator candidate review changed before execution")
        return rows

    def observed_print(*objects, **kwargs):
        text = " ".join(str(x) for x in objects)
        m = re.search(r"PLAN SHA\s+([0-9a-fA-F]{64})", text)
        if m: observed["final_sha"] = m.group(1).lower()
        f = re.search(r"FLIGHT ID\s+(F\d+)", text)
        if f: observed["flight_id"] = f.group(1)
        return original_print(*objects, **kwargs)

    def scripted_input(prompt=""):
        upper = str(prompt).upper()
        if "OPERATIONAL STRATEGY" in upper: value = "1"
        elif "SELECT PLAN" in upper: value = str(selected)
        elif "COMMIT FLIGHT" in upper:
            final_sha = observed.get("final_sha")
            if not final_sha: raise RuntimeError("Navigator final SHA not observed before commit")
            request = authorized_request_for_finalized_navigator_plan(
                intent, str(state_before["state_id"]), candidate_snapshot, authorization,
                current_navigator_state_id=str(state_before["state_id"]), current_finalized_plan_sha256=str(final_sha),
            )
            if str(final_sha) != str(finalization["finalized_plan_sha256"]):
                raise RuntimeError("Navigator final plan SHA changed after authorization")
            observed["execution_request"] = request
            value = "y"
        else: raise RuntimeError(f"unexpected Navigator execution prompt: {prompt!r}")
        original_print(f"{prompt}{value}"); return value

    def load_core(internal):
        core = original_load_core(internal); harness.install_e1_flight_qualification_adapters(core)
        core.serve_sequence_d = lambda *a, **k: original_print("E1 HUD EXECUTION SERVER HOLD SKIPPED")
        return core

    navmod.Path = redirected_path; builtins.input = scripted_input; builtins.print = observed_print
    navmod._load_core = load_core; navmod._candidate_plans = observed_candidates
    navmod._MVP_INJECTED_COMMAND = {
        "BASE_STATE": str(state_before["state_id"]), "ELAPSED_HOURS": "0", "LOCATION": str(state_before["location_token"]),
        "DESTINATION": intent.destination.strip().upper(), "PRIORITY": intent.priority.strip().upper(),
        "CONSIDER_GRAVITY_ASSISTS": "NO", "CONSIDER_PRECISION_COLLAPSE": "NO", "CONSIDER_SOLAR_WEATHER": "NO",
        "CONSIDER_EXCHANGE_ASSIST": "NO", "NOTES": "Experience One HUD explicitly authorized Navigator execution.",
    }
    try:
        navmod._navigator_one_action_main()
    finally:
        builtins.input = original_input; builtins.print = original_print; navmod.Path = original_path
        navmod._load_core = original_load_core; navmod._candidate_plans = original_candidates

    state_after = json.loads((root / "LOOM_STATE_V1.json").read_text(encoding="utf-8"))
    if str(state_after.get("state_id")) == str(state_before.get("state_id")):
        raise RuntimeError("Navigator execution returned without campaign state transition")
    if str(state_after.get("location_token", "")).upper() != intent.destination.strip().upper():
        raise RuntimeError("Navigator execution did not arrive at authorized destination")
    return {
        "state_id": state_after["state_id"], "location_token": state_after["location_token"], "epoch_utc": state_after["epoch_utc"],
        "flight_id": observed.get("flight_id") or state_after.get("last_flight_id") or "UNKNOWN",
        "execution_request": observed.get("execution_request"),
    }


class NavigatorExecutionService:
    def __init__(self, source: ExecutionSource | None = None) -> None:
        self._source = source or _navigator_execution_source

    def execute(self, root: Path, intent: FlightIntent, review_bundle: Mapping[str, Any], finalization: Mapping[str, Any], authorization: Mapping[str, Any]) -> dict[str, Any]:
        _preflight(review_bundle, finalization, authorization)
        result = dict(self._source(Path(root).resolve(), intent, review_bundle, finalization, authorization))
        result.update({"schema": "LOOM_E1_NAVIGATOR_EXECUTION_RESULT_V1", "execution_authority": "NAVIGATOR", "campaign_mutated_by_navigator": True})
        return result
