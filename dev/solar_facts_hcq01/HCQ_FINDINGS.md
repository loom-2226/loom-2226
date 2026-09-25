# HCQ-01 schema finding

## DDL DESIGN PROBLEM

`LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.2` has no relation for acquired raw-artifact identity or an audit event. It stores source metadata and `source_assertion` links, but not the artifact SHA256, byte count, or retrieval evidence inside SQLite.

Disposition: **RETAIN FROZEN SCHEMA; externalize the immutable artifact and audit manifest for this candidate harness.** No DDL or production migration was changed. A future schema revision may consider an artifact-manifest relation, but that is outside HCQ-01 vertical qualification.

## SOURCE PROBLEM

The live PDS profile pages acquired during research were marked **TEMPORAL-CONTROL EXCLUDED** because their catalog HTML carries a 2026 last-updated marker. They are retained as raw artifacts only; loaded Cohort-A provenance points to static pre-cutoff PDS archive files and the 2016/2018/2024 dataset identities.

## INGESTION PROBLEM

The first run exposed missing same-unit normalization for radius assertions. The rule was corrected before the final load; the final Cohort-A run had no rejected records.

## VOCABULARY PROBLEM

None identified.

## VALIDATION PROBLEM

None identified in the final run. Hostile regression remains passing.

## LEGITIMATE UNKNOWN

The full HAMO DTM image and complete gravity coefficient array are preserved as product artifacts/metadata relationships, not flattened into scalar facts. The schema does not justify inventing scalar summaries from those products.

## COHORT-A HOSTILE REVIEW

The exact acquired JPL artifact confirms that `469.7 km` is the Ceres **Mean Radius**, defined as the radius of a sphere with equivalent volume. It is not a polar radius or another dimensional quantity. MASS, EQUATORIAL_RADIUS, BULK_DENSITY, GM and the derived spherical VOLUME were independently checked against their source locators and normalization fields; no semantic correction was required. The before/after review is preserved in `COHORT_A_HOSTILE_REVIEW.json`.

The strengthened locator guard and regression test classify the protection as a **VALIDATION PROBLEM** discovered and corrected in the harness; the loaded scientific mapping remains unchanged.

## B-H QUALIFICATION FINDINGS

- **DDL DESIGN PROBLEM:** v0.2 has no native raw-artifact/hash/audit-event relation, no history relation, and no explicit model-to-observation relation for every product class. Immutable artifacts and JSON audit manifests remain external; no DDL change was made.
- **INGESTION PROBLEM:** real range-valued thermal evidence exposed an unsafe scalar-normalization path; it now preserves `value_min`/`value_max` without manufacturing a midpoint. Expanded material loading also exposed and fixed a SQL placeholder defect.
- **LEGITIMATE UNKNOWN:** abundance, full raster/coefficient contents, and unsupported geotechnical scalar values remain unknown rather than fabricated.
- **SOURCE PROBLEM:** one requested peer-reviewed Ahuna source was available as a public LPSC abstract rather than a journal full text; the acquired artifact is retained and represented as an abstract-level regional/model assertion.

## ROUND-2 DISPOSITION

R2-01 through R2-10 were remediated in the SQLite implementation, typed boundary, adapter, loader, and hostile tests. The rebuilt corpus contains only frozen evidence/confidence/assertion/status vocabulary. The Ahuna LPSC abstract is `OTHER`, all resolvable regional observations/models are relationally linked, and modeled PSR area is represented only by the PSR model product—not as water-ice areal extent.

Historical snapshots use source publication/release as an earliest-public-availability lower bound and never use 2026 retrieval time. They are intentionally not treated as observation dates. Results are 0 facts in 2010, 1 fact in 2016, and 8 facts in 2025.

Remaining **DDL DESIGN PROBLEMS** are limited to frozen-v0.2 representation gaps: raw artifact/hash/audit manifests remain external to SQLite, there is no native historical knowledge-event relation, and orientation uncertainty is retained in notes because the frozen orientation table has no uncertainty columns. These are documented limitations, not silently repaired by redefining v0.2.

## FINAL CLOSEOUT FINDINGS

### DDL DESIGN PROBLEM — raw artifact/audit provenance

v0.2 has no native relation connecting acquired raw-artifact identity, SHA-256, byte count, retrieval metadata, and audit manifests to the source/fact graph. HCQ-01 preserves these externally and verifies them deterministically. Future v0.3 work may add an artifact-manifest relation.

### DDL DESIGN PROBLEM / REPRESENTATIONAL LIMITATION — historical knowledge semantics

The harness supports deterministic 2010/2016/2025 snapshots using source publication/release as an earliest-public-availability lower bound. This is not equivalent to observation time, analysis time, publication time, adoption, revision, supersession, or controversy resolution. A future v0.3 knowledge-event/provenance-time model is indicated.

### DDL DESIGN PROBLEM — derived-fact lineage asymmetry

`derived_quantity` has machine-readable `derived_input` lineage, while `DERIVED` ordinary fact rows such as `BULK_DENSITY` retain lineage in prose only. Future v0.3 should support structured dependency lineage for derived fact rows.

### DDL DESIGN PROBLEM — orientation uncertainty

Orientation uncertainties are preserved in the source artifact and notes, but not in dedicated structured uncertainty fields. Future v0.3 may add parameter-level uncertainty representation.

### DDL DESIGN PROBLEM / HARDENING REQUIREMENT — update-safe semantic integrity

The SQLite analogue enforces body/region semantic consistency on INSERT and the application validator checks candidate updates. UPDATE-safe database-native protection remains a production-hardening requirement and was not used to redefine frozen v0.2 during closeout.

### VOCABULARY PROBLEM — preserved thermal preprint

The preserved `arXiv:2003.11045` artifact is an arXiv preprint. Bibliographic evidence indicates a later Astronomical Journal publication, but that journal artifact is not the artifact preserved in this HCQ corpus. The source is therefore represented as `OTHER`, the least misleading available v0.2 source type. No thermal values changed; source identity/provenance classification changed only. A future vocabulary could add `PREPRINT` without changing v0.2.

## QUALIFICATION HISTORY

`ROUND 1 — FAILED / NOT QUALIFIED` → vocabulary, temporal, regional, PSR, semantic-integrity and lineage remediation → `ROUND 2 — QUALIFIED WITH LIMITATIONS` → independent direct review → thermal preprint classification closeout → `HCQ-01 CERES — FROZEN`.

Round-1 database and report are preserved under `round1_qualification_artifact/`; the final record does not overwrite the failure history.
