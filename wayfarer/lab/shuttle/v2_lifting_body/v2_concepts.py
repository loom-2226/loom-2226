"""Shuttle v2 lifting-body concepts A/B/C - NON-CANON sketch.
Envelope: 12.8 m long, 4.3 m allowed dia (SHUTTLE_SIZER_REPORT).
Venus surface 92 bar ext / 1 bar int -> crew pressure vessel kept,
moved INSIDE a non-pressure aeroshell. Masses are screen deltas vs
v1 midpoint core dry 30.021 t; G8 docked limit 34.2 t."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyBboxPatch, Rectangle
L, ENV = 12.8, 4.3
V1_CORE, LIMIT = 30.021, 34.2
C = dict(A=dict(t="A  Hidden sphere", H=2.9, W=4.2,
           ves=[("s",5.2,0,2.5)], dves=0.0, dshell=1.0,
           note="v1 sphere, faired in.\nLowest risk."),
         B=dict(t="B  Twin spheres", H=2.35, W=4.25,
           ves=[("s",7.8,-1.05,2.0),("s",7.8,1.05,2.0)], dves=0.4, dshell=1.5,
           note="Flattest wedge.\n2 hatches + tunnel."),
         C=dict(t="C  Flat pressure tube", H=2.45, W=4.1,
           ves=[("c",5.4,0,2.1,3.2)], dves=1.6, dshell=0.8,
           note="Sleek, most floor.\n+30-60% vessel mass."))
xs = np.linspace(0, L, 200)
def half_w(x, W):   # planform: blunt nose, widens to W by 8.5 m
    return W/2*np.clip(np.sqrt(np.clip(x/8.5,0,1))*1.0,0,1)*np.where(x>11.6,1-(x-11.6)/1.2*0.25,1)
def top(x, H):      # side profile upper line, flat belly at 0
    return H*np.clip(np.sin(np.pi*np.clip(x/L*0.95+0.02,0,1))**0.6,0,1)*np.where(x<1,0.55+0.45*x,1)
fig, ax = plt.subplots(4,3, figsize=(11,9.6), gridspec_kw=dict(height_ratios=[0.62,0.42,0.62,0.42]))
ink, ves_c, tps = "#1d2733", "#c0392b", "#555"
for j,(k,c) in enumerate(C.items()):
    # plan
    a=ax[0,j]; hw=half_w(xs,c["W"])
    a.fill_between(xs,-hw,hw,color="#dfe6ee",ec=ink,lw=1.2)
    a.plot([0,1.6],[0,0],color="#2e86c1",lw=6,solid_capstyle="round")  # glazing
    for v in c["ves"]:
        if v[0]=="s": a.add_patch(Circle((v[1],v[2]),v[3]/2,fill=False,ec=ves_c,lw=1.6,ls="--"))
        else: a.add_patch(FancyBboxPatch((v[1]-v[4]/2,-v[3]/2),v[4],v[3],boxstyle="round,pad=0,rounding_size=1.0",fill=False,ec=ves_c,lw=1.6,ls="--"))
    a.add_patch(Rectangle((9.6,-0.5),2.6,1.0,fill=False,ec="#7f8c8d",ls=":"))  # rotor kit / torch bay
    a.text(10.9,0,"kit +\ntorch",ha="center",va="center",fontsize=7,color="#7f8c8d")
    a.set_title(c["t"],fontsize=13,weight="bold",loc="left"); a.set_xlim(-0.5,13.3); a.set_ylim(-2.6,2.6)
    a.set_aspect("equal"); a.axis("off"); a.text(-0.4,-2.5,"PLAN (nose left)",fontsize=7,color="#888")
    # side
    a=ax[1,j]; t=top(xs,c["H"])
    a.fill_between(xs,0,t,color="#dfe6ee",ec=ink,lw=1.2); a.plot(xs,np.zeros_like(xs),color=tps,lw=4)
    for v in c["ves"][:1]:
        if v[0]=="s": a.add_patch(Circle((v[1],0.18+v[3]/2),v[3]/2,fill=False,ec=ves_c,lw=1.6,ls="--"))
        else: a.add_patch(FancyBboxPatch((v[1]-v[4]/2,0.18),v[4],v[3],boxstyle="round,pad=0,rounding_size=1.0",fill=False,ec=ves_c,lw=1.6,ls="--"))
    a.set_xlim(-0.5,13.3); a.set_ylim(-0.4,3.3); a.set_aspect("equal"); a.axis("off")
    a.text(-0.4,-0.38,"SIDE  belly = heat shield",fontsize=7,color="#888")
    # section
    a=ax[2,j]
    a.add_patch(Circle((0,0),ENV/2,fill=False,ec="#999",ls="--",lw=1))
    th=np.linspace(0,2*np.pi,240); n=3
    sx=c["W"]/2*np.sign(np.cos(th))*np.abs(np.cos(th))**(2/n); sy=c["H"]/2*np.sign(np.sin(th))*np.abs(np.sin(th))**(2/n)
    a.fill(sx,sy,fc="#dfe6ee",ec=ink,lw=1.2); m=(th>np.radians(195))&(th<np.radians(345)); a.plot(sx[m],sy[m],color=tps,lw=4)
    for v in c["ves"]:
        d=v[3]; a.add_patch(Circle((v[2],0),d/2,fill=False,ec=ves_c,lw=1.8,ls="--"))
    a.set_xlim(-2.4,2.4); a.set_ylim(-2.3,2.75); a.set_aspect("equal"); a.axis("off")
    a.text(0,-2.25,f"{c['W']:.2f} W x {c['H']:.2f} H m in 4.3 m bore",ha="center",fontsize=8)
    a.text(0,c["H"]/2+0.15,c["note"],ha="center",fontsize=8,color=ink)
    # mass bar
    a=ax[3,j]; core=V1_CORE+c["dves"]+c["dshell"]
    a.barh([1],[V1_CORE],color="#aab7c4"); a.barh([1],[c["dshell"]],left=V1_CORE,color="#5d6d7e",label="aeroshell/TPS")
    a.barh([1],[c["dves"]],left=V1_CORE+c["dshell"],color=ves_c,label="vessel")
    a.axvline(LIMIT,color="k",lw=2); a.text(LIMIT,1.55,"G8 34.2 t",ha="center",fontsize=8)
    a.set_xlim(25,36); a.set_ylim(0.4,1.8); a.set_yticks([])
    a.set_title(f"core dry ~{core:.1f} t  margin {LIMIT-core:+.1f} t",fontsize=10)
    a.spines[["top","right","left"]].set_visible(False)
    if j==0: a.legend(fontsize=7,loc="upper left",frameon=False); a.text(25.3,1.0,"v1 mid 30.0 t",fontsize=7,va="center")
fig.suptitle("Shuttle v2 - lifting body, pressure vessel INSIDE  (NON-CANON sketch)",fontsize=14,weight="bold",y=0.995)
fig.text(0.5,0.005,"Red dashed = 92 bar crew vessel. Grey dashed = 4.3 m allowed envelope. Masses are midpoint screen deltas; "
         "pessimistic case fails for v1 too.",ha="center",fontsize=8,color="#555")
plt.tight_layout(rect=[0,0.015,1,0.98]); plt.savefig("shuttle_v2_concepts.png",dpi=110)
