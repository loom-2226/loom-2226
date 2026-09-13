# LOOM 2226 — Wayfarer Q6 Remass Mission Regression v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Purpose

Determine whether the inherited 250 t normal remass allowance is plausibly oversized, undersized or mode-dependent before changing any governing mass value.

This v0.1 pass does **not** replace Navigator. It uses ideal rocket-equation screening at the current 1,158.5 t reference wet mass to expose how strongly remass demand depends on effective exhaust velocity and ordinary-space delta-v.

## 1. Method

For a burn with effective exhaust velocity `ve` and required ordinary-space delta-v `dv`:

`m_prop = m0 * (1 - exp(-dv/ve))`

Reference starting mass for this sensitivity table: **1,158.5 t**.

The numbers are deliberately idealized: no gravity loss, no finite-burn trajectory correction, no reserve margin, no RCS use, no tank unusable fraction, and no feed-conditioning penalty. They are sizing bounds only.

## 2. Remass required by delta-v and torch mode

| Torch ve | 10 km/s | 30 km/s | 50 km/s | 100 km/s | 200 km/s | 300 km/s | 500 km/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3000 km/s ECON | 3.86 t | 11.53 t | 19.15 t | 37.98 t | 74.72 t | 110.25 t | 177.85 t |
| 2000 km/s CRUISE | 5.78 t | 17.25 t | 28.60 t | 56.50 t | 110.25 t | 161.37 t | 256.26 t |
| 1000 km/s EXPEDITE | 11.53 t | 34.24 t | 56.50 t | 110.25 t | 210.00 t | 300.26 t | 455.83 t |
| 700 km/s FAST | 16.43 t | 48.60 t | 79.86 t | 154.22 t | 287.91 t | 403.81 t | 591.37 t |
| 450 km/s HARD | 25.46 t | 74.72 t | 121.83 t | 230.85 t | 415.69 t | 563.71 t | 777.13 t |
| 300 km/s LIMIT | 37.98 t | 110.25 t | 177.85 t | 328.40 t | 563.71 t | 732.31 t | 939.69 t |

## 3. What 250 t buys at each exhaust velocity

At the 1,158.5 t starting mass, expending the entire 250 t normal remass allowance yields ideal delta-v of approximately:

- ECON 3000 km/s -> **729 km/s**;
- CRUISE 2000 km/s -> **486 km/s**;
- EXPEDITE 1000 km/s -> **243 km/s**;
- FAST 700 km/s -> **170 km/s**;
- HARD 450 km/s -> **109 km/s**;
- LIMIT 300 km/s -> **73 km/s**.

This is the central Q6.1 result.

## 4. Interpretation

The inherited `250 t remass` value is not inherently generous or conservative. Its adequacy depends on **how the ship uses the torch**.

If ordinary-space state matching is usually performed at ECON/CRUISE effective exhaust velocity, 250 t supports several hundred km/s of ideal cumulative delta-v and is likely a very large courier reserve.

If the ship routinely obtains large delta-v at HARD/LIMIT exhaust velocities, the same 250 t can disappear quickly. These modes trade exhaust velocity for force and should therefore be treated as **time-critical high-thrust modes**, not normal bulk-delta-v modes.

This suggests the final standard should distinguish:

- **high-Isp bulk delta-v doctrine** — ECON/CRUISE preferred when time/geometry permit;
- **high-thrust transient doctrine** — EXPEDITE/FAST/HARD/LIMIT used when force or burn duration matters;
- **reserve floor** — protected against route optimizer consumption;
- **RCS reserve** — separately budgeted or explicitly carved out from compatible working fluid;
- **protected water** — remains outside routine propulsion optimization.

## 5. Candidate dispatch cases for Q6.2

Before reducing the 250 t baseline, run at least these ordinary-space cumulative delta-v budgets through the real Navigator route suite:

### Case A — routine courier

`50 km/s total ordinary delta-v`

At CRUISE ve this costs ~28.6 t ideal remass.

### Case B — demanding trunk/terminal mission

`100 km/s total ordinary delta-v`

At CRUISE ve this costs ~56.5 t.

### Case C — severe degraded / metric-constrained mission

`200 km/s total ordinary delta-v`

At CRUISE ve this costs ~110.3 t.

### Case D — extraordinary ordinary-space recovery

`300 km/s total ordinary delta-v`

At CRUISE ve this costs ~161.4 t.

These cases are not route claims; they are regression buckets.

## 6. Preliminary remass-capacity implication

Q6.1 does **not** justify cutting the tanks yet, but it does justify testing lower dispatch loads while preserving structural/tank optionality.

Carry these candidate normal dispatch inventories into Q6.2:

- **100 t** — lean courier case;
- **150 t** — balanced case;
- **200 t** — heavy-reserve case;
- **250 t** — inherited baseline.

Do not change tank geometry merely because normal dispatch mass falls. Empty or partially filled feed-compatible capacity may be operationally valuable for regional sourcing, emergency tankering, cargo-water carriage and mission-specific alternate feeds.

## 7. High-thrust mode doctrine emerging from the numbers

At the current card, HARD/LIMIT are expensive in remass because their lower exhaust velocity is the mechanism by which fixed source power produces very high thrust.

Therefore the final flight standard should almost certainly prohibit route optimization from using HARD/LIMIT merely to save minutes unless an explicit cost/urgency rule authorizes it.

Candidate doctrine:

- ECON/CRUISE: unrestricted bulk-delta-v planning subject to thermal and mission constraints;
- EXPEDITE: time-critical, costed use;
- FAST: exceptional use;
- HARD: emergency/tactical/high-authority use;
- LIMIT: crew/structure/time-limited contingency only.

Exact labels and duration limits remain Q5/Q7 work.

## 8. Q6.1 disposition

**PASS as a screening result.**

The 250 t baseline is retained for comparison, but it is no longer treated as self-justifying. The next pass must use actual Navigator routes and state matching to determine the distribution of cumulative ordinary-space delta-v, then select normal dispatch remass and reserve doctrine from mission evidence.

The key finding is:

> **Wayfarer remass requirement is primarily a mission-and-mode allocation problem, not a fixed property of the torch or of water.**
