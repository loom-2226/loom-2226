# LOD, sampling and continuous refinement specification

Normative prototype algorithms. Numeric visual-policy values below are **candidate
cartographic choices**, not physical thresholds or earned device performance.
Measure their visible outcome; do not call an acceptance test green solely because
the code contains the same constants.

## Hierarchy

Semantic systems first; bounds second. Root `solar`; system nodes keyed by physical
primary; members joined using explicit anchor policy, not string heuristics.
Keep catalog barycenters as identities, not mandatory drawn physical spheres.
Optional nested asteroid systems follow the same structure. Node directory is
flat JSON with parent/child links; validate acyclicity and reachability.

Each node carries separate content and subtree spheres, both computed from actual
published epoch points and reference curve vertices in an anchor-local frame.
Transform and union child bounds in Float64 at T. Gap edges do not enlarge bounds
with invented segments. Loose Solar root bound never forces every child to load.
For 110 records, a linear directory walk is cheap and easier to audit than an
octree. Later spatial children may partition one dense system without redefining
physical parentage. Semantic IDs and spatial nodes remain independent fields.

## Geometry generation (offline only)

1. Resolve all catalog positions at T; preserve every failure. Plan requested
   horizons with pinned `automatic_plan` (default max 100 Julian years unchanged).
2. For each requested body and anchor, split at the union of known coverage/source
   boundaries. Retain the existing before/at/after boundary probes and all observed
   unresolved intervals. Never concatenate across a seam/gap or different source
   pair. Use exact service evaluations, no approximate orbit equations.
3. Seed each continuous planned interval with 65 uniform samples plus planner
   phase/coverage probes and T. Recursively query quarter, midpoint and three-quarter
   ETs on every interval. Split until all probe-to-chord distances meet
   `epsilon_sample = max(0.01 km, R*1e-6)` where R is the maximum resolved anchor-
   relative radius measured in the seed/probes. Recompute if R grows. Independently
   enforce time step <= planned span/256 to avoid a midpoint-only alias. Tie breaks
   choose earliest ET. Maximum 16,385 accepted vertices per curve / depth 20;
   exceeding either produces `SAMPLING_LIMIT`, not silent success. Cache exact
   `(body,ET bits,source identity)` queries within this one build.
4. Validate the master with an independent offset grid (at least 8,192 times per
   planned span, plus gap boundaries); compare exact governed states to their
   enclosing master chord. Include failed probes as failures/gaps; don't drop them.
   Reinsert violating valid samples, repeat once. If it still fails, publish the
   limit and fail prototype curve-quality acceptance. Save grid specification,
   maxima, worst epoch and count. This is empirical sampling qualification, not
   a mathematical guarantee between every possible ET or physical uncertainty.
5. For each continuous master segment, deterministic 3D Douglas–Peucker simplification
   uses point-to-segment distance. Retain T, endpoints, seam endpoints and all
   mandatory event indices. Build nested levels using tolerances
   `R/128, R/512, R/2048, R/8192, …` until <=epsilon_sample; finest is master.
   Generate each finer level within retained coarse intervals so indices are nested.
   Drop duplicate levels. Measure maximum deviation over *all* omitted master
   vertices and bound segment interiors by the corresponding chord intervals.
   Do not infer continuous physical error from this discrete metric.
6. Package entire levels independently. Record `sampling_probe_error_km`,
   `simplification_error_km`; conservative measured representation estimate is
   their sum. Unknown/failed sampling certification cannot yield zero error.
   No renderer-added closure. No segment bridges differing body or anchor sources.

The benchmark's 512-point paths are decision inputs, not these qualified masters.
Phobos at 2226 reduces to 33 vertices at ~49.6 km deviation from that polyline;
126 at ~8.76 km and 259 at ~0.73 km. The existing 53-point automatic path is not
assumed sufficient for close basemap inspection.

## Screen criteria

Use CSS pixels for visual thresholds; record device pixel ratio separately.
For perspective vertical FOV theta, viewport CSS height H:

`f = H / (2*tan(theta/2))`

For each bound transformed into view space, let `z_min = center_depth - radius`.
When wholly in front of the near plane, use conservative projection factor
`K = f/z_min * sqrt(1 + rho_max^2)` where `rho_max` bounds radial X/Y-to-depth
ratio over the sphere (use `(hypot(cx,cy)+radius)/z_min`). This includes off-axis
projection sensitivity; it is deliberately conservative. `SSE = error_km*K`.
For orthographic adapters `K = H/view_height_km`. Near-plane intersection makes
SSE unbounded: choose highest available useful level and mark limits, never
substitute camera-center distance as a false finite bound. Cull only after proper
near/frustum clipping. Use projected clipped bounds for display admission.

For semantic admission, use projected system extent and child's separation from
its parent marker. Candidate glyph diameter is read from style; with the existing
4 CSS-pixel marker, start local-geometry prefetch at system diameter 12px,
start fade-in at 16px, fully visible at 24px; satellite markers are admitted when
projected parent separation exceeds two marker diameters (8px for that glyph).
Root index still exposes every body at every scale; crowded labels yield to
priority/selection, never remove catalog identities. Selected identities get
an explicit clipped/overlapped/unresolved diagnostic if not visible.

Reference curves are contextual: heliocentric curves fade from normal at a
projected bound diameter of 8 viewport diagonals to zero at 16, avoiding an
unhelpful giant arc through a local view and useless extreme-detail requests.
This changes cartographic line visibility, not a body's epoch position. Local
reference curves use the same measured extent policy as they become irrelevant
at surface-like zoom; the initial prototype ends at a satellite-orbit view,
not a surface. These policies are declarative in generation/client-policy spec.

## Refinement state machine

At each camera change (coalesced to one animation frame):

1. Traverse visible subtree bounds; compute desired semantic content. Independently
   prioritize selection, screen error, projected extent, stable node ID.
2. For each admitted curve choose the coarsest available level with measured SSE
   <=0.75 CSS px. Request next useful level early when current SSE exceeds 0.5px.
   Keep current until verified replacement is decoded/uploaded. Higher detail
   beyond useful pixels is not requested. Fetch at most two resources concurrently;
   camera movement can reprioritize queued tasks. A stale response is cacheable
   under its exact build key but cannot overwrite another build/view selection.
3. Switch to finer when >0.75px; permit coarsening only if the proposed coarser
   level stays <0.35px for 250ms. These dead bands prevent threshold oscillation.
   Retain visible coarse geometry while network is slow or failed. Expose
   `DETAIL_PENDING`, `DETAIL_FAILED`, `ERROR_LIMIT` independently of physical state.
4. Geometry replacement is atomic on a frame boundary. When both representations
   meet <=0.75px discrepancy, no line cross-fade is needed (it would double ink).
   If the user jumps while download is late, use 150ms opacity cross-fade of the
   same curve, not vertex morphing; report transient error debt. Additive markers/
   local context use a continuous opacity ramp across admission interval, with
   hysteresis for resource eviction only. No curve coordinates are animated into
   invented intermediates.
5. Preserve root and active levels. Memory accounting includes decoded doubles,
   Float32 GPU arrays, old level during transition and in-flight decoded response.
   Set prototype cache bound from measured largest two-system active frontier plus
   one adjacent prefetched frontier and root, rounded up to MiB. Record the computed
   byte value in benchmark output. Evict LRU inactive finer levels first. Do not
   silently degrade active accuracy to satisfy memory; report a limit.
6. Stop drawing when camera, content and transitions are unchanged. Pinch/wheel
   changes camera distance continuously; pan/rotation change camera only. There
   is no system selector, scope change or reference-frame switch in this sequence.

## Precision and depth

World/anchor/eye values remain Float64 km in CPU memory. Before GPU upload, compute
camera-relative coordinates in doubles, rotate into camera axes, and apply one
uniform view scale (km per render unit). Only then cast to Float32. For satellites
use `(anchor(T)-eye)+local` so the small offset is not rounded away in a global
Float32 value. Do not upload a huge anchor and ask a float shader to cancel it.
Update only admitted geometry on camera changes; measure this work before trying
workers/quantization. No browser physics is involved.

Use the existing vendored Three.js r149 for the bounded prototype, camera at
render origin, perspective projection, log depth buffer capability checked at
startup; choose near/far from visible camera-relative bounds and record them.
Reject/report unsupported precision/depth capability rather than claiming a
qualified 3D result. Render symbolic labels separately. The prototype has points
and polylines, not unqualified solid planets; depth/occlusion tests cover visible
lines crossing the near plane and far reference context. No WebGPU requirement.

A numeric browser test must compare projected Float64 reference positions to GPU
input reconstructed coordinates at Solar, Mars, Phobos and Pluto scales. Budget:
conversion error <0.25 CSS px, leaving <=0.75px measured geometry error for a
1px total representation budget. Verify actual scene pixels as well as draw lists.
Global curve suppression and local refinement must not change the continuous
camera trajectory or the stationary epoch markers.
