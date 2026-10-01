# CIVPROP Long-Run Actor Machinery V0.2

Status: **NON-CANON MACHINERY TEST / INTEGRATED CIVPROP**

Standalone entry point:

    python3 engineering/civprop/propagate_long_run.py --seed 42 --output longrun_42.json

Determinism check:

    python3 engineering/civprop/propagate_long_run.py --seed 42 --verify

V0.2 replaces the V0.1 parallel miniature simulator. The launcher now builds a temporary, hash-pinned 2026-2226 Method Lab bundle and invokes the existing `HYBRID_V1 / method-reference-v9` runner boundary. Closed GAP contracts are consumed rather than reimplemented.

## Integrated surfaces

The long-run path consumes Actor State V1, Accessibility V1, Demand/Pressure V1, Project Economics V1, Mission/Knowledge V1, Pressure Observability V1, Resource Mass Balance V1, Production Accounting V1, Power Balance V1, Traffic/Fleet V1, Facility/Site Materialization V1 and Asset Lifecycle V1. The output must report GAP-001 through GAP-013 CLOSED and GAP-014/GAP-015 OPEN.

`PROSPECTING_SURVEY` is mission economics only. It is never admitted to `project_archetypes`; prospecting therefore executes only through Mission/Knowledge V1 and can never materialize as a facility.

## V0.2 machinery-test assumptions

The 13-actor fixture and Earth-to-actor budget bridge remain non-canon. Coarse actor capability cells are explicitly bridged to the existing CIVPROP technology IDs. Generic logistics access and generalized cost are explicit machinery-test assumptions, not inferred empirical transport authority.

A bounded 2026-2035 lunar strategic-requirement envelope is admitted through **Demand/Pressure V1** to exercise infrastructure bootstrapping without forcing any project award. A non-canon prospecting follow-on success-value assumption allows **Mission/Knowledge V1** to exercise commit -> observe -> update. Both are sensitivity-required test parameters in `actor_bridge_parameters_v0_1.json`.

Surface transport bootstrap is represented by the existing `SURFACE_PORT` Project Economics / Infrastructure Archetype contract. Its V0.2 production and power-load projections preserve UNKNOWN where no empirical operating model exists.

## Important boundary

GAP-012 materialization and GAP-013 lifecycle remain at their promoted runner boundary: deterministic post-engine projections. V0.2 does not falsely claim that lifecycle retirement/maintenance feeds back into later Hybrid decisions. Making lifecycle fully causal across the 201-year propagation is a separate integration change, not something hidden inside this adapter.

GAP-014 demographic depth and GAP-015 Atlas-derived metrics remain OPEN. The result is not canon and not a forecast.

## Validator correction discovered by V0.2

The first facility-producing integrated run exposed a dormant GAP-005/GAP-011 replay-validator mismatch. Hybrid schedules projects using decision-year-resolved Project Economics, while Traffic/Fleet replay validation had used the base construction lag/prerequisites. Validation now resolves the same decision-year economics before reconstructing pending-project transport requirements. The frozen GAP-013 seed-42 causal result is unchanged; its implementation fingerprint/golden file is refreshed under change control.
