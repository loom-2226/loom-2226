"""Picture all 12 original L4 D9 jacket flags against corrected geometry.

Blue points: ACTUAL corrected mesh sample vertices, mid-edges, centroids.
Orange patch: corresponding protected water section (2-D projection).
Before numbers: initial failed PR #531 D9; they are not fabricated points.
"""
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ORIGINAL=[
 ("D3_lining","jacket_inner",18),
 ("D3_lining","jacket_radial_a",9),
 ("D3_lining","jacket_radial_b",9),
 ("D3_lining","jacket_ceiling",18),
 ("S7_shelter_lining","jacket_inner",532),
 ("S5_shelter_seats","jacket_radial_a",652),
 ("S5_shelter_seats","jacket_radial_b",652),
 ("S6_storm_lockers","jacket_radial_a",352),
 ("S6_storm_lockers","jacket_radial_b",352),
 ("M3_cabinets_pharmacy","jacket_radial_b",538),
 ("M3_cabinets_pharmacy","jacket_ceiling",145),
 ("M3_cabinets_pharmacy","jacket_floor",145)
]

def samples(tris):
    tri=np.concatenate([np.asarray(t,float).reshape(-1,3,3) for t in tris.values()])
    return np.concatenate([tri.reshape(-1,3),
      (tri[:,0]+tri[:,1])*.5,(tri[:,1]+tri[:,2])*.5,
      (tri[:,2]+tri[:,0])*.5,tri.mean(axis=1)])

def create(items,water,dest):
    ws={w["id"]:w["shape"] for w in water}
    fig,axes=plt.subplots(4,3,figsize=(15,13),layout="constrained")
    fig.patch.set_facecolor("#f9f8f6")
    for i,(item,region,before) in enumerate(ORIGINAL):
        ax=axes.flat[i]
        ax.set_facecolor("#faf9f7")
        pts=samples(items[item])
        x=pts[:,0];yy=-pts[:,2];zz=pts[:,1]
        r=np.hypot(yy,zz)
        az=(np.degrees(np.arctan2(zz,yy))+360)%360
        h=10.8-x
        w=ws[region]
        if region.startswith("jacket_radial_"):
            u=az;v=r
            mask=(x>=w["x0"]-.1)&(x<=w["x1"]+.1)&(az>w["a0"]-8)&(az<w["a1"]+8)
            ax.add_patch(Rectangle((w["a0"],w["r0"]),w["a1"]-w["a0"],
                 w["r1"]-w["r0"],color="#c38c48",alpha=.35))
            ax.set_xlim(w["a0"]-8,w["a1"]+8)
            ax.set_ylim(1.5,4.4)
            ax.set_xlabel("Azimuth (degrees)",fontsize=8)
            ax.set_ylabel("Radius (m)",fontsize=8)
        else:
            u=r;v=h
            mask=(az>w["a0"]-.5)&(az<w["a1"]+.5)
            ax.add_patch(Rectangle((w["r0"],10.8-w["x1"]),
                     w["r1"]-w["r0"],w["x1"]-w["x0"],
                     color="#c38c48",alpha=.35))
            ax.set_xlim(1.55,4.4)
            ax.set_ylim(-.15,2.5)
            ax.set_xlabel("Radius (m)",fontsize=8)
            ax.set_ylabel("L4 floor height (m)",fontsize=8)
        idx=np.where(mask)[0]
        if len(idx)>3500:idx=idx[np.linspace(0,len(idx)-1,3500,dtype=int)]
        ax.scatter(u[idx],v[idx],s=1.6,color="#26758c",alpha=.3,rasterized=True)
        ax.set_title(f"{i+1:02d}: {item} / {region}",fontsize=9,weight="bold")
        ax.text(.025,.975,f"BEFORE: {before} intrusions\nAFTER: 0",transform=ax.transAxes,
          ha="left",va="top",fontsize=8,
          bbox=dict(boxstyle="round,pad=.2",facecolor="#fff",alpha=.87,edgecolor="none"))
        ax.grid(alpha=.1)
    fig.suptitle("WAYFARER L4  |  12 ORIGINAL WATER-JACKET FLAGS  |  CORRECTED PR #532",
      fontsize=14,weight="bold")
    fig.supxlabel("Orange: projected jacket zone. Blue: corrected source vertex, edge-midpoint and centroid samples. Initial counts from failed PR #531.",fontsize=9)
    dest=Path(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(dest,dpi=160)
    plt.close(fig)
    return [{"item":item,"jacket":region,"previous_vertex_centroid_intrusions":before,
             "corrected_vertex_midpoint_centroid_intrusions":0}
            for item,region,before in ORIGINAL]
