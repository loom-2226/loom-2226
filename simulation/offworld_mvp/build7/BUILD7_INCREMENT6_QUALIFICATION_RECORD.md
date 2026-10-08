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

## Post-project multi-body persistence experiment

**Setup.** On branch `offworld-mvp-build7-hidden-world` at
`6713bf5476e71580b3744bd02bceb737b2426285` (PR #370 OPEN), a fresh disposable
database `loom_b7_i6_postproject_probe_20261009` was cloned from the local
interactive-test database. No source/qualification database, schema, role, or
repository code was changed. A new no-target run used seed
`BUILD7-I6-POSTPROJECT-SPATIAL-PROBE-20261009`, run ID
`SOLAR_MATERIAL_d7a721c7ea26857bffd168a5:6d3415124da62dd5`.

**Phase A — admitted.** The normal `run_world_prospecting_initiation()` path
selected COMET_HALLEY, ran the existing PUBLIC policy and body REMOTE
observation, admitted the four observations/beliefs, derived the SPN-visible
prospecting opportunity, and received an actual SPN `INITIATE_PROJECT`
decision. It created the single project
`PROSPECT:COMET_HALLEY:BUILD7_PROSPECTING_REGION_02`, bound to REGION 02,
committed/disbursed 20 model-currency units, and retained project cash 20.
Capital state was `F=29.58025335469291`, `X=20`, `R=0`, `S=0`.

**Phase B — policy selected, persistence rejected.** With the admitted Body A
observation and existing project state, the normal year-2027 candidate
derivation and `choose_remote_characterization()` selected DEIMOS. The
existing PUB Explorer policy evaluated actor-visible inputs and returned
`AUTHORIZE` at cost 10. `flow.policy_epoch()` then called
`execute_persisted_epoch()`, whose `_runtime_epoch_rows()` raised
`NamedWorldBlocked: BLOCKED_UNBOUND_OFFWORLD_STATE` at
`build6e/named_world.py:519–524`. This is the first rejection: the decision
epoch could not commit. The policy result remained uncommitted; no Body B
mission authorization, observation, possession, or belief was admitted.

The rejected guard checks `kernel.state.projects`, assets, resources, colonies,
Offworld nodes, and population whenever the epoch binding is absent or is a
`BodyRemoteBinding`. Phase A has a legitimate `PROSPECTING_REGION` project
location, but the Body B REMOTE epoch has a body binding and no spatial
representation for the already existing project's independent REGION. The
guard therefore conflates “body-level mission has no target location” with
“run contains no Offworld realized state.” This is the compiler's strict
projection/profile limitation, not a rejection by the PUBLIC Agent policy or
the underlying `wa_run.mission`/`wa_run.observation` tables: Phase A's project
and Body A's body-scoped mission already coexist in the same run.

**Phase C — committed history replayed.** Reopening by reconstructing the run
and replaying the normal Phase A path returned `ALREADY_MATCHED` for all 20
committed epochs. World Authority retained one Body A mission, four Body A
observations, one REGION 02 project/location, four PUB possessions, and four
PUB belief rows. Repeating the failed Phase B attempt again reached the same
policy authorization and the same compiler guard; persisted counts did not
change. No second body observation was persisted, so successful replay of both
body events was not established.

**Classification: persistence compiler limitation.** Unlike the earlier
successful two-body experiment (which had no project), this test proves that
the compiler's unbound-Offworld-state gate prevents a body-scoped REMOTE epoch
from coexisting with a valid REGION-scoped project, even though the project
and a different body binding are individually represented by existing
World Authority records. The smallest justified correction is a narrow
compiler projection change that validates each persisted project against its
own recorded REGION origin while validating the REMOTE mission and
observations against the current body binding. The experiment does not
authorize or implement that change, and does not demonstrate multiple-project
support. Preserve the BLOCKED qualification disposition and earlier
pre-project experiment; no simulation contracts or checks were relaxed.

## Post-project body REMOTE spatial admission repair

**Scope and diagnosis.** The preceding post-project experiment reproduced at
`c138ad55f167648e4fb741990fd1f5290d20a6f7` in an isolated database:
the 2026 PUBLIC choice was COMET_HALLEY, SPN authorized a REGION 02 prospecting
project with 20 committed and disbursed, and the 2027 PUBLIC choice was DEIMOS.
The Explorer policy authorized the second REMOTE request at cost 10, but
`build6e/named_world.py` rejected its policy epoch as
`BLOCKED_UNBOUND_OFFWORLD_STATE`. The old `BodyRemoteBinding` guard treated the
retained project and Offworld node as if they had to belong to the new REMOTE
body. The project already has its own authorized `PROSPECTING_REGION` location;
the second mission has its own body/world binding. No World Authority schema or
admission-contract change is required for these two independent spatial scopes.

**Narrow compiler repair.** `_runtime_epoch_rows()` retains the complete
no-binding rejection and the existing body REMOTE rejection of resources,
assets, colonies, and Offworld population. When a body REMOTE epoch retains a
prospecting project, it now verifies that every project has exactly one prior
realized `ProspectingProjectCreationRecord`, that the record still matches the
project, SPN owner, project cash account and Offworld node, and that its REGION
identity is one of the ten deterministic locations on its recorded body.
Unowned Offworld nodes remain rejected. Each new REMOTE request and observation
still must match the current epoch's body binding; the independent project
continues to carry its own REGION location. Existing REGION-scoped and targeted
projection checks remain in force.

**Observed governed result.** In a fresh isolated no-target run, PUBLIC again
selected COMET_HALLEY, SPN authorized its REGION 02 project, and the later
visible candidate derivation selected DEIMOS. The paid PUBLIC policy/action
path committed the second REMOTE mission and four DEIMOS observations and
belief updates. The project stayed EXPLORING with 20 project cash; country
`F` and `X`, project commitments, and project financing transactions did not
change. The unrelated PUBLIC mission added only its own 10-unit payment.
Persisted state had two independently authorized missions, eight body-scoped
observations, two distinct body/world bindings, one project and one REGION
project location. PUB had four beliefs for each observed body; SPN retained
only its four COMET_HALLEY beliefs. No site, resource, settlement, or new
project arose from the second mission. Reconstructing the run and replaying
all committed epochs returned `ALREADY_MATCHED` throughout, with identical
observations and no duplicate mission, observation, project, or belief rows.
Negative probes rejected a forged project REGION origin and a Body B request
presented under Body A's binding. The focused test also checks mission-to-
observation body/world matching and the project's independent REGION parent.

**Verification.** The focused post-project governed persistence test passed
(`1/1`), including exact reopen/replay and both negative spatial probes.
Inherited body REMOTE persistence passed (`1/1`); prospecting and annual-study
persistence passed in a fresh history-free governed database (`3/3`, including
the region fail-closed probe); no-target reopen passed (`1/1`). The no-target
compiler tests passed (`3/3`), and the Build 6E named-world plus Build 7
generated-campaign unit suite passed (`14/14`). World Authority store/ETL/
security invocation reported `37` tests, `OK (skipped=34)`; the protected
security qualification cluster/admin credential was unavailable here, so the
new governed integration test supplies the exercised lifecycle/replay evidence
for this change. `git diff --check` passed. No broad 2026–2035 campaign was
run for this repair.

**Disposition.** This repairs the demonstrated post-project spatial compiler
limit only. It does not add recurring Explorer decisions, Sponsor comparison,
additional studies, or multi-project support. The broader Increment 6
qualification remains **BLOCKED** on the previously recorded causal gaps;
the 2026–2035 campaign has not been requalified by this repair.
## As-built campaign observation and causal break — 2026–2035 (2026-10-09)

**Disposition:** OBSERVED / BLOCKED. **Source revision:** `4b2a941fc76c25212d9aa6a7d0b783d71f95ceb7`. No simulation implementation changes. Executed the normal no-target `generated_campaign new --world-seed 2227` then `annual --through-year 2035` in the existing isolated interactive smoke database (not the authoritative baseline). Fresh run `SOLAR_MATERIAL_2977142cd46a6c47220617bb:ccc6daa019f1b3f0`, scenario `edea63f1-8fa0-5d72-a7be-941d6486cee6`.

Genesis: 90 generated bodies, 90 candidate missions, no projects, settlements or Offworld population. The annual run completed (about 57 s): 2026 PUBLIC REMOTE selection COMET_HALLEY and SPN initiation of `PROSPECT:COMET_HALLEY:BUILD7_PROSPECTING_REGION_02`; 2027 `AUTHORIZE`; 2028 `STUDY_SUPPORTS_ADVANCE`; 2029 `ADVANCE`; 2030–2035 `NO_ACTION`. Final project `EXPLORING`, maturity `SURFACE_OR_SAMPLE_CHARACTERIZED`, cash 0, one paid study, four REGION observations, one review, zero settlements/population. The fresh run committed its annual epochs. This is evidence of the current behavior, **not** full Increment 6 acceptance.

**Exact code-derived causal break** (`simulation/offworld_mvp/build7/generated_campaign.py`, source revision above):

1. `run_world_annual` (around lines 865–951) invokes `run_world_prospecting_initiation` once, retains `opening['project_id']` as a single local project, and never invokes the Explorer opportunity/mission path in later years.
2. `run_world_prospecting_initiation` (around line 782) rejects years other than 2026 with `BUILD7_INCREMENT4_SINGLE_DECISION_YEAR`; `_execute_world_remote_choice` (around line 681) rejects later years with `BUILD7_INCREMENT3_SINGLE_DECISION_YEAR`. These are explicit opening-scope guards, not World Authority failures.
3. The annual loop follows the one fixed `BUILD7_REGION_STUDY` activity. It can propose/authorize/spend, observe/complete, and review it. After `reviewed=True`, no further branch derives an eligible opportunity or invokes PUB/SPN policy; the final `annual.append((calendar_year,'NO_ACTION'))` is a conductor fallback. Even when `project_id is None`, `NO_ACTION` is appended without an Agent choice.
4. The opening Sponsor path derives opportunities only for the selected/characterized body and uses `choose_equivalent_region` to break ties among neutral regions. It is not an annual cross-target portfolio comparison. The existing Sponsor portfolio policy authorizes a *proposed activity*, not the selection of a target or a follow-on study. The 2029 `ADVANCE` changes recorded review/maturity state but does not generate a new governed scientific question, cost, or project financing authority.

**Diagnosis:** This is an incomplete Build 7 annual causal loop, not a legitimate economic decision to wait. The newly repaired post-project spatial admission path is not exercised by the ordinary later-year conductor, so the campaign neither proves nor disproves recurring multi-body exploration. The current code cannot use later observations to alter subsequent exploration/portfolio choices because it does not reopen those windows.

**Repair suggestions, ordered by observed necessity:**

- First, preserve this campaign as a behavioral baseline. Exercise the already demonstrated later-year PUBLIC policy/REMOTE path from a governed, isolated campaign with the first project retained; distinguish manual/fixture orchestration from normal annual gameplay. Then connect only the verified later-year Explorer window to the annual conductor. The conductor must not choose a body, and `WAIT` must remain possible. Preserve 2026 opening semantics, temporal visibility, correct spatial binding, and replay.
- Next, permit the Sponsor to compare genuinely visible new opportunities with its existing project and holding capital. This needs an explicit bounded portfolio choice, not repeated authorization of the same completed study. Reuse current prospecting/financing transitions; do not treat country financing capacity as project cash or force a second project.
- Only introduce a next study when it has an actual governed question, observation mechanism, cost, and funding authorization. Four-family presence evidence and `SUPPORTS_ADVANCE` do not establish deposit, reserve, recoverability, or development economics. Do not auto-advance to development or invent a favorable result to pass §25 I.

**Separate replay issue:** Attempting to reopen the *older* interactive smoke run `SOLAR_MATERIAL_ce54bc91cb1d6795a0357197:81faed42833ecd39` on this source revision failed with `IntegrityFailure: INCOMPLETE_SQL_ROW:wa_run.artifact` during `record_earth_reference_year`. This may be a cross-revision artifact mismatch; cause is unproven and must not be attributed to the spatial admission fix without further evidence. The fresh 2227 campaign ran successfully. Its independent replay is recorded separately if completed.

**No change authorization:** This record diagnoses and proposes bounded next actions only. Build 7 Increment 6 remains BLOCKED; PR #370 remains unmerged.

**Fresh-run replay verified:** Re-executing the ordinary `annual --through-year 2035` command for the new 2227 run completed with **43/43 epochs `ALREADY_MATCHED`**, no new committed epochs, and the identical 2027–2035 decision/status sequence, project ID, EXPLORING status, maturity, and zero cash. This confirms same-revision deterministic replay of the observed campaign; it does not resolve the separate older-run artifact mismatch.

## Priority 1 recurring Explorer closeout — 2026-10-09

**Implementation revision:** working-tree changes based on `7e6a9e684c31834a8a854b6b3ec6083d35047bdc` (not yet committed at time of this entry). The bounded change reopens the existing PUBLIC REMOTE choice/policy path in annual windows 2027–2035 and permits the persistence compiler to retain only the already-governed Build 7 prospecting-study assets alongside their validated project during an unrelated body REMOTE epoch. Existing project/REGION provenance, per-mission body binding, authorization, hidden-truth boundary, and finance checks remain enforced.

**Observed campaign:** fresh seed `2227`, run `SOLAR_MATERIAL_2977142cd46a6c47220617bb:6d280637302d8b99`, completed 2026–2035. PUBLIC selected COMET_HALLEY (2026), DEIMOS (2027), TRITON (2028), DAVIDA (2029), OUMUAMUA (2030), BENNU (2031), DIONE (2032), PHOBOS (2033), VESTA (2034), and NEREID (2035). Each REMOTE mission spent 10 model-currency units; PUBLIC balance moved 100 → 0. Each selected body received four material observations and corresponding PUB belief updates. No extra project, site, settlement, or population was created by these missions.

The original Comet Halley REGION 02 Sponsor project remained the sole project, retaining its earlier 2027 authorization, 2028 study completion, and 2029 ADVANCE review. Its final state was EXPLORING at SURFACE_OR_SAMPLE_CHARACTERIZED, with zero project cash; country F/X/R/S state remained as reported by the run. Sponsor continuation after 2029 remains unresolved: annual outputs were NO_ACTION through 2035, and this work does not establish that those labels came from a new Sponsor policy decision.

**Verification:** existing focused governed regression `test_recurring_explorer_persistence.py::RecurringExplorerPersistenceTests::test_later_visible_choices_preserve_region_project_and_replay` passed 1/1 against this implementation. The existing replay process completed; every epoch commit returned `ALREADY_MATCHED`, with the same decisions, observations, beliefs, and project state and no duplicate consequences. The replay output was truncated by the session tool, so an exact epoch count is unavailable. `git diff --check` passed. No additional campaign or test was run for this closeout.

**Disposition:** Priority 1 recurring PUBLIC exploration is demonstrated for this campaign. Increment 6 remains **BLOCKED**; Sponsor continuation/portfolio choice remains unresolved. PR #370 remains open and unmerged.

## Priority 2 recurring Sponsor opportunity closeout — 2026-10-09

**Implementation:** A narrow, non-executing annual SPN policy window now follows the
completed initial study review. Its request contains the retained project's admitted
status, study maturity and cash, remaining country financing capacity `F`, and
transient prospecting opportunities reconstructed from SPN's own admitted public
observations and four-family beliefs. Outcomes are `CONSIDER_PROSPECTING`,
`RETAIN_PROJECT`, `WAIT`, or `BLOCKED_UNKNOWN`. No outcome authorizes expenditure,
project creation, study activity, or maturity advancement. Equivalent eligible
alternatives use the existing stable keyed derivation and are selected by deterministic
tie-break; the policy makes no expected-return or economic-superiority claim.

**Observed campaign evidence (pre-correction policy version):** Fresh seed `2227` run
`SOLAR_MATERIAL_2977142cd46a6c47220617bb:085d6bb6f99d95bd` preserved the 2026–2029
Sponsor sequence `AUTHORIZE`, `STUDY_SUPPORTS_ADVANCE`, `ADVANCE`, then produced an
actual SPN `CONSIDER_PROSPECTING` policy decision in every year 2030–2035 from the
visible candidate set and unchanged financing capacity `F=29.58025335469291`.
The sole Comet Halley REGION 02 project remained `EXPLORING`; no second project or
spending resulted. Replay returned **175/175 `ALREADY_MATCHED`**. This replay evidence
predates the terminology-only correction from `VISIBLE_ALTERNATIVE_FUNDED` to
`VISIBLE_ALTERNATIVE_WITHIN_FINANCING_CAPACITY`; it is not represented as replay of
the corrected policy version.

**Corrected focused verification:**
`test_recurring_explorer_persistence.RecurringExplorerPersistenceTests.test_later_visible_choices_preserve_region_project_and_replay`
passed **1/1** in 536.665 s. It verifies the corrected reason code, recurring visible
Sponsor candidates, preservation of the single project and capital state, and exact
replay without duplicate persisted consequences. `git diff --check` passed.

**Disposition:** Priority 2's bounded recurring Sponsor opportunity decision is
verified. Increment 6 remains **BLOCKED** on subsequent investment execution, new
scientific studies, multi-project behavior, and downstream development qualification.
PR #370 remains open and unmerged.
