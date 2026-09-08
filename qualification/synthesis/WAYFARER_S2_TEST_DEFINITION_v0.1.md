# LOOM 2226 — Wayfarer S2 Comparison Test Definition v0.1

**Status:** ENGINEERING / RESEARCH — NON-CANON — NON-PRODUCTION

## Purpose

Compare the closed S1 generated Wayfarer candidate against the hand-authored Wayfarer baseline using the same admitted S1 physical model.

## Governing rule

This comparison is apples-to-apples only. It may compare quantities derivable from the common admitted model, including selected transforms, exact mass, CoM, admitted-body centroidal inertia, parallel-axis contributions, aggregate partial tensor, unresolved inertia fraction, hard-constraint outcomes, and visible J1–J7 objective terms.

It may not claim that the hand-authored Wayfarer has a qualified full inertia tensor or that the generated candidate is canon, production authority, or flight-dynamics authority.

## Hand-authored baseline tuple

The baseline comparison tuple is sourced from existing design-baseline transforms and the preserved S1 regression baseline:

- relational_x_m = 26.0
- launch_x_m = 21.8
- tank_x_m = 25.0

The launch transform is directly sourced from the Phase-3 geometry coupling overlay and geometry seed. The tank common station 25.0 m is the preserved hand-authored S1 regression baseline used to prove the solver does not replay the full transform tuple.

## Generated candidate

Use the closed S1 deterministic result for seed 2226.

Expected selected tuple:

- candidate_id = CAND-5719E3F3251DE6E25FDF
- relational_x_m = 26.0
- launch_x_m = 21.75
- tank_x_m = 26.5

## Required comparisons

1. component-position deltas for the three S1 variables;
2. exact mass delta;
3. CoM delta;
4. admitted centroidal tensor delta;
5. parallel-axis tensor delta;
6. aggregate partial tensor delta;
7. unresolved inertia mass-fraction delta;
8. hard-constraint pass/fail vector;
9. J1–J7 objective vectors and deltas;
10. explicit authority/firewall state.

## Interpretation constraints

A better value on any objective term is not a global design victory. S2 reports tradeoffs, not a scalar winner.

Full inertia, principal axes, radiator/docking clearances, and other quantities dependent on unresolved geometry remain OPEN where the common admitted model cannot support them.

## Acceptance

S2 comparison passes if:

- both baseline and generated layouts evaluate legally under the same S1 admitted model;
- the comparison is deterministic;
- the baseline reproduces the qualified DOCKED wet mass and CoM exactly;
- the generated result reproduces the closed S1 candidate;
- differences are reported without authority promotion;
- unresolved quantities remain explicit rather than silently filled.
