# Wayfarer Phase 1b, upstream PR 1: approved packing layout

ALL bodies. ALL sponsors. 2026–2226.

Status: DRAFT engineering integration; zero qualification/performance credit; STOP FOR kT PR REVIEW. Source main before this branch: ea50354e222e77d145a6bbbf49227506d2b560fd.

## kT decisions (verbatim, 2026-11-08)

> - House reserve 0.10 t D-He3.
> - D1 = 3.8 t D-He3, four conformal
>   core lobes, 5% LIQUID ullage.
> - APPROVE PHASE 1b.

The full Phase 1b instructions are in research PR #157: https://github.com/loom-2226/loom-research-lab/pull/157 . Each upstream PR requires separate kT review before merge.

## Source changes in this PR

- Ship-power wet D-He3 is 3.8t, with a protected 0.10t house reserve. Original 0.5t dry tank allowance is four fore-core CSlot cap proxies, each 6mm x-length; four fuel liquid lobes each carry 0.95t. Tank walls, insulation, pressure mechanics, boiloff, fill/drain and internal core webs remain UNQUALIFIED.
- The source G1 ullage is 5% of LIQUID, because CERTIFICATION_BASIS.md G1 states 300t ×1.05 =315m3. The native builder has core net 321.620667m3, rather than exact #156 BRep 321.705750m3. The conservative remass booking is 245.390432t, 0.080960t below the research 245.471391t. Native builder asserts its own liquid+headspace+fuel+caps volume closes. No phantom extra remass.
- kT-approved forward courier x14–17.5m/r4.6–6.1m/az235–305, service arm separate x14–17.5m/r2–4.3m/az225–315. Both retain source equipment mass; no hull/longeron/bulkhead moves. Courier heat, MMOD, attachment loads and neutron/dose transport are OPEN.
- D3 avionics racks outside immutable core trunk; D4 C-lite dry/wet allocated in separate electrical sector; D5 1.931109t overlap deducted from jacket water ledger and placed in existing service reservoir at 26.681109t, 50t total protected water.
- D7 existing 4 fins retain stowed normal-state shapes; source now exposes 28m torch-deployed 5mm model shapes and seven-state deployed inertia screens. Source 17.024t fin panel mass plus 4t mechanisms unchanged; heat rejection credit ZERO.
- D8 per kT: four longerons, frames, bulkhead, thrust path, all G5 primary never cut. Equipment notches around them; frame-web pipe/cable penetration ONLY >=50% web remains with doubled web and untouched flanges. Secondary floor/rack/liner/bracket cuts permit 1.5× removed-material doubler with NO mass credit. Flag >5% removed item volume; any primary movement STOPS for kT.
- D8 0.660802t required secondary doubler added to dry mass ledger as no-render, no-shield-credit provisional point-mass allowance. Actual physical double plates, flange/attachments and G5 load path are OPEN.

## Frozen CAD reference is evidence, not this branch's D9

Files under lab/packing_phase1b are copied from approved research PR #157 (3.8t, forward courier): frozen losslessly compressed STEP (.step.gz, original SHA256 retained), GLB, full 315-solid/49,455-pair/zero category-d report, plus checksum manifest. Source geometry is retained under GitHub; the current analytic builder is NOT thereby certified as 0-conflict. Do not promote D9 by reading these files as a PASS; D9 must independently regenerate and compare this branch's current output. The analytic source native vs exact BRep core-volume 0.085083m3 discrepancy is flagged.

## Current diagnostics / handoff status

Resolved in upstream branch source declaration, NOT qualification: 3.8t fuel and 0.10t house decision; four lobe and fuel cap shapes; G1 liquid ullage allocation; courier location; separated service arm; C-lite; axial racks; D5 jacket 1.931t redistribution; deployed 28m fin panel geometry.

OPEN requiring independent source checks: category(d) D9 on this branch's output; fitted D8 physical doublers + per-item lost volume; unlocated internal tank web/baffle solids; cryogenic containment; seven-state physical CG and RCS after changed inertia; forward courier strake radiation/thermal/MMOD; exact G8 zero margins; regenerated G12 renders.

Original canon reference values remain 250t remass/300t water. This branch's physical state is ~245.39/295.39t. Source G1 will therefore show a mismatch intentionally instead of silently editing the historical canon reference. The required canon alignment is a separate kT/editorial decision.

The full certify.py is attempted on this PR's branch. Current main's RCS trace artifacts are pinned to the prior geometry SHA and G4 stops with "RCS traces must match current geometry". No fake or stale trace is substituted. Replay/requalification is mandatory before full cert can PASS. No performance tuning, no gate bypass.

Future PR 2: source-derived live D9 BRep check, category-(d) == 0, plus necessary narrow primary-preserving notches. Future PR 3: full certify and revised traces/OPEN disposition/consolidated upstream handoff (subject to kT approval at each PR).

STOP at this first draft PR for kT review. No merge, no main changes, credit zero.
