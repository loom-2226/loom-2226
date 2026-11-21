# Weave shuttle: operating card (step 3)

ALL bodies. ALL sponsors. 2026-2226.

**Status:** experimental prototype, **NON-CANON** until the CCR is approved by kT. Preliminary design level (steps 1–2 accepted by Sol). For Sol review before CCR scoping.

**Labels:**
- **D** = DERIVED in this lane's models (cited);
- **A** = operating or design ASSUMPTION;
- **U** = UNKNOWN (research mystery).

Numbers are for the selected configuration unless marked "test hull" (the 20 m outing hull).

## The vehicle

A 13.02 m Osteon lifting body with three ways of moving.

| Item | Value |
|---|---|
| Crew and cargo | Six couches and a 6 m³ cargo well |
| **W2 cushion** | Cancels gravity inside its field: weightless cabin, powered hover, vertical lift |
| **Weave shift** | Carries the whole shuttle, its air included, through space; very high coordinate acceleration with modest occupant loading |
| **Conventional flight** | 17 m programmable wing (W1), 8 m² blown-flap fans (29 MWe reactor), 7.7 GW torch to orbit, 32 m³ pop-out floats |
| Field size | R 15 m sphere, 2 m wall, centred on the shuttle; the whole vehicle stays within 8.6 m of centre, wings and floats out (D, closure) |
| Mass | 49.3 t dry (8 t relational module + 1 t installation + 1.1 t flywheel); 23.1 t tank |
| Docking | Nose port; retractable collar on Wayfarer (design direction; demonstrated at step 5) |
| Interior | Closes provisionally (+0.04 m³); final hull length set at step 5 within 13.02–13.12 m |

## What it can do

**1. Lift off vertically with no downwash** (W2 cushion)
- Hover in air: air speed ≤ 0.16 m/s, pressure shift ~140 Pa; nothing blown around (D, linear compressible air).
- Vertical lift to 2 km in ~20 s: ~3.35 GJ from the flywheel at up to 168 MW. Height is paid for (A, lane cushion model).
- The cabin is weightless throughout cushion flight.

**2. Move like nothing else** (Weave shift)

| Manoeuvre | Peak | Felt by occupants |
|---|---|---|
| 200 m dash in 3 s | 125 m/s, 13 g | ~0.02 g (D, test hull) |
| 30 m sidestep in 0.5 s | 112 m/s, 71 g | ≤ ~0.7 g (D, test hull); actual host wing-tip differential ≤ 0.8% → ~0.6 g on the wing tips (D, closure) |
| 30 m sidestep in 0.4 s | 110 g | ~1 g (D) |

- **Quiet in calm air:** the shuttle carries its own pocket of air. No airflow over the hull, no wake left behind, no compression (D, exact ideal-fluid result). Air is displaced, not stirred.
- **Quiet limit:** the field edge stays subsonic while peak speed is below ~140 m/s, i.e. ≥ 0.4 s per 30 m (D).

**3. Fly and float as a conventional spacecraft**
- Water and runway landings: heavy (climb water aboard) ≤ 50 m/s in ~1 m waves; light ~37.5 m/s in 2 m waves. Uses the W1 lift uplift (A).
- Atmospheric entry as a lifting body: ~1,160 km crossrange, ~2.2 g, ~263 W/cm² peak (D, host #2643 explorer record).
- Orbit: cushion lift to 2 km, then a 1.4 g torch climb; Earth and hot extraction each need 22.6 t of the 23.1 t tank (D).
- Floats 32 m³: buoyancy ≥ 1.5× displaced at full load (D).

**4. Work in weather, on the ground and on the water**

| Setting | Behaviour |
|---|---|
| Wind 10–15 m/s | Blows straight through the field; only the hull feels it; crew 0.008–0.018 g (A, hull area) |
| Rain | Stops falling inside the field: drops halt within ~1 m and drift through with the wind; dry patch under the craft (D, estimate) |
| Landing on ground | Inside the footprint, loose ground, puddles **and people** go weightless; dust lifts with any breeze; the field edge presses the surface down by up to ~3.3 g in a ring (D, estimate). Ground crew stay outside 15–19 m |
| Hover over calm water | Pulls the sea into a bowl beneath the craft: 5.6 m deep and ~35 m across with the field centre 10 m up; nothing above ~19 m (D, static). Forms in ~1–2 s; after a jink the old pit rebounds while a new one opens (D, coarse estimate) |
| Skim | Clean above ~19 m (field centre). Lower skims plough the sea (74 MJ at 10 m) (D, kinematic) |
| Water exit / entry | Leaves the sea inside a ball of seawater (~8.9 kt on the test geometry; release ≈ 2.3 GJ splash); dives inside a ball of air. Violent, visible, ~2.7 GJ per crossing (D, kinematic) |

## Transitions

- **Cushion → wings:** at ≥ ~50 m/s airspeed the wings carry the shuttle; the field can be switched off (D).
- **Cushion → torch:** above the cushion ceiling (~2 km in this profile), the torch climbs at 1.4 g (D).
- **Shift + cushion:** run together near a planet. The cushion holds the shuttle up, the shift moves it. The shift alone cannot hover for long (~14 s before the field edge goes supersonic) (D).
- **Field off on the ground:** Earth ascent on the torch alone needs the 5 t sprint water kit; hot extraction needs the field (D).

## How it looks to others (sensor signature)

| Sensor | Signature |
|---|---|
| Radar | Sees the hull's true track and speed (Doppler ray-traced through the field); the field itself is invisible to radar (D, one head-on geometry) |
| Optical | The field bends light ≤ 2e-12 rad, so it is invisible (D, one side-on geometry). The only optical trace is faint shimmer from moved layered air, 1.7–6.5 µrad: below the eye, within reach of schlieren instruments (D) |
| Overall | A solid object doing 71–110 g with no plume, no rotor wash and no sonic boom while the field edge is subsonic. Water operations are highly visible |
| Thermal | **U**: depends on how much of each manoeuvre's borrowed energy (~0.5 GJ per sidestep) is lost as heat |

## Limits worth knowing

**Field failure** (estimates; no magic failsafe):

| Situation | Outcome |
|---|---|
| Airspeed ≥ ~50 m/s | Wings take over |
| Slow hover ≤ 5 m over water | Drop onto floats: fine |
| Slow hover ≤ ~2 m over land | Drop onto gear: fine |
| Above ~19 / 47 / 92 m (torch lights in 1 / 2 / 3 s) | Emergency torch recovers |
| Slow hover between those heights | **No recovery**. Experimental limit: such hovers are flown knowingly, not forbidden |

**Design rule (D):** the field edge must never cut the hull. The selected shuttle stays 1.4 m inside the clean zone.

**Unknowns (U):**
- the energy–momentum exchange (conservation retained);
- heat per manoeuvre, which decides how many sheddable heat sinks a dodge uses;
- behaviour with the field edge supersonic (fast hops, thin walls);
- real-sea breaking and foam;
- non-symmetric gusts.

## Sources (lane reports, `weave/` and `weave_final/`)

| Topic | Report |
|---|---|
| Cushion in air, landing, lapse correction | `WEAVE_OUTINGS_2026_11_22.md` §3, `outing_landing.py` |
| Dodge, sensors, transmedium | `WEAVE_OUTINGS_2026_11_22.md` §1, §2, §4 |
| Water bowl and its dynamics | `WEAVE_NIMITZ_VIEW_2026_11_22.md` §1, §5 (physics only; no AP use here) |
| Ideal-fluid transport, gusts | `WEAVE_SHIFT_FLUID_2026_11_21.md`, `WEAVE_SHIFT_GUST_2026_11_21.md` |
| Configuration, mass, stowage, fallback | `WEAVE_SHUTTLE_CONFIG_AND_CLOSURE_2026_11_22.md` |
| Exchange physics status | `WEAVE_SOURCE_CLOSURE_2026_11_22.md` §6 (prototype disposition) |
