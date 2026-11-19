"""Book the 16.5 t of node modules + distribution trunk out of the two plant boxes, onto the SELECTED node layout.
NON-CANON booking proposal for Sol. ALL bodies. ALL sponsors. 2026-2226.

Approved direction: kt_decisions relational_plant_layout_2026_11_16 (point 1: 12.5 t of 208 node modules + 4 t trunk leave
the boxes; plant total stays 88 t). Sol stopped the first attempt because the PR #184 13x16 baseline puts nodes on the bay-door
leaves. The selected field (metric_nacelles_ring_selected_2026_11_16, fitted per nacelle_fit_and_aft_rcs_cant_25_2026_11_17)
keeps every hull node off the door leaves (node_optimize.sites excludes x 18-32.3, az 55-125) and carries 68 nodes on the
nacelles and ring. Layout: wayfarer/lab/metric_nodes/nacelle_fit/node_coverage_fit.json (geometric proxy, not PR #356
qualification).

Booking items (ASSUMPTIONS are marked):
  hull node bands  : hull + ring-0 nodes grouped in x bands, booked at their real centroid (not axisymmetric: the door gap
                     leaves no nodes at az 55-125 over x 18-32.3)
  cone ring        : thrust-cone nodes
  nacelle sets     : each nacelle's nodes + the hoop nodes on its two tail arms; moves with the nacelle (tucked/deployed)
  trunk            : 4 t split by route length (ASSUMPTION: Manhattan route along hull frames from the feeding hub)
Hubs (ASSUMPTION): fore = fore plant box rim (x 15.5, r 2) then up to the frames; aft = node drivers in the manifold ring
(x 33.3, r 4.0; approved point 3). Each node is fed from the nearer hub by route length.
Writes plant_node_booking.json."""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, '..', '..')
LAY = json.load(open(os.path.join(HERE, '..', 'metric_nodes', 'nacelle_fit', 'node_coverage_fit.json')))
FIT = json.load(open(os.path.join(W, 'config', 'kt_decisions.json')))['nacelle_fit_and_aft_rcs_cant_25_2026_11_17']
M_DRY = json.load(open(os.path.join(W, 'config', 'mass_basis.json')))['source_dry_t']
N = np.array(LAY['nodes']); NAC, HOOP = LAY['nacelle'], LAY['hoop']
NODES_T, TRUNK_T = 12.5, 4.0; M_NODE = NODES_T / 208
R_TUCK = 4.05; R_FRAME = 4.3; HUB_F = (15.5, 2.0); HUB_A = (33.3, 4.0)
assert len(N) == 208

x, y, z = N.T; r = np.hypot(y, z); az = np.degrees(np.arctan2(z, y)) % 360
def ad(a, b): return abs((a - b + 180) % 360 - 180)
NAZ = [0, 90, 180, 270]
zone = np.array(['hull'] * 208, dtype=object); zone[:16] = 'ring0'
near_nac = np.array([min(NAZ, key=lambda q: ad(a, q)) for a in az])
# zone tags exactly as the optimiser snapped them (same site lists, fitted nacelle/hoop geometry)
import sys; sys.path.insert(0, os.path.join(HERE, '..', 'metric_nodes'))
import node_optimize as NO, node_nacelles as NN, node_ring as NR
from scipy.spatial import cKDTree
NN.NAC.update(LAY['nacelle']); NR.HOOP.update(LAY['hoop'])
S, tag = NO.sites('cone')
for q in NAZ: s_ = NN.nacelle_sites(q); S = np.vstack([S, s_]); tag = np.r_[tag, ['nacelle'] * len(s_)]
s_ = NR.hoop_sites(); S = np.vstack([S, s_]); tag = np.r_[tag, ['hoop'] * len(s_)]
zone[16:] = tag[cKDTree(S).query(N[16:])[1]]
counts = {k: int((zone == k).sum()) for k in ('ring0', 'hull', 'cone', 'nacelle', 'hoop')}
assert counts['nacelle'] == 56 and counts['hoop'] == 12 and counts['cone'] == 20, counts
door = (x >= 18) & (x <= 32.3) & np.array([55 <= a <= 125 for a in az]) & np.isin(zone, ['hull', 'ring0'])
assert not door.any(), 'node on a bay-door leaf'

def route(i):
    """polyline (ship frame) from the feeding hub to node i, DEPLOYED state; returns points and the hub used"""
    xi, ai = x[i], math.radians(az[i]); e = lambda rr, xx, aa=ai: np.array([xx, rr * math.cos(aa), rr * math.sin(aa)])
    if zone[i] in ('nacelle', 'hoop'):
        a0 = math.radians(near_nac[i]); root = 41.0
        pts = [e(HUB_A[1], HUB_A[0], a0), e(3.0, 39.3, a0), e(3.0, root, a0), e(NAC['r_axis'], root, a0)]   # down the cone, out the link
        if zone[i] == 'nacelle': pts += [e(NAC['r_axis'], xi, a0), N[i]]
        else: pts += [e(NAC['r_axis'], HOOP['x'], a0), N[i]]                                              # along nacelle, out the arm
        return np.array(pts), 'aft'
    hub = HUB_F if abs(xi - HUB_F[0]) < abs(xi - HUB_A[0]) else HUB_A
    pts = [e(hub[1], hub[0]), e(R_FRAME, hub[0]), e(R_FRAME, xi)]
    pts.append(N[i] if zone[i] != 'cone' else N[i])
    return np.array(pts), 'fore' if hub is HUB_F else 'aft'

def plen(p):
    seg = np.diff(p, axis=0); L = np.linalg.norm(seg, axis=1)
    # circumferential leg along the frame is implicit in the last segment's chord; add the arc excess (ASSUMPTION)
    return L.sum(), (p[:-1] + p[1:]) / 2, L

lens, mids, hubs = [], [], []
for i in range(208):
    p, h = route(i); L, mid, l = plen(p); L += 1.0                 # +1 m drop at each node (ASSUMPTION)
    lens.append(L); mids.append((mid, l)); hubs.append(h)
lens = np.array(lens); trunk_i = TRUNK_T * lens / lens.sum()

def nac_tucked(p, a0):
    """move a deployed nacelle/hoop node to its tucked position (radial shift on the nacelle; arms fold forward along it)"""
    a = math.radians(a0); er = np.array([0, math.cos(a), math.sin(a)])
    rr = np.hypot(p[1], p[2])
    if abs(p[0] - HOOP['x']) < 0.6 and abs(rr - HOOP['R']) < 0.7:          # hoop node: arc distance from the hinge -> along -x
        s = HOOP['R'] * math.radians(ad(math.degrees(math.atan2(p[2], p[1])), a0))
        return np.array([HOOP['x'] - s, 0, 0]) + (R_TUCK + 0.6 + 0.35) * er
    return p - (NAC['r_axis'] - R_TUCK) * er

items = []
def add(name, idx, kind, move=None):
    idx = np.array(idx); m_n = M_NODE * len(idx); m_t = float(trunk_i[idx].sum())
    pn = N[idx]; c_n = pn.mean(0)
    tw = np.concatenate([mids[i][1] for i in idx]); tp = np.vstack([mids[i][0] for i in idx]); c_t = (tp * tw[:, None]).sum(0) / tw.sum()
    m = m_n + m_t
    cg = (c_n * m_n + c_t * m_t) / m
    it = dict(id=name, kind=kind, nodes=int(len(idx)),
              node_t=round(m_n, 4), trunk_t=round(m_t, 4), total_t=round(m, 4),
              # Authoritative full-precision booking; rounded fields above are display only.
              node_t_exact=float(m_n), trunk_t_exact=m_t, total_t_exact=float(m),
              x_range=[round(float(pn[:, 0].min()), 2), round(float(pn[:, 0].max()), 2)],
              cg_deployed=[round(float(v), 3) for v in cg],
              cg_deployed_exact=[float(v) for v in cg],
              feed={h: int(sum(hubs[i] == h for i in idx)) for h in ('fore', 'aft')})
    if move is not None:
        pt = np.array([nac_tucked(N[i], move) for i in idx]); c_nt = pt.mean(0)
        tucked = (c_nt * m_n + c_t * m_t) / m
        it['cg_tucked'] = [round(float(v), 3) for v in tucked]
        it['cg_tucked_exact'] = [float(v) for v in tucked]
        it['note'] = 'moving mass: books with the nacelle parts; trunk crosses the parallel links and the arm hinges (flex/rotary joints)'
    items.append(it)

hull = np.where(np.isin(zone, ['hull', 'ring0']))[0]
BANDS = [0, 5, 10, 15, 20, 25, 30, 34.4]
for a, b in zip(BANDS[:-1], BANDS[1:]):
    idx = hull[(x[hull] >= a) & (x[hull] < b)]
    if len(idx): add(f'node_band_x{a:g}_{b:g}', idx, 'hull band (fixed)')
add('node_ring_cone', np.where(zone == 'cone')[0], 'thrust-cone ring (fixed)')
for q in NAZ:
    idx = np.where(np.isin(zone, ['nacelle', 'hoop']) & (near_nac == q))[0]
    add(f'node_set_nacelle_{q}', idx, 'nacelle set (moving)', move=q)

tot = sum(it['total_t_exact'] for it in items)
# CG effect of moving 16.5 t out of the boxes (8.25 t from each block, on axis at the block centres)
box_moment = 8.25 * np.array([15.5, 0, 0]) + 8.25 * np.array([33.3, 0, 0])
def moment(state):
    return sum(np.array(it.get('cg_' + state + '_exact', it['cg_deployed_exact'])) * it['total_t_exact'] for it in items)
d_cg = {s: [round(float(v), 4) for v in (moment(s) - box_moment) / M_DRY] for s in ('deployed', 'tucked')}

assert abs(tot - (NODES_T + TRUNK_T)) < 1e-12, tot
assert not door.any()
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.',
           status='NON-CANON booking proposal; layout is a geometric proxy; routing and hubs are ASSUMPTIONS',
           decisions=['relational_plant_layout_2026_11_16', 'metric_nacelles_ring_selected_2026_11_16', 'nacelle_fit_and_aft_rcs_cant_25_2026_11_17'],
           layout='wayfarer/lab/metric_nodes/nacelle_fit/node_coverage_fit.json', counts=counts, node_module_t=round(M_NODE, 5),
           door_leaf_nodes=0, trunk_route_total_m=round(float(lens.sum()), 1), trunk_t_per_m=round(TRUNK_T / float(lens.sum()), 5),
           items=items, total_t=round(tot, 4), total_t_exact=tot,
           plant_blocks_after=dict(plant_fore=44.0 - 8.25, plant_aft=44.0 - 8.25, note='plant total stays 88 t: 71.5 t in the blocks/ring + 16.5 t booked here'),
           dry_cg_shift_m=d_cg, dry_cg_shift_note='[dx aft, dy, dz] of the whole ship vs today; tucked = torch state',
           unchanged=dict(dry_t=M_DRY, plant_total_t=88.0),
           open=['node module volume/mount design on frames', 'trunk flex joints across nacelle links and arm hinges',
                 'aft hub routing through the manifold ring (approved point 3)', 'layout is not PR #356 qualified'])
json.dump(out, open(os.path.join(HERE, 'plant_node_booking.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'items'}, indent=1))
for it in items: print(it['id'], it['nodes'], it['total_t'], it['cg_deployed'], it.get('cg_tucked', ''), it['feed'])
