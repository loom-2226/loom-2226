"""Composite figure for the four Weave outings. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib.colors import TwoSlopeNorm
H=os.path.dirname(os.path.abspath(__file__)); J=lambda n: json.load(open(os.path.join(H,n)))
Dg=J('outing_dodge.json'); Sn=J('outing_sensors.json'); Ld=J('outing_landing.json'); Tm=J('outing_transmedium.json'); GC=J('weave_geometry_compare.json')['cases']
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'; WA='#0e7490'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(13,10)); gs=f.add_gridspec(3,2,hspace=0.6,wspace=0.28,height_ratios=[1,1,1.15])
f.suptitle('Weave prototype outings: dodge, sensors, weather landing, transmedium (NON-CANON)',color=INK,fontsize=12)
# 1 dodge
a=f.add_subplot(gs[0,0]); cs=Dg['cases']; ks=['D30_T0.5','D30_T0.4']; lab=['30 m in 0.5 s','30 m in 0.4 s']; x=np.arange(2); w=0.36
mot=[cs[k]['peak_accel_g'] for k in ks]; felt=[cs[k]['ship']['crew_peak_g'] for k in ks]
a.bar(x-w/2,mot,w*0.92,color=MUT,label='shuttle motion'); a.bar(x+w/2,felt,w*0.92,color=SH,label='crew feel')
for i in range(2): a.text(x[i]-w/2,mot[i]*1.3,f'{mot[i]:.0f} g',ha='center',fontsize=8.5,color=INK); a.text(x[i]+w/2,felt[i]*1.3,f'{felt[i]:.2f} g',ha='center',fontsize=8.5,color=INK)
a.set_yscale('log'); a.set_ylim(0.1,5000); a.set_xticks(x); a.set_xticklabels([f'{l}\nwall Mach {cs[k]["wall_mach"]:.2f}' for l,k in zip(lab,ks)],fontsize=8.5)
a.set_title('1  Dodge (hull across the motion): peak g',color=INK,loc='left'); a.legend(frameon=False,fontsize=8,loc='upper center',ncol=2)
# 2 sensors
a=f.add_subplot(gs[0,1]); A=Sn['optical_air']; m=np.array(A['by_gradient']['-1e-07']['map'])*1e6; xx=np.array(A['x']); zz=np.array(A['z'])
lim=np.abs(m).max(); im=a.pcolormesh(xx,zz,m.T,cmap='RdBu_r',norm=TwoSlopeNorm(0,-lim,lim),shading='nearest'); cb=f.colorbar(im,ax=a,pad=0.01); cb.outline.set_visible(False); cb.set_label('µrad',color=INK)
a.set_xlabel('track position (m)'); a.set_ylabel('height rel. track (m)'); a.set_title('2  Optical: shimmer from rearranged layered air (dn/dz −1e-7/m)',color=INK,loc='left',fontsize=9.5)
r=[q for q in Sn['radar'] if abs(q.get('t_emit',0)-1.5)<1e-9][0]
a.text(0.01,-0.3,f"Field itself: optical bend ≤{Sn['optical_metric']['max_rad']:.0e} rad; field RCS ~{Sn['radar_field_rcs_estimate']['field_rcs_m2']:.0e} m²\nRadar Doppler = true speed ({r['xband_doppler_Hz']/1e3:.1f} kHz X-band at 125 m/s)",transform=a.transAxes,fontsize=7.8,color=MUT,va='top')
# 3 landing
a=f.add_subplot(gs[1,0]); col=[c for c in GC if c['mode']=='lapse' and c['R_m']==15 and c['wall_d_m']==2][0]['residual_air_KE_J']
vals=[col,Ld['A2_lapse_dash_with_pressure']['final_KE_J'],Ld['A1_cushion_on']['final_KE_J']]; labs=['lapse dash,\nparcels (no pressure)','lapse dash,\nwith pressure','cushion on (1 g),\nwith pressure']
a.bar(range(3),vals,0.55,color=[LA,SH,SH]); a.set_yscale('log'); a.set_ylim(10,1e9); a.set_xticks(range(3)); a.set_xticklabels(labs,fontsize=8.3)
for i,v in enumerate(vals): a.text(i,v*1.6,(f'{v/1e6:.0f} MJ' if v>1e6 else f'{v:.0f} J'),ha='center',fontsize=8.5,color=INK)
a.set_title('3  Landing: air energy left by a lapse-type field (J)',color=INK,loc='left')
a.text(0.01,-0.3,f"Cushion hover: air ≤{Ld['A1_cushion_on']['max_air_speed_ms']:.2f} m/s, Δp {Ld['A1_cushion_on']['max_pressure_pert_Pa']:.0f} Pa: no downwash.\nWind 10–15 m/s on hull: crew 0.008–0.018 g.",transform=a.transAxes,fontsize=7.8,color=MUT,va='top')
# 4 transmedium energies
a=f.add_subplot(gs[1,1]); sk=Tm['skim']; labs=['exit','entry']+[f'skim\n{h} m' for h in ('5','10','15','19')]
vals=[Tm['exit']['APE_J'],Tm['entry']['APE_J']]+[sk[h]['APE_J'] for h in ('5','10','15','19')]
a.bar(range(6),vals,0.6,color=[WA,WA,SH,SH,SH,SH]); a.set_yscale('log'); a.set_ylim(1e3,1e11); a.set_xticks(range(6)); a.set_xticklabels(labs,fontsize=8.3)
for i,v in enumerate(vals): a.text(i,v*1.8,(f'{v/1e9:.1f} GJ' if v>1e9 else (f'{v/1e6:.0f} MJ' if v>1e6 else f'{v/1e3:.0f} kJ')),ha='center',fontsize=8.3,color=INK)
a.set_title('4  Transmedium: energy left in the water surface (released as splash/waves)',color=INK,loc='left',fontsize=9.5)
a.text(0.01,-0.3,'Skim height = field centre above the water.\nExit/entry: 60 m vertical in 1.5 s.',transform=a.transAxes,fontsize=7.8,color=MUT,va='top')
# 5 exit configuration
d=np.load(os.path.join(H,'outing_transmedium_vertical.npz')); X0,P0,Xf,Pf=d['X0'],d['P0'],d['Xf'],d['Pf']
for j,(mode,ttl) in enumerate((('exit','Exit: where the water ends up'),('entry','Entry: where the air ends up'))):
    a=f.add_subplot(gs[2,j]); S=30.0
    if mode=='exit': sel=X0<S; hgt=Xf-S
    else: sel=X0<S; hgt=S-Xf
    msk=sel&(np.abs(hgt)<60)
    a.scatter(np.concatenate([-Pf[msk],Pf[msk]]),np.concatenate([hgt[msk],hgt[msk]]),s=0.6,color=(WA if mode=='exit' else LA),alpha=0.6,lw=0)
    a.axhline(0,color=INK,lw=1); a.set_xlim(-30,30); a.set_ylim(-40,50); a.set_aspect('equal')
    a.set_xlabel('m'); a.set_ylabel('height above sea surface (m)'); a.set_title(f'5{"ab"[j]}  {ttl} (field centre {"+30" if mode=="exit" else "−30"} m)',color=INK,loc='left',fontsize=9.5)
    if mode=='exit': a.text(34,10,f"{Tm['exit']['water_above_surface_t']/1e3:.1f} kt of sea carried up\ncavity {Tm['exit']['air_below_surface_m3']/1e3:.1f}k m³ left behind\nthin water neck: ruptures (0.46 bar tension)",fontsize=8,color=INK,clip_on=False)
    else: a.text(34,10,f"{Tm['entry']['air_below_surface_m3']/1e3:.1f}k m³ of air taken down\n2.9 bar under-pressure at 30 m",fontsize=8,color=INK,clip_on=False)
f.savefig(os.path.join(H,'weave_outings.png'),dpi=150,bbox_inches='tight')
