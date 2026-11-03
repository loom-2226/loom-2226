# LOOM Shuttle v1 R2 — Resized research comparison

ALL bodies. ALL sponsors. 2026–2226.

**RESEARCH / NON-CANON / NON-QUALIFICATION.** kT decisions R1–R5, 2026-11-03. Numerical tests executed with Node on local working branch. Do not merge this PR without review, and do not treat the original B/KF OPENs as physically resolved.

## Resizing and physics provenance

- Nominal shuttle length **12.8 m** unchanged; diameter **4.3 → 3.8 m**, matching the certified Wayfarer shuttle outer diameter. The **existing 4.8 m bore / 4.8 m slot** and Wayfarer longerons, strakes, hot fins and C-tank must remain unchanged.
- Pod **2.8 → 2.5 m OD**, maximum **3 crew** (2-crew operational alternative). [WHOI Alvin](https://www.whoi.edu/what-we-do/explore/underwater-vehicles/hov-alvin/faqs/) provides an **ONLINE precedent of a 2.1 m ID three-person titanium pressure sphere**, not Venus heat or 92 bar qualification.
- Pressure shell is projected from old 3.2–7.6 t using constant dimensionless wall ratio **(2.5/2.8)^3** => **2.2777–5.4095 t**. Max shell yields analytic internal diameter **2.369 m**, above Alvin's 2.1 m accommodation precedent. External-pressure hot buckling, seals and penetrations still OPEN.
- Fittings/seals scale with **R²**; folded rover chassis with pod OD; landing gear/door/ramp mass assumed **75% hull-diameter scaling +25% fixed**; hull structure **80% perimeter scaling +20% fixed**. All assumptions are explicit in source JSON. Neither wheel stowage nor axial CG has physical qualification.
- Stowed rover wheels/chassis, rotor hub/mast, belly nozzles and folded blade spine each assumed **≤1.85 m radius** inside the **1.90 m hull radius**, yielding **0.05 m notional subsystem headroom**. This is a necessary envelope assumption, NOT measured geometry. The G8 bay's radial clearance from the *nominal* hull is **0.50 m**; physical gate B remains OPEN until actual mast/hub, pod x/CG, door/ramp and hinge envelopes are supplied. Three-metre rotor blade segments and hot gas joints/hold door apertures stay KF OPEN.
- TPS **TOTAL** 3–6 t is conserved with one sampled parameter: **one third CORE Mars base TPS (1–2 t)** and **two thirds EXTRA Venus/Titan kit TPS (2–4 t)**. Both are tagged **ASSUMPTION_DERIVED**. NASA published Mars/Venus materials/environments show different TPS needs but do *not* verify this exact split. The original total is never added as a third physical part. This is a research estimate, subject to mission-specific entry heating and physical design.

## Quantitative comparison (6,561 deterministic balanced samples per run)

| Gate / quantity | Merged 4.3 m / 2.8 m, 2/4 crew | R2 3.8 m / 2.5 m, 2/3 crew |
|---|---:|---:|
| Core docked midpoint | 31.825 t | **30.3297414235 t** |
| Kit midpoint | 11.76875 t | **10.26875 t** |
| Core min–max | 21.150–42.500 t | **20.155–40.504 t** |
| Kit min–max | 6.925–16.613 t | **5.925–14.613 t** |
| A2 core <=34.2 t | 4374 PASS /6561 =66.667% | **5103 PASS =77.778%** |
| Kit aggregate packed volume KV | 4860 PASS =74.074% | **5103 PASS =77.778%** |
| Physical KF stow | OPEN/FAIL | **OPEN/FAIL** |
| Physical B full geometry | OPEN 6561 | **OPEN 6561** |
| Rotor R necessary | 6561 PASS | **6561 PASS** |
| Venus water C necessary | 5589 PASS =85.185% | **5589 PASS =85.185%** |
| D-shuttle 2 crew | 2268 PASS =34.568% | **2835 PASS =43.210%** |
| D-shuttle maximum crew | four: 2106 PASS =32.099% | **three: 2835 PASS =43.210%** |
| D-pod detached passive, sampled 2 crew | 0.368–7.054 h | **0.450–7.910 h** |
| D-pod detached passive, sampled max crew | four: 0.364–6.452 h | **three: 0.447–7.516 h** |
| Calculated Venus rotor handover | 17/42/66 km min/median/max | **18/43/66 km** |

R2 Stage 3 runs all four worlds on the resized common shuttle. **Moon/Mars/Mercury polar H2/O2 chemical baseline A2_CHEM: 5103/6561 PASS (77.778%); chemical belly + ideal torch water 6561 PASS**. Full ascent ORBIT_FULL, physical surface thermal and source/cryogenic hardware remain OPEN; Titan KIT_VOLUME 5103 PASS, rotor model 60 km boundary remains research-only. Same loaded water and 2×50 MW Wayfarer house supply assumptions apply, not new flight qualification.

## Wayfarer integration constraints

Nominal reference docked shuttle replacement **27.900 → 30.3297414235 t**, Δ **+2.4297414235 t**. If the current **11.284117 t** unallocated reserve pays this uplift, the implied remaining reserve is **8.8543755765 t**, above the 5 t floor *before any additional hardware*. A future Wayfarer G1–G12 run must verify the whole-ship mass and dynamics without habitat or performance losses. The 1–4 t Wayfarer electrolysis/liquefaction plant remains removable PAYLOAD, NOT permanent dry mass. Venus/Titan kit stays payload.

Nothing here proves the full mast, pod, access ramp, exit-door swept geometry, pressure-sphere or physical hold fit. Those remain explicit physical holds.
