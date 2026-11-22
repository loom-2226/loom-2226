"""Figure for weave_shift_fluid.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib.colors import LogNorm
H=os.path.dirname(os.path.abspath(__file__)); J=json.load(open(os.path.join(H,'weave_shift_fluid.json'))); M=json.load(open(os.path.join(H,'weave_shift_fluid_maps.json')))
G=json.load(open(os.path.join(H,'weave_geometry_compare.json')))['cases']
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(12,8)); gs=f.add_gridspec(2,3,hspace=0.55,wspace=0.35)
f.suptitle('Can air follow the zero-expansion shift? Exact GR check, then what an ideal fluid leaves out (NON-CANON)',color=INK,fontsize=11)
a=f.add_subplot(gs[0,0]); p1=J['part1_exact_GR']; pc=J['part1_control_alcubierre']
lab=['free-fall\nvs flow','energy-mom.\nconservation','control:\nAlcubierre']; y=[p1['geo_minus_req_rel']['max'],p1['divT_rel']['max'],pc['divT_rel']['max']]
a.bar(range(3),y,color=[SH,SH,MUT],width=0.6); a.set_yscale('log'); a.set_ylim(1e-13,10); a.set_xticks(range(3)); a.set_xticklabels(lab,fontsize=8)
for i,v in enumerate(y): a.text(i,v*3,f'{v:.0e}',ha='center',fontsize=8,color=INK)
a.set_title('Exact GR residual (relative)',color=INK,loc='left',fontsize=10)
cases=['R15_d2','R12_d2','R12_d0.5']; cl=['R 15 / 2','R 12 / 2','R 12 / 0.5']
a=f.add_subplot(gs[0,1]); y=[J['part2'][c]['viscous']['peak_pattern_mach'] for c in cases]; a.bar(range(3),y,color=SH,width=0.6); a.axhline(1,color=MUT,ls=':',lw=1)
for i,v in enumerate(y): a.text(i,v+0.12,f'{v:.2f}',ha='center',fontsize=8,color=INK)
a.set_xticks(range(3)); a.set_xticklabels(cl,fontsize=8); a.set_title('Wall speed through local air (Mach)',color=INK,loc='left',fontsize=10); a.text(-0.45,1.04,'speed of sound',color=MUT,fontsize=8,ha='left')
a=f.add_subplot(gs[0,2]); x=np.arange(3); w=0.36
lap=[[c for c in G if c['mode']=='lapse' and f"R{c['R_m']:g}_d{c['wall_d_m']:g}"==k][0]['residual_air_KE_J']/1e6 for k in cases]
def ke(k,w0):
    v=M[k]; p0=np.array(v['p0']); amp=np.array(v['amp']); m=1.2*2*np.pi*p0; return float(np.sum(0.5*m*(amp*w0)**2))/1e6
sh=[ke(k,1.0) for k in cases]
a.bar(x-w/2,lap,w*0.92,color=LA,label='lapse wake (still air)'); a.bar(x+w/2,sh,w*0.92,color=SH,label='shift, 1 m/s gusts (upper bound)')
for i in range(3): a.text(x[i]-w/2,lap[i]+1.5,f'{lap[i]:.0f}',ha='center',fontsize=8,color=INK); a.text(x[i]+w/2,sh[i]+1.5,f'{sh[i]:.0f}',ha='center',fontsize=8,color=INK)
a.set_xticks(x); a.set_xticklabels(cl,fontsize=8); a.set_ylim(0,105); a.set_title('Air KE left behind (MJ)',color=INK,loc='left',fontsize=10); a.legend(frameon=False,fontsize=7.5,loc='upper left')
a=f.add_subplot(gs[1,:]); v=M['R15_d2']; im=a.pcolormesh(np.array(v['x0']),np.array(v['p0']),np.array(v['amp']),norm=LogNorm(1,200),cmap='Blues',shading='nearest')
a.set_title('Shift R 15 / wall 2: how much a small gust in each parcel of air is amplified by the dash (test-particle bound)',color=INK,loc='left',fontsize=10)
a.set_xlabel('initial track position (m)'); a.set_ylabel('radius (m)'); cb=f.colorbar(im,ax=a,pad=0.01); cb.outline.set_visible(False); cb.set_label('amplification ×',color=INK)
f.text(0.01,0.01,'Exact GR: N = 1 shift, perfect fluid with uniform ρ, p and u = n, 4D Christoffels by finite differences at V up to 0.3c. Beyond ideal: η = 1.8e-5 Pa·s, c_s = 343 m/s; gust growth from ẇᵢ = −wⱼ∂ᵢβⱼ, pressure feedback ignored.',color=MUT,fontsize=7.5)
f.savefig(os.path.join(H,'weave_shift_fluid.png'),dpi=150,bbox_inches='tight')
