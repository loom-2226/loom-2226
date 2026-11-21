"""Weave manoeuvring figures: manoeuvre card + hot-extraction sortie clocks. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse, FancyArrowPatch
H = os.path.dirname(os.path.abspath(__file__))
OPS = json.load(open(os.path.join(H, 'weave_ops.json'))); CYC = json.load(open(os.path.join(H, 'weave_cycle.json')))
INK, MUTED, BG, PANEL, SPEC = '#1d2328', '#5b6670', '#eef0ef', '#f8f8f6', '#b8392f'
COL = dict(torch='#d9611b', weave='#7a5cff', cold='#1f77b4', ok='#2a9d5c')   # validated categorical set (dataviz validator: pass)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': '#9aa3aa', 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': INK})
def clean(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.grid(color='#dde1e3', lw=.6); ax.set_axisbelow(True)
def tag(ax, x, y, s, c=SPEC, fs=7.5): ax.text(x, y, s, transform=ax.transAxes, fontsize=fs, color=c, va='top', bbox=dict(fc='white', ec=c, lw=.8, boxstyle='round,pad=.3'))
def shuttle(ax, x, y, s=1.0, c='#8a939b', alpha=1.0):
    ax.add_patch(Polygon([(x - 1.6 * s, y), (x - 0.9 * s, y + 0.45 * s), (x + 1.2 * s, y + 0.38 * s), (x + 1.7 * s, y + 0.05 * s), (x + 1.2 * s, y - 0.25 * s), (x - 1.4 * s, y - 0.25 * s)], fc=c, ec=INK, lw=.7, alpha=alpha, zorder=5))
def bubble(ax, x, y, s=1.0, alpha=.18): ax.add_patch(Ellipse((x, y + 0.08 * s), 4.6 * s, 1.9 * s, fc=COL['weave'], ec=COL['weave'], lw=.8, alpha=alpha, zorder=4))
cold = OPS['cold_budget']['cases']; mod = OPS['module']; ht = OPS['height']; cl = OPS['hot_extraction_closure']; ceil = OPS['module_ceiling_t']

# ======================================================== figure 1: manoeuvre card
fig = plt.figure(figsize=(16, 10)); fig.patch.set_facecolor(BG)
fig.text(.012, .972, 'Weave manoeuvring - the "tic-tac" mode of the metric drive (NON-CANON prototype lane)', fontsize=15, weight='bold', color=INK)
fig.text(.012, .947, 'The Weave changes POSITION; the torch owns VELOCITY. Partner = the local body (closes the energy pump). Fuel = reactor -> field bank. Limits = cold, Mc wear, the shared Loom lattice.', fontsize=9.5, color=MUTED)
# (a) scene: hover, dash zig-zag, dead stops, dodge with frost puff, silent climb
a = fig.add_axes([.02, .47, .58, .44]); a.set_facecolor('#eaf1f6'); a.set_xlim(0, 40); a.set_ylim(-2, 14); a.axis('off')
a.fill_between([0, 40], -2, 0, color='#2f6e9c', alpha=.55, zorder=1)
for k in range(9): a.plot([k * 4.6 + 1, k * 4.6 + 2.4], [-0.05, -0.05], color='white', lw=1, alpha=.6)
pts = [(5, 1.2, 'hover'), (13, 1.2, 'dash'), (16, 4.5, 'rise (paid)'), (24, 3.8, 'dodge'), (31, 6.5, 'stop'), (34, 11.5, 'climb')]
for i, (x, y, lab) in enumerate(pts):
    bubble(a, x, y, .9, alpha=.14 if i < len(pts) - 1 else .2); shuttle(a, x, y, .9, alpha=.95 if i in (0, len(pts) - 1) else .55)
    a.text(x, y - 1.35, lab, ha='center', fontsize=8.5, color=INK)
for (x0, y0, _), (x1, y1, _) in zip(pts[:-1], pts[1:]):
    a.add_patch(FancyArrowPatch((x0 + 1.6, y0 + .1), (x1 - 1.6, y1 + .1), arrowstyle='-|>', mutation_scale=12, color=COL['weave'], lw=1.6, ls=(0, (4, 3)), zorder=3))
for k in range(5): a.add_patch(Ellipse((22.4 - k * .6, 3.3 - k * .15), .9 + k * .35, .55 + k * .2, fc='#d6e8f5', ec=COL['cold'], lw=.5, alpha=.8 - k * .13, zorder=3))
a.text(20.0, 2.0, 'frost charge vented', fontsize=7.5, color=COL['cold'], ha='right')
a.text(35.8, 9.0, 'torch lights\nhere, pointed\naway (later)', fontsize=7.5, color=COL['torch'])
a.text(.5, 13.2, 'Hover - dash - stop - dodge - climb: no plume, no g on the crew, dead stops (the ship never gained kinetic speed)', fontsize=9, color=INK)
tag(a, .01, .86, 'NOT VERIFIED: geometry schematic; boundary/air behaviour UNKNOWN\n(could be a bang, a whoosh or silence - the decisive open question)', SPEC, 7.2)
# (b) card table
b = fig.add_axes([.62, .47, .37, .44]); b.axis('off')
rows = [['Move', 'Energy', 'Costs / limits'],
        ['Dash (level)', 'free', 'cold ~%g MJ, wear' % cold['central']['Q_dash_MJ']],
        ['Stop (end of dash)', 'free', 'in the dash'],
        ['Hover', 'holding only', 'hold cold load (open)'],
        ['Climb', 'pay m g h', 'bank ~%d m, then reactor' % ht['Earth']['bank_only_height_m']],
        ['Descend', 'returns m g h', 'bank headroom'],
        ['Change velocity', 'NOT Weave', 'torch / fans'],
        ['Dodge', 'a dash', 'sheds a frost charge'],
        ['Cooldown', '-', 'air ~%d s, vacuum ~%d s' % (cold['central']['cooldown_per_dash_s_air'], cold['central']['cooldown_per_dash_s_vacuum'])]]
tb = b.table(cellText=rows, loc='upper center', cellLoc='left', colWidths=[.3, .26, .44]); tb.auto_set_font_size(False); tb.set_fontsize(8.6); tb.scale(1, 2.0)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_edgecolor('#cfd5d8'); cell.set_facecolor('#e4e8ea' if r_ == 0 else 'white')
    if r_ and c_ == 1 and rows[r_][1] in ('free', 'returns m g h'): cell.get_text().set_color(COL['ok'])
    if r_ and c_ == 1 and rows[r_][1] in ('pay m g h', 'NOT Weave'): cell.get_text().set_color(COL['torch'])
b.text(0, .03, 'Central case. Cold per dash is an ASSUMPTION (0.25-4 MJ) anchored to canon ramp cold energies.', transform=b.transAxes, fontsize=7.6, color=MUTED)
# (c) energy loop
c = fig.add_axes([.04, .07, .27, .32]); c.set_facecolor(PANEL); clean(c)
lab = ['Sun partner\n(canon as written)', 'Local partner\n(lane rule W1)']; val = [CYC['cycle_1km'][k]['net_extractable_MJ_per_cycle'] for k in CYC['cycle_1km']]
c.bar([0, 1], val, color=[SPEC, COL['ok']], width=.55)
for x, v in zip([0, 1], val): c.text(x, v + 15, f'{v:.0f} MJ', ha='center', fontsize=9, color=INK)
c.set_xticks([0, 1]); c.set_xticklabels(lab, fontsize=8); c.set_ylabel('net work from one 1 km up-down cycle (MJ)'); c.set_ylim(0, 720)
c.set_title('Decisive test: Sun partner pumps, local partner closes', fontsize=9.5, loc='left', color=INK)
c.text(.5, .62, 'PUMP (CANON II §7.3 hard kill)', transform=c.transAxes, fontsize=7.5, color=SPEC); c.text(.62, .12, 'closed', transform=c.transAxes, fontsize=7.5, color=COL['ok'])
# (d) cold budget
d = fig.add_axes([.37, .07, .25, .32]); d.set_facecolor(PANEL); clean(d)
ks = ['low', 'central', 'high']; x = np.arange(3)
d.bar(x - .18, [cold[k]['dashes_from_12_charges'] for k in ks], .34, color=COL['cold'], label='dashes from buffer + 12 frost charges')
d2 = d.twinx(); d2.plot(x + .18, [cold[k]['cooldown_per_dash_s_air'] for k in ks], 'o', color=COL['ok'], ms=8, label='cooldown per dash, air (s)')
d2.plot(x + .18, [cold[k]['cooldown_per_dash_s_vacuum'] for k in ks], 's', color=COL['weave'], ms=7, label='cooldown per dash, vacuum (s)')
d2.set_yscale('log'); d2.set_ylabel('cooldown per dash (s, log)', color=MUTED); d2.spines['top'].set_visible(False)
d.set_xticks(x); d.set_xticklabels([f"{cold[k]['Q_dash_MJ']} MJ/dash" for k in ks]); d.set_ylabel('dashes available')
for xi, k in zip(x, ks): d.text(xi - .18, cold[k]['dashes_from_12_charges'] + 1.5, f"{cold[k]['dashes_from_12_charges']:.0f}", ha='center', fontsize=8)
d.set_title('Dodge budget: 12 frost charges (3 kg LH2 each)', fontsize=9.5, loc='left', color=INK)
h1, l1 = d.get_legend_handles_labels(); h2, l2 = d2.get_legend_handles_labels(); d.legend(h1 + h2, l1 + l2, fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(.62, 1.0))
# (e) module mass vs hot extraction
e = fig.add_axes([.78, .07, .2, .32]); e.set_facecolor(PANEL); clean(e)
names = list(cl.keys()); waters = [cl[n]['Weave lift to 2 km']['water_need_t'] for n in names]
e.barh(range(3), waters, color=[COL['ok'] if cl[n]['Weave lift to 2 km']['closes'] else SPEC for n in names], height=.55)
e.axvline(23.0, color=INK, lw=1, ls='--'); e.text(23.3, 1.55, 'carried\n23 t', fontsize=7.5, color=INK)
e.set_yticks(range(3)); e.set_yticklabels(['none', 'L² 13.8 t', 'half 6.9 t'], fontsize=8); e.set_xlabel('hot-extraction water need (t)')
e.set_title('Module mass is the catch: ceiling ~%.1f t' % ceil['Weave lift to 2 km'], fontsize=9.5, loc='left', color=INK)
fig.text(.66, .012, 'Module: L² size law is a CANDIDATE (CANON II §6.2), not canon. Vehicle: fold 17 m + adaptive camber + Osteon (37.3 t).', fontsize=7.2, color=MUTED)
fig.savefig(os.path.join(H, 'weave_card.png'), dpi=110, facecolor=BG); plt.close(fig)

# ======================================================== figure 2: sortie clocks (central case, air)
Qd, BUF, CH = cold['central']['Q_dash_MJ'], OPS['cold_budget']['buffer_MJ'], OPS['cold_budget']['frost_charge']['absorbs_MJ']
lift_kW = mod['cryo_lift_kW']; bankmax = mod['bank_GJ'] * 1e3; m = 61e3
t = np.arange(0, 241, 0.5); alt = np.zeros_like(t); heat = np.zeros_like(t); bank = np.zeros_like(t); charges = np.zeros_like(t)
h_, q_, b_, n_ = 500.0, 0.0, 0.0, 12; events = []
dashes = [150, 156, 162]
for i, ti in enumerate(t):
    if ti <= 20: h_ = 500 * (1 - ti / 20); b_ = min(bankmax, m * G * (500 - h_) / 1e6 if (G := 9.81) else 0)
    elif 170 <= ti <= 210:
        frac = (ti - 170) / 40; h_ = 2000 * frac ** 2; b_ = max(0.0, bankmax - m * G * h_ / 1e6)
    elif ti > 210: h_ = 2000 + 120 * (ti - 210) + 0.5 * 0.4 * 9.81 * (ti - 210) ** 2
    for td in dashes:
        if abs(ti - td) < 1e-6:
            q_ += Qd; events.append((ti, 'dash'))
            if q_ > BUF and n_ > 0: q_ -= CH; n_ -= 1; events.append((ti, 'shed'))
    q_ = max(0.0, q_ - lift_kW * 1e3 * 0.5 / 1e6)
    alt[i], heat[i], bank[i], charges[i] = h_, q_, b_, n_
fig, axs = plt.subplots(4, 1, figsize=(14, 10), sharex=True); fig.patch.set_facecolor(BG)
fig.suptitle('A Weave hot-extraction sortie: the four clocks (central case, sea level, NON-CANON)', x=.012, ha='left', fontsize=14, weight='bold', color=INK)
specs = [(alt / 1e3, 'altitude (km)', COL['weave']), (heat, 'node heat (MJ)', COL['cold']), (charges, 'frost charges', COL['cold']), (bank, 'field bank (MJ)', COL['ok'])]
for ax, (y, lab, c) in zip(axs, specs):
    ax.set_facecolor(PANEL); clean(ax); ax.plot(t, y, color=c, lw=2, drawstyle='steps-post' if lab == 'frost charges' else 'default'); ax.set_ylabel(lab)
axs[0].set_ylim(0, 3.2); axs[0].axvline(210, color=COL['torch'], lw=1.2, ls='--'); axs[0].text(211, 2.75, 'torch lights at 2 km', color=COL['torch'], fontsize=8)
axs[1].axhline(BUF, color=SPEC, lw=1, ls='--'); axs[1].text(2, BUF + .05, 'HOLD limit (buffer %.1f MJ)' % BUF, color=SPEC, fontsize=7.5)
axs[2].set_ylim(8, 12.6)
for ax in axs:
    for x0, x1, lab in ((0, 20, 'silent Weave descent\n(bank recharges)'), (20, 150, 'pickup: no plume, cryo cools'), (150, 165, 'threat: 3 dodges'), (170, 210, 'silent Weave climb\n(bank + reactor)')):
        ax.axvspan(x0, x1, color='#dfe4e8' if (x0 // 10) % 2 == 0 else '#eef1f3', alpha=.5, zorder=0)
for x0, x1, lab in ((0, 20, 'silent descent\n(bank recharges)'), (20, 150, 'pickup: no plume, cryo cools'), (150, 165, '3 dodges'), (170, 210, 'silent climb (bank + reactor)')):
    axs[0].text((x0 + x1) / 2, 2.55 if x1 - x0 > 30 else 1.6, lab, ha='center', fontsize=8, color=INK)
for ti, kind in events:
    if kind == 'shed': axs[2].annotate('frost charge shed', (ti, 11), xytext=(ti + 6, 10.0), fontsize=8, color=COL['cold'], arrowprops=dict(arrowstyle='-', color=COL['cold'], lw=.8))
axs[-1].set_xlabel('time (s)'); axs[-1].set_xlim(0, 240)
tag(axs[1], .55, .95, 'Cold per dash 1 MJ, buffer 1.5 MJ, charge 1.34 MJ, cryo lift 22 kW (air): ASSUMPTIONS / CANDIDATE', SPEC, 7)
fig.text(.012, .01, 'Not shown: Mc tile wear (one wear point per dash; requalification threshold is a campaign knob). On Wayfarer the same tiles carry the Loom: every dodge spends some of the way home.', fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, .03, 1, .95)); fig.savefig(os.path.join(H, 'weave_sortie.png'), dpi=110, facecolor=BG); plt.close(fig)
print('ok')
