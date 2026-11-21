"""'Tic Tac' Weave test article (kT 2026-11-22: 'just for fun, particularly if/when we test weave maneuvering'). NON-CANON sketch.
ALL bodies. ALL sponsors. 2026-2226. Does NOT change the selected shuttle (kt_decisions shuttle_final_weave_prototype_2026_11_22).

Premise (DERIVED in this lane): on the Weave field the craft carries its own pocket of air, so hull shape has no aerodynamic role in
field flight. A smooth capsule is the natural pure-field shape. Shape matters only for conventional flight, entry and stowage.
Capsule = cylinder + hemispherical ends. Bay: exit width across the 3.8 m slot (F10) caps the diameter (axisymmetric: rolling does not
help); stowed length 12.8 m (F9, standard - no collar needed). Mass: rough, scaled from the selected shuttle's records (ASSUMPTIONS)."""
import os, json, math
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon
H = os.path.dirname(os.path.abspath(__file__))
D, L = 3.8, 12.8
r = D / 2; Lc = L - D
V = math.pi * r ** 2 * Lc + 4 / 3 * math.pi * r ** 3; A = 2 * math.pi * r * Lc + 4 * math.pi * r ** 2
Vin = math.pi * (r - 0.12) ** 2 * Lc + 4 / 3 * math.pi * (r - 0.12) ** 3
host = json.load(open(os.path.join(H, 'closure_screen.json')))['host_record']; mi = host['mass_items_t']; SWET_HOST = 119.1
mass = dict(hull_structure=mi['hull_structure'] * A / SWET_HOST,                 # ASSUMPTION: same areal structure (Osteon cautious)
            entry_tps=mi['entry_tps'] * (D * L) / 43.8 * 1.5,                     # ASSUMPTION: planform-scaled, x1.5 for all-round capsule entry
            torch=mi['torch'], water_tank=mi['water_tank'], belly_rcs=mi['belly_rcs'], power_dist=mi['power_dist'], custody=mi['custody'], avionics=mi['avionics'],
            cabin=mi['cabin'] + mi['cabin_wall'], skids=0.5, crash_mounts=mi['crash_mounts'], reactor_small=1.5,   # ASSUMPTIONS: skids, 1.5 t reactor to charge the flywheel
            module_installed=9.0, flywheel=1.12)
dry = sum(mass.values())
disp = (dry + 1.1 + 23.1) / 1.025
R_F, D_F = 15.0, 2.0
def F(x): return 0.5 * (np.tanh((x + R_F) / D_F) - np.tanh((x - R_F) / D_F))
def Fp(x): return 0.5 / D_F * (1 / np.cosh((x + R_F) / D_F) ** 2 - 1 / np.cosh((x - R_F) / D_F) ** 2)
rmax = L / 2
diff_axial = 1 - (F(rmax) + 0 * Fp(rmax))                                        # tip on the motion axis: rho = 0
diff_trans = 1 - (F(rmax) + rmax ** 2 * Fp(rmax) / (2 * rmax))                   # tip broadside to the motion
out = dict(doc=__doc__, diameter_m=D, length_m=L, hull_m3=round(V, 1), interior_m3=round(Vin, 1), surface_m2=round(A, 1), dry_t_rough=round(dry, 1),
           mass_items_t={k: round(v, 2) for k, v in mass.items()}, floats_needed=disp * 1.5 > V and 'yes' or 'no (hull alone gives >2x reserve)',
           displaced_m3_full=round(disp, 1), field_max_radius_m=rmax, differential_axial=float(diff_axial), differential_transverse=float(diff_trans),
           differential_g_at_71g=round(71 * max(diff_axial, diff_trans), 3), bay=dict(exit_width_m=D, limit=3.8, radius_m=r, limit_r=2.15, length_m=L, limit_len=12.8),
           gives_up=['wings and fans: no conventional aerodynamic fallback (field failure = torch or ballistic + flotation)', 'lifting entry: capsule L/D ~0.3 at best, little crossrange, more TPS',
                     'not a replacement for the selected shuttle: a Weave manoeuvring test bed / demonstrator'],
           gains=['~2x the interior of the shuttle hull (test instrumentation, ballast, crew stations)', 'smallest field radius (6.4 m vs 8.55 m): cleanest carriage',
                  'floats on its own; no appendages to stow; fits the bay with standard margins (no collar)', 'the shape people expect'])
json.dump(out, open(os.path.join(H, 'tictac_test_article.json'), 'w'), indent=1)
# ---------------- picture: top views inside the field
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; CU = '#0e7490'
plt.rcParams.update({'font.size': 9.5})
f, ax = plt.subplots(1, 2, figsize=(12, 6)); f.suptitle("Weave test article 'Tic Tac' vs the selected shuttle, inside the R 15 m field (top view, NON-CANON sketch)", color=INK, fontsize=11.5)
import sys; sys.path.insert(0, os.path.join(H, '..', 'explorer')); import engine as E
cfg = json.load(open(os.path.join(H, 'closure_screen.json')))['config']; K = E.keys(cfg); xs = np.linspace(0, float(K[-1, 0]), 60)
half = np.array([E.section(K, x, cfg['keel'])[2][0] for x in xs])
for a, ttl in zip(ax, ('Selected shuttle: 13.0 m lifting body, 17 m wing', "'Tic Tac' test article: 12.8 m x 3.8 m capsule")):
    a.add_patch(Circle((0, 0), 15, fc='#eff6ff', ec=SH, lw=1.2, ls='--')); a.add_patch(Circle((0, 0), 10, fc='#dbeafe', ec=SH, lw=0.8, ls=':'))
    a.text(0, 13.2, 'field R 15 m', ha='center', color=SH, fontsize=8.5); a.text(0, 8.6, 'clean zone 10 m', ha='center', color=SH, fontsize=8)
    a.set_xlim(-16, 16); a.set_ylim(-16, 16); a.set_aspect('equal'); a.axis('off'); a.set_title(ttl, color=INK, fontsize=10.5, loc='left')
xc = 6.4
P = np.r_[np.c_[xs - xc, half], np.c_[xs[::-1] - xc, -half[::-1]]]; ax[0].add_patch(Polygon(P, fc='#cbd5e1', ec=INK, lw=1))
for s in (-1, 1): ax[0].add_patch(Rectangle((5.5 - xc, s * 2.13 if s > 0 else -8.5), 1.8, 8.5 - 2.13, fc='#94a3b8', ec=INK, lw=0.8))
ax[0].text(0, -12.5, 'max radius 8.55 m (wing tips)', ha='center', color=INK, fontsize=9)
ax[1].add_patch(FancyBboxPatch((-L / 2 + r, -r), L - D, D, boxstyle=f'round,pad=0,rounding_size={r}', fc='#f8fafc', ec=INK, lw=1.2, mutation_aspect=1))
ax[1].add_patch(Circle((-L / 2 + r, 0), r, fc='#f8fafc', ec=INK, lw=1.2)); ax[1].add_patch(Circle((L / 2 - r, 0), r, fc='#f8fafc', ec=INK, lw=1.2)); ax[1].add_patch(Rectangle((-L / 2 + r, -r), L - D, D, fc='#f8fafc', ec='none'))
ax[1].plot([-L / 2 + r, L / 2 - r], [r, r], color=INK, lw=1.2); ax[1].plot([-L / 2 + r, L / 2 - r], [-r, -r], color=INK, lw=1.2)
ax[1].text(0, -12.5, f"max radius {rmax:.1f} m · interior ~{Vin:.0f} m³ · ~{dry:.0f} t dry (rough)", ha='center', color=INK, fontsize=9)
f.text(0.02, 0.02, "On the field the craft carries its own air, so shape plays no aerodynamic role in field flight. The capsule gives up wings, fans and lifting entry (no conventional fallback): a manoeuvring test bed, not a replacement.", color=MUT, fontsize=8.5)
f.savefig(os.path.join(H, 'weave_tictac_test_article.png'), dpi=150, bbox_inches='tight')
print(json.dumps({k: v for k, v in out.items() if k not in ('doc', 'mass_items_t')}, indent=1))
