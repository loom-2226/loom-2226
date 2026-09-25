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

Pioneer 10, Pioneer 11, Voyager 1 and Voyager 2 use official mission SPKs as
historical/forecast partial authority; New Horizons is catalog-only because no
accepted local mission SPK product was available. Spacecraft are non-navigation-
grade and are never extended to 2250 by assertion.

No trajectory samples are stored in PostgreSQL. Migration 016 stores identity,
source, exact coverage, cohort accounting, spacecraft mission metadata, and
explicit outcome/provenance only.
