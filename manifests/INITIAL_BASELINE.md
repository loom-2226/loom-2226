# LOOM 2226 Initial Runtime Baseline Candidate

Status: **STAGING / RELEASE CANDIDATE**

Validated 2026-09-03.

| Artifact | SHA-256 | Distribution | Status |
|---|---|---|---|
| `src/LOOM_Solar_GIS_v0.12.9_RC8_Draggable_Graph_Nodes.py` | `73812ccf8e71d913798e8e3ebb25d64937ba4491e5540d09e5b7e80f646d4f0a` | repository | staged / validated |
| `src/LOOM_Navigator_MVP_v1.0_RC6.1_CIVSTATE_Launch_ANDROID.py` | `d2cdf9baa38ca314e7eb0ecb0cf5e746d0e39c13e77e1a3f41b1093c6a59200b` | repository | staged / validated |
| `data/LOOM_2226.sqlite3` | `ff5b1b6c4e971844847cdfe5b1c6da7a0e4081984b043e7c655345ad7a1a8267` | repository | staged / validated |
| `data/LOOM_2226_CIVSTATE.sqlite3` | `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560` | repository | staged / validated |
| `LOOM_2226_media.sqlite3` | `286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038` | GitHub Release asset `542245032` | uploaded / pinned |

Media payload size: `473837568` bytes.

CIVSTATE schema lock: `1.2-runtime`.

Navigator RC6.1 contains the corrected CIVSTATE SHA-256 lock for the validated database. No other functional source change was introduced from the tested RC6 candidate.

Validation status:

- Navigator MVP state/transaction/job/mass/history/guard suite: PASS
- Navigator K1 provider/live-binding/execution guards: PASS
- Navigator CIVSTATE hash/schema/token/context/read-only suite: PASS
- Solar GIS RC8 compile: PASS
- Updater v0.3 regression suite: PASS (complete five-artifact install, validation, unchanged detection, backup, release-asset routing, size/hash fail-closed)

Deployment rules:

- Mutable runtime/campaign state is never replaced by the updater unless explicitly requested.
- Canonical code and baseline databases are SHA-256 verified before installation.
- Large media payloads are distributed as release assets rather than ordinary Git blobs.
- The media release asset is pinned by GitHub asset ID, exact byte count, and SHA-256.
- Authentication credentials remain local to each device and are never committed.
