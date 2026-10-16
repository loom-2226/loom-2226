# Build 8 Genesis G1: proposal and immutable acceptance gates

CLASS: RESEARCH / NONCANON / PROPOSAL FIRST / OFFLINE / NO PG / NO WORLD READ.
BASE: main d3fd120c9a77954d3a7925aaf5285bd23c643b80.
Do not merge without kT review. No G2/G3/G4, WALTER or allowlist.

## Purpose
Construct a minimal truthful opening from authored data, not the frozen
Build 7 cast/horizon. One scenario data file, one loader, one validator,
one builder; a small local-only test and this report. No frozen edits.

## Predeclared PASS/FAIL before implementation
- Strict opening validation PASS and any invoked strict provenance check PASS
  without fabricating context or admitting unobserved truth. Actual Earth
  population input and any admission receipt must be source-derived.
  If incompatible, STOP and name the frozen requirement.
- Six field classes each change the *constructed or calculated usable result*
  AND the new run ID under an independent mutation:
  (1) cash: real sponsor account balance, affordability;
  (2) capability: constructed sponsor capability/readiness;
  (3) prior: constructed belief/prior;
  (4) cost: scenario-backed affordability/readiness calculation;
  (5) horizon: permitted time window/available decision slots;
  (6) policy: actor's policy identity and availability to consider search.
  Merely copying an input into a report is insufficient.
- Tests take all values and alternatives from scenario data, never test constants.
  Deterministic replay builds identical opening hashes and reports.
- Missing/invalid inputs and modified source bytes fail closed. Scenario,
  source-digest table and run ID printed in full in report.
- Local-only numeric/name scan is advisory. It cannot detect dormant parameter
  paths, indirect constants, data not actually applied, or semantic legitimacy.
- No silent post-2035 mission-cost extension. Any hold-at-2026 assumption must
  be explicitly authored in scenario, labelled provisional. G1 has no missions.
- Git frozen blobs match the pinned base. Only new Build 8 files. CI unchanged.

## Scope and stopping condition
G1 opening only. No paid looks, policy execution, secret WORLD generation,
database, container, admission inventions, frozen or historical edits.
Stop and report if strict frozen provenance cannot represent this honest
scenario, rather than adding a parallel governance path.

---

## Measured G1 results (appended after proposal-first commit)

**Local-only tests:** 8/8 PASS. **Strict opening:** PASS. **Unmodified frozen provenance:** PASS.
**Semantic status:** UNQUALIFIED opening; no epoch, PostgreSQL, WORLD read or action.
No Build 7, Build 6E, frozen kernels, CI or source file was modified.

### Primary acceptance: six field-type mutations

| Authored field type | Observable constructed/derived result | Before | After | New run identity? |
|---|---|---|---|---|
| cash | agent_cash | `50` | `70` | **YES** (`G1_SPONSOR_OPENING:9f6019ab465594fe7b5b`) |
| capability | agent_capabilities | `['EXPLORE']` | `['REVIEW_STUDY']` | **YES** (`G1_SPONSOR_OPENING:9c746b241b01f4f2e217`) |
| prior | agent_prior | `0.5` | `0.3` | **YES** (`G1_SPONSOR_OPENING:cdc69d2405e0728cd7cd`) |
| cost | potentially_affordable_looks | `5` | `3` | **YES** (`G1_SPONSOR_OPENING:3e985490a9582bf2fd9a`) |
| horizon | calendar_year_slots | `2` | `11` | **YES** (`G1_SPONSOR_OPENING:4ac57cea11e8de03ac64`) |
| policy | could_consider_exploration | `True` | `False` | **YES** (`G1_SPONSOR_OPENING:5c3aae3df098024e8dc6`) |

**Observation:** G1 does not execute an exploration policy. Cost changes a
data-driven affordability preview, horizon changes permitted calendar slots;
cash, capability, prior and policy are also reflected in actual kernel
opening objects. Those are substantive G1 effects, not merely echoing input.
Real paid exploration and post-2035 runtime behavior are deliberately untested.

### Advisory static name scan

PASS, but it only flags a short set of obvious module-level numeric/experiment
assignment names. It **cannot catch** indirect constants, nested/hard-to-name
defaults, a data field that is accepted but not consumed, missing effects,
or forged provenance. The mutation tests are the primary guard.

### Full reproducible machine report (all authored data and source digests)

The program output below includes the full authored scenario, **all six**
literal source paths and SHA-256 digests, actual source-module digest,
constructed opening fingerprint, source-derived Earth population admission
receipt count, and the new run identity. It contains no sealed-WORLD values.

```json
{
  "frozen_provenance": "PASS",
  "genesis_module_sha256": "521c759bb363b40c4daba07a2e46d0b1f2645d46d53f48737533f0f4f0b4e63b",
  "opening_result": {
    "agent_capabilities": [
      "EXPLORE"
    ],
    "agent_cash": "50",
    "agent_policy": "G1_CONSIDER_EXPLORATION",
    "agent_prior": "0.5",
    "calendar_year_slots": 2,
    "constructed_opening_fingerprint": "1b16bd1b454e05d1c48e66898ede70939a2c4f22e21ee674db3eff65e7b10b10",
    "could_consider_exploration": true,
    "last_calendar_year": 2027,
    "observation_offer_cost_used": "10",
    "potentially_affordable_looks": 5,
    "real_population_receipts": 1
  },
  "run_id": "G1_SPONSOR_OPENING:1e1a53c04f4795e19b93",
  "scenario": {
    "actors": [
      {
        "account": "SPN:FUNDS",
        "capabilities": [
          "EXPLORE"
        ],
        "id": "SPN",
        "kind": "PRIVATE_SPONSOR",
        "node": "EARTH:USA",
        "objectives": [
          "EVALUATE_DEVELOPMENT"
        ],
        "opening_cash": "50",
        "policy_ref": "G1_CONSIDER_EXPLORATION",
        "prior": "0.5",
        "prior_key": "BODY:MOON:VOLATILES"
      }
    ],
    "baseline_main_sha": "d3fd120c9a77954d3a7925aaf5285bd23c643b80",
    "bodies": [],
    "comparison": {
      "algorithm": "SHA256_FIRST64_DECIMAL_V1",
      "comparison_group": "G1_LOCAL_OPENING",
      "decimal_precision": "28",
      "decimal_rounding": "ROUND_HALF_EVEN",
      "key_schema": "LOOM_COMPARISON_RANDOM_V1",
      "policy_seed": "G1_POLICY_NO_ACTIONS",
      "world_seed": "G1_UNBOUND_WORLD_RANDOM_NOT_USED"
    },
    "mission_cost_future": {
      "hold_2026_cost": false,
      "post_boundary": "UNAVAILABLE_NO_MISSIONS_IN_G1"
    },
    "nodes": [
      {
        "id": "EARTH:USA",
        "kind": "EARTH"
      }
    ],
    "observation_offer": {
      "active_year": 2026,
      "cost": "10",
      "currency": "MODEL_CURRENCY"
    },
    "policies": {
      "G1_CONSIDER_EXPLORATION": {
        "may_consider_explore": true
      },
      "G1_WAIT_ONLY": {
        "may_consider_explore": false
      }
    },
    "projects": [],
    "scenario_id": "G1_SPONSOR_OPENING",
    "schema": "BUILD8_GENESIS_G1_SCENARIO_V1",
    "sources": {
      "simulation/offworld_mvp/build6e/named_world.py": "941c2f49f2766ac2f08425248e5400904a673d5ea5c2618afd455c689e93fbf4",
      "simulation/offworld_mvp/build7/generated_campaign.py": "6b0f97abd8ddab01bd4670136a7fcc51f0996088315220e8d31aeb2daa9f3096",
      "simulation/offworld_mvp/build7/inputs/BUILD7_EARTH_USA_2026_2045_V1.json": "b135d181910910338a6d4bcc5906f62a82256f4d8dcbc542d238be4ddaaada56",
      "simulation/offworld_mvp/build7/inputs/BUILD7_GENERATED_CAMPAIGN_V1.json": "c7bff005cdb3d3d03a7e43e2e176ac622bcb56cc0e549003091dd65ce9d9517f",
      "simulation/offworld_mvp/build7/runtime_flow.py": "b6044af978cadfaac286ca440cde711649217e38f4610e741f3b9b462b8fb7f5",
      "src/loom_world_authority/store.py": "1ee14c6914dd77dab06733bb0a2962f69ee5a27338b72dea60b93beb04c70353"
    },
    "status": "RESEARCH_NONCANON_GENESIS_ONLY_NOT_QUALIFIED",
    "test_alternatives": {
      "capability": [
        "REVIEW_STUDY"
      ],
      "cash": "70",
      "cost": "15",
      "horizon": 2036,
      "policy": "G1_WAIT_ONLY",
      "prior": "0.3"
    },
    "time": {
      "clock_ref": "SIM_YEAR_PLUS_2025_V1",
      "end_year": 2027,
      "start_year": 2026
    },
    "world_binding": null
  },
  "scenario_sha256": "8eb6b0cf7d94ff45b0dd1b31f529cfb2f03fa05344a2dae26aa69ec560da5092",
  "source_digests": {
    "simulation/offworld_mvp/build6e/named_world.py": "941c2f49f2766ac2f08425248e5400904a673d5ea5c2618afd455c689e93fbf4",
    "simulation/offworld_mvp/build7/generated_campaign.py": "6b0f97abd8ddab01bd4670136a7fcc51f0996088315220e8d31aeb2daa9f3096",
    "simulation/offworld_mvp/build7/inputs/BUILD7_EARTH_USA_2026_2045_V1.json": "b135d181910910338a6d4bcc5906f62a82256f4d8dcbc542d238be4ddaaada56",
    "simulation/offworld_mvp/build7/inputs/BUILD7_GENERATED_CAMPAIGN_V1.json": "c7bff005cdb3d3d03a7e43e2e176ac622bcb56cc0e549003091dd65ce9d9517f",
    "simulation/offworld_mvp/build7/runtime_flow.py": "b6044af978cadfaac286ca440cde711649217e38f4610e741f3b9b462b8fb7f5",
    "src/loom_world_authority/store.py": "1ee14c6914dd77dab06733bb0a2962f69ee5a27338b72dea60b93beb04c70353"
  },
  "standing": "UNQUALIFIED_G1_OPENING_NO_OBSERVATION",
  "strict_opening": "PASS"
}
```

### Not proven

- Not a qualified Build 8 simulation; the frozen four-module provenance check
  attests the *historical* module inventory, not new G1 qualification.
- No decision worker, private exploration policy, scheduled look, repeat draw,
  mission lineage, database persistence or replay across a database restart.
- No body/project/WORLD realization. No live information or admission invented.
- Year 2036 mutation only exercises the authored horizon preview; no future
  mission price is inferred or silently extended from 2026.
- WALTER and any future allowlist, G2/G3/G4 are outside this PR.

**Stop at G1. PR remains draft and unmerged pending kT approval.**

