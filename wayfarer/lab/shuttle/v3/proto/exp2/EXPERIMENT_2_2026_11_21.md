# Prototype lane, experiment 2: smallest extraordinary capability
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON research only, per kT's brief of 2026-11-21. No canon change, no Wayfarer change, no new design population, no winner. Numbers are screening results from the explorer ROM plus simple bounds.

**Reference vehicles:**
- Conventional reference: #2643 + Osteon cautious.
- Adaptive reference: W1 + Osteon cautious (17 m span, 18 t tank, 38.38 t dry).
- Bay: 12.8 m baseline, with 14.3 m kept as a contingency.

**Files:** `exp2_w1.py/.json`, `exp2_w2.py/.json`, `exp2_w3.py/.json`, `exp2_figures.py` → `exp2_departure.png`, `exp2_w1_w3.png`.

## Corrections to the first lane note
- **2 km lift energy:** mgh for 60 t raised 2 km is **1.18 GJ**. The earlier "~3 GJ" was (mgh + ½mv²)/η, with v = 125 m/s and η = 0.6; it is now itemised.
- **"20 s" climb:** this contradicted its own 0.4 g profile, which reaches 2 km in 32 s at 125 m/s. Climbing 2 km in 20 s needs about 1 g net.
- **"1 t flywheel":** this uses kT's **declared 2226** storage (1 kWh/kg, 150 kW/kg; ship_power record of 2026-11-01). That is about 10× an ordinary 2026 flywheel. With ordinary storage, no field scenario closes.
- **W3 air energy:** the 0.2–0.9 GJ figure assumed one boundary model (hypothesis 1 or 2 below). It is not a universal requirement.

## W1: programmable structure vs conventional mechanisms
**Osteon vs W1:**
- *Osteon (established):* a static, stronger titanium (22–38% lighter on primary members).
- *Programmable structure (proposed):* geometry or stiffness switching, with no evidence anywhere in the repo.

**Bay fit (geometry):**
- A *conventional* 17 m fold-over-top wing fits: there is a 0.74 m clear band above the spine inside the 2.15 m envelope, and two stacked folded panels need 0.53 m.
- Fans, floats, the cradle and the hinge fittings sharing that band have **not** been checked.
- A single-stage telescoping wing cannot reach 17 m, because 6.4 m panels are longer than the hull is wide.

**Decomposition (model):** all seven variants pass all five missions; they differ in margin.

| Variant | Dry (t) | Hot touchdown (m/s) |
|---|---:|---:|
| A telescoping 13.7 m | 35.95 | 49.5 |
| B conventional fold 17 m | 37.28 | 48.0 |
| D programmable stow only | 38.38 | 49.3 |
| **E conventional fold + adaptive camber** | **37.28** | **43.3** |
| F full W1 (lane reference) | 38.38 | 44.3 |

- The margin comes from adaptive camber (CL cap 5, a sensitivity), **not** from shape-changing stowage.
- Programmable stowage is heavier than a fold in this model (1.5× against 1.2× wing mass).

**Stiffness and control (required values):**
- A flat-stowed wing that locks into a box needs **35–170 MPa** of shear at the locks (8 g × 1.5).
- Friction or vacuum jamming gives about 0.05 MPa, so the locks have to be mechanical (teeth, zippers, bistable shells) or a reversible structural bond.
- An unlocked web turns the box into an open section with about 1% of the torsional stiffness. Lock integrity is therefore flight-critical.

**Actuation:** energy is trivial (0.1–1 MJ). Mass is the open question.

**Adaptive stiffness (credible value):**
- Re-armable slam and crash absorbers.
- At 5 m/s sink, a 0.15–0.30 m adaptive stroke cuts slam load from about 25 g (rigid) to 4–9 g.
- A 16 g crash at 15 m/s needs 0.7 m of stroke, absorbing about 7 MJ, and the absorber can be reset afterwards rather than replaced.

## W2: four departures (M1 field, central assumptions)
**The three mechanisms, kept apart:**
- **M1, reduced effective gravitational loading:** the reaction goes to the planet. It needs a new constitutive relation. It is in tension with the equivalence principle only if it is framed as changing matter rather than as an applied coupling.
- **M2, modified inertia:** in tension with a governing invariant (the equivalence principle, plus momentum or energy on switch-off). It gives no lift, so it is dropped.
- **M3, engineered geometry:** canon-family physics but beyond canon technology. The wall may not cut water or people.

| | to 200 m | to 2 km | exhaust at surface | source energy | peak power | device ceiling (central / pessimistic) | new choice |
|---|---|---|---|---|---|---|---|
| S0 conventional | 5.2 s | 16.5 s | yes | – | – | – | – |
| S1 15 s partial pulse | 5.2 s | 16.5 s | yes | 0.9 GJ | 112 MW | 0.5 t / none | none |
| **S2 field to 200 m** | 9.0 s | 24.2 s | **no** | 0.35 GJ | 67 MW | **3.5 / 3.0 t** | exhaust-free pickup; vertical landing on land (field 0.65 W + fans) |
| S3 field to 2 km | 9.0 s | 28.6 s | no | 3.2 GJ | 218 MW | 7.5 / 5.5 t | exhaust-free to 2 km; 7 t of water spare |

**Findings:**
- **A field climb at 1.5 W is slower off the ground than the torch.** It has to exceed 2.5 W to match the torch's exposure time.
- **Its value is the missing plume, not speed.** The torch at the surface puts MW/m² near its axis.
- **Hover is ideally almost free under M1,** because a static force does no work. Real hover cost is losses plus upkeep (unknown). The torch hovers at 1.4 t of water per minute; the fans carry 35% of weight.
- **The 14.3 m 8-couch variant closes hot extraction only under S3**, with a device of ≤ 4.5 t.
- **Environment:**
  - If the reaction is local rather than planet-wide, the footprint sees about 14 kPa. That is a 1.4 m dimple in water and a crush hazard to people underneath.
  - The torch at 200 m radiates 0.15–4.6 kW/m² to the ground, so it must be pitched away from people.
- The device ceilings above are **integration limits**, not predictions of what such a device would weigh.

## W3: a 50–100 m step
**The three boundary hypotheses:**
- **H1, the region sweeps through the air:** ordinary aerodynamics applies. 100 m in 1 s costs 3–44 MJ and is subsonic; in 0.1 s it costs 0.3–4.4 GJ and is Mach 3.
- **H2, interaction only at the departure and arrival boundaries:** ≤ 56–213 MJ per step (13–51 kg TNT equivalent), a sharp bang that scales with region volume. If the transition swaps the contents of the two volumes, the cost falls toward zero.
- **H3, needs a cleared operating volume:** in practice, vacuum only.

**Survival value:**
- A 50–100 m step completed inside the last 0.5 s defeats a 30 g interceptor's endgame. That interceptor can null only 37 m of offset in that time; an 8 g jink makes 10 m.

**Vacuum:**
- The environment term is zero.
- It supersedes canon technology limits (§18A, the ramp and path card), not invariants: a level step changes neither momentum nor energy.

**Energy ledger:**
- Field creation and recovery are unknown.
- Transition costs m·g·dz for vertical steps.
- The environment term depends on which hypothesis holds.

## Answers
1. **Smallest credible programmable-material capability:** adaptive camber/trailing structure that holds shape at 8 g, plus re-armable slam and crash absorbers, on a conventionally folded 17 m wing. Hot touchdown 43.3 m/s at 37.3 t dry. No new physics; flown morphing trailing edges are its precedent.
2. **Smallest metric effect that materially changes hot extraction:** about 1.5 × weight for about 9 s to 200 m (about 0.35 GJ source, about 70 MW peak), plus about 0.65 × weight to hover alongside the fans. This gives exhaust-free pickup and vertical landing on land, with a device budget of about 3.5 t. A brief partial pulse alongside the torch changes nothing.
3. **What must be resolved before a controlled metric displacement is plausible:** what the field boundary does to matter during a transition — carries or swaps it, pushes it aside, or fails. The same property decides whether a W2 field can start from a floating shuttle.

## Review response (2026-11-21, kT's assessment)
All four challenges are accepted.

1. **Reaction partner.** `w2_coupling.py/.json` bounds every known coupling for 0.9 MN at up to 200 m. None of them works:
   - Gravity would need about 2×10¹³ kg overhead.
   - A Lorentz force across Earth's field would need about 2×10⁹ A.
   - Electrostatic lift is capped by air breakdown at 40 Pa, against 13.4 kPa needed.
   - Inductive repulsion over seawater reaches only metres.

   So W2 is not an ordinary force. It is coherent only as an extension of the canon metric miracle (M2), which already licenses a declared nonlocal momentum partner (§7.1b). Outside M2 it would be a third miracle. Inside M2 it still needs:
   - a powered channel;
   - a generator about 4× lighter than the canon-scaled ~13 t (L²);
   - a boundary that tolerates water, air and people.

   The 0.35 GJ source figure is an *assumed* 60% efficiency, not evidence. Only the 0.18 GJ delivered to the shuttle is kinematics.
2. **Exhaust-free is not disturbance-free.** The claim is now limited to *no torch plume at the pickup*. Fan downwash, a local footprint (~14 kPa if the reaction lands locally), water displacement and boundary effects all remain. The "2 km" line is relabelled a screening assumption.
3. **Slam/crash credit withdrawn.** The reviewer is right that 25 g → 5 g needs 5× the stroke (0.05 → 0.25 m at 5 m/s). That stroke is not designed. The "rigid 25 g" baseline was also a strawman: a deadrise hull gets stroke from water penetration, and seaplane landing loads are a few g. What remains:
   - The bay envelope has 0.64 m clear below the belly, shared with the floats, where a deployable keel/step absorber could stow.
   - A 16 g crash at 15 m/s needs about 0.7 m of stroke.

   Both go to a small mechanical check before any credit is given.
4. **W3 is an advantage, not immunity.** The interceptor result assumes a head-on geometry and no reacquisition model. A level step keeps velocity and attitude, so the trajectory that follows is *offset*, not changed.
