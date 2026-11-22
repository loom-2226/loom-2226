"""Figure for weave_coupled.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); d=json.load(open(os.path.join(H,'weave_coupled_series.json'))); r=json.load(open(os.path.join(H,'weave_coupled.json')))
t=np.array(d['t']); P=np.array(d['P']); dE=np.array(d['dE']); W=np.array(d['W'])
INK='#1f2933'; MUT='#6b7280'; A='#2563eb'; B='#d97706'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f,ax=plt.subplots(2,2,figsize=(10,7)); f.suptitle('Coupled dash from one action: field carries ship, wall pushes on relational mode (NON-CANON)',color=INK,fontsize=11)
a=ax[0,0]; a.plot(t,d['X'],color=A,lw=2,label='hull'); a.plot(t,d['Xd'],color=B,lw=2,ls='--',label='domain wall'); a.set_title('Position: 200 m in 3 s, stopped',color=INK,loc='left'); a.set_ylabel('m'); a.legend(frameon=False)
a=ax[0,1]; a.semilogy(t,np.maximum(d['felt'],1e-16),color=A,lw=2); a.set_title(f"Crew felt load (peak {r['shuttle']['max_felt_crew_g']:.0e} g)",color=INK,loc='left'); a.set_ylabel('g'); a.axhline(13.1,color=MUT,lw=1,ls=':'); a.text(0.05,1e-1,'conventional push peak ≈ 13 g',color=MUT,fontsize=8)
a=ax[1,0]; a.plot(t,(P-P[0])*1e9,color=A,lw=2); a.set_title('Total momentum change (ship + wall + mode)',color=INK,loc='left'); a.set_ylabel('nN·s'); a.set_ylim(-120,115); a.set_xlabel('s'); a.text(0.03,0.97,va='top',s='ship+wall peak 7.8e6 N·s;\nmode carries the opposite',transform=a.transAxes,color=MUT,fontsize=8)
a=ax[1,1]; a.plot(t,dE/1e6,color=A,lw=2,label='ΔE (all sectors)'); a.plot(t,W/1e6,color=B,lw=2,ls='--',label='actuator work'); a.set_title('Energy changes only by actuator work',color=INK,loc='left'); a.set_ylabel('MJ'); a.set_xlabel('s'); a.legend(frameon=False)
f.text(0.01,0.005,'Assumptions: A1 universal carriage field (lapse gradient) · A2 wall effective inertia · A3 translation-invariant wall–mode coupling (M1 exchange law)',color=MUT,fontsize=8)
f.tight_layout(rect=(0,0.03,1,0.95)); f.savefig(os.path.join(H,'weave_coupled.png'),dpi=150)
