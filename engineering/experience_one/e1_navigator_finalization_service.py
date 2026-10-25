from __future__ import annotations

"""Bounded Navigator finalization for Experience One.

The service re-runs the existing Navigator path against a temporary campaign copy,
selects exactly one already-reviewed candidate, captures Navigator's final solved
plan and plan SHA, and declines commit. The supplied campaign root must remain
bit-identical. This service creates no authorization and performs no execution.
"""

import builtins
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable, Mapping

QUAL_DIR = Path(__file__).resolve().parent / "qualification"
if str(QUAL_DIR) not in sys.path:
    sys.path.insert(0, str(QUAL_DIR))

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent
from engineering.experience_one.qualification import e1_neptune_disposable_campaign as harness

FinalizationSource = Callable[[Path, FlightIntent, Mapping[str, Any], int], tuple[Mapping[str, Any], str]]


def _review_mapping(review_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    review = review_bundle.get("review")
    if not isinstance(review, Mapping):
        raise ValueError("review bundle missing typed review")
    if str(review.get("planner_authority") or "") != "NAVIGATOR":
        raise ValueError("review planner authority must be NAVIGATOR")
    if str(review.get("execution_authority") or "") != "NONE_REVIEW_ONLY":
        raise ValueError("review must remain review-only")
    return review


def build_finalization_bundle(
    review_bundle: Mapping[str, Any],
    selected_plan_number: int,
    finalized_plan: Mapping[str, Any],
    finalized_plan_sha256: str,
) -> dict[str, Any]:
    review = _review_mapping(review_bundle)
    candidates = review.get("candidates") or []
    selected = None
    for candidate in candidates:
        if isinstance(candidate, Mapping) and int(candidate.get("plan_number", -1)) == int(selected_plan_number):
            selected = dict(candidate)
            break
    if selected is None:
        raise ValueError("selected plan was not present in reviewed Navigator candidates")
    digest = str(finalized_plan_sha256).lower().strip()
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("finalized plan SHA must be a 64-character hex digest")
    state_id = str(review.get("navigator_state_id") or "").strip()
    review_sha = str(review.get("review_sha256") or "").strip()
    if not state_id or not review_sha:
        raise ValueError("review lacks state/hash binding")
    return {
        "schema": "LOOM_E1_NAVIGATOR_FINALIZATION_V1",
        "navigator_state_id": state_id,
        "review_sha256": review_sha,
        "selected_plan_number": int(selected_plan_number),
        "selected_candidate": selected,
        "finalized_plan": dict(finalized_plan),
        "finalized_plan_sha256": digest,
        "planner_authority": "NAVIGATOR",
        "calculation_authority": "NAVIGATOR_ONLY",
        "execution_authority": "NONE_FINALIZED_NOT_AUTHORIZED",
        "campaign_mutation": "NONE",
    }


def _navigator_finalization_source(
    root: Path,
    intent: FlightIntent,
    review_bundle: Mapping[str, Any],
    selected_plan_number: int,
) -> tuple[Mapping[str, Any], str]:
    review = _review_mapping(review_bundle)
    repo = harness.DEFAULT_REPO.resolve()
    navmod = harness.load_module(repo / "src" / "loom_navigator_core.py")
    captured_plan: dict[str, Any] = {}

    with tempfile.TemporaryDirectory(prefix="loom_e1_finalize_") as td:
        temp_root = Path(td)
        harness.prepare_disposable(root, temp_root)
        state = json.loads((temp_root / "LOOM_STATE_V1.json").read_text(encoding="utf-8"))

        original_path = navmod.Path
        original_input = builtins.input
        original_load_core = navmod._load_core
        original_plan_summary = navmod._plan_summary
        download_literal = "/storage/emulated/0/Download"

        def redirected_path(*parts):
            if len(parts) == 1 and str(parts[0]) == download_literal:
                return temp_root
            return Path(*parts)

        def observed_plan_summary(*args, **kwargs):
            plan = original_plan_summary(*args, **kwargs)
            captured_plan.clear()
            captured_plan.update(dict(plan))
            return plan

        def scripted_input(prompt=""):
            upper = str(prompt).upper()
            if "OPERATIONAL STRATEGY" in upper:
                return "1"
            if "SELECT PLAN" in upper:
                return str(int(selected_plan_number))
            if "COMMIT FLIGHT" in upper:
                return "n"
            raise RuntimeError(f"unexpected Navigator finalization prompt: {prompt!r}")

        def load_core(internal):
            core = original_load_core(internal)
            harness.install_e1_flight_qualification_adapters(core)
            core.serve_sequence_d = lambda *a, **k: None
            return core

        navmod.Path = redirected_path
        navmod._load_core = load_core
        navmod._plan_summary = observed_plan_summary
        builtins.input = scripted_input
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
            "NOTES": "Experience One HUD Navigator finalization request; commit prohibited.",
        }
        try:
            navmod._navigator_one_action_main()
        finally:
            builtins.input = original_input
            navmod.Path = original_path
            navmod._load_core = original_load_core
            navmod._plan_summary = original_plan_summary

        if not captured_plan:
            raise RuntimeError("Navigator final plan was not captured")
        plan_sha = navmod._sha_bytes(navmod._canon(captured_plan))

    if str(review.get("navigator_state_id")) != str(state.get("state_id")):
        raise ValueError("Navigator state changed between review and finalization")
    return captured_plan, plan_sha


class NavigatorFinalizationService:
    def __init__(self, source: FinalizationSource | None = None) -> None:
        self._source = source or _navigator_finalization_source

    def finalize(
        self,
        root: Path,
        intent: FlightIntent,
        review_bundle: Mapping[str, Any],
        selected_plan_number: int,
    ) -> dict[str, Any]:
        campaign_root = Path(root).resolve()
        before = harness.campaign_hashes(campaign_root)
        plan, plan_sha = self._source(campaign_root, intent, review_bundle, int(selected_plan_number))
        after = harness.campaign_hashes(campaign_root)
        if before != after:
            raise RuntimeError("SOURCE CAMPAIGN MUTATED — HARD FAIL")
        bundle = build_finalization_bundle(review_bundle, int(selected_plan_number), plan, plan_sha)
        bundle["source_campaign_hashes_before"] = before
        bundle["source_campaign_hashes_after"] = after
        bundle["source_campaign_unchanged_pass"] = True
        return bundle
