# LOOM Wayfarer L1 · Android-safe 3D rendering correction
**2026-10-29 · RESEARCH · NON-CANON · NON-RUNTIME**

## User-observed failure

On Android the previous self-contained HTML document loaded its headings, buttons and labels, but the 3D display area was entirely blank (user screenshot). The prior tests in headless Chromium using the software WebGL stack were insufficient evidence of compatibility with Android's local `content://media/external/downloads/...` document handling and graphics drivers.

**Exact device-side root cause is unconfirmed**: the screenshot only establishes *no visible 3D output*, not whether the failure was shader compilation, platform restrictions, browser GPU policy, draw path, or another JavaScript issue.

## Small direct fix

Produce a **separate simpler viewer**, `render/out/wayfarer_l1_android_safe_3d.html`, using ordinary **2D Canvas software projection of 3D geometry**, without creating WebGL contexts, loading modules, dependencies, textures or network assets. The program draws depth-ordered three-dimensional floors, segmented acceleration-seat shells and represented occupants, role displays, central low-g command workpoint and separate former-S4-site mission work area. All six acceleration seats are retained.

The new page supports:
- click/tap **new F1-R2 vs original F1** and immediately repaint the actual scene;
- one-finger orbit, two-finger pinch/pan, mouse wheel zoom;
- plan, side and orbit view presets, with reset;
- toggles for occupants, displays, deck platforms and labels;
- embedded **base64 PNG rendering of revised F1** behind the canvas as a static fallback if JavaScript cannot run. Only hide this fallback after first successful Canvas2D paint.
- self-contained single HTML; no remote dependencies, internet access or WebGL needed.

## Actual verification performed

- Python generator syntax and extracted JavaScript syntax checked.
- Chromium with `--disable-webgl --disable-webgl2 --disable-gpu` and mobile-sized viewport 412×915: both variants displayed via Canvas2D with distinct image hashes; 412×493 pixel canvas had varied image content; no browser errors.
- Alternative camera view was selected successfully.
- Chromium JavaScript completely **disabled**, 412px mobile viewport: embedded fallback PNG loaded, natural dimensions 600×404, remained visible without script; screenshot inspected.
- Not directly tested on user's physical Pixel/Android `content://` path. **Don't claim device-confirmed success until user opens it.**

## Preservation and authority

Source on isolated research branch under `render/make_l1_canvas2d_android_viewer.py`. The corresponding committed HTML already embeds its fallback preview and is the exact deliverable; its generator may optionally read `render/out/l1_android_preview.png` in the research VM when regenerating.

Only research changes. Existing source Rev7, PR #432, canonical technology timeline and runtime are not modified. Stop after delivering a viewer that visibly paints on Android-class devices; don't build a graphics framework.
