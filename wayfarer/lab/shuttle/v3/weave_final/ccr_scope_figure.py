"""Canon II provisions vs the Weave shuttle CCR proposal (draft, NON-CANON)."""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

H = os.path.dirname(os.path.abspath(__file__))
plt.rcParams['font.family'] = 'Inter' if 'Inter' in {f.name for f in __import__('matplotlib').font_manager.fontManager.ttflist} else 'DejaVu Sans'

COL = {'amend': ('#fde7cf', '#b45309', 'SCOPED EXCEPTION'),
       'option': ('#e0e7ff', '#3730a3', 'OPTION A (kT)'),
       'keep': ('#dcfce7', '#15803d', 'PRESERVED'),
       'note': ('#f1f5f9', '#475569', 'INTERACTION ONLY'),
       'sep': ('#fae8ff', '#86198f', 'SEPARATE PROPOSAL')}
rows = [
    ('amend', '§3 plant scale', '~8 t module; material UNKNOWN, not Mc-299m'),
    ('amend', '§5 / §9 ramps, paths', 'own near-body card; no 0.268c, no long baseline'),
    ('amend', '§6 certification', 'EXPERIMENTAL, UNCERTIFIED'),
    ('amend', '§18A tactical split', 'sidesteps = test behaviour, not doctrine'),
    ('option', '§7.1b exchange partner', 'Sun for certified Metric; prototype UNKNOWN'),
    ('keep', '§2 foundational limits', 'METRIC family; no third miracle'),
    ('keep', '§7.3 conservation firewall', 'full exchange; not reactionless wake thrust'),
    ('keep', '§21 hard kills', 'all stand'),
    ('note', '§3.1 / §11 / §12.1 / §13', 'Mc budget, node failure, commit lock, mass'),
    ('sep', 'Docking collar (v2.5a bay)', 'proposed; demonstrate at Step 5'),
]
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 11); ax.set_ylim(0, len(rows) + 1.6); ax.axis('off')
ax.text(0.2, len(rows) + 1.1, 'Weave shuttle CCR proposal: which Canon II provisions move',
        fontsize=15, color='#0f172a')
ax.text(0.2, len(rows) + 0.6, 'CCR-2026-0005 PROPOSED (PR #570) · kT accepted Step 4 · nothing in canon changed yet',
        fontsize=10, color='#64748b')
for i, (k, sec, txt) in enumerate(rows):
    y = len(rows) - 1 - i + 0.1
    fc, ec, lab = COL[k]
    ax.add_patch(FancyBboxPatch((0.2, y), 10.6, 0.78, boxstyle='round,pad=0.02,rounding_size=0.12',
                                fc=fc, ec=ec, lw=1.2))
    ax.text(0.45, y + 0.39, sec, va='center', fontsize=11.5, color='#0f172a', weight='bold')
    ax.text(3.9, y + 0.39, txt, va='center', fontsize=10.5, color='#1e293b')
    ax.text(10.6, y + 0.39, lab, va='center', ha='right', fontsize=9, color=ec, weight='bold')
fig.savefig(os.path.join(H, 'weave_ccr_scope.png'), dpi=150, bbox_inches='tight', facecolor='white')
