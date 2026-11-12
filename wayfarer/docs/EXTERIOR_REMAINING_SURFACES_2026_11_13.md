# Wayfarer remaining exterior surfaces (PROPOSAL, F4: sketch + numbers)

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-13: thrust cone 2, bay doors 2, radiators and fins 2.** These are the large exterior surfaces that
are blank only because nobody has decided their surface yet. Renders are in
`wayfarer/lab/exterior_remaining_options/` (the repo render chain plus a sketch-only
shader copy). No GLB, geometry, `loomgl.js`, mass or canon change. Every mark is a
demarcation only, as with Option B.

Already decided: the hull cylinder (9 Nov + B), the bow shoulder (clean), the crown
tiles, the torch end (11 Nov canon finish) and the maintenance panels. The shuttle
already carries engraved seams from its 8 Nov model, which print at 0.5 mm, so it
needs no decision.

## Thrust cone (x 34.3-39.3, r 4.4 to 2.95; 60 mm shell)

| | 1 Clean (as built) | 2 Load lines | 3 Tiles |
|---|---|---|---|
| Marks | None | 4 meridians at the fin-root azimuths (40/140/220/320) + 1 ring at x 36.8 | A joint every 20 deg + a ring every 1 m |
| Meaning | Smooth shell | The structure that carries thrust out to the fin roots | Copies the hull's B tiles |
| At 1:100 | Nothing | 0.5 mm grooves | 0.5 mm grooves, dense |

**Claude: 2.** The lines sit where the loads go. Option 3 makes the cone read as
Strata armour, which it isn't.

## Bay doors (x 18.25-32.05, 57.8-122.2 deg)

| | 1 B joints cross the doors (viewer now) | 2 Clean leaves | 3 Rings + centre split |
|---|---|---|---|
| Marks | Hull rings + 20 deg joints run across the doors | Door edges + 90 deg centre split only | Hull rings + edges + split, no 20 deg joints (the 1:100 print spec today) |

**Claude: 2.** The doors are separate moving leaves, so hull frames and tile joints
should not run across them. The 90-degree split where the two leaves meet is a real
edge and appears in every option. Note that the viewer today (option 1) and the
print spec (option 3) disagree, so this needs a decision whichever way it goes.

## Radiator strakes and hot fins

| | 1 Clean (as built) | 2 Heat-pipe channels | 3 2 m segments |
|---|---|---|---|
| Marks | None (hot glow already bands every 2 m) | A line every 0.5 m, running root to tip | A joint every 2 m at the frame stations |
| At 1:100 | Nothing | 5 mm pitch | 20 mm pitch |

**Claude: 2.** Root-to-tip channels show what a radiator does: it moves heat from
the root manifold out to the tip. The fins print as separate deployable parts, so
the lines go on the printed fin faces.

## APPROVED (kT 2026-11-13): 2 / 2 / 2

- **Thrust cone:** load lines. Four meridians at 40/140/220/320 deg plus one ring at x 36.8.
- **Bay doors:** clean leaves. Door edges at 57.77/122.23 deg plus the 90 deg centre split only. No hull rings and no 20 deg joints on the doors.
- **Radiator strakes, hot fins and fin roots:** heat-pipe channels every 0.5 m, root to tip, on both faces.

Every mark is a demarcation only: no mass, no protrusion, no canon change.

**Decision record:** this is deliberately **not yet written to `kt_decisions.json`**. A PR that
touches that file currently triggers `wayfarer-exterior-detail-f3.yml`, which rebuilds the
released canon GLBs and does not reproduce them byte for byte (see PR #540). Sol adds this entry
once the workflow is fixed:

```json
"exterior_remaining_surfaces_2026_11_13": {
  "authority": "kT APPROVED 2026-11-13 (Claude chat)",
  "source": "wayfarer/docs/EXTERIOR_REMAINING_SURFACES_2026_11_13.md (PR #541)",
  "thrust_cone": "Option 2 load lines: meridians 40/140/220/320 deg + ring x 36.8",
  "bay_doors": "Option 2 clean leaves: edges 57.77/122.23 deg + 90 deg centre split only; no hull rings or 20 deg joints on doors",
  "radiators_fins": "Option 2 heat-pipe channels every 0.5 m root-to-tip, both faces, strakes + hot fins + fin roots",
  "meaning": "surface demarcations only; no gaps, mass or protrusion",
  "mass_rebooking_t": 0, "canon_change": false, "G1_G12": "NOT RUN",
  "status": "APPROVED; viewer by Sol, print spec by Claude"
}
```
