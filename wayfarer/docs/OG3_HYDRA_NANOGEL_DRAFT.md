# OG-3 HYDRA Nanogel | Wayfarer WWS-1 material substitution

**ALL bodies. ALL sponsors. 2026–2226.**  
**DRAFT · RESEARCH-ASSUMED MATERIAL · NON-CANON · NO MERGE · kT DECIDES.**

## Decision and invariants

Substitute the existing AOI interlayer in WWS-1 side windows and crown with **OG-3 HYDRA** at unchanged **66.611712004 kg/m²**, comprising a **2 mm AOI-2226 optical/electrochromic skin** over an **alkane organogel** containing an assumed **0.5 wt% hydrogen-functionalised BNNT nanofibre network** (strictly below 1%) and **1 wt% enriched ¹⁰B carborane**. These are material-model assumptions, not a known transparent 2226 formulation. The remaining 98.5 wt% bulk is alkane carrier. **Every material and operative numerical parameter is in `wayfarer/config/og3_hydra.json`**, pinned by SHA-256 in the ship input. The G6 code reads it rather than inserting unexplained material values.

This **replaces** booked AOI mass; it does not add mass or change dry/wet ship states, hull, berth count, shelter or any mechanical rating. **No deep gel.** The previously discussed **1.04 t option remains uncommitted within the existing reserve**; it is not a newfound 1.04t credit.

Pressure panes and closure unchanged: replaceable external bumper → full-pressure ceramic primary → 2mm AOI skin / HYDRA bulk → independent full-pressure ceramic backup → closing Strata shutter. Each pressure pane's independent pressure survival is **OPEN**.

## Shielding: mass is not dose

Using source configuration (10 kg/m² = 1 g/cm²):

| Operating state | Constituent nominal column | Areal mass |
|---|---|---:|
| OPEN / quiet sun | bumper 37.5 + primary 105 + backup 105 + HYDRA 66.611712 kg/m² | **31.411171 g/cm²** |
| CLOSED / SPE, torch, Metric/LOOM | OPEN plus Strata 270 kg/m² | **58.411171 g/cm²** |

OG-3 is now **counted as physical material areal column in G6**, with a source-pinned composition; **no numerical dose equivalent is calculated**. The existing 3D ray screen already treats armour as continuous, so adding the OG-3 column a second time to that ray caster would *double count* and is prohibited. The G6 per-aperture check is a separate accounting column, *not* new mission-dose credit or proof of shielding at seams.

The unchanged LOOM **40 g/cm² minimum ray criterion is a storm/SPE design screen**, **not** NASA's claimed universal GCR cutoff. G6 OPEN's ~31.41 is below that screen: deliberately **close shutters on SPE alert**, torch ignition, Metric/LOOM operations, high dust, or heat-pump failure. Quiet-sun viewing is a doctrine choice subject to actual GCR exposure controls and uncalculated dose.

NASA Norman et al. (2017), [NTRS 20170005580](https://ntrs.nasa.gov/citations/20170005580) reports an approximately 20–30 g/cm² **aluminium** modelled GCR dose-equivalent minimum driven by secondary production; hydrogenous **polyethylene** instead decreases and flattens with increasing thickness. It does not validate a universal 20g threshold for all hydrogenous mixtures, nor predict dose behind OG-3. Model HZETRN/OLTARIS or Geant4 with the full material, ¹⁰B captures, neutron and ion secondaries, aperture geometry and habitat positions before claiming dose reduction.

## Why this remains *a material concept*, not a qualified pane

A source-derived dimensional problem is explicitly left visible. The originally modelled crown interspace contains 3.023m³ across ~45.037m² (average projected column ~67.13mm). The OG-3 bulk's nominal assumed 1000kg/m³ gives ~64.21mm, plus 2mm AOI skin = **66.21mm equivalent column**. **The existing minimum local interspace is only 59.73mm.** The average volume can fit numerically while the narrowest part cannot accommodate a uniform 66mm layer. A conformal variable-depth gel, density change, or geometry redesign might solve this; none is authorised or physically qualified here. Actual alkane-rich gel densities may be lower than the model's optimistic 1000kg/m³, worsening fit.

The assumed 0.5wt% BNNT-H network needs index matching, uniform distribution and durable dispersion while retaining visible/NIR modes. No demonstrated optical throughput, scattering, darkening resistance, radiation response, controllable phase/viscosity or service life exists in the source. Enriched ¹⁰B can capture thermal neutrons but produces reaction products, so **zero dose benefit is claimed**.

## Open without caveat laundering

- Flammability and pyrolysis within a sealed oxygen-free layer; containment after a pane failure is not sealed.
- Radiolysis and long-term trapped-gas generation.
- Outgassing and ceramic/optical coating contamination.
- Freeze, boil, viscosity, swelling and pressure-pulse ranges across missions.
- BNNT-H dispersion, index matching, and optical/NIR clarity over decades.
- ¹⁰B carborane ageing, secondary neutron capture dose and radiochemistry.
- Ceramic darkening, erosion and damage over exposure.
- Crown minimum interspace geometry vs HYDRA equivalent thickness, and independent-pane shock/fracture survival.
- Per-aperture open/closed material transport through Strata seams, actual GCR/SPE dose at berths and occupied open ports.

**Acceptance scope:** existing G1–G12 numerical design gates must rerun on a pinned source hash, but a PASS or PASS-DECLARED is **not** materials qualification. No Halo or Lightfold structural/radiation changes are imported from the research library.
