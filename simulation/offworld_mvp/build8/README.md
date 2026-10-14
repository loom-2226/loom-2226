# Build 8: Experiment A, country-capital boundary

**Experimental, non-canon. Reviewed source hash df9c257. Economic tests need external Earth v4 data. Not a qualification baseline.**

**Current status (2026-10-11):** This directory preserves disposable Build 8 research and simulation experiments, **not** an activated Build 8 economic runtime or authoritative national-capital model. The 80-economy results are authored allocation and mobilization trials, not independent economic choices by 80 country Agents or all named Sponsors. The latest four-USA-Sponsor trial uses real Sponsor and financier policies, frozen financing requests, an authored 0.50-unit fund, and order-independent clearing; its underwriting and manifest are synthetic, TEST_ONLY, and uncalibrated. It does not establish an economic forecast, actual capital markets, or qualification. See [BUILD8_CHECKPOINT.md](BUILD8_CHECKPOINT.md) for the current detailed checkpoint, test results, limits, and session-card hash. Reproducing economic executions requires the separately supplied Earth v4 baseline (`LOOM_EARTH_V4_ROOT`); a clean-clone import check is **not** an economic execution check.

## Current executor-to-deal research (review candidate, 2026-10-11)

**Experimental, non-canon, not a baseline. Economic tests require external Earth v4 data.** The branch `experiment/build8-pi01-executor-quotes` now includes executor quotes, Sponsor development authorization, BUILD→LAND delivery and failure consequences, competing projects with shared executor capacity, actual existing Sponsor/financier policy calls, private-evidence-driven ranking, next-year funding deferral, immediate-funding counterfactuals, failure-payment contracts, and a read-only deal view. The branch name is historical; the scope is much wider than PI-01.

**Trust boundary:** The kernel decisions, transfers, conservation checks, deterministic replay and stage outcomes execute. Executor prices, project budgets, capacity, motives, synthetic lunar evidence and fund size are authored. The physical handoffs are tokens; the financier is test-only; the two-slot trial measures a one-year *schedule* loss, not lost monetary returns. The deal view reconstructs access from a separate evidence fixture, not event-time provenance in a single world. See the capability-by-capability real/authored/stand-in table in [BUILD8_CHECKPOINT.md](BUILD8_CHECKPOINT.md#executor-to-deal-research-line-2026-10-11-branch-review-candidate). No promotion to canon, qualification or runtime.

**Run:** `PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:. python3 -m unittest discover -s simulation/offworld_mvp/build8 -t . -p 'test_*.py' -q`, with Earth v4 configured through `LOOM_EARTH_V4_ROOT`. A fresh clone without those external inputs cannot reproduce economic tests.

**Job 2 follow-up:** The screened economic trial now generates synthetic evidence in its own kernel and records observation/publication/disclosed-posterior and deal-party term receipts as events occur. `deal_record.py` reads these receipts; it no longer reconstructs a second fixture. Earlier historical notes about the separated evidence fixture remain applicable to the older experiments, not this screened trial. See the checkpoint for scope and limitations.

**Reading guide:** The numbered increments below are historical experiment notes retained for provenance. Their original "Next" statements and "no financing decisions" statements describe the state **at that increment**, not the current branch. Do not use them as current authority or instructions to expand the model.

## Historical experiment log (superseded status statements)

Status: initial implementation, not an activated runtime campaign or qualification.

The first increment exposes read-only 2026–2035 investment capacities for 80 Earth economies from the promoted Earth v4 local baseline. It does **not** mint capital, change Build 7, create government Agents, introduce strategic pressure, or make financing decisions.

`country_capital_input.load_investment_capacity(baseline_root)` returns country/year investment capacity and SHA-256 provenance. It reads `qualified_inputs/countries_2026_2031.ndjson` for 2026–2031 and `stage_2031_2060/countries_2031_2060.ndjson` for 2032–2035. The two inputs both contain 2031; the qualified-input series wins that boundary rather than silently mixing series. The result is a **capacity input**, not an account balance.

Next: run a reproducible Build 7 control with the available World Authority services, then wire these inputs to country-capital state without changing mobilization semantics. No Sponsor or FIN changes are authorized by this increment.

## Second increment: non-mutating preview

`capital_preview.preview_country_capital(root, commercial_opportunity)` applies **the existing Build 7 `derive_mobilization` function** independently to all 800 country-years. `commercial_opportunity=False` and the unchanged zero-pressure scenario yield zero; `True` exposes potential mobilization under the authored ceiling. This is counterfactual capacity, not a spendable balance, executed transfer, or claim of 80-country runtime coupling.

**Observed blocker to actual runtime coupling:** Build 7's `mobilize_country_capital` requires a matching country-specific Earth assertion and an `EARTH:<country>` source account; its generated campaign currently constructs these only for USA. Simply iterating 80 countries would violate the existing contract. The next implementation should supply admitted country assertions and matching accounts in a Build 8-specific conductor, without relaxing the invariant or altering Build 7.

The full disposable database-backed control could not yet be rerun: the default PostgreSQL service definitions are absent in the current shell, and the integrated health harness requires separately provisioned database credentials. Focused unit regressions are not a replacement for that run.

## Third increment: isolated two-country kernel transaction trial

`two_country_trial.run_two_country_trial(root)` constructs a disposable **in-memory** Build 7 kernel, replaces only the trial's 2026 USA investment assertion with Earth v4, adds an Australia investment assertion, creates matching Earth boundary and country financing accounts, and calls the existing `mobilize_country_capital` transition. No database or persisted campaign is changed. The inherited Build 7 manifest is altered for this isolated experiment; this is **not** an approved Build 8 genesis manifest or qualification. Country assertions refer to the Earth v4 files by SHA-256 and carry an explicit trial authorization reference.

Observed in 2026 with a visible opportunity and zero strategic pressure: USA `4.958025335469291`, AUS `0.412288545182134` MODEL_CURRENCY. Both transfers are country-scoped and reconcile in the trial's ledger. The boundary source balances are negative, representing the external inflow, not national debt. No project commitments or Sponsor financing are executed. The next step is a proper Build 8 genesis/admission path, followed by all 80 countries, rather than mutating a Build 7 manifest in a production campaign.

## Fifth increment: ten-year regression and persistent-genesis seam

`test_ten_year_trial.py` now covers all 800 country-year transitions in one in-memory kernel, and the negative control with no commercial opportunity and zero strategic pressure. The full focused suite executed 20 tests (19 passed, 1 skipped).

**Exact persistence blocker:** Build 7 `generated_campaign._build_kernel` constructs and hashes its opening `BoundaryManifest` before `start_world_run` calls `_attach_persistence`. It authors USA-only `EARTH_REFERENCE` contracts, country assertions, opening accounts and opening bindings. The Build 8 trial mutates `boundary_manifest.assertions` and adds accounts *after* this hash was computed. Those mutations must not be persisted under the Build 7 opening identity. A legitimate Build 8 genesis must author the 80-country assertion set, source hashes, country accounts and opening bindings **before** computing the opening manifest hash and run identity. Build 7's executable must remain unchanged. The Earth v4 files are currently local inputs, not checked-in immutable campaign input artifacts.

Do not patch the kernel's assertion/account checks or persist the trial as if it were qualified. The next smallest executable step is a Build 8-specific opening path, then a fresh isolated World Authority run and replay using it. The existing `integrated_health.py` illustrates disposable PostgreSQL setup but requires a configured PostgreSQL 18 admin credential; it has not been rerun for this Build 8 change.

## Sixth increment: first persisted non-USA mobilization

In the isolated PostgreSQL service `/tmp/loom_b7_health_isolated.pg_service.conf`, a real generated 90-body Build 7 world was used as the physical seed for a **distinct** Build 8 run identity. Build 8 pre-epoch opening passed `validate_opening`; its 2026 Earth-reference epoch persisted and replayed. A 2026 Australia `mobilize_country_capital` transition persisted as `ACTION:2:mobilize_country_capital` with `COMMITTED` then `ALREADY_MATCHED` on reconstruction, balance `0.412288545182134` model-currency units. No sponsor or financing decision was involved.

`persistent_trial.run_persistent_trial(root,control_run_id,countries=('AUS',))` reproduces the experiment when an isolated World Authority service and pinned Earth v4 input files are available. It does not create the database or generate a new world.

The experiment exposed that country-specific `SYSTEM_TRANSITION` use contracts must be admitted, and future-year `SCENARIO` assertions cannot be included with later `available_from` times at the 2026 opening. Build 8 now includes 79 non-USA 2026 scenario assertions for mobilization; 800 country-year REAL investment assertions remain in the opening. **Future-year scenario admission is deferred.** USA's existing Build 7 scenario investment remains unchanged and must be reconciled with v4 inputs before claiming all-country year-by-year production equivalence. This is an isolated persisted experiment, not a qualified Build 8 release.

## Seventh increment: persisted 80-country 2026 trial

Executed against the isolated World Authority PostgreSQL runtime using the pinned generated 90-body world and promoted Earth v4 data. The first complete 2026 pass committed 75 new country-capital epochs and replay-matched 5 already committed epochs. A reconstructed second pass replay-matched **all 80 epochs** with zero new commits. Both produced the exact aggregate **25.10396510558080532339 MODEL_CURRENCY**. The source sequence for the existing run was `AUS, USA, CAN, GBR, JPN`, followed by all remaining country codes in sorted order. World Authority requires stable epoch ordering; attempting to replay the same run with all codes sorted immediately failed `INCOMPLETE_SQL_ROW:wa_run.artifact`. Do not bypass this integrity failure or treat arbitrary reorderings as equivalent. This is an isolated, persistent, one-year experiment; it does not establish 2027–2035 temporal admission, sponsor spending, or a qualified release.

## Eighth increment: finite prospecting capital changes decisions

`finite_capital_trial.py` exercises **two competing prospecting project proposals by the existing SPN Agent** in one disposable Build 8 kernel, using the actual Build 7 sponsor policy and prospecting creation/commitment/disbursement methods. With 2026 USA mobilization of `4.958025335469291` model-currency units and two sequential requests of `3` units each, the first decision is `INITIATE_PROJECT` and spends `3`; the second decision is `WAIT` with `1.958025335469291` remaining. The ledger and capital coupling reconcile, and the result reproduces deterministically. This is **not two independent Sponsors** and is **not yet a persisted prospecting-project trial**. No new financing system, government Agents, or strategic pressure was added.

## Generic dated transport-to-money, treasury-corrected TEST_ONLY trial (PR #410)

See [GENERIC_DATED_TRANSPORT_MONEY.md](GENERIC_DATED_TRANSPORT_MONEY.md).
Two authored rows share generic Earth→Ceres / Earth→Mars freight economics.
The selected Ceres 2.660653 MODEL_CURRENCY quote is appropriated from
`treasury:IND` through frozen-ledger `PUBLIC_SUBSIDY` and paid to an
Earth-side shipper at departure, not prefilled into a seed account.
The treasury starts at zero and receives separate, explicitly TEST_ONLY
annual country mobilisation transfers bounded by unallocated Earth
mobilisation; these are **not** future Ceres export receipts and do not
affect legacy Earth/Offworld capital pins. The Mars treasury and an
additional empty-Ceres-treasury case block, with no shipment or benefit.
The revised opt-in scenario fingerprint is
`46e390772ed0ef4cca3d07e79e39a4dfa1a26db5c774162a77dff7887b0b0563`.
The completed scenario JSON and geometry cache remain outside Git.

## Earth-side freight spending line (Build 8 PR 3, read-only projection)

The opt-in dated transport-to-money consumer can now return its **unchanged
canonical result** together with an enriched annual gauge using
`settle_money_chain(row, ready, quote, report_freight_gauge=True)`.
The extra visible annual line is
`earth_side_transport_spending_for_offworld_projects`. Without the
report flag, the existing result structure, bytes, and fingerprints
remain exactly as before. With the flag, the first returned result is
still byte-identical; only the separately returned display rows gain
this line. This avoids moving any pinned state identity.

**Definition:** sum the amount of each actual `TRANSPORT_PAYMENT` ledger
transaction once in its payment year when its source and destination
accounts are on Earth **and** its parent IDs explicitly identify an
existing Offworld project/transport order. Do not count the earlier
treasury appropriation, a quote, a cargo movement, an unlinked payment,
or a payment involving an Offworld endpoint. Zero years are explicitly
`"0"`, never absent/null. This does not change the source, vehicle,
pricing, wait, departure, payment, or delivery rules.

| Year | Ceres Earth-side freight | Ceres Offworld draw | Ceres new draw | Ceres recycled |
|---|---:|---:|---:|---:|
| 2038 | 0 | 0.080 | 0.080 | 0 |
| 2039 | **2.660653** | **0** | **0** | **0** |
| 2040 | 0 | 0 | 0 | 0 |

Ceres's unique 2039 actual `TRANSPORT_PAYMENT` from Earth sponsor
budget to Earth shipper is linked to the Offworld seed-factory order,
and counts **exactly once**. The treasury-to-budget `PUBLIC_SUBSIDY`
does not count a second time. Its funded source is India's treasury
`treasury:IND`. The illustrative Mars row, the Ceres empty-treasury
negative control, and no-departure cases show **zero**.

The existing identity remains unchanged in every annual row:
`new_capital_draw + recycled_returned_cash_spent = offworld_draw`.
The 2039 freight payment is an Earth-to-Earth supplier transfer, not
an Earth-to-Offworld capital transfer. The transport line sits alongside,
not inside, that identity.

**Before/after byte audit, 201 annual rows per project:** full canonical
Ceres result SHA-256 remains
`8c7006395bb840bc66a6b40c69e0e604fd1183205d4e372720c22983f5d5fb01`;
Mars remains
`bdee7b0bff0d2f965c28b123f549f1a2f8774e261fae666063bd05db109fb625`.
The complete opt-in scenario fingerprint remains
`46e390772ed0ef4cca3d07e79e39a4dfa1a26db5c774162a77dff7887b0b0563`.
Deleting the *one* new field from the display projection reproduces
all 201 pre-change annual rows exactly. No pinned figure requires
modification. Before/after JSON snapshots and derived gauge rows are
stored under `/tmp/build8-pr3-*` outside Git.
