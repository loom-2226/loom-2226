# CIVPROP Long-Run Actor Machinery V0.1

Status: **NON-CANON MACHINERY TEST**

Standalone entry point:

    python engineering/civprop/propagate_long_run.py --seed 42 --output longrun_42.json

Determinism check:

    python engineering/civprop/propagate_long_run.py --seed 42 --verify

The executable runs the 2026-2226 machinery-test horizon. It combines the promoted 2026 actor fixture with a compact, provenance-pinned subset of the promoted Earth V4 economic trajectory and the existing CIVPROP Project Economics V1 archetypes.

## Causal loop exercised

Earth economic context -> explicit scenario allocation rule -> actor budget -> capability/access check -> BUY/PARTNER interaction where admitted -> project commitment -> construction lag -> commissioned facility/capacity -> maintenance/depreciation/retirement -> replacement or growth investment -> later actor decisions.

The Earth-to-actor allocation fractions, behavior weights, lifecycle rates, maintenance schedule and service lives are explicit **NON_EMPIRICAL_MACHINERY_TEST_ASSUMPTIONS**. They exist to exercise the machine, not to claim that named actors actually behave according to these values.

No GDP, national capital, market capitalization, or valuation is silently treated as spendable actor cash. The compiled Earth support subset preserves its source Earth phase hashes. No future canon event is injected.

## V0.1 boundaries

This executable does not replace HYBRID_V1 / method-reference-v9 or the frozen 2026-2036 qualification baseline. It is the first long-run actor-machinery experiment. Shared infrastructure is intentionally simplified in V0.1, and actor admission, budget calibration, interaction formation, facility siting, resource discovery, failure stochasticity, demography and Earth/off-world feedback remain later refinement surfaces.

## Measured VM runtime, 2026-10-02

On quantifactus:
- seed 42: about 0.15 s simulation CPU time; about 0.47 s wall for --verify including a second deterministic run and Python startup;
- 100 serial seeds: 24.52 s wall, mean 0.243 s/seed, p95 0.345 s/seed;
- full CIVPROP test suite after integration: 321 tests in 4.211 s, PASS.

Runtime on a Pixel or Windows host will differ by Python/filesystem performance, but the executable is stdlib-only and repo-relative.
