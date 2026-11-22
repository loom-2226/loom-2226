"""Figure for weave_shift_gust.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.ticker; from matplotlib.colors import LogNorm
H=os.path.dirname(os.path.abspath(__file__)); M=json.load(open(os.path.join(H,'weave_shift_gust_main.json')))['runs']; S=json.load(open(os.path.join(H,'weave_shift_gust_main_series.json')))
runs={}
for w in ('coarse','fine'):
    p=os.path.join(H,f'weave_shift_gust_{w}.json')
    if os.path.exists(p): runs.update(json.load(open(p))['runs'])
runs.update(M); SW=json.load(open(os.path.join(H,'weave_shift_gust_swirl.json')))
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'; GR='#9ca3af'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(12,8.6)); gs=f.add_gridspec(3,2,height_ratios=[1.1,0.8,0.8],hspace=0.6,wspace=0.25)
f.suptitle('One 1 m/s gust through the shift dash (R 15 m, wall 2 m): with vs without pressure (NON-CANON)',color=INK,fontsize=11)
a=f.add_subplot(gs[0,0]); sty={'h0.5_dash_pressure':(SH,'-','dash, with pressure'),'h0.5_dash_nopressure':(LA,'--','dash, no pressure'),'h0.5_nodash_pressure':(GR,'-','no dash, with pressure'),'h0.5_nodash_nopressure':(GR,':','no dash, no pressure')}
for k,(c,ls,l) in sty.items():
    L=S['series'][k]; a.plot(L['t'],np.array(L['ke'])+np.array(L['pe']),color=c,ls=ls,lw=2,label=l)
a.set_yscale('log'); a.set_ylim(3,2e4); a.set_xlabel('s'); a.set_title('Gust energy in the air (J), started at 32 J',color=INK,loc='left'); a.legend(frameon=False,fontsize=8,loc='upper left')
a=f.add_subplot(gs[0,1]); cats=['no dash','dash']; rem=[runs['h0.5_nodash_pressure']['E_final_J'],runs['h0.5_dash_pressure']['E_final_J']]; rad=[runs['h0.5_nodash_pressure']['absorbed_J'],runs['h0.5_dash_pressure']['absorbed_J']]
E0=runs['h0.5_dash_pressure']['E0_J']; oth=[E0-rem[i]-rad[i] for i in range(2)]
a.bar(range(2),rem,0.5,color=SH,label='left in the air'); a.bar(range(2),rad,0.5,bottom=rem,color=GR,label='radiated as sound'); a.bar(range(2),oth,0.5,bottom=np.array(rem)+np.array(rad),color='#e5e7eb',label='exchanged with field / numerical')
for i in range(2): a.text(i,rem[i]/2,f'{rem[i]:.1f}',ha='center',color='white',fontsize=9); a.text(i,rem[i]+rad[i]/2,f'{rad[i]:.1f}',ha='center',color=INK,fontsize=9)
a.set_xticks(range(2)); a.set_xticklabels(cats); a.set_ylim(0,36); a.set_title('With pressure: where the 32 J went (J)',color=INK,loc='left'); a.legend(frameon=False,fontsize=8,loc='upper right')
a=f.add_subplot(gs[1,0]); hs=[h for h in (1.0,0.5,0.25) if f'h{h:g}_dash_pressure' in runs]
a.plot(hs,[runs[f'h{h:g}_dash_pressure']['E_final_J']/E0 for h in hs],'o-',color=SH,lw=2,label='with pressure')
hs2=[h for h in (1.0,0.5,0.25) if f'h{h:g}_dash_nopressure' in runs]; a.plot(hs2,[runs[f'h{h:g}_dash_nopressure']['E_final_J']/E0 for h in hs2],'s--',color=LA,lw=2,label='no pressure')
a.set_xscale('log'); a.set_yscale('log'); a.invert_xaxis(); a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.set_xticks(hs2); a.set_xticklabels([f'{h:g} m' for h in hs2]); a.set_xlabel('grid spacing'); a.set_title('Energy ratio after dash vs grid: pressure converges',color=INK,loc='left',fontsize=10); a.legend(frameon=False,fontsize=8)
a=f.add_subplot(gs[1,1]); b=SW['blobs']; ks=list(b); a.bar(range(len(ks)),[b[k] for k in ks],0.6,color=SH); a.axhline(1,color=MUT,ls=':',lw=1)
a.set_xticks(range(len(ks))); a.set_xticklabels([k.replace('_',' ').replace('x','x ').replace('r','ρ ') for k in ks],fontsize=7.5); a.set_ylim(0,1.3)
a.set_title('Swirl gusts (exact, pressure-free by symmetry): energy ratio',color=INK,loc='left',fontsize=10)
for i,k in enumerate(ks): a.text(i,b[k]+0.04,f'{b[k]:.2f}',ha='center',fontsize=8,color=INK)
sn=S['snaps']
for j,k in enumerate(('h0.5_dash_pressure','h0.5_dash_nopressure')):
    a=f.add_subplot(gs[2,j]); g=sn[k]['grid']; tk=max(sn[k]['snaps'],key=float); v=np.array(sn[k]['snaps'][tk]); x=np.array(g['x']); p=np.array(g['p'])
    im=a.pcolormesh(x,p,v.T,norm=LogNorm(1e-3,1),cmap='Blues',shading='nearest'); a.set_ylim(0,40); a.set_xlim(-45,275)
    a.set_title(('With pressure' if j==0 else 'No pressure')+f': gust speed at t = {float(tk):.0f} s (m/s)',color=INK,loc='left',fontsize=10); a.set_xlabel('track position (m)'); a.set_ylabel('radius (m)')
    cb=f.colorbar(im,ax=a,pad=0.01); cb.outline.set_visible(False)
f.text(0.01,0.005,'Linearized compressible air in the N = 1 shift metric, axisymmetric meridional gust (1 m/s Gaussian, L = 3 m, at x = 60 m on axis). w = velocity measured in the local free-fall frame. Sponge-absorbed energy counted as radiated.',color=MUT,fontsize=7.5)
f.savefig(os.path.join(H,'weave_shift_gust.png'),dpi=150,bbox_inches='tight')
