# Build 8: Experiment A, country-capital boundary

Status: initial implementation, not an activated runtime campaign or qualification.

The first increment exposes read-only 2026–2035 investment capacities for 80 Earth economies from the promoted Earth v4 local baseline. It does **not** mint capital, change Build 7, create government Agents, introduce strategic pressure, or make financing decisions.

`country_capital_input.load_investment_capacity(baseline_root)` returns country/year investment capacity and SHA-256 provenance. It reads `qualified_inputs/countries_2026_2031.ndjson` for 2026–2031 and `stage_2031_2060/countries_2031_2060.ndjson` for 2032–2035. The two inputs both contain 2031; the qualified-input series wins that boundary rather than silently mixing series. The result is a **capacity input**, not an account balance.

Next: run a reproducible Build 7 control with the available World Authority services, then wire these inputs to country-capital state without changing mobilization semantics. No Sponsor or FIN changes are authorized by this increment.
