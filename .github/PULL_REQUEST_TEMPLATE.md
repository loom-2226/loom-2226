# LOOM Pull Request Contract

> **GitHub outranks the chat.** Complete this template from current repository state, not remembered context.

## Change identity

**Primary change class** — choose one:

- [ ] `class:research`
- [ ] `class:canon`
- [ ] `class:engineering`
- [ ] `class:runtime`
- [ ] `class:data`
- [ ] `class:asset-media`
- [ ] `class:governance`

**Parent issue / work item:**

**Workstream:**

**Current authority tier:**

**Promotion target:**

## Purpose

What problem or decision does this PR address?

## Mutation scope

### Changes

List the files/components intentionally changed.

### Explicit non-scope

State what this PR deliberately does **not** change.

## Authority / canon impact

- [ ] No canon impact.
- [ ] Raises a canon finding only; does not modify canon.
- [ ] Approved CCR exists and is linked below.
- [ ] Current canon is modified under `class:canon`.

**CCR (if applicable):**

## Dependencies and invalidation

**Upstream authorities/dependencies checked:**

**Downstream dependents checked:**

Classify affected downstream components where applicable:

- [ ] `UNCHANGED_COMPATIBLE`
- [ ] `REVIEW_REQUIRED`
- [ ] `REVALIDATION_REQUIRED`
- [ ] `MIGRATION_REQUIRED`
- [ ] `BLOCKED_PENDING_UPSTREAM`
- [ ] `SUPERSEDED`

## Runtime / data / schema impact

- [ ] No runtime/data/SQLite impact.
- [ ] Runtime behavior changes.
- [ ] Schema/migration changes.
- [ ] Release manifest/compatibility changes.
- [ ] Pixel/Windows launcher/update behavior changes.

Describe impact and recovery path if any:

## Asset / media / 3D impact

- [ ] None.
- [ ] Representational only.
- [ ] Consumes authoritative engineering parameters.
- [ ] Changes authoritative geometry/packaging inputs.

Describe impact:

## Research freeze / preregistration

- [ ] No frozen/preregistered object affected.
- [ ] Successor work only; frozen source remains untouched.
- [ ] This PR touches a frozen/preregistered object — **STOP unless an explicit governance rule permits it.**

**Relevant frozen SHA / preregistration:**

## Testing / qualification

Required class:

- [ ] Documentation/governance only — no functional tests required.
- [ ] Unit regression.
- [ ] Unit + functional tests.
- [ ] Full end-to-end production regression.
- [ ] Exact preregistered scientific qualification.
- [ ] Other — explain below.

**Tests performed / evidence:**

## Vendor / AI / black-box assurance

Does this PR introduce or materially depend on an external vendor, API, hosted service, AI model, opaque algorithm, proprietary dataset, or other black box?

- [ ] No.
- [ ] Yes — provider, documented capability, cost/licensing, data handling, portability/lock-in and fallback are described below.

**Assurance notes:**

## Recovery / rollback

State exact recovery point, rollback method, or why rollback is not applicable.

## WALTER / #LOOMSAFE

- [ ] I have checked the declared scope against current workstate and authority.
- [ ] I have not treated an LLM/model output as evidence without source/test support.
- [ ] I have not silently crossed authority classes.
- [ ] I have not changed a frozen experiment merely because the improvement looked useful.

**Known assurance concern / accepted risk / exception ID:**

## Final statement

I have described what this PR changes, what it does not change, and the evidence required for its intended promotion.
