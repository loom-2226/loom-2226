# Atlas Research Protocol v1.0

ARP is a reusable research-control layer above Solar Facts v0.3-R1. It
organizes evidence work; it does not promote facts, alter Phase-4 authority,
or decide scientific truth.

## Operating loop

`ASSESS → ACQUIRE → EXTRACT → VALIDATE → CLOSE GAPS / QUALIFY`

Every campaign starts with existing coverage. Pass 1 seeks broad authoritative
coverage across applicable body-profile lanes. Pass 2 targets material gaps,
conflicts, provenance deficiencies, or resolution deficiencies. Stop when the
configured stopping rule is met: sufficient authoritative evidence, convergence
onto derivative evidence, an established epistemic/resolution boundary, or a
diminishing-return threshold.

## Firewall

The boundary is `SEARCH RESULT → SOURCE CANDIDATE → ACQUIRED ARTIFACT →
EXTRACTED ASSERTION → NORMALIZED CANDIDATE → VALIDATED CANDIDATE`. A source
candidate is never an authoritative fact by discovery alone.

## Coverage and frontier

Coverage (`COVERED`, `PARTIAL`, `MODEL_ONLY`, `CONFLICTED`, `NOT_APPLICABLE`,
`UNKNOWN`, `SOURCE_NOT_FOUND`) is separate from scientific state. The
epistemic frontier uses `KNOWABLE`, `INFERRED`, `FUTURE_OBSERVABLE`,
`ENGINEERING_DERIVED`, and `ECONOMIC_DERIVED`. The last two are explicitly
outside empirical-factual authority.

Resolution, region, temporal scope, method, uncertainty, and independent
evidence-lineage identity are part of an assertion. Publications sharing an
underlying observation do not become independent evidence merely by count.

## Resumption and qualification

Stable IDs, lane coverage, unresolved gaps, artifact hashes, canonical
assertion keys, lineage IDs, metrics, and liens make campaigns resumable and
idempotent. An independent qualification pass reports liens rather than
silently repairing them. Blocking `OPEN` liens fail qualification; valid
unknowns can be represented by `ACCEPTED_UNKNOWN`, `SOURCE_UNAVAILABLE`, or
`DEFERRED_SCHEMA`.

See `profiles/body_profiles.json`, `policies/source_authority.json`, and
`contracts/` for machine-readable inputs. Run the validator with:

```text
PYTHONPATH=. python -m dev.atlas_research_protocol campaign.json \
  --authority-policy dev/atlas_research_protocol/policies/source_authority.json
```
