# CIVPROP-0 Earth–Luna prospecting reference experiment

**Result: PASS — bounded scenario experiment, not operational mission qualification.**
Class: `class:engineering`. Main basis: `b22703ab7ce5586fecfeda0998d19b7d1fbbfe30`.
Architecture basis: open PR #321 at `bb117d933a863fab4dbedc2add3783c7cad004a1`;
that PR was neither changed nor merged. Review/acquisition date: 2026-09-28.

## Exact experiment and results

Australia (`AUS`, existing Earth country identity) considers one robotic mission
from Earth through orbit to a **synthetic** site within a lunar polar permanently
shadowed region. Departure: 2026-09-28 UTC; arrival/observation: 2026-10-03 UTC.
The question is binary local ice presence, not recoverable inventory or ore grade.
There is one actor, one mission, one site and one observation per executed run.
The two saved runs are independent trials of the same experiment.

| Saved run | Seed | Evaluator-only ice truth | Observation | Prior → posterior | Decision | Capital |
|---|---:|---|---|---|---|---|
| `runs/adverse.json` | 0 | absent | no detection | 0.30 → 0.0703125 | PROSPECT → REJECT | 100 − 5 = 95 |
| `runs/favourable.json` | 1 | present | detection | 0.30 → 0.7083333333 | PROSPECT → CONTINUE | 100 − 5 − 50 = 45 |

The mission expenditure funds a survey instrument. CONTINUE funds analysis
capacity for that existing instrument under an explicit scenario rule; it creates
no mine, settlement or second mission. Potential value is never booked as cash.
Before observing, the standalone continuation option has expected net value −20;
positive information changes it to approximately +20.8333, negative information
to −42.96875. Expected value of sample information, less mission cost, is +2.5.
Low capital, excessive prospecting cost or unavailable technology produces WAIT
with no expenditure, mission, observation or infrastructure.

## Runtime semantics earned

Frozen dataclasses represent Run, Actor, KnowledgeState, Opportunity, Decision,
Mission, Observation, CapitalTransaction, InfrastructureChange and Event. No ORM,
database schema, service or new dependency is introduced for replay.

`actor.py` receives only knowledge, observation, economic parameters, budget and
feasibility. It receives neither the seed, run artifact nor the instrument. Only
`observation.py` owns and reads the frozen physical realization. Evaluator audit
truth is deliberately included in the portable artifact, **not in the actor API**.
This is an in-process code/data-flow firewall, tested by imports/signatures and
behavior; it is not a security sandbox against hostile Python introspection.

The observation uses sensitivity 0.85 and false-positive probability 0.15, both
scenario inputs. Bayes' rule updates the probability of local ice; site mismatch,
duplicate observations and malformed evidence classes/measurement units fail.
An unchanged belief produces unchanged decisions regardless of unrelated physical
realizations. Tests include false positives and false negatives; seed 2 produces
a positive observation despite absent ice, followed by CONTINUE as it should.

SHA-256 keyed draws separate physical realization from instrument error and use
seed, body/site identity, generator/prior versions and empirical-context identity.
Unrelated discovery order cannot advance a global random stream. Run IDs additionally
bind complete inputs, scenario configuration and implementation hashes. JSON replay
re-executes the model and compares the entire result/causal trace, rejecting changes.

Events are appended internally with stable IDs, simulation times, actor/run IDs,
causal parents and authority-labelled payloads. Capital transactions and funded
assets are explicit; the final balance is reconciled to starting scenario capital.
The experiment owns these deltas and performs no withdrawal from Earth authority.

## Existing authorities consumed

- **Earth:** read-only `loom_earth.earth_area` AUS identity and validated snapshot
  `earth-v0-1-9934d0ac-20260925`. No Earth economy/capital number is misrepresented
  as available actor funds. Scenario credits provide the bounded budget.
- **Solar:** read-only `loom_solar` Earth/Moon identities, active NAIF identifiers,
  qualified DE440 source and coverage records. The promoted
  `src/loom_spice_ephemeris_adapter.py` and shared spatial service actually resolved
  both bodies at departure and arrival, using pinned DE440 and NAIF0012 assets.
  Four vectors/provenance records are frozen in `inputs.json`; frame is the
  promoted service's `J2000/ECLIPTIC` label, underlying SPICE `ECLIPJ2000`, km/km/s.
  The open Inspector/Basemap branches are not dependencies.
- **Solar Facts/M4-B:** existing `MOON_POLAR_WATER_ICE` assertion and its provenance
  from `campaign_assertions.json`, explicitly retained as **CANDIDATE** and
  **PRESENT_UNQUANTIFIED** with regional scope. Synthetic-site abundance remains
  null/UNKNOWN. Regional presence allows uncertain local presence; it neither
  establishes a local probability nor guarantees ice at this invented site.
- **Timeline:** read-only `loom_timeline.interpretation_rule` records are retained
  with their source identity. They constrain the interface: the date does not
  unlock technology, private access or installed capacity. Technology availability
  is separately declared in the scenario. No future milestone is auto-triggered.
- **M2 / Navigator / CIVSTATE:** inspected for boundaries, not executed as authority
  replacements. D&O remains an external economic-kernel seam. Retained Navigator's
  future-ship direct route workflow is unsuitable as a complete robotic lunar
  surface mission. CIVSTATE is unnecessary for this country's scenario delta.

`capture_inputs.py` uses a single repeatable-read **READ ONLY** PostgreSQL
transaction and governed local assets. No database write, migration or schema
creation was performed. Frozen input file hashes and source hashes are checked;
normal runs/replay require only Python's standard library and repository files.
The JSON bundle is a disposable immutable experiment input, not editable authority.

## Scenario fixtures and gaps

All numeric decision parameters are **SCENARIO_TEST_INPUT**: prior 0.30, instrument
0.85/0.15, capital 100, mission cost 5, continuation cost 50, contingent option
value 100, strict net-value threshold 0, in artificial scenario credits with no
currency conversion. No parameter is a measured Solar fact or D&O reproduction.
The expected contingent value is an option/science-value fixture, not mining revenue.

`assess_mission` is a narrow typed tri-state transport interface. It verifies the
requested endpoint states/epochs/frame/units/navigation status and explicit
technology availability. FEASIBLE means **conditional on scenario assumptions**:
launch, five-day transfer, polar landing and execution succeed. Endpoint separation
is context only, never a trajectory or delta-v. Missing pinned epoch context or
unknown technology returns UNKNOWN; unavailable technology returns INFEASIBLE.
There is no Basemap geometry, restored Navigator authority or new trajectory solver.

Exposed gaps are qualified surface-to-orbit/transfer/landing mission estimates,
site coordinates/terrain and resource inventory, calibrated instrument/prior data,
actor-specific spendable budgets/access, and validated resource economics. Mission
failure risk and communications latency are not modelled; execution/receipt are
coarsened to the declared arrival time. These limits do not justify a research
campaign or permanent schema in this experiment.

## Tests and hostile review

Tests were written first and initially failed on missing implementation. Final
bounded suite: **19/19 PASS**, covering all 12 requested semantics, full causal loop,
committed positive/negative artifacts, fresh-process CLI replay, source hashes,
invalid inputs, noisy detection, rational WAIT and evidence-status preservation.

Hostile review checked oracle access, observation scope, duplicate information,
UNKNOWN/null preservation, scenario/evidence separation, input/trace tampering,
funding before infrastructure, and unaffordable follow-up option values. Invalid
observation labels/units were rejected and the discovery-order fixture was corrected
to stay within the intentionally supported lunar-polar scope. No authority file
was changed; only the experiment and this report are added. No broad regression ran.

## Architectural lessons and next milestone

Likely durable concepts: run/input/model identity; scenario seed and physical
realization reference; actor reference; scoped observation and ownership;
knowledge revision; mission and opportunity assessment with liens; decision with
input rationale; capital transaction; funded infrastructure change; causal event.
These are lessons, **not a proposed permanent PostgreSQL schema**.

Keep keyed random sampling, Bayes arithmetic, expected-value calculations,
ephemeris evaluation and transport assessment runtime-derived. Pin their inputs
and versions; retain decisions/observations/transactions for audit. Do not copy
Earth/Solar ownership into CIVPROP. A generated realization remains scenario truth,
and its observation remains simulated even when it resembles empirical evidence.

**Recommended next milestone:** qualify one replaceable Earth–Luna robotic
mission transport/cost adapter against this same loop, retaining the scenario
fallback and tri-state uncertainty. Stop at this one dependency seam; defer
permanent persistence, general priors, additional actors and destinations.

## Reproduce

From repository root (Python 3.12 used):

```sh
python3 -m unittest engineering.civprop.civprop0.test_civprop0 -v
python3 -m engineering.civprop.civprop0.experiment --seed 1 --output /tmp/civprop0.json
python3 -m engineering.civprop.civprop0.experiment --replay /tmp/civprop0.json
python3 -m engineering.civprop.civprop0.experiment --replay engineering/civprop/civprop0/runs/adverse.json
```

Optional recapture requires the existing host PostgreSQL/qualified SPICE assets
and Solar virtual environment; it intentionally replaces only the disposable
input files and invalidates old artifacts if inputs changed. Ordinary reproduction
must use the committed capture rather than recapturing current database state.
