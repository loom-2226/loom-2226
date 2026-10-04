# Build 5 Implementation Authorization 002 — Public Institutional Explorer Test 002A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “let's build NASA”  
**Normative runtime identity:** generic `PUBLIC_INSTITUTIONAL_AGENT`  
**Design shorthand only:** “NASA-like”

## 1. Authorized purpose

Implement the smallest FRD-aligned autonomous public-institutional exploration slice needed to demonstrate that a public Agent can decide whether to acquire information without access to hidden scenario truth.

The authorized causal slice is:

`DecisionSnapshot -> public exploration policy -> ExplorationDecision -> scheduled funding/expenditure -> WORLD_SIM observation -> Agent information/belief update`.

## 2. Authorized Agent semantics

The bounded Agent may use only admitted Agent-visible state, including:

- public institutional Agent identity;
- finite account balance;
- declared capabilities;
- declared objectives;
- admitted exploration opportunity/cost facts;
- existing Agent information and beliefs.

The first policy may authorize, decline, defer, or block a REMOTE observation opportunity.

The first rule is intentionally parameter-light. It may require the declared `PUBLIC_INFORMATION` objective, `EXPLORE` capability, known cost, and sufficient admitted budget. It shall not introduce an empirically styled hurdle rate or other consequential numeric behavioral baseline merely to make the fixture decide.

## 3. World-side observation boundary

The Agent shall not receive:

- hidden resource truth;
- scenario resource registry;
- universe identity;
- world seed/random stream;
- kernel or scheduler;
- world observation draw.

If the Agent authorizes exploration, a later WORLD_SIM/SYSTEM transition may:

- validate the action;
- fund the public exploration project through ledgered transitions;
- spend the declared exploration cost;
- consult hidden scenario truth;
- generate an imperfect keyed observation using explicit synthetic fixture likelihoods;
- deliver only the resulting observation to the Agent;
- update Agent information/belief through the governed observation mechanism.

Exploration changes information, not physical resource truth.

## 4. Explicitly outside Test 002A

Not authorized by this slice:

- literal NASA institutional data/calibration;
- real mission/instrument fidelity;
- surface-prospecting physics;
- autonomous sponsor/operator behavior;
- autonomous mining/extraction;
- publication to other Agents;
- autonomous financier changes;
- empirical observation-model calibration;
- production forecasting;
- settlement behavior;
- runtime LLM authority.

Publication/information sharing to the financier is a later bounded step.

## 5. Structural pass condition

Test 002A may be considered structurally successful only if:

1. identical admitted public-Agent state produces identical exploration decisions across hidden NULL/RICH world states before observation;
2. the policy cannot access hidden world state, clock, environment, filesystem, network, or system randomness;
3. known affordable REMOTE exploration can be authorized;
4. insufficient budget or missing capability/objective can produce a non-authorizing decision;
5. required UNKNOWN admitted inputs block rather than silently become values;
6. the Agent decision itself does not mutate world state;
7. exploration expenditure and observation occur only in later scheduled SYSTEM transitions;
8. the observation is generated from hidden world state plus declared keyed synthetic observation-model inputs;
9. the Agent receives the observation, not hidden truth;
10. the resulting Agent information/belief may diverge only after the distinguishing observation;
11. accounting/conservation and scheduled-runtime invariants survive the integrated transition;
12. deterministic replay is preserved.

## 6. Epistemic standing

Synthetic Test 002A costs and observation-model likelihoods are fixture inputs only.

They are not empirical calibration, policy baselines, forecast inputs, or claims about NASA or any real institution.

This authorization permits implementation of the bounded autonomous public exploration mechanism only.
