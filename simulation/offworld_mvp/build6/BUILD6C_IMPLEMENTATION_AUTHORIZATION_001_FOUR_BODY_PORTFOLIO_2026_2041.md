# BUILD 6C IMPLEMENTATION AUTHORIZATION 001 — MOON / MARS / CERES / BENNU PORTFOLIO 2026–2041

Status: AUTHORIZED / MULTIPLE-BODY STRUCTURAL PORTFOLIO / SCENARIO-BOUND / NOT_EMPIRICALLY_VALIDATED

Parent frozen baseline:
`build6b-final-v1-2026-10-05`
-> `1581138edb2c5536b8f92aa42e47a92e6d2f78e1`

Branch:
`offworld-mvp-build6c-four-body-portfolio`

Governance dependency:
`BUILD6_EXPANSION_GATE_DISPOSITION_001_MULTIPLE_ECONOMIES_DEFERRED.md`

## Purpose

Run the first named-body Offworld portfolio qualification across calendar years 2026–2041
using:

- Moon;
- Mars;
- Ceres;
- Bennu.

The experiment asks:

> Given only admitted 2026 evidence and later study results, which bounded
> prospecting/project-study actions are authorized, started, completed, deferred or abandoned
> when all four projects compete for finite capital over real elapsed calendar time?

No project is required to become DEVELOPMENT_READY and no mine is required to be built.

## Calendar

Build 6C SHALL use explicit calendar simulation time.

Reference:

`2026-01-01 = calendar 2026.0`

Qualification horizon:

`2026.0 <= t <= 2041.999...`

Dates/opportunity windows may use fractional calendar years in the first structural run.
A future exact-date adapter may replace them without changing Agent semantics.

## Body / resource candidates

The first portfolio is restricted to:

1. **Moon polar volatiles**
2. **Mars hydrated/water-bearing material ISRU prospect**
3. **Ceres volatiles**
4. **Bennu hydrated/carbonaceous material prospect**

These labels identify project opportunity families, not economic reserves.

No opening recoverable tonnage may be inferred from body composition evidence.

## Evidence authority

Build 6C SHALL reuse promoted/qualified Solar evidence already present in the main repository
where available.

Pinned source baseline:

- main commit: `1581138edb2c5536b8f92aa42e47a92e6d2f78e1`;
- `dev/solar_civprop_m4b/campaign_assertions.json` blob
  `b936825faafb3efde094533a57ba2803747e8b37`;
- `dev/solar_civprop_m4b/reports/M4B_ASSERTION_PROVENANCE_LEDGER.csv` blob
  `a02bcbb6e724d3d1bd236cf9d6179ad6b6acfb4e`;
- `dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv` blob
  `94e8925fe2ef8fcb18a53f6f251b01326388171f`;
- Technology Timeline Register blob
  `3767610b337dde737eac5ef4147590b5ff3878c5`.

Research support is pinned separately from runtime authority:

- research repo main:
  `3825917e18f021f27e576b48ef87fbad897dd96e`;
- lead-time research note blob:
  `0125560433e8318a6ba6c5141288d02faa194fd1`;
- prospecting/decision-gate research note blob:
  `543bd739a2b513e00e29d083f5de167687799923`.

Research artifacts may justify authored scenario structure/ranges. They do not become hidden
world truth or canon.

## Required 2026 epistemic packet

The executable input fixture SHALL preserve body-specific evidence asymmetry.

### Moon

Admit the qualified `MOON_POLAR_WATER_ICE` assertion only at its preserved scope:

- VOLATILES;
- polar/selected surface footprints;
- PRESENT_UNQUANTIFIED;
- no global inventory;
- no local mineable abundance unless later prospecting earns it.

### Mars

Admit the qualified `MARS_GALE_HYDRATED_MINERALS` assertion only at preserved scope:

- site-scale Gale samples;
- hydrated minerals / volatile-bearing material;
- PRESENT_UNQUANTIFIED;
- not free-water abundance;
- not global Mars inventory;
- not proof of an accessible mid-latitude ice deposit.

Mars may therefore begin with scientifically meaningful water-bearing evidence while still
requiring new prospecting to establish a project-specific water/ISRU opportunity.

### Ceres

Admit qualified volatile evidence only with original epistemic limits, including:

- `SF3_MATERIAL_1`: enhanced hydrogen consistent with exposed water ice, abundance UNKNOWN;
- `SF3_MATERIAL_2`: reported water-vapor production rate retained as production rate, not
  surface abundance;
- `SF3_MATERIAL_6`: volatile-rich-shell physical-model interpretation, abundance UNKNOWN
  and not a resource-potential assertion.

No global recoverable water inventory may be fabricated.

### Bennu

Admit returned-sample evidence with explicit sample scope, including:

- `BENNU_HYDRATED_PHYLLOSILICATES`;
- optionally `BENNU_ORGANICS` as a distinct information attribute.

The returned sample establishes material composition at sampled material, not whole-body
recoverable tonnage, grade or mineability.

## Scenario lead-time / cost inputs

Build 6C may use authored deterministic structural scenario values for:

- study/prospecting cost;
- mission development;
- opportunity waiting;
- transit;
- campaign duration;
- analysis/publication latency.

Every such value SHALL carry:

- stable input ID;
- body/project scope;
- unit;
- authored scenario rationale;
- source/research references;
- `SCENARIO_NOT_CALIBRATED` standing.

No value may be represented as empirical truth merely because it is literature-informed.

The first qualification remains deterministic. No stochastic schedule risk is authorized.

## Technology Timeline standing

The Technology Timeline may constrain or annotate opportunity feasibility.

A date SHALL NOT:

- automatically authorize an Agent action;
- create installed capacity;
- create funding;
- create a launch/transport relationship;
- create a resource;
- make a project profitable.

Where the selected moderate scenario does not support a later development action, the project
may remain in study/prospecting state through 2041.

## Capital

All four projects compete for one finite structural sponsor/public prospecting pool.

The first qualification SHALL NOT add multiple economies.

Capital decisions use only admitted information and currently available funds.

Spending remains sunk through existing Build 6B ledger semantics.

## Project-study semantics

Build 6C reuses the Build 6B maturity ladder.

The qualification should exercise only the stages actually supported by the 2026–2041
scenario and admitted evidence.

No project may skip maturity edges.

No positive evidence automatically implies DEVELOPMENT_READY.

## Body timing

Build 6C SHALL demonstrate materially different elapsed information calendars by body.

At minimum:

- Moon must permit relatively short-cycle follow-up compared with deep-space targets;
- Mars must contain an explicit authored departure/opportunity cadence constraint consistent
  with the research-supported Earth–Mars launch-window phenomenon;
- Ceres must include materially longer remote/surface mission lead time than Moon;
- Bennu must distinguish high-quality returned-sample knowledge from the separate lead time
  required to obtain new body-wide/site-specific prospecting information.

Exact opportunity windows remain authored structural scenario inputs in Build 6C. SPICE
generation is not authorized in this slice.

## Selection policy

Build 6C may reuse the existing Test-only portfolio policy for affordability/priority only if
priority inputs are authored and declared.

However, the named-body qualification SHOULD prefer a bounded scenario decision rule that
can react to:

- current study maturity;
- admitted evidence standing;
- cost;
- time to next information;
- available capital.

It must not become a general portfolio optimizer.

If such a policy introduces a new ranking/threshold assumption that materially determines
the four-body history, that assumption must be explicit in the input manifest and validation.

## Acceptance

Build 6C passes only if:

1. Moon/Mars/Ceres/Bennu coexist as distinct named body/project opportunities;
2. 2026 evidence is body-specific and provenance-pinned;
3. no body receives fabricated abundance/tonnage;
4. multiple-economy machinery remains absent;
5. all four compete for one finite capital pool;
6. study spending is conserved and sunk;
7. projects execute asynchronously on calendar time;
8. body-specific opportunity/lead-time differences affect available actions;
9. future results do not leak backward;
10. the same evidence packet produces deterministic replay;
11. candidate ordering does not determine history accidentally;
12. no Technology Timeline date acts as an automatic unlock;
13. no project reaches DEVELOPMENT merely from a positive observation;
14. direct maturity skips remain blocked;
15. at least one rational deferral occurs because of capital/time/opportunity competition;
16. at least one project may fail/abandon or remain immature without qualification failure;
17. terminal 2041 standing is reported for all four projects;
18. full semantic trace can be rendered as:
    KNOW -> BELIEVE/STATE -> DECIDE -> COMMIT/SPEND -> WAIT/EXECUTE -> RESULT -> ADMIT -> REVIEW;
19. focused/hostile tests pass;
20. full governed regression passes;
21. executable source is Git-object hash verified;
22. guiding FRD remains byte-unchanged.

## Explicitly not authorized

Build 6C does not authorize:

- multiple Earth economies;
- country policy;
- endogenous commodity prices;
- macroeconomic feedback;
- stochastic schedule risk;
- SPICE-derived opportunity calculation;
- mine construction merely because a project reaches FEASIBILITY;
- settlement;
- inter-body trade;
- detailed fleet/launch-market simulation;
- hidden calibrated resource inventories;
- empirical prediction of what humanity will actually do by 2041.

## Closure standing

Passing Build 6C earns only a deterministic named-body 2026–2041 project-study portfolio
qualification.

Any move into stochastic scheduling, multiple economies, development construction or
coupled markets requires a separate authorization.
