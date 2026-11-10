"""Minimal numpy signed-distance-field modelling kit (mm units)."""
import numpy as np

BIG = 1e3
CHUNK = None  # (lo, hi) of the block being evaluated, for culling
CHUNK_SCALE = 1.0


def length(v):
    return np.sqrt(np.einsum('...i,...i->...', v, v))


def rotm(yaw=0.0, pitch=0.0, roll=0.0):
    """Yaw about z (+ turns +x toward +y), pitch (+ tilts +x up), roll about x (+ raises +y)."""
    y, p, r = np.radians([yaw, pitch, roll])
    Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
    a = -p
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
    return Rz @ Ry @ Rx


def frame_from_axis(axis):
    """Rotation whose local z is `axis`."""
    z = np.asarray(axis, float); z = z / np.linalg.norm(z)
    tmp = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(tmp, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.stack([x, y, z], 1)


def loc(P, t, R=None):
    q = P - np.asarray(t, float)
    if R is not None:
        q = q @ R
    return q


def active(center, radius):
    """Cull test: does a sphere overlap the current block?"""
    if CHUNK is None:
        return True
    lo, hi = CHUNK
    c = np.asarray(center, float)
    d = np.maximum(np.maximum(lo - c, c - hi), 0)
    return float(np.sqrt((d * d).sum())) <= radius


def full(P, v=BIG):
    return np.full(len(P), v, dtype=np.float64)


# ---------------- primitives (on local coords) ----------------
def box(q, half, r=0.0):
    d = np.abs(q) - (np.asarray(half, float) - r)
    return length(np.maximum(d, 0)) + np.minimum(d.max(-1), 0) - r


def ellipsoid(q, rad):
    rad = np.asarray(rad, float)
    k0 = length(q / rad)
    k1 = length(q / rad ** 2)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sphere(q, r):
    return length(q) - r


def capsule(P, a, b, r):
    a = np.asarray(a, float); b = np.asarray(b, float)
    pa = P - a; ba = b - a
    h = np.clip(pa @ ba / (ba @ ba), 0, 1)
    return length(pa - h[:, None] * ba) - r


def roundcone(P, a, b, r1, r2):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = P - a
    y = pa @ ba
    z = y - l2
    x = pa * l2 - y[:, None] * ba
    x2 = (x * x).sum(-1)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    out = np.where(np.sign(y) * a2 * y2 < k, d2, d3)
    out = np.where(np.sign(z) * a2 * z2 > k, d1, out)
    return out


def cyl(q, r, h, rr=0.0):
    """Capped cylinder along local z, radius r, half-height h, edge rounding rr."""
    d0 = length(q[:, :2]) - (r - rr)
    d1 = np.abs(q[:, 2]) - (h - rr)
    d = np.stack([d0, d1], -1)
    return np.minimum(d.max(-1), 0) + length(np.maximum(d, 0)) - rr


def poly2d(p, V):
    V = np.asarray(V, float)
    n = len(V)
    d = ((p - V[0]) ** 2).sum(-1)
    s = np.ones(len(p))
    j = n - 1
    for i in range(n):
        e = V[j] - V[i]
        w = p - V[i]
        b = w - e * np.clip((w @ e) / (e @ e), 0, 1)[:, None]
        d = np.minimum(d, (b * b).sum(-1))
        c1 = p[:, 1] >= V[i, 1]
        c2 = p[:, 1] < V[j, 1]
        c3 = e[0] * w[:, 1] > e[1] * w[:, 0]
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
        j = i
    return s * np.sqrt(d)


def extrude(q, d2, h, r=0.0):
    w0 = d2 + r
    w1 = np.abs(q[:, 2]) - (h - r)
    w = np.stack([w0, w1], -1)
    return np.minimum(w.max(-1), 0) + length(np.maximum(w, 0)) - r


def box2d(p, half):
    d = np.abs(p) - np.asarray(half, float)
    return length(np.maximum(d, 0)) + np.minimum(d.max(-1), 0)


# ---------------- operators ----------------
def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def carve(d, cutter, depth):
    """Cut `cutter` into the body but only within `depth` of the surface."""
    g = np.maximum(cutter, -(d + depth))
    return np.maximum(d, -g)


def hash2(a, b):
    v = np.sin(a * 127.1 + b * 311.7) * 43758.5453
    return v - np.floor(v)


# ---------------- grid evaluation ----------------
def build_grid(f, lo, hi, h, block=48, verbose=True):
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    n = np.ceil((hi - lo) / h).astype(int) + 1
    G = np.empty(n, dtype=np.float32)
    global CHUNK
    tot = int(np.prod(np.ceil(n / block)))
    k = 0
    for i0 in range(0, n[0], block):
        xs = lo[0] + h * np.arange(i0, min(i0 + block, n[0]))
        for j0 in range(0, n[1], block):
            ys = lo[1] + h * np.arange(j0, min(j0 + block, n[1]))
            for k0 in range(0, n[2], block):
                zs = lo[2] + h * np.arange(k0, min(k0 + block, n[2]))
                X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
                P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1)
                CHUNK = (P.min(0) / CHUNK_SCALE, P.max(0) / CHUNK_SCALE)
                v = f(P)
                G[i0:i0 + len(xs), j0:j0 + len(ys), k0:k0 + len(zs)] = v.reshape(X.shape)
                k += 1
        if verbose:
            print(f'  slab {i0}/{n[0]}', flush=True)
    CHUNK = None
    return G
