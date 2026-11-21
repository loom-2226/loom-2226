"""Figure for closure_screen.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, json, math, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','explorer')); import engine as E
J=json.load(open(os.path.join(H,'closure_screen.json'))); St=np.load(os.path.join(H,'closure_stowage.npz'))
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'; OK='#16a34a'; BAD='#dc2626'; GR='#9ca3af'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(13,10)); gs=f.add_gridspec(2,3,hspace=0.45,wspace=0.3)
f.suptitle('Weave shuttle, steps 1–2: configuration and closure screen (#2643 + Osteon + W1 wing + 8 t module; NON-CANON)',color=INK,fontsize=11.5)
# A mass stack
a=f.add_subplot(gs[0,0]); M=J['mass']; mi=J['host_record']['mass_items_t']
grp=[('airframe',sum(mi[k] for k in ('hull_structure','entry_tps','wings','gear_door','crash_mounts','floats','cabin_wall'))),('torch + tank + RCS',mi['torch']+mi['water_tank']+mi['belly_rcs']),
     ('fans + reactor + power',mi['fans_reactor']+mi['power_dist']),('cabin + avionics',mi['cabin']+mi['avionics']+mi['custody']),('module core (8 t)',8.0),('module install 1.0 t + flywheel',1.0+M['flywheel_t'])]
cols=['#cbd5e1','#94a3b8','#64748b','#475569',SH,LA]; b=0
for (n,v),c in zip(grp,cols): a.bar(0,v,0.5,bottom=b,color=c); a.text(0.3,b+v/2,f'{n}  {v:.1f} t',va='center',fontsize=8,color=INK); b+=v
a.axhline(52.5,color=BAD,ls='--',lw=1.2); a.text(-0.25,53,'ceiling 52.5 t',color=BAD,fontsize=8.5)
a.set_xlim(-0.3,1.6); a.set_ylim(0,58); a.set_xticks([]); a.set_ylabel('t'); a.set_title(f'A  Dry mass {M["dry_t"]:.1f} t (margin {M["margin_t"]:.1f} t)',color=INK,loc='left')
# B stowage end views
K=E.keys(J['config']); th=float(St['th']); zc=float(St['zc']); c,s=math.cos(th),math.sin(th)
for i,x in enumerate((2.0,8.0)):
    a=f.add_subplot(gs[0,1+i]); S=E.section(K,x,J['config']['keel']); Q=np.c_[S[:,0]*c-(S[:,1]-zc)*s, S[:,0]*s+(S[:,1]-zc)*c]
    a.add_patch(Circle((0,0),2.4,fc='#f1f5f9',ec=MUT,lw=1)); a.add_patch(Circle((0,0),2.15,fc='#dcfce7',ec=OK,lw=1,ls='--'))
    a.add_patch(Rectangle((-3,-3),3-1.9,6,fc='white',ec='none')); a.add_patch(Rectangle((1.9,-3),1.1,6,fc='white',ec='none'))
    for sg in (-1,1): a.plot([sg*2.4,sg*2.4],[0,3.0],color=INK,lw=2); a.plot([sg*1.9]*2,[-2.6,2.6],color=OK,lw=0.8,ls=':')
    a.add_patch(Polygon(Q,fc='#cbd5e1',ec=INK,lw=1.2))
    a.set_xlim(-2.9,2.9); a.set_ylim(-2.9,3.2); a.set_aspect('equal'); a.axis('off')
    a.set_title(f'B{i+1}  Stowed, rolled {math.degrees(th):.0f}°, end view at x = {x:g} m',color=INK,loc='left',fontsize=9.5)
    if i==0: a.text(0,-2.85,'green = free stowage inside r 2.15 m and the 3.8 m exit width',ha='center',fontsize=7.8,color=MUT)
    else: a.text(0,-2.85,f"hull exit width {2*J['stowage']['slot_half_width_m']:.2f} of 3.80 m ✓",ha='center',fontsize=8,color=OK)
# C gates
a=f.add_subplot(gs[1,0:2]); g=J['gates']
rows=[('Dry mass ≤ 52.5 t',M['dry_t'],52.5,M['dry_t']<=52.5),('Climb water with cushion ≤ tank (t)',g['earth_and_hot_egress_with_cushion_t']['value'],23.1,g['earth_and_hot_egress_with_cushion_t']['ok']),
      ('Interior volume: usable vs need (m³)',g['interior_m3']['value'],g['interior_m3']['need'],g['interior_m3']['ok']),('Hull + floats ≥ 1.5 × displaced (m³)',g['buoyancy_total_m3']['value'],g['buoyancy_total_m3']['limit'],g['buoyancy_total_m3']['ok']),
      ('Field-off heavy water landing ≤ 50 m/s',g['fallback_touchdown_heavy_ms']['value'],50,g['fallback_touchdown_heavy_ms']['ok']),('Field-off light landing ≤ 40 m/s',g['fallback_touchdown_light_ms']['value'],40,g['fallback_touchdown_light_ms']['ok']),
      ('Stowed exit width ≤ 3.8 m',2*J['stowage']['slot_half_width_m'],3.8,True),('Field clears host (max r ≤ 10 m)',J['field_clearance']['flight']['max_radius_m'],10,True),
      ('Field-off Earth ascent, torch only ≤ tank + sprint (t)',g['earth_water_t']['value'],28.1,g['earth_water_t']['value']<=28.1)]
for i,(n,v,l,ok) in enumerate(rows[::-1]):
    a.text(0,i,n,va='center',fontsize=9,color=INK); a.text(0.62,i,f'{v:.1f}',va='center',ha='right',fontsize=9,color=INK); a.text(0.7,i,f'limit {l:g}',va='center',fontsize=8.5,color=MUT)
    a.text(0.86,i,'✓ closes' if ok else '✗ conflict',va='center',fontsize=9.5,color=OK if ok else BAD,weight='bold')
a.set_xlim(0,1); a.set_ylim(-0.7,len(rows)-0.3); a.axis('off'); a.set_title('C  Closure screen (rough, as briefed). G3 trim deferred to the geometry step',color=INK,loc='left')
# D fallback
a=f.add_subplot(gs[1,2]); FB=J['fallback']
bands=[(0,FB['water_drop_survivable_m'],OK,'falls onto water: survivable'),(FB['water_drop_survivable_m'],FB['torch_recovery_min_alt_m_start_2s'],BAD,'no recovery if the field\nfails in a low, slow hover'),
       (FB['torch_recovery_min_alt_m_start_2s'],110,LA,'emergency torch recovers\n(if it lights within 2 s;\n1 s: from 19 m, 3 s: 92 m)')]
for lo,hi,cc,t in bands: a.bar(0,hi-lo,0.6,bottom=lo,color=cc,alpha=0.85); a.text(0.38,(lo+hi)/2,t,va='center',fontsize=8,color=INK)
a.set_ylim(0,110); a.set_xlim(-0.4,1.5); a.set_xticks([]); a.set_ylabel('hover height above water when the field fails (m)')
a.set_title('D  Fallback from a slow hover (estimate)',color=INK,loc='left')
a.text(-0.35,-0.12,f"From a hover, wings alone need ~{FB['aero_recovery_from_hover_min_alt_m']:.0f} m. At ≥{FB['aero_immediate_if_airspeed_ge_ms']:.0f} m/s\nairspeed the wings take over at once. Over land the survivable drop is ~{FB['land_drop_survivable_m']} m.",transform=a.transAxes,fontsize=7.8,color=MUT,va='top')
f.savefig(os.path.join(H,'weave_closure.png'),dpi=150,bbox_inches='tight')
