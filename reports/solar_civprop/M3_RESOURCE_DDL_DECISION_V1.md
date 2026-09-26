# M3 Resource DDL Decision V1

## Decision

**NO NEW MATERIAL TABLE IS REQUIRED.**

The existing qualified Solar Facts material_evidence DDL already carries the empirical fields required by the Dorrington–Olsen/CIVPROP boundary: body and region scope, material family/species/form, evidence class, abundance semantics/value/range/unit, depth/thickness/area/volume, heterogeneity/resolution/method, confidence/status, observation linkage and source provenance.

Creating another resource table would duplicate authority and invite semantic drift. M3 therefore freezes a small consumer contract/view over the existing table instead.

## What must now be populated

The problem is population, not schema.

The current 110-body bulk baseline has useful physical inventory support (10 MASS, 36 EFFECTIVE_DIAMETER, 39 MEAN_RADIUS, 49 BULK_DENSITY candidate assertions), but the promoted multi-body factual database contains only 7 material_evidence rows across 2 bodies (Ceres and Europa).

For CIVPROP screening, every eligible body needs explicit coverage for the modeled resource families:
- VOLATILES
- METALS
- SILICATES_ROCK
- CARBONACEOUS_ORGANICS

A coverage state may be quantified, bounded, present but unquantified, nondetection/absence, upper limit, inferred/modelled, or UNKNOWN. **No row is not equivalent to UNKNOWN.**

This does not mean inventing four material claims per body. Where the scientific corpus genuinely does not establish a resource state, the coverage layer must explicitly record the frontier/UNKNOWN state rather than fabricate material evidence.

## Authority firewall

Taxonomy may inform a downstream probabilistic prior; it is not abundance.
Regional evidence may not be globalized.
UNKNOWN may not become zero.
Model/inference may not become direct measurement.
Resource evidence may not become an economic value.
Navigator owns delta-v/TOF.
Technology owns mining/recovery performance.
CIVPROP/economics owns prices, costs, NPV and BEMR.

## Next population pass

Build a contract-driven resource coverage matrix for the 110-body qualification catalog. Reuse existing qualified material evidence first, map structured existing sources second, and perform targeted external research only for materially useful gaps. Preserve genuine unknowns.

That population matrix, not a new DDL redesign, is the gate before CIVPROP resource propagation.
