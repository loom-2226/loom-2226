# E1 GA Evidence Adapter v0.1

## Purpose

Provide a conservative, read-only adapter from existing E1 qualification artifacts and current Navigator solved-candidate output into the two minimum GA acceptance-evidence packages qualified by `E1_GA_MINIMUM_ACCEPTANCE_EVIDENCE_v0.1`.

This adapter inventories evidence. It does **not** certify geometric admissibility, change a GA axis disposition, move the earned Neptune endpoint, mutate campaign state, or bind runtime policy.

## Evidence states

The adapter distinguishes:

- `PRESENT_OPERATIONAL_EVIDENCE` — the current operational payload exposes evidence relevant to the required field;
- `PARTIAL_OPERATIONAL_EVIDENCE` — only part of a compound required field is exposed;
- `PRESENT_QUALIFIED_SUPPORT` — a qualified supporting artifact exists but is not itself the missing acceptance result;
- `PRESENT_BUT_NOT_ACCEPTANCE_AUTHORITY` — evidence exists, but promotion to an axis acceptance result is not earned;
- `PRESENT_BUT_REQUIRES_AUTHORITY_REVIEW` — a live field may look relevant, but semantic/authority review is required before promotion;
- `RUNTIME_INSPECTION_REQUIRED` — the static repository contract is insufficient and the read-only Navigator payload must be inspected;
- `MISSING` — no governed evidence satisfying the required item has been identified.

Field presence never equals certification authority automatically.

## Package A — endpoint/domain physical compatibility

Static repository evidence currently supports:

- committed ship identity (`WAYFARER_BASELINE`), but not yet a complete certified configuration tuple as a GA acceptance artifact;
- qualified J2-corrected Neptune local tidal reference;
- qualified standard-GR causal-pathology materiality screen;
- uncertainty/provenance carried by those qualified references.

The adapter intentionally does **not** promote those references into acceptance results.

The principal unresolved items remain:

1. governed translation-domain geometry or certification envelope for the committed E1 configuration;
2. local-geometry compatibility across that certified domain;
3. Loom-specific metric-domain causal compatibility, or a governed equivalent certification invariant.

Operational domain-like fields discovered at runtime are reported for review, not treated as a certified envelope.

## Package B — route/vessel coherence

The adapter runs the existing read-only E1 Navigator acquisition/solver path in a temporary workspace and inventories the selected solved-candidate payload.

It looks generically for semantic evidence corresponding to:

- route solution identity and direction;
- destination state and momentum/velocity mapping;
- route burden and uncertainty;
- committed configuration identity and domain membership/attachment state;
- formation and integrity state;
- hardware condition and lattice/thermal/bank margins;
- certification/admissibility disposition.

Aliases and nested payload paths are preserved in the report rather than requiring hard-coded Neptune-specific field names.

A certification-like field, if present, is reported as `PRESENT_BUT_REQUIRES_AUTHORITY_REVIEW`; it is never promoted automatically to GA acceptance authority.

## Runtime behavior

`e1_ga_evidence_adapter.py --live`:

1. creates a temporary Navigator workspace;
2. loads the real Navigator core;
3. uses the existing route-scoped SOURCE-010 acquisition seam;
4. solves the current Ceres → Neptune E1 candidate using `WAYFARER_BASELINE`;
5. inventories the selected candidate and solved leg;
6. maps discovered paths into the two evidence packages;
7. emits a deterministic JSON evidence report;
8. performs no campaign mutation.

## Qualification routing

This change also closes the remaining Pixel branch-discovery gap by teaching the governed runner to prefer the dedicated remote routing ref:

`origin/qualification/active`

That ref is qualification-routing authority only. Its pointed commit contains `engineering/pixel/active_qualification.txt`, which names the actual branch and command. It grants no merge, runtime, campaign, calculation, or scientific authority.

The runner retains the previous current-unmerged-branch and `origin/main` fallbacks when the pointer ref is absent.

## Authority

- Runtime policy mutation: `ZERO`
- Campaign state mutation: `ZERO`
- LLM calculation authority: `ZERO`
- Automatic GA certification: `FALSE`
- Cross-axis compensation: `FALSE`
- Package-level shortcut to admissible: `FALSE`

## Expected next decision

The live report determines the shortest legitimate convergence path:

- if Package B is substantially present operationally, qualify only the missing certification disposition / formation authority rather than rebuilding route evidence;
- Package A remains blocked until a governed translation-domain envelope and the corresponding geometry/causal acceptance evidence are actually earned.
