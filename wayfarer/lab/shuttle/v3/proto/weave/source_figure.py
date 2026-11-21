"""Figure for weave_source_ledger.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); J=json.load(open(os.path.join(H,'weave_source_ledger.json'))); L=J['ledger']
t=np.array(L['t']); E=np.array(L['E_J']); P=np.array(L['Px_Ns']); Pa=np.array(L['Pabs_Ns']); xE=np.array(L['xE_Jm']); KS=np.array(L['KS_W']); dE=np.array(L['energy_balance']['dEdt_W'])
X=200*(6*(t/3)**5-15*(t/3)**4+10*(t/3)**3); Xc=np.where(E!=0,xE/np.where(E==0,1,E),np.nan)
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f,ax=plt.subplots(1,4,figsize=(16,4.4)); f.suptitle('What GR requires of any source of the R 15 m / 2 m shift during the 200 m dash (NON-CANON)',color=INK,fontsize=11)
a=ax[0]; a.plot(t,-E,color=SH,lw=2); a.set_yscale('log'); a.set_ylim(1e30,3e33); a.set_xlabel('s'); a.set_title('−(local source energy), J',color=INK,loc='left',fontsize=10)
a.text(1.5,1.6e30,'ADM energy of the field = 0',ha='center',color=MUT,fontsize=8)
a=ax[1]; a.plot(t,Pa,color=LA,lw=2,label='gross internal flow ∫|p| dV'); a.plot(t,np.abs(P)+1,color=SH,lw=2,ls='--',label='net ∫p dV (numerical residue)')
a.set_yscale('log'); a.set_ylim(1e20,1e32); a.set_xlabel('s'); a.set_title('Source momentum, N·s',color=INK,loc='left',fontsize=10); a.legend(frameon=False,fontsize=8,loc='lower center')
a=ax[2]; a.plot(t,dE/1e33,color=SH,lw=2,label='dE/dt'); a.plot(t,KS/1e33,color=LA,lw=2,ls='--',label='∫ K_ij S^ij dV'); a.axhline(0,color=MUT,lw=0.8)
a.set_xlabel('s'); a.set_title('Local energy balance (10³³ W): closes',color=INK,loc='left',fontsize=10); a.legend(frameon=False,fontsize=8)
a=ax[3]; a.plot(t,X,color=MUT,lw=2,label='domain centre'); a.plot(t,Xc,color=SH,lw=2,ls='--',label='local energy centroid'); a.axhline(0,color=LA,lw=2,label='ADM charges (field alone): 0')
a.set_xlabel('s'); a.set_ylabel('m'); a.set_title('Centroid moves; global charges do not',color=INK,loc='left',fontsize=10); a.legend(frameon=False,fontsize=8,loc='upper left')
f.text(0.01,0.0,'3+1 formulas validated against the 4D Einstein tensor at 0.1c (E 5e-7, p 1e-4, S 1e-5 relative). Net momentum is ≤ 5e-7 of the gross flow (numerical). Boundary fields ≤ 2e-11 of peak.',color=MUT,fontsize=8)
f.tight_layout(rect=(0,0.04,1,0.93)); f.savefig(os.path.join(H,'weave_source_ledger.png'),dpi=150)
