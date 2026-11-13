"""Bay door leaf swing diagram, from the same cross-section as the STL. ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, math, os, importlib.util, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('dl', os.path.join(HERE, 'door_leaf.py')); dl = importlib.util.module_from_spec(sp); sp.loader.exec_module(dl)
loops, _ = dl.section(); loops = sorted(loops, key=lambda c: -abs(dl.signed_area(c)))
INK, HOT, MUT = '#1d2228', '#d9773a', '#6b737c'
fig, ax = plt.subplots(figsize=(10, 7.5), dpi=110); fig.patch.set_facecolor('#f6f5f2'); ax.set_facecolor('#f6f5f2'); ax.set_aspect('equal'); ax.axis('off')
t = np.radians(np.linspace(0, 180, 400))
for a0, a1 in ((0, dl.A_H), (180 - dl.A_H, 180)):
    tt = np.radians(np.linspace(a0, a1, 200))
    ax.fill(np.r_[45 * np.cos(tt), 43 * np.cos(tt[::-1])], np.r_[45 * np.sin(tt), 43 * np.sin(tt[::-1])], color='#cfd3d1', ec=INK, lw=0.8)
ax.text(40, 10, 'hull shell', color=MUT, fontsize=10)
c = np.array(dl.PIVOT)
def draw(loop, ang, mirror, col, alpha):
    p = loop.copy()
    R = np.array([[math.cos(math.radians(-ang)), -math.sin(math.radians(-ang))], [math.sin(math.radians(-ang)), math.cos(math.radians(-ang))]])
    p = (p - c) @ R.T + c
    if mirror: p[:, 0] *= -1
    ax.fill(p[:, 0], p[:, 1], color=col, alpha=alpha, ec=INK, lw=0.6)
for mirror in (False, True):
    draw(loops[0], 0, mirror, '#8a8f94', 0.9)
    for a in (25, 50): draw(loops[0], a, mirror, '#b9bfbc', 0.35)
    draw(loops[0], 75.1, mirror, HOT, 0.9)
    for h in loops[1:]: draw(h, 0, mirror, 'white', 1); draw(h, 75.1, mirror, 'white', 1)
ax.plot([c[0], -c[0]], [c[1], c[1]], 'o', color=INK, ms=3)
ax.annotate('pin: 1.75 mm filament\nthrough the hinge boss', xy=(c[0] + 0.5, c[1] - 0.6), xytext=(30, 30), fontsize=10, arrowprops=dict(arrowstyle='->', color=INK))
ax.text(-13, 72, 'OPEN: vertical (75 deg swing)', color=HOT, fontsize=11, weight='bold', ha='center')
ax.text(0, 47.5, 'CLOSED', color=INK, fontsize=11, weight='bold', ha='center')
ax.text(0, 30, 'shuttle bay', color=MUT, fontsize=11, ha='center')
ax.set_xlim(-55, 55); ax.set_ylim(20, 78)
fig.text(0.04, 0.95, 'Wayfarer 1:100 bay doors: one pin each, swing closed to vertical', fontsize=15, weight='bold', color=INK)
fig.text(0.04, 0.915, 'Section across the ship, looking forward. Leaves 138 mm long, 1.6 mm thick; hinge boss 3.5 mm. Swing clears the hull to 80 deg.', fontsize=10, color=MUT)
fig.savefig(os.path.join(HERE, 'bay_door_swing_1to100.png'), facecolor=fig.get_facecolor())
