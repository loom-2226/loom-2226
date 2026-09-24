# EPHEMERIS_FOUNDATION_V1 qualification evidence

This repository records the evidence identity without changing the original
qualification artifact. The original remains at
`/home/ubuntu/loom_solar_assets/qualification/EPHEMERIS_FOUNDATION_V1/qualification_evidence.json`.

- Evidence SHA-256: `294890bc0ad5624d0bc2f0bf0ec850a7f19322093685adbb427c50c2dac9e56a`
- DE440 SHA-256: `a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5`
- Ceres supplementary SPK SHA-256: `adb69cc0723550fad437b7466fedaf7480e2e36c489e9d2d727e783a78566137`
- Ceres SPK object ID: `20000001` (external SPICE identifier only; not a LOOM body ID or MPC identity)

The frozen JSON artifact is the test oracle for Earth 2026, Earth 2226,
Neptune-system barycenter 2226, Ceres 2026, Ceres 2226, expected fail-closed
cases, and frame/time/unit/aberration semantics. The adapter tests consume it
read-only and preserve its hash above.

## PostgreSQL migration correction

Live PostgreSQL 16.15 qualification identified that product-level coverage
must represent `body_id IS NULL`. Migration 009 now declares `body_id`
explicitly nullable and uses PostgreSQL 16 `UNIQUE NULLS NOT DISTINCT`
instead of placing the nullable column in a primary key, while retaining the invariant:

- `PRODUCT` requires `body_id IS NULL`;
- `BODY` and `DERIVED` require `body_id IS NOT NULL`.

The migration regression suite covers these cases and orphan-body FK
enforcement. The frozen qualification JSON and kernel assets were not changed.

## Implementation qualification result

`EPHEMERIS_FOUNDATION_V1` passed the bounded implementation qualification.

### PostgreSQL 16.15

Migration 009 was exercised against the disposable PostgreSQL qualification
database after the nullable product-coverage correction.

Result:

- 8 tests executed;
- 8 passed;
- 0 failures;
- 0 errors;
- 0 skipped.

The live tests verified product-level NULL-body coverage, rejection of
product coverage carrying a body, valid body-specific coverage, rejection of
NULL body-specific coverage, the DERIVED body requirement, and orphan-body
foreign-key rejection.

### Governed SPICE adapter

The final adapter/qualification suite executed 13 tests successfully.

The qualified behavior includes:

- Earth states at 2026 and 2226 against the frozen qualification evidence;
- Ceres states at 2026 and 2226 through the qualified supplementary SPK;
- Neptune-system barycenter identity remains distinct from Neptune center;
- unsupported DE440-only Ceres and Neptune-center requests fail closed;
- explicit UTC normalization into SPICE time handling;
- ECLIPJ2000 geometric state semantics with no aberration correction;
- km and km/s state units;
- pinned kernel/evidence provenance;
- coverage enforcement;
- only QUALIFIED coverage backed by a QUALIFIED source is eligible;
- body-specific coverage outranks product-level coverage;
- equally specific qualified sources fail closed rather than using metadata
  order as an authority rule.

The frozen qualification evidence remained unchanged at SHA-256
`294890bc0ad5624d0bc2f0bf0ec850a7f19322093685adbb427c50c2dac9e56a`.

No Ceres civilization schema, Earth schema, CIVSTATE schema, legacy SQLite
authority, or `loom_world` authority was modified as part of this foundation.
