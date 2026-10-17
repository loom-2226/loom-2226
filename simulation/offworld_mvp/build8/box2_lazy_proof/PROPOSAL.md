# Build 8 Box 2 lazy travel-price proof: preregistered experiment

**RESEARCH / NON-CANON / NON-RUNTIME / DRAFT.** New branch from main. Do not merge without approval. PRs #423–#425 and frozen artifacts are excluded.

Objective: demonstrate that the existing on-demand Box 2 geometry can support a narrowly authored, priced, sampled Sponsor ranking for Earth→Mars/Eros/Vesta/Jupiter in 2026 and 2100. Arrokoth and a natural satellite are negative controls. Do not invent travel or prices for unsupported routes.

Implementation limits: one experiment-local authored JSON, one experiment-local Python runner, one result report, and narrow tests if useful. No edits to existing modules or frozen data. Check required kernel assets before any solve; missing means `UNSUPPORTED: REQUIRED_KERNEL_ASSET_MISSING`. Natural satellites remain `UNKNOWN_LOCAL_LEG` and ineligible.

Authored inputs, hashed into run identity and printed verbatim: selected bodies and years, exact departure-date policy (28-day stride plus December 31), optional daily refinement near observed transitions, 10 km/s endpoint limits, 45–1400 day flight range, 0.25-day flight step, pilot 2026 ORBITAL_RECON rate 72.269449528 USD millions per km/s burden, Sponsor valuations, and all other effective policy values. Include source file SHA-256 and installed dependency versions. No fallback route, missing cost, or zero-priced unknown.

Pricing: rate × (departure v-infinity + arrival v-infinity), with printed `HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL` caveat. Sponsor score = authored value minus travel price; rank only feasible priced choices. Geometry cached by qualified source/solver/sampling keys; measure cache hits and solver times. Two deterministic replays must match scientific output and identity hashes; timing telemetry is separate and not part of replay hash.

Stopping conditions: any frozen edit, unrecorded experiment value, flight range outside supported solver bounds, missing scientific calibration, unqualified source, or non-reproducible output. Report source URL, manifest size/hash, and network reachability for missing Phase 4E files without downloading them. Stop at draft PR, no merge.
