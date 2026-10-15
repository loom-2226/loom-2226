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
