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
