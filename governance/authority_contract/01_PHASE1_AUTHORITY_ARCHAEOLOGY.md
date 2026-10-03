# LOOM Authority Archaeology and Source Inventory
## Phase 1 Working Record — Pass 1

**Date:** 2026-10-03  
**Owner:** @kT  
**Branch:** `authority-contract-v1-phase0`  
**Status:** PRE-CONTRACT / DESCRIPTIVE ARCHAEOLOGY / CANDIDATE  
**Governing predecessor:** `00_AUTHORITY_PROBLEM_STATEMENT.md`, Revision 3, Phase 0 CLOSED

## 1. Method

This record begins Phase 1 under §34 of the Phase 0 authority statement.

Rules for this phase:

- inspect actual holdings;
- do not silently repair defects;
- do not grandfather historical qualification into v1 qualification;
- classify every archaeology answer as `ESTABLISHED`, `NOT LOCATED`, or `NOT ESTABLISHED`;
- require identifiable evidence for `ESTABLISHED`;
- treat all archaeological classifications and proposed mappings as CANDIDATE until human acceptance;
- preserve the distinction between GitHub authority records, VM-resident artifacts, PostgreSQL projections, SQLite holdings, scenario material, and simulated outputs.

Pass 1 inspected current GitHub `main` and read-only state on the connected `quantifactus` VM. It did not modify source holdings.

## 2. Evidence Boundary Recorded in Pass 1

### GitHub

Repository: `loom-2226/loom-2226`.

The Phase 0 branch was created from current `main` at `27c5a4cb0b968baed219ffde48c550db6690a3c7`. Phase 1 archaeology treats current-main holdings as evidence and previous CIVPROP implementations as archaeology, not inherited architecture.

### quantifactus

The VM contains numerous historical LOOM worktrees/artifact directories, including Earth, Solar, CIVPROP, qualification, recovery and experimental runs. Their existence does not establish current authority.

The local `/home/ubuntu/LOOM_DEV` Git worktree is **not** current main. At inspection it was on `fix/ceres-atlas-display-semantics-20260921` at `625e139a32f3461068e2b84192725e79f42a4c89` with modified and untracked files. It is therefore evidence of historical/local state only and shall not be treated as the branch authority for this Phase 1 work.

PostgreSQL database `loom_dev` is live and contains schemas:
`loom_control`, `loom_earth`, `loom_solar`, `loom_timeline`, `loom_narrator`, and `loom_gate_l_qual`.

Observed direct row counts include:

| Relation | Rows |
|---|---:|
| `loom_control.snapshot` | 2 |
| `loom_control.source_artifact` | 18 |
| `loom_earth.earth_area` | 237 |
| `loom_earth.earth_demographic_year` | 47,637 |
| `loom_earth.earth_economic_year` | 16,080 |
| `loom_earth.earth_sector_year` | 160,800 |
| `loom_solar.body` | 110 |
| `loom_timeline.milestone` | 43 |

The two observed PostgreSQL snapshot IDs are:
- `earth-v0-1-9934d0ac-20260925`
- `timeline-v0-1-0232bf23494f-20260925`

This is an inventory fact, not a v1 qualification.

## 3. Domain Inventory — Initial Findings

### Q1. What artifacts supply Earth information?
**ESTABLISHED — partial inventory.**

Evidence located:
- `manifests/earth_long_run_economic_baseline/` with current pointers, promotion records, model specifications, field semantics, provenance and qualification records.
- VM-resident promoted Earth artifacts under `/home/ubuntu/loom_earth_2026_2035/`.
- PostgreSQL `loom_earth` projection with annual demographic, economic, sector, asset and labor/cohort relations.
- `loom_control.temporal_coverage` records separate 237-area demographic coverage from 80-economy economic coverage and record modeled/superseded periods.
- `loom_control.source_artifact` hash-pins WPP source files and promoted/model output files with source Git commits and retained locations.

Finding: “Earth” is not one homogeneous authority. It contains source evidence, modeled reference trajectories, promoted successors, semantic records and operational projections.

### Q2. What artifacts supply technology/scenario information?
**ESTABLISHED — initial inventory.**

Evidence located:
- `docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md`.
- `data/postgres/migrations/010_timeline_projection.sql`.
- `docs/database_semantics/LOOM_TIMELINE_POSTGRES_PROJECTION_v0.1.md`.
- PostgreSQL `loom_timeline`.

Observed PostgreSQL milestone classes:
- 19 `CANON_HISTORY / GOVERNING_CANON / CANON_HISTORY`;
- 18 `MODERATE_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / AUTHOR_SCENARIO_MODERATE`;
- 5 `FICTIONAL_PHYSICS_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / SPECULATIVE_FICTION`;
- 1 `SOCIAL_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / AUTHOR_SCENARIO_MODERATE`.

Finding: timeline storage already preserves materially different authority/epistemic classes. PostgreSQL storage is explicitly not promotion.

### Q3. What artifacts supply Solar information?
**ESTABLISHED — partial inventory.**

Evidence located:
- PostgreSQL `loom_solar` identity/metadata/ephemeris relations, including 110 bodies.
- Solar identity/ephemeris contracts and SPICE foundation material.
- `dev/solar_civprop_m4b/` candidate material-evidence campaign.
- M4-B reports including qualification, coverage, hostile validation and unresolved frontier.
- VM copy `/home/ubuntu/LOOM_SOLAR_ENRICHMENT_TARGETS_2026-10-03/LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3`.

M4-B records 380 body×resource-family lanes across 95 eligible bodies, 37 supported lanes and 343 `UNKNOWN_AFTER_SEARCH` lanes. Candidate material evidence remains distinguishable from promoted information.

Finding: “Solar” contains at least identity, physical/metadata, ephemeris/spatial, empirical material evidence, coverage state and model/transport-related families. It is not a single authority class.

### Q4. What artifacts define actors?
**ESTABLISHED — incomplete and semantically split.**

Evidence located:
- `governance/agents/AGENT_REGISTRY.yml` defines autonomous LOOM technical agents, not necessarily CIVPROP civilization actors.
- `engineering/civprop/contracts/actor_state_v1.py` defines historical CIVPROP actor-state machinery.
- CIVPROP compiled inputs and scoped actor-access evidence exist for actors such as `AUS`.
- Prior CIVPROP documentation explicitly notes gaps in generic actor technology/access/budget evidence.

Finding: no single canonical “agent/actor registry” has yet been established for the future CIVPROP meaning. Technical LOOM agents and simulated civilization actors must not be conflated.

### Q5. What relevant sources exist outside those domains?
**ESTABLISHED — initial inventory.**

At least:
- governing canon chronology;
- physical/spatial/ephemeris authority;
- transport/accessibility models;
- resource economics;
- institutional/governance records;
- database semantic dossiers and recovery records;
- qualification/test artifacts;
- physical-law and mathematical machinery;
- identifier and vocabulary contracts.

This confirms that the earlier four-domain picture is an organizational convenience, not a complete authority model.

### Q6. Where do physical-law and transport authorities reside?
**ESTABLISHED — partial inventory.**

Evidence located in Solar spatial foundation, SPICE/DE440 ephemeris machinery, transport/accessibility contracts and Lambert-related CIVPROP/engineering artifacts. Existing documentation distinguishes qualified local SPICE state from Lambert accessibility modeling and from later propulsion models.

The complete authority-root treatment remains NOT ESTABLISHED pending deeper inventory.

### Q7. What institutional/governance rules exist?
**ESTABLISHED — partial inventory.**

Evidence includes current canon/governance records, historical qualification/promotion decisions, Phase 0 governance, source-role classifications, and technical agent registry/governance material.

A complete institutional-authority inventory is not yet established.

### Q8. What model parameters exist explicitly or implicitly?
**NOT ESTABLISHED.**

Explicit parameters are known to exist across Earth models, technology scenarios, transport, resource economics and historical CIVPROP machinery, but Phase 1 has not yet produced a complete parameter inventory or separated fitted, assumed, derived and hard-coded values.

### Q9. Which artifacts carry provenance?
**ESTABLISHED — partial inventory.**

Examples include Earth `PROVENANCE.md` and run/baseline manifests, PostgreSQL `loom_control.source_artifact`, source Git commits, SHA-256 records, timeline source links, M4-B evidence/coverage lineage and CIVPROP compiler manifests.

Completeness across holdings is not yet established.

### Q10. Which carry qualification or promotion status?
**ESTABLISHED — partial inventory.**

Earth promotion/qualification records, M4-B qualification/hostile-validation reports, timeline authority/epistemic classes, Solar qualification artifacts and numerous historical CIVPROP qualification/gate records exist.

Historical labels do not equal v1 qualification under D0.6/D0.19.

## 4. Immediate Archaeological Findings

1. **The VM is not itself an authority root.** It contains many mutually historical worktrees, databases and generated artifacts.
2. **The live PostgreSQL projection is richer than the four-pillar shorthand.** It already carries snapshots, source artifacts, temporal coverage and multiple semantic classes.
3. **Current PostgreSQL does not contain the full Solar material-evidence campaign.** Solar identity/ephemeris and M4-B material evidence currently span different representations.
4. **Earth reference material is explicitly modeled and coverage-limited.** 237-area demographic coverage must not be silently equated to 80-economy economic coverage.
5. **Technology/scenario separation is already encoded in several places.** That historical design is evidence for Phase 2, not automatically the final v1 taxonomy.
6. **Actor authority remains structurally weak compared with Earth/Solar/timeline holdings.**
7. **Previous CIVPROP code is evidence of prior design decisions and defects, not the architecture of the new CIVPROP.**

## 5. Pass 1 Next-Pass Plan (superseded by Pass 2 below)

Pass 2 shall continue Q11–Q40 and deepen Q1–Q10 where current answers are explicitly partial. Priority targets are:

- observation vs projection;
- UNKNOWN vs zero/absence;
- uncertainty representation;
- candidate vs promoted state;
- simulated/reference mixing;
- consumers and transformations;
- qualification mechanisms;
- shared/incompatible identifiers;
- authority by convention and missing apparent authorities;
- assumptions and mutability;
- causal reproducibility;
- AI/automation provenance and human approvals;
- fallback/imputation/interpolation/clamping/default/null-coalescing;
- units/currency/base year;
- knowledge time;
- crosswalks;
- feedback/calibration/fitting;
- code recoverability;
- test/gate coverage;
- conflicts;
- unknown-dropping joins/filters/aggregations;
- additional authority roots;
- physical-law/mathematical authority;
- temporal leakage.

No repair is authorized by this record.


## 6. Pass 2 — Archaeology Questions Q11–Q40

Pass 2 remains descriptive and PRE-CONTRACT. The classifications below are candidate archaeological findings, not v1 qualification.

### Q11. Which distinguish observation from projection?
**ESTABLISHED — partial inventory.**

Earth records distinguish observed/source material from modeled future state in manifests, provenance and field semantics. Timeline records distinguish `CANON_HISTORY`, authored scenario anchors and speculative-fiction anchors. Solar M4-B distinguishes evidence assertions from unresolved lanes. The distinction exists, but no common LOOM-wide claim taxonomy has yet been established.

### Q12. Which distinguish unknown from zero/absence?
**ESTABLISHED — strong examples, incomplete system coverage.**

M4-B explicitly defines `UNKNOWN_AFTER_SEARCH` as neither absence nor zero. Its hostile validation includes an `UNKNOWN_TO_ZERO` negative fixture. Solar baseline identity work also preserves `SOURCE_NOT_FOUND` and held/ambiguous identity states rather than name fallback. The PostgreSQL Ceres blueprint states that nullable admitted values remain SQL NULL and zero is preserved only when the source value is a qualified zero.

System-wide UNKNOWN behavior is not yet established.

### Q13. Which contain uncertainty?
**ESTABLISHED — heterogeneous representation.**

Solar M4-B carries unresolved uncertainty and assertion-level confidence/scope. Solar facts preserve intervals and model disagreement in promotion liens. Technology records include basis/uncertainty prose. Existing engineering/canon material sometimes separates deterministic limits from confidence layers. No common quantitative uncertainty model is established.

### Q14. Which distinguish candidate from promoted information?
**ESTABLISHED.**

Solar Facts and Earth long-run baseline holdings explicitly distinguish candidates, qualification results, promotion recommendations/records and promoted packages. M4-B remains candidate despite successful qualification checks. Historical promotion is provenance and does not imply v1 qualification.

### Q15. Which mix simulated and reference information?
**ESTABLISHED — multiple historical interfaces require later classification.**

Historical CIVPROP outputs carry `SIMULATION_EVENT`; Earth future trajectories are modeled reference products; canon chronology is preserved as a comparator; technology mixes governing canon history with provisional scenario anchors in one timeline projection while retaining class labels. The coexistence is explicit in several artifacts, but the complete set of mixed stores and consumer assumptions is not yet established.

### Q16. What consumes each artifact?
**NOT ESTABLISHED.**

Individual consumers are identifiable in code and documentation, but a complete producer-consumer graph has not been recovered. This is a Phase 1 deliverable still outstanding.

### Q17. What transformations create derived claims?
**ESTABLISHED — partial inventory.**

Earth runners and repair/successor pipelines, PostgreSQL import/projection migrations, Solar research/promotion builders, SPICE/transport calculations, timeline projection code and historical CIVPROP compilers all create derived records. Exact transformation lineage is recoverable for some promoted packages through manifests and hashes, but not yet mapped comprehensively.

### Q18. What qualification mechanisms exist?
**ESTABLISHED — heterogeneous historical mechanisms.**

Located mechanisms include executable validators, qualification reports, hostile fixtures, promotion validators, lab gates, coverage matrices, manifests, hash checks, regression tests and historical CIVPROP gates. They do not constitute a common v1 qualification framework.

### Q19. Which identifiers/vocabularies are shared?
**ESTABLISHED — partial inventory.**

Solar uses stable `body_id` plus identifier/crosswalk machinery including NAIF identifiers. Earth uses country/area and sector identifiers across annual relations. Timeline uses milestone/family identifiers. Historical CIVPROP binds actor IDs, body/location IDs, capability IDs and event IDs. A LOOM-wide identifier registry has not been established.

### Q20. Which are incompatible?
**NOT ESTABLISHED.**

Known crosswalk/semantic boundaries exist, but Phase 1 has not yet proven a complete incompatibility set.

### Q21. Which artifacts rely on authority by convention?
**ESTABLISHED — examples identified.**

Examples include governing canon chronology, historically selected/promoted model packages, authored scenario dates, and physical/mathematical machinery whose use has historically depended on accepted method/source contracts. The legitimacy and root type of each convention is not yet classified under v1.

### Q22. Which apparent authorities cannot be located?
**NOT ESTABLISHED.**

No complete expected-authority register exists yet against which absence can be proven. Specific missing authorities may emerge from the producer-consumer graph.

### Q23. Which claims depend on undocumented assumptions?
**ESTABLISHED — existence; exhaustive set NOT ESTABLISHED.**

Historical model and CIVPROP code necessarily contain parameters/rules not all represented as independent governed claims. Prior CIVPROP documentation itself records open capability, cost, budget and access gaps. A claim-level assumption inventory remains outstanding.

### Q24. Which artifacts are mutable?
**ESTABLISHED — classes identified; exhaustive set NOT ESTABLISHED.**

The live `loom_dev` PostgreSQL database is mutable operational state. VM worktrees and generated artifact directories are mutable filesystem holdings. Git commits and content hashes provide immutable references to particular versions, but branch tips and working trees are mutable. The inspected `/home/ubuntu/LOOM_DEV` worktree was dirty and on a historical branch, demonstrating this distinction directly.

### Q25. Which outputs cannot presently be causally reproduced?
**NOT ESTABLISHED.**

Some Earth packages preserve exact runner bytes, input hashes and run manifests; historical CIVPROP events preserve causal parents in some runs. That proves reproducibility mechanisms exist, not that all material outputs are reproducible. A negative inventory is still required.

### Q26. Which artifacts were produced, modified or classified by AI or automation, and what record exists?
**NOT ESTABLISHED.**

Automation is evident from builders, validators, importers and generated manifests. AI authorship/classification is not consistently discoverable from artifact metadata in the material inspected so far. Phase 1 must not infer human authorship merely from absence of an AI marker.

### Q27. What explicit human approvals exist for assumptions, parameters, promotions or classifications?
**NOT ESTABLISHED.**

Historical owner decisions and promotion records exist, but a complete approval ledger with human identity, scope and authorized act has not been located.

### Q28. Which pipelines contain fallback, imputation, interpolation, clamping, default or null-coalescing logic, and what values did they produce?
**ESTABLISHED — material example; exhaustive inventory outstanding.**

The Earth investment-rate correction documents a prior fallback problem and an explicit replacement imputation. The old seed used projected OECD 2024 destination GFCF/value-added for Myanmar, Nigeria and Taiwan; its WEO bridge updated GDP without updating the already-provided GFCF amount. The replacement rule uses current WDI observations and, where missing, an authored pooled imputation equal to the unweighted median of 2024 WDI percentages for 74 modeled economies: **22.3283039488531%**. The record explicitly says this is an authored pooled imputation, not an observation.

This proves fallback/imputation can materially alter long-run Earth state and must be inventoried mechanically before qualification.

### Q29. For every relevant quantity, are unit, currency and base year explicit or implied?
**ESTABLISHED — defects/ambiguities exist; exhaustive inventory outstanding.**

The database-semantics blueprint explicitly forbids inventing country currency or price year. The data dictionary contains quantities expressed as `model currency/year`. Historical CIVPROP capability work labels monetary fields as model proxy monetary units rather than observed appropriations. CIVPROP engine documentation warns that logical dimensions are not automatically MW, tonnes/year or other physical units. Therefore semantic metadata exists but is not uniformly physical, monetary or observational.

### Q30. Which artifacts carry as-of/knowledge-time information?
**ESTABLISHED — examples; common model NOT ESTABLISHED.**

Actor-capability documentation requires validity interval plus source/observation date and freezes an explicit as-of date. Solar qualification campaigns use source cutoffs/blindness boundaries. A common LOOM-wide knowledge-time field or rule has not yet been established.

### Q31. Which identifier crosswalks exist, who authored them and how were they checked?
**ESTABLISHED — Solar example; authorship completeness NOT ESTABLISHED.**

Solar baseline contains `identity_crosswalk` logic, NAIF-ID handling, held ambiguous identities and an external-crosswalk coverage report. One report records 99/110 bodies matched externally (90%) with known held cases. A complete cross-domain crosswalk inventory, author list and validation basis remains outstanding.

### Q32. Do downstream outputs feed back into upstream inputs, calibration or parameter choices?
**NOT ESTABLISHED.**

Historical simulation and successor pipelines exist, but Phase 1 has not yet demonstrated the complete feedback graph or established absence of circular calibration.

### Q33. Which parameters were fitted, to what, and were they later validated against the same target?
**NOT ESTABLISHED.**

No complete fitted-parameter/validation-target ledger has been located. This remains a required hostile check because outcome-conditioned fitting can masquerade as validation.

### Q34. Which code versions produced derived artifacts, and can those versions be recovered?
**ESTABLISHED — substantial positive examples; not universal.**

`loom_control.source_artifact` stores source Git commits for Earth and timeline source artifacts. Earth v3 provenance preserves the exact numerical runner bytes and SHA-256, distinguishes them from a later descriptor-only edit, and records output hashes. Promoted Earth source rows point to Git commit `d6372ece50976fecfaf76b382d9b682560b70273`; timeline source rows point to `c0b50afdd792cecf0b32a8752855e5afa8694ddd`. Universal recoverability is not established.

### Q35. Which tests, gates or validation reports exist, and what do they not cover?
**ESTABLISHED — broad inventory exists; coverage map incomplete.**

Examples include M4-B qualification and hostile validation, Solar Facts promotion qualifications, Earth qualification/promotion validators, PostgreSQL field qualification evidence, historical CIVPROP gates and regression tests. Several reports explicitly preserve liens or `NOT_TESTED` dimensions. A unified test-to-claim coverage matrix does not yet exist.

### Q36. Where do conflicting claims already exist, and how were they resolved?
**ESTABLISHED — examples.**

Solar Facts preserves competing model scopes/assumptions as liens rather than forcing a single scalar. Earth repair records preserve signed negative Taiwan ENERGY current-price value added alongside positive gross output and previous-year-price value added, and explicitly state that negative current-price VA does not imply no production. Historical resolution patterns therefore include preservation, scoped interpretation and modeled reconstruction rather than simple overwrite.

### Q37. Which joins, filters and aggregations drop unknown/null rows?
**NOT ESTABLISHED.**

No systematic static/dynamic audit of joins, filters and aggregations has yet been completed. This is a concrete remaining archaeology task.

### Q38. Do existing holdings expose authority-root types not covered by D0.18?
**ESTABLISHED — candidates identified, classification deferred.**

Candidate additional roots include physical law/mathematical relationship, standards/identity authority, governing canon/institutional authority and internally verified deterministic computation. Phase 0 anticipated these possibilities. Phase 1 evidence confirms they are not hypothetical categories, but whether each is a distinct root or a governed derivation from evidentiary/authorized roots belongs to Phase 2.

### Q39. Where are physical-law or mathematical outputs treated as authority, and on what basis?
**ESTABLISHED — partial inventory.**

SPICE/DE440 ephemeris/state machinery, Lambert accessibility calculations and other engineering calculations are consumed as mathematically/physically constrained outputs under source/method contracts. Existing documentation distinguishes ephemeris truth from transport-model outputs and warns against extending one into another. Their precise standing under v1 remains a Phase 2 question.

### Q40. Which artifacts contain temporal leakage, where later knowledge can affect earlier modeled state?
**NOT ESTABLISHED.**

Some campaigns explicitly prevent leakage using source cutoffs/blindness boundaries. That demonstrates awareness of the problem but does not prove absence elsewhere. A systematic knowledge-time audit remains required.

## 7. Pass 2 Material Findings

1. **UNKNOWN semantics are strongest in Solar M4-B, not yet LOOM-wide.** M4-B gives us executable evidence that unknown-to-zero corruption was anticipated and tested.
2. **Earth contains documented imputation.** At least one current long-run economic repair uses an explicitly authored pooled imputation, correctly labeled as non-observational. This is legitimate archaeology evidence and exactly the sort of claim Phase 2 must classify rather than hide.
3. **Historical qualification is heterogeneous.** There is no single meaning of “qualified” across Earth, Solar, PostgreSQL and CIVPROP holdings.
4. **Knowledge time exists locally but not yet as a universal contract.** Solar blindness cutoffs and actor observation dates are positive precedents.
5. **Reproducibility is unevenly strong.** Some Earth artifacts preserve exact executable bytes and hashes; we cannot infer the same for all holdings.
6. **Physical/mathematical authority is real and must be handled explicitly.** It cannot be squeezed into “database source” merely because that would make the schema prettier.
7. **The largest unresolved archaeology risks are now structural:** complete consumer graph, implicit assumptions/parameters, AI/human authorization history, feedback/fitting loops, null-dropping transformations and temporal leakage.

## 8. Pass 3 Required Work

The next pass shall target the remaining `NOT ESTABLISHED` areas and convert broad partial findings into evidence-backed inventories:

- Q8 parameter inventory;
- Q16 producer-consumer graph;
- Q20 incompatible identifiers/semantics;
- Q22 expected-but-unlocated authorities;
- Q23 undocumented assumptions;
- Q25 irreproducible outputs;
- Q26 AI/automation provenance;
- Q27 human approvals;
- Q28 full fallback/imputation/default audit;
- Q31 cross-domain crosswalks;
- Q32 feedback graph;
- Q33 fitting/validation reuse;
- Q35 test-to-claim coverage;
- Q37 unknown/null loss audit;
- Q40 knowledge-time/temporal-leakage audit.

No repair is authorized by Pass 2.


## 9. Pass 3 — Structural Risk Audit

Pass 3 targeted the unresolved structural questions rather than attempting repairs. Evidence was taken from current GitHub `main` and the already-inspected VM/PostgreSQL holdings. Old CIVPROP material remains archaeology only.

### Q8 deepening — parameter inventory
**ESTABLISHED — material parameter families located; exhaustive enumeration still incomplete.**

Historical CIVPROP contains explicit parameter-bearing contracts rather than one parameter authority. Located examples include:

- `CIVPROP_DEMAND_PRESSURE_V1` with status `UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1`;
- `CIVPROP_PROJECT_ECONOMICS_V1` parameter sets;
- mission-knowledge observation parameters marked `UNCALIBRATED_SCENARIO_OBSERVATION_MODEL`;
- infrastructure Method Lab parameter sets marked `SYNTHETIC_METHOD_FIXTURE`;
- unresolved resource-process parameters marked `UNRESOLVED_PROCESS_MODEL`;
- actor-bridge parameters including allocation fractions, commit threshold and decision noise;
- CIVPROP-0 synthetic scenario prior, sensitivity, false-positive rate, costs, value and decision threshold;
- Earth long-run model parameters and explicit inherited assumptions, including a 10-year TFP transition half-life;
- biosynthetic/demographic parameters including age schedules, medical-health recovery fraction and calibration boundaries.

Finding: parameter status is already heterogeneous and often explicitly labeled. No single parameter registry or human-authorization ledger has been established.

### Q16 deepening — producer/consumer graph
**ESTABLISHED — architectural spine; exhaustive graph incomplete.**

A recoverable historical spine exists:

`source artifacts -> domain-specific builders/importers -> Earth/Solar/timeline projections or compiled CIVPROP inputs -> historical propagation engine -> event/state outputs -> Atlas/GIS/materialized consumers`.

The historical engine requirements explicitly specify a replaceable boundary:

`authoritative inputs -> compiled/frozen CIVPROP input -> propagation engine -> stable CIVPROP output -> Atlas/GIS/materialized consumers`.

Actor-capability work documents direct read-only consumption of `loom_earth` and `loom_timeline`; CIVPROP input compilation reads timeline and other governed/context records. A machine-complete file/table/function dependency graph has not yet been produced.

### Q20 deepening — incompatible identifiers/semantics
**ESTABLISHED — incompatibility classes located.**

At minimum:

- LOOM technical-agent IDs are not CIVPROP civilization-actor IDs by semantics;
- country identity does not imply authority over domestic firms/providers;
- Solar canonical `body_id`, NAIF identifiers and external source identifiers require explicit crosswalks;
- timeline aliases are identity mappings, not duplicate inventions;
- Earth demographic coverage (237 WPP areas) and economic coverage (80 modeled economies) are not interchangeable populations;
- `model proxy monetary units`, `SCENARIO_CREDIT`, and physical/currency-denominated quantities are not directly fungible;
- technology milestone date, installed capability, actor access and mission feasibility are distinct states.

These are contract incompatibilities even where strings or years happen to align.

### Q22 deepening — expected but unlocated authorities
**ESTABLISHED — bounded list.**

Historical CIVPROP documentation explicitly identifies missing or unresolved authorities for:
- actor-access/capability at mission scope;
- observed/authorized spendable mission budgets;
- provider contracts/service slots;
- payload/service envelopes and prices;
- several process/resource capacities;
- lifecycle/failure parameters;
- complete physical/economic parameterization for infrastructure archetypes.

The actor-capability foundation states that Earth aggregate economics cannot establish accessible cash, spacecraft, launch service, specialist competence or access rights. These gaps are therefore documented absences, not merely search failure.

### Q23 deepening — undocumented/weakly governed assumptions
**ESTABLISHED — material examples.**

CIVPROP-0 embeds synthetic scenario values directly in its `Scenario` dataclass: prior 0.3, sensitivity 0.85, false-positive 0.15, capital 100, mission cost 5, continuation cost 50, success value 100, threshold 0 and technology=true, all explicitly scoped as scenario test inputs/credits. Later historical contracts improve labeling but still contain uncalibrated or synthetic parameter sets.

Earth code also contains inherited forecast assumptions such as `TFP_TRANSITION_HALF_LIFE_YEARS = 10.0`, explicitly described as pending direct persistence calibration.

Finding: the main risk is not always hidden values; many values are honestly labeled but lack a common authorization/standing model.

### Q25 deepening — causal reproducibility
**ESTABLISHED — mixed standing.**

Positive cases:
- CIVPROP-0 `Run` records seed, scenario, inputs, input SHA-256, implementation SHA-256 map, events and audit state.
- actor-state runtime replays versioned events and rejects invalid/unknown-state inventions.
- Earth packages preserve run manifests, parameter hashes, exact runner bytes and determinism reports; one successor reports 18 primary artifacts byte-identical across rerun.

Negative/unresolved:
- no evidence establishes this standard across all historical LOOM outputs;
- local mutable worktrees and numerous generated VM directories cannot be treated as reproducible merely because they still exist.

Thus causal reproducibility is demonstrably achievable but not universally inherited.

### Q26 deepening — AI/automation provenance
**NOT ESTABLISHED — governance gap confirmed.**

Automated builders, importers, validators and generated manifests are readily identifiable from code. The inspected artifact metadata does not provide a systematic field distinguishing human-authored, AI-assisted, AI-generated or automated classification decisions. Absence of such a marker cannot establish human authorship.

This is a genuine Phase 2 governance requirement, not a defect that Phase 1 may repair.

### Q27 deepening — human approvals
**NOT ESTABLISHED — governance gap confirmed.**

Owner decisions exist in Git history, governance documents and promotion records, but no common machine-readable approval ledger was located that records human identity, authorized act, scope, basis and time across assumptions, parameters, promotions and classifications.

### Q28 deepening — fallback/default audit
**ESTABLISHED — material classes located; exhaustive static audit remains future tooling work.**

Earth contains explicit fallback/imputation and inherited fallback provenance. Examples include:
- the corrected investment-rate pooled WDI median imputation;
- PWT boundary fallback noted for ARE;
- historical OECD ICIO fallback provenance for Nigeria, later replaced;
- long-horizon transition assumptions rather than country-specific endpoint tuning.

CIVPROP historical contracts frequently fail closed instead of defaulting UNKNOWN to numeric values. Examples reject UNKNOWN accessibility values, UNKNOWN budgets with amount/unit, and UNKNOWN actor fact sets containing asserted records.

Finding: LOOM contains both fallback-bearing scientific models and fail-closed operational contracts. v1 must distinguish authorized scientific substitution from silent runtime default.

### Q31 deepening — crosswalks
**ESTABLISHED — important crosswalks present; no universal registry.**

Solar identity crosswalks explicitly hold ambiguity rather than applying name fallback. Timeline aliases are explicit. Earth area/economy/sector identifiers are stable within their projections. No common registry establishes every cross-domain mapping and its author/validation basis.

### Q32 deepening — feedback graph
**ESTABLISHED — feedback-capable historical models exist; CIVPROP-to-Earth closed loop not established as current authority.**

Earth successor models couple demographic/labor/economic state internally and carry restored calibration/trade state. Historical CIVPROP requirements anticipate path dependence and accumulated state affecting later opportunity. No evidence in this pass establishes a currently governed two-way CIVPROP ↔ Earth realized-state loop. Therefore such a loop must not be presumed to exist.

### Q33 deepening — fitting and validation reuse
**ESTABLISHED — controlled examples plus unresolved inventory.**

Earth records explicitly distinguish calibration from endpoint fitting:
- Nigeria's 2226 share is documented as a diagnostic, never a calibration target;
- the repaired v3 states there was no country outcome cap, ranking target or 2226 Atlas calibration;
- the medical longevity schedule is described as setting calibration and explicitly “not fitted to an endpoint”;
- demographic code performs a WPP mortality boundary calibration.

This is positive evidence of anti-target-fitting discipline in named models, but there is no LOOM-wide fitted-parameter ledger proving that all validation targets are independent of fitting targets.

### Q35 deepening — test-to-claim coverage
**ESTABLISHED — mechanisms rich, common coverage model absent.**

Historical artifacts include negative fixtures, deterministic reruns, unit/regression tests, qualification reports, promotion validators, coverage matrices and explicit liens. M4-B's UNKNOWN-to-zero hostile fixture is a particularly direct semantic test. PostgreSQL field qualification evidence can explicitly record `NOT_TESTED`.

No universal mapping currently answers “which test establishes which claim under which contract version.”

### Q37 deepening — unknown/null loss
**NOT ESTABLISHED — requires mechanical code/query audit.**

Strong fail-closed contracts exist, but they do not prove that every SQL join, Python filter, aggregation or serialization path preserves UNKNOWN/NULL semantics. No complete null-loss audit was located. This remains one of the highest-value technical audits before qualified input compilation.

### Q40 deepening — temporal leakage
**ESTABLISHED — prevention mechanisms exist; system-wide absence NOT ESTABLISHED.**

The actor-capability foundation explicitly freezes an as-of date and states that later evidence must not leak into initial knowledge. Solar research qualification uses predeclared source cutoffs/blindness boundaries. These are positive controls.

No system-wide audit proves that every Earth, Solar, timeline, actor or historical CIVPROP consumer respects knowledge time. Temporal-leakage absence therefore remains unproven.

## 10. Pass 3 Synthesis

The archaeology no longer supports a picture of LOOM as four clean authoritative databases. The evidence instead supports a **network of claims, models, scenario material, projections, physical/mathematical transforms, compiled interfaces, qualification artifacts and simulated state with uneven governance maturity**.

The most important result is also slightly less dramatic than discovering a smoking crater in the database: many historical designers already knew these distinctions mattered. UNKNOWN is often protected; scenario values are frequently labeled; Earth calibration records often disclose fallback and anti-endpoint-fitting rules; Solar qualification preserves ambiguity and scope.

The failure mode is therefore primarily **lack of one common authority contract and common consumption boundary**, not universal scientific sloppiness.

### High-risk unresolved items before Phase 1 can close

1. **Q26 AI/automation authorship and classification provenance** — no common record.
2. **Q27 human authorization ledger** — no common record.
3. **Q37 null/UNKNOWN-loss audit** — no complete mechanical audit.
4. **Q40 system-wide temporal leakage** — prevention exists locally, absence not proven.
5. **Q16 complete producer-consumer graph** — architectural spine established, machine-complete graph not yet built.
6. **Q8 complete parameter inventory** — families established, exhaustive enumeration not yet built.
7. **Q33 universal fit-vs-validation independence** — good named examples, no universal ledger.

These do not justify repairing old systems during archaeology. They determine what Phase 2 must govern and what tooling/qualification must later test.

## 11. Phase 1 Closure Readiness

**NOT YET CLOSED.**

The 40 archaeology questions have now all been investigated beyond the initial inventory, and the major authority families and failure modes are visible. However, closing Phase 1 now would silently convert several “absence not proven” findings into assumed safety.

A final Pass 4 should be narrow and mechanical rather than another architecture essay:

- enumerate parameter-bearing CIVPROP/Earth artifacts and status labels;
- enumerate direct domain consumers/importers;
- scan SQL/Python consumption paths for null-dropping/default/coalescing behavior;
- inventory explicit as-of/cutoff fields and rules;
- inventory human/AI/automation provenance fields actually present;
- produce a compact unresolved-risk register.

No repairs, schema changes or model changes are authorized by this Pass 3 record.
