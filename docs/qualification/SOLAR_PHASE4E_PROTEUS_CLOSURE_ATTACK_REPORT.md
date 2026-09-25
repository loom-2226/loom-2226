# Solar Phase 4E — Proteus closure attack

## Result

Proteus (`PROTEUS`, NAIF 808) is **PARTIAL**, not 2250-qualified.

The authoritative source search found the current official NAIF release
`NEP098 Part 3`. Its actual SPK inventory contains targets 807, 808, 814 and
899, plus the planetary support bodies. Target 808 is directly covered from
`1799-12-31T23:59:18.816Z` through `2199-12-30T23:58:50.816Z` in
`ECLIPJ2000`, km and km/s. The source is the July 2026 NEP098 ephemeris-version
25 SATORBINT integrated Neptune-system solution using DE442.

Serious candidates audited:

| Product | Target 808 | Result |
|---|---:|---|
| `nep097.bsp` | no | Neptune/Triton-era product; no Proteus segment |
| `nep101xl-802.bsp` | no | Nereid-only long product |
| `nep101xl.bsp` | no | targets 809–813 only |
| `nep104.bsp` | no | targets 809–813 and support bodies |
| `nep105.bsp` | no | Nereid-only updated product |
| `nep098_part-3.bsp` | yes | accepted direct partial authority |

The previous catalog-only outcome was therefore corrected to `PARTIAL`; no
2250 claim was made.

## Propagation decision

A reduced governed experiment was attempted using the existing LOOM numerical
architecture: Neptune-system GM, Neptune J2, solar tidal perturbation, Triton
and inner-moon point-mass perturbations, ECLIPJ2000, km/km/s, deterministic RK4
with 300-second steps. It was initialized from NEP098 states and back-tested
against withheld NEP098 epochs.

The one-year held-out position error was approximately 228,000 km with
approximately 14.8 km/s velocity error. The error is dominated by orbital
phase loss and is not a defensible basis for a 2250 arbitrary-epoch state.
The model was rejected rather than promoted. Reproducing SATORBINT would
require its fitted force-model implementation and parameters, which are not
provided as a runtime-authoritative public product in the acquired kernel.

## Governance outcome

Migration `018_solar_proteus_nep098_partial.sql` records the source, hash,
identity, parent semantics, exact coverage and `EPHEMERIS_PARTIAL` capability.
The resolver succeeds for in-range direct epochs and fails closed after the
direct boundary. No trajectory samples are stored in PostgreSQL.
