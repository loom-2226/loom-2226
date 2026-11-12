#!/usr/bin/env python3
"""Three reproducible views: Claude proposal Option 1 vs live approved 2/2/2.
Source camera geometry and image resolution are identical for each pair.
Read the before images from the already-committed PR541 proposal renders.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib

root=Path(__file__).resolve().parents[2]
before=root/"lab/exterior_remaining_options/renders"
after=root/"render/out"
output=root/"docs"
output.mkdir(exist_ok=True,parents=True)
pairs=[
 ("THRUST","T1.png","exterior_222_thrust.png"),
 ("DOORS","D1.png","exterior_222_doors.png"),
 ("RADIATORS","R1.png","exterior_222_radiators.png")
]
try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",27)
except OSError: font=ImageFont.load_default()
manifest=[]
for name,bfile,afile in pairs:
    b=Image.open(before/bfile).convert("RGB")
    a=Image.open(after/afile).convert("RGB")
    assert b.size==a.size==(1600,900),(name,b.size,a.size)
    combined=Image.new("RGB",(3200,955),(15,22,29))
    combined.paste(b,(0,55));combined.paste(a,(1600,55))
    drawer=ImageDraw.Draw(combined)
    drawer.text((20,12),"BEFORE: Claude Option 1 source-render sketch",font=font,fill=(245,246,248))
    drawer.text((1620,12),"AFTER: approved 2/2/2 in live loomgl.js viewer",font=font,fill=(245,246,248))
    path=output/f"WAYFARER_EXTERIOR_222_{name}_BEFORE_AFTER_2026_11_13.png"
    combined.save(path,optimize=True)
    assert path.stat().st_size>50000
    manifest.append(dict(subject=name,source_before=str((before/bfile).relative_to(root)),
      approved_after=str((after/afile).relative_to(root)),
      comparison=str(path.relative_to(root)),
      image_size=list(combined.size),
      before_sha256=hashlib.sha256((before/bfile).read_bytes()).hexdigest(),
      after_sha256=hashlib.sha256((after/afile).read_bytes()).hexdigest()))
print(json.dumps(dict(status="THREE_APPROVED_222_BEFORE_AFTER_RENDER_PAIRS",
    source="same camera and scene, Claude Option 1 vs live approved shader",
    pictures=manifest),indent=2))
