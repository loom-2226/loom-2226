"""Wayfarer v0.5 builder -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Reads inputs/wayfarer_v05_inputs.json and writes
out/wayfarer_v05_geometry.json: every part with its shape, mass, provenance and
render material; the habitat rooms; the protected-water split; and mass
properties (mass, centre of mass, inertia tensor) for every certification state.
Python 3 standard library only. Deterministic (fixed seeds).
Usage: python build_v05.py"""
import hashlib, json, math, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
INP = HERE.parent / "config" / "wayfarer_v05_inputs.json"
OUT = HERE.parent / "results" / "out"
NS = 4000          # sample points per part for inertia
NS_BIG = 20000     # for wrap-around tank shapes, whose centroid is sampled
TAU = 2 * math.pi


def ang(y, z):
    return math.degrees(math.atan2(z, y)) % 360.0


def in_arc(t, a0, a1):
    """theta t (deg) inside arc a0->a1 going counter-clockwise (a1 may exceed 360 or a0 be negative)."""
    span = a1 - a0
    if span >= 360 - 1e-9:
        return True
    return (t - a0) % 360.0 <= span + 1e-9


# ---------------------------------------------------------------- shapes
class Shape:
    """Each shape knows: contains(x,y,z), bbox, volume, sample(rng)."""

    def sample(self, rng, n):
        pts, tries = [], 0
        (x0, x1), (y0, y1), (z0, z1) = self.bbox()
        while len(pts) < n and tries < n * 400:
            tries += 1
            p = (rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(z0, z1))
            if self.contains(*p):
                pts.append(p)
        self._acc = len(pts) / max(tries, 1)
        return pts

    def mc_volume(self, n=60000, seed=7):
        rng = random.Random(seed)
        (x0, x1), (y0, y1), (z0, z1) = self.bbox()
        hit = sum(self.contains(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(z0, z1)) for _ in range(n))
        return hit / n * (x1 - x0) * (y1 - y0) * (z1 - z0)


class Sector(Shape):
    """Annular sector prism along x: x0..x1, r0..r1, theta a0..a1 (deg, CCW)."""

    def __init__(self, x0, x1, r0, r1, a0=0.0, a1=360.0):
        self.x0, self.x1, self.r0, self.r1, self.a0, self.a1 = x0, x1, r0, r1, a0, a1

    def contains(self, x, y, z):
        if not (self.x0 <= x <= self.x1):
            return False
        r = math.hypot(y, z)
        return self.r0 <= r <= self.r1 and in_arc(ang(y, z), self.a0, self.a1)

    def bbox(self):
        return (self.x0, self.x1), (-self.r1, self.r1), (-self.r1, self.r1)

    def volume(self):
        return math.radians(min(self.a1 - self.a0, 360)) / 2 * (self.r1 ** 2 - self.r0 ** 2) * (self.x1 - self.x0)

    def sample(self, rng, n):
        out = []
        for _ in range(n):
            r = math.sqrt(rng.random() * (self.r1 ** 2 - self.r0 ** 2) + self.r0 ** 2)
            t = math.radians(self.a0 + rng.random() * min(self.a1 - self.a0, 360))
            out.append((rng.uniform(self.x0, self.x1), r * math.cos(t), r * math.sin(t)))
        return out

    def spec(self):
        return {"k": "sector", "x0": self.x0, "x1": self.x1, "r0": self.r0, "r1": self.r1, "a0": self.a0, "a1": self.a1}


class CSlot(Shape):
    """Wrap-around tank region: annulus minus the top slot (|y| < hw, z > 0) minus outer grooves.
    Optional y-sign and x-range filters split it into cells."""

    def __init__(self, x0, x1, r0, r1, hw, grooves=(), gw=0.0, gd=0.0, side=0, holes=()):
        self.x0, self.x1, self.r0, self.r1, self.hw = x0, x1, r0, r1, hw
        self.grooves, self.gw, self.gd, self.side = list(grooves), gw, gd, side
        self.holes = [list(h) for h in holes]     # (y, z, radius) circles cut out (longerons through the tank)

    def contains(self, x, y, z):
        if not (self.x0 <= x <= self.x1):
            return False
        if self.side and y * self.side < 0:
            return False
        r = math.hypot(y, z)
        if not (self.r0 <= r <= self.r1):
            return False
        if z > 0 and abs(y) < self.hw:
            return False
        for hy, hz, hr in self.holes:
            if (y - hy) ** 2 + (z - hz) ** 2 < hr * hr:
                return False
        if self.gw and r > self.r1 - self.gd:
            for a in self.grooves:
                c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
                along, across = y * c + z * s, -y * s + z * c
                if along > 0 and abs(across) < self.gw / 2:
                    return False
        return True

    def bbox(self):
        return (self.x0, self.x1), (-self.r1, self.r1), (-self.r1, self.r1)

    def sample(self, rng, n, xlo=None):
        out = []
        x0 = self.x0 if xlo is None else xlo
        while len(out) < n:
            r = math.sqrt(rng.random() * (self.r1 ** 2 - self.r0 ** 2) + self.r0 ** 2)
            th = rng.random() * TAU
            x, y, z = rng.uniform(x0, self.x1), r * math.cos(th), r * math.sin(th)
            if self.contains(x, y, z):
                out.append((x, y, z))
                if not self.side and self.contains(x, -y, z):
                    out.append((x, -y, z))      # mirror sample: the shape is symmetric in y
        return out[:n]

    def volume(self):
        """deterministic polar midpoint grid over the section (about 0.05% accurate), times length"""
        if not hasattr(self, "_v"):
            nr, nt = 300, 1440
            dr, dt = (self.r1 - self.r0) / nr, TAU / nt
            xm = (self.x0 + self.x1) / 2
            area = 0.0
            for i in range(nr):
                r = self.r0 + (i + 0.5) * dr
                cs = [(math.cos((j + 0.5) * dt), math.sin((j + 0.5) * dt)) for j in range(nt)] if i == 0 else cs
                area += r * dr * dt * sum(1 for c, s in cs if self.contains(xm, r * c, r * s))
            self._v = area * (self.x1 - self.x0)
        return self._v

    def spec(self):
        return {"k": "cslot", "x0": self.x0, "x1": self.x1, "r0": self.r0, "r1": self.r1, "hw": self.hw,
                "grooves": self.grooves, "gw": self.gw, "gd": self.gd, "side": self.side, "holes": self.holes}


class DomeCyl(Shape):
    """Body of revolution along x: half-ellipsoid nose from xa (apex) to xb, then cylinder to xc.
    Radius R. If t > 0 it is a shell of thickness t (plus no end caps)."""

    def __init__(self, xa, xb, xc, R, t=0.0, xs=None, rin=0.0, gaps=()):
        self.xa, self.xb, self.xc, self.R, self.t = xa, xb, xc, R, t
        self.xs = xs          # optional flat cut: keep only x >= xs (solid only)
        self.rin = rin        # optional axial bore: keep only r >= rin (solid only; v0.5.4 sensor ring)
        self.gaps = tuple(tuple(g) for g in gaps)   # optional azimuth gaps (centre_deg, half_width_deg), solid only (v0.5.5)

    def rad(self, x):
        if x < self.xa or x > self.xc:
            return -1.0
        if x >= self.xb:
            return self.R
        u = (self.xb - x) / (self.xb - self.xa)
        return self.R * math.sqrt(max(0.0, 1 - u * u))

    def contains(self, x, y, z):
        R = self.rad(x)
        if R < 0 or (self.xs is not None and x < self.xs):
            return False
        r = math.hypot(y, z)
        if self.rin and r < self.rin:
            return False
        if self.gaps:
            a = math.degrees(math.atan2(z, y)) % 360
            if any(abs((a - g + 180) % 360 - 180) <= hw for g, hw in self.gaps):
                return False
        if self.t:
            # shell: inside outer surface, outside the inner surface offset by t
            inner = DomeCyl(self.xa + self.t, self.xb, self.xc, self.R - self.t).rad(x)
            return r <= R and (inner < 0 or r >= inner)
        return r <= R

    def bbox(self):
        return (self.xa if self.xs is None else self.xs, self.xc), (-self.R, self.R), (-self.R, self.R)

    def volume(self):
        if not self.t and (self.xc < self.xb or self.rin or self.gaps):
            # v0.5.4 fix: the closed form below assumed xc >= xb; integrate the solid of revolution directly
            x0 = max(self.xa, self.xs if self.xs is not None else self.xa)
            n = 4000
            h = (self.xc - x0) / n
            tot = 0.0
            for i in range(n):
                rr = self.rad(x0 + (i + 0.5) * h)
                tot += math.pi * max(0.0, rr * rr - self.rin * self.rin) * h if rr > self.rin else 0.0
            return tot * (1 - sum(2 * hw for _, hw in self.gaps) / 360)
        full = 2 / 3 * math.pi * self.R ** 2 * (self.xb - self.xa) + math.pi * self.R ** 2 * (self.xc - self.xb)
        if not self.t:
            if self.xs is not None:
                h, d = self.xb - self.xa, min(self.xs - self.xa, self.xb - self.xa)
                full -= math.pi * self.R ** 2 * (d * d / h - d ** 3 / (3 * h * h))
            return full
        Ri, ai = self.R - self.t, self.xa + self.t
        inner = 2 / 3 * math.pi * Ri ** 2 * (self.xb - ai) + math.pi * Ri ** 2 * (self.xc - self.xb)
        return full - inner

    def spec(self):
        s = {"k": "domecyl", "xa": self.xa, "xb": self.xb, "xc": self.xc, "R": self.R, "t": self.t}
        if self.xs is not None:
            s["xs"] = self.xs
        if self.rin:
            s["rin"] = self.rin
        if self.gaps:
            s["gaps"] = [list(g) for g in self.gaps]
        return s


class Frustum(Shape):
    """Cone frustum along x, radius r0 at x0 to r1 at x1; shell of thickness t if t > 0."""

    def __init__(self, x0, x1, r0, r1, t=0.0):
        self.x0, self.x1, self.r0, self.r1, self.t = x0, x1, r0, r1, t

    def rad(self, x):
        return self.r0 + (self.r1 - self.r0) * (x - self.x0) / (self.x1 - self.x0)

    def contains(self, x, y, z):
        if not (self.x0 <= x <= self.x1):
            return False
        R, r = self.rad(x), math.hypot(y, z)
        return r <= R and (not self.t or r >= R - self.t)

    def bbox(self):
        m = max(self.r0, self.r1)
        return (self.x0, self.x1), (-m, m), (-m, m)

    def volume(self):
        L = self.x1 - self.x0
        solid = math.pi * L / 3 * (self.r0 ** 2 + self.r0 * self.r1 + self.r1 ** 2)
        if not self.t:
            return solid
        a, b = self.r0 - self.t, self.r1 - self.t
        return solid - math.pi * L / 3 * (a * a + a * b + b * b)

    def spec(self):
        return {"k": "frustum", "x0": self.x0, "x1": self.x1, "r0": self.r0, "r1": self.r1, "t": self.t}


class Tube(Shape):
    """Solid cylinder of radius r between points p0 and p1 (any direction)."""

    def __init__(self, p0, p1, r):
        self.p0, self.p1, self.r = tuple(p0), tuple(p1), r
        d = [b - a for a, b in zip(p0, p1)]
        self.L = math.sqrt(sum(c * c for c in d))
        self.u = [c / self.L for c in d]

    def contains(self, x, y, z):
        v = (x - self.p0[0], y - self.p0[1], z - self.p0[2])
        s = sum(a * b for a, b in zip(v, self.u))
        if s < 0 or s > self.L:
            return False
        perp2 = sum(c * c for c in v) - s * s
        return perp2 <= self.r ** 2

    def bbox(self):
        lo = [min(a, b) - self.r for a, b in zip(self.p0, self.p1)]
        hi = [max(a, b) + self.r for a, b in zip(self.p0, self.p1)]
        return (lo[0], hi[0]), (lo[1], hi[1]), (lo[2], hi[2])

    def volume(self):
        return math.pi * self.r ** 2 * self.L

    def spec(self):
        return {"k": "tube", "p0": list(self.p0), "p1": list(self.p1), "r": self.r}


class Box(Shape):
    def __init__(self, x0, x1, y0, y1, z0, z1):
        self.b = ((x0, x1), (y0, y1), (z0, z1))

    def contains(self, x, y, z):
        return all(lo <= v <= hi for v, (lo, hi) in zip((x, y, z), self.b))

    def bbox(self):
        return self.b

    def volume(self):
        return math.prod(hi - lo for lo, hi in self.b)

    def sample(self, rng, n):
        return [tuple(rng.uniform(lo, hi) for lo, hi in self.b) for _ in range(n)]

    def spec(self):
        (x0, x1), (y0, y1), (z0, z1) = self.b
        return {"k": "box", "x0": x0, "x1": x1, "y0": y0, "y1": y1, "z0": z0, "z1": z1}


class Panel(Shape):
    """Flat plate along x at azimuth a: from radius r0 outward by span, thickness t (tangential)."""

    def __init__(self, x0, x1, a, r0, span, t):
        self.x0, self.x1, self.a, self.r0, self.span, self.t = x0, x1, a, r0, span, t
        self.c, self.s = math.cos(math.radians(a)), math.sin(math.radians(a))

    def contains(self, x, y, z):
        if not (self.x0 <= x <= self.x1):
            return False
        along, across = y * self.c + z * self.s, -y * self.s + z * self.c
        return self.r0 <= along <= self.r0 + self.span and abs(across) <= self.t / 2

    def bbox(self):
        R = self.r0 + self.span + self.t
        return (self.x0, self.x1), (-R, R), (-R, R)

    def volume(self):
        return (self.x1 - self.x0) * self.span * self.t

    def sample(self, rng, n):
        out = []
        for _ in range(n):
            along = self.r0 + rng.random() * self.span
            across = (rng.random() - 0.5) * self.t
            out.append((rng.uniform(self.x0, self.x1), along * self.c - across * self.s, along * self.s + across * self.c))
        return out

    def spec(self):
        return {"k": "panel", "x0": self.x0, "x1": self.x1, "a": self.a, "r0": self.r0, "span": self.span, "t": self.t}


class SettledWater(Shape):
    """Water filling the aft fraction f of a container (thrust settles it aft)."""

    def __init__(self, base, f):
        self.base, self.f = base, max(0.0, min(1.0, f))
        (x0, x1), _, _ = base.bbox()
        self.xcut = x1 - self.f * (x1 - x0)

    def contains(self, x, y, z):
        return x >= self.xcut and self.base.contains(x, y, z)

    def bbox(self):
        (x0, x1), yb, zb = self.base.bbox()
        return (self.xcut, x1), yb, zb

    def volume(self):
        return self.base.volume() * self.f

    def sample(self, rng, n):
        if isinstance(self.base, CSlot):
            return self.base.sample(rng, n, xlo=self.xcut)
        pts = self.base.sample(rng, int(n / max(self.f, 0.05)) + 10)
        return [p for p in pts if p[0] >= self.xcut][:n]

    def spec(self):
        s = self.base.spec()
        s["settled_fraction"] = self.f
        return s


class Offset(Shape):
    """Any shape moved sideways by (dy, dz)."""

    def __init__(self, base, dy, dz):
        self.base, self.dy, self.dz = base, dy, dz

    def contains(self, x, y, z):
        return self.base.contains(x, y - self.dy, z - self.dz)

    def bbox(self):
        bx, (y0, y1), (z0, z1) = self.base.bbox()
        return bx, (y0 + self.dy, y1 + self.dy), (z0 + self.dz, z1 + self.dz)

    def volume(self):
        return self.base.volume()

    def sample(self, rng, n):
        return [(x, y + self.dy, z + self.dz) for x, y, z in self.base.sample(rng, n)]

    def spec(self):
        s = self.base.spec()
        s["offset_yz"] = [self.dy, self.dz]
        return s


def exact_centroid(sh):
    """Analytic centroid where it is simple; None means sample it."""
    if isinstance(sh, Offset):
        c = exact_centroid(sh.base)
        return None if c is None else [c[0], c[1] + sh.dy, c[2] + sh.dz]
    if isinstance(sh, Sector):
        span = math.radians(min(sh.a1 - sh.a0, 360))
        if span >= TAU - 1e-9 or sh.r1 <= 0:
            rb = 0.0
        else:
            rb = 2 / 3 * (sh.r1 ** 3 - sh.r0 ** 3) / (sh.r1 ** 2 - sh.r0 ** 2) * math.sin(span / 2) / (span / 2)
        mid = math.radians(sh.a0) + span / 2
        return [(sh.x0 + sh.x1) / 2, rb * math.cos(mid), rb * math.sin(mid)]
    if isinstance(sh, Box):
        return [(lo + hi) / 2 for lo, hi in sh.b]
    if isinstance(sh, Tube):
        return [(a + b) / 2 for a, b in zip(sh.p0, sh.p1)]
    if isinstance(sh, Panel):
        rm = sh.r0 + sh.span / 2
        return [(sh.x0 + sh.x1) / 2, rm * sh.c, rm * sh.s]
    return None


_MEMO = {}


# ---------------------------------------------------------------- parts
class Part:
    def __init__(self, pid, name, system, shape, mass_t, prov, mat, dry=True, tags=()):
        self.id, self.name, self.system, self.shape = pid, name, system, shape
        self.mass_t, self.prov, self.mat, self.dry, self.tags = mass_t, prov, mat, dry, set(tags)

    def moments(self):
        """centroid (analytic where simple) and second moments from uniform samples (memoised by shape)."""
        if not hasattr(self, "_m"):
            key = self.id + json.dumps(self.shape.spec(), sort_keys=True)
            if key not in _MEMO:
                rng = random.Random(int(hashlib.sha1(self.id.encode()).hexdigest()[:8], 16))
                big = isinstance(self.shape, (CSlot, SettledWater)) or isinstance(getattr(self.shape, "base", None), CSlot)
                pts = self.shape.sample(rng, NS_BIG if big else NS)
                n = len(pts)
                c = exact_centroid(self.shape) or [sum(p[i] for p in pts) / n for i in range(3)]
                S = [[sum((p[i] - c[i]) * (p[j] - c[j]) for p in pts) / n for j in range(3)] for i in range(3)]
                _MEMO[key] = (c, S, n)
            self._m = _MEMO[key]
        return self._m


def mass_props(parts):
    M = sum(p.mass_t for p in parts) * 1000.0
    cg = [sum(p.mass_t * 1000 * p.moments()[0][i] for p in parts) / M for i in range(3)]
    I = [[0.0] * 3 for _ in range(3)]
    for p in parts:
        m = p.mass_t * 1000
        c, S, _ = p.moments()
        d = [c[i] - cg[i] for i in range(3)]
        cov = [[S[i][j] + d[i] * d[j] for j in range(3)] for i in range(3)]   # second moments about ship CG
        tr = cov[0][0] + cov[1][1] + cov[2][2]
        for i in range(3):
            for j in range(3):
                I[i][j] += m * ((tr if i == j else 0.0) - cov[i][j])
    return {"mass_t": M / 1000, "cg_m": cg, "inertia_kg_m2": I}


def eig_sym3(A):
    """Jacobi eigenvalues for a symmetric 3x3 matrix."""
    a = [row[:] for row in A]
    v = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    for _ in range(60):
        p, q = max(((i, j) for i in range(3) for j in range(i + 1, 3)), key=lambda ij: abs(a[ij[0]][ij[1]]))
        if abs(a[p][q]) < 1e-9 * (abs(a[p][p]) + abs(a[q][q]) + 1e-30):
            break
        th = 0.5 * math.atan2(2 * a[p][q], a[q][q] - a[p][p])
        c, s = math.cos(th), math.sin(th)
        for k in range(3):
            akp, akq = a[k][p], a[k][q]
            a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
        for k in range(3):
            apk, aqk = a[p][k], a[q][k]
            a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
        for k in range(3):
            vkp, vkq = v[k][p], v[k][q]
            v[k][p], v[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    return [a[i][i] for i in range(3)], [[v[k][i] for k in range(3)] for i in range(3)]


# ---------------------------------------------------------------- build
def build(I, dy=0.0, dz=0.0):
    """dy, dz: sideways offset of the torch chain and aft RCS (thrust-line offset)."""
    H, L = I["hull"], I["ledger"]
    parts = []

    def add(*a, **k):
        p = Part(*a, **k)
        parts.append(p)
        return p

    Ro, Rp = H["outer_r_m"], H["pressure_r_m"]
    # --- habitat shell, pressure vessel, decks
    hx0, hx1 = H["habitat_shell_x_m"]
    add("armor", "Armour and fixed shielding shell", "habitat", DomeCyl(hx0, hx0 + H["bow_cap_depth_m"], hx1, Ro, Ro - Rp),
        L["armor_fixed_shield_t"], "CANON_MASS_DESIGN_POSITION", "hull_armor")
    px0, px1 = H["pressure_vessel_x_m"]
    SS = L["structure_split"]
    hab = I["habitat"]
    ft = hab["floor_thickness_m"]
    add("pressure_vessel", "Pressure vessel (inner hull)", "structure",
        DomeCyl(px0, px0 + H["pressure_head_depth_m"], px1 - ft, Rp, 0.03), SS["pressure_vessel_and_bulkheads"] * 0.75,
        "ENGINEERING_ASSUMPTION", "pressure_hull")
    add("aft_bulkhead", "Aft pressure bulkhead (L5 floor)", "structure", Sector(px1 - ft, px1, 0.0, Rp),
        SS["pressure_vessel_and_bulkheads"] * 0.25 + L.get("aoi_aft_bulkhead_reinforcement_t",0.), "ENGINEERING_ASSUMPTION: aft pressure bulkhead reserve-funded shielding margin; test G6", "bulkhead")
    decks = hab["decks"]
    floors = [d for d in decks[:-1]]
    for d in floors:
        f0 = d["x_m"][1]
        add(f"floor_{d['id']}", f"{d['id']} floor", "structure", Sector(f0, f0 + ft, hab["core_r_m"], hab["usable_r_m"]),
            SS["decks_and_core"] * 0.75 / len(floors), "ENGINEERING_ASSUMPTION", "floor")
    core_x0 = decks[1]["x_m"][0]
    add("core_trunk", "Central trunk (utilities, avionics racks, goods lift)", "habitat",
        Sector(core_x0, decks[-1]["x_m"][1], 0.0, hab["core_r_m"]), SS["decks_and_core"] * 0.25, "ENGINEERING_ASSUMPTION", "core")
    av = L["avionics_split"]
    add("core_racks", "Avionics racks in the trunk", "avionics", Sector(core_x0, decks[-1]["x_m"][1], 0.0, hab["core_r_m"] * 0.9),
        av["core_racks"], "ENGINEERING_ASSUMPTION", "avionics")
    d1 = decks[0]
    CL = d1.get("command_layout", {})
    SR = CL.get("sensor_ring")
    if SR:
        sens_shape = DomeCyl(px0, px0 + H["pressure_head_depth_m"], SR["x_aft_m"], hab["usable_r_m"], rin=SR["r_in_m"], gaps=SR["gaps_deg"])
    else:
        sens_shape = DomeCyl(px0, px0 + H["pressure_head_depth_m"], d1["x_m"][0] + 0.8, hab["usable_r_m"], rin=CL.get("sensor_bore_r_m", 0.0))
    add("bow_sensors", "Bow sensors and command electronics" + (" (shoulder ring)" if SR else (" (ring around the viewing bore)" if CL else "")), "avionics",
        sens_shape, av["bow_sensors"],
        "ENGINEERING_ASSUMPTION", "avionics")
    if CL.get("platform"):
        pl = CL["platform"]
        add("command_platform", "Command platform (raised forward couches)", "habitat",
            Box(pl["x_m"][0], pl["x_m"][1], pl["y_m"][0], pl["y_m"][1], pl["z_m"][0], pl["z_m"][1]), pl["mass_t"], pl["prov"], "equipment")
    I4 = CL.get("i4_lock")
    if I4:
        for name, pl in I4["platforms"].items():
            add(name, name.replace("_", " "), "habitat",
                Box(pl["x_m"][0], pl["x_m"][1], pl["y_m"][0], pl["y_m"][1], pl["z_m"][0], pl["z_m"][1]),
                pl["mass_t"], pl["prov"], "equipment")
        for st in I4["stations"]:
            x, (y,z) = st["base_x"], st["center_yz"]
            add("i4_seat_"+st["id"], "I4 station hardware surrogate "+st["id"], "habitat",
                Box(x-0.10,x+0.10,y-0.35,y+0.35,z-0.35,z+0.35),
                I4["seating_hardware_t_each"], "ENGINEERING_ASSUMPTION: redistributed existing L1 room outfitting; nonqualified seat proxy", "equipment",tags=("no_render",))
        for name, mass, y,z in (("mission_table",I4["shared_table_t"],0.40,-3.45),
                                  ("workbench",I4["workbench_t"],-2.45,-2.18),
                                  ("cabinetry",I4["other_cabinetry_t"],-3.45,1.10)):
            add("i4_"+name,name,"habitat",Box(2.86,2.98,y-0.20,y+0.20,z-0.20,z+0.20),
                mass,"ENGINEERING_ASSUMPTION: redistributed L1 room outfitting; low-g visual mass proxy","equipment",tags=("no_render",))
    # 2026-11-01 I4 candidate carry-over: reserve-funded interior pieces only.
    # Existing I4 NAV/terrace structural platforms are NOT duplicated.
    for obj in I.get("i4_carryover",{}).get("items",[]):
        tag=obj["id"]
        if obj["kind"]=="box":
            x,y,z=obj["xyz"];sx,sy,sz=obj["size"]
            shape=Box(x-sx/2,x+sx/2,y-sy/2,y+sy/2,z-sz/2,z+sz/2)
        elif obj["kind"]=="tube":
            shape=Tube(tuple(obj["a"]),tuple(obj["b"]),obj["radius_m"])
        elif obj["kind"]=="arc":
            # Deterministic ring-rail approximation with fixed 18 angular segments.
            for k in range(18):
                a=obj["angles_rad"][0]+(obj["angles_rad"][1]-obj["angles_rad"][0])*k/18
                b=obj["angles_rad"][0]+(obj["angles_rad"][1]-obj["angles_rad"][0])*(k+1)/18
                y,z=obj["radius_m"]*math.cos(a),obj["radius_m"]*math.sin(a)
                yy,zz=obj["radius_m"]*math.cos(b),obj["radius_m"]*math.sin(b)
                add("i4_"+tag+"_"+str(k),tag,"habitat",
                    Tube((obj["x_m"],y,z),(obj["x_m"],yy,zz),obj["tube_radius_m"]),
                    obj["mass_t"]/18,"I4_CARRYOVER: "+obj["source"],"rail",
                    tags=("from_reserve","no_render"))
            continue
        else:
            raise ValueError("unknown I4 item kind "+obj["kind"])
        add("i4_"+tag,tag,"habitat",shape,obj["mass_t"],
            "I4_CARRYOVER: "+obj["source"],"equipment",tags=("from_reserve","no_render"))
    if CL.get("flight_deck"):
        fd = CL["flight_deck"]
        add("flight_deck", "Flight deck (mezzanine carrying the pilot and navigator couches)", "habitat",
            Box(fd["x_m"][0], fd["x_m"][1], fd["y_m"][0], fd["y_m"][1], fd["z_m"][0], fd["z_m"][1]), fd["mass_t"], fd["prov"], "equipment")
    # --- rooms
    rooms = []
    ff = hab["free_fraction"]
    jac = hab["shelter_jacket"]["water_thickness_m"]
    jacket_parts = []
    for d in decks:
        x0, x1 = d["x_m"]
        for rm in d["rooms"]:
            a0, a1 = rm["theta_deg"]
            if d.get("dome"):
                xs_cut = None if d.get("command_layout", {}).get("sensor_ring") else d1["x_m"][0] + 0.8
                shape = DomeCyl(px0, px0 + H["pressure_head_depth_m"], x1, hab["usable_r_m"], xs=xs_cut)
                xin0 = x0
            else:
                r0, r1 = rm.get("r_m", hab["room_r_m"])
                shape = Sector(x0, x1, r0, r1, a0, a1)
            interior = shape
            if rm.get("jacket"):
                r0, r1 = hab["room_r_m"]
                da = math.degrees(jac / ((r0 + r1) / 2))
                faces = [("outer", Sector(x0, x1, r1 - jac, r1, a0, a1)), ("inner", Sector(x0, x1, r0, r0 + jac, a0, a1)),
                         ("radial_a", Sector(x0, x1, r0, r1, a0, a0 + da)), ("radial_b", Sector(x0, x1, r0, r1, a1 - da, a1)),
                         ("ceiling", Sector(x0, x0 + jac, r0, r1, a0, a1)), ("floor", Sector(x1 - jac, x1, r0, r1, a0, a1))]
                faces = [f for f in faces if f[0].split("_")[0] in hab["shelter_jacket"]["faces"]]
                for nm, sh in faces:
                    jacket_parts.append((nm, sh))
                x1i = x1 - jac if "floor" in hab["shelter_jacket"]["faces"] else x1
                interior = Sector(x0 + jac, x1i, r0 + jac, r1 - jac, a0 + da, a1 - da)
            vol = interior.volume()
            rooms.append({"id": rm["id"], "deck": d["id"], "name": rm["name"], "kind": rm["kind"], "who": rm.get("who"),
                          "theta_deg": [a0, a1], "x_m": [x0, x1], "volume_m3": vol,
                          "nhv_m3": vol * ff[rm["kind"]], "couches": rm.get("couches", 0), "windows": rm.get("windows", 0),
                          "shape": interior.spec(), **{k: rm[k] for k in ("occupancy", "bunks", "door", "entrance", "berth_viewports") if k in rm}})
            add(f"room_{rm['id']}", rm["name"], "habitat", interior, rm["mass_t"], "ENGINEERING_ASSUMPTION", f"room_{rm['kind']}",
                tags=("room",))
        if not d.get("dome"):
            cr = hab["corridor_r_m"]
            sh = Sector(x0, x1, cr[0], cr[1])
            rooms.append({"id": f"{d['id']}-corridor", "deck": d["id"], "name": "Corridor ring", "kind": "corridor", "who": None,
                          "theta_deg": [0, 360], "x_m": [x0, x1], "volume_m3": sh.volume(),
                          "nhv_m3": sh.volume() * ff["corridor"], "couches": 0, "windows": 0, "shape": sh.spec()})
    # --- v0.5.6 crew systems, paid from the engineering reserve (dry mass unchanged)
    CS = hab.get("crew_systems")
    if CS:
        rt = ("from_reserve",)
        nr = ("from_reserve", "no_render")
        WM = I["features"].get("window_mass")
        if WM:
            def wmass(d):
                return max(WM["min_assembly_t"], WM["t_per_0p8m_window"] * math.pi * (d / 2) ** 2 / WM["area_0p8m_m2"])
            fw = [f for f in features(I, rooms) if f["kind"] == "window"]
            CD = CL.get("crown_dome", {})
            if CD.get("adopted"):   # v0.5.7: crown dome assembly (panes, Osteon frame, brow ring, gore tracks and drives); the gores carry the armour the opening removes
                add("crown_dome", "Crown dome: ceramic panes, Osteon frame, brow ring, tambour gore tracks and drives", "habitat",
                    Box(0.0, 0.6, -CD["r_m"], CD["r_m"], -CD["r_m"], CD["r_m"]), sum(CD["mass_t"].values()), CD["prov"], "frame", tags=nr)
            # kT Option A (2026-11-01): second independent transparent ceramic pressure
            # dome and AOI fill are PHYSICAL MASS from reserve, never a pressure seal.
            AOI = CD.get("adaptive_optogel")
            if AOI:
                rr = CD["i4_crown_option_B"]["inner_diameter_m"] / 2
                # Coarse spatial mass surrogate, preserving separate independent components.
                add("crown_backup_pressure_dome", "Independent monolithic ceramic backup pressure dome",
                    "habitat", Box(-0.12,0.48,-rr,rr,-rr,rr),
                    AOI["backup_pressure_dome_mass_t"],
                    "kT Option A: 7m independently pressure-capable backup +0.12m forward; proof OPEN", "frame",
                    tags=("from_reserve","no_render"))
                add("crown_adaptive_optogel", "AOI-2226 optical gel interspace (not pressure boundary)",
                    "habitat", Box(-0.06,0.54,-rr,rr,-rr,rr),
                    AOI["mass_t"], AOI["research_ref"]+"; optical modes declared; impact credit zero",
                    "window", tags=("from_reserve","no_render"))
            for k, f in enumerate(fw):
                hb = 0.15 if not f.get("berth") else 0.09   # v0.5.7 berth viewports: smaller box, kept outside the berth water ring
                c = [f["pos"][i] - (hb + 0.01) * f["normal"][i] for i in range(3)]
                add(f"window_{f['room']}_{k}", f"Window assembly ({f['room']}, {f['d_m']:.2f} m)", "habitat",
                    Box(c[0] - hb, c[0] + hb, c[1] - hb, c[1] + hb, c[2] - hb, c[2] + hb), wmass(f["d_m"]), WM["prov"], "frame", tags=nr)
        fdc = CL.get("flight_deck", {}).get("columns")
        if fdc:
            fd = CL["flight_deck"]
            Lc = d1["x_m"][1] - fd["x_m"][1]
            m1 = math.pi / 4 * (fdc["od_m"] ** 2 - (fdc["od_m"] - 2 * fdc["wall_m"]) ** 2) * Lc * fdc["density_t_m3"] * fdc["fittings_factor"]
            for k, (y, z) in enumerate(fdc["positions_yz_m"]):
                add(f"flight_deck_column_{k}", "Flight-deck column", "habitat", Tube((fd["x_m"][1], y, z), (d1["x_m"][1], y, z), fdc["od_m"] / 2),
                    m1, fdc["prov"], "frame", tags=rt)
        if I4 and I4.get("terrace_columns"):
            tc = I4["terrace_columns"]
            for k,(y,z) in enumerate(tc["positions_yz_m"]):
                add(f"i4_terrace_column_{k}", "I4 terrace column (nominal; load path HOLD)",
                    "habitat",Tube((tc["x_m_end"],y,z),(d1["x_m"][1],y,z),tc["od_m"]/2),
                    tc["mass_total_t"]/len(tc["positions_yz_m"]),tc["prov"],"frame",tags=("from_reserve",))
        iso = CS.get("l4_l5_isolation")
        if iso:
            d4 = next(d for d in decks if d["id"] == "L4")
            fx = d4["x_m"][1]
            for h in iso["hatches"]:
                lw = next(l for l in hab["ladderways"] if l["theta_deg"] == h["ladderway_theta_deg"])
                y, z = lw["r_m"] * math.cos(math.radians(lw["theta_deg"])), lw["r_m"] * math.sin(math.radians(lw["theta_deg"]))
                hs = iso["hatch_size_m"] / 2
                add(f"hatch_L4L5_{lw['theta_deg']}", f"L4/L5 pressure hatch at the {lw['theta_deg']} deg ladderway", "habitat",
                    Box(fx, fx + 0.06, y - hs, y + hs, z - hs, z + hs), iso["hatch_t"], iso["prov"], "hatch", tags=rt)
            add("trunk_plug_L4L5", "Trunk pressure plug with lift hatch and feedthroughs (L4/L5)", "habitat",
                Sector(fx, fx + hab["floor_thickness_m"], 0.0, hab["core_r_m"]), iso["trunk_plug_t"], iso["prov"], "bulkhead", tags=nr)
        for rm in [r for d in decks for r in d["rooms"] if r.get("entrance", {}).get("closure_mass_t")]:
            e = rm["entrance"]
            d = next(d for d in decks if rm in d["rooms"])
            th = math.radians(e["center_deg"])
            y, z = e["at_r_m"] * math.cos(th), e["at_r_m"] * math.sin(th)
            add(f"doors_{rm['id']}", f"{rm['name']}: bi-parting sliding doors", "habitat",
                Box(d["x_m"][0], d["x_m"][1], y - 0.1, y + 0.1, z - 0.1, z + 0.1), e["closure_mass_t"], e["change_prov"], "door", tags=nr)
        sb = CS.get("shelter_backup")
        if sb:
            d4 = next(d for d in decks if d["id"] == "L4")
            sh = next(r for r in d4["rooms"] if r["kind"] == "shelter")
            th = math.radians(sum(sh["theta_deg"]) / 2)
            xm = sum(d4["x_m"]) / 2
            add("shelter_backup", "Storm shelter 72 h stored life support (O2, LiOH, food, battery)", "habitat",
                Box(xm - 0.2, xm + 0.2, 3.0 * math.cos(th) - 0.2, 3.0 * math.cos(th) + 0.2, 3.0 * math.sin(th) - 0.2, 3.0 * math.sin(th) + 0.2),
                sb["mass_t"], sb["prov"], "equipment", tags=nr)
        if CS.get("rescue_kit_t"):
            th = math.radians(230)
            xm = sum(next(d for d in decks if d["id"] == "L4")["x_m"]) / 2
            add("rescue_kit", "Litter, vertical-lift harness, rope system and hoist points", "habitat",
                Box(xm - 0.15, xm + 0.15, 3.5 * math.cos(th) - 0.15, 3.5 * math.cos(th) + 0.15, 3.5 * math.sin(th) - 0.15, 3.5 * math.sin(th) + 0.15),
                CS["rescue_kit_t"], CS["prov"], "equipment", tags=nr)
        dv = CS.get("docking_view")
        if dv:
            for k, cam in enumerate(dv["cameras"]):
                x, y, z = cam["pos_m"]
                add(f"docking_camera_{k}", f"Docking camera: {cam['name']}", "service", Box(x - 0.1, x + 0.1, y - 0.1, y + 0.1, z - 0.1, z + 0.1),
                    dv["cameras_t"] / len(dv["cameras"]), dv["prov"], "rcs", tags=rt)
    n_dist = len([d for d in decks])
    for d in decks:
        x0, x1 = d["x_m"]
        orr = hab.get("outfit_r_by_deck_m", {}).get(d["id"], [hab["usable_r_m"] - 0.1, hab["usable_r_m"]])
        add(f"outfit_{d['id']}", f"{d['id']} distributed outfitting", "habitat", Sector(x0, x1, orr[0], orr[1]),
            hab["distributed_outfitting_t"] / n_dist, "ENGINEERING_ASSUMPTION", "outfit")
    bs = hab.get("berth_shield")
    if bs:
        jacket_parts.append(("berth_ring", Sector(bs["x_m"][0], bs["x_m"][1], bs["r_m"][0], bs["r_m"][1], bs["theta_deg"][0], bs["theta_deg"][1])))
        for k, cl in enumerate(bs.get("floor_collars", [])):
            jacket_parts.append(("berth_ring", Sector(cl["x_m"][0], cl["x_m"][1], cl["r_m"][0], cl["r_m"][1], cl["theta_deg"][0], cl["theta_deg"][1])))
    jacket_vol = sum(sh.volume() for _, sh in jacket_parts)
    # --- service region
    sv = I["service"]
    pf = sv["plant_fore"]
    add("plant_fore", "Relational plant, fore block", "plant", Sector(pf["x_m"][0], pf["x_m"][1], 0.0, pf["r_m"]),
        pf["mass_t"], pf["prov"], "plant")
    sec = {k: Sector(v["x_m"][0], v["x_m"][1], v["r_m"][0], v["r_m"][1], v["theta_deg"][0], v["theta_deg"][1])
           for k, v in sv["sectors"].items()}
    add("courier_systems", "Mission and courier systems", "mission", sec["transfer_and_courier"], L["mission_courier_systems_t"],
        "CANON_MASS_DESIGN_POSITION", "equipment")
    rs = L["rcs_split"]
    add("service_arm", "Service arm and umbilicals", "service", sec["transfer_and_courier"], rs["service_arm_and_umbilicals"],
        "ENGINEERING_ASSUMPTION", "equipment")
    dc = sv["docking_collar"]
    cz0 = -(Ro - 0.9)
    add("docking_collar", "Docking collar", "service", Tube((dc["x_m"], 0.0, cz0), (dc["x_m"], 0.0, -(Ro + 0.25)), dc["port_d_m"] / 2),
        rs["docking_collar"], dc["prov"], "collar")
    segs = sv["tunnel"]["segments"]
    tl = sum(math.dist(s["from"], s["to"]) for s in segs)
    for i, s in enumerate(segs):
        add(f"tunnel_{i}", f"Pressure tunnel: {s['name']}", "service", Tube(s["from"], s["to"], sv["tunnel"]["d_m"] / 2),
            rs["transfer_tunnel"] * math.dist(s["from"], s["to"]) / tl, sv["tunnel"]["prov"], "tunnel", tags=("inhabited",))
    # --- structure
    lo = I["longerons"]
    holes = []
    for it in lo["items"]:
        if it["kind"] == "tube":
            y, z = it["y_m"], it["z_m"]
            shp = Tube((lo["x_m"][0], y, z), (lo["x_m"][1], y, z), it["d_m"] / 2)
            holes.append((y, z, it["d_m"] / 2 + 0.02))
        else:
            r0, r1 = it["r_m"]
            shp = Panel(lo["x_m"][0], lo["x_m"][1], it["theta_deg"], r0, r1 - r0, it["width_m"])
        add(f"longeron_{it['name'].replace(' ', '_')}", f"Longeron ({it['name']})", "structure", shp,
            SS["longerons"] / len(lo["items"]), lo["prov"], "longeron", tags=("longeron",))
    VB = I["habitat"].get("crew_systems", {}).get("viewport_band")
    if VB:   # v0.5.7 rev 3: panoramic viewport band round L2 (panes, Osteon mullions, tambour shutter), paid from the reserve
        tot_m2 = sum((sg["x_m"][1] - sg["x_m"][0]) * Rp * math.radians(sg["theta_deg"][1] - sg["theta_deg"][0]) for sg in VB["segments"])
        for k, sg in enumerate(VB["segments"]):
            a_m2 = (sg["x_m"][1] - sg["x_m"][0]) * Rp * math.radians(sg["theta_deg"][1] - sg["theta_deg"][0])
            add(f"viewport_band_{k}", f"L2 viewport band, segment {k} ({sg['theta_deg'][0]}-{sg['theta_deg'][1]} deg)", "habitat",
                Sector(sg["x_m"][0], sg["x_m"][1], Rp - 0.05, Rp, sg["theta_deg"][0], sg["theta_deg"][1]),
                (VB["mass_t"] * a_m2 / tot_m2) if "mass_t" in VB else a_m2 * sum(VB["kg_per_m2"].values()) / 1000, VB["prov"], "frame", tags=("from_reserve", "no_render"))
    SB = I["habitat"]["berth_shield"].get("service_band")
    if SB:   # v0.5.7: polyethylene band in the service section, restores the berths' aft-outboard screen once the planks are gone
        add("service_shield_band", "Service-section shield band (polyethylene)", "habitat", Sector(SB["x_m"][0], SB["x_m"][1], SB["r_m"][0], SB["r_m"][1]),
            SB["mass_t"], SB["prov"], "equipment", tags=("from_reserve", "no_render"))
    LJ = lo.get("joints")
    if LJ:   # v0.5.7: joints for the four sized tubes (conventional masses), paid from the structure line's longeron share
        tubes = [it for it in lo["items"] if it["kind"] == "tube"]
        ef = LJ["end_fittings"]
        for x in ef["x_m"]:
            for it in tubes:
                xa = x if x < lo["x_m"][1] else x - 0.5
                add(f"longeron_end_fitting_{x:g}_{it['name'].replace(' ', '_')}", f"Longeron end fitting ({it['name']}, x {x:g})", "structure",
                    Box(xa, xa + 0.5, it["y_m"] - 0.3, it["y_m"] + 0.3, it["z_m"] - 0.3, it["z_m"] + 0.3), ef["each_t"], LJ["prov"], "frame", tags=("longeron_joint", "no_render"))
        nm = LJ["node_mounts"]
        add("node_mount_allowance", "Field-node mounts and access hatches (allowance; location open)", "structure",
            Sector(lo["x_m"][0], lo["x_m"][1], Ro - 0.13, Ro - 0.02), nm["count"] * nm["each_t"], LJ["prov"] + "; " + nm["note"], "frame", tags=("longeron_joint", "no_render"))
        bc = LJ["bay_corners"]
        for x in bc["x_m"]:
            for sg in (-1, 1):
                add(f"bay_corner_{x:g}_{'s' if sg > 0 else 'p'}", f"Bay-slot corner doubler (x {x:g})", "structure",
                    Box(x - 0.3, x + 0.3, sg * I["tanks"]["slot_half_width_m"] - 0.15, sg * I["tanks"]["slot_half_width_m"] + 0.15, 3.3, 3.7),
                    bc["each_t"], LJ["prov"], "frame", tags=("longeron_joint", "no_render"))
    mx0, mx1 = H["midship_x_m"]
    T = I["tanks"]
    add("skin_service", "Outer skin, service region", "structure", Sector(H["service_x_m"][0], H["service_x_m"][1], Ro - 0.02, Ro),
        SS["outer_skin_midship"] * 4 / 20.3, "ENGINEERING_ASSUMPTION", "hull_skin")
    add("skin_midship", "Outer skin, midship (C-shaped, open at the slot)", "structure",
        CSlot(mx0, mx1, Ro - 0.02, Ro, T["slot_half_width_m"]), SS["outer_skin_midship"] * 14.3 / 20.3, "ENGINEERING_ASSUMPTION", "hull_skin")
    add("skin_aft", "Outer skin, manifold region", "structure", Sector(mx1, H["manifold_x_m"][1], Ro - 0.02, Ro),
        SS["outer_skin_midship"] * 2 / 20.3, "ENGINEERING_ASSUMPTION", "hull_skin")
    frames = [x for x in frange(H["service_x_m"][0], H["manifold_x_m"][1], I["frames"]["spacing_m"])]
    FR = I["frames"]
    for x in frames:
        if mx0 <= x < mx1:
            shp = CSlot(x, x + 0.15, FR["r_m_midship"][0], FR["r_m_midship"][1], T["slot_half_width_m"])
        else:
            shp = Sector(x, x + 0.15, FR["r_m_elsewhere"][0], FR["r_m_elsewhere"][1])
        add(f"frame_{x:g}", f"Ring frame x {x:g}", "structure", shp, SS["ring_frames"] / len(frames), "ENGINEERING_ASSUMPTION", "frame")
    tx0, tx1 = T["x_m"]
    g = T["groove"]
    add("tank_shell_out", "Tank outer wall", "structure", CSlot(tx0, tx1, T["r_out_m"] - 0.02, T["r_out_m"], T["slot_half_width_m"], g["azimuths_deg"], g["width_m"], 0.0),
        (SS["tank_shells"] + L["c_tank_penalty_t"]) * 0.55, "ENGINEERING_ASSUMPTION", "tank_shell")
    add("tank_shell_in", "Tank inner wall", "structure", CSlot(tx0, tx1, T["r_in_m"], T["r_in_m"] + 0.02, T["slot_half_width_m"]),
        (SS["tank_shells"] + L["c_tank_penalty_t"]) * 0.45, "ENGINEERING_ASSUMPTION", "tank_shell")
    B = I["bay"]
    add("bay_liner", "Bay liner and cradle", "structure", CSlot(B["x_m"][0], B["x_m"][1], B["bore_r_m"], B["bore_r_m"] + 0.04, B["slot_half_width_m"]),
        SS["bay_liner"] - B["doors"]["mass_t"], "ENGINEERING_ASSUMPTION", "bay")
    half = math.degrees(math.acos(B["slot_half_width_m"] / Ro))
    add("door_starboard", "Bay door, starboard", "structure", Sector(B["x_m"][0], B["x_m"][1], Ro - 0.1, Ro, half, 90.0),
        B["doors"]["mass_t"] / 2, B["doors"]["prov"], "door", tags=("door",))
    add("door_port", "Bay door, port", "structure", Sector(B["x_m"][0], B["x_m"][1], Ro - 0.1, Ro, 90.0, 180 - half),
        B["doors"]["mass_t"] / 2, B["doors"]["prov"], "door", tags=("door",))
    add("thrust_cone", "Thrust cone (longerons to reactor frame)", "structure",
        Frustum(H["shield_x_m"][0], H["shield_x_m"][1], Ro - 0.1, H["shield_r_m"] + 0.2, 0.06), SS["thrust_cone"],
        "ENGINEERING_ASSUMPTION", "thrust_cone")
    # --- midship equipment
    es = L["electrical_split"]
    add("electrical", "Electrical conversion and distribution (aft C-ring)", "electrical",
        CSlot(tx1, mx1, T["r_in_m"], T["r_out_m"], T["slot_half_width_m"]), es["aft_c_ring"], es["prov"], "equipment")
    er = I["service"]["electrical_ring"]
    add("electrical_fwd", "Electrical conversion and distribution (service ring)", "electrical",
        Sector(er["x_m"][0], er["x_m"][1], er["r_m"][0], er["r_m"][1], er["theta_deg"][0], er["theta_deg"][1]), es["service_ring"], es["prov"], "equipment")
    add("plant_aft", "Relational plant, aft block", "plant", Sector(mx1, H["manifold_x_m"][1], 0.0, pf["r_m"]),
        I["ledger"]["relational_plant_t"] - pf["mass_t"], "DERIVED", "plant")
    add("manifold", "Radiator manifold, pumps and heat exchangers", "thermal",
        Sector(mx1, H["manifold_x_m"][1], pf["r_m"], Ro - 0.02), L["thermal_radiators_t"], "CANON_MASS_DESIGN_POSITION", "manifold")
    R = I["radiators"]
    for a in R["azimuths_deg"]:
        add(f"strake_{a}", f"Radiator strake {a} deg (stowed)", "thermal",
            Panel(R["x_m"][0], R["x_m"][1], a, R["root_r_m"] - g["depth_m"], g["depth_m"], g["width_m"]),
            L["radiator_panels_t"] / 4, R["prov"], "radiator", tags=("strake",))
    # --- hot fins aft of the shield (v0.5.2): paid from the engineering reserve, folded except in torch burns
    HF = I.get("hot_fins")
    if HF:
        nf = len(HF["azimuths_deg"])
        fx0, fx1 = HF["x_m"]
        panels_t = 2 * nf * (fx1 - fx0) * HF["pleat_m"] * HF["pleats"] * HF["kg_per_m2_face"] / 1000
        for a in HF["azimuths_deg"]:
            add(f"hotfin_{a}", f"Hot fin {a} deg (folded)", "thermal",
                Panel(fx0, fx1, a, HF["root_r_m"], HF["pleat_m"], HF["stowed_stack_thickness_m"]),
                panels_t / nf, HF["prov"], "hotfin", tags=("fin", "from_reserve"))
            add(f"hotfin_root_{a}", f"Hot fin {a} deg root truss, fold-out drive and hot loop", "thermal",
                Panel(HF["x_m"][0] + 5.0, fx1, a, 3.0, HF["root_r_m"] - 3.0, 0.3),
                HF["allowance_t"] / nf, HF["allowance_prov"], "radiator", tags=("from_reserve",))
    # --- RCS
    for c in I["rcs"]["clusters"]:
        y, z = c["r_m"] * math.cos(math.radians(c["theta_deg"])), c["r_m"] * math.sin(math.radians(c["theta_deg"]))
        bx = Box(c["x_m"] - 0.4, c["x_m"] + 0.4, y - 0.4, y + 0.4, z - 0.4, z + 0.4)
        if c["id"].startswith("A"):
            bx = Offset(bx, dy, dz)
        n_ax = sum(1 for k in I["rcs"]["clusters"] if k.get("axial"))
        m_ax = L.get("rcs_axial_t", 0.0) / n_ax if c.get("axial") and n_ax else 0.0     # rev 6: one axial thruster per cluster, paid from the reserve
        add(f"rcs_{c['id']}", f"RCS cluster {c['id']}" + (" (with axial thruster)" if m_ax else ""), "rcs", bx,
            rs["rcs_clusters"] / len(I["rcs"]["clusters"]) + m_ax, I["rcs"]["prov"], "rcs", tags=("torch_chain",) if c["id"].startswith("A") else ())
    # --- torch
    P = L["propulsion_split"]
    tc = ("torch_chain",)
    add("shield", "Shadow shield", "propulsion", Offset(Sector(*H["shield_x_m"], 0.0, H["shield_r_m"]), dy, dz), P["shield"], P["prov"], "shield", tags=tc)
    add("reactor", "Fusion reactor and thrust frame", "propulsion", Offset(Sector(*H["reactor_x_m"], 0.0, H["reactor_r_m"]), dy, dz), P["reactor"], P["prov"], "reactor", tags=tc)
    add("nozzle", "Magnetic nozzle", "propulsion", Offset(Frustum(*H["nozzle_x_m"], *H["nozzle_r_m"], 0.15), dy, dz), P["nozzle"], P["prov"], "nozzle", tags=tc)
    # --- shuttle and drones (state-dependent)
    S = I["shuttle"]
    add("shuttle", "Rover-drop shuttle (docked, tanks empty)", "shuttle", Tube((S["x_m"][0], 0, 0), (S["x_m"][1], 0, 0), S["diameter_m"] / 2),
        S["dry_t"], S["prov"], "shuttle", tags=("shuttle", "inhabited_when_docked"))
    hold_s, hold_p = sec["hold_starboard"], sec["hold_port"]
    k = 0
    for dr in I["drones"]["carried"]:
        for i in range(dr["count"]):
            hs = hold_s if k % 2 == 0 else hold_p
            yc = 3.1 * (1 if k % 2 == 0 else -1)
            x0 = 14.3 + 1.3 * (k // 2)
            l, w, h = dr["stowed_m"]
            add(f"drone_{k}", f"{dr['name']} {i + 1}", "drones", Box(x0, x0 + w, yc - l / 2 * 0.3, yc + l / 2 * 0.3, -l / 2, l / 2),
                dr["mass_t"], I["drones"]["prov"], "drone", tags=("drone",))
            k += 1
    # --- rev 7: external equipment. Items with a ledger line are located (mass moved from that line's part);
    #     only new hardware ("draw_from": "reserve") is paid from the engineering reserve.
    EQ = I.get("external_equipment")
    if EQ:
        for it in EQ["items"]:
            for k, (x0, x1, a0, a1, r0, r1) in enumerate(equipment_sectors(I, it)):
                m = it["each_t"]
                if it["draw_from"] == "reserve":
                    tags = ("from_reserve", "external")
                else:
                    host = next(q for q in parts if q.id == it["draw_from"])
                    host.mass_t -= m
                    assert host.mass_t > 0, it["id"]
                    tags = ("external", "located")
                add(f"ext_{it['id']}_{k}", it["name"], "external", Sector(x0, x1, r0, r1, a0, a1), m,
                    it.get("prov", EQ["prov"]) + ("" if it["draw_from"] == "reserve" else f"; mass moved from {it['draw_from']}"), it["mat"], tags=tags)
    # --- engineering reserve: spread over the dry parts in proportion to mass
    dry_parts = [p for p in parts if p.dry and "from_reserve" not in p.tags]
    base = sum(p.mass_t for p in dry_parts)
    reserve = L["engineering_reserve_t"] + L["structure_split"].get("released_to_reserve", 0.0)   # v0.5.7: longeron mass released to the reserve
    for p in dry_parts:
        p.mass_t *= 1 + reserve / base
    sec["_holes"] = holes
    return parts, rooms, jacket_parts, jacket_vol, sec


def frange(a, b, s):
    x = a
    while x <= b + 1e-9:
        yield round(x, 6)
        x += s


def fluids(I, sec, jacket_parts, jacket_t, w_service, state):
    """Water parts for one state: shelter jacket, service tank, four C-tank cells (settled aft under thrust)."""
    T = I["tanks"]
    st = I["states"][state]
    g = T["groove"]
    cells = {}
    xm = (T["x_m"][0] + T["x_m"][1]) / 2
    for name in T["cells"]["names"]:
        side = 1 if name.startswith("starboard") else -1
        x0, x1 = (T["x_m"][0], xm) if name.endswith("fore") else (xm, T["x_m"][1])
        cells[name] = CSlot(x0, x1, T["r_in_m"] + 0.02, T["r_out_m"] - 0.02, T["slot_half_width_m"], g["azimuths_deg"], g["width_m"], g["depth_m"], side,
                            holes=sec["_holes"])
    out = []
    jv = sum(sh.volume() for _, sh in jacket_parts)
    for nm, sh in jacket_parts:
        label = ("L3 berth shield ring (8 cm water)" if sh.r1 - sh.r0 < 0.1 else "L3 berth shield collar at the floor edge (12 cm water)") if nm == "berth_ring" else f"Storm-shelter water jacket ({nm})"
        out.append(Part(f"jacket_{nm}", label, "water", sh, jacket_t * sh.volume() / jv,
                        "DERIVED (protected water)", "water", dry=False, tags=("water", "protected") + (("berth_shield",) if nm == "berth_ring" else ())))
    tank = sec["protected_water_tank"]
    if w_service > 0:
        f = w_service / (tank.volume() / (1 + I["protected_water"]["service_tank_ullage_fraction"]))
        out.append(Part("pw_service", "Protected water, service tank", "water", SettledWater(tank, f * (1 / (1 + I["protected_water"]["service_tank_ullage_fraction"]))),
                        w_service, "DERIVED (protected water)", "water", dry=False, tags=("water", "protected")))
    w_ctank_protected = I["canon"]["protected_water_t"] - jacket_t - w_service
    remass = st["remass_t"]
    gross = {n: c.volume() for n, c in cells.items()}
    net_f = 1 - tank_structure(I, sum(gross.values()))["displaced_m3"] / sum(gross.values())
    vol = {n: v * net_f for n, v in gross.items()}
    tot = sum(vol.values())
    iso = st.get("isolated_cell")
    for n, c in cells.items():
        share = vol[n] / tot
        w = (remass + w_ctank_protected) * share
        if n == iso and st.get("vented"):
            continue
        if w <= 1e-6:
            continue
        f = w / vol[n]
        out.append(Part(f"water_{n}", f"Water, tank cell {n.replace('_', ' ')}" + (" (isolated)" if n == iso else ""), "water",
                        SettledWater(c, f), w, "DERIVED", "water", dry=False, tags=("water",) + (("isolated",) if n == iso else ())))
    usable = remass * (1 - (vol[iso] / tot if iso else 0.0))
    return out, cells, usable, w_ctank_protected


def payload_parts(I, sec, state):
    st = I["states"][state]
    out = []
    if st["payload_t"]:
        for k, f in I["payload"]["split"].items():
            out.append(Part(f"payload_{k}", f"Payload in {k.replace('_', ' ')}", "payload", sec[k], st["payload_t"] * f,
                            I["payload"]["prov"], "cargo", dry=False, tags=("payload",)))
    return out


def state_parts(I, parts, sec, jacket_parts, jacket_t, w_service, state):
    st = I["states"][state]
    ps = [p for p in parts if not ("shuttle" in p.tags and st["shuttle"] == "absent")]
    fl, cells, usable, wcp = fluids(I, sec, jacket_parts, jacket_t, w_service, state)
    return ps + fl + payload_parts(I, sec, state), cells, usable, wcp


def hull_surface(I, x):
    """outer radius and outward unit normal (x, radial) of the hull at station x (armour, skin, shield, reactor, nozzle)."""
    H = I["hull"]
    Ro, xa, xb = H["outer_r_m"], H["habitat_shell_x_m"][0], H["habitat_shell_x_m"][0] + H["bow_cap_depth_m"]
    if x < xb:
        u = (xb - x) / (xb - xa)
        rr = Ro * math.sqrt(max(0.0, 1 - u * u))
        nx, nr = -u / (xb - xa), rr / Ro ** 2
        L = math.hypot(nx, nr)
        return rr, nx / L, nr / L
    if x <= H["manifold_x_m"][1]:
        return Ro, 0.0, 1.0
    if x <= H["shield_x_m"][1]:
        return H["shield_r_m"], 0.0, 1.0
    if x <= H["reactor_x_m"][1]:
        return H["reactor_r_m"], 0.0, 1.0
    (n0, n1), (r0, r1) = H["nozzle_x_m"], H["nozzle_r_m"]
    rr = r0 + (r1 - r0) * (x - n0) / (n1 - n0)
    L = math.hypot(r1 - r0, n1 - n0)
    return rr, -(r1 - r0) / L, (n1 - n0) / L


def equipment_sectors(I, it):
    """rev 7: (x0, x1, a0, a1, r0, r1) patches on the hull for one external-equipment item."""
    out = []
    lx, w, h = it["size_m"]
    if "rails" in it:
        for x0, x1, th in it["rails"]:
            rr = hull_surface(I, x0)[0]
            da = math.degrees(0.04 / rr) / 2
            out.append((x0, x1, th - da, th + da, rr, rr + 0.03))
        return out
    pts = it.get("at") or [(x, th) for x in it["grid"]["x_m"] for th in it["grid"]["theta_deg"]]
    for x, th in pts:
        rr = hull_surface(I, x)[0]
        da = math.degrees(w / rr) / 2
        out.append((x - lx / 2, x + lx / 2, th - da, th + da, rr - h + 0.015, rr + 0.015))
    assert len(out) == it["count"], it["id"]
    return out


def node_faces(I, F_other):
    """rev 7 (kT 2026-10-26, Sol AGREE with qualifications): 208 visible metric node faces on the rev 5 longeron-study layout.
    Placement is HOLD (PR #184); each face carries flags for the conflicts the placement check must resolve."""
    NF = I.get("node_faces")
    if not NF:
        return []
    H, R, T = I["hull"], I["radiators"], I["tanks"]
    Lh = H["length_m"]
    g_half = math.degrees(T["groove"]["width_m"] / 2 / H["outer_r_m"])
    doors = [(v["x_m"], v["theta_deg"]) for k, v in I["service"]["sectors"].items() if k.startswith("hold")]
    BD = I["bay"]["doors"] if "doors" in I["bay"] else {}
    out = []
    r_face = NF["face_d_m"] / 2
    for k in range(NF["rings"]):
        x = Lh * (k + 0.5) / NF["rings"]
        rr, nx, nr = hull_surface(I, x)
        for j in range(NF["per_ring"]):
            th = NF["azimuth_phase_deg"] + j * NF["azimuth_step_deg"]
            t = math.radians(th)
            pos = [x, rr * math.cos(t), rr * math.sin(t)]
            nrm = [nx, nr * math.cos(t), nr * math.sin(t)]
            fl = []
            if R["x_m"][0] <= x <= R["x_m"][1] and any(abs((th - a + 180) % 360 - 180) <= g_half for a in R["azimuths_deg"]):
                fl.append("under_stowed_strake")
            if 18.25 <= x <= 32.05 and 57.77 <= th % 360 <= 122.23:
                fl.append("on_bay_door")
            if x > H["manifold_x_m"][1]:
                fl.append("on_torch_chain")
            if nx < -0.1 and x < H["habitat_shell_x_m"][1]:
                fl.append("faces_dust_flow_bow_first")
            for f in F_other:
                d = math.dist(pos, f["pos"])
                rad = f.get("d_m") or max(f.get("size_m", [0.0, 0.0])) / 2 * 2
                if d < r_face + rad / 2 + 0.05:
                    fl.append(f"overlaps_{f['kind']}")
                    break
            out.append({"kind": "node_face", "ring": k, "theta_deg": th, "pos": pos, "normal": nrm, "d_m": NF["face_d_m"], "flags": fl})
    return out


def features(I, rooms):
    """Visual hull features (windows, hatches, hold doors) placed from the room and sector data."""
    F, H = I["features"], I["hull"]
    Ro, xa, xb = H["outer_r_m"], H["habitat_shell_x_m"][0], H["habitat_shell_x_m"][0] + H["bow_cap_depth_m"]
    out = []
    for r in rooms:
        n = r.get("windows", 0)
        if not n:
            continue
        a0, a1 = r["theta_deg"]
        x0, x1 = r["x_m"]
        if r["kind"] == "command":
            xs, ths = [1.25] * n, [45 + 90 * k for k in range(n)]
        else:
            xs, ths = [(x0 + x1) / 2 + 0.2] * n, [a0 + (a1 - a0) * (k + 0.5) / n for k in range(n)]
        for x, th in zip(xs, ths):
            if x < xb:
                u = (xb - x) / (xb - xa)
                rr = Ro * math.sqrt(1 - u * u)
                nx, nr = -u / (xb - xa), rr / Ro ** 2
                L = math.hypot(nx, nr)
                nrm = [nx / L, nr / L * math.cos(math.radians(th)), nr / L * math.sin(math.radians(th))]
            else:
                rr = Ro
                nrm = [0.0, math.cos(math.radians(th)), math.sin(math.radians(th))]
            pos = [x, rr * math.cos(math.radians(th)), rr * math.sin(math.radians(th))]
            out.append({"kind": "window", "room": r["id"], "pos": pos, "normal": nrm, "d_m": F["window_d_m"].get(r["kind"], 0.5)})
    BV = I["habitat"].get("crew_systems", {}).get("berth_viewports")
    if BV:   # v0.5.7: one viewport at the outer end of every berth, acrylic shield plug in the armour bore
        for r in rooms:
            if not r.get("berth_viewports"):
                continue
            for b in r.get("bunks", []):
                th = math.radians(b["angle_deg"])
                for tier in (["lower", "upper"][:b["tiers"]]):
                    x = BV["x_m_by_tier"][tier]
                    out.append({"kind": "window", "room": r["id"], "berth": True, "tier": tier, "pos": [x, Ro * math.cos(th), Ro * math.sin(th)],
                                "normal": [0.0, math.cos(th), math.sin(th)], "d_m": BV["d_m"]})
    for r in rooms:
        if r["kind"] == "airlock":
            th = math.radians(sum(r["theta_deg"]) / 2)
            x = sum(r["x_m"]) / 2
            out.append({"kind": "hatch", "room": r["id"], "pos": [x, Ro * math.cos(th), Ro * math.sin(th)],
                        "normal": [0, math.cos(th), math.sin(th)], "d_m": F["airlock_hatch_d_m"]})
    for cam in I["habitat"].get("crew_systems", {}).get("docking_view", {}).get("cameras", []):
        x, y, z = cam["pos_m"]
        r = math.hypot(y, z) or 1.0
        out.append({"kind": "camera", "name": cam["name"], "pos": [x, y, z], "normal": [0.0, y / r, z / r], "d_m": 0.2})
    for k, v in I["service"]["sectors"].items():
        if k.startswith("hold"):
            th = math.radians(sum(v["theta_deg"]) / 2)
            x = sum(v["x_m"]) / 2
            out.append({"kind": "hold_door", "sector": k, "pos": [x, Ro * math.cos(th), Ro * math.sin(th)],
                        "normal": [0, math.cos(th), math.sin(th)], "size_m": F["hold_door_m"]})
    out += node_faces(I, list(out))
    return out


def plate_beta(ab, nu=0.3, N=199):
    """Simply supported a x b plate (a >= b) under uniform pressure q: sigma_max = beta q b^2 / t^2.
    Navier double series at the centre (Timoshenko and Woinowsky-Krieger); 1.0 -> 0.2874, long -> 0.75 (Roark 11.4 case 1a)."""
    a, b = max(ab, 1.0), 1.0
    mx = my = 0.0
    for m in range(1, N + 1, 2):
        for n in range(1, N + 1, 2):
            k = 16 / (math.pi ** 6 * m * n * (m * m / a ** 2 + n * n / b ** 2) ** 2) * (-1) ** ((m - 1) // 2 + (n - 1) // 2)
            wxx, wyy = k * (m * math.pi / a) ** 2, k * (n * math.pi / b) ** 2
            mx += wxx + nu * wyy
            my += wyy + nu * wxx
    return 6 * max(mx, my)


def tank_structure(I, gross_m3):
    """Size the tank's walls, tie-webs, baffles and bulkheads for the ultimate hydrostatic head plus ullage pressure.
    Returns the panel table, the structural mass needed and the water volume the structure displaces."""
    TS, T, M = I["tank_structure"], I["tanks"], I["materials"]
    sig, rho = M["cfrp_allowable_mpa"] * 1e6, M["cfrp_density_t_m3"]
    ro, ri, hw = T["r_out_m"], T["r_in_m"], T["slot_half_width_m"]
    L = T["x_m"][1] - T["x_m"][0]
    h = L / 2                                          # head of one fore/aft cell along the thrust axis
    p = TS["ultimate_factor"] * (1000 * 9.80665 * TS["design_g"] * h + TS["ullage_mpa"] * 1e6)
    g = T["groove"]
    span_o = 360 - (180 - 2 * math.degrees(math.acos(hw / ro)))
    span_i = 360 - (180 - 2 * math.degrees(math.acos(min(1.0, hw / ri))))
    arc_o, arc_i = math.radians(span_o) * ro, math.radians(span_i) * ri
    zo, zi = math.sqrt(ro ** 2 - hw ** 2), math.sqrt(max(ri ** 2 - hw ** 2, 0.0))
    sill_z = next(it["z_m"] for it in I["longerons"]["items"] if it["kind"] == "tube" and it["z_m"] > 0)
    A_sec = gross_m3 / L
    depth = ro - ri
    sw, bs, mg = TS["web_spacing_outer_m"], TS["baffle_spacing_m"], TS["min_gauge_mm"] / 1000
    of, allow = TS["perforated_open_fraction"], TS["model_wall_allowance_m"]

    def thick(a, b):
        a, b = max(a, b), min(a, b)
        return max(mg, b * math.sqrt(plate_beta(a / b, TS["nu"]) * p / sig)), a / b

    rows = []

    def add(name, area, t, displaced, solid=1.0, note=""):
        rows.append({"item": name, "area_m2": area, "t_mm": t * 1000, "mass_t": area * t * rho * solid, "displaced_m3": displaced, "note": note})

    t, r = thick(bs, sw)
    add("outer wall", arc_o * L + 4 * 2 * g["depth_m"] * L, t, (arc_o * L) * max(0.0, t - allow), note=f"panels {sw} x {bs} m between tie-webs and baffles")
    t, r = thick(bs, sw * ri / ro)
    add("inner wall", arc_i * L, t, arc_i * L * max(0.0, t - allow), note=f"panels {sw * ri / ro:.2f} x {bs} m")
    t, r = thick(bs, max(sill_z - zi, zo - sill_z))
    add("slot walls (2)", 2 * (zo - zi) * L, t, 2 * (zo - zi) * L * t, note=f"supported at the inner corner, the sill longeron and the outer corner; panels {bs} x {max(sill_z - zi, zo - sill_z):.2f} m")
    t, r = thick(depth, sw)
    add("solid bulkheads (fore, mid, aft)", 3 * A_sec, t, 3 * A_sec * t, note=f"panels {sw} x {depth:.2f} m between tie-webs")
    t, r = thick(depth, bs)
    add("keel cell wall", depth * L, t, depth * L * t, note=f"port/starboard cell split; panels {bs} x {depth:.2f} m")
    n_web = int(arc_o / sw)
    t_web = max(mg, p * sw / (sig * (1 - of)))
    add(f"radial tie-webs ({n_web}, perforated)", n_web * depth * L, t_web, n_web * depth * L * t_web * (1 - of), 1 - of,
        note=f"tension {p * sw / 1e6:.2f} MN/m each")
    n_baf = max(0, int(round(L / bs)) - 2)
    t_b = TS["intermediate_baffle_mm"] / 1000
    add(f"ring baffles ({n_baf}, perforated)", n_baf * A_sec, t_b, n_baf * A_sec * t_b * (1 - of), 1 - of)
    mass = sum(r_["mass_t"] for r_ in rows)
    disp = sum(r_["displaced_m3"] for r_ in rows)
    # axial: the aft bulkhead pushes the water's inertia into the walls; check wall stress and panel buckling
    perim = arc_o + arc_i + 2 * (zo - zi)
    wall_area = sum(rr["area_m2"] / L * rr["t_mm"] / 1000 for rr in rows[:3])
    Fax = p * A_sec
    sig_ax = Fax / wall_area
    tmin = min(rows[0]["t_mm"], rows[1]["t_mm"]) / 1000
    E = M["cfrp_e_gpa"] * 1e9
    sig_cr = 4 * math.pi ** 2 * E / (12 * (1 - TS["nu"] ** 2)) * (tmin / sw) ** 2
    return {"ultimate_pressure_mpa": p / 1e6, "panels": rows, "mass_needed_t": mass, "displaced_m3": disp,
            "axial_wall_stress_mpa": sig_ax / 1e6, "panel_buckling_mpa": sig_cr / 1e6, "perimeter_m": perim}


def snames(I):
    return [k for k in I["states"] if k.startswith("S")]


def trim_deg(I, mp, dy=0.0, dz=0.0):
    cg = mp["cg_m"]
    e = math.hypot(cg[1] - dy, cg[2] - dz)
    arm = I["torch"]["thrust_point_x_m"] - cg[0]
    return math.degrees(math.atan2(e, arm)), e


def main():
    raw = INP.read_bytes()
    I = json.loads(raw)
    parts, rooms, jacket_parts, jacket_vol, sec = build(I)
    jacket_t = jacket_vol * 1.0
    tank_cap = sec["protected_water_tank"].volume() / (1 + I["protected_water"]["service_tank_ullage_fraction"])
    w_max = min(tank_cap, I["canon"]["protected_water_t"] - jacket_t)
    # choose the protected-water split and the thrust-line offset that minimise the worst trim angle.
    # Mass properties are linear in the torch-chain offset, so the offset is searched analytically.
    m_chain = sum(p.mass_t for p in parts if "torch_chain" in p.tags)
    TO = I["torch"]["thrust_line_offset"]
    st_ = TO["step_m"]
    ys = [TO["search_y_m"][0] + i * st_ for i in range(int(round((TO["search_y_m"][1] - TO["search_y_m"][0]) / st_)) + 1)]
    zs = [TO["search_z_m"][0] + i * st_ for i in range(int(round((TO["search_z_m"][1] - TO["search_z_m"][0]) / st_)) + 1)]
    cand = []
    wgrid = sorted(set([0.0] + [math.floor(w_max * k / 4 * 100) / 100 for k in range(1, 5)]))
    for w in wgrid:
        mps = {}
        for s in snames(I):
            ps, *_ = state_parts(I, parts, sec, jacket_parts, jacket_t, w, s)
            mps[s] = mass_props(ps)
        for dy in ys:
            for dz in zs:
                worst = 0.0
                for s, mp in mps.items():
                    M = mp["mass_t"]
                    cg = [mp["cg_m"][0], mp["cg_m"][1] + m_chain * dy / M, mp["cg_m"][2] + m_chain * dz / M]
                    worst = max(worst, trim_deg(I, {"cg_m": cg}, dy, dz)[0])
                cand.append((w, worst, dy, dz))
    ok = [c for c in cand if c[1] <= TO["design_target_deg"]]
    best = min(ok, key=lambda c: (round(math.hypot(c[2], c[3]), 3), c[1])) if ok else min(cand, key=lambda c: c[1])
    w_service, _, DY, DZ = best
    parts, rooms, jacket_parts, jacket_vol, sec = build(I, DY, DZ)
    states = {}
    for s in snames(I):
        st = I["states"][s]
        ps, cells, usable, wcp = state_parts(I, parts, sec, jacket_parts, jacket_t, w_service, s)
        mp = mass_props(ps)
        ev, evec = eig_sym3(mp["inertia_kg_m2"])
        t, e = trim_deg(I, mp, DY, DZ)
        states[s] = {**st, **mp, "principal_kg_m2": ev, "principal_axes": evec, "trim_deg": t, "lateral_offset_m": e,
                     "usable_remass_t": usable, "water_t": sum(p.mass_t for p in ps if "water" in p.tags),
                     "parts": [p.id for p in ps]}
    # hot fins deployed (torch burns): same mass, panels unfolded to full span
    HF = I.get("hot_fins")
    fins_out = None
    if HF:
        span_dep = HF["pleat_m"] * HF["pleats"]
        for s in snames(I):
            ps, *_ = state_parts(I, parts, sec, jacket_parts, jacket_t, w_service, s)
            dep = [Part(p.id + "_deployed", p.name.replace("(folded)", "(deployed)"), p.system,
                        Panel(p.shape.x0, p.shape.x1, p.shape.a, p.shape.r0, span_dep, 0.06), p.mass_t, p.prov, p.mat, tags=p.tags)
                   if "fin" in p.tags else p for p in ps]
            mpd = mass_props(dep)
            evd, evecd = eig_sym3(mpd["inertia_kg_m2"])
            states[s]["fins_deployed"] = {"cg_m": mpd["cg_m"], "inertia_kg_m2": mpd["inertia_kg_m2"], "principal_kg_m2": evd,
                                          "principal_axes": evecd, "trim_deg": trim_deg(I, mpd, DY, DZ)[0]}
        fins_out = {"span_m": span_dep, "panels_t": sum(p.mass_t for p in parts if "fin" in p.tags),
                    "total_t": sum(p.mass_t for p in parts if "from_reserve" in p.tags), "temperature_k": HF["temperature_k"],
                    "azimuths_deg": HF["azimuths_deg"], "root_r_m": HF["root_r_m"], "x_m": HF["x_m"]}
    dry = sum(p.mass_t for p in parts if p.dry)
    by_system = {}
    for p in parts:
        by_system[p.system] = by_system.get(p.system, 0.0) + p.mass_t
    ref_parts, cells, _, wcp = state_parts(I, parts, sec, jacket_parts, jacket_t, w_service, "S1")
    tank_gross = sum(c.volume() for c in cells.values())
    ts = tank_structure(I, tank_gross)
    tank_vol = tank_gross - ts["displaced_m3"]

    def pjson(p):
        c, _, n = p.moments()
        return {"id": p.id, "name": p.name, "system": p.system, "mass_t": p.mass_t, "prov": p.prov, "mat": p.mat,
                "dry": p.dry, "tags": sorted(p.tags), "shape": p.shape.spec(), "volume_m3": p.shape.volume(), "centroid_m": c}

    all_water = {}
    for s in snames(I):
        ps, *_ = state_parts(I, parts, sec, jacket_parts, jacket_t, w_service, s)
        all_water[s] = [pjson(p) for p in ps if not p.dry]
    out = {
        "header": "ALL bodies. ALL sponsors. 2026-2226.",
        "status": f"NON-GOVERNING SANDBOX. Wayfarer v{I['version']} geometry and mass properties.",
        "features": features(I, rooms),
        "l1_i4_lock": I.get("habitat",{}).get("decks",[{}])[0].get("command_layout",{}).get("i4_lock"),
        "window_bore": I["features"].get("window_bore"),
        "bands": ([{"x": sg["x_m"], "a": sg["theta_deg"], "mullion_deg": I["habitat"]["crew_systems"]["viewport_band"]["mullion_spacing_deg"]}
                   for sg in I["habitat"]["crew_systems"]["viewport_band"]["segments"]] if I["habitat"].get("crew_systems", {}).get("viewport_band") else []),
        "crown": ({"r": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["r_m"], "mer": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["roots"],
                   "center": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["centre_ring_r_m"], "fork": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["fork_r_m"],
                   "innerR": I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("i4_crown_option_B",{}).get("inner_diameter_m",0)/2,
                   "outerPaneRings": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["panes"].get("ring_boundaries_m"),
                   "outerBandStaggerRad": I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["panes"].get("outermost_band_stagger_rad",0.0),
                   "aoi": I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("adaptive_optogel")}
                  if I["habitat"]["decks"][0].get("command_layout", {}).get("crown_dome", {}).get("adopted") else None),
        "version": I["version"], "inputs_sha256": hashlib.sha256(raw).hexdigest(),
        "length_m": I["hull"]["length_m"], "dry_t": dry,
        "dry_by_system_t": by_system,
        "protected_water": {"jacket_t": jacket_t, "berth_shield_t": sum(sh.volume() for nm, sh in jacket_parts if nm == "berth_ring"),
                            "shelter_jacket_t": sum(sh.volume() for nm, sh in jacket_parts if nm != "berth_ring"), "service_tank_t": w_service, "c_tank_t": I["canon"]["protected_water_t"] - jacket_t - w_service,
                            "service_tank_capacity_t": tank_cap, "chosen_to_minimise_worst_trim_deg": best[1]},
        "thrust_line_offset_m": {"y": DY, "z": DZ, "torch_chain_t": m_chain},
        "hot_fins": fins_out,
        "tank_volume_m3": tank_vol, "tank_volume_gross_m3": tank_gross, "tank_structure": ts,
        "tank_cells_m3": {n: c.volume() for n, c in cells.items()},
        "service_sectors_m3": {k: v.volume() for k, v in sec.items() if not k.startswith("_")},
        "parts": [pjson(p) for p in parts],
        "fluids_by_state": all_water,
        "rooms": rooms,
        "states": states,
    }
    if I.get("skin"):
        nfs = [f for f in out["features"] if f["kind"] == "node_face"]
        fl = {}
        for f in nfs:
            for t in f["flags"]:
                fl[t] = fl.get(t, 0) + 1
        ext = [p for p in parts if "external" in p.tags]
        out["skin"] = I["skin"]
        out["node_faces"] = {"count": len(nfs), "clear": sum(1 for f in nfs if not f["flags"]), "flags": fl, "status": I["node_faces"]["status"]}
        out["external_equipment"] = {"parts": len(ext), "located_t": sum(p.mass_t for p in ext if "located" in p.tags),
                                     "new_from_reserve_t": sum(p.mass_t for p in ext if "from_reserve" in p.tags),
                                     "not_built": I["external_equipment"]["not_built"]}
        out["ledger_reserve_t"] = I["ledger"]["engineering_reserve_t"] + I["ledger"]["structure_split"].get("released_to_reserve", 0.0)
    OUT.mkdir(exist_ok=True)
    txt = json.dumps(out, indent=1, default=float)
    (OUT / "wayfarer_v05_geometry.json").write_text(txt)
    print(f"dry {dry:.1f} t; parts {len(parts)}; rooms {len(rooms)}; tank {tank_vol:.0f} m3; jacket {jacket_t:.1f} t; "
          f"service tank {w_service:.1f} t (cap {tank_cap:.1f}); thrust line offset y {DY:+.2f} z {DZ:+.2f} m; worst trim {best[1]:.3f} deg")
    for s, v in states.items():
        cg = v["cg_m"]
        print(f"  {s} {v['mass_t']:7.1f} t  cg ({cg[0]:6.2f}, {cg[1]:+.3f}, {cg[2]:+.3f})  trim {v['trim_deg']:.3f} deg  "
              f"Ixx {v['inertia_kg_m2'][0][0]:.3e} Iyy {v['inertia_kg_m2'][1][1]:.3e} Izz {v['inertia_kg_m2'][2][2]:.3e}")
    print("sha256", hashlib.sha256(txt.encode()).hexdigest())


def shape_from_spec(s):
    """Rebuild a shape from its JSON spec (used by certify.py and the renderers)."""
    s = dict(s)
    off = s.pop("offset_yz", None)
    f = s.pop("settled_fraction", None)
    k = s.pop("k")
    if k == "sector":
        sh = Sector(s["x0"], s["x1"], s["r0"], s["r1"], s["a0"], s["a1"])
    elif k == "cslot":
        sh = CSlot(s["x0"], s["x1"], s["r0"], s["r1"], s["hw"], s.get("grooves", ()), s.get("gw", 0.0), s.get("gd", 0.0),
                   s.get("side", 0), s.get("holes", ()))
    elif k == "domecyl":
        sh = DomeCyl(s["xa"], s["xb"], s["xc"], s["R"], s["t"], s.get("xs"), s.get("rin", 0.0), s.get("gaps", ()))
    elif k == "frustum":
        sh = Frustum(s["x0"], s["x1"], s["r0"], s["r1"], s["t"])
    elif k == "tube":
        sh = Tube(s["p0"], s["p1"], s["r"])
    elif k == "box":
        sh = Box(s["x0"], s["x1"], s["y0"], s["y1"], s["z0"], s["z1"])
    elif k == "panel":
        sh = Panel(s["x0"], s["x1"], s["a"], s["r0"], s["span"], s["t"])
    else:
        raise ValueError(k)
    if f is not None:
        sh = SettledWater(sh, f)
    if off:
        sh = Offset(sh, off[0], off[1])
    return sh


if __name__ == "__main__":
    main()
