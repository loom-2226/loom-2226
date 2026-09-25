# ARP-QUAL-01 Ceres — Reference-Miss Forensics

Change class: `class:research`

This is a post-hoc analysis of the frozen ARP-QUAL-01 attempts. It does not
alter either blind campaign, its artifacts, its assertions, or HCQ-01.

## Separation of evidence

The blind evidence is limited to `frozen_attempt_01/` and `attempt_02/`.
The answer key was inspected only after those campaign outputs and manifests
were frozen. The original failed attempt remains byte-for-byte represented by
its existing manifest and campaign hash.

## Miss findings

### GM — source discovery, with coverage-accounting contribution

The blind run acquired JPL physical parameters and a Dawn gravity product but
did not acquire the DE440/DE441 paper used by the HCQ GM assertion. The JPL
artifact contains physical-parameter/gravity documentation, but the HCQ scalar
locator is the DE440/DE441 paper table. The gravity lane was marked `COVERED`
without recording which foundational scalar questions were answered.

This is not evidence that an acquired GM value was lost in normalization or
that the evaluator rejected an equivalent value. Primary classification:
`SOURCE_DISCOVERY_DEFECT`; contributing classification:
`COVERAGE_ACCOUNTING_DEFECT`.

### Surface temperature — extraction/implementation defect

The acquired `thermal_arxiv.html` contains the 170–180 K disk-averaged
brightness-temperature result in the page metadata and abstract (lines 30, 41,
and 128 of the preserved artifact). The blind candidates retained thermal
inertia but no `SURFACE_TEMPERATURE` assertion. This is a genuine extraction
miss from an acquired artifact, not a post-hoc source-discovery claim.

Primary classification: `EXTRACTION_DEFECT`; contributing classification:
`IMPLEMENTATION_DEFECT`.

The value is not added to the frozen campaign by this forensic record.

### Ahuna evidence — coverage accounting, with source-discovery contribution

No Ahuna artifact was acquired in the blind run. The regional lane was marked
`COVERED`, while geology/geotechnical remained `PARTIAL`; no explicit basis
listed the regional evidence questions addressed, unresolved, or unavailable.
The HCQ Ahuna source is a separate LPSC artifact absent from the blind artifact
set.

Primary classification: `COVERAGE_ACCOUNTING_DEFECT`; contributing
classification: `SOURCE_DISCOVERY_DEFECT`.

## Foundational-coverage hypothesis

Supported as a risk, not proved as the sole cause of all three misses. The
campaign found optional/deep evidence while lane-level `COVERED` states did not
expose foundational question coverage. GM and Ahuna also involve source-family
discovery, and surface temperature is an extraction miss.

## Narrow general remediation

ARP v1.0.2 adds an opt-in, body-agnostic `coverage_contract_version: "1.0.2"`.
Under that contract, a lane marked `COVERED` must include explicit evidence
question basis entries. A basis may honestly be `SUPPORTED`, `UNKNOWN`,
`SOURCE_NOT_FOUND`, or `NOT_APPLICABLE`; unresolved states require a rationale.
This prevents optional evidence volume from silently substituting for
foundational accounting. It does not encode Ceres lanes, values, source IDs, or
answer-key expectations and does not determine scientific truth.

## Disposition

ARP v1.0.1 formalizes the repaired reported/normalized-value, uncertainty, and
provenance implementation. The coverage correction is separately identified as
ARP v1.0.2 because it extends behavior beyond that earned patch.

`NOT_READY_FOR_ARP_QUAL_02`: v1.0.2 must first be exercised by a fresh
independent body qualification. No Europa campaign is started here.
