"""L1 viewing cone through the armour bore (used by command/l1_study.py). -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX (found while rendering layout D, v0.5.5). command/l1_study.py tests each ray
where it crosses the inner surface of the dome, so it treats the window as a hole in a thin sheet.
In front of that surface sits 0.20 m of armour. This re-runs the pilots' 60 and 90 deg cones with
one more test: the ray must also clear the armour opening at the outer surface, whose radius is the
window radius plus 0.20 m x tan(splay). Splay 0 is a straight bore.
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "command"))
import l1_options as O
import l1_study as S

I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
ARMOUR_T = 0.20                     # armour thickness at the nose (armour dome xa 0.0, pressure vessel xa 0.2)
ARM_R, ARM_XB = 4.5, 2.35           # armour outer ellipsoid: xa 0.0, xb 2.35, R 4.5 (out/wayfarer_v05_geometry.json part "armor")


def outer_x(r):
    return ARM_XB - ARM_XB * math.sqrt(max(0.0, 1 - (r / ARM_R) ** 2))


def outer_hit(p, d):
    p = list(p)
    for _ in range(4000):
        p = [p[k] + d[k] * 0.002 for k in range(3)]
        if p[0] < outer_x(math.hypot(p[1], p[2])):
            return p
    return None


def cone(sc, st, full, splay_deg, n=1500):
    """share of a cone of full angle `full` about the bow axis that is clear: (study test, study + armour bore)."""
    e, half = st["eye"], math.radians(full / 2)
    ok = okb = 0
    for i in range(n):
        c = 1 - (1 - math.cos(half)) * (i + 0.5) / n
        s = math.sqrt(1 - c * c)
        ph = i * math.pi * (3 - math.sqrt(5))
        d = [-c, s * math.cos(ph), s * math.sin(ph)]
        hit, kind = O.dome_hit(sc, e, d)
        if not (hit and O.through_window(sc, hit, kind) and not O.blocked(sc, e, hit, st["id"])):
            continue
        ok += 1
        po = outer_hit(hit, d)
        for _, wy, wz, dd in sc.windows:
            if math.hypot(hit[1] - wy, hit[2] - wz) <= dd / 2:
                if po and math.hypot(po[1] - wy, po[2] - wz) <= dd / 2 + ARMOUR_T * math.tan(math.radians(splay_deg)):
                    okb += 1
                break
    return round(ok / n, 3), round(okb / n, 3)
