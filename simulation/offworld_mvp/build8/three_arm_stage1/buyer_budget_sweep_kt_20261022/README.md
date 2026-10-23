# Buyer budget sweep — TEST_ONLY

**Classification:** authored, synthetic, non-canon simulation scenario. This is
not a forecast, Earth policy proposal, buyer commitment, or body-specific
funding claim.

**Change class:** class:engineering (simulation implementation and
qualification artifacts only; no canon or runtime promotion).

The sweep changes only an annual external Earth inflow into the shared
`earth_market` account. Each year's inflow begins in a new, explicitly funded
`EARTH_BOUNDARY` account and reaches `earth_market` through kernel account and
transfer operations. The campaign resets its conservation reference after
that declared external boundary input; kernel transfers and all project
callbacks must conserve money for the rest of that callback. Totals are
summed at high precision and checked to 1e-20 model currency, with the raw
residual reported each year to account for sub-precision Decimal summation
drift across thousands of accounts.

The levels are 10, 100, and 1,000 model currency units per year. The existing
synthetic buyer endowment is 100 units per project, so these are transparent
0.1x, 1x, and 10x endowment reference levels. They are sensitivity points,
not empirically calibrated budgets. They apply identically across every buyer,
body, sponsor, and year. No buyer names, body prices, body sizes, or policy
governor set the level. The shared Earth buyer pool carries unspent funds
forward, so it stays finite while accumulated prior inflows remain available.

Three rendezvous cases run from 2026 through 2226. A separate zero-conversion
control uses the medium inflow and sets only the mission price conversion to
zero; physical construction and sales remain enabled. Source quote coverage,
candidate eligibility, sponsor-only selection, buyer affordability, starts,
sales, returns, placeholder status, ties, and non-Ceres projects are reported
separately. Outputs retain TEST_ONLY provenance.

Run from the repository root with the project Python environment and the
documented `PYTHONPATH` in the task request:

```sh
PYTHONDONTWRITEBYTECODE=1 /home/ubuntu/worktrees/loom/offworld-runtime-b7/.venv/bin/python \
  simulation/offworld_mvp/build8/three_arm_stage1/buyer_budget_sweep_kt_20261022/run_sweep.py
```
