"""Picture for b4_cabin_options.json. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch, Rectangle
HERE = os.path.dirname(os.path.abspath(__file__)); d = json.load(open(os.path.join(HERE, 'b4_cabin_options.json')))
INK, MUTE, BG, TI, CAB, KIT = '#0b0b0b', '#52514e', '#fcfcfb', '#8f8a80', '#2a78d6', '#d99a1e'
GOOD, BAD = '#1baf7a', '#c8432f'
body = [(0, .55), (.6, 1.25), (2.2, 2.2), (4, 2.45), (11.5, 2.4), (12.8, 1.9), (12.8, .2), (10, 0), (2, 0), (.4, .25)]
opts = [('Today: two spheres', d['B4_twin_spheres_tps_fixed'], 'today'), ('A: one long Ti capsule', d['A_one_capsule'], 'A'), ('B: big cabin + Venus pod in the kit', d['B_split_cabin_venus_pod_in_kit'], 'B')]
fig, axs = plt.subplots(3, 1, figsize=(9, 11.5), dpi=150); fig.patch.set_facecolor(BG)
fig.text(.04, .965, 'More room inside B4: three ways', fontsize=16, weight='bold'); fig.text(.04, .945, 'Side view, bow left, to scale. NON-CANON screen; heat-shield fix included in every option. G8 limit 34.2 t.', fontsize=9.5, color=MUTE)
for ax, (title, o, k) in zip(axs, opts):
    ax.set_facecolor(BG); ax.add_patch(Polygon(body, closed=True, fc='#eef0f3', ec=MUTE, lw=1.2))
    if k == 'today':
        for cx in (6.85, 8.75): ax.add_patch(Circle((cx, 1.2), .95, fc=TI, ec=INK, lw=1))
        ax.add_patch(Rectangle((7.6, 1.0), .4, .4, fc=TI, ec=INK, lw=.8))
    if k == 'A':
        ax.add_patch(FancyBboxPatch((4.55, .25), 6.5 - .0, 1.9, boxstyle='round,pad=0,rounding_size=.95', fc=TI, ec=INK, lw=1))
        for xx in (5.8, 6.7, 7.6, 8.5, 9.4): ax.plot([xx, xx], [.27, 2.13], color='#5d5850', lw=1.2)
    if k == 'B':
        ax.add_patch(FancyBboxPatch((2.9, .25), 8.2, 1.95, boxstyle='round,pad=0,rounding_size=.25', fc=CAB, ec=INK, lw=1, alpha=.85))
        ax.text(7.0, 1.22, '1-bar cabin  30 m³', ha='center', va='center', color='white', fontsize=10, weight='bold')
        ax.add_patch(Circle((15.2, 1.2), 1.05, fc='none', ec=KIT, lw=1.6, ls=(0, (4, 2)))); ax.text(15.2, 1.2, 'Venus pod\n2.1 m Ti\n(in the kit)', ha='center', va='center', fontsize=8, color='#9a6a0c')
    c = o['core_dry_t']; p = o['pass_G8']
    txt = f"crew room {o['crew_pressurised_m3']:.0f} m³  ·  dry {c['mid']:.1f} t ({c['p5']:.0f}–{c['p95']:.0f})  ·  under G8 {p * 100:.0f}%"
    ax.set_title(title, loc='left', fontsize=12, weight='bold', color=INK); ax.text(0, -.55, txt, fontsize=10, color=GOOD if p > .9 else (BAD if p < .5 else '#9a6a0c'), weight='bold')
    ax.set_xlim(-.3, 17); ax.set_ylim(-.8, 2.8); ax.set_aspect('equal'); ax.axis('off')
notes = ['v1 for reference: one 2.5 m sphere, 8 m³, 30.0 t, under G8 96%.',
         'B: everyone flies in the cabin. On Venus the crew ride down in the pod and the cabin is vented and left to the heat.',
         'B: the pod is also the Venus rover; it adds ~3.9 t to the detachable Venus/Titan kit, not to the shuttle.',
         'B: away from Venus there is no rover unless the kit is carried.']
for i, n in enumerate(notes): fig.text(.04, .055 - i * .016, '• ' + n, fontsize=9, color=INK)
plt.subplots_adjust(left=.03, right=.98, top=.91, bottom=.11, hspace=.45)
fig.savefig(os.path.join(HERE, 'b4_cabin_options.png'), facecolor=BG)
