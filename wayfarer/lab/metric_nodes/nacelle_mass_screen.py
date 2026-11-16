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

L = NAC['x1'] - NAC['x0']                       # 14 m
SHELL_A = 2 * math.pi * NAC['radius'] * L       # 52.8 m2 per nacelle
ARM_L = 2 * math.pi * HOOP['R'] / 8             # ~3.5 m, an eighth of the hoop
ARM_A = 2 * math.pi * 0.2 * ARM_L               # tube r 0.2 m

# per-nacelle items [lo, hi] t, with the reason
PER = {
 'shell': ([SHELL_A * 6e-3, SHELL_A * 12e-3], f'{SHELL_A:.1f} m2 composite shell at 6-12 kg/m2 (stowed under ~1 g torch, up to 7.5 g strake limit)'),
 'frames_rails_trunk_tray': ([0.12, 0.25], 'ring frames, node rails for ~13 nodes, trunk cable tray'),
 'thermal_shroud': ([SHELL_A * 2e-3, SHELL_A * 5e-3], 'refractory outer + MLI: tucked 0.7 m from the nozzle exit and between 1,750 K fins during burns'),
 'parallel_links_actuators': ([0.20, 0.45], 'two link pairs, drives, locks, root fittings on torch structure'),
 'tail_arms': ([2 * ARM_A * 6e-3, 2 * ARM_A * 12e-3], f'two {ARM_L:.2f} m arc tubes r 0.2 m, 6-12 kg/m2'),
 'arm_hinges_latches': ([0.06, 0.15], 'two 90 deg arm hinges, tip latch pair, alignment cones'),
 'hard_points': ([0.08, 0.20], 'backing structure into the shield/reactor ring frames'),
}
N_NAC = 4
GROWTH = [1.00, 1.20]                           # immature design growth on the hardware

# credits: nodes riding on nacelles/hoop no longer need hull mounts
moved = ZONES['nacelle'] + ZONES['hoop']
mount_allow = 1.1                               # mass_basis node_mount_allowance, physically allocated t
CREDIT = {'hull_mount_share': ([mount_allow * moved / 208 * 0.75, mount_allow * moved / 208],
                               f'{moved} of 208 nodes leave the hull: their share of the 1.1 t mount allowance (75-100%)')}

FREE = MB['free_buffer_above_floor_t']          # above the 16.8 t combined floor
FLOOR = MB['combined_uncommitted_floor_t']
UNCOMMITTED = MB['combined_uncommitted_t']

rng = np.random.default_rng(2026); N = 200000
hw = np.zeros(N); parts = {}
for k, ((lo, hi), _) in PER.items():
    x = N_NAC * rng.uniform(lo, hi, N); parts[k] = x; hw += x
g = rng.uniform(*GROWTH, N); need = hw * g
cred = np.zeros(N)
for k, ((lo, hi), _) in CREDIT.items():
    cred += rng.uniform(lo, hi, N)
net = need - cred
gap = net - FREE

pc = lambda a: {p: round(float(np.percentile(a, q)), 2) for p, q in (('p5', 5), ('mid', 50), ('p95', 95))}
out = dict(
 header='ALL bodies. ALL sponsors. 2026-2226.',
 status='NON-CANON research screen; all ranges are ASSUMPTIONS',
 decision='metric_nacelles_ring_selected_2026_11_16',
 samples=N, seed=2026,
 basis=dict(dry_t=MB['source_dry_t'], combined_uncommitted_t=round(UNCOMMITTED, 3), combined_floor_t=FLOOR,
            free_above_floor_t=round(FREE, 3), note='dry mass is fixed: anything added must come from the uncommitted reserve or an offset'),
 assumptions={k: v[1] for k, v in PER.items()} | {'growth': f'x{GROWTH[0]}-{GROWTH[1]} on hardware'} | {k: v[1] for k, v in CREDIT.items()},
 hardware_mid_t={k: round(float(np.median(v)), 3) for k, v in parts.items()},
 need_t=pc(need), credit_t=pc(cred), net_t=pc(net), gap_vs_free_t=pc(gap),
 fits_in_free_fraction=round(float((gap <= 0).mean()), 3),
 combined_after_mid_t=round(UNCOMMITTED - float(np.median(net)), 2),
)
json.dump(out, open(os.path.join(HERE, 'nacelle_mass_screen.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
