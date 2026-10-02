# Legacy Navigator / Solar GIS forensics

This report distinguishes two implementations. Source locations below are read
at PR299 `f0c373a` (GIS is identical to inspected main); old records do not become
current physical authority. Archived HTML is measured as historical bytes, not
claimed to be a reproducible current release.

## Solar GIS v0.12.9 RC8

`src/loom_solar_gis.py` contains the real implementation; the named RC8 script is
an older packaged surface. Trace:

1. `SolarStore.get_state` (around line 2304) caches instantaneous vectors keyed by
   identity, UTC epoch, reference frame and plane in SQLite. `build_scene` (3074)
   checks the cache first. Parent-center Horizons calls are skipped when all moon
   states for that parent are cached. Refresh bypasses this cache.
2. On misses, Python obtains Horizons vectors. Python immediately computes
   192-sample heliocentric osculating ellipses and 160-sample parent-centered moon
   osculating ellipses (`osculating_orbit_from_state`, 553;
   `local_osculating_orbit_from_state`, 606). These are not repeated multi-epoch
   governed SPICE trajectories. SQLite orbit snapshots store model metadata;
   `build_scene` regenerates the geometry in memory.
3. `SolarScene.to_json_dict` (around 407) emits coordinates and metadata, including
   physical and display coordinates. `serve` (5677) serializes once, before serving
   requests. The handler returns static in-memory bytes: bootstrap, geometry,
   details, full/core scene. No orbit calculation occurs per browser request.
4. Client JS (5274) fetches bootstrap first, then geometry and details in parallel;
   graph-view is a separate request. `prepareScene` normalizes coordinate arrays
   once. Canvas2D `project` applies yaw/pitch and scale; `scheduleDraw` coalesces
   changes into requestAnimationFrame and is idle when unchanged. DPR is capped 2.
5. Local orbit drawing filters by focus parent (around 3970). `viewMode=FOCUS`,
   camera bands and manual focus controls switch between Solar and system views;
   scale modes include nonlinear ASINH presentation. This is not seamless
   scale-driven publication. Full geometry still arrives in one request.

### Measured fixture, not live historical latency

The existing `build_scene(..., provider=demo_provider)` was run with its own
in-memory SQLite store; no real SQLite file was opened or seeded. It completed
in 558 ms on this host. This excludes Horizons/network, production DB initialization,
media and service startup; it cannot establish historical Pixel startup latency.

| Output | Raw bytes | gzip bytes (offline comparison) |
|---|---:|---:|
| Full JSON | 7,590,463 | 904,178 |
| Bootstrap | 625,352 | 49,920 |
| Geometry | 754,818 | 301,312 |
| Details | 6,210,419 | 551,736 |
| Client JS | 188,458 | 53,047 |

Fixture has 164 entities: Sun + 20 primaries + 28 moons + 115 infrastructure
entries; 20 heliocentric tracks, 28 local tracks, zero infrastructure orbit tracks,
and 900 synthetic non-catalog belt dots. The server's printed “127 propagated
infrastructure objects” string is not this measured count. Geometry includes
physical and nonlinear display variants. Compression figures do not assert the
old server actually negotiated gzip. Initialization can still be slow when caches
miss; browser speed does not establish acquisition speed.

## Navigator RC6.1 / embedded Sequence-H core

`src/loom_navigator.py` loads `loom_navigator_core.py`; `_load_core` (848) decodes
`CORE_B64`, verifies SHA-256, and imports the embedded 245,121-byte Python core.
Verified embedded SHA:
`33a651cb0dfef6e853e5a28b8106212af96eb2b8fc95fe932581d648583c3e55`.
The audit decoded it to `/tmp` without executing its campaign workflow.

Embedded source trace (line numbers refer to those decoded bytes):

- `encode_cache_entry` / `decode_cache_entry` (551/573): gzip with mtime=0,
  canonical request metadata, response hash, binary little-endian Float64 rows
  `(JD,x,y,z,vx,vy,vz)`. `fetch_or_cache` (618), dependency index (1009) and
  offline replay consume cached data. Fetch timestamps are excluded from stable
  content identity by `stable_cache_content_sha256` (947).
- `compile_ephemeris_payload` (2011): precomputes screen tracks for NAV/TRUE and
  TOP/OBLIQUE/EDGE views plus depths. Quantizes and encodes second differences as
  varints; identical tracks are deduplicated. Decoder materializes Float32 arrays
  on demand and caches them. Browser time selection indexes precompiled tracks.
- `_solar_osculating_points` (1946) makes solar reference ellipses;
  `_circle_plane_points` (1965) makes 72-segment moon reference rings from T0 plane
  and radius. These are explicitly reference geometry, not full physical paths.
- `compile_sequence_b`, `inject_native_payloads`, `target_determinism_gate`:
  compile payloads, embed base64 into HTML, build twice and compare identities.
  SVG creates projected orbit/route primitives; browser does not invoke a resolver
  to produce Solar context. Camera views are preselected projections, not a free
  3D hierarchy. “Cheap client” came partly from constrained camera choices.

Measured archived file:
`LOOM_ARCHIVE/PIXEL/2026-09-24/shared_download/LOOM_TEST/LOOM_Navigator_Current.html`,
SHA `f752b34ad614c32110297548f712cedf50aafeb335633d74ff1df4b507e9c2f4`.
2,101,421 bytes HTML (762,213 gzip in offline comparison). Ephemeris payload alone
is 1,607,452 base64 characters, 1,205,589 decoded bytes: 582,748 metadata and
622,837 binary. It has 673 frames, 10 primary Solar bodies and 34 base tracks,
with more camera variants encoded separately. Five other embedded payloads
supply Atlas, routes, flights, decisions and local routes; see measurement JSON.

Three unthrottled Chromium 412×915/3× trials showed useful SVG primitives at
722/477/509 ms, 152 SVG elements, no page errors. Requests were the HTML plus
an intercepted diagnostic POST (not a geometry fetch). One first-run animation
interval was 2,558 ms; preserve it as a cold outlier, not evidence of smooth
sustained physical-device rendering. The archive's external requests were locally
fulfilled; nothing was sent to its original logging endpoint.

## Donor disposition

| Reuse principle | Reject from current product | Superseded owner |
|---|---|---|
| Compile before client, immutable snapshots, split useful context/details | Old UTC/source priority/cache as authority; import of historical coordinates | Solar PostgreSQL ledger + native ET registry |
| Explicit reference-geometry semantics and local origin | Analytic ellipses, circular fallback, synthetic moon phase or belt bodies | Governed exact samples only |
| Deterministic cache/build identities, codec roundtrip testing | Screen XY as reusable 3D scene; loading all timeframes/camera variants | New epoch scene contract |
| On-demand draws, capped DPR, camera independent of physics | Manual system switching as refinement mechanism | Continuous scale admission/SSE |
| Parent-relative geometry packaging | Barycenter/planet conflation on cache-sufficient paths; source fallback | Explicit governed parent and cartographic anchor IDs |

Fast appearance is explained by precomputation, caching, bounded sample counts,
preprojection and staged/embedded delivery. It is not evidence that old authority
or runtime physics should be restored.
