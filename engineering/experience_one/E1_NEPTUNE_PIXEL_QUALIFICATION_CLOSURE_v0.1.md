# Experience One — Ceres → Neptune Pixel qualification closure v0.1

## Disposition

`PASS / EMPIRICALLY_TESTED / 2226_FLIGHT_STATE_PERSISTENCE_SEAM_CLOSED`

## Target

Bounded Experience One mechanics seam only:

`CERES start → deterministic plan → explicit authorization → existing Navigator execution → NEPTUNE_SYSTEM arrival → restart → replay`

This is not a claim that the full 2226 Experience One product is complete.

## Pixel evidence

Platform: Pixel 10 Pro / Termux  
Checkout: `engineering/experience-one-neptune-flight-closure-2026-09-13`  
Runtime inputs: `/storage/emulated/0/Download/LOOM_TEST`  
Disposable qualification root: `/storage/emulated/0/Download/LOOM_E1_NEPTUNE_QUAL`

Authoritative 2226 result artifact:
`engineering/experience_one/evidence/E1_NEPTUNE_2226_PIXEL_QUALIFICATION_RESULT_2026-09-13.json`

Qualification epoch:
`2226-08-22T01:32:00Z`

Observed:

- origin `CERES`;
- destination `NEPTUNE_SYSTEM`;
- route-scoped authoritative ephemeris acquisition used only `CE` / Ceres and `NE` / Neptune system barycenter;
- eight deterministic direct candidate plans produced;
- plan 1 explicitly selected;
- explicit `COMMIT FLIGHT? [y/N] y` authorization required;
- selected plan `HARD / CRUISE`;
- departure `2226-08-22T01:32:00Z`;
- arrival `2226-08-22T09:45:17.864616Z`;
- total transit `8.222 h`;
- plan SHA `38b43bc50363cffc69eea114fc6231ed50441aec85aa4bc8458270feb6c91f2e`;
- `FLIGHT_COMMITTED` recorded;
- two authoritative `FLIGHT_PHASE` records recorded;
- `FLIGHT_ARRIVED` recorded;
- arrival state `S000002-17d132b08c45` at `NEPTUNE_SYSTEM`;
- post-arrival remass `236.603241561 t` from `250.000000 t` start;
- restart recovered the same Neptune state and epoch;
- authoritative flight-runtime determinism PASS;
- expected and replay runtime SHA both `4ed0223c83d1900d0cfcb57cb0622d982bdddfed2ef8f3241dfc392dd3a8d350`;
- replay PASS;
- live campaign state/history hashes were bit-identical before and after;
- qualification result reported `qualification_pass: true`.

## What this earns

The 2226 E1 Ceres → Neptune flight/state/persistence mechanics seam is empirically closed on the first-class Pixel runtime without introducing a second flight, state, ephemeris, clock, or execution authority.

The production path remains the existing Navigator authority.

Sequence B/C/D whole-map presentation compilation was intentionally outside this qualification scope and does not gate the authoritative flight seam.

## Prior evidence retained

The earlier 2027 disposable Pixel qualification remains useful historical evidence for the same authority path but no longer defines the temporal boundary of this seam. The 2226 V3 run is the controlling qualification evidence for E1 flight closure.

## Remaining E1 critical-path work

1. port/re-earn the minimal typed request/review/authorization seam from PR #99 onto current E1/main without wholesale merging the stale branch;
2. keep Navigator as sole planning/execution/campaign authority;
3. insert audited Mara/OpenAI through the provider-neutral typed seam only after that deterministic contract is re-earned;
4. build HUD presentation/interaction in front of Navigator, not around it;
5. selectively reuse PR #103 spatial presentation patterns where they do not reintroduce epoch/frame authority conflicts;
6. prove minimum grounded Neptune orientation;
7. run the Pixel zero-instruction Experience One acceptance path: `You’re aboard Wayfarer. Explore.`

## Falsifier retained

This closure is invalid if later production integration bypasses existing Navigator authority, loses explicit authorization, produces divergent restart/replay state, mutates an unintended campaign, or relies on browser/LLM calculation or state authority.
