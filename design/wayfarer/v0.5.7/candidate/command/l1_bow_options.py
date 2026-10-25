"""L1 bow options: how much sky each person sees -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING CONCEPT STUDY (v0.5.6 baseline; does not change the geometry).
Ray tests from the six couch eyes and four standing eyes (1 g cruise, eye 1.6 m above the L1 floor)
for three bows, with the real obstacles (sensor ring, flight deck and columns, couches with occupants, displays):
  A  v0.5.6: 8 nose windows + 4 shoulder windows, armour openings splayed 12 deg;
  B  panoramic: glazed to the shoulder (r <= 4.15 m) on a 12-meridian frame; the sensor ring has to leave L1;
  C  crown dome: glazed inside the sensor ring (r <= 2.8 m) on an Osteon frame (8 roots forking into 16 blades round a clear 2.3 m central pane); shoulder windows kept.
Also: dust (Grun 1985 flux) and pane sizing for the mass estimate.
Writes command/l1_bow_options_results.json. Usage: python command/l1_bow_options.py (standard library only)"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "command"))
import l1_options as O
import l1_study as S
import l1_bore_check as BC

FLOOR = O.FLOOR
RIB_W = 0.08


def fib(n):
    for i in range(n):
        c = 1 - 2 * (i + 0.5) / n
        s = math.sqrt(1 - c * c)
        ph = i * math.pi * (3 - math.sqrt(5))
        yield [-c, s * math.cos(ph), s * math.sin(ph)]      # c > 0: toward the bow (-x)


def on_rib(y, z, r_glass, n_mer, hoops, crown=0.6):
    r = math.hypot(y, z)
    if r > r_glass - RIB_W / 2:                              # rim frame
        return True
    if any(abs(r - h) < RIB_W / 2 for h in hoops):
        return True
    if r < crown:
        return False
    a = math.atan2(z, y)
    step = 2 * math.pi / n_mer
    k = round(a / step)
    return abs(a - k * step) * r < RIB_W / 2


def osteon_rib(y, z, R=2.8, c0=1.15, rf=2.0, n=8, w=RIB_W):
    """Osteon frame: 8 roots from the brow ring (r 2.8) to r 2.0, each forking into 2 blades that land on a ring at r 1.15
    round a clear central pane. Blade width 8 cm (conservative: real blades are 3-7 cm and set edge-on to the pilots)."""
    r = math.hypot(y, z)
    if r > R - w / 2 or abs(r - c0) < w / 2:
        return True
    if r < c0:
        return False
    a = math.atan2(z, y)
    half = math.pi / n / 2
    for j in range(n):
        a0 = 2 * math.pi * j / n
        if r >= rf:
            cands = [a0]
        else:
            t = (rf - r) / (rf - c0)
            e = t * t * (3 - 2 * t)
            cands = [a0 - half * e, a0 + half * e]
        for ac in cands:
            if abs((a - ac + math.pi) % (2 * math.pi) - math.pi) * r < w / 2:
                return True
    return False


def make(option):
    o = S.built_option()
    sc = o["scene"]
    if option == "B":
        sc.solids = [(n, s) for n, s in sc.solids if n != "sensors"]
    return sc


def clear(sc, option, e, d, me):
    hit, kind = O.dome_hit(sc, e, d)
    if not hit or O.blocked(sc, e, hit, me):
        return False
    y, z = hit[1], hit[2]
    if option == "A":
        if not O.through_window(sc, hit, kind):
            return False
        for _, wy, wz, dd in sc.windows:
            if math.hypot(y - wy, z - wz) <= dd / 2:
                po = BC.outer_hit(hit, d)
                return bool(po) and math.hypot(po[1] - wy, po[2] - wz) <= dd / 2 + BC.ARMOUR_T * math.tan(math.radians(12))
        return True                                          # shoulder window
    if kind != "dome":
        return False
    if option == "B":
        return math.hypot(y, z) <= 4.15 and not on_rib(y, z, 4.15, 12, (1.4, 2.8))
    if option == "C":
        if math.hypot(y, z) <= 2.8:
            return not osteon_rib(y, z)
        return O.through_window(sc, hit, kind) and all(math.hypot(y - wy, z - wz) > dd / 2 for _, wy, wz, dd in sc.windows)


def score(sc, option, e, me, n=1600):
    fwd = up90 = tot90 = 0
    for d in fib(n):
        ok = clear(sc, option, e, d, me) if d[0] < 0 else False
        fwd += ok
        if -d[0] >= math.cos(math.radians(45)):
            tot90 += 1
            up90 += ok
    return {"sky_share_pct": round(100 * fwd / n, 1), "forward_hemisphere_pct": round(200 * fwd / n, 1), "cone90_pct": round(100 * up90 / max(tot90, 1), 1)}


def standing_eyes():
    x = FLOOR - 1.6
    return {f"STAND_{a}": (x, 2.2 * math.cos(math.radians(a)), 2.2 * math.sin(math.radians(a))) for a in (0, 90, 180, 270)}


def grun_flux(m_g):
    """Grun et al. (1985) interplanetary flux at 1 AU, impacts per m2 per year on a randomly oriented plate, mass >= m (grams), 20 km/s mean."""
    c = (3.156e7, 2.2e3, 15.0, 1.3e-9, 1e11, 1e27, 1.3e-16, 1e6)
    return c[0] * ((c[1] * m_g ** 0.306 + c[2]) ** -4.38 + c[3] * (m_g + c[4] * m_g ** 2 + c[5] * m_g ** 4) ** -0.36
                   + c[6] * (m_g + c[7] * m_g ** 2) ** -0.85)


def dust(v_kms):
    """ram-facing pane: flux scaled by speed (20 km/s reference) and craters scaled with energy^(1/3)."""
    rows = []
    for m in (1e-12, 1e-9, 1e-6):
        f20 = grun_flux(m)
        d_um = (6 * m / (math.pi * 2.5)) ** (1 / 3) * 1e4
        rows.append({"mass_g": m, "diameter_um": round(d_um, 1), "flux_per_m2_yr_at_20kms": f20})
    out = {"rows": rows}
    # obscured area per m2 per year: sum over decades, crater diameter ~ 15 x particle at 20 km/s, x (v/20)^(2/3)
    tot = 0.0
    ms = [10 ** (k / 4) for k in range(-60, -8)]
    for i in range(len(ms) - 1):
        n = grun_flux(ms[i]) - grun_flux(ms[i + 1])
        dc = 15 * (6 * ms[i] / (math.pi * 2.5)) ** (1 / 3) * 1e-2 * (v_kms / 20) ** (2 / 3)
        tot += n * (v_kms / 20) * math.pi * dc ** 2 / 4
    out["v_kms"] = v_kms
    out["cratered_fraction_per_year"] = tot
    return out


def panes(R_c=8.6, p=101.3e3):
    cases = {"fused silica (2026, design 10 MPa)": (10e6, 2.2), "ALON (2026, 700 MPa flexure, design 70 MPa)": (70e6, 3.69),
             "flaw-controlled ceramic (2226 extrapolation, design 200 MPa)": (200e6, 3.69)}
    out = {}
    for k, (s, rho) in cases.items():
        t = max(p * R_c / (2 * s), 0.006)
        tot = 2 * t + 0.008 + 0.003
        out[k] = {"pressure_pane_mm": round(t * 1e3, 1), "stack_mm": round(tot * 1e3, 1), "kg_per_m2": round(tot * rho * 1e3, 0)}
    return out


if __name__ == "__main__":
    res = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING concept study (v0.5.6 baseline)", "options": {}}
    for opt in ("A", "B", "C"):
        sc = make(opt)
        rows = {}
        for c in sc.couches:
            rows[c["id"]] = score(sc, opt, c["eye"], c["id"])
        for k, e in standing_eyes().items():
            rows[k] = score(sc, opt, e, None)
        res["options"][opt] = rows
        print(opt, json.dumps(rows))
    res["dust"] = {v: dust(v) for v in (20, 100, 300)}
    res["panes"] = panes()
    print(json.dumps(res["dust"], default=float)[:600])
    print(json.dumps(res["panes"]))
    (ROOT / "command/l1_bow_options_results.json").write_text(json.dumps(res, indent=1, default=float))
