# LOOM 2226 — E1.1 Operator Context / Location Finding v0.1

**Status:** EMPIRICAL CAMPAIGN-STATE SHAPE REQUIRED BEFORE COMPOSITION CONTRACT  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Current diagnosis:** `DIAGNOSIS_UNRESOLVED`

## Question

Experience One requires Mara to answer ordinary operator questions such as:

> Where am I?

That question must not be answered from Canon Context Projection merely because the surrounding world context is Ceres. Ship/operator location is campaign/runtime state and belongs to Navigator/Python authority.

The next seam is therefore not a broader world-context abstraction. It is identifying the smallest existing Navigator-owned state fields that can answer location without creating a duplicate state authority.

## Authority split to preserve

- **Where is Wayfarer / what state is the ship in?** — Navigator campaign-state authority.
- **What is Ceres / what is interesting here?** — read-only Canon Context Projection.
- **What is at a destination such as Neptune?** — destination canon/context projection.
- **Mara** — synthesis only; zero calculation, state, or canon authority.

No composition layer may flatten those into one new authoritative object.

## First discriminator

Before adding any runtime contract, run:

`engineering/experience_one/spikes/e1_1_campaign_state_location_probe.py`

against the actual Pixel `LOOM_STATE_V1.json`.

The probe:

- reads the existing JSON file only;
- hashes the exact source bytes;
- records root keys;
- walks scalar paths;
- reports fields whose paths look location/body/position/target/epoch/kinematic/flight/ship related;
- performs no mutation and no model call;
- claims no state or calculation authority.

This is intentionally diagnostic. Candidate fields are not promoted to a typed Experience Context contract until the empirical state shape is inspected.

## Change classification

Current increment: `DIAGNOSTIC_ONLY`.

Downstream compatibility impact: none. No `src/**` runtime behavior changes, schema changes, launcher changes, persistence changes, campaign mutation, or UI replacement.

## Why this comes before composition

Creating a generic `ExperienceContext` before inspecting the real campaign state would risk:

- duplicate state authority;
- invented location semantics;
- binding to stale or fixture-only fields;
- letting surrounding canon context masquerade as ship state;
- architecture growth before a demonstrated seam.

The empirical location shape should determine the smallest adapter, if one is needed.

## Pass condition for this discriminator

The probe identifies an existing, unambiguous Navigator-owned field or bounded field set sufficient to state Wayfarer's current location/kinematic boundary while preserving provenance and source authority.

## Replan condition

Replan if the live state has no unambiguous location representation, if current location must be reconstructed through substantial calculation, or if multiple conflicting state representations exist.

## Falsifier

Do not claim this discriminator passed from source inspection or fixture shape alone. It requires the actual Pixel campaign-state artifact.
