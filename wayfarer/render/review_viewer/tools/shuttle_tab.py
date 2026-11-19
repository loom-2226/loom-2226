"""Build the review viewer's "Shuttle B4-S" tab (shuttle.html) from the lab B4-S viewer, adding Ship/Shuttle tabs.
Visual reference only. ALL bodies. ALL sponsors. 2026-2226. Run lab/shuttle/v2_lifting_body/b4s_viewer.py first."""
import sys
from pathlib import Path
R = Path(__file__).resolve().parents[3]   # wayfarer/
SRC = R / 'lab/shuttle/v2_lifting_body/viewer/b4s.html'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else R / 'render/review_viewer/shuttle.html'
s = SRC.read_text()
nav = ('<nav style="position:fixed;right:12px;top:calc(10px + env(safe-area-inset-top));display:flex;gap:6px;z-index:5">'
       '<a href="index.html" style="font:600 13px/1 system-ui;padding:8px 14px;border-radius:16px;border:1px solid #33404f;background:#1c2430;color:#e6e6e6;text-decoration:none">Ship</a>'
       '<a style="font:600 13px/1 system-ui;padding:8px 14px;border-radius:16px;background:#2a78d6;color:#fff">Shuttle B4-S</a></nav>')
assert '<canvas id="c"></canvas>' in s
s = s.replace('<canvas id="c"></canvas>', '<canvas id="c"></canvas>\n' + nav, 1)
s = s.replace('#hud{position:fixed;left:12px;top:calc(10px + env(safe-area-inset-top));right:12px;', '#hud{position:fixed;left:12px;top:calc(48px + env(safe-area-inset-top));right:12px;', 1)
OUT.write_text(s); print(OUT, len(s))
