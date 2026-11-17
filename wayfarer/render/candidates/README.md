# Wayfarer nacelle approval candidates — 2026-11-17

**ALL bodies. ALL sponsors. 2026–2226. Class: engineering. NOT RELEASED CANON.**

Two independent full-ship GLBs have 20 newly tessellated physical B-rep
solids appended to the corresponding read-only, released torch or Metric GLB.

- Torch: wayfarer_nacelle_torch_f173094b.glb — four nacelles tucked at r=4.05m, tail arms folded.
- Metric: wayfarer_nacelle_Metric_f173094b.glb — four nacelles at r=4.6m, eight 45-degree ring arms locked at x=53.9m.

Actual source solids: wayfarer/lab/build_v05.py nacelle_shapes(),
wayfarer/results/out/wayfarer_v05_geometry.json metric_states, and
wayfarer/lab/metric_nodes/nacelle_source_brep.py. The Metric nacelle
has a cut ring-lock receiver in the NEW nacelle body. Original ship
solids and the pinned torch chain remain untouched.

The PNGs are presentation renders; the full torch hot-fin deployed span
is omitted for clarity. The HTML selector switches between the candidate
GLBs with a network-hosted viewer (serve this directory over HTTP(S)).
Neither render nor viewer is collision certification.

Two candidate STEP assemblies, each consisting of the SAME unmodified
certified #559 full-ship source STEP and a separate 20-solid mode STEP overlay,
and strict D9 evidence are produced by
.github/workflows/wayfarer-nacelle-two-state-d9.yml:
194 unchanged protected solids + 20 new installed = 214 solids and
22,791 pairs in EACH state, original category-(d) >0.01m3 rule,
all 43 original primary B-rep audits; both states MUST PASS.

OPEN: mid-stroke motion envelope. The sampled nacelle_fit survey is
not a motion-envelope D9 state. Also open: thermal soak, ring latches,
field-wall standoff.

Canon pointer and released GLBs untouched. Source books 8.0t p95
from the original 7.75t allowance and 0.25t reserve. Dry mass and
ECON delta-v preserved.
