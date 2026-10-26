# Wayfarer certification basis v0.2

ALL bodies. ALL sponsors. 2026-2226.

**Status: AGREED by Claude and Sol (2026-10-26); PROPOSED to kT. NON-GOVERNING.** This file says what "certified" means for Wayfarer v0.5. It changes no canon.
**Dates:** v0.1 2026-10-25; v0.2 2026-10-26 (G10 replaced by flight-dynamics tests). **Authors:** Claude (draft), Sol (review).

## 1. Goal (kT, 2026-10-24)

A fully certified Wayfarer that Claude and Sol both agree to: it meets flight-dynamics needs, has its major compartments and crew space defined, and has fully rendered images.

## 2. Scope decisions already made by kT (2026-10-24)

| Decision | Choice |
|---|---|
| Layout | Keep the v0.4 layout (C-shaped wrap-around tanks, bay in the midship; four longerons since v0.5.7). Departures from canon go to kT as a proposed canon amendment. |
| Shuttle | Rover-drop shuttle (TORCH150, biconic, Venus rover dropped from a cloud city): 27.9 t empty, 12.8 x 3.8 m. |
| People aboard | 6 crew (canon normal crew, unchanged) + 4 guest berths. |
| Images | Exterior stills, cutaways, deck plans, phone 3D viewer. |

## 3. Relationship to existing work

- The Wayfarer Flight System Qualification Plan v0.1 (2026-09-11, branch `engineering/wayfarer-flight-system-qualification-v1`) already defines Q1-Q7. This basis reuses its dispositions (BASELINE / CANDIDATE / QUALIFIED / REJECTED), its provenance classes, and where they exist its sizing points (Q4 RCS: 25 kN thrusters, 16-24 units, ~100 kN normal and ~200 kN abort translation, minute-class slews; Q7 dispatch: 150 t normal, 100 t minimum, 50 t protected optimizer reserve, one tank isolated = 25% loss).
- Gates G5 (structure), G6 (radiation), G7 (compartments), G8 (shuttle and bay), G11 (canon fit) and G12 (images) are new.
- Geometry authority stays as the repo states it: canon, then `geometry/wayfarer_geometry_seed.sql`, then the compiler, then renders. v0.5 hands Sol a parameter table in that form; renders are derivatives.

## 4. Rules

1. **Provenance on every number:** CANON, PUBLISHED_PHYSICS (with source), DERIVED, ENGINEERING_ASSUMPTION, FICTIONAL_CONSTITUTIVE_LAW, or OPEN.
2. **Data, not code:** every input and every pass threshold lives in a data file that is hashed and printed in the report (kT's standing no-hardcoding rule).
3. **No third miracle.** The torch is canon (mature D-He3 torch, CANON I §5.2). Its insides are not re-derived; certification checks its interfaces and states what the torch must deliver as declared interface requirements.
4. **One script decides.** A gate passes only when `certify.py` computes it from the record's inputs. Python 3 standard library only, so WALTER (loom-gate) can run it.
5. **Verdicts:** PASS; PASS-DECLARED (passes only because of a listed ENGINEERING_ASSUMPTION or FICTIONAL_CONSTITUTIVE_LAW, which kT must accept); FAIL; OPEN.
6. **No moving goalposts.** A threshold may not change in the same session that it failed. Any change is logged with a reason and needs both reviewers.
7. **Disagreement holds the gate.** A finding from either reviewer keeps that gate OPEN until it is fixed or withdrawn.

## 5. Mass states checked everywhere

Protected water (50 t) is always aboard.

| State | Remass | Shuttle | Hold |
|---|---|---|---|
| S1 reference departure | 250 t | docked | empty |
| S2 loaded departure | 250 t | docked | 50 t payload |
| S3 normal dispatch | 150 t | docked | empty |
| S4 burnt out, shuttle home | 0 t | docked | empty |
| S5 burnt out, shuttle away | 0 t | absent | empty |
| S6 full, shuttle away | 250 t | absent | empty |
| S7 one tank cell isolated | 187.5 t, uneven | docked | empty |

## 6. Gates

Thresholds marked (A) are authored engineering assumptions open to Sol's challenge before results are run.

### G1 Mass and fluids ledger (Q-plan mass closure)
- Component ledger sums to dry mass within 0.1 t; wet = dry + 300 t water + payload.
- Tank volume >= 315 m3 (300 t at 1 t/m3 plus 5% ullage).
- Every state S1-S7 reports mass, centre of mass (x, y, z) and full inertia tensor.
- Differences from the canon ledger (858.5 t dry, 1,158.5 t wet) are listed for G11.

### G2 Torch and reach (Q2)
- Torch card exhaust velocities unchanged from CANON II §14.
- ECON full-remass delta-v at S1 >= 95% of the canon card's ~729 km/s, i.e. >= 693 km/s (A: keeps Navigator's card valid within 5%).
- Acceleration at the canon cruise thrust (11.361 MN, 1 g at canon wet mass) >= 0.95 g at S1 (A).
- Remass for each state reported; the dispatch rules of Q7 apply.

### G3 Balance and attitude (Q4)
- Thrust trim: in every state the torch must point through the centre of mass with a nozzle vector angle <= 0.5 deg (A).
- Slew: 180 deg about the worst transverse axis in <= 120 s using 2 x 25 kN couples (Q4 sizing point), with intrinsic component inertias, not centroid-only.
- One RCS cluster out: still three-axis controllable.
- Shuttle undocking: the centre-of-mass jump is trimmable within the same 0.5 deg.

### G4 Power and heat (Q5)
- Metric HARD heat (CANON II §5 equivalent: 719 m2 at 900 K) is rejected at the design temperature with radiators inside their stowage and deployment limits.
- Habitat and avionics heat for 10 people is rejected by the habitat loop with margin >= 25% (A).
- Torch interface (PASS-DECLARED): non-exhaust torch heat reaching the ship <= the radiators' torch-burn capacity. The allowed fraction of jet power is stated as a torch interface requirement.
- Canon rule kept: no state needs a major torch burn and high Metric at once.

### G5 Structure and loads (new)
- Design load: 5 g axial (the HARD torch case the radiators are rated for) with ultimate factor 1.5 (A).
- Longeron stress <= allowable; longeron and shell buckling >= 1.5 x load.
- The bay cut-out: section stiffness with the slot open is computed; doors are not counted as structure unless designed as such.
- Tank wall holds hydrostatic head at 5 g plus ullage pressure.
- First bending mode >= 1 Hz (A: keeps it clear of attitude-control bandwidth).
- Material allowables are 2026 high-modulus carbon composite values, used as a conservative floor for 2226.

### G6 Radiation (new)
- Shadow shield: every inhabited volume, the shuttle bay and the docking collar lie inside the shield's shadow cone with >= 0.5 m margin.
- Storm shelter for all 10 people: >= 40 g/cm2 water equivalent in every direction (NASA: >= 20 g/cm2 vehicle shielding for missions over 6 months, plus 20 cm water for a 1-in-1000-year event), >= 2 m3 per person (A), 72 h life support (A).
- Galactic cosmic rays: annual dose reported at 2026 free-space rates (1.8 mSv/day measured in cruise by Curiosity) against NASA's 600 mSv career limit. Long-term crew protection depends on canon's off-Earth MED-MOD-RADIATION milestone, so this item is PASS-DECLARED or OPEN, never PASS.
- Torch neutrons and gammas (PASS-DECLARED): the attenuation the shadow shield must provide is stated as a torch interface requirement.

### G7 Compartments and crew space (new)
- 10 people: 6 crew + 4 guests.
- Net habitable volume >= 25 m3 per person (NASA long-duration guidance, 24-25 m3), so >= 250 m3 total. Target 45 m3 per crew member (the canon-candidate 270 m3 for 6).
- ~~A private quarter for every person >= 2.1 m3 (ISS crew-quarter class).~~ Changed by kT on 2026-10-25 (private cabins removed; Sol to agree as second reviewer): a cabin berth with 5 g restraints for every person, and at least 2.1 m3 of cabin volume per occupant.
- An acceleration couch for every person (HARD torch burns reach ~4-5 g).
- Decks perpendicular to the thrust axis; clear height >= 2.1 m (A).
- Two independent ways off every deck.
- Defined rooms: command, crew quarters, guest quarters, galley and wardroom, hygiene, medical bay, exercise, life support, stores, airlock and suit room, storm shelter, docking port, pressure-tight tunnel to the shuttle, custody locker for carried evidence (canon courier role).

### G8 Shuttle, drones and bay exit (new)
- Bay fits the shuttle with >= 0.25 m radial and >= 0.5 m axial clearance.
- Lateral departure path clears strakes, radiators and doors by >= 0.5 m (radiators stowed is an allowed doctrine).
- Pressure-tight crew transfer from the habitat to the shuttle (canon).
- Berths for >= 4 drones (canon: 4-12 per independent ship) and the rover's Venus kit.
- Shuttle refuel water is drawn from remass; the delta-v cost per trip is reported.

### G9 Failures and reserves (Q7)
- One of four radiator assemblies lost: reachable torch and Metric modes reported; the ship stays thermally safe.
- One tank cell isolated (S7): controllable (G3 trim limit) and the 25% remass loss shown.
- One RCS cluster lost: covered in G3.
- One longeron lost: the other four carry 1 g at limit load.
- Protected life-support water is never used for routine propulsion.

### G10 Flight dynamics: RCS, torch, Metric, Loom

Run by `g10/g10_flight_dynamics.py`, which `certify.py` calls. The tests
import main's `src/` modules; they do not copy them.

#### C. Card conformance
- The card names the geometry sha256 it was made from.
- The card's mass, CG and inertia match the geometry in every state
  (≤ 1% relative).
- The card's torch exhaust velocities and thrust by mode agree with the
  working card, `src/wayfarer_torch_mode_cards.py` (≤ 1%), which governs
  (kT, 2026-10-26).
- The ship runs no mode above its heat-rejection ceiling on jet power.

#### R. RCS
- 180° slews on roll, pitch and yaw settle in every state, within 240 s.
  - Main's controller and gates are used: 0.25°, 0.05°/s, 2 s hold.
  - Inertia and axis torque come from rev 5.
- 180° slews on all axes still settle with any one cluster out (state S2).
- Attitude is held against the torch's disturbance torque in every state and
  mode. The disturbance is thrust × lever × sin(trim + 0.5° error). It is
  held by the RCS, by declared torch thrust-vector authority, or both.
  - The 0.5° error is an ENGINEERING_ASSUMPTION, not a demonstrated
    disturbance history. Any TVC figure derived from it is conditional on
    that assumption; it is not a qualified nozzle capability.
- Translation on all three axes meets main's response law (0.16 s⁻¹) at
  main's test velocities.

#### T. Torch
- A time-stepped burn of the full usable remass in every mode:
  - integrated Δv agrees with the rocket equation within 0.1%;
  - peak acceleration stays within the crew cap (4 g) and the structural
    rating (5 g);
  - trim stays within the G3 limit as the CG migrates from S1 to S4.
- Interrupted burns are simulated: no burn segment longer than 2 h 45 min
  ([V2 6113]), with a coast between segments (15 min each, an
  ENGINEERING_ASSUMPTION). In free space the coasts change elapsed time, not
  Δv, so the Δv check above holds on the interrupted burn.

#### M. Metric
- The mode sequence is valid: prep, ramp, transport, collapse, NRE
  relaxation.
- Going from torch to Metric without a coast is refused.
- The cold load in every mode is within the cryoplant class.
- G4 rejects the heat of every mode.
- Ramp times are within canon's 10-30 s.
- **Not computed:** Metric Δv and remass (CANON II §20).

#### L. Loom
- The sequence is valid: Metric collapse, NRE relaxation, Loom formation,
  translation, arrival.
- Going directly from mid-field Metric to Loom is refused (not crew-rated).
- The E1 configuration lock (DOCKED / FREE / STOWED) is declared in the card
  or inputs. Each item passes only if it is declared; nothing is assumed:
  - shuttle docked in the translating states;
  - hot fins folded outside torch burns;
  - strakes stowed for Loom (a LOOM span entry of 0);
  - crown gores closed for Loom (named in the crown doctrine);
  - docking collar free of external attachments (a declared collar state).
  - This is a declaration check, not a dynamic lock.
- Torch Δv available at arrival, above the 50 t reserve, is reported.
- **Not computed:** Loom domain fit (PR #356, INDETERMINATE_NOT_CERTIFIABLE)
  and the natural transport map.

#### Follow-up validation (not gating)
- E1, FR-01B-R and MV-01 flown in Navigator, once fixtures, a card import and
  the §20 solver exist.

Replaces v0.1's G10 (Navigator flies E1, FR-01B-R and MV-01 to an arrival remass of at least 50 t), which could not be met: no executable mission fixtures, no ship-card import in Navigator, and CANON II §20 bars exact remass and delta-v outputs until a calibrated U^M_gamma and terminal solver exist. Agreed by Sol on 2026-10-26 after an independent rerun.

### G11 Canon fit
- Every departure from CANON II v2.4 and the v2.4a amendment is listed with its reason and proposed amendment text. Nothing is overwritten silently.
- Canon's normal crew stays 6; guests are carried people, not crew.

### G12 Images
- Every image is generated by script from the hashed v0.5 geometry file and stamped VISUAL REFERENCE with that hash.
- Set: exterior stills (at least 4 views), cutaways (at least 2), a plan of every deck, and a phone 3D viewer with parts that can be switched on and off.

## 6a. v0.5.2 additions (new hardware; no existing threshold changed)

- G4: light on the reactor's aft face at most 10 MW/m2 (ITER divertor targets, steady state); hot fins must carry the torch heat model's hot-structure load; strakes in torch burns must carry the magnet coils' cryo heat at the declared span.
- G8: no hot fin within 1.0 m of the slot edge lines on the +Z side (A).
- G9: with one hot fin lost the torch must still run at half power or more (A).

## 7. Sign-off

1. Claude runs `certify.py` and publishes the report.
2. A separate agent re-derives the key numbers without seeing the working.
3. Sol re-runs `certify.py` from the repository root (G10 imports main's `src/` modules) and reviews against canon: signs or lists findings.
4. loom-gate (WALTER) passes on the PR.
5. kT decides on the canon amendment. Sol then binds the accepted geometry into the governed seed and compiler chain.

**Certified** = every gate PASS or PASS-DECLARED, every declared assumption accepted by kT, both reviewers signed, loom-gate green.

## 8. Sources

- NASA OCHMO, Radiation Protection technical brief: 600 mSv career limit; >= 20 g/cm2 vehicle shielding for missions over 6 months; 10-20 cm water storm shelter for 1-in-100 and 1-in-1000-year events. https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf
- SwRI / Zeitlin et al. 2013, Curiosity RAD: 1.8 mSv/day in cruise. https://www.swri.org/press-release/swri-led-team-calculates-radiation-exposure-associated-trip-mars
- NASA NTRS 20180002051: 24 m3 habitable volume per crew member (Mars DRA5 guidance). https://ntrs.nasa.gov/api/citations/20180002051/downloads/20180002051.pdf
- IAC-19 A5.2: Defining the required net habitable volume for long-duration exploration missions. https://iafastro.directory/iac/archive/browse/IAC-19/A5/2/50308/
- Repo: CANON II v2.4 §5, §13, §14; Schematic Amendment v2.4a; Wayfarer Flight System Qualification Plan v0.1; Q4 Mass Properties/RCS v0.2; Q7 Dispatch Doctrine v0.1; Wayfarer Canon Candidate Specification v0.1 §6.
