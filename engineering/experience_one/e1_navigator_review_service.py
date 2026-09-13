from __future__ import annotations

"""Read-only Experience One Navigator comparison service.

The service never commits a flight. Production candidate generation runs the
existing Navigator path against a temporary copy of the supplied campaign and
intentionally stops at Navigator's plan-selection prompt. The source campaign is
hashed before and after and must remain bit-identical.
"""

import builtins
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable, Mapping, Sequence

# The qualified disposable harness intentionally imports its sibling qualification
# adapters as direct modules because it is also a standalone Pixel script. Make
# that established script layout available before importing it as a package here.
QUAL_DIR = Path(__file__).resolve().parent / "qualification"
if str(QUAL_DIR) not in sys.path:
    sys.path.insert(0, str(QUAL_DIR))

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent
from engineering.experience_one.e1_navigator_interaction_adapter import review_from_navigator_output
from engineering.experience_one.qualification import e1_neptune_disposable_campaign as harness

CandidateSource = Callable[[Path, FlightIntent, Mapping[str, Any]], Sequence[Mapping[str, Any]]]


class _ReviewReady(RuntimeError):
    pass


def _required_number(raw: Mapping[str, Any], key: str) -> float:
    value = raw.get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Navigator candidate missing numeric {key}") from None


def build_review_bundle(
    intent: FlightIntent,
    navigator_state_id: str,
    navigator_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidates = [dict(row) for row in navigator_candidates]
    if not candidates:
        raise ValueError("Navigator returned no comparison candidates")
    review = review_from_navigator_output(intent, navigator_state_id, candidates)
    display: list[dict[str, Any]] = []
    for index, row in enumerate(candidates, start=1):
        metric = str(row.get("metric") or "").strip()
        torch = str(row.get("torch") or "").strip()
        thermal = str(row.get("thermal") or "").strip()
        if not metric or not torch or not thermal:
            raise ValueError("Navigator candidate missing display fields")
        display.append({
            "plan_number": index,
            "metric": metric,
            "torch": torch,
            "total_s": _required_number(row, "total_s"),
            "remass_used_t": _required_number(row, "remass_used_t"),
            "arrival_remass_t": _required_number(row, "arrival_remass_t"),
            "thermal": thermal,
        })
    return {
        "schema": "LOOM_E1_NAVIGATOR_REVIEW_BUNDLE_V1",
        "review": review,
        "candidate_display": display,
        "planner_authority": "NAVIGATOR",
        "calculation_authority": "NAVIGATOR_ONLY",
        "caller_calculation_authority": "ZERO",
        "execution_authority": "NONE_REVIEW_ONLY",
        "campaign_mutation": "NONE",
    }


def _navigator_candidate_source(
    root: Path,
    intent: FlightIntent,
    state: Mapping[str, Any],
) -> Sequence[Mapping[str, Any]]:
    repo = harness.DEFAULT_REPO.resolve()
    navmod = harness.load_module(repo / "src" / "loom_navigator_core.py")
    captured: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="loom_e1_review_") as temp_dir:
        temp_root = Path(temp_dir)
        harness.prepare_disposable(root, temp_root)

        original_path_ctor = navmod.Path
        original_input = builtins.input
        original_load_core = navmod._load_core
        original_candidate_plans = navmod._candidate_plans
        download_literal = "/storage/emulated/0/Download"

        def redirected_path(*parts):
            if len(parts) == 1 and str(parts[0]) == download_literal:
                return temp_root
            return Path(*parts)

        navmod.Path = redirected_path
        navmod._MVP_INJECTED_COMMAND = {
            "BASE_STATE": str(state["state_id"]),
            "ELAPSED_HOURS": "0",
            "LOCATION": str(state["location_token"]),
            "DESTINATION": intent.destination.strip().upper(),
            "PRIORITY": intent.priority.strip().upper(),
            "CONSIDER_GRAVITY_ASSISTS": "NO",
            "CONSIDER_PRECISION_COLLAPSE": "NO",
            "CONSIDER_SOLAR_WEATHER": "NO",
            "CONSIDER_EXCHANGE_ASSIST": "NO",
            "NOTES": "Experience One HUD read-only Navigator comparison request.",
        }

        def observed_candidate_plans(*call_args, **call_kwargs):
            candidates = original_candidate_plans(*call_args, **call_kwargs)
            captured[:] = [dict(row) for row in candidates[:8]]
            return candidates

        def scripted_input(prompt=""):
            upper = str(prompt).upper()
            if "OPERATIONAL STRATEGY" in upper:
                return "1"
            if "SELECT PLAN" in upper:
                if not captured:
                    raise RuntimeError("Navigator comparison candidates were not captured")
                raise _ReviewReady("Navigator comparison ready")
            raise RuntimeError(f"unexpected Navigator review prompt: {prompt!r}")

        def load_core_for_review(internal):
            core = original_load_core(internal)
            harness.install_e1_flight_qualification_adapters(core)
            core.serve_sequence_d = lambda *a, **k: None
            return core

        builtins.input = scripted_input
        navmod.Path = redirected_path
        navmod._load_core = load_core_for_review
        navmod._candidate_plans = observed_candidate_plans
        try:
            try:
                navmod._navigator_one_action_main()
            except _ReviewReady:
                pass
        finally:
            builtins.input = original_input
            navmod.Path = original_path_ctor
            navmod._load_core = original_load_core
            navmod._candidate_plans = original_candidate_plans

    if not captured:
        raise RuntimeError("Navigator produced no review candidates")
    return captured


class NavigatorReviewService:
    def __init__(self, candidate_source: CandidateSource | None = None) -> None:
        self._candidate_source = candidate_source or _navigator_candidate_source

    def generate(self, root: Path, intent: FlightIntent) -> dict[str, Any]:
        campaign_root = Path(root).resolve()
        state_path = campaign_root / "LOOM_STATE_V1.json"
        if not state_path.exists():
            raise FileNotFoundError(f"campaign state not found: {state_path}")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("campaign state must be a JSON object")
        state_id = str(state.get("state_id") or "").strip()
        location = str(state.get("location_token") or "").strip().upper()
        if not state_id or not location:
            raise ValueError("campaign state lacks state_id/location_token")
        destination = intent.destination.strip().upper()
        if destination == location:
            raise ValueError("destination equals current location")

        before = harness.campaign_hashes(campaign_root)
        candidates = self._candidate_source(campaign_root, intent, state)
        after = harness.campaign_hashes(campaign_root)
        if before != after:
            raise RuntimeError("SOURCE CAMPAIGN MUTATED — HARD FAIL")

        bundle = build_review_bundle(intent, state_id, candidates)
        bundle["source_campaign_hashes_before"] = before
        bundle["source_campaign_hashes_after"] = after
        bundle["source_campaign_unchanged_pass"] = True
        return bundle
