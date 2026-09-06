# LOOM 2226 — GIS / Navigator Current Status

Date: 2026-09-06
Status: **Phase-6 MVP physically accepted on migrated Pixel runtime**

## 1. Current accepted loop

The integrated GIS/Navigator flow is operational on the migrated split-root runtime:

1. user selects a destination in GIS
2. GIS resolves it against Navigator endpoint authority
3. Navigator discovers candidate routes
4. GIS presents/compares candidates
5. selected route is previewed
6. planning commit locks the route choice without changing campaign state
7. explicit execute computes arrival and performs one canonical campaign transition
8. historical route overlay is produced
9. GIS rebinds to the new campaign location/state

Physical Mars → Ceres qualification passed end-to-end.

## 2. Authority boundaries

Navigator remains authoritative for:

- endpoint registry
- route discovery
- flight compilation
- deterministic flight calculations
- route-layer production

GIS remains authoritative for:

- map interaction
- destination selection UX
- route comparison/presentation
- navigation overlays and camera behavior
- explicit user planning/execute actions

Campaign persistence remains authoritative through the legacy canonical campaign service:

- stale-state guard
- revision increment
- history append
- atomic save
- read-back verification
- exact-byte rollback on failure

Shadow campaign SQL remains diagnostic/best-effort only.

## 3. Current Phase-6 behavior

Known working endpoint examples include major bodies such as Mercury, Venus, Earth, Moon, Mars, Phobos, Deimos, Ceres, Jupiter, Saturn, Uranus, Neptune, Pluto, Charon, Haumea, Makemake, Eris, and Sedna.

Vesta and Psyche are not currently in the declared Navigator endpoint registry. Their unavailability is a deferred coverage item, not a migration regression.

Android planning defaults to cache/provider acquisition. Offline/cache-only mode is explicit.

The current accepted route execution model is intentionally more general than a fully continuous trajectory simulation. Gate-B continuous trajectory/HUD work remains deferred.

## 4. Physical acceptance evidence

Final accepted Pixel flight:

- route: `MARS>CERES`
- strategy: `DIRECT_NAVIGATION`
- metric: `HARD`
- torch: `CRUISE`
- departure campaign revision: 8
- arrival campaign revision: 9
- departure state: `S000008-1f8140b205a7`
- arrival state: `S000009-249837ce08c5`
- arrival location: `CERES`
- flight ID: `flight-e47fc2515426dacd`
- remass used: `11.334524545223303 t`
- `/flight-planning/preview`: 200
- `/flight-planning/commit`: 200
- `/flight-planning/execute`: 200

GIS visibly rebound to `ARRIVED · CERES · REV 9`.

## 5. UI / integration surface already present

The current runtime contains:

- `src/loom_gis.py`
- `src/loom_navigator.py`
- `src/loom/gis/flight_planning.py`
- `src/loom/gis/flight_planning_http.py`
- `src/loom/gis/flight_planning.js`
- `src/loom/gis/flight_planning_selection.js`
- `src/loom/gis/flight_planning_unified_drawer.js`
- navigation overlay contracts and browser controls
- runtime tracing/diagnostics integration

The unified NAV/ATLAS drawer is installed without making GIS the source of Navigator truth.

## 6. Deferred product/engineering work

The following are deliberately deferred beyond the accepted Phase-6 MVP:

- continuous trajectory / Gate-B HUD representation
- FOLLOW SHIP behavior
- route playback and richer temporal visualization
- broader minor-body endpoint coverage
- more advanced route comparison UX
- campaign SQL authority promotion
- deeper concurrency hardening around HTTP trace/session state
- longer-term separation of immutable world seed data from mutable runtime-derived WORLD database state

## 7. Next planning question

The next thread should not begin by coding randomly. It should first decide what the Navigator/GIS application is becoming as a product surface now that the runtime foundation is stable.

The planning discussion should cover, in order:

1. target user experience for selecting, planning, previewing, executing, and following a flight
2. what information belongs in GIS versus Navigator versus campaign state
3. route/trajectory visualization levels: abstract route, sampled path, continuous playback, and live ship following
4. endpoint expansion strategy, including minor bodies and infrastructure destinations
5. HUD/instrumentation design and how it uses authoritative navigation payloads without inventing physics
6. historical route/archive experience
7. operational debugging/diagnostics UX
8. platform parity expectations for Pixel and Windows
9. sequencing into small qualification gates that preserve the physically accepted Phase-6 loop

## 8. Preservation rule

Future Navigator/GIS development must preserve the currently accepted Phase-6 loop unless a change is explicitly designed, tested, and physically qualified as a replacement.

Do not casually alter campaign persistence authority, endpoint authority, runtime roots, updater boundaries, or the distinction between planning commit and execution.
