# Build 8 Box 3 PR F: Stop After Find

**PROPOSAL / PREREGISTRATION. All text through "Pre-run stopping rule" precedes any 10,000-seed PR F execution. Append measurements below without altering this prefix.**

**Baseline:** `6a6cb33983426169976e79a4ea2d7291b714a35a` (live GitHub main confirmed).
**Class:** `class:engineering`; **RESEARCH / NON-CANON / OPT-IN / IN-MEMORY / SYNTHETIC-ONLY**.
**No** D1, PR C, PR E, kernel, frozen Build 5/6/7/phase3b, CI selection, database, persisted scenario or actual hidden world values may change.

## 1. Existing rule and narrow PR F rule

Merged D1 repeats searches while `belief * 200 - 10 >= hurdle` and has search cash. This treats another study as a project in its own right, not as an input into a *development funding* decision. PR E observed 9,916 / 10,000 present seeds spend all 50 across five searches.

PR F: compute one-step **gross expected value of sample information** (EVSI) for the sponsor's *development* authorize/decline decision; search if `EVSI >= search_cost` (exact tie allowed) **and** uncommitted sponsor cash can fund the observation. Otherwise stop and hand off to PR C's `p * success_value - development_cost >= hurdle` economic funding decision. D1 remains the unchanged observation/payment service, and its existing internal veto, if any, must be reported rather than bypassed.

For current belief `p`, sensor likelihoods detection `d=0.8`, false positive `f=0.2`, development cost `Cd=60`, search cost `Cs=10`, sponsor hurdle `H=0`, effective success value `V`:

```text
V = money_value + motive_value + country_pressure_value
U(p) = max(0, p*V - Cd - H)
q(positive|p) = p*d + (1-p)*f
p_plus = p*d/q; p_minus = p*(1-d)/(1-q)
EVSI = q*U(p_plus) + (1-q)*U(p_minus) - U(p)
search iff EVSI >= Cs and sponsor_available_cash >= Cs
```

Each input is authored and visible; no inferred behavioral weights, hidden scores or newly fitted country-pressure generator. Financing assumption: **a capital source could become available later for development**. Thus development economic worth is evaluated independently of immediate development affordability. If `would_fund` but cash < 60, the result MUST read `WOULD_FUND_DEFERRED_FOR_CAPITAL`; no development authorization or imaginary payment. Sunk observation costs are real existing in-memory D1 `EXPLORATION` ledger transfers.

**Important:** D1's private trusted synthetic presence/absence switch only determines how sensor draws become noisy signals; it may not enter the decision rule, sponsor snapshot, exported per-seed data, or PR C decision.

## 2. Three authored sponsor profiles, zero defaults

| name | prior | money | motive | pressure | hurdle | effective success value | funding threshold |
|---|---:|---:|---:|---:|---:|---:|---:|
| neutral | 0.50 | 200 | 0 | 0 | 0 | 200 | .30 |
| motive | 0.50 | 200 | 100 | 0 | 0 | 300 | .20 |
| pressured | 0.10 | 200 | 0 | 300 | 0 | 500 | .12 |

All cost 10/search, cost 60/development, available opening search cash 50 and d/f = .8/.2. The three value contributions, prior, hurdle, search/development costs and likelihoods must appear **as individual fields in every reported sponsor profile/row**. No origin model for motive or national pressure in this experiment.

One-step hand examples:
- neutral prior .5: gross EVSI 10 = price 10, search by tie; positive -> p=.8, EVSI 0, stop / would fund but cash 40 < 60. Negative -> p=.2, EVSI 12.8, search again; two negatives -> p=1/17, EVSI 0 stop.
- neutral miss/positive -> p=.5, search continues; do not confuse a positive observation with irreversible success.
- motive prior .5 / V300: p_minus=.2 meets funding threshold, so EVSI 0; **zero searches**, would fund at p=.5; no cost, cash50, development deferred for 10 shortfall.
- pressured prior .1 / V500: p_plus=4/13=.307692, p_minus=1/37=.027027, positive probability .26. Expected information benefit 24.4 > 10, so search once. The successor beliefs yield EVSI below 10; after + development is desirable, after - it is not. Cash40 after one search.

## 3. Preregistered sample inventory, outcomes and tolerances

Exact names `BUILD8_BOX3_E_SEED:00000` through `BUILD8_BOX3_E_SEED:09999` inclusive. Same 10,000 IDs in all six arms, year 2, same D1 attempt-numbered keyed draw and 0.8/0.2 signal likelihood. No post-outcome reseeding, refusal removal or survivor resampling.

All rows below are **expectations, not results**.

| Profile / synthetic presence | stops0 | stops1 | stops2 | stops3 | stops4 | stops5 | spent MODEL_CURRENCY | would fund at stop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| neutral / present | 0 | 8000 | 400 | 1280 | 64 | 256 | 141760 | 9484.8 |
| neutral / absent | 0 | 2000 | 6400 | 320 | 1024 | 256 | 211360 | 2371.2 |
| motive / present | 10000 | 0 | 0 | 0 | 0 | 0 | 0 | 10000 |
| motive / absent | 10000 | 0 | 0 | 0 | 0 | 0 | 0 | 10000 |
| pressured / present | 0 | 10000 | 0 | 0 | 0 | 0 | 100000 | 8000 |
| pressured / absent | 0 | 10000 | 0 | 0 | 0 | 0 | 100000 | 2000 |

Absent-case `would fund` is an erroneous development recommendation **given synthetic conditional absence**, not an actual funded project. With motive profile, zero observations means zero **observed false-positive signals**, but 10,000 absence-conditional would-fund errors. Neutral absent 2371.2 and pressured absent 2000 are expected signal-induced false-positive funding recommendations (conditional synthetic absence). Report both categories separately. The **observational money sunk on absent regions** is all absent-arm search expenditure above; no world-development expense is issued.

Neutral predictive stop path probabilities for present: `[0,.8,.04,.128,.0064,.0256]`, for absent `[0,.2,.64,.032,.1024,.0256]` for stops0..5. Conditional on present, D1 positive=.8; conditional on absent, positive=.2. Neutral `would fund` probability on present = `.8 + .128 + .0256*.8 = .94848`; on absent = `.2 + .032 + .0256*.2 = .23712`. Motive would-fund probability=1; pressured would-fund probabilities=.8 present/.2 absent.

**Frozen 3-sigma tolerance:** for each expected count probability `p`, require inclusive `abs(actual-10000*p) <= 3*sqrt(10000*p*(1-p))`. This also applies to `would_fund` and absent error counts, which can have fractional expectations. Deterministic `p=0` or `p=1` outcomes require exact equality.

For aggregate search spending, multiply 10 by the number of searches for each seed. Let `k` be paid-search count with the above declared per-seed stopping probabilities, and require inclusive `abs(actual_spend - 100000*E[k]) <= 30*sqrt(10000*(E[k^2]-E[k]^2))`. For deterministic stop counts the tolerance is zero. In all arms require observed stop counts sum to 10000, actual spend = sum(paid searches)*10, cash conservation per D1 scenario, no negative funds and zero development transfers.

**Replay requirement:** rerun same six arms from new in-memory instances, require identical full counted summary, per-arm SHA-256 streams from admitted signals, posterior, D1 transactions and stop reason, and aggregate fingerprint; do not include wall time or resident RAM in result fingerprints. Report both runs' elapsed seconds and peak resident memory.

**Disallowed shortcuts:** No fixed attempt cap as an economic stopping policy; naturally finite search payment budget (50) is already visible. The harness may explicitly bound a control loop at the existing maximum funded steps (six decision calls) for nontermination detection, but it must not introduce an extra policy cutoff. An unfundable or refused attempt must not be counted as paid. New tests local-only, CI fast-ten unchanged. No new mechanism replacing D1 draws or Bayes.

## 4. Design-only country pressure question (no data coupling in PR F)

Country pressures should *eventually* come from admitted, explicitly dated country-specific strategic goals or mission mandates, with a sponsor/country attribution and a documented estimate of incremental value of success. The existing Build 8 `country_capital_input.py` reads **80-economy Earth-v4 annual modeled investment capacity**, and `all_sponsors_country_trial.py` contains an **authored** twenty-sponsor roster, home-country mapping and `PREFERENCES` used for optional capital allocation. Neither is a measured or admitted strategic pressure value. No vetted country-pressure series or pressure-to-money valuation was identified in those paths. **CIVSTATE is legacy, not a target**, and cannot be silently repurposed as national-pressure truth.

Should pressure add to `V` or lower `H`? In this one-project binary choice, a fixed pressure bonus can be represented as higher conditional success value only if pressure benefits **depend on success**. A lower hurdle is the more honest parameter when pressure expresses an independently mandated willingness to accept a lower financial return, since it changes authorization even if success is unlikely. They are **not interchangeable across all beliefs** (`p*(V+P)-Cd >= H` versus `p*V-Cd >= H-P`). PR F intentionally makes pressure a visible sponsor-assigned value component because kT specified additive `V`; no inferred conversion or runtime claim.

## 5. Intended tests and boundaries

Local tests for all profiles' hand values, zero/miss/find branches, tie handling, financing deferral/no imaginary transfer, differences in priors and motives, full source-visible field rendering, private D1 observation boundary, exactly one exploration transfer per paid attempt, absence-conditional errors, replay, and fixed 3-sigma statistical comparisons. No new tests in CI selection.

## Pre-run stopping rule

**No 10,000-seed PR F run has occurred when this preregistration is authored.** Once merged-main pinned proposal is opened, add new Build 8-only harness and local tests in a second commit, run the preregistered sample unchanged, and append observed report results in a third commit. If anything fails, report failure rather than adjust seeds or parameters. No merge without kT approval.

---

## Measured results: 10,000-seed PR F run and exact replay (APPENDED AFTER PRE-REGISTRATION)

Pre-registered report preserved **byte for byte** through the pre-run stopping rule.
First PR F commit: `596a7bf`. Runner and nine local tests committed
separately before the full runs: `2d57269`. The prescribed PR E 10,000 seed
identities and all six arm inputs were used unchanged. **57/57 checks PASS.**

### Observed stopping distributions vs the frozen expectations

| Sponsor / arm | Prior | Money | Motive | Country pressure | Effective V | Hurdle | Stops 0 / 1 / 2 / 3 / 4 / 5: expected | Stops: actual |
|---|---:|---:|---:|---:|---:|---:|---|---|
| neutral / present | 0.5 | 200 | 0 | 0 | 200 | 0 | 0 / 8000 / 400 / 1280 / 64 / 256 | 0 / 7944 / 410 / 1280 / 66 / 300 |
| neutral / absent | 0.5 | 200 | 0 | 0 | 200 | 0 | 0 / 2000 / 6400 / 320 / 1024 / 256 | 0 / 2056 / 6332 / 334 / 994 / 284 |
| motive / present | 0.5 | 200 | 100 | 0 | 300 | 0 | 10000 / 0 / 0 / 0 / 0 / 0 | 10000 / 0 / 0 / 0 / 0 / 0 |
| motive / absent | 0.5 | 200 | 100 | 0 | 300 | 0 | 10000 / 0 / 0 / 0 / 0 / 0 | 10000 / 0 / 0 / 0 / 0 / 0 |
| pressured / present | 0.1 | 200 | 0 | 300 | 500 | 0 | 0 / 10000 / 0 / 0 / 0 / 0 | 0 / 10000 / 0 / 0 / 0 / 0 |
| pressured / absent | 0.1 | 200 | 0 | 300 | 500 | 0 | 0 / 10000 / 0 / 0 / 0 / 0 | 0 / 10000 / 0 / 0 / 0 / 0 |

### Spending, synthetic-absence errors and financing handoff

| Sponsor / arm | Prior | Money | Motive | Country pressure | Effective V | Hurdle | Search spending expected / actual | Would fund expected / actual | Search cash-limited stops |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| neutral / present | 0.5 | 200 | 0 | 0 | 200 | 0 | 141,760 / 143,680 | 9,484.8 / 9,466 | 58 |
| neutral / absent | 0.5 | 200 | 0 | 0 | 200 | 0 | 211,360 / 211,180 | 2,371.2 / 2,450 | 224 |
| motive / present | 0.5 | 200 | 100 | 0 | 300 | 0 | 0 / 0 | 10,000.0 / 10,000 | 0 |
| motive / absent | 0.5 | 200 | 100 | 0 | 300 | 0 | 0 / 0 | 10,000.0 / 10,000 | 0 |
| pressured / present | 0.1 | 200 | 0 | 300 | 500 | 0 | 100,000 / 100,000 | 8,000.0 / 7,944 | 0 |
| pressured / absent | 0.1 | 200 | 0 | 300 | 500 | 0 | 100,000 / 100,000 | 2,000.0 / 2,056 | 0 |

**All** decisions judged worth funding remain **WOULD_FUND_DEFERRED_FOR_CAPITAL**:
the original sponsor has at most 50 cash and development costs 60.
Development payments = **0** and the in-memory project remains PROPOSED.
Every paid search is the existing D1 10-unit EXPLORATION transfer to the Earth-side supplier.

Absent synthetic truth is a **test fixture only**, never an admitted or exported world
claim. In those absent arms, every search expenditure is money sunk investigating
an absent region; these expenses are not evidence of real-world financial loss:

| Sponsor | Expected absent-region money sunk | Actual absent-region money sunk |
|---|---:|---:|
| neutral | 211,360 | 211,180 |
| motive | 0 | 0 |
| pressured | 100,000 | 100,000 |

| Sponsor | Expected absent-case would-fund errors | Actual errors | False-positive observed signals | Observation-free recommendations |
|---|---:|---:|---:|---|
| neutral | 2,371.2 | 2,450 | 4,346 | none; at least one positive signal for every would-fund case |
| motive | 10,000.0 | 10,000 | 0 | all 10,000 would-fund decisions use prior only |
| pressured | 2,000.0 | 2,056 | 2,056 | none; at least one positive signal for every would-fund case |

**Interpretation:** the motive-driven sponsor did not observe anything. Its
10,000 erroneous absent-case funding recommendations are **not instrument
false positives**. Neutral and pressured sponsors' absent-case would-fund
decisions are erroneous signal-driven development recommendations; however,
no development cost was paid, and all remain deferred for capital.

### First fixed seed demonstrates different beliefs and money

For the identical named seed `BUILD8_BOX3_E_SEED:00000` (not selected
after scanning for an interesting witness), sponsor profiles apply their
own priors to the **same potential D1 keyed observation stream**, but only
receive signals they actually pay for. Zero-search sponsor is not given
a free sensor outcome. These are illustrations, not the acceptance statistic:

| Synthetic arm / profile | Prior | Money | Motive | Pressure | Effective V | Hurdle | Actually bought signals | Posterior on stop | Searches | Worth developing? | Available cash |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|
| present / neutral | 0.5 | 200 | 0 | 0 | 200 | 0 | POSITIVE | 0.8 | 1 | YES; defer for capital | 40 |
| present / motive | 0.5 | 200 | 100 | 0 | 300 | 0 | (none) | 0.5 | 0 | YES; defer for capital | 50 |
| present / pressured | 0.1 | 200 | 0 | 300 | 500 | 0 | POSITIVE | 0.3076923076923076923076923077 | 1 | YES; defer for capital | 40 |
| absent / neutral | 0.5 | 200 | 0 | 0 | 200 | 0 | NEGATIVE, NEGATIVE | 0.05882352941176470588235294118 | 2 | NO; below hurdle | 30 |
| absent / motive | 0.5 | 200 | 100 | 0 | 300 | 0 | (none) | 0.5 | 0 | YES; defer for capital | 50 |
| absent / pressured | 0.1 | 200 | 0 | 300 | 500 | 0 | NEGATIVE | 0.02702702702702702702702702703 | 1 | NO; below hurdle | 40 |

### Deviations and registered three-sigma tolerances

Counts and money are computed from the **preregistered** binomial and
per-seed variance equations, not fitted after observation. All 57
registered checks (36 stopping buckets, 6 would-fund, 6 spending,
6 cash/handoff, and 3 absent-only checks) passed.

| Arm | Outcome | Expected | Actual | Difference | Predeclared 3-sigma bound | PASS |
|---|---|---:|---:|---:|---:|---|
| neutral_present | Funding-worthy | 9,484.80 | 9,466 | -18.80 | ±66.32 | PASS |
| neutral_present | Search spending | 141,760.00 | 143,680 | +1,920.00 | ±2,757.41 | PASS |
| neutral_absent | Funding-worthy | 2,371.20 | 2,450 | +78.80 | ±127.59 | PASS |
| neutral_absent | Search spending | 211,360.00 | 211,180 | -180.00 | ±2,780.62 | PASS |
| motive_present | Funding-worthy | 10,000.00 | 10,000 | +0.00 | ±0.00 | PASS |
| motive_present | Search spending | 0.00 | 0 | +0.00 | ±0.00 | PASS |
| motive_absent | Funding-worthy | 10,000.00 | 10,000 | +0.00 | ±0.00 | PASS |
| motive_absent | Search spending | 0.00 | 0 | +0.00 | ±0.00 | PASS |
| pressured_present | Funding-worthy | 8,000.00 | 7,944 | -56.00 | ±120.00 | PASS |
| pressured_present | Search spending | 100,000.00 | 100,000 | +0.00 | ±0.00 | PASS |
| pressured_absent | Funding-worthy | 2,000.00 | 2,056 | +56.00 | ±120.00 | PASS |
| pressured_absent | Search spending | 100,000.00 | 100,000 | +0.00 | ±0.00 | PASS |

### Replay, elapsed time and memory

- First pass: **29.2101 s**, peak resident memory **37,992 KiB**.
- Exact replay: **29.1685 s**, peak resident memory **37,992 KiB**.
- Both full measurement JSON objects are exactly equal (timing/RSS excluded).
- Per-arm D1 signal, paid transfer, belief, profile and decision fingerprints match exactly.
- Aggregate SHA-256 on BOTH runs: `b1184990ce28fd2cc1c9d76ed1d419917e93e33cf236a074d3ad2cfcc04a84ce`.
- Local-only F + E + D1 + PR C regression: **38/38 PASS**.

### Scope limitations and conclusions

- The tests evaluate **conditional synthetic presence and absence**, not geology.
- Same seed names use the same keyed observation inputs, but all case counts
  share a deterministic keyed family and do not prove physical independence.
- No real sealed WORLD, no database, no persistence and no new actor evidence
  admission mechanism. Only new Build 8 experiment files changed.
- Sponsor motives and pressure are visible authored inputs; no causal
  explanation, currency calibration or inferred weighting is claimed.
- The handoff uses **PR C's expected-net/hurdle economic rule** with D1
  sponsor cash. It is **not** a call to PR C's separate two-project policy
  fixture, nor a completed development activity. Every would-fund case is
  explicitly deferred when development is unaffordable.
- D1's internal repeat-search feasibility check remains in place and was
  not changed. All six approved profiles were compatible with it;
  unrelated arbitrary profiles are NOT claimed to be proven compatible.
- The low-prior pressured sponsor stops after a single paid observation;
  the high-motive sponsor knowingly stops without observing. This is
  economically coherent for their **authored** values but does not imply
  success is physically likely.
- No fixed economic attempt governor added. Five paid searches is an
  existing cash-budget consequence, not a newly imposed cap.
- Local tests are not included in CI fast-ten. No CI selection, frozen
  paths, D1, PR C, PR E, models, or baselines were changed.

**Draft proposal only. No merge. Stop for kT review.**

