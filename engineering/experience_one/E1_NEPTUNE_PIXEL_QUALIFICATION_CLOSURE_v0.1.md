# Experience One — Ceres → Neptune Pixel qualification closure v0.1

## Disposition

`PASS / EMPIRICALLY_TESTED / 2226_TYPED_INTERACTION_FLIGHT_STATE_PERSISTENCE_SEAM_CLOSED`

## Target

Bounded Experience One interaction + mechanics seam:

`CERES start → typed intent → Navigator comparison candidates → typed review → Navigator final solve → explicit typed authorization → existing Navigator execution → NEPTUNE_SYSTEM arrival → restart → replay`

This is not a claim that the full 2226 Experience One product is complete.

## Pixel evidence

Platform: Pixel 10 Pro / Termux  
Checkout: `engineering/experience-one-neptune-flight-closure-2026-09-13`  
Runtime inputs: `/storage/emulated/0/Download/LOOM_TEST`  
Disposable qualification root: `/storage/emulated/0/Download/LOOM_E1_NEPTUNE_QUAL`

Controlling typed 2226 result artifact:
`engineering/experience_one/evidence/E1_NEPTUNE_2226_TYPED_PIXEL_QUALIFICATION_RESULT_2026-09-13.json`

Qualification epoch: `2226-08-22T01:32:00Z`

Observed:
- origin `CERES`, destination `NEPTUNE_SYSTEM`;
- interaction contract `LOOM_E1_FLIGHT_INTENT_V1`;
- eight deterministic direct candidates produced by Navigator;
- plan 1 explicitly selected;
- Navigator produced the final plan SHA only after selection/final solve;
- typed review SHA `9f6da59c1eb686ad30e9aaf4bc9c9aacb5ecf516d8f0b4e3970c6afed6cff785`;
- typed authorization contract `LOOM_E1_FLIGHT_AUTHORIZATION_V1`;
- typed execution-request contract `LOOM_E1_NAVIGATOR_EXECUTION_REQUEST_V1`;
- `typed_interaction_pass: true`;
- explicit `COMMIT FLIGHT? [y/N] y` authorization required;
- committed plan SHA `c323db2f783774c85eecb0bde362e8567aba631ff7f22c680f69c595ed66c6dd`;
- typed execution request final plan SHA matched the actual committed Navigator plan SHA;
- `FLIGHT_COMMITTED`, two `FLIGHT_PHASE` records, and `FLIGHT_ARRIVED` recorded;
- arrival state `S000002-b32f118834b5` at `NEPTUNE_SYSTEM`;
- restart recovered Neptune state at `2226-08-22T09:45:17.864616Z`;
- authoritative flight-runtime determinism PASS;
- expected and replay runtime SHA both `7e0620be4ee337e36554263e2cdd566547e8d2563e0b38b4ec5831cb9fc933a7`;
- replay PASS;
- live campaign state/history hashes were bit-identical before and after;
- `qualification_pass: true`.

## What this earns

The 2226 E1 typed interaction + flight/state/persistence seam is empirically closed on the first-class Pixel runtime without introducing a second planning, flight, state, ephemeris, clock, or execution authority.

Human/Mara/NPC/system intent remains nonauthoritative. Review is nonexecuting. Explicit authorization binds to Navigator-owned state, the reviewed candidate set, and Navigator's finalized plan SHA. Navigator remains sole planning/execution/campaign authority.

Sequence B/C/D whole-map presentation compilation remains outside this qualification scope.

## Prior evidence retained

The earlier 2027 disposable Pixel qualification remains historical evidence. The 2226 V3 run closed campaign-time flight/state/persistence. The 2226 V4 typed Pixel run is now controlling evidence for the interaction + flight seam.

## Remaining E1 critical-path work

1. insert audited Mara/OpenAI through the qualified provider-neutral typed seam, preserving zero LLM calculation/state/execution authority;
2. build HUD presentation/interaction in front of Navigator;
3. selectively reuse PR #103 spatial presentation patterns without epoch/frame authority conflicts;
4. prove minimum grounded Neptune orientation after arrival;
5. run the Pixel zero-instruction Experience One acceptance path: `You’re aboard Wayfarer. Explore.`

## Falsifier retained

This closure is invalid if later production integration bypasses Navigator authority, weakens explicit authorization, permits an LLM/browser to calculate or mutate state, produces divergent restart/replay state, or mutates an unintended campaign.
