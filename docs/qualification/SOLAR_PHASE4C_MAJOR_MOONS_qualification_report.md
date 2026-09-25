# Solar Phase 4C Major-Moon Qualification

**Result:** PASS  
**Manifest:** `manifests/solar/SOLAR_PHASE4C_MAJOR_MOONS_V1.json`  
**Migration:** `014_solar_phase4c_major_moons.sql`  
**Horizon gate:** all required targets reach at least `2251-01-01T00:00:00Z`

All 17 required targets are directly qualified from accepted JPL/NAIF SPKs. No
Phase-4B propagation was needed.

| Target | NAIF | Accepted source | Actual coverage end |
|---|---:|---|---|
| Phobos | 401 | MAR099 | 2600-01-01T23:58:50.816Z |
| Deimos | 402 | MAR099 | 2600-01-01T23:58:50.816Z |
| Mimas | 601 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Enceladus | 602 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Tethys | 603 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Dione | 604 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Rhea | 605 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Titan | 606 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Hyperion | 607 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Iapetus | 608 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Phoebe | 609 | SAT441XL part 2 | 4500-01-17T23:58:50.817Z |
| Ariel | 701 | URA184 part 3 | 2399-12-16T23:58:50.817Z |
| Umbriel | 702 | URA184 part 3 | 2399-12-16T23:58:50.817Z |
| Titania | 703 | URA184 part 3 | 2399-12-16T23:58:50.817Z |
| Oberon | 704 | URA184 part 3 | 2399-12-16T23:58:50.817Z |
| Miranda | 705 | URA184 part 3 | 2399-12-16T23:58:50.817Z |
| Triton | 801 | NEP097 | 2399-12-30T23:58:50.816Z |

Each target was verified at 2026, 2226, 2250-01-01 and
`2250-12-31T23:59:59Z` with position and velocity, ECLIPJ2000, km/km/s,
deterministic replay, source provenance and hash validation. Exact source
boundaries resolve and post-coverage requests fail closed. Physical satellite
identities remain distinct from parent-system barycenters.

The accepted kernels also contain Saturn NAIF 612 and Uranus NAIF 716–724 and
75051. They remain inventoried but unpromoted because Phase 4C scope is the
required major-moon set; no speculative irregular-moon catalog work was added.
