# Prototype acceptance and benchmark plan

No prototype PASS is claimed by this architecture packet. Tests below are future
implementation gates. Decision experiments already run are in RESEARCH_EVIDENCE.

## Test matrix

| ID | Falsifiable requirement / evidence |
|---|---|
| A1 authority | Same input snapshot as live ledger; 110 entries at the measured baseline, 103 resolved/7 unresolved at ET 7131844800.0. Recompute if authority changes, with explicit identity/diff review, never retune a count to hide lost bodies. Every physical marker equals governed state at T. |
| A2 geometry semantics | For every required local sample, `q=X_body(t)-X_anchor(t)`; drawn world position is `X_anchor(T)+q`. At T equals physical marker. Compare also Sun-frame worldline: differences must equal anchor displacement, so a wrong center cannot pass just because HTTP succeeds. |
| A3 identity/frame/provenance | Exact body, anchor, horizon reference, ET bits, ECLIPJ2000, km, geometric/NONE, source/capability and coverage from service survive into source dictionary and sample indices. Negative mismatches reject. |
| A4 boundaries/failure | Gap/source seam in either body or anchor creates a break at every LOD; no closure edge. Missing body/anchor, catalog-only, truncated horizon and sampling limit have distinct statuses. Inject failures using fixtures, not authority writes. Root retains unresolved IDs/reasons. |
| A5 deterministic publication | Two fresh-process builds with same immutable input/environment/spec: same manifest ID and every artifact byte/hash. Change one source hash, coverage window, ET, anchor policy or sampling policy: different build; source tampering fails. Atomic publication crash preserves previous current pointer. |
| A6 error qualification | Independent grid residual <= epsilon_sample; simplified-to-master max <= declared tolerance for each segment. Sampling-limit fails close-scale quality. GPU conversion <0.25 CSS px, total measured geometry+conversion <=1px at settled views. No claim of physical accuracy tighter than source uncertainty. |
| A7 continuous zoom | Replay a smooth log-distance camera trajectory from 50 AU context toward Mars, then ~100,000 km camera distance near Mars; orbit and markers appear/refine automatically, no system/reference control, no reference state mutation. Continue until Phobos/Deimos separate and orbit detail is useful; maintain readable diagnostic status. |
| A8 second system | Repeat approach to Pluto/Charon, preserving barycenter/primary distinction. Validate actual drawn local curve and T marker as in A2; no Sun-frame Float32 cancellation. |
| A9 renderer reconciliation | For every root feature and requested curve: identity → resolution → chunk → segment/index → draw list → material → clip/projection → pixel contribution. Capture isolated and composed pixels at scale checkpoints; missing line must have a classified reason. Actual raster comparison, not submission only. |
| A10 client independence | Disable/deny every resolver/API URL; serve only publication and shell. Camera/refinement still works. Count zero authority calls and zero client propagation modules. Two minimal consumers (QA and non-DOM loader test) load the same manifest. |
| A11 cache/failure | Cold/warm revisit same Mars/Pluto route; zero re-download of immutable unchanged chunks on warm revisit while retained in budget. Tampered hash, stale build response, aborted fetch, network failure, bad schema, unknown semantic, cycle and near-plane crossings remain explicit; verified coarse content persists. |
| A12 interaction | 412×915 portrait, DPR3/render cap2 and desktop; pinch/wheel/pan continuous. Rotate to test depth/edge-on curves. No horizontal overflow, empty-frame transition, repeated fetch thrash, label obstruction of all local geometry, or unexplained missing catalog row. |

## Performance experiment design

First generate the same qualified product, then expose two delivery controls:
progressive (manifest/root/lazy levels) and monolithic (all same bytes concatenated
into one JSON response). Monolithic is a test control only. Neither can invent a
cheaper physical dataset. All metrics include useful **rendered** scene, not just
network response or decoded JSON.

Measure 5 cold browser-context trials and 5 warm same-context revisit trials each
at desktop and Pixel-sized viewport. Record full individual trials, median, p95,
max; do not discard cold outliers. Use (a) loopback unthrottled; (b) explicit test
profile 10 Mbit/s down, 80ms latency, CPU slowdown4 through CDP. This profile is a
stress scenario, not measured Pixel bandwidth/CPU. Same profile/control/camera
path and run order alternation for both. Physical Pixel measurements later use
actual hardware and access path, with device/browser/thermal/network recorded.

Metrics and comparators:

- **Initial data size**: manifest+root <=49,920 gzip bytes (legacy fixture bootstrap
  measured budget). Root includes complete status index and coarse eight-planet
  context; no local fine geometry. If provenance descriptors exceed this, report
  failure and identify bytes before splitting another contract or removing facts.
- **Initial requests**: exactly two product requests (manifest/root), separately
  inventory shell/JS/design/font. Child packages are not prerequisites for root.
- **First useful scene**: timestamp after root's resolved markers and planetary
  curves rasterize with legend/status. Under throttled profile progressive median
  must beat monolithic median; confidence/noise assessed using all trials. If
  indistinguishable, benefit is unearned and record INCONCLUSIVE, not faster.
- **Refinement payload**: measure every byte, vertex and index. Fetch only useful
  levels; per-system packet size must equal canonical descriptor. Report compression
  ratio and parse/upload cost. A two-moon 512-point XYZ baseline is ~31KB gzip,
  not a cap on higher-resolution qualified products.
- **Refinement latency**: selection → request → decoded/verified → first pixels.
  With 150ms candidate cross-fade, cost beyond wire/latency + measured decode/upload
  + two frame intervals must be explained. No blank interval while waiting.
- **Frame behavior**: record camera replay rAF intervals, measured selection,
  decode/upload, draw calls/vertices, long tasks, visible error debt. For the tested
  host/profile, progressive p95 frame interval must not exceed the monolithic
  control p95 by more than one measured display interval (~16.7ms unthrottled here).
  Also report count of frames >2 intervals. This comparison does not certify a
  device FPS; physical Pixel remains a separate gate.
- **Memory**: measure JS heap (estimate), typed-array bytes, GPU buffer accounting,
  peak transition buffers. Progressive geometry peak must be less than loading
  all levels monolithically; after eviction no sustained growth across ten
  back-and-forth visits. Cache ceiling is derived from measured active frontier
  (LOD spec), not invented to make results green.
- **Cache**: after first visit, unchanged nodes are obtained from retained buffers
  or HTTP cache; record transfer bytes/cache hit class. No new resolver requests.
- **Thrash**: oscillate around threshold at +/-5% every 100ms for 5s: no duplicate
  concurrent request per key, no coarsening before 250ms dwell; counters expose
  transitions. Pan to another system during a fetch, then back.

Fail on authority/semantics/coverage/hash defects immediately. Performance misses
falsify the recommended packaging/refinement benefit for this prototype; measure
cause and make a bounded evidence-backed revision, preserving failed runs. A
structural schema PASS is insufficient for any of A1–A12.

## Reproduction commands

Architecture experiments (existing clients only):

```bash
python3 engineering/solar_basemap/bench/measure.py \
  --inspector-root /home/ubuntu/LOOM_SOLAR_INSPECTOR \
  --legacy-html /home/ubuntu/LOOM_ARCHIVE/PIXEL/2026-09-24/shared_download/LOOM_TEST/LOOM_Navigator_Current.html \
  --output /tmp/basemap-measurements.json
NODE_PATH=/home/ubuntu/LOOM_SOLAR_INSPECTOR/node_modules \
LEGACY_HTML=/home/ubuntu/LOOM_ARCHIVE/PIXEL/2026-09-24/shared_download/LOOM_TEST/LOOM_Navigator_Current.html \
CORPUS=/tmp/sample_corpus.json OUTPUT=/tmp/basemap-browser.json \
node engineering/solar_basemap/bench/browser.cjs
python3 engineering/solar_basemap/bench/validate.py
```

Archive path is optional for Python experiment; browser archive case requires it.
If unavailable, use recorded hashed archive measurements; do not replace it with
fabricated historical bytes. Future prototype commands and exact outputs are in
the handoff. Architecture-only work requires packet/schema/experiment validation
and loom-gate, not the entire Inspector functional suite; no Inspector code changed.
