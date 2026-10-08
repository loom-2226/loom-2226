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

## Causal continuation repair — Gate 1 diagnosis

**Disposition remains BLOCKED.** At the reviewed 2029 `ADVANCE` in the first
campaign, the persisted project is `EXPLORING` at
`SURFACE_OR_SAMPLE_CHARACTERIZED`; the one `BUILD7_REGION_STUDY` activity is
`COMPLETED` and reviewed. Its `SUPPORTS_ADVANCE` result and four admitted SPN
REGION-family beliefs (VOLATILES 0.8, METALS 0.2, SILICATES_ROCK 0.8,
CARBONACEOUS_ORGANICS 0.8) are the earned information. The study spent the
project's 20 model-currency units, leaving project cash 0. The 2026 capital
mobilization/disbursement left country financing cash `F=29.58025335469291`
and exposure `X=20`; `R=0`, `S=0`. These are distinct accounts: remaining
country `F` is not an authorized project study budget. The persisted study,
belief, expense, and review records are replayed exactly in the 43/43 matched
epochs reported above.

| Causal step | Input → output | Code authority / limit |
|---|---|---|
| Annual scheduler | 2026 opening project → one `BUILD7_REGION_STUDY` → 2027 authorize/spend → 2028 observe/admit → 2029 review → 2030–2035 `NO_ACTION` | `generated_campaign.py:775–851,865–941`; the final label is appended without `policy_epoch()` |
| Study state | REGION project + opening cash → one plan, `REMOTE_CHARACTERIZED` → `SURFACE_OR_SAMPLE_CHARACTERIZED` on positive review | `methodology.py:1605–1640,1751–1810`; initialization rejects a second state and review rejects the same activity twice |
| Sponsor policy | Proposed activity + admitted project cash/status/window → `AUTHORIZE` or `DEFER` | `project_activity.py:133–152`; `policies/sponsor_portfolio_v1.py:25–85` requires a nonempty candidate list and `PROPOSED` activity. The sole activity is `COMPLETED` |
| Structural next edge | `SURFACE_OR_SAMPLE_CHARACTERIZED` → `RESOURCE_ASSESSMENT` | `build6b_staged_prospecting_fixture.py:85–120` provides an authored test activity, cost 20, and future result. It is not a generated-world Build 7 activity, cost authority, or observation contract |
| Finance | Country `F` 29.58 and project cash 0 → no authorized follow-on disbursement | `methodology.py:2598–2636,2668–2692` mobilizes cash and restricts country disbursement to an `INITIATE_PROJECT` prospecting request. Build 5 finance requires resource-existence belief and PRICE/CAPEX/OPEX/LEAD_TIME underwriting (`mvp_state.py:521–529`), which coarse REGION material evidence does not establish |
| Other Sponsor policy | Project + resource/observation → resource-bound decision | `sponsor_protocol.py:17–25`; the Build 7 prospecting project has no resource, site, deposit, quantity, grade, reserve, or recoverability conclusion |

The missing call after the 2029 review is a **scheduler connection**, but
connecting it to the present policies cannot produce a valid decision:
there is no eligible proposed next activity, no governed Build 7
`RESOURCE_ASSESSMENT` question/result from the coarse four-family regional
truth, and no authorized funded follow-on study. Passing the completed
activity as a candidate or treating country `F` as project cash would falsify
the policy/accounting inputs. The Build 6B maturity edge and fixture establish
structural progression, not the missing scientific/economic and financing
semantics. Existing REGION evidence supports the completed characterization
stage only; it does not establish development viability.

**Repair gate result:** no code-only recurring post-review Sponsor opportunity
is currently available. A follow-on study needs a specifically authorized
study question/result and cost/funding decision compatible with the generated
WORLD, or an explicit project continuation/closure decision contract that
accepts this state without pretending another study exists. Both are model
decisions outside a scheduler-only repair. Stop before implementing or
claiming an Agent-authored 2030 `NO_ACTION`; retain this qualification as
BLOCKED.

## Recurring exploration and allocation — feasibility check

**Disposition remains BLOCKED; no recurrence code changed.** The existing
PUBLIC choice function already derives the full year-specific visible Solar
candidate set and excludes bodies with admitted completed REMOTE observations
(`build7/opportunities.py:79–120`, `build7/exploration_choice.py:22–53`). It can
return `WAIT` for exhausted public funds or no eligible unresolved body. The
runtime handoff, however, rejects years after 2026 and assumes its observation
leaves *no* project or asset in the kernel
(`build7/generated_campaign.py:663–753`). Reusing the pure decision is
possible; executing it after the first project is not a scheduling-only call.

The existing Sponsor prospecting policy evaluates **one** region-scoped
request, using that body's admitted four-family evidence, beliefs and priors,
scenario prospecting cost/value, and available country financing cash. It does
not compare bodies or an existing project against another project
(`offworld_kernel/prospecting.py:240–276`,
`offworld_kernel/policies/sponsor_prospecting_v1.py:23–62`). The Build 6A
portfolio policy evaluates only already-registered `PROPOSED` activities
against project cash, status, window and priority; it does not select a Solar
target (`offworld_kernel/project_activity.py:133–152`,
`offworld_kernel/policies/sponsor_portfolio_v1.py:25–85`). The current annual
conductor and I5 kernel attach one fixed `BUILD7_REGION_STUDY`, then append
`NO_ACTION` after its review (`build7/generated_campaign.py:865–941`,
`offworld_kernel/methodology.py:1605–1640`). The prior Gate 1 diagnosis above
records why no governed next study or funded continuation activity exists.

There is also a concrete World Authority admission limit for the requested
second target. In the current compiler, a `BodyRemoteBinding` epoch rejects
*any* existing project, asset or Offworld node
(`build6e/named_world.py:511–526`). A `ProspectingRegionBinding` epoch checks
the current binding against **every** project-creation record and checks
REGION observations against that same body/location
(`build6e/named_world.py:813–857,1029–1050`). The runtime carries one
`named_binding` for each epoch. Thus a second body's REMOTE observation while
retaining the first project, or two separately authorized projects at different
REGIONs, cannot pass strict persistence admission. Removing these checks
without replacing their per-mission/per-project spatial lineage would weaken
the hidden-truth and location firewall.

Country `F` carries forward, but the existing country disbursement is scoped
to one initiating `SponsorProspectingRequest` and `INITIATE_PROJECT` decision;
it cannot silently fund the first project's next study
(`offworld_kernel/methodology.py:2668–2692`). The structural Build 6B
`RESOURCE_ASSESSMENT` example is an authored test activity/result, not a
Build 7 generated-world study (`build6b_staged_prospecting_fixture.py:85–120`).
These are distinct gaps: a small Sponsor comparison contract is authorized by
the repair request, but a scientifically legitimate follow-on activity and
multi-body/multi-project governed execution require additional model and
persistence relationships. The smallest requested end-to-end repair therefore
exceeds a narrow conductor connection. Preserve the previous campaign evidence
and BLOCKED finding; do not label conductor fallthrough as Agent deferral or
commit a partial recurring-choice path.

## Two-body spatial persistence experiment

**Scope and setup.** On branch head `2931eef8818fb28232c2ac53f1389c8781d4521c`, PR #370 OPEN, a disposable local database
`loom_b7_i6_spatial_experiment_20261009` was cloned from the interactive-test
database. A fresh no-target run used world seed
`BUILD7-I6-TWO-BODY-SPATIAL-PROBE-20261009` and run ID
`SOLAR_MATERIAL_9ffc865af31e9545db1d265a:f9cb3e264ff90c1e`.
Experimental orchestration lived only in `/tmp/loom_b7_i6_spatial_probe.py`;
no repository code, schema, role, or validation rule was changed. Both missions
used the existing PUBLIC exploration policy, scheduler, paid WORLD_SIM REMOTE
transition, strict compiler, and `execute_persisted_epoch()` transaction.
The second candidate was derived after the first observation, excluding the
already characterized body; identities were not chosen for physical outcomes.
Both missions occurred in simulation year 2026 **before any project existed**.

**Binding trace.** `build7/generated_campaign.py:677–735` restricts its
convenience handoff to 2026 and assigns `h['named_binding']` from each selected
body. `build7/runtime_flow.py:205–216,345–360` passes the current binding to
each persisted policy/action epoch and checks the REMOTE subject against it.
`build6e/named_world.py:862–880` emits a separate `wa_run.world_binding` and
body-scoped mission for each authorized request; `:1029–1070` checks each
observation against its epoch binding. `:1295–1344` validates and commits one
epoch at a time. These checks require **one correct spatial subject per epoch**,
not one body for the entire no-project campaign.

**Observed result: ADMITTED.** The first authorized mission observed
`COMET_HALLEY`; the second, independently authorized mission observed
`DONALDJOHANSON`. Each has a distinct `wa_run.mission` body/world identity,
distinct `wa_run.world_binding`, its own planned request artifact and PUB
`wa_info.action_authorization`, and four `wa_run.observation` rows whose body
and world match that mission. Both missions have `target_location_id=NULL` as
valid body-level REMOTE observations. Each body's four observations generated
four `wa_info.possession` rows for PUB and four family-specific PUB belief rows.
The second observation did not create a site or project. Final persisted counts
were **2 missions, 8 observations, 2 body bindings, 8 PUB possessions, 8 PUB
beliefs, 0 projects**. Reconstructing the same run and repeating both governed
missions returned **21/21 epochs `ALREADY_MATCHED`**; the observation identities,
signals, and belief results were unchanged and no rows duplicated.

**Classification: Build 7 adapter/orchestration limitation for this tested
case.** World Authority's existing contract and the inherited compiler already
admit multiple independently authorized body subjects in one no-project run.
The normal Build 7 handoff's 2026-only guard and fixed opening flow prevent
later-year use; a recurring caller would need unique mission/request/epoch
identities and must set the existing body binding for each authorized action.
The previous feasibility note's assertion that the compiler itself prevents
*all* multi-body observations is too broad and is corrected by this experiment.

**Unresolved boundary.** This experiment did not put an existing prospecting
project in the kernel. The compiler still rejects a `BodyRemoteBinding` epoch
when any Offworld project, asset, or node exists
(`build6e/named_world.py:519–524`), and its REGION projection checks the active
binding against project origins (`:813–839`). Thus this result does **not**
qualify a later REMOTE mission alongside a retained project or multiple projects.
No compiler or World Authority correction is justified by the two-body,
pre-project result alone. Preserve the broader Increment 6 BLOCKED disposition
pending separate evidence for project coexistence and the other causal gaps.
