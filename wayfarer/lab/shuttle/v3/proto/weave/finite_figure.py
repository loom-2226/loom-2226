"""Figure for weave_finite.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); C=json.load(open(os.path.join(H,'weave_finite.json')))['cases']
INK='#1f2933'; MUT='#6b7280'; A='#2563eb'; B='#d97706'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
lab=[f"R {c['R_m']:g} m\nwall {c['wall_d_m']:g} m\nf(ends) {c['f_at_hull_ends']:.2f}" for c in C]
f=plt.figure(figsize=(11,7.2)); gs=f.add_gridspec(2,2,height_ratios=[1,1.05])
f.suptitle('Finite carriage field (A1 check): 20 m hull, 200 m / 3 s dash (NON-CANON)',color=INK,fontsize=11)
a=f.add_subplot(gs[0,0]); y=[max(c['peak_crew_g'],1e-6) for c in C]; a.bar(range(4),y,color=A,width=0.55); a.set_yscale('log'); a.set_ylim(1e-6,10)
a.set_xticks(range(4)); a.set_xticklabels(lab,fontsize=8); a.set_title('Crew peak felt load (g)',color=INK,loc='left')
for i,c in enumerate(C): a.text(i,y[i]*1.6,('0' if c['peak_crew_g']==0 else f"{c['peak_crew_g']:.1e}"),ha='center',color=INK,fontsize=8)
a.axhline(13.1,color=MUT,ls=':',lw=1)
a=f.add_subplot(gs[0,1]); y=[max(c['peak_hull_axial_kN'],1e-6) for c in C]; a.bar(range(4),y,color=A,width=0.55); a.set_yscale('log'); a.set_ylim(1e-6,1e4)
a.set_xticks(range(4)); a.set_xticklabels(lab,fontsize=8); a.set_title('Hull peak axial load (kN)',color=INK,loc='left')
for i,c in enumerate(C): a.text(i,y[i]*1.6,f"{c['peak_hull_axial_kN']:.1g}",ha='center',color=INK,fontsize=8)
a=f.add_subplot(gs[1,:])
for c,col,ls in ((C[0],B,'--'),(C[1],A,'-')):
    a.plot(c['ambient']['x0'],c['ambient']['v'],color=col,lw=2,ls=ls,label=f"R {c['R_m']:g} m")
a.axhline(0,color=MUT,lw=0.8); a.axvspan(-10,10,color=MUT,alpha=0.12); a.axvspan(190,210,color=MUT,alpha=0.12)
a.text(0,a.get_ylim()[1]*0.85,'hull start',ha='center',color=MUT,fontsize=8); a.text(200,a.get_ylim()[1]*0.85,'hull end',ha='center',color=MUT,fontsize=8)
a.set_title('Loose matter on the path: speed left behind after the dash',color=INK,loc='left'); a.set_xlabel('initial position (m)'); a.set_ylabel('final speed (m/s)'); a.legend(frameon=False,loc='lower right')
f.text(0.01,0.005,'Same action as weave_coupled.py with field profile f(u); momentum exact; ΔE − W ≤ 11 kJ (integration). Ambient = 1 kg test parcels every 2 m, no collisions.',color=MUT,fontsize=8)
f.tight_layout(rect=(0,0.03,1,0.95)); f.savefig(os.path.join(H,'weave_finite.png'),dpi=150)
