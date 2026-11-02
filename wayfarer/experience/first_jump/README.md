# Wayfarer First Jump v0.4 · Earth → Mars

**ALL bodies. ALL sponsors. 2026–2226.**
**DRAFT PLAYTEST, NON-CANON, NON-RUNTIME FLIGHT, NO NAVIGATOR.**

## Run on the Pixel

In Termux with Git, Python and curl installed:

```sh
curl -fsSL https://raw.githubusercontent.com/loom-2226/loom-2226/experience/first-jump-v04-continuous-playback/wayfarer/experience/first_jump/start_pixel.sh | bash
```

This uses a separate lightweight `~/.local/share/loom-first-jump-v04` checkout and opens **http://127.0.0.1:8881**. It leaves v0.1/v0.2 and existing LOOM repositories untouched. Ctrl-C in Termux stops the local server.

On first start, the launcher uses existing private Termux API key configuration, or offers a hidden key prompt. If no API key is provided, Mara has in-world scripted comms. If configured, each question sends the **selected accepted FQ11 case** and **Canon II §§7.1a/b excerpts** to the live model. In-character responses are screened against their cited FQ11 numbers, with provider outcomes and unsupported claims in the local JSONL session log.

## Continuous playback v0.4

A **single FQ11-elapsed mission clock**, smoothly advanced by browser `requestAnimationFrame`, controls narrative scene/caption, map frame/camera, timer and display interpolations. The server synchronises the clock and persists player actions; the browser never solves physics. **204 seconds** of active presentation (~3:24 plus decision time): 29 s burn, 151 s Metric, 18 s RCS turn, 6 s trim. The ship remains fixed at Earth during preburn and Metric, appears at Mars only at the Metric boundary, and never traverses an invented line. Three required decisions only: **authorise burn, authorise jump, authorise trim**. Metric runs directly into the 220 s source-time RCS turn with no extra gate. Manual pause and mission-wide scrub are visual controls, with seeking capped by already-authorised decisions.

Burn plume + FQ11-interpolated water remass (0 to the accepted 2.827 t nominal), camera Earth close → solar pull-back → Mars close, pulse/shimmer, FQ11 94.057° nominal attitude turn, and source-endpoint arrival mismatch animation (19.431 to 0.121 m/s). All intermediate values are explicitly **linear presentation interpolation**, not additional calculated physics. Every earned numeric endpoint remains in FQ11 with evidence drawer inspection and session log.

**Open numerical item:** the requested 4.83 km/s preburn Δv is absent as an accepted scalar in FQ11_RESULT.json. It is **not claimed or displayed** in this build. A speed counter requires a separately accepted measurement with a traceable scalar endpoint. This is the only requested animation datum intentionally deferred to preserve the FQ11-only authority rule.

## Playable controls

- Captain's **GO/HOLD** at each decision; first session always nominal. Under-burn is on replay or explicitly selected in the ship's record.
- **NAV/DECK** swaps an animated solar map and existing `cmd_pov` / Wayfarer art. Earth and Mars occupy precisely precompiled display positions; the ship is **at Earth**, then **at Mars**, never drawn along a transit trajectory.
- During the Metric interval the source-time planet context advances; the ship stays at Earth until the arrival effect at Mars. **No connecting line** or ordinary-space occupancy. Animated pulses are theatrical, not sampled Metric physics.
- At arrival a separate **stylised Mars close view** contains a Wayfarer approach marker but **no radius, range, scale bar, physical XYZ coordinate or capture orbit**.
- Use **PAUSE/RESUME**, **SCRUB** within the current authorised phase (the command automatically holds playback), **+/- zoom**, **rotate buttons**, or drag and pinch the map on the Pixel.
- Numbers stay grounded in accepted FQ11 `timeline.json`. Tap an **earned** reading to open the actual FQ11 JSON pointer in the closed-by-default evidence panel. Mara's speaking text stays free of citations and audit language. End scene is: “Holding at Mars approach shell. Mars Traffic has us from here.” Only **Replay** remains at completion.

## Display data and authority

`map_display.json` is a **read-only presentation product** generated once by `build_map_display.py`, not by the Pixel. Its sole planetary source is **the existing FQ11 input snapshot**:
`wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101/FQ11_INPUT.json` at **2226-08-29T05:00:00Z** (original Solar-system `ephemeris_states` source). It uses the **same FQ11 `metric_arrival_v1.planetary_state`** Sun-only ephemeris propagation already used by FQ11 to compile 189 Earth/Mars display samples and contextual orbit lines, projected once into fixed Sun-centered map coordinates. These are **planetary display context, not flight values**. Generation runs offline with numpy/scipy; the Pixel requires neither. At server startup, the input/source epoch hash, accepted FQ11 result hash, display role and all phase durations are validated. No Navigator core or solver is imported or run.

**Important visual limitation:** Earth and Mars move physically only a tiny fraction of a map pixel across a short Metric leg. The source-clock advance is real within the FQ11 ephemeris model; bright jump pulses, camera controls and the final Mars view communicate the discontinuous transfer. It would be scientifically dishonest to animate rapid orbital motion or a continuous ship path just to make the picture dramatic.

FQ11 finite preburn, Metric duration, RCS and trim remain the only source for flight measurements. No exact ordinary-flight sample history is available in accepted results, so **no interpolated burn/recovery trajectory is presented**. That remains a separate later PR. The preburn delta-v is not shown because it is not a source FQ11 field.

The server alone owns **viewing-time phase progression**. Scrub and pause change the single mission presentation cursor, not authoritative campaign time or ship state. JavaScript only draws precompiled screen coordinates and manipulates camera zoom/rotation. No browser-side physics, ephemeris propagation, or ship position calculation.

**No new renders.** The solar map is lightweight SVG in the existing UI; original art remains. No Navigator integration, no capture, no certified collapse position, no new physics, no canon mutation. This PR includes v0.2 story/evidence changes from draft #451 as well as v0.3; it is reviewable against main as a single unmerged change.

## Test

```sh
python3 -m unittest discover -s wayfarer/experience/first_jump -p 'test_*.py' -v
bash -n wayfarer/experience/first_jump/start_pixel.sh
```

The display compiler can be rerun **only in an offline engineering checkout with NumPy/SciPy**:

```sh
python3 wayfarer/experience/first_jump/build_map_display.py
```

Stop at draft PR. Keep Navigator parked.

Additional narrow browser clock check: `node wayfarer/experience/first_jump/test_clock.js` (engineering host only).
