# LOOM Offworld Build 7 Acceptance Criteria

**Status:** Build 7 completion gate  
**Branch:** `offworld-mvp-build7-hidden-world`  
**Scope:** Finish Build 7 as the first complete generated-world Offworld simulation baseline. Do not create Build 8 for this work.

## 1. Generated hidden WORLD coverage

- Build 7 uses the existing generated/hidden WORLD as the physical simulation source.
- The same executable path must work against **100% of bodies eligible in the pinned hidden-world catalog**.
- At the current pinned baseline the expected eligible count is **90 bodies**.
- Eligibility must be discovered from authority/policy inputs, not hard-coded as a 90-name list.
- Earth, Jupiter, Saturn, Uranus and Neptune remain excluded under the current material-model applicability rules.
- No body-specific runtime path may be required for Cabeus, Ceres, Moon, Mars, or the historical four-body portfolio.

## 2. Epistemic separation

- Hidden physical truth remains distinct from actor-visible knowledge.
- `R_IN_SITU` may exist as hidden WORLD truth.
- `R_ACCESSIBLE` and `R_RECOVERABLE` remain unknown until a legitimate capability/assessment earns them.
- Prospecting, observations, and later capability assessment are the routes by which actors gain corresponding knowledge.
- No dummy resource, genericized Cabeus, or privileged actor access to hidden WORLD state.

## 3. Full existing Offworld chain

Build 7 must connect the generated WORLD to the existing simulation machinery so a campaign can proceed, where conditions permit, through:

`WORLD -> GENESIS -> remote prospecting -> surface prospecting -> publication -> sponsor decision -> financing -> development -> capability/recoverability -> operations/extraction -> market sale -> surplus/reinvestment -> settlement infrastructure -> transport/population -> enterprise review -> subsequent operation`

Early termination is valid. A barren body, negative prospect, abandoned project, rejected financing, unavailable recovery process, or uneconomic operation is a successful simulation outcome if produced honestly.

## 4. Capability/recoverability transition

- Prospecting must not itself manufacture recoverability.
- Build 7 must use existing generated-world physical/environmental state and existing capability machinery to determine accessibility/recoverability only when an appropriate development/process capability exists.
- Reuse the existing `bind_generated_target()`-style physical checks where suitable rather than inventing a new resource architecture.
- Conservation of in-situ, accessible, recoverable, and remaining material must hold.

## 5. 2026-2045 simulation horizon

- Official Build 7 operational horizon: **2026 through 2045 inclusive**.
- This is the maximum required qualified horizon for this release.
- Build 7 does not claim to be a validated 2026-2226 Offworld simulation.
- Campaigns must be able to persist, resume, and continue across multiple years within this horizon rather than merely execute one scripted demonstration.

## 6. Earth demographic and economic authority

- Build 7 must consume the **current promoted LOOM Earth demographic and economic authority**, not the old thin fixed Earth fixture as its substantive Earth state.
- Annual Earth values must roll forward with simulation year.
- Relevant current authority includes biological population/demographic state, value added, gross output, investment, productive capital, and relevant labor state where applicable.
- The current promoted Earth authority remains the source, with its own authority distinctions and provenance preserved.
- Earth economic indicators are context/resources for the simulation, not automatically spendable actor budgets unless an existing rule legitimately maps them into one.

## 7. Earth geographic scope

- For the present Offworld campaign machinery, **USA annual Earth state** is the default consumed Earth economic/demographic context because the existing Earth node is `EARTH:USA`.
- The broader promoted Earth authority remains available, currently covering 237 demographic areas and 80 economic economies.
- Other countries are consumed only when an actual modeled actor, relationship, or event requires them.
- Do not build a global macroeconomic simulator merely because the data exists.

## 8. Technology handling

- Build 7 may hold **2026 technology capability state fixed through 2045**.
- No technological progress model is required for this update.
- Existing technology/capability state may persist across the entire run unless changed by already-existing legitimate simulation machinery.
- Build 7 must not invent post-2026 capability merely because time passes.

## 9. Timeline availability

- The complete current LOOM Timeline projection must be available to Build 7.
- At the current pinned baseline the expected projection count is **43 milestones**.
- Authority distinctions must be preserved.
- Timeline data is contextual/frontier information only.
- A milestone date must **not automatically create technology, capacity, assets, settlements, access, or knowledge**.
- No automatic Timeline unlocks.

## 10. Persistence and deterministic resume

- GENESIS must establish the World Authority run binding through the existing lifecycle.
- Every committed simulation epoch must persist through World Authority.
- Campaigns must reopen through the normal bound-world path.
- Resume must reproduce the existing prefix as matching history and continue from the correct next state.
- Same seed + inputs + code must reproduce the same WORLD/run/history.
- No duplicate history on replay.

## 11. Clean forward runtime

- Build 7 must have a normal forward-simulation entrypoint under `simulation/offworld_mvp/build7/`.
- The normal Build 7 runtime must no longer depend on `build6e/qualification/build6e_fixture.py` as its orchestration engine.
- Reuse of underlying qualified kernel classes/functions is encouraged.
- Build 6/6E remains historical qualification/regression material.
- Do not create a parallel simulator.

## 12. Qualification

### Breadth

All currently eligible hidden-world bodies must be able to generate, start a campaign, commit an opening/first legitimate epoch, persist, and reopen through the same Build 7 runtime path.

### Behavioral depth

Deterministic cases must demonstrate at least:

- zero/absent target -> negative/abandon path;
- positive physical target but unsuccessful economic/project outcome;
- viable target that reaches development/operation;
- one case reaching the deepest existing chain including extraction, market, and settlement/transport if the existing economics legitimately allow it.

### Temporal depth

At least one campaign must demonstrate annual Earth roll-forward and persistence/resume beyond the initial scripted chain toward the **2045 boundary**.

Existing relevant regression tests must continue passing.

## 13. Git/GitHub completion

- Continue on `offworld-mvp-build7-hidden-world`.
- Do not create Build 8 for this work.
- Update PR #370 with the completed integration.
- Review the full diff for temporary/debug/generated junk.
- Push the exact tested commit.
- Do not merge until the completed Build 7 acceptance suite passes.
- Report the exact tested SHA.

## Stop condition

Build 7 is finished when:

> **Any currently eligible generated hidden-WORLD body can enter the same 2026-2045 Offworld simulation, using authoritative annual LOOM Earth demographic/economic state, fixed 2026 technology, read-only Timeline context, legitimate discovery/capability semantics, the full existing decision/economic/settlement chain where conditions permit, and deterministic World Authority persistence/resume, without Cabeus or any other body-specific runtime dependency.**

After this gate is satisfied, stop engineering Build 7 and use the simulation.
