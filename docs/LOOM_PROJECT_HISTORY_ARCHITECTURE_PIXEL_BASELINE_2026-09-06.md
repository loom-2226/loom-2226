# LOOM 2226 — Project History, Architecture, and Pixel Runtime Baseline

**Baseline date:** 2026-09-06  
**Status:** Project continuity / architecture record. Descriptive, not an independent canon authority.  
**Repository:** `loom-2226/loom-2226`

This document preserves the working project history and architecture accumulated through the LOOM 2226 development threads, together with the known runtime state of the Pixel as of this baseline. Where a local-device fact has not been directly enumerated, this document says so rather than pretending GitHub has inspected the phone filesystem.

---

## 1. Project purpose

LOOM 2226 is a hard-science-fiction world simulation and interactive navigation/GIS system. It combines:

- authoritative world/canon data;
- derived historical/economic/demographic/transport simulation;
- solar-system spatial and ephemeris data;
- ship engineering and flight planning;
- a browser-based Solar GIS and link-analysis surface;
- image/media assets tied to canonical entities;
- CIVSTATE/runtime state;
- a developing epistemic/intelligence architecture for player/NPC knowledge, claims, provenance, confidence, deception, and incidents/events.

The project deliberately separates **authority** from **derived/runtime presentation**. Canon and authoritative SQL remain the source of truth; browsers, reports, snapshots, caches, and visualizations are inspection/runtime surfaces.

---

## 2. Canon and provenance discipline

The repository contains dedicated areas for canon, engineering, research, governance, characters, geometry, data, source code, tests, deployment, manifests, documentation, and web assets.

The current production WORLD database lineage is schema 12. The working authoritative data set includes entity/spatial records and associated demographic, economic, transport, authority, infrastructure, knowledge, and media metadata. CIVSTATE is maintained separately for runtime/civil-state material.

Important project rule: derived values must be traceable to authoritative inputs and models. Ephemeris is used as spatial/accessibility input rather than as an arbitrary population multiplier. Historical propagation work from 2026 toward 2226 is intended to produce defensible derived numbers rather than manually decorating the setting.

Key governing/source documents developed during the project include the Foundational Canon, Canon I/II/III v2.4 family, Earth/Solar System Canon Atlas, Shipbuilding Engineering Manual, Ship Operations/Courier Compendium, Institutions & Organizations Register, Xenoarchaeology Terminal Mobilization Canon, Core Mechanics, Technical Paper Series, HUD/Navigator architecture/work plans, runtime architecture/delivery workflow, and validation/hash manifests.

---

## 3. Runtime/data architecture

### 3.1 Authoritative WORLD SQLite

Primary file: `data/LOOM_2226.sqlite3`.

Important entity/media linkage observed in production code:

- `entities.entity_id` is the spatial/world entity key.
- `knowledge_entities.noun_id` is the knowledge noun key.
- `knowledge_entities.spatial_entity_id` links a knowledge noun to a spatial entity.
- `image_assets.entity_id` links image metadata to `knowledge_entities.noun_id`.
- current approved hero selection uses `asset_role='HERO'`, `is_current=1`, and `review_status='APPROVED_REFERENCE'`.

The browser/GIS should use schema-driven access rather than spreading hard-coded payload names throughout consumers.

### 3.2 CIVSTATE SQLite

Primary file: `data/LOOM_2226_CIVSTATE.sqlite3`.

CIVSTATE is a separate runtime/civil-state authority surface and is included by the Media + Canon Browser inspector when direct entity-keyed records exist.

### 3.3 MEDIA SQLite

Primary runtime file: `data/LOOM_2226_media.sqlite3`.

The media database is large and is distributed as a GitHub Release asset rather than a normal Git blob. At this baseline:

- release tag: `v0.1.0-runtime-baseline`
- release asset id: `542245032`
- release id: `381754456`
- size: `473,837,568` bytes
- SHA-256: `286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038`

`media_assets` stores original and thumbnail BLOBs. The GIS/media browser preferentially serves the thumbnail where available and can serve the original on request.

At the successful Pixel media-browser test immediately before this archive, the UI reported **182 assets, 182 thumbnails, 182 current**.

### 3.4 Ephemeris/cache/runtime state

Ephemeris and generated runtime state are treated differently from authoritative source. Local state/caches are preserved by deployment rather than blindly overwritten. The release manifest preserve list includes:

- `LOOM_STATE_V1.json`
- `LOOM_STATE_V1.bak`
- `LOOM_CAMPAIGN_HISTORY.jsonl.gz`
- `LOOM_Navigator_Browser_Report.json`
- `LOOM_Navigator_Current.html`
- `ephemeris_cache`

---

## 4. Navigator and flight architecture

Navigator is the ship flight/planning runtime. Development has emphasized physically disciplined strategies while keeping consumers insulated from raw payload changes through typed/validated schemas, adapters, and accessors.

A representative qualification run used Ceres → Neptune system barycentric capture. Multiple strategies were previewed, including EXPEDITE/PRECISION_COLLAPSE, HARD/ROUTINE_PRECISION, and FAST/PRECISION_COLLAPSE. The selected EXPEDITE plan combined staging and metric phases, tracked remass, holonomy and precision residual, and passed preview qualification.

Project engineering preference is to keep orbit/capture behavior sufficiently general where detailed orbital mechanics are not yet worth locking prematurely, while retaining physically meaningful constraints and explicit future extension points.

The Courier/Wayfarer engineering baseline developed during the project includes a roughly 57 m × 9 m vessel, ~1,210 t full mass, ~250 t remass, torch/metric systems, Mc-299m isomer hardware, large radiator area, thermal-buffer constraints, and acceleration/Δv envelopes. These engineering figures remain governed by the engineering/canon documents rather than this continuity note.

---

## 5. Solar GIS architecture

The Solar GIS evolved from a visualization into a local operational inspection surface. It combines spatial entities, solar-system layout/ephemeris, infrastructure, media, navigation/planning integration, and link-analysis behavior.

Important historical milestones:

- draggable graph/link-analysis nodes restored the investigative GIS behavior;
- approved media thumbnails were stabilized by serving/embedding authoritative MEDIA assets rather than depending on fragile browser object-URL behavior;
- the Pixel successfully runs the GIS locally;
- current GIS can be launched with a Navigator runtime root and offline planning mode.

A process observed on the Pixel at this baseline was:

`python ... src/loom_gis.py --nav-runtime-root /storage/emulated/0/Download/LOOM_TEST --nav-planning-offline`

This matters because the project currently has **two distinct Pixel roots**: a Git working/source root and an installed runtime root.

---

## 6. Media + Canon Browser

The Media Library was created so the visual corpus can be inspected directly without manually opening the ~474 MB media SQLite.

The successful Pixel browser runs on localhost. During development port 8766 was initially used; the hardened Media + Canon Browser v1.2 defaults to **127.0.0.1:8767** to avoid collision with other LOOM local services.

Current v1.2 capabilities:

- read-only WORLD/MEDIA/CIVSTATE access;
- search;
- **Celestial Object** filter;
- **Object Type** filter;
- **Media Role** filter;
- thumbnail grid;
- click-through to full original media;
- entity ancestry resolution;
- **Inspect authoritative SQL** link per media card;
- schema-driven inspection of direct entity-keyed records across WORLD and CIVSTATE;
- BLOB values represented by size rather than dumped into HTML;
- derived thumbnail snapshot export.

The SQL inspector deliberately uses exact entity-key relationships. It does **not** perform fuzzy text matching and therefore does not claim arbitrary prose references as authoritative relationships. This is an intentional epistemic/provenance boundary.

The first working Pixel screen showed examples including Aphrodite Cloudport Network and Arafura–Northern Australia Spaceport, confirming that the local media DB and metadata joins were functioning.

---

## 7. Pixel architecture and known local state

### 7.1 Device/runtime

Current mobile development/runtime device: Android Pixel, using Termux/Python for command-line execution and the Android browser for localhost LOOM interfaces. Pydroid has also been used historically for Python execution.

### 7.2 Git working copy

Known source/Git working root:

`/storage/emulated/0/Download/LOOM_TEST`

This is where the user has successfully run source directly and where Git synchronization/push/pull work is performed.

### 7.3 Installed runtime root

Updater-managed runtime root:

`/storage/emulated/0/Documents/LOOM`

The updater installs code under `src/` and data under `data/` relative to this runtime root.

The distinction is deliberate and must not be blurred:

- **LOOM_TEST** = Git/source working copy.
- **Documents/LOOM** = installed runtime copy managed by the updater.

Code should derive its runtime root from its own installed location unless `LOOM_HOME` or an explicit root is supplied. This avoids accidentally reaching back from the installed runtime into the Git checkout.

### 7.4 Known Pixel runtime facts at baseline

- Solar GIS is operational locally.
- Media + Canon Browser v1.2 is operational locally.
- Media + Canon Browser successfully reads local WORLD/MEDIA data and renders all 182 thumbnails seen in the test.
- The v1.2 browser's celestial/object-type/media-role filters and authoritative SQL inspector were reported working by the user.
- A GIS Python process was observed running with Navigator runtime root `/storage/emulated/0/Download/LOOM_TEST` and `--nav-planning-offline`.
- Android/Termux denied `ss` access to the netlink socket, so process inspection was used instead.

This archive **does not claim to be a byte-for-byte inventory of every file currently on the Pixel**. GitHub cannot inspect arbitrary local phone storage through the connector. The authoritative reproducible runtime payload is therefore defined by the release manifest + release assets, while local mutable/preserved state remains device-local unless explicitly exported/pushed.

---

## 8. GitHub deployment architecture

Private repository: `loom-2226/loom-2226`.

The deployment model is:

1. develop/change source under Git control;
2. run required regression/functional tests;
3. commit source to GitHub;
4. update `manifests/release_manifest.json` with exact SHA-256 and size for deployable artifacts;
5. distribute oversized media through a GitHub Release asset;
6. run `deploy/loom_update.py` locally;
7. updater downloads/verifies payloads and installs them atomically into the runtime root while preserving named mutable local state.

This means local Python reads **local SQLite**. GitHub is source/distribution synchronization; it is not the live database server.

Current code/data artifacts include Navigator, Solar GIS, Media + Canon Browser, its launcher, WORLD SQLite, CIVSTATE SQLite, and the MEDIA release asset.

---

## 9. Cross-platform rule

Pixel and Windows use the same source architecture where possible, but launch/runtime paths differ. Platform-specific launchers are acceptable; core logic should not fork unnecessarily.

Windows runtime convention has been `~/Documents/LOOM`. Android installed runtime convention is `/storage/emulated/0/Documents/LOOM`.

Any future release should explicitly identify whether an instruction targets:

- Git/source checkout;
- installed Pixel runtime;
- installed Windows runtime.

---

## 10. Testing/release discipline

Standing project rule:

- before sending/releasing a new Python file, run unit regression tests;
- for substantive functional changes, run unit regression **and functional tests**;
- reserve full end-to-end regression for finalization immediately before a production run.

The project should avoid untested one-off Python drops. Exact artifact hashes and sizes belong in the release manifest.

The Media + Canon Browser v1.2 change was compile/synthetic-functional tested for celestial inheritance, object-type/filter data, cross-table entity inspection, BLOB retrieval, snapshot export, and HTTP inspector behavior before release; it was then confirmed working on the Pixel.

---

## 11. Simulation/history program

A major current direction is to derive the 2226 world from a defensible 2026 baseline rather than reverse-engineer arbitrary 2226 numbers. Work has included demographic, economic, productivity/capital, commodity sourcing, infrastructure, transport, technology thresholds, accessibility/ephemeris, institutional fragmentation, and historical propagation concerns.

The target architecture is hybrid rather than a single monolithic model: stock/flow and cohort models, economic/IO relationships, discrete-choice/path-dependent behavior, transport/accessibility networks, institutional constraints, and first-class spatial-temporal events. Countries, corporations, and institutions should be introduced once the baseline propagation machinery is sufficiently stable to avoid baking narrative answers into the model.

---

## 12. Rabbit-hole / epistemic architecture

The planned intelligence/epistemic layer is explicitly dual:

- WORLD/GM SQL stores objective authoritative truth;
- each player/significant NPC has a sparse knowledge/belief graph.

Knowledge graphs are intended to support claims with confidence, provenance, timestamps, salience, verification state, false connections, deception, and limited second-order beliefs. Incidents/events are first-class spatial-temporal objects linking who/what/where/when, allowing relationships and investigative patterns to emerge from co-occurrence rather than only from manually authored edges.

This is the architectural bridge between LOOM's simulation authority and the investigative/link-analysis behavior of the GIS.

---

## 13. Current source-control checkpoint

Media + Canon Browser v1.2 source commit immediately preceding this archive:

`fba5516f6cfe61ec7b1ea6ab894762f50a00beae`

Release-manifest update for v1.2 immediately preceding this archive:

`f411424a8a891a25a783b5139ec903f7c21e3b23`

The release manifest identifies the v1.2 release as:

`media-canon-browser-v1.2-2026-09-06`

---

## 14. Recovery / continuation instructions for a future LOOM session

A future developer/assistant should begin by reading:

1. this continuity document;
2. `manifests/release_manifest.json`;
3. current repository README/docs;
4. current canon baseline/validation manifests;
5. relevant current source and tests before editing.

Then determine which root is being discussed (Git checkout versus installed runtime) before giving device commands.

Do not infer that a file exists on the Pixel merely because it exists in GitHub. Conversely, do not assume device-local mutable state has been committed merely because the runtime payload is reproducible.

When changing schemas or runtime payloads, preserve the authority/derived distinction and use adapters/accessors rather than proliferating hard-coded field names.

---

## 15. What is and is not captured here

Captured:

- project intent and architecture;
- authoritative/derived boundaries;
- WORLD/CIVSTATE/MEDIA organization;
- Navigator/GIS/media-browser architecture;
- GitHub/updater/runtime-root model;
- known Pixel paths and verified working services;
- simulation and epistemic direction;
- release/testing discipline;
- current recovery checkpoint.

Not captured byte-for-byte:

- arbitrary untracked files in Pixel storage;
- current mutable local state/caches unless already represented in Git/release assets;
- the complete text of every historical chat.

Those require a **Pixel-side inventory/export**. A future hardening step should add a read-only `loom_runtime_inventory.py` command that emits filenames, sizes and SHA-256 values for the installed runtime and selected preserved state, with explicit exclusions for secrets and transient caches. That inventory can then be committed as a dated machine-readable device baseline without uploading unnecessary duplicate media BLOBs.
