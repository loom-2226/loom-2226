# Pluto six-body numerical convergence and long-baseline withheld-truth evidence

Preserved 2026-10-01 from Quantifactus /tmp after the PLU060 exact-constant reproduction work.

## Scope

These are experimental validation artifacts for the published PLU060 six-body dynamical model reproduced independently with SciPy DOP853 and direct DE440 external forcing. They do not mutate the LOOM authority ledger and they do not make propagated state DIRECT.

## Numerical convergence

The 2180-2199 tests at rtol=1e-12 gave global annual-sampled worst position errors of 13.265 m at 10800 s, 13.289 m at 5400 s, and 13.279 m at 2700 s maximum step. The 5400 s to 2700 s year-19 Hydra result changed by 9.473 mm. Further timestep reduction is not justified by this evidence.

## 186-year withheld-truth validation

The 2013-2199 run used DOP853, rtol=1e-12, and max_step=5400 s; recorded runtime was 6492.8 s. Global annual-sampled worst position error was 46.631 m for CHARON at year 184.

Per-body annual-sampled maxima: PLUTO 42.875 m (year 186), CHARON 46.631 m (year 184), NIX 42.520 m (year 186), HYDRA 42.442 m (year 186), KERBEROS 42.269 m (year 186), STYX 42.572 m (year 186).

## Interpretation boundary

This demonstrates very strong reproduction fidelity inside the PLU060 withheld-truth interval. It does **not** demonstrate positional accuracy through 2500. Post-PLU060 continuation remains a propagated estimate and must not be labelled DIRECT.

Raw validation JSON and run logs are preserved below convergence/ and long_baseline/. SUMMARY.json is derived only for convenient inspection. SHA256SUMS.json hashes every preserved artifact except itself.
