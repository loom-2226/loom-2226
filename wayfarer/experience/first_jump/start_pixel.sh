#!/usr/bin/env bash
# One-command Pixel entry: isolated sparse checkout, existing art, accepted FQ11.
set -euo pipefail
BRANCH="experience/first-jump-v04-continuous-playback"
ROOT="${FIRST_JUMP_DIR:-$HOME/.local/share/loom-first-jump-v04}"
PORT="${FIRST_JUMP_PORT:-8881}"
PYTHON_BIN="$(command -v python || command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python required (Termux: pkg install python git)"; exit 2; }
if [[ ! -d "$ROOT/.git" ]]; then
  command -v git >/dev/null || { echo "Git is required (Termux: pkg install git python)"; exit 2; }
  # Python interpreter selected above (python on Termux, python3 elsewhere).
  mkdir -p "$(dirname "$ROOT")"
  git clone -q --depth 1 --filter=blob:none --no-checkout --branch "$BRANCH" \
    https://github.com/loom-2226/loom-2226.git "$ROOT"
  cd "$ROOT"
  git sparse-checkout init --no-cone >/dev/null
  git sparse-checkout set --no-cone \
    '/wayfarer/experience/first_jump/*' \
    '/wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json' \
    '/wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101/FQ11_INPUT.json' \
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
if [[ -z "${OPENAI_API_KEY:-}" && -r "$HOME/.config/loom/openai.env" ]]; then
  source "$HOME/.config/loom/openai.env"
fi
if [[ -z "${OPENAI_API_KEY:-}" && -r "$HOME/.config/loom/first_jump.env" ]]; then
  source "$HOME/.config/loom/first_jump.env"
fi
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Mara live model: no API key found in this Termux process."
  echo "Paste an OpenAI API key for live dialogue, or press Enter for scripted ship comms."
  if [[ -t 2 && -r /dev/tty ]]; then
    printf 'API key (hidden): ' > /dev/tty
    KEY=""
    IFS= read -r -s KEY </dev/tty || true
    printf '\n' >/dev/tty
    if [[ -n "$KEY" ]]; then
      umask 077
      mkdir -p "$HOME/.config/loom"
      printf 'export OPENAI_API_KEY=%q\n' "$KEY" > "$HOME/.config/loom/first_jump.env"
      chmod 600 "$HOME/.config/loom/first_jump.env"
      export OPENAI_API_KEY="$KEY"
    fi
    unset KEY
  fi
fi
echo "Mara channel: $(if [[ -n "${OPENAI_API_KEY:-}" ]]; then echo 'LIVE MODEL CONFIGURED'; else echo 'SCRIPTED / MISSING KEY'; fi)"
echo "FIRST JUMP / $(git rev-parse --short HEAD)"
echo "FQ11 playback; local URL http://127.0.0.1:$PORT"
echo "Session log under $HOME/.local/state/loom/first_jump/"
"$PYTHON_BIN" wayfarer/experience/first_jump/server.py --port "$PORT" &
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
