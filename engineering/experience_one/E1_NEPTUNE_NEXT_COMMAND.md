Qualification command contract once the tested Spike B harness is present on this branch:

1. Seed a disposable Ceres campaign root with `e1_neptune_seed_ceres.py` using the Pixel runtime root as read-input source.
2. Run the tested disposable continuity harness with that seeded root and `--destination NEPTUNE_SYSTEM`.
3. Preserve its JSON result.
4. Require origin `CERES`, destination `NEPTUNE_SYSTEM`, both `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED`, restart at Neptune, replay PASS, and live campaign hashes unchanged.
