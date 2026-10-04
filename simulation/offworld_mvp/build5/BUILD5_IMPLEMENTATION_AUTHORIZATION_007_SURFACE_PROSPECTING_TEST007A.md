# Build 5 Implementation Authorization 007 — Surface Prospecting Test 007A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go surface prospecting”  
**Scope:** second-stage public institutional exploration using the existing generic AGENT and exploration architecture

## 1. Authorized purpose

Implement the minimum FRD-aligned SURFACE prospecting path required by §16.

The authorized causal slice is:

`REMOTE observation -> public Agent information/belief -> autonomous SURFACE prospecting decision -> governed funding/expenditure -> WORLD_SIM surface observation -> agent-side information admission/belief update`.

Surface prospecting remains information acquisition.

It shall not extract, deplete, move, reserve or otherwise change the modeled physical resource.

## 2. Existing Agent architecture remains normative

The public institutional explorer remains the same generic `AGENT / PUBLIC` actor.

No surface-prospecting Agent class or separate agent engine is authorized.

A second bounded policy of the same public Agent may decide whether to authorize SURFACE prospecting through:

`AgentState -> immutable DecisionSnapshot -> isolated policy -> ExplorationDecision -> scheduled SYSTEM transitions`.

## 3. Second-stage prerequisite

Test 007A SURFACE prospecting shall require an explicit prior REMOTE observation reference.

The public Agent must legitimately possess that referenced observation.

Before executing SURFACE prospecting, the WORLD_SIM/SYSTEM boundary shall validate that the prerequisite observation:

- exists;
- is possessed by the requesting public Agent;
- concerns the same resource;
- has channel `REMOTE`.

A policy decision alone does not satisfy these world-side validations.

## 4. Bounded policy semantics

The Test 007A surface policy shall introduce no arbitrary probability threshold.

It may authorize SURFACE prospecting only when:

- Agent kind is `PUBLIC`;
- objective includes `PUBLIC_INFORMATION`;
- capabilities include `EXPLORE` and `SURFACE_PROSPECT`;
- a prerequisite REMOTE observation id is supplied and appears in the Agent's admitted information references;
- SURFACE prospecting cost is KNOWN;
- public budget is sufficient.

Otherwise it shall DEFER, DECLINE or BLOCKED_UNKNOWN with explicit reason.

This is a structural public-information mission rule, not an empirical model of NASA or another agency.

## 5. Exploration request compatibility

The existing `ExplorationRequest` shall remain the common exploration request type.

Remote Test 002A compatibility shall be preserved.

The request contract may be extended with an optional prerequisite-observation reference and channel-specific required facts:

- REMOTE requires `exploration.REMOTE_COST`;
- SURFACE requires `exploration.SURFACE_COST`.

Existing REMOTE requests remain legal without a prerequisite observation.

SURFACE requests require one.

## 6. Surface observation model

Test 007A shall use an explicitly versioned synthetic WORLD_SIM observation model that is structurally higher quality than the existing Test 002A REMOTE model.

For the structural fixture only:

- REMOTE world false-positive rate = `0.20`;
- REMOTE world false-negative rate = `0.20`;
- SURFACE world false-positive rate = `0.05`;
- SURFACE world false-negative rate = `0.05`.

These numbers are `TEST_ONLY / NOT_CALIBRATED / NOT_POLICY_BASELINE`.

Higher quality here means the declared false-positive and false-negative rates are strictly lower. It does not mean every stochastic realization must be correct.

## 7. World-side versus Agent-side informational parameters

WORLD_SIM observation-generation parameters and Agent-side belief-update parameters remain distinct even when the structural fixture uses numerically corresponding values.

The surface observation-generation record shall preserve:

- observation id;
- resource id;
- actor id;
- prerequisite remote observation id;
- world observation-model id;
- world false-positive rate;
- world false-negative rate;
- deterministic keyed draw;
- signal;
- expenditure transaction id;
- exploration-asset id.

The public Agent shall not receive the world draw, hidden truth or world likelihood parameters merely because WORLD_SIM used them.

## 8. Agent-side belief update

A separate governed information-update method shall update an Agent belief from an admitted observation using explicitly declared Agent-side likelihood parameters.

For the structural fixture only:

- Agent detection rate = `0.95`;
- Agent false-positive rate = `0.05`.

The update shall be Bayesian and shall consume only:

- prior Agent belief;
- observed signal;
- Agent-side likelihood model.

It shall not query hidden resource state.

An immutable belief-update record shall preserve:

- agent id;
- observation id;
- belief key;
- prior;
- posterior;
- agent-side detection rate;
- agent-side false-positive rate;
- model id;
- source reference.

## 9. Economic treatment

The Test 007A surface cost is a synthetic structural input.

Fixture values:

- REMOTE cost = `10 MODEL_CURRENCY`;
- SURFACE cost = `25 MODEL_CURRENCY`.

SURFACE prospecting is therefore more expensive than REMOTE observation in the fixture, but that relationship is not promoted to an empirical claim.

Funding/expenditure shall use existing commitment, disbursement, Earth resource-allocation and exploration-accounting machinery.

Surface expenditure shall be ledgered and create an exploration WIP/knowledge-candidate asset as existing exploration mechanics allow.

## 10. Structural qualification cases

### RICH confirmation

The same public Agent shall:

1. authorize and execute REMOTE observation;
2. possess the resulting REMOTE observation;
3. in a later decision epoch authorize SURFACE prospecting;
4. pay the declared SURFACE cost;
5. receive a higher-quality SURFACE observation;
6. update belief using Agent-side likelihoods;
7. leave hidden resource quantity unchanged.

### NULL false-positive correction

A pinned NULL structural universe shall be selected before qualification such that:

- REMOTE Test 002A model legitimately produces a false-positive observation;
- SURFACE Test 007A model legitimately produces a negative observation under its independently keyed SURFACE stream.

The surface system shall therefore be capable of correcting misleading earlier information without any retrospective change to the hidden scenario or earlier observation.

The selected universe id and deterministic draws shall be recorded in the validation record.

## 11. Required falsification and guard tests

Test 007A shall demonstrate:

1. SURFACE decision cannot depend on hidden resource state before the surface observation;
2. missing prerequisite REMOTE observation causes no SURFACE execution;
3. an observation not possessed by the actor cannot satisfy the prerequisite;
4. wrong-resource or wrong-channel prerequisite is rejected world-side;
5. UNKNOWN SURFACE cost blocks before worker execution;
6. insufficient budget prevents authorization;
7. missing `SURFACE_PROSPECT` capability prevents authorization;
8. policy hostile-access isolation remains intact;
9. surface observation changes information/belief but not physical resource quantity;
10. world-side draw/model parameters do not enter Agent snapshot;
11. Agent belief update depends only on admitted observation plus Agent-side likelihoods;
12. SURFACE world error rates are strictly lower than REMOTE fixture rates;
13. public expenditure reconciles through A1-A9;
14. deterministic stream/replay behavior remains exact;
15. unrelated REMOTE Test 002A behavior remains regression-compatible.

## 12. Grade/quantity estimate standing

FRD §16 permits surface prospecting to provide “potentially an estimate of grade or quantity within modeled limits.”

Test 007A is authorized to close the mandatory higher-quality-information portion using a higher-quality presence observation.

It shall not invent a grade/quantity measurement model merely to populate an optional field.

A future grade/quantity observation model requires an explicit measurement contract and separately governed uncertainty semantics.

## 13. Explicitly outside scope

Test 007A does not authorize:

- extraction or resource depletion;
- drilling/mining engineering;
- grade or quantity estimation;
- autonomous sponsor prospecting policy;
- sponsor development-policy changes;
- technology/transport economics;
- empirical sensor calibration;
- real NASA instrument claims;
- production forecasting;
- settlement dynamics.

## 14. Epistemic standing

All surface observation rates, Agent likelihoods and costs are synthetic structural fixtures.

Passing Test 007A establishes surface-prospecting information mechanics only.

It does not establish empirical sensor performance, real institutional behavior, calibrated geological inference or forecast validity.
