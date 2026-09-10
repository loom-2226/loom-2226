from __future__ import annotations

"""Pinned Wayfarer engineering handoff for HUD qualification consumers.

The HUD is not engineering authority. This module loads exact machine-readable
artifacts imported from PR #96, verifies their source Git blob identities, and
normalizes only the fields the current HUD is permitted to consume. All source
objects remain NON-CANON and unresolved engineering states remain visibly open.
"""

import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONTRACT = "LOOM_HUD_WAYFARER_ENGINEERING_HANDOFF_V1"
ENGINEERING_SOURCE_BRANCH = "engineering/wayfarer-flight-system-qualification-v1"
ENGINEERING_SOURCE_COMMIT = "e2df887d5e901eed9378c7aeb7d4964040b9a7e6"
AUTHORITY = "HUD_CONSUMER_OF_PINNED_ENGINEERING_NON_CANON"

_ARTIFACTS = {
    "baseline": (
        "engineering/current/wayfarer_flight_system_baseline_v0.1.json",
        "a6045b0e325b805e99b3170d360f13f699c7bcf9",
    ),
    "attitude": (
        "engineering/current/wayfarer_q4_hud_attitude_envelope_v0.4.json",
        "b377372ff2711e1c5520024a1ec03bf32045867b",
    ),
    "power_thermal": (
        "engineering/current/wayfarer_q5_power_thermal_envelope_v0.2.json",
        "06352a0173c74b35fee42dedf9f7f0917e3aada1",
    ),
    "dispatch": (
        "engineering/current/wayfarer_q7_dispatch_doctrine_v0.1.json",
        "a89955712dd16849dfe0ce10829a74e81167111f",
    ),
    "feedstock": (
        "engineering/current/wayfarer_torch_feedstock_screening_v0.2.json",
        "418a9b53ce1836336202dd0dcb6c3962de43da1b",
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_verified(relative_path: str, expected_blob_sha1: str) -> dict[str, Any]:
    path = _repo_root() / relative_path
    data = path.read_bytes()
    actual = _git_blob_sha1(data)
    if actual != expected_blob_sha1:
        raise RuntimeError(
            f"Wayfarer engineering artifact drift: {relative_path} "
            f"expected Git blob {expected_blob_sha1}, got {actual}"
        )
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"engineering artifact must be a JSON object: {relative_path}")
    return value


@lru_cache(maxsize=1)
def _load_cached() -> dict[str, Any]:
    docs = {
        key: _load_verified(path, blob_sha)
        for key, (path, blob_sha) in _ARTIFACTS.items()
    }
    baseline = docs["baseline"]
    attitude = docs["attitude"]
    thermal = docs["power_thermal"]
    dispatch = docs["dispatch"]
    feedstock = docs["feedstock"]

    if baseline.get("status") != "ENGINEERING_BASELINE_NON_CANON":
        raise ValueError("Wayfarer baseline lost NON-CANON engineering status")
    if attitude.get("hud_use_allowed") is not True or attitude.get("canon_promotion_allowed") is not False:
        raise ValueError("Q4 artifact is not explicitly qualified for HUD-only use")
    if attitude.get("instantaneous_attitude_reset_allowed") is not False:
        raise ValueError("Q4 artifact no longer forbids instantaneous attitude reset")

    mass = baseline["mass_states"]
    torch = baseline["mobility_regimes"]["torch"]
    cards = {str(card["mode"]): dict(card) for card in torch["mode_cards"]}
    working_policy = dispatch["working_policy"]
    doctrine_text = dispatch["working_policy_interpretation"]

    primary_candidate = feedstock["provisional_doctrine"].get("primary")
    certified_species: list[str] = []
    # Q2 screening dispositions are deliberately not certification ratings.
    for item in feedstock.get("feeds", []):
        if item.get("screening") == "CERTIFIED":
            certified_species.append(str(item["species"]))

    return {
        "contract": CONTRACT,
        "authority": {
            "classification": AUTHORITY,
            "hud_consumer_only": True,
            "engineering_non_canon": True,
            "canon": False,
            "flight_control_authority": False,
            "navigator_targeting_authority": False,
        },
        "source": {
            "branch": ENGINEERING_SOURCE_BRANCH,
            "commit": ENGINEERING_SOURCE_COMMIT,
            "artifacts": {
                key: {"path": path, "git_blob_sha1": blob_sha}
                for key, (path, blob_sha) in _ARTIFACTS.items()
            },
        },
        "mass": {
            "status": baseline["status"],
            "dry_mass_t": float(mass["dry_mass_t"]),
            "reference_wet_mass_t": float(mass["reference_wet_mass_t"]),
            "normal_remass_allowance_t": float(mass["normal_remass_allowance_t"]),
            "protected_water_reserve_t": float(mass["protected_water_reserve_t"]),
            "working_fluid_water_inventory_t": float(mass["working_fluid_water_inventory_t"]),
        },
        "torch": {
            "status": torch["qualification_disposition"],
            "physics_class": torch["physics_class"],
            "mode_cards": cards,
            "feedstock_identity_status": torch["feedstock_identity"]["status"],
            "water_only_requirement": bool(torch["feedstock_identity"]["water_only_requirement"]),
            "jet_power_is_electrical_bus_power": bool(
                baseline["power_thermal"]["torch_jet_power_is_electrical_bus_power"]
            ),
            "ordinary_momentum_exchange_required": torch["physics_class"] == "ordinary_momentum_exchange",
        },
        "mobility_firewall": {
            "metric_status": baseline["mobility_regimes"]["metric"]["status"],
            "loom_status": baseline["mobility_regimes"]["loom"]["status"],
            "metric_ordinary_velocity_reset_allowed": bool(
                baseline["mobility_regimes"]["metric"]["ordinary_velocity_reset_allowed"]
            ),
            "torch_terminal_state_matching_required_when_needed": bool(
                baseline["mobility_regimes"]["metric"]["torch_terminal_state_matching_required_when_needed"]
            ),
            "hard_kills": list(baseline["hard_kills"]),
        },
        "attitude": {
            "status": attitude["status"],
            "authority": attitude["authority"],
            "instantaneous_attitude_reset_allowed": bool(attitude["instantaneous_attitude_reset_allowed"]),
            "control_cases": copy.deepcopy(attitude["control_cases"]),
            "mass_states": copy.deepcopy(attitude["mass_states"]),
            "not_qualified_for": list(attitude["not_qualified_for"]),
        },
        "power_thermal": copy.deepcopy(thermal),
        "dispatch": {
            "status": dispatch["status"],
            "authority_boundary": dispatch["authority_boundary"],
            "normal_dispatch_remass_t": float(working_policy["normal_dispatch_remass_t"]),
            "minimum_dispatch_remass_t": float(working_policy["minimum_dispatch_remass_t"]),
            "protected_optimizer_reserve_t": float(working_policy["protected_optimizer_reserve_t"]),
            "protected_water_reserve_t": float(mass["protected_water_reserve_t"]),
            "contingency_feed_reserve_t": float(working_policy["contingency_feed_reserve_t"]),
            "one_tank_isolation_fraction": float(working_policy["one_tank_isolation_fraction"]),
            "protected_optimizer_reserve_is_protected_water": False,
            "routine_optimizer_may_consume_protected_water": False,
            "torch_mode_authorization": copy.deepcopy(dispatch["torch_mode_authorization"]),
            "optimizer_rules": list(dispatch["optimizer_rules"]),
            "open_items": list(dispatch["open_items"]),
            "interpretation": copy.deepcopy(doctrine_text),
        },
        "feedstock": {
            "status": feedstock["status"],
            "authority_boundary": feedstock["authority_boundary"],
            "primary_candidate": primary_candidate,
            "provisional_doctrine": copy.deepcopy(feedstock["provisional_doctrine"]),
            "feeds": copy.deepcopy(feedstock["feeds"]),
            "certified_species": certified_species,
            "final_mode_ratings_closed": False,
            "required_final_rating_variables": list(feedstock["required_final_rating_variables"]),
        },
    }


def load_wayfarer_engineering_state() -> dict[str, Any]:
    """Return a defensive copy of the verified HUD-consumable engineering state."""

    return copy.deepcopy(_load_cached())
