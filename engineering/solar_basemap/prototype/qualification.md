# Progressive Solar basemap prototype qualification

**Result:** `EMULATED_PROTOTYPE_PASS`; `PHYSICAL_PIXEL_PENDING`.

This qualifies the bounded prototype described in `../LUNA_IMPLEMENTATION_HANDOFF.md` against `../ACCEPTANCE_BENCHMARKS.md`. It is not production publication infrastructure and does not qualify a physical handset.

## Authority and deterministic product

The compiler ran from code commit `2530d2e5983e25d676a8d5484c4108b2907f5a76` against the read-only `loom_dev` authority snapshot. The TDB epoch is `2226-01-01T00:00:00 TDB` (ET `7131844800.0`, binary64 `41fa91750c000000`), scene center `SUN`, frame `ECLIPJ2000`, aberration `NONE`. Product build ID is `d9d4b4082049a979eabacac0fec400122f0ed3278d33b99f76758e8d2a003a4f`; build-spec ID is `73aac6ecb58fef135d47b1a970280fadaa45aa446b53f3f9cffdf3b217d2d1bd`.

The two independent output trees `/tmp/loom-basemap-a` and `/tmp/loom-basemap-b` passed `--verify-identical`: all 102 files were byte-identical. Product validation passed. The governed catalog contains 110 identities: 103 resolved (90 direct, 13 governed propagated, 5 partial catalog) and 7 unresolved (2 catalog-only). Twelve requested curves are available; each has zero failed independent probes. No client or compiler data was synthesized to fill authority gaps.

The complete build report and immutable current pointer are in [build-reproducibility.json](build-reproducibility.json) and [build-current-pointer.json](build-current-pointer.json). Authority ledger SHA-256 is `fd0784e9fdcaea22d9e8e8b8c93b6ca5db8e6cd84ce293be1bdf4310c8db23a`; canonical ledger SHA-256 is `633e95358b71d7142667c5a3107144f62d69b858c747029674dd45e8ccc4a2f3`.

Manifest plus root is 34,756 gzip bytes (manifest 6,817; root 27,939), within the 49,920-byte initial product budget. Progressive startup requests exactly two product resources. The same-product monolithic control requests one response, with median initial transfer of 15,223,916 bytes in these loopback runs.

## Browser and rendering qualification

The final matrix used Playwright Chromium headless with SwiftShader CPU rendering. The Pixel profile emulated 412×915 CSS pixels at DPR 3 with the renderer capped at DPR 2; desktop emulated 1280×800 at DPR 1. Each delivery/profile has five independent browser trials, each with an unthrottled context and a 10 Mbps down / 80 ms latency / CPU slowdown 4 context, plus a same-context warm route. Delivery order alternated by trial. These network and CPU settings are a reproducible stress case, not a claim about Pixel hardware.

| Viewport | Delivery | First useful scene, plain median | First useful scene, stress median | Frame p95, plain | Frame p95, stress |
|---|---|---:|---:|---:|---:|
| Pixel-sized | Progressive | 563 ms | 1,821 ms | 239.3 ms | 344.8 ms |
| Pixel-sized | Monolithic control | 9,448 ms | 26,314 ms | 244.7 ms | 347.0 ms |
| Desktop | Progressive | 538 ms | 1,785 ms | 235.1 ms | 332.1 ms |
| Desktop | Monolithic control | 9,739 ms | 26,605 ms | 229.5 ms | 331.4 ms |

Progressive frame-p95 deltas against control were −5.4 / −2.2 ms for Pixel-sized plain / stress, and +5.6 / +0.7 ms for desktop plain / stress. All are within the acceptance allowance of one 16.7 ms display interval. The progressive useful-scene median was 16–17× lower in all four profile comparisons. The progressive post-startup JS heap median was 10 MB versus 410 MB for the monolithic control. Raw individual frame samples, timings, cache/heap records, scene summaries and one complete visual/reconciliation record per profile/delivery are retained in [browser-measurements.json](browser-measurements.json).

Absolute RAF p95 and counts above 33.4 ms are high in this software-rendered headless environment: the measured p95 values are about 229–347 ms. Both deliveries show this host limitation, and the relative acceptance comparison passes. This result does not establish frame rate, thermal behavior or memory use on a physical Pixel; test that device before production promotion.

Representative emulated Pixel and desktop local-system captures: [Pixel Earth/Moon](pixel-earth-local.png), [Pixel Mars](pixel-mars-local.png), [Pixel Pluto/Charon](pixel-pluto-local.png), [desktop Earth/Moon](desktop-earth-local.png), [desktop Mars](desktop-mars-local.png), and [desktop Pluto/Charon](desktop-pluto-local.png). The browser harness also samples all eight heliocentric root curves and checks that projected curves contribute pixels. At 412×915/DPR2 render resolution, the Pixel-sized raster sample measured 1,588 Phobos-curve pixels and 2,078 Deimos-curve pixels in Mars context; Moon/Earth measured 230 pixels and Charon/Pluto measured 1,020 pixels. Pluto checks isolate Charon. The continuous routes do not change the Sun-centered physical scene reference.

The corrected replay renders every camera animation step and schedules view refinement during the route. The browser regression requires at least one scene draw per step. An earlier harness revision changed camera state on animation frames but rendered only at segment ends; those intervals were invalid as frame measurements and are excluded from this qualification. The revision was bounded to the QA replay and measurement; the final five-trial matrices use the corrected path. During the Pixel ten-visit Mars/Pluto revisit, immutable chunks had zero transfer bytes, no eviction or memory-limit event, and 2.17 MB of accounted cache use against a 4.84 MB budget.

## A1–A12 acceptance record

| ID | Result | Evidence |
|---|---|---|
| A1 authority | PASS | Product manifest and all-feature browser reconciliation preserve 110 identities, the frozen ET, 103 resolved and 7 unresolved. Epoch positions are from the governed compiler snapshot. |
| A2 geometry semantics | PASS | Compiler tests compare parent-relative `X_body(t)-X_anchor(t)` and the frozen anchor transform against governed samples; Mars/Pluto scene reports compare markers and rendered curves. |
| A3 provenance | PASS | Manifest, source dictionary and sample indices carry authority hashes, source/capability/coverage, IDs, ET bits, frame, units and aberration semantics; negative mismatch tests reject. |
| A4 failures and gaps | PASS | Contract/compiler regression fixtures cover missing source/anchor, catalog-only, segment gaps, horizon truncation and sampling-limit status; no geometry closes across a source gap. Unresolved identities remain in the root index. |
| A5 determinism | PASS | Independent clean output trees compare byte-for-byte (102 files); build IDs and hashes match. |
| A6 errors | PASS | Adaptive probe and simplification tests pass; settled Mars and Pluto GPU conversion is below 0.25 CSS px and total declared geometry debt is at most 1 CSS px. |
| A7 continuous zoom | PASS | Pixel-sized and desktop camera replay draws every animation step; automatic Mars-local Phobos/Deimos refinement appears without a system/reference switch. |
| A8 second system | PASS | Pluto/Charon route resolves and submits parent-relative geometry while preserving Sun-centered anchor/marker distinctions and bounded conversion error. |
| A9 renderer reconciliation | PASS | Identity through resolution/chunk/segment/draw/material/clip/pixels is reported; root curves, Moon, Phobos, Deimos and Charon have visible pixel checks at their test scales. Off-frustum geometry is separately classified. |
| A10 client independence | PASS | QA runs from static publication only; all 40 browser sessions report zero authority calls. Loader tests also verify that no resolver service is required. |
| A11 cache/failure | PASS | Loader regressions cover tampered hash, stale build, aborted/network failure, bad schema, unknown semantic and cyclic hierarchy. Ten Pixel back-and-forth visits fit the derived cache budget with zero immutable-chunk transfer on revisit. |
| A12 interaction | PASS | Pixel-sized and desktop wheel, pan, rotation and touch/pinch interactions keep the viewport within bounds, preserve a nonempty scene and exercise edge-on diagnostics. |

## Reproduction and tests

The required test commands passed after the final browser changes: Python contract/compiler unit tests **14/14**; browser selection cases **5/5**; loader cases **10/10** with zero authority calls; architecture packet validator **7/7**; product validator **110 features**; and independent product reproduction **102/102 files identical**. JavaScript syntax, Python compilation, and `git diff --check` also passed.

The test commands required by the handoff were:

```bash
/home/ubuntu/loom_solar_assets/.venv/bin/python -m unittest tests.test_solar_basemap_contract tests.test_solar_basemap_compile
node tests/solar_basemap_selection.cjs
node tests/solar_basemap_loader.cjs
node --check tests/solar_basemap_browser.cjs
node --check web/solar-basemap/qa.js
node --check web/solar-basemap/renderer.js
python3 -m py_compile tools/serve_solar_basemap_qa.py
python3 engineering/solar_basemap/bench/validate.py
git diff --check
```

Full outputs are recorded in the implementation commit/CI. Generated full products remain in `/tmp`; no authority, Inspector service, database, Solar coverage, or qualification threshold was modified. Physical Pixel qualification remains the only device-level limitation.
