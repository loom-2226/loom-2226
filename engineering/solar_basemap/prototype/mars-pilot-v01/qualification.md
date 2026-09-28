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
an exact device URL can be asserted. Stop here for physical Pixel human
acceptance. Pluto/Charon, compiler regeneration, full Solar requalification and
the large benchmark matrix remain deferred until that acceptance passes.

**Policy overrides:** none. Sandbox elevation was used only to launch the
read-only preflight process, the loopback viewer and Chromium required by the
requested browser check; no LOOM rule, contract, threshold or authority gate was
overridden.
