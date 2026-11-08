"""Torch -> stipulated cooling/folding coast -> RCS, using rev7 settled-water builder.
The fluid distribution is an equilibrium assumption, not a slosh simulation.
"""
import copy,json
import numpy as np
import study as s
import build_v05 as b
I=copy.deepcopy(s.G.I);G=s.G.G;tr=s.torch(m0=G['states']['S1']['mass_t']*1000,tag='torch_geometry')
I['states']['POST_BURN']=dict(I['states']['S1'],remass_t=250-tr['propellant_used_kg']/1000)
offset=G['thrust_line_offset_m']
parts,rooms,jacket,jv,sec=b.build(I,offset['y'],offset['z'])
ps,*_=b.state_parts(I,parts,sec,jacket,G['protected_water']['jacket_t'],G['protected_water']['service_tank_t'],'POST_BURN')
mp=b.mass_props(ps);m=mp['mass_t']*1000;cg=np.array(mp['cg_m']);tensor=np.array(mp['inertia_kg_m2'])
assert abs(m-tr['final_mass_kg'])<.01
turn=s.fly('combined_settled_turn',coarse=25000,T=40,override=(m,tensor,cg),save=True)
# Initial body -X points along inertial +X; rotate turn-relative residuals accordingly.
rotation=np.array([-1,1,-1]);coast=60.;postburn_time=coast+44
result={'torch':tr,'coast_before_turn_s':coast,'turn':turn,'cg_at_turn_m':cg.tolist(),
 'inertia_at_turn_kg_m2':tensor.tolist(),'mass_kg_at_turn':m,
 'position_end_m':(np.array([tr['numeric_position_m']+tr['numeric_dv_m_s']*postburn_time,0,0])+rotation*np.array(turn['displacement_m'])).tolist(),
 'velocity_end_m_s':(np.array([tr['numeric_dv_m_s'],0,0])+rotation*np.array(turn['residual_velocity_m_s'])).tolist(),
 'initial_body_to_inertial_q':[0,0,1,0],'torch_force_body_axis':'minus x',
 'boundary_position_velocity_mass_jumps':[0,0,0],
 'postburn_mass_properties_source':'build_v05.build/state_parts/mass_props; actual rev7 protected water split and thrust offset retained',
 'limitations':['60 s cooling/folding coast assumed, not thermally qualified','zero spin during fin folding; no flexible/deployment dynamics',
                'water remains in builder settled-aft distribution during RCS; no slosh model','RCS propellant not integrated: ve and feed/tank hardware absent',
                'ideal torch TVC, perfect state estimate, no environmental forces in this combined case']}
s.dump('combined.json',result)
print(json.dumps(result,indent=2))
