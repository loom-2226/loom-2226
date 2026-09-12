# LOOM 2226 — E1.1 Ceres Projection Diagnostic Finding v0.1

**Status:** EMPIRICALLY TESTED — PROJECTION WORK JUSTIFIED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` additive/non-replacement evidence  
**Parent:** PR #110 — E1.1 read-only Canon Context Projection  
**Canon effect:** none  
**Mutation:** none

## Objective

Test the first E1.1 discriminator before adding lore or broad projection architecture:

> Does governed Ceres information already exist in WORLD/CIVSTATE/Atlas at sufficient depth that a thin user experience should first be treated as a `PROJECTION_FAILURE` rather than a `DATA_FAILURE`?

## Pixel artifact

External Pixel artifact: `E1_1_CERES_PROJECTION_PROBE.json`.

Uploaded artifact SHA-256:

`3df7c41a1278b64297b1a06ed3c5136ab9d4cc80cfd32838e0af34766dea12ff`

The probe ran in `READ_ONLY_URI_MODE`, made no model call, performed no mutation and replaced no UI.

## Source identity

WORLD:

- path: `/storage/emulated/0/Download/LOOM_TEST/data/LOOM_2226.sqlite3`
- SHA-256: `23b13321ef56a63a28498455a8f9e403decce4e5bf1da0e5bdfcbeff3b904386`
- relations scanned: 43
- Ceres-bearing relations found: 20
- sampled matching rows: 96

CIVSTATE:

- path: `/storage/emulated/0/Download/LOOM_TEST/data/LOOM_2226_CIVSTATE.sqlite3`
- SHA-256: `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`
- relations scanned: 64
- Ceres-bearing relations found: 16
- sampled matching rows: 87

Atlas:

- `canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md`
- 8 Ceres-bearing blocks captured by the diagnostic.

## What already exists

The evidence is materially richer than a name/description lookup.

### Place and infrastructure

WORLD already identifies Ceres plus five major infrastructure nodes:

- `CER-P01` Occator Industrial Lift & Surface Port;
- `CER-P02` Ceres Polar Volatiles Terminal;
- `CER-P03` Ceres Belt Exchange;
- `CER-P04` Ceres Shipyard Arc;
- `CER-P05` Ceres Metric & Loom Anchorage.

These records carry facility roles, traffic classes, commercial actors, commercial regimes, civil/administrative/security authority, synthetic constituencies, institutional morphology, provenance and explicit epistemic/boundary notes.

### Demography and settlement form

The data distinguishes surface/in-body adult civic/work residence from near-Earth-gravity orbital family habitat. The Ceres total is approximately 7.73M biological and 4.46M synthetic persons, with the majority of biological residents in the rotating habitat/shipyard network rather than on the 0.028 g surface.

### Economy and mobility

CIVSTATE carries system economic state, productive/infrastructure capital, investment, workforce and automation. WORLD/Atlas classify Ceres + Belt as EXTREME bulk torch traffic, MAJOR metric traffic, PRIMARY Loom gate, PRIMARY shipbuilding, heavy repair YES, and EXTREME feeder density.

### Governance and institutions

Ceres is not represented as a monolithic state. Existing records distinguish Ceres Commonwealth civil authority from Belt Transit Authority, Belt Standards Directorate, Ceres Volatiles Cooperative, concession operators and Belt Security & Rescue Directorate. Facility-level governance differs across the five Ceres nodes.

### Relationships and actors

WORLD knowledge relationships and CIVSTATE graph views already expose direct authority, operations, security and actor-exposure relationships. Examples include Asteria Ship Systems at the Shipyard Arc, Axiom Precision & Metrology at the Metric/Loom Anchorage, Concord Mutual at the Belt Exchange, Ferrum Meridian across several nodes and Helios Materials Group at the Volatiles Terminal.

### Place texture

`civ_place_dna` and `civ_runtime_place_context` provide differentiated governance style, security posture, commercial openness, corporate proxy level, local autonomy, institutional trust, synthetic acceptance, migration openness, scarcity pressure, social tension, law-enforcement reach, outsider attitude and concise behaviorally constrained prompts per facility.

The five nodes are measurably different. For example, the Volatiles Terminal is more commercially open/cooperative while the Metric & Loom Anchorage is much more security-heavy, restrictive and civically assertive.

## Diagnostic conclusion

**Primary classification: `PROJECTION_FAILURE` is the first supported E1.1 hypothesis.**

The governed data already contains enough place, institutional, economic, demographic, infrastructure, relationship and behavioral structure to support a substantially richer Ceres experience than a thin summary screen.

This does **not** prove `DATA_FAILURE` is absent everywhere. It proves only that E1.1 must first expose and test the existing governed structure before authoring additional lore/data.

The previously noted habits/everyday-life gap remains a plausible later `DATA_FAILURE`, but it is not the next engineering move.

## Next implementation shape

Build a small typed read-only `LOOM_CANON_CONTEXT_PROJECTION_V1` that assembles existing authority into a bounded projection for one selected entity/place. The first target should be Ceres and its five canonical infrastructure nodes.

The projection should expose, where present:

- identity and role;
- short BLUF/context;
- population/settlement form;
- transport/economic role;
- civil/administrative/security authority;
- major commercial/institutional actors;
- selected relationship edges;
- place-DNA/behavioral signals;
- provenance and epistemic status for every projected section;
- explicit unavailable fields rather than inferred filler.

Do not give the model direct SQLite access. Do not promote engineering-reference positions to navigation authority. Do not synthesize new canon inside the projection layer.

## G2 standing invariant

Still holds for this increment:

- WORLD/CIVSTATE/Atlas remain source authority;
- projection is read-only and reconstructible;
- no model calculation or state authority;
- no browser authority;
- no campaign mutation;
- no UI replacement.

## Falsifier

Reclassify toward `DATA_FAILURE` for a required Experience One question if the bounded projection cannot answer it from governed WORLD/CIVSTATE/Atlas records without inventing information, after entity resolution and relevant relationship joins are functioning correctly.
