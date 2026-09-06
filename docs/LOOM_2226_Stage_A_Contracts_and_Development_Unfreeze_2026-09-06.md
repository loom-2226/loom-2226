# LOOM 2226 — Stage A: Contracts and Development Unfreeze

Date: 2026-09-06  
Branch: `planning/navigator-gis-hud-next-phase-2026-09-06`  
Baseline preserved: `release/runtime-devops-gis-baseline-2026-09-06` at `43fc7cd92a71e0460e551bcc2d6a717ccac796ca`

## Status

Stage A implementation is complete in Git pending repository CI and physical Pixel development-sync qualification.

The accepted release baseline remains frozen and unchanged. Development proceeds on the planning branch.

## Why an explicit development unfreeze was required

The accepted release updater is intentionally reproducible and pinned:

- `manifests/release_manifest.json` names a fixed `source_ref`.
- runtime artifacts have exact digest pins.
- `deploy/loom_update.py` rejects a requested ref that differs from the manifest `source_ref`.

That is correct for release deployment but blocks iterative next-phase development: pulling a newer Git branch into `/storage/emulated/0/Documents/LOOM_GIT` does not by itself change the active APP runtime under `/storage/emulated/0/Documents/LOOM/runtime`.

Stage A therefore does **not** weaken the release updater. It adds a separate development activation path.

## Development-source authority

Git working branch:

`planning/navigator-gis-hud-next-phase-2026-09-06`

Pixel checkout:

`/storage/emulated/0/Documents/LOOM_GIT`

Active Pixel APP root:

`/storage/emulated/0/Documents/LOOM/runtime`

Campaign and canonical DATA remain outside development-sync authority.

## Development sync

New tool:

`deploy/loom_dev_sync.py`

Purpose:

- copy mutable application sources from the local Git checkout into `LOOM_APP_ROOT`;
- preserve path structure;
- skip unchanged files by SHA-256;
- atomically replace changed application files;
- back up replaced files under `.loom_dev_backups/<UTC timestamp>/`;
- record `.loom_dev_state.json` with Git branch/commit when available.

Hard exclusions:

- no `data/` discovery or installation;
- no campaign state/history/SQLite discovery or installation;
- no deletion of runtime files;
- no modification of the pinned release updater or its authority model.

Allowlisted development source surfaces:

- `src/loom/**` application `.py`, `.js`, `.html`, `.css`, `.json` files;
- top-level `src/loom_*.py` runtime entry/core files;
- `web/**` application assets;
- Android/Windows deployment launchers.

The allowlist is intentionally application-focused. Canon, research, engineering documents, data databases, campaign state, credentials, and unrelated storage are not sync targets.

## Pixel activation procedure

From Termux/Pydroid-capable shell with the existing Git checkout:

```bash
cd /storage/emulated/0/Documents/LOOM_GIT

git fetch origin
git switch planning/navigator-gis-hud-next-phase-2026-09-06
git pull --ff-only origin planning/navigator-gis-hud-next-phase-2026-09-06

python deploy/loom_dev_sync.py status
python deploy/loom_dev_sync.py sync
```

Expected header:

```text
LOOM DEV SOURCE: /storage/emulated/0/Documents/LOOM_GIT
LOOM APP ROOT:   /storage/emulated/0/Documents/LOOM/runtime
CAMPAIGN/DATA:   EXCLUDED
```

After sync, existing migrated Pixel launchers continue to launch from APP root; they now consume the planning-branch application files that were activated by development sync.

Rollback remains available through:

1. `.loom_dev_backups/` for files replaced by development sync;
2. the preserved release branch / pinned release updater for a full accepted-runtime reinstall;
3. retained `/storage/emulated/0/Download/LOOM_TEST` until separately authorized for removal.

## Stage-A contracts

New package:

`src/loom/application/`

Contracts introduced:

- `CampaignClockState`
- `SpatialState`
- `TrajectorySegment`
- `TrajectorySolution`
- `LoomRouteSolution`
- `FlightPlaybackState`
- `LoomSessionState`

These are cross-application contracts. They do **not** replace the existing navigation-domain contracts in `src/loom/navigation/contracts.py` during Stage A.

### Authority intent

`CampaignClockState`

- represents authoritative campaign ID, revision, and game epoch;
- is independent of whether persistence is current JSON/history or future campaign SQLite;
- must not be replaced by playback or historical-query time.

`SpatialState`

- requires explicit XYZ position and velocity;
- requires an explicit reference frame and epoch;
- carries provenance/navigation-grade/uncertainty metadata without forcing current consumers to adopt every field immediately.

`TrajectorySolution`

- is stamped with campaign revision and solution epoch;
- is expressed in an explicit reference frame;
- carries time-bounded segments and optional sampled spatial states;
- provides the stable future bridge from Navigator physics into GIS/HUD 3D rendering.

`LoomRouteSolution`

- is deliberately relational and distinct from a metric-space trajectory;
- supports directional relational edges, confidence, endpoint geometry, timing, and terminal-state requirements;
- does not create a false physical path through intervening light-years.

`FlightPlaybackState`

- is explicitly non-authoritative;
- tracks animation/replay cursor, playback rate, and camera mode over an already-authorized flight.

`LoomSessionState`

- links application/conversation context to campaign revision/epoch;
- does not own campaign truth.

## Tests

New unit tests cover:

- campaign-clock timezone/revision validation;
- explicit 3-vector spatial states;
- campaign-stamped trajectory solutions;
- relational Loom-route semantics and confidence bounds;
- playback state/camera normalization;
- development-sync application allowlisting;
- campaign/data exclusion;
- development-sync backup behavior.

Local Stage-A focused result before Git commit:

`7 tests passed` under the repository's `unittest` style.

The GitHub regression workflow is also updated on the planning branch to:

- run on pushes to `planning/navigator-gis-hud-next-phase-2026-09-06`;
- include both `src` and `deploy` in `PYTHONPATH`;
- compile `src` and `deploy`;
- run the complete existing `unittest` regression suite.

## Preservation constraints

Stage A intentionally does **not**:

- promote campaign SQLite to authority;
- modify campaign JSON/history semantics;
- change preview/commit/execute behavior;
- change Mars → Ceres accepted physics;
- modify canonical data databases;
- change runtime roots;
- alter the pinned release manifest to point at a development branch;
- delete the accepted frozen branch or rollback source.

## Stage-A exit gate

Stage A is closed when all of the following are true:

1. planning branch contains the cross-application contracts;
2. development sync is present and authority-guarded;
3. full GitHub Python regression suite passes on the planning branch;
4. Pixel checkout is switched to the planning branch;
5. `loom_dev_sync.py status` shows the expected APP root and campaign/data exclusion;
6. `loom_dev_sync.py sync` completes successfully;
7. existing GIS/Navigator launch remains functional on Pixel after development activation.

Only items 4–7 require physical action on the Pixel. No campaign flight should be executed merely to qualify Stage A; the accepted Phase-6 transition remains preserved for later functional gates.

## Next stage

Stage B is persistent campaign clock implementation behind the `CampaignClockState` contract. It should first adapt the current authoritative JSON/history campaign service without promoting shadow campaign SQL. Campaign SQLite promotion remains a later explicit gate.
