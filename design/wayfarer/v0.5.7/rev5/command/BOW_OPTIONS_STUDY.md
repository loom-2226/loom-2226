# Wayfarer L1 bow options: how much sky can we give the crew?

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING STUDY, 2026-10-25. Option C (crown dome) was adopted into the v0.5.7 candidate as the main design on kT's instruction; see `CHANGES_v0.5.7.md`.** Answers kT's brief "Wayfarer Panoramic Command Deck", with the changes agreed before it ran. Baseline: the v0.5.6 package (geometry `14bb3c2c...`), which this study does not change. Numbers come from `command/l1_bow_options.py` (results in `l1_bow_options_results.json`): rays from the six couch eyes and four standing eyes, with the real obstacles (sensor ring, flight deck and its columns, couches with occupants, displays).

## 1. Answer in one paragraph

A mostly transparent bow is physically reasonable by 2226 for the pressure job, but not for the debris job.
- **Pressure:** curved transparent ceramic panes carry cabin pressure well. At realistic stresses the pressure panes are about 6 mm thick each.
- **Debris:** in the ram direction at cruise speed, interplanetary dust arrives at tens of kilojoules per grain. No credible glass stops that, so the glass must be closed behind armour whenever the bow faces the flow at speed.

The best design glazes the **crown of the bow inside the sensor ring** (25 m², option C) on a Builder-grammar (Osteon) frame, closed by Strata tambour gores that retract into a brow ring. Pilots go from 22% to 76% of the forward sky. Crew standing on L1 at 1 g cruise go from 2% to about 47% of the sky above them: a sky ceiling over the working deck. It costs about 3 to 6 t of the 42.6 t reserve, and needs one materials step: transparent ceramic panes about 2 m across, roughly three times today's largest.

Glazing the whole bow (option B) gives the support couches a real view too, but only if the 8.4 t sensor ring leaves L1. It also needs 4 m petals that fold over the forward thrusters.

## 2. The three options, on numbers

Share of the forward hemisphere (the half of the sky toward the bow) that each person sees directly:

| | A: v0.5.6 windows | B: panoramic bow | C: crown dome |
|---|---|---|---|
| Glazing | 8 nose + 4 shoulder windows, 2.7 m² | 64 m², to the shoulder | 25 m² inside the sensor ring, plus the 4 shoulder windows |
| Pilot and navigator | 22% | 72% | **76%** |
| Support couches S1-S4 | 2% | 58% | 8% |
| Standing on L1 at 1 g (sky overhead, 90° cone) | 3% | 89% | **89%** |
| Standing on L1, whole forward hemisphere | 2% | 79% | 47% |
| Sensor ring | stays | **must leave L1 (8.4 t)** | stays |
| Added mass (2226 ceramic, 2026 fused silica) | 0 | +9 to +17 t, plus moving the sensors | **+2.7 to +5.8 t** |
| Shutters when open | none | ~4.3 m petals over the forward thrusters | gores stowed in the brow ring; nothing outside the glass |

Notes:
- **A** includes the armour bore (12° splay). The 22% here is measured over the whole forward hemisphere on a uniform grid; the 32% in the L1 study was measured differently.
- **C's frame is laid out around the pilots.** An Osteon frame: 8 graded roots spring from the brow ring and fork once into 16 thin blades that land on a slim ring round a clear 2.3 m central pane. The blades are flat, 3-7 cm thick, and set edge-on to the pilots, so both pilots' 60° cones stay clear. Scored with 8 cm blades to stay conservative.
- **The pilot displays** hang from the dome in v0.5.6. In C they would move to arms on the flight deck.

## 3. Materials: what's real and what's speculative

| Tier | What it is |
|---|---|
| Established physics | Glass and transparent ceramics fail by brittle fracture from their largest flaw, so strength falls with size and with sustained load in moist air (static fatigue). Impact energy rises with the square of speed. |
| Demonstrated (2026) | **ISS Cupola:** 7 windows, 80 cm top window, four panes (debris, two 25 mm pressure panes, scratch) of fused silica and borosilicate, Kevlar/Nextel shutters, 1.88 t. **ALON:** 700 MPa flexural strength, toughness 2.0-2.4 MPa·m½, density 3.69 t/m³, panes to about 0.5 x 0.76 m. Crewed pressure structures use an ultimate factor of 3.0 and a proof test at 2.0 x pressure. |
| Reasonable extrapolation (2226) | Flaw-controlled transparent ceramic segments about 1.5-2.5 m across, proof-tested and inspected. Design stress about 70-200 MPa. Two independent pressure panes each carrying full load. Embedded crack sensing. |
| Highly speculative | Glass that survives hypervelocity dust; self-healing panes; monolithic domes several metres across. **None of these is assumed.** |

Pane sizing at the bow crown (radius of curvature 8.6 m, cabin pressure 101 kPa). The stack is two pressure panes plus an 8 mm debris pane and a 3 mm scratch pane:

| Material | Design stress | Each pressure pane | Stack | kg per m² |
|---|---|---|---|---|
| Fused silica, 2026 | 10 MPa | 44 mm | 98 mm | 216 |
| ALON, 2026 | 70 MPa | 6 mm | 23 mm | 87 |
| Flaw-controlled ceramic, 2226 | 200 MPa | 6 mm (handling minimum) | 23 mm | 85 |

The 10 MPa and 200 MPa design stresses are illustrative bounds, not material data.

What this means:
- **Curved panes carry pressure as a membrane**, which is far more efficient than the flat Cupola panes, which carry it in bending.
- **Panes are not the mass problem.** In 2226 the mass sits in the frame, the shutters and their drives.
- **Panel count:** neither "a handful of enormous panels" nor a fine grid is best. Use one large central pane where the pilots look, and about 1.5 m segments elsewhere, so a single crack loses one segment, not the dome.

## 4. Environment: what glass can and can't handle

**Dust is the hard limit.** This uses the Grün (1985) flux at 1 AU, which assumes 20 km/s, scaled to a ram-facing pane:

| Grain | Energy at 300 km/s | Hits per year on a 25 m² dome at 300 km/s |
|---|---|---|
| ≥ 1 µg (90 µm) | 45 J | ~570 |
| ≥ 0.1 mg | 4.5 kJ (rifle-bullet class) | ~4 |
| ≥ 1 mg | 45 kJ | ~0.2 |

- **At low speed it's benign.** At 20 km/s (planetary orbit, rendezvous) a ram-facing pane loses about 0.002% of its clear area a year to pitting.
- **At speed, the panes are closed in the ram direction.** The tambour gores restore the armour (27 g/cm²).
- **Direction is the lever.** At 300 km/s, dust moving at about 20 km/s cannot catch the trailing side of the ship, so a surface facing away from the flow sees almost no hits.
  - **Braking burns** fly tail-first, so the bow trails the flow and the dome can be open while braking. The view is then backward, toward where the ship came from.
  - **Coasting tail-first** puts the shadow shield into the flow as a dust shield. The magnetic nozzle and folded radiators would then also face the flow; that needs checking before it becomes doctrine.

**Radiation:**
- **Cosmic rays:** the hull barely changes cosmic-ray dose (G6's accepted declared item), so open glazing adds little.
- **Solar particle events:** these still go to the storm shelter, which is unchanged.
- **Radiation belts** (Jupiter and similar): dome closed.
- With the dome open, L1 loses the 27 g/cm² armour over the crown; the glass stack gives 2-9 g/cm².

**Light and heat:** glare and solar heating are handled with coatings and partly closed gores; the inner scratch pane carries the coating. Thermal cycling is a seal and frame design problem, not a showstopper.

## 5. Shutters: Astra's leaves versus tambour gores

**Astra's concentric rotating leaves** solve coverage geometrically, but:
- the leaves are 8-34 mm thick, and its own README says they are not armour;
- the stowed stacks reach r 5.06 m even when closed;
- the polar bearing sits in front of the pilots.

**Strata tambour gores in a brow ring (option C, revised after the petal version looked like a sandworm):**
- **The brow ring** is a smooth raised band (about 22 cm high, 1 m wide) round the dome's rim. It carries the frame roots and houses the shutters.
- **16 tambour gores** of Strata laminate slats run on meridian tracks, like a roll-top desk. Closed, they meet over the crown and sit flush in the armour opening, restoring its 27 g/cm². Open, they retract into the brow ring, so **nothing sits outside the glass and the envelope never grows**.
- **Mass:** the gores carry the armour the crown loses (about 6.8 t), so they aren't new mass; tracks and drives add about 0.5 t.
- **Grounded mechanism:** slats short enough to follow a doubly curved track, as tambour doors and camera irises already do. The Strata laminate is what makes armour-equivalent slats thin enough to stow.

**Failure states:**
- **Stuck closed** is safe; you only lose the view.
- **Stuck open:** nothing protrudes, so burns are unaffected, but the glass is exposed. Turn the bow away from the dust flow or limit speed until it is fixed. A single jammed gore leaves one 22.5° wedge open.
- **Maintenance:** gores and panes are replaced from outside during EVA, segment by segment.

## 6. People: what the crew actually sees

- **Above 1.5 g** everyone lies on their back facing the bow. The pilots' view is the one that matters for flying, and C gives them 76% of the forward sky, with no ribs inside their 60° cones.
- **At about 1 g cruise** people stand on the L1 floor and the bow is overhead. That is a sky ceiling over a working deck: about 89% of the overhead 90° cone is open sky from anywhere on the walkways. It is the main human-experience gain.
- **The support couches stay limited (8%)** because the sensor ring blocks the shoulder. Their direct views come from the four shoulder windows and the L2 observation lounge.
- **Comfort:**
  - partly closed gores give shade and privacy;
  - dimmable cabin lighting keeps the dome dark for viewing;
  - a closed-dome "night" mode helps rest at 1 g.

## 7. Recommendation

1. **Adopt option C (crown dome) as the bow concept to develop.** It delivers most of the experience at a small cost: pilots 22% to 76%, standing crew 3% to 89% overhead, +3 to +6 t from the reserve. It keeps layout D's couches, eye points, flight deck and sensor ring unchanged.
2. **Keep B as the 2226 stretch**, only if the sensors can leave L1 (for example, in the brow ring or aft of the habitat). Without that, the extra glazing is mostly hidden behind the ring.
3. **Separating observation from command** is achieved by mode, not by a second room. In C the same crown serves the pilots under thrust and the whole deck at 1 g, and the gores decide when it is safe.

**The smallest set of speculative steps:**
- **one materials step:** proof-tested transparent ceramic panes about 2 m across (today about 0.76 m);
- **one engineering item:** armour tambour gores with tracks, drives and seals in the brow ring (tambour mechanisms are 2026-class engineering; the Builder-derived Strata laminate makes the slats thin enough);
- **one operating rule:** glazing open only at low speed or facing away from the dust flow.

## 8. What C still needs before it could enter the design

- Frame and pane sizing.
- Gore tracks, drives and seals; the slat-to-track fit on a doubly curved surface.
- Pilot displays moved onto flight-deck arms.
- A dose check for L1 with the dome open.
- A tail-first coasting check: dust on the magnetic nozzle and folded radiators.
- kT's acceptance of the ceramic-pane technology milestone, as was done for the 1,750 K fins.

Sources: [ISS Cupola](https://en.wikipedia.org/wiki/Cupola_(ISS_module)), [ALON properties (Surmet data)](https://www-eng.lbl.gov/~shuman/NEXT/MATERIALS&COMPONENTS/Quartz/ALON.pdf), [Glass and window design factors (ECSS/SSP)](https://www-eng.lbl.gov/~shuman/NEXT/MATERIALS&COMPONENTS/Quartz/suprasil_fatigue_esa.pdf), [Grün interplanetary flux model (ESA)](https://space-env.esa.int/madweb/hmodels.php).
