# LOOM 2226 — Computational Shipyard Integrated Vehicle Work Plan v0.3

**Date:** 2026-09-09  
**Status:** ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION  
**Authority:** ARCHITECTURE / WORK-PLAN ONLY

## Goalposts

The Computational Shipyard is accepted only when one governed ship Design State can drive both:

1. a physics-consumable vehicle used by Navigator/HUD with admitted astrodynamics, propulsion, mass-state and configuration rules; and
2. a derived visualization chain consisting of semantic GLB, interactive inspection, deterministic reference views and non-authoritative AI visual realization.

The two outputs must not diverge into separately maintained ships.

```text
                     GOVERNED DESIGN STATE
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
        VEHICLE DYNAMICS CONTRACT   SEMANTIC SPATIAL CONTRACT
                 |                       |
          Navigator / HUD          deterministic GLB
          mission evaluation       interactive viewer
                                    reference renders
                                    yard grammar
                                    AI realization
```

## Non-negotiable authority split

- Design State and admitted engineering evidence own the ship.
- Navigator may consume only vehicle-dynamics fields with explicit admitted authority and validity.
- Semantic geometry and GLB are derived engineering-traceable artifacts.
- AI imagery is non-authoritative and may not back-propagate engineering facts.
- Current coarse Shipyard geometry does not gain flight-inertia authority merely by being rendered.

## Phase A — Visualization closure

### A1 — Semantic GLB v0.1

Export governed semantic geometry to deterministic glTF 2.0 binary with stable object identity, semantic metadata, provenance, hashes and an explicit authority manifest. No presentation-only geometry.

### A2 — GLB-native Pixel viewer

Load semantic GLB directly in the offline localhost Pixel viewer. Retain orbit/zoom, component selection, semantic labels, filtering, envelopes, structural hypotheses, center-of-mass/thrust-axis overlays when admitted, keep-outs and OPEN-state display. No cinematic graphics requirement.

### A3 — Shipyard realization grammar v0.1

Formalize ASTERIA, KELDRIN, SHIKARI and TASCHEN as structured manufacturing/institutional grammars rather than aesthetic adjectives. Yard capability constrains manufacturable design space; yard doctrine influences choice among viable designs; AI may elaborate only unconstrained visual detail.

### A4 — Wayfarer visual acceptance and freeze

Run one governed Wayfarer Design State through semantic geometry, GLB, Pixel inspection, deterministic reference views and four yard realization packets. Freeze visualization v1 after acceptance unless a demonstrated engineering/interaction deficiency requires reopening it.

An older user-supplied Wayfarer GLB may be used as a visualization-only compatibility fixture. It is not engineering authority for the current governed Design State.

## Phase B — Vehicle Dynamics Contract

Define a typed, validated interface from Shipyard to Navigator/HUD. Candidate fields include identity/design-state hash, dry/current mass, mass-state decomposition, center of mass, qualified inertia only where admitted, propulsion modes, remass state, thrust/acceleration envelope, exhaust/performance parameters, duty/thermal constraints, configuration/deployment/docking state, Metric/Loom eligibility and explicit validity/authority/uncertainty metadata.

Navigator must not reach into arbitrary Shipyard tables or infer missing physics from geometry.

## Phase C — Wayfarer Navigator integration

### C1 — Torch

Use real astrodynamics for coast, gravity, finite burns, acceleration limits, braking/capture and mass depletion. Validate against simple comparators before complex transfers.

### C2 — Metric

Represent Metric as its admitted transport regime rather than fake high-speed rocket propagation. Conventional orbital state matters before activation and after collapse/arrival; transit follows the governed Metric model.

### C3 — Loom

Represent Loom as its admitted relational/route transition mechanism, not thrust and not ordinary FTL integration. Consume boundary/configuration/route eligibility explicitly.

### C4 — HUD

HUD consumes the same vehicle state for propulsion regime, kinematics, trajectory, arrival/intercept, remass, thermal/configuration limits, maneuver availability and Metric/Loom eligibility.

## Phase D — Generative Shipyard Foundation v0.2

### D1 — Architecture Domain

Separate FIXED_CANON, BOUNDED_DESIGN_CHOICE, DERIVED and OPEN_NOT_ADMITTED. Only admitted design freedoms may enter search.

### D2 — Executable discipline graph

Propagate architecture changes through mass, structure, packaging, thermal, power, propulsion, shielding, maintenance and manufacturing. No hidden conversion shortcuts.

### D3 — Model adequacy

Every model carries validity domain, fidelity, known omissions, evidence/calibration basis, uncertainty and adequacy for screening/rejection/final comparison.

> No candidate may be eliminated by a model that is not adequate for the reason it is being eliminated.

### D4 — Uncertainty state

Use typed uncertainty such as FIXED_KNOWN, DESIGN_VARIABLE, ALEATORY, EPISTEMIC, MODEL_FORM, MANUFACTURING_TOLERANCE, OPERATIONAL_VARIABILITY and OPEN_NOT_ADMITTED.

## Phase E — Iterative candidate engine

For each candidate:

```text
generate / mutate
      -> compile Design State
      -> coupled discipline evaluation
      -> adequacy / uncertainty checks
      -> spatial validation
      -> manufacturing validation
      -> Vehicle Dynamics Contract
      -> Navigator mission evaluation
      -> objectives
      -> reject / retain / mutate
```

Mission performance is inside the design loop rather than a post-hoc check.

## Phase F — Pareto archive and lineage

Retain non-dominated candidates and full rejection/mutation ancestry. Do not collapse prematurely to one "best" ship. Candidate objectives may include mission time, remass use, dry mass, payload, thermal margin, manufacturing cost/time, maintenance burden, reliability, damage tolerance, crew protection and relational-system burdens where admitted.

## Phase G — Materials, fabrication, environment and robotics

The permitted design space must depend on:

`MATERIAL SYSTEM x FABRICATION PROCESS x CONSTRUCTION ENVIRONMENT x ROBOTIC ASSEMBLY/MAINTENANCE CAPABILITY`

Earth, lunar, Martian, orbital-microgravity and asteroid construction are allowed to produce genuinely different feasible geometries rather than cost multipliers on one geometry.

## Phase H — Automatic dual realization

Every retained candidate automatically emits:

- Vehicle Dynamics Contract -> Navigator/HUD; and
- Semantic Spatial Contract -> GLB -> Pixel inspection -> reference board -> yard visual realization.

Different engineering candidates must alter both their mission behavior and their spatial realization. Different yards may then realize the same candidate differently within engineering freedoms.

## Acceptance milestones

### M1 — One ship closes

One governed Wayfarer is physics-consumable by Navigator/HUD and visually consumable by semantic GLB/Pixel/reference/AI pipelines.

### M2 — Ships vary

Multiple genuinely different Wayfarer architectures propagate correctly through engineering, Navigator behavior and semantic geometry.

### M3 — Ships evolve

The Shipyard iteratively searches architecture space, rejects candidates for traceable adequate reasons, retains a robust Pareto frontier and produces flyable plus visualizable descendants.

## Explicit non-goal

Increasing presentation detail is not a program milestone unless it solves an engineering, interaction, Navigator/HUD or downstream-conditioning need.
