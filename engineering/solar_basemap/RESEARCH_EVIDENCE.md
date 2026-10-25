# Research and evidence register

Retrieved/inspected 2026-09-28 (Melbourne). Primary technical sources only.
`FACT` means documented implementation/specification or observed bytes;
`INFERENCE` means a LOOM design conclusion, not a vendor claim.

## Repository authority map

All PR299 implementation references are pinned to
`f0c373a4deb5589584619b64a91ac2ac1d2ed936`:

| Concern | Implementation / evidence |
|---|---|
| Identity, source membership and qualification | PostgreSQL `loom_solar.body`, `body_identifier`, `ephemeris_source`, `ephemeris_coverage`, `object_metadata`, `curated_cohort_member`; `src/loom_solar_postgres.py:read_ledger/load_authority` |
| Registry/source precedence | `src/loom_spice_ephemeris_adapter.py:SolarEphemerisRegistry.source_for` |
| SPICE state service | same file `SolarStateService.resolve_et`, `_direct_lookup`, `_source_pool`; validates actual selected target SPK, canonical frame/units |
| Time | `src/loom_solar_time.py`; `manifests/solar/SOLAR_NATIVE_ET_COVERAGE_V1.json`; migration 020 |
| Trajectory/horizon/reference | `src/loom_solar_inspector.py:relative_state`, `automatic_plan`, `automatic_path`, `trajectory`; gaps/seams and both sources |
| Physical display | `web/solar-inspector/inspector.js`, `presentation.js`; PHYSICAL map `[x,z,-y]/AU_KM`; named manual system/reference controls |
| Qualification | `docs/qualification/SOLAR_INSPECTOR_V01_QUALIFICATION.md`, HUMAN_Q8 LOCAL_PATH evidence/tests, original Q8 before/after Fit evidence |
| Legacy donors | `src/loom_solar_gis.py`; `src/loom_navigator.py`, `loom_navigator_core.py` plus hash-verified embedded core; LEGACY_FORENSICS |

The live API authority digest agrees with the prior Q8 ledger identity, but this
measurement at ET 7131844800.0 has 103 resolved bodies rather than Q8's 108. At
2226 unresolved: DACTYL, HYDRA, KERBEROS, NIX, PROTEUS, SELAM, STYX. Exact failure
reasons are in `evidence/measurements.json`; unavailable target coverage is retained.
The current 110 catalog identities include nine barycenters, 31 natural satellites,
eight planets, 17 asteroids, 11 dwarf planets and other curated classes. Counts are
reported as registry classes, not astronomical reclassification.

The old Q8 98 requests and 15 truncated horizons are evidence at their own epoch,
not acceptance constants for 2226. The historical unavailable path was Earth/Sun
served by stale code; it was repaired, not an intrinsic absent Earth orbit. Do not
carry a stale “one unavailable” expectation into a new product.

## External architectural candidates

| Source / documented fact | LOOM inference / disposition |
|---|---|
| [OGC 3D Tiles 1.1](https://docs.ogc.org/cs/22-025r4/22-025r4.pdf): bounds, geometric error, ADD/REPLACE refinement, transforms, external content | Borrow SSE/error and availability/refinement separation. Full tiling/implicit subdivision/glTF payload stack is excessive for ~100 bodies. Non-geographic sphere/box principles fit; Earth-region coordinates do not. |
| [Esri I3S specification](https://github.com/Esri/i3s-spec/blob/master/format/Indexed%203d%20Scene%20Layer%20Format%20Specification.md) and [node index](https://github.com/Esri/i3s-spec/blob/master/docs/1.9/3DNodeIndexDocument.cmn.md): hierarchy, bounds, child/resource links, LOD metrics/node pages | Borrow published hierarchy and separate geometry/attributes. Do not adopt SLPK, node-page protocols, texture mesh machinery or ArcGIS hosting dependency. Semantic systems fit better than terrestrial spatial partitions. |
| [ArcGIS scene layers](https://pro.arcgis.com/en/pro-app/3.4/help/mapping/layer-properties/what-is-a-scene-layer-.htm): cached scene publication/package and ready-to-serve content | Publication is distinct from viewing. Commercial ArcGIS authoring/hosting is unnecessary for LOOM; no subscription/service or licensing commitment is introduced. This is documentation for a specific Pro version, not a claim that 3.4 is the latest. |
| [Cesium3DTileset](https://cesium.com/learn/cesiumjs/ref-doc/Cesium3DTileset.html): screen error target, cacheBytes and overflow affect loading | Borrow explicit memory/error tradeoff accounting. Do not import its default error/memory values as LOOM targets. [CesiumJS license](https://github.com/CesiumGS/cesium/blob/main/LICENSE.md) is Apache-2.0; hosted ion is a separate optional service, not required by the format or this design. |
| [NASA Eyes](https://science.nasa.gov/eyes/) and [FAQ](https://science.nasa.gov/eyes/faq/): browser/mobile exploration of NASA data and multiple astronomical scales | Behavioral precedent only. Reviewed pages do not document its chunk format, cache hierarchy or LOD internals. No architectural claim about those internals is made. No NASA data/imagery redistribution dependency is proposed. |
| [NAIF spkgeo](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkgeo_c.html): geometric target relative to observer, ET, frame, km/km/s; no aberration option; numerical outputs can depend on environment | Reuse existing governed adapter; distinguish per-sample subtraction from frozen anchor translation. Pin numerical environment for build identity. No new browser SPICE instance. |
| [OpenSpace SpiceTranslation](https://docs.openspaceproject.com/latest/reference/asset-components/Translation/SpiceTranslation.html): scene nodes can consume SPICE target/observer/frame translation and fixed date | Independently useful astronomical scene-graph precedent. Borrow explicit frame/node/epoch association. Reject importing a desktop astrovisualization engine or executing client SPICE. [OpenSpace repository](https://github.com/OpenSpace/OpenSpace) declares MIT licensing; no code is copied here. |
| [Three.js rendering on demand](https://threejs.org/manual/pages/rendering-on-demand.html), [LOD](https://threejs.org/docs/pages/LOD.html): on-demand draws and distance levels with hysteresis | Use on-demand rendering and dead bands; simple distance-only LOD misses feature size and error across Solar scale. Reuse existing pinned r149, not an unreviewed dependency upgrade. [MIT license](https://github.com/mrdoob/three.js/blob/dev/LICENSE) retained when distributing assets. |
| [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html): scene nodes/accessors/buffers and line primitives | Reserve for meshes. A glTF 2.0 POSITION accessor uses Float32; scientific provenance and exact sample ET still need an external contract. Not selected for these few double-precision polylines; not a claim about all newer/extensions' capabilities. |
| [LOCALIS paper](https://arxiv.org/abs/1909.05511): view-adaptive line LOD from Douglas–Peucker hierarchy | Supports considering line-specific refinement rather than mesh tiles. LOOM needs a simple deterministic CPU-generated nested simplification pyramid, not its GPU system. No performance claims transfer. |
| [RFC 8949 CBOR](https://www.rfc-editor.org/rfc/rfc8949.html): compact binary format with deterministic encoding rules | Viable later. Additional encoder/decoder has no measured need here; gzip JSON is chosen. |
| [RFC 9111 HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html): cache directives/validators | Immutable content identities plus revalidated current pointer; transport caching must not merge different authority builds. |

No vendor framework is adopted. The commercial-stack comparison is an architectural
fit decision, not a general claim that those standards are unsuitable for space.
No unsupported NASA internals, performance transfer or scientific result is used.

## Measurements and decision limits

`bench/measure.py` ran against the live read-only server. The first exploratory
run completed all physics calls but failed while treating the archive's plain
JSON Atlas payload as a binary header. It was corrected; the recorded successful
run's server calls were therefore **warm cache**: catalog 33.7ms, scene 2.84ms,
automatic paths 1.76–2.35ms, 512-point path responses 6.74–7.03ms. These do not
measure cold kernel validation or initial physical compilation. The full path
API returns 186–191 KB/curve with provenance/state repetition; the display-only
coordinate arrays are ~30 KB. Neither size is a finished basemap package.

| 512 vertices (XYZ only) | JSON gzip | Float64 LE gzip | Float32 LE gzip | Float32 max deviation |
|---|---:|---:|---:|---:|
| Mars/Sun | 15,415 B | 11,721 B | 5,780 B | 10.837 km |
| Phobos/Mars | 15,386 B | 9,200 B | 5,722 B | 0.000519 km |
| Deimos/Mars | 15,431 B | 9,610 B | 5,682 B | 0.001113 km |
| Moon/Earth | 15,366 B | 10,328 B | 5,731 B | 0.020816 km |
| Charon/Pluto | 15,479 B | 8,561 B | 5,679 B | 0.000984 km |

ET/index/source metadata adds bytes; budget it in prototype output. Compression
is gzip with mtime=0, not a promise of wire transfer on the existing no-store
Inspector. For 100 curves of 512 vertices, bare coordinate arrays are approximately
1.5 MB gzip; this is an analytical scale estimate, not a proposed initial download.
At one system at a time, JSON parsing is a small measured cost (0.3ms median,
0.4ms p95 per 512-vertex array in 100 repetitions).

`bench/browser.cjs` ran existing clients at 412×915 CSS, DPR3, Chromium/SwiftShader,
no CPU/network throttling. Three fresh browser contexts each (OS/server warm):
Inspector first submitted marker 373–382ms with only 29–65 objects observed during
measurement, 14–19 requests; NOT whole-catalog readiness. Approximate reported JS
heap 10MB. Legacy archive 477–722ms, heap 11.9–12.7MB; one 2558ms frame interval
outlier, otherwise ~16.7ms medians. Heap is a browser estimate, not GPU/process
memory. These results cannot qualify a physical Pixel. All page-error lists empty.

The prototype's initial manifest+root goal is <=49,920 gzip bytes, the measured
legacy fixture bootstrap size, while adding explicit failure/provenance and coarse
planetary context. This is a falsifiable comparative budget, not a latency promise.
Expected local 512-vertex two-moon coordinates: ~31KB gzip plus ET/source metadata;
finest adaptive geometry will be larger and must be measured. First useful scene,
refinement latency and smoothness are tested against a static monolithic control
of the **same** product, not inferred from warm resolver timings.
