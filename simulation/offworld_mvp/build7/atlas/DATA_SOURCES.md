# Build 7 source semantics and PostgreSQL lineage audit

**Audit scope:** generated-world 2026–2035 path at source commit `66c641d25e641e0aff77940a8cadbf1653247113`; inspected PostgreSQL **isolated test runtime** `loom_b7_health_isolated_20261010` on 2026-10-10. Counts below are observations of this database, **not schema invariants or global production counts**. No writes were made to the database.

## Semantic hierarchy: what each source is

| Source | Declared standing and metadata | Role in Build 7 | Limits / provenance |
|---|---|---|---|
| `BUILD7_EARTH_USA_2026_2045_V1.json` | `DERIVED_READ_ONLY_SLICE_OF_CURRENT_PROMOTED_EARTH_AUTHORITY`; `source_snapshot_id=earth-v0-1-9934d0ac-20260925`; promotion SHA, active economic/demographic pointers, source model, USA 2026–2045 coverage | 20 annual USA demographic/economic/legacy labor rows; loader maps population, value added, gross output, investment, capital, legacy employment to explicitly typed `MODEL_PROJECTION` context values; annual `record_earth_reference_year` consumes 2026–2035; investment feeds country capital mobilization | Projected reference, **not realized observed 2035 GDP or spendable money**; 237 demographic areas/80 economies in source coverage metadata do **not** mean the runtime models 237 countries |
| `BUILD7_SOLAR_BODY_CATALOG_V1.json` | `PINNED_READ_ONLY_PROJECTION_OF_CURRENT_LOOM_SOLAR_AUTHORITY`; eligible-body count 90, supporting bodies, source refs and SHA256 row digests | Installs stable body identity in `wa_geo.body`; feeds visible mission candidates and world generation | Named-body identity is not physical deposit truth, mission feasibility or empirical survey evidence |
| `BUILD7_SOLAR_ACCESSIBILITY_REFERENCE_V1.json` | `ENGINEERING INPUT AUTHORITY MAP — NOT A ROUTE TABLE`; 83 DERIVABLE, 7 UNKNOWN; public ephemeris refs, NAIF identifiers, qualification status, external JPL Horizons method basis | Establishes whether public qualified ephemeris support exists; compiled screen checks its SHA | DERIVABLE **does not mean feasible, affordable or navigable**; external Horizons basis is not itself the runtime route authority |
| `BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1.json` | `ENGINEERING_PRELIMINARY_TRANSFER_SCREEN_NOT_MISSION_DESIGN`; source manifests, method, reference SHA, sampled departure/TOF/v-infinity/transfer burden; 90 × 10 = 900 rows | PUB receives annual SCREENED/UNKNOWN status and PRELIMINARY_COMPARABLE where capability allows | Preliminary transfer screen, **not qualified mission design**, transport operation or trajectory execution |
| `BUILD7_MISSION_COSTS_2026_2035_PROVISIONAL_V1.csv` | Explicit **PROVISIONAL** table; year/body/mission type, spacecraft mass, departure/arrival, flight days, v-infinity, C3, one-way cost USD millions, `method` | `MissionCostLookup` validates rows; 5,400 rows in loaded profile; `ORBITAL_RECON` mission costs are converted to model currency by ×0.001, and drive PUB affordability **and least-cost selection** | This is an **authored cost surrogate**, not observed procurement cost or exchange rate. Missing/NO_TRAJECTORY is unavailable, not zero cost |
| `BUILD7_GENERATED_CAMPAIGN_V1.json` | `FORWARD_SIMULATION_BASELINE_STRUCTURAL_PARAMETERS`; policy seed, comparison group, account and study parameters, fixed 2026 recovery profile | Kernel and decision configuration, run identity, authored policy parameters | Fixed profile explicitly `STRUCTURAL_2026_CAPABILITY_NOT_EMPIRICALLY_CALIBRATED`; configured values do not prove a pathway is exercised |
| `BUILD7_MATERIAL_FAMILY_PRIORS_V1.json` | `HIGH_SENSITIVITY_FICTIONAL_SCENARIO_INPUT_NOT_EMPIRICAL_OCCURRENCE_PROBABILITY`; four material families, regime groups, authored presence probabilities, volatile consistency, empirical material handling | Consumed by `build6e/generated_world.py`; seeded world generation creates sealed body/region material truth | No whole-body extrapolation from local samples; UNKNOWN is **not zero or negative evidence**; no grade/reserve/recoverability/economic meaning |
| `BUILD7_PROSPECTING_ECONOMICS_V1.json` | `AUTHORED_HIGH_SENSITIVITY_FICTIONAL_SCENARIO_PARAMETERS`; parameter semantics, authorization, exclusions, mobilization formula | Required regional capital=2; information value=3; investment normalization 1e9 and mobilization m_max=0.001, gated by commercial opportunity or strategic pressure | These are **scenario choice thresholds**, not market-observed prices, reserve value or a fitted investment response |
| `BUILD7_TIMELINE_SNAPSHOT_V1.json` | `READ_ONLY_TIMELINE_CONTEXT`; 43 milestones, projection manifest, interpretation rules | Admitted and hash-pinned context | `auto_unlock=false`: date alone does not grant capability |
| `BUILD7_RESOURCE_RETURN_SCENARIOS_V1.json` | `AUTHORED_FICTIONAL_SCENARIO_NON_CANON_NOT_OBSERVATION`; illustrative revenue, operating cost, capital assumptions | Loaded by `resource_returns.compare_returns` for **offline illustrative comparisons** | Not evidence of realized sales, operating production or recurring investment return in annual campaign |
| `BUILD7_ECONOMIC_USES_SCENARIO_V1.json` | `AUTHORED_SCENARIO_NON_CANON_NON_EMPIRICAL`; potential uses by family, demand_required=true, `economic_reserve_from_family_presence=UNKNOWN` | **Reference-only in audited annual path**; no loader call from generated annual conductor | Potential uses **do not establish buyers, demand, prices, reserves or profitability**. Its `currency_bridge.conversion=UNDEFINED_DO_NOT_COMBINE` applies to this reference document, **not** the separate active mission-cost normalization |

## PostgreSQL: semantic layers, not interchangeable tables

| Schema.table | Metadata and observed structure | Interpretation and read path |
|---|---|---|
| `wa_geo.body` | `semantic_key`, `canonical_name`, `body_class`, `parent_body_id`, `status_lexeme`, `original_ref`; 100 rows observed | **Reference identity**, not hidden composition; includes supporting bodies beyond 90 eligible. `store.install_generation_body_catalog` binds stable UUID identities |
| `wa_geo.location` | `location_kind`, `origin_kind`, `geometry_id`, `source_ref`, `notes`; 1,181 rows observed, including **900** `AUTHORED_SPATIAL_ANCHOR` REGION rows | Prospecting regions are authored **identity partitions**, not empirical GIS deposit polygons; geometry may be NULL. Other rows include empirically identified locations and must not be conflated |
| `wa_world.generation_model` | `semantic_key`, `version`, `status_lexeme`, `implementation_sha256`, `implementation_locator`, `model_family_ref`, `uncertainty_contract_ref`, `parameter_schema_ref` | Model provenance; observed `SOLAR_WATER_BLOCK_COMPILER_V1`, status `AUTHORED_SCENARIO_MODEL` |
| `wa_world.generation_policy` | `policy_type_lexeme`, JSONB `parameters`, `parameter_schema_ref`, `policy_sha256`, `authorization_ref`; 90 rows | Authored conditional priors, not scientific assertions. Observed policy carries `AUTHORED_V0_3_CONDITIONAL_PRIOR`, high sensitivity, material-family policy hash, source snapshot SHA, `regional_presence_fraction=0.35` |
| `wa_world.scenario` | `world_context`, `definition_locator`, `definition_sha256`, `authorization_ref` | Scenario identity and authorization; observed locator `simulation/offworld_mvp/build6e/generated_world.py` |
| `wa_world.realization` | `world_seed_lexeme`, `seed_lineage_ref`, `random_algorithm_ref`, `key_schema_ref`, `constraints_digest`, `generator_output_sha256`, `world_context`; 900 rows observed | **Sealed generated WORLD realizations**, multiple campaigns/seeds in isolated DB, not 900 bodies or observed celestial discoveries |
| `wa_world.physical_property` | `property_code`, `value_domain`, `physical_semantics_ref`, `schema_ref` | Semantic lookup defining physical meaning; e.g. `R_RESERVE` has `ECONOMIC_RESERVE_UNKNOWN`, while `R_IN_SITU` and `R_ACCESSIBLE` have different semantics |
| `wa_world.hidden_state` | `property_code`, `value_state`, `numeric_value`, `unit_key`, `model_family_ref`, `uncertainty_ref`, `derivation_ref`, `value_sha256`; 58,500 rows observed | **WORLD_SIM-only synthetic physical state**, not Agent knowledge or measured fact. Observed family-presence rows use `GEN_FRACTION_V1` and `SOLAR_WATER_BLOCK_COMPILER_V1` |
| `wa_world.deposit` | `resource_class`, `initial_in_situ_state`, `concentration_state`, `geometry_class_lexeme`, `provenance_ref` | Synthetic generated resource/deposit state; **in situ is not automatically recoverable or an economic reserve** |
| `wa_info.agent_snapshot`, `belief`, `decision` | Actor-specific information and decision records | **Agent perspective** and decision evidence, distinct from hidden `wa_world` state |
| `wa_run.artifact` | `record_kind`, `serializer_ref`, `payload_bytes`, `payload_sha256`; 16,240 rows observed | Persisted REQUEST, DECISION_STATE, DECISION, INFORMATION_STATE, ADMITTED_INFORMATION and transition artifacts; use for exact decision provenance, not invented rationale |
| `wa_run.causal_envelope` | `event_ordinal`, `actor_ref`, `process_ref`, `action_ref`, `reason_code`, time fields, pre/post hashes, trace hashes; 2,872 rows observed | **Ordered realized causal trace**; not itself a complete explanation of a policy's admitted facts |
| `wa_run.accessibility_assessment` | 0 rows observed | **Not the source of the 900 annual public accessibility rows.** Those are in pinned JSON `BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1.json` |

**Database metadata caveat:** The inspected runtime account exposes no `wa_meta` tables via `information_schema.tables`, despite the schema existing. Source code declares `wa_meta.source_snapshot` in its fixed table specifications, but this audit **cannot claim live rows or permissions for that table**. No PostgreSQL table comments were present in the visible `wa_*` table set. Column semantics above are grounded in field names, declared source metadata, stored model/policy fields and their consumers, **not fabricated SQL comments**.

## Data flow with explicit boundaries

```text
PROMOTED / PUBLIC REFERENCE INPUTS (JSON + CSV, pinned digests)
    Solar catalog -> wa_geo body/location identities -> visible PUB candidates
    Accessibility authority map -> compiled public screen -> PUB eligibility
    Provisional mission-cost CSV -> PUB affordability and lowest-cost selection
    Earth USA projection -> typed Earth reference -> country-capital proxy
    Technology timeline -> read-only context, no automatic unlock

AUTHORED GENERATIVE SCENARIO
    Material family priors + generation policy + seed
        -> wa_world realization / hidden_state / deposit
        -> [authorized WORLD_SIM observation transition ONLY]
        -> noisy observation -> PUB belief -> published evidence -> SPN belief

AUTHORED ECONOMIC DECISION INPUTS
    Prospecting capital / information value + mobilized F + SPN evidence
        -> SPN policy requests / admitted snapshots / decisions
        -> system epochs -> project/study/financing consequences

PERSISTENCE
    wa_info: Agent-perspective information and decisions
    wa_run.artifact: serialized requests, snapshots, decisions, realized states
    wa_run.causal_envelope: ordered events, time, actors, hashes
```

## Corrections to earlier atlas wording

1. The reference accessibility map is **not** a route table. The separate compiled screen contains sampled preliminary transfers. The mission-cost CSV is a third source, not a field in the screen.
2. The Earth reference is a **promoted projection**; calling it observed current economic cash would be false.
3. `wa_geo.location` region identity does not establish physical survey geometry.
4. Generated material presence is neither a measured deposit nor a reserve. `wa_world.physical_property` explicitly distinguishes in-situ, accessible, recoverable and unknown economic reserve.
5. PostgreSQL `wa_run.accessibility_assessment` is **empty in the inspected DB** and must not be drawn as the source of public accessibility candidates.
6. A source file can be valid research/reference content without being **consumed by the annual runtime**. `BUILD7_ECONOMIC_USES_SCENARIO_V1.json` and offline return scenarios must remain outside active causal diagrams.

## Audit limits

The live PostgreSQL inspection used the isolated test runtime and current privileges; it does not prove production metadata state. Table counts aggregate multiple runs and seeds. This is a source/metadata semantic audit, not independent replay qualification or proof of every simulated physical assumption. No Build 7 runtime behavior or database records were changed.
