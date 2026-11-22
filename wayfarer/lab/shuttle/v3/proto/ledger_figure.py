"""Prototype-lane ledger figure. ALL bodies. ALL sponsors. 2026-2226."""
import sys, os, json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(H, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
MW = json.load(open(os.path.join(H, 'metric_wildcards.json')))
g = dict(by[2643]['params'])
cfg = [('#2643 conventional (corrected)', dict(g), None),
       ('W1 programmable alone (17 m)', dict(g, wildcard='programmable', span=17.0, chord=1.8, water_t=23.1), None),
       ('W2 metric cushion alone (8 t module)', dict(g, water_t=23.1), 8),
       ('Osteon cautious alone', dict(g, wildcard='osteon_cautious'), None),
       ('W1 + Osteon cautious', dict(g, wildcard='osteon_cautious+programmable', span=17.0, chord=1.8), None),
       ('W1 + Osteon + 14.3 m, 8 couches', dict(g, wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1, length=14.3, seats=8), None),
       ('W2 (8 t) + W1 + Osteon', dict(g, wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=23.1), 8)]
rows = []
for name, p, mod in cfg:
    r = E.evaluate(p); ms = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
    ok = {k: m['ok'] for k, m in ms.items()}; dry = r['dry_t']
    if mod is not None:                     # metric cushion replaces landing + near-ground climb; re-check water/mass (hypothesis)
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()): import metric_wildcards as M
        cu = M.cushion(p, mod); dry = cu['dry_t']
        for k in ('earth', 'evac', 'hot'): ok[k] = bool(cu['fits'])
    rows.append((name, dry, ok))
fig = plt.figure(figsize=(17, 10)); fig.patch.set_facecolor('#f7f7f5')
a = fig.add_axes([0.02, 0.50, 0.50, 0.42]); a.axis('off')
hdr = ['Configuration (6 couches unless noted)', 'dry t', 'Earth', 'Evac', 'Orbital', 'Surface', 'Hot']
xs = [0, .52, .63, .71, .79, .88, .96]
for j, h in enumerate(hdr): a.text(xs[j], .97, h, weight='bold', fontsize=10, transform=a.transAxes, va='top')
for i, (n, dry, ok) in enumerate(rows):
    y = .88 - i * .12; spec = n.startswith('W')
    a.text(xs[0], y, n, fontsize=10, transform=a.transAxes, va='top', color='#7a5cff' if 'W2' in n else ('#d9611b' if spec else '#1d2328'))
    a.text(xs[1], y, f'{dry:.1f}', fontsize=10, transform=a.transAxes, va='top')
    for j, k in enumerate(('earth', 'evac', 'orbital', 'surface', 'hot')):
        a.text(xs[j + 2], y, '✓' if ok[k] else '✗', fontsize=13, color='#2f8a4e' if ok[k] else '#b8392f', transform=a.transAxes, va='top')
a.set_title('Each wildcard alone, then combined (rough models; orange/purple = prototype lane, non-canon)', loc='left', fontsize=11.5, weight='bold')
b = fig.add_axes([0.58, 0.55, 0.39, 0.36])
for name, col in (('#2643 + Osteon cautious', '#2f6e9c'), ('#2643 14.3 m, 8 couches, Osteon cautious', '#d9611b')):
    cu = MW['w2_cushion_2km'][name]; ms_ = [float(k) for k in cu]; ws = [cu[k]['hot_water_t'] for k in cu]
    b.plot(ms_, ws, 'o-', color=col, label=name.replace('#2643 ', '#2643: '))
cu = MW['w2_cushion_alone_and_combos']['#2643']; b.plot([float(k) for k in cu], [cu[k]['hot_water_t'] for k in cu], 's--', color='#5d6872', label='#2643 conventional')
b.axhline(23.1, color='#1d2328', ls=':'); b.text(2.2, 23.4, 'tank 23.1 t', fontsize=8.5)
b.axvline(MW['scaling']['L2 (area, candidate fit §6.2)']['plant_t'] + 1, color='#7a5cff', ls='--'); b.text(12.3, 14.2, 'L² candidate\nestimate ~14 t →', color='#7a5cff', fontsize=8.5, ha='center')
b.text(2.2, 25.0, f"L¹ scaling ~{MW['scaling']['L1 (sqrt area)']['plant_t'] + 1:.0f} t,\nWayfarer plant 88 t: off the chart", fontsize=8.5, color='#b8392f')
b.set_xlabel('shuttle relational module mass, t (nodes, Mc tiles, cryo, mounts)'); b.set_ylabel('hot-extraction water needed, t'); b.legend(fontsize=8, loc='upper left'); b.set_ylim(13, 30); b.grid(alpha=.3)
b.set_title('W2 decisive number: the module must be ≤ ~8-12 t\n(cushion to 2 km, flywheel energy included)', fontsize=11)
c = fig.add_axes([0.02, 0.03, 0.96, 0.42]); c.axis('off')
T = [('Wildcard', 'Minimum new effect', 'Canon TECHNOLOGY limit it supersedes', 'Deeper invariant at risk', 'Decisive unknown'),
     ('W1 programmable\nstructure', 'none in physics: Builder-derived\nshape/stiffness-switching structure', '2026-2226 material baseline (only Osteon\nhas repo evidence as a Builder material)', 'none (energy for actuation is paid);\nfatigue, heat at re-entry', 'stiffness-vs-morph trade; mass factor\n(1.5x wing assumed); stowed shape'),
     ('W2 metric cushion\n(lift-off / landing)', 'POWERED metric: onboard energy into the\nship\'s ordinary state, Sun as partner', '~88 t plant (§3; L² law is only a candidate,\n§6.2); ENERGY-B energy-neutral rule (§7.1a);\nnear-body certification (§6, §9); doctrine §18A', 'none if the ledger closes (§7.3): energy\npaid ≥ mgh/η, wall clear of hull, water\nand people (domain continuity)', 'module mass ≤ 8-12 t; is the powered\nchannel inside M2 or a third miracle?;\nnear-matter correction power (§6.3)'),
     ('W3 metric impulse\n("tic-tac")', 'short-ramp (~0.1 s), km-scale metric\nhops near a body', 'ramp ≥ 10 s / 0.4 Mkm path (§5, §9);\nnear-body certification; plant scale;\n"metric is not a close-combat dodge" (§18A)', 'level hops: none (ENERGY-B: ~0 J);\nup-hops need paid speed or W2;\nSILENT hypersonic dash breaks ∇T=0 with air', 'wall–air interaction: 0.1-1 GJ into the\nair per sea-level hop (boom/heat);\ncontrol bandwidth; asymmetric collapse'),]
cx = [0, .13, .33, .57, .78]
for i, r in enumerate(T):
    for j, t in enumerate(r):
        c.text(cx[j], .97 - i * .245, t, fontsize=9.5 if i else 10.5, weight='bold' if (i == 0 or j == 0) else 'normal', transform=c.transAxes, va='top',
               color=('#7a5cff' if i >= 2 and j == 0 else '#d9611b' if i == 1 and j == 0 else '#1d2328'))
fig.suptitle('Builder prototype lane: what each wildcard buys, what it would need, and what would kill it (non-canon)', fontsize=13.5, y=.99)
fig.savefig(os.path.join(H, 'prototype_ledger.png'), dpi=105, facecolor=fig.get_facecolor())
for r in rows: print(r)
