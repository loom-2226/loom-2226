# BUILD 6C VALIDATION RECORD 001 — FOUR-BODY PORTFOLIO 2026–2041

Status: **STRUCTURAL PASS / GOVERNED MULTIPLE-BODY EXPANSION / SCENARIO-BOUND / SINGLE EARTH ECONOMY / NOT_EMPIRICALLY_VALIDATED**

## Authority

Frozen Build 6B parent: `build6b-final-v1-2026-10-05` at `1581138edb2c5536b8f92aa42e47a92e6d2f78e1`.

Expansion disposition:
`BUILD6_EXPANSION_GATE_DISPOSITION_001_MULTIPLE_ECONOMIES_DEFERRED.md`

Authorization:
`BUILD6C_IMPLEMENTATION_AUTHORIZATION_001_FOUR_BODY_PORTFOLIO_2026_2041.md`

Executable/ODD qualification candidate:
`eca209ffff0f679981bfce184e67d2bdf25c1437`

Branch:
`offworld-mvp-build6c-four-body-portfolio`

The guiding FRD is byte-unchanged relative to frozen Build 6B.

## Expansion-gate standing

The FRD recommends:

`multiple projects -> multiple economies -> multiple bodies/resources`

while requiring each expansion to earn its complexity through causal need.

Build 6C explicitly defers, rather than deletes, the multiple-economies rung. The immediate experiment requires physically distinct bodies because admitted evidence, opportunity timing, study lead time and information arrival differ by target. A second Earth economy is not needed to answer that question.

Multiple economies remain deferred for later work involving distinct capital sources, buyers, ownership/distribution, trade counterparties, country policy or country-level economic consequence coupling.

Build 6C uses exactly one Earth economy and one finite sponsor capital pool.

## Purpose

Build 6C asks how Moon, Mars, Ceres and Bennu compete for finite project-study capital from 2026 through 2041 given only admitted 2026 evidence plus later scenario study results.

No project is required to become DEVELOPMENT_READY, enter DEVELOPMENT or build a mine.

## Calendar and scenario

Reference: `2026-01-01 = 2026.0`.

Horizon: `2026.0 <= t <= 2041.999`.

Scenario input:
`simulation/offworld_mvp/build6/inputs/BUILD6C_2026_2041_PORTFOLIO_SCENARIO_V0_1.json`

Scenario SHA-256:
`be4de46ef8182949e99dd119f794eca9190edc7de0568f59a03a7cd05867e502`

Standing:
`PRE_CONTRACT_AUTHORED_STRUCTURAL_SCENARIO_NOT_EMPIRICALLY_VALIDATED`

Costs, durations, opportunity windows and future study-result standings are deterministic authored scenario values, not empirical predictions.

## Pinned evidence authority

Main evidence baseline:
`1581138edb2c5536b8f92aa42e47a92e6d2f78e1`

Pinned promoted Solar sources:

- `campaign_assertions.json` blob `b936825faafb3efde094533a57ba2803747e8b37`
- `M4B_ASSERTION_PROVENANCE_LEDGER.csv` blob `a02bcbb6e724d3d1bd236cf9d6179ad6b6acfb4e`
- `M4B_COVERAGE_MATRIX.csv` blob `94e8925fe2ef8fcb18a53f6f251b01326388171f`
- Technology Timeline blob `3767610b337dde737eac5ef4147590b5ff3878c5`

Pinned research context:

- research main `3825917e18f021f27e576b48ef87fbad897dd96e`
- lead-time note blob `0125560433e8318a6ba6c5141288d02faa194fd1`
- prospecting/decision-gate note blob `543bd739a2b513e00e29d083f5de167687799923`

The runtime scenario loader verifies local Git blob identity for pinned promoted sources before execution.

## Opening evidence asymmetry

### Moon

Project: `PROJ:MOON:POLAR_VOLATILES`

Opening maturity: `REMOTE_CHARACTERIZED`

Evidence: `MOON_POLAR_WATER_ICE`

Standing remains footprint-scoped and `PRESENT_UNQUANTIFIED`. No global inventory, project-site recoverable tonnage or mineable grade is inferred.

### Mars

Project: `PROJ:MARS:WATER_ISRU`

Opening maturity: `SCREENED`

Evidence: `MARS_GALE_HYDRATED_MINERALS`

This preserves high-confidence Gale site-scale hydrated-mineral evidence, but not free-water abundance, a global inventory or proof of an accessible project-site ice deposit.

### Ceres

Project: `PROJ:CERES:VOLATILES`

Opening maturity: `REMOTE_CHARACTERIZED`

Evidence:

- `SF3_MATERIAL_1`: enhanced hydrogen consistent with exposed water ice, abundance UNKNOWN
- `SF3_MATERIAL_2`: water-vapor production rate preserved as production rate, not abundance
- `SF3_MATERIAL_6`: volatile-rich-shell physical-model interpretation, not a resource-potential assertion

### Bennu

Project: `PROJ:BENNU:HYDRATED_CARBONACEOUS`

Opening maturity: `SURFACE_OR_SAMPLE_CHARACTERIZED`

Evidence:

- `BENNU_HYDRATED_PHYLLOSILICATES`
- `BENNU_ORGANICS`

Returned samples justify higher opening characterization maturity but do not establish whole-body abundance, recoverable tonnage or mineability.

## New structural state

Build 6C adds provenance-bearing:

- `NamedBodyEvidenceRecord`
- `BodyPortfolioBinding`
- `Build6CActivitySpec`
- `Build6CPortfolioScenario`

These bind body -> OFFWORLD node -> project -> opening study maturity -> admitted evidence without creating hidden resource inventory.

## Technology Timeline standing

The canonical fixture creates zero `TechnologyCapabilityState` records and zero transport relationships.

Therefore no Technology Timeline date automatically unlocks an action in this qualification.

## Canonical capital state

Opening sponsor cash: `220`

Replenishment: `NONE`

Earth economies: `1`

Named offworld bodies: `4`

Terminal accounting:

- sponsor cash: `0`
- supplier cash: `220`
- paid study spend: `220`
- knowledge-asset book value: `220`
- economic transactions: `14`
- persistent decision epochs: `30`

## Canonical semantic history

At 2026.25 the sponsor authorizes four initial activities in stable priority order:

1. Bennu resource assessment, cost 15
2. Mars regional remote screening, cost 20
3. Moon polar surface prospecting, cost 35
4. Ceres dedicated volatile characterization, cost 70

Moon and Ceres wait for authored opportunity windows. Bennu and Mars start immediately.

### Bennu

- 2026.25: A1 starts; 15 spent
- 2027.00: SUPPORTS_ADVANCE result completes
- 2027.01: result admitted
- 2027.02: maturity advances to RESOURCE_ASSESSMENT
- 2027.10: concept-scoping study starts; 25 spent
- 2028.10: result is INSUFFICIENT
- 2028.12: review DEFER

Terminal Bennu: `EXPLORING / RESOURCE_ASSESSMENT`, spend 40.

### Mars

- 2026.25: regional screening starts; 20 spent
- 2027.75: SUPPORTS_ADVANCE result completes
- 2027.77: maturity advances to REMOTE_CHARACTERIZED
- 2027.78: proposed 60-unit landed campaign DEFERRED for insufficient available capital
- 2030.50: at its authored opportunity, the same campaign is again DEFERRED for insufficient available capital

Terminal Mars: `EXPLORING / REMOTE_CHARACTERIZED`, spend 20; landed campaign remains PROPOSED.

The deferral is caused by finite portfolio capital, not hidden Mars resource truth.

### Moon

- 2026.25: surface campaign authorized and waits
- 2027.50: campaign starts; 35 spent
- 2029.00: SUPPORTS_ADVANCE result completes
- 2029.02: maturity advances to SURFACE_OR_SAMPLE_CHARACTERIZED
- 2029.10: resource-assessment study starts; 30 spent
- 2030.60: result is INSUFFICIENT
- 2030.62: review DEFER

Terminal Moon: `EXPLORING / SURFACE_OR_SAMPLE_CHARACTERIZED`, spend 65.

### Ceres

- 2026.25: long campaign authorized and waits
- 2028.50: campaign starts; 70 spent
- 2034.50: SUPPORTS_ADVANCE result completes
- 2034.52: maturity advances to SURFACE_OR_SAMPLE_CHARACTERIZED
- 2034.60: resource-assessment study starts; final 25 spent
- 2035.60: SUPPORTS_ADVANCE result completes
- 2035.62: maturity advances to RESOURCE_ASSESSMENT

Terminal Ceres: `EXPLORING / RESOURCE_ASSESSMENT`, spend 95.

No further scenario activities occur after 2035.62, so this state persists unchanged through 2041.

## 2041 terminal state

| Body | Project lifecycle | Study maturity | Spend | Key unresolved standing |
|---|---|---|---:|---|
| Bennu | EXPLORING | RESOURCE_ASSESSMENT | 40 | Concept evidence insufficient |
| Ceres | EXPLORING | RESOURCE_ASSESSMENT | 95 | No concept/PFS/FS earned |
| Mars | EXPLORING | REMOTE_CHARACTERIZED | 20 | Landed campaign never funded |
| Moon | EXPLORING | SURFACE_OR_SAMPLE_CHARACTERIZED | 65 | Resource assessment insufficient |

No project is in DEVELOPMENT.
No project is DEVELOPMENT_READY.
No mine exists.
No settlement exists.

## Determinism and hostile coverage

Eight Build 6C tests verify:

1. canonical four-body history and deterministic replay;
2. initial candidate order does not alter history;
3. 2026 evidence is pinned and scope-limited with no fabricated resource scalar fields;
4. evidence-source blob tampering is rejected;
5. exactly one Earth economy is present and technology/transport state is absent;
6. body/project/evidence bindings are distinct and consistent;
7. all events remain inside the 2026–2041 horizon and body-specific waits differ;
8. Mars's later surface campaign is capital-blocked while hidden resource truth is absent.

Focused inheritance:
`28/28 PASS` in 92.663 s.

Broader accounting/scheduler/firewall regression:
`76/76 PASS` in 107.281 s.

Full governed regression:
`337/337 PASS` in 722.686 s.

All 329 frozen Build 6B tests remain present and pass. Build 6C adds eight tests.

## Executable provenance

Filesystem executable source-tree SHA-256:

`069a798b0a4ce89b854d351134e7bc74c60d38c110790bc5d786f6400bc9c052`

Git-object reconstructed executable source-tree SHA-256:

`069a798b0a4ce89b854d351134e7bc74c60d38c110790bc5d786f6400bc9c052`

Standing: `GIT_OBJECT_VERIFIED`.

## Size / bloat

Executable package LOC:

- frozen Build 6B: 12,141
- Build 6C candidate: 12,628
- net: +487 lines, 4.01%

No second scheduler, ledger, Project lifecycle, Agent hierarchy or macroeconomic engine was introduced.

## FRD / ODD standing

Guiding FRD diff from frozen Build 6B: `0` lines.

Executable ODD registry: `ODD_SCHEMA_REGISTRY_0_19`.

Build 6C activates an existing multiple-body/resource expansion rung under an explicit governed deferment of the multiple-economy rung. It does not rewrite the FRD.

## Explicitly not earned

Build 6C does not earn multiple Earth economies, country policy, empirical prediction of the 2026–2041 history, calibrated costs/durations, stochastic schedule risk, SPICE-generated windows, exact mission architecture, endogenous resource quantity/grade, endogenous prices, general portfolio optimization, development construction, mine engineering, settlement, inter-body trade or coupled macroeconomics.

## Conclusion

Build 6C structurally earns a deterministic named-body project-study portfolio across Moon, Mars, Ceres and Bennu from 2026 through 2041.

The result is deliberately not a mine forecast. The four opportunities consume finite capital on different information calendars and end at different knowledge/maturity states. Strong evidence can still produce an insufficient study; a promising Mars campaign can remain unfunded; a long Ceres campaign can dominate capital for years; and no positive result automatically creates a mine.
