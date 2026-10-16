"""Build 8 G1: data-owned offline genesis. No WORLD simulation or database.

Historical Build 7 is a pinned reference input, not an inherited cast.
Only a strict, unqualified opening is constructed; there is no event execution.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal as D
from pathlib import Path
from dataclasses import replace

from offworld_kernel.boundary import (
    BUILD6E_AUTHORIZATION, BUILD6E_CONTRACT, BoundaryManifest,
    ConsumptionRequest, admit_for_use, validate_opening,
)
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.causal_trace import canonical, content_hash
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AgentKind, AgentState, PopulationLedger
from simulation.offworld_mvp.build7 import generated_campaign as historical

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCENARIO_PATH = Path(__file__).with_name("genesis_g1_scenario.json")
SCHEMA = "BUILD8_GENESIS_G1_SCENARIO_V1"


def load_scenario(path=DEFAULT_SCENARIO_PATH):
    """Load byte-exact authored data, returning both content and source digest."""
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    if raw != (json.dumps(data, indent=2, sort_keys=True) + "\n").encode():
        raise ValueError("noncanonical scenario bytes")
    return data, hashlib.sha256(raw).hexdigest()


def validate_scenario(data):
    """Validate only the minimal G1 scenario and its already declared sources."""
    if data.get("schema") != SCHEMA or data.get("world_binding") is not None:
        raise ValueError("G1 only accepts a non-WORLD opening")
    if data.get("bodies") != [] or data.get("projects") != []:
        raise ValueError("G1 does not construct WORLD entities or projects")
    if len(data.get("actors", [])) != 1 or len(data.get("nodes", [])) != 1:
        raise ValueError("G1 expects its authored single-actor opening")
    if not isinstance(data.get("test_alternatives"), dict):
        raise ValueError("test alternatives must be authored data")
    when, agent, offer = data["time"], data["actors"][0], data["observation_offer"]
    if when["clock_ref"] != "SIM_YEAR_PLUS_2025_V1":
        raise ValueError("unsupported frozen clock")
    if not (isinstance(when["start_year"], int) and isinstance(when["end_year"], int)
            and when["start_year"] <= when["end_year"]):
        raise ValueError("invalid year interval")
    if offer["currency"] != "MODEL_CURRENCY" or not (
            when["start_year"] <= offer["active_year"] <= when["end_year"]):
        raise ValueError("offer outside period")
    if data["mission_cost_future"]["hold_2026_cost"]:
        raise ValueError("G1 cannot extend historical mission costs")
    if data["mission_cost_future"]["post_boundary"] != "UNAVAILABLE_NO_MISSIONS_IN_G1":
        raise ValueError("G1 cannot assert unavailable future mission costs")
    if not agent["id"] or agent["account"] == "" or agent["node"] != data["nodes"][0]["id"]:
        raise ValueError("unbound actor/account/node")
    if agent["kind"] not in AgentKind.__members__ or data["nodes"][0]["kind"] not in NodeKind.__members__:
        raise ValueError("unsupported actor/node kind")
    if (not isinstance(agent["capabilities"], list) or
            not all(isinstance(c, str) and c for c in agent["capabilities"]) or
            len(set(agent["capabilities"])) != len(agent["capabilities"])):
        raise ValueError("invalid authored capabilities")
    if agent["policy_ref"] not in data["policies"]:
        raise ValueError("unknown authored policy")
    if set(data["policies"][agent["policy_ref"]]) != {"may_consider_explore"}:
        raise ValueError("undeclared G1 preview policy")
    if not isinstance(data["policies"][agent["policy_ref"]]["may_consider_explore"], bool):
        raise ValueError("invalid policy choice")
    for field in ("opening_cash", "prior"):
        if not isinstance(agent[field], str) or not D(agent[field]).is_finite():
            raise ValueError("opening numeric value must be a finite decimal string")
    if not D(agent["opening_cash"]) >= 0 or not D(0) <= D(agent["prior"]) <= D(1):
        raise ValueError("negative cash or invalid prior")
    if not isinstance(offer["cost"], str) or not D(offer["cost"]).is_finite() or D(offer["cost"]) <= 0:
        raise ValueError("cost must be an authored positive decimal")
    if not agent["prior_key"]:
        raise ValueError("missing belief key")
    sources = data["sources"]
    if len(sources) < 2:
        raise ValueError("no pinned original references")
    # The declared paths are data; confinement is a file-integrity invariant.
    for relative, expected in sources.items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or len(expected) != 64:
            raise ValueError("unconfined source reference")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("SOURCE_DIGEST_MISMATCH: " + relative)
    # G1 genuinely consumes the historical, pinned Earth and configuration input.
    if str(historical.EARTH_INPUT.relative_to(ROOT)) not in sources or str(historical.INPUT.relative_to(ROOT)) not in sources:
        raise ValueError("source-backed Earth/config required")
    return data


def build_opening(data, *, scenario_sha256):
    """Build one genuine, source-backed strict kernel opening; do not run it."""
    canonical_bytes = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    if hashlib.sha256(canonical_bytes).hexdigest() != scenario_sha256:
        raise ValueError("SCENARIO_BYTE_DIGEST_MISMATCH")
    validate_scenario(data)
    actor = data["actors"][0]
    when = data["time"]
    cost = D(data["observation_offer"]["cost"])
    cash = D(actor["opening_cash"])
    # The historical Build 7 configuration is a *pinned data input* for the
    # many inherited frozen boundary parameters. Its fixed cast is NOT built.
    historical_config = historical.load_config()
    earth, earth_sha, earth_document = historical._load_earth_authority()
    reference = next(
        (v for v in earth if v.concept == "population" and
         v.valid_from == str(when["start_year"])), None
    )
    if reference is None:
        raise ValueError("NO_SOURCE_BACKED_POPULATION_FOR_OPENING_YEAR")
    params = {str(k): str(v) for k, v in historical_config["structural_parameters"].items()}
    params.update({
        "N": reference.value,
        "reference_population_bound": reference.value,
        "prior": actor["prior"],
        "belief_key." + actor["id"]: actor["prior_key"],
        "remote_cost": data["observation_offer"]["cost"],
        "opening_effective_time": str(when["start_year"] - 2025),
        # Distinct authored Build 8 fingerprints are recorded, but we do not
        # invent a new authorization or claim the four old modules qualify us.
        "build7.profile": historical.PROFILE,
        "build8.g1.scenario_sha256": scenario_sha256,
        "build8.g1.end_year": str(when["end_year"]),
        "build8.g1.policy_ref": actor["policy_ref"],
        "build8.g1.source_pin": content_hash(tuple(sorted(data["sources"].items()))),
    })
    comparison = {str(k): str(v) for k, v in data["comparison"].items()}
    source_pins = data["sources"]
    config_path = historical.INPUT.relative_to(ROOT).as_posix()
    earth_path = historical.EARTH_INPUT.relative_to(ROOT).as_posix()
    pinned_modules = tuple(
        (p, source_pins[p]) for p in source_pins
        if p.endswith(("/generated_campaign.py", "/runtime_flow.py", "/named_world.py", "/store.py"))
    )
    run_id = data["scenario_id"] + ":" + content_hash((
        scenario_sha256, tuple(sorted(source_pins.items())),
        tuple(sorted(params.items())), tuple(sorted(comparison.items())),
        hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    ))[:20]
    frozen_population_use = (
        "GENESIS", "EARTH_REFERENCE", "population", "COUNTRY:USA",
        "REAL", "GOVERNANCE", "PERSON", "EARTH_REFERENCE",
    )
    m = BoundaryManifest(
        BUILD6E_CONTRACT,
        "BUILD8_G1_INPUT:" + scenario_sha256,
        data["scenario_id"], SCHEMA, run_id,
        ((historical.INPUT.name, source_pins[config_path]),),
        (("EARTH_AUTHORITY:" + earth_document["source_snapshot_id"],
          earth_document["promotion_manifest_sha256"]),),
        "0" * 64,
        (("BUILD8_G1_SCENARIO", scenario_sha256),),
        (frozen_population_use,), (),
        ("BUILD8_G1_COMPARISON", content_hash(tuple(sorted(comparison.items())))),
        (historical.EARTH_INPUT.name, earth_sha),
        (historical.INPUT.name, source_pins[config_path]),
        when["clock_ref"], "ODD_SCHEMA_REGISTRY_0_20", BUILD6E_AUTHORIZATION,
        (reference,), tuple(sorted(params.items())),
        tuple(sorted(comparison.items())), (), (), pinned_modules,
    )
    rid = RunIdentity(data["scenario_id"], SCHEMA, m.input_snapshot_id,
                      BUILD6E_CONTRACT, m.parameters)
    kernel = MethodologyHardenedBuild4Kernel(
        rid, boundary_manifest=m, lambda_displacement=D(params["lambda"])
    )
    for node in data["nodes"]:
        kernel.add_node(node["id"], NodeKind[node["kind"]])
    kernel.add_account(actor["account"], actor["id"], actor["node"],
                       AccountKind.FUNDS, cash)
    a = AgentState(actor["id"], AgentKind[actor["kind"]], actor["node"],
                   actor["account"], set(actor["capabilities"]),
                   tuple(actor["objectives"]), decision_policy=actor["policy_ref"])
    a.priors[actor["prior_key"]] = D(actor["prior"])
    a.beliefs[actor["prior_key"]] = D(actor["prior"])
    kernel.add_agent(a)
    # This receipt is produced by the EXISTING admitted REAL Earth source,
    # not authored or forged by G1.
    request = ConsumptionRequest(
        "G1_EARTH_POPULATION", "GENESIS", "EARTH_REFERENCE",
        "USA", "population", "COUNTRY:USA", "CALENDAR_YEAR",
        str(when["start_year"]), str(when["start_year"]), "REAL", "",
        "GOVERNANCE", "", "ADMITTED", "PERSON", "EARTH_REFERENCE",
    )
    admitted, receipt = admit_for_use(kernel, request)
    if admitted != reference or admitted.value is None:
        raise ValueError("Earth population source not admitted")
    kernel._boundary_genesis_inputs = ((receipt, admitted),)
    kernel.population = PopulationLedger(int(D(admitted.value)), {})
    opening = tuple((key, canonical(kernel._boundary_opening_value(key)))
        for key in ("accounts", "agents", "resources", "constraints",
                    "population", "earth_admission_receipts"))
    kernel.boundary_manifest = replace(
        m, opening_bindings=opening,
        opening_state_hash=content_hash(kernel._boundary_projection()),
    )
    validate_opening(kernel)
    kernel.assert_methodology_invariants()
    # Check the unmodified strict provenance inventory; G1 is not a governed
    # action and makes no qualification claim.
    from offworld_kernel.provenance import ReplayProvenance
    from offworld_kernel.runtime import ScheduledSimulationRuntime
    labels = {
        "BOUNDARY_SHA256": kernel.boundary_manifest.fingerprint(),
        "EARTH_SLICE_SHA256": m.earth_slice_ref[1],
        "COMPARISON_CONFIG_SHA256": m.comparison_spec_ref[1],
        "QUALIFICATION_PROTOCOL_SHA256": m.qualification_protocol_ref[1],
    }
    historical_labels = {
        "generated_campaign.py": "BUILD7_CAMPAIGN_SHA256",
        "runtime_flow.py": "BUILD7_RUNTIME_FLOW_SHA256",
        "named_world.py": "NAMED_WORLD_COMPILER_SHA256",
        "store.py": "WORLD_AUTHORITY_STORE_SHA256",
    }
    for name, label in historical_labels.items():
        path, digest = next((p, s) for p, s in pinned_modules if p.endswith("/" + name))
        labels[label] = digest
    provenance = ReplayProvenance.from_kernel(kernel, table_manifest_ids=tuple(
        label + ":" + digest for label, digest in sorted(labels.items())
    ))
    ScheduledSimulationRuntime(kernel, provenance)._validate_boundary_provenance()
    # Deliberately a derived *readiness preview*, NOT a funded policy decision.
    permitted = ("EXPLORE" in a.capabilities and
                 data["policies"][actor["policy_ref"]]["may_consider_explore"])
    result = {
        "agent_capabilities": sorted(a.capabilities),
        "agent_prior": str(a.priors[actor["prior_key"]]),
        "agent_cash": str(kernel.state.accounts[actor["account"]].balance),
        "agent_policy": a.decision_policy,
        "could_consider_exploration": bool(permitted and cash >= cost),
        "potentially_affordable_looks": int(cash // cost) if permitted else 0,
        "calendar_year_slots": when["end_year"] - when["start_year"] + 1,
        "last_calendar_year": when["end_year"],
        "observation_offer_cost_used": str(cost),
        "real_population_receipts": len(kernel._boundary_genesis_inputs),
        "constructed_opening_fingerprint": kernel.boundary_manifest.opening_state_hash,
    }
    return kernel, {
        "standing": "UNQUALIFIED_G1_OPENING_NO_OBSERVATION",
        "scenario": data,
        "source_digests": source_pins,
        "scenario_sha256": scenario_sha256,
        "genesis_module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "run_id": run_id,
        "strict_opening": "PASS",
        "frozen_provenance": "PASS",
        "opening_result": result,
    }


def main():
    data, digest = load_scenario()
    _, report = build_opening(data, scenario_sha256=digest)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
