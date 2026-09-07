# LOOM 2226 — Governance Adoption Step 1 Inventory & Freeze Audit

**Date:** 7 September 2026  
**Status:** STEP 1 COMPLETE — INVENTORY / RECOVERY ONLY  
**Machine register:** `IN_FLIGHT_BRANCH_REGISTER_2026-09-07.yml`

## Purpose

Capture the exact repository, research, game-development, runtime, release, media and Wayfarer-3D state before implementing repository-wide governance. This step is intentionally non-functional: it records and pins recovery points without changing game behavior, physics, canon content, SQLite bytes, launchers, updater semantics, media assets, or 3D assets.

## Adoption pause

Until Governance Baseline v1.0 reaches its explicit restart gate:

- no gameplay development;
- no Navigator/GIS/HUD functional change;
- no media-library functional change;
- no Wayfarer 3D functional change;
- no runtime/data migration;
- no canon change;
- no physics execution or tuning;
- no schema change;
- no release promotion;
- no rebase/amendment of PR #19.

Existing workstreams are grandfathered. The governance system must adapt to legitimate existing LOOM architecture rather than forcing working software to reorganize itself.

## Critical recovery points

| Area | Live ref | Captured SHA | Recovery ref | Status |
|---|---|---|---|---|
| Main | `main` | `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7` | `archive/pre-governance-2026-09-07-main` | frozen adoption baseline |
| S1 / PR #19 | `research/relational-foundations-deterministic-curvature` | `314efe50875630ba4be720b4097a2ca14075e620` | `archive/pre-governance-2026-09-07-pr19-s1` | exact frozen experiment |
| Stage-A / PR #16 | `research/relational-foundations-matter-induced-prereg` | `b60086d906f63211206502f23458be490902c2df` | `archive/pre-governance-2026-09-07-pr16-stage-a` | preregistered / on hold |
| Foundations / PR #20 | `research/reviewer-constellation-cross-reference` | `2c239a0d67ad356814108f9f3eddf7edbd6539fc` | `archive/pre-governance-2026-09-07-pr20-foundations` | temporary adoption host |
| Navigator/GIS/HUD | `planning/navigator-gis-hud-next-phase-2026-09-06` | `c664c1a66b68e8354295cc2b3b36ff3007e1276a` | `archive/pre-governance-2026-09-07-navigator` | paused |
| Runtime/devops | `integration/runtime-devops-convergence-2026-09-06` | `43fc7cd92a71e0460e551bcc2d6a717ccac796ca` | `archive/pre-governance-2026-09-07-runtime-devops` | paused |
| Phase-6 release branch | `release/phase6-converged-mvp-2026-09-06` | `0e4fd69b984ed8ae3ef35e285fe8a54fc199a141` | `archive/pre-governance-2026-09-07-phase6-release` | retained release baseline |
| Pixel runtime | `release/pixel-runtime-post-migration-2026-09-06` | `f41c22d256ad5a9228cccf71607e0dd7a35ef930` | `archive/pre-governance-2026-09-07-pixel-runtime` | retained recovery baseline |
| Wayfarer 3D | `workstream/wayfarer-3d` | `062bb0a2bfd718305dc0cf92dba9e61bab909d2d` | `archive/pre-governance-2026-09-07-wayfarer-3d` | paused |
| Media lineage | latest observed media commit | `0aeebdb4476a6574e93dc09834242fba54f6a109` | `archive/pre-governance-2026-09-07-media` | paused |

Recovery refs are policy-immutable: they must never be advanced or force-moved.

## Existing release/data baseline

Existing release tag `v0.1.0-runtime-baseline` resolves to commit `97faaab2514835c8f45aee13f5ec6c2ff1b1cc4e` and is additionally pinned by `archive/pre-governance-2026-09-07-release-tag-source`.

Current `main` release manifest is `manifests/release_manifest.json` at blob `06c4ff091611fca86daa1b7f2fe9bebdbda9d15b`.

Recorded data digests:

- `data/LOOM_2226.sqlite3` — SHA-256 `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- `data/LOOM_2226_CIVSTATE.sqlite3` — SHA-256 `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`.
- release asset `LOOM_2226_media.sqlite3` — SHA-256 `286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038`, 473,837,568 bytes.

The media database is a release asset and is therefore tracked by release digest, not inferred from a code branch.

## Runtime path stability

The current deployment topology is frozen for adoption. `deploy/loom_update.py`, Android launchers under `deploy/android/`, and Windows launchers under `deploy/windows/` are recorded in the machine register with their Git blob SHAs.

Governance adoption SHALL NOT move or rename these paths merely to make the repository look cleaner.

## Existing subsystem CI

The Phase-6 game/release lineage already contains phase-specific GitHub Actions for ephemeris qualification, Navigator/GIS phases, campaign execution and Python regression. These are grandfathered subsystem CI. Future repository-wide governance should orchestrate or complement them rather than deleting/replacing them by assumption.

## Authority item discovered, not resolved

The current Wayfarer recovery manifest identifies both:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`, and
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`

as governing Wayfarer sources. The v2.4a file itself declares status `GOVERNING SCHEMATIC / PHYSICAL-PACKAGING AMENDMENT` and names CANON II v2.4 as parent authority.

Step 1 does **not** reinterpret this relationship. Governance Step 3 must explicitly define how governing amendments participate in the authority map, baseline manifest, hashing, supersession, and downstream dependency invalidation.

## Repository governance state at capture

- `main` reported `protected: false`.
- repository rulesets reported none.
- no branch deletion is permitted during adoption.
- no existing workstream is required to rebase onto `main` during adoption.

## Acceptance result

**PASS.** Recovery points exist for all critical active/frozen workstreams; deployed data digests and launcher topology are recorded; PR #19 remains byte-identical at its exact preregistered head; no functional source, canon, database, experiment or asset bytes were modified by Step 1.

## Next permitted action

**Step 2 only:** create the dedicated governance implementation branch from the frozen `main` baseline. No development or physics work resumes yet.
