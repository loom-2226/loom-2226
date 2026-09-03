# LOOM 2226 — GIS Phase 6 Campaign Execution v1.0

**Status:** Phase-6 implementation / Gate-C qualification reference  
**Branch:** `feature/gis-navigator-convergence`  
**Governing parent:** `LOOM_2226_GIS_Navigator_Convergence_Architecture_and_Work_Plan_v1.0.md`

## 1. Phase decision

Phase 6 crosses the persistence boundary without moving authority into GIS.

The operational chain is:

```text
GIS interaction
  -> committed FlightPlan
  -> Navigator execute_flight()
  -> FlightExecutionResult / authoritative arrival state
  -> CampaignExecutionService
  -> FLIGHT_ARRIVED history record
  -> atomic canonical state replacement
  -> GIS planning session rebinds to persisted arrival state
```

GIS performs no flight math and does not write campaign state directly.

## 2. Authorities

- **Navigator:** route discovery, flight compilation, deterministic runtime, mass ledger, terminal boundary, authoritative arrival-state transition.
- **Campaign service:** stale-state guard, history append, state persistence, rollback of primaries on commit failure, read-back verification.
- **GIS:** selection, preview, planning commit, explicit execute command, display refresh.

There is one authoritative `location_token`, one authoritative `epoch_utc`, and one campaign revision lineage.

## 3. Commit semantics

Phase-5 `COMMIT` remains a planning lock only. It does not advance time or state.

Phase-6 `EXECUTE` is a separate explicit action. It is accepted only when:

1. a route has been discovered, previewed and committed;
2. the plan has a compiled Navigator flight;
3. the on-disk `LOOM_STATE_V1.json` is byte-equivalent at the data-model level to the planning snapshot;
4. Navigator returns `ARRIVED_HOLD` and delegates persistence to `CAMPAIGN`;
5. the arrival revision is exactly current revision + 1;
6. arrival provenance identifies the committed flight, departure state, plan hash and runtime hash.

If the canonical state changed after planning, execution is rejected and the user must rediscover/recommit.

## 4. Campaign transaction

`LegacyCampaignExecutionService` deliberately reuses frozen RC6.1 campaign machinery:

- `_validate_state`
- `HistoryLedger`
- `_outcome_summary`
- `_atomic_save`
- existing `FLIGHT_ARRIVED` record semantics

The service snapshots the live state and history primaries before the commit. If the history append or state replacement/read-back fails, those primaries are restored to their exact pre-commit bytes.

On success:

- one `FLIGHT_ARRIVED` record is appended;
- one new state revision is persisted;
- location advances once;
- epoch advances once;
- remass/wet mass come from Navigator's authoritative mass ledger;
- `last_flight` preserves flight, plan and runtime provenance.

The legacy Navigator HTML output is not campaign authority and is not written by the Phase-6 campaign service.

## 5. GIS post-arrival behavior

After successful execution the planning session is rebound to the persisted arrival state. Candidates, preview and committed selection are cleared. The executed route is returned as a historical GIS overlay and the new planning origin is the arrival `location_token`.

This means a second `EXECUTE` cannot replay the same in-memory plan. A new flight requires a new destination discovery and planning commit from the new campaign state.

## 6. Contracts

Planning remains additive/backward-compatible under:

```text
LOOM_GIS_FLIGHT_PLANNING_V1
```

Phase 6 adds:

```text
execution_available
last_execution
```

Persistent execution result contract:

```text
LOOM_CAMPAIGN_EXECUTION_V1
```

Minimum execution fields include flight identity, state IDs/revisions, origin/destination, departure/arrival epochs, remass before/after, state/history paths, history record identity and final canonical state.

## 7. Gate C qualification

Gate C requires real frozen Navigator infrastructure, not mocks alone. Two related but distinct checks are deliberately kept separate:

- **Gate A** remains the byte-for-byte frozen physics oracle. The Phase-6 workflow reruns Gate A first and requires the recorded frozen runtime SHA to reproduce exactly.
- **Gate C** exercises a new GIS-originated planning request. Because its request identity/provenance envelope is newly generated, its whole canonical runtime SHA is a run artifact and is not required to equal the historical replay SHA. Its runtime SHA must instead remain internally consistent through Navigator execution, campaign persistence and `last_flight` provenance.

The Gate-C qualifier:

1. downloads the frozen Pixel pre-clean runtime archive;
2. reruns Gate A and proves the frozen physics oracle independently;
3. derives the preserved Ceres departure snapshot from authoritative campaign history;
4. creates an isolated transactional runtime;
5. runs real offline Sequence-H route discovery from the archived cache;
6. previews and commits through `GISFlightPlanningSession`;
7. executes via extracted Navigator service;
8. persists via campaign service;
9. verifies the state file and GIS session agree;
10. verifies revision increments exactly once;
11. verifies one and only one `FLIGHT_ARRIVED` record;
12. verifies runtime provenance survives unchanged from the new Gate-C solve into the persisted campaign record;
13. rejects duplicate execution after arrival.

The live HTTP Gate-C smoke performs the same `discover -> preview -> commit -> execute` sequence against the running converged GIS server and verifies the historical overlay and persisted campaign files.

## 8. Gate C acceptance

**PASS only when all are true:**

- Python unit regression remains green;
- the frozen Gate-A byte oracle still reproduces exactly;
- prior Phase 3 / Phase 4 / Phase 5 qualifications remain green;
- Phase-6 unit tests pass;
- real frozen-infrastructure Ceres->Mars execution passes;
- live GIS HTTP execution passes;
- canonical state advances exactly once;
- exactly one `FLIGHT_ARRIVED` record is created;
- duplicate execute is rejected;
- Gate-C runtime provenance is preserved across Navigator -> campaign persistence.

When these conditions hold, Gate C — Operational Convergence — is closed.
