"""Waterfall: shuttle v1 -> B4-S standard (A2 docked dry, middle values). NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); d = json.load(open(os.path.join(HERE, 'b4s_mass.json')))
g = json.load(open(os.path.join(HERE, 'b4_mass_gate.json')))['v1_baseline_A']['changed_parts_mid_t']; s = d['standard_A2']['parts_mid_t']
v1 = d['v1_same_draws']['A2_dry_t']['mid']; v1hab = v1water = 1.5
steps = [('Ti pressure sphere\n(moves to Venus kit)', -g['pressure_pod_titanium_shell_t']), ('pod fittings → cabin\nhatches + seals', s['cabin_hatches_seals_t'] - g['pressure_pod_fittings_seals_t']),
         ('lifting-body hull', s['hull_thermal_structure_t'] - g['hull_thermal_structure_t']), ('heat shield', s['base_entry_tps_core_t'] - g['base_entry_tps_core_t']),
         ('wings', s['b4_wings_t']), ('heat-proof cabin wall', s['cabin_wall_heat_tolerant_t']),
         ('6 seats: life support', s['crew_habitat_thermal_package_6_seats_t'] - v1hab), ('6 seats: water', s['water_tank_insulated_t'] - v1water),
         ('light rover\n(cabin, outfit, chassis)', s['rover_light_cabin_shell_t'] + s['rover_outfit_life_support_power_t'] + s['rover_chassis_crab_t'] - g['folding_rover_chassis_t'])]
INK, MUTE, BG, UP, DN = '#0b0b0b', '#52514e', '#fcfcfb', '#c8432f', '#1baf7a'
fig, ax = plt.subplots(figsize=(9, 8.5), dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
y = len(steps) + 1; ax.barh(y, v1, color='#b8bdc4', height=.6); ax.text(v1 + .2, y, f'v1 today  {v1:.1f} t', va='center', fontsize=10, weight='bold')
x = v1
for i, (lab, dv) in enumerate(steps):
    y -= 1; ax.barh(y, dv, left=x, color=UP if dv > 0 else DN, height=.6)
    ax.text(max(x, x + dv) + .2, y, f'{dv:+.1f}', va='center', fontsize=9.5, color=UP if dv > 0 else DN, weight='bold')
    ax.text(25.3, y, lab, va='center', ha='right', fontsize=9, color=INK); x += dv
y -= 1; a2 = d['standard_A2']['dry_t']; ax.barh(y, a2['mid'], color='#2a78d6', height=.6)
ax.text(a2['mid'] + .2, y, f"B4-S standard  {a2['mid']:.1f} t", va='center', fontsize=10, weight='bold')
ax.axvline(d['G8_limit_t'], color=INK, lw=1, ls=(0, (4, 3))); ax.text(d['G8_limit_t'] + .1, len(steps) + 1.55, 'G8 limit 34.2 t', fontsize=9)
ax.set_xlim(16, 37.5); ax.set_ylim(-.6, len(steps) + 2); ax.set_yticks([]); ax.set_xlabel('docked dry mass, t (middle of range)', color=MUTE)
for sp in ('top', 'right', 'left'): ax.spines[sp].set_visible(False)
fig.text(.04, .96, 'Shuttle B4-S: where the mass goes', fontsize=14, weight='bold')
fig.text(.04, .935, f"NON-CANON screen. Range {a2['p5']:.0f}–{a2['p95']:.0f} t; under G8 in {d['standard_A2']['pass_G8'] * 100:.0f}% of cases (v1 {d['v1_same_draws']['A2_pass_G8'] * 100:.0f}%). "
         f"Venus kit {d['venus_kit']['kit_t']['mid']:.1f} t (v1 {d['v1_same_draws']['kit_t']['mid']:.1f} t), carried as cargo.", fontsize=9, color=MUTE)
plt.subplots_adjust(left=.04, right=.97, top=.9, bottom=.08)
fig.savefig(os.path.join(HERE, 'b4s_mass.png'), facecolor=BG)
