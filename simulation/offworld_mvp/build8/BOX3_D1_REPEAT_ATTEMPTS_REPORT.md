# Build 8 Box 3 D1 — Repeat Attempts (In-Memory, Proposal-First)

**RESEARCH / NON-CANON / OPT-IN / IN-MEMORY ONLY.** Authorised main baseline: `336471f8feb5a2295bba2466a44254828d0509de`. No database, World Authority, hidden-world generator, frozen-path edit, baseline edit, pin edit, placeholder edit, PR D2, or 10,000-seed experiment.

## Predeclared parameters and expected decisions (written before executing D1)

- **One paying sponsor:** `SPN`; **one project:** `P-REGION`; **one synthetic body/region:** `BODY:SYNTHETIC` / `REGION:01`; **one material:** `VOLATILES`.
- **Opening sponsor cash:** 50 MODEL_CURRENCY. **Cost per paid attempt:** 10 MODEL_CURRENCY. Fixed **success value:** 200 MODEL_CURRENCY. **Sponsor minimum expected net hurdle:** 0 MODEL_CURRENCY. Initial belief 0.5, detection 0.8 and false-positive 0.2.
- Fixed run identity `BUILD8_BOX3_D1_REPEAT` / `v1`; fixed observation year **2** for the same-year experiment. Test-only conditional truth is synthetic, held privately by the observer and *never* present in actor snapshots or exported reports.
- **Predeclared expected funding:** At initial p=0.5, expected net 0.5×200−10=90, hence sponsor attempts search #1. After one NEGATIVE, p=0.2, expected net 30, hence sponsor can fund #2. After two NEGATIVE results, p=1/17, expected net 30/17 ≈ 1.764706, hence sponsor can fund #3. After three NEGATIVE results, p=1/65, expected net −90/13 ≈ −6.923077, hence sponsor declines #4, with no payment and no numbered paid attempt. Following NEGATIVE then POSITIVE, p=0.5 and expected net 90; sponsor remains eligible if it chooses to continue.
- If cash runs out, the sponsor is refused for **INSUFFICIENT_CAPITAL** regardless of a positive expected net value. A declined or unfunded proposal is not a paid attempt and consumes no attempt number. No extra retry governor, policy change or automatic forced attempt is introduced.
- **Expected two-attempt fixture cash movement:** sponsor 50 → 30, supplier 0 → 20, **two** distinct EXPLORATION transactions for 10 each, and no double debit on replay. Both attempts use the same year, region and material but different attempt numbers.
- The **exact signal pattern** of each independent keyed draw is not preselected or guaranteed. The fixed synthetic control only determines whether the conditional truth for the test is present or absent. Tests assess actual draw outcomes without retuning a seed or financial value. The 50→20→1/17→1/65 chain and the NEGATIVE→POSITIVE recovery are also verified using separately admitted, authored synthetic signal controls through the existing Bayesian updater; these controls are distinct from the randomly generated two-attempt fixture, not falsely described as its observed outcome.
- A **predeclared, 32-case fixed witness inventory** of independent run identities `BUILD8_BOX3_D1_REPEAT:WITNESS:00` through `:31`, with identical values, costs, region, year and synthetic conditional-**present** control, tests whether any genuinely sampled first-miss / second-positive sequence appears. This is a finite demonstration of possibility, **not** the deferred 10,000-seed frequency experiment. No identities are changed or added after seeing the outcomes; a zero-witness result would be reported as such.

## Design

A Build 8 wrapper holds numbered immutable attempt records: sponsor, project, body, region, material, paid attempt number, paid amount, kernel transaction ID, private observation ID, and original kernel Bayesian belief-update record/event, prior/posterior, observed signal and deterministic draw. The latter is **random measurement noise**, not geological hidden truth.

The trusted, in-memory Build 8 observer invokes the **existing** `kernel.keyed_draw` with exactly:

`OBS | year | sponsor | body:region:material:project:attempt | REGION`

A privately held, synthetic conditional-present bit is consulted only to turn that draw into a POSITIVE/NEGATIVE signal with the declared 0.20 miss and 0.20 false-positive probabilities. The bit is neither attached to kernel state nor returned in reports, actor snapshots or attempt records. A new `BodyRemoteObservation(public=False)` is admitted only to the paying actor, and `update_agent_belief_from_observation` performs the existing 0.8/0.2 Bayesian update. No frozen `observe_region_study` or study-review method is invoked.

A sponsor calls a Build 8 decision method using current admitted belief, authored 200 success value, 10 cost and hurdle 0, then pays by the existing `kernel.transfer` to an Earth-side study supplier with `TxPurpose.EXPLORATION`. This narrow experiment models the **sponsor paying for an observation service**, not a fully qualified Build 7 study activity, exploration WIP or World Authority accounting cycle. The Offworld project remains PROPOSED (waiting), never ABANDONED; no artificial mutation of its lifecycle is performed. Each decision uses existing sponsor funds, no new governor.

Attempt idempotency is local to the Build 8 wrapper: retrying an already-paid attempt number returns its immutable record without another transfer, observation or belief update; proposing a future number out of sequence is rejected. A declined or unaffordable proposal leaves the next paid number available.

A second **nonpaying sponsor actor, without a second project**, exists only to test confidentiality. It has no observation reference; the private read method refuses it, the frozen belief updater rejects it for lack of admission, and its ordinary `build_decision_snapshot` excludes the observation and its signal. This is an **in-memory agent-information boundary**, not an operating-system security sandbox or SQL permission proof.

## Six required evidence items

The parameters above were preserved through execution. Final evidence is documented below, with explicit distinction between randomly drawn signals and authored Bayesian controls.

1. Two separately paid attempts in the same year and two distinct draws: **PASS**.
2. Deterministic replay, full ledger/state fingerprint and in-instance exactly-once debit: **PASS**.
3. Nonpaying sponsor denied observation read, belief update and snapshot signal: **PASS within the in-memory actor boundary**.
4. Exact rational negative chain to 1/65, existing kernel within Decimal precision; positive second observation updates current belief: **PASS**, including independently sampled synthetic-present miss-then-find witnesses.
5. Rational retry under predeclared 200/10/0 values, with below-hurdle and insufficient-capital decline: **PASS**.
6. Legacy identical same-year key repeats the exact same draw, while numbered keys differ: **PASS**.

## CI and limits

Only new Build 8 files. All new tests local-only. Existing Build 8 Fast Tests 10-test selection and workflows untouched. No governed admission receipts, two-paying-sponsor world, DB persistence/reopen, conditional truth export, scientific measurement independence validation, Earth supply reservation, or 10,000-seed statistical claims.

**Do not merge without kT approval. Do not modify the PR after opening without first notifying kT.**

## Executed D1 evidence (local-only; predeclared assumptions above unchanged)

**11/11 new local D1 tests passed** after adapting numerical assertions to the existing kernel's 28-digit decimal precision. This is not a frozen change. Details of previous intermediate failed rounding assertions are not qualification failures of the final tests.

### 1. Two separately paid same-year attempts

The fixed named test identity, one sponsor, one project, same year 2, region and material, produced the following measurements with **synthetic conditional-present**. The random draws are visible nondiagnostic measurement samples, **not source truth**.

| Paid attempt | Year | Key suffix | Draw | Signal | Belief before | Belief after | Kernel expense transfer |
|---|---:|---|---|---|---:|---:|---|
| 1 | 2 | `:P-REGION:1` | 0.4708358879808665974986761626 | POSITIVE | 0.5 | 0.8 | `tx-000001` 10 |
| 2 | 2 | `:P-REGION:2` | 0.07530562752602841514442538751 | NEGATIVE | 0.8 | 0.5 | `tx-000004` 10 |

Two distinct observation IDs, transfer IDs and `ObservationBeliefUpdateRecord`s. Both transfers are `TxPurpose.EXPLORATION`, sponsor `SPN:POOL` -> supplier `SUPPLIER:EARTH`; final balances sponsor 30 and supplier 20. **Same year**, two distinct draw inputs, no frozen observer involved.

### 2. Deterministic replay and idempotency

Two newly instantiated identical runs yielded exactly the same complete evidence reports, draw values, payments, balances, belief updates, snapshot fingerprints, and kernel state fingerprint. Re-invoking `try_attempt(attempt_number=1)` or 2 on a run with both already paid returns the recorded immutable attempt without a third payment/observation/update and leaves the full evidence equal to its pre-replay value.

- Sponsor expense ledger fingerprint: `a1fe7c27c727a8a26ed3f9be165e9805b012277f3983f24c63af1b1daf7c4a09`.
- Synthetic-present kernel state fingerprint: `bb926cb568659fa025b1939aefc6a7cdd07392b2a7cf2a556db9406191da7600`.
- Synthetic-absent kernel state fingerprint: `a0e090d72162c97962d61ce33f19d996f34c46a04c0afad2b9c5c0cb09a9181d`.

This is **in-memory replay**, not reopening a persisted World Authority run.

### 3. Nonpaying sponsor privacy

Actor `OTHER` owns **no second project**. It receives no private observation ID. Build 8 actor-scoped observation read refuses access; the **existing** `update_agent_belief_from_observation` rejects an update because `OTHER` lacks admission; and the normal `build_decision_snapshot` for `OTHER` contains zero private observation references and facts. Its prior stays 0.5 and belief remains absent. Global trusted-kernel storage is still privileged in-process; this is not an SQL or operating-system security qualification.

### 4. Bayesian chain and positive second observation

Separately authored, explicitly admitted synthetic NEGATIVE signal controls (not falsely reported as random draws) were applied through the unchanged Bayesian updater:

`1/2 -> 1/5 -> 1/17 -> 1/65` (50%, 20%, 5.882352941...%, 1.538461538...%). Exact fractions were proved with rational arithmetic, and finite-precision kernel values matched within `1e-26`; the third kernel posterior may differ from the rounded decimal rendering of 1/65 in its final 28th digit.

The fixed **synthetic-absent** test using the *same keyed random draws* produced NEGATIVE on attempt 1 (belief 0.5 -> 0.2) and POSITIVE on attempt 2 (0.2 -> 0.5). This second positive is an admitted **synthetic false positive**, not evidence of a true finding. It proves a later positive updates the current posterior, not the initial prior.

### 5. Rational retry with predeclared values (200, 10, hurdle 0)

At 50% the sponsor's expected net is **90**; it funds attempt 1. In the executed synthetic-absent sequence, after first NEGATIVE the expected net is **30**; it funds attempt 2. A separate three-negative admitted-control path shows expected net of **30/17 ≈ 1.7647** after two negatives (would fund next attempt if the sponsor elects to ask) and **−90/13 ≈ −6.9231** after the third (declines). Decline returns `BELOW_HURDLE` with **no debit and no numbered paid attempt**. A separately declared low-capital fixture (10 opening funds) funds exactly one attempt; the next attempt returns `INSUFFICIENT_CAPITAL` with no debit or consumed attempt number. No forced retry count, new filter or lifecycle abandonment.

### 6. Legacy identical-key negative control

Repeating old exact input `OBS | 2 | SPN | BODY:SYNTHETIC:REGION:01:VOLATILES | REGION` gives identical draw `0.5655606392532198730023484945`. The D1 suffix `:P-REGION:1` / `:P-REGION:2` produces the two distinct draws shown above. Same-year reuse is therefore demonstrated, not merely asserted.

## Regression and delivery

- Final D1 local suite: **11/11 PASS**, including negative control, privacy, accounting, posterior chains, replay/idempotency and fixed-value decisions.
- **Final combined regression: 37/37 PASS** in the clean branch. Breakdown: D1 **11/11** new local-only tests, prior PR C **12/12**, prior PR B **6/6**, and Build 6A temporal multiproject **8/8**. None skipped or failed. The ten-test Build 8 Fast Tests workflow selection itself was not edited; GitHub CI outcome must be checked on the proposed PR head independently.
- No DB, postgres container, World Authority service, future D2 work or 10,000-seed experiment executed.
- The project remains `PROPOSED`, not `ABANDONED`; there are **zero** project study reviews. This design intentionally does not register a governed Build 6B/Build 7 study activity, maturity progression or geological truth.

**Remaining limitation:** the Build 8 wrapper checks privacy against agent admission; arbitrary trusted Python code holding the kernel object can inspect its global observation registry. In-memory actor visibility is proved, not isolation against malicious in-process code. An eventual governed DB path must admit attempt identities, actor-specific snapshots, computed sponsor priorities and transfer/observation receipts before claiming World Authority qualification. Not attempted in D1.

## Additional fixed synthetic-present miss-then-find witnesses

The predeclared 32 named test controls yielded **two** synthetic-present cases with a first negative followed by a second positive (run names ending `:06` and `:22`). Neither identifier was added or chosen after observing results. Both attempted observations were separately paid and used the original detection=0.8/false-positive=0.2 observation model.

| Fixed run suffix | First draw (NEGATIVE) | Second draw (POSITIVE) | Belief sequence |
|---|---|---|---|
| `:06` | 0.1769532091637104567901327135 | 0.8208835507673677771528324143 | 0.5 → 0.2 → 0.5 |
| `:22` | 0.1281405863117383777402893963 | 0.7603349734295594493827148697 | 0.5 → 0.2 → 0.5 |

These two positives are **test-controlled detections of synthetic conditional presence**, as distinct from the false positive in the fixed synthetic-absent fixture. They are not observations of real hidden-world material. The 32-case set was a deterministic witness inventory only, **not** a statistical miss-rate experiment, and supports no frequency calibration claim.
