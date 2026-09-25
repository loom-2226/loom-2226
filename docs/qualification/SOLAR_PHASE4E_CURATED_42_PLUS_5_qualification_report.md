# Solar Phase 4E — Curated 42+5 qualification

Phase 4E records the locked 42 natural-object and 5 historical-spacecraft cohort
without expanding membership. The machine-readable accounting artifact contains
47 rows and asserts 42 natural, 5 spacecraft, and 47 accounted outcomes.

35 natural objects use JPL/Horizons-generated SPKs through at least
2251-01-01. Nereid uses official NAIF `nep101xl-802` coverage through
17000-01-10. Nix, Hydra, Kerberos and Styx retain explicit PLU060 partial
authority ending 2199-12-29. Proteus, Dactyl and Selam are catalog-only because
no independent authoritative SPK target was available. The interstellar objects
retain their Horizons hyperbolic identities and actual SPK target IDs.

The targeted residual closure subsequently acquired the official New Horizons
PDS OD164 SPK through 2033. Pioneer 10/11 and Voyager 1/2 now have explicit
LOOM empirical extensions from their mission kernels through 2251, and New
Horizons has the same extension after its direct OD164 interval. All five
extensions use solar gravity plus differential DE440 planetary perturbations,
fixed-step RK4, held-out comparisons, conservative uncertainty, and
`navigation_grade=false`.

Proteus, Dactyl and Selam remain catalog-only; Nix, Hydra, Kerberos and Styx
remain partial under PLU060 because no defensible independent 2250 state source
was found.

No trajectory samples are stored in PostgreSQL. Migration 016 stores identity,
source, exact coverage, cohort accounting, spacecraft mission metadata, and
explicit outcome/provenance only.
