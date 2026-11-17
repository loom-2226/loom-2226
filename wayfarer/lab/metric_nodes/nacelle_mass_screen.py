"""Four nacelles + aft ring: ROM mass screen against the free reserve.
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226.
Every range below is an ASSUMPTION (Claude, for kT). Independent uniform
sampling of each range, the same method as the B4 shuttle screen.
Reads the live reserve from wayfarer/config/mass_basis.json and node counts
from node_ring.json; writes nacelle_mass_screen.json."""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, '..', '..', 'config')
MB = json.load(open(os.path.join(CFG, 'mass_basis.json')))
RING = json.load(open(os.path.join(HERE, 'node_ring.json')))
NAC, HOOP = RING['nacelle'], RING['hoop']
ZONES = RING['options']['four_nacelles_ring']['metrics']['count_by_zone']

ARM_L = 2 * math.pi * HOOP['R'] / 8             # ~3.5 m, an eighth of the hoop
ARM_A = 2 * math.pi * 0.2 * ARM_L               # tube r 0.2 m

def per_nacelle(L):
    """per-nacelle items [lo, hi] t, reason, and whether the item scales with nacelle length"""
    A = 2 * math.pi * NAC['radius'] * L
    return {
     'shell': ([A * 6e-3, A * 12e-3], f'{A:.1f} m2 composite shell at 6-12 kg/m2 (stowed under ~1 g torch, up to 7.5 g strake limit)'),
     'frames_rails_trunk_tray': ([0.12 * L / 14, 0.25 * L / 14], 'ring frames, node rails, trunk cable tray (scaled with length from 0.12-0.25 t at 14 m)'),
     'thermal_shroud': ([A * 2e-3, A * 5e-3], 'refractory outer + MLI: tucked 0.7 m from the nozzle exit and between 1,750 K fins during burns'),
     'parallel_links_actuators': ([0.20, 0.45], 'two link pairs, drives, locks, root fittings on torch structure (not scaled)'),
     'tail_arms': ([2 * ARM_A * 6e-3, 2 * ARM_A * 12e-3], f'two {ARM_L:.2f} m arc tubes r 0.2 m, 6-12 kg/m2'),
     'arm_hinges_latches': ([0.06, 0.15], 'two 90 deg arm hinges, tip latch pair, alignment cones'),
     'hard_points': ([0.08, 0.20], 'backing structure into the shield/reactor ring frames'),
    }
N_NAC = 4
GROWTH = [1.00, 1.20]                           # immature design growth on the hardware

# Credits and shared-component offsets: ZERO until a specific booked component is shown to shrink (Sol review of PR #556).
# The 1.1 t node_mount_allowance books 20 mounts + hatches on five midship rings (x 14-34.3); the nodes that move
# to the nacelles and hoop come from the aft/cone region, so no booked mount is shown to disappear.
CREDITS = {
 'node_mount_allowance': (0.0, 'UNVERIFIED: books 20 midship mounts; none shown to disappear'),
 'plant_trunk_4t': (0.0, 'UNVERIFIED: trunk redistribution is HELD'),
 'node_housings': (0.0, 'UNVERIFIED: no booked housing mass identified'),
 'hotfin_root_truss_hard_points': (0.0, 'UNVERIFIED: shared hard points not shown'),
}

FREE = MB['free_buffer_above_floor_t']          # above the 16.8 t combined floor (floor NOT to be lowered)
FLOOR = MB['combined_uncommitted_floor_t']
UNCOMMITTED = MB['combined_uncommitted_t']

def screen(L, seed=2026, N=200000):
    rng = np.random.default_rng(seed); PER = per_nacelle(L); hw = np.zeros(N); parts = {}
    for k, ((lo, hi), _) in PER.items():
        x = N_NAC * rng.uniform(lo, hi, N); parts[k] = x; hw += x
    need = hw * rng.uniform(*GROWTH, N); net = need - sum(v for v, _ in CREDITS.values())
    return PER, parts, need, net, net - FREE

pc = lambda a: {p: round(float(np.percentile(a, q)), 2) for p, q in (('p5', 5), ('mid', 50), ('p95', 95))}
variants = {}
for name, L in (('nacelle_14m', 14.0), ('nacelle_10m', 10.0)):
    PER, parts, need, net, gap = screen(L)
    variants[name] = dict(length_m=L, assumptions={k: v[1] for k, v in PER.items()},
        hardware_mid_t={k: round(float(np.median(v)), 3) for k, v in parts.items()},
        need_t=pc(need), net_t=pc(net), gap_vs_free_t=pc(gap), fits_in_free_fraction=round(float((gap <= 0).mean()), 3))
cov = json.load(open(os.path.join(HERE, 'node_ring_length.json')))['variants']
for k in variants: variants[k]['coverage'] = {m: cov[k]['metrics'][m] for m in ('max_gap_m', 'p95_gap_m', 'load_cv', 'reach_cover', 'web_pieces', 'count_by_zone', 'aft_quadrant_counts')}
out = dict(
 header='ALL bodies. ALL sponsors. 2026-2226.',
 status='NON-CANON research screen; all ranges are ASSUMPTIONS; coverage is a geometric proxy, not PR #356 qualification',
 decision='metric_nacelles_ring_selected_2026_11_16',
 samples=200000, seed=2026,
 basis=dict(dry_t=MB['source_dry_t'], combined_uncommitted_t=round(UNCOMMITTED, 3), combined_floor_t=FLOOR,
            free_above_floor_t=round(FREE, 3), floor_policy='16.8 t floor is NOT lowered', note='dry mass is fixed: anything added must come from the free reserve or a verified offset'),
 growth=f'x{GROWTH[0]}-{GROWTH[1]} on hardware',
 credits={k: dict(t=v, why=w) for k, (v, w) in CREDITS.items()},
 variants=variants,
 saving_10m_vs_14m_mid_t=round(variants['nacelle_14m']['need_t']['mid'] - variants['nacelle_10m']['need_t']['mid'], 2),
 review='Sol review of PR #556 (2026-11-16): mount credit not verified -> 0; no speculative credits; floor not lowered',
)
json.dump(out, open(os.path.join(HERE, 'nacelle_mass_screen.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('variants',)}, indent=1))
for k, v in variants.items(): print(k, v['need_t'], v['gap_vs_free_t'], v['coverage'])
