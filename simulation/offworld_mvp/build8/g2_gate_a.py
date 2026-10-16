"""G2 Gate A only: private policy with the UNCHANGED strict runtime."""
from dataclasses import dataclass, replace
from decimal import Decimal as D
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from offworld_kernel.boundary import (ConsumptionRequest, ContextValue,
                                     admit_for_use, snapshot_facts)
from offworld_kernel.causal_trace import validate_trace
from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel.mvp_state import ExplorationDecisionOutcome, RuntimeObjectClass
from offworld_kernel.policy import FactState, build_decision_snapshot
from offworld_kernel.policy_runner import (PolicyExecutionResult,
                                           assert_policy_source_safe, snapshot_to_wire,
                                           exploration_request_to_wire)
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.runtime import ScheduledSimulationRuntime
from simulation.offworld_mvp.build7.runtime_flow import strict_provenance
from .genesis_g1 import build_opening, ROOT

HERE = Path(__file__).parent
MODULES = ("g2_gate_a.py", "g2_private_worker.py", "g2_private_policy.py")


class PrivateReason(str, Enum):
    APPROVED_PRIVATE_REMOTE_EXPLORATION = "APPROVED_PRIVATE_REMOTE_EXPLORATION"
    INSUFFICIENT_BUDGET = "INSUFFICIENT_BUDGET"
    INFORMATION_VALUE_BELOW_HURDLE = "INFORMATION_VALUE_BELOW_HURDLE"
    PRIVATE_POLICY_OR_CAPABILITY_BLOCK = "PRIVATE_POLICY_OR_CAPABILITY_BLOCK"
    OUTSIDE_AUTHORED_HORIZON = "OUTSIDE_AUTHORED_HORIZON"


@dataclass(frozen=True)
class PrivateRemoteDecision:
    id: str
    request_id: str
    actor_id: str
    authorized: bool
    authorized_cost: D
    channel: str
    outcome: ExplorationDecisionOutcome
    reason_code: PrivateReason
    snapshot_ref: str
    policy_version: str
    decision_version: str = "BUILD8_PRIVATE_REMOTE_DECISION_V1"

    def validate_protocol(self, request):
        request.validate_protocol()
        if (self.request_id != request.id or self.channel != request.channel
                or not self.id or not self.actor_id or not self.snapshot_ref
                or not self.policy_version):
            raise ValueError("PRIVATE_DECISION_LINEAGE")
        if (self.authorized != (self.outcome == ExplorationDecisionOutcome.AUTHORIZE)
                or (self.authorized and self.authorized_cost <= 0)
                or (not self.authorized and self.authorized_cost != 0)):
            raise ValueError("PRIVATE_DECISION_PAYMENT")
        return self

def verify_extension(data):
    for name in MODULES:
        relative = "simulation/offworld_mvp/build8/" + name
        expected = data["sources"].get(relative)
        actual = sha256((HERE / name).read_bytes()).hexdigest()
        if expected != actual:
            raise ValueError("G2_EXTENSION_SOURCE_MISMATCH:" + name)
    assert_policy_source_safe((HERE / "g2_private_policy.py").read_bytes())

def worker(payload):
    cp = subprocess.run([sys.executable, "-I", "-S",
                         str(HERE / "g2_private_worker.py")],
                        input=json.dumps(payload, sort_keys=True), text=True,
                        capture_output=True, timeout=3,
                        cwd="/", env={"PYTHONHASHSEED": "0"})
    if cp.returncode:
        raise RuntimeError("G2_POLICY_ISOLATION_FAILURE")
    return json.loads(cp.stdout), sha256(cp.stdout.encode()).hexdigest()


def run(data, digest, *, probe=False, tamper_decision=False, tamper_version=False):
    verify_extension(data)
    k, base = build_opening(data, scenario_sha256=digest)
    actor = data["actors"][0]
    g = data["g2"]
    sid = actor["id"]
    time = str(data["time"]["start_year"] - 2025)
    # The source-backed G1 opening is unmodified. These additional scenario
    # use contracts are declared BEFORE the first governed decision.
    specs = (("agent.STATE", "TYPED_AGENT_STATE", "ADMITTED_INFORMATION", "AGENT_STATE"),
             ("agent.BELIEF", "PROBABILITY", "ACTOR_BELIEF", "BELIEF"),
             ("agent.PRIOR", "PROBABILITY", "AGENT_PRIOR", "PRIOR"),
             ("exploration.REMOTE_COST", "MODEL_CURRENCY", "POLICY_PARAMETER", None))
    contracts = tuple((sid, "POLICY", concept, "AGENT:" + sid, context,
                       "AGENT", unit, role)
                      for concept, unit, role, _ in specs
                      for context in (("SCENARIO",) if concept.startswith("exploration.") else ("REALIZED",)))
    selectors = tuple((sid, concept, selector) for concept, _, _, selector in specs if selector)
    # The authored cost is an actual SCENARIO assertion; its source is the
    # complete canonical scenario bytes, already hash-verified by G1.
    cost_source = ContextValue(
        assertion_id="G2:OFFER:" + digest, subject_id=sid,
        concept="exploration.REMOTE_COST", scope="AGENT:" + sid,
        world_context="SCENARIO", context_id=k.boundary_manifest.scenario_id,
        perspective="AGENT", perspective_actor_id=sid, value_state=FactState.KNOWN,
        value=data["observation_offer"]["cost"], unit="MODEL_CURRENCY",
        reason_code="AUTHORED", proposition_kind="SCENARIO_INPUT",
        proposition_role="POLICY_PARAMETER", epistemic_mode="AUTHORED_SCENARIO",
        admission_state="ADMITTED", uncertainty_state="DECLARED", uncertainty_ref="",
        valid_from=time, valid_to=time, time_basis="SIM_TIME", available_from=time,
        source_refs=("G2_SCENARIO",), source_hashes=(digest,),
        warrant_refs=(), support_conflict_refs=(), dependency_refs=(),
        transformation_ref="", transformation_version="",
        authorization_ref="BUILD8_AUTHORED_SCENARIO", reference_role="SCENARIO_INPUT",
        exception_flags=(), record_version="CONTEXT_VALUE_V1", source_time=time)
    m = k.boundary_manifest
    k.boundary_manifest = replace(m, allowed_use_contracts=m.allowed_use_contracts + contracts,
                                  source_resolver_bindings=selectors,
                                  assertions=m.assertions + (cost_source,))
    k.begin_decision_epoch("G2_PRIVATE", g["chain_id"])
    receipts = []
    for concept, unit, role, _ in specs:
        context = "SCENARIO" if concept.startswith("exploration.") else "REALIZED"
        q = ConsumptionRequest("G2:" + concept, sid, "POLICY", sid, concept,
                               "AGENT:" + sid, "SIM_TIME", time, time,
                               context, m.scenario_id if context == "SCENARIO" else m.run_id,
                               "AGENT", sid, "ADMITTED", unit, role)
        v, receipt = admit_for_use(k, q)
        if v.value_state != FactState.KNOWN:
            raise ValueError("G2_NO_GENUINE_ADMISSION:" + concept)
        receipts.append(receipt)
    receipts = tuple(receipts)
    snap = build_decision_snapshot(k, sid, "G2_PRIVATE", time,
                                   snapshot_facts(k, receipts), admission_receipts=receipts)
    request = build_exploration_request(
        g["request_id"], g["service_year"], "", "", channel="REMOTE",
        body_id=g["body_id"], question_ref=g["question_ref"])
    safe = snapshot_to_wire(snap)
    parameters = {"cost": data["observation_offer"]["cost"],
                  "information_value": g["information_value"], "hurdle": g["hurdle"],
                  "service_year": g["service_year"], "end_year": data["time"]["end_year"],
                  "prior_key": actor["prior_key"],
                  "policy_allowed": data["policies"][actor["policy_ref"]]["may_consider_explore"]}
    if probe:
        return worker({"mode": "PROBE", "snapshot": safe})[0]
    version = "G2_PRIVATE:" + sha256(json.dumps(
        {"inputs": parameters, "sources": {n: data["sources"]["simulation/offworld_mvp/build8/" + n]
                                         for n in MODULES}},
        sort_keys=True).encode()).hexdigest()
    k.scheduler.register_coupling(CouplingSpec("G2_PRIVATE_DECISION", "G2_V1",
        RuntimeObjectClass.SYSTEM, (), ("agent_snapshot",), (), "EVENT", Phase.DECISION_WINDOW))
    ref = k.scheduler.open_decision_window(snap.period_key, snap.fingerprint())
    eid = "G2:PRIVATE:DECISION"
    k.scheduler.schedule(ScheduledEvent(eid, D(time), Phase.DECISION_WINDOW, 0,
                                        sid, "G2_PRIVATE_DECISION", snapshot_ref=ref))
    runtime = ScheduledSimulationRuntime(k, strict_provenance(k, policies=(version,)))
    def policy(ctx):
        verify_extension(data)
        raw, fingerprint = worker({"mode": "EVALUATE", "snapshot": safe,
                                   "request": exploration_request_to_wire(request),
                                   "parameters": parameters, "decision_key": ctx.decision_key})
        decision = PrivateRemoteDecision(
            "G2:" + sha256((request.id + ctx.decision_key + version).encode()).hexdigest()[:20],
            request.id, sid, raw["outcome"] == "AUTHORIZE",
            D(raw["authorized_cost"]), request.channel,
            ExplorationDecisionOutcome(raw["outcome"]),
            PrivateReason(raw["reason_code"]), ctx.snapshot_ref, version)
        if tamper_decision:
            decision = replace(decision, request_id="TAMPERED")
        return PolicyExecutionResult(decision, version + (":BAD" if tamper_version else ""), "G2_SCENARIO:" + digest,
                                     fingerprint, ())
    runtime.register_policy_handler(eid, sid, snap, g["decision_slot"], policy,
                                    request=request, admission_receipts=receipts,
                                    expected_policy_version=version)
    runtime.seal()
    result = runtime.run()
    validate_trace(k.causal_envelopes, k.causal_artifacts)
    dref = runtime._strict_emitted_decisions[eid]
    decision = policy_result_decision(k, dref)
    evidence = next(e for e in k.causal_envelopes if e.action == "POLICY_EVALUATION")
    if (len(evidence.request_refs) != 1 or len(evidence.decision_refs) != 1
            or len(evidence.input_receipt_refs) != len(receipts)):
        raise RuntimeError("G2_INCOMPLETE_ORIGINAL_LINEAGE")
    from simulation.offworld_mvp.build7.generated_campaign import load_config
    legacy = load_config()["structural_parameters"]
    origin = lambda name, value: ("PINNED_BUILD7_CONFIG" if name in legacy and
        str(legacy[name]) == value else "AUTHORED_G1_SCENARIO_OR_EARTH_SOURCE")
    return {"run_id": m.run_id, "scenario": data, "source_digests": data["sources"],
            "effective_parameters": {
                name: {"value": value, "origin": origin(name, value)}
                for name, value in m.parameters},
            "policy_parameters": {"source": "AUTHORED_G2_SCENARIO", "values": parameters},
            "outcome": decision["outcome"], "reason": decision["reason_code"],
            "request_originals": len([x for x in k.causal_artifacts if x.startswith("REQUEST:")]),
            "decision_originals": len([x for x in k.causal_artifacts if x.startswith("DECISION:")]),
            "receipt_count": len(receipts),
            "rule_refs": tuple(x for e in k.causal_envelopes for x in e.rule_refs
                               if x.startswith("POLICY_RULE:")),
            "causal_trace": "PASS", "no_observations": len(k.observations) == 0,
            "no_payments": len(k.state.transactions) == 0,
            "result_fingerprint": result.result_fingerprint}

def policy_result_decision(k, ref):
    obj = json.loads(k.causal_artifacts[ref][1])
    return {key: value["value"]["value"] if isinstance(value.get("value"), dict) else value["value"] for key, value in obj["fields"]["decision"]["fields"].items()
            if key in ("outcome", "reason_code")}

if __name__ == "__main__":
    from .genesis_g1 import load_scenario
    doc, sha = load_scenario(HERE / "g2_gate_a_scenario.json")
    print(json.dumps(run(doc, sha), sort_keys=True, indent=2))
