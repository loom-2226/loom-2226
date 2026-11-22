# Weave prototype outings: dodge, sensors, weather landing, transmedium (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-22. Sol's outings brief, run in Sol's order. The prototype is operational and its M1/M2 exchange physics is UNKNOWN; that is not a blocker.

- **Geometry:** R 15 m / wall 2 m zero-expansion shift.
- **Shuttle:** 61 t (20 m hull, crew seat, cargo mount).
- **Models:** the simplest existing ones.

Code: `outing_dodge.py`, `outing_sensors.py`, `outing_landing.py`, `outing_transmedium.py`, `outings_figure.py` → `weave_outings.png`. Data: `outing_*.json`.

Labels: DERIVED (mathematical, within the stated model), ESTIMATE, ASSUMED (LOOM operating assumption), UNKNOWN.

## 0. Cross-cutting findings

1. **Gravity support.** The shift alone cannot hover. Its interior is in free fall, so holding altitude needs an interior shift growing as g·t. The field edge's speed through the local air reaches Mach 1 after about 14 s (DERIVED). Near a planet the prototype therefore runs as **W2 cushion (gravity-cancelling, interior weightless) + Weave shift (translation)**: ASSUMED operating mode, from the lane's W2. The cushion's height is "paid" through the unknown exchange (lane W2).
2. **Lapse wake correction.** With air pressure included, a lapse-type field barely disturbs uniform air (0.2 kJ, against 20–45 MJ in the collisionless model; DERIVED, linear). The shift carries air; a lapse field leaves air in place and exposes the hull to ordinary aerodynamics. `WEAVE_GEOMETRY_COMPARE_2026_11_21.md` is annotated.

## 1. Dodge: one lateral sidestep, 30 m in 0.5 s (hull across the motion)

| | 30 m / 0.5 s | 30 m / 0.4 s (quiet limit) |
|---|---|---|
| Peak speed / acceleration | 112 m/s / 71 g | 141 m/s / 110 g |
| Crew / cargo felt | 0.66 g / 0.65 g | 1.07 g / 1.05 g |
| Hull peak load | 122 kN | 190 kN |
| Field-edge speed through local air | Mach 0.80 | Mach 1.00 |
| Energy lent: ship / air (returned) | 0.39 GJ / 0.14 GJ | 0.60 GJ / 0.22 GJ |
| Peak exchange power | ~4 GW | ~8 GW |

- **The shuttle:** steps 30 m sideways in half a second and stops (0.24 m short at the hull ends). Hull across the motion is the harshest orientation: the hull ends sit in stronger return flow than in the end-on dash (0.018 g at 13 g). (DERIVED)
- **Occupants:** under 1 g for 71–110 g of manoeuvre. (DERIVED)
- **Observer / sensor:** a solid object jinking at 71 g with no plume, and sound only if the field edge goes supersonic. A thermal signature is **not** ruled out: it depends on the unknown loss fraction η (corrected after Sol review). The quiet limit is T ≥ 1.875·D·2.45/c_s = **0.40 s for 30 m**. (DERIVED)
- **Environment:** 68 t of air moved more than 1 m; peak air speed 163 m/s during the move; no residual wind in calm air. (DERIVED, ideal fluid)
- **Unknown:**
  - the loss fraction η of the lent energy; heat per dodge ≈ η × ~1 GJ throughput, which sets how many sheddable heat sinks a dodge uses;
  - the exchange partner;
  - behaviour when the field edge goes supersonic.

## 2. Sensor signature: one radar and one optical geometry

**Radar: head-on monostatic, rays traced through the time-dependent metric** (dispersion ω = c|k| + b·k; reflection in the hull's local frame). (DERIVED)
- The received Doppler equals ordinary two-way Doppler for the reflector's local speed, at every time step tested: 8.3 kHz X-band at 125 m/s.
- The −0.66% residual is exactly F(10) = 0.993 at the hull nose. With a stiff hull moving at V it is classical.
- The field adds less than 1e-13 s of delay.
- **Radar sees the true speed and track.**
- Field radar cross-section ~3e-11 m² against a hull of ~10 m² (ESTIMATE). The field itself is invisible to radar.

**Optical: side-on camera, rays crossing the field at peak speed.**
- Metric deflection ≤ 2e-12 rad. First-order bending cancels for a crossing ray because b_y is odd along the line of sight. (DERIVED)
- The visible effect is **air the dash has rearranged in a layered atmosphere**. Parcels are moved up to 9.5 m vertically, giving ray deflections of 1.7 / 4.2 / 6.5 µrad for dn/dz of −4e-8 / −1e-7 / −1.57e-7 per metre (DERIVED from the parcel map). That is at or below normal atmospheric shimmer (~5 µrad), so not visible to the eye. Shimmer imaging (background-oriented schlieren) could detect a faint shimmer column along the track and a ring at the stop point.
- **Unknown:** imaging at high field speeds (first-order effects for rays along the motion); carried particulates (dust, rain, birds move with the bubble and would show on radar and optical).

## 3. Landing in moderate weather (10 m/s wind, gusts to 15 m/s, moderate rain)

- **The shuttle:** approaches on the shift, hovers on the cushion, descends.
  - The cushion switching on to full gravity cancellation in air gives peak air speed **0.16 m/s**, pressure shifts of **137 Pa** (quasi-static ρ·g·Φ = 136 Pa), and **0.006 J** radiated (DERIVED, linear compressible).
  - **No downwash.**
  - Wind blows through the domain unaffected; only the hull feels it.
- **Occupants:** the cabin is weightless during cushion flight. Wind drag on the hull (ASSUMED 80 m² side area, Cd 1) gives crew 0.008 g at 10 m/s and 0.018 g at 15 m/s; the field cannot cancel it for the crew. Touchdown: weight returns over the release ramp. (ESTIMATE)
- **Observer / sensor:** no rotor wash and no exhaust. **Rain stops falling inside the field.**
  - Weightless drops halt within ~1.1 m (about 0.4 s) and drift through with the wind (~3 s residence).
  - That leaves a ~30 m sphere of hanging rain, a dry patch under the craft and a wetter strip downwind. (ESTIMATE)
- **Environment at touchdown:**
  - The spherical domain reaches the ground when the field centre is ~19 m up.
  - Inside the footprint, loose ground matter, puddles and **people are weightless**; dust lifts with any breeze ("levitating debris", not brownout).
  - The field's edge, where it crosses the ground, presses surface matter down by up to **3.3 g** (reverse-force factor on axis). On soft ground that could leave a ring imprint, radius ~14.7 m at a 3 m hover.
  - Ground crew must stay outside ~15–19 m. (ESTIMATE)
- **Unknown:** cushion source and exchange; real soil response; whether a flattened domain is admissible (not modelled; existing geometry only); behaviour on release if loose matter is still airborne.

## 4. Transmedium: two-layer air/water, gravity (exit, entry, skim)

Model: exact kinematic shift transport, cushion-weightless interior, gravity through the advected configuration. Transit relaxation under gravity is not modelled (transit 1.5 s, comparable to √(R/g) = 1.2 s).

| | Exit (−30 → +30 m, 1.5 s) | Entry (+30 → −30 m) |
|---|---|---|
| Carried across the surface | **8.9 kt of sea** lifted inside the field (centroid 26 m up) | **8,900 m³ of air** taken down (mean depth 26 m) |
| Left behind | air cavity 9,300 m³ (mean depth 5 m) | 8.5 kt water crown thrown up (centroid 4.9 m) |
| Energy in the disturbed surface (APE) | **2.7 GJ** (2.3 GJ splash on release + 0.45 GJ cavity collapse) | **2.7 GJ** (2.3 GJ buoyant bubble + crown) |
| Pressure check | A thin annular water neck stays continuous from sea to ball (to 20 m at lattice resolution). As a hydrostatic column it needs ~0.46 bar tension above ~10 m: it **cavitates/ruptures** and drains as spray (CONDITIONAL on hydraulic connection) | Carried bubble at 1 atm in 3.9 atm water: **2.9 bar under-pressure**. If released it collapses (up to ~1.4 GJ, ESTIMATE) and/or rises as a boil (2.3 GJ) |

| Skim (field centre above water) | 5 m | 10 m | 15 m | 19 m |
|---|---|---|---|---|
| APE left in the water | 121 MJ | 74 MJ | 4 MJ | 18 kJ |
| Water lifted above the surface | 2,440 t (to 4.5 m) | 1,460 t (to 8.8 m) | 246 t (to 2.8 m) | 0 |
| Sea carried the full 200 m | 898 t cap | 8 t | 0 | 0 |

- **The shuttle:** crosses the interface inside its own pocket of whichever fluid it started in. It leaves the sea wrapped in a weightless ball of seawater and dives inside a ball of air.
- **Occupants:** weightless and undisturbed inside the field. The interface passes through the wall region, not the cabin, if clearance holds. (DERIVED within the model)
- **Observer / sensor:** exit is a breaching sphere of sea, a ruptured neck raining spray, and a collapsing cavity, then a 2.3 GJ splash when the ball is released. Entry is a water crown plus a delayed boil or underwater collapse pulse. Low skims plough a furrow with ridges and white water. Above ~19 m (field centre) the skim is clean. These signatures are anything but stealthy, and radar would see the water mass.
- **Environment:** gigajoule-scale splashes and waves per crossing (~0.6 t TNT-equivalent of energy, released over seconds as water motion, not explosively). Outgassing likely wherever carried water is decompressed. **Vapour cavitation does occur** in the exit neck, which ruptures; elsewhere no tension beyond the vapour limit was found. (CONDITIONAL)
- **Unknown:**
  - free-surface dynamics during transit and release (needs a free-surface solver: not built);
  - whether the cushion edge can hold the entry bubble against 2.9 bar;
  - spray and wave generation details;
  - effect of a hull-hugging domain (would cut carried mass to ~2.4 kt; not modelled);
  - salt and biology.

## 5. What the outings reveal (for kT and Sol)

- **Air:** the shuttle is sensor-quiet but not invisible. The field itself is undetectable, while radar tracks the hull's true kinematics, including 71–110 g jinks with no plume.
- **Weather:** the strongest visual signature is rain hanging in a sphere and levitating debris at touchdown.
- **Water:** the opposite of stealth. Every crossing moves thousands of tonnes and leaves GJ-scale splashes; low skims plough.
- **Rules that emerged:**
  - quiet dodge T ≥ 0.4 s per 30 m;
  - clean skim above ~19 m (field centre);
  - cushion needed for hover;
  - ground and people inside the footprint go weightless.
- **Still UNKNOWN:** exchange physics, loss fraction (heat-sink use per manoeuvre), supersonic-edge behaviour, free-surface details.

No canon change. Results return to kT and Sol first.

## 6. Sol review of e7f28ef: qualifications and AP comparison (2026-11-22)

**Qualifications accepted** (they matter for observation comparisons, not for prototype operation):

1. **"Sensor-quiet" is limited to the geometries tested.** Direct field signatures are weak for one radar and one optical geometry. Radar still detects the hull. Other viewing angles and higher speeds are untested.
2. **No exhaust does not mean no heat.** The thermal signature depends on the unknown loss fraction (§1 corrected).
3. **Water results are kinematic.** The 2.7 GJ figure is the available potential energy of the displaced water, not a resolved splash, cavitation or wave calculation.

**AP comparison (Sol; non-canon theory-to-observation comparison; AP v0.2 baseline left untouched).**
- Weave reproduces, *inside LOOM*, several reported behaviours: abrupt manoeuvres without corresponding crew loading, and no visible conventional propulsion or downwash.
- The strongest correspondence is **movement plus a water-surface disturbance without submersion**: a skim with the field centre 10 m above the water displaces ~1,460 t (74 MJ).
- It does **not** explain any verified real-world anomaly. Foam, wave pattern and duration are not computed, so resemblance to any witness account is not established.
- **Possible falsifier:** Weave predicts a violent interface crossing. A verified *quiet* water crossing would challenge this configuration.
- Optical metric distortion is negligible in the tested view, so it offers no explanation for apparent rotation or parallax-type effects.

**Sol's suggested next step (not started; awaiting kT):** render an external observer's view of a 10 m skim over calm water from the existing displacement map, and compare observable features with the witness record. Keep separate the disturbance, the object's position and motion, the absence of visible propulsion, and what cannot be corroborated. No new propulsion physics.
