# Solar Phase 4D Strategic Bodies Qualification

**Result:** PASS  
**Manifest:** `manifests/solar/SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json`  
**Migration:** `015_solar_phase4d_strategic_bodies.sql`  
**Horizon gate:** `2251-01-01T00:00:00Z`

Nineteen required bodies have direct JPL Horizons SPKs through the guard horizon.
Bennu uses the authoritative JPL/OSIRIS-REx reconstructed mission SPK through
2135, followed by an explicit Phase-4B RK4/N-body propagation seam. No propagated
state is represented as direct JPL authority.

| Body | NAIF | Accepted authority | Capability | Actual end |
|---|---:|---|---|---|
| 16 Psyche | 20000016 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| Eris | 20136199 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 10 Hygiea | 20000010 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 2 Pallas | 20000002 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 4 Vesta | 20000004 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 216 Kleopatra | 20000216 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| Makemake | 20136472 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 2060 Chiron | 20002060 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 617 Patroclus | 20000617 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 101955 Bennu | 2101955 | JPL mission SPK + LOOM propagation | propagated after 2135 | 2251-01-01T00:01:00Z |
| 162173 Ryugu | 20162173 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 6178 (1986 DA) | 20006178 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 3554 Amun | 20003554 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 67P/Churyumov-Gerasimenko | 1000012 | JPL Horizons SPK, K284/1 | direct | 2251-01-01T23:58:50.816Z |
| 1P/Halley | 1000036 | JPL Horizons SPK, JPL#75 | direct | 2251-01-01T23:58:50.816Z |
| Haumea | 20136108 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 3548 Eurybates | 20003548 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 433 Eros | 20000433 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 25143 Itokawa | 20025143 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |
| 65803 Didymos | 20065803 | JPL Horizons SPK | direct | 2251-01-01T23:58:50.816Z |

Every target resolved position and velocity at 2026, 2226, 2250-01-01 and
`2250-12-31T23:59:59Z`, with ECLIPJ2000, km/km/s, deterministic replay, exact NAIF
identity, source provenance and hash verification. Requests beyond accepted source
coverage fail closed.

## Bennu limitation and backtest

Horizons reports that Bennu's authoritative reconstructed trajectory is available
through 2135-09-30 and refuses creation of a new SPK because of its specialized
OSIRIS-REx/Yarkovsky solution. The accepted predecessor is
`sb-101955-118_long.bsp` (JPL#118 / ORX_merged_DE424). The extension uses the
existing Phase-4B RK4/N-body architecture with DE440 planetary perturbations, a
6-hour integration step and 12-hour SPK sampling. Withheld overlap comparison
against the predecessor gave position errors of approximately 0.7 thousand km in
2030, 0.21 million km in 2050, 51.8 million km in 2100 and 222 million km in
2130. The promoted extension therefore carries `uncertainty_km=1,000,000,000` and
`navigation_grade=false`; it is suitable for explicit long-horizon spatial
modeling, not precision navigation.

## Binary and comet semantics

Kleopatra, Patroclus and Didymos are represented as the authoritative numbered
primary/system solutions. Their named companions (Alexhelios/Cleoselene,
Menoetius and Dimorphos) are recorded in manifest semantics but not assigned
invented independent NAIF trajectories. Horizons comet solutions retain their
published non-gravitational models, including the 67P K284/1 and Halley JPL#75
parameters.
