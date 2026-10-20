# Vehicle cost curve and investment selection: design only

**NON-CANON / NON-RUNTIME / NOT AUTHORIZATION TO IMPLEMENT.** kT direction: **cost decides, not hard limits; remove governors; money running out is not reality, because there is always something to invest in.** All newly selected numeric values below are **TBD — kT**. No model parameters, calibration constants, vehicle specifications or finance rates are supplied by the assistant. Before any future run: print the complete kT-authored input (including defaults, policy switches, units, curves, bounds and sampling), SHA-256 hash the exact bytes, and include both content/hash in the run identity. Existing historical values are labeled as observed, not new choices.

## 1. Convert existing limits into priced consequences

| Existing restriction | Proposed economic representation | Non-negotiable distinction | kT-authored values |
|---|---|---|---|
| Departure v-infinity <= observed 10 km/s | Required LEO injection delta-v -> propellant/mass ratio -> launch, vehicle and operations cost; quote higher-energy trajectories if physically modeled | A vehicle's *actual* propulsion feasibility cannot be declared away by price | **TBD — kT** vehicle envelope, cost terms |
| Rendezvous arrival v-infinity <= observed 10 km/s | Arrival braking/capture propellant, hardware, risk and duration cost; flyby does not buy capture | Arrival physics, gravity assists and capture method must be explicit, not a silent arrival penalty | **TBD — kT** capture method and pricing |
| Flight 45–1,400 days | Longer flights are candidates with time-dependent mission operations, reliability, capital carrying and opportunity costs | Finite ephemeris coverage and solver validity remain visible **UNKNOWN**, not infeasible | **TBD — kT** search horizon and duration costs |
| Linear speed proxy | Replace with vehicle-based cost where calibrated; preserve old proxy only as an explicit legacy/limiting case | A linear money-per-km/s rate is not a rocket equation | **TBD — kT** transition and calibration |
| Sponsor cash/ceiling/concentration veto | Borrowing, credit pricing, risk-adjusted expected surplus and competing investment return | Insolvency is still an economic consequence; no magical infinite resources | **TBD — kT** financing and investment inputs |

## 2. Vehicle-class authored inputs and physical mapping

Minimum vehicle class must author **exhaust velocity**, **dry-mass fraction** (with denominator clearly defined), **payload mass**, **launch cost per kg**. All **TBD — kT**. Additional necessary choices to price a mission rather than merely compute an idealized mass ratio: LEO parking orbit radius/altitude, Earth gravitational parameter source, injection-stage versus cruise-stage assignment, departure burn efficiency/losses, payload/propellant accounting convention, propellant cost, stage manufacture/refurbishment cost, mission operations cost, arrival capture mechanism and any risk/reliability treatment. Each numeric choice **TBD — kT**; physical constants must have pinned source and version, not invented per run.

For impulsive injection from circular LEO, with Earth parameter `mu_E`, parking radius `r_LEO`, and heliocentric transfer departure hyperbolic excess speed `v_inf,dep`:

`v_circ = sqrt(mu_E/r_LEO)`; `v_peri,hyp = sqrt(v_inf,dep^2 + 2*mu_E/r_LEO)`;

**`Delta_v_LEO = v_peri,hyp - v_circ`** (ideal patched-conic injection; does not include gravity/drag/finite-burn losses).

For ideal rocket propulsion: **`mass_ratio = exp(Delta_v / v_exhaust)`**; propellant `m_prop = m_initial - m_final`, with dry-mass/payload conventions resolved before computing `m_initial`. Cost then follows from authored vehicle production/propellant/launch costs and any staging/reuse rules. If an injection stage cannot supply the required mass ratio under its authored physical configuration, mark **PHYSICALLY_UNSUPPORTED** with reason; do not fabricate a purchasable price. For a rendezvous, compute arrival capture delta-v separately using the chosen destination orbit/capture mechanism and include its mass in the staging calculation. A v-infinity value alone does **not** uniquely determine arrival capture delta-v without destination parameters and maneuver design.

## 3. The observed $72.269449528 million/(km/s) proxy

This is the existing **TEST_ONLY**, uncalibrated proxy from `three_arm_stage1/experiment.json:39-41`, derived as a median of prior Build 7 orbital-recon observations (see PR427 `experiment.json` pricing provenance). The earlier approximation is `price = rate * charged_speed_terms`: departure + arrival for rendezvous, departure only for flyby. It is **not** a validated market price, physical propulsion cost or evidence that an infeasible trajectory can be flown.

Options for **kT to decide**: (a) legacy regression-only limiting mode exactly reproducing the old proxy; (b) an explicitly derived approximation to a calibrated vehicle curve over a **kT-authored** domain; or (c) replacement with the new curve. Do not force the new curve to equal the proxy without evidence. Calibration targets: historical launch services and mass-to-orbit price by vehicle/era; spacecraft dry/payload/propellant masses; mission delta-v and injection performance; mission operations by duration; actual procurement/mission costs with currency year and uncertainty; arrival/capture cases. Separate transfer physics, technological learning, market prices and inflation. Calibration data, time basis, fitting objective, tolerance and validity domain are all **TBD — kT**.

## 4. Flyby versus rendezvous

**Flyby:** charge Earth departure injection, cruise hardware, operations, duration/risk and financed capital. Do **not** charge arrival capture burn. **Rendezvous:** charge the same departure and cruise components **plus** capture/matching velocity at destination, associated propellant/stage/operations and their financed cost. The old regression terms remain departure-only and departure-plus-arrival respectively. Gravity-assist, aerocapture, low-thrust and staging models require explicit selected treatment (**TBD — kT**), not hidden zero-cost assumptions.

## 5. Flights beyond 1,400 days

Do not interpret the old `flight_range_days=[45,1400]` as a physical limit. kT authors the future duration search domain (**TBD — kT**) and the price of time: annual operations, probability of mission loss, delayed scientific/economic benefit, discounting, finance carry, aging and opportunity cost (**all TBD — kT**). Longer flight searches expand the Lambert flight-time grid and ephemeris interval; at fixed departure sampling, approximate candidate-solve work grows with the number of flight-time grid points. Refinement, SPK table extent and memory must be measured later, **not run here**. Distinguish `NO_CANDIDATE_SAMPLED`, `EPHEMERIS_UNAVAILABLE`, `SOLVER_UNSUPPORTED`, `PHYSICALLY_UNSUPPORTED` and `PRICED_BUT_NOT_SELECTED`. No silent fallback from unknown geometry to a priced route.

## 6. Narrow Route 1 seam and regression contract

Only a future opt-in PR427 experiment should replace A1 quote calculation, purchase selection and (if explicitly authorized) financing treatment. **Do not** edit frozen Route 1, loader, manifests, PRs #423–#426, executor identity, A2 rules, evidence provenance, ledger conservation or deterministic replay. Keep existing `ABSTRACT_FALLBACK`, `BLOCK`, `EXTRAPOLATE_PROXY` and original control behavior unchanged when selected. Existing full-clock baseline hash: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.

Future regression specification (**not executed**): pin the exact PR427 source and quote bytes; choose **LEGACY_PROXY_EXACT** with original authored bounds, years, rounding, tie order, quote-status policy, ceilings and financing, and demand byte-identical canonical scientific results and stable hash against the saved baseline for every old case. Compare all receipts, blocked reasons, sponsor balances, stage timing and deterministic identities, excluding explicitly noncanonical timing telemetry. If bitwise identity cannot be achieved, report the first divergent field and do not claim equivalence. New model runs have new identities; equivalence is tested only at the old-model limiting case.

## 7. Financing without a cash wall

`ACTUAL_SPONSOR_CASH` becomes **available liquidity plus priced credit**, not a veto based solely on current cash. An eligible purchase can be financed with a loan **at an authored interest rate (TBD — kT)** and an explicitly recorded repayment obligation. Loan draw posts a cash asset and matching debt liability for the borrower, with a corresponding loan receivable and funding movement for the lender; principal repayment reduces both; interest posts payer expense/recipient income and corresponding transfers. **After every posting**, check balanced debits/credits, cash conservation across transfers, debt/receivable symmetry and no negative or unaccounted creation of money. Avoid pretending an asset transfer is new economic wealth. Loan availability, credit spread, default recovery, collateral and maturity **TBD — kT**; do not silently assume limitless free credit.

`FINANCIER_CONCENTRATION` becomes an authored exposure-sensitive financing price, risk premium, collateral requirement or declining lender willingness, rather than an arbitrary fixed rejection threshold. Genuine inability to obtain credit can still be an outcome, recorded with reasons, but not imposed as a disguised hard cash wall. `FINANCIER_INFORMATION` becomes information uncertainty and priced due diligence; `FINANCIER_RETURN` maps naturally to the opportunity-cost decision below. Whether the current financier policy remains as a legacy regression-only mode is **TBD — kT**.

## 8. Opportunity cost: alternative investments are always available

Purchase only if **risk-adjusted expected net present surplus exceeds the value of the best available alternative use of the same resources**, evaluated over comparable horizons. Candidate inputs: mission cost curve; timing of payments; sponsor-specific benefit if successful; success probability and evidence quality; failure loss/recovery; arrival date and time to benefit; discount rate; debt interest, financing terms and default consequences; alternative investment expected return, risk, liquidity and duration; competing projects and available execution capacity. **Authored by kT:** sponsor valuation/benefit schedule, beliefs or priors, discount/risk preferences, alternative-return process, interest/spreads, failure/recovery assumptions, financing eligibility, allocation horizon and any policy preferences. **Derived, not authored:** trajectory delta-v from qualified geometry, vehicle mass ratio from authored class and sourced constants, computed costs, loan balance and opportunity-cost comparison. Any uncertainty remains visible; it must not become a fabricated deterministic fact.

A positive nominal balance does not imply spend; a zero balance does not imply no project. The alternative investment is the comparator, not an invented bottomless wallet.

## 9. Endogenous pacing without governors

Potential pacing drivers: time-varying orbital opportunities and flight duration; vehicle cost curve and technology; competing investment returns; sponsor expected benefits and beliefs; information gained from A1 and delayed A2; real delivery/production lead times; executor prices and genuine capacity scarcity; loan cost and exposure risk; uncertainty and failure; capital already committed to other projects. None is a newly selected numerical throttle. If every body is bought immediately, inspect those modeled prices, benefits and alternatives **before** inventing an annual purchase cap. If the world genuinely makes every purchase attractive, the model should allow it.

## 10. Open decisions for kT (all TBD)

1. Vehicle classes: exhaust velocity, dry-mass fraction and its denominator, payload, launch cost/kg, parking orbit, stage assignment, propellant and hardware cost, reusable/expended share, burn losses.
2. Capture design: destination parking orbit or matching target, capture method, arrival propellant and operational cost; flyby hardware/operations and risk.
3. Cost curve: whether to retain proxy only for regression or as calibrated limit; calibration dataset, price-year/currency, uncertainty, fit metric, domain and acceptance tolerance.
4. Search: maximum flight duration, sampling/flight-step/refinement choices, ephemeris horizon, compute budget and handling of physically unsupported trajectories.
5. Financing: interest rates, rate term structure, lender and borrower identity, maturity, spreads, collateral, loan supply, credit risk, recovery and default handling; whether concentration becomes premium or actual lender decision.
6. Investment choice: sponsor benefits and timing, mission success priors, discount/risk treatment, opportunity-return benchmark, alternative project set and their financing needs.
7. Institutional realism: executor capacity as priced scarcity versus structural lack of service, A1/A2 review and timing rules, exclusivity and repeat-purchase semantics.
8. Legacy equivalence: exact old policy mode, pinned reference hashes and rounding/tie conventions; approval criteria before changing any runtime behavior.

**Stop condition for this design:** two documents, no implementation and no simulation run. Any new authored value must be provided by kT, printed, hashed and included in the run identity before future use.
