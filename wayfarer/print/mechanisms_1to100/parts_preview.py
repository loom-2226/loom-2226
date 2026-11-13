"""Top-down preview of every plug-in part, drawn from the same solids as the STLs. ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, os, importlib.util
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('fp', os.path.join(HERE, 'fin_parts.py')); fp = importlib.util.module_from_spec(sp); sp.loader.exec_module(fp)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); fr = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
PX = 4.0   # px per mm
tiles = []
for name, p in fp.PARTS.items():
    F, occ, A = p['fn']().mesh()
    zc = (A[2][:-1] + A[2][1:]) / 2
    top = np.where(occ.any(2), np.array(A[2][1:])[np.argmax(np.where(occ, np.arange(occ.shape[2])[None, None, :], -1), axis=2)], np.nan)
    xs = np.arange(A[0][0], A[0][-1], 1 / PX); ys = np.arange(A[1][0], A[1][-1], 1 / PX)
    ix = np.clip(np.searchsorted(A[0], xs, 'right') - 1, 0, occ.shape[0] - 1); iy = np.clip(np.searchsorted(A[1], ys, 'right') - 1, 0, occ.shape[1] - 1)
    H = top[np.ix_(ix, iy)].T[::-1]
    gy, gx = np.gradient(np.nan_to_num(H, nan=0.0))
    sh = np.where(np.isnan(H), 0.96, np.clip(0.62 + 0.25 * (np.nan_to_num(H) / np.nanmax(H)) - 0.9 * gx + 0.9 * gy, 0.15, 0.95))
    rgb = np.dstack([sh * 255, sh * 250, sh * 244]).astype(np.uint8); rgb[np.isnan(H)] = (246, 245, 242)
    im = Image.fromarray(rgb)
    if im.height > 600: im = im.resize((int(im.width * 600 / im.height), 600), Image.LANCZOS)
    t = Image.new('RGB', (max(im.width, 360) + 20, im.height + 70), (246, 245, 242)); t.paste(im, (10, 60))
    d = ImageDraw.Draw(t); d.text((10, 6), f'{name}  x{p["qty"]}', font=fb, fill=(29, 34, 40)); d.text((10, 32), p['what'][:60], font=fr, fill=(107, 115, 124))
    tiles.append(t)
W = 1500; rows = []; row = []; w = 0
for t in tiles:
    if w + t.width > W and row: rows.append(row); row = []; w = 0
    row.append(t); w += t.width + 10
rows.append(row)
H = sum(max(t.height for t in r) for r in rows) + 80
S = Image.new('RGB', (W, H), (246, 245, 242)); d = ImageDraw.Draw(S)
d.text((10, 10), 'Wayfarer 1:100 plug-in fins and strakes: 21 printed parts (PLACEHOLDER profile)', font=fb, fill=(29, 34, 40))
d.text((10, 40), 'Top view, root bar at the bottom of each part. Pegs: 1.75 mm filament offcuts, 5 mm long.', font=fr, fill=(107, 115, 124))
y = 70
for r in rows:
    x = 0
    for t in r: S.paste(t, (x, y)); x += t.width + 10
    y += max(t.height for t in r)
S.save(os.path.join(HERE, 'parts_preview.png')); print(S.size)
