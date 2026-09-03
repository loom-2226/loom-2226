# LOOM 2226 Initial Baseline Candidate

Status: **STAGING / NOT YET RELEASED**

Validated 2026-09-03.

| Artifact | SHA-256 | Status |
|---|---|---|
| `src/LOOM_Solar_GIS_v0.12.9_RC8_Draggable_Graph_Nodes.py` | `73812ccf8e71d913798e8e3ebb25d64937ba4491e5540d09e5b7e80f646d4f0a` | staged source |
| `src/LOOM_Navigator_MVP_v1.0_RC6_CIVSTATE_Launch_ANDROID.py` | `9374ffda96bce396c55a0458367f7b4449bbca17cfb7da93984246f1387428ed` | corrected staging candidate |
| `data/LOOM_2226.sqlite3` | `ff5b1b6c4e971844847cdfe5b1c6da7a0e4081984b043e7c655345ad7a1a8267` | **UPLOAD REQUIRED** |
| `data/LOOM_2226_CIVSTATE.sqlite3` | `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560` | **UPLOAD REQUIRED** |

CIVSTATE schema lock: `1.2-runtime`.

Navigator correction: uploaded RC6 locked CIVSTATE SHA-256 `cd83bc3b70f40b8150161b9636c7ff7de4c84d9ba79756c4bbf9bcd19f7bc12d`; staging candidate locks the validated database hash `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`. No other source change was introduced.

Self-test result for corrected Navigator candidate:

- MVP state/transaction/job/mass/history/guard suite: PASS
- K1 provider/live-binding/execution guards: PASS
- CIVSTATE hash/schema/token/context/read-only suite: PASS

Known packaging dependency: world data references a sibling `LOOM_2226_media.sqlite3`; media payload strategy must be closed before the first complete release.
