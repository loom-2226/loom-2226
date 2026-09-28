# CIVPROP actor capability foundation V1

Date: 2026-09-29. Class: `class:engineering`; inspection and architecture only.
Promoted main: `a26f6f9da56cdc96c22f893386e3f2168dbe3308`.
PR #321 merged as `7b54d5f32f1977349a07e3a2fb31becc1c2a582e`; #322 merged
as the main commit above. Both unchanged heads were mergeable, passed `loom-gate`
and had no reviews/comments/unresolved threads. CIVPROP-0 passed 19/19 bounded
tests again. #322 was re-evaluated after #321. Unrelated local work was preserved.

## Verdict

**Add an evidence-backed actor access/capacity assessment, not a technology unlock
calendar or a GDP-to-capability score.** Current Earth and timeline authority
support the surrounding model but cannot establish Australia's 2026 ability to
execute or procure this particular lunar mission. The defensible current empirical
answer is **UNKNOWN**, not unavailable. No executable probe is needed to resolve
this architecture; CIVPROP-0 remains unchanged as the reference harness.

Four questions remain separate: what capability exists globally; what this actor
can access; whether the requested mission is physically/operationally feasible;
and whether the actor chooses it. Timeline entries alone answer none completely.

## 2026 Empirical Boundary

Initialize only task-scoped assertions with actor/provider identity, service or
asset, location/activity scope, validity interval, source/observation date,
quantities/units where supported, and provenance. Freeze an explicit as-of date:
for the existing experiment, 2026-09-28 departure. Later evidence must not leak
back into the actor's initial knowledge; January-1 Earth accounts do not establish
September service availability.

Keep `OBSERVED_2026_CAPABILITY`, `OBSERVED_2026_ACCESS`,
`DERIVED_2026_CAPABILITY` (named rule and source chain), and
`UNKNOWN_2026_CAPABILITY` distinct. Absence needs positive scoped evidence;
missing rows are not negative evidence. These are evidence classes, independent
of whether a capability is usable. `FUTURE_SIMULATED_CAPABILITY` is a later run
output, never a retrospective upgrade of the empirical baseline.

For this mission, evidence must distinguish payload/instrument provision,
Earth-to-lunar-site delivery, and command/communications/operations through the
observation. A documented integrated service may cover several requirements;
there is no need to invent separate providers. State who supplies each function,
what the actor must supply, and what remains conditional or unknown. No sovereign
launch vehicle is intrinsically required.

## Existing Earth Authority

Inspected live `loom_dev` in explicit READ ONLY transactions. `loom_earth` has
nine tables. Common keys are `snapshot_id`, `iso3`, and year where temporal;
`derivation_id` links model lineage. Snapshot
`earth-v0-1-9934d0ac-20260925` is VALIDATED.

| Table | Actual relevant fields | 2026 availability / legitimate use |
|---|---|---|
| `earth_area` | `iso3`, `display_name`, WPP ID/type, `economic_qualified` | 237 identities; country identity/reference, not decision authority over all domestic firms |
| `earth_demographic_year` | biological population, births/deaths, median age, age bands | 237 rows; population context from WPP projection, not skilled staff |
| `earth_biological_cohort_year` | sex, age start/span, persons, open-ended flag | Age/sex demographic detail, not occupational qualification |
| `earth_economic_year` | value added, gross output, investment, capital, population | 80 economies; aggregate economic context, not accessible cash or spacecraft |
| `earth_legacy_labor_year` | employment, labour force, working-age population | 80 rows; persons/FTE proxies, not mission-operator competencies |
| `earth_sector_year` | sector, output/value added, investment/capital, employment/effective labour | 800 rows: ten sectors per economy. Employment and investment populated; effective labour null in 2026 |
| `earth_sector_asset_year` | sector, asset class, capital/investment, depreciation, replacement/expansion fields | 3,200 rows: four asset classes. Capital/depreciation populated; investment and all replacement/expansion amounts null in 2026 |
| `earth_labor_composition_year` | biological/synthetic labour, machine tasks, recognized persons | No 2026 rows; later modeled interface, not missing values to fill with zero |
| `earth_derivation` | model, method, epistemic status, scenario, artifact hash, notes | Seven provenance records, including qualified v4 economics and WPP empirical projection source |

Australia's actual 2026 rows include population **27,103,088**, legacy employment
**13,844,988**, value added **1,728,703,629,851.8467**, capital
**8,113,842,605,984.885**, and annual investment **412,288,545,182.134**.
The monetary fields are explicitly **model proxy monetary units / QUALIFIED_MODEL**,
not observed government appropriations or a mission budget. `SHIPS_AEROSPACE`
includes modeled capital about 26.10 billion and employment about 38,993; neither
identifies a spacecraft plant, launch service, experienced operator or access right.
Asset classes are machinery, structures, transport equipment and other assets.

There are no dedicated live Earth fields/tables for actor technology, named launch
infrastructure, provider contracts, service availability, institutional relationships,
trade links or specialist workforce. Productivity ratios can be derived as economic
diagnostics, not technological competence. The repository's v4 lineage includes
qualified-method productivity and trade-network topology, but these are not live
service-access records. Historical v3 adoption-convergence constants are explicitly
validation bounds, not century-scale causal coefficients. Legacy CIVSTATE's
institution membership and owner/operator/financier distinctions are useful semantic
precedents; gameplay breadth scores and alliance integration are not 2026 evidence.

## Timeline Semantics

Live `loom_timeline`: **43 milestones, 62 source links, one alias, five rules**;
snapshot `timeline-v0-1-0232bf23494f-20260925` is VALIDATED. Source roles are
19 GOVERNING_CONTENT, 19 STABLE_ID_MAPPING and 24 SCENARIO_DEFINITION links.
The alias joins `IND-2140-OUTER` to `TRN-2140-TORCH-MATURE`, not a second invention.
Migration 010 and both referenced source hashes match main.

| Live class | Count | Correct runtime interpretation |
|---|---:|---|
| CANON_HISTORY / GOVERNING_CANON | 19 | Governing fictional chronology, preserved as comparator for this forward simulation; not empirical capability observations or actor grants |
| MODERATE_SCENARIO_ANCHOR / AUTHOR_SCENARIO_MODERATE | 18 | Provisional practical-achievement hypotheses with prerequisites; earlier, later or failed achievement allowed |
| FICTIONAL_PHYSICS_SCENARIO_ANCHOR / SPECULATIVE_FICTION | 5 | Explicit fictional assumptions; not scientific forecasts or automatic successful engineering |
| SOCIAL_SCENARIO_ANCHOR / AUTHOR_SCENARIO_MODERATE | 1 | Optional institutional act; date alone neither changes rights nor creates persons/capability |

`start_year/end_year` preserve EXACT_YEAR, RANGE, DECADE_OR_RANGE, APPROX_YEAR or
APPROX_RANGE semantics. EXACT_YEAR on a scenario row is precise scheduling of an
assumption, not high evidential confidence. `capability_change_md`,
`threshold_gate_md` and `basis_uncertainty_md` describe propositions/conditions;
they are not executable predicates, measured capacities or price curves.
`milestone_source` preserves source hash/commit/role; `milestone_alias` preserves
identity; `interpretation_rule` controls consumption.

All five rules apply: DATE_DOES_NOT_UNLOCK, FOUR_TECH_STATES,
CANON_COMPARATOR_NOT_DESTINATION, SITE_SPECIFIC, UNKNOWN_NOT_ZERO.
The four technology states are demonstration/knowledge, reliable operational
design, installed local capacity, and actor access/adoption. ACC and SCI explicitly
have no universal date. The 2040 heavy-launch anchor is about sustained high-cadence
service, not the first possibility of any launch; 2035 lunar relay service does
not establish universal surface coverage or prohibit every earlier mission.

Thus the timeline is a source-classed opportunity/constraint scaffold and comparison
surface, not an empirical global-frontier database or a universal earliest-possible
calendar. Actual frontier realization requires evidence or simulated achievements.
Canon remains governing for fictional-history claims, but the explicit propagation
contract does not force its events. A future canon-conditioned run would need an
explicit, scoped scenario binding of those events and temporal precision; no such
binding currently grants actor capacity. Differences are reported for reconciliation,
not repaired by rewriting canon or forcing investments/outcomes.

## Missing Actor-Capability Bridge

A minimum claim relates **actor → capability/service → supplier or owned asset →
conditions and capacity → evidence valid at the requested epoch**. It must cover
operational use and access, not merely membership, national location or a technology
announcement. Qualification of one supplier does not demonstrate a whole chain.

The current consumer is AUS with scenario capital 100, cost 5, continuation 50,
contingent value 100, and `Scenario.technology: bool | None = True`.
`transport.assess_mission(inputs, scenario)` tests that flag plus four pinned
Earth/Moon states and five-day duration. Launch, transfer, polar landing and
execution success remain scenario assumptions. No payload mass or service envelope
is presently specified. M4-B resource knowledge and its hidden realization remain
separate and cannot establish actor capability.

A boolean therefore cannot justify an empirical result: the same actor may access
an orbital payload service but not lunar-surface delivery, or a small payload slot
but not the requested mass. At minimum the next consumer contract needs a delivery/
operations service class, site/coverage scope, requested payload envelope (mass in
kg when claimed), one available slot/window, and supported operations duration.
Unknown requirements or service bounds must remain unknown. Fleet-wide throughput
and annual cadence are unnecessary for one mission; a dated slot suffices. Detailed
reliability, propulsion and trajectory metrics belong to later mission qualification.
Price/currency/base-year, scope and finance conditions are needed before replacing
scenario economics, not invented as capability scores. Power/data interface limits
are required only when the selected service actually depends on them.

## Capability Possession and Access

Use two orthogonal distinctions rather than one mutually exclusive ownership enum:
**provision** (own asset or referenced provider) and **access basis** (ownership,
contract, partnership/consortium agreement, or other sourced right). Domestic
location is not ownership by the country. Procurement is a process; an advertised
service is not an awarded contract or a reserved slot. Consortium membership is
not automatically access to every member's infrastructure. Financing a provider
establishes no delivery entitlement without the associated agreement.

Separately assess usability as USABLE, CONDITIONAL, UNUSABLE or UNKNOWN.
CONDITIONAL requires identified, evidenced conditions such as approval, payment or
reservation; it must not hide missing evidence. UNUSABLE requires a known blocking
condition for the specified path/epoch, not merely absence of domestic launch.
An unavailable route does not prove all other routes unavailable. Provider IDs are
references, not additional simulated actors; an actor reference can later identify
a corporation/consortium without building a generic-agent platform now.

## Capability Evolution

Initialize empirical assertions, then apply run-owned events: contract award grants
scoped rights; payment/reservation allocates a service slot; construction followed by
commissioning/qualification creates usable installed capacity; successful operation
adds documented experience. Cancellation, expiry, failure, maintenance or retirement
can reduce access/capacity. Investment alone changes committed finance, not immediate
operational ability. A failed project is valid. Learning/diffusion rates require a
separately qualified model; no rate is inferred from GDP or timeline dates.

Re-evaluate capability from those facts/events at each decision boundary, with
quantities and dependency validity. Procurement rights can enable use without
technology transfer. Reconcile any later Earth capital/stock transfer once; the
current 100 scenario credits remain an isolated experiment budget.

## Authority Boundaries

| Owner | Responsibility |
|---|---|
| `loom_earth` | Existing identities and promoted demographic/economic trajectories, with their actual evidence/model status |
| `loom_timeline` | Source-classed chronology, scenario anchors, conditions and interpretation rules |
| `loom_solar` | Physical identity, states, coverage and provenance; no actor-access or economic value fields |
| Empirical capability intake | Versioned 2026 evidence assertions/reference packet, separately qualified; permanent storage owner remains undecided |
| Future `loom_civprop` | Run-owned rights, commitments, assets, experience and capability-changing events; future simulated state |
| Economics/resource economics | Budget/quote/valuation/decision inputs with units and scope; D&O remains unimplemented and is not lunar mission authority |
| Runtime | Capability resolution, requirement matching, transport feasibility and decision calculations, each separate |

## CIVPROP-0 Consumer Contract

Recommended pure interface (proposal only):

```text
resolve_actor_capability(actor_ref, epoch, mission_requirements,
                         boundary_evidence_ref, run_state_ref, timeline_policy_ref)
  -> assessment_id, status, evaluated_scope, valid_window,
     requirement_results[], provision_paths[], supported_limits_with_units,
     conditions[], unmet_or_unknown[], evidence_and_derivation_refs[], liens[]
```

Each path identifies supplier/asset and access basis, validity, operational status,
capacity/reservation constraints and supporting evidence. Preserve evidence class,
as-of date and contradictory assertions; do not average conflicts into a fabricated
confidence score. Report USABLE only when all required access/capacity propositions
for one complete path are supported. Report UNKNOWN for missing requirements,
stale/inapplicable evidence or unresolved conflicts. A proven expired right is
a blocking condition for that path; stale evidence alone establishes no absence. Evaluate known blocking
conditions before unknowns within a path; retain the scope of that conclusion.

The resolver owns no money mutation or trajectory computation. Acquisition terms
flow to economics and a procurement decision; an intent to buy cannot satisfy an
execution precondition. A capability assessment can be USABLE while physical
mission feasibility is UNKNOWN or the actor decides WAIT.

Minimum later integration seam: compute an assessment immediately before
`experiment.execute` calls `assess_mission`, then pass that assessment to the narrow
transport adapter. USABLE permits further transport checks; scoped UNUSABLE blocks;
CONDITIONAL and UNKNOWN cannot silently become FEASIBLE. Keep full reasons rather
than collapsing permanently back to bool. The actor still consumes feasibility and
economic inputs. Retain the existing scenario adapter/default replay path unchanged;
a separate evidence-backed path may honestly terminate in WAIT. New model versions
must not invalidate the original artifact's pinned implementation silently.

## Persistence Implications

Eventually persist admitted boundary evidence/version, actor and provider references,
owned/operated assets, scoped access rights/contracts, capacity reservations,
funding/commissioning/retirement events and experience/qualification evidence.
Persist enough decision/assessment provenance to reproduce which rights and limits
were used. Derive current usability, residual capacity, matched service paths,
financial affordability and trajectory feasibility at runtime; optional materialized
results are caches, not new authority. No permanent tables or DDL are earned here.

## Empirical Data Gaps

| Priority | Minimum missing input / disposition |
|---|---|
| REQUIRED_NOW for empirical replacement | Explicit one-mission requirement envelope and as-of date (design inputs, not research); one sourced actor/provider path covering payload, delivery and observation operations, with validity and conditions |
| REQUIRED_NOW for a positive access claim | Evidence of actor entitlement/procurement eligibility and provider operational service scope; actual demonstrated capability versus plan/objective; available slot/capacity or explicit uncertainty |
| REQUIRED_FOR_LATER_CAPABILITY | Commissioned assets, staff/operational experience, replacement/maintenance needs and access-changing events needed for sustained propagation |
| REQUIRED_FOR_LATER_ECONOMICS | Spendable actor allocation, committed funds, service quote with currency/base-year/scope, financing and payment terms; no GDP proxy |
| DERIVABLE | Eligibility/capacity matching and known residual reservations from admitted records; economic diagnostic ratios only within their existing meanings |
| UNKNOWN_ACCEPTABLE | Undisclosed price, unallocated slot, unsupported landing/site/payload limits, unverified partnership entitlement; these may prevent a positive result |
| OPTIONAL now | All-country rankings, launch-market census, general alliance network, industrial diffusion curves and long-run actor trajectories |

A **bounded external evidence intake is needed before claiming an empirical usable
path**. Scope it to AUS, the experiment's 2026 cutoff and one candidate integrated
provider/partner route. Seek dated primary agency/operator mission records,
procurement/award/access documents and technical service specifications. Distinguish
completed operations, current offer/eligibility, signed access and aspirational plans.
Stop when each required proposition is supported, conditional, contradictory or
explicitly unknown; do not search indefinitely for a favourable answer. New active
research follows the Research Lab boundary and separate upstream evidence admission.
No external research/acquisition was performed by this assessment.

## Liens / Unknowns

No sourced 2026 capability/access record in the inspected consumer or live Earth
schema resolves AUS's complete lunar-surface mission. This is a repository evidence
gap, not a claim about Australia's actual space capability. Some useful macro/trade
lineage exists elsewhere but supplies no named access agreement. Candidate Solar
resource evidence remains candidate. Surface transport and scenario economics stay
unqualified. No live PostgreSQL authority was modified.

## Next Executable Milestone

**AUS-CAP-0: admit and resolve one 2026 service-access case.** Freeze the one-mission
requirement envelope, perform the bounded evidence intake above, and implement a
small pure resolver over that one versioned packet. Keep any provider as a reference,
not a second simulated actor. Output a traceable USABLE/CONDITIONAL/UNUSABLE/UNKNOWN
assessment and a CIVPROP-0 adapter check; retain scenario economics and transport.

Stop when the real evidence case resolves honestly (UNKNOWN/WAIT is a passing
result), and synthetic tests prove no calendar/GDP unlock, ownership distinct from
access, expiry/conditions/quantity matching, and no launch while unresolved. Preserve
all 19 original CIVPROP-0 tests/replays. No permanent schema, propagation trajectory,
transport physics, extra actors or general capability framework.

## Evidence and checks

Live reads: `information_schema.columns`; all nine Earth table contracts and 2026
coverage/null counts; AUS demographic/economic/labour/sector records;
`loom_control.variable_semantics`, derivations, snapshots and migration ledger;
all four timeline tables/classes/rules/source roles; Solar Earth/Moon DE440 coverage.
Migrations 004/008/009/010 and both timeline source hashes matched main exactly.

Repository: promoted `engineering/civprop/civprop0/{model,transport,actor,experiment}.py`;
`docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md` §§1–7;
`docs/database_semantics/LOOM_TIMELINE_POSTGRES_PROJECTION_v0.1.md`;
`tools/earth_temporal_pg.py`; Earth current pointer, v4 promotion decision and
`build_promotion_records.py`; historical v3 `runner.py` validation bounds;
`docs/database_semantics/LOOM_CIVSTATE_IMPORTANT_TABLES_RECOVERY_v0.4.md`.
Search covered capability, diffusion, procurement, partnership/consortium, adoption,
trade and infrastructure terms in current docs, engineering, code and manifests.

Validation: baseline 19/19 tests, merge gates/review checks, read-only live/repository
reconciliation and documentation whitespace check. One new document only.
