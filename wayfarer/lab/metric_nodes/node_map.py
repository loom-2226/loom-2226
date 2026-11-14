import json, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/'
G = json.load(open(W + 'results/out/wayfarer_v05_geometry.json'))
HW = json.load(open(W + 'print/hardware_1to100/hardware_inventory.json'))
az = lambda p: (math.degrees(math.atan2(p[2], p[1])) + 360) % 360
ad = lambda a, b: abs((a - b + 180) % 360 - 180)
nf = [f for f in G['features'] if f['kind'] == 'node_face']
others = [f for f in G['features'] if f['kind'] in ('window', 'hatch', 'hold_door', 'camera')]
LONG = [43.4, 136.6, 223.4, 316.6]
def hw_hit(f):
    x, a = f['pos'][0], az(f['pos']); R = math.hypot(f['pos'][1], f['pos'][2])
    for h in HW:
        if h['name'] == 'bow_sensors': continue
        L = max(h['size_m'][0], .2); C = max(h['size_m'][1], h['size_m'][2], .2)
        if abs(x - h['x']) < L / 2 + .33 and math.radians(ad(a, h['az'])) * R < C / 2 + .33: return h['name']
    for o in others:
        if abs(x - o['pos'][0]) < .6 and math.radians(ad(a, az(o['pos']))) * R < .6: return o['kind']
    return None
CL = [  # class, colour (validated categorical order), label
 ('torch', '#e34948', 'On the torch chain: thrust cone, shield, reactor, magnetic nozzle (hot, high field)'),
 ('strake', '#eb6834', 'Under a stowed strake, over a longeron (the open placement conflict)'),
 ('door', '#e87ba4', 'On a bay-door leaf (moves)'),
 ('hw', '#eda100', 'On or within 0.15 m of hardware, a window, hatch or camera'),
 ('bow', '#6250d6', 'Bow shoulder: faces the dust flow, no mount structure'),
 ('ok', '#2a78d6', 'Clear hull skin')]
def cls(f):
    x, a = f['pos'][0], az(f['pos'])
    if 'on_torch_chain' in f['flags']: return 'torch'
    if 'under_stowed_strake' in f['flags'] or (14 <= x <= 34.3 and min(ad(a, l) for l in LONG) < 3): return 'strake'
    if 'on_bay_door' in f['flags']: return 'door'
    if hw_hit(f) or any(k.startswith('overlaps') for k in f['flags']): return 'hw'
    if 'faces_dust_flow_bow_first' in f['flags']: return 'bow'
    return 'ok'
C = [cls(f) for f in nf]
fig = plt.figure(figsize=(13, 8.2), dpi=110); fig.patch.set_facecolor('#fcfcfb')
ax = fig.add_axes([0.05, 0.27, 0.93, 0.585]); ax.set_facecolor('#fcfcfb')
# body zones
Z = [(0, 2.35, 'Bow'), (2.35, 14, 'Habitat L1-L5'), (14, 34.3, 'Midship: bay, tanks, strakes'), (34.3, 39.3, 'Thrust\ncone'), (39.3, 46.3, 'Reactor'), (46.3, 53.3, 'Magnetic\nnozzle')]
for i, (a, b, n) in enumerate(Z):
    ax.add_patch(Rectangle((a, 0), b - a, 360, fc='#f1efe9' if i % 2 else '#f7f6f2', ec='none', zorder=0))
    ax.text((a + b) / 2, -4, n.replace('\n', ' '), ha='center', va='bottom', fontsize=8.5, color='#52514e', clip_on=False)
for a0 in (40, 140, 220, 320):   # stowed strakes and hot fins
    ax.add_patch(Rectangle((14, a0 - 12.7), 18.3, 25.4, fc='#eb6834', alpha=.10, ec='#eb6834', lw=.6, zorder=1))
    ax.add_patch(Rectangle((34.3, a0 - 4.3), 19, 8.6, fc='#52514e', alpha=.18, ec='none', zorder=1))
for l in LONG: ax.plot([14, 34.3], [l, l], color='#52514e', lw=1, ls=(0, (4, 3)), zorder=2)
ax.add_patch(Rectangle((18.25, 57.77), 13.8, 64.46, fc='#e87ba4', alpha=.12, ec='#e87ba4', lw=.8, zorder=1))
ax.plot([18.25, 32.05], [90, 90], color='#e87ba4', lw=.8, zorder=2)
for h in HW:
    if h['name'] == 'bow_sensors': continue
    L = max(h['size_m'][0], .2); Cc = max(h['size_m'][1], h['size_m'][2], .2); da = math.degrees(Cc / 4.5)
    ax.add_patch(Rectangle((h['x'] - L / 2, h['az'] - da / 2), L, da, fc='#8e8c86', ec='none', alpha=.6, zorder=2))
for o in others: ax.plot(o['pos'][0], az(o['pos']), marker='s', ms=3.5, color='#8e8c86', zorder=2)
# nodes
for k, col, _ in CL:
    pts = [(f['pos'][0], az(f['pos'])) for f, c in zip(nf, C) if c == k]
    if pts: ax.scatter(*zip(*pts), s=46, color=col, edgecolor='#fcfcfb', linewidth=1.2, zorder=4)
# labels on the map
ax.text(23.2, 40, 'strake 40°', fontsize=7, color='#b5481c', ha='center', va='center', zorder=5)
ax.text(25.15, 103, 'bay doors', fontsize=7.5, color='#b44b77', ha='center', zorder=5)
ax.text(14.2, 47.5, 'longeron', fontsize=6.5, color='#52514e', zorder=5)
ax.text(52.9, 44.8, 'hot fin', fontsize=6.5, color='#52514e', ha='right', zorder=5)
ax.set_xlim(-0.3, 53.6); ax.set_ylim(0, 360); ax.invert_yaxis()
ax.set_yticks(range(0, 361, 45)); ax.set_xticks(range(0, 54, 5))
ax.set_xlabel('x from bow (m)', color='#52514e'); ax.set_ylabel('azimuth (deg)', color='#52514e')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.tick_params(colors='#52514e', length=0); ax.grid(color='#e4e3df', lw=.6, zorder=0)
fig.text(0.05, 0.955, "Wayfarer's 208 Metric node faces against the hull (13 rings x 16, the PR #184 baseline)", fontsize=14, weight='bold')
fig.text(0.05, 0.925, 'Hull unrolled: bow left, every azimuth. Grey blocks = exterior hardware. Only 20 of the 208 have any mount mass booked, and no node module has a mass line.', fontsize=9, color='#52514e')
cnt = {k: C.count(k) for k, _, _ in CL}
for i, (k, col, lab) in enumerate(CL):
    yy = 0.20 - (i % 3) * 0.055; xx = 0.05 + (i // 3) * 0.47
    fig.text(xx, yy, '●', fontsize=14, color=col, va='center')
    fig.text(xx + .02, yy, f'{cnt[k]:>3}  {lab}', fontsize=9.5, color='#0b0b0b', va='center')
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_conflict_map.png'), facecolor=fig.get_facecolor())
print(cnt, sum(cnt.values()))
