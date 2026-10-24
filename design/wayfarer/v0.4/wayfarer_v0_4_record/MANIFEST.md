# Manifest and how to re-run

ALL bodies. ALL sponsors. 2026-2226.

NON-GOVERNING SANDBOX. Python 3 standard library only (no packages needed). `REPO` = a clone of github.com/loom-2226/loom-2226 (used only to read `geometry/wayfarer_geometry_seed.sql`).

Read first: `SPEC.md`.

## Final designs (re-run in this order)

| Command | Makes | What |
|---|---|---|
| `python shuttle_search.py --rebuild` | shuttle_tables.json, shuttle_results.json | flies every ascent and entry (about 2 min), then sizes every shuttle combination |
| `python shuttle_final.py` | shuttle_v0_2_final.json | the final landing shuttle v0.2 |
| `python uav_final.py` | uav_candidates.json | the two drones and their drop pods |
| `python wayfarer_v4.py REPO` | wayfarer_v4_results.json (+ parts JSON on stdout, saved as wayfarer_v4_parts.json) | Wayfarer v0.4 around the new shuttle |

Note: shuttle_results.json and shuttle_checks.json in this bundle came from the v0.1 runs at 1 GW/t; shuttle_space.json now holds the 2226 baseline (2 GW/t), so re-running them gives lighter shuttles.

## Inputs (authored, every assumption visible)

- shuttle_space.json: worlds, atmospheres, engines, heat shields, rovers, Venus strategies, hardening, 2226 baseline, sources
- uav_space.json: drone worlds, rotor/wing/power models, roles, drop pod, sources
- design_space.json, radiators_v3.json, radiators.json: Wayfarer hull, plant and radiator options
- ship_rules.json, shuttle_options.json, concepts.json: earlier rounds

## Code

- shuttle_physics.py: atmospheres, engines, ascent and entry simulators
- shuttle_search.py: shuttle sizing and search (`size_design`)
- shuttle_requirements.py: requirement costs, Venus strategies, heat shields, re-fly, sensitivity (v0.1)
- aerocapture_check.py: umbrella heating for fast arrivals
- uav_search.py: drone sizing and search
- optimize_v3.py, export_v3.py: Wayfarer v0.3 search and 3D parts
- wayfarer_v4.py: Wayfarer re-run with the new shuttle
- earlier rounds: ship_sizer.py (+ test_ship_sizer.py), optimize.py, optimize_v0_1.py, radiators.py, more_panels.py, close_winner.py, plant_options.py, concepts.py, shuttle_trade.py, export_picks.py

## Results

- shuttle_v0_2_final.json, uav_candidates.json, uav_sensitivity.json, wayfarer_v4_results.json, wayfarer_v4_parts.json (final)
- shuttle_tables.json, shuttle_results.json, shuttle_checks.json, shuttle_matrix.json, aerocapture_check.json (shuttle rounds)
- search_results_v3.json, search_results.json, search_results_v0_1.json, radiator_results.json, more_panels_results.json (Wayfarer rounds)
