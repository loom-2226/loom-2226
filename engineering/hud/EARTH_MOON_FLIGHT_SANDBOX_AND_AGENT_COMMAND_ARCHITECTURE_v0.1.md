# Earth-Moon Flight Sandbox + Agent Command Architecture v0.1

Status: ACTIVE WORK PLAN / NON-CANON / QUALIFICATION ONLY

## Goal
Use the Earth-Moon HUD as the proving ground for one deterministic flight system that can be operated at multiple abstraction levels without creating separate realities for human and agent pilots.

## Governing rule
Humans and agents may propose commands. Only deterministic flight-control and physics systems may move the universe.

`intent -> maneuver plan -> deterministic command executor -> physics -> new authoritative vehicle state`

The HUD is a human interface to this stack. An LLM is a cognitive/crew interface to the same stack. Neither owns physics.

## Shared command surface
Manual pilot input, Navigator output, LLM-generated plans, NPC pilots and scripted/system behavior must converge on the same typed flight-command contract. Command origin is provenance only and never grants execution authority.

Initial command vocabulary:
- COAST
- TORCH_BURN
- ROTATE_TO_VECTOR
- HOLD_ATTITUDE

Future commands are admitted only when the underlying control/physics capability exists.

## LLM interface direction
Keep an embedded crew/command channel in the HUD architecture, preferably a collapsible bottom drawer on mobile. It may:
- inspect current deterministic ship/world state;
- translate natural-language intent into typed maneuver-plan requests;
- explain returned deterministic plans;
- propose constraints/modifications;
- request explicit execution.

It may not:
- directly mutate physics state;
- pulse actuators at control-loop frequency;
- invent sensor certainty, trajectory state, thermal margin, remass or actuator capability;
- silently convert prose into thrust.

Expected interaction pattern:
`PLAYER/CREW INTENT -> LLM interpretation -> typed request -> Navigator/planner -> typed maneuver plan -> REVIEW/EXECUTE/MODIFY/TAKE MANUAL -> deterministic executor`

## Sandbox growth path
1. Earth-centered orbital diagnostics and persistent qualification state.
2. Seed/enter physically meaningful Earth orbit and coast under gravity.
3. Deterministic maneuver execution against the same integrator used for preview.
4. Manual attitude/thrust controls that emit the shared command vocabulary.
5. One Earth-orbit station with real orbital state; rendezvous/phasing/velocity-match.
6. Navigator-generated plan using the same commands as manual flight.
7. Embedded LLM command drawer over typed requests/plans.
8. Lunar orbit/stations, multiple spacecraft, proximity ops and docking.
9. Failures/damage/sensors/thermal constraints and agent replanning from actual state.

## Current increment
This branch introduces:
- `LOOM_FLIGHT_COMMAND_V1` and `LOOM_MANEUVER_PLAN_V1` contracts;
- explicit MANUAL / LLM / NPC / SYSTEM provenance with identical execution authority;
- Earth-centered osculating orbital diagnostics (`LOOM_HUD_ORBITAL_STATE_V1`).

No maneuver execution boundary is opened by this increment. No campaign state or canon is mutated.
