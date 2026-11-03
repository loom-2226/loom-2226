#!/bin/sh
# Wayfarer v0.5 full chain -- ALL bodies. ALL sponsors. 2026-2226.
# build -> checks -> I4 command scene sync (scene for the renders) -> renders -> deck plans -> GLB -> viewer -> checks again (G12 needs the images) -> viewer with final verdicts
# command/l1_study.py is the pre-I4 L1 study (reads the removed flight_deck key); the I4 scene exporter is render/sync_i4_scene.py.
set -e
cd "$(dirname "$0")"
python3 build_v05.py
python3 command/l1_i4_checks.py > /dev/null
(cd ../render && python3 sync_i4_scene.py > /dev/null)
python3 habitat/hab_overlay_checks.py > /dev/null
python3 certify.py > /dev/null
(cd ../render && node render.js && python3 deckplans.py && node render.js decks && node export_glb.mjs && python3 make_viewer.py)
python3 certify.py
(cd ../render && python3 make_viewer.py)
