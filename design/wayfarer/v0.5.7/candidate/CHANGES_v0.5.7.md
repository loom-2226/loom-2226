# Wayfarer v0.5.7 candidate (rev 3): crown dome, viewports everywhere, four longerons

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING SANDBOX.** No canon promotion, no runtime integration. Do not put the amendment in `canon/current/`. PR #430 stays as is. Let loom-gate run; no bypass.

**For comparison with v0.5.6.** The accepted v0.5.6 files are in `compare/v0.5.6/`. The viewer carries both versions behind a toggle.

| | v0.5.6 (accepted) | v0.5.7 (candidate) |
|---|---|---|
| Geometry sha256 | `14bb3c2c...629369` | `262b21a3...dda0` |
| Dry / departure (S1) mass | 867.7 / 1,167.7 t | 867.7 / 1,167.7 t (unchanged) |
| Worst thrust trim | 0.347° | 0.347° |
| Nose | 8 nose windows (Cupola-style cluster) | **Crown dome**, 25 m², Osteon frame and tambour gores |
| Pilots' view (forward sky / 60° cone) | 22% / 99.7% | **75% / 99.9%** |
| Longerons | 5 (3 flat planks outside the tank, 2 sills): 36.9 t, 65 MPa against 400 | **4 CFRP tubes in an X**, matching canon: 11.4 t, 211 MPa against 400 |
| Longeron joints | not counted | 3.5 t (8 end fittings, node-mount and hatch allowance, 4 bay-corner doublers) |
| Buckling between frames / first bending mode | 14.6x / 8.7 Hz | 23x / 5.0 Hz (need 1.5x / 1 Hz) |
| One longeron lost, 1 g | 10.9 MPa | 37.4 MPa |
| Engineering reserve | 42.6 t | **54.6 t** (33.5 t ledger + 21.2 t released from the longerons) |
| Tank volume | 322.6 m³ | 321.6 m³ (need 315) |
| Glazing | 15 windows, ~4 m² | **~48 m²**: crown dome 25 m², L2 viewport band 19 m², 22 round viewports. Every opening below the crown has an acrylic shield plug and a Strata shutter |
| Berth radiation screen (minimum) | 40.24 g/cm² | **40.75 g/cm²** (need 40) |
| Storm shelter screen | 55.1 g/cm² | 55.6 g/cm² |
| Gates | G1-G9, G11, G12 pass; G10 open | Same; two new G6 declared items await kT: `crown_dome` and `berth_viewports` |

## Rev 3: maximise viewports (kT 2026-10-25: "maximize viewports and take advantage of the specific tech ... for livability. They can be shuttered too")

The technology is what makes this possible:
- **Acrylic shield plugs** carry the armour's (and ring's or jacket's) g/cm², so an opening costs no shielding.
- **Osteon titanium frames** carry load round large openings.
- **Strata tambour shutters** close flush and stow in a lip, so nothing protrudes.

**L2 viewport band (the common deck).**
- A continuous panoramic band round 330° of L2, at standing and seated eye height (x 3.9-4.5 m). In the observation lounge it rises to 1.6 m tall (x 3.6-5.2 m). It skips only the washroom.
- It replaces the lounge's two 0.8 m windows and the rev 2 round viewports on L2. Glazed area: 19.4 m².
- **Mullions:** 23 Osteon titanium mullions, 5 x 20 cm, every 15°, forking into the sill and head beams. The worst load is twice the pressure end load (11.1 MN), giving 48 MPa against a 600 MPa allowable. Thrust: 5 g x 1.5 on the 64.8 t ahead, 4.8 MN. Buckling margin 4.4 on the 1.6 m lounge mullions. This is a new G5 check.
- **Panes:** curved with the hull, so they carry pressure as hoop membranes: 12.4 mm each needed, 16 mm assumed.
- **Shutter:** a Strata tambour band runs round the hull in a track and stows in the head beam.
- **Mass:** 4.34 t (225 kg/m²).

**Round viewports.**
- Berths: enlarged to 0.5 m (10). Each tier has 0.82 m of clear height.
- L4 medical: 2.
- **L4 storm shelter: 2.** The plug continues through the 20 cm water jacket as 17 cm more acrylic, so people sheltering for 72 h can see out without losing their screen.
- L5: suit room 1, workshop 2. The vestibule window stays. The 4 L1 shoulder windows stay.

**Shutters.** Every opening has one; one control in the viewer.
- **Closed** (cruise at speed, solar storms, torch burns, night): the hull reads as one smooth shell (`ext_closed`).
- **Open** (low speed, bow out of the dust flow): `ext_hab_viewports`.

**Heat.** With every shutter open, about 2.0 kW radiates through 48 m² of low-e glazing. Shutters close for night. Listed in G7.

**Count.** The crown, the band and 22 round viewports, against canon's suggested 10-16 windows. Amendment v2.4e asks kT to lift the limit.

## 0. Crown dome replaces the nose windows (kT 2026-10-25: "incorporate the crown viewport design into main design")

Source: `command/BOW_OPTIONS_STUDY.md`, option C. Inputs: `habitat.decks[L1].command_layout.crown_dome`. The 8 nose windows are kept in the inputs for comparison, but they are no longer built.

- **Glazing:** 25 m² inside the sensor ring (r ≤ 2.8 m).
  - Panes: flaw-controlled transparent ceramic, a 2226 extrapolation of ALON. Two 6 mm pressure panes, each carrying full load, plus an 8 mm debris pane and a 3 mm scratch pane: 85 kg/m².
  - About 1.5 m segments, plus a clear 2.3 m centre pane where the pilots look.
- **Frame (Osteon, Builder-derived OST-22):** 8 graded titanium roots spring from the brow ring and fork once into 16 flat blades, 3-7.5 cm thick, set edge-on to the pilots, landing on a slim ring round the centre pane.
- **Brow ring:** a smooth band, about 22 cm high and 1 m wide, round the rim. It holds the roots and the 16 retracted gores.
- **Gores (Strata laminate tambour, Builder-derived MHL-22):** they run on meridian tracks and close flush in the armour opening, restoring its 27 g/cm². When open, nothing protrudes outside the glass and the ship's outline never changes (good for Loom configuration). The gores carry the armour the opening removes, so they add no new mass.
- **Mass:** 4.93 t from the reserve: panes 2.13, frame 1.8, brow ring 0.5, tracks and drives 0.5. This replaces the 1.85 t nose cluster (net +3.08 t).
- **Doctrine:** open only at low speed, or with the bow facing away from the dust flow (braking and tail-first coasting). Closed for solar particle events, radiation belts and torch burns. Stuck closed is safe; stuck open means turning the bow out of the dust flow. With the gores open, L1 loses the armour over the crown (glass gives 2-9 g/cm²). L1 is not a shelter.
- **Views (L1 study, 12/12 checks):**
  - pilots: 99.9% clear across 60°, 75% of the forward sky (nose windows: 22%);
  - crew standing at 1 g: 89% of the overhead cone;
  - support couches: unchanged, about 8%, because the sensor ring blocks the shoulder.
- **Pilot displays** now ride on arms from the flight deck instead of hanging from the nose.
- **Declared, awaiting kT:** `crown_dome` (G6).
  - Ceramic panes up to 2.3 m (today's largest is about 0.76 m): a materials milestone like the 1,750 K fins.
  - The Strata gores.
  - The operating rule.
- **The ship's look:** closed, the crown reads as a smooth striped cap (`ext_hero`); open, it shows a leaf-veined skylight (`ext_nose`). Nothing round and dark sits at the front at cruise speed.

## 1. Four longerons, sized (structure)

Source: `structure/longeron_study.py` and `LONGERON_STUDY.md`, asked for by kT on 2026-10-25.

- **The members.** Four CFRP tubes, 0.40 m across with a 72 mm wall, run x 14-34.3 m. The upper pair sit where the v0.5.6 sills were, edging the bay slot. The lower pair mirror them in the tank's lower cells. This matches canon's "4 axial longerons", so the five-longeron departure leaves the proposed amendment.
- **Why they could shrink.** The v0.5.6 members ran at 65 MPa against 400, so nothing checked was setting their size. They are now sized at 5 g x 1.5 to a 250 MPa design stress: the 400 MPa floor times 0.62 for impact, joints and environment. G5 reads 211 MPa because its part masses include the reserve spread.
- **Joints are now counted.** Conventional 2026 masses:
  - 8 titanium end fittings, at the habitat ring frame and the thrust cone;
  - a 20-unit allowance for node mounts and access hatches;
  - 4 bay-corner doublers.
  - Osteon (Builder OST-22) joints would save another 0.8-1.4 t. They are **not** assumed.
- **Mass.** The structure line is unchanged. 21.2 t of the longeron share is released to the engineering reserve and spread like the reserve.
- **Twist:** carried by the tank's closed cell (G5 torsion mode 3.8 Hz). The 0.8 m of open slot aft of the tank is bridged by the tubes.

**Found during integration:**
- **The node mounts can't sit on the longeron lines.** The lines (43.4°) lie under the stowed strakes (40° ± 12.7°). The allowance stands, but the mounts go on ring frames in the clear arcs (beam and keel) and tie into the longerons through the frames. **Sol to place them against PR #184.** For the same reason, the "service bands" in the longeron study are not in this build.
- **The v0.5.6 planks were also radiation shielding.** They screened the berths' aft, outboard rays. Without them, the weakest berth ray (crew cabin B, 311°, running aft through the service section) fell from 49.1 to 39.97 g/cm². A 0.6 t polyethylene band in the service section (x 14-17, r 4.30-4.36) restores the berth minimum to 41.06 g/cm². After the crown and the habitat viewports drew on the reserve, it is 40.92 g/cm².
- **The strake clash is gone.** The 0.40 m tubes clear the strake roots, so the strake-root housings proposed in the study are not needed.

## 2. Berth viewports (habitat)

Source: `habitat/berth_viewport_figure.py`. kT 2026-10-25: "my biggest design choice with that spacecraft's livability feature."

- **Where:** one 0.35 m viewport at the outer end of every berth, just above the mattress. 10 in all, two tiers where berths are stacked.
- **How it keeps the shielding:** acrylic plugs.
  - A 23 cm plug fills the splayed armour opening: 27.1 g/cm² against the armour's 27.0.
  - A 7 cm insert replaces the berth ring's water: 8.3 g/cm² against 8.0.
  - So the berths stay storm-shelter grade with the shutter open. The external shutter only handles dust, glare and heat, and closes at cruise speed like every window.
- **More habitat viewports (kT: "...and in the habitat").** Six 0.45 m viewports with the same kit: L2 wardroom 2, galley 1 and exercise 1; L4 medical 1; L5 workshop 1. The existing shoulder, lounge and vestibule windows also take acrylic plugs, so every window below the crown is shielded. Mass: 0.51 t.
- **Mass:** 0.8 t of berth viewport assemblies, 0.51 t of habitat viewports, 0.6 t for the band and 4.93 t for the crown, less the 1.85 t nose cluster: ledger line `crew_systems_v057_t` = 9.16 t after rev 3, all from the reserve.
- **Declared, awaiting kT:** `berth_viewports` (G6). The g/cm² is shown; the dose is not. Acrylic is about 8% hydrogen by mass against water's 11%, so a transport check may ask for a thicker plug. Acrylic is also flammable, so it is encapsulated and needs a fire-load entry.
- **Window count.** The canon candidate suggests 10-16 windows. v0.5.7 has the crown dome plus 23 windows and viewports, and amendment v2.4e proposes raising the limit. **kT's call.** The L1 check is now "at least 10".
- **SOL TO AGREE:** this changes his berth ring.

## 3. Concepts (not in the build)

The crown dome was a concept here; it is now the main design (§0). Its concept images are kept in `docs/concepts/`.

- **Bow and spine options** (`docs/concepts/wayfarer_bow_spine_options.jpg`): today's bow, a "don't" (hoops), four external spines, and a visor. These are sketches. The real longerons are internal, so any external spine is styling.

## 4. Viewer

`render/out/wayfarer_v05_viewer.html` carries v0.5.6 and v0.5.7 behind a **Version** toggle, with stats showing the v0.5.6 value wherever it differs. It adds a **Structure** mode (longerons in amber, ring frames, thrust cone) and **Dome open / closed** in every mode except *Habitat decks* and *Structure*. *Command deck* uses the crown, with look-around from each station and standing at 1 g. *Habitat decks* shows the viewports. Switching to v0.5.6 brings back the nose windows.

**New or changed stills:**
- New: `ext_viewports`, `ext_hab_viewports` (all open), `ext_closed` (all closed), `structure_v057`.
- Now the main design: `crown_open`, `crown_closed`, `crown_standing`.
- Updated for the crown: `ext_nose`, `cmd_pov`, `cmd_cutaway`, `ext_hero` (dome closed).
- Relabelled: `cut_mid`, `hab_crew`.

## For Sol

1. **Review:**
   - the four-longeron layout and sizing (`structure/longeron_study.py`, G5);
   - the service shield band;
   - the berth viewports (his berth ring);
   - the crown dome: `command/l1_study.py` now scores it, and the pilot displays move to flight-deck arms.
2. **Place the 20 node mounts** against PR #184. They go on frames, off the strake lines.
3. **Still open from v0.5.6:** berths 2.10 x 0.70 m, medical opening at 202°, floor-edge collar, the G7 berth-per-person rule.
4. **Fly G10** with `out/wayfarer_v05_card.json`. The card is unchanged from v0.5.6: same mass and the same 4 g cap.

Re-run everything with `./run_all.sh`.
