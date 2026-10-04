# Phase 3B Build 4 MVP R4 Resolution-Invariance Baseline Record

**Status:** FROZEN RESOLUTION-INVARIANCE BASELINE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Baseline branch:** `offworld-mvp-build4-mvp-r4-resolution-invariance-2026-10-04`
**Baseline commit:** `bba276b3eff69a0101fed1235f5958cd4186e6d0`
**Predecessor:** `offworld-mvp-build4-mvp-r3-policy-firewall-2026-10-04` @ `5f3285b28e4ce05979afc52f29930f9966e79983`

R4 preserves R3 and closes autonomous-policy pre-gate review item 3:

- AGGREGATE -> AGENT exposure uses an explicit `ResolutionExposurePlan`;
- selected identity, selection basis and selection reference are recorded;
- allocation basis and allocation reference are recorded;
- equal-member allocation derives share from represented membership;
- one of four equal represented members therefore receives exactly 25%, without a separate authored share;
- the aggregate-only and exposed-Agent fixtures follow the same per-member rule over five periods;
- declared represented system totals are pathwise identical after every period;
- exposure records are included in methodology lineage/fingerprint state.

Validation authority:

`PHASE3B_KERNEL_VALIDATION_RECORD_008_RESOLUTION_INVARIANCE.md`.

At freeze, **66 tests passed** from a fresh Git archive on `quantifactus`.

This baseline does not authorize autonomous policies and remains NOT_EMPIRICALLY_VALIDATED.
