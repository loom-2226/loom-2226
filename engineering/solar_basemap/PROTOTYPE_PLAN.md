# Bounded prototype implementation plan

Implementation is a subsequent authorized task. This packet implements no part
of the production basemap. Entry and commands are in LUNA_IMPLEMENTATION_HANDOFF.

1. Establish a separate prototype worktree based on pinned PR299 code; incorporate
   only this engineering packet. Do not merge main or the specification branch
   into PR299. Re-read current main governance and verify dependency identity.
2. Implement typed product records and structural + semantic validators first.
   Add negative fixtures for missing authority, mixed frame/ET, mismatched source,
   invalid anchor, broken hierarchy, malformed counts/hash and gap bridging.
3. Implement read-only offline acquisition using existing ledger/registry/resolver
   and Inspector helper algorithms. Freeze 2226 TDB. Acquire every catalog epoch
   position; requested curves: eight planets around Sun, Moon/Earth,
   Phobos/Mars, Deimos/Mars and Charon/Pluto. Record all other curves NOT_REQUESTED.
4. Implement adaptive exact sampling, independent probe validation, segmented
   simplification and bounds as specified. Neither runtime HTTP nor client does
   physical work. Deterministic captures/fixtures allow ordinary unit tests offline.
5. Serialize canonical manifest/root/chunks/provenance; validate every resource;
   build twice with separate process/query caches. Compare byte hashes. Publish
   into a temporary output root and atomically write current only after all gates.
6. Implement shared browser loader/refinement/diagnostic module, independent from
   a renderer. Unit test deterministic camera sequences and failure/cache cases.
7. Implement minimal QA page with existing Three.js and LOOM design tokens. Camera
   supports pinch/wheel, pan and rotation in a single Sun-centered scene; optional
   focus button may move camera but cannot switch systems. Show epoch, reference-
   geometry legend, catalog failures and active content/LOD diagnostics. Do not add
   Atlas, civilization, gameplay, time controls, ship dynamics or Inspector menus.
8. Automate continuous camera flight through Solar → inner Solar → Mars → local
   Mars → Phobos/Deimos, then a separate Pluto/Charon sequence. Camera path is
   replayable and independent of refinement decisions. Run all acceptance cases.
9. Produce compressed-byte/request, first useful scene, per-refinement, memory,
   frame, provenance and before/after-pixel reports. Compare progressive versus
   monolithic same-data control under identical network/CPU conditions. Stop if
   objectives fail; correct within scope or record falsification, not threshold tuning.
10. Commit/push prototype code and earned evidence on its own PR, never merge.
    Report EMULATED_PROTOTYPE_PASS/FAIL separately from PHYSICAL_PIXEL_PENDING.

Expected future files (not created by this spike):

```text
src/loom_solar_basemap_contract.py
src/loom_solar_basemap_compile.py
tools/build_solar_basemap.py
tools/serve_solar_basemap_qa.py           static files only
web/solar-basemap/basemap.js              reusable loader + selection + diagnostics
web/solar-basemap/renderer.js             Three.js adapter only
web/solar-basemap/index.html
web/solar-basemap/qa.js
web/solar-basemap/qa.css
tests/test_solar_basemap_contract.py
tests/test_solar_basemap_compile.py
tests/solar_basemap_selection.cjs
tests/solar_basemap_browser.cjs
engineering/solar_basemap/prototype/qualification.md
engineering/solar_basemap/prototype/evidence/*
```

Do not extract/refactor Inspector just to share helpers during this prototype;
import the pinned pure/offline helper behavior behind a basemap adapter. If later
separation is necessary, it is a small separately tested refactor after proving
this publication design. Compiler status is derived-cartographic in every output.
