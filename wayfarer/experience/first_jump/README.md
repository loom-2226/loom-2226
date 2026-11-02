# Wayfarer: First Jump v0.2

ALL bodies. ALL sponsors. 2026–2226.

**DRAFT / EARTH → MARS PLAYTEST ONLY.** FQ11-derived flight figures. No Navigator, new physics, invented collapse radius, orbital capture, new rendered assets, or canon changes.

## Pixel: one command (Termux)

```bash
curl -fsSL https://raw.githubusercontent.com/loom-2226/loom-2226/experience/first-jump-v02-story-evidence-pixel/wayfarer/experience/first_jump/start_pixel.sh | bash
```

Requires Git, Python and curl installed in Termux. The launcher makes its **own** sparse checkout in `~/.local/share/loom-first-jump-v02`, opens **http://127.0.0.1:8879**, and does not modify any existing LOOM checkout. Stop with Ctrl-C. Do not use the older v0.1 localhost port 8878 for testing this draft.

## Mara's live channel

The earlier Pixel screenshot clearly showed `OFFLINE EVIDENCE` and an `evidence_fallback` response. In v0.1, that exact status means the running server saw **no `OPENAI_API_KEY`**. That is why there was no live LLM call. This cannot be fixed by rewriting dialogue alone.

v0.2 checks, in order: environment `OPENAI_API_KEY`; existing Pixel `~/.config/loom/openai.env`; and dedicated `~/.config/loom/first_jump.env`. If absent it **prompts once in Termux** for an OpenAI API key (input hidden). If supplied, saves it only on that device in the dedicated file (mode 600) and passes it to the server process; it is never returned to the browser. Press Enter instead to play scripted comms. The terminal prints `LIVE MODEL CONFIGURED` or `SCRIPTED / MISSING KEY`; the evidence drawer includes channel configuration. A configured key is **not proof the API responded**: each question's `live_llm` success or specific API/fallback reason is stored in the session JSONL. External model connectivity was not exercised by automated tests.

At each free-text question the Python server sends *only* the selected accepted FQ11 case, Canon II §§7.1a/b excerpts, and the player's question to the live Responses API. The model is instructed to return in-world lines and internal support keys; the server validates the referenced keys and screens every spoken number against the specifically cited current-case timeline values, rejecting bad lines into the log and using an in-character fallback. No browser-side model or physics calculation. Screened numeric provenance is the narrow earned guard, not independent validation of every possible qualitative claim.

## Two layers, one ship

**STORY**: In-character command deck, torch, weave, Mars approach, trim, and Mars Traffic handoff. Mara/crew speech has no footnotes, lab qualification language or audit status. Existing `cmd_pov.png` and exterior Wayfarer images are cropped in CSS as immersive scene backdrops. Mars grows as a **purely theatrical CSS approach cue**, *not* range or trajectory rendering. No new image assets.

**EVIDENCE**: Ship's record panel, closed by default. Numeric HUD readings have an **earned** mark. Tap a figure and the server fetches the exact FQ11 JSON pointer, then logs the inspection. The drawer also holds an optional replay-case selector and diagnostic status, out of the story view.

First play is **NOMINAL** unconditionally. Replay is seeded and may choose under-burn; optional replay setting selects nominal/under-burn explicitly. Captain GO/HOLD remains at actionable phases; end/quit screens show only **Replay**. Final on-screen line: “Holding at Mars approach shell. Mars Traffic has us from here.”

### Flight evidence is unchanged

Source: `wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json` on merged main. `timeline.json` contains copied values with individual source pointers and SHA256, verified at startup. Neither server nor browser simulates a trajectory, calculates physical quantities, or changes flight state. No 4.83 km/s preburn Δv appears, because FQ11 does not directly report that field. No numerical Earth/Mars shell is assigned. The existing FQ11 frozen-potential and E/p/L identity limitations remain intact behind the presentation.

Session logs: `~/.local/state/loom/first_jump/<session>.jsonl`. They preserve questions, live/scripted replies, references, rejected unsupported numerical claims, GO/HOLD, viewing time per phase, replay seed/case, and quit point. The user may inspect logs locally; **the browser shows only the relevant number's provenance on request**.

## Checks

```bash
python3 -m unittest discover -s wayfarer/experience/first_jump -p 'test_*.py' -v
bash -n wayfarer/experience/first_jump/start_pixel.sh
```

Local tests cover source integrity, in-world JSON model protocol with mocked Responses API, numeric guard, first-nominal branch, replay variant, HTTP/evidence path and logging. Actual live LLM reply and Pixel visual acceptance require a configured key and on-device playtest; do not claim either from a local mock.

Stop at draft. No merge.
