# LOOM 2226 — Relational Foundations Independent Work Plan v0.3

**Date:** 7 September 2026  
**Status:** EXPLORATORY RESEARCH WORK PLAN — NON-CANON — NON-RUNTIME  
**Owner lane:** `research/rabbit_holes/`  
**Primary rule:** This workstream must not alter, import into, depend on, or block the Navigator / Solar GIS / runtime delivery workstream.  
**Current research posture:** preserve Relational Topography as the leading LOOM foundations research hypothesis, but treat every claimed step from toy relational dynamics to LOOM physics as independently falsifiable and non-promotional until earned.

---

## 1. Purpose

The Relational Foundations program asks a deliberately narrow first question before it is allowed to ask the larger LOOM questions:

> Can a dynamical relational system with no supplied ordinary spatial coordinates develop robust locality, effective dimension, and reconstructible geometric structure without those results being smuggled in by the model design?

The larger long-horizon question is now sharpened to:

> Can a coordinate-free relational dynamics generate robust locality and geometric order without target geometry being supplied by construction, and can the same underlying relational structure eventually support physically inequivalent embeddings, controllable transitions, and a globally acyclic causal order?

These are **research questions, not canon claims**. The first is the immediate computational target. The second defines the distant ladder of evidence that would be required before the research could materially constrain the fictional M1/M2 architecture.

This program is not a project to prove LOOM physics, derive a metric drive from contemporary physics, explain high-strangeness claims, or solve quantum gravity. It is a bounded computational and mathematical falsification program. A reproducible negative result is a valid success if it tells us which assumption supplied or prevented geometric emergence.

### v0.3 reason for revision

Version 0.3 incorporates four developments since the previous work-plan revision:

1. the recovered RQO-1 program was audited, reconstructed, and subjected to null, ablation, sign, and finite-trajectory qualification work;
2. the historical curvature action was found to contain both a **sign mismatch in its interpretation** and a **stochastic sampled-action implementation**, materially limiting equilibrium claims;
3. the corrected-sign curvature program nevertheless produced a small but directionally persistent locality-like shift through 10N proposals, while remaining far from the historical locality gate and becoming increasingly sticky;
4. an independent Claude review and subsequent adversarial discussion proposed three potentially valuable foundations refinements — a gauge/moduli-space route for possible M1/M2 unification, a structural causal-order route for chronology, and Group Field Theory/tensor-condensate mathematics as a possible graduation framework — while also confirming that no standard alternative transport picture currently offers an obviously cleaner LOOM architecture.

The practical consequence is **not** to abandon the current graph program and **not** to promote Relational Topography. Instead, the program is split more sharply into:

- a cheap, hostile **graph falsification track**;
- a separate **foundations track** for M1/M2 and chronology mathematics;
- a clearly gated **graduation track** to richer pregeometric frameworks only if the toy program earns it.

---

## 2. Authority, canon, engineering, and research boundaries

### 2.1 Governing source hierarchy

The current repository authority map and frozen v2.4 canon remain untouched. Governing authority includes:

- `governance/current/LOOM_2226_Canon_Baseline_Manifest_v2.4.md`
- `canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_III_Authority_Continuity_GM_Model_v2.4.md`
- `canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md`
- `canon/current/LOOM_2226_Core_Mechanics_v0.5.md`

Research companions include:

- `research/technical_papers/LOOM_2226_Technical_Paper_Series_Complete_v1.0.pdf`
- `research/rabbit_holes/LOOM_2226_Rabbit_Hole_Priority_Table_v1.3.md`
- `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf` in the research source corpus
- `research/relational_foundations/HISTORICAL_RECONSTRUCTION_v0.1.md`
- the RQO-1 protocols, reconstruction, null-scaling, sign-sensitivity, convergence, matter-preregistration, and instrumentation artifacts under `research/relational_foundations/`

The authority hierarchy remains:

`GOVERNING CANON > DERIVED CANON > declared PROVISIONAL MODEL > declared TEST FIXTURE > RESEARCH OPEN`.

No result in this work plan changes that hierarchy.

### 2.2 Connection to the foundational physics paper

The Technical Paper Series is the conceptual parent of this research program, but is not routine runtime authority. Its key discipline is preserved here:

- contemporary physics does **not** predict LOOM;
- M1 and M2 remain fictional physical permissions unless a later foundations program genuinely derives a more economical parent structure;
- ordinary GR/QFT/thermodynamics/conservation must be recovered in the low-energy / inactive-relational limit;
- identity preservation, non-duplication, global composability, conservation, and chronology are load-bearing constraints rather than decorative language;
- the deeper pregeometric action is research ancestry, not established physics;
- every arrow in the sequence from relational degrees of freedom to geometry, causal structure, continuum physics, autonomous domains, M1, and M2 must have an explicit stop/failure gate.

The work plan therefore preserves the Technical Paper epistemic stack:

- **E** — established physics or mathematics;
- **A** — analogy / mathematical ancestry;
- **P** — fictional postulate;
- **C** — constitutive closure / canon calibration;
- **D** — derived result;
- **O** — open problem.

No research result may silently migrate from A/O into P/C/D.

### 2.3 Connection to governing physics/engineering canon

CANON II v2.4 states the foundational engineering rule:

> **Physics generates engineering. Engineering may refine calibration, hardware and certification without adding a third miracle.**

That rule is binding on this research plan. The governing propulsion distinction remains:

- **TORCH** — ordinary momentum exchange;
- **METRIC** — continuous subluminal relational/metric transport;
- **LOOM** — discontinuous interstellar relational re-embedding.

The current research may investigate possible mathematical ancestry for the relational sector, but it may not rewrite the certified engineering stack, machine constants, Mc-299m/NRE calibration, metric speed card, environmental certification architecture, flight procedure, or ship state model.

In particular:

- FTL Metric remains a hard kill;
- Loom remains the sole FTL mechanism;
- Loom is route translation / relational re-embedding, not a hidden traversed corridor;
- no research result may add a separate free-energy, free-momentum, braking, inertia-cancellation, or chronology mechanism;
- engineering may not be used to tune the research action toward already-known ship performance.

### 2.4 Connection to hidden topology and Core Mechanics

CANON III v2.4 keeps the hidden Loom graph as objective GM/model topology and explicitly forbids narrative need from adding, deleting, or upgrading hidden edges. The research program therefore may **not fit to the hidden Loom graph**. Any emergent graph/topology produced here is a toy-model research object only.

Core Mechanics v0.5 also separates observation, solution, formation, commit, transition, relaxation, emergence, and reacquisition. Research outputs must not collapse these operational phases into one speculative physical variable.

Chronology remains operationally tracked through distinct records of **SHIP MET**, **EXT EPOCH**, and **CAUSAL OFFSET** where a discrepancy is established. A research hypothesis about deeper causal order does not authorize the runtime to normalize away such discrepancies or to invent a selectable temporal-navigation capability.

### 2.5 Runtime firewall

This branch of work SHALL NOT:

- edit anything under production `src/`, `web/`, `deploy/`, `data/`, `geometry/`, or runtime `tests/`;
- edit current canon or governance files;
- edit Navigator/HUD/Solar GIS/runtime architecture baselines;
- modify CORE, MEDIA, CIVSTATE, campaign/save/history SQLite files;
- import Navigator or GIS modules;
- call Navigator endpoints or consume Navigator route payloads;
- add dependencies to the production/runtime Python environment;
- change release hashes for runtime artifacts;
- make Navigator/GIS CI depend on research tests;
- block a Navigator/GIS release because research fails.

### 2.6 Physical/canon firewall

Research results SHALL NOT silently promote, demote, or retune:

- M1: degenerate physical embedding;
- M2: controllable relational susceptibility;
- the two-miracle accounting rule;
- chronology limits;
- the hidden Loom graph;
- Metric or Loom operating behavior;
- Mc-299m/NRE engineering calibration;
- courier mass/power/thermal values;
- world/history/economic/civilizational state.

If a toy model fails, canon does not automatically fail. If a toy model succeeds, canon is not thereby proved.

---

## 3. Current research state as of 7 September 2026

### 3.1 Historical RQO-1 lessons retained

Recovered and reconstructed project history establishes:

1. relation-first finite-degree graph ensembles naturally tended toward random-regular / expander-like behavior — project shorthand: **expander soup**;
2. short-cycle reward terms could make graphs look more local but created an answer-smuggling problem;
3. an internal simulation clock could create Lorentzian-looking diagnostics but did not derive GR/QFT and risked relabeling numerical update order as physical time;
4. the historical RQO-1 action used Ollivier-Ricci curvature and triangle terms with degree-preserving connected double-edge swaps;
5. the historical `+alpha * curvature_sum` convention was described as though positive alpha rewarded positive curvature, but under energy minimization it actually favored lower/more-negative curvature;
6. the historical sampled curvature diagnostic also contained a scaling issue at small N;
7. the recovered historical smoke test was scientifically insufficient and is not a verdict on RQO-1.

### 3.2 Corrected-sign program

The corrected-sign experimental action was separated from historical reproduction:

`S_C = -alpha * curvature_sum`

This is a **new experimental convention**, not a silent repair of historical code.

Across the bounded qualification program, corrected curvature produced a small but directionally consistent shift toward:

- slightly larger `avg_shortest_path / log(N)`;
- smaller normalized-Laplacian spectral gap;

relative to both the historical sign convention and, more weakly, the random-regular null.

The effect remained far below the historical provisional `1.3 * log(N)` path gate.

### 3.3 PR #17 convergence result and methodological limitation

The longer-trajectory convergence qualification at N=80, degree 4, seeds 2226–2228, T=1, corrected alpha=1, checkpoints 2N/5N/10N showed:

- the directional locality-like effect persisted at all checkpoints;
- the corrected-minus-null path/logN difference grew from roughly +0.0042 at 2N to +0.0121 at 10N;
- the corrected spectral gap remained below null at all checkpoints;
- the mean corrected acceptance fraction fell from about 0.085 at 2N to 0.035 at 10N;
- action autocorrelation was very high where defined;
- no seed crossed the historical path gate.

However, code audit established that `curvature_sum(..., max_edges=20)` uses random edge sampling on each action evaluation. Therefore the sampled action is **not a deterministic function of graph state**. The recovered/corrected sampled-action chain cannot currently be treated as ordinary Metropolis sampling of a fixed Boltzmann target.

The permitted conclusion is therefore narrow:

> **A small corrected-curvature directional effect is stable over longer sampled-action trajectories. This does not establish equilibrium, a thermodynamic phase, or detailed-balance sampling of a deterministic target.**

PR #17 is merged to `main` at `7c482f807c1592c46e328a90695d4ea824144ac9` after Pixel/Termux validation and 25/25 research tests passed.

### 3.4 Matter-induced locality preregistration

The separate matter-action work package remains preregistered and on hold pending closure of the curvature-comparator methodology.

Its field-theory-motivated candidate is:

`S_phi = 1/2 phi^T L phi`

with Gaussian integration giving:

`Z_phi[G] ∝ (det' L_G)^(-1/2)`

and effective matter action:

`Gamma_matter[G] = +1/2 log det' L_G`.

By Kirchhoff:

`det' L_G = N * tau(G)`

so the matter term has a real and dangerous failure mode: minimizing it can favor fewer spanning trees, bottlenecks, modular/barbell-like structures, or fragility rather than genuine locality.

For that reason Stage A includes explicit pathology diagnostics rather than treating path length or spectral gap alone as sufficient evidence.

---

## 4. Independent Claude review and adversarial refinement

### 4.1 Why the review matters — and what it does not mean

Claude was explicitly invited to discard Relational Topography if a better physical architecture existed. It did not. Instead it recommended retaining the top-level relational-topography idea while tightening its mathematical ancestry and separating the cheap graph toy from a possible richer parent framework.

That outcome is meaningful for **research-selection confidence**, because the review was not framed as a defense exercise. It surveyed standard alternatives including traversable wormholes, Alcubierre-type warp, ER=EPR-style transport, braneworld shortcuts, causal-set structures, and GFT/tensor approaches.

The review does **not** constitute independent empirical evidence for LOOM physics. Multiple language models reasoning over overlapping physics literature are not multiple laboratories. The correct update is:

- confidence that Relational Topography is a **good current LOOM research hypothesis** increases;
- confidence that Relational Topography is **true physics** barely changes.

### 4.2 Claude proposal A — gauge connection / moduli-space unification

Claude proposed a genuine gauge connection on the deeper relational state space:

`A_R`

with curvature:

`F_R = dA_R + A_R ∧ A_R`

and a flat-vacuum moduli space:

`M_flat = {A_R : F_R = 0} / G`.

Under this framing:

- M1-adjacent structure would arise if the physically meaningful relational sector admits multiple gauge-inequivalent vacua / embeddings;
- M2-adjacent control would arise if matter carrying the relevant relational coupling can bias finite-action transitions among those vacua;
- the existing schematic Euclidean transition action and `Gamma ~ exp(-B)` rate gain a clearer instanton/bounce ancestry rather than being treated as an isolated phenomenological formula;
- gauge-invariant observables, holonomy, Wilson-loop-like structure, and moduli-space topology offer concrete mathematical tools for distinguishing protected identity from external embedding data.

This is adopted as a **research refinement**, not a canon rewrite.

Crucially, it does **not yet reduce the miracle count**. A gauge sector with a nontrivial moduli space does not automatically imply controllable matter-driven transitions. Miracle reduction is earned only if one microscopic theory jointly yields both:

1. physically relevant embedding degeneracy / non-injective reconstruction;
2. finite-action, finite-authority matter controllability of transitions.

If the matter coupling has to be postulated independently with exactly the desired behavior, M1 and M2 remain separate fictional permissions.

### 4.3 Claude proposal B — causal-set-style chronology structure

Claude proposed replacing the current chronology IOU with a causal-set-flavored partial-order structure, arguing that an acyclic partial order structurally excludes closed causal loops.

The useful part is retained, but the original claim was too strong.

LOOM chronology is not solved merely because the relational edge relation is acyclic. Ordinary spacetime propagation and Loom transitions can each be individually acyclic while their **combined transitive closure** contains a cycle.

The stronger research target is therefore:

`prec_phys = TC(prec_g ∪ prec_R)`

with the requirement:

`x not prec_phys x` for all physically admissible events x.

The foundations question becomes:

> Can ordinary Lorentzian causal propagation and every admissible relational transition embed in one global acyclic order that is generated or preserved by the parent theory?

If this is genuinely derived, candidate-M3 chronology censorship may disappear. If it must be imposed independently, the third-miracle problem remains.

Claude also suggested checking whether current undirected Stage-A graphs are compatible with “some” partial order. That suggestion is **rejected for Stage A** because any undirected graph can be given an arbitrary acyclic orientation by imposing a vertex ranking. Such a post-hoc orientation would not be physical evidence. Causal-order work belongs in a later directed/ordered relational model where orientation is generated or dynamically preserved rather than assigned after the fact.

### 4.4 Claude proposal C — Group Field Theory / tensor condensates

Claude recommended Group Field Theory (GFT) / tensor-condensate mathematics as the eventual parent framework if the toy graph program earns graduation.

This is accepted as a **candidate graduation framework**, not as the next experiment and not as a canon ancestry claim.

The attraction is methodological:

- the current degree-regular NetworkX graph program is a deliberately crude falsification tool;
- GFT/tensor models are actual pregeometric many-body frameworks in which collective geometric behavior can be studied with field-theoretic machinery;
- they are better suited than “just scale the graph to 10,000 nodes” for eventual continuum, universality, condensate, and coarse-graining questions.

One Claude inference is explicitly rejected as too fast: many microscopic states mapping to the same coarse macrostate is **not automatically M1**. Ordinary statistical coarse-graining is non-injective everywhere. M1 requires the much stronger property that one protected physical subsystem identity can persist across physically inequivalent external embeddings. Any GFT/tensor ancestry must still earn that distinction.

### 4.5 Claude proposal D — standard transport alternatives

The review found no clean replacement that obviously improves the miracle budget:

- traversable wormholes import exotic stress-energy / stability / controllability problems and conflict with the no-hidden-corridor design;
- FTL Alcubierre-type warp remains excluded by governing canon and imports its own exotic-stress-energy burden;
- ER=EPR-style ideas do not supply controllable traversable transport without additional assumptions and do not remove the M2-equivalent control problem;
- causal sets provide causal structure but not by themselves a transport shortcut;
- braneworld/bulk-shortcut mathematics is a valuable analogy for `d_metric != d_deeper`, but simply relocates the unexplained questions to “why can matter access the bulk?” and “why does the bulk contain useful shortcuts?”;
- GFT/tensor models are better interpreted as possible parent mathematics for relational topography than as a competing transport mechanism.

The result is not “Relational Topography is true.” The result is:

> Relational Topography remains the best current LOOM research architecture because it combines canon fit, mathematical ancestry, minimal extra conceptual machinery, and the ability to fail cleanly under toy-model tests.

---

## 5. Revised research architecture

The program now has three explicitly separated tracks.

### Track A — graph falsification engine

Purpose: cheaply test whether relation-first local dynamics can move away from generic expander behavior without target geometry being supplied.

This track is intentionally small, reproducible, and easy to kill.

It is **not** a candidate fundamental theory.

### Track B — foundations mathematics

Purpose: separately sharpen the deeper questions that the Technical Paper leaves open:

- can a single relational gauge sector jointly support M1-like degeneracy and M2-like controllability?
- can protected identity be defined through a nontrivial algebraic/gauge-invariant structure rather than ordinary coarse-graining?
- can all ordinary and relational causal propagation be embedded in one global acyclic order?
- can the existing schematic transition-action language be given a disciplined instanton/moduli-space ancestry without pretending contemporary QFT predicts LOOM?

This track is conceptual/mathematical until a concrete model is justified.

### Track C — graduation framework

Purpose: identify the next microscopic language **only if** Track A either:

- produces robust locality worth explaining; or
- fails in a way that can be specifically attributed to limitations of fixed-degree undirected graph ensembles.

GFT/tensor-condensate approaches are a leading candidate, but not an entitlement. A failure diagnosis must be written before graduation.

---

## 6. Revised phase plan

### Phase 0 — historical reproduction and audit — substantially complete

The historical RQO-1 source, null behavior, sign convention, implementation limitations, and recovered smoke-test status have been audited. Historical code remains preserved rather than silently rewritten.

Outstanding historical work should be done only where it materially changes interpretation of the current program.

### Phase 1 — deterministic corrected-curvature control — NEXT

**Goal:** determine whether the corrected-curvature directional effect survives when the action is a deterministic function of graph state.

Run one bounded control using full/all-edge curvature rather than the 20-edge random sample.

Frozen principles:

- no new action term;
- no matter term;
- no coefficient sweep chosen after viewing output;
- no change to historical reconstruction;
- preserve matched null;
- preserve fixed-degree connected rewiring;
- preserve research-local reproducibility and tests;
- classify trajectory behavior separately from equilibrium behavior.

Primary question:

> Does the corrected-sign locality-like shift persist under a deterministic curvature energy suitable for ordinary Metropolis interpretation?

Possible outcomes:

- **PERSISTS under deterministic action** — corrected curvature may be used as a legitimate baseline comparator in Stage A, subject to mixing/equilibration caution;
- **DOES NOT PERSIST** — demote corrected curvature as a baseline and record the prior effect as specific to sampled-action dynamics;
- **COMPUTATIONALLY INTRACTABLE / MIXING FAILURE** — do not invent a success claim; revise only if the limitation is technically specific and preregistered.

No result from this phase is a locality-phase PASS by itself.

### Phase 2 — matter-determinant Stage A

**Goal:** test one physically motivated field-theoretic action family without answer-smuggling.

Frozen cells:

- `NULL`: `S_0 = 0`
- `CORRECTED_CURVATURE`: `S_C = -1.0 * curvature_sum` if Phase 1 qualifies it as comparator
- `MATTER_ONLY`: `S_M = +1.0 * Gamma_matter`
- `COMBINED`: `S_CM = -1.0 * curvature_sum + 1.0 * Gamma_matter`

No coefficient scan in Stage A.

Required diagnostics include:

- average path and path/logN;
- normalized-Laplacian gap;
- diameter;
- clustering and triangle count;
- connectivity / damage sensitivity;
- exact/validated log-det and spanning-tree relation;
- conductance/Cheeger-style bottleneck estimate with method documented;
- edge-betweenness concentration;
- node-betweenness concentration;
- low-mode eigenvector localization/IPR where cheap;
- action components and acceptance statistics.

Interpretation rules:

- gap reduction is not independent evidence when the action itself contains a spectral functional;
- bridges/articulation alone are insufficient in fixed degree 4;
- a multi-edge sparse cut / barbell-like structure counts as pathology even when literal bridges are absent;
- the historical 1.3 path/log gate is reference only, not a new success threshold;
- no partial-order/DAG diagnostic is added to this undirected Stage-A experiment.

Stage-A classification remains:

- `NO DIRECTIONAL EFFECT`
- `DIRECTIONAL EFFECT WITH BOTTLENECK PATHOLOGY`
- `DIRECTIONAL EFFECT WITHOUT OBVIOUS BOTTLENECK PATHOLOGY`

Only the third earns scaling. None is an RQO-1 / emergent-geometry PASS.

### Phase 3 — formal graph-program stop/go gate

This phase is mandatory. It exists to prevent endless action tuning.

If Stage A produces robust, pathology-free directional structure, perform only a preregistered scaling test sufficient to determine whether the signal strengthens, stabilizes, or disappears with N.

If Stage A again produces only tiny shifts, inconsistent seeds, or bottleneck/crumpled structure:

1. **freeze the current graph-action search**;
2. write a `GRAPH_ANSATZ_FAILURE_DIAGNOSIS` before adding any new microscopic family;
3. classify the failure as primarily:
   - implementation/mixing;
   - fixed-degree undirected ensemble limitation;
   - action-family limitation;
   - finite-size limitation with evidence;
   - deeper evidence against generic relation-first locality emergence;
   - unresolved.

The graph program may not graduate merely because we like Relational Topography.

### Phase 4 — one justified alternate microscopic family OR graduation

Only after Phase 3.

Two possible branches:

**4A — one additional cheap microscopic family**  
Allowed only if the failure diagnosis identifies one specific, tractable limitation and one principled alternative can test it without target geometry.

**4B — graduation to richer pregeometry**  
Allowed only if the diagnosis explains why a GFT/tensor/related framework contains specific structure missing from the graph ansatz and why that structure addresses the observed failure rather than simply adding tunable freedom.

No “GFT next because graph failed” automatic rule exists.

### Phase 5 — robust locality and dimension gate

Only after a legitimate ordered/non-expander phase exists.

Require:

- stable locality across seeds and declared perturbations;
- empirical null separation;
- at least two genuinely different effective-dimension estimators;
- finite-size drift analysis;
- a meaningful scaling window rather than one-number dimension claims;
- pathology veto survival.

Do not hardcode a target dimension.

### Phase 6 — emergent order / chronology foundations gate

Only after robust geometric order.

The numerical MCMC step is never physical time.

The research target is stronger than the previous `q_R = const` heuristic:

> identify whether the physical model supplies an internally defined relational order compatible with both ordinary causal propagation and admissible relational transitions such that the combined transitive closure is acyclic.

A causal-set-style partial order may be used as mathematical ancestry, but only if orientation/order is generated or preserved by the physical model rather than assigned post hoc.

Success here would support — but not automatically prove — retirement of candidate-M3 chronology censorship.

### Phase 7 — reconstruction and protected-identity gate

Ask whether relational observables reconstruct an effective geometry and whether the reconstruction map is non-injective in a physically meaningful way.

The test must distinguish:

- ordinary gauge redundancy;
- ordinary statistical coarse-graining;
- representational non-uniqueness;

from the stronger M1-adjacent requirement:

- one protected physical subsystem identity;
- multiple physically inequivalent external embeddings;
- acceptable information/leakage behavior;
- finite-action accessibility if dynamics is claimed.

Candidate mathematical tools include gauge-invariant observable algebras, holonomy/Wilson-loop-like observables, representation structure, correlation/entanglement invariants, and reconstruction-map analysis.

### Phase 8 — M1/M2 unification gate

Investigate the gauge/moduli-space hypothesis only after earlier gates justify it.

Research hypothesis:

> M1 and M2 may be descendants of one relational gauge sector rather than two unrelated fictional permissions.

A genuine reduction requires one microscopic framework to establish both:

- a physically relevant moduli/reconstruction degeneracy;
- finite, matter-coupled controllability of transitions across that structure.

If either requires an independent ad hoc permission, the two-miracle accounting remains.

### Phase 9 — continuum / IR gate

Only after all prior gates.

Questions include:

- continuum/universality behavior;
- Lorentzian effective structure;
- acceptable local relativistic propagation;
- ordinary GR/QFT/thermodynamic recovery in the inactive-relational limit;
- absence of hidden free-energy, free-momentum, or chronology channels.

No claim to derive Einstein gravity, the Standard Model, or real matter is allowed from a small graph/GFT toy result without an actual derivation.

### Phase 10 — foundations decision memo

Produce one explicit verdict:

- **STOP** — no robust emergence or no defensible bridge to the required physics;
- **REVISE ONCE** — one specific defect with one preregistered follow-up;
- **CONTINUE** — robust evidence earns a new work plan;
- **M1/M2 REMAIN FICTIONAL CLOSURE** — deeper program may still be scientifically interesting but has not reduced the canon miracle budget.

No automatic Phase 11 exists.

---

## 7. Revised hypothesis mapping

The existing H0–H13 sequence remains historical research context. v0.3 adds three refinements without silently replacing the source hypothesis paper.

### H5* — global causal-order compatibility

Replace the weak target “a causal orientation may be conserved/superselected” with the stronger research question:

> Do ordinary and relational causal processes embed in one global acyclic order whose transitive closure remains cycle-free under all physically admissible transitions?

This is an O/A research refinement, not canon promotion.

### H6/10* — gauge/moduli-space unification candidate

Sharpen the joint M1/M2 question:

> Can a single relational gauge sector with nontrivial physically meaningful moduli support both protected embedding degeneracy and matter-coupled finite-action controllability?

This is a candidate ancestry, not a claim that contemporary gauge theory predicts LOOM.

### Graduation hypothesis — GFT/tensor condensates

Treat GFT/tensor-condensate mathematics as one candidate next-level framework if and only if the graph-program diagnosis justifies richer many-body/pregeometric structure.

It is not part of the Stage-A action and does not alter current canon.

---

## 8. Success, failure, and anti-goalpost rules

A result is only scientifically interesting if it survives the following discipline:

1. no supplied x/y/z coordinates or target manifold in candidate dynamics;
2. no direct reward for the diagnostic used to declare success unless independently justified and explicitly discounted as non-independent evidence;
3. null distributions are measured rather than assumed;
4. seeds and parameter families are frozen before inspection;
5. pathology diagnostics are frozen before inspection;
6. finite-size behavior is reported rather than hidden;
7. mixing/equilibration limitations are stated explicitly;
8. a stochastic action is not called a deterministic equilibrium energy;
9. a graph effect is not promoted to geometry, dimension, continuum physics, M1, or M2 without passing each intermediate gate;
10. failure of one microscopic ansatz does not automatically kill canon, but repeated principled failures must be allowed to count against the broader research hypothesis.

The most important anti-goalpost rule added in v0.3 is:

> **A failed graph ansatz must receive a written failure diagnosis before the program may move to GFT, tensor models, causal sets, or another richer framework.**

---

## 9. Testing and reproducibility standard

Every research release must include:

- deterministic seed capture where the method is deterministic;
- explicit reporting of stochastic estimator use where it is not;
- environment/dependency manifest;
- unit tests for graph/state invariants and observables;
- functional test for a short deterministic simulation or explicitly documented stochastic contract;
- null-model regression tests;
- config snapshot for every published result;
- machine-readable output tables/JSON;
- hash/provenance record for promoted research results;
- no generated chart without underlying data export.

For substantive research changes, run unit + functional research tests before publication. Full Navigator/GIS end-to-end regression is not required and should not become required; if it does, the research/runtime isolation boundary has been violated.

Pixel/Termux remains a valid qualification environment for this research lane when dependencies are supported. Qualification output must record Python/platform/dependency status and the Git SHA used.

---

## 10. Repository isolation design

Preferred layout remains:

```text
research/
  rabbit_holes/
    LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md
  relational_foundations/
    HISTORICAL_RECONSTRUCTION_v0.1.md
    README.md
    protocols...
    config/
    src/
    tests/
    results/
    reports/
```

Research code must remain runnable independently of Navigator/GIS and must not require production SQLite state, campaign state, local GIS servers, production Android deploy roots, or runtime environment variables.

Historical reconstruction files must remain immutable unless a correction is explicitly versioned as a new research artifact.

---

## 11. Branch and merge discipline

Use branch naming family:

`research/relational-foundations-*`

Pull requests should touch only `research/relational_foundations/` plus, when necessary, this plan or the rabbit-hole register.

Merges into `main` require:

- research-local tests pass;
- no production/runtime files changed;
- no current canon/governance files changed;
- result status clearly `NON-CANON / NON-RUNTIME`;
- scientific claims traceable to established mathematics, declared analogy, fictional postulate, or reproducible project result;
- negative results and methodological defects preserved rather than rewritten away.

---

## 12. Explicitly out of scope / hard research kills

The following remain prohibited or non-evidentiary in this cycle:

- synchronicity or personal anecdote as calibration evidence;
- UAP, apparitional, psi, anomalous-cognition, psychedelic, or consciousness claims as M2 evidence/control mechanism;
- fitting to the hidden Loom graph;
- fitting to Navigator route times;
- fitting to Mc-299m, ship mass, speed, or engineering constants;
- wormhole/hyperspace reinterpretation of Loom;
- FTL Metric;
- ER=EPR as a destination mechanism;
- quantum teleportation as ship transport;
- duplication or destructive reconstruction;
- free energy/momentum/braking;
- arbitrary hidden-route editing;
- target dimension inserted into the action;
- direct path/gap/diameter/community/modularity/resistance optimization used as a disguised answer;
- simulation step relabeled as physical time;
- a causal order assigned post hoc and then claimed as emergent chronology protection;
- GFT/tensor complexity added merely because the graph result is disappointing;
- canon promotion from a toy-model result.

---

## 13. Immediate execution order

The near-term sequence is now frozen as:

1. **deterministic/full-curvature corrected-sign control**;
2. review comparator status;
3. **matter-determinant Stage A** under the existing preregistration/instrumentation rules;
4. mandatory graph-program stop/go diagnosis;
5. only then choose scaling, one justified alternate microscopic family, or a richer graduation framework.

The foundations-mathematics track may proceed in parallel as reading, theorem/model formulation, and hypothesis sharpening, but it must not alter the preregistered Stage-A action or success criteria.

---

## 14. Current executive verdict

Relational Topography remains the leading LOOM foundations research hypothesis **not because the project is committed to it, but because it currently has the best combination of**:

- compatibility with governing canon and engineering constraints;
- credible mathematical ancestry without claiming established support for LOOM itself;
- a route to potentially unify rather than proliferate fictional assumptions;
- compatibility with identity-preserving, non-corridor, non-duplication Loom translation;
- explicit chronology and conservation failure tests;
- and, most importantly, the ability to fail cleanly under inexpensive experiments.

The independent Claude review materially strengthened the case that the research question is well posed and that no obvious standard alternative currently dominates it. It did **not** materially strengthen the claim that the underlying physics is real.

Accordingly, the program will continue — but with stricter gates, stronger failure accounting, and a harder separation between:

`toy graph result -> relational geometry -> continuum physics -> protected identity -> controllable transitions -> LOOM`.

Every arrow must be earned.

---

## 15. Next work package

**Title:** Deterministic Corrected-Curvature Comparator Qualification  
**Status:** NEXT / PREREGISTER BEFORE EXECUTION

**Question:** Does the corrected-sign locality-like effect persist when curvature energy is evaluated deterministically over the graph rather than through the recovered 20-edge stochastic action estimator?

**Why now:** PR #17 established longer-trajectory persistence but simultaneously demonstrated that the sampled-action implementation cannot support ordinary equilibrium claims. Stage A should not use corrected curvature as an equilibrium comparator until this methodological debt is closed.

**Required deliverables:**

- frozen protocol;
- deterministic action implementation isolated from historical reconstruction;
- matched null;
- research-local unit + functional tests;
- Pixel/Termux qualification if computationally practical;
- machine-readable result;
- explicit comparator verdict;
- no matter action until verdict reviewed.

**Stop condition:** if deterministic full-curvature evaluation is computationally impractical at the preregistered scale, record that limitation and reduce scale only by an explicitly documented protocol amendment made before viewing comparative scientific output.

---

**End of v0.3 work plan.**
