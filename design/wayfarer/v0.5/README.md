# Wayfarer v0.5 — non-governing certification submission (2026-10-25)

**Status:** NON-GOVERNING SANDBOX / NOT CANON / NOT ENGINEERING CLOSURE / NOT QUALIFIED.

**Source:** Claude Wayfarer v0.5 design and proposed certification exercise supplied by kT on 2026-10-25. This is a successor archival record to v0.4 and v0.4.1. Neither predecessor is modified.

**Original archive:** [`wayfarer_v0_5_record_2026-10-25.zip`](wayfarer_v0_5_record_2026-10-25.zip), unmodified, 46 ZIP entries including directories, 41 regular extracted files.

**SHA-256:** `e0d1e7869f3fc626ff5ddee53355789698536994a5cbef25c7c6f71fad938c0f` (verified on quantifactus).

## Read in this order

1. [`CERTIFICATION_BASIS_v0.1.md`](wayfarer_v0_5_record/CERTIFICATION_BASIS_v0.1.md) — **proposed** basis, not approved.
2. [`out/CERTIFICATION_REPORT_v0.5.md`](wayfarer_v0_5_record/out/CERTIFICATION_REPORT_v0.5.md) — generated submission report.
3. [`SPEC_v0.5.md`](wayfarer_v0_5_record/SPEC_v0.5.md) — design summary.
4. [`PROPOSED_CANON_AMENDMENT_v2.4d.md`](wayfarer_v0_5_record/PROPOSED_CANON_AMENDMENT_v2.4d.md) — proposal only; **NOT CANON**.

## Design snapshot

- 53.3 m long, 867.7 t dry, 1,167.7 t wet with 300 t water (250 t remass + 50 t protected), 722.8 km/s ECON delta-v.
- C-section four-cell water tank surrounding an axial 4.8 m launch bore; five longerons, four accordion radiator strakes at 1,300 K; offset torch thrust line.
- Rover-drop shuttle: 27.9 t empty, 12.8 × 3.8 m; Venus surface exploration by separate rover from cloud-city altitude. Six crew and four guest berths aboard the mothership.
- Five defined habitat decks, 318 m³ net living volume, storm shelter, four drones in pods, geometry-derived exterior/cutaway/deck-plan renders and phone viewer.

## Submitted gate results (not independently signed)

G1, G2, G3, G5, G7, G8, G9, G11, G12: **submitted PASS**. G4 and G6: **submitted PASS-DECLARED** subject to five explicit assumptions requiring kT's acceptance. G10 Navigator mission suite: **OPEN**. The report is not a certificate.

Declared assumptions concern torch waste heat (<= 387 MW into ship, ~34 ppm of jet power), Metric HARD cryo electrical (~34.8 MW at 1,300 K), 72 h shelter life support, cosmic-ray career-dose mitigation, and torch neutron/gamma attenuation. None is silently accepted by this archive.

## Reproduction

Python 3 standard library only, from the extracted folder:

```sh
python3 build_v05.py
python3 certify.py
```

The submitted geometry SHA-256 is `406424a71d8d3195dc23bc732d29ec3ca6686ef15d5bf61fa0be64171eeba2a1`. `out/wayfarer_v05_card.json` is the proposed G10 Navigator input; missions E1, FR-01B-R, MV-01 require arrival remass >= 50 t each.

## Independent review findings / boundaries

- **G1:** the full inertia tensors exist in `out/wayfarer_v05_geometry.json` for the seven states; the smaller Navigator card publishes only diagonal terms. Navigator interoperability needs an explicit mass-properties mapping if it consumes the full tensor.
- **G4 review finding:** the 387 MW torch heat-leak limit and 34.8 MW cryo power are proposed interfaces, not demonstrated canon capabilities. Retain PASS-DECLARED only as an authored assumption, not physical closure.
- **G5 review finding:** the submitted report explicitly says the flat C-wall/slot detailed shell model remains OPEN; the simplified longeron checks do not close that structural detail.
- **G6 review finding:** reactor neutron/gamma source and required shield attenuation are not quantified; cosmic-ray protection also remains dependent on an unspecified future medicine capability. This cannot become unconditional PASS.
- **G10:** no Navigator mission execution or arrival-remass result is established by the submitted report. Keep OPEN until E1, FR-01B-R and MV-01 are actually flown using the v0.5 card.
- **G11:** 'all departures listed' is a bookkeeping claim, not approval of any deviation. In particular the governing CANON II §13.2 four-longeron/four-tank grammar differs from this five-longeron/C-tank design.

**Review disposition:** no independent certification sign-off; these findings require review/resolution under the proposed basis before any gate can be treated as accepted. No threshold changes have been made.

## Authority

Preservation under `design/wayfarer/v0.5/` does not promote the proposed amendment or alter `canon/current/**`, `engineering/current/**`, Navigator, runtime, data, geometry authority, or previous archived versions. Canon decisions require explicit kT disposition and governed promotion. WALTER/loom-gate protections remain in force.
