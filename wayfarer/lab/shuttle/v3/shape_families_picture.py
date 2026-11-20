"""Picture for shape_families.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, math, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import shape_families as SF
d = json.load(open("shape_families.json")); F = d["families"]; B4 = d["reference"]["B4-S (today)"]
names = list(F); cols = ["#2f6fb0", "#8e44ad", "#16a085", "#7f8c8d", "#d35400", "#c0392b"]
fig = plt.figure(figsize=(17, 9.5))
for i, n in enumerate(names):
    a = fig.add_axes([0.03 + i * 0.16, 0.56, 0.145, 0.36]); fam = SF.FAM[n]
    sec = fam["sec"]; zc = F[n]["fit"]["center_z_m"]
    a.add_patch(Circle((0, zc), 2.4, fc="#f2f3f4", ec="#95a5a6", lw=1))
    a.add_patch(Circle((0, zc), 2.15, fc="none", ec="#95a5a6", ls="--", lw=.8))
    p = np.vstack([sec, sec[:1]]); a.fill(p[:, 0], p[:, 1], color=cols[i], alpha=.75); a.plot(p[:, 0], p[:, 1], color="k", lw=.8)
    a.set_xlim(-2.6, 2.6); a.set_ylim(zc - 2.6, zc + 2.6); a.set_aspect("equal"); a.axis("off")
    a.set_title(n.replace(", ", ",\n").replace(" lifting", "\nlifting"), fontsize=9, color=cols[i])
    f = F[n]; a.text(0, zc - 2.75, f"{f['volume_m3']:.0f} m³ · crossrange {f['earth_entry']['crossrange_km']:.0f} km", ha="center", fontsize=8, va="top")
fig.text(0.03, 0.95, "Biggest cross-section of each family inside the bay (grey 2.4 m bore, dashed 2.15 m envelope)", fontsize=10)
# volume vs crossrange
a = fig.add_axes([0.05, 0.07, 0.42, 0.38])
for i, n in enumerate(names):
    a.scatter(F[n]["volume_m3"], F[n]["earth_entry"]["crossrange_km"], s=90, color=cols[i], zorder=3); a.text(F[n]["volume_m3"] + 2, F[n]["earth_entry"]["crossrange_km"] + 25, n.split()[0], fontsize=9)
a.scatter(B4["volume_m3"], B4["earth_entry"]["crossrange_km"], s=140, marker="*", color="k", zorder=3); a.text(B4["volume_m3"] + 2, B4["earth_entry"]["crossrange_km"] + 25, "B4-S today", fontsize=9)
a.axvline(d["basis"]["volume_needed_W2_m3"], color="#c0392b", ls="--"); a.text(d["basis"]["volume_needed_W2_m3"] + 1, 1180, "W2 hull-only\n111 m³", color="#c0392b", fontsize=8, va="top")
a.set_xlabel("enclosed volume, m³"); a.set_ylabel("Earth re-entry crossrange, km (58 t)")
a.set_title("The trade: volume vs reach from orbit", fontsize=10); a.set_xlim(0, 135); a.set_ylim(0, 1250); a.grid(alpha=.3)
# subsonic L/D
b = fig.add_axes([0.55, 0.07, 0.42, 0.38]); labs, vals, cc = [], [], []
for i, n in enumerate(names):
    for w, x in F[n]["wings"].items(): labs.append(f"{n.split()[0]} {w.split(' (')[0].split('/')[0]}"); vals.append(x["subsonic_LD_max"]); cc.append(cols[i])
labs.append("B4-S today"); vals.append(B4["wings"]["fold (B4)"]["subsonic_LD_max"]); cc.append("k")
b.barh(range(len(vals)), vals, color=cc); b.set_yticks(range(len(vals))); b.set_yticklabels(labs, fontsize=8); b.invert_yaxis()
b.set_xlabel("subsonic glide L/D (ROM)"); b.set_title("Glide: span is what moves it", fontsize=10); b.grid(axis="x", alpha=.3)
fig.suptitle("Shuttle v3 step 3: shape families in Wayfarer's bay (ROM, same tools as B4)", fontsize=13, y=0.995)
fig.savefig("shape_families.png", dpi=120)
