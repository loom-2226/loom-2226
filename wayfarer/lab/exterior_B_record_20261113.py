#!/usr/bin/env python3
"""Record the approved exterior B variant only after geometry and picture PASS."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"render/out"
r=json.loads((OUT/"wayfarer_exterior_B_medical_88ce19fc_visual_report.json").read_text())
assert r["status"]=="VISUAL_EXTERIOR_B_MEDICAL_3X2_D9_CONTAINMENT_PASS"
assert r["D9_category_d_total"]==0 and r["containment"]=="PASS"
assert len(r["six_states"])==6 and r["source_dry_t"]==868.1922552640087
assert r["ECON_dv_km_s"]==707.845 and r["mass_rebooking_t"]==0
path=ROOT/"config/kt_decisions.json"
dec=json.loads(path.read_text())
choice=dec["exterior_surface_2026_11_13"]
assert choice["canon_change"] is False and "APPROVED" in choice["status"]
# kT's APPROVED decision is already recorded by PR #536. Keep it immutable:
# writing kt_decisions.json here would invoke the released-canon F3 workflow.
# The separate noncanon visual report is the authoritative build evidence.
assert choice["status"]=="APPROVED; build by Sol"
assert choice["mass_rebooking_t"]==0 and choice["G1_G12"]=="NOT RUN"
doc=ROOT/"docs/EXTERIOR_SURFACE_OPTIONS_2026_11_13.md"
s=doc.read_text()
s+="""

## Approved B visual integration (non-canon WWS-1)

The six-state noncanon exterior visual GLBs have real cut-out BReps for three
L4 medical ports through pressure and armour solids. Each source region had
positive physical material; the rebuilt hull and armour have zero remaining
intersection with the approved bore cutter at each port. Centres x=9.30
(h=1.50) from x=9.10, diameter 1.55, azimuth 180/210/240 unchanged.

The original source geometry, original released exterior six-state GLBs, and
the canon_glb.json release pointer have NOT been edited. These are
NON-CANON WWS-1 design-position variants, not a canon re-release.
No pressure-seal or shielding performance qualification is claimed.

Option B mid-bay rings and 20-degree tile joints are shaded demarcations in
loomgl.js, with EVA and medical frames. No physical Strata seams or
armour removal for tile markings. C's selected EVA lane/tether/keepout
details remain print-only and absent from the renderer.

EVA source frame: x=12.25 m, diameter 1.1 m. Interior L5 clear hatch:
x=12.30 m, diameter 1.0 m. Difference: interior is 50 mm aft of
the source outer frame; neither part has been moved.

Six-state D9 category-d 0 and containment PASS, no new mass:
dry 868.192255 t, ECON delta-v 707.845 km/s. G1-G12 not rerun.

![Medical port before/after](WAYFARER_EXTERIOR_B_MEDICAL_BEFORE_AFTER_2026_11_13.png)

![EVA hatch before/after](WAYFARER_EXTERIOR_B_EVA_BEFORE_AFTER_2026_11_13.png)

![Whole ship before/after](WAYFARER_EXTERIOR_B_WHOLE_BEFORE_AFTER_2026_11_13.png)
"""
doc.write_text(s)
for short in ("EVA","MEDICAL","WHOLE"):
    p=ROOT/"docs"/f"WAYFARER_EXTERIOR_B_{short}_BEFORE_AFTER_2026_11_13.png"
    assert p.is_file() and p.stat().st_size>10000
print("APPROVED_B_RECORD_COMPLETE",len(r["six_states"]))
