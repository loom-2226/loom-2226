"""L1 nose windows: does the armour bore cut the pilots' view? -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX (found while rendering layout D, v0.5.5). command/l1_study.py tests each ray
where it crosses the inner surface of the dome, so it treats the window as a hole in a thin sheet.
In front of that surface sits 0.20 m of armour. This re-runs the pilots' 60 and 90 deg cones with
one more test: the ray must also clear the armour opening at the outer surface, whose radius is the
window radius plus 0.20 m x tan(splay). Splay 0 is a straight bore.
Writes command/l1_bore_check_results.json. Usage: python command/l1_bore_check.py (standard library only)"""
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


def web_m(splay_deg):
    """narrowest armour web left between neighbouring nose openings at the outer surface."""
    W = [(w["yz_m"], w["d_m"]) for w in S.CL["forward_windows"]]
    g = ARMOUR_T * math.tan(math.radians(splay_deg))
    return round(min(math.dist(a, b) - da / 2 - db / 2 - 2 * g for i, (a, da) in enumerate(W) for (b, db) in W[i + 1:]), 3)


if __name__ == "__main__":
    sc = S.built_option()["scene"]
    rows = []
    for splay in (0, 10, 12, 15, 20, 36):
        r = {"splay_deg": splay, "armour_web_m": web_m(splay)}
        for st in sc.couches[:2]:
            s60, b60 = cone(sc, st, 60, splay)
            s90, b90 = cone(sc, st, 90, splay)
            r[st["id"]] = {"60deg_study": s60, "60deg_with_bore": b60, "90deg_study": s90, "90deg_with_bore": b90}
        rows.append(r)
        print(r)
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING check, v0.5.5 layout D",
           "geometry_sha256": S.SHA, "armour_t_m": ARMOUR_T, "criterion": ">= 90% clear across 60 deg (L1_OPTIONS_v0.5.5.md)", "rows": rows}
    (ROOT / "command/l1_bore_check_results.json").write_text(json.dumps(out, indent=1))
