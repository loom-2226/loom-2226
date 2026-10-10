# Build 7 causal audit: source-to-arrow verification

**Authority:** executable source pinned at `66c641d25e641e0aff77940a8cadbf1653247113`. **Scope:** generated-world annual path only. **Method:** inspect function branches and metadata, cross-check diagram claims, distinguish source-supported transitions from observed isolated-PostgreSQL rows. This is not a scientific validation of authored parameters or independent replay qualification.

| ID | Source-to-diagram claim | Evidence | Result |
|---|---|---|---|
| C01 | Pinned public catalog and accessibility determine visible mission candidates; not sealed world state | `opportunities.py:47–120`, `generated_campaign.py:195–228,640–657` | PASS: keep public and hidden inputs separate |
| C02 | PUB helper first filters unresolved SCREENED/capable/preliminary-comparable destinations and finite affordable costs, then minimizes modeled cost; hash only breaks exact ties | `exploration_choice.py:23–54`, `generated_campaign.py:702–744` | PASS: helper is **not** an Agent policy epoch |
| C03 | PUB policy AUTHORIZE gates paid remote observation; WAIT does not execute it | `generated_campaign.py:744–774` | PASS |
| C04 | WORLD_SIM observation is noisy, initially nonpublic, and PUB beliefs update before independent publication policy | `generated_campaign.py:767–798` | PASS: corrected diagrams that previously collapsed publication into paid observation |
| C05 | In this path, non-PUBLISH is blocked, and PUBLISH transition updates SPN information/belief; hidden truth never directly enters Sponsor choice | `generated_campaign.py:779–798`, `runtime_flow.py:233–375` | PASS: PUBLISH is a required conditional transition, not an automatic side effect of remote sensing |
| C06 | Opening SPN opportunity depends on PUB actually selecting/characterizing a body, plus visible regional opportunity | `generated_campaign.py:908–943` | PASS: corrected unconditional opening wording |
| C07 | USA promoted investment is a model projection; authored normalization/mobilization drives capital proxy, not empirical cash | `generated_campaign.py:148–184,943–950`; input metadata | PASS: empirical-money inference excluded |
| C08 | SPN policy initiation precedes distinct project creation, commitment and disbursement transitions | `generated_campaign.py:950–993` | PASS |
| C09 | Annual project activity progresses by state branch: initialize, PROPOSED portfolio, ACTIVE/due region observation, COMPLETED/unreviewed study review | `generated_campaign.py:1020–1104` | PASS: states are **not** simultaneous stages in one year |
| C10 | Annual opportunity eligibility is snapshotted **after PUB remote choice but before** processing this year's projects; requires opening project ID | `generated_campaign.py:1019–1023,1110–1144` | PASS: corrected ambiguous "year opening" wording |
| C11 | CONSIDER_PROSPECTING is followed by a second prospecting decision and drift check, not immediate financing | `generated_campaign.py:850–908,1119–1138` | PASS |
| C12 | `NO_ACTION` can be conductor summary, not Agent WAIT | `generated_campaign.py:1105–1113` | PASS |
| C13 | Policy epochs and system epochs persist through runtime flow; causal envelope is not equivalent to epoch count | `runtime_flow.py:194–375`, observed `wa_run.artifact`, `wa_run.causal_envelope` | PASS with explicit unit distinction |
| C14 | Fixed recovery profile is configured; a causal edge into annual study *performance* is not established | `BUILD7_GENERATED_CAMPAIGN_V1.json`, `generated_campaign.py:998–1154` | CORRECTED: removed misleading active edge |
| C15 | `wa_run.accessibility_assessment` does not supply the compiled public screen | checked-in screen metadata, isolated DB query returning zero rows | PASS: do not conflate PostgreSQL table with JSON lookup |
| C16 | Potential economic uses and offline resource returns do not feed annual prospecting decisions | `generated_campaign.py:908–1154`, `resource_returns.py`, input metadata | CORRECTED: removed misleading reference-to-active-economics arrow |
| C17 | `wa_geo.location` region anchors are authored identities, not empirical geometry | observed `origin_kind=AUTHORED_SPATIAL_ANCHOR`, `location_kind=REGION` and source region installer | PASS |
| C18 | Hidden physical properties and model policy metadata preserve stock/reserve and synthetic-truth boundaries | observed `wa_world.physical_property`, `generation_model`, `generation_policy`, `hidden_state` | PASS; database observations are scoped to isolated runtime |

## What this audit does *not* establish

- All Mermaid edges independently executed in one or more isolated replay campaigns. The checks above are **source-path and metadata checks**.
- PostgreSQL counts as single-run invariants: the isolated database contains multiple seeds and runs.
- `wa_meta` live table contents, which were not visible under the inspected runtime account.
- Physical calibration of the Lambert screen, material priors, observation likelihoods, recovery profile, or economic proxies.
- Active FIN underwriting, commodity price formation, extraction, transport, or settlement in the generated annual conductor.

**Promotion gate:** Keep the atlas PR in draft until rendered diagram review and independent deterministic replay/trace comparison are completed. Do not silently upgrade the audit label from SOURCE-CHECKED to QUALIFIED.
