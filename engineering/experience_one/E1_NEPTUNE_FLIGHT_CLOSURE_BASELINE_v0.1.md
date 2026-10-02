# LOOM Experience One — Neptune Flight Closure Baseline v0.1

**Class:** ENGINEERING / REQUIRED_FOR_E1  
**Authority:** Experience One Product Convergence Workplan v1.2  
**Bootstrap:** protected `main` at `f3db4ce59c3ead4b8bac1567d4ebeb1164fd542c`  
**Date:** 2026-09-13

## Purpose

Freeze Ceres feature expansion and establish the smallest production path needed to complete the governed Ceres → Neptune Experience One flight.

## Ceres disposition

`FROZEN_FOR_E1_FEATURE_EXPANSION`

Ceres may be changed on this branch only when an end-to-end flight test demonstrates a departure blocker. No new Ceres lore, NPC systems, motivation architecture, emergent-reality runtime, relationship graph runtime, ABM, quest engine, or presentation polish is authorized here.

## Verified production authority on main

`src/loom_navigator_core.py` already owns:

- authoritative campaign state and validation;
- quantitative flight calculations and operational choices;
- `FLIGHT_COMMITTED` history semantics;
- authoritative phase history;
- `FLIGHT_ARRIVED` history semantics;
- atomic state save / backup;
- replay requiring both `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED`.

Therefore this branch MUST NOT create a second campaign-state model, flight executor, ephemeris, clock, trajectory authority, or browser/LLM execution authority.

## Flight closure sequence

1. Reuse current Navigator flight authority.
2. Establish a disposable 2226 Ceres/Wayfarer qualification starting state without mutating a user's live campaign.
3. Resolve Neptune through existing authoritative target/navigation paths.
4. Produce deterministic candidate plan(s) and preserve the selected plan provenance.
5. Require explicit authorization before commit.
6. Execute through existing Navigator authority and produce `FLIGHT_COMMITTED` + `FLIGHT_ARRIVED`.
7. Verify authoritative post-flight location is Neptune.
8. Reload from disk and verify Neptune survives restart.
9. Replay the flight from campaign history and verify required records/provenance.
10. Expose only the minimum Neptune orientation needed by Experience One.
11. Run the same governed closure on Pixel and capture evidence.

## Immediate engineering question

The next change must identify the narrowest adapter/harness required to drive the existing Navigator flight path from a disposable Ceres qualification state through Neptune arrival and restart. If existing Navigator interfaces already provide this without production code changes, prefer a qualification harness and tests over new runtime architecture.

## Pass condition

No `PASS` is claimed by this document. Flight closure passes only with empirical evidence showing:

- Ceres start;
- Neptune target;
- deterministic selected plan;
- explicit authorization boundary;
- `FLIGHT_COMMITTED`;
- `FLIGHT_ARRIVED`;
- authoritative Neptune post-state;
- restart persistence;
- replay provenance;
- Pixel qualification.

## WALTER rails

Fail/replan if the implementation introduces duplicate state authority, duplicate ephemeris/clock, browser physics, LLM calculation/state authority, fixture promotion into canon, hidden live-campaign mutation, or feature expansion unrelated to the Ceres → Neptune seam.

**Rule:** close seams, not horizons.