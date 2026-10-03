# LOOM AUTHORITY AND STATE CONTRACT v1
## Phase 1 Review Addendum and D0.20 Disposition

**Document:** `02_PHASE1_REVIEW_ADDENDUM.md`  
**Status:** PRE-CONTRACT / OWNER-AUTHORIZED PHASE 1 ADDENDUM  
**Date:** 2026-10-03  
**Owner:** @kT  
**Parent:** `01_PHASE1_AUTHORITY_ARCHAEOLOGY.md`  
**Review basis:** Claude, `Phase 1 Archaeology — Independent Review`, final verdict `ACCEPT WITH LIENS`  
**Normative effect:** This addendum refines the closed Phase 1 archaeological record without editing or reopening the closed parent text. It does not qualify any underlying LOOM holding and does not release `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1`.

## 1. Review disposition

The final Claude review returned:

`ACCEPT WITH LIENS`

The review found no CRITICAL findings, four MAJOR findings, four MINOR findings and three NOTES. It concluded that no new archaeology is required before Phase 2, provided the Phase 1 record is corrected through preserved-lineage addendum and the owner records the D0.20 decision.

The reviewer also disclosed an independence limitation: the same reviewer participated in the earlier architecture/Phase 0 work and therefore is not independent of the four-domain/four-pillar criticism in the strongest sense. That limitation remains recorded and becomes a later independent-check lien.

## 2. R-01 — Scoped meaning of UNKNOWN_AFTER_SEARCH

Phase 1 previously summarized M4-B `UNKNOWN_AFTER_SEARCH` too broadly.

Corrected archaeological finding:

- M4-B `UNKNOWN_AFTER_SEARCH` is relative to a **recorded bounded search scope**.
- 343 lanes carry that disposition.
- 324 lanes, covering 81 bodies × four resource families, were assessed against four earlier LOOM corpora recorded in the M4-B coverage matrix.
- 19 unknown lanes, on the bounded-pass-B target bodies, record an additional external source.
- The disposition is not evidence of absence and must not be interpreted as an exhaustive external search.
- M4-B does not establish a general representation for confirmed negative material evidence; the hostile `NONDETECTION_TO_ABSENCE` case is not an admitted positive semantics.

**Phase 2 lien:** an unknown state must reference the search/assessment scope that produced it. The epistemic label alone is insufficient.

## 3. R-02 — NULL/default audit correction

Phase 1 section 12.3 identified one consequential `or 0.0` site in `engineering/civprop/contracts/asset_lifecycle_v1.py` but missed a second.

The two relevant sites are:

1. replacement capital:
   `sum((e.replacement_capital or 0.0) ...)`
2. closing capital:
   `capital=max(0.0, opening-(depreciation or 0.0)+replacement)`

The second can convert `depreciation=None` into zero in the closing-capital calculation. The same module permits a `REPLACEMENT` event to restore ACTIVE status even when replacement capital is not supplied.

These observations do not establish a pervasive LOOM-wide UNKNOWN-to-zero convention. They do establish that the bounded Phase 1 search was incomplete.

**Q37 remains NOT ESTABLISHED.**

**Qualification lien:** before qualified input compilation, conduct a mechanical NULL/default audit covering at least `or 0`, `.get(k, 0)`, SQL `DEFAULT 0`, null-skipping aggregates, joins and filters, with scope and search mechanics recorded.

## 4. R-03 — Earth investment imputation version scope

The 22.3283039488531% pooled-median investment-rate imputation is established as an archaeological exemplar in the package:

`manifests/earth_long_run_economic_baseline/investment_rate_source_round1_2026_09_23/`

It applies in that package to ARE, JOR, LAO, MMR, NGA and TWN and is explicitly described there as an authored pooled imputation rather than an observation.

Phase 1 did **not** establish that this exact imputation survives into the currently promoted Earth reference.

Its relation to the promoted Earth reference is therefore:

`NOT ESTABLISHED`

The evidence bundle also demonstrates substantial late-horizon sensitivity across successive Earth repairs. Nigeria's 2226 VA share appears as 26.23% in the earlier alpha=.60 comparison, 17.56% in the national-GFCF successor, and 7.58% in repaired v3. This is archaeological evidence of model/version sensitivity, not a calibrated reliability statement.

The source record also distinguishes missing-current-value fallback from stale historical observations. Phase 2 must not collapse `STALE` and `MISSING` into one condition merely because a later substitution rule treated both operationally.

**Phase 2 lien:** establish current Earth version lineage and whether the pooled-median bridge survives before relying on that bridge as current input authority.

## 5. R-05 — Knowledge-time scope correction

Phase 1 established local knowledge-time controls but described their coverage too broadly.

Corrected finding:

- knowledge-time/as-of controls exist in multiple LOOM holdings;
- those controls apply only where relevant dates or validity metadata are actually present;
- M4-B contains records with missing temporal fields;
- absence of temporal metadata must not be converted into an implied date.

**Phase 2 lien:** time itself may be UNKNOWN. The claim/state model must support unknown temporal extent or knowledge time where warranted.

## 6. R-06 — Common-contract wording

The Phase 1 diagnosis is narrowed.

LOOM does have a partial common provenance/control plane for at least Earth and timeline holdings through `loom_control`, including snapshots, source artifacts and temporal coverage.

The stronger supported conclusion is:

> LOOM does not yet have one common LOOM-wide **authority and qualification contract** governing all relevant holdings and governed consumption boundaries.

Phase 2 shall use that narrower formulation.

## 7. R-07 — Existing delegation instrument

Phase 1 under-read `governance/agents/AGENT_REGISTRY.yml`.

The registry is not a civilization-actor registry, but it is relevant governance evidence. It records bounded technical-agent delegation, including WALTER's human-approved creation-review scope, deterministic blocking boundaries and restrictions against treating LLM judgment as evidence.

This does not supersede D0.8 default-deny. It is an existing candidate delegation instrument to classify under the Phase 2 authorization/delegation model.

## 8. R-08 — Reproducible negative searches

Phase 1 bounded negative searches did not consistently preserve enough mechanics to rerun each negative result.

Future archaeology/qualification searches that support `NOT LOCATED`, `NOT ESTABLISHED`, or equivalent negative findings should record, where applicable:

- repository/holding version or commit;
- searched paths;
- exact patterns/query classes;
- tool/method used;
- material exclusions or limits.

This is a methodological lien, not a reason to reopen Phase 1.

## 9. Review independence lien

The Claude review is hostile and evidence-bearing but is not independent of every challenged proposition. In particular, Claude participated in the earlier architecture work that produced the four-domain/four-pillar criticism.

Therefore:

- the Phase 1 finding that the four-domain shorthand is inadequate remains usable as archaeological evidence for Phase 2 design;
- it must not be represented as independently confirmed by this Claude review;
- a reviewer without that history should later check the finding before any governance claim requiring independent confirmation relies on it.

## 10. D0.20 owner disposition

On 2026-10-03 the owner selected **Option B**:

> Phase 2 Claim and Authority Model design may proceed under `SINGLE-AUTHORITY`.

This authorization is deliberately limited.

Phase 2 may, under `SINGLE-AUTHORITY`:

- construct and revise the candidate Claim and Authority Model;
- define candidate epistemic classes, scope semantics and dependency rules;
- adjudicate candidate authority-root types for design purposes;
- define candidate authorization, delegation, conflict, uncertainty and temporal semantics;
- carry forward and formalize the liens identified by Phase 1 and its review;
- inspect existing holdings as evidence for those design decisions.

While this disposition applies:

- all Phase 2 work remains `PRE-CONTRACT`;
- Phase 2 work requiring independence carries `SINGLE-AUTHORITY` rather than an independence claim;
- no Phase 2 design decision by itself qualifies, promotes or reclassifies an underlying LOOM holding;
- no AI or automated process acquires governance authority;
- the owner acting as authorizer and eventual consumer is disclosed rather than treated as independent review;
- a second-authorizer mechanism or an explicit later independent-review mechanism must be established before any act whose governing rule requires independent authorization can claim that requirement is satisfied.

This disposition satisfies the pre-Phase-2 decision required by D0.20. It does not satisfy future requirements for independent authorization.

## 11. Liens carried into Phase 2

Phase 2 begins with the following explicit liens:

1. unknowns must carry the scope of the search/assessment that produced them;
2. temporal fields and knowledge time may themselves be unknown;
3. current Earth version lineage and the standing of the pooled-median imputation remain to be established before governed consumption;
4. a mechanical NULL/default audit is required before qualified input compilation;
5. Phase 1's parameter-authorization, producer-consumer, fit/validation, AI-provenance and human-approval risks remain open;
6. existing delegation instruments must be classified under D0.8;
7. physical/mathematical standing must distinguish at least measured/source quantities, fitted model solutions, deterministic transforms and future extrapolated/projected state rather than treating them as one class;
8. a later reviewer without the existing Claude architecture history must independently check the four-domain finding where independent confirmation is required;
9. negative-search evidence should become mechanically rerunnable.

## 12. Phase transition

With this addendum and the D0.20 owner disposition recorded:

`PHASE 1: CLOSED WITH REVIEW LIENS PRESERVED`

`PHASE 2: CLEARED TO BEGIN UNDER PRE-CONTRACT / SINGLE-AUTHORITY`

Nothing in this addendum qualifies existing LOOM holdings, releases Contract v1, or adopts historical CIVPROP architecture.
