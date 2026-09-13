# LOOM 2226 — Wayfarer Q5 Power & Thermal Closure v0.2

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Purpose

Turn the Q5.1 thermal firewall into a bounded design envelope for radiator rejection, thermal buffering, RCS power and allowable torch-to-ship heat coupling. This document does not alter CANON II.

## 1. Governing anchors retained

- high-drive reject interface: 900 K;
- current torch jet-power card: approximately 5.11–12.78 TW at the 1,158.5 t reference wet mass;
- major torch and high metric remain mutually exclusive;
- the 719 m² HARD metric value is an equivalent radiator requirement, not a literal total panel area;
- torch jet power is not electrical-bus power.

## 2. Candidate physical radiator envelope

Screen an **effective radiating area of 3,000–4,000 m²** across four major radiator assemblies. This is an engineering candidate only; geometry/packaging must still prove it can be physically deployed and survive plume/interference constraints.

At 900 K and emissivity 0.9:

- 3,000 m² -> ~100.5 MW steady rejection;
- 3,500 m² -> ~117.2 MW;
- 4,000 m² -> ~134.0 MW.

This immediately gives the desired system behavior: ordinary hotel/metric/RCS recovery loads can be steady-state or slowly recovering, while multi-TW torch power remains overwhelmingly directed into exhaust rather than dumped into the ship.

## 3. Candidate thermal buffer

Screen a **60 GJ usable high-temperature thermal buffer** as the Q5 design point, with 50 GJ as a lower sensitivity case. This value is not canon and must later be tied to specific buffer media, mass, temperature swing and structural integration.

At 60 GJ, ignoring simultaneous radiator rejection, buffer-only endurance is:

- 50 MW net heat -> 1,200 s = 20 min;
- 100 MW -> 600 s = 10 min;
- 200 MW -> 300 s = 5 min;
- 500 MW -> 120 s;
- 1 GW -> 60 s.

With a 100 MW-class deployed radiator system, only heat above roughly 100–130 MW needs to accumulate in the buffer.

## 4. Torch heat-coupling requirement

For the current reference mode card, require two separate quantities:

1. `JET_POWER` — directed exhaust kinetic power;
2. `SHIP_COUPLED_HEAT` — heat that actually enters spacecraft thermal loops.

A candidate **normal continuous ship-coupled torch-heat ceiling of 50 MW** is adopted for screening. A **100 MW excursion ceiling** is used for bounded transient sensitivity only.

At 50 MW, approximate coupling fractions are:

- ECON 5.11 TW -> 9.8e-6;
- CRUISE 11.36 TW -> 4.4e-6;
- EXPEDITE 11.36 TW -> 4.4e-6;
- FAST 11.93 TW -> 4.2e-6;
- HARD/LIMIT 12.78 TW -> 3.9e-6.

Therefore the mature torch must hold steady ship coupling to roughly **4e-6 at the high-power end**, and no worse than about **1e-5 in ECON**, if 50 MW is to remain a credible normal thermal load.

This is a fictional constitutive engineering requirement, not an empirically established fusion-torch coefficient.

## 5. RCS architecture disposition

Q4 established a candidate 25 kN individual high-authority thruster, approximately 100 kN aggregate normal translation and approximately 200 kN aggregate abort authority.

The Q5 screening point is now:

### Precision mode

- internal momentum storage preferred for pure attitude hold;
- external RCS deeply throttled;
- minimum impulse bit and plume cleanliness dominate;
- high-Isp operation may be used where thrust is low enough for bus closure.

### Maneuver mode

Adopt **20 km/s nominal high-authority exhaust velocity** as the current lead point, with 50 km/s retained as an alternate high-Isp setting.

At 25 kN per thruster:

- 20 km/s -> 250 MW jet power, 1.25 kg/s;
- 50 km/s -> 625 MW jet power, 0.50 kg/s.

At 100 kN aggregate:

- 20 km/s -> 1.0 GW jet power, 5.0 kg/s;
- 50 km/s -> 2.5 GW jet power, 2.0 kg/s.

At 200 kN abort authority:

- 20 km/s -> 2.0 GW jet power, 10 kg/s;
- 50 km/s -> 5.0 GW jet power, 4.0 kg/s.

Because RCS delta-v is small, the 20 km/s setting is preferred for force-heavy maneuvers unless mission analysis shows the remass penalty dominates.

## 6. RCS efficiency and thermal sensitivity

Do not assume all RCS input power becomes jet power. Screen conversion efficiencies of 0.90 and 0.95.

For 100 kN aggregate at 20 km/s:

- jet power = 1.0 GW;
- at 95% conversion, input ≈1.053 GW and conversion heat ≈52.6 MW;
- at 90%, input ≈1.111 GW and conversion heat ≈111 MW.

Thus a 100 kN maneuver can plausibly sit near the radiator/buffer boundary if conversion efficiency is high. It should not be assumed indefinitely continuous.

For 200 kN abort at 20 km/s:

- jet power = 2.0 GW;
- at 95% conversion, conversion heat ≈105 MW;
- at 90%, ≈222 MW.

With ~100 MW steady radiator rejection and a 60 GJ buffer, even the 90%-efficient abort case has several minutes of thermal margin before buffer exhaustion. That is adequate for an abort-class system if actual maneuver durations are tens of seconds to a few minutes.

## 7. Power architecture candidate

Carry forward a split propulsion-energy architecture:

- **direct torch channel:** multi-TW source-to-exhaust path, not routed through the ordinary electrical bus;
- **main electrical bus:** tens-of-MW class continuous loads for habitat, controls, cryogenics, metric and ordinary ship systems;
- **high-power maneuver branch / pulse conversion:** GW-class short-duty path feeding RCS without implying a GW-class continuously rejected hotel bus;
- **reversible field bank:** remains the canon 2 GJ relational formation/control/abort bank and is not silently repurposed as the RCS energy store;
- **thermal buffer:** stores waste heat, not propulsion energy.

Exact electrical storage technology and pulse-bank energy remain OPEN.

## 8. RCS energy-duration examples

At 100 kN and 20 km/s, jet power is 1 GW:

- 10 s maneuver -> 10 GJ jet energy;
- 30 s -> 30 GJ;
- 60 s -> 60 GJ.

At 200 kN and 20 km/s:

- 10 s -> 20 GJ;
- 30 s -> 60 GJ;
- 60 s -> 120 GJ.

These figures show why the RCS power path should be a high-power **conversion branch**, not necessarily a battery containing the entire maneuver energy. The reactor/source can feed the maneuver in real time while the thermal buffer only absorbs inefficiency and transient ship-coupled heat.

## 9. Q5.2 engineering disposition

Supported for continued qualification:

- candidate effective radiator envelope: **3,000–4,000 m² at ~900 K**;
- candidate usable thermal buffer: **50–60 GJ**, lead screening point 60 GJ;
- normal torch ship-coupled heat target: **≤50 MW**;
- bounded transient torch thermal sensitivity: **≤100 MW**;
- required high-power torch coupling at HARD/LIMIT: order **4e-6** for the 50 MW target;
- high-authority RCS lead exhaust setting: **20 km/s**;
- alternate high-Isp RCS setting: **50 km/s**;
- 25 kN individual / 100 kN normal aggregate / 200 kN abort remains a viable Q4/Q5 candidate if conversion efficiency approaches 95% and duty is bounded;
- direct torch, electrical bus, RCS pulse-conversion path and thermal buffer must remain separate ledgers.

## 10. Still open before Q5 PASS

1. physical radiator geometry and deployed area proof;
2. buffer medium, mass and temperature swing;
3. exact RCS conversion efficiency and hardware mass;
4. exact continuous electrical generation capacity;
5. high-power maneuver branch topology and switching mass;
6. species-dependent Q2 conditioning losses;
7. torch coupling coefficient as a constitutive in-universe machine property;
8. mission-derived duty cycles;
9. degraded-radiator failure behavior.

**Q5 remains OPEN, but the design space is now bounded tightly enough to proceed into mission regression without inventing unlimited cooling or an unlimited electrical bus.**
