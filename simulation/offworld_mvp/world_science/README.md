# LOOM Offworld World Science Baseline

**Status:** EMPIRICAL SCIENCE PACKAGE / PRE-CONTRACT / NON-CANON / BUILD-INDEPENDENT  
**Parent:** `simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md`

This directory preserves the empirical Solar-System science substrate developed for LOOM Offworld. It is deliberately independent of any numbered implementation build. Builds may consume a governed version; they do not own it.

## Baseline
The preserved laboratory baseline is under `lab_v0_1/`. The SQLite file is `LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3`. At preservation it contains 47 bodies, 880 scientific assertions, 208 sources, 101 regions and 54 spatial products. Hidden-world, project-site and deposit populations are zero.

Original completed-lab SQLite SHA-256 before repository relocation: `40312c33892a390b0121426f74b7be5d803915cf192fa77b6868d694601614ff`.

Repository-relocated deterministic baseline SHA-256: `72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`.

The byte change is caused by making rebuild paths repository-relative and preserving M4B source-artifact locators as source-relative rather than worktree-specific absolute paths. Scientific counts, source hashes and evidence semantics are preserved. Two clean rebuilds at the repository location produced identical SQLite bytes. See `lab_v0_1/PRESERVATION_MANIFEST.json`.

The database is an empirical constraint/evidence package, not a navigation ephemeris authority, scenario-world authority, reserve database, or Agent knowledge store.

## Start here
- `WORLD_SCIENCE_AUTHORITY_AND_BOUNDARY.md`: authority and epistemic firewall.
- `WORLD_SCIENCE_RESEARCH_PROTOCOL.md`: repeatable research/population process.
- `WORLD_SCIENCE_SCHEMA.md`: relational structure and semantic layers.
- `WORLD_SCIENCE_6D_INTERFACE.md`: build-independent interface to hidden-world/runtime machinery.
- `seeds/`: canonical research seed template and representative worked seeds.
- `lab_v0_1/`: preserved database, schema, population scripts, manifests, validation, rebuild and readiness artifacts.

## Governing rule
Evidence constrains generation only at its supported scope, or through an explicit scientifically supported extrapolation relationship. Generated WORLD truth never becomes REAL evidence merely because LOOM generated or simulated it.

## Navigation
SPICE/JPL/NAIF remain the appropriate navigation/astrodynamics authorities where applicable. This package may identify and provenance those authorities and their coverage; it does not replace them with handcrafted ephemerides.

## Future promotion
A future PostgreSQL or other production representation must be a separately governed migration from a frozen, validated source baseline. Migration must preserve provenance, scope, ontology, uncertainty, UNKNOWN, conflicts, deterministic identity and the REAL/SCENARIO/REALIZED boundary.
