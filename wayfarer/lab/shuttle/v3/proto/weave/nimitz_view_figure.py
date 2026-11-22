"""Observer view of a Weave shuttle low over calm water (hover bowl; pass). NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import outing_nimitz_view as nv
H=os.path.dirname(os.path.abspath(__file__)); J=json.load(open(os.path.join(H,'outing_nimitz_view.json'))); P=np.load(os.path.join(H,'outing_nimitz_pass.npz'))
INK='#1f2933'; MUT='#6b7280'; SEA='#1d4e89'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT})
ls=LightSource(azdeg=315,altdeg=40)
def shade(Z,steep):
    rgb=ls.shade(Z,cmap=plt.cm.Blues_r,vert_exag=1.0,blend_mode='soft',vmin=Z.min()-2,vmax=Z.max()+2)
    rgb[...,:3]=np.where(steep[...,None],0.95,rgb[...,:3]); return rgb
def hull(ax,xc,zc):
    u,v=np.mgrid[0:2*np.pi:30j,0:np.pi:15j]; ax.plot_surface(xc+10*np.cos(u)*np.sin(v),2*np.sin(u)*np.sin(v),zc+2*np.cos(v),color='#e5e7eb',linewidth=0,shade=True,zorder=10)
def domain(ax,xc,zc):
    u=np.linspace(0,2*np.pi,80)
    for a in (0,np.pi/2): ax.plot(xc+15*np.cos(u),15*np.sin(u)*np.cos(a),zc+15*np.sin(u)*np.sin(a),color='#93c5fd',lw=0.6,alpha=0.6)
f=plt.figure(figsize=(13,10.5)); gsm=f.add_gridspec(2,2,height_ratios=[1.5,1]); f.suptitle('A Weave shuttle low over calm water, as an observer above would see it (NON-CANON; whitewater not computed)',color=INK,fontsize=11.5)
# A hover bowl
ax=f.add_subplot(gsm[0,0],projection='3d'); ax.computed_zorder=False; xs=np.linspace(-32,32,161); X,Y=np.meshgrid(xs,xs); S=np.hypot(X,Y)
sg=np.linspace(0,64,641); eta1=nv.bowl(10.0,sg); Z=np.interp(S,sg,eta1)
gy,gx=np.gradient(Z,xs,xs); steep=np.degrees(np.arctan(np.hypot(gx,gy)))>25
ax.plot_surface(X,Y,Z,facecolors=shade(Z,steep),rstride=1,cstride=1,linewidth=0,antialiased=False,shade=False)
hull(ax,0,10); domain(ax,0,10); ax.set_box_aspect((1,1,0.55)); ax.set_xlim(-32,32); ax.set_ylim(-32,32); ax.set_zlim(-10,16); ax.view_init(elev=24,azim=-58); ax.dist=6.5; ax.set_axis_off()
ax.set_title('A  Hovering on the cushion, field centre 10 m up:\nthe sea is pulled into a bowl beneath it',color=INK,loc='left',fontsize=10)
# B pass
ax=f.add_subplot(gsm[0,1],projection='3d'); ax.computed_zorder=False; Q=P['s1.5']; Zp=Q[2]+10.0
gx=np.gradient(Zp,axis=0); gy=np.gradient(Zp,axis=1); steep=np.degrees(np.arctan(np.hypot(gx,gy)))>25
win=(Q[0]>55)&(Q[0]<135)
ix=np.where(win.any(1))[0]; sl=slice(ix.min(),ix.max()+1)
ax.plot_surface(Q[0][sl],Q[1][sl],Zp[sl],facecolors=shade(Zp[sl],steep[sl]),rstride=1,cstride=1,linewidth=0,antialiased=False,shade=False)
hull(ax,100,10); domain(ax,100,10); ax.set_box_aspect((1.6,1,0.55)); ax.set_xlim(55,135); ax.set_ylim(-30,30); ax.set_zlim(-10,16); ax.view_init(elev=24,azim=-62); ax.set_axis_off()
ax.set_title('B  Mid-pass at 125 m/s, field centre 10 m up:\nwater drawn up into the field, trough behind',color=INK,loc='left',fontsize=10)
# C hover table
a=f.add_subplot(gsm[1,0]); T=J['hover']; Zh=[r['Z_m'] for r in T]
a.plot(Zh,[r['depth_m'] for r in T],color='#2563eb',lw=2,label='bowl depth'); a.plot(Zh,[2*r['surface_radius_m'] for r in T],color='#d97706',lw=2,ls='--',label='disturbed patch width')
a.axvline(19,color=MUT,ls=':',lw=1); a.text(19.2,30,'field clears\nthe water',color=MUT,fontsize=8)
a.set_xlabel('hover height of field centre above water (m)'); a.set_ylabel('m'); a.set_xlim(1,21); a.set_ylim(0,42)
a.set_title('C  Hover disturbance vs height (R 15 m field)',color=INK,loc='left'); a.legend(frameon=False,fontsize=8.5)
for spine in ('top','right'): a.spines[spine].set_visible(False)
# D energy
a=f.add_subplot(gsm[1,1]); a.semilogy(Zh[1:],[r['wave_energy_J'] for r in T][1:],color='#0e7490',lw=2,label='wave energy released if it leaves (J)')
a.semilogy(Zh[1:],[r['displaced_t']*1e3 for r in T][1:],color=MUT,lw=2,ls='--',label='water displaced (kg)')
a.axvline(19,color=MUT,ls=':',lw=1); a.set_xlabel('hover height of field centre above water (m)'); a.set_xlim(1,21)
a.set_title('D  What collapses when the craft jinks away',color=INK,loc='left'); a.legend(frameon=False,fontsize=8.5)
for spine in ('top','right'): a.spines[spine].set_visible(False)
f.text(0.01,0.01,'White shading = surface slope > 25° (breaking-likely proxy, not a foam model). Hull drawn 20 m long. Hover = W2 cushion equilibrium (interface on an equipotential); pass = kinematic shift transport.',color=MUT,fontsize=8)
f.subplots_adjust(left=0.05,right=0.98,top=0.92,bottom=0.07,hspace=0.12,wspace=0.12)
f.savefig(os.path.join(H,'weave_nimitz_view.png'),dpi=150)
