# Build 5 Validation Record 002 — Public Institutional Explorer Test 002A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-public-institutional-agent`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_002_PUBLIC_EXPLORER_TEST002A.md`  
**Implementation commit:** `90d4e86943c5383ee3878f34553c743dbccfc68c`  
**ODD-aligned executable anchor:** `5fdb042785f7f6f92502e37c95e91831e06530fc`

## 1. Result

The first bounded autonomous public institutional exploration policy is executable and passes its structural, information-firewall, scheduler, accounting, replay and hidden-world separation tests.

The Agent is a generic `PUBLIC_INSTITUTIONAL_AGENT`. “NASA-like” is design shorthand only and carries no claim about NASA policy, calibration, institutional behavior or mission design.

Test 002A closes only the bounded REMOTE information-acquisition decision path.

## 2. Autonomous semantic slice

The verified causal path is:

`DecisionSnapshot -> PUBLIC_EXPLORER_V1 -> ExplorationDecision -> scheduled public funding -> scheduled exploration expenditure -> WORLD_SIM observation -> Agent information/belief update`.

The Agent decision does not mutate world state.

The policy receives no kernel, scheduler, scenario-resource registry, universe identity, world seed, hidden resource state, clock, filesystem, environment or network access.

## 3. Policy identity

Policy:

`PUBLIC_EXPLORER_V1`

Semantic version:

`0.1`

Policy semantics:

`PUBLIC_INFORMATION_ACQUISITION_STRUCTURAL_V1`

Policy contract SHA-256:

`d645af536518d10166074c5d986e5182e2d8dd05b8415cf003f2eff61e04463c`

Policy version:

`PUBLIC_EXPLORER_V1:0.1:d4aeadfbf51b3c851886f7943e7424b3138ece33f205510d593c275533a6cccf`

The policy contract contains no consequential numeric behavioral parameters. It requires only:

- public Agent class;
- `EXPLORE` capability;
- `PUBLIC_INFORMATION` objective;
- `REMOTE` channel;
- admitted known `exploration.REMOTE_COST`.

The policy authorizes a remote observation only when the required mission/capability state is admitted and the known declared cost does not exceed admitted public cash.

## 4. Executable identity

Executable `offworld_kernel` source-tree SHA-256 at the ODD-aligned executable anchor:

`c9c5a9d0147ef11aaa2e2688eed37b52034d89a6fb3d24f8949b87ee76bb57bf`

Git-object reconstructed source-tree SHA-256:

`c9c5a9d0147ef11aaa2e2688eed37b52034d89a6fb3d24f8949b87ee76bb57bf`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 5. Test result

The governed kernel suite is executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Result at the ODD-aligned executable anchor:

**127 tests executed; 127 passed in 9.383 seconds.**

The prior Build 5 baseline contained 117 tests. Test 002A adds 10 focused public-explorer tests.

## 6. Hidden-world equivalence before observation

The Test 002A fixture constructs otherwise identical public-Agent decision state against hidden NULL and RICH scenario resources.

Before observation:

- the two `DecisionSnapshot` objects are identical;
- the two `ExplorationRequest` objects are identical;
- the same decision key is supplied;
- the resulting formal `ExplorationDecision` objects are identical;
- worker fingerprints are identical.

Therefore hidden resource truth does not alter the Agent's pre-observation decision.

## 7. Controlled divergence after observation

After the identical public Agent authorizes REMOTE exploration, the later WORLD_SIM observation transition may inspect hidden scenario resource state and use the declared keyed synthetic observation model.

The deterministic structural fixtures produce:

- RICH fixture `RICH_PUBLIC_3`: POSITIVE observation;
- NULL fixture `NULL_PUBLIC_1`: NEGATIVE observation.

The observation is added to the public Agent's information set. The existing governed observation mechanism updates the Agent's resource belief from the same initial value to different post-observation values:

- RICH/POSITIVE -> `0.50`;
- NULL/NEGATIVE -> `0.05`.

The hidden resource itself is unchanged by exploration.

Thus divergence occurs only after distinguishing information is generated.

## 8. UNKNOWN and non-authorizing branches

The public policy structurally exercises:

- `AUTHORIZE / APPROVED_PUBLIC_INFORMATION_MISSION`;
- `DECLINE / INSUFFICIENT_BUDGET`;
- `DECLINE / CAPABILITY_OR_OBJECTIVE_BLOCK`;
- `BLOCKED_UNKNOWN / BLOCKED_REQUIRED_INPUT_UNKNOWN`.

A missing/UNKNOWN required cost blocks before worker execution. It is not converted to zero or a guessed fallback.

## 9. Scheduler and accounting

For an authorized case, execution order is:

`public-explore-decision -> public-explore-finance -> public-remote-observation`.

The later scheduler phases:

1. create the public exploration commitment;
2. disburse public funds to the exploration project;
3. reserve the declared Earth-supplied expenditure;
4. spend the exploration cost to the supplier;
5. generate the WORLD_SIM observation.

For the nominal cost-10 structural fixture:

- public funds: `100 -> 90`;
- exploration project cash: `0 -> 10 -> 0`;
- Earth supplier: `0 -> 10`.

A1 through A9 all pass after the integrated transition.

## 10. Hostile-access isolation

The isolated subprocess hostile probe reports no leak of:

- world/kernel state;
- scenario resource registry;
- universe/run identity;
- world seed/hidden state;
- wall clock;
- system randomness;
- environment;
- filesystem;
- network.

The public policy uses the same serialized-input isolation boundary already established for Build 5 autonomous policy execution.

## 11. Replay

Repeated integrated RICH runs reproduce:

- the same formal exploration decision;
- the same keyed observation;
- the same observation draw;
- the same final run/result fingerprint.

Deterministic replay remains intact.

## 12. Parameter and empirical standing

The public exploration decision rule introduces no consequential numeric behavioral policy baseline.

The structural fixture still contains synthetic world-side values, including remote observation cost and observation-model false-positive/false-negative rates. Those values are test fixtures only.

They are not:

- calibrated NASA values;
- empirical observation accuracy;
- policy authority;
- production forecast inputs;
- probabilities assigned to scenario universes.

## 13. Not yet earned

Test 002A does not establish:

- surface prospecting;
- publication of observations to another Agent;
- financier response to public information;
- autonomous sponsor/operator behavior;
- empirical observation-model calibration;
- real mission/instrument physics;
- extraction/development autonomy;
- settlement dynamics;
- full MVP success.

## 14. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC INSTITUTIONAL EXPLORER TEST 002A: STRUCTURAL PASS;
- PRE-OBSERVATION HIDDEN-WORLD INDEPENDENCE: PASS;
- WORLD_SIM-GENERATED IMPERFECT OBSERVATION PATH: PASS;
- POST-OBSERVATION BELIEF DIVERGENCE: PASS;
- SCHEDULER-MEDIATED CONSEQUENCE: PASS;
- A1-A9 INTEGRATED ACCOUNTING: PASS;
- DETERMINISTIC REPLAY: PASS;
- EMPIRICAL VALIDATION: UNEARNED;
- SURFACE PROSPECTING: UNEARNED;
- PUBLICATION / CROSS-AGENT INFORMATION TRANSFER: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
