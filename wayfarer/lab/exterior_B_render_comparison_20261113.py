#!/usr/bin/env python3
"""Build paired BEFORE/AFTER images from the existing source-approved snapshots
and fresh approved renderer outputs. This does not alter visual geometry.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1]
before=R/"lab/exterior_surface_options/renders"
after=R/"render/out"
dest=R/"docs"
dest.mkdir(exist_ok=True,parents=True)
font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try: face=ImageFont.truetype(font,32)
except OSError:face=ImageFont.load_default()
manifest=[]
for short,source,target in [
    ("eva","eva_0.png","exterior_B_eva.png"),
    ("medical","med_0.png","exterior_B_medical.png"),
    ("whole","full_0.png","exterior_B_whole.png")
]:
    b=Image.open(before/source).convert("RGB")
    a=Image.open(after/target).convert("RGB")
    assert b.size==a.size==(1600,900),(b.size,a.size)
    out=Image.new("RGB",(3200,958),(14,22,30))
    out.paste(b,(0,58));out.paste(a,(1600,58))
    d=ImageDraw.Draw(out)
    d.text((20,12),"BEFORE: kT 9 Nov source grid",fill=(235,244,253),font=face)
    d.text((1620,12),"AFTER: approved B + noncanon WWS-1 port move",fill=(235,244,253),font=face)
    dst=dest/f"WAYFARER_EXTERIOR_B_{short.upper()}_BEFORE_AFTER_2026_11_13.png"
    out.save(dst,optimize=True)
    manifest.append(str(dst.relative_to(R)))
print(json.dumps(dict(status="EXTERIOR_B_COMPARISON_IMAGES_BUILT",pictures=manifest),indent=2))
