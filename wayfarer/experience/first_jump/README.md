# First Jump v0.1 · Wayfarer Earth → Mars

**DRAFT / NON-CANON GAMEPLAY / FQ11 SOURCE-ONLY / NO NAVIGATOR.**
ALL bodies. ALL sponsors. 2026–2226.

## Pixel launch (one command in Termux)

```sh
curl -fsSL https://raw.githubusercontent.com/loom-2226/loom-2226/experience/first-jump-fq11-pixel-v01/wayfarer/experience/first_jump/start_pixel.sh | bash
```

Requires Termux Python and Git, and a network connection for the initial tiny sparse checkout. Creates a **separate** checkout under `~/.local/share/loom-first-jump-v01`; it does not switch, mutate or qualify the user's existing LOOM_GIT directory. Opens `http://127.0.0.1:8878` in the Pixel browser. Stop with Ctrl-C. Launching from the PR head allows testing without merging. If `curl` is unavailable, install it via Termux package manager.

To run from an already checked-out PR branch: `bash wayfarer/experience/first_jump/start_pixel.sh`. It still uses the isolated sparse checkout; never touches Navigator or campaign state.

## Experience

Captain **GO/HOLD** gates at briefing, preburn, Metric, arrival RCS turn, and trim. Seeded reproducible FQ11 nominal/1% underburn branch. Source-calibrated HUD, reused `wayfarer/render/out` stills. Server-side viewing clock: preburn 115 s, Metric 565 s, turn 42 s, trim 12 s, plus questions and decisions, targeting about 15 minutes. These are **presentation durations**, not flight measurements; physical durations come exclusively from accepted FQ11.

The captain may ask Mara questions during any phase. With `OPENAI_API_KEY` set in Termux, Mara's narration uses a server-side OpenAI Responses API call, with FQ11 timeline and Canon II §§7.1a/b excerpts supplied each time. Without a configured API key or on model/API failure, an openly identified deterministic source-backed reply is used. The browser never receives the API key and never computes flight physics. The LLM has no execution/authorization authority; any generated numerical claim absent from the approved timeline is rejected and logged, then replaced with a source-based reply. This numeric-screening is not a general semantic proof of every nonnumeric sentence.

**Roleplay accommodation:** Canon character file says Mara Venn is the human captain. The temporary `MARA / FLIGHT COMPUTER` label and player-as-captain role are **playtest framing only** and do not amend character canon.

## Numeric authority and honest limits

`build_timeline.py` copies values from the already merged, unmodified
`wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json`.
Each displayed measured number carries its precise JSON source pointer.
`timeline.json` is generated evidence, and the server refuses to start if its content differs from a fresh derivation against the pinned source. No browser-side or server-side flight calculation occurs.

The requested **4.83 km/s preburn Δv** is **NOT a directly recorded FQ11_RESULT.json field** and is deliberately absent from the HUD. Its absence is not an invitation to infer it. Source-recorded values include nominal ~497.7 s, 2827.4 kg, 0.990 g; ~4897.4 s Metric; 19.431 m/s mismatch; 220 s RCS turn at 5 Hz; ~2.001 s trim; 0.121 m/s final. The underburn case records ~492.76 s, 77.740 m/s mismatch, ~8.003 s trim and ~0.481 m/s final. All are evidence playback, not current runtime dynamics.

**Mars approach shell** is a *non-numeric Option A placeholder*, not a certified position. No landing, capture, N-body evolution, thermal certification, Navigator or environmental gate promotion. ENERGY-B and Sun E/p/L balancing remain declared Canon II assumptions/identities, not measured exotic physics.

Session JSONL logs are local (default `~/.local/state/loom/first_jump`) and include seed/case, captain GO/HOLD, questions, replies/provider, unsupported-number evaluation and phase viewing times and quit point. If an API key is configured, questions and FQ11/Canon excerpts go to OpenAI; otherwise questions stay local.

## Quick checks

```sh
python wayfarer/experience/first_jump/build_timeline.py
python -m unittest discover -s wayfarer/experience/first_jump -p 'test_*.py' -v
```

Stop at DRAFT PR. Do not merge or alter the parked Metric workstream.
