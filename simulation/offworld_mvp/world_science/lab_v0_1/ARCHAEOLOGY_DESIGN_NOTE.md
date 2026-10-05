# Archaeology / Design Note
Status: EXPERIMENTAL, NON-CANON, NON-RUNTIME, NON-AUTHORITATIVE, NON-QUALIFICATION.

Live GitHub authority inspected: loom-2226/loom-2226 origin/main at 788f31c200ce59e844e44ef01ca62f37eb129bd8 (2026-10-05).

## Decisions
KEEP: LOOM-owned body identity; external identifier crosswalks; source/source-artifact separation; explicit candidate/admission state; coverage gaps; reconciliation; observation/region/material evidence; knowledge events; immutable artifact hashes; deterministic replay discipline.

EXTEND: HCQ observation model with explicit spatial products, sample entities, representativeness, bounds/ranges, vertical sensitivity, and source lineage.

GENERALIZE: physical scalar assertions into a typed scientific_assertion relation that supports numeric, vector/text, detection, bounds/ranges, models, spatial-product references and explicit UNKNOWN without forcing everything into a scalar.

REFACTOR: navigation authority is represented as identity + ephemeris source/coverage metadata. Full ephemeris time series are deliberately absent. This follows the current Solar Phase-1 contract: governed SPICE/DE440 evaluation remains outside persistence.

REPLACE FOR THIS LAB ONLY: the predecessor generic candidate_assertion is not the sole science representation. It remains traceable through imported rows but richer science uses observation, sample, region, spatial_product and material_evidence relations.

RETIRE: nothing in authoritative LOOM. This lab does not modify predecessors.

## Key predecessor findings
V10 verified: 110 authority bodies, 922 candidate assertions, 2,972 coverage rows, 67 source artifacts; no preferred facts. M4B retains sample/region/model scope and explicit unknowns. HCQ v0.3 adds spatial resolution, vertical sensitivity, typed fact inputs and knowledge events. Current Solar architecture explicitly separates body identity/ephemeris metadata from SPICE evaluation.

## Firewall
Scientific tables accept REAL_EVIDENCE, MODEL_INFERENCE, DERIVED and REALIZED_OBSERVATION only. Hidden realization state lives in separate tables keyed through world_realization. Generation policy is separate from empirical evidence.
## Mercury/Venus transfer result
V10 contained 16 physical/navigation candidates per body; M4B contained zero material rows for either. The existing architecture transferred without redesign. One minimal general schema extension was required for typed vertical support so Venus atmospheric altitude is not conflated with subsurface depth. No original six-body assertion semantics were migrated.

## Mars satellite hierarchy finding
V10 identifies Phobos and Deimos as NATURAL_SATELLITE with technical parent MARS_SYSTEM_BARYCENTER. The lab body hierarchy does not instantiate barycenters as geographic WORLD bodies, so the deterministic loader now adapts that technical parent to MARS while retaining the predecessor identity/classification. Parent-before-child insertion is now generic and FK-safe.

## Giant-planet and Pluto relationship finding
V10 uses JUPITER_SYSTEM_BARYCENTER as Jupiter's technical parent and PLUTO_SYSTEM_BARYCENTER as Pluto's. Neither barycenter is a WORLD geographic body in this lab. With satellites explicitly excluded from this pass, both target bodies remain root body records while their barycentric navigation lineage remains in imported source assertions. No Charon body was added.
