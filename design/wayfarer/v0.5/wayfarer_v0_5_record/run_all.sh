#!/bin/sh
# Wayfarer v0.5 full chain -- ALL bodies. ALL sponsors. 2026-2226.
# build -> checks -> renders -> deck plans -> viewer -> checks again (G12 needs the images) -> viewer with final verdicts
set -e
cd "$(dirname "$0")"
python3 build_v05.py
python3 certify.py > /dev/null
(cd render && node render.js && python3 deckplans.py && node render.js decks && python3 make_viewer.py)
python3 certify.py
(cd render && python3 make_viewer.py)
