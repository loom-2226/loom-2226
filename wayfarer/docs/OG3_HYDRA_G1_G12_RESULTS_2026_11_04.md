# OG-3 HYDRA exact-hash certification and physical holds

**ALL bodies. ALL sponsors. 2026–2226.**

**STATUS: DRAFT / NON-CANON / NON-QUALIFICATION / NO MERGE.** kT decides. Stacked on WWS-1 PR #465.

**Geometry SHA-256:** `274e94fb43cfe549a3d2087abbdff4d65499ce6f5055ad2d7ade790414fbaaf9`. Full `bash wayfarer/lab/run_all.sh` exit **0**, all source-hash renders/deckplans/GLB/viewer rebuilt. FQ **78/78 PASS_NUMERICAL**, both current RCS traces hash match.

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
- The **side-port** AOI allocation remains **66.611712004kg/m²** (crown is zoned); OG-3 skin **2.4kg/m²**, bulk **64.211712004kg/m²**. Crown now has **+0.041015t additional physical gel** funded by reducing existing uncommitted reserve, so total ship dry/wet **unchanged**; no deep gel, uncommitted **1.04t** option untouched, no new reserve credit.
- Nuclear/health dose: **GCR annual dose equivalent = NOT COMPUTED; SPE event dose = NOT COMPUTED; dose reduction credited = ZERO**. NASA [NTRS 20170005580](https://ntrs.nasa.gov/citations/20170005580) verifies an aluminium local minimum near 20–30g/cm² and polyethylene flattening, not a universal hydrogenous 20g limit.

## Conformal crown zones: recomputed real material areal mass within a source-fitted normal-gap field

The **actual backup-dome surface is not specified**. Rather than assert a false fit, OG-3 uses a SOURCE-CONSTRAINED INTERPOLATED normal-gap field preserving 3.023m³ total and 59.73mm minimum. Its shape differs from the unqualified declared 120mm axial offset. Each zone is source-locked in `og3_hydra.json` and can be independently recomputed using `python wayfarer/lab/og3_conformal.py`.

| Annulus m | Surface m² | Gap min / mean / max mm | OG-3 mass t | OG-3 kg/m² | Open g/cm² | Closed g/cm² |
|---|---:|---|---:|---:|---:|---:|
| 0–0.75 | 1.775 | 74.78/75.14/75.51 | 0.134120 | 75.543 | 32.304 | 59.304 |
| 0.75–2 | 11.261 | 70.35/72.54/74.78 | 0.821375 | 72.943 | 32.044 | 59.044 |
| 2–2.75 | 12.661 | 65.77/68.02/70.35 | 0.866317 | 68.423 | 31.592 | 58.592 |
| 2.75–3.5 | 19.340 | 59.73/62.64/65.77 | 1.219203 | 63.040 | 31.054 | 58.054 |

Total crown **3.041015t**, up **0.041015t** from prior. Engineering reserve after debit **9.122455t** (floor5), combined uncommitted **18.656156t** (floor16.8). Deep-gel 1.04t stays unspent. These are areal-material checks, NOT calculated GCR/SPE dose. All shutters CLOSED restore nominal minimum areal mass in G6 while GCR/SPE dose reduction credit remains ZERO.

## Preserved ship reserves and vehicle state

- Engineering reserve **9.122455t**, uncommitted released structure **9.533700t**, combined **18.656156t**. OG-3 crown zonal fit +0.041015t physically debited from reserve. No credit from protected 1.04t as new mass.
- S1 total **1172.681453t**, unchanged from WWS-1 R2, remass 250t, ECON exhaust velocity 3000km/s. No Halo or Lightfold in dry mass or passive armour.

## OPEN / stop conditions

- Conformal interpolation respects the source 59.73mm minimum and total 3.023m³, but **does not verify the actual backup dome**. Its declared 120mm uniform axial offset would instead imply ~4.618m³ for same-profile surfaces, inconsistent with the recorded volume. Physical fit/independent pressure domes OPEN.
- Flammability (nominal oxygen-free sealed case), radiolysis, outgassing, freeze/boil/viscosity, optical darkening, index match and BNNT dispersion lifetime.
- Pressure-pane independent fracture, optical heat/NIR response, nanofibre/carborane irradiation and reaction-product dose.
- Actual GCR/SPE dose and Strata shutter edge streaming via HZETRN/OLTARIS or Geant4, not performed.
- No changes in this PR to PR #184 placement HOLD, shelter openings, passive armour, Shuttle or Halo.
