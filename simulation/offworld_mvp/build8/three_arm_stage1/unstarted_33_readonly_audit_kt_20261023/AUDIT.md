# Read-only PR427 audit: 33 bodies without project starts

**No simulation runs. No downloads. No pre-existing file edits.** This audits the accepted 57-start campaign. A quoted trajectory cap is not the same as the campaign policy rejecting a candidate.

## The 33 bodies

| Body | Group | Price (model units) | Observed blocker | What it needs |
|---|---|---:|---|---|
| ARROKOTH | earlier outer 24 | 9.022e+9 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| ATLAS3I | earlier outer 24 | 1.881e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| BORISOV | earlier outer 24 | 1.971e+18 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| CHARON | earlier outer 24 | 3.826e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| CHIRON | earlier outer 24 | 18.67 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| COMET_HALLEY | earlier outer 24 | 3.691e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| DACTYL | unpriced | — | Gravity missing | Gravity + quote |
| ERIS | earlier outer 24 | 6.028e+34 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| GONGGONG | earlier outer 24 | 2.309e+31 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| HAUMEA | earlier outer 24 | 2.573e+13 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| HYDRA | earlier outer 24 | 4.100e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| HYPERION | unpriced | — | No supported quote | Complete quote |
| IXION | earlier outer 24 | 6.268e+8 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| KERBEROS | earlier outer 24 | 4.080e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| MAKEMAKE | earlier outer 24 | 7.772e+15 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| MIRANDA | six additional moons | 22.30 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| MS4 | earlier outer 24 | 5.959e+12 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| NEREID | six additional moons | 3.094e+5 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| NIX | earlier outer 24 | 4.047e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| ORCUS | earlier outer 24 | 6.766e+12 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| OUMUAMUA | earlier outer 24 | 1.674e+21 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| PLUTO | earlier outer 24 | 4.467e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| PROTEUS | six additional moons | 1.375e+4 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| QUAOAR | earlier outer 24 | 4.326e+9 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| SALACIA | earlier outer 24 | 1.943e+13 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| SEDNA | earlier outer 24 | 1.775e+28 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| SELAM | unpriced | — | Gravity missing | Gravity + quote |
| STYX | earlier outer 24 | 4.020e+7 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| SWIFTTUTTLE | earlier outer 24 | 4.230e+11 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| TITANIA | six additional moons | 38.40 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| TRITON | six additional moons | 4.641e+4 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| UMBRIEL | six additional moons | 42.55 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |
| VARUNA | earlier outer 24 | 1.135e+11 | Sponsor affordability; 1,400-day price window | Lower quoted cost or more sponsor capital |

The six additional priced bodies outside the original outer 24 are **MIRANDA, NEREID, PROTEUS, TITANIA, TRITON, UMBRIEL**. Their original quote flight days are 1400, 1400, 1361.25, 1305, 1400, 1272.5 respectively. The latter three under 1,400 days prove the cap is **not universally binding**.

## Why priced candidates do not start

- `moon_price_precedence_kt_20261023/run_multi_project.py:160-182`: every positive A1 with a quote becomes a candidate; mission quote plus construction/float determines commitment.
- Same file `:185-210`: sponsor policy ranks commitments and can defer candidates; `:213-224` checks actual sponsor capital. `:267-288` retries pending candidates on later annual callbacks.
- The saved run reports `DEFERRED_NO_AFFORDABLE_ELIGIBLE_PROJECT` for the pending bodies through 2226. **Not** `NO_POSITION_TABLE`, `TABLE_HORIZON`, or `FLIGHT_TIME` as start-decision reasons.
- `experiment.json:52-54` fixes geometry flight range at 45–1,400 days; `PR427_COMPLETE_MOON_GIANT_RENDEZVOUS_TEST_ONLY.py:49-60` prices the giant-system quotes from that range. A 3,500–4,000-day alternative has not been calculated.

## Existing positions and kernels

- `PR427_ASSIST_2035_NUMERIC_TABLE_MANIFEST_TEST_ONLY.json`: nine pinned planet position tables (EARTH, JUPITER, MARS, MERCURY, NEPTUNE, PLUTO, SATURN, URANUS, VENUS) run **2026-02-15 to 2035-12-31**. They do not cover arrivals in 2100 or 2226.
- `PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json`: four giant-planet parent tables end **2031-10-31**.
- `stage1_destination_lattice_first_slice/slice_manifest.json`: first-slice table ends **2031-10-31**, including PLUTO.
- `PHASE4E_RECOVERY_20261020/RECOVERY_RESULTS.json`: 34 existing small-body SPK files are labeled **2026–2251**; includes ARROKOTH, ATLAS3I, BORISOV, GONGGONG, IXION, MS4, OUMUAMUA, ORCUS, QUAOAR, SALACIA, SEDNA, SWIFTTUTTLE, VARUNA. They are recovery assets, not automatically accepted by the pinned 2035 table manifest.
- Existing `de440.bsp`, `phase4b/plu060.bsp`, `satellite_systems/nep097.bsp`, `sat441.bsp`, `ura184_part-3.bsp`, plus `phase4f_pluto6` continuations exist under `/home/ubuntu/loom_solar_assets/kernels/spk/`. Presence alone does not prove coverage at 2226 for each original kernel.
- `phase4f_pluto6/BUILD.json`: six-body **propagated estimates**, 2199–2251, not original pinned ephemeris truth. Pluto-system long-date states could be assembled from these plus appropriate parent/barycenter coverage, but must retain estimate status.

## Pluto six and a 3,500–4,000-day mission

**Plausible from local files for departures whose arrivals lie inside available kernel coverage; not yet a validated quote.** PLUTO, CHARON, HYDRA, NIX, KERBEROS and STYX have local `plu060` source and six-body propagated continuation files. The current pinned 2035 tables only support arrivals through 2035; extending the flight range and deriving new quote records is a separate future experiment. The continuation is estimated rather than original-kernel truth.

## External kernel/download needs

- **No external download is demonstrated necessary merely to inspect or test longer trips for the 30 priced candidates**: local original/recovery SPKs and satellite-system kernels already exist for many; their exact object/date coverage must be checked before declaring any specific 2100/2226 route computable.
- **DACTYL, SELAM**: local `phase4f_estimated_relative/estimated_dactyl_...bsp` and `estimated_selam_...bsp` exist, but their **missing gravity values** still prevent complete supported prices. New ephemeris downloads alone do not solve that.
- **PROTEUS**: local `phase4f_estimated_relative/estimated_proteus_808_2199_2251.bsp` exists; use with estimated provenance, not as an authoritative original kernel.
- **HYPERION**: local Saturn system `sat441.bsp` and `sat441xl_part-2.bsp` exist; whether Hyperion is covered over a requested long arrival interval requires object-specific SPK coverage inspection. The observed blocker is a missing supported quote, not proven missing position table.
- **No body can be honestly classified as requiring a new external download solely from these manifests**. A definitive per-body external-kernel shopping list requires object-ID and time-interval coverage checks against the local SPKs. Do not infer that the absence of a 2035 table means an external kernel is absent.

## Evidence limits

The price and project-start reports do not encode a counterfactual affordable flight duration. Do not assign the 1,400-day limit as a proved root cause for every deferred project. Nor do these files show which sponsor budget increase would suffice for each candidate.

## Database and delivery

DB SHA-256 before and after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
