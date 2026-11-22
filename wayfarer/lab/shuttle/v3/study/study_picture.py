"""Comparison picture for the 2026-11-21 study. ALL bodies. ALL sponsors. 2026-2226."""
import json, os, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, 'study_numbers.json')))['candidates']
W = json.load(open(os.path.join(H, '..', 'explorer', 'wildcard_screen.json')))['results']
B = json.load(open(os.path.join(H, '..', 'bay', 'bay_trade.json')))['options']
BS = json.load(open(os.path.join(H, '..', 'explorer', 'bay_screen.json')))['results']
F = json.load(open(os.path.join(H, '..', 'families', 'families.json')))['results']
fig = plt.figure(figsize=(17, 11)); fig.patch.set_facecolor('#f7f7f5')
# 1 Osteon basis (B5)
a = fig.add_axes([0.11, 0.56, 0.22, 0.36])
ost = S['B5 + Osteon central']['osteon']; mass = S['B5 reference']['mass']
items = ['hull_structure', 'wings', 'gear_door', 'crash_mounts', 'cabin_wall']
tot = [mass.get(k, 0) for k in items]; el = [ost['eligible_t'].get(k, 0) for k in items]
y = range(len(items)); a.barh(y, tot, color='#d5d8dc', label='component mass'); a.barh(y, el, color='#2f6e9c', label='eligible (primary structure)')
for i, (t, e) in enumerate(zip(tot, el)): a.text(t + .2, i, f'{e:.1f} of {t:.1f} t', va='center', fontsize=8)
a.set_yticks(list(y)); a.set_yticklabels(['hull structure', 'wings', 'gear, door, ramp', 'crash mounts', 'cabin wall (optimistic only)'], fontsize=9); a.invert_yaxis()
a.set_xlabel('t (B5)'); a.legend(fontsize=8, loc='lower right'); a.set_xlim(0, 21)
a.set_title(f"Osteon basis on B5: {ost['eligible_total_t']} t eligible, not 21 t\nsaves 2.5 / 3.5 / 4.8 t (22 / 30 / 38%), not 6.4 t", fontsize=10)
# 2 mission passes vs Osteon case
b = fig.add_axes([0.40, 0.56, 0.25, 0.36]); cases = ['none', 'osteon_cautious', 'osteon_airframe', 'osteon_optimistic']; lab = ['none', 'cautious\n22%', 'central\n30%', 'optimistic\n38%']
import numpy as np
x = np.arange(4); ev = [W[c]['missions']['evac'] for c in cases]; ht = [W[c]['missions']['hot'] for c in cases]; al = [W[c]['all_five'] for c in cases]
b.bar(x - .27, ev, .27, color='#2f8a4e', label='evacuation'); b.bar(x, ht, .27, color='#d9611b', label='hot extraction'); b.bar(x + .27, al, .27, color='#1d2328', label='all five')
for i in range(4): b.text(x[i] + .27, al[i] + 3, al[i], ha='center', fontsize=8)
b.axhline(170, color='#b8392f', ls=':'); b.text(-.4, 174, 'yesterday (uniform 30%, uncorrected): 170', fontsize=8, color='#b8392f')
b.set_xticks(x); b.set_xticklabels(lab, fontsize=9); b.set_ylabel('6+ couch designs passing (of 735)'); b.legend(fontsize=8, loc='center left'); b.set_ylim(0, 200)
b.set_title('Corrected: missions passed by Osteon case', fontsize=10)
# 3 bay options
c = fig.add_axes([0.72, 0.56, 0.26, 0.36])
keys = ['A 12.8 m (today)', 'B 14.3 m', 'C 16.8 m', 'W wider bore r 2.7 m']
lost = [B[k].get('econ_dv_lost_pct', 0) for k in keys]; rem = [B[k]['remass_removed_t'] for k in keys]
cols = ['#7b8792', '#2f8a4e', '#b9861a', '#b8392f']
c.bar(range(4), lost, color=cols)
for i, k in enumerate(keys): c.text(i, lost[i] + .4, (f"{rem[i]:.0f} t remass\n-{lost[i]:.1f}% ECON Δv" if rem[i] else "no remass\nlost"), ha='center', fontsize=8)
c.text(3.95, 1, 'D 18 m:\nconflicts\n(habitat or\ntorch manifold)', ha='center', fontsize=8, color='#b8392f')
c.set_xlim(-.6, 4.6); c.set_xticks(range(5)); c.set_xticklabels(['12.8 m\ntoday', '14.3 m', '16.8 m', 'wider\nr 2.7', '18 m'], fontsize=9); c.set_ylabel('Wayfarer ECON Δv lost, %'); c.set_ylim(0, 20)
c.set_title('Bay options: what Wayfarer pays\n(14.3 m: relocate the x 17-18 equipment band, no remass)', fontsize=10)
# 4 candidate table
t = fig.add_axes([0.03, 0.04, 0.94, 0.44]); t.axis('off')
rows = [('Candidate', 'Couches', 'Dry / on Wayfarer, t', 'Earth', 'Evac', 'Orbital', 'Surface', 'Hot', 'Note')]
def mk(name, short, note):
    v = S[name]; m = v['missions']; ok = lambda k: '✓' if m[k]['ok'] else '✗'
    rows.append((short, str(v['seats']), f"{v['dry_t']} / {v['docked_t']}", ok('earth'), ok('evac'), ok('orbital'), ok('surface'), ok('hot'), note))
mk('B5 reference', 'B5 (today)', 'evac touchdown 54.3 m/s; hot: water, thrust-short, touchdown')
mk('#2643 conventional', '1. Best corrected conventional: #2643', 'evac misses by 0.1 m/s, hot by 2.6 m/s; 10 t lighter than B5 on Wayfarer')
mk('#2643 Osteon cautious', '2. Best Osteon: #2643 (cautious 22%)', 'passes all five in all three Osteon cases; hot touchdown headroom 0.5-2.6 m/s')
mk('#2643 14.3 m, 8 couches, Osteon central', '3. 14.3 m bay: #2643-8, Osteon central', 'all five with 8 couches; fails hot at cautious (-1.0 m/s); conventional fails Earth')
mk('#2430 compact sea courier', '4a. Compact sea courier #2430 (no wings)', 'lightest Earth courier; no evac / hot (60.7 m/s touchdown, 7.8 °/s)')
rows.append(('4b. Vacuum utility (B5 core, no aero kit)', '6', f"{F['vacuum_utility']['dry_t']} / —", '—', '—', '✓', 'Moon/icy', '—', f"Δv {F['vacuum_utility']['dv_kms_23t_ve50']} km/s on 23 t; Moon round trip {F['vacuum_utility']['moon_round_trip_water_t']} t water"))
dc = F['ftl_daughtercraft']
rows.append(('5. FTL daughtercraft (Loom)', '—', f"~{dc['lean_dry_t']}-{dc['practical_dry_t']} dry / {dc['lean_wet_t']}-{dc['practical_wet_t']} wet", '', '', '', '', '', f"not a shuttle: 88 t plant + 10 kg Mc; carried, Wayfarer ECON Δv {dc['wayfarer_econ_dv_today_kms']:.0f} → {dc['lean_wayfarer_econ_dv_kms']:.0f}-{dc['practical_wayfarer_econ_dv_kms']:.0f} km/s"))
colw = [0.25, 0.05, 0.11, 0.04, 0.04, 0.05, 0.06, 0.04, 0.36]; xs = [sum(colw[:i]) for i in range(len(colw))]
for i, r in enumerate(rows):
    for j, cell in enumerate(r):
        col = '#2f8a4e' if cell == '✓' else '#b8392f' if cell == '✗' else '#1d2328'
        t.text(xs[j], 0.95 - i * 0.12, cell, fontsize=10 if i else 10.5, weight='bold' if i == 0 or j == 0 else 'normal', color=col, transform=t.transAxes, va='top')
fig.suptitle('Shuttle explorer: corrected baseline, Osteon basis, bay options and families (non-canon; kT decides)', fontsize=14, y=.985)
fig.savefig(os.path.join(H, 'study_comparison.png'), dpi=110, facecolor=fig.get_facecolor())
