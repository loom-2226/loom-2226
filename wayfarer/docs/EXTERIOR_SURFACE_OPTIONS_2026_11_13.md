# Wayfarer exterior surface options (PROPOSAL, F4: sketch + numbers)

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-13** as amended below (decision `exterior_surface_2026_11_13`).
The A/B/C renders stay as the record of the proposal. Renders in
`wayfarer/lab/exterior_surface_options/`, made with the repo render chain plus a
sketch-only shader copy (`loomgl_opt.js`). Canon GLBs and `loomgl.js` are untouched.

## Finding: the exterior openings update is smaller than expected

| Opening | On the outer hull? | State |
|---|---|---|
| EVA hatch (L5 airlock, 0 deg) | Yes | **Already in source geometry**: `features` hatch, x 12.25, 0 deg, d 1.1 m. Matches kT's l5 decision (1.0 m clear, centre x 12.3, 5 cm difference). |
| L4 medical ports, lowered x 9.10 to 9.30 | Yes | **The only exterior change.** Same size and azimuths (180/210/240). Shown on the option renders. |
| Tunnel hatch (L5 floor, aft bulkhead) | No, internal | No exterior change |
| Shelter plug door | No, internal | No exterior change |
| L3/L4 slab pocket | No, internal | No exterior change |

## Options (all are etched into the surface; nothing protrudes)

| | A Structural | B Armour tiles | C Working hull |
|---|---|---|---|
| Seams | Approved 9 Nov grid only, now real grooves | A + mid-bay rings + a joint every 20 deg | B |
| Tile size (real) | Bays 2.6 m (habitat), 2 m (aft) | About 1.3 x 1.57 m; about 500 tiles | B |
| Openings | EVA hatch frame and 8 latches; medical port frames | A | A + 1.05 m keep-out ring round the EVA hatch |
| EVA | Existing rails only | Existing rails only | Lane between the existing +/-14 deg rails, x 13.4 to 24.0, tread every 0.4 m; clear of node faces at 14.35, 18.45, 22.55 |
| Tether points | None | None | Rings at the 24 existing crawler points |
| Groove at 1:100 | 0.5 mm = 50 mm real | Same | Same; tether rings (3.2 mm) marginal, so 1:25 only |
| Groove at 1:25 | 0.5 mm = 12.5 mm real | Same | Same, all features print |
| New mass | 0 | 0 | 0 |
| F1 (no protrusions) | PASS | PASS | PASS |
| F2 (no blocks) | PASS | PASS | PASS |
| Design-level change | None (approved grid) | New Strata joint pattern (look is a placeholder) | B + EVA markings |

Depth: 0.16 mm minimum relief (2 layers) from `wayfarer/print/surfaces_1to25/print_profile.json`.

## APPROVED (kT 2026-11-13, after Sol's review)

- **1:100 hull: Option B.** The tiles are surface demarcations only, not gaps through the armour.
- **1:25 diorama: B plus selected C details**: EVA hatch keep-out ring, lane edge lines with **no tread** (the tread read as decorative ribbing), and the 24 tether rings.
- **Print grooves are model exaggeration**, not physical seam width. The 1:100 hull gets its own print profile.
- **EVA hatch:** source d 1.1 m = outer frame, 1.0 m = clear opening; centre is x 12.25 (source).
- **Medical ports** move to x 9.30 on the exterior model as real openings through hull and armour, with D9 + containment. WWS-1 stays non-canon.

## Claude's recommendation (as proposed)

**B on the 1:100 hull, plus C's extras on the 1:25 diorama only.** At 1:100, A
leaves the flanks almost blank (26 mm between rings), so the model loses its sense
of scale. C's lane and tether rings are below what the printer can resolve at
1:100, but they print well at 1:25. The print profile can drop features that are
too small at each scale automatically, so one surface definition serves both
prints.

