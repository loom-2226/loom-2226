from pathlib import Path
p=Path('/home/ubuntu/wayfarer_flight_lab_scratch_20261026/flightlab.py')
out=Path('/tmp/wayfarer_fq_20261031/faultlab.py')
s=p.read_text()
needle="        for j,(t,h) in enumerate(steps):\n            mass,cg,I=mass_properties(ship,state['tanks'])"
replacement="""        for j,(t,h) in enumerate(steps):
            # FQ10 non-governing fault injector; one persistent spacecraft state.
            for fault in experiment.get('faults',[]):
                if state['t'] < fault['when_s'] or fault.get('_applied'):continue
                fault['_applied']=True
                if fault['kind']=='cluster_out':
                    affected=[e for e in ship['rcs'] if e['id'].startswith(fault['cluster']+'_')]
                    assert len(affected)==4
                    for e in affected:e['enabled']=False
                elif fault['kind']=='stuck_tvc':
                    # Freeze the torch nozzle at a declared 1-degree deflection
                    # to expose attitude/control response, not a real TVC failure law.
                    engine=ship['torch'][0]
                    engine['auto_trim']=False
                    engine['direction']=[-math.cos(math.radians(1)),math.sin(math.radians(1)),0.0]
                elif fault['kind']=='stuck_thruster':
                    assert any(e['id']==fault['nozzle'] for e in ship['rcs'])
                else:raise ValueError('unsupported fault '+str(fault['kind']))
            mass,cg,I=mass_properties(ship,state['tanks'])"""
assert needle in s
s=s.replace(needle,replacement,1)
needle="                    peak_throttle=max(peak_throttle,float(np.max(avg)))"
replacement="""                    for k,e in enumerate(engines):
                        for fault in experiment.get('faults',[]):
                            if (fault['kind']=='stuck_thruster' and fault.get('_applied')
                                    and e['id']==fault['nozzle']):
                                avg[k]=fault.get('stuck_fraction',1.)
                                state['act'][e['id']]=avg[k]; state['cmd'][e['id']]=avg[k]
                    peak_throttle=max(peak_throttle,float(np.max(avg)))"""
assert needle in s
s=s.replace(needle,replacement,1)
out.write_text(s)
print('FQ10 patched source',len(s),'bytes',out)
