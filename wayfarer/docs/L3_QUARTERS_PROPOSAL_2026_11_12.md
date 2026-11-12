# Wayfarer L3 Quarters: organic Japandi furniture proposal (12 Nov 2026)
**ALL bodies. ALL sponsors. 2026-2226.**

**Status:** kT APPROVED the layout on 12 Nov 2026. The 3D model is FOR REVIEW. Claude designed it in the approved L2 language. Not built. This is a rule F4 proposal package. Canon, BRep, mass and the exterior are unchanged. D9 has not been run.

Berths, doors, walls and windows are taken unchanged from `wayfarer_v05_inputs.json` (L3 deck) and the source geometry. Mass rule: `room_register_2026_11_12` (each room's booking pays for its own furniture).

**Source:** `wayfarer/lab/l3_quarters/` (`l3geom.py`, `export3.py` and `run3.py`, using `../l2_organic_study`).

**Output:** `render/out/proposal_L3_quarters.glb` (21 nodes).

![plan](L3_QUARTERS_PROPOSAL_2026_11_12_plan.png)
![section](L3_QUARTERS_PROPOSAL_2026_11_12_section.png)

## Hatch interface (kT decision 12 Nov 2026)
The L2/L3 hatch flaps built in PR #526 hang into L3 at h 1.68–2.30 m. That puts them in front of the guest-cabin door (195°) and the crew-washroom door (345°). Their corners also reach r 1.945 m, about 2 cm into the upper guest berth's head end.

**kT decision:** flip the L2/L3 leaves so they open **upward into L2**. Parked open, each stands 0.92 m tall in L2 beside the ladder opening and acts as a guard rail. L3 then has no flaps. The mass and booking are unchanged; Sol re-runs D9. This model assumes the flip.

## Items and mass (estimates, including berths)
| Cabin / room | Items | Est. | Booked |
|---|---|---:|---:|
| Captain (1) | Berth pod, wardrobe with secure stowage, fold-down desk with secure terminal and docked seat, visitor seat | ~260 kg | 461 kg |
| Crew A (2) | Two-tier berth, 2 lockers, fold-down desk and seat | ~345 kg | 921 kg |
| Guest (4) | Two two-tier berths, 4 lockers, racetrack table and 2 docked seats | ~620 kg | 1,843 kg |
| Crew B (3) | Two-tier and single berths, 3 lockers, fold-down desk and seat | ~465 kg | 1,382 kg |
| Guest washroom | Toilet pod, shower cabin, basin | ~215 kg | 614 kg |
| Crew washroom | Toilet pod, shower cabin, basin | ~215 kg | 614 kg |
| Deck-wide (outfit_L3) | Lining, cove, lighting, overhead rail | ~145 kg | 819 kg |

- **Berth pods:** source tiers (frame 0.14, mattress 0.12, 0.82 m clear). Each has 5 g teal restraint straps, one solid side and a linen privacy screen. The headboard carries a reading light, vent, personal display and lock indicator, and the viewport is at the foot.
- **Cabin walls:** the source 4 cm partition and radial walls. Doors are 0.80 × 2.05 m sliding doors with a titanium track, lock indicator and recessed pull. Wall mass is shared from each room's booking.

**No rebooking.** Dry mass 868.192255 t and ECON Δv 707.845 km/s are unchanged.

## Envelope (Claude screen, not D9)
- r 1.30–4.07 m (the inner face of the water ring) and h 0–2.30 m.
- The berth viewports are drawn at Ø0.5 m, per SPEC. WWS-1 round 2 lists Ø0.8 m as a draft design position; neither size has been changed.
- Lockers, desks and seats were checked in plan against the berth footprints.

![guest](L3_QUARTERS_PROPOSAL_2026_11_12_guest.png)
![captain](L3_QUARTERS_PROPOSAL_2026_11_12_capt.png)
![crew B](L3_QUARTERS_PROPOSAL_2026_11_12_crewb.png)
