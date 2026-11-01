#!/usr/bin/env bash
# One-command Pixel entry: isolated sparse checkout, existing art, accepted FQ11.
set -euo pipefail
BRANCH="experience/first-jump-fq11-pixel-v01"
ROOT="${FIRST_JUMP_DIR:-$HOME/.local/share/loom-first-jump-v01}"
PORT="${FIRST_JUMP_PORT:-8878}"
if [[ ! -d "$ROOT/.git" ]]; then
  command -v git >/dev/null || { echo "Git is required (Termux: pkg install git python)"; exit 2; }
  command -v python >/dev/null || { echo "Python is required (Termux: pkg install python git)"; exit 2; }
  mkdir -p "$(dirname "$ROOT")"
  git clone -q --depth 1 --filter=blob:none --no-checkout --branch "$BRANCH" \
    https://github.com/loom-2226/loom-2226.git "$ROOT"
  cd "$ROOT"
  git sparse-checkout init --no-cone >/dev/null
  git sparse-checkout set --no-cone \
    '/wayfarer/experience/first_jump/*' \
    '/wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json' \
    '/canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md' \
    '/wayfarer/render/out/cmd_pov.png' '/wayfarer/render/out/cmd_cutaway.png' \
    '/wayfarer/render/out/ext_burn.png' '/wayfarer/render/out/ext_metric.png' \
    '/wayfarer/render/out/ext_departure.png' >/dev/null
  git checkout -q HEAD
else
  cd "$ROOT"
  [[ -z "$(git status --porcelain)" ]] || { echo "Refusing refresh: local First Jump checkout is modified."; exit 3; }
  git fetch -q --depth 1 origin "$BRANCH"
  git checkout --detach -q FETCH_HEAD
fi
if [[ -z "${OPENAI_API_KEY:-}" && -f "$HOME/.config/loom/openai.env" ]]; then
  # Existing Pixel key convention; never transmit this file to the browser.
  source "$HOME/.config/loom/openai.env"
fi
echo "FIRST JUMP / $(git rev-parse --short HEAD)"
echo "FQ11 playback; local URL http://127.0.0.1:$PORT"
echo "Session log under $HOME/.local/state/loom/first_jump/"
python wayfarer/experience/first_jump/server.py --port "$PORT" &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT INT TERM
sleep 1
if ! kill -0 "$PID" 2>/dev/null; then
  echo "Server exited. Check whether port $PORT is occupied." >&2
  wait "$PID"
fi
if command -v termux-open-url >/dev/null 2>&1; then
  termux-open-url "http://127.0.0.1:$PORT"
else
  echo "Open http://127.0.0.1:$PORT in a browser on this machine."
fi
wait "$PID"
