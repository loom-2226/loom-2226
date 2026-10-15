"""Opt-in, in-memory Box 3 capital choice. No WORLD, DB, or new policy."""
from __future__ import annotations

from decimal import Decimal as D

from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import ActionKind, AgentKind, AgentState, BodyRemoteObservation
from offworld_kernel.policy import FactState, SnapshotFact, build_decision_snapshot
from offworld_kernel.project_activity import ProjectActivity, build_sponsor_portfolio_request
from offworld_kernel.policy_runner import run_sponsor_portfolio_policy
from .freight_gauge import with_earth_side_freight_line

# Entirely authored, visible experimental inputs. Not world economic data.
POOL = D("100")
COSTS = {"A": D("60"), "B": D("60")}
PRIORITY = {"A": 1, "B": 2}
YEARS = (1, 2, 3)
BELIEF_KEY = "BODY:SYNTHETIC:VOLATILES_PRESENT"


def _snapshot(k, label, year, candidate_ids):
    facts = [
        SnapshotFact("portfolio.AVAILABLE_CAPITAL", FactState.KNOWN,
                     str(k.project_activity_available_capital("SPN")),
                     "KERNEL:UNCOMMITTED_SPONSOR_CASH"),
    ]
    for aid in sorted(candidate_ids):
        a = k.project_activities[aid]
        p = k.state.projects[a.project_id]
        fields = {
            "PROJECT_ID": a.project_id,
            "PROJECT_STATUS": p.status,
            "STATUS": a.status.value,
            "COMMITMENT": str(a.capital_commitment),
            "PRIORITY": str(a.priority),
            "WINDOW_VALID": "1",
        }
        facts.extend(SnapshotFact(f"activity.{aid}.{suffix}", FactState.KNOWN,
                                  str(value), "KERNEL:VISIBLE_ACTIVITY")
                     for suffix, value in fields.items())
    # Authored sensor record has already been admitted to SPN. No source truth.
    obs_id = next(oid for oid in sorted(k.agents["SPN"].information)
                  if oid in k.observations)
    facts.append(SnapshotFact("observation.VISIBLE_SIGNAL", FactState.KNOWN,
                              k.observations[obs_id].signal,
                              "SYNTHETIC:SPN_ADMITTED_OBSERVATION"))
    snap = build_decision_snapshot(k, "SPN", label, year, facts)
    assert not k.resources and not hasattr(k, "hidden_world")
    return snap


def _visible_snapshot(snapshot):
    return {
        "actor": snapshot.agent_id, "time": snapshot.effective_time,
        "account_balance": str(snapshot.account_balance),
        "capabilities": list(snapshot.capabilities),
        "objectives": list(snapshot.objectives),
        "admitted_observations": [ref for ref in snapshot.information_refs
                                  if ref.startswith("ACTOR_EVIDENCE:")],
        "admitted_activity_results": [ref for ref in snapshot.information_refs
                                      if not ref.startswith("ACTOR_EVIDENCE:")],
        "beliefs": {name: str(p) for name, p in snapshot.beliefs},
        "priors": {name: str(p) for name, p in snapshot.priors},
        "facts": {f.key: {"value": f.value, "source": f.source_ref}
                  for f in snapshot.admitted_facts},
        "fingerprint": snapshot.fingerprint(),
    }


def _gauge(k):
    """Break down unchanged kernel shadow; never treat allocation as another draw."""
    project_accounts = {k.state.projects["P-" + x].cash_account_id: x for x in ("A", "B")}
    qualifying = {TxPurpose.DISBURSE, TxPurpose.PUBLIC_SUBSIDY, TxPurpose.OTHER_INVESTMENT}
    # This authored experiment has no owner-return/sale/appropriation lineage.
    assert not any(tx.purpose in {TxPurpose.REVENUE, TxPurpose.OWNER_DISTRIBUTION,
                                  TxPurpose.RETURN_TO_EARTH, TxPurpose.PUBLIC_SUBSIDY}
                   for tx in k.state.transactions)
    rows = []
    for year in YEARS:
        shadow = k.earth_shadow_at(year)
        draw = shadow["capital_diverted_to_offworld"]
        per_project = {"A": D(0), "B": D(0)}
        unmatched = D(0)
        for tx in k.state.transactions:
            if tx.year != year or tx.purpose not in qualifying:
                continue
            if (k.state.nodes[tx.source_location].kind != NodeKind.EARTH or
                k.state.nodes[tx.destination_location].kind != NodeKind.OFFWORLD):
                continue
            tag = project_accounts.get(tx.destination_account)
            if tag is None:
                unmatched += tx.amount
            else:
                per_project[tag] += tx.amount
        new_draw, recycled = draw, D(0)  # No source-proven returned funds in this fixture.
        assert new_draw + recycled == draw
        assert sum(per_project.values(), D(0)) + unmatched == draw
        rows.append({
            "year": year, "country": "EARTH:X",
            "project_A_capital_received": str(per_project["A"]),
            "project_B_capital_received": str(per_project["B"]),
            "unattributed_capital": str(unmatched),
            "new_capital_draw": str(new_draw),
            "recycled_returned_cash_spent": str(recycled),
            "offworld_draw": str(draw),
            "returns_received": str(shadow["capital_returned_to_earth"]),
            "study_spending": str(sum((tx.amount for tx in k.state.transactions
                                       if tx.year == year and tx.purpose == TxPurpose.EXPLORATION), D(0))),
            "offworld_purchases_from_earth": str(shadow["offworld_purchases_from_earth"]),
        })
    return with_earth_side_freight_line(k.state, rows)


def run_two_project_choice(signal="NEGATIVE"):
    """Two distinguishable synthetic admitted signals; same priorities and finances."""
    if signal not in ("NEGATIVE", "POSITIVE"):
        raise ValueError("only declared, synthetic actor-visible belief cases")
    k = MethodologyHardenedBuild4Kernel(RunIdentity(
        "BUILD8_BOX3_TWO_PROJECT", "v1", "VISIBLE_SYNTHETIC_SCENARIO",
        "NONCANON_IN_MEMORY_ONLY", ()))
    k.add_node("EARTH:X", NodeKind.EARTH)
    for tag in ("A", "B"):
        k.add_node("OFF:PROJECT:" + tag, NodeKind.OFFWORLD)
    k.add_account("SPN:POOL", "SPN", "EARTH:X", AccountKind.FUNDS, POOL)
    k.add_agent(AgentState("SPN", AgentKind.PRIVATE_SPONSOR, "EARTH:X",
                           "SPN:POOL", {"AUTHORIZE_ACTIVITY", "DEVELOP"},
                           ("RETURN",), priors={BELIEF_KEY: D(".5")}))
    for tag in ("A", "B"):
        node = "OFF:PROJECT:" + tag
        k.add_account("cash:" + tag, "SPN", node, AccountKind.PROJECT_CASH)
        k.add_project("P-" + tag, node, "cash:" + tag, {"SPN": D(1)})
        k.register_project_activity(ProjectActivity(
            "ACT-" + tag, "P-" + tag, "CAPITAL_ALLOCATION", "SPN",
            PRIORITY[tag], D(1), D(1), COSTS[tag], "PROJECT_FUNDING_RESULT"))

    # Evidence and Bayesian belief are actor-visible synthetic controls. There
    # is intentionally no hidden-WORLD or geological truth in this fixture.
    observation = BodyRemoteObservation(
        "ACTOR_EVIDENCE:" + signal, 1, "SPN", "SYNTHETIC",
        "VOLATILES_PRESENT", "AUTHORED_SENSOR_CONTROL", signal, False)
    k.observations[observation.id] = observation
    k.agents["SPN"].information.add(observation.id)
    k.update_agent_belief_from_observation(
        1, "SPN", observation.id, BELIEF_KEY, D(".8"), D(".2"),
        "SYNTHETIC_VISIBLE_LIKELIHOOD", "AUTHORED_NOT_WORLD_TRUTH")
    before = {
        tag: {"balance": str(k.state.accounts["cash:" + tag].balance),
              "project_status": k.state.projects["P-" + tag].status,
              "activity_status": k.project_activities["ACT-" + tag].status.value}
        for tag in ("A", "B")
    }
    snapshot = _snapshot(k, "BOX3:INITIAL", 1, ("ACT-A", "ACT-B"))
    request = build_sponsor_portfolio_request("BOX3:PORTFOLIO:1", 1, ("ACT-A", "ACT-B"))
    result = run_sponsor_portfolio_policy(snapshot, request, "BOX3:EXISTING_POLICY")
    choice = result.decision
    assert choice.outcome.value == "AUTHORIZE" and choice.selected_activity_id == "ACT-A"
    k.authorize_project_activity(1, choice)
    k.start_project_activity(1, choice.selected_activity_id)
    k.complete_project_activity(2, choice.selected_activity_id, "BOX3:AUTHORIZE_FUNDING")
    k.admit_project_activity_result(2, choice.selected_activity_id, "SPN")
    paid = k.transfer(2, "SPN:POOL", "cash:A", COSTS["A"], TxPurpose.OTHER_INVESTMENT,
                      parent_ids=(choice.id, choice.selected_activity_id))
    k.transition_project_status(2, "SPN", "P-A", "DEVELOPMENT", choice.id)
    funded_status_event = k.events[-1]

    # Distinct decision after real transfer: B is still eligible but unaffordable.
    deferred_snapshot = _snapshot(k, "BOX3:REMAINDER", 2, ("ACT-B",))
    remainder_request = build_sponsor_portfolio_request("BOX3:PORTFOLIO:2", 2, ("ACT-B",))
    deferred = run_sponsor_portfolio_policy(
        deferred_snapshot, remainder_request, "BOX3:EXISTING_POLICY").decision
    assert (deferred.outcome.value, deferred.reason_code.value) == (
        "DEFER", "INSUFFICIENT_AVAILABLE_CAPITAL")
    deferred_event = k.event(2, "SPN", ActionKind.AUTHORIZE_ACTIVITY, "DEFERRED",
                             ("P-B", "ACT-B", deferred.id, deferred.reason_code.value),
                             (deferred.id,))
    k.assert_invariants()
    after = {
        tag: {"balance": str(k.state.accounts["cash:" + tag].balance),
              "project_status": k.state.projects["P-" + tag].status,
              "activity_status": k.project_activities["ACT-" + tag].status.value}
        for tag in ("A", "B")
    }
    gauge = _gauge(k)
    return {
        "classification": "RESEARCH_NONCANON_IN_MEMORY",
        "scenario_inputs": {
            "opening_shared_capital": str(POOL),
            "commitments": {tag: str(COSTS[tag]) for tag in ("A", "B")},
            "priorities": dict(PRIORITY),
            "signal": signal,
            "likelihoods": {"detection": "0.8", "false_positive": "0.2"},
            "funding_year": 2,
        },
        "before": before, "after": after,
        "initial_snapshot": _visible_snapshot(snapshot),
        "remaining_snapshot": _visible_snapshot(deferred_snapshot),
        "decision": {
            "outcome": choice.outcome.value,
            "selected": choice.selected_activity_id, "reason": choice.reason_code.value,
            "amount": str(choice.reserved_capital), "id": choice.id,
        },
        "funding_transaction": {
            "id": paid.id, "source": paid.source_account,
            "destination": paid.destination_account, "amount": str(paid.amount),
            "purpose": paid.purpose.value,
            "funded_project_status_event_id": funded_status_event.id,
        },
        "unfunded": {
            "project": "P-B", "disposition": "DEFERRED_NOT_ABANDONED",
            "project_status": k.state.projects["P-B"].status,
            "reason": deferred.reason_code.value, "decision_id": deferred.id,
            "recorded_event_id": deferred_event.id,
        },
        "gauge": gauge,
        "replay_fingerprint": k.state.fingerprint() if hasattr(k.state, "fingerprint") else k.decision_epoch_state_fingerprint(),
    }
