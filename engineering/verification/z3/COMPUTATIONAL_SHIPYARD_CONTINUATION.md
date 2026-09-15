# LOOM Computational Shipyard — Z3 continuation checkpoint

Status: ENGINEERING WORKING NOTE / NON-CANON / NON-CERTIFICATION
Checkpoint base: main at `f4976aa4a5e9a53e7a27f017d55418fa39ff36d1` (merged PR #230)

## Earned capability

The first Computational Shipyard slice is merged and independently Pixel-qualified. The current formal layer can:

- enforce current Wayfarer mass/inventory identities;
- enforce the four-tank / four-longeron / four-radiator / one-primary-torch structural grammar used by the current engineering layer;
- check an explicitly candidate dry-mass ledger without promoting it to canon;
- check the explicitly candidate aft shield/reactor/nozzle axial packaging envelope;
- reason over launch, radiator, torch and high-metric operating states;
- preserve the recovered torch/high-metric exclusion;
- synthesize a satisfying integrated configuration;
- reject hostile integrated state combinations and candidate-ledger overruns with named UNSAT cores;
- execute through native Z3 and the governed Pixel qualification path.

## Important implementation lessons preserved

1. Generated/shared exact data should replace duplicated hand-authored numeric truth where possible.
2. Python calculates physical quantities; Z3 verifies discrete/configuration relationships and exact algebraic identities.
3. Native Z3 process exit status is authoritative for solver execution health; the appearance of `sat` in partial output is insufficient.
4. Zero-arity SMT `define-fun` declarations are constants and must be referenced without function-application parentheses.
5. Hostile proofs that request UNSAT cores must enable `:produce-unsat-cores true` before `check-sat`.
6. Candidate packaging/mass values remain candidate verification inputs and do not become canon or hardware certification because Z3 can satisfy them.

## Next Shipyard increment — intentionally deferred

Resume from this checkpoint by moving from **configuration checking** to **bounded configuration synthesis**.

Recommended scope:

- central typed/Python source for candidate subsystem choices and authority labels;
- generated SMT configuration vocabulary rather than duplicated numeric/configuration truth;
- Z3-selected subsystem presence/variant, bounded mass allocations, axial placement and operating state;
- protected 50 t water excluded from normal torch remass consumption;
- required subsystem presence and mutually exclusive operating states;
- explicit OPEN/HELD/CERTIFIED/FROZEN authority/status vocabulary without allowing Z3 to manufacture certification;
- RCS integration holds and primary-source realizability hold represented as unresolved requirements;
- SAT candidate configuration output plus hostile impossible-configuration UNSAT cores;
- structured machine-readable verification report rather than grep-only result inspection;
- Python independent evaluation of any Z3-proposed candidate before qualification.

Do not add nonlinear trajectory integration, rocket-log equations, continuous optimization, invented efficiencies, invented component masses, or unearned physical closure merely to make the SMT problem solvable.

## Re-entry rule

Before resuming, bootstrap from live GitHub authority. Main may have advanced. Re-read current governance/workstate, scoped `engineering/AGENTS.md`, current Wayfarer candidate/current specification, and the merged `engineering/verification/z3/wayfarer_shipyard_*` artifacts. GitHub outranks this checkpoint.
