# LOOM 2226 — E1.1 Claude Independent Validation Packet v0.1

**Purpose:** independent hostile review from repository authority, not chat claims.

## Authority / target

Repository: `loom-2226/loom-2226`

Pull request: **#110 — E1.1: add read-only Canon Context Projection**

Branch: `engineering/experience-one-e1-1-canon-context-projection-2026-09-12`

Expected pre-validation head before this packet was added:

`422e2b31125753ac6d94318fe3518e78de5668e0`

The reviewer must re-fetch PR #110 and record the actual head SHA before drawing conclusions. GitHub outranks this packet if anything differs.

PR #110 is stacked on E1.0 PR #109. G1 baseline capture remains open, so only additive/non-replacement E1.1 work is authorized.

## Reviewer instruction

Do not accept any statement in this packet, prior chat, or finding document as evidence by itself. Validate directly from GitHub source, tests, diffs, and governing files.

The review question is not "does this look sensible?" It is:

> Has E1.1 earned a bounded, read-only path from authoritative campaign/world state to operator-facing context without creating duplicate state, calculation, canon, or model authority?

Return **PASS / PASS WITH CONDITIONS / REPLAN / FAIL** with exact file/line or diff evidence and explicit falsifiers.

## Governing constraints to verify first

Inspect:

- `src/AGENTS.md`
- `governance/current/LOOM_CURRENT_WORKSTATE.yml`
- `governance/current/LOOM_EXPERIENCE_ONE_PRODUCT_CONVERGENCE_WORKPLAN_v1.0.md`
- `governance/current/LOOM_EXPERIENCE_ONE_PRODUCT_CONVERGENCE_WORKPLAN_v1.1.md`
- PR #109 contract/body
- PR #110 contract/body

Verify:

1. normal governed development is authorized;
2. G1 is still open/documentary and therefore replacement work remains blocked;
3. G2 authority separation is treated as a standing invariant;
4. E1.1 work remains additive/read-only/non-replacement.

## Current operator-context seam — primary validation target

Inspect:

- `src/loom_campaign_operator_context.py`
- `tests/test_loom_campaign_operator_context.py`
- `engineering/experience_one/spikes/e1_1_campaign_state_location_probe.py`
- `tests/test_e1_1_campaign_state_location_probe.py`
- `engineering/experience_one/spikes/e1_1_operator_location_query.py`
- `engineering/experience_one/E1_1_CAMPAIGN_OPERATOR_CONTEXT_FINDING_v0.1.md`

Independently verify from code that:

- `LOOM_STATE_V1.location_token` is treated as current-location authority;
- `last_flight.route` cannot override current location;
- `epoch_utc` and `kinematic_boundary` are projected from Navigator state rather than inferred by a model;
- wrong/missing required state fails closed;
- the adapter does not mutate its input;
- model calculation/state/canon authority remains ZERO;
- world/canon context is not silently merged into campaign location;
- no duplicate campaign state or execution authority has been introduced.

Cross-check against existing Navigator implementation on the authoritative base/main lineage, especially `src/loom_navigator_core.py`, to ensure the adapter is consuming an established state contract rather than inventing a parallel one.

### Pixel empirical claim to assess

The finding records the following external Pixel evidence:

- active state file: `/storage/emulated/0/Download/LOOM_TEST/LOOM_STATE_V1.json`
- source file SHA-256: `4d89892fa9feed7a8f59e4cb10d4ee27df1b27268bfe2e68c19d70585697e48c`
- `location_token = MARS`
- `epoch_utc = 2027-06-15T08:57:51.391985Z`
- `kinematic_boundary.status = BODY_RENDEZVOUS`
- `ship_identity.ship_name = wayfarer`
- unit tests: 8/8 PASS
- operator query harness: `all_pass: True`

Important: GitHub cannot independently reproduce the user's local Pixel file. Treat these as recorded empirical observations, not repository-internal proof. Validate that the harness and tests are capable of supporting those claims and that the finding does not overclaim beyond the evidence.

## Canon Context / Ceres projection seam

Inspect:

- `src/loom_canon_context_projection.py`
- `src/loom_canon_context_query.py`
- `src/loom_canon_entity_reference.py`
- their tests
- `engineering/experience_one/E1_1_CERES_PROJECTION_FINDING_v0.1.md`
- `engineering/experience_one/E1_1_CERES_PROJECTION_DIAGNOSTIC_FINDING_v0.1.md`

Validate whether the diagnosis `PROJECTION_FAILURE before DATA_FAILURE` is supported, whether provenance is sufficiently field-level, and whether the implementation remains read-only and fails closed instead of inventing lore.

## Mara grounded synthesis seam

Inspect all v0.4-v0.6 synthesis code/tests/findings, especially:

- `engineering/experience_one/spikes/e1_1_mara_grounded_synthesis_v06.py`
- `tests/test_e1_1_mara_epistemic_contract_v06.py`
- `engineering/experience_one/E1_1_MARA_SYNTHESIS_FINDING_v0.2.md`
- `engineering/experience_one/E1_1_MARA_SYNTHESIS_V06_EMPIRICAL_CLOSURE.md`

Validate that:

- model receives typed/deterministic packets rather than direct SQLite;
- evidence paths are deterministically checked;
- target resolution remains deterministic/bounded;
- acceptable epistemic assessment sets were preregistered and are not merely broadened to force green;
- no model calculation/state/canon authority has appeared.

### Known review caveat

The structural v0.6 run was recorded as all four cases PASS. However, the exact v0.6 answer prose was not captured in the chat transcript used to create the closure; the exact v0.5 prose had been manually reviewed and v0.6 changed assessment acceptance rather than evidence/authority structure.

Treat this carefully. If the Git history/finding claims full semantic empirical closure without preserving or independently reviewing the exact v0.6 prose, flag the distinction between:

- **structural/deterministic v0.6 PASS**, and
- **manual semantic review of the exact v0.6 prose**.

Do not silently waive this if the governing finding requires manual prose review.

## Specific hostile checks

Look actively for:

- duplicate state authority;
- model or browser authority creep;
- inference from `last_flight.route` masquerading as current state;
- direct SQLite access by the model;
- hard-coded field coupling that should use shared contracts/accessors;
- mutation hidden in read-only adapters;
- unsupported aliases/fuzzy entity matching;
- provenance that points to broad objects instead of actual fact sources;
- tests that only test the implementation against itself;
- documentation-as-progress;
- fixture evidence presented as live evidence;
- Pixel-only assumptions that silently break Windows or vice versa;
- a generalized Experience Context merger being introduced before the smaller seams are empirically earned;
- any E1.1 replacement of existing user-visible behavior while G1 remains open.

## Expected reviewer output

Return a short independent report with:

1. PR/head SHA actually reviewed;
2. governing-state verdict;
3. operator-context verdict;
4. Canon Context verdict;
5. Mara synthesis verdict;
6. any critical/major/minor findings;
7. whether E1.1 may continue to the next smallest seam;
8. exact conditions/falsifiers for continuation.

Do not merge or mutate production authority as part of validation unless separately authorized.
