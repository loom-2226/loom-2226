"""Experiment 2, W1: does programmable structure beat conventional mechanisms? NON-CANON prototype lane.
ALL bodies. ALL sponsors. 2026-2226.
Reference: #2643 + Osteon cautious (+ programmable for W1), 17 m span, 1.8 m chord, 18 t tank (38.38 t dry, W1 lane 2026-11-21).
Labels: GEOMETRY = direct from the explorer loft; MODEL = explorer ROM; ASSUMPTION = stated coefficient; REQUIRED = what a hypothesis must achieve."""
import sys, os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(H, '..', '..', 'explorer', 'explorer_results.json'))); G2643 = {r['id']: r for r in D['results']}[2643]['params']
G = 9.81
# extra sensitivity wildcards for this experiment only (not added to the explorer)
E.WILDCARDS['fold'] = dict(wing_factor=1.2, note='ASSUMPTION: conventional two-hinge fold-over-top wing, +20% wing mass for hinges/locks/actuators')
E.WILDCARDS['tele2'] = dict(wing_factor=1.6, note='ASSUMPTION: two-stage telescoping wing needed above ~13.7 m (6.4 m panels exceed hull width), +60%')
E.WILDCARDS['camber'] = dict(cl_cap=5.0, cl_slope=3.25, note='programmable camber credit only (CL cap 5) [sensitivity]')
E.WILDCARDS['prog_geom'] = dict(wing_factor=1.5, note='programmable flat-stow skin, 1.5x wing mass, no camber credit')

def run(p):
    r = E.evaluate(p); ms = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
    td = lambda k: next((c['value'] for c in ms[k]['checks'] if 'touchdown' in c['name']), None)
    return dict(dry_t=r['dry_t'], wing_t=r['mass_t']['wings'], clmax=r['land']['clmax'], S=r['land']['S'], glide=r['glide_LD'], turn=r['max_turn_dps'],
                evac_td=td('evac'), hot_td=td('hot'), hot_headroom=round(50 - td('hot'), 1), all_five=all(m['ok'] for m in ms.values()),
                failing=[k for k, m in ms.items() if not m['ok']], interior_margin_m3=r['interior_margin_m3'])
ref = dict(G2643, water_t=18.0)
variants = {
 'A conventional telescoping 13.7 m (#2643 + Osteon)': dict(ref, wildcard='osteon_cautious'),
 'B conventional fold-over-top 17 m': dict(ref, wildcard='osteon_cautious+fold', span=17.0, chord=1.8),
 'C conventional two-stage telescope 17 m': dict(ref, wildcard='osteon_cautious+tele2', span=17.0, chord=1.8),
 'D programmable geometry only 17 m (flat stow, no camber)': dict(ref, wildcard='osteon_cautious+prog_geom', span=17.0, chord=1.8),
 'E fold 17 m + programmable camber (adaptive trailing structure)': dict(ref, wildcard='osteon_cautious+fold+camber', span=17.0, chord=1.8),
 'F full W1: programmable geometry + camber 17 m (lane reference)': dict(ref, wildcard='osteon_cautious+programmable', span=17.0, chord=1.8),
 'G telescoping 13.7 m + programmable camber only': dict(ref, wildcard='osteon_cautious+camber'),
}
res = {k: run(p) for k, p in variants.items()}

# ---------------------------------------------------------------- GEOMETRY: free band above / below the hull inside the bay envelope
p = variants['F full W1: programmable geometry + camber 17 m (lane reference)']; V, F, K, _, _ = E.loft(p)
def band(x, zc, width=1.8):
    S = E.section(K, x, p['keel']); ys = np.linspace(-width / 2, width / 2, 19)
    top = np.interp(np.abs(ys), [0, S[1][0], S[2][0]], [S[0][1], S[1][1], S[2][1]])
    bot = np.interp(np.abs(ys), [0, S[3][0], S[2][0]], [S[4][1], S[3][1], S[2][1]])
    circ = np.sqrt(np.maximum(E.R_ENV ** 2 - ys ** 2, 0))
    return float(np.min(zc + circ - top)), float(np.min(bot - (zc - circ)))
# admissible bay-centre heights: chine and every section point inside R_ENV
xs = np.linspace(0.6, 12.8, 62); best = None
for zc in np.linspace(-0.6, 0.6, 121):
    ok = all(np.hypot(E.section(K, x, p['keel'])[:, 0], E.section(K, x, p['keel'])[:, 1] - zc).max() <= E.R_ENV + 1e-3 for x in xs)
    if ok:
        gt = min(band(x, zc)[0] for x in np.linspace(5.0, 12.4, 30)); gb = min(band(x, zc)[1] for x in np.linspace(5.0, 12.4, 30))
        if best is None or gt > best[1]: best = (round(zc, 3), round(gt, 3), round(gb, 3))
panel_len = (17.0 - 4.26) / 2; t_panel = 0.12 * 1.8
fold = dict(bay_envelope_r_m=E.R_ENV, centre_z_m=best[0], top_band_clear_m=best[1], belly_band_clear_m_at_same_centre=best[2], band_width_m=1.8, band_x_m='5.0-12.4',
            outer_panel_m=round(panel_len, 2), panel_thickness_m=round(t_panel, 3), two_panels_stacked_with_hinge_gaps_m=round(2 * t_panel + 0.1, 2),
            fits_top=bool(2 * t_panel + 0.1 <= best[1]), telescope_17m_single_stage=bool(panel_len <= 4.26),
            telescoped_13p7m_box_volume_m3=round(2 * (13.739 - 4.26) / 2 * 1.563 * 0.12 * 1.563 * 0.8, 2),
            verdict='GEOMETRY: a conventional fold-over-top 17 m wing fits the 2.15 m envelope with margin; programmable flat-stow is NOT required for span. '
                    'Unchecked: fans, pop-out floats and cradle/rails sharing the top band; G8 exit clearance; hinge fittings at the chine.')

# ---------------------------------------------------------------- REQUIRED: lock strength for a laminate that stows flat and locks into a box
m_heavy = res['F full W1: programmable geometry + camber 17 m (lane reference)']['dry_t'] + 2.6 + 18.0   # dry + payload + full tank
S = res['F full W1: programmable geometry + camber 17 m (lane reference)']['S']; Sw = (17.0 - 4.26) * 1.8
L_side = 8.0 * m_heavy * 1e3 * G * (Sw / S) / 2                     # limit load, wing share by area [ASSUMPTION: area share]
b = panel_len; M_root = L_side * 4 * b / (3 * math.pi)                # elliptic-ish spanwise centroid
h_box = 0.8 * t_panel; F_cap = M_root / h_box
lock = {}
for wj in (0.02, 0.05, 0.10):
    lock[f'{int(wj*1000)} mm lock lands'] = round(L_side * 1.5 / (2 * h_box * wj) / 1e6, 1)   # ultimate 1.5x, two webs, MPa
jam = dict(vacuum_jamming_MPa=0.05, electroadhesion_MPa=0.02, structural_adhesive_MPa=30, titanium_pin_or_tooth_MPa=500)
stiff = dict(limit_load_g=8.0, heavy_mass_t=round(m_heavy, 1), wing_area_share=round(Sw / S, 3), lift_per_side_MN=round(L_side / 1e6, 2), root_moment_MNm=round(M_root / 1e6, 2),
             box_depth_m=round(h_box, 3), cap_force_MN=round(F_cap / 1e6, 1), cap_area_cm2_Ti_900MPa_x1p5=round(F_cap * 1.5 / 900e6 * 1e4),
             REQUIRED_lock_shear_MPa=lock, known_reversible_locks_MPa=jam,
             finding='Friction/vacuum jamming is ~400x short of an 8 g wing. A flat-stow wing needs a mechanical interlock (teeth, zipper, bistable shell) '
                     'or a reversible structural bond of >=20-100 MPa. Torsion needs a CLOSED cell: an unlocked web leaves an open section with roughly 1% of the torsional stiffness, '
                     'so lock integrity is flight-critical (flutter/divergence) and must be monitored.')

# ---------------------------------------------------------------- MODEL (simple): water-slam and crash loads, rigid vs adaptive stroke
slam = []
for w in (3.0, 5.0, 7.0):                                             # vertical sink relative to waves at touchdown [ASSUMPTION range]
    slam.append(dict(sink_ms=w, rigid_local_stroke_0p05m_g=round(w * w / (2 * 0.05) / G, 1), adaptive_0p15m_g=round(w * w / (2 * 0.15) / G, 1),
                     adaptive_0p30m_g=round(w * w / (2 * 0.30) / G, 1)))
crash = dict(rule='crash 16-20 g (kT 2026-11-21)', stroke_for_16g_at_15ms_m=round(15 ** 2 / (2 * 16 * G), 2), stroke_for_16g_at_20ms_m=round(20 ** 2 / (2 * 16 * G), 2),
             note='energy absorbed per crash at 60 t, 15 m/s: %.1f MJ; a one-shot crushable must be replaced; a re-armable programmable absorber is the advantage' % (0.5 * 60e3 * 225 / 1e6))
actuation = dict(strain_energy_bound_MJ=round(0.5 * (900e6) ** 2 / 110e9 * (res['F full W1: programmable geometry + camber 17 m (lane reference)']['wing_t'] / 4.5) / 1e6, 2),
                 note='upper bound: whole wing taken to Ti yield strain energy; actual reconfiguration energy ~0.1-1 MJ, ~0.1 MW for 10 s, trivially within the 29 MWe fan reactor. '
                      'Mass, not energy, is the actuator question: the ROM already charges +50% wing mass (1.5x) vs +20% for a conventional fold.')
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) experiment 2, W1', model_version=E.MODEL_VERSION,
           osteon_vs_programmable=dict(osteon_ESTABLISHED='OST-22 titanium: 22-38% lighter on longerons/end fittings/doublers (Wayfarer mass basis, 13 items). A static, stronger structural metal. No shape or stiffness switching is evidenced.',
                                       programmable_PROPOSED='reversible geometry or stiffness: NOT evidenced anywhere in the repo; extrapolated from the existence of Builder materials'),
           variants=res, bay_fold=fold, stiffness=stiff, slam_g=slam, crash=crash, actuation=actuation)
json.dump(out, open(os.path.join(H, 'exp2_w1.json'), 'w'), indent=1)
if __name__ == '__main__':
    for k, v in res.items(): print(f"{k:70s} dry {v['dry_t']:5.2f} wing {v['wing_t']:4.2f} CL {v['clmax']:.2f} evac {v['evac_td']} hot {v['hot_td']} all5 {v['all_five']} {v['failing']}")
    print(fold); print(stiff); print(slam); print(crash); print(actuation)
