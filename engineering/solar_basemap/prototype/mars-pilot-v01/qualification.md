# Mars basemap pilot v0.1

**Current result:** `AUTOMATED_PIXEL_REPAIR_PASS`; `PHYSICAL_PIXEL_PENDING`
for a new human device test. The first physical Pixel acceptance failed on touch
orientation, body selection, zoom sensitivity and presentation. It also
physically demonstrated coherent Solar → Mars → Phobos/Deimos refinement.
The current product did not develop Jupiter local moon-orbit context.

**Primary change class:** `class:runtime`. This is a bounded repair stacked on
PR #318. PR #319 (`9a6b87c0a83c27bc02432625718b529d16f403ec`) is included as a
tooling dependency only; it contributes the governed-development Skill and its
two read-only review profiles. Neither source PR is changed or merged.

## Scope and inputs

- Baseline: PR #318 head `2ce658c53b819dd5d8cf7632265a0483dd65fc99`.
- Product: existing validated build `d9d4b4082049a979eabacac0fec400122f0ed3278d33b99f76758e8d2a003a4f` from `/tmp/loom-basemap-a`.
- Product identity remains numeric ET `7131844800.0` TDB, Sun / ECLIPJ2000 / km, with 110 catalog identities (103 resolved, seven unresolved).
- No compiler/product regeneration, Solar authority call, database write, Pluto/Charon route, full Solar qualification, or comparative benchmark matrix was run.

## Defect and repair

The first Mars-only replay selected a Pluto system detail level while the camera
was approaching Mars. In `currentView`, a system bound wholly behind the camera
had `zmin <= 0`, which was treated as a near-plane intersection and assigned
infinite screen error. That admitted and fetched unrelated local detail. The
renderer now rejects a bound when `depth + radius <= 0`; a bound that intersects
the near plane still receives conservative refinement.

A temporary test assertion requiring Mars to be the only local system also
reported Earth detail in the view. That assertion was narrowed to the authorized
deferred boundary: Mars detail must be present and Pluto/Charon detail must not
be selected. The product contract does not prohibit visible Earth context. No
acceptance threshold or product contract changed.

## Initial replay-based Mars slice (historical; not the pilot acceptance path)

This first browser result used the QA `replayApproach` flight hook and therefore
does not establish the governing real-user-path requirement. The focused
DOM-touch acceptance and its complete authority audit are recorded in the
`PILOT AUTHORITY completeness audit` below; that is the acceptance evidence for
this repair.

Command:

```bash
SOLAR_BASEMAP_URL=http://127.0.0.1:8770 \
SOLAR_BASEMAP_EVIDENCE=/tmp/loom-basemap-mars-pilot-evidence \
node tests/solar_basemap_browser.cjs \
  --profile pixel --delivery progressive --trial-index 0 --mars-only
```

The retained evidence is `pixel-progressive-trial-0.json` and
`pixel-progressive-warm-mars.png` in this directory.

- Pixel-sized viewport 412×915, emulated DPR 3 / renderer cap 2; one unthrottled
  Chromium/SwiftShader trial.
- Continuous Solar-to-Mars route completed 60 requested animation steps with
  193 rendered frames; Phobos and Deimos reference curves each contributed
  isolated pixels (1,588 and 2,078).
- All 110 identities reconciled; Mars local detail was selected and deferred
  Pluto/Charon detail was not selected.
- Settled Mars geometry and camera-relative Float32 error remained within the
  existing 1 CSS px total / 0.25 CSS px conversion limits. Wheel zoom, drag
  pan/rotation and two-finger pinch changed the camera; no horizontal overflow;
  99 markers remained visible after interaction.
- Warm revisit transferred zero immutable object bytes. The browser made zero
  authority/resolver calls and reported no page errors.
- Initial useful scene: 585 ms in this emulated run. This is a single-trial
  diagnostic, not a performance qualification. The recorded frame samples are
  host/software-renderer behavior and do not establish Pixel performance.

## Other checks

- `python -m unittest tests.test_solar_basemap_contract tests.test_solar_basemap_compile` — 14 passed.
- `node tests/solar_basemap_selection.cjs` — 5 passed.
- `node tests/solar_basemap_loader.cjs` — 10 passed; zero authority calls.
- `tools/build_solar_basemap.py --validate /tmp/loom-basemap-a` — valid, 110 features.
- `tools/build_solar_basemap.py --verify-identical /tmp/loom-basemap-a /tmp/loom-basemap-b` — identical, 102 files.
- `node --check tests/solar_basemap_browser.cjs` and `git diff --check` — passed.

## First physical Pixel result and next gate

The first physical Pixel test failed on mobile orientation, selection, zoom
sensitivity and Navigator fidelity. The product's Mars hierarchy was observed
working on the device; Jupiter's generalized hierarchy was not available.
The bounded repairs and new automated touch evidence below are ready for a
new human Pixel test. Handset visual comprehension, touch feel, frame timing
and thermals have not yet passed that retest.
Live serving is now verified: `tailscale serve status` maps
`https://quantifactus.tail94e5cb.ts.net:8443/` to `http://127.0.0.1:8770/`;
the exact progressive-delivery URL returned HTTP 200 and served the committed
repair HTML, renderer and basemap scripts. The worktree also lacks the
`design/Montserrat-VF.woff2` asset referenced by the existing token CSS; the
viewer uses that CSS font stack's platform fallback (the server log records the
font request as HTTP 404). No token or font asset was changed. Stop here for
physical Pixel human acceptance. Pluto/Charon, compiler regeneration, full
Solar requalification and the large benchmark matrix remain deferred until that
acceptance passes.

**Policy overrides:** none. Sandbox elevation was used only to launch the
read-only preflight process, the loopback viewer and Chromium required by the
requested browser check; no LOOM rule, contract, threshold or authority gate was
overridden.

## Historical pre-physical PILOT AUTHORITY audit — superseded

The following automated audit preceded the failed physical Pixel test. Its
reported PASS rows are preserved as historical evidence, not the current
physical-gate verdict. The historical runner source is retained at commit
`f298a9679999eb617c062a40b72821ed493606b3`; the current runner was revised
for the repair. The updated audit after repair is below.

The focused acceptance path is `tests/solar_basemap_mars_acceptance.cjs`. It
drives only the viewer's DOM touch path in a 412×915 CSS-pixel viewport at DPR
3; camera, target, system and reference state are observed through a read-only
diagnostic snapshot. It does not call `replayApproach()`, `moveToward()`, or an
equivalent flight/teleport API. The retained run is
`solar-basemap-mars-real-user-acceptance.json` with screenshot
`solar-basemap-mars-real-user-acceptance.png` in this directory. Product build
is unchanged at
`d9d4b4082049a979eabacac0fec400122f0ed3278d33b99f76758e8d2a003a4f`.

| PILOT AUTHORITY item | Status | Deterministic evidence |
|---|---|---|
| Fine Solar LOD emits finer curves into the draw list and rendered pixels before coarse geometry exceeds the refinement bound. | PASS | Real touch-path trace selected and drew Solar level 3 (8 curves; Mars 257 vertices), with 8,988 amber line pixels. Maximum sampled coarse error before fine draw was 0.537804 CSS px; the bound is 0.75 CSS px. Initial embedded representation measured 0.559702 CSS px. Evidence JSON `fine_solar_lod`; repair in `basemap.js` and Solar error measurement in `renderer.js`. |
| Continuous Mars admission preserves useful heliocentric context until Mars-local Phobos/Deimos context is useful. | PASS | Same pinch route ends at 3,146,480.84 km from Mars; Mars label is visible with a clipped, 5,000,000 km Mars heliocentric context arc (4 projected/15 vertices, opacity 0.12), while Phobos and Deimos each have 33 projected vertices and mint pixels total 152. Evidence JSON `mars_context`. |
| One-finger map pan, focal-point-aware pinch zoom, and distinct rotation gesture. | PASS | DOM touch evidence records changed target with unchanged rotation for one-finger pan; pinch changes distance and target while maximum Mars-anchor drift is 15.2333 CSS px; two-finger twist changes rotation while distance is unchanged. Evidence JSON `one_finger_pan`, `focal_pinch`, and `two_finger_twist`. |
| Restrained orbit styling and clear Sun/planet/minor-body symbol hierarchy. | PASS | Renderer uses subordinate heliocentric/reference orbit opacities (0.28/0.44 base; Mars local context arc 0.12) and token colors. Acceptance observes Sun/planet/minor symbol sizes 9/6/4 CSS px and asserts strict hierarchy; it also asserts the parent arc is fainter than Mars moon curves. Evidence JSON `mars_context` and test assertions in `tests/solar_basemap_mars_acceptance.cjs`. |
| Useful scale-aware labels, truthful scale readout, and quieter QA chrome. | PASS | Mars label observed in Mars-local view. Acceptance recomputes center scale from camera projection within 1% and scale-bar length within 2 CSS px of its labeled distance. Screenshot shows compact context/scale panel, subordinate QA controls, symbol legend and gesture hints. Evidence JSON `mars_context` and retained PNG. |
| Real-user-path Solar → Mars → Phobos/Deimos acceptance with no privileged route or authority access. | PASS | `tests/solar_basemap_mars_acceptance.cjs` uses CDP touch events on the same canvas pointer handlers available to the user. It asserts the Solar→Mars→both moons route and rendered pixels, and that forbidden flight/system/camera mutation calls are absent from the test path. Runtime instrumentation observed zero authority/resolver/ephemeris/state API requests and zero browser errors. Evidence JSON method, `authority_calls: 0`, `page_errors: []`. |

### Pilot presentation policy recorded

These are renderer presentation/admission choices for this pilot; no generated
product, compiler contract, governed positions, authority semantics or acceptance
threshold was changed:

- Prefetch the next Solar level when active representation error is above 0.25
  and no more than 0.75 CSS px; the existing 0.75 CSS px refinement bound is
  retained.
- Preserve a Mars heliocentric context arc within 5,000,000 km of Mars, clipped
  to its nearest governed orbit samples and drawn at opacity 0.12.
- Keep Mars-local reference lines visible from the existing 16 CSS px detail
  admission point with a 0.35 opacity floor, ramping to full by 24 CSS px.
- Use 9/6/4 CSS px Sun/planet/minor symbols; show labels at 5 CSS px Sun
  diameter, 22 CSS px heliocentric planet separation and 20 CSS px parent-relative
  minor-body separation. Focal snapping is limited to an 8 CSS px feature hit
  radius.
- Reference curves use subdued token colors/opacity and the mobile QA panel
  uses compact status, scale, gestures and catalog/reset controls.

**Policy overrides recorded:** none. These bounded renderer decisions are
within the authorized presentation work; no governance rule or inherited
acceptance criterion was overridden. No pilot-authority item is deferred.

## Physical Pixel repair — current PILOT AUTHORITY COMPLETENESS

The physical Pixel trial failed the previous presentation/interaction gate. It
also demonstrated that the qualified product can refine from the Solar scene
into coherent Mars, Phobos and Deimos context. The current repair changes only
the client renderer, touch interaction and QA presentation. The current
qualifying run is `solar-basemap-pixel-repair-acceptance.json`, with overview and
Mars-oblique screenshots in this directory. The 412×915 DPR3 browser runner
uses actual canvas touch events for every navigation action; read-only
instrumentation observes state and pixels. Human physical Pixel retest remains
required.

Focused deterministic checks on this repair: `node tests/solar_basemap_selection.cjs`
(5/5), `node tests/solar_basemap_loader.cjs` (10/10, zero authority calls),
`node tests/solar_basemap_mars_acceptance.cjs` (PASS with retained JSON and
screenshots), `node --check` for the changed JavaScript files, and
`git diff --check` (PASS). No Pluto/Charon flight, compiler regeneration, full
Solar qualification or large benchmark matrix was run.

| # | PILOT AUTHORITY item | Status | Evidence |
|---:|---|---|---|
| 1 | Fine Solar LOD | PASS | Touch trace drew level 3 in the Solar draw list and projected lines with 14,783 lit pixels; maximum sampled pre-fine coarse error was 0.371 CSS px, below the unchanged 0.75 CSS px bound. JSON `fine_solar_lod`. |
| 2 | Mars parent/local context | PASS | At 383,373 km camera distance, a clipped Mars heliocentric arc remains at opacity 0.09 while Phobos and Deimos each project 33 curve vertices at opacity 0.56. All three have visible labels/markers at useful moon-orbit scale; 2,627 lit pixels and the Mars-oblique screenshot record the view. JSON `mars_context`. |
| 3 | One-finger pan | PASS | One-finger DOM touch changes the target and leaves rotation unchanged. JSON `one_finger_pan`. |
| 4 | Focal pinch zoom | PASS | The selected Mars marker stays at the focal point through 15 real touch pinches, with maximum measured drift 0 CSS px. Camera distance changes continuously from 7.48 billion to 383,373 km. JSON `pinch`. |
| 5 | Controlled Pixel zoom sensitivity | PASS | A 4% pinch span change falls inside the 6 CSS px deadband and changes neither distance nor target. A full 2.4× span gesture produces a 0.518 distance ratio using 0.82 log gain; the test checks this absolute ratio once against alternating pointer events. Each gesture is bounded to at most 3×. JSON `pinch` and test assertion. |
| 6 | Mobile yaw and pitch orientation | PASS | A parallel two-finger drag changes yaw from 0 to −0.15 radians and pitch from 0 to +0.35 radians while distance remains unchanged. The retained Mars-oblique screenshot shows the tilted local orbital plane. JSON `orientation`. |
| 7 | Tap body selection/focus | PASS | Real marker taps select Sun, Earth, Mars, Jupiter and Saturn. Each has a visible selection ring and the same camera distance; non-Sun selection eases the target to the governed position without a jump in distance. JSON `focus`. |
| 8 | Navigator-derived symbol hierarchy | PASS | Sun is a warm circular glow/core (17 CSS px), planets are filled ice circles (10 CSS px), and minor bodies are subdued steel diamonds (4 CSS px). Only existing LOOM token colors are used. JSON `presentation`; overview screenshot. |
| 9 | Navigator-derived orbit/label styling | PASS | Heliocentric curves use subdued steel, local reference curves ice, parent context 0.09 opacity, and local curves up to 0.56 opacity. Labels are gray-white, prioritized and collision-checked; the selected body remains legible. Default map details are collapsed. JSON `presentation` and both screenshots. |
| 10 | Truthful scale readout | PASS | Acceptance recomputes the center projection within 1% and the 1/2/5 scale-bar width within 2 CSS px of its labeled distance. At Mars orbit scale it reads about 347 km per CSS px with a 20,000 km bar. JSON `mars_context`. |
| 11 | Ordinary-touch Solar → selected Mars → Phobos/Deimos route | PASS | The same viewer touch path pans, taps Mars, performs 15 bounded pinches, and reaches visible Mars/Phobos/Deimos labels, markers and governed local curves. No user-facing system mode changes. JSON `focus`, `pinch`, `mars_context`; Mars-oblique screenshot. |
| 12 | No privileged acceptance shortcuts | PASS | The runner dispatches CDP touch events only; its evaluations read diagnostic state/pixels and append an observation trace. It does not invoke flight hooks, set camera/target, switch systems or call hidden fit-to-body routes. Source: `tests/solar_basemap_mars_acceptance.cjs`. |
| 13 | Zero authority calls | PASS | Browser request instrumentation observed zero authority/resolver/ephemeris/state API calls and zero page errors. JSON `authority_calls`, `page_errors`. |
| 14 | Jupiter limitation recorded as product-content scope | ESCALATED | Qualified product root SHA-256 `b6b6979f5de33d54620f54b2c12646a5e4ca13760a264ce88f1ba45ce1d9ff8c` has local nodes only for Earth, Mars and Pluto and no Jupiter parent-relative reference curves. The physical Jupiter observation is recorded in `JUPITER_PRODUCT_BOUNDARY_ESCALATION.md`; future generic product generation requires separate authorization. JSON `jupiter_product_limitation`. |

### Current renderer presentation policy

The 0.75 CSS px Solar refinement limit remains unchanged. Renderer-only choices
for this Pixel repair are a 6 CSS px pinch deadband, 0.82 log-distance gain and
3× maximum distance ratio per gesture; two-finger orientation begins after a
9 CSS px shared-center movement or 0.12 radian turn and excludes zoom for that
gesture. Tap hit radius is at least 18 CSS px. The selected body remains the
focal anchor and target motion eases for 520 ms. These are user interaction
controls, not new spatial authority or generated-product thresholds.

The parent-context arc applies generically to product local nodes (Earth, Mars
and Pluto): its radius is the greater of 5,000,000 km or 160 times the product
node bound, and it activates only near that parent and at that camera scale.
It clips existing governed orbit samples. Local reference curves retain the
existing 16 CSS px admission and use a 0.5 opacity floor, rising to full by
24 CSS px. Catalog satellites under `solar` without a local product node, and
barycenters, remain inspectable in the catalog but do not masquerade as local
map detail. No client-side orbit is synthesized.

**Policy overrides:** none. Product build, compiler, Solar authority, schema,
database, launcher and reference frame are unchanged. The Pixel retest is the
remaining human gate. Jupiter product generation is a separate escalated
successor; it does not block the bounded Mars retest.
