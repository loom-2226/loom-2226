# LOOM 2226 — E1 Astra Independent Architecture Review — 2026-10-02

**Class:** ENGINEERING REVIEW  
**Scope:** Experience One (E1)  
**Status:** REVIEW / NON-CANON / NON-RUNTIME-POLICY  
**Authority:** GitHub remains authoritative. This artifact records an independent architectural review; it does not itself authorize implementation, flight, canon mutation, or qualification.

## Review basis

Astra Codex was instructed to perform an autonomous architectural review of LOOM 2226 Experience One using live GitHub authority, with particular attention to PR #356 in the context of the complete E1 system. It was instructed not to implement or merge changes.

Reviewed baseline reported by Astra:
- GitHub main: `1415c86dceea3545fa024947b56fee7040c3e847`
- PR #356 head: `6b05b6d9ef06e027184f0790ebb286bf9d31e21f`
- operational E1 branch / PR #112 head: `6c1fd55`

## Executive finding

> E1 has a sound authority model and a working operational flight seam, but it is not yet one qualified, continuous flight system.

The architecture should be repaired by connecting existing qualification and execution machinery and eliminating divergent calculations, not by building another runtime, campaign kernel, navigation authority, or flight executor.

## Current architecture observed

- Governing authority: registered canon and scoped amendments; engineering supplies subordinate models and qualifications.
- Campaign authority: `loom_navigator_core.py` owns campaign state, revisions/hashes, flight commits, history, arrival, recovery, and replay.
- Flight calculation: Navigator loads a compressed, hash-checked embedded solver. NAV-V1-A calculates Metric displacement and terminal Torch burn while preserving ordinary inertial velocity through Metric transport. Ship gravity and several environmental effects remain explicitly parked.
- Operational interaction: PR #112 adds Mara intent -> Navigator review/finalization -> human authorization -> Navigator execution. Persistent Pixel evidence supports arrival, restart, and replay, but the interaction files remain on that open PR rather than current main.
- Newer physical qualification: Torch, mass/inertia, RCS, environment, configuration, membership, and Compound GA modules mostly produce engineering evidence rather than govern committed flights.

The repository therefore contains one established campaign writer alongside several incompletely connected calculation and qualification paths.

## Findings

### A. Qualification does not yet close the execution loop — HIGH

The flight commit path does not consume the newer configuration, boundary, membership, Compound GA, or rotational qualifications. Persisted configuration is materially thinner than the authored E1 qualification configuration.

A successful operational flight and an indeterminate physical qualification can therefore coexist legitimately, but neither proves the other.

**Smallest correction:** extend the existing campaign snapshot and finalized-plan contract to bind the actual configuration and required qualification evidence. Revalidate that binding at Navigator's existing commit gate. Keep derived boundary, inertia, and certification results reproducible from that snapshot; do not create another mutable ship state.

### B. Calculation authority has already diverged — HIGH

Astra identified at least two concrete divergences:

| Calculation | Navigator | Newer E1 machinery |
| --- | ---: | ---: |
| CRUISE Torch thrust | 11.970 MN | 11.361004025 MN |
| Between-row SOURCE-010 sampling | linear interpolation | cubic Hermite interpolation |

The same embedded solver hash is used by current main and PR #112, but shared source rows or canon references do not establish calculation parity. These differences can alter burn duration, arrival, and certification geometry.

**Smallest correction:** select and version the governing implementation for each calculation, then require execution and qualification to consume it. Preserve prior behavior explicitly as a regression fixture where necessary; do not silently replace constants or interpolation inside an already-qualified model.

### C. Some fail-closed qualification interfaces are not safe authorization interfaces — HIGH

Astra reproduced behavior equivalent to:
- `evaluate_ga({}) -> ADMISSIBLE`
- a partial GA axis set can also produce `ADMISSIBLE`.

The evaluator checks supplied axes rather than completeness of the required axis set. Route-coherence classification also relies substantially on matching field names, while the aggregate GA report contains a manually assembled axis inventory rather than composing all current evaluators.

**Smallest correction:** require complete, versioned axis sets and validated evidence values at the authorization seam. Bind every result to the same plan/configuration/input snapshot. Keep evidence discovery distinct from certification acceptance.

### D. PR #356 places B_D at the correct conceptual layer, with qualifications

A calibrated engineering translation-domain boundary provider is the appropriate abstraction. It should produce observable geometry, uncertainty, and provenance without requiring Tick/Tock, a cell complex, or fundamental Weave physics.

Additional architectural constraints:
- Navigator supplies candidate mode, state, and environment and consumes the result during planning/revalidation. The dependency is not merely a one-way pipeline preceding Navigator.
- Boundary solution, component containment, and overall flight permission remain distinct results. `SOLVED_CERTIFIABLE` must not imply permission to fly.
- Calibration applicability needs explicit regime/mode, validity, authority, and revocation semantics.
- Loom boundary anchors cannot automatically calibrate Metric merely because hardware is shared.
- The PR #356 executable artifact is a fixed evidence assessment, not yet a calibration validator or numerical solver. Its `status: PASS` must remain visibly distinct from physical certifiability.

### E. Operational adapter is brittle under concurrent requests — HIGH before wider use

PR #112 drives execution by replacing process-global `input`/`print`, matching CLI prompts, and extracting the printed plan hash. Its server uses `ThreadingHTTPServer`. Concurrent review/finalization/execution requests can therefore interfere with those global replacements.

**Smallest correction:** first serialize these operations. Then expose a small structured API around existing Navigator functions, retaining the CLI as a caller. Keep base-state validation and mutation within one serialized commit operation. Preserve the existing executor rather than replacing it.

### F. Earned arrival remains a provisional navigation boundary

NAV-V1-A solves a gravity-free terminal state match to the selected destination's ephemeris state. That is insufficient evidence for a continuous, physically admissible Neptune-local arrival with attitude, configuration, environmental, and propulsion constraints.

**Smallest correction:** preserve existing arrival behavior as a regression fixture. Qualify the explicit transition into ordinary local flight using the same state and clock. Do not describe the historical operational PASS as completion of the newer end-to-end flight objective.

## Recommended architectural direction

Keep:
- one campaign writer;
- one clock;
- one Navigator planning/commit path;
- shared deterministic physical models;
- read-only qualification results.

Torch, Metric, and Loom should have explicit regime-specific transition contracts over that shared state. A future Weave backend may supply qualified models through the same contracts, but it must not acquire independent navigation, state, calculation, or execution authority.

## Ordered next steps

1. **Pin integration authority.** Create one E1 integration manifest identifying the reviewed operational baseline, engineering baseline, solver/model versions, open PR dependencies, and authority boundaries.
2. **Close calculation divergence.** Resolve and test Torch thrust and SOURCE-010 interpolation authority; audit for additional duplicate calculations.
3. **Bind qualification to execution.** Make configuration and qualification evidence complete, versioned, snapshot-bound, replayable, and genuinely fail-closed at the existing finalized-plan/commit seam.
4. **Continue B_D deliberately.** Specify the fail-closed calibration-package schema and validator, including regime/mode, applicability, validity, authority, revocation, uncertainty, and provenance. Keep geometry unresolved until supporting authority exists.
5. **Qualify one complete Ceres -> Neptune path.** Test execution, restart, and replay, plus negative cases for stale configuration, missing certification, and duplicate/concurrent execution.
6. **Then qualify ordinary local arrival.** Preserve the current arrival as regression behavior while adding the physically continuous Neptune-local transition.

## Explicitly do not

- Build a second campaign kernel or flight executor.
- Infer boundary shape from area, hull dimensions, Hill/SOI, or current collapse radius.
- Treat Metric displacement as an ordinary-space collision trajectory.
- Make foundational Weave research an E1 prerequisite.
- Promote fixtures, field presence, a qualification-script `PASS`, or a solved boundary into flight permission.
- Rewrite working machinery for elegance.

## Administrative observation

At the time of the Astra review, PR #356's LOOM Gate reported LG001 due to missing change-class metadata. That is governance/metadata debt and does not establish or refute physical qualification.

## Review disposition

**Architecture direction: preserve. Integration debt: material.**

The immediate program is integration and authority convergence, not architectural replacement.
