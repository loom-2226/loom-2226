# LOOM Solar Phase 4 — 2250 Ephemeris Completion Work Plan v1.0

**Status:** PHASE 4B CLOSED; PHASE 4C/5 NOT STARTED
**Primary class:** `class:engineering` with governed `class:data` promotion steps
**Date:** 2026-09-25
**Repository:** `loom-2226/loom-2226`
**Gate:** Phase 5 MUST NOT begin until the Phase-4 completion gate in this document passes.

## 1. Decision

Phase 4 is expanded from a representative ephemeris qualification into the complete
pre-Phase-5 Solar spatial authority baseline.

The governing body-state rule is:

> A physical body resolves to its physical center. A system barycenter remains a
> separate first-class dynamical point and is never silently substituted for the body.

The governing horizon rule is:

> "Through 2250" means uninterrupted governed state capability through
> `2250-12-31T23:59:59Z`; a source satisfies the full-horizon gate only when its
> declared coverage reaches at least `2251-01-01T00:00:00Z`.

A successful query must preserve exact identity, source, epoch/time-scale, frame,
units, coverage, quality, provenance and uncertainty semantics.

## 2. Why this is Phase 4

The causal chain remains:

`ephemeris -> geometry -> accessibility -> transport -> infrastructure -> civilization`.

Phase 5 must not build a broad catalog on top of barycenter substitutions, missing
physical centers, hidden coverage holes, or objects that cannot produce a governed
state over the modeled horizon. Therefore identity/ephemeris closure is a Phase-4
qualification obligation.

## 3. State-quality classes

Catalog membership and ephemeris quality are separate.

Every catalog object must carry one of these state-capability dispositions:

- `DIRECT_SPICE_2250_QUALIFIED` — pinned authoritative SPK/source covers the full horizon and passes the governed SPICE contract.
- `HORIZONS_SPK_2250_QUALIFIED` — pinned JPL Horizons-generated SPK covers the full horizon and passes the same contract.
- `EMPIRICAL_PROPAGATED_2250` — authoritative empirical orbit solution can provide the full horizon through a governed offline propagator, with explicit uncertainty and `navigation_grade=False`.
- `EPHEMERIS_PARTIAL` — empirical source exists but does not cover the full horizon.
- `CATALOG_ONLY` — identity exists but no governed 2026-2250 state capability has yet been earned.
- `UNRESOLVED` — identity/source conflict or missing authority; blocks operational use.

No object may receive a stronger class merely because a kernel happens to contain its
NAIF target.

## 4. Phase 4A — promote authority already earned

Promote the recovered/qualified Solar work before acquiring anything new.

### 4A.1 Earned target set

`SOLAR_PHASE4_EARNED_AUTHORITY_V1` contains 19 targets:

**DE440 — 14 targets**

- Mercury system barycenter — NAIF 1
- Venus system barycenter — NAIF 2
- Earth-Moon barycenter — NAIF 3
- Mars system barycenter — NAIF 4
- Jupiter system barycenter — NAIF 5
- Saturn system barycenter — NAIF 6
- Uranus system barycenter — NAIF 7
- Neptune system barycenter — NAIF 8
- Pluto system barycenter — NAIF 9
- Sun — NAIF 10
- Mercury — NAIF 199
- Venus — NAIF 299
- Moon — NAIF 301
- Earth — NAIF 399

**Previously qualified supplementary authority**

- Ceres — NAIF 20000001 — JPL/Horizons Ceres SPK
- Mars — NAIF 499 — MAR099
- Saturn — NAIF 699 — SAT441
- Uranus — NAIF 799 — URA184 part 3
- Neptune — NAIF 899 — NEP097

Migration `012_solar_phase4_earned_authority.sql` materializes only those earned
identities, sources and exact coverage intervals into `loom_solar`.

It does NOT promote additional moons merely because MAR099/SAT441/URA184/NEP097
contain their targets.

### 4A.2 Current full-horizon result

Of the 19 promoted targets, 17 already satisfy the full 2026-through-2250 gate.

Current promoted holes:

- **Ceres** — current qualified SPK ends `2226-12-31T23:58:50.816Z`.
- **Saturn physical center** — SAT441 ends `2250-01-05T23:58:50.816055Z`.

Jupiter and Pluto system barycenters are covered by DE440, but their physical centers
are not part of the earned promotion and remain separate Phase-4 holes.

## 5. Phase 4B — close physical-center and system horizon holes

### 4B.1 Ceres

Goal: physical Ceres state for the entire 2026-through-2250 horizon.

Plan:

1. acquire a new JPL Horizons-generated Ceres SPK covering at least
   `2025-01-01T00:00:00Z` through `2251-01-01T00:00:00Z`, preferably with guard
   coverage beyond both boundaries;
2. preserve Horizons response, orbit-solution identity, acquisition timestamp,
   source URL, bytes and SHA-256;
3. inspect `spkobj`, `spkcov` and segment descriptors;
4. compare the overlap against the currently qualified Ceres SPK at 2026 and 2226
   plus a dense deterministic overlap sample;
5. record any changed orbit solution rather than calling numerical differences drift;
6. qualify exact start/end boundaries and fail closed outside them;
7. promote only after deterministic replay and provenance tests pass.

Small-body uncertainty is part of the authority record. A longer SPK does not turn an
orbit solution into exact future truth.

### 4B.2 Saturn system

Goal: Saturn physical center and the high-value Saturn satellites through the full
calendar year 2250.

Current short source: SAT441 ends 2250-01-05.

Primary candidate: official NAIF `sat441xl_part-2.bsp`, whose published inventory
contains Saturn 699 and major satellites and extends from 2014 into 4500.

Plan:

1. acquire from the current NAIF generic satellite directory;
2. pin official catalog/checksum metadata plus local SHA-256;
3. inspect exact per-target `spkcov`; filename-level coverage is insufficient;
4. qualify Saturn 699 and each promoted moon separately;
5. preserve DE440 as the planetary backbone and prove load/source precedence;
6. cross-check overlap with SAT441 before retiring SAT441 as the preferred future
   source;
7. require coverage through at least 2251-01-01.

### 4B.3 Jupiter system

Goal: Jupiter 599 plus at minimum Io 501, Europa 502, Ganymede 503 and Callisto 504
through 2250.

Current generic JUP365 contains those targets but ends in 2200. Current generic JPL
satellite products do not establish the required 2250 horizon.

Plan, in authority order:

1. re-audit the live NAIF/JPL satellite index at acquisition time for a newly
   published official product reaching 2251;
2. if no suitable generic SPK exists, generate/pin JPL Horizons SPKs for Jupiter and
   the four Galilean moons through 2251 with guard coverage;
3. preserve exact Horizons solution/request provenance and source binaries;
4. qualify each target independently; Jupiter system barycenter NAIF 5 remains a
   separate DE440 identity;
5. compare overlap with JUP365 inside its valid interval;
6. explicitly reject barycenter substitution;
7. keep Research-Lab derived Jupiter-center candidates as non-authoritative
   comparators unless separately disposed/promoted through governance.

One accepted Jupiter-system source package should also inventory any additional
moon targets it legitimately supports, but those targets receive no authority until
object-level qualification is performed.

### 4B.4 Pluto system

Goal: Pluto 999 and Charon 901 through 2250, with Nix/Hydra/Kerberos/Styx included
when the selected authority supports them.

Current PLU060 ends in 2199.

Plan:

1. re-audit current official JPL/NAIF products;
2. if no direct official generic source reaches 2251, acquire JPL Horizons-generated
   SPKs for the required Pluto-system bodies;
3. preserve Pluto-system barycenter NAIF 9 as a separate DE440 dynamical point;
4. cross-check overlap with PLU060;
5. qualify each physical target independently and preserve uncertainty;
6. keep Research-Lab derived Pluto-center candidates non-production/non-authority
   unless separately promoted.

## 6. Phase 4C — promote moons already present in qualified system kernels

Presence in a source is not qualification. Use the already acquired official kernels
to perform object-level qualification and promote the following first.

### Mars / MAR099

- Phobos 401
- Deimos 402

### Saturn / SAT441 or its accepted long-horizon successor

- Mimas 601
- Enceladus 602
- Tethys 603
- Dione 604
- Rhea 605
- Titan 606
- Hyperion 607
- Iapetus 608
- Phoebe 609

Additional supported Saturn targets may follow only after explicit identity and
coverage qualification.

### Uranus / URA184 and qualified long-range companion products

- Ariel 701
- Umbriel 702
- Titania 703
- Oberon 704
- Miranda 705

### Neptune / NEP097

- Triton 801

Each object must pass exact identity, source-object coverage, 2026/2226/2250 state,
boundary, deterministic replay and provenance tests before promotion.

## 7. Phase 4D — strategic resource/object priority set

The following priority set originated as a user-supplied resource-value shortlist.
Its resource scores are **not** promoted here as empirical authority. The list only
sets ephemeris/catalog acquisition priority.

Already covered by Phase 4A/4B/4C work include Ceres, Moon, Titan, Callisto,
Triton, Pluto, Ganymede, Enceladus, Rhea, Titania, Oberon, Iapetus, Europa,
Dione, Ariel, Umbriel, Charon, Phoebe, Tethys, Miranda, Mimas, Phobos, Deimos,
Io and Hyperion.

Strategic direct small-body/dwarf/comet acquisition queue:

- 16 Psyche
- Eris
- 10 Hygiea
- 2 Pallas
- 4 Vesta
- 216 Kleopatra
- Makemake
- 2060 Chiron
- 617 Patroclus
- 101955 Bennu
- 162173 Ryugu
- 6178 (1986 DA)
- 3554 Amun
- 67P/Churyumov-Gerasimenko
- 1P/Halley
- Haumea
- 3548 Eurybates
- 433 Eros
- 25143 Itokawa
- 65803 Didymos

For each strategic small body:

1. resolve immutable LOOM identity and authoritative JPL/MPC/IAU aliases;
2. prefer a direct authoritative JPL/NAIF product when it satisfies the full horizon;
3. otherwise generate and pin a JPL Horizons SPK through 2251;
4. preserve orbit-solution identity, covariance/uncertainty where available, and
   observation/solution epoch;
5. distinguish physical ephemeris from resource/composition claims;
6. run 2026/2226/2250 plus exact-boundary qualification;
7. fail closed rather than substitute a parent/system barycenter.

Comets require explicit treatment of non-gravitational model provenance where the
selected Horizons solution uses it.

## 8. Phase 4E — broad empirical Solar catalog with 2250 state capability

Phase 4 now establishes the baseline empirical catalog before Phase 5.

### 8.1 Catalog scope

Freeze a dated authoritative source snapshot/crosswalk covering:

- Sun and planets;
- recognized planetary/dwarf-planet bodies;
- natural satellites;
- asteroids and NEOs;
- Centaurs and TNOs;
- comets;
- Jupiter Trojans and other relevant populations;
- known interstellar objects such as 1I/Oumuamua.

Identity ingestion must preserve external designations/aliases, object class,
discovery/source metadata and source snapshot/version.

### 8.2 Position capability

The broad catalog must not imply one universal precision class.

For every object admitted to the Phase-4 baseline, the resolver must either:

1. resolve a pinned direct/Horizons SPICE state through 2250; or
2. resolve a governed empirical propagated state through 2250 from an authoritative
   orbit solution, explicitly `navigation_grade=False`, with model/source/epoch and
   uncertainty provenance.

No runtime network dependency is allowed for ordinary state queries after the
baseline is frozen.

Strategic/operational bodies MUST use the qualified direct-SPICE/Horizons-SPK path;
the propagated tier is for the broad long tail, not a shortcut around strategic
qualification.

### 8.3 Broad-catalog propagation work

If exhaustive pre-generated SPKs are operationally unreasonable, build one governed
offline small-body propagation path rather than millions of ad-hoc trajectory rows.

Required controls:

- source orbit solution and epoch are immutable inputs;
- DE440 planetary perturbation authority remains pinned;
- algorithm/version and numerical tolerances are recorded;
- uncertainty/quality are explicit;
- representative asteroids, comets, TNOs and an interstellar object are compared
  against held-out Horizons states;
- propagated states remain non-navigation-grade unless a later qualification earns
  stronger status;
- no monthly/daily trajectory table is materialized by default.

## 9. PostgreSQL contract

`loom_solar` remains the metadata/identity/provenance/coverage authority. Kernel
bytes remain governed files.

Minimum existing tables remain:

- `loom_solar.body`
- `loom_solar.body_identifier`
- `loom_solar.ephemeris_source`
- `loom_solar.ephemeris_coverage`

Do not create another Solar truth database.

Schema extension is allowed only when Phase-4 requirements prove that the existing
four-table contract cannot represent catalog hierarchy, state-capability class or
propagated-model provenance without ambiguity.

Every forward migration must preserve exact rollback/backup and migration hashes.

## 10. Qualification matrix

At minimum test:

- 2026-01-01
- 2100-01-01
- 2190-01-01
- 2226-01-01
- 2250-01-01
- 2250-12-31T23:59:59Z
- exact source start/end boundaries
- one instant outside each boundary

For each direct SPICE target verify:

- exact LOOM identity and NAIF target;
- physical body vs barycenter distinction;
- exact source/object coverage from `spkcov`;
- pinned hash and byte count;
- deterministic replay;
- UTC -> SPICE ET/TDB;
- ECLIPJ2000 evaluation;
- canonical J2000/ECLIPTIC output;
- km and km/s;
- aberration `NONE`;
- fail-closed source ambiguity/missing coverage.

## 11. Phase-4 completion gate

Phase 5 is blocked until ALL of these are true:

1. the 19 already-earned targets are promoted into authoritative `loom_solar`;
2. Ceres, Saturn, Jupiter and Pluto physical-center horizon holes are closed through
   the full calendar year 2250;
3. the major/strategic moons in Sections 6 and 7 have object-level 2250 qualification;
4. every object in the strategic resource priority set has governed 2250 state
   capability, with direct SPICE/Horizons authority required for operational use;
5. a frozen empirical catalog source snapshot is ingested across all required object
   classes;
6. every admitted catalog object has a non-`UNRESOLVED` 2250 state-capability
   disposition;
7. the broad long-tail resolver, if required, passes held-out empirical validation and
   preserves non-navigation-grade uncertainty semantics;
8. PostgreSQL metadata exactly matches the governed manifests;
9. kernel/source binaries are hash-pinned and locally reproducible without runtime
   network access;
10. relevant unit, SPICE, PostgreSQL, backup/restore and `loom-gate` checks pass;
11. a machine-readable Phase-4 completion report records counts by object class,
    capability class, source and unresolved state.

**Required final unresolved operational targets: 0.**

## 12. Phase 5 boundary after completion

Only after the Phase-4 gate passes may Phase 5 proceed.

Phase 5 then means scientific/catalog enrichment and wider object-population use on
top of a completed 2026-through-2250 state foundation; it may not reopen basic
physical-center identity or horizon coverage as hidden prerequisites.

## 13. Phase 4B closure record (2026-09-26)

Phase 4B is closed for its required physical-center targets. Ceres and Saturn use
direct JPL/Horizons or JPL/NAIF SPKs through the required horizon. Jupiter, Io,
Europa, Ganymede, Callisto, Pluto and Charon use an explicit, deterministic,
offline RK4/N-body propagation seam initialized from the authoritative JUP365 or
PLU060 predecessor solution and validated against withheld predecessor overlap.
Those propagated states are recorded as `EMPIRICAL_PROPAGATED_2250`, carry explicit
uncertainty and `navigation_grade=false`, and are never represented as direct JPL
authority. The machine-readable authority manifest and qualification report are
the controlling implementation evidence.

Phase 4C remains a separate future work item. No satellite inventory promotion or
Phase 5 work is included in this closure.
