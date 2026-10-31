# LOOM 2226 — Wayfarer RCS / Torch / Metric Geometry Priority v0.1

**Status:** ACTIVE ENGINEERING PRIORITY / NON-CANON  
**Date:** 2026-09-15

## Priority

Wayfarer geometry work is ordered by spacecraft function, not by renderer convenience:

1. **RCS / attitude control** — recover and requalify prior actuator-placement work against current geometry, mass properties and interference constraints.
2. **Torch / remass / thrust chain** — preserve the gross reactor/shield/nozzle geometry while closing feed, thermal, structural and plume interfaces before freezing detailed plumbing/hardware.
3. **Metric** — continue the distributed 208-node design baseline and field-boundary qualification, but reopen placement where RCS or torch exclusion envelopes require it.
4. **Loom** — detailed physical design deferred. Shared Mc/NRE hardware relationships remain canon, but this work makes zero Loom formation or certification claims.

## Current recovered RCS status

The prior PR #96 / HUD flight-control lineage contains a serious 16-hardpoint RCS candidate rather than presentation-only geometry. It is now recovered in `src/wayfarer_recovered_rcs_candidate.py` with provenance and current deterministic-geometry point-clearance checks.

The recovered hardpoint pattern remains **ENGINEERING_CANDIDATE_NON_CANON**. Historical wrench-rank, one-cluster-out, bounded-allocation, gimbal and Q5 energy/thermal results are prior evidence, not current flight authority.

Computational Shipyard Phase 5B remains controlling for rotational dynamics authority: the complete Wayfarer inertia tensor is still `WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`. Old Q4 torque/slew targets therefore remain screening ancestry until requalified against a complete configuration-aware inertia model.

## Current torch/remass status

Earlier Q2 multi-feed work remains candidate evidence. Later Shipyard Phase 9–11 is the controlling conservative physical-feed interpretation: no feed architecture is selected; bulk storage is not silently equated to engine-feed hardware; header/collector/pump/conditioning architectures require admitted propulsion-inlet, fluid-state, transient-duty and component models before geometry is frozen.

## Metric interaction rule

The 208-node count is governing canon. The current 13 × 16 placement is a design baseline only. A metric-node placement that blocks qualified RCS actuation, finite plume clearance, torch feed/service routing, thermal rejection, launch extraction or docking is invalid and must move.

The shared geometry stack must therefore expose RCS, torch and metric layers as distinct systems with explicit provenance and interference relationships.

## Non-claims

No final RCS hardware, full inertia tensor, closed-loop GNC, torch feed architecture, metric boundary, domain membership or detailed Loom design is certified by this priority record.
