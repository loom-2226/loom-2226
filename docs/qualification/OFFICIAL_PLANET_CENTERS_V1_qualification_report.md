# Official Planet Centers V1 qualification

**Result:** PASS
**Primary change class:** `class:engineering`
**Scope:** physical centers Mars 499, Saturn 699, Uranus 799, Neptune 899 through `2250-01-01T00:00:00Z`

No derived orbit, barycenter substitution, runtime network dependency, or Research Lab PR #84 artifact is used. Jupiter 599 and Pluto 999 remain outside this implementation.

## Selected official inputs

The candidates were selected from the [current NAIF generic satellite SPK directory](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/). Selection used the official directory inventory, comments, summaries, and checksums, then direct binary inspection with `spkobj`, `spkcov`, and DAF segment descriptors. Filenames were not treated as evidence.

| LOOM body | Official product | Exact target coverage from SPK | Bytes | SHA-256 |
|---|---|---|---:|---|
| MARS / 499 | MAR099.01 | 1599-12-31T23:59:18.815889Z — 2600-01-01T23:58:50.816341Z | 1,227,574,272 | `9991e57b196bae1a096acc6e2afc6718102ee420d684695de0f0333064c046bc` |
| SATURN / 699 | SAT441.24 | 1749-12-29T23:59:18.816003Z — 2250-01-05T23:58:50.816055Z | 661,592,064 | `d7e444a9ba7a52b8f448ff0747030789524d2f0c1212e4e2bd7f5fc3c96444d5` |
| URANUS / 799 | URA184 part 3; 799 solution URA182.21 | 1600-01-03T23:59:18.815802Z — 2399-12-16T23:58:50.816698Z | 386,885,632 | `273cd4ccc470d1098562cd4e94fa48fc2b4c6b1c2896308e473c949b87937c53` |
| NEPTUNE / 899 | NEP097 / ephemeris version 24 | 1600-01-09T23:59:18.815630Z — 2399-12-30T23:58:50.816313Z | 105,262,080 | `5c1132fdc48c54e5d2e4eb663e1ed1a876911eae9433c203f29a5a1b5e1fa9b1` |

All byte counts and official MD5 values matched the NAIF catalog. SHA-256 values were computed locally. The selected target segments are SPK type 2 in frame ID 1 (`J2000`) and are centered on IDs 4, 6, 7, and 8 respectively. Coverage is represented by exact SPK ET bounds and normalized to UTC with pinned `naif0012.tls`.

`mar099`, `sat441`, and `nep097` contain embedded planetary-backbone segments from DE440. `ura184_part-3` contains DE442 backbone segments. Every supplementary source therefore loads the selected satellite-system SPK first and pinned DE440 last; SPICE precedence preserves DE440 as LOOM's planetary backbone while the supplementary source contributes only the missing physical-center target.

## Qualification result

Each center passed at 2026-01-01, 2226-01-01, and 2250-01-01 through the existing `HybridCelestialStateService` authority. Tests verified the exact NAIF target and source, pinned hashes, deterministic replay, explicit UTC conversion to SPICE ET/TDB, `ECLIPJ2000` evaluation, canonical `J2000/ECLIPTIC` output, km and km/s, geometric state with aberration `NONE`, exact source boundaries, and fail-closed behavior one microsecond outside each interval.

The physical centers remained measurably distinct from their system barycenters:

| Body | 2026 separation (km) | 2226 separation (km) | 2250 separation (km) |
|---|---:|---:|---:|
| Mars | 0.000102200 | 0.000132217 | 0.000203954 |
| Saturn | 271.622436 | 293.949315 | 299.950463 |
| Uranus | 30.749405 | 32.600954 | 41.966695 |
| Neptune | 74.003254 | 74.219637 | 73.933058 |

Requests for `MARS`, `SATURN`, `URANUS`, and `NEPTUNE` returned IDs 499, 699, 799, and 899. Explicit requests for the corresponding `*_SYSTEM_BARYCENTER` identities returned DE440 IDs 4, 6, 7, and 8. A regression also proved that metadata cannot claim NAIF 899 coverage from DE440 when object 899 is absent from that primary source asset.

Machine evidence: `OFFICIAL_PLANET_CENTERS_V1_evidence.json`
Evidence SHA-256: `953951ed26f18f35a042190337618179a19c8ef76b3ed3934374ebf76aa5e0be`
Acquisition manifest SHA-256: `2241829f4fd107d9b1a148e96c30a9e4dddfc2ed7d1b2b500aa63f47a770951a`

## Solar ephemeris coverage matrix

`2250 status` is authority availability for an ordinary governed request, not merely presence of an identity.

| Entity | NAIF | Classification | Governed source / exact relevant end | 2250 status |
|---|---:|---|---|---|
| MERCURY | 199 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| VENUS | 299 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| EARTH | 399 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| MARS | 499 | QUALIFIED SUPPLEMENTARY | MAR099 / 2600-01-01T23:58:50.816341Z | PASS |
| JUPITER | 599 | UNRESOLVED | Current official JUP365 ends 2200-01-10 ET; separate DERIVED CANDIDATE excluded | HOLD / NOT PROMOTED |
| SATURN | 699 | QUALIFIED SUPPLEMENTARY | SAT441 / 2250-01-05T23:58:50.816055Z | PASS |
| URANUS | 799 | QUALIFIED SUPPLEMENTARY | URA184 part 3 / 2399-12-16T23:58:50.816698Z | PASS |
| NEPTUNE | 899 | QUALIFIED SUPPLEMENTARY | NEP097 / 2399-12-30T23:58:50.816313Z | PASS |
| PLUTO | 999 | UNRESOLVED | Current official PLU060 ends 2199-12-30 ET; separate DERIVED CANDIDATE excluded | HOLD / NOT PROMOTED |
| MOON | 301 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| CERES | 20000001 | QUALIFIED SUPPLEMENTARY | Existing qualified Ceres SPK / 2226-12-31T23:58:50.816Z | UNRESOLVED AT 2250 |
| MERCURY SYSTEM BARYCENTER | 1 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| VENUS SYSTEM BARYCENTER | 2 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| EARTH-MOON BARYCENTER | 3 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| MARS SYSTEM BARYCENTER | 4 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| JUPITER SYSTEM BARYCENTER | 5 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| SATURN SYSTEM BARYCENTER | 6 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| URANUS SYSTEM BARYCENTER | 7 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| NEPTUNE SYSTEM BARYCENTER | 8 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |
| PLUTO SYSTEM BARYCENTER | 9 | OFFICIAL JPL/NAIF | DE440 / 2650-01-24T23:58:50.815708Z | COVERED |

The matrix does not register the non-scope Mercury, Venus, Jupiter, Pluto, Moon, or additional barycenter identities in migration 010. It records coverage disposition only and does not expand the catalog.

## Residual risk

SAT441 meets the requested threshold by only about five days. It is valid for `2250-01-01T00:00:00Z`, but requests after its exact `2250-01-05T23:58:50.816055Z` boundary fail closed. No required body is on HOLD for the specified 2250-01-01 target.
