# LOOM AUTHORITY AND STATE CONTRACT v1
## Phase 0: Authority Problem Statement
### Revision 3

**Document:** `00_AUTHORITY_PROBLEM_STATEMENT.md`  
**Status:** PHASE 0 CLOSED — OWNER-AUTHORIZED AND INDEPENDENTLY REVIEWED/ACCEPTED  
**Phase:** 0  
**Date:** 2026-10-03  
**Owner:** @kT  
**Scope:** LOOM-level governance for new and newly coupled work  
**Normative status:** Phase 0 principles bind any work that claims governed status or consumes governed work. No technical mechanism is normative.  
**Phase 0 decisions:** D0.1–D0.20  
**First hostile review:** Claude, `Phase 0 Authority Statement — Hostile Review`  
**Review disposition:** F-01–F-22 and N-1–N-4 OWNER ACCEPTED on 2026-10-03. Independent hostile review subsequently completed and accepted by the owner on 2026-10-03; no unresolved critical contradiction remains.

## 1. Purpose

LOOM requires a common authority and state framework before new simulation systems are permitted to consume existing LOOM information and generate consequential simulated state.

The immediate pressure for this work arises from CIVPROP, but this document does not define CIVPROP architecture.

CIVPROP is understood here as a causal simulation system that may consume governed information about Earth, technology, the Solar System, actors, physical constraints, institutions and other relevant LOOM authorities, then propagate civilization through actor decisions, processes and consequences.

The authority problem exists upstream of CIVPROP.

LOOM already contains or may contain observations, derived information, projections, scenario declarations, model parameters, explicit unknowns, authored material, physical-law products and simulated results. These are not epistemically equivalent merely because they coexist in a database, repository or model.

The purpose of `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1` is to establish how LOOM represents, qualifies, preserves, transforms and consumes information without allowing its epistemic meaning, permitted use or causal lineage to drift.

This Phase 0 document establishes the governing principles the later contract must satisfy. It does **not** prescribe their technical implementation.

## 2. Vocabulary

**Claim.** An identifiable assertion about a subject, with content and applicable scope, to which provenance and authority can be attached independently. A claim need not correspond to one database cell. The eventual technical representation is undecided.

**Authority.** The warrant under which LOOM may rely upon a claim for a specified scope and use. Authority is not synonymous with truth.

**Authorization.** An explicit governance act permitting a claim, assumption, parameter, classification, rule or transformation to be used for a defined purpose.

**Provenance.** Records where a claim came from and the relevant history by which it reached its present form. Provenance describes origin and transformation. It does not by itself establish authority.

**Qualification.** A governed determination that a claim, collection, interface or process satisfies specified requirements for a stated use and scope. Qualification does not certify universal correctness.

**Standing.** The combination of a claim's epistemic class, evidentiary extent, temporal extent, permitted use, qualification status and limitations. Dependency rules compare standing. Standing is not truth.

**Truth.** Correspondence with reality. LOOM governance does not claim to certify truth merely by qualifying information or producing a governed result.

**Trust.** A human or institutional judgment concerning reliance on a source, process or system. Trust may contribute to governance decisions but is not itself a substitute for recorded authority.

**Governed.** A result produced in accordance with the applicable LOOM authority contract and its recorded qualification requirements. Governed status certifies the applicable warrant, reproducibility/audit properties and causal traceability required by the contract. It does **not** certify truth, empirical correctness, model validity, predictive success or scientific acceptance.

A governed model can be wrong. It must not be mysterious about how it became wrong.

## 3. Problem Statement

LOOM must combine heterogeneous information without silently changing what that information means.

Without explicit authority rules, transformations such as these become possible:

```text
projection → observation
scenario assumption → prediction
unknown → zero
unknown → excluded row
unknown → false condition
missing → interpolated fact
simulation → evidence
qualified-for-X → qualified-for-everything
database membership → authority
conflict → silent winner
missing uncertainty → certainty
reference trajectory → rewritten history
model output → adopted reference without authorization
```

Each can produce plausible outputs while violating the meaning of the underlying information.

For governed information LOOM must be able to establish what the claim is and means; why it may be relied upon; its evidentiary, temporal and intended-use scope; when it was known; its provenance and transformations; its dependencies and uncertainty; treatment of unknowns and conflicts; assumptions and simulation ancestry; who authorized relevant judgments; the governing qualification rules; replay/audit status; and reconstructable causal path.

## 4. D0.1 — Scope

The authority contract belongs at the **LOOM level**, not inside CIVPROP.

It governs new work subject to the contract, new interfaces between existing LOOM components, and existing claims when newly consumed through a governed interface.

Existing work is neither presumed compliant nor presumed defective merely because the new contract exists. Qualification follows governed consumption.

## 5. D0.2 — Three Coequal Integrity Requirements

A governed LOOM result must preserve:

1. **Epistemic integrity:** LOOM must not represent information as better known, more empirical, more certain or broader than its warrant supports.
2. **Reproducibility and audit integrity:** LOOM must preserve sufficient identity, inputs, transformations and computational context to satisfy its declared replay mode and permit causal audit.
3. **Causal integrity:** simulated consequences must trace to legitimate prior state, rules, decisions, processes and events.

No requirement substitutes for another.

## 6. D0.3 — Unknowns Block Their Dependents

UNKNOWN remains UNKNOWN. A dependent operation **shall block unless an explicitly authorized bridge applies**. Unrelated operations may continue only where no governed dependency or invariant couples them to the blocked operation.

```text
UNKNOWN ≠ 0
UNKNOWN ≠ FALSE
UNKNOWN ≠ average
UNKNOWN ≠ default
UNKNOWN ≠ empty
UNKNOWN ≠ excluded
UNKNOWN ≠ interpolated fact
UNKNOWN ≠ permission to infer
```

An aggregate containing relevant unknown members cannot silently report the aggregate of only known members as the complete aggregate. It may instead produce an explicitly partial result, bound, interval or unknown result when governing rules authorize that interpretation.

Logical treatment of unknown must preserve a state distinct from TRUE and FALSE where relevant. Representation changes must preserve semantic distinctions among unknown, zero, false, empty and not present.

An assumption may bridge an unknown only through authorized governance.

> **The model's need for a value does not create authority to supply one.**

Dependencies and invariants that couple operations, including conservation, accounting and identity invariants, shall be declared through authorized governance before a result relies on the independence of those operations. A coupling discovered after a result was produced is a defect against that result, and its governed status is suspended until the coupling is declared and the result re-evaluated. The absence of a declared coupling is not evidence that none exists.

## 7. D0.4 — Claim Authority and Computed Standing

Authority ultimately attaches to claims.

Common metadata may be inherited from a qualified parent structure only when the parent explicitly states which members are covered, how that coverage was established, applicable scope and use, and known exceptions. Absence of a recorded exception is not itself evidence that a member conforms.

A claim-specific override may **weaken** inherited standing. It may not strengthen standing without an independently authorized governance act.

A computed claim cannot silently acquire stronger standing than its dependencies. Its standing may not exceed the weakest applicable standing, narrowest applicable evidentiary or temporal extent, and most restrictive permitted use among dependencies necessary to produce it, unless an independently governed process explicitly authorizes otherwise.

Where dependency classes are not meaningfully rankable, their contribution must remain visible rather than being collapsed into a falsely stronger single class.

A scenario assumption that happens to match an observation remains a scenario assumption unless independently sourced and explicitly reclassified.

## 8. D0.5 — Simulation Is Not Evidence by Inheritance

Simulated state may legitimately parent later simulated state within a governed lineage. Simulation does not become empirical evidence merely through persistence, reuse, storage, merging, repetition or agreement with observation.

A governed result's required ancestry must itself be governed or explicitly adopted through an authorized process. An ungoverned result cannot silently enter a governed lineage.

Any epistemic class change is a lineage-recorded governance event, never an in-place relabeling. A model output becomes an adopted projection or reference only through an explicit adoption decision identifying the producing model/version and applicable scope.

## 9. D0.6 — Existing Artifacts and Interface Qualification

Existing LOOM artifacts retain their historical status. Historical qualification labels are provenance about the governance mechanism that produced them. They do **not** constitute qualification under v1.

When governed work consumes an existing artifact, the relevant claims, collections or interface must satisfy applicable v1 requirements.

Qualification must not silently create a filtered world. A governed result must disclose coverage of its intended domain, including excluded, blocked, quarantined or unqualified portions where those omissions affect interpretation. Coverage representation is deferred. The default treatment of insufficient or undefined coverage is established in D0.15.

## 10. D0.7 — Projection and Scenario Assumption

**PROJECTION** is an evidence/model-derived estimate of an unknown future state.

**SCENARIO_ASSUMPTION** is a condition declared true within a defined scenario without claiming it is an empirical forecast.

These distinctions are binding. A scenario may intentionally contradict a projection. That does not automatically constitute an evidentiary conflict because the scenario describes a counterfactual or stipulated world. A scenario purporting to describe past or present empirical reality while contradicting accepted evidence requires explicit treatment.

## 11. D0.8 — Human-Rooted Authorization

New assumptions, model parameters and governance judgments require explicit authorization. Classification, qualification, promotion, source acceptance, epistemic reclassification and conflict-resolution rules are governance acts and require human authorization.

Until a later delegation framework is explicitly approved:

> **Delegation is default-deny.**

No AI system, automated process, optimizer or software component possesses independent governance authority. Its outputs may become candidates for human acceptance. They acquire no authority merely because of their origin.

A fitted parameter must preserve its fitting basis. A value must not be validated against the same target used to fit it without that dependency being explicitly represented and the validation claim correspondingly limited.

A value chosen or adjusted after observing the output it influences, whether by fitting, manual tuning or selection among alternatives, is **outcome-conditioned**. Its authorization shall record that condition and the outputs observed when it was chosen. Validation against those outputs is invalid, and results depending on the value shall disclose the condition.

Authorizations must ultimately record the authorizing human, date, subject, permitted scope/use, applicable version/scenario where relevant, and basis.

Post-hoc authorization is permitted only as a new governance event and must remain visible as such. A failed or blocked run is not retroactively rewritten as though authorization existed beforehand.

## 12. D0.9 — Conflicts Remain Information

Contradictory qualified claims remain visible as conflict unless a governed resolution rule applies.

Resolution rules are explicit authorizations, are versioned, state the class of conflicts to which they apply, operate prospectively, and preserve their use in lineage. A run retains the rule set under which it operated. Broad convenience rules do not receive unlimited implied scope.

Different epistemic classes may conflict differently. A scenario versus a future projection may represent deliberate counterfactual divergence, while two competing observations of the same quantity may constitute evidentiary conflict.

> **Conflict is information.**

## 13. D0.10 — Storage Cannot Create Authority

PostgreSQL is not authority. SQLite is not non-authority. A Git merge is not truth. YAML is not provisional by definition. JSON is not governed by definition.

Storage may preserve identity, integrity, version, immutability, transactionality and provenance. It cannot create epistemic warrant.

Moving claims between approved representations must preserve semantics, not merely bytes. Semantic round-trip testing must eventually address distinctions such as unknown, zero, false, empty, identity, unit and applicable metadata. Implementation is deferred.

## 14. D0.11 — Reference and Realized State Remain Distinct

Reference state and realized simulated state are permanently distinguishable and independently queryable. A simulation may diverge from reference. It may never overwrite the historical identity of the reference it consumed.

Every realized run must identify the exact reference version from which it diverged.

No Earth delta architecture, coupling mechanism or storage implementation is selected here.

`REFERENCE ≠ REALIZED`

## 15. D0.12 — Replay and Audit Are Distinct

Every governed computational result must declare its reproducibility mode and acceptance criterion. Candidate modes include `REPLAY_EXACT`, `REPLAY_WITHIN_TOLERANCE` and `AUDIT_ONLY`; final vocabulary is deferred.

**Replay** concerns whether recomputation reproduces the result according to a declared criterion.

**Audit** concerns whether recorded causal history explains how the result arose.

Causal audit is mandatory for governed simulation regardless of replay mode.

The applicable record must identify, as necessary, governed inputs, model/code version, parameters, assumptions, random state/seed where applicable, reference version, causal history, governing contract version and declared replay criterion.

Bitwise cross-platform determinism remains undecided.

## 16. D0.13 — Qualification Is Graduated, Scoped and Explicit

Qualification is not universal.

Its eventual representation must capture at least what was qualified; evidentiary extent; temporal validity; intended use; who authorized qualification; basis; contract/version; and applicable limitations.

The earlier pseudo-signature `Qualification(claim, scope, intended_use, contract_version)` is withdrawn because it prematurely implied a schema.

Qualification vocabulary remains provisional. Use restrictions propagate through dependency standing under D0.4.

## 17. D0.14 — Contract Versions Are Immutable

A released contract version does not silently change meaning. Changed normative rules require a new version. Migration or requalification is governed.

`QUALIFIED_v1 ≠ automatically QUALIFIED_v2`

`QUALIFIED_v1 ≠ automatically INVALID_v2`

Discovery of a defect in a released contract does not rewrite history. The defect must be recorded against the affected version and affected governed outputs must be identifiable and flaggable. Correction occurs through an explicit new version or other governed remedial mechanism.

## 18. D0.15 — Local Failure Versus Result Failure

Failures affecting unconsumed or irrelevant claims need not invalidate an otherwise governed result. Failures affecting claims actually consumed by a result may compromise that result.

Whole-result governed status fails where required epistemic, replay/audit or causal guarantees cannot be established.

A blocked operation must generate an explicit **BLOCKED** outcome where its absence could otherwise be mistaken for a negative decision or nonexistent opportunity.

Operations coupled through conservation, accounting, identity or other invariants block together where proceeding independently would violate those invariants.

Every governed result shall report its coverage of its intended domain. A governed result may claim to represent a phenomenon only where an authorized coverage threshold exists for that phenomenon and the result's coverage meets it. Where no authorized threshold exists, the result shall report its coverage and shall not claim representation. The threshold mechanism is deferred. The default is not.

Dependencies and invariants that couple operations, including conservation, accounting and identity invariants, shall be declared through authorized governance before a result relies on the independence of those operations. A coupling discovered after a result was produced is a defect against that result, and its governed status is suspended until the coupling is declared and the result re-evaluated. The absence of a declared coupling is not evidence that none exists.

A diagnostic or experimental computation may still execute after governed status is lost, but its outputs remain explicitly non-governed unless subsequently adopted through a governed process.

`COMPUTATION COMPLETED ≠ GOVERNED RESULT`

## 19. D0.16 — Inspectable Explanation

Every governed material result must permit traversal through sufficient stable lineage to explain its causal ancestry:

`RESULT → EVENT/STATE TRANSITION → DECISION OR PROCESS → INPUTS + RULES → SOURCES/ASSUMPTIONS/PRIOR STATE`

Governed systems must also preserve causally relevant non-events, including BLOCKED outcomes, when their absence would otherwise be indistinguishable from a deliberate decision not to act.

The determination that lineage is “sufficient” is itself governed. An approved criterion may operationalize that judgment under §27. No ledger implementation is selected here.

## 20. D0.17 — Uncertainty Is Preserved, Not Invented

Known uncertainty must survive legitimate transformation. Unknown or uncharacterized uncertainty must not be represented as zero uncertainty.

Simulation variability is not automatically epistemic uncertainty. Spread across random seeds or ensemble runs describes variability within the model under those conditions. It does not by itself measure uncertainty about reality.

Scenario assumptions do not acquire probabilities merely because simulations can be run over them. Projection uncertainty is conditional on the model, assumptions and evidence underlying the projection.

Determinations of material uncertainty require authorized criteria rather than implementer convenience.

## 21. D0.18 — Authority Roots Are Explicit but Extensible

Authority must have an explicit root.

Phase 0 recognizes two **known** legitimate authority-root forms:

1. **Evidentiary warrant:** an identified source accepted through an explicit governance decision for defined scope and use.
2. **Explicit authorization:** an assumption, parameter or imposed model condition authorized through governance.

These are not declared exhaustive.

Phase 1 must investigate whether existing LOOM holdings require additional legitimate authority-root types, particularly around physical law, mathematical relationships, standards, institutional or legal authority, entity identity and internally verified computation.

Until another root type is explicitly recognized:

> **An implementation may not invent a new authority root merely because a claim does not fit an existing one.**

Computation, storage, automation, AI generation, inheritance and repeated use are not authority roots by themselves.

## 22. D0.19 — Interim Governance

Until `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1` is released, no work can hold v1-governed status.

All new work is **PRE-CONTRACT** and shall carry that label in its outputs and manifests.

Work may continue.

PRE-CONTRACT work shall not describe itself as governed, qualified or authoritative under LOOM governance.

Phase 0 principles are the standard against which PRE-CONTRACT work is later qualified, and a violation is a finding under §26.

The §34 sequence is a plan for the work, and a gate only on governed status.

If PRE-CONTRACT work is later consumed by governed work, it must satisfy applicable qualification requirements like any other pre-contract artifact.

Historical qualification labels remain historical provenance and do not automatically satisfy v1.

There is no grandfathering window between Phase 0 and v1.

## 23. D0.20 — Single-Authority Disclosure Pending Governance Design

Where the same person both authors a claim and consumes it, independence requires a second person.

Until a second authorizer is named, such claims and any result depending on them carry `SINGLE-AUTHORITY`.

The label discloses a governance limitation; does not invalidate the underlying claim merely by existing; does not constitute independent review; cannot be silently removed; propagates to dependent standing where independence is required; and is resolved only through recorded independent authorization.

No second authorizer is appointed during Phase 0 merely to manufacture procedural independence.

Before Phase 2 begins, LOOM must either establish the second-authorizer mechanism or explicitly decide which Phase 2 activities may proceed under `SINGLE-AUTHORITY`.

## 24. Meaning Is Part of the Claim

Where applicable, claim meaning includes units, physical dimensions, currency, currency basis/base year, entity identity, temporal identity, identifier mappings, unit conversions and ontology mappings.

Mappings and crosswalks are themselves claims and therefore require provenance, authority and applicable scope.

A transformation joining two claims through an incorrect identity mapping has not preserved authority merely because both source claims were individually qualified.

Physical-law implementations and mathematical transformations are subject to dependency standing and qualification even where Phase 1 establishes that their authority root differs from ordinary empirical evidence.

## 25. Scope Has Multiple Dimensions

Phase 0 distinguishes:

- **Contract scope:** which LOOM work the governance contract applies to.
- **Evidentiary extent:** the population, entity, location, sample or other domain over which a claim is warranted.
- **Temporal validity:** when the claim applies.
- **Knowledge time:** when information became available to the modeled or governing system.
- **Intended use:** purposes for which the claim has been qualified.

Extending a claim beyond evidentiary or temporal extent is an inference and requires authority.

A simulation must not permit information unavailable at modeled time `t` to influence an actor at `t` merely because the information exists in the modern database.

## 26. Architecture Must Not Weaken the Principles

Later architecture should be informed by what Phase 1 discovers. That does **not** permit existing artifacts to redefine Phase 0 principles.

If archaeology discovers an existing artifact conflates unknown and zero, lacks provenance, mixes scenario and evidence, lacks unit semantics, cannot reproduce its derivation, or violates another Phase 0 principle, that is a finding about the artifact.

The artifact may subsequently be qualified, qualified with limitations, remediated, quarantined, excluded or superseded depending on later governance.

Its non-compliance is not evidence that the principle should be weakened.

Established Phase 0 distinctions may be refined. They may not be silently merged. Changing a Phase 0 principle requires governed amendment under D0.14 and human approval.

## 27. Judgment, Materiality and Independence

Terms requiring judgment, including material, sufficient, independent, applicable, representative and relevant, do not grant implicit discretion to an implementer.

Authorization of a judgment may take the form of an approved criterion stating the term it governs, the conditions under which it applies and the evidence it requires. Applying an approved criterion without discretion is not itself a governance act. Each application shall be recorded with the criterion and version applied.

Where no approved criterion covers a judgment affecting authority, qualification or governed status, the dependent operation blocks. Human authorization of an individual application is required only where the criterion calls for discretion.

For Phase 0, **independent** means independent of both the consumer requiring the claim or value and the author or process whose claim is being independently justified.

Where one person both authors a claim and consumes it, independence requires a second person. Until a second authorizer is named, such claims and any result depending on them carry `SINGLE-AUTHORITY`. The label discloses the limit and does not remove it.

## 28. Established Phase 0 Distinctions

Phase 0 does **not** establish a complete epistemic taxonomy. It **does** establish binding distinctions:

- UNKNOWN vs known
- OBSERVED/empirical warrant vs SIMULATED
- PROJECTION vs SCENARIO_ASSUMPTION
- REFERENCE vs REALIZED
- authority vs authorization
- provenance vs authority
- qualification vs truth
- standing vs truth
- replay vs audit
- governed vs non-governed
- PRE-CONTRACT vs v1-governed
- independent vs SINGLE-AUTHORITY

Later phases may refine these distinctions. They may not silently merge distinctions established by Phase 0.

## 29. Explicit Non-Decisions

Phase 0 does not select a complete epistemic taxonomy; UNKNOWN subtypes; an L0-L5 or other layer architecture; runtime snapshot implementation; PostgreSQL, SQLite, Git, YAML or JSON as universal authority representation; canonical agent representation; Earth reference-plus-delta architecture; Earth/CIVPROP coupling mechanics; final qualification vocabulary; domain-specific qualification gates; CIVPROP decision/budget/diffusion/commitment behavior; bitwise determinism; a delegation hierarchy; coverage thresholds; uncertainty mathematics; a lineage/ledger schema; or the complete set of authority-root types.

Until delegation is designed, delegation remains default-deny.

## 30. Phase 1 Archaeology Questions

Phase 1 must establish from actual LOOM holdings:

1. What artifacts supply Earth information?
2. What artifacts supply technology/scenario information?
3. What artifacts supply Solar information?
4. What artifacts define actors?
5. What relevant sources exist outside those domains?
6. Where do physical-law and transport authorities reside?
7. What institutional/governance rules exist?
8. What model parameters exist explicitly or implicitly?
9. Which artifacts carry provenance?
10. Which carry qualification or promotion status?
11. Which distinguish observation from projection?
12. Which distinguish unknown from zero/absence?
13. Which contain uncertainty?
14. Which distinguish candidate from promoted information?
15. Which mix simulated and reference information?
16. What consumes each artifact?
17. What transformations create derived claims?
18. What qualification mechanisms exist?
19. Which identifiers/vocabularies are shared?
20. Which are incompatible?
21. Which artifacts rely on authority by convention?
22. Which apparent authorities cannot be located?
23. Which claims depend on undocumented assumptions?
24. Which artifacts are mutable?
25. Which outputs cannot presently be causally reproduced?
26. Which artifacts were produced, modified or classified by AI or automation, and what record exists?
27. What explicit human approvals exist for assumptions, parameters, promotions or classifications?
28. Which pipelines contain fallback, imputation, interpolation, clamping, default or null-coalescing logic, and what values did they produce?
29. For every relevant quantity, are unit, currency and base year explicit or implied?
30. Which artifacts carry as-of/knowledge-time information?
31. Which identifier crosswalks exist, who authored them and how were they checked?
32. Do downstream outputs feed back into upstream inputs, calibration or parameter choices?
33. Which parameters were fitted, to what, and were they later validated against the same target?
34. Which code versions produced derived artifacts, and can those versions be recovered?
35. Which tests, gates or validation reports exist, and what do they not cover?
36. Where do conflicting claims already exist, and how were they resolved?
37. Which joins, filters and aggregations drop unknown/null rows?
38. Do existing holdings expose authority-root types not covered by D0.18?
39. Where are physical-law or mathematical outputs treated as authority, and on what basis?
40. Which artifacts contain temporal leakage, where later knowledge can affect earlier modeled state?

Every answer must be classified as `ESTABLISHED`, `NOT LOCATED` or `NOT ESTABLISHED`.

An `ESTABLISHED` answer requires identifiable supporting evidence. Archaeological classifications are candidates until human acceptance.

## 31. First Hostile Review Disposition

The owner accepts the following dispositions:

| Finding | Disposition | Revision 3 treatment |
|---|---|---|
| F-01 | AMEND | D0.18 explicit but extensible authority roots; D0.8 human authorization |
| F-02 | AMEND | D0.4 computed standing; D0.5 governed ancestry |
| F-03 | AMEND | D0.3 SHALL block; UNKNOWN escape routes closed |
| F-04 | AMEND | BLOCKED outcomes, coupling and coverage |
| F-05 | AMEND | Class changes governed; model-output adoption explicit |
| F-06 | AMEND | §25 separates scope dimensions and knowledge time |
| F-07 | AMEND | Claim defined; inheritance obligations established |
| F-08 | AMEND | §27 governs judgment criteria |
| F-09 | AMEND | Delegation default-deny; fitting and outcome-conditioning governed |
| F-10 | AMEND | Conflict rules scoped, versioned and prospective |
| F-11 | AMEND | Replay and audit separated |
| F-12 | AMEND | D0.19 PRE-CONTRACT rule |
| F-13 | AMEND | §24 units, identity and mappings |
| F-14 | AMEND | §26 prevents evidence from weakening principles |
| F-15 | AMEND | §2 vocabulary |
| F-16 | AMEND | §28 lists established distinctions |
| F-17 | AMEND | Simulation variability separated from epistemic uncertainty |
| F-18 | AMEND | Contract defects recorded without historical rewriting |
| F-19 | AMEND | Premature qualification pseudo-schema removed |
| F-20 | AMEND | Consumed/unconsumed failures distinguished |
| F-21 | AMEND | Review adjudication and stopping rule |
| F-22 | AMEND | D0.1–D0.20 explicitly represented |
| N-1 | DEFER TO PHASE 1 | Archaeology Q6, Q7, Q38, Q39 |
| N-2 | DEFER TO LATER PHASE | Successor/co-owner governance |
| N-3 | ACCEPT | Exact reference version required |
| N-4 | ACCEPT | Independent second hostile review required |

Dispositions in this section, and any text in this document not authored directly by the owner, are CANDIDATE until the owner records acceptance under D0.8. The record names the accepting human, date and sections accepted. A section without such a record has no authority.

The Owner Acceptance Record below supplies that acceptance for this Revision 3.

## 32. Review Adjudication and Stopping Rule

1. The owner records each hostile-review finding as `ACCEPT`, `AMEND`, `REJECT` or `DEFER`.
2. `AMEND` and `REJECT` require rationale.
3. Critical findings must be resolved before Phase 0 closes.
4. Revision 3 receives one additional hostile review from a reviewer that did not materially shape the architecture or questions leading to this document.
5. That review is the final planned hostile-review round for Phase 0 unless it discovers a new `CRITICAL` contradiction.
6. A new critical finding requires remediation and one targeted re-review of the amended area.
7. Minor disagreement alone does not create an endless review loop.
8. Dispositions in §31, and any text in this document not authored directly by the owner, are CANDIDATE until the owner records acceptance under D0.8. The record names the accepting human, the date and the sections accepted. A section without such a record has no authority.

## 33. Phase 0 Exit Criteria

Phase 0 closes when:

1. the authority problem is stated independently of implementation;
2. contract scope is established;
3. integrity requirements are established;
4. authority has an explicit root requirement;
5. computed-claim standing is constrained;
6. unknowns cannot silently disappear;
7. reference and realized state are separated;
8. projection and scenario are distinguished;
9. human authorization boundaries are explicit;
10. interim governance prevents grandfathering;
11. architecture cannot weaken principles merely to accommodate existing artifacts;
12. unresolved empirical questions are assigned to Phase 1;
13. all first-review findings have recorded owner adjudication;
14. all hostile-review critical findings are resolved;
15. the second independent hostile review has been adjudicated;
16. no unresolved critical contradiction remains;
17. Revision 3 or its successor has an explicit owner acceptance record.

Phase 0 completion does **not** qualify existing LOOM holdings. It authorizes archaeology.

## 34. Phase 1 Boundary

Phase 1 is **LOOM Authority Archaeology and Source Inventory**.

It is descriptive. It must inspect actual holdings. It may identify defects. It may not silently repair them. It may propose classifications, mappings and authority roots. Those proposals remain candidates until governed human acceptance.

Missing evidence is recorded as missing. Memory does not substitute for archaeology.

Planned sequence:

```text
PHASE 0
Authority Constitution
        ↓
PHASE 1
Authority Archaeology
        ↓
Claim / Authority Model
        ↓
State Model
        ↓
Runtime Boundary
        ↓
Qualification Framework
        ↓
LOOM Authority and State Contract v1
        ↓
Qualified Inputs
        ↓
CIVPROP FRD / DLD
        ↓
Agent Engine
```

This sequence is a work plan, not a prohibition on PRE-CONTRACT exploratory work. It is a gate on governed status.

The evidence informs later architecture.

**The principles constrain what architectures are permissible.**

Those statements are intentionally different.

---

# Owner Acceptance Record

**Artifact:** `00_AUTHORITY_PROBLEM_STATEMENT.md`, Revision 3  
**Owner:** @kT  
**Acceptance date:** 2026-10-03  
**Accepted scope:** D0.1–D0.20, §§1–34, and dispositions F-01–F-22 and N-1–N-4.

> I accept `00_AUTHORITY_PROBLEM_STATEMENT.md`, Revision 3, including D0.1–D0.20, §§1–34, and the proposed dispositions of F-01–F-22 and N-1–N-4, as the Phase 0 candidate authority statement to be submitted for independent hostile review. This acceptance establishes the document as owner-authorized Phase 0 governance but does not close Phase 0, qualify existing LOOM holdings, or release `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1`.

## Independent Hostile Review and Phase 0 Closure

**Review status:** COMPLETED AND OWNER ACCEPTED  
**Closure date:** 2026-10-03  
**Owner:** @kT

The owner records that the required independent hostile review of Revision 3 was completed and accepted. No unresolved critical contradiction remains from that review.

All Phase 0 exit criteria in §33 are therefore recorded as satisfied.

**PHASE 0: CLOSED.**

Phase 0 closure does **not** qualify existing LOOM holdings and does **not** release `LOOM_AUTHORITY_AND_STATE_CONTRACT_v1`.

The authorized next phase is **Phase 1 — LOOM Authority Archaeology and Source Inventory**. New work remains PRE-CONTRACT under D0.19 until the v1 contract is released and applicable qualification is completed.
