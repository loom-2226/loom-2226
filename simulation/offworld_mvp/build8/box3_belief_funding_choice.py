"""PR C: opt-in expected monetary value choice using the #415 kernel and policy."""
from __future__ import annotations

from decimal import Decimal as D
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import ActionKind, AgentKind, AgentState, BodyRemoteObservation
from offworld_kernel.policy import FactState, SnapshotFact, build_decision_snapshot
from offworld_kernel.project_activity import ProjectActivity, build_sponsor_portfolio_request
from offworld_kernel.policy_runner import run_sponsor_portfolio_policy
from .box3_two_project_choice import POOL, COSTS, _gauge, _visible_snapshot

# Fixed authored parameters, MODEL_CURRENCY; synthetic evidence, not World Authority.
ASSIGNED_VALUES = {"A": D("200"), "B": D("130")}
SPONSOR_HURDLE = D("0")
DETECTION, FALSE_POSITIVE = D("0.8"), D("0.2")
# 50% is derived from opposing sequential admitted observations; not assigned.
SIGNALS = {"20%": ("NEGATIVE",), "50%": ("POSITIVE", "NEGATIVE"), "80%": ("POSITIVE",)}
BELIEF_KEYS = {t: "BODY:SYNTHETIC:PROJECT:" + t + ":VOLATILES_PRESENT" for t in ("A", "B")}


def _observe(k, sponsor, tag, case):
    for i, signal in enumerate(SIGNALS[case], 1):
        oid = f"ACTOR_EVIDENCE:{tag}:{i}:{signal}"
        obs = BodyRemoteObservation(oid, 1, sponsor, "SYNTHETIC:PROJECT:" + tag,
                                    "VOLATILES_PRESENT", "AUTHORED_SENSOR_CONTROL", signal, False)
        k.observations[oid] = obs
        k.agents[sponsor].information.add(oid)
        k.update_agent_belief_from_observation(
            1, sponsor, oid, BELIEF_KEYS[tag], DETECTION, FALSE_POSITIVE,
            "SYNTHETIC_VISIBLE_LIKELIHOOD", "AUTHORED_NOT_WORLD_TRUTH")


def _snapshot(k, sponsor, label, year, offered, rows, hurdle):
    facts = [
        SnapshotFact("portfolio.AVAILABLE_CAPITAL", FactState.KNOWN,
                     str(k.project_activity_available_capital(sponsor)),
                     "KERNEL:UNCOMMITTED_SPONSOR_CASH"),
        SnapshotFact("sponsor.MIN_EXPECTED_NET_VALUE", FactState.KNOWN,
                     str(hurdle), "SPONSOR:AUTHORED_HURDLE"),
    ]
    for tag in ("A", "B"):
        r = rows[tag]
        for name, value in (
            ("SUCCESS_VALUE", r["value_if_successful"]), ("COST", r["cost"]),
            ("BELIEF", r["belief"]), ("EXPECTED_NET_VALUE", r["expected_net_value"]),
            ("DERIVED_PRIORITY", str(r["priority"])),
        ):
            facts.append(SnapshotFact(f"project.P-{tag}.{name}", FactState.KNOWN,
                                      value, "SPONSOR:VISIBLE_EXPECTED_VALUE"))
    for aid in sorted(offered):
        a = k.project_activities[aid]
        for name, value in (
            ("PROJECT_ID", a.project_id),
            ("PROJECT_STATUS", k.state.projects[a.project_id].status),
            ("STATUS", a.status.value), ("COMMITMENT", str(a.capital_commitment)),
            ("PRIORITY", str(a.priority)), ("WINDOW_VALID", "1"),
        ):
            facts.append(SnapshotFact(f"activity.{aid}.{name}", FactState.KNOWN,
                                      value, "SPONSOR:ADMITTED_POLICY_INPUT"))
    for oid in sorted(k.agents[sponsor].information):
        if oid in k.observations:
            facts.append(SnapshotFact(f"observation.{oid}.SIGNAL", FactState.KNOWN,
                                      k.observations[oid].signal,
                                      "SYNTHETIC:SPONSOR_ADMITTED_OBSERVATION"))
    assert not k.resources and not hasattr(k, "hidden_world")
    return build_decision_snapshot(k, sponsor, label, year, facts)


def run_belief_funding_choice(a_case="50%", b_case="50%", *,
                              assigned_values=None, hurdle=SPONSOR_HURDLE, sponsor_id="SPN"):
    """Independent one-shot sponsor choice; no database, hidden truth or repeated attempt."""
    values = {t: D((ASSIGNED_VALUES if assigned_values is None else assigned_values)[t])
              for t in ("A", "B")}
    hurdle = D(hurdle)
    k = MethodologyHardenedBuild4Kernel(RunIdentity(
        "BUILD8_BOX3C_BELIEF_FUNDING", "v1", "VISIBLE_SYNTHETIC_SCENARIO",
        "NONCANON_IN_MEMORY_ONLY", ()))
    k.add_node("EARTH:X", NodeKind.EARTH)
    for t in ("A", "B"):
        k.add_node("OFF:PROJECT:" + t, NodeKind.OFFWORLD)
    pool = sponsor_id + ":POOL"
    k.add_account(pool, sponsor_id, "EARTH:X", AccountKind.FUNDS, POOL)
    k.add_agent(AgentState(sponsor_id, AgentKind.PRIVATE_SPONSOR, "EARTH:X", pool,
                           {"AUTHORIZE_ACTIVITY", "DEVELOP"}, ("RETURN",),
                           priors={key: D("0.5") for key in BELIEF_KEYS.values()}))
    for t in ("A", "B"):
        node = "OFF:PROJECT:" + t
        k.add_account("cash:" + t, sponsor_id, node, AccountKind.PROJECT_CASH)
        k.add_project("P-" + t, node, "cash:" + t, {sponsor_id: D(1)})
    for t, case in (("A", a_case), ("B", b_case)):
        _observe(k, sponsor_id, t, case)

    rows = {}
    for t in ("A", "B"):
        belief = D(k.agents[sponsor_id].beliefs[BELIEF_KEYS[t]])
        net = belief * values[t] - COSTS[t]
        rows[t] = dict(project_id="P-" + t, activity_id="ACT-" + t,
                       belief=str(belief), value_if_successful=str(values[t]),
                       cost=str(COSTS[t]), expected_net_value=str(net),
                       above_or_at_hurdle=net >= hurdle)
    ranked = sorted(("A", "B"),
                    key=lambda t: (-D(rows[t]["expected_net_value"]),
                                   rows[t]["project_id"], rows[t]["activity_id"]))
    for priority, t in enumerate(ranked, 1):
        rows[t]["priority"] = priority
        k.register_project_activity(ProjectActivity(
            "ACT-" + t, "P-" + t, "CAPITAL_ALLOCATION", sponsor_id,
            priority, D(1), D(1), COSTS[t], "PROJECT_FUNDING_RESULT"))
    def states():
        return {t: {"balance": str(k.state.accounts["cash:" + t].balance),
                    "project_status": k.state.projects["P-" + t].status,
                    "activity_status": k.project_activities["ACT-" + t].status.value}
                for t in ("A", "B")}
    before = states()
    offered = tuple("ACT-" + t for t in ranked if rows[t]["above_or_at_hurdle"])
    snap = _snapshot(k, sponsor_id, "BOX3C:INITIAL", 1, offered, rows, hurdle)
    remaining_snap, paid_info, unfunded = None, None, {}
    nets = {t: rows[t]["expected_net_value"] for t in ("A", "B")}
    # Record threshold exclusions at decision year 1, before any year-2 transfer.
    for t in ("A", "B"):
        if not rows[t]["above_or_at_hurdle"]:
            event = k.event(1, sponsor_id, ActionKind.AUTHORIZE_ACTIVITY, "DECLINED",
                            ("P-" + t, "ACT-" + t, nets[t], str(hurdle), "BELOW_HURDLE"))
            unfunded[t] = dict(disposition="WAITING_BELOW_HURDLE", reason="BELOW_HURDLE",
                               recorded_event_id=event.id)

    if not offered:
        reason = "ALL_EXPECTED_NET_VALUES_BELOW_HURDLE"
        evt = k.event(1, sponsor_id, ActionKind.AUTHORIZE_ACTIVITY, "DECLINED",
                      ("HURDLE=" + str(hurdle),) +
                      tuple("P-" + t + "=" + nets[t] for t in ("A", "B")) +
                      (reason,), tuple(sorted(k.agents[sponsor_id].information)))
        decision = dict(outcome="DECLINED", selected=None, reason=reason,
                        amount="0", id=evt.id, hurdle=str(hurdle), expected_net_values=nets)
    else:
        request = build_sponsor_portfolio_request("BOX3C:PORTFOLIO:1", 1, offered)
        choice = run_sponsor_portfolio_policy(snap, request, "BOX3C:EXISTING_POLICY").decision
        assert choice.outcome.value == "AUTHORIZE" and choice.selected_activity_id in offered
        winner = choice.selected_activity_id[-1]
        k.authorize_project_activity(1, choice)
        k.start_project_activity(1, choice.selected_activity_id)
        k.complete_project_activity(2, choice.selected_activity_id, "BOX3C:AUTHORIZE_FUNDING")
        k.admit_project_activity_result(2, choice.selected_activity_id, sponsor_id)
        paid = k.transfer(2, pool, "cash:" + winner, COSTS[winner],
                          TxPurpose.OTHER_INVESTMENT,
                          parent_ids=(choice.id, choice.selected_activity_id))
        k.transition_project_status(2, sponsor_id, "P-" + winner, "DEVELOPMENT", choice.id)
        paid_info = dict(id=paid.id, source=paid.source_account,
                         destination=paid.destination_account, amount=str(paid.amount),
                         purpose=paid.purpose.value, status_event_id=k.events[-1].id,
                         parent_ids=list(paid.parent_ids))
        decision = dict(outcome=choice.outcome.value, selected=choice.selected_activity_id,
                        reason=choice.reason_code.value, amount=str(choice.reserved_capital),
                        id=choice.id, hurdle=str(hurdle), expected_net_values=nets)
        remainder = tuple(aid for aid in offered if aid != choice.selected_activity_id)
        if remainder:
            remaining_snap = _snapshot(k, sponsor_id, "BOX3C:REMAINDER", 2,
                                       remainder, rows, hurdle)
            req2 = build_sponsor_portfolio_request("BOX3C:PORTFOLIO:2", 2, remainder)
            deferred = run_sponsor_portfolio_policy(
                remaining_snap, req2, "BOX3C:EXISTING_POLICY").decision
            assert (deferred.outcome.value, deferred.reason_code.value) == (
                "DEFER", "INSUFFICIENT_AVAILABLE_CAPITAL")
            tag = remainder[0][-1]
            event = k.event(2, sponsor_id, ActionKind.AUTHORIZE_ACTIVITY, "DEFERRED",
                            ("P-" + tag, "ACT-" + tag, deferred.id,
                             deferred.reason_code.value), (deferred.id,))
            unfunded[tag] = dict(disposition="DEFERRED_NOT_ABANDONED",
                                 reason=deferred.reason_code.value,
                                 decision_id=deferred.id, recorded_event_id=event.id)

    for t in unfunded:
        unfunded[t]["project_status"] = k.state.projects["P-" + t].status
        unfunded[t]["activity_status"] = k.project_activities["ACT-" + t].status.value

    k.assert_invariants()
    gauge = _gauge(k)  # Reuses #415 gauge and tests both identities every year.
    for g in gauge:
        assert D(g["new_capital_draw"]) + D(g["recycled_returned_cash_spent"]) == D(g["offworld_draw"])
        assert sum((D(g[x]) for x in ("project_A_capital_received",
                                     "project_B_capital_received", "unattributed_capital")), D(0)) == D(g["offworld_draw"])
    return {
        "classification": "RESEARCH_NONCANON_OPT_IN_IN_MEMORY",
        "scenario_inputs": dict(
            sponsor_id=sponsor_id, objective="EXPECTED_MONETARY_VALUE_ONLY",
            opening_shared_capital=str(POOL),
            success_values={t: str(values[t]) for t in ("A", "B")},
            costs={t: str(COSTS[t]) for t in ("A", "B")},
            hurdle=str(hurdle), hurdle_comparison="expected_net_value >= hurdle",
            belief_signals={t: list(SIGNALS[case]) for t, case in
                            (("A", a_case), ("B", b_case))},
            likelihoods=dict(detection=str(DETECTION), false_positive=str(FALSE_POSITIVE)),
            initial_prior="0.5", funding_year=2),
        "ranked_projects": ["P-" + t for t in ranked],
        "candidates": rows, "offered_to_policy": list(offered),
        "initial_snapshot": _visible_snapshot(snap),
        "remaining_snapshot": _visible_snapshot(remaining_snap) if remaining_snap else None,
        "decision": decision, "funding_transaction": paid_info,
        "before": before, "after": states(), "unfunded": unfunded,
        "final_sponsor_capital": str(k.state.accounts[pool].balance),
        "gauge": gauge,
        "replay_fingerprint": k.state.fingerprint() if hasattr(k.state, "fingerprint")
                              else k.decision_epoch_state_fingerprint(),
    }
