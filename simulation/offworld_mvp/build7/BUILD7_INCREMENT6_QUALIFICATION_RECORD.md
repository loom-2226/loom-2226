# Build 7 Increment 6 — emergent qualification disposition

**Class:** engineering qualification
**Disposition:** BLOCKED; no simulation behavior changed
**Implementation under test:** `f6527e65afc40ae804d99f05b45e99c3c389389e` on `offworld-mvp-build7-hidden-world`
**Horizon:** 2026–2035 inclusive

The governing acceptance source is `BUILD7_ACCEPTANCE_CRITERIA.md` beneath
`OFFWORLD_MVP_GUIDING_FRD.md`; `BUILD7_EMERGENCE_IMPLEMENTATION_GUIDE.md`
sets the Increment 6 procedure. The Research Lab's
`BUILD7_SEMANTIC_CAUSAL_MODEL_MAP.md` was consulted only as a non-authoritative
comparison. Its own implementation check predates the tested commit.

## Observed campaigns

Runs used the committed no-target CLI against an isolated copy of the
Increment 5 governed-test database. The original qualification database,
World Authority roles, and repository implementation were unchanged.

| World seed | Run ID | 2027 | 2028 | 2029 | 2030–2035 | Final project |
|---|---|---|---|---|---|---|
| `QUANTIFACTUS-INTERACTIVE-SMOKE-20261008` | `SOLAR_MATERIAL_ce54bc91cb1d6795a0357197:81faed42833ecd39` | AUTHORIZE | STUDY_SUPPORTS_ADVANCE | ADVANCE | NO_ACTION | EXPLORING, `SURFACE_OR_SAMPLE_CHARACTERIZED`, cash 0 |
| `BUILD7-I6-QUAL-20261008-A` | `SOLAR_MATERIAL_ab0cb0e8ee4e9877a932ba6d:0cc9cd62c4082801` | AUTHORIZE | STUDY_NEGATIVE | ABANDON | NO_ACTION | ABANDONED |
| `BUILD7-I6-QUAL-20261008-B` | `SOLAR_MATERIAL_540f045c06f112c28a0d6746:9206275acbe2dcea` | AUTHORIZE | STUDY_NEGATIVE | ABANDON | NO_ACTION | ABANDONED |

Each GENESIS reported 90 generated bodies, 90 candidate missions, zero
projects, zero settlements, and zero Offworld population. The persisted catalog
has 900 prospecting REGION locations: exactly ten for each of 90 bodies.
Each campaign made a PUBLIC remote choice, produced four body-level and four
REGION-level observations, and created exactly one sponsor-authorized project.
The common Comet Halley body choice is the current stable tie-break over
equivalent initial actor-visible candidates. After body-level observation, the
ten REGION alternatives remain information-equivalent; the stable region
tie-break selected REGION 02. Neither choice asserts superior hidden conditions.
World-seed variation did not change the pre-observation body choice.

Reopening the first run through 2035 returned 43/43 epochs `ALREADY_MATCHED`,
including its prior observation, financing, study, review, and annual Earth
epochs. A direct `wa_info.decision` inspection found no Agent decision after
2029 in any of the three runs. Focused Build 7 opportunity, exploration,
prospecting, REGION truth, and study-adapter unit tests: **18 tests, OK**.

## Acceptance matrix

| Criterion | Observed evidence | Status | Gap |
|---|---|---|---|
| §25 A, §§1–3: no-target GENESIS and coverage | Three openings with 90 bodies, zero projects/settlements/population; 90/900 catalog | PASS | None in opening path |
| §25 B: legitimate no-action case | `NO_ACTION` years persist, and focused budget tests produce WAIT | NOT DEMONSTRATED | The 2030–2035 label is appended without an Agent decision or fresh opportunity window |
| §25 C, §§5–7: endogenous exploration | PUBLIC authorized one visible candidate; one body received observations; unchosen bodies received none | PASS for opening choice | Later annual exploration opportunities are absent |
| §25 D: hidden-truth firewall twin | Varied hidden seeds selected the same pre-observation body; focused firewall tests passed | NOT DEMONSTRATED as the full controlled twin | Exact otherwise-identical hidden-world twin was not run in this blocked qualification |
| §25 E: visible-information sensitivity twin | Focused test changes the chosen candidate after a legitimate visible knowledge change | NOT DEMONSTRATED as the full integrated twin | No ten-year paired campaign was run |
| §25 F, §§8–13: capital gating | Existing focused tests show bounded mobilization, commitment/disbursement distinction, F/X update and Earth-shadow diversion; campaigns spent finite project cash | NOT DEMONSTRATED in full | No return/loss continuation or recurring annual mobilization occurred |
| §25 G, §14: endogenous project creation | One SPN `INITIATE_PROJECT` decision preceded each project; exact replay added no duplicate | PASS for creation | None in initial project transition |
| §25 H, §17: path dependence | 2028 REGION evidence led to 2029 SPN `ADVANCE` or `ABANDON`; state and decisions persisted | PASS for one later decision | Changed maturity is not offered a subsequent decision opportunity |
| §25 I, §§4, 15, 18: ten-year emergent chain | Three runs advance to 2035; one reaches study maturity, none can reach development or operation | FAIL | Annual conductor stops deriving opportunities/asking policies after the single study review |
| §§23, 26: replay and preserved targeted qualification | First run replayed 43/43 epochs exactly; prior targeted qualification is recorded in the repair record | NOT DEMONSTRATED as final gate | Full targeted regressions were deferred after the structural blocker was identified |

## Concrete blocker and boundary

`run_world_annual()` invokes `run_world_prospecting_initiation()` once. That
opening path only accepts calendar year 2026. The annual loop then follows one
hard-coded `BUILD7_REGION_STUDY` activity through authorization, observation,
and review. After review it appends `NO_ACTION` and records annual Earth context,
without deriving fresh public/sponsor opportunities, updating country capital,
or invoking an Agent policy. `NO_ACTION` in those years is a conductor fallback,
not an Agent's WAIT/DECLINE/DEFER. This directly misses the recurrent annual
loop required by acceptance §§4 and 18 and the ten-year case §25 I.

The smallest correction to examine is a recurrent decision window that consumes
persisted beliefs, project/study state, and finite finance, then presents only
currently legitimate opportunities to the existing bounded policies. A
reviewed project needs an explicit next eligible study/activity or a traceable
blocked outcome. The existing four-family REGION signals establish only coarse
material evidence; they do not establish a site, deposit, resource quantity,
grade, recoverability, reserve, or development economics. Any transition that
requires those propositions needs its own governed evidence relationship.

No model, conductor, financing, study, or project code was changed in this
qualification pass. Increment 6 is not accepted; the full final targeted
regression and acceptance suite should follow a justified repair.
