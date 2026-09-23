# Implemented Earth 2060–2226 model

This records the equations actually implemented in `runner_executed.py` and `long_run_repair.py`. `runner.py` differs only by the corrected TFP descriptor string. The run starts from the existing **qualified frozen 2060 country state**. For the one active zeroed sector, the within-country 2060 boundary reconstruction in `PROVENANCE.md` is applied before forward propagation. The existing v2 alpha ceiling of 0.60 and WDI national GFCF/GDP rate are the initial operative policy at that boundary.

## Production and factor-share transition

For country `i`, sector `s`, year `t > 2060`:

```text
n = t - 2060
w_alpha(t) = 1 - 2^(-n/20)
alpha_i(t) = alpha_i(2060 operative) + w_alpha(t) * (1/3 - alpha_i(2060 operative))
labor_exponent_i(t) = 1 - alpha_i(t)
Y_i,s,t = TFP_i,t * technology_multiplier_i,s,t * A_i,s,t
          * K_i,s,t^alpha_i(t) * L_effective_i,s,t^(1-alpha_i(t))
```

Immediately before production at the **current** capital and effective labor inputs, operative A is rebased once for that annual alpha change:

```text
A_new = A_old * exp[(alpha_old - alpha_new) * ln(K_current / L_effective_current)]
```

This makes output at those inputs continuous across the parameter change. The source/historical `cobb_douglas_A_2026` is carried unchanged; the operative `A` is separate. The 20-year alpha-transition half-life is a **LOOM simulation assumption**, not an estimated OECD coefficient.

## Investment and capital

The code first advances each asset using the inherited stock-flow identity, then calculates current production and the investment budget that will enter the next year's asset state. With `D_i,t = sum_assets(delta_asset * K_asset,t)`, `Y_prev` the previous year's country VA, `K` current total productive capital, and `r_i,2060` the WDI-derived national rate:

```text
w_I(t) = 1 - 2^(-(t-2060)/20)
I_target_i,t = max(0,
    D_i,t + 3.4 * (Y_i,t - Y_i,t-1) + 0.05 * (3.4 * Y_i,t - K_i,t))
I_i,t = max(0, (1-w_I(t)) * r_i,2060 * Y_i,t + w_I(t) * I_target_i,t)
K_asset,t+1 = (1-delta_asset) * K_asset,t + I_asset,t
```

The target is a **3.4 capital/VA ratio**. The replacement/depreciation term, output-growth term and 5% annual capital-gap closure are all in the implemented rule. The country investment budget is distributed through the inherited asset replacement and expansion allocator. The 20-year investment blend and **5% gap adjustment** are LOOM simulation assumptions, not estimated OECD coefficients. No country-specific outcome cap or Nigeria-specific rule exists.

## TFP and retained structure

The existing qualified PWT-derived TFP mechanism remains numerically unchanged:

```text
g_log_base(t) = g_frontier_log
  + [ln(1+g_2060) - g_frontier_log] * exp[-ln(2)*(t-2060)/10]
g_TFP_simple(t) = exp[g_log_base(t) + beta * max(0, gap_log_t)] - 1
TFP_t = TFP_t-1 * (1 + g_TFP_simple(t))
gap_log_t+1 = max(0, gap_log_t * exp(-beta))
```

The run's qualified PWT calibration reported frontier growth **0.1053% simple annual** and catch-up speed **0.01304**. It uses comparable CTFP-derived country gaps and within-country PWT growth, without treating internal TFP multipliers as cross-country levels. The inaccurate old raw descriptor was replaced with `FRONTIER_GROWTH_TRANSITION_DECAYING_CATCHUP`; that string correction changed no TFP equation, annual value, multiplier or numerical trajectory.

The inherited WPP demographic tail, labor allocation, asset depreciation, OECD trade-topology rewiring and evidence-bounded neutral technology multiplier remain in use. OECD conditional-convergence variables for governance, globalization and macro stability were **not** added because qualified inputs were unavailable; the defensible frontier and catch-up core was retained.

The [OECD 2025 long-run model](https://www.oecd.org/en/publications/oecd-global-long-run-economic-scenarios_00353678-en/full-report/component-4.html) is the methodological reference for the approximately **1/3 capital share** and **3.4 capital/output target**, not a claim that this LOOM run reproduces OECD projections. The OECD's [mixed-convergence annex](https://www.oecd.org/en/publications/oecd-global-long-run-economic-scenarios_00353678-en/full-report/component-8.html) describes the omitted conditional variables.
