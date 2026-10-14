# Build 8: Catalog-wide date-qualified travel endpoint eligibility

**RESEARCH / NON-CANON / NON-RUNTIME.** Exact base: `fc949bd3e07e3fb79280b69cbd9622f36b60feec`.

This is **not a route search**. Each entry checks the qualified source for that exact date. No vehicle, price, wait, payment, local-access or delivery placeholders change.

## Status legend

- **D** = `DIRECT`: qualified navigation-grade ephemeris and no additional unsupported local-leg requirement.
- **L** = `UNKNOWN_LOCAL_LEG`: **DIRECT** ephemeris exists, but the moon-to-parent-system local leg (time/cost/feasibility) is not authored; this is not delivery permission.
- **P** = `UNKNOWN_EPHEMERIS_PROPAGATED`: not qualified navigation-grade.
- **M** = `UNKNOWN_EPHEMERIS_MISSING`: no qualified direct state at the date.
- **S** = `UNSUPPORTED_SUN_ENDPOINT`: direct Solar ephemeris exists but the Sun is not a transport endpoint.
- **C** = `UNKNOWN_CATALOG_ENTITY`: for IDs outside these 110.

Statuses are **as at 00:00:00 UTC on 1 January** of each column year. Source availability does not establish a feasible journey. Barycenters are never substituted for physical centers.

## All 110 catalog identities

| Body ID | Class | Parent identity | 2026 | 2100 | 2199 | 2200 | 2226 |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| AMUN | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| APOPHIS | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| ARIEL | NATURAL_SATELLITE | URANUS_SYSTEM_BARYCENTER | L | L | L | L | L |
| ARROKOTH | TRANS_NEPTUNIAN_OBJECT | — | D | D | D | D | D |
| ASTEROID_6178 | ASTEROID | — | D | D | D | D | D |
| ATLAS3I | INTERSTELLAR_OBJECT | — | D | D | D | D | D |
| BENNU | NEAR_EARTH_ASTEROID | — | D | D | P | P | P |
| BORISOV | INTERSTELLAR_OBJECT | — | D | D | D | D | D |
| BORRELLY | COMET | — | D | D | D | D | D |
| BRAILLE | ASTEROID | — | D | D | D | D | D |
| CALLISTO | NATURAL_SATELLITE | JUPITER_SYSTEM_BARYCENTER | L | L | L | L | P |
| CERES | DWARF_PLANET | — | D | D | D | D | D |
| CHARON | NATURAL_SATELLITE | PLUTO_SYSTEM_BARYCENTER | L | L | L | P | P |
| CHIRON | CENTAUR | — | D | D | D | D | D |
| COMET_67P | COMET | — | D | D | D | D | D |
| COMET_HALLEY | COMET | — | D | D | D | D | D |
| DACTYL | NATURAL_SATELLITE | IDA | M | M | M | M | M |
| DAVIDA | ASTEROID | — | D | D | D | D | D |
| DEIMOS | NATURAL_SATELLITE | MARS_SYSTEM_BARYCENTER | L | L | L | L | L |
| DIDYMOS | BINARY_ASTEROID_PRIMARY | — | D | D | D | D | D |
| DINKINESH | ASTEROID | — | D | D | D | D | D |
| DIONE | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| DONALDJOHANSON | ASTEROID | — | D | D | D | D | D |
| EARTH | PLANET | — | D | D | D | D | D |
| EARTH_MOON_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| ENCELADUS | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| ERIS | DWARF_PLANET | — | D | D | D | D | D |
| EROS | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| EUROPA | NATURAL_SATELLITE | JUPITER_SYSTEM_BARYCENTER | L | L | L | L | P |
| EURYBATES | TROJAN_ASTEROID | — | D | D | D | D | D |
| GANYMEDE | NATURAL_SATELLITE | JUPITER_SYSTEM_BARYCENTER | L | L | L | L | P |
| GASPRA | ASTEROID | — | D | D | D | D | D |
| GONGGONG | DWARF_PLANET | — | D | D | D | D | D |
| HARTLEY2 | COMET | — | D | D | D | D | D |
| HAUMEA | DWARF_PLANET | — | D | D | D | D | D |
| HYDRA | NATURAL_SATELLITE | PLUTO | L | L | L | M | M |
| HYGIEA | ASTEROID | — | D | D | D | D | D |
| HYPERION | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| IAPETUS | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| IDA | ASTEROID | — | D | D | D | D | D |
| INTERAMNIA | ASTEROID | — | D | D | D | D | D |
| IO | NATURAL_SATELLITE | JUPITER_SYSTEM_BARYCENTER | L | L | L | L | P |
| ITOKAWA | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| IXION | TRANS_NEPTUNIAN_OBJECT | — | D | D | D | D | D |
| JUNO | ASTEROID | — | D | D | D | D | D |
| JUPITER | PLANET | JUPITER_SYSTEM_BARYCENTER | D | D | D | D | P |
| JUPITER_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| KERBEROS | NATURAL_SATELLITE | PLUTO | L | L | L | M | M |
| KLEOPATRA | BINARY_ASTEROID_PRIMARY | — | D | D | D | D | D |
| LEUCUS | TROJAN_ASTEROID | — | D | D | D | D | D |
| LUTETIA | ASTEROID | — | D | D | D | D | D |
| MAKEMAKE | DWARF_PLANET | — | D | D | D | D | D |
| MARS | PLANET | — | D | D | D | D | D |
| MARS_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| MATHILDE | ASTEROID | — | D | D | D | D | D |
| MERCURY | PLANET | — | D | D | D | D | D |
| MERCURY_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| MIMAS | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| MIRANDA | NATURAL_SATELLITE | URANUS_SYSTEM_BARYCENTER | L | L | L | L | L |
| MOON | NATURAL_SATELLITE | — | L | L | L | L | L |
| MS4 | TRANS_NEPTUNIAN_OBJECT | — | D | D | D | D | D |
| NEPTUNE | PLANET | — | D | D | D | D | D |
| NEPTUNE_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| NEREID | NATURAL_SATELLITE | NEPTUNE_SYSTEM_BARYCENTER | L | L | L | L | L |
| NEWHORIZONS | SPACECRAFT | — | P | P | P | P | P |
| NIX | NATURAL_SATELLITE | PLUTO | L | L | L | M | M |
| OBERON | NATURAL_SATELLITE | URANUS_SYSTEM_BARYCENTER | L | L | L | L | L |
| ORCUS | DWARF_PLANET | — | D | D | D | D | D |
| ORUS | TROJAN_ASTEROID | — | D | D | D | D | D |
| OUMUAMUA | INTERSTELLAR_OBJECT | — | D | D | D | D | D |
| PALLAS | ASTEROID | — | D | D | D | D | D |
| PATROCLUS | BINARY_ASTEROID_PRIMARY | — | D | D | D | D | D |
| PHOBOS | NATURAL_SATELLITE | MARS_SYSTEM_BARYCENTER | L | L | L | L | L |
| PHOEBE | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| PIONEER10 | SPACECRAFT | — | P | P | P | P | P |
| PIONEER11 | SPACECRAFT | — | P | P | P | P | P |
| PLUTO | DWARF_PLANET | PLUTO_SYSTEM_BARYCENTER | D | D | D | P | P |
| PLUTO_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| POLYMELE | TROJAN_ASTEROID | — | D | D | D | D | D |
| PROTEUS | NATURAL_SATELLITE | NEPTUNE_SYSTEM_BARYCENTER | L | L | L | M | M |
| PSYCHE | ASTEROID | — | D | D | D | D | D |
| QUAOAR | DWARF_PLANET | — | D | D | D | D | D |
| RHEA | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| RYUGU | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| SALACIA | DWARF_PLANET | — | D | D | D | D | D |
| SATURN | PLANET | — | D | D | D | D | D |
| SATURN_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| SEDNA | DWARF_PLANET | — | D | D | D | D | D |
| SELAM | NATURAL_SATELLITE | DINKINESH | M | M | M | M | M |
| STEINS | ASTEROID | — | D | D | D | D | D |
| STYX | NATURAL_SATELLITE | PLUTO | L | L | L | M | M |
| SUN | STAR | — | S | S | S | S | S |
| SWIFTTUTTLE | COMET | — | D | D | D | D | D |
| TEMPEL1 | COMET | — | D | D | D | D | D |
| TETHYS | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| THEMIS | ASTEROID | — | D | D | D | D | D |
| TITAN | NATURAL_SATELLITE | SATURN_SYSTEM_BARYCENTER | L | L | L | L | L |
| TITANIA | NATURAL_SATELLITE | URANUS_SYSTEM_BARYCENTER | L | L | L | L | L |
| TOUTATIS | NEAR_EARTH_ASTEROID | — | D | D | D | D | D |
| TRITON | NATURAL_SATELLITE | NEPTUNE_SYSTEM_BARYCENTER | L | L | L | L | L |
| UMBRIEL | NATURAL_SATELLITE | URANUS_SYSTEM_BARYCENTER | L | L | L | L | L |
| URANUS | PLANET | — | D | D | D | D | D |
| URANUS_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| VARUNA | DWARF_PLANET | — | D | D | D | D | D |
| VENUS | PLANET | — | D | D | D | D | D |
| VENUS_SYSTEM_BARYCENTER | BARYCENTER | — | D | D | D | D | D |
| VESTA | ASTEROID | — | D | D | D | D | D |
| VOYAGER1 | SPACECRAFT | — | P | P | P | P | P |
| VOYAGER2 | SPACECRAFT | — | P | P | P | P | P |
| WILD2 | COMET | — | D | D | D | D | D |

## Source coverage seams (2026–2226)

Qualifying source windows are compared **one second before and one second after** each internal start/end boundary. A qualified source may change without a status change; those are shown separately. Timestamp precision and overlapping hand-offs are preserved by the resolver.

| Body | UTC source boundary | Status before → after | Ephemeris before → after | Source before → after |
|---|---|---|---|---|
| BENNU | 2135-09-30T23:58:50.818000Z | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_BENNU_SB441 → PROP_BENNU_2101955_PHASE4D |
| CALLISTO | 2200-01-09T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_JUP365_PRE2250 → PROP_CALLISTO_504_PHASE4B |
| CHARON | 2199-12-29T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_PLU060_PRE2250 → PROP_CHARON_901_PHASE4B |
| EUROPA | 2200-01-09T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_JUP365_PRE2250 → PROP_EUROPA_502_PHASE4B |
| GANYMEDE | 2200-01-09T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_JUP365_PRE2250 → PROP_GANYMEDE_503_PHASE4B |
| HYDRA | 2199-12-29T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_MISSING | DIRECT → UNKNOWN_EPHEMERIS_MISSING | NAIF_PLU060_4E → None |
| IO | 2200-01-09T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_JUP365_PRE2250 → PROP_IO_501_PHASE4B |
| JUPITER | 2200-01-09T23:58:50.816000Z | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_JUP365_PRE2250 → PROP_JUPITER_599_PHASE4B |
| KERBEROS | 2199-12-29T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_MISSING | DIRECT → UNKNOWN_EPHEMERIS_MISSING | NAIF_PLU060_4E → None |
| NEWHORIZONS | 2033-01-01T11:58:51Z | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | NAIF_NH_OD164 → PROP_4E_NEWHORIZONS |
| NIX | 2199-12-29T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_MISSING | DIRECT → UNKNOWN_EPHEMERIS_MISSING | NAIF_PLU060_4E → None |
| PLUTO | 2199-12-29T23:58:50.816000Z | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | DIRECT → UNKNOWN_EPHEMERIS_PROPAGATED | JPL_PLU060_PRE2250 → PROP_PLUTO_999_PHASE4B |
| PROTEUS | 2199-12-30T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_MISSING | DIRECT → UNKNOWN_EPHEMERIS_MISSING | NAIF_NEP098_808 → None |
| STYX | 2199-12-29T23:58:50.816000Z | UNKNOWN_LOCAL_LEG → UNKNOWN_EPHEMERIS_MISSING | DIRECT → UNKNOWN_EPHEMERIS_MISSING | NAIF_PLU060_4E → None |
| VOYAGER1 | 2099-12-31T23:58:50.816000Z | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | NAIF_VOYAGER1_SPK → PROP_4E_VOYAGER1 |
| VOYAGER2 | 2099-12-31T23:58:50.816000Z | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | UNKNOWN_EPHEMERIS_PROPAGATED → UNKNOWN_EPHEMERIS_PROPAGATED | NAIF_VOYAGER2_SPK → PROP_4E_VOYAGER2 |

## Status counts

| Epoch (Jan 1 UTC) | Direct ephemerides | Propagated | Missing | Local leg unknown | Supported direct non-moon endpoint |
|---|---:|---:|---:|---:|---:|
| 2026 | 103 | 5 | 2 | 29 | 73 |
| 2100 | 103 | 5 | 2 | 29 | 73 |
| 2199 | 102 | 6 | 2 | 29 | 72 |
| 2200 | 95 | 8 | 7 | 23 | 71 |
| 2226 | 90 | 13 | 7 | 19 | 70 |

## Replay control

The eight original on-demand geometry routes were sampled at **2026-05-14T00:00:00Z** on exact main **before** editing and at the same time/flight grid **after** the catalog resolver was installed. Complete compact sorted JSON records (including provenance and cache keys) matched byte-for-byte: **8/8**. Main-branch expected SHA-256s are pinned in `test_catalog_eligibility.py`. Test-only comparison data remains outside Git.

The resolver never solves Lambert routes. Source selection uses the qualified Phase4 manifests and the exact fourteen DE440 source coverages promoted by SQL migration 012. For the older overlapping Saturn center source, the official planet-center manifest is the governing source; duplicate source coverage is deduplicated, not randomly ordered.

**Scope:** Build 8 code, tests and this report only; no baseline, frozen source, Build 7, or kernel modifications.
