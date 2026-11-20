# Shuttle v3 design explorer
ALL bodies. ALL sponsors. 2026-2226. NON-CANON engineering screen.

Generates shuttle + kit concepts inside Wayfarer's bay and scores them with the v3 models.

1. `python3 engine.py --n 1600 --seed 2226`: random designs over `SPACE`, plus the B5 reference (id 0).
2. `python3 evolve.py --gens 2 --pop 400 --seed 7`: mutates the best-trade-off (non-dominated) feasible designs.
3. `python3 reeval.py`: re-evaluates the population with the current engine (adds margins, limiting constraint, model version, input hash, mission results; Pareto without capability count).
4. `python3 archetypes.py`: picks named concepts (long reach, flying boat, light courier, hot extraction, big cabin, all-rounder).
5. `python3 build_site.py`: writes `site/data.json` and copies the model sources to `site/py/*.txt`.
6. `site/`: the interactive explorer page (`index.html` + `data.json`), published as a claude.ai artifact.

Gates (fail any = infeasible): bay fit r ≤ 2.15 m, dry ≤ 52.5 t, Earth sortie water ≤ tank, interior closes, W2 buoyancy (hull + floats).
Models: same ROM as the v3 steps (see engine.py docstring). For comparing concepts, not sign-off.

The page runs `engine.evaluate` and `missions.evaluate` in the browser with Pyodide (same Python files), so edits are recalculated by the real models. `missions.json` holds the mission profiles: all ASSUMPTIONS, editable on the page.
