"""Visual operating card for the Weave shuttle (step 3). NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
H=os.path.dirname(os.path.abspath(__file__))
INK='#1f2933'; MUT='#6b7280'; CU='#0e7490'; SH='#2563eb'; CO='#64748b'; WARN='#d97706'; BAD='#dc2626'; OK='#16a34a'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(13,9.6)); f.suptitle("Weave shuttle 'Tic Tac' — operating card (experimental prototype, NON-CANON)",color=INK,fontsize=13,x=0.02,ha='left',y=0.985)
f.text(0.02,0.945,"'Tic Tac' 12.8 × 3.8 m capsule · 6 couches + rover kit or 6 m³ cargo · 45.4 t dry · R 15 m field · torch, parachutes   (D derived · A assumed · U unknown)",color=MUT,fontsize=9.5)
tiles=[('W2 CUSHION',CU,['Hover with no downwash','air ≤ 0.16 m/s, ~140 Pa  (D)','Vertical lift to 2 km in ~20 s','3.1 GJ, 154 MW: design assumption  (A)','Cabin weightless']),
       ('WEAVE SHIFT',SH,['30 m sidestep in 0.5 s: 71 g','0.66 g felt in 20 m test-hull model  (D)','200 m in 3 s: 13 g, ~0.02 g felt','Own air: no residual wake (ideal fluid)  (D)','Quiet if ≥ 0.4 s per 30 m  (D)']),
       ('ASCENT & FALLBACK',CO,['Orbit: cushion to 2 km + 1.4 g torch','19.0 of 23.1 t water  (A, lane calc.)','Entry: blunt body, ~480 km crossrange  (D)','Field off: parachutes (no wings)','Chutes ~17,400 m²: screening assumption  (A)'])]
for i,(t,c,lines) in enumerate(tiles):
    x0=0.02+i*0.327; ax=f.add_axes([x0,0.6,0.31,0.32]); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0.0,rounding_size=0.04',fc=c,alpha=0.08,ec=c,lw=1.5,transform=ax.transAxes))
    ax.text(0.05,0.88,t,color=c,fontsize=13,weight='bold',transform=ax.transAxes)
    for k,l in enumerate(lines): ax.text(0.05,0.72-k*0.145,l,color=INK if k%2==0 else MUT,fontsize=10.5 if k%2==0 else 9.5,transform=ax.transAxes)
# motion vs felt
a=f.add_axes([0.06,0.08,0.26,0.42]); lab=['dash\n200 m/3 s','dodge\n30 m/0.5 s','dodge\n30 m/0.4 s']; mot=[13.1,71,110]; felt=[0.018,0.66,1.07]; x=np.arange(3)
a.bar(x-0.18,mot,0.34,color='#cbd5e1',label='shuttle motion'); a.bar(x+0.18,felt,0.34,color=SH,label='occupants feel')
for i in range(3): a.text(x[i]-0.18,mot[i]*1.25,f'{mot[i]:.0f} g',ha='center',fontsize=8.5,color=INK); a.text(x[i]+0.18,felt[i]*1.25,f'{felt[i]:.2g} g',ha='center',fontsize=8.5,color=INK)
a.set_yscale('log'); a.set_ylim(0.01,2000); a.set_xticks(x); a.set_xticklabels(lab,fontsize=8.5); a.set_title('Manoeuvre vs felt load (D, 20 m test-hull model)',color=INK,loc='left'); a.legend(frameon=False,fontsize=8,loc='upper left')
# height ladder over water
a=f.add_axes([0.42,0.08,0.22,0.42]); a.set_xlim(0,1); a.set_ylim(0,110)
zones=[(0,5.1,OK,'field fails: drop onto the\nhull, estimated survivable'),(5.1,32,BAD,'field fails in a slow\nhover: no recovery'),(32,66,WARN,'parachutes, if they inflate\nin 2.5–6 s (assumption)'),(66,110,'#e5e7eb','parachutes')]
ys={0:3.0,1:27.0,2:49.0,3:88.0}
for k,(lo,hi,c,t) in enumerate(zones): a.bar(0.18,hi-lo,0.3,bottom=lo,color=c,alpha=0.8); a.text(0.38,ys[k],t,va='center',fontsize=8,color=INK)
a.axhline(19,color=CU,ls='--',lw=1.2); a.text(0.38,15.5,'below ~19 m (field centre):\nsea pulled into a bowl',fontsize=7.6,color=CU,va='center')
a.set_xticks([]); a.set_ylabel('height above water (m)'); a.set_title('Low over water',color=INK,loc='left')
# environment / sensors / limits
ax=f.add_axes([0.68,0.06,0.31,0.46]); ax.axis('off')
txt=[('SEEN BY OTHERS',INK,True),('Radar: true track; negligible field signature (tested geometry)  (D)',INK,False),('Optical: negligible field signature; faint shimmer 2–7 µrad  (D)',INK,False),('No plume, no rotor wash, no boom while subsonic',INK,False),
     ('Thermal: unknown, set by heat per manoeuvre  (U)',WARN,False),('',INK,False),('ENVIRONMENT',INK,True),('Rain hangs inside the field  (D est.)',INK,False),
     ('Landing footprint goes weightless: dust, water, people  (D est.)',INK,False),('Water crossings: ~2.7 GJ, very visible  (D)',INK,False),('',INK,False),
     ('LIMITS',INK,True),('Field edge must never cut the hull (3.6 m spare)',INK,False),('Field off on the surface: no take-off; wait (W3 exception)',WARN,False),('Exchange physics and heat losses unknown  (U)',WARN,False),('Supersonic field edge unexplored  (U)',WARN,False)]
for k,(t,c,b) in enumerate(txt): ax.text(0,1-k*0.066,t,color=c,fontsize=10.5 if b else 9,weight='bold' if b else 'normal',transform=ax.transAxes)
f.savefig(os.path.join(H,'weave_operating_card.png'),dpi=150)
