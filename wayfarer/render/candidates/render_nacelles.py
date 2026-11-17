#!/usr/bin/env python3
"""Approval renders from exact source positions, no claim of CAD/D9 qualification."""
import json,math,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[2]
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
G=json.loads(GEO.read_text())
S=hashlib.sha256(GEO.read_bytes()).hexdigest()[:8]
OUT=Path(__file__).resolve().parent
INK="#f0f3f5"; SOFT="#9eb1bb"; BACK="#0d131c"
METRIC="#6bd6df"; GOLD="#d8b46b"; RING="#fa8370"; FRAME="#697783"
def er(az):
 a=math.radians(az)
 return np.array([math.cos(a),math.sin(a)])
def cyl(ax,x0,x1,r,alpha=1,n=14,nx=4):
 xx=np.linspace(x0,x1,nx)
 th=np.linspace(0,2*np.pi,n)
 X,T=np.meshgrid(xx,th)
 Y=ax[0]+r*np.cos(T)
 Z=ax[1]+r*np.sin(T)
 return X,Y,Z
def cone(x0,x1,r0,r1,cy=0,cz=0):
 xx=np.linspace(x0,x1,15)
 th=np.linspace(0,2*np.pi,28)
 X,T=np.meshgrid(xx,th)
 rr=np.linspace(r0,r1,len(xx))[None,:]
 return X,cy+rr*np.cos(T),cz+rr*np.sin(T)
def line(ax,p,q,c,lw=1.2,alpha=1):
 ax.plot([p[0],q[0]],[p[1],q[1]],[p[2],q[2]],color=c,lw=lw,alpha=alpha)
def draw_ship(ax):
 for mesh,col,alpha in [(cone(24,34.3,4.48,4.48),FRAME,.13),
                        (cone(34.3,39.3,4.4,2.95),FRAME,.48),
                        (cone(39.3,46.3,2.125,2.125,0,-.26),FRAME,.38),
                        (cone(46.3,53.3,2.125,3.0,0,-.26),"#bb8b68",.6)]:
  ax.plot_surface(*mesh,color=col,alpha=alpha,linewidth=0,shade=False)
 for az in (40,140,220,320):
  u=er(az)
  for xx in (34.3,53.3):
   line(ax,(xx,4.75*u[0],4.75*u[1]),(xx,6.75*u[0],6.75*u[1]),SOFT,.65,.45)
  for rr in (4.75,6.75):
   line(ax,(34.3,rr*u[0],rr*u[1]),(53.3,rr*u[0],rr*u[1]),SOFT,.65,.45)
def draw_nacelles(ax,state):
 R=4.05 if state=="torch" else 4.6
 for az in (0,90,180,270):
  u=er(az)
  a=np.array([R*u[0],R*u[1]-.26])
  mesh=cyl(a,39.5,54.3,.6)
  ax.plot_surface(*mesh,color=METRIC,alpha=.85,linewidth=0,shade=True)
  for x,base in ((40.5,2.125),(49.5,2.525)):
   p=(x,base*u[0],base*u[1]-.26)
   q=(x,(R-.6)*u[0],(R-.6)*u[1]-.26)
   line(ax,p,q,GOLD,3)
  if state=="torch":
   v=np.array([-u[1],u[0]])
   for side in (-1,1):
    yz=(R+.91)*u+side*.46*v
    line(ax,(50.6876,yz[0],yz[1]-.26),
         (54.3,yz[0],yz[1]-.26),RING,4)
 if state=="Metric":
  t=np.linspace(0,2*np.pi,361)
  ax.plot(np.full_like(t,53.9),4.6*np.cos(t),4.6*np.sin(t)-.26,
          color=RING,lw=4,alpha=1)
  for a in range(0,360,45):
   q=math.radians(a)
   ax.scatter([53.9],[4.6*math.cos(q)],[4.6*math.sin(q)-.26],
              color=INK,s=12)
def make(state):
 fig=plt.figure(figsize=(13.6,7.7),dpi=160)
 fig.patch.set_facecolor(BACK)
 ax=fig.add_axes([.035,.10,.68,.79],projection="3d")
 ax.set_facecolor(BACK)
 draw_ship(ax)
 draw_nacelles(ax,state)
 ax.view_init(elev=21,azim=-52)
 ax.set_xlim(31,55)
 ax.set_ylim(-7,7)
 ax.set_zlim(-7,7)
 ax.set_box_aspect((2.4,1.4,1.4))
 ax.set_axis_off()
 title="TORCH / TUCKED" if state=="torch" else "METRIC / RING LOCKED"
 fig.text(.06,.945,f"WAYFARER 2226  |  {title}",color=INK,size=19,weight="bold")
 fig.text(.06,.905,"Four source nacelles at 0° / 90° / 180° / 270°  •  Candidate, not released canon",color=SOFT,size=10)
 fig.text(.715,.74,"GEOMETRY",color=INK,size=10,weight="bold")
 info=[
   ("Nacelle cylinder","R 0.60 m × 14.8 m"),
   ("Longitudinal","x 39.5–54.3 m"),
   ("Axis radius","r 4.05 m tucked" if state=="torch" else "r 4.60 m deployed"),
   ("Linkage","two radial parallel links × 4"),
   ("Aft RCS","25° outward × 4 aft"),
   ("Hoop","8 × 45° tail arms"),
   ("Ring lock","folded along nacelle" if state=="torch" else "x 53.9, R 4.6, tube r 0.35"),
   ("Torch-chain pin","y +0.03, z −0.26 m"),
 ]
 for j,(k,v) in enumerate(info):
  yy=.70-j*.064
  fig.text(.715,yy,k,color=SOFT,size=9)
  fig.text(.715,yy-.023,v,color=INK,size=9,weight="semibold")
 fig.text(.06,.056,"Approximate candidate presentation; D9 uses independent exact B-rep source STEP. Torch hot-fin deployed span omitted for clarity.",color=SOFT,size=8)
 fig.text(.06,.029,f"Source geometry SHA-256: {S}…  |  no canon GLB or canon_glb.json change",color=SOFT,size=8)
 dst=OUT/f"wayfarer_nacelle_{state}_{S}.png"
 fig.savefig(dst,facecolor=BACK)
 plt.close(fig)
 print("RENDER",dst,dst.stat().st_size)
for state in ("torch","Metric"):make(state)
