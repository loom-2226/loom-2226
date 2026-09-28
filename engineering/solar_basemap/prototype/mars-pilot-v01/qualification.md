# Mars basemap pilot v0.1

**Result:** `EMULATED_MARS_PILOT_PASS`; `PHYSICAL_PIXEL_PENDING`.

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

## Automated Mars slice

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

## Limits and next gate

This evidence is emulated only. Physical Pixel visual comprehension, touch
behavior, handset frame timing and thermal behavior remain unqualified. The
viewer is served from loopback at `http://127.0.0.1:8770/`; the existing
quantifactus-to-Pixel route still needs host identity/access confirmation before
an exact device URL can be asserted. The worktree also lacks the
`design/Montserrat-VF.woff2` asset referenced by the existing token CSS; the
viewer uses that CSS font stack's platform fallback (the server log records the
font request as HTTP 404). No token or font asset was changed. Stop here for
physical Pixel human acceptance. Pluto/Charon, compiler regeneration, full Solar
requalification and the large benchmark matrix remain deferred until that
acceptance passes.

**Policy overrides:** none. Sandbox elevation was used only to launch the
read-only preflight process, the loopback viewer and Chromium required by the
requested browser check; no LOOM rule, contract, threshold or authority gate was
overridden.

## PILOT AUTHORITY completeness audit

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
