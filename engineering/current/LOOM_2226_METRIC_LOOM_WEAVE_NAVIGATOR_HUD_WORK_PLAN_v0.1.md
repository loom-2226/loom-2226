# LOOM 2226 — Metric / Loom / Weave to Navigator-HUD Work Plan v0.1

**Class:** ENGINEERING  
**Status:** ACTIVE CANDIDATE WORK PLAN / NON-CANON  
**Parent foundation:** \`engineering/current/LOOM_2226_METRIC_LOOM_WEAVE_FICTIONAL_ENGINEERING_FOUNDATIONS_v0.1.md\`

## 0. Objective

Turn the fictional-engineering foundation into deterministic software that can:

1. evolve a Weave state with Tick/Tock dynamics;
2. generate an inspectable metric;
3. reproduce current Metric operating cards as calibrated fictional control solutions;
4. solve M2 inverse-control problems;
5. evaluate Loom attachment candidates \(T_{AB}\);
6. model M1 as a replaceable Mc-299m constitutive layer;
7. expose all relevant state to Navigator;
8. drive a HUD that shows actual solver outputs rather than decorative numbers.

Development order:

\[
\boxed{
\text{model}
\rightarrow
\text{unit tests}
\rightarrow
\text{functional tests}
\rightarrow
\text{Navigator}
\rightarrow
\text{HUD}
}
\]

not:

\[
\text{HUD}
\rightarrow
\text{retrofit equations}.
\]

## 1. Governance / dependency posture

### Change class

\`class:engineering\`.

### Upstream consumed authority

- Canon II Engineering Ships & Operations v2.4;
- Wayfarer Schematic Amendment v2.4a;
- current Metric/Loom plant quantities and operating-state contract;
- existing \(\beta_{\rm machine}=\chi_MJ_M/N_{\rm eff}\) reduced-order law;
- current Loom/lattice coherence separation;
- current Navigator authority boundary.

### Downstream impact at plan creation

- runtime: unchanged;
- data/SQLite: unchanged;
- Navigator: future review required at implementation stage;
- HUD: future review required at implementation stage;
- 3D: unchanged for now;
- release/Pixel/Windows: unchanged for now.

### Research boundary

Relational Foundations and anomaly research do not supply engineering authority for this program.

Any external or Research Lab work may inform options only through normal governed intake.

## 2. W0 — Vocabulary and schema freeze

**Goal:** make every existing Metric/Loom term map to one mathematical object.

Freeze typed conceptual schemas for:

- \(\mathcal L=(V,E,F,C,\partial)\);
- \(W=(Q,P)\);
- Tick/Tock state;
- tetrad/frame field \(e^A_{\ \mu}\);
- 3+1 readout \(N,\beta^i,\gamma_{ij}\);
- Metric path operator \(U_\gamma^M\);
- Loom translation map \(T_{AB}\);
- committed domain \(D\);
- boundary \(\Sigma\);
- Loom coherence \(C_L\);
- lattice coherence \(C_D\);
- mismatch functional \(\mathcal J_{AB}\);
- M2 abstract control vector \(u\);
- M1 constitutive mapping \(\mathcal C_{\rm Mc}\).

### Exit

- no duplicate meanings;
- units and frames explicit;
- unresolved coefficients represented as unknown/candidate, never silently zero;
- adapters defined for existing Navigator/engineering names.

## 3. W1 — Weave Kernel v0.1

**First executable target.**

Candidate module:

\`src/loom/weave/weave_kernel.py\`

The initial kernel should do only:

\[
W_n
\xrightarrow{\rm Tick/Tock}
W_{n+1}
\xrightarrow{\mathcal M}
g_{\mu\nu}
\xrightarrow{\rm diagnostics}
\{\text{constraints, curvature, stability}\}.
\]

### Minimum implementation

- small cell-complex representation;
- \(Q,P\) state containers;
- Hamiltonian interface;
- fixed-step symplectic Tick/Tock integrator;
- deterministic seed/configuration;
- constraint residuals;
- reproducible serialization.

### Required unit tests

- deterministic replay;
- known static state remains static;
- reversible test case where appropriate;
- bounded numerical drift over preregistered toy intervals;
- invalid state rejected;
- units/schema validation.

### Stop rule

Do not implement Loom translation or M1 until the kernel is numerically clean.

## 4. W2 — Metric Forward Solver

Implement:

\[
W
\rightarrow
e^A_{\ \mu}
\rightarrow
g_{\mu\nu}
\rightarrow
\{N,\beta^i,\gamma_{ij}\}
\rightarrow
\Gamma
\rightarrow
R.
\]

### Deliverables

- metric tensor at requested sample points;
- lapse/shift/spatial metric;
- curvature/tidal diagnostics;
- causal/pathology checks;
- field residuals;
- external-environment coupling interface;
- uncertainty container.

### 208-node basis

Introduce node basis functions \(N_k(x)\):

\[
Q(x)=Q_0(x)+\sum_{k=1}^{208}q_kN_k(x).
\]

Do not freeze physical node positions merely to complete the solver.

### Exit

A legal toy Weave state produces a deterministic, internally consistent metric readout and diagnostics.

## 5. W3 — Bind current Metric cards

Goal: connect current engineering cards to the new forward model without redefining their governing values.

Interpret

\[
\beta_{\rm machine}
=
\chi_M\frac{J_M}{N_{\rm eff}}
\]

as a reduced-order axial control relation.

Represent NORMAL / FAST / EXPEDITE / HARD as certified target Weave states or bounded control manifolds.

### Required result

For each card, the solver returns a stable target state whose reduced-order \(\beta\) agrees with the existing card interface within a frozen fictional calibration tolerance.

### Important distinction

This is **model calibration to governing fictional engineering**, not scientific validation.

### Power model

Separate:

- ramp energy;
- hold power;
- cryogenic load;
- control losses;
- correction power;
- field-bank state;
- environmental derating.

Preserve:

\[
\dot m_{\rm remass}=0
\]

for Metric operation.

## 6. W4 — M2 inverse-control solver

M2 solves:

\[
g^*_{\mu\nu}
\rightarrow
u^*
\]

or:

\[
T_{AB}^*
\rightarrow
u^*.
\]

Start with linearized/quadratic control around qualified operating points:

\[
u^*
=
\arg\min_u
\left[
\|g(W(u))-g^*\|_Q^2
+
\lambda\|u\|_R^2
+
\mu\|\mathcal C(W)\|^2
\right].
\]

Then consider nonlinear/model-predictive control only if required.

### M2 must return

- requested target;
- achieved target;
- actuator vector;
- residual;
- constraint margins;
- energy/bank estimate;
- thermal burden;
- convergence status;
- explicit infeasible state when appropriate.

### Unit/functional tests

- reachable target;
- unreachable target;
- damaged-node target;
- thermal-limited target;
- field-bank-limited transition;
- deterministic repeated solve.

## 7. W5 — Loom Formation / \(T_{AB}\)

Implement bounded domain \(D\) and boundary \(\Sigma\).

For candidate destination B evaluate:

\[
T_{AB}:\Sigma_A\rightarrow\Sigma_B.
\]

Start with candidate boundary diagnostics:

\[
\Delta h_{ab},
\qquad
\Delta K_{ab},
\qquad
\Delta P,
\qquad
\Delta E.
\]

Construct:

\[
\mathcal J_{AB}
=
w_h\|\Delta h\|^2
+
w_K\|\Delta K\|^2
+
w_P\|\Delta P\|^2
+
w_C\|\mathcal C\|^2
+
w_E\|\Delta E\|^2.
\]

### Output

Navigator receives ranked candidate attachment solutions, not a single magic boolean.

Each candidate must expose:

- route/attachment burden;
- uncertainty;
- environmental burden;
- boundary mismatch components;
- ordinary-state momentum consequence;
- lattice requirement;
- failure/hold reason.

### Stop rule

No committed translation state until route and lattice axes are separately inspectable.

## 8. W6 — Loom and lattice coherence vectors

Do not collapse immediately into a universal scalar.

### Loom coherence vector

Candidate components:

- route existence/support;
- boundary geometry compatibility;
- curvature compatibility;
- destination-state compatibility;
- environmental/tidal burden;
- momentum-map burden;
- route uncertainty.

### Lattice coherence vector

Candidate components:

- node topology/health;
- tile health;
- mass-state integrity;
- structural-domain membership;
- field-bank state;
- thermal/cryogenic margin;
- phase alignment;
- damage state.

### Exit

A decision rule may be proposed only after all axes can be inspected separately.

## 9. W7 — M1 replaceable constitutive layer

Define the Mc-299m hardware interface:

\[
u
=
\mathcal C_{\rm Mc}
(J,T,B,\text{tile state}).
\]

Candidate frequency-domain response:

\[
u_\alpha(\omega)
=
\sum_k
\chi_{\alpha k}(\omega,\ldots)J_k(\omega).
\]

### Architectural requirement

Navigator and M2 must depend on an abstract M1 interface, not one hard-coded microscopic explanation.

This allows alternate fictional formulations later without rewriting the entire flight stack.

### Initial model classes

Potential interchangeable fictional models:

- linear susceptibility kernel;
- nonlinear saturating susceptibility;
- hysteretic/phase-memory model;
- temperature-dependent tensor response;
- damage/lot-dependent response.

Only one becomes operational after deliberate engineering selection.

## 10. W8 — Conservation and failure harness

The fictional model must not hide conservation or failure behind the word “Metric.”

Track at minimum:

- ordinary-state momentum;
- field-bank energy;
- control/electrical input;
- thermal rejection;
- environment/wake ledger;
- transition energy;
- unresolved conservation terms.

### Adversarial scenarios

- impossible metric target;
- node dropout;
- tile failure;
- insufficient bank energy;
- cryogenic derate;
- strong external tidal field;
- boundary mismatch;
- contradictory coherence axes;
- direct mid-field Metric-to-Loom request;
- stale or uncertain environmental input;
- damaged committed domain;
- loss of M1 calibration.

Expected output is often HOLD / DERATE / REORIENT / COLLAPSE / ABORT, not success.

## 11. W9 — Navigator integration

Create typed schemas between the deterministic engine and Navigator.

### Input contract

\[
X=
\{
\text{ship state},
\text{environment},
\text{destination},
\text{hardware state},
\text{mode request}
\}.
\]

### Output contract

\[
Y=
\{
W,
g_{\mu\nu},
R^\rho{}_{\sigma\mu\nu},
T_{AB},
C_L,
C_D,
\mathcal J,
u^*,
\text{margins},
\text{uncertainty}
\}.
\]

### Authority rule

Navigator owns deterministic calculation/planning state.

Browser/HUD may:

- request intent;
- display;
- review;
- compare;
- visualize.

Browser/HUD may not independently calculate or execute authoritative Weave state unless separately governed.

## 12. W10 — HUD v1

Build only after Navigator exposes validated outputs.

### Core panels

- Tick/Tock phase;
- Weave-state summary;
- 208-node map;
- 100-tile state;
- current/target Metric card;
- target vs achieved \(\beta\);
- target vs achieved metric residual;
- lapse/shift summaries;
- curvature/tidal envelope;
- Loom coherence vector;
- lattice coherence vector;
- \(\mathcal J_{AB}\) breakdown;
- route candidates;
- formation state;
- bank energy;
- thermal/cryogenic state;
- uncertainty;
- hold/abort reasons.

### Visualization

Represent \(T_{AB}\) as a relational attachment preview, not as a fake trajectory through normal space.

### Rule

If the deterministic solver did not produce a value, the HUD displays UNKNOWN / UNRESOLVED rather than inventing one.

## 13. W11 — Experience One end-to-end qualification

Run a governed scenario:

1. ordinary flight;
2. Metric request;
3. M2 solution;
4. Tick/Tock ramp;
5. stable Metric cruise;
6. Metric collapse;
7. NRE relax/rephase;
8. Loom formation;
9. multiple candidate \(T_{AB}\);
10. Navigator review;
11. pre-commit translation preview;
12. translation-state result visualization;
13. ordinary-state arrival mismatch handoff.

### Acceptance

Every displayed quantity must trace to:

- deterministic engine output;
- governing engineering/canon value;
- explicitly identified candidate parameter;
- or explicit unresolved state.

No hidden LLM calculation authority.

## 14. W12 — Natural-phenomena / worldbuilding consumer layer

Only after the engineering stack is stable, optionally consume the same model for fictional natural phenomena.

Examples:

- spontaneous phase slip;
- multiple attachment basins;
- local seam condition;
- partial domain isolation;
- natural reattachment.

This layer is a **consumer of the engineering model**, not a calibrator of it.

Real-world anomaly reports remain non-authoritative.

## 15. W13 — Optional foundational interpretation layer

The deeper \(\mathcal R\) / Pauli-Jung-compatible formulation is kept outside control authority.

It may inform:

- lore;
- characters;
- intelligence analysis;
- philosophical disputes;
- “sensitives” as possible noisy detectors.

It may not alter M1/M2 parameters or Navigator decisions without a separate governed fictional-engineering bridge.

## 16. Immediate next action

The immediate implementation target is:

\[
\boxed{
\text{W1 — Weave Kernel v0.1}
}
\]

Before creating code:

1. inspect current \`src/\` architecture and scoped agent rules;
2. identify the correct package location and typed-schema conventions;
3. add unit tests first;
4. implement the smallest deterministic Tick/Tock kernel;
5. run unit regression;
6. only then add the Metric forward readout.

## 17. Exit state of this work plan

If W0–W11 complete successfully, LOOM gains a traceable fictional-engineering chain:

\[
\boxed{
\text{Mc hardware}
\rightarrow
\text{M1}
\rightarrow
\text{M2}
\rightarrow
\text{Weave}
\rightarrow
\text{Metric/Loom}
\rightarrow
\text{Navigator}
\rightarrow
\text{HUD}.
}
\]

At that point Wayfarer no longer “has a magic drive.”

It has a deterministic fictional field-control system with explicit state, constraints, failure modes, power/thermal burden, route admissibility, and inspectable user interfaces.
