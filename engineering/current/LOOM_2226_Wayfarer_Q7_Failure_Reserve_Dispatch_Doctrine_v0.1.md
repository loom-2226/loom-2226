# LOOM 2226 — Wayfarer Q7 Failure, Reserve & Dispatch Doctrine v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Purpose

Convert Q4/Q5/Q6 engineering findings into explicit dispatch and degraded-state rules without prematurely changing the inherited 250 t remass baseline.

This doctrine is intentionally parameterized. Final remass quantities remain blocked on the populated Q6 Navigator mission suite.

## 1. Working dispatch hypothesis

For regression only:

- normal dispatch remass: **150 t**;
- minimum dispatch remass: **100 t**;
- protected optimizer reserve: **50 t**;
- contingency-feed reserve: **0 t pending Q2/Q5 closure**.

These values are **CANDIDATE screening points**, not qualified replacements for current canon.

The 50 t protected optimizer reserve is ordinary propulsion remass withheld from routine planning. It is **not** the separate 50 t protected life-support/water reserve in CANON II.

## 2. Mode authorization doctrine

- **ECON** — routine bulk-delta-v mode.
- **CRUISE** — routine bulk-delta-v mode.
- **EXPEDITE** — time-critical, costed authorization required.
- **FAST** — exceptional authorization required.
- **HARD** — emergency/tactical use; route optimizer may not select it solely to improve schedule.
- **LIMIT** — contingency-only; requires explicit duration, thermal, structural, and reserve closure.

Higher urgency permits lower-tier modes, but not vice versa.

## 3. Reserve doctrine

Routine route optimization may consume only remass above the protected optimizer reserve.

A mission is considered dispatch-feasible only when:

1. departure remass is at or above the minimum dispatch threshold;
2. predicted accessible remass after declared tank/feed degradations is sufficient for planned usage;
3. predicted arrival remass remains at or above the protected optimizer reserve;
4. protected life-support/water reserve is excluded from routine propulsion accounting.

If a route consumes the protected optimizer reserve but does not exhaust propulsion remass, disposition is **DIVERT_OR_REPLAN**, not automatic dispatch.

If predicted consumption exceeds accessible propulsion remass, disposition is **MISSION_INFEASIBLE**.

## 4. One-tank isolation

Current geometry carries four equal major tanks. Until actual fill-state accessibility is supplied by Navigator, Q7 uses a first-order assumption:

- one full tank isolated -> **25% loss of accessible propulsion remass**.

This is conservative bookkeeping, not a claim that every tank will always be equally filled.

Isolation requires:

- accessible-remass recomputation;
- center-of-mass and inertia recomputation;
- RCS/trim authority re-evaluation;
- route and reserve re-score.

## 5. Primary remass unavailable / alternate feed only

If normal primary remass cannot be loaded at destination:

- use only a Q2-certified or Q2-derated alternate;
- apply the alternate feed's usable fraction and mode restrictions;
- apply Q5 conditioning/thermal penalties;
- recompute the mission before dispatch.

No generic 'any fluid works' fallback is permitted.

A separately carried contingency-feed reserve remains **OPEN** until the mission suite proves its benefit exceeds tank, conditioning, and logistics cost.

## 6. Metric unavailable or uncertified

Required response:

1. replan in ordinary space;
2. preserve ECON/CRUISE as bulk-delta-v modes where geometry/time permit;
3. assess diversion or safe-haven options;
4. block any plan that spends the protected optimizer reserve without explicit emergency authority.

Metric unavailability does not authorize a free ordinary-state reset.

## 7. Torch unavailable

If the main torch is unavailable before departure:

- cancel any high-delta-v departure that depends on it;
- retain RCS for local safety, docking, station keeping, and collision avoidance only;
- use endurance propulsion only if separately qualified and sufficient for the local escape/safe-haven problem;
- seek tug, repair, or safe haven.

Torch failure after departure becomes a Q6 degraded-mission problem; survival may remain possible, but original mission completion is not assumed.

## 8. Endurance drive unavailable

If E1/E2 is absent or failed:

- revert to E0 planning;
- route remains valid only if torch/metric/remass/thermal ledgers independently close;
- endurance failure alone must not strand a ship whose baseline standard claims E0 compatibility.

## 9. Radiator degradation

Radiator degradation requires:

- reduced continuous duty;
- recalculated thermal-buffer consumption and recovery;
- blocking any propulsion card whose Q5 thermal ledger no longer closes.

No 'short burn' waiver may use an unbounded thermal buffer.

## 10. Reduced reactor / bus power

Power degradation requires:

- RCS derating when its power channel is affected;
- blocking torch/RCS/endurance cards whose source or conversion power no longer closes;
- preservation of avionics, life support, navigation, and safe attitude authority before schedule performance.

## 11. RCS cluster loss

After one cluster loss:

- recompute translation vectors and pitch/yaw/roll torque authority;
- identify plume/dead-zone changes;
- block docking or close-proximity operations whose geometry no longer closes;
- reduce permitted slew/settle envelope as required.

A surviving aggregate thrust number alone is insufficient; directional controllability must remain closed.

## 12. Attitude momentum system degraded

Required response:

- reduce nominal slew envelope;
- increase settle margin;
- rely more heavily on external RCS for unloading/high-authority corrections;
- prohibit main-torch or metric acquisition if pointing/alignment tolerance cannot be maintained.

## 13. Launch DOCKED / ABSENT asymmetry

The launch changes mass and lateral balance. Any transition between DOCKED and ABSENT requires:

- mass-property refresh;
- trim refresh;
- RCS authority verification;
- metric boundary/configuration recertification where required by governing canon.

## 14. Abort / diversion triggers

The candidate automatic triggers are:

- projected arrival reserve below protected optimizer reserve -> **DIVERT_OR_REPLAN**;
- departure remass below minimum dispatch -> **NO_DISPATCH**;
- projected consumption greater than accessible propulsion remass -> **MISSION_INFEASIBLE**;
- thermally or power-uncLOSED mode -> **BLOCK_MODE**;
- attitude/docking control geometry unclosed -> **BLOCK_OPERATION**;
- metric certification HOLD/BLACK -> ordinary-space replan, not override.

Emergency authority may deliberately spend protected propulsion reserve only when the alternative is loss of ship/crew or a comparably severe safety outcome. That expenditure must remain explicit in the mission/event ledger.

## 15. Q7 v0.1 disposition

**PASS as doctrine architecture; numerical reserve values remain CANDIDATE.**

Q7 has now established:

- a mode-authorization ladder;
- explicit optimizer reserve protection;
- dispatch/replan/infeasible dispositions;
- degraded-state actions;
- one-tank-isolation handling;
- alternate-feed handling;
- separation of propulsion reserve from protected life-support water.

Final normal dispatch remass, minimum dispatch remass, and contingency-feed reserve remain blocked on populated Q6 Navigator evidence.
