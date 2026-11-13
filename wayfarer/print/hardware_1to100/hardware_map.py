"""Wayfarer 1:100 exterior hardware map (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Positions from the canon stowed/closed exterior GLB nodes (dry:*), drawn on the 1:100 hull development. PROPOSAL (F4)."""
import json, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
hw = json.load(open(os.path.join(HERE, 'hardware_inventory.json')))
im = Image.open(os.path.join(HERE, '..', 'hull_1to100', 'hull_development_1to100.png')).convert('RGB')
bg = Image.blend(im, Image.new('RGB', im.size, (246, 245, 242)), 0.55); d = ImageDraw.Draw(bg)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15); fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
H = 1131; col = {'A': (47, 111, 143), 'B': (63, 143, 90), 'C': (217, 119, 58)}
P = lambda x, az: (10 + (x - 2.35) * 40, 50 + (1 - az / 360) * H)
labels = {'rcs': 'RCS cluster', 'ext_eva_rail': 'EVA rails (4)', 'ext_crawler_point': 'crawler points (24)', 'ext_vent': 'vent', 'ext_grapple_fixture': 'grapple plate',
          'ext_rf_array': 'RF array', 'ext_sensor_turret': 'sensor turret', 'ext_service_port': 'service port', 'ext_laser_terminal': 'laser terminal'}
done = set()
for o in hw:
    if not (2.35 <= o['x'] <= 34.3): continue
    x, y = P(o['x'], o['az']); c = col[o['cat']]
    if 'eva_rail' in o['name']: L = o['size_m'][0] * 40; d.line((x - L / 2, y, x + L / 2, y), fill=c, width=6)
    else: r = 10 if o['cat'] == 'A' else 7; d.ellipse((x - r, y - r, x + r, y + r), fill=c, outline=(29, 34, 40))
    key = next((k for k in labels if o['name'].startswith(k)), None)
    if key and key not in done: done.add(key); d.text((x + 12, y + 4), labels[key], font=fs, fill=(29, 34, 40))
x, y = P(15.5, 270); d.text((x - 60, y - 46), 'docking cluster: collar,\nservice arm, camera, target', font=fs, fill=(29, 34, 40))
lx, ly = bg.width - 470, 8
d.rectangle((lx - 8, ly - 4, bg.width - 6, ly + 100), fill=(255, 255, 255), outline=(180, 180, 180))
for i, (k, t) in enumerate((('A', 'A  Print as part of the hull (1 mm+)'), ('B', 'B  Engrave outline only (flat plates)'), ('C', 'C  Too thin: exaggerate to print minimum'))):
    d.ellipse((lx, ly + 6 + i * 24, lx + 14, ly + 20 + i * 24), fill=col[k]); d.text((lx + 22, ly + 4 + i * 24), t, font=f, fill=(29, 34, 40))
d.text((lx, ly + 78), 'Off this map: bow sensors + 4 forward RCS (bow piece).', font=fs, fill=(107, 115, 124))
bg.save(os.path.join(HERE, 'hardware_map_1to100.png'))
