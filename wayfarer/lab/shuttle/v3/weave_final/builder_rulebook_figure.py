"""Builder Tic Tac rulebook: what each rule rests on. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, textwrap, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'builder_rulebook.json')))
COL = {'DERIVED within the adopted field model': ('#dbeafe', '#1d4ed8', 'DERIVED within the field model'), 'NEW BUILDER PERMISSION': ('#fee2e2', '#b91c1c', 'NEW BUILDER PERMISSION'),
       'CONDITIONAL HYPOTHESIS': ('#fae8ff', '#86198f', 'CONDITIONAL HYPOTHESIS'), 'CHOSEN OPERATING RULE': ('#fef3c7', '#b45309', 'CHOSEN OPERATING RULE'),
       'OPEN (narrative)': ('#f1f5f9', '#475569', 'OPEN')}
rules = D['rules']; n = len(rules)
f, ax = plt.subplots(figsize=(13, 12)); ax.set_xlim(0, 13); ax.set_ylim(-1.0, n + 2.2); ax.axis('off')
ax.text(0.15, n + 1.75, 'Builder Tic Tac rulebook: what each rule rests on (corrected after Sol review)', fontsize=15, color='#0f172a')
ax.text(0.15, n + 1.3, 'Fiction-first, NON-CANON. Only R1, R2, R4 follow within the adopted field model; the rest are a new permission, conditional hypotheses or chosen rules', fontsize=9.8, color='#64748b')
for i, r in enumerate(rules):
    y = n - 1 - i + 0.08; fc, ec, lab = COL[r['status']]
    ax.add_patch(FancyBboxPatch((0.15, y), 12.7, 0.84, boxstyle='round,pad=0.02,rounding_size=0.1', fc=fc, ec=ec, lw=1.1))
    lines = textwrap.wrap(r['rule'], 150)[:3]
    for k, ln in enumerate(lines): ax.text(0.35, y + 0.64 - k * 0.24, ln, fontsize=9.2, color='#0f172a', weight='bold' if k == 0 else 'normal')
    ax.text(12.7, y + 0.1, lab, ha='right', fontsize=8.3, color=ec, weight='bold')
nums = D['numbers']
ax.text(0.15, -0.35, f"Partner criterion NOT chosen: equal pull gives Earth {nums['earth_equal_pull_km']:,} km (the Sun pulls the Moon ×{nums['sun_vs_earth_pull_on_moon']} harder than Earth); "
        f"Laplace sphere gives Earth {nums['earth_soi_km']:,} km, Moon {nums['moon_soi_km']:,} km.", fontsize=9, color='#334155')
h = nums['hop_ledger_TJ']; ks = list(h)
ax.text(0.15, -0.75, f"Conditional examples (endpoint mechanical energy only, not hop formation cost): Fravor-type level hop {h[ks[0]]:.2f} TJ · hop to 200 km natural arrival {h[ks[1]]:.2f} TJ · hop to 200 km matched to Wayfarer {h[ks[2]]:.2f} TJ", fontsize=9, color='#334155')
f.savefig(os.path.join(H, 'weave_builder_rulebook.png'), dpi=150, bbox_inches='tight', facecolor='white')
