"""Build 8 D1: numbered private paid regional attempts, in memory only.

The synthetic conditional-present control lives only on this trusted test observer.
It is never placed in a kernel store, actor snapshot, observation, or report.
No frozen regional observer, study review, DB or World Authority is involved.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D
from hashlib import sha256
import json

from offworld_kernel.build3 import RunIdentity
from offworld_kernel.kernel import InvariantError
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import (
    ActionKind, AgentKind, AgentState, BodyRemoteObservation,
)
from offworld_kernel.policy import FactState, SnapshotFact, build_decision_snapshot

SPONSOR = "SPN"
OTHER = "OTHER"  # Nonpaying privacy-test actor; no second project.
PROJECT = "P-REGION"
BODY = "BODY:SYNTHETIC"
REGION = "REGION:01"
MATERIAL = "VOLATILES"
QUESTION = f"REGION:{REGION}:{MATERIAL}_PRESENT"
BELIEF_KEY = f"BODY:{BODY}:{QUESTION}"
POOL = D("50")
COST = D("10")
SUCCESS_VALUE = D("200")
HURDLE = D("0")
DETECTION, FALSE_POSITIVE = D("0.80"), D("0.20")
YEAR = 2


@dataclass(frozen=True)
class PaidAttempt:
    sponsor: str
    project: str
    region: str
    material: str
    attempt_number: int
    paid_amount: D
    transaction_id: str
    observation_id: str
    belief_update: object  # Existing kernel ObservationBeliefUpdateRecord, not reimplemented.
    signal: str
    draw: D
    decision_expected_net: D

    @property
    def belief_before(self):
        return self.belief_update.prior

    @property
    def belief_after(self):
        return self.belief_update.posterior


@dataclass(frozen=True)
class AttemptDeclined:
    reason: str
    belief: D
    expected_net: D
    hurdle: D
    amount_charged: D = D(0)
    attempt_number: None = None


class Box3D1:
    """One sponsor, project, material and region; no simulation database."""

    def __init__(self, *, synthetic_conditional_present: bool,
                 run_name="BUILD8_BOX3_D1_REPEAT", opening_cash=POOL):
        if type(synthetic_conditional_present) is not bool:
            raise ValueError("synthetic conditional control must be bool")
        self._conditional_present = synthetic_conditional_present
        self.kernel = k = MethodologyHardenedBuild4Kernel(RunIdentity(
            run_name, "v1", "VISIBLE_SYNTHETIC_CONTROL", "NONCANON_IN_MEMORY", ()))
        k.add_node("EARTH:X", NodeKind.EARTH)
        k.add_node("OFF:REGION", NodeKind.OFFWORLD)
        k.add_account("SPN:POOL", SPONSOR, "EARTH:X", AccountKind.FUNDS, D(opening_cash))
        k.add_account("SUPPLIER:EARTH", "SUPPLIER", "EARTH:X", AccountKind.SUPPLIER)
        k.add_account("P:PROJECT_CASH", SPONSOR, "OFF:REGION", AccountKind.PROJECT_CASH)
        k.add_project(PROJECT, "OFF:REGION", "P:PROJECT_CASH", {SPONSOR: D(1)})
        k.add_agent(AgentState(
            SPONSOR, AgentKind.PRIVATE_SPONSOR, "EARTH:X", "SPN:POOL",
            {"AUTHORIZE_ACTIVITY"}, ("RETURN",), priors={BELIEF_KEY: D("0.5")}))
        # This actor exists ONLY to exercise the existing information boundary.
        k.add_account("OTHER:POOL", OTHER, "EARTH:X", AccountKind.FUNDS)
        k.add_agent(AgentState(
            OTHER, AgentKind.PRIVATE_SPONSOR, "EARTH:X", "OTHER:POOL",
            {"AUTHORIZE_ACTIVITY"}, ("RETURN",), priors={BELIEF_KEY: D("0.5")}))
        self.attempts: dict[int, PaidAttempt] = {}

    @property
    def next_paid_number(self):
        return len(self.attempts) + 1

    def choice(self):
        """PR C expected-net and hurdle, followed by ordinary available cash."""
        k = self.kernel
        belief = k.agents[SPONSOR].beliefs.get(
            BELIEF_KEY, k.agents[SPONSOR].priors[BELIEF_KEY])
        expected_net = belief * SUCCESS_VALUE - COST
        if expected_net < HURDLE:
            return AttemptDeclined("BELOW_HURDLE", belief, expected_net, HURDLE)
        if k.state.accounts["SPN:POOL"].balance < COST:
            return AttemptDeclined("INSUFFICIENT_CAPITAL", belief, expected_net, HURDLE)
        return None

    def try_attempt(self, *, year=YEAR, sponsor=SPONSOR, attempt_number=None):
        """Exactly-once local attempt; a retry of its ID returns existing evidence."""
        if sponsor != SPONSOR:
            raise PermissionError("actor is not the paying project sponsor")
        number = self.next_paid_number if attempt_number is None else attempt_number
        if type(number) is not int or number < 1:
            raise ValueError("paid attempt number must be positive integer")
        if number in self.attempts:
            return self.attempts[number]  # No draw, debit or belief update on replay.
        if number != self.next_paid_number:
            raise ValueError("paid attempts cannot skip numbers")
        declined = self.choice()
        if declined is not None:
            return declined  # No transaction, observation or number consumed.

        k = self.kernel
        attempt_id = f"D1:{SPONSOR}:{PROJECT}:{REGION}:{MATERIAL}:{number}"
        # Exactly the existing five-input keyed draw, with attempt in input 4.
        draw = k.keyed_draw(
            "OBS", year, sponsor, f"{BODY}:{REGION}:{MATERIAL}:{PROJECT}:{number}", "REGION")
        signal = ("POSITIVE" if draw >= D("0.20") else "NEGATIVE") if self._conditional_present else (
            "POSITIVE" if draw < FALSE_POSITIVE else "NEGATIVE")
        before = k.agents[SPONSOR].beliefs.get(BELIEF_KEY, k.agents[SPONSOR].priors[BELIEF_KEY])
        expected_net = before * SUCCESS_VALUE - COST

        # One real existing-kernel transfer for one service; not a WIP/Build 7 study.
        paid = k.transfer(
            year, "SPN:POOL", "SUPPLIER:EARTH", COST, TxPurpose.EXPLORATION,
            supplier_location="EARTH:X", asset_location="OFF:REGION",
            parent_ids=(PROJECT, attempt_id))
        oid = f"D1_OBS:{SPONSOR}:{PROJECT}:{REGION}:{MATERIAL}:{number}"
        observation = BodyRemoteObservation(
            oid, year, SPONSOR, BODY, QUESTION, "REGION:D1_IN_MEMORY", signal, False)
        k.observations[oid] = observation
        k.agents[SPONSOR].information.add(oid)
        k.event(year, SPONSOR, ActionKind.EXPLORE, "PRIVATE_REGION_MEASUREMENT",
                (attempt_id, paid.id, oid), (paid.id,))
        update = k.update_agent_belief_from_observation(
            year, SPONSOR, oid, BELIEF_KEY, DETECTION, FALSE_POSITIVE,
            "BOX3_D1_SYNTHETIC_LIKELIHOOD", "ADMITTED_PRIVATE_OBSERVATION")
        record = PaidAttempt(
            SPONSOR, PROJECT, REGION, MATERIAL, number, COST, paid.id, oid,
            update, signal, draw, expected_net)
        self.attempts[number] = record
        k.assert_invariants()
        return record

    def private_observation(self, actor, observation_id):
        """Agent information boundary; trusted kernel's global registry is not an API."""
        if actor not in self.kernel.agents or observation_id not in self.kernel.agents[actor].information:
            raise PermissionError("observation not admitted to requesting actor")
        return self.kernel.observations[observation_id]

    def snapshot(self, actor):
        k = self.kernel
        if actor not in k.agents:
            raise ValueError("unknown actor")
        facts = []
        for oid in sorted(k.agents[actor].information):
            if oid in k.observations:
                obs = self.private_observation(actor, oid)
                facts.append(SnapshotFact(
                    f"observation.{oid}.SIGNAL", FactState.KNOWN, obs.signal,
                    "ADMITTED_PRIVATE_OBSERVATION:" + oid))
        if actor == SPONSOR:
            belief = k.agents[actor].beliefs.get(BELIEF_KEY, D("0.5"))
            for key, val in (
                ("sponsor.SUCCESS_VALUE", SUCCESS_VALUE),
                ("sponsor.NEXT_ATTEMPT_COST", COST),
                ("sponsor.MIN_EXPECTED_NET_VALUE", HURDLE),
                ("sponsor.NEXT_EXPECTED_NET_VALUE", belief * SUCCESS_VALUE - COST)):
                facts.append(SnapshotFact(key, FactState.KNOWN, str(val),
                                          "SPONSOR:AUTHORED_OR_DERIVED"))
        assert not k.resources and not hasattr(k, "hidden_world")
        return build_decision_snapshot(k, actor, "BOX3_D1:VISIBLE", YEAR, facts)

    def evidence(self):
        """Only actor-visible signal, paid ledger and replay fingerprints; no source truth."""
        k = self.kernel
        rows = [{
            "sponsor": a.sponsor, "project": a.project, "region": a.region,
            "material": a.material, "attempt_number": a.attempt_number,
            "paid_amount": str(a.paid_amount), "transaction_id": a.transaction_id,
            "observation_id": a.observation_id,
            "belief_update_event_id": a.belief_update.event_id,
            "belief_before": str(a.belief_before), "belief_after": str(a.belief_after),
            "signal": a.signal, "draw": str(a.draw),
            "decision_expected_net": str(a.decision_expected_net),
        } for a in self.attempts.values()]
        transactions = [{
            "id": t.id, "year": t.year, "source": t.source_account,
            "destination": t.destination_account, "amount": str(t.amount),
            "purpose": t.purpose.value, "parents": list(t.parent_ids),
        } for t in k.state.transactions]
        return {
            "classification": "TEST_ONLY_IN_MEMORY_NONCANON",
            "authored_inputs": {
                "opening_cash": str(POOL), "cost": str(COST),
                "success_value": str(SUCCESS_VALUE), "hurdle": str(HURDLE),
                "detection": str(DETECTION), "false_positive": str(FALSE_POSITIVE),
                "observation_year": YEAR, "body": BODY, "region": REGION,
                "material": MATERIAL, "project": PROJECT, "sponsor": SPONSOR,
            },
            "paid_attempts": rows, "transactions": transactions,
            "cash": {
                "sponsor": str(k.state.accounts["SPN:POOL"].balance),
                "supplier": str(k.state.accounts["SUPPLIER:EARTH"].balance),
            },
            "beliefs": {name: str(v) for name, v in k.agents[SPONSOR].beliefs.items()},
            "project_status": k.state.projects[PROJECT].status,
            "review_count": len(k.project_study_review_records),
            "other_visible_refs": list(self.snapshot(OTHER).information_refs),
            "kernel_fingerprint": k.decision_epoch_state_fingerprint(),
            "ledger_fingerprint": k.fingerprint(),
        }


def full_fingerprint(evidence):
    return sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
