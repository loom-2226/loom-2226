"""Figure for outing_bowl_dynamics.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib.colors import TwoSlopeNorm
H=os.path.dirname(os.path.abspath(__file__)); J=json.load(open(os.path.join(H,'outing_bowl_dynamics.json'))); S=np.load(os.path.join(H,'outing_bowl_dynamics_snaps.npz'))
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(13,8.4)); gs=f.add_gridspec(2,5,height_ratios=[1,0.95],hspace=0.45,wspace=0.35)
f.suptitle('Cushion over calm water (field centre 10 m up): does the bowl keep up? Coarse linear surface response (NON-CANON)',color=INK,fontsize=11)
eq=-J['equilibrium_depth_m']
for j,hv in enumerate((0.5,5.0)):
    a=f.add_subplot(gs[0,j*5//2:(j+1)*5//2+(1 if j==1 else 0)]) if False else f.add_subplot(gs[0,0:2] if j==0 else gs[0,2:5])
    L=J[f'series_{hv:g}s']; t=np.array(L['t'])
    a.plot(t,L['under_craft'],color=SH,lw=2,label='surface under the craft'); a.plot(t,L['old_site'],color=LA,lw=2,ls='--',label='surface at the first hover spot')
    a.axhline(eq,color=MUT,ls=':',lw=1); a.text(19.8,eq+0.3,'equilibrium bowl',ha='right',va='bottom',color=MUT,fontsize=8)
    a.axvspan(hv,hv+0.5,color='#e5e7eb'); a.text(hv+0.25,6.3,'30 m\njink',ha='center',color=MUT,fontsize=8)
    a.set_ylim(-11.5,7.5); a.set_xlim(0,20); a.set_xlabel('s'); a.set_ylabel('surface height (m)')
    r=J[f'hover_{hv:g}s']; a.set_title(f'{hv:g} s hover: bowl {r["depth_at_departure_m"]:.1f} m deep at departure ({100*r["bowl_fraction_at_departure"]:.0f}% of equilibrium)',color=INK,loc='left',fontsize=10)
    if j==0: a.legend(frameon=False,fontsize=8,loc='upper right')
hv=5.0; keys=[k for k in S.files if k.startswith('h5s_') and len(k.split('_'))==2]; keys=sorted(keys,key=lambda k: float(k.split('_')[1]))[:5]
lim=6.0; x0=-80; y0=-70
for i,k in enumerate(keys):
    a=f.add_subplot(gs[1,i]); e=S[k]; ts=float(k.split('_')[1])
    im=a.imshow(e.T,origin='lower',extent=(x0,x0+e.shape[0],y0,y0+e.shape[1]),cmap='RdBu_r',norm=TwoSlopeNorm(0,-lim,lim))
    xc=0 if ts<=hv else 30; a.plot([xc],[0],marker='o',ms=5,mfc='none',mec=INK); a.set_xlim(-50,80); a.set_ylim(-60,60)
    a.set_title(('at departure' if ts==hv else f'+{ts-hv:g} s'),color=INK,loc='left',fontsize=9.5); a.set_xlabel('m')
    if i==0: a.set_ylabel('m')
cb=f.colorbar(im,ax=f.axes[-5:],fraction=0.02,pad=0.01); cb.outline.set_visible(False); cb.set_label('surface height (m)',color=INK)
f.text(0.01,0.005,'Cushion switched on over 0.2 s; the 2 s ramp variant overshoots almost as much (9.8 m): the bowl period is ~5 s. Bottom: 5 s hover then jink, seen from above (circle = craft).\nDeep water, inviscid, small-slope theory on a bowl with 30° rims: timing meaningful, amplitudes coarse; breaking and foam not modelled.',color=MUT,fontsize=8)
f.savefig(os.path.join(H,'weave_bowl_dynamics.png'),dpi=150,bbox_inches='tight')
