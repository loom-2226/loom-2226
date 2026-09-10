# LOOM HUD / NAVIGATION PHYSICS WORKPLAN

Date: 2026-09-11
Status: ACTIVE WORK PLAN
Repository authority: live GitHub
Primary HUD integration branch: `feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11`
Parent engineering source: PR #96 / `engineering/wayfarer-flight-system-qualification-v1`

## Purpose

Advance LOOM from the current Earth-Moon qualification HUD toward a high-fidelity mission-analysis and navigation stack without turning the HUD into a second physics authority or duplicating Navigator.

Architecture remains:

`authoritative/qualified providers -> typed state contracts -> Navigator / engineering consumers -> HUD presentation`

The HUD is a consumer and acceptance surface. Navigator owns trajectory/astrodynamics. Wayfarer engineering owns vehicle constraints. Research artifacts do not become canon or flight authority without governed promotion.

## Phase A — Close current Wayfarer/HUD integration

Goals:

1. Finish PR #99 consumption of the pinned PR #96 engineering state.
2. Replace presentation-only ad hoc engineering fields with typed HUD engineering datums carrying value, unit, source, authority, availability, status/quality and provenance.
3. Preserve Q4 finite-attitude timing as qualified-for-HUD engineering state.
4. Preserve Q5 as `OPEN_BOUNDED` where applicable; do not invent radiator geometry or buffer medium closure.
5. Preserve Q7 as candidate/screening doctrine pending populated Q6 Navigator mission regression.
6. Keep `NORMAL_DISPATCH_REMASS`, `OPERATIONAL_REMASS_FLOOR`, `PROTECTED_OPTIMIZER_RESERVE`, and `PROTECTED_WATER_RESERVE` separate.
7. Do not allow routine optimization to consume protected water.
8. Preserve Q2 feedstock screening as candidate/open; H2O may be presented as primary candidate, not certified.
9. Pixel regression after substantive HUD integration changes.

Exit criteria:
- typed engineering state available through existing HUD data boundary;
- no duplicated mass/Torch/Q4 constants in UI code;
- OPEN/CANDIDATE states remain visible;
- unit tests + relevant functional tests + full regression green;
- Pixel acceptance confirms no mobile layout regression.

## Phase B — Navigation Physics v3

Goals:

1. Introduce adaptive higher-order numerical integration behind a Navigator-owned propagation interface.
2. Keep the existing shared gravity primitive as one force contribution; do not move force ownership into HUD.
3. Add a clean force-model interface supporting a documented supplied-body set and later higher-fidelity effects.
4. Centralize frame and epoch transforms; prevent HUD/GIS from independently reproducing astrodynamics.
5. Add SPICE-quality ephemeris/body-orientation adapters where available and preserve provenance/uncertainty.
6. Add a general targeting interface so Earth-Moon shooting logic is no longer the mission-design architecture.
7. Preserve finite burns, remass accounting and finite attitude timing through propagation.
8. Keep TORCH / METRIC / LOOM mobility regimes separate; no free momentum reset or reactionless Torch behavior.

Initial force-model progression:
- Newtonian N-body point mass;
- body nonspherical gravity where justified by mission regime;
- third-body perturbations through the same provider interface;
- solar radiation pressure;
- atmospheric drag for applicable bodies/altitudes;
- relativistic corrections when material;
- other force terms only through explicit governed qualification.

Exit criteria:
- adaptive propagation contract implemented and independently tested;
- same initial state produces deterministic bounded results within configured tolerances;
- frame/epoch provenance preserved end to end;
- HUD receives state rather than recomputing it.

## Phase C — GMAT cross-validation

Purpose: use NASA GMAT as an external benchmark, not as LOOM authority.

Build a reproducible comparison suite covering:

1. two-body orbit propagation;
2. Earth-Moon transfer;
3. lunar flyby;
4. lunar rendezvous terminal state;
5. finite burn;
6. multi-body/third-body perturbation case;
7. coordinate/frame transformation cases;
8. event timing / closest approach;
9. selected degraded Wayfarer cases once vehicle constraints are qualified.

Compare:
- position residual vs time;
- velocity residual vs time;
- event epochs;
- burn duration and delivered delta-v;
- terminal state;
- closest approach;
- propellant/remass accounting where models are equivalent.

No claim of GMAT parity is earned until comparison tolerances and model equivalence are explicitly documented.

## Phase D — Vehicle-constrained mission planning

Goals:

1. Couple qualified Wayfarer thermal/power constraints into Navigator mission feasibility.
2. Enforce qualified dispatch/reserve policy only after Q6/Q7 closure.
3. Add degraded RCS/control cases and finite attitude timing to all relevant maneuver plans.
4. Consume real Q6 Navigator route results for Earth-Ceres, Mars-Ceres, Mars-Jupiter, Ceres-Neptune and required degraded cases.
5. Derive reserve doctrine from mission distribution instead of preserving screening values by inertia.
6. Surface vehicle constraint margins through typed HUD state.

HUD candidates once authority exists:
- active attitude phase / slew time remaining;
- control case (`NOMINAL`, `ONE_CLUSTER_OUT`, etc.);
- thermal margin / transient state;
- radiator configuration/status;
- dispatch reserve and operational remass floor;
- protected water state;
- Torch authorization/degraded mode;
- maneuver residual and execution state.

## Phase E — Navigation-grade state estimation

Longer-term goals:

1. covariance propagation;
2. measurement models;
3. orbit determination / filtering;
4. maneuver reconstruction;
5. uncertainty-aware targeting;
6. tracking-data provenance and quality;
7. HUD uncertainty ellipses/volumes, encounter dispersion and navigation-quality indicators.

This phase must distinguish objective simulation truth from estimated/known state.

## Phase F — Qualification, integration and freeze

Before promotion/freeze:

1. unit regression on every Python release increment;
2. relevant functional tests for substantive changes;
3. full end-to-end regression;
4. Pixel physical acceptance;
5. Windows semantic/usability acceptance where applicable;
6. GMAT comparison suite green to documented tolerances for equivalent models;
7. affected Navigator/Wayfarer interface revalidation;
8. WALTER governance review.

## Sequencing rule

Do not wait for full GMAT-class Navigator maturity before improving the HUD. As new authority is earned, wire it through typed state and let the existing HUD expose it. Conversely, do not implement new physical truth in browser/UI code just because the display would benefit from it.

## Current starting point

At creation of this work plan:
- PR #99 is the active HUD/Wayfarer integration branch;
- PR #96 is the pinned non-canon engineering qualification source;
- Q4 finite-attitude timing is already consumed by the rendezvous qualification path;
- the HUD exposes PR #96 engineering state read-only;
- JPL/Hermite lunar state, Earth+Moon point-mass gravity, finite Torch burns/remass and terminal-state correction are qualification-only tools;
- the current HUD realtime propagator still uses semi-implicit Euler with bounded 10 s steps and is not a GMAT-class propagator;
- Q5/Q7/Q2 remain explicitly open/candidate where their source artifacts say so;
- Q6 awaits a full real Navigator route set before reserve doctrine can close.

## WALTER hard stops

Block or flag any change that:
- makes HUD a physics/navigation authority;
- duplicates Navigator trajectory/frame logic;
- promotes engineering candidate values to canon;
- silently consumes protected water;
- conflates Torch jet power with electrical bus power;
- erases ordinary velocity mismatch through Metric;
- invents missing RCS, thermal, structural, feedstock or docking authority;
- treats CI success alone as physical qualification.
