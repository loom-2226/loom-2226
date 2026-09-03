# LOOM 2226 — GIS / Navigator Convergence Status and Next Steps

**Date:** 2026-09-03  
**Branch:** `feature/gis-navigator-convergence`  
**Governing plan:** `docs/architecture/LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`  
**Status baseline before this document:** `dc35b34f92727a70df832dc1ec6cd1b1e69f2aca`  
**Purpose:** authoritative handoff/status checkpoint after Phase 6 automated convergence and first Android physical-device qualification.

---

## 1. Executive status

The GIS/Navigator convergence architecture is working at the domain/service level and in automated qualification. The Solar GIS is now the sole intended operational surface; Navigator planning/execution logic is behind typed/adapted service seams rather than duplicated inside GIS.

Phases 0–6 have been substantially implemented. Gates A and the automated form of Gate C are closed. Gate B remains open because authoritative continuous sampled trajectory geometry is still not exposed for full old-renderer parity.

The first physical Android qualification uncovered two deployment/UI issues that CI could not expose:

1. **Pydroid is not a reliable host for the long-running local GIS HTTP server.** The process disappeared without Python traceback or orderly shutdown. The same runtime stays alive under Termux.
2. **The Phase-6 planning UI is functionally connected but not yet physically acceptable.** Under Termux, Mars→Ceres route discovery succeeds and candidate state survives reload, but candidate cards currently display `TIME 0.0 min`, `HOLONOMY 0.000`, and `CONFIDENCE 0.000`, indicating a presentation/field-mapping defect. Execution was deliberately withheld until those values are verified.

Therefore:

- **Automated Gate C:** PASS.
- **Android physical Gate C acceptance:** OPEN / near-complete.
- **Production promotion to `main`:** NOT YET.
- **Phase 7 SQL migration work:** should wait until the Android physical Gate-C acceptance and immediate UI defects are closed.

---

## 2. Status against governing work plan

### Phase 0 — Freeze known-good pre-convergence state

**Status: COMPLETE.**

The pre-convergence Navigator/GIS runtime, campaign artifacts, qualification outputs, and hashes were frozen before extraction work. The frozen Navigator physics oracle remains:

`c834998cc9b8016dcbf5f0e200db781cb1d2f5dc9245c091a8f205dea280107b`

That oracle continues to be reproved during later qualification rather than being replaced by GIS-originated request hashes.

### Phase 1 — Repository hygiene and versioning model

**Status: COMPLETE FOR CONVERGENCE WORKSTREAM; broader cleanup remains evolutionary.**

The convergence work is carried on `feature/gis-navigator-convergence`; source and contracts are Git-versioned, runtime state remains external/mutable, and feature work is being isolated from `main` pending qualification.

### Phase 2 — Extract Navigator domain logic

**Status: COMPLETE. Gate A CLOSED.**

Navigator services were extracted behind canonical/adapted interfaces including navigation request/context, ephemeris acquisition, route discovery/compile/execution, and GIS-facing route-layer assembly. Existing frozen results are reproduced independently of the old visual Navigator.

The implementation specifically avoids giving GIS flight-physics authority and avoids hard-coding legacy payload shapes across consumers.

### Phase 3 — Establish GIS navigation-layer contract

**Status: COMPLETE.**

`LOOM_ROUTE_LAYER_V1` is the GIS-facing navigation contract. GIS consumes route/phase/vehicle/arrival semantics and owns display styling. Navigator remains authoritative for route truth.

### Phase 4 — Render Navigator routes in GIS

**Status: IMPLEMENTED FOR CURRENT AUTHORITATIVE OUTPUTS; Gate B OPEN.**

GIS can render the authoritative navigation states currently exposed by the extracted Navigator services, including active routes, alternates, phases, maneuvers, ship position, and historical route overlays.

**Remaining Gate-B blocker:** RC6.1 does not yet expose authoritative sampled continuous trajectory geometry sufficient to reproduce every meaningful old Navigator visual state. No fake straight/curved line should be fabricated merely for visual completeness.

### Phase 5 — Move flight planning interaction into GIS

**Status: FUNCTIONALLY COMPLETE; MOBILE UX POLISH REQUIRED.**

GIS can select a destination, call Navigator route discovery, display candidates, preview a candidate, commit a planning choice, cancel it, and preserve campaign state until execution.

Physical Android testing exposed UI debt that must be fixed before production promotion:

- flight-planning panel cannot yet be cleanly minimized/closed/repositioned;
- Atlas/attribute drawer and planning panel compete for limited phone screen area;
- destination selection flow is still awkward on touch;
- preferred improvement is an explicit `PLAN FLIGHT HERE` action from the selected Atlas body, plus deterministic panel controls (`MINIMIZE`, `CLOSE`, optionally `FLOAT/DOCK`);
- a long-press/context action may be considered later, but should not be the only mobile path because Android canvas/browser gesture behavior is less deterministic;
- candidate list/navigation needs compact mobile behavior and clear current/committed state.

### Phase 6 — Integrate campaign execution

**Status: AUTOMATED COMPLETE; ANDROID PHYSICAL ACCEPTANCE OPEN.**

Automated Gate-C qualification has already proven the full authoritative chain:

`GIS → discover → preview → commit → execute → Navigator arrival → one campaign commit → GIS refresh`

Automated qualification also proved stale-plan rejection and one-and-only-one campaign transition.

Physical Pixel qualification status as of this checkpoint:

- Pydroid local server lifetime: **FAIL / unsuitable host for current long-running runtime**.
- Termux local server lifetime: **PASS**.
- Termux Python dependency `requests/urllib3`: initially missing, installed successfully.
- Mars→Ceres route discovery under Termux: **PASS**.
- Candidate state survives browser reload: **PASS**.
- Planning commit state visible: **PASS** (`HARD/CRUISE` shown committed in the physical run).
- Candidate card summary fields: **FAIL / suspect mapping** (`TIME 0.0 min`, `HOLONOMY 0.000`, `CONFIDENCE 0.000`; remass `11.886 t` appears plausible).
- Physical execute/arrival: **NOT YET ATTEMPTED** by design until summary values are verified.

**Android physical Gate-C acceptance closes only after:**

1. candidate summary field mapping is corrected and validated against the authoritative Navigator candidate object;
2. a physically discovered Mars→Ceres route is previewed/committed with credible displayed values;
3. `EXECUTE COMMITTED FLIGHT` is run from the Pixel;
4. canonical campaign state changes exactly once;
5. origin/location, epoch, remass, and history are verified after arrival;
6. stale/second execution is rejected;
7. GIS refreshes cleanly to the new authoritative state.

### Phase 7 — SQL migration discipline

**Status: NOT STARTED.**

Do not begin until the immediate Phase-6 Android acceptance defects are closed. Phase 7 remains the next architectural phase once the current convergence runtime is physically proven.

### Phase 8 — Automated qualification

**Status: PARTIALLY IMPLEMENTED / ACTIVE THROUGHOUT.**

Unit, functional, frozen-oracle, live HTTP, and provider regressions have been run throughout Phases 2–6. The eventual Phase-8 task remains to normalize these into the formal repository qualification structure and golden fixture suite described by the governing plan.

### Phase 9 — Retire old Navigator renderer

**Status: NOT STARTED / BLOCKED.**

Do not retire the visual Navigator yet. Gate B remains open, and Android physical Gate-C acceptance is still pending.

### Phase 10 — One production launcher

**Status: NOT STARTED; Android runtime decision emerging.**

Physical testing indicates Termux is the better Android runtime host for LOOM's long-running local Python HTTP service. Pydroid remains useful for ad hoc scripts but should not currently be treated as the production host for the converged GIS server.

The eventual Android production launcher should target Termux-compatible Python, install/check required dependencies, preserve mutable campaign/database artifacts, and launch the same converged GIS entrypoint used on desktop.

---

## 3. Current Android runtime findings

### Pydroid

Observed behavior: GIS starts and serves initial payloads, then the Python process disappears without a Python traceback or orderly HTTP shutdown. Chrome subsequently reports `ERR_CONNECTION_REFUSED` on `127.0.0.1:8766`.

Per-run process and HTTP logging confirmed that the process can vanish independently of a Navigator discovery request. This makes Pydroid unsuitable as the authoritative long-running host until proven otherwise.

### Termux

Observed behavior: the same converged entrypoint remains alive and serves the GIS normally. Running directly from the shared runtime:

```bash
cd /storage/emulated/0/Download/LOOM_TEST
python src/loom_gis.py --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST
```

Initial discovery exposed a missing `requests/urllib3` dependency. After installing those packages, Navigator successfully discovered Mars→Ceres candidates and the planning state survived reload.

**Provisional Android decision:** continue physical qualification under Termux.

---

## 4. Immediate next work — do this before Phase 7

### A. Fix candidate summary mapping

Inspect the authoritative `RouteCandidate` / planning-session candidate payload returned for the successful Termux Mars→Ceres run. Correct the GIS card adapter so it displays the canonical values rather than zeros or missing legacy aliases.

Verify at minimum:

- duration / arrival time;
- remass;
- holonomy or applicable metric-quality value;
- confidence / selection quality if truly authoritative and meaningful;
- strategy/mode labels.

Do not manufacture values that Navigator does not expose. If confidence or holonomy is not present/applicable, show `—` rather than `0.000`.

### B. Complete physical Gate C

After summary values are correct:

1. Termux launch.
2. Pixel Chrome opens `127.0.0.1:8766`.
3. Select Ceres from Mars.
4. Discover routes.
5. Preview authoritative route.
6. Commit route.
7. Execute.
8. Verify canonical state/history exactly once.
9. Verify GIS reflects arrival.
10. Attempt duplicate execute and confirm rejection.

### C. Fix mobile planning-window ergonomics

Before production promotion, make the flight-planning UI operable as a real HUD panel:

- `MINIMIZE` / restore;
- `CLOSE` or hide without cancelling committed state;
- optional `FLOAT/DOCK` mode for larger screens;
- compact candidate list with internal scrolling;
- avoid covering Atlas/map controls unnecessarily;
- clear distinction between closing the visual panel, cancelling a planning session, and cancelling a committed plan.

For destination selection, add a first-class `PLAN FLIGHT HERE` action tied to the authoritative selected Atlas body. A secondary body picker/drop-down may also be useful for touch devices, especially when the map is crowded.

### D. Normalize Android launch/dependency setup

Once Termux qualification passes, create the Phase-10-ready Android deployment seam incrementally:

- dependency preflight (`requests`, `urllib3`, other Navigator requirements);
- shared-storage permission check;
- authoritative runtime-root detection;
- one Termux launcher;
- clean stop/restart behavior;
- per-run diagnostic logs retained for qualification builds, reduced/rotated for production.

Do not promote this to `main` until physical Gate C is complete and regression gates are green at the same head.

---

## 5. Known architectural invariants — do not regress

1. GIS owns interaction and rendering, not flight physics.
2. Navigator owns route planning, compile, execution, ephemeris interpretation, and arrival truth.
3. Campaign services own the single persistent state transition.
4. Preview/selection must not mutate canonical campaign state.
5. Commit-planning-choice is not the same as execute-flight.
6. Stale plans must be rejected if campaign state changes after planning.
7. No duplicate authoritative location/epoch between GIS and Navigator.
8. Do not invent continuous trajectory geometry or engineering values when authoritative data is unavailable.
9. Frozen Gate-A physics oracle remains independent of new GIS-originated request/provenance hashes.
10. Old Navigator visual renderer stays available until Gate B and physical operational acceptance justify retirement.

---

## 6. Next-chat seed prompt

Copy/paste the following into the next chat:

> Reference the **GIS/Navigator Convergence Architecture and Work Plan v1.0** and **GIS/Navigator Convergence Status and Next Steps — 2026-09-03** in GitHub on `feature/gis-navigator-convergence`. Continue from the physical Android Phase-6 qualification. Automated Gate C is green, but Pixel physical acceptance is still open. Pydroid proved unreliable as the long-running local HTTP host; Termux is stable. After installing `requests/urllib3` in Termux, Mars→Ceres route discovery succeeded and a `HARD/CRUISE` candidate showed committed, with plausible remass (~11.886 t), but the GIS candidate cards incorrectly show `TIME 0.0 min`, `HOLONOMY 0.000`, and `CONFIDENCE 0.000`. Do **not** execute yet. First inspect the authoritative RouteCandidate/planning payload and fix the GIS summary-field adapter so missing/inapplicable values render as `—`, not fake zeroes. Then regression-test, give me the minimal Termux/Pixel update, and complete the physical Gate-C flow through execute/arrival/duplicate-execute rejection. Also treat mobile HUD ergonomics as immediate Phase-6 cleanup: flight-planning panel needs minimize/restore, hide/close distinct from cancel, compact scrolling, and preferably `PLAN FLIGHT HERE` from the selected Atlas body; consider a body dropdown as a secondary touch path. Do not start Phase 7 until physical Gate C is closed and the same-head regression stack is green.

---

## 7. Handoff state

**Development branch:** `feature/gis-navigator-convergence`  
**Pre-status branch head:** `dc35b34f92727a70df832dc1ec6cd1b1e69f2aca`  
**Current release posture:** development / physical qualification; not ready for `main` promotion.  
**Next architectural phase after closure:** Phase 7 — SQL migration discipline.
