from pathlib import Path
p=Path('/tmp/wayfarer_fq_20261031/faultlab.py')
s=p.read_text()
s=s.replace('    phases=[];hist=[];metrics={};rcs_trace=[]',
'''    phases=[];hist=[];metrics={};rcs_trace=[]
    safety={"mode":"nominal","events":[],"peak_attitude_error_deg":0.,
            "peak_rate_deg_s":0.,"torch_cap_fraction":1.,"saturation_s":0.}
    reserve_kg=float(ship.get("reserve_policy",{}).get("rcs_floor_kg",0.))
    assert reserve_kg >=0 and all(e["tank"]=="remass" for e in ship["torch"])
''',1)
needle='''                elif fault['kind']=='stuck_thruster':
                    assert any(e['id']==fault['nozzle'] for e in ship['rcs'])
                else:raise ValueError('unsupported fault '+str(fault['kind']))
            mass,cg,I=mass_properties(ship,state['tanks'])'''
repl='''                elif fault['kind']=='stuck_thruster':
                    assert any(e['id']==fault['nozzle'] for e in ship['rcs'])
                else:raise ValueError('unsupported fault '+str(fault['kind']))
                safety["events"].append({"t_s":round(state["t"],4),"event":"fault_injected","kind":fault["kind"]})
            mass,cg,I=mass_properties(ship,state['tanks'])
            if kind=="torch" and experiment.get("safing"):
                tvc=[f for f in experiment.get("faults",[])
                     if f["kind"]=="stuck_tvc" and f.get("_applied")]
                if tvc and safety["mode"]=="nominal" and state["t"]+1e-9>=tvc[0]["when_s"]+float(experiment["safing"].get("detect_delay_s",.2)):
                    e=ship["torch"][0]
                    f0,ve0,d0,_=torch_force(e,phase["mode"],mass,1.,cg)
                    tw=np.cross(vec(e["pos_m"])-cg,f0*d0)
                    en,A=rcs_wrench(ship,cg,state["gdir"])
                    cmd0,fraction=allocation(A,-tw)
                    safety["authority_fraction"]=float(fraction)
                    safety["torch_cap_fraction"]=max(0.,min(.90*float(fraction),.56 if phase["mode"]=="CRUISE" else .14))
                    safety["mode"]="throttle_limited"
                    safety["detect_time_s"]=round(state["t"],4)
                    safety["events"].append({"t_s":round(state["t"],4),
                               "event":"detected_then_throttled",
                               "mode":phase["mode"],
                               "torque_unmitigated_Nm":float(np.linalg.norm(tw)),
                               "calculated_allocation_fraction":float(fraction),
                               "torch_cap_fraction":safety["torch_cap_fraction"]})
            if kind=="torch" and safety["mode"]=="throttle_limited":
                # These are experimental thresholds; no flight sensor / FDIR qualification.
                angle=math.degrees(float(np.linalg.norm(qerror(qstart,state["y"][:4]))))
                rate=math.degrees(float(np.linalg.norm(state["y"][4:7])))
                if angle>float(experiment["safing"].get("cut_angle_deg",0.75)) or rate>float(experiment["safing"].get("cut_rate_deg_s",0.50)) or safety["saturation_s"] >= float(experiment["safing"].get("max_saturation_s",.4)):
                    safety["mode"]="torch_cut"
                    safety["torch_cap_fraction"]=0.
                    safety["cut_time_s"]=round(state["t"],4)
                    safety["events"].append({"t_s":round(state["t"],4),"event":"torch_cut_due_to_loss_of_control","angle_deg":angle,"rate_deg_s":rate,"saturation_s":safety["saturation_s"]})
'''
assert needle in s;s=s.replace(needle,repl,1)
needle="                    clipped=float(np.clip(requested,0,1));throttle_limits+=int(requested!=clipped)"
repl='''                    if experiment.get("safing"):
                        requested=min(requested,safety["torch_cap_fraction"])
                    clipped=float(np.clip(requested,0,1));throttle_limits+=int(requested!=clipped)'''
assert needle in s;s=s.replace(needle,repl,1)
needle='''                minfraction=min(minfraction,fraction)
                allocation_limits+=int(fraction<1.-1e-9)'''
repl='''                minfraction=min(minfraction,fraction)
                allocation_limits+=int(fraction<1.-1e-9)
                if kind=="torch" and experiment.get("safing") and safety["mode"]=="throttle_limited":
                    if fraction < float(experiment["safing"].get("allocation_limit",.98)):
                        safety["saturation_s"]+=h
                    else:
                        safety["saturation_s"]=0.'''
assert needle in s;s=s.replace(needle,repl,1)
needle='''                # Empty tank shuts down only engines fed by that tank.
                factors={tank:min(1.,state['tanks'][tank]/(dot*h)) if dot*h>0 else 1.
                         for tank,dot in mdots.items()}
                if any(v<1.-1e-12 for v in factors.values()):
                    state['depletion_steps']+=1
                    if 'propellant depleted within step: thrust curtailed' not in state['warnings']:
                        state['warnings'].append('propellant depleted within step: thrust curtailed')
                actual_levels=[];engine_samples=[]
                for e,ff,tt,f,ve,source in contributions:
                    factor=factors.get(e.get('tank'),1.) if ve is not None else 1.
'''
repl='''                # RCS has priority on the shared remass inventory; torch may not
                # consume the ring-fenced 5t. One physical tank, not a new dry mass.
                factors={};rcs_dots={};torch_dots={}
                for e,ff,tt,f,ve,source in contributions:
                    if ve is None or e.get("tank") is None:continue
                    table=rcs_dots if source=="rcs" else torch_dots
                    tank=e["tank"];table[tank]=table.get(tank,0.)+f/ve
                for tank,dot in mdots.items():
                    rdot=rcs_dots.get(tank,0.);tdot=torch_dots.get(tank,0.)
                    rfac=min(1.,state["tanks"][tank]/(rdot*h)) if rdot>0 else 1.
                    remaining=max(0.,state["tanks"][tank]-rfac*rdot*h)
                    floor=reserve_kg if tank=="remass" else 0.
                    tfac=min(1.,max(0.,remaining-floor)/(tdot*h)) if tdot>0 else 1.
                    factors[tank]=(rfac,tfac)
                    if rfac<1.-1e-12 or tfac<1.-1e-12:
                        state['depletion_steps']+=1
                        tag="RCS tank depleted" if rfac<1.-1e-12 else "Torch held at RCS reserve floor"
                        if tag not in state["warnings"]:state["warnings"].append(tag)
                actual_levels=[];engine_samples=[]
                for e,ff,tt,f,ve,source in contributions:
                    factor=factors.get(e.get('tank'),(1.,1.))[0 if source=="rcs" else 1] if ve is not None else 1.
'''
assert needle in s;s=s.replace(needle,repl,1)
needle='''                for tank,dot in mdots.items():
                    dot*=factors[tank];mdots[tank]=dot
                    used=dot*h;state['tanks'][tank]=max(0.,state['tanks'][tank]-used)'''
repl='''                for tank,dot in mdots.items():
                    dot=rcs_dots.get(tank,0.)*factors[tank][0]+torch_dots.get(tank,0.)*factors[tank][1]
                    mdots[tank]=dot
                    used=dot*h;state['tanks'][tank]=max(0.,state['tanks'][tank]-used)'''
assert needle in s;s=s.replace(needle,repl,1)
needle='''            if state['t']+1e-8>=nextsample:'''
repl='''            if kind=="torch" and experiment.get("safing"):
                safety["peak_attitude_error_deg"]=max(safety["peak_attitude_error_deg"],
                    math.degrees(float(np.linalg.norm(qerror(qstart,state["y"][:4])))))
                safety["peak_rate_deg_s"]=max(safety["peak_rate_deg_s"],
                    math.degrees(float(np.linalg.norm(state["y"][4:7]))))
            if state['t']+1e-8>=nextsample:'''
assert needle in s;s=s.replace(needle,repl,1)
needle="            'evidence_class':'non-governing numerical experiment; experimental metric laws not physical validation',"
repl="""            'safing_observations':safety,
            'reserve_floor_kg':reserve_kg,
            'evidence_class':'non-governing numerical experiment; experimental metric laws not physical validation',"""
assert needle in s;s=s.replace(needle,repl,1)
out=Path('/tmp/wayfarer_fq_20261031/faultlab_safing.py');out.write_text(s)
print('Created isolated safing solver',len(s),out)
