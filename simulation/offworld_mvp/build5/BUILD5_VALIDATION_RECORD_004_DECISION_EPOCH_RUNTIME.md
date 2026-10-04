# Build 5 Validation Record 004 — Governed Decision-Epoch Runtime

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-decision-epochs`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_004_DECISION_EPOCH_RUNTIME.md`  
**Executable anchor:** `e113d4f78d96815ce7a9e207e9e5e9949fc0db9f`

## 1. Result

Build 5 now supports repeated governed autonomous decision cycles over one persistent kernel/world state without relaxing the immutable DecisionSnapshot firewall.

The verified runtime pattern is:

`persistent state -> begin epoch -> fresh scheduler plan -> fresh pinned DecisionSnapshot(s) -> seal -> scheduled decisions/actions/transitions -> immutable run result -> verified epoch completion -> persistent state -> next epoch`.

The first qualification chain executes public observation publication in Epoch 1 and the autonomous financier decision plus financing consequence in Epoch 2 on the same kernel instance.

## 2. Decision-epoch record

Each successfully completed epoch produces a `DecisionEpochRecord` containing:

- chain identity;
- epoch identity;
- ordinal;
- parent epoch result fingerprint;
- scheduler-plan fingerprint;
- initial methodology fingerprint;
- final methodology fingerprint;
- execution fingerprint;
- result fingerprint.

The root epoch has an empty parent result fingerprint. Every later epoch's parent result fingerprint must equal the immediately prior epoch's result fingerprint.

Duplicate epoch identities are rejected.

## 3. Persistent-state boundary

Decision-epoch mode distinguishes persistent world state from scheduler-plan state.

A decision-epoch persistent-state fingerprint includes the methodology/world state and epoch-chain history while excluding the current scheduler plan.

This allows legitimate construction of a fresh scheduler plan between epochs without permitting silent world-state edits.

Once an epoch chain has started:

- governed world mutator methods remain blocked outside scheduled-event context, including between epochs;
- raw state changes between completed epochs are detected before the next epoch opens;
- raw state changes after epoch-open and before seal are detected before execution;
- a new scheduler plan alone does not count as world-state mutation.

## 4. Seal lifecycle

The legacy single sealed `ScheduledSimulationRuntime` behavior remains intact outside decision-epoch mode.

In decision-epoch mode:

1. the epoch is explicitly opened;
2. persistent state is fingerprinted;
3. a fresh scheduler plan and DecisionSnapshot references are configured;
4. seal verifies persistent state has not changed since epoch-open;
5. execution occurs under the existing private scheduler token;
6. plan identity and methodology invariants are rechecked;
7. immutable run result hashes are computed;
8. only then is the epoch recorded and the seal released for preparation of the next epoch.

Failed or tampered epochs do not earn a completed epoch record.

## 5. Existing policy firewall preserved

No policy interface was weakened.

DECISION_WINDOW policies still receive only:

- immutable `DecisionSnapshot`;
- pinned snapshot reference;
- opaque deterministic decision key.

They do not receive:

- kernel;
- scheduler;
- hidden scenario resource state;
- universe/run identity;
- world seed;
- mutable world state.

A stale pre-publication financier snapshot is rejected when registration is attempted in the post-publication epoch because it no longer matches current admitted Agent-visible state.

## 6. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`5e8456213e7e2823335a91e73e0aa3db934766b18b754931562057ac9a1c1044`

Git-object reconstructed source-tree SHA-256:

`5e8456213e7e2823335a91e73e0aa3db934766b18b754931562057ac9a1c1044`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 7. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Result at the executable anchor:

**146 tests executed; 146 passed in 15.176 seconds.**

The prior Test 002B baseline contained 137 tests. Decision-epoch Test 004 adds 9 focused tests.

## 8. Two-epoch RICH qualification chain

Fixture:

`RICH_PUBLIC_3`

Source observation:

`POSITIVE`

After Epoch 1 publication, the financier's fresh Epoch 2 snapshot contains:

`belief(resource_exists) = 0.5`

The existing bounded financier policy produces:

`APPROVE`

The later scheduled financing transition produces:

- financier cash: `100 -> 40`;
- project cash: `0 -> 60`.

### Epoch 1

Epoch id:

`EPOCH-1`

Ordinal:

`1`

Parent result fingerprint:

empty root

Plan fingerprint:

`2c583a4b716f9298ae17cc245ded768a6d04fd572a1ba8cdf014d4e125433373`

Initial fingerprint:

`bac4785b306f824e50086bd5947b5205d897df1cd4c743dca0d05d5e70351e9d`

Final fingerprint:

`526356b74106ae19a67a183b479c4894f58355553898fb083a4105a35cec9a57`

Execution fingerprint:

`72035f0064de63f204e17249bf01d96f28c50e8fa10e03918e1765c8f723b136`

Result fingerprint:

`8ebfc4a03a98695dd7317bfdf03532c6589789dc009414b20b2286ce6cf5f643`

### Epoch 2

Epoch id:

`EPOCH-2`

Ordinal:

`2`

Parent result fingerprint:

`8ebfc4a03a98695dd7317bfdf03532c6589789dc009414b20b2286ce6cf5f643`

Plan fingerprint:

`47dceee4d477aa698134fcfdd1718b773b014ac1920f9a9f2887d64b34763c88`

Initial fingerprint:

`b032962779a7b02f6874a9787899f465e902032f5b1e20f91bbce45ea3905229`

Final fingerprint:

`69677a7a6d3dea7a4830deabfcdd5c01316cd1a8bb60e18b500b06c1cc880d79`

Execution fingerprint:

`f7d68048fd4dc2ffeec33f882887b7aafe8091155c7d47795e7d05efe3166171`

Result fingerprint:

`e4b590da1a31dbb79352199cd3645052297991f7b8767f778d043e0dca3b4c7c`

The Epoch 2 parent link exactly equals the Epoch 1 result fingerprint.

## 9. Two-epoch NULL qualification chain

Fixture:

`NULL_PUBLIC_1`

Source observation:

`NEGATIVE`

Fresh Epoch 2 financier belief:

`0.05882352941176470588235294118`

Financier outcome:

`REJECT`

No financing transition occurs:

- financier cash remains `100`;
- project cash remains `0`.

The NULL chain also records exact parent-linked epoch hashes and replays deterministically.

## 10. Stale snapshot falsification

A financier snapshot created before publication is retained as a hostile stale candidate.

After Epoch 1 publishes information and changes financier information/belief state, Epoch 2 attempts to register that stale snapshot.

Registration fails because the immutable snapshot fingerprint no longer matches current admitted Agent-visible state.

This demonstrates that decision-epoch chaining does not permit reuse of an obsolete epistemic view.

## 11. Between-epoch mutation falsification

After successful Epoch 1 completion, a direct governed mutator call is rejected in decision-epoch chain mode.

A separate hostile test changes account state through raw object access between Epoch 1 and Epoch 2.

The next `begin_decision_epoch` detects persistent-state fingerprint mismatch and refuses to open Epoch 2.

Thus successful epoch completion does not create an ungoverned mutation gap.

## 12. Open-to-seal tamper falsification

After Epoch 2 opens, the scheduler plan is configured legitimately.

A hostile raw account-state mutation is then introduced before seal.

Seal compares current persistent state to the state fingerprint captured at epoch-open and rejects execution.

Thus scheduler configuration is allowed while world-state mutation is not.

## 13. Replay

Repeating the complete RICH two-epoch chain reproduces:

- both `DecisionEpochRecord` objects;
- parent linkage;
- plan fingerprints;
- initial/final fingerprints;
- execution fingerprints;
- result fingerprints;
- final persistent methodology fingerprint;
- financier decision.

Deterministic chained replay is structurally verified.

## 14. What this closes

Test 004 closes the runtime seam identified during Test 002B.

The simulation can now legitimately execute:

`Agent A decision -> scheduled world consequence -> changed persistent state -> fresh Agent B snapshot -> Agent B decision -> later scheduled consequence`

without rebuilding the world as a separate fixture or exposing mutable live state to policy code.

This is the runtime prerequisite for sponsor/operator autonomy, iterative prospecting, development/abandonment choices and longer endogenous histories.

## 15. What is not earned

Test 004 does not establish:

- sponsor/operator autonomy;
- surface prospecting;
- empirical observation or policy calibration;
- transport/technology economics;
- project lifecycle autonomy;
- extraction/sale autonomy;
- settlement dynamics;
- concurrency;
- rollback/recovery;
- asynchronous decision execution;
- runtime LLM agents;
- production forecasting.

The runtime remains deterministic, sequential and explicitly epoch-governed.

## 16. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC EXPLORER TEST 002A: STRUCTURAL PASS;
- PUBLICATION / CROSS-AGENT TEST 002B: STRUCTURAL PASS;
- GOVERNED PERSISTENT DECISION-EPOCH RUNTIME TEST 004: STRUCTURAL PASS;
- FRESH POST-CONSEQUENCE SNAPSHOTS: PASS;
- EPOCH PARENT HASH LINKAGE: PASS;
- BETWEEN-EPOCH MUTATION BLOCK: PASS;
- RAW BETWEEN-EPOCH TAMPER DETECTION: PASS;
- OPEN-TO-SEAL TAMPER DETECTION: PASS;
- STALE SNAPSHOT REJECTION: PASS;
- CHAINED DETERMINISTIC REPLAY: PASS;
- GENERAL AUTONOMOUS-AGENT AUTHORITY: NOT GRANTED;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
