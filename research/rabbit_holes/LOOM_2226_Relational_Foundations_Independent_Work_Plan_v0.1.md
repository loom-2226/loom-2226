# LOOM 2226 — Relational Foundations Independent Work Plan v0.2

**Date:** 6 September 2026  
**Status:** EXPLORATORY RESEARCH WORK PLAN — NON-CANON — NON-RUNTIME  
**Owner lane:** `research/rabbit_holes/`  
**Primary rule:** This workstream must not alter, import into, depend on, or block the Navigator / Solar GIS / runtime delivery workstream.

---

## 1. Purpose

Reopen the smallest scientifically useful part of the Relational Foundations rabbit hole:

> Can a dynamical relational system with no supplied ordinary spatial coordinates develop robust locality, effective dimension, and reconstructible geometric structure without those results being smuggled in by the model design?

This is not a project to prove LOOM physics, derive a metric drive, explain UAP/ghosts/synchronicity, or solve quantum gravity. It is a bounded computational falsification program intended to answer a narrower question: whether a clean toy model can make a map from relationships.

The expected result is failure or ambiguity. That is acceptable. A useful outcome is a reproducible negative result that identifies which assumption supplied or prevented geometric emergence.

**v0.2 change:** recovered project-history artifacts show that this experiment was already partially implemented on 28 August 2026. The immediate work therefore begins with historical reproduction and audit, not a clean-room rewrite.

---

## 2. Authority and non-interference boundary

### 2.1 Governing source hierarchy

The current repository authority map and frozen v2.4 canon remain untouched. The relevant governing sources are:

- `governance/current/LOOM_2226_Canon_Baseline_Manifest_v2.4.md`
- `canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_III_Authority_Continuity_GM_Model_v2.4.md`
- `canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md`
- `canon/current/LOOM_2226_Core_Mechanics_v0.5.md`

The following are research companions, not canon authority:

- `research/technical_papers/LOOM_2226_Technical_Paper_Series_Complete_v1.0.pdf`
- `research/rabbit_holes/LOOM_2226_Rabbit_Hole_Priority_Table_v1.3.md`
- `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf` in the project research archive / source corpus.
- `research/relational_foundations/HISTORICAL_RECONSTRUCTION_v0.1.md` — recovered research-history synthesis; not canon.

The Technical Paper Series deliberately fixes M1 and M2 as fictional postulates while requiring ordinary GR/QFT/conservation matching where applicable. The relational-foundations hypothesis work explicitly treats the deeper parent model as exploratory and says locality/dimensionality must survive actual failure gates rather than be assumed.

### 2.2 Runtime firewall

This branch of work SHALL NOT:

- edit anything under `src/`, `web/`, `deploy/`, `data/`, `geometry/`, or `tests/` used by Navigator/GIS/runtime;
- edit `engineering/current/` Navigator, HUD, Solar GIS, runtime or delivery baselines;
- edit current canon or governance files;
- modify CORE, MEDIA, CIVSTATE, campaign/save/history SQLite files;
- import Navigator or GIS modules;
- call Navigator endpoints or consume Navigator route payloads;
- add dependencies to the production/runtime Python environment;
- change repository release hashes for Navigator/GIS artifacts;
- make Navigator/GIS CI depend on research tests;
- block a Navigator/GIS release because the research branch fails.

The Navigator and GIS workstream remains authoritative for route geometry, ephemerides, flight execution, campaign state and visualization according to its existing architecture. This research workstream has no runtime authority.

### 2.3 Physical/canon firewall

Research results SHALL NOT silently promote, demote or retune:

- M1: degenerate physical embedding;
- M2: controllable relational susceptibility;
- the hidden Loom graph;
- certified metric operating modes;
- Loom translation behavior;
- Mc-299m engineering calibration;
- courier mass/power/thermal values;
- 2226 world/economic/civilizational state.

If a toy model fails, canon does not fail. If a toy model succeeds, canon is not thereby proved.

---

## 3. Historical state recovered before restart

The project file archive contains three important prior artifacts:

- `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf`;
- `RQO-1_protocol.md`;
- `rqo1_experiment.py`.

The preserved history establishes:

1. **AUIF v1** tested relation-first finite-degree graphs and produced random-regular / expander-like states rather than useful locality — project shorthand: **expander soup**.
2. Adding short-cycle terms could produce more local-looking states, but created a target-leakage problem: rewarding the desired geometric diagnostic is not the same as deriving geometry.
3. Adding an internal-clock constraint improved Lorentzian-looking propagation / causal structure but did not derive GR, QFT or realistic matter.
4. The project correctly stopped instead of retuning indefinitely.
5. On 28 August, **RQO-1** was then implemented as a more disciplined rerun using random-regular graphs, degree-preserving Metropolis rewiring, an Ollivier-Ricci + triangle action, multiple seeds, spectral/volume-growth diagnostics and an explicit broad-phase gate.
6. The recovered protocol records only a **tiny smoke-test FAIL** (`N≈40`, two trial cells, ~30 MCMC steps) and explicitly states that this was not a scientific verdict.
7. No recovered artifact yet proves that the intended full RQO-1 scan was executed to completion.

Therefore this plan must reproduce and audit the historical experiment before inventing a new one.

---

## 4. Research question and preregistered success criteria

### 4.1 Primary question

Given a finite set of relational degrees of freedom with no assigned ordinary coordinates, can a physically motivated local minimum / ordered phase emerge whose large-scale observables are consistent with a stable low-dimensional geometry?

### 4.2 Minimum success criteria

A run is only "interesting" if all of the following are demonstrated without post-hoc retuning to a target answer:

1. **No supplied embedding:** no x/y/z or target manifold is used in the dynamics.
2. **Emergent locality:** graph neighborhoods become stable and non-expander-like over a sustained regime.
3. **Dimension signal:** at least two independent estimators converge toward a stable effective dimension over a meaningful scale window.
4. **Robustness:** the result survives multiple random seeds and a declared perturbation family.
5. **Nontriviality:** shuffled/null models do not produce the same signal at comparable frequency.
6. **No hidden answer:** ablation shows that removal of any explicit locality-promoting term does not simply reveal that geometry was put in by hand.

### 4.3 Stronger, later criteria

Do not pursue these until the minimum gate passes:

- Lorentzian/causal structure;
- emergent internal clock/order;
- reconstructible effective metric;
- continuum-limit behavior;
- GR-like infrared dynamics;
- QFT-like propagation;
- non-injective reconstruction relevant to M1;
- controlled relational perturbation relevant to M2.

---

## 5. Phase plan

### Phase 0 — RF-WP0: Historical reproduction and audit

**Goal:** establish exactly what was previously implemented, what actually ran, and where the earlier work stopped before writing replacement theory code.

Preserve and audit the recovered 28 August artifacts.

Required tasks:

- recover the full historical `RQO-1_protocol.md` and `rqo1_experiment.py` source into the research lane without modifying their scientific logic;
- record source hashes and original timestamps where available;
- reproduce the historical smoke test with the recovered code;
- establish a standalone dependency/environment manifest;
- add research-local unit tests for graph invariants, curvature helper behavior, dimension diagnostics and deterministic seed handling;
- identify implementation bugs separately from theoretical/model defects;
- reproduce the original `alpha/beta` grid and seed policy;
- run increasing-N null ensembles to measure the actual finite-size distribution of expander diagnostics;
- replace or justify the provisional `1.3 × log(N)` cutoff using empirical null-ensemble statistics and/or a defensible graph-theoretic criterion;
- explicitly run null, curvature-only, triangle-only and curvature+triangle ablations;
- determine whether any recovered result supports a scientific PASS, FAIL, or only INCONCLUSIVE.

**Critical rule:** do not modify the action to improve results during RF-WP0. Reproduction first.

**Exit artifact:** `RF_WP0_HISTORICAL_REPRODUCTION_REPORT_v0.1.md` with one of:

- `HISTORICAL RESULT REPRODUCED`;
- `HISTORICAL IMPLEMENTATION DEFECT FOUND`;
- `HISTORICAL EVIDENCE INSUFFICIENT / INCONCLUSIVE`.

Only after this report is accepted may Phase 1 begin.

### Phase 1 — Freeze the new experiment contract

**Goal:** prevent us from moving the goalposts after seeing output.

Create only research-local artifacts:

- `research/relational_foundations/README.md`
- `research/relational_foundations/EXPERIMENT_CONTRACT_v0.1.md`
- `research/relational_foundations/config/`
- `research/relational_foundations/notebooks_or_reports/`
- `research/relational_foundations/src/`
- `research/relational_foundations/tests/`

Before any **new** simulation logic is committed, freeze:

- graph/state definition;
- allowed dynamics;
- observables;
- null models;
- seed policy;
- pass/fail thresholds;
- forbidden post-hoc tuning rules.

The new contract must explicitly state what is inherited unchanged from historical RQO-1 and what is being replaced, with reasons.

**Exit:** experiment contract reviewed against Paper I, Relational Foundations Hypotheses v0.2, and RF-WP0 findings.

### Phase 2 — Baseline nulls

**Goal:** know what meaningless graphs look like under our metrics.

Implement standalone generators for:

- Erdős-Rényi-like random graphs;
- random regular graphs;
- preferential-attachment graphs;
- small-world controls;
- explicitly geometric graphs used only as positive controls, never as candidate dynamics.

Measure:

- degree distribution;
- clustering;
- path-length distribution;
- expansion/conductance proxies;
- spectral gap;
- graph curvature proxy if justified;
- random-walk return probability;
- spectral dimension estimate;
- local neighborhood growth dimension.

**Exit:** metrics correctly distinguish obvious random/non-geometric controls from explicit geometric positive controls.

### Phase 3 — Minimal relational dynamics A

**Goal:** test whether the simplest defensible dynamics produce ordered locality without coordinates.

Start deliberately small. Candidate state:

`W_t = (Gamma_t, Phi_t, Q_t)`

where `Gamma_t` is a dynamical relation graph, `Phi_t` optional node/edge state, and `Q_t` conserved bookkeeping if the chosen dynamics require it.

Rules must be local in relational state, not local in hidden Euclidean coordinates.

Run fixed parameter grids selected before results are inspected.

**Kill condition:** no robust locality/dimension signal across the preregistered grid.

If killed, document why and stop. Do not add complexity in the same phase.

### Phase 4 — Minimal relational dynamics B

**Only if Phase 3 produces a legitimate near miss or partial signal.**

Test one additional dynamical family motivated by published pregeometry / graphity / causal / quantum-information analogues. One family per work package; no soup model.

Required comparison:

- baseline dynamics;
- added term/dynamics;
- ablation;
- null ensemble.

**Kill condition:** geometry appears only when the new term is equivalent to explicitly imposing locality or target dimension.

### Phase 5 — Emergent ordering/time probe

**Only after a stable geometric phase exists.**

Test whether an internal monotone ordering variable or relational clock can be defined from the system itself rather than using simulation step number as physical time.

The external numerical step remains bookkeeping. It must not be silently relabeled as emergent physical time.

**Exit:** either a defensible internal-order observable exists, or the result is recorded as an explicit failure.

### Phase 6 — Reconstruction probe

**Only after Phases 3/4 and 5 pass.**

Ask whether relational observables permit reconstruction of an effective metric/geometry and whether the reconstruction is unique.

This is the earliest phase that may touch the M1-adjacent question of non-injective reconstruction.

A non-unique reconstruction is not automatically M1. It is only a candidate mathematical ancestry requiring further work.

### Phase 7 — Decision gate

Produce one concise decision memo:

- **STOP:** no robust emergence; archive code/results and do not expand the workstream.
- **REVISE ONCE:** a specific tractable defect is identified with one justified follow-up experiment.
- **CONTINUE:** robust emergent locality/dimension survives ablation/null/seed tests and warrants a second research plan.

No automatic Phase 8 exists.

---

## 6. Testing and reproducibility standard

This research lane inherits the project discipline that code releases receive tests before use, but it remains isolated from production regression.

Every research release must include:

- deterministic seed capture;
- environment/dependency manifest;
- unit tests for graph/state invariants and observables;
- functional test for a short deterministic simulation;
- null-model regression tests;
- config snapshot for every published result;
- machine-readable output tables;
- hash/provenance record for any promoted research result;
- no generated chart without underlying data export.

For substantive changes, run unit + functional research tests before publication. Full Navigator/GIS end-to-end regression is **not required** because this workstream must not touch those systems. If a change ever creates a reason to run Navigator/GIS regression, that is evidence the isolation boundary has been violated and the change should be redesigned.

---

## 7. Repository isolation design

Preferred future layout:

```text
research/
  rabbit_holes/
    LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md
  relational_foundations/
    HISTORICAL_RECONSTRUCTION_v0.1.md
    README.md
    EXPERIMENT_CONTRACT_v0.1.md
    historical/
    config/
    src/
    tests/
    results/
    reports/
```

Research code must be runnable independently, for example:

```text
python -m research.relational_foundations.src.run_experiment --config <research-config>
```

It must not require:

- `LOOM_2226.sqlite3`;
- `LOOM_2226_media.sqlite3`;
- `LOOM_2226_CIVSTATE.sqlite3`;
- a Navigator campaign state;
- a GIS local server;
- Android deployment paths;
- production runtime environment variables.

Production launchers must never discover or execute the research package automatically.

---

## 8. Branch and merge discipline

Use a dedicated branch naming family for implementation work:

`research/relational-foundations-*`

Do not develop this work on a Navigator/GIS feature branch.

Pull requests should touch only `research/relational_foundations/` plus, when necessary, this plan or the rabbit-hole register. A PR that modifies production/runtime paths must be split before review.

Merges into `main` are allowed only when:

- research-local tests pass;
- no production files changed;
- no current canon/governance files changed;
- result status is clearly `NON-CANON / NON-RUNTIME`;
- any scientific claim is traceable to either an external source, a declared analogy, or a reproducible project result.

---

## 9. Explicitly out of scope

The following are prohibited in the first research cycle:

- Kevin/Nicole synchronicity as evidence;
- UAP reports as calibration data;
- ghosts, psi, anomalous cognition or consciousness as a physical control mechanism;
- retrocausality claims;
- ER=EPR as a destination mechanism;
- quantum teleportation as Loom transport;
- wormhole/hyperspace reinterpretation of the Loom;
- fitting to the existing hidden Loom graph;
- fitting to Navigator route times;
- fitting to Mc-299m or courier engineering constants;
- updating LOOM canon from a toy-model result.

If later mathematics independently predicts a discriminating anomalous signature, a separate evidence plan may be proposed. It may not be back-filled into this work package.

---

## 10. First executable work package: RF-WP0

**Title:** Reproduce before reinventing.

**Scope:** historical recovery, reproduction and audit only.

**Deliverables:**

1. recovered RQO-1 source preserved under `research/relational_foundations/historical/`;
2. source provenance and hashes;
3. standalone environment manifest;
4. deterministic smoke-test reproduction;
5. research-local unit and functional tests around recovered implementation;
6. increasing-N null calibration;
7. null / curvature-only / triangle-only / combined ablation matrix;
8. scientific status memo: REPRODUCED / DEFECT / INCONCLUSIVE.

**Budget rule:** keep RF-WP0 computationally cheap enough to run locally on ordinary desktop hardware. Do not escalate compute until the recovered implementation has been validated.

**Do not begin a new action family automatically.**

---

## 11. Relationship to existing rabbit-hole priorities

This plan is a narrow sub-work-package under the existing deep-theory seam represented by RH-024, not a replacement for the ranked Rabbit-Hole Priority Table.

It does not displace higher-priority LOOM engineering, simulation, Navigator, GIS, CIVSTATE, Wayfarer, or gameplay work. Its value comes specifically from being cheap, isolated, and easy to stop.

Recommended project posture:

- Navigator/GIS/runtime: continue on their existing delivery path;
- relational-foundations work: opportunistic side-lab only;
- canon: frozen unless separately and explicitly amended;
- research success: earns another research question, not canon promotion.

---

## 12. Final decision rule

The project should bother with relational foundations only while each step buys a sharper test.

The immediate question is no longer simply "can relationships make a map?"

It is:

> **What exactly did the earlier model demonstrate, can we reproduce it, and can we distinguish a real failure of the relational hypothesis from a failure of implementation, scale, diagnostics, or an action that smuggled in the desired answer?**

If reproduction fails because the historical implementation was defective, fix only the defect and rerun.

If reproduction confirms expander soup under principled tests, preserve the negative result and stop or revise once.

If a broad non-expander finite-dimensional phase survives proper nulls and ablations, attack it harder before claiming anything.
