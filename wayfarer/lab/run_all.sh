#!/bin/sh
# Wayfarer v0.5 full chain -- ALL bodies. ALL sponsors. 2026-2226.
# build -> checks -> I4 command scene sync (scene for the renders) -> renders -> deck plans -> GLB -> viewer -> checks again (G12 needs the images) -> viewer with final verdicts
# command/l1_study.py is the pre-I4 L1 study (reads the removed flight_deck key); the I4 scene exporter is render/sync_i4_scene.py.
# Render requires Node >=20 and locked Playwright; on first run npm ci + Chromium/system deps install may need OS privileges.
set -e
cd "$(dirname "$0")"
# Use the pinned Wayfarer venv when system Python lacks these packages.
WAYFARER_PYTHON="$(python3 ../ensure_env.py)"
export PATH="$(dirname "$WAYFARER_PYTHON"):$PATH"
python3 build_v05.py
(cd ../render && python3 sync_i4_scene.py > /dev/null)
python3 habitat/hab_overlay_checks.py > /dev/null
python3 certify.py > /dev/null
# npm dependencies and Chromium are installed only when missing or mismatched.
(
  cd ../render
  if [ ! -f node_modules/playwright/package.json ] || ! node -e "const p=require('./package.json');const i=require('./node_modules/playwright/package.json');process.exit(i.version===p.dependencies.playwright?0:1)"; then
    npm ci
  fi
  if ! node -e "const fs=require('fs');const {chromium}=require('playwright');process.exit(fs.existsSync(chromium.executablePath())?0:1)"; then
    npx playwright install --with-deps chromium
  fi
)
(cd ../render && node render.js && python3 deckplans.py && node render.js decks && node export_glb.mjs && python3 make_viewer.py)
python3 certify.py
(cd ../render && python3 make_viewer.py)
