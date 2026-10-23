# Corrected priced-window ephemeris extension: active checkpoint

TEST_ONLY / NON-CANON / PR427. **Not complete. No campaigns run.**

## Horizon

The last independently priced departure is 2035-12-31 00:00 UTC. Add 8,000 days: **2057-11-25 00:00 UTC**. Campaign years 2036–2226 hold the 2026 price level and do not require new trajectory departures. Numeric lattice runs from 2026-01-01 to 2057-11-25 at 0.25-day spacing (46,605 samples per body).

## Kernel recovery

- ARROKOTH: `/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020/arrokoth_2026_2251.bsp`, 3,986,432 bytes, SHA-256 `9c0146d456a9762fa16345e1937da523b333718c3f87698060984273f7d1d2ea`; **EXISTS; matches committed VM manifest**.
- DAVIDA: `/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020/davida_2026_2251.bsp`, 4,059,136 bytes, SHA-256 `6cafbc1855f375e625399dcd8fa9d15484e492492179dadcacc84a89354a4a12`; **EXISTS; matches committed VM manifest**.
- Both corresponding `/home/ubuntu/loom_solar_assets/kernels/spk/phase4e/` registered paths are **ABSENT**. No copy, symlink, source override, or registry modification was made. Registered-source validation excludes them pending explicit source-resolution work.

## Resource-constrained table builder

`build_all.py` runs `build_one.py` as a separate subprocess per body. Each writes a `.npy` table directly via memory mapping, in 512-row chunks. Each chunk is independently checked against scalar SPICE at its first, middle and last sampled lattice epochs using exact bitwise equality, not tolerances. Failed tables are deleted; successful tables remain on the VM and each body has a JSON result. A sampled scalar/vector SPICE equality check is the same check pattern as the previous planetary tables; it is **not an independent physical ephemeris model**.

The VM has 3,832 MiB RAM and zero swap. Initial MemAvailable was 1,155 MiB. Logs: `build_all.log` (VM only); per-body `results/*.json` (VM only). Work is ongoing, not certified as complete.

At this checkpoint: three PASS tables (AMUN, ARIEL, ASTEROID_6178), three exclusions for missing registered kernels (APOPHIS, ARROKOTH, ATLAS3I), BENNU still processing. The required seven registry-gap bodies will be excluded, not fabricated. No user-prohibited download, install, or pre-existing-file edit was performed.

## Remaining steps

Step 1 full 90-body disposition and Step 2 full independent verification **in progress**. Step 3 all-body four-limit repricing and Step 4 four campaign runs **not started**. Route 1 and Ceres controls **not newly run**. Database SHA-256 before and after the checkpoint: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
