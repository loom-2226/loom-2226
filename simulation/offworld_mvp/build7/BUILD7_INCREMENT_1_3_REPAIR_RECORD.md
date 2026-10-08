# Build 7 Increment 1–3 Repair and Validation Record

**Class:** ENGINEERING RECORD
**Scope:** Build 7 Increments 1–3 only
**Status:** HISTORICAL IMPLEMENTATION / REPAIR PROVENANCE
**Branch:** `offworld-mvp-build7-hidden-world`
**PR:** #370
**Does not establish:** new FRD authority, new acceptance criteria, new runtime semantics, Increment 4 authorization, or authority for the preliminary semantic causal model map.

## Purpose

This record preserves material implementation blockers, maintainer decisions, repairs, and closure evidence encountered while implementing Build 7 Increments 1–3. It is a provenance aid for understanding why the resulting implementation differs from the first attempted path.

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

## Increment closure state

| Increment | Final tested SHA | Repair disposition |
|---|---|---|
| 1 | `3c7e9240355c46be31dd034523e933e18b651bfd` | CLOSED |
| 2 | `7c48657bb9cf955702a9ee17b46470276daeb82d` | CLOSED |
| 3 | `271462478490075f32b73aeea449bad192728323` | CLOSED |

Increment 4 was not started by any repair recorded here.

## Use of this record

When a later change touches a repaired seam above, use the cited commit, governing Build 7 authority, and current tests as the implementation evidence. This record explains the historical reason for the seam; it does not override current Git authority or authorize broader architecture.
