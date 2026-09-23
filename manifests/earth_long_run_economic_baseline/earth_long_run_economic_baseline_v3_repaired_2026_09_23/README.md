# Current v3 Earth baseline semantics

The [data dictionary](DATA_DICTIONARY.md) and [machine-readable field semantics](FIELD_SEMANTICS.json) cover every field in the qualified country, sector, asset, Taiwan boundary-repair, checkpoint and trajectory-summary records. They describe modeled accounting quantities and their provenance; they do not change the baseline or its outputs.

Run `python3 -B -m unittest -v test_field_semantics.py` here to check schema coverage, pinned implementation/output hashes and endpoint identities. The test reads the designated quantifactus baseline and does not run the model.

The authoritative baseline designation remains `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23`; resolve it through the [current pointer](../EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json). See [MODEL_SPEC.md](MODEL_SPEC.md) for the equations and [PROVENANCE.md](PROVENANCE.md) for source lineage.
