# Wayfarer First Jump v0.3 · Earth → Mars

**ALL bodies. ALL sponsors. 2026–2226.**
**DRAFT PLAYTEST, NON-CANON, NON-RUNTIME FLIGHT, NO NAVIGATOR.**

## Run on the Pixel

In Termux with Git, Python and curl installed:

```sh
curl -fsSL https://raw.githubusercontent.com/loom-2226/loom-2226/experience/first-jump-v03-animated-solar-display/wayfarer/experience/first_jump/start_pixel.sh | bash
```

This uses a separate lightweight `~/.local/share/loom-first-jump-v03` checkout and opens **http://127.0.0.1:8880**. It leaves v0.1/v0.2 and existing LOOM repositories untouched. Ctrl-C in Termux stops the local server.

On first start, the launcher uses existing private Termux API key configuration, or offers a hidden key prompt. If no API key is provided, Mara has in-world scripted comms. If configured, each question sends the **selected accepted FQ11 case** and **Canon II §§7.1a/b excerpts** to the live model. In-character responses are screened against their cited FQ11 numbers, with provider outcomes and unsupported claims in the local JSONL session log.

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

The server alone owns **viewing-time phase progression**. Scrub and pause change the presentation cursor, not authoritative campaign time or ship state. JavaScript only draws precompiled screen coordinates and manipulates camera zoom/rotation. No browser-side physics, ephemeris propagation, or ship position calculation.

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
