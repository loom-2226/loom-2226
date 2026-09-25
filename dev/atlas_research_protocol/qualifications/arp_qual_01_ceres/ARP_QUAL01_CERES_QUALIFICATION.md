# ARP-QUAL-01 — Ceres qualification

Date: 2026-09-26
Knowledge cutoff: `2025-12-31T23:59:59Z`
Research tier: Tier A / deep empirical envelope
Repository baseline: `b4bc58a2e4c88bfd2a0267be692e04fd1fb1c57f`

## Decision

`ARP v1.0: NOT QUALIFIED — REMEDIATION REQUIRED`.

The blind v1.0 attempt exposed a real contract failure: JPL mass was stored as
the normalized kilogram value in the reported-value fields, and the supplied
bulk-density uncertainty was omitted. The blind attempt is preserved unchanged.

The repaired implementation is identified as `ARP v1.0.1-reported-normalization-and-uncertainty-hardening`.
Its second attempt passed deterministic validation, reference comparison, and
independent hostile fixtures with limitations. It is a candidate successor
implementation, not a retroactive qualification of merged v1.0.

## Blindness and freeze

Research executed from `/home/ubuntu/ARP01_CERES_BLIND`, an external-input
allowlist containing only the generic ARP implementation/contracts/profile/policy
and public artifacts acquired for this attempt. HCQ-01 SQLite specimens, Ceres
gold fixtures, HCQ reports, semantic diffs, and ARP qualification reports were
not present in that environment. The resulting attempt-01 campaign was frozen
and hashed before the reference comparison. Attempt 01 campaign SHA-256:
`4275e6d7e83535ce22a1d9492495d827bccd33bbe413a3136d31ca0e8c4514d9`.

The HCQ reference remained unchanged at:
`0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`.

## Campaign and evidence

The blind run acquired 12 artifacts and extracted 16 assertion candidates
across 11 independent evidence lineages. Sources included JPL physical
parameters, NASA PDS Dawn gravity/coordinate/shape products, Dawn-derived
primary analyses, a preserved arXiv preprint, and pre-2026 peer-reviewed
analyses. Representative authoritative sources are the [JPL physical-parameter
table](https://ssd.jpl.nasa.gov/planets/phys_par.html), [PDS Ceres SPC shape
model](https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=DAWN-A-FC2-5-CERESSHAPESPC-V1.0),
[PDS gravity bundle](https://pds.nasa.gov/ds-view/pds/viewBundle.jsp?identifier=urn%3Anasa%3Apds%3Adawn-rss-der-ceres&version=1.0),
[Dawn coordinate-system document](https://sbnarchive.psi.edu/pds3/dawn/grav/DWNCGRS_2_v3_181005/DOCUMENT/CERES_COORD_SYS_180628.HTM),
and the [Ceres PSR paper](https://doi.org/10.1002/2016GL069368).

Pass 1 covered identity, rotation/orientation, gravity/shape, regional,
water/volatile and mineralogy lanes. Pass 2 added targeted thermal, regional
and composition evidence. Final coverage remained partial for orbit geometry,
geology/geotechnical, thermal environment and history. Site-scale mechanical
properties remain `UNKNOWN`; no value was fabricated.

## Reference comparison after freeze

Against the HCQ-01 gold fixture, attempt 01 had 3 matched scalar facts, 3
reference misses (GM, surface temperature, Ahuna regional evidence), 10
defensible additions, 1 supported thermal-unit difference, and 2
misclassified additions caused by the preservation defect. Attempt 02 corrected
the two misclassifications: 5 matched scalar facts, the same 3 reference
misses, 10 defensible additions, 1 supported difference, and zero unsupported
or misclassified additions.

The reference misses are not silently treated as failures of scientific truth;
they are recorded for protocol improvement. No candidate was promoted into
HCQ-01 or Solar Facts authority.

## Hostile evaluation

Both attempts were attacked with 12 synthetic cases. All 12 were rejected:
secondary-source substitution, duplicate evidence-lineage inflation,
regional-to-global promotion, coarse-to-site resolution laundering,
model-to-direct promotion, post-cutoff evidence, range midpoint fabrication,
UNKNOWN fabrication, FUTURE_OBSERVABLE promotion, forbidden engineering
frontier contamination, false completeness, and ignored blocking liens.

The repair added explicit reported/normalized value distinction, normalization
method metadata, uncertainty fields and checks, and assertion-artifact/source
identity checking. New ARP tests: 3. Full ARP tests after repair: 17/17 PASS.

## Integrity and boundaries

- v0.2 HCQ-01: unchanged and verified by SHA-256 above.
- All blind assertions remained `CANDIDATE`.
- No preferred facts, Phase-4 state, CIVPROP, resource, habitation,
  transport, economic, engineering, or fictional post-cutoff state was added.
- No post-cutoff source entered the campaign state.
- The campaign is resumable and idempotent under the ARP state contract.
- Independent hostile review produced no open blocking lien; accepted unknowns
  and source-unavailable limits remain explicit.

## Qualification artifacts

- `attempt_01_manifest.json` — frozen failed v1.0 attempt.
- `attempt_02_manifest.json` — repaired attempt manifest.
- `attempt_01_reference_comparison.json` and `attempt_02_reference_comparison.json`.
- `frozen_attempt_01/` and `attempt_02/` — campaign, validation, hostile-review,
  and hashed source artifacts.
- `research_extraction_attempt.py`, `hostile_review_runner.py`, and
  `reference_compare.py` — reproducibility/evaluation tooling.

Recommendation: keep merged ARP v1.0 blocked for the next body; review and
promote the repaired v1.0.1 implementation as a separately governed protocol
release before ARP-QUAL-02 Europa.
