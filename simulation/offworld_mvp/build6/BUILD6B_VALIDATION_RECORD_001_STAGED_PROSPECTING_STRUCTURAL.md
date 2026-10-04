# BUILD 6B VALIDATION RECORD 001 — STAGED PROSPECTING / PROJECT-STUDY MATURITY

Status: STRUCTURAL PASS / FRD-CONSISTENT ELABORATION / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED

## Authority

Frozen Build 6A parent tag: build6a-final-v1-2026-10-05
Parent merge commit: 3f1e001fe28a9ee2f08f831f14362177fc9fb8a8
Authorization commit: c710cb6aacd1ccbc72bac72d57413fcdc077792c
Executable/ODD qualification candidate: 7ee1f36db38718a35ef12e53837850291da4ea5e
Branch: offworld-mvp-build6b-staged-prospecting

Authorization:
simulation/offworld_mvp/build6/BUILD6B_IMPLEMENTATION_AUTHORIZATION_001_STAGED_PROSPECTING.md

The guiding FRD is byte-unchanged relative to frozen Build 6A.

## Result

Build 6B Test 001A structurally passes.

Earned causal seam:

candidate study -> finite-capital authorization -> elapsed activity -> real ledger
expenditure -> exploration WIP -> completed study result -> knowledge asset ->
information admission -> sponsor review -> advance / defer / abandon.

Project-study maturity is orthogonal to Project lifecycle. A Project may remain EXPLORING
while study maturity advances.

Structural ladder:

SCREENED -> REMOTE_CHARACTERIZED -> SURFACE_OR_SAMPLE_CHARACTERIZED ->
RESOURCE_ASSESSMENT -> CONCEPT_SCOPING -> PREFEASIBILITY -> FEASIBILITY ->
DEVELOPMENT_READY

Only adjacent declared edges are legal. DEVELOPMENT_READY does not automatically enter
DEVELOPMENT.

## Reuse

Build 6B reuses Build 6A ProjectActivity, finite shared capital reservation, scheduler,
decision epochs, the transaction ledger, OTHER_INVESTMENT, EXPLORATION,
EXPLORATION_WIP, KNOWLEDGE, Earth resource-allocation constraints, the existing
EXPLORING -> ABANDONED transition, the isolated policy worker and existing replay,
tamper and accounting machinery.

The older explore_paid path was internally refactored to reuse a lower-level
spend_exploration_wip primitive. External semantics remain unchanged.

## Study expenditure

At study start the structural fixture executes:

SPONSOR_FUNDS -> PROJECT_CASH -> EARTH SUPPLIER

using existing OTHER_INVESTMENT and EXPLORATION transaction purposes.

Study expenditure reduces sponsor cash, creates exploration WIP, remains attributed to the
project/activity, and is not simultaneously counted as an unspent reservation.

Study spending is sunk. Negative or insufficient findings do not restore cash.

Completed studies become KNOWLEDGE assets even when the result is insufficient or negative.

## Sponsor study-review policy

Policy: SPONSOR_STUDY_REVIEW_V1
Semantic version: 0.1
Policy version:
SPONSOR_STUDY_REVIEW_V1:0.1:cfbaf739e6118c788590fa498ef325d18d13bd4cdbae9ef4d7e4545a07114c98

Contract SHA-256:
847781ccc9b2a027ec753ebfb8e7201e7c68c54558288ed9f1e2222399539623

Standing: TEST_ONLY / NOT_POLICY_BASELINE / NOT_EMPIRICALLY_VALIDATED.

Required admitted facts:

- project.STATUS
- study.CURRENT_MATURITY
- study.ACTIVITY_ID
- study.RESULT_REF
- study.RESULT_STANDING
- study.NEXT_MATURITY

Structural rule:

- SUPPORTS_ADVANCE -> ADVANCE
- INSUFFICIENT -> DEFER
- NEGATIVE -> ABANDON
- UNKNOWN required input -> BLOCKED_UNKNOWN before worker execution

No hidden resource truth, future result, unadmitted economics or Technology Timeline state
enters the policy.

## Execution boundary

SYSTEM execution independently verifies request/decision/activity/plan/result lineage,
sponsor review capability, project/activity state, completion, result admission, exact
predecessor maturity, exact adjacent maturity edge, result standing against decision outcome,
and duplicate-review prohibition.

A forged ADVANCE against a NEGATIVE result is rejected. A later-stage study cannot be
authorized before its predecessor maturity is earned.

## Canonical three-project history

Initial sponsor cash: 150.

P-A, P-B and P-C begin EXPLORING / SCREENED.

ACT-B-WAIT reserves 80 for a future-window study. ACT-A-REMOTE then spends 30. Sponsor
cash becomes 120 while B's unspent reservation leaves only 40 available.

ACT-C-REMOTE requires 50 and therefore returns DEFER /
INSUFFICIENT_AVAILABLE_CAPITAL.

The unspent B plan is canceled before start. Its reservation releases without creating cash,
making C affordable.

Project A spends 30 on remote characterization, 25 on surface/sample characterization and
20 on resource assessment. Each admitted result supports advancement. Terminal A remains
EXPLORING at RESOURCE_ASSESSMENT.

Project C spends 50. Its completed result is INSUFFICIENT. Review returns DEFER.
Terminal C remains EXPLORING / SCREENED. The 50 remains spent and the work remains
knowledge.

Project B later executes a redesigned 20 study. Its admitted result is NEGATIVE. Review
returns ABANDON and reuses the existing EXPLORING -> ABANDONED transition. The 20
remains spent.

## Terminal accounting

Decision epochs: 23
Economic transactions: 10
Study expenditure: 145
Sponsor cash: 150 -> 5
Supplier cash: 0 -> 145
Available sponsor capital: 5
Knowledge-asset book value: 145

Five completed paid studies remain knowledge assets.

No cash is manufactured by cancellation, deferral, negative evidence or abandonment.

## Hostile coverage

Ten Build 6B cases verify:

1. staged spending, maturity progression, insufficiency, negative abandonment and replay;
2. non-adjacent maturity plans are rejected;
3. later-stage authorization is rejected before predecessor maturity;
4. duplicate study spending is rejected through the governed scheduler;
5. UNKNOWN review input blocks before worker execution;
6. result information is absent before completion/admission;
7. duplicate review is rejected;
8. forged ADVANCE against NEGATIVE is rejected;
9. raw study-maturity tampering is detected;
10. the review policy passes source-safety and stable identity checks.

## Focused qualification

Command:
python3 -m unittest tests.test_odd_schema_drift tests.test_build6a_temporal_multiproject tests.test_build6b_staged_prospecting

Result: 20/20 passed in 31.160 s.

## Broader regression

Command:
python3 -m unittest tests.test_build3 tests.test_accounting_edges tests.test_accounting_property tests.test_scheduler tests.test_scheduled_runtime tests.test_policy_firewall tests.test_build5_policy_runner tests.test_build5_decision_epochs tests.test_build6a_temporal_multiproject tests.test_build6b_staged_prospecting tests.test_odd_schema_drift

Result: 68/68 passed in 47.990 s; wall 48.26 s.

## Full governed regression

Command:
python3 -m unittest discover -s tests

Executed on 7ee1f36db38718a35ef12e53837850291da4ea5e.

Result:

- 329 tests
- 329 passed
- 0 failures
- 0 errors
- runtime 647.894 s
- wall time 648.29 s

All 319 Build 6A baseline tests remain present and pass. Build 6B adds ten tests.

## Executable provenance

Filesystem source-tree SHA-256:
66a59d9d2ada3f8713c520f86872e4f88ce2489d57d007500055965391b85d38

Git-object reconstructed source-tree SHA-256:
66a59d9d2ada3f8713c520f86872e4f88ce2489d57d007500055965391b85d38

Standing: GIT_OBJECT_VERIFIED.

## Size / bloat

Executable offworld_kernel Python LOC:

- frozen Build 6A: 11,278
- Build 6B candidate: 12,141
- net: +863 lines (7.65%)

No second scheduler, accounting ledger, Project lifecycle or Agent hierarchy was created.

## FRD / ODD standing

Guiding FRD diff from frozen Build 6A: 0 lines.

Executable ODD registry: ODD_SCHEMA_REGISTRY_0_18.

Build 6B is an elaboration of existing FRD exploration, knowledge, project, capital,
scheduler and epistemic requirements.

## Explicitly not earned

Build 6B does not earn named Solar targets, multiple bodies/resources, multiple economies,
empirical resource inventories, legal JORC/CIM/CRIRSCO standing, calibrated resource
confidence thresholds, calibrated prospecting/PFS/FS costs or durations, endogenous
value-of-information optimization, stochastic delay, SPICE-derived mission opportunities,
development construction, detailed mining/processing engineering, new Agent classes,
endogenous technology/markets, or an empirical 2026-2041 forecast.

## Conclusion

Build 6B structurally earns staged generic information acquisition and project-study
maturity under finite capital and real elapsed time.

Projects can spend money to learn, preserve negative/insufficient work as knowledge, fail to
earn advancement, progress only through declared maturity edges, or be abandoned after
admitted negative evidence. Capital loss and information history persist.

The next expansion question is the FRD gate: whether to activate multiple bodies/resources
for the Moon/Mars/Ceres/Bennu portfolio before introducing the recommended intermediate
multiple-economies rung.
