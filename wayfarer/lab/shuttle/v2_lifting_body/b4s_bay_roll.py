"""B4-S in Wayfarer's bay: as built vs rolled 90 deg about its long axis (Sol G8 STOP, 2026-11-19). End view looking forward.
NON-CANON. ALL bodies. ALL sponsors. 2026-2226. Exit path: the shuttle rises +Z through the 4.8 m slot; G8 needs 0.5 m each side."""
import os, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import build_b4s as S
HERE = os.path.dirname(os.path.abspath(__file__))
I = json.load(open(os.path.join(HERE, '..', '..', '..', 'config', 'wayfarer_v05_inputs.json')))
SL = I['bay']['slot_half_width_m']; BORE = I['bay']['bore_r_m']
lon = [it for it in I['longerons']['items'] if it['kind'] == 'tube' and it['z_m'] > 0]
INK, MUTE, BG, RED, GREEN = '#0b0b0b', '#52514e', '#fcfcfb', '#c8432f', '#1baf7a'
out = {}
fig, axs = plt.subplots(1, 2, figsize=(10, 6.2), dpi=150); fig.patch.set_facecolor(BG)
fig.text(.04, .95, 'Getting B4-S out of the bay: roll it on its side', fontsize=14, weight='bold')
fig.text(.04, .915, 'End view, looking forward. It leaves by rising +Z through the slot; G8 needs 0.5 m clear each side. NON-CANON check.', fontsize=9.5, color=MUTE)
for ax, (title, roll) in zip(axs, (('As built (wings level)', False), ('Rolled 90° (starboard up)', True))):
    ax.set_facecolor(BG)
    ax.add_patch(Circle((0, 0), BORE, fc='#eef0f3', ec=MUTE, lw=1.2))
    for s in (-1, 1): ax.plot([s * SL, s * SL], [0, 5.2], color=INK, lw=2.2)
    ax.text(0, 5.0, 'slot 4.8 m', ha='center', fontsize=9, color=MUTE)
    for it in lon: ax.add_patch(Circle((it['y_m'], it['z_m']), it['d_m'] / 2, fc='#555', ec='none'))
    worst = 9
    for st, col, ls in (('flight', '#2a78d6', '-'), ('venus', '#d99a1e', '--')):
        P = S.shuttle(st); V = np.vstack([P[k][0] for k in P]); yz = V[:, 1:3]
        if roll: yz = np.c_[-yz[:, 1], yz[:, 0]]            # +90 deg roll: starboard (+y) to +Z
        from scipy.spatial import ConvexHull
        h = ConvexHull(yz); ax.add_patch(Polygon(yz[h.vertices], fc=col if ls == '-' else 'none', alpha=.55 if ls == '-' else 1, ec=col, lw=1.4, ls=ls))
        hw = float(np.abs(yz[:, 0]).max()); cl = SL - hw; worst = min(worst, cl); out[f"{'rolled' if roll else 'level'}_{st}"] = dict(half_width_m=round(hw, 3), slot_clearance_m=round(cl, 3),
            longeron_clearance_m=round(min(abs(it['y_m']) - it['d_m'] / 2 for it in lon) - hw, 3))
        for sgn in (-1, 1): ax.plot([sgn * hw] * 2, [-.3, 4.3], color=col, lw=.8, ls=':')
    ax.text(0, -2.85, f"slot clearance {worst:.2f} m " + ('✓' if worst >= .5 else '✗ (needs 0.5)'), ha='center', fontsize=10.5, weight='bold', color=GREEN if worst >= .5 else RED)
    ax.set_title(title, fontsize=11.5, weight='bold'); ax.set_xlim(-3.2, 3.2); ax.set_ylim(-3.1, 5.4); ax.set_aspect('equal'); ax.axis('off')
fig.text(.04, .04, 'Blue = standard shuttle; dashed gold = with the Venus kit fairing. Dark dots: the upper longerons. The nose port stays on the bay axis, so docking is unchanged.', fontsize=8.8)
fig.savefig(os.path.join(HERE, 'b4s_bay_roll.png'), facecolor=BG)
json.dump(out, open(os.path.join(HERE, 'b4s_bay_roll.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
