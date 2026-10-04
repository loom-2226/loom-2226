# Build 5 Validation Record 007 — Surface Prospecting Test 007A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-surface-prospecting`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_007_SURFACE_PROSPECTING_TEST007A.md`  
**Executable anchor:** `f802487b441cf379f0914a75ca34155a47adda10`

## 1. Result

Build 5 now implements the FRD §16 higher-quality SURFACE prospecting path as second-stage information acquisition by the existing public institutional Agent.

The verified causal slice is:

`REMOTE observation -> public Agent information/belief -> autonomous SURFACE decision -> scheduled funding/expenditure -> WORLD_SIM SURFACE observation -> separate Agent-side Bayesian belief update`.

Surface prospecting changes information and economic state only.

It does not change hidden or realized resource quantity.

## 2. Generic Agent architecture preserved

The same generic public `AGENT` used by Test 002A performs Test 007A.

No surface-prospecting Agent class or separate agent engine was introduced.

The second bounded policy is:

`PUBLIC_SURFACE_PROSPECTOR_V1`

Policy semantic version:

`0.1`

Policy contract SHA-256:

`7829ee528a61a2c8c146b73f319ab85cbf95a6865ec634b0c1e60ef3384afae0`

Policy version:

`PUBLIC_SURFACE_PROSPECTOR_V1:0.1:8bdb9d5c0048de2f6e35f003825e17092831fc4d954d3ab79259a6f512057dbd`

## 3. Exploration request compatibility

The existing `ExplorationRequest` remains the common request artifact.

The contract now carries an optional prerequisite-observation reference.

Channel-specific fact contracts are:

- REMOTE -> `exploration.REMOTE_COST`;
- SURFACE -> `exploration.SURFACE_COST`.

REMOTE requests remain legal without a prerequisite observation.

SURFACE requests require one.

This extends rather than replaces the Test 002A exploration request architecture.

## 4. Surface policy semantics

The surface policy introduces no consequential numeric behavioral threshold.

It authorizes SURFACE prospecting only when:

- Agent kind = `PUBLIC`;
- objective contains `PUBLIC_INFORMATION`;
- capabilities include `EXPLORE` and `SURFACE_PROSPECT`;
- the referenced prior observation appears in the Agent's admitted information;
- SURFACE cost is KNOWN;
- available public funds cover that cost.

Otherwise the policy returns an explicit DEFER, DECLINE or BLOCKED_UNKNOWN result.

The policy does not receive hidden resource state, world random state, scenario identity or sensor-generation parameters.

## 5. World-side prerequisite validation

Policy possession of an observation reference is not treated as sufficient world authority.

Before SURFACE execution the SYSTEM/WORLD_SIM boundary additionally verifies that the prerequisite observation:

- exists;
- is possessed by the public Agent;
- has channel `REMOTE`;
- concerns the same resource.

Focused hostile tests reject:

- unpossessed observations;
- SURFACE observations masquerading as REMOTE prerequisites;
- REMOTE observations of the wrong resource.

All are rejected before exploration spending occurs.

## 6. Surface observation model

Model id:

`SURFACE_PRESENCE_MODEL_TEST007A_V1`

Model SHA-256:

`b7e0fd44b2e608c17b3dd08eb3648450ae56233e32cb1e58c7e2e0a70271f7a7`

Epistemic standing:

`TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE`

Structural WORLD_SIM rates:

- REMOTE false-positive reference = `0.20`;
- REMOTE false-negative reference = `0.20`;
- SURFACE false-positive = `0.05`;
- SURFACE false-negative = `0.05`.

Thus the declared Test 007A surface model is structurally higher quality than the Test 002A remote model on both error dimensions.

These are synthetic validation values, not empirical sensor-performance claims.

## 7. World-side and Agent-side parameters remain distinct

The surface model preserves separate informational roles.

WORLD_SIM generation fields are:

- world false-positive rate;
- world false-negative rate;
- deterministic keyed draw.

Agent-side belief fields are:

- detection rate;
- false-positive rate;
- prior belief.

The Test-only Agent-side likelihoods are:

- detection rate = `0.95`;
- false-positive rate = `0.05`.

Even where values correspond numerically to world-side complements/rates, they remain separately named and separately consumed.

WORLD_SIM uses hidden truth plus world-side rates to generate the observation.

The Agent-side update uses only the resulting observation signal plus Agent-side likelihoods.

## 8. Surface world record

Each surface execution creates an immutable `SurfaceProspectingWorldRecord` containing:

- year;
- actor;
- resource;
- prerequisite REMOTE observation id;
- resulting SURFACE observation id;
- world model id;
- world false-positive/false-negative rates;
- deterministic keyed draw;
- signal;
- expenditure transaction id;
- exploration-asset id.

This record remains WORLD_SIM provenance.

Its draw and hidden-world parameters are not inserted into the Agent DecisionSnapshot.

## 9. Agent-side belief update record

Each post-observation update creates an immutable `ObservationBeliefUpdateRecord` containing:

- year;
- Agent id;
- observation id;
- belief key;
- prior;
- posterior;
- Agent-side detection rate;
- Agent-side false-positive rate;
- model id;
- source reference;
- causal event id.

The update is Bayesian.

For a positive signal:

`posterior = detection * prior / (detection * prior + false_positive * (1-prior))`.

For a negative signal:

`posterior = (1-detection) * prior / ((1-detection) * prior + (1-false_positive) * (1-prior))`.

No hidden resource state is an input to this update.

## 10. Economic fixture

Test-only costs are:

- REMOTE = `10 MODEL_CURRENCY`;
- SURFACE = `25 MODEL_CURRENCY`.

Initial public funds:

`100`.

After REMOTE spending:

`90`.

After SURFACE spending:

`65`.

Earth supplier cash after both stages:

`35`.

Both stages use existing commitment, disbursement, Earth resource-allocation and exploration-expenditure mechanics.

Each stage creates a separate exploration-WIP asset.

No claim is made that real surface prospecting costs 2.5 times remote sensing.

## 11. RICH confirmation case

Universe:

`RICH_PUBLIC_3`

Hidden resource remaining before and after both exploration stages:

`20`.

### REMOTE stage

Deterministic REMOTE draw:

`0.6480946651064352834453047292`

Signal:

`POSITIVE`

Public-Agent belief:

`0.20 -> 0.50`

REMOTE decision:

`XDEC-467c1aefca719c802b63 / AUTHORIZE`

REMOTE observation:

`obs-000004`

### SURFACE decision

The fresh surface DecisionSnapshot contains:

- resource belief = `0.50`;
- possessed prerequisite observation = `obs-000004`;
- known surface cost = `25`;
- sufficient public budget;
- required capabilities/objective.

Decision:

`XDEC-5a2d7cb894e55ccc76f7`

Outcome:

`AUTHORIZE`

Reason:

`APPROVED_SURFACE_INFORMATION_MISSION`

Authorized cost:

`25`

### SURFACE observation

Deterministic SURFACE draw:

`0.9018843396144714354210718266`

Signal:

`POSITIVE`

SURFACE observation:

`obs-000009`

Surface expenditure transaction:

`tx-000007`

Agent belief update:

`0.50 -> 0.95`

Belief-update event:

`evt-000011`

Hidden resource remains:

`20`.

Thus higher-quality prospecting sharpens Agent belief without changing physical reality.

## 12. NULL false-positive correction case

Pinned structural universe:

`NULL_SURFACE_1`

Hidden resource:

`0`.

This universe was selected before qualification because its deterministic keyed streams satisfy the declared Test-only error models without changing either model after observation.

### REMOTE stage

REMOTE draw:

`0.1668687604247574150957700301`

NULL world REMOTE false-positive threshold:

`0.20`

Therefore:

`0.166868... < 0.20`

and the legitimate REMOTE observation is:

`POSITIVE`.

The public Agent therefore reaches the same admitted pre-SURFACE belief as in RICH:

`0.50`.

### Pre-SURFACE equivalence

Before SURFACE observation, the RICH and NULL cases have identical:

- public-Agent DecisionSnapshot;
- exploration request;
- surface policy decision;
- isolated worker fingerprint.

Both produce:

`XDEC-5a2d7cb894e55ccc76f7 / AUTHORIZE / APPROVED_SURFACE_INFORMATION_MISSION`.

Thus hidden resource truth cannot alter the surface decision when admitted information is identical.

### SURFACE stage

SURFACE draw:

`0.1556196131252563241448988451`

NULL world SURFACE false-positive threshold:

`0.05`

Therefore:

`0.155619... >= 0.05`

and the SURFACE observation is:

`NEGATIVE`.

Agent belief then updates:

`0.50 -> 0.05`.

Hidden resource remains:

`0`.

The earlier REMOTE observation remains unchanged as a legitimate historical false positive.

No scenario truth or prior observation is retrospectively rewritten.

## 13. Higher-quality information semantics

Test 007A does not claim that every surface observation must be correct.

A higher-quality stochastic model can still produce false positives or false negatives.

The earned claim is narrower:

- declared surface error rates are lower than declared remote error rates;
- observation streams are independently keyed by channel;
- a later surface observation can legitimately confirm or overturn earlier evidence;
- Agent belief responds only to admitted observations and Agent-side likelihoods.

## 14. Exploration changes information, not resource state

In both qualification worlds:

- REMOTE spending changes cash, exploration assets, information and belief;
- SURFACE spending changes cash, exploration assets, information and belief;
- hidden/realized resource remaining does not change.

RICH:

`20 -> 20`.

NULL:

`0 -> 0`.

No extraction method is invoked.

## 15. Policy and world separation

The surface policy decision itself does not:

- spend money;
- reserve Earth supply;
- generate an observation;
- update belief;
- mutate resource state.

Later scheduled SYSTEM transitions perform, in order:

1. funding/resource reservation;
2. WORLD_SIM surface observation generation;
3. Agent-side information/belief update.

This preserves request/decision/action separation.

## 16. UNKNOWN behavior

When `exploration.SURFACE_COST` is UNKNOWN:

- outcome = `BLOCKED_UNKNOWN`;
- unknown key = `exploration.SURFACE_COST`;
- policy worker is not invoked;
- no funding or surface observation occurs.

No fallback cost is substituted.

## 17. Budget and capability behavior

If post-REMOTE public funds are below SURFACE cost:

- outcome = `DECLINE`;
- reason = `INSUFFICIENT_BUDGET`.

If `SURFACE_PROSPECT` capability is absent:

- outcome = `DECLINE`;
- reason = `CAPABILITY_OR_OBJECTIVE_BLOCK`.

If the prerequisite observation is not admitted to the Agent:

- outcome = `DEFER`;
- reason = `DEFER_PREREQUISITE_OBSERVATION`.

## 18. Hostile-access isolation

The surface policy executes through the same isolated serialized-input subprocess boundary as the previously qualified Build 5 policies.

The hostile probe exposes no access to:

- kernel;
- scheduler;
- hidden resource registry;
- run/universe identity;
- world seed;
- filesystem;
- network;
- wall clock;
- system randomness;
- environment.

The surface DecisionSnapshot contains no world-side draw or world false-positive/false-negative fields.

## 19. Belief-update hidden-world isolation

A focused test installs the same positive SURFACE observation and same prior `0.50` in a separate NULL kernel.

Using the same Agent-side likelihood model produces the same posterior:

`0.95`.

Therefore the belief-update function depends on observation plus Agent-side likelihoods, not hidden truth.

## 20. Accounting

A1 through A9 pass after both:

- REMOTE epoch;
- SURFACE epoch.

RICH and NULL correction cases both reconcile.

Public spending is explicit and double-sided.

## 21. Decision-epoch chain

Each qualification history uses one persistent kernel and two cryptographically linked epochs.

### RICH

Epoch 1 REMOTE result:

`04ad5f35050f30bd3757b70c65f5d642da7d601db9474a2170c31e573d09166b`

Epoch 2 SURFACE parent:

same Epoch 1 result

Epoch 2 SURFACE result:

`cc2df7274a07cc22250ce1109dc6434767b4ecb5b89a45e286863e9865889759`

### NULL correction

Epoch 1 REMOTE result:

`01ff448c669194459d6830b796633e10e578def61929625c81e2276545a6ad50`

Epoch 2 SURFACE parent:

same Epoch 1 result

Epoch 2 SURFACE result:

`a146e7904ce4b72f31d37b29b94d850e873e88ae50298bcabb58a220b64392b3`

## 22. Deterministic replay

Repeated RICH and NULL qualification chains reproduce:

- remote policy decision;
- remote observation;
- surface policy decision;
- surface world record;
- surface belief-update record;
- decision-epoch records;
- final methodology fingerprint.

Replay is exact.

## 23. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`797bf49e30484c4868c7f2270018e0d511fd6d4f8b99c5e9408b9c10054c658a`

Git-object reconstructed source-tree SHA-256:

`797bf49e30484c4868c7f2270018e0d511fd6d4f8b99c5e9408b9c10054c658a`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 24. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Result at the executable anchor:

**183 tests executed; 183 passed in 53.464 seconds.**

The preceding project-lifecycle baseline contained 169 tests.

Test 007A adds 14 focused surface-prospecting tests.

Legacy Test 002A REMOTE behavior remains regression-green.

## 25. Grade/quantity estimate standing

FRD §16 permits surface prospecting to provide “potentially an estimate of grade or quantity within modeled limits.”

Test 007A deliberately does not invent such a measurement.

The mandatory higher-quality-information capability is now structurally present through the higher-quality SURFACE presence observation.

A grade/quantity estimate remains a possible future extension requiring:

- explicit measurement semantics;
- unit definition;
- uncertainty/error model;
- Agent-side interpretation model;
- provenance and calibration standing.

## 26. Not yet earned

Test 007A does not establish:

- empirical surface-sensor accuracy;
- real NASA instrument behavior;
- grade estimation;
- quantity estimation;
- autonomous sponsor choice to prospect;
- drilling/mining engineering;
- extraction;
- operating economics;
- transport/technology economics;
- settlement effects;
- production forecasting.

## 27. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC EXPLORER REMOTE TEST 002A: STRUCTURAL PASS;
- PUBLICATION / CROSS-AGENT TEST 002B: STRUCTURAL PASS;
- GOVERNED DECISION-EPOCH RUNTIME TEST 004: STRUCTURAL PASS;
- PRIVATE SPONSOR/OPERATOR TEST 005A: STRUCTURAL PASS;
- PROJECT DEVELOPMENT LIFECYCLE TEST 006A: STRUCTURAL PASS;
- SURFACE PROSPECTING TEST 007A: STRUCTURAL PASS;
- SECOND-STAGE REMOTE -> SURFACE INFORMATION ACQUISITION: PASS;
- HIGHER-QUALITY DECLARED SURFACE OBSERVATION MODEL: PASS;
- WORLD/AGENT INFORMATIONAL-PARAMETER SEPARATION: PASS;
- BAYESIAN AGENT-SIDE SURFACE BELIEF UPDATE: PASS;
- NULL REMOTE-FALSE-POSITIVE -> SURFACE-CORRECTION PATH: PASS;
- PRE-SURFACE HIDDEN-WORLD DECISION EQUIVALENCE: PASS;
- EXPLORATION PHYSICAL-NONMUTATION: PASS;
- A1-A9: PASS;
- DETERMINISTIC REPLAY: PASS;
- GRADE/QUANTITY MEASUREMENT: NOT IMPLEMENTED / OPTIONAL UNDER CURRENT FRD WORDING;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
