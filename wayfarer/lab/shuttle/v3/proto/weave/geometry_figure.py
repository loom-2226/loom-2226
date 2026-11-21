"""Figure for weave_geometry_compare.py. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); C=json.load(open(os.path.join(H,'weave_geometry_compare.json')))['cases']; S=json.load(open(os.path.join(H,'weave_geometry_compare_series.json')))
INK='#1f2933'; MUT='#6b7280'; SH='#2563eb'; LA='#d97706'
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False})
f=plt.figure(figsize=(12,8.4)); gs=f.add_gridspec(3,2,height_ratios=[1.1,0.75,0.75],hspace=0.55,wspace=0.22)
f.suptitle('Same hull, same 200 m / 3 s dash, same sea-level air: lapse-gradient vs zero-expansion shift (NON-CANON)',color=INK,fontsize=11)
cases=[(15.0,2.0),(12.0,0.5),(12.0,2.0)]; get=lambda mo,R,d:[c for c in C if c['mode']==mo and c['R_m']==R and c['wall_d_m']==d][0]
lab=[f'R {R:g} m, wall {d:g} m' for R,d in cases]; xi=np.arange(3); w=0.36
a=f.add_subplot(gs[0,0])
for off,mo,col in ((-w/2,'lapse',LA),(w/2,'shift',SH)):
    y=[max(get(mo,R,d)['crew_peak_g'],1e-5) for R,d in cases]; a.bar(xi+off,y,w*0.92,color=col,label=mo)
    for i,v in enumerate(y): a.text(xi[i]+off,v*1.5,f'{v:.2g}',ha='center',fontsize=8,color=INK)
a.set_yscale('log'); a.set_ylim(1e-5,300); a.set_xticks(xi); a.set_xticklabels(lab,fontsize=8); a.set_title('Crew peak felt load (g)',color=INK,loc='left'); a.legend(frameon=False,loc='upper left')
a=f.add_subplot(gs[0,1])
for off,mo,col in ((-w/2,'lapse',LA),(w/2,'shift',SH)):
    y=[get(mo,R,d)['residual_air_KE_J']/1e6 for R,d in cases]; a.bar(xi+off,y,w*0.92,color=col,label=mo)
    for i,v in enumerate(y): a.text(xi[i]+off,v+0.8,f'{v:.0f}',ha='center',fontsize=8,color=INK)
a.set_xticks(xi); a.set_xticklabels(lab,fontsize=8); a.set_ylim(0,55); a.set_title('Air kinetic energy left after the stop (MJ)',color=INK,loc='left')
a=f.add_subplot(gs[1,:])
for mo,col,ls in (('lapse',LA,'-'),('shift',SH,'--')):
    L=S['series'][f'{mo}_R15_d2']; a.plot(L['t'],np.array(L['ke'])/1e6,color=col,lw=2,ls=ls,label=mo)
a.set_title('Air kinetic energy during the dash, R 15 m / wall 2 m (MJ): shift lends more and takes it all back',color=INK,loc='left'); a.set_xlabel('s'); a.legend(frameon=False)
for j,(mo,key,ttl,cm,vmax) in enumerate((('lapse','v','Lapse: air speed left behind (m/s)','Oranges',120),('shift','dx','Shift: air displacement left behind (m), speed 0','Blues',200))):
    a=f.add_subplot(gs[2,j]); F=S['fields'][mo]; x0=np.array(F['x0']); p0=np.array(F['p0'])
    val=np.array(F['v']) if key=='v' else np.sqrt(np.array(F['dx'])**2+np.array(F['dp'])**2)
    im=a.pcolormesh(x0,p0,val,cmap=cm,vmin=0,vmax=vmax,shading='nearest'); a.set_title(ttl,color=INK,loc='left',fontsize=9.5)
    a.set_xlabel('initial track position (m)'); a.set_ylabel('radius (m)'); cb=f.colorbar(im,ax=a,pad=0.01); cb.outline.set_visible(False)
f.text(0.01,0.008,'Axisymmetric, collisionless air (exact for shift: div β = 0, no pressure change; lapse shell-crosses → shocks in real air). Domain trajectory commanded in both. Shift reaction routed by explicit A3 bookkeeping.',color=MUT,fontsize=8)
f.savefig(os.path.join(H,'weave_geometry_compare.png'),dpi=150,bbox_inches='tight')
