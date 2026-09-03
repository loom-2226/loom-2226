# LOOM 2226 — Runtime Diagnostic Telemetry and Forensic Debugging Plan v1.0

**Status:** Architecture/design plan only. Not implemented.  
**Repository:** `loom-2226/loom-2226`  
**Branch:** `feature/gis-navigator-convergence`  
**Date:** 2026-09-04  
**Purpose:** Define a cross-platform debugging/forensic mode that can capture correlated evidence across the LOOM runtime without becoming a second authority or altering simulation behavior.

## 1. Executive decision

LOOM should eventually gain an explicit **diagnostic telemetry mode** capable of recording a causally correlated trail across browser/HUD interaction, JavaScript rendering, HTTP, GIS adapters, Navigator services, campaign state, SQLite, process/stdout/stderr, and visual evidence.

The diagnostic system must be **observation-only**. It may record, correlate, hash, package, and upload evidence. It may never calculate navigation truth, mutate campaign state, advance game time, alter SQL data, change UI state, or become a persistence authority.

Do **not** stream every event directly to GitHub. The target design is **local-first append-only spooling with asynchronous/batched publication of forensic sessions**.

This plan is intentionally deferred while Phase 6 physical qualification remains open.

## 2. Architectural fit

This design follows the existing LOOM authority model:

- GIS remains the sole visual application;
- Navigator remains numerical navigation authority;
- Campaign Runtime remains mutable-state and game-time authority;
- SQLite/runtime stores remain persistence authorities within their defined roles;
- diagnostic telemetry observes those layers but owns none of their truth.

Conceptual architecture:

```text
                    LOOM RUNTIME
                         |
        +----------------+----------------+
        |                |                |
      Browser          Python           SQLite
      / HUD            services         / state
        |                |                |
        +--------- diagnostic events -----+
                         |
                LOCAL DEBUG SIDECAR
                  append-only spool
                         |
          +--------------+-------------+
          |                            |
   searchable metadata           binary evidence
   JSONL / manifest / MD         screenshots / bundles
          |                            |
          +-------- optional GitHub publication
```

## 3. Trace model

Use an **OpenTelemetry-shaped internal model** even if no external OTel collector is deployed.

Minimum correlation identities:

```text
session_id
trace_id
span_id
parent_span_id
request_id
action_id
flight_id / route_id when applicable
campaign_id
state_id
revision
source_git_sha
platform
```

A single user action should be traceable end-to-end, for example:

```text
ui.plan_details
  -> http.POST /flight-planning/preview
     -> gis.preview
        -> navigation.compile_flight
           -> sequence_h.target_determinism_gate
           -> trajectory payload normalization
        -> route_layer.build
        -> navigation_overlay.build
  -> renderer.route_draw
  -> diagnostic.snapshot
```

The implementation should support W3C-style trace propagation across browser -> HTTP -> Python boundaries rather than inventing incompatible per-layer IDs.

## 4. Diagnostic clocks

Every diagnostic event should record three time concepts where applicable:

1. **wall-clock UTC** — real-world debugging chronology;
2. **monotonic process time** — reliable ordering and duration measurement;
3. **authoritative LOOM game epoch + state revision** — copied from campaign authority.

Wall-clock and monotonic telemetry must never influence the authoritative game clock.

## 5. Evidence by layer

### 5.1 Browser / HUD

Capture semantic events, not raw touch noise:

- control/action identifier;
- click/tap intent;
- selected entity;
- NAV/ATLAS mode;
- contextual drawer state;
- viewport dimensions;
- camera state/intention;
- fetch request start/end/status;
- JS exceptions;
- unhandled Promise rejections;
- significant UI-state transitions.

Do not log every pointer move or render frame by default.

### 5.2 Renderer

Record enough to distinguish missing truth from display failure:

```text
route_id
geometry_mode
authoritative_sample_count
ordinary_sample_count
points_consumed
points_projected
points_clipped
route_world_bbox
route_screen_bbox
camera_bbox
fit_route_decision
ship_sample_index
phase markers rendered
```

This is especially important for trajectory bugs where a correct backend payload can otherwise be mistaken for a camera/rendering defect.

### 5.3 HTTP / local API

Capture:

- method/path;
- trace/request ID;
- status;
- elapsed duration;
- safe request/response summary;
- relevant contract/version;
- body hash where useful.

Authorization headers, cookies, credentials, and GitHub tokens must be redacted before disk.

### 5.4 GIS adapters / canonical contracts

Capture adapter decisions and provenance:

- input contract/version;
- output contract/version;
- authoritative source type;
- selected accessor path or structural resolution result;
- missing/inapplicable fields;
- fallback/compatibility seam used;
- validation outcome;
- payload hashes/byte sizes instead of uncontrolled payload dumps.

### 5.5 Navigator

Capture domain-stage evidence without exposing or duplicating physics authority:

- normalized request identity;
- candidate/route/flight IDs;
- determinism-gate stage boundaries;
- returned object/container types;
- declared payload versions/codecs;
- validation result;
- sample counts;
- payload hashes and byte lengths;
- explicit reason when authoritative geometry is absent.

### 5.6 Campaign state

Record state identities, not a competing mutable copy:

```text
state_id
revision
state_hash
epoch_utc
location_token
commit/reject/idempotency result
revision_before/revision_after
```

Consequential full-state snapshots should be opt-in evidence and always marked as copies of authority, never authority themselves.

### 5.7 SQLite

Capture operational metadata:

- DB identity/path/schema version/hash where practical;
- transaction begin/commit/rollback;
- query category/table names;
- duration;
- row count;
- SQLite error code/exception.

Do not record arbitrary SQL literal values or bind parameters by default. Sensitive/query parameter capture must be explicit and redacted.

### 5.8 Process / terminal

Capture:

- startup manifest;
- Python/runtime versions;
- stdout/stderr;
- stack traces;
- process/subprocess exit codes;
- runtime paths and dependency versions relevant to qualification.

## 6. Local-first spool

Target structure:

```text
state/debug/
  D20260904T062200Z-PIXEL-xxxx/
      manifest.json
      events.ndjson
      http.ndjson
      ui.ndjson
      db.ndjson
      stderr.log
      screenshots/
      evidence/
```

Requirements:

- append-only where practical;
- bounded/ring-buffer mode for long sessions;
- crash-safe enough to preserve recent events;
- diagnostics failure must not fail gameplay;
- GitHub/network availability must have zero effect on runtime execution;
- upload occurs later and asynchronously.

## 7. Diagnostic levels

Recommended modes:

### OFF

No meaningful diagnostic overhead beyond ordinary production logging.

### ERROR

Maintain a bounded local ring buffer. Preserve/upload only around significant exceptions or failed invariants.

### DEBUG

Capture semantic UI actions, API/service spans, state transitions, renderer decisions, DB summaries, and selected screenshots/checkpoints.

### TRACE

Temporarily capture richer structural diagnostics, payload/container probes, detailed adapter decisions, and additional evidence. TRACE should be deliberate and short-lived.

## 8. Screenshots and UI evidence

Visual evidence is desirable, but distinguish two capabilities.

### 8.1 Canvas/map evidence

The browser can capture the GIS canvas directly as PNG/WebP evidence. This should be cross-platform and does not require desktop tooling.

### 8.2 Full HUD evidence

A full rendered viewport including DOM panels may require a dedicated browser capture implementation. Chrome DevTools Protocol is a strong option during Windows/ADB-assisted qualification but should not become a required Pixel runtime dependency.

Until a robust full-viewport capture exists, every screenshot checkpoint should be accompanied by a **machine-readable UI snapshot** containing:

```text
viewport dimensions
visible controls
control text
DOM bounding rectangles
selected entity
NAV/ATLAS mode
drawer state
camera state
route geometry mode
sample/projected/clipped counts
```

The UI snapshot is first-class evidence, not merely a fallback for the image.

## 9. GitHub publication model

Do not use the source repository as a high-frequency telemetry bus.

Preferred future target:

```text
loom-2226/loom-diagnostics   # private
```

Store small searchable artifacts in Git:

```text
session_manifest.json
summary.md
errors.ndjson
trace_excerpt.ndjson
ui_snapshot.json
```

Store large/binary evidence outside ordinary Git history, preferably as release/workflow/other GitHub binary assets:

```text
full-session.zip
browser screenshots
large terminal logs
selected payload evidence
optional DB snapshot
```

A failed/manual session may optionally create a GitHub issue that links the forensic session. Normal sessions should not create issues.

Before freezing this architecture, experimentally verify that private screenshot/binary evidence uploaded through the chosen GitHub mechanism is readily inspectable through the available ChatGPT/GitHub connector workflow.

## 10. Security and privacy

Redact **before writing to disk**, not only before upload.

Never persist in diagnostic logs:

- GitHub/token secrets;
- Authorization headers;
- cookies/session credentials;
- passwords;
- private API secrets.

Sensitive user/game data should be captured only when required by a specific diagnostic mode.

Every evidence file should be hashed. The session manifest should contain evidence hashes and source/runtime provenance so a debug packet is internally verifiable.

## 11. Session manifest

Minimum manifest content:

```text
diagnostic_schema_version
session_id
started_wall_utc
ended_wall_utc
platform / device
OS version
Python version
browser/runtime version
source_git_sha
LOOM app/runtime version
navigation contract version
campaign contract version
DB schema versions
DB/source hashes where practical
campaign state_id/revision/hash at start
campaign state_id/revision/hash at end
redaction policy version
evidence file hashes
termination reason
```

## 12. Performance rules

- diagnostics must be asynchronous where possible;
- no GitHub network operation occurs on a gameplay critical path;
- no screenshot on every frame/action;
- no raw SQL row/event flood;
- use sampling and semantic checkpoints;
- TRACE overhead is acceptable only when explicitly enabled;
- if the diagnostics subsystem raises an exception, it must fail open and LOOM continues.

## 13. Proposed implementation phases

Deferred until current Phase 6 convergence work is closed.

### D0 — evidence-contract prototype

- define `LOOM_DIAGNOSTIC_EVENT_V1`;
- define trace/session identifiers;
- implement local JSONL writer with redaction;
- prove no authority mutation.

### D1 — Python service tracing

- GIS HTTP;
- planning adapters;
- Navigator service boundaries;
- campaign transitions;
- SQLite summaries;
- stdout/stderr capture.

### D2 — browser correlation

- propagate trace/request IDs;
- semantic UI events;
- renderer metrics;
- global JS error/unhandled rejection capture;
- local POST/beacon ingestion endpoint.

### D3 — visual evidence

- canvas screenshot checkpoints;
- UI DOM-state snapshot;
- error/manual screenshot triggers;
- evaluate full-HUD capture path.

### D4 — forensic packaging

- manifest + hashes;
- bounded evidence bundle;
- export command/button;
- manual local inspection.

### D5 — GitHub publication experiment

- separate private diagnostics repository;
- searchable small artifacts;
- binary asset strategy;
- verify ChatGPT connector can inspect private visual evidence efficiently.

### D6 — qualification and default policy

- Pixel and Windows same behavior;
- performance/size limits;
- redaction tests;
- diagnostics-failure isolation tests;
- document when ERROR/DEBUG/TRACE should be used.

## 14. Acceptance criteria

A future diagnostic implementation is acceptable only if:

1. one user action can be followed browser -> HTTP -> GIS -> Navigator/campaign -> persistence -> renderer;
2. route/payload loss can be localized without manually copying terminal logs;
3. screenshots/UI snapshots can be tied to exact trace/state/source identities;
4. no diagnostic component can mutate authoritative state;
5. diagnostics can be fully disabled;
6. diagnostics failure cannot stop or alter LOOM;
7. secrets are redacted before local persistence;
8. Pixel and Windows use one logical diagnostic architecture;
9. GitHub publication is batched and non-blocking;
10. retained evidence is useful to both a human developer and an LLM debugging through the GitHub connector.

## 15. Immediate project decision

**Do not implement this during the current Phase 6 trajectory/HUD qualification.** Preserve it as a subsequent engineering work package.

Resume Phase 6 at the current blocker: live GIS planning reaches authoritative Navigator execution but the preview route is still arriving at the GIS route layer as `AUTHORITATIVE_PHASE_ANCHORS_ONLY`, while the frozen qualification route proves Sequence-B mixed geometry with authoritative samples. The current diagnostic probe should be used to identify the exact live determinism-gate payload shape before any further adapter changes.
