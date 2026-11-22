# Weave shuttle: configuration (step 1) and closure screen (step 2)

ALL bodies. ALL sponsors. 2026-2226.

**Status:** Sol GO for steps 1–2 after bc0eeb5. **NON-CANON** until a CCR is approved by kT. No Wayfarer geometry, mass booking or released GLB changed. This is a rough geometric and mass screen, as briefed.

Code: `closure_screen.py` (→ `closure_screen.json`, `closure_stowage.npz`), `closure_figure.py` → `weave_closure.png`. Option check: `closure_options.json`.

## 1. Configuration (fixed per kT 2026-11-22; not redesigned)

| Item | Value | Basis |
|---|---|---|
| Host airframe | Explorer **#2643** hull (12.8 m, fit r 2.13 m, hull 76.6 m³, usable interior 63.8 m³), 6 couches | explorer_results.json |
| Structure | Osteon cautious (22% on eligible primary structure) | engine WILDCARDS |
| Wing | W1 programmable, 17 m span, 1.8 m chord, folds flat for the bay | proto/w1_programmable.py |
| Fans | 8 m² upper-surface blowing, 29 MWe reactor | #2643 |
| Floats | 30 m³ pop-out sponsons | #2643 |
| Tank | 23.1 t | lane W2 combination |
| Relational module | **8.0 t core** (kT) + **1.0 t install allowance** (mounts 0.3, cooling 0.4, power conditioning 0.3; ASSUMPTION) = **9.0 t** | Sol: honest accounting |
| Flywheel | **1.12 t** (cushion lift to 2 km: 3.35 GJ, 168 MW over 20 s, η 0.6), counted **once**, in dry mass | lane `cushion()` model, reproduced |
| Field | Weave shift + W2 cushion, R 15 m / wall 2 m | outings |

## 2. Closure screen

| Check | Value | Limit | Result |
|---|---|---|---|
| Dry mass | **48.99 t** (lane 47.97 + 1.0 t install allowance) | 52.5 t | ✓ (3.5 t margin) |
| Climb water, Earth and hot extraction with cushion lift | 22.3 t | 23.1 t tank | ✓ |
| Field-off Earth ascent, torch only | 25.8 t | tank + 5 t sprint kit | ✓ with kit; ✗ without |
| Field-off hot extraction, torch only | 35.6 t, thrust-short on the 2.5 g leg | – | ✗ (limitation) |
| **Interior volume** | usable 63.8 m³ | need 71.9 m³ (host 62.4 + module 8.4 + flywheel 0.56 + cooling 0.5) | **✗ −8.1 m³** |
| **Hull + floats ≥ 1.5 × displaced** | 106.6 m³ | 107.1 m³ | **✗ −0.5 m³** |
| Hull alone ≥ displaced | 76.6 m³ | 71.4 m³ | ✓ |
| **Field-off heavy water landing** (climb water aboard, ~1 m waves) | 51.2 m/s | 50 m/s (kT rule) | **✗ +1.2 m/s** |
| Field-off light landing (2 m waves) | 38.4 m/s | 40 m/s | ✓ |
| Stowed length / radius / exit width | 12.8 m / 2.13 m / 3.12 m rolled 86° | 12.8 / 2.15 / 3.8 m | ✓ (hull) |
| Field clears the actual host | max radius 6.6 m stowed, **8.55 m** wings and floats deployed | 10 m (= R − 2.5 d) | ✓; wing-tip differential carriage ≤ 0.8% (≈ 0.6 g at a 71 g jink) |
| Wayfarer thrust trim (G3) | – | ≤ 0.5° | **deferred**: needs a certify.py run with the booked shuttle mass and CG at step 5 |

**Interior volume basis.** The module's volume is taken at the density of Wayfarer's fore relational-plant block: 35.75 t in r 2 m × 3 m, i.e. 0.95 t/m³ (wayfarer_v05_inputs.json). With the 23.1 t tank, the host alone has only 1.4 m³ spare.

**Stowage.** Free space inside r 2.15 m and the 3.8 m exit width, in the rolled exit attitude:
- **Wing:** 99 m² of hull surface has ≥ 8 cm of clearance, 22 m² of it on the upper (leeward) surfaces. The folded wing needs ~23 m².
- **Fans:** about 54 m³ with ≥ 0.5 m of clearance, mostly around the tapered nose and upper deck, which fits four 1.6 m fan pods.
- **Belly:** nothing needs to ride on the heat-shield belly.
- **Verdict:** CONDITIONAL on the wing's conformal fold and on fan pods stowing on the upper deck. The mechanisms are not designed.

## 3. Conventional fallback (Sol: real capability; limitations documented, no miraculous failsafe)

**ASSUMPTIONS:**
- survivable vertical impact 10 m/s on water and 6 m/s on land;
- emergency torch lights in 1–3 s at full power (max 1.54 MN, net 1.15 g at lift-off mass);
- wing recovery = dive to the heavy minimum flying speed plus a 2.5 g pull-out.

**Field failure, by situation:**

| Situation | Outcome |
|---|---|
| Airspeed ≥ 51 m/s | Wings and fans take over immediately |
| Slow hover over water, ≤ 5 m up | Drop onto floats: survivable |
| Slow hover over land, ≤ 1.8 m up | Drop onto gear: survivable |
| Slow hover, 5 m (water) or 1.8 m (land) up to **19 / 47 / 92 m** (torch lights in 1 / 2 / 3 s) | **No recovery**: experimental limitation |
| Above that | Emergency torch arrests the fall |
| From hover, ≥ ~350 m | Wings alone recover (dive to flying speed, then pull out) |

**Field-off landings:**
- Field-off heavy water landings exceed the 50 m/s rule by 1.2 m/s.
- Field-off Earth ascent needs the 5 t sprint kit.
- Field-off hot extraction is not possible.

## 4. Conflicts for kT (not redesigned, per Sol's stopping condition)

**1. Interior volume, −8.1 m³ (real conflict).**

| Option | Effect | Cost |
|---|---|---|
| **a. Keep the 12.8 m bay; module takes the 6 m³ cargo well; couch allowance 3.5 → 3.15 m³** | Closes at ~0 m³ | No internal cargo well (courier cargo by kit or cabin space); tighter couches |
| **b. 14.3 m bay (option B), 6 couches** | Interior +3.0 m³ ✓, buoyancy ✓ | Dry 50.9 t (1.6 t margin); cushion climb water **24.2 t > 23.1 t tank** (needs a bigger tank, i.e. more Wayfarer remass, or the sprint kit); Wayfarer equipment move, +0.9 t structure, trim recheck |
| c. Declare a more compact module | – | Would mean inventing a Builder material specification (Sol: no); it does not close alone in any case |

**2. Buoyancy, −0.5 m³ (0.5%, marginal).** Floats 30 → 31 m³ (+0.03 t) closes it.

**3. Field-off heavy water landing, +1.2 m/s (marginal).** Two choices:
- **Procedure:** dump the climb water before a field-off ditching, which gives the light case, 38.4 m/s ✓. No hardware change.
- **Accept:** treat it as a limitation, with field-off heavy ditching only in seas calmer than ~1 m.

**Stopping condition met.** The selected configuration closes on mass, water, stowage (CONDITIONAL), field clearance and fallback (with documented limits). One real conflict (interior) and two marginal ones need kT's decision before the interior layout and the operating card.

## 5. Closure v2 (Sol revised direction after 34fc20c)

Code: `closure_v2.py` → `closure_v2.json`.

**Kept:**
- the 12.8 m #2643 airframe, 6 couches at 3.5 m³ and the 6 m³ cargo well;
- wings, fans, floats and torch;
- the 8 t module + 1.0 t install allowance;
- the lane's fast cushion lift (20 s) and its flywheel; the 23.1 t tank.

**Prototype assumptions (explicit; not established Builder properties):**

| Assumption | Accounting |
|---|---|
| Module packaging density **2–4 t/m³**: dense core plus a field network distributed in the hull wall | The distributed part thickens the wall *inward* and is charged to the interior; no mass reduced anywhere |
| Cooling integrated with the fan-reactor loop and the water tank as heat sink | 0.2 m³ hardware |
| Mounts and power | 0.1 m³ |
| **Floats 32 m³** (31 + 1 margin) | +0.06 t |
| **W1 programmable wing field-off CLmax uplift +5.1%** (5.0 → 5.26) | The minimum needed to keep the 50 m/s heavy-landing rule; no geometry change, so bay fit and field clearance are unaffected |

| Module density | Module volume | Interior residual at 12.8 m | Dry | Climb water (cushion) | Buoyancy | Heavy / light field-off touchdown |
|---|---|---|---|---|---|---|
| 2 t/m³ | 4.0 m³ | **−3.5 m³** | 49.06 t | 22.3 / 23.1 t ✓ | 108.6 / 107.2 ✓ | 50.0 ✓ / 37.5 ✓ |
| 3 t/m³ | 2.7 m³ | **−2.1 m³** | 49.06 t | ✓ | ✓ | ✓ |
| 4 t/m³ | 2.0 m³ | **−1.5 m³** | 49.06 t | ✓ | ✓ | ✓ |

**Closed by v2:** buoyancy, the field-off heavy landing, mass and water.

**Remaining contradiction: interior volume at 12.8 m.**
- Even at 4 t/m³ the module + flywheel (0.56 m³) + installation (0.3 m³) exceed the host's 1.4 m³ of spare volume by 1.5 m³.
- Closing it at 12.8 m by density alone would need ~15 t/m³, which is not credible.
- Trimming the tank and replacing the flywheel with slower reactor-fed lift would recover ~0.9 m³ but spend the water margin and slow hot extraction (not done).

**Smallest closing change:** stretch the parallel body **+0.22 m (13.02 m)** at 4 t/m³, or +0.32 m (13.12 m) at 3 t/m³.

| | 13.02 m (4 t/m³) | 13.12 m (3 t/m³) |
|---|---|---|
| Dry | 49.32 t | 49.45 t |
| Climb water (cushion) | 22.6 t ✓ | 22.7 t ✓ |
| Buoyancy | ✓ | ✓ |
| Field-off touchdown | ✓ (uplift 4.5%) | ✓ (uplift 4.3%) |
| Interior residual | +0.04 m³ | +0.17 m³ |

**Wayfarer side.** The nose port is fixed at x 18.75 (F7, HARD), so the stretch comes out of the **aft** docked clearance: 0.5 m (F9) → 0.28 / 0.18 m. That clearance is the room the shuttle needs to back 0.5 m off the port before rising (F11, HARD).

**Minimum useful Wayfarer modification:** a **~0.22–0.32 m retractable docking collar**. It withdraws on undocking, so the 0.5 m separation is collar retraction plus back-off. There is no remass, plant or trim-relevant change, but the docked aft clearance falls to 0.18–0.28 m. That needs kT to revisit the 2026-11-20 decision to keep the axial margin at 0.5 m.

**Alternative:** the 14.3 m bay (option B). It is much larger than needed.

**Stopping condition met.** Everything else closes credibly. One concrete contradiction, the interior volume at 12.8 m, needs kT's decision: hull stretch with the docking collar, the 14.3 m bay, or an explicit utility trade.
