"""Shaded preview of the printed shuttle STL (painter's algorithm). ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np, struct, os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE = os.path.dirname(os.path.abspath(__file__))
d = open(os.path.join(HERE, 'parts', 'shuttle_v1_1to100.stl'), 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
F = np.frombuffer(d[84:], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')], count=n)['v'].astype(float)
F = F - F.reshape(-1, 3).mean(0)
# back to ship-like axes for viewing: print (X=Y_ship, Y=Z_ship, Z=tail-up) -> x along ship
G = np.stack([-F[..., 2], -F[..., 0], F[..., 1]], -1)   # proper rotation: x = toward the tail, y = -ship Y (port), z = ship Z (up)
def view(ax, az, el, title):
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    V = G @ (Rx @ Rz).T
    nrm = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); nl = np.linalg.norm(nrm, axis=1) + 1e-12; nrm /= nl[:, None]
    vis = nrm[:, 1] < 0
    L = np.array([-0.4, -0.7, 0.6]); L /= np.linalg.norm(L); sh = np.clip(0.30 + 0.70 * np.abs(nrm @ L), 0, 1)
    order = np.argsort(-V[:, :, 1].mean(1)); order = order[vis[order]]
    cols = np.c_[sh * 0.78, sh * 0.82, sh * 0.86][order]
    ax.add_collection(PolyCollection(V[order][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=0.6, antialiaseds=False))
    ax.set_xlim(-70, 70); ax.set_ylim(-26, 26); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, loc='left', fontsize=11, weight='bold')
fig, axs = plt.subplots(3, 1, figsize=(11, 10.5), dpi=120); fig.patch.set_facecolor('#f6f5f2')
view(axs[0], 0, 75, 'From above, as seen through the open bay doors: gullwing crew-door outline')
view(axs[1], 0, 20, 'Starboard side: spine groove with the two engraved blade outlines')
view(axs[2], 180, 20, 'Port side: heat-shield edges and the four belly-nozzle pits')
fig.suptitle('Wayfarer v1 shuttle, 1:100 print (128 x 38 mm) - NON-CANON, PLACEHOLDER profile', x=0.04, ha='left', fontsize=14, weight='bold')
fig.savefig(os.path.join(HERE, 'shuttle_print_preview.png'), facecolor=fig.get_facecolor())
