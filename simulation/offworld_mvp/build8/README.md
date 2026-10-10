# Build 8: Experiment A, country-capital boundary

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
