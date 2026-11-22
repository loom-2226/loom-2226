"""Tic Tac vs selected shuttle: one-page comparison. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); D = json.load(open(os.path.join(H, 'tictac_vs_shuttle.json')))
s, t = D['shuttle'], D['tictac']; tc = t['cases']['+ parachutes']; tt = t['cases']['torch-only fallback']
INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; TT = '#0e7490'; OK = '#16a34a'; BAD = '#dc2626'
plt.rcParams.update({'font.size': 10})
rows = [  # label, shuttle text, tic tac text, winner ('s', 't', '=')
    ('Dry mass (ceiling 52.5 t)', f"{s['dry_t']:.1f} t", f"{tc['dry_t']:.1f} t with chutes ({tt['dry_t']:.1f} without)", 't'),
    ('Mass margin', f"{s['margin_t']:.1f} t", f"{tc['margin_t']:.1f} t ({tt['margin_t']:.1f})", 't'),
    ('Climb water (tank 23.1 t)', f"{s['water_t']:.1f} t", f"{tc['water_t']:.1f} t ({tt['water_t']:.1f})", 't'),
    ('Interior: spare after everything', f"{s['interior_spare_m3']:.2f} m³ (none)", f"{t['interior_spare_m3']:.0f} m³", 't'),
    ('Floats on its own hull', 'needs 32 m³ pop-out floats', f"yes: {t['hull_m3']:.0f} m³ hull vs {tc['buoyancy'][1]:.0f} needed", 't'),
    ('Wayfarer bay', '13.02 m: needs the collar, aft gap 0.28 m', '12.8 m: no change to Wayfarer; width exactly at the limit', 't'),
    ('Felt-load lever (field radius used)', f"{s['field_max_radius']} m (wing tips)", f"{t['field_max_radius']} m", 't'),
    ('Entry heating (peak)', f"{s['peak_heat']} W/cm²", f"{t['peak_heat_a40']} W/cm²", 't'),
    ('Entry crossrange', f"{s['crossrange_km']:,} km (L/D {s['hyper_LD']})", f"{t['crossrange_km_a40']} km (L/D {t['hyper_LD']:.1f})", 's'),
    ('If the field fails near the ground', 'wings + fans: fly out above ~50 m/s,\nland on water at ≤ 50 m/s', 'torch only (needs height and water)\nor parachutes; no gliding', 's'),
    ('Floating upright (W6)', 'checked with floats', 'NOT checked: a round hull wants to roll', 's'),
    ('kT decisions', 'as decided (keep wings, fans, floats)', 'reverses "keep wings, fans and floats\nas fallback"', 's'),
]
f = plt.figure(figsize=(13, 9.4)); f.suptitle('Is a Tic Tac redesign materially better? Same rules, same module, same tank (NON-CANON)', x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
f.text(0.02, 0.948, 'Selected shuttle 13.02 m lifting body vs a 12.8 m × 3.8 m capsule. Green marks the better side on each line.', color=MUT, fontsize=9.5)
ax = f.add_axes([0.02, 0.1, 0.96, 0.82]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, len(rows) + 1)
ax.text(0.30, len(rows) + 0.5, 'Selected shuttle', color=SH, fontsize=12, weight='bold'); ax.text(0.64, len(rows) + 0.5, "'Tic Tac' capsule", color=TT, fontsize=12, weight='bold')
for i, (lab, a, b, w) in enumerate(rows):
    y = len(rows) - 1 - i + 0.1
    if i % 2 == 0: ax.add_patch(FancyBboxPatch((0.0, y - 0.02), 1.0, 0.86, boxstyle='round,pad=0,rounding_size=0.01', fc='#f8fafc', ec='none'))
    ax.text(0.01, y + 0.42, lab, va='center', color=INK, fontsize=10)
    for x0, txt, side in ((0.30, a, 's'), (0.64, b, 't')):
        win = (w == side)
        ax.text(x0, y + 0.42, txt, va='center', fontsize=9.6, color=OK if win else INK, weight='bold' if win else 'normal')
f.text(0.02, 0.035, 'Tic Tac assumptions: hull structure scales with wetted area and entry TPS with planform (host rules); 1.0 t power unit kept for cooling and flywheel recharge; '
       'parachutes ~3.5% of landing mass.\nNot done for the Tic Tac: floating stability, structure detail, door and rover access, Venus fan hover replacement.', fontsize=8.6, color=MUT)
f.savefig(os.path.join(H, 'weave_tictac_vs_shuttle.png'), dpi=150, facecolor='white')
