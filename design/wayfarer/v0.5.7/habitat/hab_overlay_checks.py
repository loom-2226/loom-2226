"""Habitat overlay checks for Sol's v0.5.3 candidate -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Supplementary evidence, not a certification gate. Reads the integrated
geometry (out/wayfarer_v05_geometry.json) and inputs, and checks the items Sol asked Claude to
reconcile: berth-shield water against the actual parts, berth and door clearances in plan, the L4
stretcher opening, and a bunk radiation screen in state S5 (Sol's method: 600 directions, 2 cm steps).
Usage: python habitat/hab_overlay_checks.py [--quick]   (standard library only)"""
import json, math, random, sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build_v05 as B
from certify import ray_density

G = json.loads((ROOT / "out/wayfarer_v05_geometry.json").read_text())
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
HAB = I["habitat"]
OUT = {}


def ring_overlap(n=20000):
    bs = HAB["berth_shield"]
    ring = B.Sector(bs["x_m"][0], bs["x_m"][1], bs["r_m"][0], bs["r_m"][1], bs["theta_deg"][0], bs["theta_deg"][1])
    pts = ring.sample(random.Random(7), n)
    for cl in bs.get("floor_collars", []):      # v0.5.6 collar behind the edge of floor L3
        pts += B.Sector(cl["x_m"][0], cl["x_m"][1], cl["r_m"][0], cl["r_m"][1], cl["theta_deg"][0], cl["theta_deg"][1]).sample(random.Random(8), n // 4)
    hits = {}
    for p in G["parts"]:
        sh = B.shape_from_spec(p["shape"])
        (x0, x1), (y0, y1), (z0, z1) = sh.bbox()
        if x1 < bs["x_m"][0] or x0 > bs["x_m"][1]:
            continue
        k = sum(1 for x, y, z in pts if sh.contains(x, y, z))
        if k:
            hits[p["id"]] = k
    water = [w for w in G["fluids_by_state"]["S1"] if "berth_shield" in w["tags"]]
    return {"ring_volume_m3": round(ring.volume(), 4), "samples": len(pts), "overlap_samples": hits, "ring_water_t_S1": round(sum(w["mass_t"] for w in water), 4),
            "in_every_state": all(any("berth_shield" in w["tags"] for w in G["fluids_by_state"][s]) for s in G["fluids_by_state"]),
            "protected_water": G["protected_water"]}


def plan_checks():
    rows = []
    ring_r = HAB["berth_shield"]["r_m"][0]
    for r in G["rooms"]:
        for b in r.get("bunks", []):
            ri, ro = b["radial_m"]
            hw = b["width_m"] / 2
            corner = math.hypot(ro, hw)
            a0, a1 = r["theta_deg"]
            # sideways room-wall clearance at the bunk's inner and outer ends (distance from the bunk edge to the sector's radial wall)
            side = min(rad * math.sin(math.radians(min(b["angle_deg"] - a0, a1 - b["angle_deg"]))) - hw for rad in (ri, ro))
            d = r.get("door")
            gap = None
            if d:
                # door opening edges on the r 1.9 wall vs the nearest bunk corner (plan distance)
                rw = HAB["corridor_r_m"][1]
                half = d["clear_width_m"] / 2 / rw
                edges = [(rw * math.cos(math.radians(d["center_deg"]) + s_ * half), rw * math.sin(math.radians(d["center_deg"]) + s_ * half)) for s_ in (-1, 1)]
                t = math.radians(b["angle_deg"])
                u, v = (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))
                cs = [(ri * u[0] + s_ * hw * v[0], ri * u[1] + s_ * hw * v[1]) for s_ in (-1, 1)]
                gap = min(math.dist(e, c) for e in edges for c in cs)
            rows.append({"room": r["id"], "bunk_deg": b["angle_deg"], "tiers": b["tiers"], "outer_corner_r_m": round(corner, 4),
                         "clear_to_shield_m": round(ring_r - corner, 4), "clear_to_side_walls_m": round(side, 3),
                         "door_edge_to_bunk_corner_m": round(gap, 3) if gap is not None else None})
    med = next(r for r in G["rooms"] if r["id"] == "L4-medical")
    e = med["entrance"]
    arc = math.degrees(e["clear_width_m"] / e["at_r_m"])
    fits = (e["center_deg"] - arc / 2 >= med["theta_deg"][0]) and (e["center_deg"] + arc / 2 <= med["theta_deg"][1])
    occ = sum(r.get("occupancy", 0) for r in G["rooms"])
    tiers = HAB["decks"][2]["berths"]
    deck = HAB["decks"][2]
    return {"bunks": rows, "medical_entrance": {"arc_deg": round(arc, 1), "spans_deg": [round(e["center_deg"] - arc / 2, 1), round(e["center_deg"] + arc / 2, 1)],
            "medical_wall_deg": med["theta_deg"], "fits_in_medical_wall": fits},
            "berths_total": occ, "two_tier_stack_m": tiers["two_tiers_m"], "deck_clear_m": round(deck["x_m"][1] - deck["x_m"][0], 3)}


DIRS = []


class OpenBores:
    """rev 7 sensitivity only: the armour with every metric node face treated as an open bore through it
    (the worst case; the faces' materials, covers and seals are OPEN). Not the design case."""

    def __init__(self, sh, faces, depth):
        self.sh, self.depth = sh, depth
        self.rings = {}
        for f in faces:
            self.rings.setdefault(round(f["pos"][0], 3), []).append(f)

    def bbox(self):
        return self.sh.bbox()

    def contains(self, x, y, z):
        if not self.sh.contains(x, y, z):
            return False
        for rx, fs in self.rings.items():
            if abs(x - rx) > 0.6:
                continue
            for f in fs:
                d = (x - f["pos"][0], y - f["pos"][1], z - f["pos"][2])
                n = f["normal"]
                a = d[0] * n[0] + d[1] * n[1] + d[2] * n[2]
                if -self.depth - 0.02 <= a <= 0.02:
                    q = (d[0] - a * n[0], d[1] - a * n[1], d[2] - a * n[2])
                    if q[0] ** 2 + q[1] ** 2 + q[2] ** 2 < (f["d_m"] / 2) ** 2:
                        return False
        return True


def _init(open_bores=False):
    global ITEMS, DIRS
    ITEMS = []
    faces = [f for f in G["features"] if f["kind"] == "node_face" and f["pos"][0] <= I["hull"]["habitat_shell_x_m"][1]]
    for p in G["parts"] + G["fluids_by_state"]["S5"]:
        if "shuttle" in p.get("tags", []) or p["volume_m3"] <= 0:
            continue
        sh = B.shape_from_spec(p["shape"])
        if open_bores and p["id"] == "armor":
            sh = OpenBores(sh, faces, I["hull"]["outer_r_m"] - I["hull"]["pressure_r_m"])
        ITEMS.append((sh, p["mass_t"] / p["volume_m3"], sh.bbox()))
    N = 600
    DIRS = []
    for i in range(N):
        z = 1 - 2 * (i + .5) / N
        rr = math.sqrt(1 - z * z)
        ph = i * math.pi * (3 - math.sqrt(5))
        DIRS.append((z, rr * math.cos(ph), rr * math.sin(ph)))


def _screen(task):
    label, o, step = task
    v = [ray_density(o, d, ITEMS, step, 65) for d in DIRS]
    m = min(v)
    return label, m, DIRS[v.index(m)]


def radiation_screen(step=0.02, open_bores=False):
    pts = []
    for r in G["rooms"]:
        for b in r.get("bunks", []):
            th = math.radians(b["angle_deg"])
            for x in (6.45, 7.55):
                for rad in (2.25, 3.05, 3.85):
                    pts.append((f"{r['id']}@{b['angle_deg']}:x{x}:r{rad}", (x, rad * math.cos(th), rad * math.sin(th)), step))
    with Pool(2, initializer=_init, initargs=(open_bores,)) as pool:
        res = pool.map(_screen, pts)
    res.sort(key=lambda t: t[1])
    return {"state": "S5", "points": len(res), "directions": 600, "step_m": step, "minimum_g_cm2": round(res[0][1], 2),
            "below_40": sum(1 for _, m, _ in res if m < 40), "worst": [(lab, round(m, 2), [round(c, 3) for c in d]) for lab, m, d in res[:6]],
            "by_point": {lab: round(m, 2) for lab, m, _ in res}}


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    OUT["geometry_sha256"] = __import__("hashlib").sha256((ROOT / "out/wayfarer_v05_geometry.json").read_bytes()).hexdigest()
    OUT["ring"] = ring_overlap()
    print("ring", json.dumps(OUT["ring"]), flush=True)
    OUT["plan"] = plan_checks()
    print("plan", json.dumps(OUT["plan"]), flush=True)
    OUT["radiation"] = radiation_screen(0.05 if quick else 0.02)
    print("radiation", json.dumps({k: v for k, v in OUT["radiation"].items() if k != "by_point"}), flush=True)
    if any(f["kind"] == "node_face" for f in G["features"]):   # rev 7: node faces as open bores (worst case, sensitivity only)
        OUT["radiation_node_faces_open"] = radiation_screen(0.05 if quick else 0.02, open_bores=True)
        print("radiation_node_faces_open", json.dumps({k: v for k, v in OUT["radiation_node_faces_open"].items() if k != "by_point"}), flush=True)
    (ROOT / "habitat" / ("hab_overlay_results_quick.json" if quick else "hab_overlay_results.json")).write_text(json.dumps(OUT, indent=1))
