# Rendezvous experiment: stopped at first numerical failure (TEST ONLY)

**Status: PARTIAL / FAILED.** Do not interpret this as a completed 59-body geometry run, a price calibration, or a Route 1 result. No existing runtime, Route 1, loader, manifest, or PR files were edited.

## Preserved output order

1. `RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv` and `RENDEZVOUS_WORLD_AUTHORITY_REPORT_TEST_ONLY.json` were completed first: 90 bodies, 57 with one or more missing requested physical parameters. `data/LOOM_2226.sqlite3` `celestial_dynamics` holds Earth GM 398600.4355 km³/s² and radius 6371.0084 km, matching the prior kT-authored references. Source population logic `src/loom_solar_gis.py:1191,1402`.
2. `RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json` preserves the old flyby input hash and new kT-authored rendezvous $700M fixed cost and $0 per flight-year operating cost. Its full input and hash were printed before computation. The run identity hash was printed.
3. `RENDEZVOUS_SAMPLED_DEPARTURES_TEST_ONLY.csv` contains 55 completed departure records for AMUN and APOPHIS, 2026, including departure and arrival speeds. `RENDEZVOUS_PRICES_TEST_ONLY.csv` contains their two completed body-year prices. The files were flushed after each row.
4. The first geometry for ARROKOTH, 2026 triggered `OverflowError: (34, 'Numerical result out of range')` at `rendezvous_cost_test_only.py:14`, evaluating `payload*factor**n`. This is floating-point overflow on a very large modeled serial-stage mass, not an authored mass or stage cap.
5. The remaining geometry, prices, control replay and Route 1 variant were **not run**. No `RENDEZVOUS_GEOMETRY_REPORT_TEST_ONLY.json` or `RENDEZVOUS_ROUTE1_REPORT_TEST_ONLY.json` was produced.

## Hand checks, using kT-authored input

- 10 km/s departure, 3 km/s arrival: braking stage count 1, braking stack 887.3623901803162 kg; departure delta-v 7.085723212271492 km/s, departure stage count 1, LEO mass 8001.516756437676 kg; launch $32,006,067.025750704, fixed $700,000,000, operating $0, total $732,006,067.0257508. The 8.0 t hand check matches.
- 20 km/s departure, 5 km/s arrival: braking stage count 1, braking stack 1629.0763546489202 kg; departure delta-v 15.062706254050262 km/s, departure stage count 2, LEO mass 203304.36288079017 kg; launch $813,217,451.5231607, fixed $700,000,000, operating $0, total $1,513,217,451.5231607.

## Run identity and hashes

- New authored input SHA-256 `afb5903ea80f209928d8f51346a25b13d126a8c1ab8cea6008bebb9b48d01668`.
- Parent flyby input SHA-256 `1a45564a1efb9f6bb134f00d43d05aa763ce71f99a34a9ee79029f0e97eae167`.
- Printed partial-run identity SHA-256 `00a00a4b353da14853f2237494b2a783cb10a708ac3eeb5ffd3e7e4729328507`.
- World-authority CSV SHA-256 `9a8573a16cb11e95800d71b17c753d8b8818f9cc08659b093ec9530fb4568149`.
- World-authority JSON SHA-256 `8f874e1f87f0d188b127fb916de77c6f6247e6318bea00217e9eacfc6281c1a4`.
- Partial departure CSV SHA-256 `64069dcab210d40f719e21235f87f6634b2b09908629590e1b8447721aaa16a6`.
- Partial prices CSV SHA-256 `363ae766b1505dbb212c75c42a9bbfcf4e4b02dfcde01adb6aba711bfd6feb33`.
- Prior flyby prices CSV SHA-256 `2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73` (validated unchanged before geometry).
- Route 1 control hash `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` was **not rerun**; no new pass claim.

## Performance

- Last completed checkpoint: 17.75 seconds elapsed, peak RSS 282,128,384 bytes. No complete-run time or peak-memory figure exists.

## Required correction before a continuation

Represent extremely large masses and costs without float overflow (e.g., log mass or sufficiently ranged Decimal), while preserving derived stage counts and no cap. Continuation must preserve the already flushed partial data, avoid resampling previously completed geometry, and distinguish any changed runner identity from the failed run identity. Do not claim recovered departure refinement matches prior sampling unless actually verified.
