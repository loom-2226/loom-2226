# LOOM 2226 — Wayfarer RCS / Torch / Metric Geometry Priority v0.1

**Status:** ACTIVE ENGINEERING PRIORITY / NON-CANON DESIGN RECORD  
**Date:** 2026-09-15  
**Authority:** governing canon remains `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`

## Purpose

Preserve the current physical-engineering priority for the Wayfarer and prevent subsystem terminology from drifting across HUD, Computational Shipyard, E1 qualification and later detailed design.

Current physical priority is:

1. **RCS / attitude-control geometry**
2. **Torch / reactor / magnetic-nozzle geometry**
3. **Metric distributed-node geometry and certified metric-domain boundary**
4. **Loom detailed physical design deferred**

This ordering is a project-engineering priority. It does not alter governing physics or canon.

## Regime separation

Canon explicitly preserves three physically distinct propulsion regimes:

- `TORCH` — ordinary momentum exchange;
- `METRIC` — continuous subluminal relational/metric transport;
- `LOOM` — discontinuous interstellar relational re-embedding.

No geometry artifact may silently make one subsystem perform another subsystem's work.

## RCS

RCS remains a separate conventional attitude/translation-control subsystem.

Required future geometry work includes:

- station count and placement;
- thrust-vector authority and torque closure;
- plume and keep-out volumes;
- launch-bay extraction interference;
- radiator deployed/stowed interference;
- docking dead zones;
- torch/nozzle exclusion geometry;
- ordinary-space control authority.

The current 208-node metric array does **not** define RCS geometry.

## Torch

Torch geometry remains the ordinary-momentum propulsion chain centered on the current aft reactor / thrust-frame / magnetic-nozzle envelopes.

Required future work includes:

- reactor/torch detailed physical envelope;
- shadow-shield layering and line-of-sight geometry;
- thrust-frame and longeron load closure;
- magnetic-nozzle coil/support geometry;
- plume envelope;
- service/feed/thermal routing;
- mutual exclusions with RCS and deployable systems.

The current 208-node metric array does **not** define torch geometry.

## Metric

Metric work may proceed now because E1 requires a vessel-configuration-bound certified translation-domain boundary.

Governing node count:

- `208 distributed boundary/metric nodes` — CANON.

Current exact placement baseline:

- `src/wayfarer_metric_node_array.py`
- 13 axial rings × 16 azimuthal nodes = 208;
- cell-centered axial spacing across the 57 m reference length;
- 22.5° circumferential sectors;
- ring support radii follow the current deterministic structural envelope by axial zone.

Placement status is **DESIGN_BASELINE**, not recovered canon.

This baseline is intended to become a shared Wayfarer geometry consumer across:

- Computational Shipyard;
- HUD / inspection rendering;
- semantic GLB derivatives;
- E1 metric-boundary work.

Any change to placement must follow the main-repository provenance/backpropagation record and identify stale derived assets and qualification evidence.

## Loom boundary

Canon states that Metric and Loom ultimately share Mc/NRE order-parameter hardware and distributed hardware. That hardware commonality does **not** mean detailed Loom geometry, formation, collapse/rephase/formation sequence, or Loom certification is being designed here.

Current project rule:

> Preserve future shared-hardware compatibility, but make **zero Loom design or certification claims** until Loom is explicitly taken up as its own engineering workstream.

## E1 implication

The metric node-placement baseline is necessary input to a distributed-node metric field solution, but it is not sufficient evidence for:

- certified metric-domain boundary geometry;
- numeric certified domain extent;
- domain membership containment;
- local-geometry compatibility;
- causal compatibility;
- lattice/coherence certification;
- overall GA certification.

The next E1 step remains:

`committed vessel geometry + metric node placement + governing metric environment architecture -> certified metric field boundary -> containment result`

## Non-claims

This record does not promote the 13 × 16 arrangement to canon. It does not change the 208-node canon count. It does not define RCS or torch station geometry. It does not certify Loom formation or metric transport. It does not mutate campaign state.
