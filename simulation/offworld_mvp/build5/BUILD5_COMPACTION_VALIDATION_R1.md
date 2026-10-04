# BUILD 5 COMPACTION VALIDATION R1

Status: **PASS / ZERO-FEATURE REFACTOR / BEHAVIOR PRESERVED**

## Authority

Validated Test 012 parent: `4447f068bb25c06d395708d7991e803c5f5c8830`  
Authorization commit: `4b07aa3`  
Candidate executable commit: `0f5d7037a82858fff39df1477307bd614b7df3e7`

The guiding FRD and executable ODD were not modified.

## Change surface

Executable change: `offworld_kernel/policy_runner.py` only.

The refactor replaced repeated contract-policy source loading, contract hashing,
policy-version hashing, decision-ID construction, worker-payload construction, and
blocked-UNKNOWN result construction with private shared helpers. Existing public
runner functions and all policy source files remain in place.

No simulation state, schema, policy contract, Agent behavior, transport behavior,
technology behavior, accounting rule, population rule, or qualification semantics
were added or removed.

The settlement execution paths were reviewed but deliberately not merged. Test 011
performs direct historical aggregate migration; Test 012 performs departure,
in-transit holding, and deterministic arrival. Their repeated checks guard different
state transitions and were retained rather than hidden behind a misleading common
executor.

## Size result

Executable Python LOC (`offworld_kernel/**/*.py`):

- Test 011 parent `768e25e...`: 8,976
- validated Test 012 `4447f06...`: 10,161
- compacted candidate `0f5d703...`: 10,014

Compaction removed a net **147 executable lines** from Test 012, a **1.45%** reduction
of the current runtime package. Net runtime growth from Test 011 is reduced from
1,185 lines to 1,038 lines.

`policy_runner.py` changed from 908 lines to 761 lines.

## Policy identity stability

All nine contract-backed policy contract hashes and policy-version identities were
computed from both the validated Test 012 worktree and the compacted worktree and
matched exactly.

Test 012 transport-settlement identity remains:

`PUBLIC_SETTLEMENT_TRANSPORT_V1:0.1:18e73a25d3e65dd99cc7e671795822c150b567359b592930103f3678debc71ef`

Its contract SHA remains:

`cad5d6416f25aa19b473a2d2d589aa2a898d6043f6ad8ed80042662cf0790b66`

## Cross-branch canonical Test 012 check

The validated Test 012 parent and compacted candidate produced identical semantic
outputs for the canonical RICH passenger-settlement case, including:

- AUTHORIZE / `SETTLEMENT_TRANSPORT_AUTHORIZED`;
- 10 authorized residents;
- support amount 10;
- transport amount 20;
- departure time 12 and arrival time 13;
- Earth population 990, offworld population 10, in-transit population empty;
- total population 1000;
- settlement stage `DEPENDENT_SETTLEMENT`;
- settlement-support balance 10;
- transport-provider balance 20;
- public-funds balance 60;
- 13 decision epoch records;
- distinct support and transport transactions present.

The serialized semantic comparison had an empty diff.

## Focused regression

Command:

`python3 -m unittest tests.test_odd_schema_drift tests.test_build5_settlement tests.test_build5_transport_technology`

Result:

- 45 tests executed
- 45 passed
- 0 failures
- 0 errors
- runtime 216.934 s

## Full governed regression

Command:

`python3 -m unittest discover -s tests`

Executed on candidate executable commit `0f5d7037a82858fff39df1477307bd614b7df3e7`.

Result:

- 287 tests executed
- 287 passed
- 0 failures
- 0 errors
- runtime 508.981 s

## Executable provenance

Filesystem executable source-tree SHA-256:

`d9f62592d47ba70a1ad0f50ca9e714b238550a0675c8ddde9a4d739582937ca8`

Git-object reconstructed executable source-tree SHA-256 at candidate commit:

`d9f62592d47ba70a1ad0f50ca9e714b238550a0675c8ddde9a4d739582937ca8`

Standing: `GIT_OBJECT_VERIFIED`.

## FRD / ODD standing

Diff from validated Test 012 parent:

- guiding FRD: 0 lines
- executable ODD: 0 lines

## Conclusion

Build 5 Compaction R1 passes as a zero-feature refactor. The policy runner is smaller
and future contract-backed policies can reuse common internal plumbing without
replicating the same hashing and worker-envelope machinery. Test 011 and Test 012
state-transition semantics remain distinct and unchanged.

No Test 013 capability is earned by this record.
