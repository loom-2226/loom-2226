# Build 7 Increment 1–3 Repair and Validation Record

**Class:** ENGINEERING RECORD
**Scope:** Build 7 Increments 1–3 repair provenance plus Increment 4 maintainer decisions recorded before implementation
**Status:** HISTORICAL IMPLEMENTATION / REPAIR PROVENANCE
**Branch:** `offworld-mvp-build7-hidden-world`
**PR:** #370
**Does not establish:** new FRD authority, new acceptance criteria, implementation completion, qualification, or authority for the preliminary semantic causal model map. Increment 4 entries below record maintainer decisions within the already-authorized Increment 4 scope.

## Purpose

This record preserves material implementation blockers, maintainer decisions, repairs, and closure evidence encountered while implementing Build 7. It also records bounded maintainer decisions made before Increment 4 implementation. It is a provenance aid, not a substitute for governing authority.

Git commits and repository authority outrank this summary. The Codex rollout history was used only to recover the sequence of stops, findings, and maintainer-directed repairs; it is not repository authority.

## Evidence basis

- Governing Build 7 authority: `OFFWORLD_MVP_GUIDING_FRD.md`, `BUILD7_ACCEPTANCE_CRITERIA.md`, `BUILD7_EMERGENCE_IMPLEMENTATION_GUIDE.md`, and scoped `AGENTS.md`.
- Preserved targeted-consequence baseline: `8b19259223346ed91a7280687c4fa3dbdd765640`.
- Codex thread: `01a1156b-a4b1-7f02-b776-15ab37ab1c1a`.
- Codex rollout: `/home/ubuntu/.codex/sessions/2026/10/07/rollout-2026-10-07T19-12-18-01a1156b-a4b1-7f02-b776-15ab37ab1c1a.jsonl`.
- Increment 1 tested commit: `3c7e9240355c46be31dd034523e933e18b651bfd`.
- Increment 2 authority-map commit: `02baa99864cf1365069db1e4e88a920abe7d075a`.
- Increment 2 tested commit: `7c48657bb9cf955702a9ee17b46470276daeb82d`.
- Non-authoritative semantic-map commit `0ae37ccc94b7509f231c9edc91049d07e2ba9d03` was removed by `a0f3ec57010e10bbb3eaa41b0960a84dc0b847f1` and was not used as implementation authority.
- Increment 3 first tested commit: `de2f16753b173a4e2c3a9baeebf2e65631a22a64`.
- Increment 3 material-characterization repair: `271462478490075f32b73aeea449bad192728323`.

---

## Increment 1 — No-target GENESIS + persistence

### I1-R01 — Existing persistence compiler required a selected location binding

**Initial finding:** BLOCKED before implementation.

The Build6E persistence compiler required a `NamedLocationBinding`. Its opening projection always emitted a world binding and target-dependent physical/project/settlement rows. A genuine no-target GENESIS had none of those identities or entities.

A Build 7-local persistence compiler would have duplicated governed persistence. A dummy binding would have fabricated the very target Increment 1 was required to remove.

**Maintainer-authorized repair:** Generalize the existing shared compiler narrowly for `binding=None`.

For an unbound opening, persist only target-independent run, causal, admission, actor/system, and Earth-origin state. Omit world binding, physical stock, project location, settlement, target-bound mission/observation, and Offworld population rows. On replay, skip bound-world loading and bound-resource head comparison while retaining normal run-head and causal replay checks. Preserve the existing bound path.

**Repair commit:** `3c7e9240355c46be31dd034523e933e18b651bfd`.

**Closure evidence:**
- focused no-target tests: 4/4;
- relevant Build6E/Build7/World Authority unit tests: 18/18;
- World Authority security suite: 33/33 on disposable PostgreSQL 18;
- Build6E transaction surface: 5/5;
- inherited Build 7 breadth: 90/90 openings committed and reopened as `ALREADY_MATCHED`;
- inherited and changed bound opening compilers matched across 222 rows and terminal references;
- `git diff --check`: PASS.

**Disposition:** CLOSED.

### I1-Q01 — Breadth replay invalidated by changing compiler during the run

An early breadth attempt failed because the compiler changed while the qualification run was in progress, invalidating the pinned replay input hash.

**Repair:** rerun from a stable source tree after the implementation stopped changing.

**Closure:** stable-source breadth run passed 90/90.

**Disposition:** CLOSED as a qualification-execution issue. No runtime semantic change resulted.

---

## Increment 2 — Public Solar opportunities

### I2-R01 — No legitimate body-differentiated accessibility input

**Initial finding:** BLOCKED at the accessibility gate.

The public catalog identified all 90 eligible bodies, but the admitted CIVPROP accessibility package did not provide comparable Earth-to-body accessibility across the candidate universe. It contained narrow Earth–Moon material and could not legitimately rank the 90 bodies. Target-specific fixture costs could not differentiate bodies, and hidden generated heliocentric state could not be used without violating the epistemic firewall.

**Repair path:**
1. Pin the public accessibility authority/reference map in `02baa99864cf1365069db1e4e88a920abe7d075a`.
2. Build an offline preliminary accessibility compiler using existing qualified Solar/SPK authority and promoted DE440 Earth coverage.
3. Sample bounded departure dates and times of flight and use Sun-centered prograde zero-revolution Lambert calculations only as a comparison screen.
4. Persist the compiled screen as runtime input so runtime has no SPICE/Lambert dependency.
5. Preserve `UNKNOWN` where the screen cannot produce a qualified comparison.
6. Derive immutable public mission candidates from public body identity, screen result, actor capability, year, and provenance only.

**Tested repair commit:** `7c48657bb9cf955702a9ee17b46470276daeb82d`.

**Resulting boundary:** 83 bodies/year are `SCREENED`; seven remain `UNKNOWN`. Departure-v∞ + arrival-v∞ is a preliminary comparison burden, not operational trajectory feasibility, final mission ΔV, or destination attractiveness.

**Closure evidence:**
- focused/inherited unit suite: 19 passed;
- focused opportunity rerun: 3 passed;
- governed no-target commit/reopen/2027 replay: 1 passed with 90 candidates and identical replay digest;
- targeted persistence regression preserved;
- offline artifact recomputation `--check`: PASS;
- `git diff --check`: PASS;
- hidden-world counterfactual produced identical candidates;
- no named body or historical fixture received a special selection rule.

**Disposition:** CLOSED.

### I2-Q01 — Exact-harness and local test invocation issues

During development, one targeted replay correctly rejected a changed input under the exact-harness guard, and early test setup required the repository `PYTHONPATH`.

**Repair:** rerun against the final pinned implementation with the repository test environment correctly configured.

**Disposition:** CLOSED as development/qualification execution issues. No model semantics changed.

---

## Increment 3 — Endogenous public exploration

### I3-R01 — Existing authority could not justify a positive exploration choice

**Initial finding:** BLOCKED before implementation.

The 90 candidates exposed public identity, class, preliminary accessibility, and capability, but the normal no-target run had zero public cash, no admitted REMOTE mission cost, no candidate-specific information-value relationship, and no general Solar-wide continuation economics. The existing Mission/Knowledge EVSI machinery correctly returned WAIT when follow-on value was UNKNOWN.

**Maintainer decision:** Increment 3 uses a bounded **decision-relevant information need**, not full economic EVSI. The prospective decision is whether to preserve a body as a candidate for future Offworld use by acquiring additional characterization. Public exploration receives an explicit opening balance of 100 model-currency units and REMOTE characterization costs 10. F/X/R/S mobilization remains outside this increment.

**Disposition:** CLOSED by the Increment 3 implementation path. Rich valuation remains deferred to Increment 4.

### I3-R02 — Candidate-specific information question was missing

**Finding:** BLOCKED.

The candidate representation had no scoped proposition or observation question. Existing sponsor evidence gates required an existing project/resource and therefore could not define pre-project information demand. Hidden generated deposits could not be used to define pre-observation interest.

**Maintainer decision:** Admit a body-level prospective information-acquisition question. `SCREENED` is sufficient only to consider a candidate for preliminary REMOTE characterization. It does not establish operational mission, development, transport, or commercial feasibility. `UNKNOWN` remains ineligible/blocked.

**Disposition:** CLOSED by the body-characterization mission contract.

### I3-R03 — Qualified observation path was project/resource bound

**Finding:** BLOCKED at the execution handoff.

The existing paid exploration request required project and resource IDs, charged project cash, created project-owned exploration WIP, and read a materialized resource. No-target GENESIS intentionally had none. The older project-free observer was explicitly blocked as an unqualified legacy transition.

**Maintainer-authorized repair:** Generalize the existing governed observation path only enough to admit two concrete cases:
1. existing project/resource observation, unchanged;
2. project-free body-level REMOTE characterization tied to a selected body and governed question.

Use the same WORLD_SIM authority, provenance/evidence, scheduler/replay, and belief-update machinery. Do not create a second observer, dummy project, dummy resource, or generic subject framework.

**Disposition:** CLOSED in `de2f16753b173a4e2c3a9baeebf2e65631a22a64`.

### I3-R04 — World Authority required a surface/location target

**Finding:** BLOCKED at persistence.

`wa_run.mission.target_location_id` and `wa_run.observation.location_id` were mandatory. A body-wide REMOTE mission had a public body identity but no legitimate surface/site location. Reusing the hidden generated site would have implied site selection before observation.

**Maintainer-authorized repair:** Admit a narrow BODY-level REMOTE spatial scope in World Authority while preserving the existing LOCATION-level observation scope. Location may be absent only for the governed body-remote mission/observation contract. Matching mission/body/world identity remains enforced. No synthetic site is created.

**Repair:** migration `002_body_remote_observation.sql`, store/compiler/runtime changes in `de2f16753b173a4e2c3a9baeebf2e65631a22a64`.

**Disposition:** CLOSED. Subsequent hostile review found the body-scoped exception narrow and defensible.

### I3-R05 — First completed implementation narrowed generic characterization to water

**Finding after hostile review:** HOLD.

The first completed Increment 3 implementation worked mechanically, but the universal mission question was hard-coded as `WATER_BEARING_MATERIAL_PRESENT`. That silently narrowed the authorized decision-relevant characterization mechanism to water prospecting.

This was not hidden-truth leakage or named-body steering. It was a semantic narrowing of the information being acquired.

**Baseline implementation:** `de2f16753b173a4e2c3a9baeebf2e65631a22a64`.

**Research recovery:** M4B already defines four resource/material evidence families:
- `VOLATILES`;
- `METALS`;
- `SILICATES_ROCK`;
- `CARBONACEOUS_ORGANICS`.

Research Lab PR #147 documented the water-only hidden-WORLD prior/generation work but did not itself authorize runtime changes.

**Disposition:** REPAIR REQUIRED before Increment 4.

### I3-R06 — Four-family evidence existed, but generation and sensing semantics did not

**Finding:** BLOCKED before the repair was coded.

M4B establishes family names, evidence states, and scope, but mostly reports `UNKNOWN_AFTER_SEARCH`; it does not provide whole-body abundance or occurrence probabilities. Research Lab PR #147 supplies a fictional prior/generation policy only for water-bearing material. Existing 0.80 detection / 0.20 error semantics were likewise water-question parameters.

A code-only generalization would therefore have invented generation and sensing semantics without maintainer authority.

**Maintainer-authorized repair:**
- use broad body-regime-conditioned authored priors for coarse fictional PRESENT/ABSENT hidden truth across the four M4B families;
- label the priors explicitly as high-sensitivity fictional scenario inputs, not empirical occurrence probabilities;
- preserve `UNKNOWN_AFTER_SEARCH != ABSENT/zero`;
- do not extrapolate local/sample evidence to whole-body abundance;
- preserve existing water presence as implying volatile presence;
- use one deliberately coarse shared REMOTE observation abstraction for Increment 3 with authored 0.80 detection and 0.20 false-positive semantics;
- produce family-specific observations and beliefs;
- create no reserve, recoverability, grade, economic value, project, site, or resource conclusion.

**Repair commit:** `271462478490075f32b73aeea449bad192728323`.

**Closure evidence:**
- four family-specific hidden states and observations;
- hidden truth read only inside the authorized WORLD_SIM transition after mission authorization;
- hidden-truth twin retains identical pre-observation choice;
- family-specific beliefs update independently;
- one mission payment produces four bounded characterization observations;
- selected body only receives mission/observation/knowledge consequence;
- no project/site/resource/reserve/recoverability state is fabricated;
- governed no-target/body-observation suite: 5/5;
- targeted breadth: 90/90 openings and 90/90 exact replays;
- inherited targeted case reached 2045 and reopened with 33/33 epochs `ALREADY_MATCHED`;
- `git diff --check`: PASS.

The final inherited/unit run reported 57 passed and 33 dedicated security-cluster tests skipped because the admin credential was unavailable. This repair did not change World Authority schema/store; the directly affected governed persistence suite passed.

**Disposition:** CLOSED after hostile review of `271462478490075f32b73aeea449bad192728323`.

### I3-Q01 — Temporary deterministic tie-break

The keyed deterministic tie-break among otherwise equivalent eligible candidates is accepted only as bounded Increment 3 behavior. It is replay-safe, order-independent, hidden-truth-independent, and contains no named-body preference.

It is not a substantive destination-value model.

**Disposition:** ACCEPTED FOR INCREMENT 3. Reassessment of competing information-acquisition value is explicitly deferred to Increment 4 in `INCREMENT4_EXPLORATION_VALUATION_DEFERRED.md`.

---

## Increment 4 — Pre-implementation maintainer decisions

These decisions resolve the bounded readiness questions identified before Increment 4 implementation. They authorize the smallest implementation within the existing Increment 4 objective. They do not mark Increment 4 implemented or qualified.

### I4-D01 — REMOTE material-family evidence creates a prospecting opportunity, not a development conclusion

**Status:** RESOLVED FOR INCREMENT 4 / PROVISIONAL MODEL / IMPLEMENTATION PENDING.

Sufficiently relevant actor-visible REMOTE material-family evidence may create a **prospective commercial prospecting opportunity**. The proposition is that available evidence may justify spending private capital to characterize a body further.

Family presence or belief does **not** establish abundance, concentration, grade, accessibility, recoverability, reserve, production rate, extraction cost, or development value. A sponsor-authorized project at this stage is therefore a prospecting project. Development/extraction requires later evidence and later authorized decisions.

This is a deliberately coarse Increment 4 bridge. Preserve the future option to replace or augment it with richer prospective-resource models, including probabilistic quantity/concentration/accessibility/recovery and information-value treatment, if later simulation behavior earns that complexity. No such richer machinery is authorized here.

### I4-D02 — Use a minimal prospecting-economic scenario input

**Status:** RESOLVED FOR INCREMENT 4 / PROVISIONAL MODEL / IMPLEMENTATION PENDING.

Increment 4 uses a small, versioned prospecting-economic scenario input containing only the model-currency cost/value assumptions required to decide whether further prospecting is worth financing. Do not reinterpret development/extraction validation fixtures as prospecting economics.

Where an existing qualified parameter has genuinely matching prospecting semantics it may be reused; otherwise add only the minimum explicit authored Increment 4 parameter. Such values are high-sensitivity model abstractions, not empirical forecasts.

Earth investment remains a real-economic capacity proxy rather than spendable actor cash. The existing capital-coupling abstraction must provide the explicit bounded mapping from Earth capacity into model-currency Offworld financing; do not silently reinterpret the Earth investment series as cash.

### I4-D03 — Preserve the existing Earth–Offworld capital-coupling abstraction

**Status:** RESOLVED BY EXISTING AUTHORITY / IMPLEMENTATION PARAMETERIZATION PENDING.

Do not introduce a new mobilization model. Implement the already-authorized country-level coupling state and equations:

- F(c,t): cash available for new Offworld financing;
- X(c,t): outstanding country-origin Offworld capital exposure;
- R(c,t): realized Offworld cash returned during the period;
- S(c): strategic pressure;
- M(c,t) = I(c,t) * m(c,t);
- 0 <= m(c,t) <= m_max;
- m = f(CommercialOpportunity, StrategicPressure).

Commercial opportunity and strategic pressure remain distinct causal inputs under the governing abstraction. Increment 4 may author only the minimum bounded numerical parameterization required to exercise that abstraction. It does not authorize a new additive/nonlinear formula, banks, securities, portfolio optimization, or sponsor risk-tolerance subsystem.

Existing transaction semantics remain authoritative: commitment alone is not disbursement; actual disbursement reduces available financing and increases exposure; actual return/loss reduces exposure according to the declared transaction; successful return is recorded as realized return. Any richer reinvestment behavior remains governed by the existing abstraction and later earned implementation, not this decision.

### I4-D04 — Prospecting projects target one of ten coarse prospecting regions

**Status:** RESOLVED FOR INCREMENT 4 / PROVISIONAL MODEL / IMPLEMENTATION PENDING.

Each eligible body has **10 deterministic coarse prospecting regions** used by this simulation mechanism. They are stable spatial subdivisions and convey **no implied geology, resource presence, or economic value**.

A prospecting project targets exactly one such region. Use the existing World Authority spatial ontology rather than inventing a second area subsystem: prospecting areas are body-anchored wa_geo.location spatial identities with REGION semantics, and project/location association uses the existing governed project-location relationship.

The ten-region partition is the uniform simulation prospecting geography. Existing empirical/scientific locations may remain in World Authority but do not give a body extra prospecting opportunities or an authored attractiveness advantage.

Region selection does not imply a site or deposit. Hidden WORLD properties may vary regionally. Prospecting may produce regional evidence. Site refinement and deposit/resource-development conclusions remain downstream and must be earned by evidence.

The ten-region partition is provisional. Richer spatial subdivision may replace or augment it later if simulation behavior demonstrates that additional resolution matters.

### I4-D05 — Sponsor consumes public observations, not PUB posterior beliefs

**Status:** RESOLVED FOR INCREMENT 4 / PROVISIONAL MODEL / IMPLEMENTATION PENDING.

A genuinely PUBLIC observation is legitimate actor-visible evidence for the sponsor. SPN ingests the public observation and updates/maintains its **own** material-family beliefs through the governed information/belief machinery.

Do not copy PUB's private posterior or belief state into SPN. Hidden WORLD truth remains inaccessible except through authorized observation.

The causal bridge is:

WORLD truth -> PUBLIC observation -> SPN information -> SPN belief -> SPN decision.

Existing body-level REMOTE evidence does not reveal which of the ten prospecting regions is preferable. Where regions remain information-equivalent, region choice uses the smallest deterministic/replay-safe tie-break. Regional differentiation must arise from legitimate subsequent prospecting evidence, not hidden truth or authored named-region preference.

Richer information institutions such as proprietary surveys, publication delay, information markets, or secrecy remain future options and are not authorized by this decision.

---

## Increment 4 — Implementation disposition

### I4-Q01 — Bounded prospecting initiation closure

**Status:** CLOSED FOR INCREMENT 4.

The implemented seam preserves I4-D01 through I4-D05:

- actor-visible four-family PUBLIC observations update SPN's own beliefs;
- qualifying evidence creates a transient prospecting opportunity, not a resource or development conclusion;
- a versioned high-sensitivity scenario supplies prospecting cost `20`, information value `30`, Earth-investment normalization `1,000,000,000` proxy units per model-currency unit, and `m_max = 0.01`;
- absent authority for weights or a response curve, either qualifying commercial opportunity or positive strategic pressure activates the same bounded `m_max`, while neither activates zero; both causal inputs remain separate in the mobilization record;
- actual disbursement, rather than commitment, decreases `F`, increases `X`, and produces the existing Earth-shadow diversion;
- all 90 eligible bodies receive exactly ten deterministic, geology-neutral `REGION` locations;
- only an isolated SPN `INITIATE_PROJECT` decision creates one `EXPLORING` prospecting project at one region;
- no site, deposit, resource, reserve, recoverability, development, settlement, or Offworld population is created.

**Material qualification findings:**

- the promoted Earth investment value must be converted through its decimal text, not directly from a binary float;
- region UUIDs must remain typed UUIDs at the World Authority persistence boundary for exact immutable-row replay;
- SPN body-belief persistence must identify the governed body/question contract rather than depend on Python import aliases;
- the full project-creation run and exact replay persisted one project, one project-location row, four independent SPN body beliefs, `20` model-currency disbursed, `X = 20`, nonnegative retained `F`, and no forbidden physical/development rows;
- the inherited targeted REMOTE campaign committed once and repeated with all six epochs `ALREADY_MATCHED`.

The exact tested Git SHA is the commit containing this closure entry and is reported in the PR disposition and completion report. Increment 5 remains unimplemented.

---

## Increment closure state

| Increment | Final tested SHA | Repair disposition |
|---|---|---|
| 1 | `3c7e9240355c46be31dd034523e933e18b651bfd` | CLOSED |
| 2 | `7c48657bb9cf955702a9ee17b46470276daeb82d` | CLOSED |
| 3 | `271462478490075f32b73aeea449bad192728323` | CLOSED |
| 4 | Commit containing I4-Q01; exact SHA in completion report | CLOSED |

I4-D01 through I4-D05 remain the governing bounded decisions for this closure.

## Use of this record

When a later change touches a repaired seam above, use the cited commit, governing Build 7 authority, and current tests as the implementation evidence. This record explains the historical reason for the seam; it does not override current Git authority or authorize broader architecture.

## Increment 5 — REGION study and annual handoff

### I5-D01 — REGION-scoped prospecting observation contract

**Finding:** The inherited surface prospecting action required a resource, while the I4 project owns only one geology-neutral REGION.

**Maintainer resolution:** An authorized paid study may observe that project's selected REGION through WORLD_SIM and return bounded material-family evidence. The observation itself establishes no site, deposit, resource, reserve, recoverability, or development value.

**Implementation:** The existing Build 6B activity spends project cash through EXPLORATION_WIP. A narrow REGION observation transition reads the selected REGION's hidden state only after the sponsor's activity authorization, emits four noisy signals, and updates SPN's own regional family beliefs. The existing Build 6B result, information admission, and sponsor review transitions consume the completed study.

### I5-D02 — provisional hidden REGION material-family realization

**Finding:** Body-level material truth could not answer a REGION study without an unsupported spatial inference.

**Maintainer resolution:** Add hidden, body-conditioned fictional family presence across the ten existing REGION identities. This is a **PROVISIONAL MODEL**, not geology or an empirical occurrence estimate. The shared regional presence fraction `0.35` is a **HIGH-SENSITIVITY FICTIONAL SCENARIO INPUT**. A body-absent family is absent in all ten REGIONs; a body-present family occurs in at least one and not all ten REGIONs. Keyed generation is independent of Agent choice and stable on replay.

**Implementation:** Generated WORLD stores four coarse hidden family states per REGION. A narrow World Authority read resolves persisted project REGION to its body and existing run WORLD, fails closed on missing or ambiguous identity, and never creates a new world binding. The REGION truth enters only the authorized WORLD_SIM study transition.

### I5-Q01 — bounded annual disposition

**Verification:** The 2026–2029 governed fixture created one I4 prospecting project, paid one Build 6B study from its `20` model-currency project cash, persisted four REGION observations and SPN belief updates, resolved WIP to KNOWLEDGE, and admitted a structural study result. The 2029 sponsor review consumed that result and took an adjacent maturity decision. Reopen matched every prior epoch without duplicate project, expense, observation, or review. The existing 90-body/900-REGION catalog was unchanged. A no-project annual run also persisted no-action years. The accounting auditor recognizes only the actual WIP-to-KNOWLEDGE conversion, leaving cash conservation checks in force.

**Disposition:** Increment 5 stops at information/study maturity. No site, resource quantity, grade, recoverability, reserve, development economics, production, settlement, or Increment 6 behavior is inferred or activated.
