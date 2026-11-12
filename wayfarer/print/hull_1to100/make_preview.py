"""Coupon preview drawn straight from the same raster the STL is meshed from (bow end up). ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, json, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'hull_etch.py')}; exec(open(ns['__file__']).read().replace("if __name__ == '__main__': main()", ""), ns)
spec = json.load(open(os.path.join(HERE, 'etch_spec_1to100.json'))); R, K, n = 4.5, 10, 2880
W, xs, th = ns['raster'](spec, 8.0, 14.2, 0.05, n, set())
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22); fr = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
panels = []
for azc, title in ((0, 'EVA hatch side (0 deg)'), (210, 'Medical port side (210 deg)')):
    U = np.arange(-R * K * 0.98, R * K * 0.98, 0.05); s = U / (R * K)
    ci = (((azc + np.degrees(np.arcsin(s))) % 360) / 360 * n).astype(int) % n
    img = W[:, ci].astype(float)                     # row 0 = x 8.0 = bow end = top of the print
    light = 0.35 + 0.65 * np.clip(np.cos(np.arcsin(s)) * 0.8 - s * 0.5, 0, 1)
    base = np.where(img == 2, 0.82, np.where(img == 1, 0.55, 0.05)) * light[None, :]
    base = np.clip(base + 0.10 * np.clip(np.diff(img, axis=0, prepend=img[:1]), -1, 1), 0, 1)
    im = Image.fromarray((base * 255).astype(np.uint8)).resize((len(U) // 4, W.shape[0] // 4), Image.LANCZOS)
    c = Image.new('RGB', (im.width + 20, im.height + 50), (245, 245, 242)); c.paste(im.convert('RGB'), (10, 40))
    ImageDraw.Draw(c).text((10, 8), title, font=fb, fill=(0, 0, 0)); panels.append(c)
S = Image.new('RGB', (sum(p.width for p in panels) + 20, panels[0].height + 40), (245, 245, 242)); x = 0
for p in panels: S.paste(p, (x, 0)); x += p.width + 20
ImageDraw.Draw(S).text((10, panels[0].height + 8), '1:100 coupon x 8.0-14.2: 62 mm tall, 90 mm dia. Grooves 0.5 x 0.24 mm. Bow end up. Black = openings.', fill=(0, 0, 0), font=fr)
S.save(os.path.join(HERE, 'coupon_preview_1to100.png'))
