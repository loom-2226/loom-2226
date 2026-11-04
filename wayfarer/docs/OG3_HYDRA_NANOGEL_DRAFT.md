# OG-3 HYDRA Nanogel | Wayfarer WWS-1 material substitution

**ALL bodies. ALL sponsors. 2026–2226.**  
**DRAFT · RESEARCH-ASSUMED MATERIAL · NON-CANON · NO MERGE · kT DECIDES.**

## Decision and invariants

Substitute the existing AOI interlayer in WWS-1 side windows and crown with **OG-3 HYDRA**. **Side windows retain the nominal 66.611712004 kg/m² column; the crown is now a conformal radial-zoned fill**, comprising a **2 mm AOI-2226 optical/electrochromic skin** over an **alkane organogel** containing an assumed **0.5 wt% hydrogen-functionalised BNNT nanofibre network** (strictly below 1%) and **1 wt% enriched ¹⁰B carborane**. These are material-model assumptions, not a known transparent 2226 formulation. The remaining 98.5 wt% bulk is alkane carrier. **Every material and operative numerical parameter is in `wayfarer/config/og3_hydra.json`**, pinned by SHA-256 in the ship input. The G6 code reads it rather than inserting unexplained material values.

This **replaces** booked AOI mass. The conformal crown requires an extra **0.041015 t**, physically booked by reducing uncommitted engineering reserve from **9.163470 to 9.122455 t**; ship dry mass, hull, berth count, shelter and mechanical ratings stay unchanged because the extra gel displaces the exact same reserve allocation. **No deep gel.** The previously discussed **1.04 t option remains uncommitted within the existing reserve**; it is not a newfound 1.04t credit.

Pressure panes and closure unchanged: replaceable external bumper → full-pressure ceramic primary → 2mm AOI skin / HYDRA bulk → independent full-pressure ceramic backup → closing Strata shutter. Each pressure pane's independent pressure survival is **OPEN**.

## Shielding: mass is not dose

Using source configuration (10 kg/m² = 1 g/cm²). The following **31.411 / 58.411 g/cm² columns apply to the uniform WWS-1 SIDE WINDOWS**, not every crown annulus:

| Operating state | Constituent nominal column | Areal mass |
|---|---|---:|
| OPEN / quiet sun | bumper 37.5 + primary 105 + backup 105 + HYDRA 66.611712 kg/m² | **31.411171 g/cm²** |
| CLOSED / SPE, torch, Metric/LOOM | OPEN plus Strata 270 kg/m² | **58.411171 g/cm²** |

OG-3 is now **counted as physical material areal column in G6**, with a source-pinned composition; **no numerical dose equivalent is calculated**. The existing 3D ray screen already treats armour as continuous, so adding the OG-3 column a second time to that ray caster would *double count* and is prohibited. The G6 per-aperture check is a separate accounting column, *not* new mission-dose credit or proof of shielding at seams.

The unchanged LOOM **40 g/cm² minimum ray criterion is a storm/SPE design screen**, **not** NASA's claimed universal GCR cutoff. G6 OPEN's ~31.41 is below that screen: deliberately **close shutters on SPE alert**, torch ignition, Metric/LOOM operations, high dust, or heat-pump failure. Quiet-sun viewing is a doctrine choice subject to actual GCR exposure controls and uncalculated dose.

NASA Norman et al. (2017), [NTRS 20170005580](https://ntrs.nasa.gov/citations/20170005580) reports an approximately 20–30 g/cm² **aluminium** modelled GCR dose-equivalent minimum driven by secondary production; hydrogenous **polyethylene** instead decreases and flattens with increasing thickness. It does not validate a universal 20g threshold for all hydrogenous mixtures, nor predict dose behind OG-3. Model HZETRN/OLTARIS or Geant4 with the full material, ¹⁰B captures, neutron and ion secondaries, aperture geometry and habitat positions before claiming dose reduction.

## Why this remains *a material concept*, not a qualified pane

**Conformal crown now implemented in the source model.** The original crown declares **3.023m³** of interspace, minimum local **normal** gap **59.73mm**, parent pressure-dome meridian radius 4.3m and depth 3.343118m, with four radial annuli [0,.75,2,2.75,3.5]m. The exact backup dome meridian is NOT separately defined. The claimed 120mm axial shell offset, when treated as a uniform translation of that meridian, implies ~4.618m³ of projected cavity rather than 3.023m³ and cannot reconcile both given constraints. We therefore fit a clearly labelled **interpolated** conformal normal-gap profile g(r)=59.73mm + A·[1−(r/3.5m)²] to the source minimum plus total volume, with A solved by surface integration (A≈15.776mm). This is **not a surveyed physical surface** and must remain an OPEN physical-integration issue.

| Crown annulus radius | Modelled mean OG-3 areal kg/m² | Min local normal gap mm | Max normal gap mm |
|---|---:|---:|---:|
| 0–0.75m | **75.5428** | see zonal JSON | see zonal JSON |
| 0.75–2.0m | **72.9428** | see zonal JSON | see zonal JSON |
| 2.0–2.75m | **68.4233** | see zonal JSON | see zonal JSON |
| 2.75–3.5m | **63.0404** | **59.73** at rim | see zonal JSON |

A full **2mm AOI skin** is subtracted from each zone's fitted normal gap and the remaining local space filled with source-declared **1000kg/m³ HYDRA organogel**; 2mm AOI at **1200kg/m³** remains bonded to the primary. The integrated model gives **3.04101485t**, versus the formerly booked **3.000000t**; delta **+0.04101485t**, booked against *existing* uncommitted engineering reserve, so dry ship **867.531453t** unchanged. The **1.04t deep gel** remains entirely unspent in the original reserve; no additional cavity layer. Source and repeatable mass check: `wayfarer/config/og3_hydra.json` and `python wayfarer/lab/og3_conformal.py`.

The annular mass / open and closed column is separately checked in G6; the WWS side-window 66.611712kg/m² column and static ray surrogate are **not** blindly applied to the entire crown. Optical/electrical and dose credits remain ZERO. The model cannot certify actual backup-dome contact, thermal expansion, 120mm axial offset, independent pressure fracture, or long-term gel dispersion; those remain OPEN.

The assumed 0.5wt% BNNT-H network needs index matching, uniform distribution and durable dispersion while retaining visible/NIR modes. No demonstrated optical throughput, scattering, darkening resistance, radiation response, controllable phase/viscosity or service life exists in the source. Enriched ¹⁰B can capture thermal neutrons but produces reaction products, so **zero dose benefit is claimed**.

## Open without caveat laundering

- Flammability and pyrolysis within a sealed oxygen-free layer; containment after a pane failure is not sealed.
- Radiolysis and long-term trapped-gas generation.
- Outgassing and ceramic/optical coating contamination.
- Freeze, boil, viscosity, swelling and pressure-pulse ranges across missions.
- BNNT-H dispersion, index matching, and optical/NIR clarity over decades.
- ¹⁰B carborane ageing, secondary neutron capture dose and radiochemistry.
- Ceramic darkening, erosion and damage over exposure.
- Actual backup-dome meridian vs interpolated conformal interspace (120mm axial-offset contradiction), and independent-pane shock/fracture survival.
- Per-aperture open/closed material transport through Strata seams, actual GCR/SPE dose at berths and occupied open ports.

**Acceptance scope:** existing G1–G12 numerical design gates must rerun on a pinned source hash, but a PASS or PASS-DECLARED is **not** materials qualification. No Halo or Lightfold structural/radiation changes are imported from the research library.
