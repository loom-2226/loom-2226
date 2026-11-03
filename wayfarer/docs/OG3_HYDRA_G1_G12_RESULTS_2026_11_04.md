# OG-3 HYDRA exact-hash certification and physical holds

**ALL bodies. ALL sponsors. 2026–2226.**

**STATUS: DRAFT / NON-CANON / NON-QUALIFICATION / NO MERGE.** kT decides. Stacked on WWS-1 PR #465.

**Geometry SHA-256:** `e9717b871804dc4bf1802ef4441165feb36426eb2c11cf2245f4a1b89722dde7`. Full `bash wayfarer/lab/run_all.sh` exit **0**, all source-hash renders/deckplans/GLB/viewer rebuilt. FQ **78/78 PASS_NUMERICAL**, both current RCS traces hash match.

## G1–G12 certification

| Gate | Verdict | Failed checks |
|---|---|---|
| G1 | PASS | None |
| G2 | PASS | None |
| G3 | PASS | None |
| G4 | PASS-DECLARED | None |
| G5 | PASS-DECLARED | None |
| G6 | PASS-DECLARED | None |
| G7 | PASS-DECLARED | None |
| G8 | PASS | None |
| G9 | PASS-DECLARED | None |
| G10 | PASS-DECLARED | None |
| G11 | PASS | None |
| G12 | PASS-DECLARED | None |

Every PASS-DECLARED remains design-screen/assumption qualification only. No existing numeric criterion was changed.

## OG-3 G6: areal mass only, not dose

| Check | Source-hashed result | Interpretation |
|---|---:|---|
| OG-3 HYDRA OPEN: physical areal column only (NOT GCR or SPE dose) | 31.411171 | Quiet-sun physical areal column, no GCR/SPE biological dose |
| OG-3 HYDRA CLOSED: local areal mass meets unchanged SPE ray rule | 58.411171 | Strata shutters closed for SPE/torch/Metric/LOOM; per-aperture mass, no ray transport |
| OG-3 nano-fibre below 1% by mass; composition declared only | 0.005 | 0.5% BNNT-H, source assumed optical index match |
| OG-3 has ZERO quantified radiation-dose and optical heat credit | [None, None, 0, 0] | GCR and SPE dose fields NULL; no optical heat credit |

- Original shell/armour and mechanical inserts unchanged. **G6 storm shelter sample minimum: 53.390349 g/cm²**. Shelter remains **ZERO windows**. Actual neutron/ion secondary particle transport is not computed.
- Nominal OG-3 OPEN 31.411171 g/cm² is less than existing LOOM 40g/cm² SPE ray screen, requiring a shutter closure on alert. Closed 58.411171 g/cm² exceeds the per-aperture material screen, not a guarantee of a sealed shield or safe lifetime dose.
- The original AOI allocation is **66.611712004kg/m²**; OG-3 skin **2.4kg/m²**, bulk **64.211712004kg/m²**. No added dry/wet mass, no deep gel, uncommitted **1.04t** option untouched, no new reserve credit.
- Nuclear/health dose: **GCR annual dose equivalent = NOT COMPUTED; SPE event dose = NOT COMPUTED; dose reduction credited = ZERO**. NASA [NTRS 20170005580](https://ntrs.nasa.gov/citations/20170005580) verifies an aluminium local minimum near 20–30g/cm² and polyethylene flattening, not a universal hydrogenous 20g limit.

## Preserved ship reserves and vehicle state

- Engineering reserve **9.163470t** (same as WWS-1 R2), uncommitted released structure **9.533700t**, combined **18.697170t**. No credit from 1.04t as “new mass”.
- S1 total **1172.681453t**, unchanged from WWS-1 R2, remass 250t, ECON exhaust velocity 3000km/s. No Halo or Lightfold in dry mass or passive armour.

## OPEN / stop conditions

- 66.21mm equivalent OG-3 column vs 59.73mm minimum local crown interspace: geometric local fit is **NOT PROVEN**, although average-volume screen fits.
- Flammability (nominal oxygen-free sealed case), radiolysis, outgassing, freeze/boil/viscosity, optical darkening, index match and BNNT dispersion lifetime.
- Pressure-pane independent fracture, optical heat/NIR response, nanofibre/carborane irradiation and reaction-product dose.
- Actual GCR/SPE dose and Strata shutter edge streaming via HZETRN/OLTARIS or Geant4, not performed.
- No changes in this PR to PR #184 placement HOLD, shelter openings, passive armour, Shuttle or Halo.
