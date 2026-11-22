"""Builder Tic Tac rulebook: what each rule rests on. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, textwrap, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'builder_rulebook.json')))
COL = {'LANE': ('#dbeafe', '#1d4ed8', 'DERIVED (lane)'), 'LEDGER': ('#dcfce7', '#15803d', 'DERIVED (ledger)'), 'CANON + POSTULATE': ('#fef3c7', '#b45309', 'CANON + POSTULATE'),
       'LEDGER + POSTULATE': ('#ecfccb', '#4d7c0f', 'DERIVED + POSTULATE'), 'POSTULATE (RT-inspired)': ('#fae8ff', '#86198f', 'POSTULATE (RT-inspired)'),
       'CANON + RT': ('#e0e7ff', '#3730a3', 'CANON + RT'), 'OPEN (narrative)': ('#f1f5f9', '#475569', 'OPEN')}
rules = D['rules']; n = len(rules)
f, ax = plt.subplots(figsize=(13, 12)); ax.set_xlim(0, 13); ax.set_ylim(-1.0, n + 2.2); ax.axis('off')
ax.text(0.15, n + 1.75, 'Builder Tic Tac rulebook: what each rule rests on', fontsize=15, color='#0f172a')
ax.text(0.15, n + 1.3, 'Fiction-first, NON-CANON. Three postulates: P1 hull = Loom boundary · P2 record frame = force-dominant body · P3 bounded relational range', fontsize=9.8, color='#64748b')
for i, r in enumerate(rules):
    y = n - 1 - i + 0.08; fc, ec, lab = COL[r['status']]
    ax.add_patch(FancyBboxPatch((0.15, y), 12.7, 0.84, boxstyle='round,pad=0.02,rounding_size=0.1', fc=fc, ec=ec, lw=1.1))
    lines = textwrap.wrap(r['rule'], 150)[:3]
    for k, ln in enumerate(lines): ax.text(0.35, y + 0.64 - k * 0.24, ln, fontsize=9.2, color='#0f172a', weight='bold' if k == 0 else 'normal')
    ax.text(12.7, y + 0.1, lab, ha='right', fontsize=8.3, color=ec, weight='bold')
nums = D['numbers']
ax.text(0.15, -0.35, f"Earth dominates her by force ×{nums['force_ratio_earth_vs_sun_at_surface']:,} at the surface (the Sun dominates by potential ×{nums['potential_ratio_sun_vs_earth_at_surface']}): force weighting is what makes her local.  "
        f"Earth sphere {nums['earth_soi_km']:,} km · Moon sphere {nums['moon_soi_km']:,} km.", fontsize=9, color='#334155')
h = nums['hop_ledger_TJ']; ks = list(h)
ax.text(0.15, -0.75, f"Ledger: Fravor-type level hop {h[ks[0]]:.2f} TJ · hop to 200 km natural arrival {h[ks[1]]:.2f} TJ · hop to 200 km matched to Wayfarer {h[ks[2]]:.2f} TJ", fontsize=9, color='#334155')
f.savefig(os.path.join(H, 'weave_builder_rulebook.png'), dpi=150, bbox_inches='tight', facecolor='white')
