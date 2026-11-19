"""Shuttle v1 vs v2 B4: one-page scorecard for kT's decision. NON-CANON. ALL bodies. ALL sponsors. 2026-2226.
Sources: aero_results.json (ROM aero/entry/landing), b4_mass_gate.json (mass screen), SHUTTLE_V2_B4_PROPOSAL_2026_11_15.md."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, 'aero_results.json'))); M = json.load(open(os.path.join(HERE, 'b4_mass_gate.json')))
V1, B4 = 'v1 biconic', 'B4 double fold'
E = lambda b, k, f: A['entry'][b][k][f]
L = lambda b, k, f: A['landing'][b][k][f]
rows = [  # label, v1, B4, higher_is_better, fmt, group
 ('Sideways reach, Venus entry (km)', E('Venus', V1, 'crossrange_km'), E('Venus', B4, 'crossrange_km'), True, '{:.0f}', 'Getting down'),
 ('Sideways reach, Earth entry (km)', E('Earth', V1, 'crossrange_km'), E('Earth', B4, 'crossrange_km'), True, '{:.0f}', 'Getting down'),
 ('Sideways reach, Titan entry (km)', E('Titan', V1, 'crossrange_km'), E('Titan', B4, 'crossrange_km'), True, '{:.0f}', 'Getting down'),
 ('Peak g, Venus entry', E('Venus', V1, 'peak_g'), E('Venus', B4, 'peak_g'), False, '{:.1f}', 'Getting down'),
 ('Heat soaked up, Venus entry (MJ/m²)', E('Venus', V1, 'heat_load_MJm2'), E('Venus', B4, 'heat_load_MJm2'), False, '{:.0f}', 'Getting down'),
 ('Glide ratio, wings out', L('Venus', V1, 'LDmax'), L('Venus', B4, 'LDmax'), True, '{:.1f}', 'Landing'),
 ('Unpowered touchdown, Venus (m/s)', L('Venus', V1, 'v_td'), L('Venus', B4, 'v_td'), False, '{:.0f}', 'Landing'),
 ('Unpowered touchdown, Titan (m/s)', L('Titan', V1, 'v_td'), L('Titan', B4, 'v_td'), False, '{:.0f}', 'Landing'),
 ('Torch Δv (km/s)', 11.3, 10.9, True, '{:.1f}', 'Living with it'),
 ('Inside volume (m³)', 119, 82.5, True, '{:.0f}', 'Living with it'),
 ('Dry mass, middle (t)', M['v1_baseline_A']['mid'], M['v2_B4_side_door']['mid'], False, '{:.1f}', 'Living with it'),
 ('Under the 34.2 t bay limit (% of cases)', 100 * M['v1_baseline_A']['pass_G8_fraction'], 100 * M['v2_B4_side_door']['pass_G8_fraction'], True, '{:.0f}', 'Living with it'),
]
INK, MUTE, BG, GOOD, BAD = '#0b0b0b', '#52514e', '#fcfcfb', '#1baf7a', '#c8432f'
fig = plt.figure(figsize=(9, 11), dpi=150); fig.patch.set_facecolor(BG)
fig.text(.05, .965, 'Shuttle v1 vs v2 B4', fontsize=17, weight='bold', color=INK)
fig.text(.05, .945, 'Rough-order numbers from the lab tests. NON-CANON. Green = B4 better, red = B4 worse.', fontsize=9.5, color=MUTE)
ax = fig.add_axes([.05, .08, .9, .84]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(.60, .985, 'v1', ha='right', fontsize=11, weight='bold', color=MUTE); ax.text(.76, .985, 'B4', ha='right', fontsize=11, weight='bold', color=INK)
ax.text(.97, .985, 'change', ha='right', fontsize=10, color=MUTE)
y = .95; grp = None
for lab, a, b, hib, fmt, g in rows:
    if g != grp:
        y -= .012; ax.text(0, y, g, fontsize=12, weight='bold', color=INK); y -= .045; grp = g
    better = (b > a) == hib; col = GOOD if better else BAD; ch = (b - a) / a * 100
    ax.add_patch(plt.Rectangle((-.01, y - .022), 1.0, .044, color='#f0f1f2' if better else '#fbecea', lw=0))
    ax.text(0, y, lab, va='center', fontsize=10, color=INK)
    ax.text(.60, y, fmt.format(a), va='center', ha='right', fontsize=10.5, color=MUTE)
    ax.text(.76, y, fmt.format(b), va='center', ha='right', fontsize=10.5, color=INK, weight='bold')
    ax.text(.97, y, f'{ch:+.0f}%', va='center', ha='right', fontsize=10.5, color=col, weight='bold'); y -= .055
y -= .01
ax.text(0, y, 'Also', fontsize=12, weight='bold'); y -= .04
for t in ['B4: the crew spheres drive out a side door as a rover; v1 has a belly rover.',
          'Mars, Pluto and Triton landings are torch-only for both shapes.',
          'B4 has 7 open engineering items (side opening, door seals, hinges, hot wheels...).',
          'B4\'s heat shield mass was scaled by area, not by the +31% heat load: an open item.']:
    ax.text(0, y, '• ' + t, fontsize=9.5, color=INK); y -= .033
fig.savefig(os.path.join(HERE, 'compare_v1_b4.png'), facecolor=BG)
