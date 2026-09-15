# F1 — Superconductor / High-Field Magnet Evidence Pass v0.1

**Status:** EVIDENCE / ADMISSIBILITY PASS — NOT FROZEN  
**Protocol:** `LOOM_2226_ENGINEERING_FRONTIER_PROTOCOL_v0.1`  
**Target epoch:** 2226  
**Downstream numerical authority:** NONE

## BLUF

The first evidence pass does **not** earn a statistical 2226 field forecast.

The available primary-source anchors demonstrate substantial progress in superconducting magnet engineering, but the obvious record points are not one like-for-like time series. They mix laboratory/user magnets, fusion magnets, bore sizes, duty regimes, conductor generations, and system purposes. Under the Frontier Protocol's minimum-N and like-with-like rules, F1 is therefore currently:

`hindcast_status = INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`

The next defensible MVP path is **bounded scenario construction plus coupled physical/system constraints**, while continuing to expand the evidence dataset. This is preferable to manufacturing statistical confidence from incomparable records.

## Evidence table — first pass

| Approx. epoch | System / evidence | Field | Operating class | Relevant semantics | F1 use |
|---|---|---:|---|---|---|
| ~2000-era | ITER Central Solenoid Model Coil / conductor qualification context | up to ~13 T class | large superconducting fusion-engineering coil | Nb3Sn; large conductor/structure; relevant strain/quench regime | historical large-system context, not spacecraft analogue |
| 2004 | MagLab 900 MHz wide-bore MRI/NMR magnet | 21.1 T | persistent superconducting user magnet | 105 mm bore; long-lived operation | demonstrated continuous superconducting-system anchor |
| 2009 | MagLab YBCO test coil | 27.4 T | HTS test coil in development context | test-coil record, not complete user magnet | conductor/coil trajectory context only |
| 2017 | MagLab SCM-32T | 32 T | all-superconducting continuous user magnet | HTS+LTS; previous superconducting record cited by MagLab as 24 T; currently undergoing HTS-coil repair in 2026 | strongest demonstrated all-superconducting user-magnet anchor; repair status is a lifetime/reliability warning |
| 2021 | MIT/CFS SPARC full-scale HTS fusion magnet | 20 T | large-bore/full-scale fusion magnet test | REBCO; 267 km HTS tape; fusion-scale geometry | high-value large-scale field/geometry/structure anchor, not record-user-magnet series |
| 2026 | ITER toroidal-field system design / manufactured system | 11.8 T max | enormous superconducting fusion magnet system | 330 t per TF coil; 41 GJ total TF magnetic energy; Nb3Sn | system-mass/stored-energy/industrial-scale anchor |
| 2026 | ITER central solenoid assembled stack | 13 T max design | very large pulsed superconducting electromagnet | ~1000 t completed system; 6.4 GJ stored energy | system mass, structure, energy and pulsed-duty anchor |
| development | MagLab 40 T all-superconducting program | 40 T target | all-superconducting development target | 34 mm bore; HTS development | trajectory evidence only; NOT observed 40 T baseline |

## Primary-source observations

### National MagLab

MagLab's current world-record summary identifies 32 T as the highest field for a superconducting magnet. Its SCM-32T page states that the 32 T system is the first of a new class using HTS materials and that the previous superconducting record was 24 T. The same current page reports that the 32 T magnet is undergoing repairs on its HTS coils in 2026. That repair status is relevant to F1 because peak field alone cannot stand in for lifetime/reliability.

MagLab's timeline reports a YBCO test coil reaching 27.4 T in 2009 and the 32 T all-superconducting record in 2017. It also records a 21 T superconducting ICR-system funding milestone in 2009 and a 21.1 T wide-bore persistent magnet that has operated since 2004. These observations are useful but are not all the same operating class.

MagLab's 40 T all-superconducting program remains a development target and must not be inserted into the observed series as though 40 T has been demonstrated.

### MIT / Commonwealth Fusion Systems

MIT reports that the SPARC team demonstrated 20 T in 2021 in a large-bore, full-scale HTS fusion magnet using REBCO tape, with 267 km of superconducting tape in the magnet. This is a particularly useful system-scale anchor because it trades record field for a geometry and load regime closer to large engineered machinery. It is not directly comparable to a small-bore user magnet and therefore should not simply be appended to a `tesla vs year` record curve.

### ITER

ITER reports its toroidal-field coils at 11.8 T maximum field, 330 tonnes each, with 41 GJ total magnetic energy across the TF system. ITER reports the central solenoid at 13 T maximum field and 6.4 GJ stored magnetic energy; in June 2026 the six-module stack reached full height, with the completed system about 1,000 tonnes when structure and instrumentation are included.

ITER also explicitly describes superconducting operating limits as dependent on field, current density and temperature, with quench causing rapid resistive heating. Historical ITER conductor qualification material documents strain sensitivity and cycling degradation concerns for Nb3Sn. These are direct evidence that F1's critical-surface, structure, protection and lifetime axes are not optional derating decorations.

## Admissibility decision

### Candidate series A — record all-superconducting continuous field

Current evidence contains useful milestones, but this pass does not yet establish six independent, like-for-like observations with consistent bore, duty, system boundary and operating semantics.

**Disposition:** `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`.

### Candidate series B — large fusion-scale superconducting magnets

The MIT/CFS 20 T magnet and ITER's 11.8–13 T systems are high-value system anchors, but they are too few and too different in purpose/duty/geometry to form a six-point validated forecasting series.

**Disposition:** `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`.

### Candidate series C — pulsed / hybrid / resistive records

Useful for contextual physical and engineering ceilings but categorically unsuitable as direct observations for a continuous all-superconducting spacecraft magnet forecast.

**Disposition:** `CONTEXT_ONLY / NOT_F1_PRIMARY_TREND`.

## Consequence for F1 methodology

No long-horizon exponential, Wright-law, or other statistical trend is currently authorized for F1's primary large continuous magnet capability. The evidence is too sparse/incomparable under the protocol we just adopted.

That is a successful protocol outcome, not a failure. F1 now moves to bounded scenario construction:

1. establish demonstrated 2026 system anchors by operating class;
2. define consumer-relevant geometry and duty semantics rather than a universal tesla number;
3. derive conditional 2226 improvement scenarios for conductor engineering current density, structure, cryogenics/protection and radiation lifetime separately, each with explicit provenance;
4. impose all applicable known-physics constraints;
5. construct installed-system mass/energy/thermal envelopes;
6. use coupled satisfiability to find feasible field/bore/duty regions;
7. choose the least favorable downstream capability among surviving defensible scenarios for `LOOM_2226_MVP`;
8. retain a separately labeled aggressive envelope;
9. keep any unclosed physics/system constraint explicit.

## F1 constraint ledger — required before a numerical field envelope

| Constraint | Current evidence status | Required disposition before freeze |
|---|---|---|
| Field + bore geometry | observed anchors exist | consumer geometry cases required |
| `Jc(B,T,strain)` / engineering `Je` | known to be governing; no 2226 envelope yet | evidence-derived scenario required |
| magnetic/mechanical stress | known governing | geometry-aware stress model required |
| reinforcement + installed mass | observed to be material at large scale | system mass model required |
| stored magnetic energy | observed from ITER-scale systems | protection/energy-density model required |
| quench / thermal runaway | directly evidenced | protection constraint required |
| operating temperature / cryogenic burden | directly relevant | thermal/power model required |
| radiation / fluence lifetime | consumer-specific, not yet quantified | Wayfarer-relevant scenario/hold required |
| operating margin / duty | required | explicit cases required |
| repairability / lifetime | 32 T repair status shows relevance | explicit lifetime/reliability treatment required |

No single item above may be used as the sole field ceiling.

## Provisional machine-readable disposition

```text
frontier_id = F1_SUPERCONDUCTOR_MAGNET
frontier_version = v0.1-evidence-pass
producer_version_hash = PENDING_FREEZE
baseline_year = 2026
target_year = 2226
hindcast_status = INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST
forecast_method = BOUNDED_SCENARIO_CONSTRUCTION_PENDING
loom_2226_mvp_large_continuous_field = UNSET
aggressive_2226_large_continuous_field = UNSET
conditional_upper_bound = ~375 T EXPERIMENT_ONLY_NOT_AUTHORITY
component_hardware_certified = false
new_physics_required_by_frontier = false
```

## References

1. National High Magnetic Field Laboratory, **MagLab Timeline** — 2009 YBCO 27.4 T test-coil milestone; 2017 32 T superconducting record. https://nationalmaglab.org/about-the-maglab/organization/history/timeline/
2. National High Magnetic Field Laboratory, **World Records** — current superconducting, continuous, pulsed and coil-in-background record categories. https://nationalmaglab.org/about-the-maglab/facts-figures/world-records/
3. National High Magnetic Field Laboratory, **32 Tesla Superconducting Magnet (SCM-32T)** — 32 T system, previous 24 T record, current repair status. https://nationalmaglab.org/user-facilities/dc-field/magnets-instruments/superconducting-magnets/scm-32-t/
4. National High Magnetic Field Laboratory, **10 Cool Things About the World's Strongest MRI Magnet** — 21.1 T / 900 MHz persistent magnet, charged in 2004. https://nationalmaglab.org/news-events/feature-stories/10-cool-things-the-world-s-strongest-mri-magnet/
5. National High Magnetic Field Laboratory, **40-tesla Superconducting Magnet** — development target; not treated as demonstrated baseline. https://nationalmaglab.org/magnet-development/magnet-projects/40-tesla-superconducting-magnet/
6. MIT News, **MIT-designed project achieves major advance toward fusion energy** (2021) — 20 T large-bore full-scale HTS fusion magnet; 267 km REBCO tape. https://news.mit.edu/2021/MIT-CFS-major-advance-toward-fusion-energy-0908
7. ITER Organization, **Superconducting Magnets** — TF system 11.8 T / 330 t coils / 41 GJ; central solenoid 13 T / 6.4 GJ and system scale. https://www.iter.org/machine/magnets
8. ITER Organization, **Standing tall** (29 Jun 2026) — central-solenoid stack assembly milestone and ~1,000 t completed system context. https://www.iter.org/node/20687/standing-tall
9. ITER Organization, **Good news from Naka** — superconducting operating range dependence on field/current density/temperature and quench-heating description. https://www.iter.org/node/20687/good-news-naka
10. ITER Organization, **Robustness of ITER's solenoid conductor confirmed** — Nb3Sn strain sensitivity, conductor construction and cycling-degradation context. https://www.iter.org/robustness-iters-solenoid-conductor-confirmed-0
