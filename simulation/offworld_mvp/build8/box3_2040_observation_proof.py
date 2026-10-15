"""Opt-in 2040 paid region study against an existing 2026 sealed WORLD.

Research proof only. Requires an isolated World Authority instance supplied by caller.
Build 7 and the kernel are never modified. No automatic study-review is invoked.
"""
from __future__ import annotations

from decimal import Decimal as D
import os
from pathlib import Path

import psycopg

from offworld_kernel import policy_runner as workers
from offworld_kernel.causal_trace import content_hash
from offworld_kernel.project_activity import build_sponsor_portfolio_request
from offworld_kernel.project_study import region_study_activity_id
from simulation.offworld_mvp.build7.generated_campaign import (
    AUTHORIZATION, run_world_prospecting_initiation,
)
from simulation.offworld_mvp.build7.increment5 import classify_regional_material_observation
from simulation.offworld_mvp.build7 import runtime_flow as flow

# Deliberate synthetic PROOF inputs, not predictions of Earth's 2040 economy.
SYNTHETIC_2040_STUDY_SUPPLY_CLAIM = D("2")
SYNTHETIC_2026_PROJECT_CAPITAL = D("2")
STUDY_START_YEAR = 2039
STUDY_PAYMENT_AND_OBSERVATION_YEAR = 2040
SEED = "BUILD7-I5-QUAL-POSITIVE-V3"  # Existing fixture seed, not chosen by trial-and-error.


def run_2040_paid_study(run_id: str) -> dict:
    # Fail closed if anyone accidentally points this proof at a real service.
    service_file = os.environ.get("PGSERVICEFILE", "")
    if not service_file.startswith("/tmp/loom-box3-proof/"):
        raise RuntimeError("BOX3_PRIVATE_SERVICE_FILE_REQUIRED")
    with psycopg.connect(service="runtime") as check:
        database, principal = check.execute(
            "SELECT current_database(),current_user").fetchone()
    if (database, principal) != ("box3_proof", "box3_runtime"):
        raise RuntimeError("BOX3_PRIVATE_DATABASE_REQUIRED")
    k, h, world, opened = run_world_prospecting_initiation(
        reference_service="reference_reader", runtime_service="runtime",
        run_id=run_id, calendar_year=2026, _return_runtime=True,
    )
    pid = opened.get("project_id")
    assert pid and opened["prospecting_decision"] == "INITIATE_PROJECT", opened
    project = k.state.projects[pid]
    assert project.status == "EXPLORING" and not k.project_study_states
    cash_id = project.cash_account_id
    assert k.state.accounts[cash_id].balance == SYNTHETIC_2026_PROJECT_CAPITAL
    # The existing 2040 Earth reference is available; the amount requested and
    # actually reserved by this proof is a disclosed synthetic assumption.
    constraint = k.resource_constraints[("EARTH:USA", 15)]
    opening_earth_capacity = constraint.available
    assert opening_earth_capacity >= SYNTHETIC_2040_STUDY_SUPPLY_CLAIM

    pub_prior = dict(k.agents["PUB"].beliefs)
    fin_prior = dict(k.agents["FIN"].beliefs)
    supplier_id = "earth_supplier"
    supplier_before = k.state.accounts[supplier_id].balance
    cash_before = k.state.accounts[cash_id].balance
    activity_id = region_study_activity_id(pid)
    location_id = opened["prospecting_location_id"]
    body_key = opened["selected_body_id"]

    # Study is initialized and legitimately authorized/started in 2039.
    # Its frozen one-year duration makes completion and *payment* in 2040.
    flow.system_epoch(k, h, "initialize_region_study", "14",
                      (14, pid, location_id))
    activity = k.project_activities[activity_id]
    request = build_sponsor_portfolio_request(
        "BOX3:2040:STUDY_AUTHORIZATION", 14, (activity.id,))
    decision, decision_ref = flow.policy_epoch(
        k, h, "BOX3_PORTFOLIO_2039", "SPN", "14",
        request, request.required_fact_keys,
        workers.run_sponsor_portfolio_policy,
        workers.sponsor_portfolio_policy_version(), {"project_id": pid},
    )
    assert decision.outcome.value == "AUTHORIZE", decision
    flow.system_epoch(k, h, "authorize_project_study_activity", "14",
                      (14, decision), decision_refs=(decision_ref,))
    flow.system_epoch(k, h, "start_project_activity", "14",
                      (14, activity_id), decision_refs=(decision_ref,))

    expense = flow.system_epoch(k, h, "spend_project_study_activity", "15",
                                (15, activity_id, "PROJECT"),
                                decision_refs=(decision_ref,))
    observations, _ = flow.system_epoch(
        k, h, "observe_region_study", "15",
        (15, "SPN", body_key, location_id, pid, activity_id),
        decision_refs=(decision_ref,),
    )
    signal_rows = []
    for obs in observations:
        belief_key = "BODY:" + obs.body_id + ":" + obs.question_ref
        prior = k.agents["SPN"].beliefs.get(
            belief_key, k.agents["SPN"].priors[belief_key])
        flow.system_epoch(k, h, "update_agent_belief_from_observation", "15",
                          (15, "SPN", obs.id, belief_key, D(".80"), D(".20"),
                           "BUILD7_REGION_MATERIAL_V1", AUTHORIZATION),
                          decision_refs=(decision_ref,))
        posterior = k.agents["SPN"].beliefs[belief_key]
        signal_rows.append({"id": obs.id, "signal": obs.signal,
                            "belief_key": belief_key, "prior": str(prior),
                            "posterior": str(posterior),
                            "private": not obs.public})
    standing = classify_regional_material_observation(observations)
    result_ref = "BOX3:2040:REGION_STUDY:" + content_hash(
        (pid, tuple(o.id for o in observations)))[:24]
    flow.system_epoch(k, h, "complete_project_study_activity", "15",
                      (15, activity_id, standing.value, result_ref),
                      decision_refs=(decision_ref,))
    flow.system_epoch(k, h, "admit_project_activity_result", "15",
                      (15, activity_id, "SPN"), decision_refs=(decision_ref,))

    cash_after = k.state.accounts[cash_id].balance
    supplier_after = k.state.accounts[supplier_id].balance
    c = k.resource_constraints[("EARTH:USA", 15)]
    assert cash_before - cash_after == expense.amount
    assert supplier_after - supplier_before == expense.amount
    # The frozen kernel reserves the claim and immediately consumes it into spent.
    assert c.reserved == 0 and c.spent == SYNTHETIC_2040_STUDY_SUPPLY_CLAIM
    assert len(k.project_activity_expense_records) == 1
    assert len(signal_rows) == 4 and all(row["private"] for row in signal_rows)
    assert all(D(r["posterior"]) != D(r["prior"]) for r in signal_rows)
    assert all(D(r["posterior"]) > 0 for r in signal_rows if r["signal"] == "NEGATIVE")
    assert k.state.projects[pid].status == "EXPLORING"
    assert not k.project_study_review_records
    assert k.agents["PUB"].beliefs == pub_prior
    assert k.agents["FIN"].beliefs == fin_prior
    assert all(r["id"] in k.agents["SPN"].information for r in signal_rows)
    assert all(r["id"] not in k.agents["PUB"].information for r in signal_rows)
    assert all(r["id"] not in k.agents["FIN"].information for r in signal_rows)
    return {
        "run_id": run_id, "sealed_world_digest": world["sealed_world_digest"],
        "world_scenario_id": world["scenario_id"], "generated_body_count": world["body_count"],
        "project_id": pid, "body": body_key,
        "location_id": location_id, "study_activity_id": activity_id,
        "start_calendar_year": STUDY_START_YEAR,
        "payment_and_observation_year": STUDY_PAYMENT_AND_OBSERVATION_YEAR,
        "funding_origin": "2026 REAL KERNEL DISBURSEMENT (2 MODEL_CURRENCY)",
        "synthetic_2040_supply_claim": str(SYNTHETIC_2040_STUDY_SUPPLY_CLAIM),
        "2040_frozen_earth_reference_capacity": str(opening_earth_capacity),
        "cash_before": str(cash_before), "cash_after": str(cash_after),
        "supplier_before": str(supplier_before), "supplier_after": str(supplier_after),
        "study_expense": str(expense.amount),
        "earth_reserved": str(c.reserved), "earth_spent": str(c.spent),
        "standing": standing.value, "project_status": k.state.projects[pid].status,
        "observations": signal_rows, "review_count": len(k.project_study_review_records),
        "other_actor_beliefs_unchanged": True,
        "epoch_commits": list(h["epoch_commits"]),
        "causal_head": str(k.causal_envelopes[-1].envelope_id) if k.causal_envelopes else "",
        "tx_fingerprint": content_hash(k.state.transactions),
        "observation_fingerprint": content_hash(tuple(
            (r["id"], r["signal"], r["prior"], r["posterior"]) for r in signal_rows)),
        "belief_fingerprint": content_hash(k.agents["SPN"].beliefs),
    }
