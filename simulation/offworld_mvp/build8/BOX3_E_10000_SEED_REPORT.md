# Build 8 Box 3 PR E: 10,000-seed repeat-attempt measurement

**PRE-REGISTERED PROPOSAL. The entire section through "Pre-run stopping rule" was authored BEFORE executing the 10,000-seed experiment.** This header and the experiment specifications are frozen for this PR; later measured results are appended separately and do not rewrite this declaration.

**Authority:** `loom-2226/loom-2226` main `bbfc3a4a9e014c0ece2ae1eb7abd18908a2f9399`. **RESEARCH, NON-CANON, IN-MEMORY, NO DATABASE.** No kernel/frozen-path modifications, no D1 edits, no new observer mechanism, no changes to current CI selection, no real geological truth or sealed-world access.

## Predeclared experiment inputs (before first run)

- Sample **N = 10,000** deterministic run identities, exactly `BUILD8_BOX3_E_SEED:00000` through `BUILD8_BOX3_E_SEED:09999` inclusive, consecutive integers with five-digit zero padding. The **same exact seeds** are used for synthetic-present, synthetic-absent and sponsor-rule experiments, and for all replays. No outcome-dependent sampling, replacement or seed tuning.
- **One sponsor `SPN`, one project `P-REGION`, one body `BODY:SYNTHETIC`, one region `REGION:01`, one material `VOLATILES`**, year **2** for all attempted observations. Use the *already-merged D1* `Box3D1` and its `try_attempt` method without editing D1.
- The trusted observer's `synthetic_conditional_present=True/False` input is synthetic test control, **not** an accessible hidden-world value, resource distribution or a property of the actual world. It must not appear in actor snapshots or per-seed exported evidence. Results report the experiment arm's test-control label, not geological truth.
- Under D1's unchanged parameters, sponsor opening cash **50 MODEL_CURRENCY**, cost per paid attempt **10**, success value **200**, hurdle **0**, prior **0.5**, detection **0.80**, false-positive rate **0.20**.
- **Forced observation arms (present and absent): exactly three attempts on every seed.** D1's `try_attempt` is called three times in sequence; given the fixed D1 financial parameters, it is guaranteed able to pay those first three attempts even after all negatives. The test explicitly asserts three returned `PaidAttempt`s per seed; any refusal is a test failure, not skipped sampling. No sponsor-dependent stopping/selection of which observations enter the forced-arm statistics. All three attempts use the genuine D1 attempt-numbered keyed draw, its synthetic signal mapping, and the existing Bayesian update. Each paid sample uses D1's existing kernel transfer. Do not reconstruct or substitute a statistical RNG.
- **Sponsor-rule arm:** call unmodified D1 `try_attempt` on each same-named synthetic-**present** seed until `AttemptDeclined`. Count **decision calls** including the final decline, and number of paid attempts separately. D1 makes the decision from its admitted belief, `p * 200 - 10 >= 0`, and cash. With fixed cash 50, at most five attempts are paid, so the first decline must occur by decision **6**. Predeclared expected stopping distribution: decision **1: 0; 2: 0; 3: 0; 4: about 80**, the three-consecutive-miss seeds; **5: 0; 6: about 9,920** when cash is exhausted. Report decisions 1 through 6, stop reasons, and aggregate actual spending; do not conceal continuations beyond decision 4. Expected spending: **(80 × 3 + 9,920 × 5) × 10 = 498,400 MODEL_CURRENCY**. This is a probabilistic expectation, not a precommitted outcome.
- Replay reruns the exact three arms and fixed seed inventory with no changed inputs. Require identical counts, per-seed streamed SHA-256 fingerprints (draws, signals, paid transfer IDs and amounts, beliefs, terminal reason), and aggregate fingerprint; timing/memory are excluded from the replay fingerprint.

## Predeclared statistical expectations

All distributional expectations below are conditional on **synthetic true presence**, 20% missed detection per attempt and conditional independence of draws. Exactly 10,000 seeds, each offered three draws.

| Mutually exclusive outcome | Probability | Expected seeds |
|---|---:|---:|
| First detection on attempt 1 | 0.8 | **8,000** |
| First detection on attempt 2 | 0.2 × 0.8 = 0.16 | **1,600** |
| First detection on attempt 3 | 0.2² × 0.8 = 0.032 | **320** |
| All three missed | 0.2³ = 0.008 | **80** |

| Cumulative misses | Probability | Expected seeds |
|---|---:|---:|
| Miss on attempt 1 | 0.2 | **2,000** |
| Miss on attempts 1 and 2 | 0.04 | **400** |
| Miss on all three attempts | 0.008 | **80** |

**Synthetic-absent** control: false positives on **attempt 1: 0.2 × 10,000 = 2,000**. Collect all three absent draws but first-attempt false positives are the predeclared comparison.

## Predeclared tolerances and independence tests

- For **each reported count** with expected success probability `p`, use the **inclusive 3-sigma binomial tolerance** `|observed - N*p| <= 3*sqrt(N*p*(1-p))`, with **N=10,000** for fixed-count present/absent tests. Do not change tolerance after seeing the results. Equivalently, expected found-on-1 8,000 ± 120; found-on-2 1,600 ± ~110; found-on-3 320 ± ~53; all-three-missed 80 ± ~27; first miss 2,000 ± 120; first-two misses 400 ± ~59; absent first false positives 2,000 ± 120. Values are judged by the formula, not rounded illustrative intervals.
- Conditional-independence check among synthetic-present draws: `P(miss #2 | miss #1)` and `P(miss #3 | misses #1 and #2)` must each be near **0.20**. The same inclusive 3-sigma **conditional binomial proportion** rule applies: `|observed fraction - 0.2| <= 3*sqrt(0.2*0.8 / observed eligible cohort)`. Never instead compare against 10,000 as the conditional denominator.
- Separately verify `P(miss #2)` and `P(miss #3)` unconditional, also with the same N=10,000 tolerance. Zero-size conditional cohorts would fail the test rather than passing vacuously.
- An acceptable 3-sigma observation is a **reproducibility/consistency check**, not proof of exact mathematical independence. Keyed SHA-based draws are deterministic pseudorandom values, and these checks cannot qualify any real instrument's sensitivity, geological truth or physical stochastic independence.

## Pre-run stopping rule

The preregistered **seed set, sample size, threshold, decision inputs and bounds will not be adjusted** in response to results. If statistical tests fail, record failure and actual counts in the PR; do not resample, rerun with changed parameters, edit D1 or manufacture a pass. Replay uses exactly the same settings. Measured results, elapsed runtimes and process peak RAM will be appended after the first measurement. Existing workflow selection stays untouched.

## Measured results (append only, after the first run)

**Not yet run at proposal registration.**

---

## Measured results: first full 10,000-seed pass and exact replay

The pre-registration above remains unchanged, including its original pre-run status marker. The first measurement was performed from the already-pushed harness commit `e9c2732322abf1b7e1b63ec0d9da96539a6f9a20` after the pre-registered report commit `ad19e5e6259d05620e99599b0126cded508c0e32`. **No seeds, test values, tolerance, code, test controls or implementation were changed between the full measurement and replay.**

**Result: 17/17 quantitative and accounting checks PASS.** These comprise seven expected-count checks for synthetic presence, one false-positive count for synthetic absence, two unconditional attempt miss-rate checks, two conditional independence checks, and five sponsor choice/cash reconciliation checks. All observed count deviations are strictly inside their preregistered **3-standard-deviation tolerance**.

### Synthetic-present: 10,000 independent named run identities, 3 paid D1 observations each

| First detection occurrence | Expected count | Observed count | Deviation (observed minus expected) | 3σ tolerance | Outcome |
|---|---:|---:|---:|---:|---|
| First positive on attempt 1 | 8,000 | **7,944** | −56 | ±120 | PASS |
| First positive on attempt 2 | 1,600 | **1,646** | +46 | ±109.98 | PASS |
| First positive on attempt 3 | 320 | **326** | +6 | ±52.8 | PASS |
| All three missed | 80 | **84** | +4 | ±26.73 | PASS |

Observed first-detection buckets sum to exactly **10,000**. In ordinary terms: 56 fewer seeds were detected immediately than expected, but 46 more were first detected on the second attempt and six more on the third. Only four more seeds than the expected 80 missed all three. Nothing approaches the preregistered three-sigma boundary.

| Cumulative misses | Expected | Observed | Deviation | 3σ tolerance | Outcome |
|---|---:|---:|---:|---:|---|
| First attempt negative | 2,000 | **2,056** | +56 | ±120 | PASS |
| First two attempts negative | 400 | **410** | +10 | ±58.79 | PASS |
| All three attempts negative | 80 | **84** | +4 | ±26.73 | PASS |

Unconditional misses across all 10,000 named seeds were **2,056, 2,022, 2,039** for attempts 1, 2 and 3 respectively. The second and third are only 22 and 39 above the expected 2,000 each, both PASS.

### Conditional independence

For synthetic-present attempts using exactly the same 10,000 names and fixed D1 observation year:

- **P(miss on 2 | miss on 1): 410 / 2,056 = 19.94163424%**, compared with 20% expected. The observed conditional count 410 is 1.2 below the expected 411.2 within ±54.41 at three sigma. PASS.
- **P(miss on 3 | misses on 1 and 2): 84 / 410 = 20.48780488%**, compared with 20% expected. Observed 84 is two above 82 expected within ±24.30. PASS.

These are compatible with independent conditional misses at the test's finite sample size. This does **not** establish mathematical independence of all keyed draws, nor observational instrument calibration.

### Synthetic-absent control

With the **same seed identities and same numbered D1 draws**, the synthetic-absent observation path returned **2,056 false positives on attempt 1**, against **2,000 expected**: 56 above expectation and within the ±120 preregistered three-sigma boundary, PASS. All 10,000 seeds had three paid D1 observations, even if the first one was positive. All three-attempt distributions were collected, but **attempt-1 false positives** were the predeclared absent-case statistical acceptance test.

The equality of 2,056 synthetic-present first misses and 2,056 synthetic-absent first false positives follows directly from the unmodified D1 threshold mapping applied to the **same first draw** in both test-control arms. It is not a separate independent replication sample.

### Sponsor-rule arm: actual unmodified D1 payment and PR C choice

The same **10,000** named seeds were run with the synthetic-present control until D1 itself returned `AttemptDeclined`. No forced sponsor choices. A **decision** is a request to consider the next attempt; the declined request is counted as the final decision but **not** as a payment or numbered attempt.

| Stopped on decision number | Expected | Actual | Paid attempts per seed |
|---|---:|---:|---:|
| 1 | 0 | **0** | 0 |
| 2 | 0 | **0** | 1 |
| 3 | 0 | **0** | 2 |
| 4 | 80 | **84** | 3 |
| 5 | 0 | **0** | 4 |
| 6 | 9,920 | **9,916** | 5 |

**Stop reasons, observed:** 132 `BELOW_HURDLE` and 9,868 `INSUFFICIENT_CAPITAL`. Specifically, **84** declined on decision 4 after three consecutive negatives; another **48** declined below hurdle on decision 6 after five paid attempts; **9,868** hit the zero-cash constraint on decision 6.

**Correction to an over-simple preregistered explanation, without altering it:** the original proposal described decision-six stops as cash-exhaustion stops. That description was too broad. Given five measurements, an uncommon balance of signals can yield a posterior below the 0.05 profitability threshold even when the sponsor is also out of cash. The unchanged D1 `choice()` checks below-hurdle **before** insufficient capital, so it correctly returns `BELOW_HURDLE` in 48 decision-six cases. **The expected stopping decision counts, payment totals, parameters and threshold were not revised.**

- Sponsor paid **49,832** real D1 in-memory transfer events (84×3 + 9,916×5).
- **Total money spent = 498,320 MODEL_CURRENCY**, compared with the predeclared expected **498,400**, a difference of **−80** (a tiny 0.016% below the expected total).
- **Total decision calls = 59,832** including terminal declines. Every seed terminated by decision 6 and conserved sponsor + supplier cash.
- Present forced-arm transactions = **30,000** and absent forced-arm transactions = **30,000**, each costing 10, so each forced arm spent 300,000 synthetic model currency **across independent, separately reset 50-unit seed worlds**. These are **not** a single shared fund or an aggregate world economy.

### Replay, run time, peak memory

Two separate processes ran exactly the same **10,000-seed present + absent + sponsor** experiment. Both returned byte-for-byte equal **measurement JSON objects**, including every count and numerical check and the individual SHA-256 streams based on paid draws, signals, transfer IDs/amounts, belief updates and kernel state fingerprints. Resources are deliberately excluded from the result hash.

| Measure | First full run | Exact replay |
|---|---:|---:|
| Present forced-arm runtime | 6.6700 s | 7.2448 s |
| Absent forced-arm runtime | 6.3849 s | 6.4060 s |
| Sponsor-rule runtime | 8.5717 s | 8.5557 s |
| **Total elapsed** | **21.6269 s** | **22.2069 s** |
| **Peak resident RAM (Linux ru_maxrss)** | **37,360 KiB (~36.48 MiB)** | **37,360 KiB (~36.48 MiB)** |

**Aggregate replay fingerprint, both runs:**
`629476a401c74fc676c6badb82cc01785d85f6bde28cd27aea96d9974c68ea38`

Individual per-arm outcome hashes also match across both runs:
- present: `53708940f000a110e2b032456f52b4d9e3637aa2c5b625013faac39ab8f5c7b3`
- absent: `0cc7bf000f13ca9b3c6406ceaae94a91fd3711431e6ade592d224c157afc2472`
- sponsor: `49d91eac10ef72ca2ab3e15c8de239222563d1bc4361dda7075464b5359cde07`

### Scope and limits

- Uses `Box3D1.try_attempt` with synthetic `True/False` control **only**. Every forced sample received exactly three distinct paid, actor-private D1 observations with actual kernel transfer IDs. There is no new random sampler or observer implementation.
- Conditional rates on one fixed hash-derived key family are consistent with independence at the declared statistical tolerance; they do not prove all inputs statistically independent in general.
- Sampling is synthetic conditional presence/absence, not real planetary geology, hidden-world state, or physical instrument validation. No sealed-world data, database, governed audit admission, World Authority operation or runtime persistence were used.
- Sponsor expenditures are sum-of-independent-scenario totals, not transactions drawn from a shared inter-seed economy.
- Local-only tests and result recording do not alter GitHub CI selection, frozen files, D1 implementation, baselines or pinned dependencies.
- **Proposal-only PR; no merge. Stop for kT review.**
