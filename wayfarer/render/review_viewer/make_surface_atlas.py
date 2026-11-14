"""Build tex/surface_atlas.png for the review viewer from the approved 1:25 surface library. ALL bodies. ALL sponsors. 2026-2226.
Same generator as the print tiles (wayfarer/print/surfaces_1to25/surfaces.py), so viewer and print cannot drift apart.
Atlas 4 x 3 tiles of 256 px, row 0 at the bottom: W-A W-B W-C W-D / F-1 F-2 F-3 F-4 / C-1 C-2 C-3. 1 tile = 1 m real.
Height: 0..1 over base-1 .. base+2 mm print (75 mm real)."""
import importlib.util, numpy as np, json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('s', os.path.join(HERE, '..', '..', 'print', 'surfaces_1to25', 'surfaces.py')); s = importlib.util.module_from_spec(sp); sp.loader.exec_module(s)
ORDER = ['W-A', 'W-B', 'W-C', 'W-D', 'F-1', 'F-2', 'F-3', 'F-4', 'C-1', 'C-2', 'C-3']; T = 256
atlas = np.zeros((3 * T, 4 * T), np.float32)
for i, sid in enumerate(ORDER):
    t = s.Tile(); s.SURF[sid]['fn'](t, sid)
    h = np.clip((t.H - (s.BASE - 1.0)) / 3.0, 0, 1)
    im = np.array(Image.fromarray((h * 65535).astype(np.uint16)).resize((T, T), Image.BILINEAR), np.float32) / 65535
    c, r = i % 4, i // 4
    atlas[(2 - r) * T:(3 - r) * T, c * T:(c + 1) * T] = im[::-1]
os.makedirs(os.path.join(HERE, 'tex'), exist_ok=True)
Image.fromarray((atlas * 255).round().astype(np.uint8)).save(os.path.join(HERE, 'tex', 'surface_atlas.png'))
json.dump({'order': ORDER, 'tile_px': T, 'height_range_print_mm': [-1.0, 2.0], 'scale': '1 tile = 1 m real (40 mm at 1:25)'}, open(os.path.join(HERE, 'tex', 'surface_atlas.json'), 'w'))
