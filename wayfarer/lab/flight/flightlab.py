"""LOOM scratch flight lab MVP. SI units; body->inertial scalar-first quaternions.
Non-governing experimental models. Conventional dynamics are rigid-body approximations.
"""
from __future__ import annotations
import copy, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.spatial.transform import Rotation

G0=9.80665
C=299792458.0

def vec(v): return np.asarray(v,dtype=float)
def crossmat(v): return np.dot(v,v)*np.eye(3)-np.outer(v,v)
def qmul(q,p): return np.r_[q[0]*p[0]-q[1:]@p[1:],q[0]*p[1:]+p[0]*q[1:]+np.cross(q[1:],p[1:])]
def rotation(q): return Rotation.from_quat(np.r_[q[1:],q[0]])
def qerror(q,target): return (rotation(q).inv()*rotation(target)).as_rotvec()
def qaxis(axis,angle):
    a=np.eye(3)[axis] if isinstance(axis,(int,np.integer)) else unit(vec(axis))
    return np.r_[math.cos(angle/2),a*math.sin(angle/2)]
def unit(v):
    n=np.linalg.norm(v)
    if n<1e-15: raise ValueError("zero direction vector")
    return v/n

def mass_properties(ship,tanks):
    """Assemble components and fuel at declared fixed centroids, including intrinsic tensors."""
    parts=[ship['base']]+ship.get('components',[])
    # Optional installation mass is additional to base/components, never inferred.
    parts += [dict(mass_kg=e['installed_mass_kg'],cg_m=e['pos_m'],
                   inertia_kg_m2=e.get('installed_inertia_kg_m2',np.zeros((3,3)).tolist()))
              for key in ('rcs','torch') for e in ship.get(key,[])
              if e.get('installed_mass_kg',0)>0]
    masses=[]; centers=[]; inertias=[]
    for p in parts:
        m=float(p['mass_kg'])
        if m<0:raise ValueError('negative component mass')
        masses.append(m); centers.append(vec(p['cg_m']))
        inertias.append(vec(p.get('inertia_kg_m2',np.zeros((3,3)).tolist())))
    for t in ship.get('tanks',[]):
        fuel=float(tanks[t['id']]); nominal=float(t['capacity_kg'])
        if nominal<=0:raise ValueError('positive tank capacity required')
        if fuel < -1e-6 or fuel > nominal+1e-5: raise ValueError('tank out of range: '+t['id'])
        masses.append(fuel);centers.append(vec(t['cg_m']))
        inertias.append(vec(t.get('inertia_full_kg_m2',np.zeros((3,3)).tolist()))*(fuel/nominal))
    m=sum(masses)
    if m<=0: raise ValueError('spacecraft requires positive mass')
    cg=sum((mm*cc for mm,cc in zip(masses,centers)),np.zeros(3))/m
    inertia=sum((ii+mm*crossmat(cc-cg) for mm,cc,ii in zip(masses,centers,inertias)),np.zeros((3,3)))
    if np.min(np.linalg.eigvalsh(inertia))<=0: raise ValueError('non-positive inertia tensor')
    return m,cg,inertia

def source_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate(ship):
    ids=[x['id'] for key in ('rcs','torch') for x in ship.get(key,[])]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate engine IDs')
    tk={t['id'] for t in ship.get('tanks',[])}
    if len(tk)!=len(ship.get('tanks',[])): raise ValueError('duplicate tank IDs')
    for engine in ship.get('rcs',[])+ship.get('torch',[]):
        if engine.get('tank') is not None and engine['tank'] not in tk: raise ValueError('unknown tank '+engine['tank'])
        if engine.get('max_N',0)<=0 and 'modes' not in engine: raise ValueError('thruster missing thrust')
        unit(vec(engine['direction']))
        for key in ('lag_s','command_slew_fullscale_s','gimbal_limit_deg','gimbal_slew_deg_s','installed_mass_kg'):
            if engine.get(key,0)<0:raise ValueError('negative engine limit: '+key)
        exhaust_velocity(engine)
        if 'gimbal' in engine:
            g=engine['gimbal'];gimbal_direction(engine,[0,0])
            if any(float(g.get(k,0))<0 for k in ('limit_deg','rate_deg_s','lag_s')):
                raise ValueError('negative gimbal limit')
            initial=vec(g.get('initial_angles_deg',[0,0]))
            if initial.shape!=(2,) or np.max(abs(initial))>g['limit_deg']+1e-9:
                raise ValueError('initial gimbal angle exceeds limit')
        for spec in engine.get('modes',{}).values():
            if spec['max_N']<=0:raise ValueError('torch mode requires positive thrust')
            exhaust_velocity(spec)
    tanklevels={t['id']:float(t.get('initial_kg',t['capacity_kg'])) for t in ship.get('tanks',[])}
    mass_properties(ship,tanklevels)
    return tanklevels

def rcs_wrench(ship,cg,gdirs=None):
    engines=[e for e in ship.get('rcs',[]) if e.get('enabled',True)]
    if not engines: return engines,np.zeros((6,0))
    pos=np.array([e['pos_m'] for e in engines],float)
    dirs=np.array([unit(vec((gdirs or {}).get(e['id'],e['direction']))) for e in engines])
    caps=np.array([float(e['max_N']) for e in engines])
    return engines,np.vstack((dirs.T,np.cross(pos-cg,dirs).T))*caps

def allocation_wrench(A,b):
    """Largest realizable exact six-component wrench with bounded thrusters."""
    n=A.shape[1];b=vec(b)
    if n==0 or np.linalg.norm(b)<1e-6: return np.zeros(n),0.0 if n==0 else 1.0
    scales=np.r_[np.full(3,1e6),np.full(3,2e7)]
    eq=np.column_stack((A,-b))/scales[:,None]
    sol=linprog(np.r_[np.zeros(n),-1.],A_eq=eq,b_eq=np.zeros(6),
                bounds=[(0,1)]*(n+1),method='highs')
    if not sol.success: raise RuntimeError('RCS allocation LP: '+sol.message)
    fraction=float(sol.x[-1])
    if fraction<1e-10:return np.zeros(n),0.0
    least=linprog(np.ones(n),A_eq=A/scales[:,None],b_eq=b*fraction/scales,
                  bounds=[(0,1)]*n,method='highs')
    if not least.success: raise RuntimeError('RCS minimum allocation LP: '+least.message)
    return np.clip(least.x,0.,1.),float(np.clip(fraction,0.,1.))

def allocation(A,target_torque):
    """Request exact torque with zero net force."""
    return allocation_wrench(A,np.r_[np.zeros(3),target_torque])

def reference(t,T,axis,angle_rad=math.pi):
    u=np.clip(t/T,0,1)
    theta=angle_rad*(10*u**3-15*u**4+6*u**5)
    w=angle_rad/T*(30*u*u-60*u**3+30*u**4)
    a=angle_rad/T**2*(60*u-180*u*u+120*u**3)
    direction=np.eye(3)[axis] if isinstance(axis,(int,np.integer)) else unit(vec(axis))
    return qaxis(axis,theta),direction*w,direction*a

def initial_state(ship,experiment):
    levels=validate(ship)
    start=experiment.get('initial',{})
    q=unit(vec(start.get('q_body_to_inertial',[1.,0.,0.,0.])))
    return {'y':np.r_[q,vec(start.get('omega_rad_s',[0,0,0])),vec(start.get('position_m',[0,0,0])),
                       vec(start.get('velocity_m_s',[0,0,0]))],
            'tanks':levels,'act':{e['id']:0.0 for e in ship.get('rcs',[])},
            'cmd':{e['id']:0.0 for e in ship.get('rcs',[])},
            'gdir':{e['id']:gimbal_direction(e,np.radians(e['gimbal'].get('initial_angles_deg',[0,0]))) if 'gimbal' in e else unit(vec(e['direction'])) for e in ship.get('rcs',[])},
            'gangle':{e['id']:np.radians(e['gimbal'].get('initial_angles_deg',[0,0]))
                      for e in ship.get('rcs',[]) if 'gimbal' in e},
            'torch_act':{e['id']:0. for e in ship.get('torch',[])},
            'torch_cmd':{e['id']:0. for e in ship.get('torch',[])},
            'torch_mode':{e['id']:e.get('default_mode','CRUISE') for e in ship.get('torch',[])},
            'torch_dir':{e['id']:unit(vec(e['direction'])) for e in ship.get('torch',[])},
            't':0.,'metric_path_m':0.,'metric_unresolved':False,
            'depletion_steps':0,'propellant_unresolved':False,
            'warnings':[],'fuel_used_kg':{},'rcs_propellant_unresolved':False,
            'rcs_impulse_Ns':0.,'torch_impulse_Ns':0.}

def integrate(y,F,T,m,I,dt,grav_mu=0.):
    inv=np.linalg.inv(I)
    def rhs(z):
        q=unit(z[:4]);w=z[4:7];r=z[7:10]
        a=rotation(q).apply(F)/m
        if grav_mu:
            norm=np.linalg.norm(r)
            if norm<=0:raise ValueError('gravity requires nonzero position')
            a-=grav_mu*r/norm**3
        return np.r_[.5*qmul(q,np.r_[0.,w]),inv@(T-np.cross(w,I@w)),z[10:13],a]
    k1=rhs(y);k2=rhs(y+.5*dt*k1);k3=rhs(y+.5*dt*k2);k4=rhs(y+dt*k3)
    yy=y+dt*(k1+2*k2+2*k3+k4)/6
    yy[:4]=unit(yy[:4])
    return yy

def torch_force(engine,mode,mass,throttle,cg):
    spec=engine['modes'][mode]
    ve=exhaust_velocity(spec)
    F=float(spec['max_N'])*float(np.clip(throttle,0,1))
    if engine.get('max_N') is not None:F=min(F,float(engine['max_N']))
    if engine.get('jet_power_ceiling_W') and ve is not None:F=min(F,2*engine['jet_power_ceiling_W']/ve)
    if engine.get('accel_cap_g'):F=min(F,engine['accel_cap_g']*G0*mass)
    nominal=unit(vec(engine['direction']))
    actual=nominal.copy(); angle=0.
    if engine.get('auto_trim',False):
        target=unit(cg-vec(engine['pos_m']))
        angle=math.acos(float(np.clip(nominal@target,-1,1)))
        maxangle=math.radians(engine.get('gimbal_limit_deg',0))
        if angle>maxangle+1e-9:
            perp=unit(target-nominal*(target@nominal))
            actual=math.cos(maxangle)*nominal+math.sin(maxangle)*perp
        else:actual=target
    return F,ve,unit(actual),math.degrees(angle)

def exhaust_velocity(spec):
    ve=spec.get('ve_m_s')
    isp=spec.get('isp_s')
    if ve is not None and float(ve)<=0:raise ValueError('positive exhaust velocity required')
    if isp is not None and float(isp)<=0:raise ValueError('positive Isp required')
    if ve is not None and isp is not None and not math.isclose(float(ve),float(isp)*G0,rel_tol=1e-6):
        raise ValueError('inconsistent Isp and exhaust velocity')
    return float(ve) if ve is not None else (float(isp)*G0 if isp is not None else None)

def gimbal_direction(engine,angles):
    """Two mechanical angles, each bounded; not a circular cone limit.
    d=cos(b)cos(a)n + cos(b)sin(a)t + sin(b)axial.
    """
    nominal=unit(vec(engine['direction']))
    axial=unit(vec(engine['gimbal']['axial_direction']))
    if abs(axial@nominal)>1e-8:raise ValueError('gimbal axial direction must be perpendicular to neutral')
    tangent=np.cross(axial,nominal);a,b=angles
    return math.cos(b)*math.cos(a)*nominal+math.cos(b)*math.sin(a)*tangent+math.sin(b)*axial

def dynamic_gimbals(engines,state,wrench,elapsed,duration,dt):
    peakrate=0.;peakangle=0.;limited=0
    for e in engines:
        if 'gimbal' not in e:continue
        g=e['gimbal'];angles=state['gangle'][e['id']]
        policy=g.get('policy','fixed')
        if policy=='wrench_sign':
            positive=wrench[int(g.get('wrench_component',4))]>=0
            target=g['positive_angles_deg'] if positive else g['negative_angles_deg']
        elif policy=='phase_fraction':
            target=g['positive_angles_deg'] if elapsed<duration*g.get('switch_fraction',.5) else g['negative_angles_deg']
        elif policy=='schedule':
            target=g.get('target_angles_deg',[0,0])
            for point in g.get('schedule',[]):
                if elapsed>=point['time_s']:target=point['angles_deg']
        elif policy=='fixed':target=g.get('target_angles_deg',[0,0])
        else:raise ValueError('unknown gimbal policy: '+policy)
        clipped=np.clip(vec(target),-g['limit_deg'],g['limit_deg'])
        limited+=int(np.any(abs(clipped-vec(target))>1e-9))
        target=np.radians(clipped);tau=float(g.get('lag_s',0))
        requested=(target-angles)*(1-math.exp(-dt/tau)) if tau else target-angles
        cap=math.radians(g['rate_deg_s'])*dt
        change=np.clip(requested,-cap,cap)
        limited+=int(np.any(abs(requested)>cap+1e-12))
        angles=angles+change;state['gangle'][e['id']]=angles
        state['gdir'][e['id']]=gimbal_direction(e,angles)
        peakrate=max(peakrate,float(np.max(abs(change)))/dt*180/math.pi)
        peakangle=max(peakangle,float(np.max(abs(angles)))*180/math.pi)
    return peakrate,peakangle,limited

def actuator_average(old,command,dt,tau):
    if not tau:return command,command
    decay=math.exp(-dt/tau)
    return command+(old-command)*tau/dt*(1-decay),command+(old-command)*decay

def sequence_check(experiment):
    """Optional explicit operating constraints, experimental scheduling only."""
    rules=experiment.get('sequence_constraints',{});previous=None;coast=0.
    for phase in experiment['phases']:
        kind=phase['kind']
        allowed=rules.get('allowed_next',{}).get(previous)
        if allowed is not None and kind not in allowed:raise ValueError('operating sequence forbids '+str(previous)+' -> '+kind)
        required=rules.get('coast_before_s',{}).get(kind,0.)
        if coast+1e-9<required:raise ValueError('operating sequence requires coast before '+kind)
        coast=coast+phase['duration_s'] if kind=='coast' else 0.
        previous=kind

def gimbal_update(engine,now,dt):
    """Rate-limited direction command; fixed or prescribed-vector gimbal candidate."""
    target=unit(vec(engine.get('gimbal_target_direction',engine['direction'])))
    nominal=unit(vec(engine['direction']))
    bound=math.radians(engine.get('gimbal_limit_deg',0))
    theta=math.acos(float(np.clip(nominal@target,-1,1)))
    if theta>bound+1e-12:
        if bound<=0:target=nominal
        else:
            perp=unit(target-nominal*(target@nominal))
            target=math.cos(bound)*nominal+math.sin(bound)*perp
    step=math.radians(engine.get('gimbal_slew_deg_s',0))*dt
    angle=math.acos(float(np.clip(now@target,-1,1)))
    if angle<=step or angle<1e-12:return target
    fraction=step/angle
    return unit(now*math.sin((1-fraction)*angle)/math.sin(angle)+target*math.sin(fraction*angle)/math.sin(angle))

def evaluate(checks,metrics,indeterminate=False):
    if indeterminate:
        measured=evaluate(checks,metrics,False)
        return {'status':'fail' if measured['status']=='fail' else 'indeterminate','checks':measured['checks'],
                'reason':'metric physical arrival state unresolved; request/hold and conditional path checks do not close endpoints'}
    out=[]
    for key,bounds in checks.items():
        val=metrics.get(key)
        if val is None:
            out.append({'metric':key,'status':'indeterminate','reason':'unmeasured'})
            continue
        if isinstance(bounds,dict):
            ok=('min' not in bounds or val>=bounds['min']) and ('max' not in bounds or val<=bounds['max'])
        else:ok=val<=bounds
        out.append({'metric':key,'measured':float(val),'criterion':bounds,'status':'pass' if ok else 'fail'})
    status='fail' if any(v['status']=='fail' for v in out) else ('indeterminate' if any(v['status']=='indeterminate' for v in out) else 'pass')
    return {'status':status,'checks':out}

def canonical_metric_operation(phase, pre_state, torch_outputs):
    """Execute the request/hold state machine, never an uncalibrated U^M map.

    Gate records are experiment declarations, not independently verified certificates.
    The copied source's open physics holds cannot be cleared by these declarations.
    """
    import ast, sys
    root=Path(__file__).resolve().parents[3]  # actual repository root; no old 'source/' checkout
    card_path='src/wayfarer_e1_metric_frontier_closure.py'
    support_path='src/wayfarer_2226_frontier_accountant.py'
    g10_path='wayfarer/lab/g10/g10_flight_dynamics.py'
    canon_path='canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md'
    spec_path='engineering/experience_one/WAYFARER_E1_METRIC_CANON_AND_GLB_INTEGRATION_SPEC_v0.1.md'
    # Import the existing repo source card, not a duplicate; suppress bytecode.
    old_bytecode=sys.dont_write_bytecode
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(root))
    try:
        from src.wayfarer_e1_metric_frontier_closure import build_metric_closure
        closure=build_metric_closure(phase.get('support_scenario','MVP_2226'))
    finally:
        sys.path.pop(0)
        sys.dont_write_bytecode=old_bytecode
    # G10 has unrelated executable imports; read its literal transition table only.
    tree=ast.parse((root/g10_path).read_text())
    allowed=next(ast.literal_eval(n.value) for n in tree.body
                 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALLOWED' for t in n.targets))
    mode=phase['mode']
    beta=float(phase.get('beta',closure['modes'].get(mode,{}).get('beta',0)))
    if not math.isfinite(beta) or beta<0:raise ValueError('invalid metric beta')
    if beta>=1:raise ValueError('FTL metric BLACK / hard kill')
    if mode not in closure['modes'] or beta!=float(closure['modes'][mode]['beta']):
        raise ValueError('uncertified metric mode/beta; saturation ~0.678c prohibited')
    if phase.get('major_torch_active') or max([0.]+list(torch_outputs.values()))>0:
        raise ValueError('major torch/high metric overlap prohibited; shutdown must be established')
    if mode in ('EXPEDITE','HARD') and phase.get('degraded_critical_node_sector') is True:
        raise ValueError(mode+' requires no degraded critical node sector (Canon II §11)')
    requirements={name:{key:float(value) for key,value in row.items()}
                  for name,row in closure['modes'].items()}
    sequence=phase.get('operating_sequence',[])
    aliases={'TORCH_SHUTDOWN':'COAST','RELATIONAL_READY':'METRIC_PREP',
             'METRIC_CRUISE':'METRIC_TRANSPORT','NRE_RELAX_REPHASE':'NRE_RELAXATION'}
    e1={'METRIC_PREP':'RELATIONAL_READY','METRIC_TRANSPORT':'METRIC_CRUISE',
        'NRE_RELAXATION':'NRE_RELAX_REPHASE'}
    normalized=[aliases.get(p['state'],p['state']) for p in sequence]
    for a,b in zip(normalized,normalized[1:]):
        if b not in allowed.get(a,()):raise ValueError('illegal canonical transition: '+a+' -> '+b)
    if sequence and normalized!=['COAST','METRIC_PREP','METRIC_RAMP','METRIC_TRANSPORT',
                                 'METRIC_COLLAPSE','NRE_RELAXATION','COAST']:
        raise ValueError('canonical operation requires coast/prep/ramp/transport/collapse/relaxation/coast')
    trace=[];requested_time=0.;input_holds=[]
    for i,(p,state_name) in enumerate(zip(sequence,normalized)):
        duration=p.get('duration_s')
        if duration is None:
            input_holds.append(p['state']+' duration_s missing (explicit experiment input required)')
        elif not math.isfinite(float(duration)) or float(duration)<0:
            raise ValueError('finite nonnegative operating phase duration required')
        elif state_name=='METRIC_RAMP' and float(duration)!=requirements[mode]['ramp_s']:
            raise ValueError('ramp duration differs from source-derived mode requirement')
        elif state_name not in ('COAST',) and float(duration)<=0:
            raise ValueError('positive operating phase duration required')
        if p.get('major_torch_active') or any(float(v)>0 for v in p.get('torch_outputs',{}).values()):
            raise ValueError('major torch/high metric overlap prohibited in operating sequence')
        if p.get('mode',mode)!=mode:raise ValueError('mid-field metric mode switching unsupported')
        trace.append({'requested_state':p['state'],'g10_state':state_name,
                      'e1_state':e1.get(state_name,state_name),'duration_s':duration,
                      'requested_start_s':requested_time,
                      'duration_basis':'source mode card' if state_name=='METRIC_RAMP' else 'experiment input; no physical time constant',
                      'status':'NOT_ENTERED'})
        requested_time=None if duration is None or requested_time is None else requested_time+float(duration)
    if not sequence:input_holds.append('operating_sequence missing; prep/relaxation/collapse/transport times not assumed')
    gates={}
    supplied=phase.get('gates',{})
    for name in ('environment','plant','power_thermal','topology','conservation','u_calibration','bank_abort','rset'):
        record=supplied.get(name)
        reasons=[]
        if not isinstance(record,dict):reasons.append('missing evidence record; booleans do not certify')
        else:
            if record.get('status')!='PASS':reasons.append('declared status '+str(record.get('status','UNKNOWN')))
            if record.get('revoked') is not False:reasons.append('non-revocation not established')
            for key in ('standard_version','record_id','authority','signature','provenance'):
                if not record.get(key):reasons.append('missing '+key)
            now=phase.get('certification_time_s')
            start=record.get('valid_from_s');end=record.get('valid_until_s')
            if now is None or start is None or end is None:reasons.append('validity window not established')
            elif not (float(start)<=float(now)<=float(end)):reasons.append('stale/not yet valid')
            age=record.get('cache_age_s');limit=record.get('max_cache_age_s')
            if age is None or limit is None:reasons.append('cache freshness not established')
            elif not (0<=float(age)<=float(limit)):reasons.append('stale cache')
            scope={**phase.get('certification_scope',{}),'mode':mode,'ramp_s':requirements[mode]['ramp_s']}
            for key in ('ship_id','array_id','lot_id','environment_class','ramp_family','mode','ramp_s'):
                if key not in scope or key not in record:reasons.append('missing applicability '+key)
                elif record[key]!=scope[key]:reasons.append('not applicable: '+key)
            # Even a syntactically complete record has no trusted validation adapter here.
            reasons.append('experiment declaration unverified; no external certification/calibration authority')
        gates[name]={'status':'HOLD','reasons':reasons,'supplied_record':copy.deepcopy(record)}
    limits=[]
    capacities=phase.get('declared_capacities',{})
    for key,required in (('cold_load_w',requirements[mode]['cold_load_w']),
                         ('delivered_electrical_w',requirements[mode]['delivered_electrical_w']),
                         ('required_upstream_electrical_w',requirements[mode]['required_upstream_electrical_w'])):
        available=capacities.get(key)
        if available is not None and (not math.isfinite(float(available)) or float(available)<0):
            raise ValueError('invalid declared capacity: '+key)
        limits.append({'requirement':key,'required':required,'declared_available':available,
                       'status':'UNKNOWN' if available is None else ('FAIL' if float(available)<required else 'DECLARED_SUFFICIENT'),
                       'scope':'input comparison only; no installed hardware certification'})
    if phase.get('hard_veto'):raise ValueError('metric hard veto: '+str(phase['hard_veto']))
    current='COAST'
    if trace and not input_holds:
        trace[0]['status']='REQUEST_ACCEPTED'
        current='RELATIONAL_READY'
        trace[1]['status']='REQUEST_ACCEPTED'
        trace[2]['status']='HOLD'
    else:
        if trace:trace[0]['status']='HOLD'
    # No phase after acquisition HOLD is entered. Schedule times are not flight times.
    terminal={key:None for key in ('position_m','velocity_m_s','mass_kg','remass_kg','tanks_kg',
                                   'matching_delta_v_m_s','q_body_to_inertial','omega_rad_s',
                                   'ordinary_energy_j','ordinary_momentum_kg_m_s')}
    illustrative=None
    if phase.get('illustrative_profile')=='linear_ramp_plateau_collapse':
        ramp=requirements[mode]['ramp_s'];duration=float(phase['duration_s'])
        if not math.isfinite(duration) or duration<2*ramp:raise ValueError('illustrative duration shorter than ramp plus collapse')
        illustrative={'profile':phase['illustrative_profile'],'active_duration_s':duration,
                      'metric_path_m':beta*C*(duration-ramp),
                      'scope':'CONDITIONAL experiment-declared linear profile; no physical trajectory or finite energy accounting',
                      'energy_j':None}
    # Only an explicitly scoped ordinary Solar System phase gets the
    # Canon II §7.1a new-lab ENERGY-B default. Legacy FQ1-FQ10 never
    # declare this regime, so their canonical HOLD stays pinned.
    # Position, environmental certification and capture remain HOLD.
    arrival=None
    if (phase.get('canon_arrival') or {}).get('regime')=='ORDINARY_SOLAR_SYSTEM':
        from metric_arrival_v1 import canonical_energy_b_arrival,new_lab_metric_arrival_rule
        rule=new_lab_metric_arrival_rule(phase)
        if rule=='ENERGY_ORBIT_RELATIVE_B':
            scoped_phase={**phase,'arrival_rule':rule}
            arrival=canonical_energy_b_arrival(scoped_phase,pre_state,closure['modes'][mode])
            terminal['velocity_m_s']=arrival['arrival_velocity_m_s']
            terminal['matching_delta_v_m_s']=arrival['relative_mismatch_m_s']
    return {'sequence_status':'VALID' if sequence and not input_holds else 'INDETERMINATE',
            'execution_status':'ARRIVAL_VELOCITY_RESOLVED' if arrival else 'HOLD',
            'arrival_velocity_resolution':arrival,
            'physical_status':'INDETERMINATE','last_accepted_state':current,
            'held_request':('METRIC_COLLAPSE_CERTIFICATION_AND_CAPTURE' if arrival else
                            ('METRIC_RAMP' if current=='RELATIONAL_READY' else 'RELATIONAL_READY')),
            'phase_trace':trace,'input_holds':input_holds,'gates':gates,'declared_load_checks':limits,
            'pre_metric_state':copy.deepcopy(pre_state),'terminal_state':terminal,
            'mode':mode,'mode_requirements':requirements,'requirements_class':'SOURCE_DERIVED_REQUIREMENTS; not measured loads',
            'support_load_scope':'scenario-derived upstream support only; UNKNOWN correction/standby/switching/wake/duty loads excluded; distribution area conditional, not installed geometry or automatically additive to canon area',
            'support_scenario':closure['scenario'],'producer_register_version':closure['producer_register_version'],
            'producer_version_hash':closure['producer_version_hash'],
            'requirement_provenance':{'mode_card':canon_path+' §5; '+card_path+':build_metric_closure',
                'upstream_support':spec_path+' §3; '+support_path+' (scenario efficiencies; excludes UNKNOWN corrections)',
                'transitions':g10_path+':ALLOWED; '+spec_path+' §4',
                'gates':canon_path+' §§6–7, 10–11; '+spec_path+' §§4–5'},
            'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest()
                             for p in (card_path,support_path,g10_path,canon_path,spec_path)},
            'physics_validation_holds':list(closure['physics_validation_holds']),
            'unknown':{key:'UNKNOWN' for key in ('environmental_correction','duty_profile','rset','wake',
                       'finite_conservation_ledgers','bank_abort_profile','terminal_state','total_energy_accounting')},
            'illustrative_profile':illustrative,
            'time_basis':('natural arrival velocity evaluated at moving destination epoch; physical collapse/time progression HOLD'
                          if arrival else 'requested experiment schedule only; no physical flight time advanced on HOLD'),
            'authority_boundary':'in-world crew-rated operation exists; open numerical laws do not revoke it'}

def run(ship,experiment,dt=.1,sample_s=1.):
    """Single mutable physical spacecraft state across conventional phases and explicit metric transitions."""
    sequence_check(experiment)
    ship=copy.deepcopy(ship);state=initial_state(ship,experiment)
    if dt<=0 or sample_s<=0:raise ValueError('positive timestep and sample interval required')
    phases=[];hist=[];metrics={};rcs_trace=[]
    nextsample=0.0
    for phase in experiment['phases']:
        kind=phase['kind'];T=float(phase.get('duration_s',0))
        if (kind in ('rcs_turn','rcs_translate') and dt>0.2+1e-12 and
                not experiment.get('allow_coarse_rcs_dt_for_sensitivity_study',False)):
            raise ValueError('RCS control requires >= 5 Hz (dt <= 0.2 s); '
                             'coarse dt allowed only for explicit sensitivity studies')
        if T<=0:raise ValueError('positive phase duration required')
        if state['metric_unresolved']:raise ValueError('canonical metric arrival unresolved: cannot resume ordinary flight or another metric law')
        post_hold=float(phase.get('post_hold_s',0.)) if kind=='rcs_turn' else 0.
        if post_hold<0: raise ValueError('post_hold_s must be nonnegative')
        total_phase_time=T+post_hold
        main_n=max(1,math.ceil(T/dt));main_h=T/main_n
        steps=[(j*main_h,main_h) for j in range(main_n)]
        if post_hold:
            hold_n=max(1,math.ceil(post_hold/dt));hold_h=post_hold/hold_n
            steps += [(T+j*hold_h,hold_h) for j in range(hold_n)]
        t0=state['t']
        qstart=state['y'][:4].copy();ystart=state['y'].copy()
        mass_start,cg_start,I_start=mass_properties(ship,state['tanks'])
        start_unresolved=state['metric_unresolved']
        tanks_start=dict(state['tanks'])
        peak_gimbal_rate=0.;peak_gimbal_angle=0.;gimbal_limits=0
        peak_cmd_slew=0.;peak_throttle=0.;slew_limits=0;throttle_limits=0
        thrust_limits=0;allocation_limits=0;phase_prop_unresolved=False
        peak_wrench_residual=0.;peak_force_residual=0.;depletion_start=state['depletion_steps']
        actuators_start={'rcs_cmd':dict(state['cmd']),'rcs_act':dict(state['act']),
                         'torch_cmd':dict(state['torch_cmd']),'torch_act':dict(state['torch_act']),
                         'gimbal_angles_deg':{k:np.degrees(v).tolist() for k,v in state['gangle'].items()}}
        canonical=None
        if kind=='metric':
            idle=experiment.get('sequence_constraints',{}).get('metric_entry_max_throttle')
            if idle is not None and max([0.]+list(state['act'].values())+list(state['torch_act'].values()))>idle:
                raise ValueError('metric entry requires idle propulsion actuators')
            if ship['metric'][phase['model']]['law']=='canonical_envelope':
                canonical=canonical_metric_operation(phase,{
                    'time_s':t0,'state_vector':ystart.tolist(),
                    'position_m':ystart[7:10].tolist(),'velocity_m_s':ystart[10:13].tolist(),
                    'q_body_to_inertial':ystart[:4].tolist(),'omega_rad_s':ystart[4:7].tolist(),
                    'mass_kg':mass_start,'tanks_kg':tanks_start,'cg_m':cg_start.tolist(),
                    'inertia_kg_m2':I_start.tolist(),'actuators':actuators_start,
                    'experiment_initial_inputs':copy.deepcopy(experiment.get('initial',{}))},state['torch_act'])
                state['metric_unresolved']=True
                profile=canonical['illustrative_profile']
                state['metric_path_m']=None if profile is None else profile['metric_path_m']
                steps=[]
                hist.append({'time_s':t0,'phase':'metric',
                    'operating_state':'VELOCITY_RESOLVED_PHYSICAL_HOLD' if canonical['arrival_velocity_resolution'] else 'HOLD',
                    **{key:None for key in ('position_m','velocity_m_s','q_body_to_inertial',
                        'omega_rad_s','mass_kg','cg_m','propellant_kg','inertia_kg_m2','force_body_N','torque_body_Nm')},
                    'gimbal_angles_deg':None,'metric_path_m':state['metric_path_m']})
        axis={'roll':0,'pitch':1,'yaw':2}.get(phase.get('axis','pitch'),1)
        if kind=='rcs_turn' and 'axis_vector_body' in phase:
            # FQ11-only direct pointing: unchanged controller/nozzles/limits.
            axis=unit(vec(phase['axis_vector_body']))
        if kind=='rcs_turn':
            angle=float(phase.get('angle_deg',180))
            if not -360<=angle<=360: raise ValueError('single turn requires -360..360 degrees')
            target=qmul(qstart,qaxis(axis,math.radians(angle)))
        if kind=='rcs_translate':
            dvbody=vec(phase['delta_v_body_m_s'])
            dvtarget=rotation(qstart).apply(dvbody)
            velstart=state['y'][10:13].copy()
        maxforce=0.;maxother=0.;minfraction=1.;maxtrim=0.;peak_phase_rate=0.
        phasefuel=0.;unresolved=canonical is not None;phase_rcs_unresolved=False
        gate_entry=None;gate_hold=0.;at_target=None
        for j,(t,h) in enumerate(steps):
            mass,cg,I=mass_properties(ship,state['tanks'])
            y=state['y'];q=y[:4];w=y[4:7]
            F=np.zeros(3);torque=np.zeros(3)
            mdots={tid:0. for tid in state['tanks']}
            extra={'torch':[]};scalar_rcs_step=0.;scalar_torch_step=0.
            if kind=='metric':
                mconf=phase['model']; mode=phase['mode']
                config=ship['metric'][mconf]
                v=float(config['modes'][mode]['beta'])*C
                ramp=float(config['modes'][mode]['ramp_s'])
                if ramp<=0 or T<2*ramp:raise ValueError('metric duration shorter than ramp plus collapse')
                plateau=T-2*ramp
                def speed(tt):
                    if tt<ramp:return v*tt/ramp
                    if tt<ramp+plateau:return v
                    return v*max(0.,(T-tt)/ramp)
                ds=.5*(speed(t)+speed(t+h))*h
                state['metric_path_m']+=ds
                if config['law'] in ('experimental_coordinate_shift','experimental_frame_rotation'):
                    # Ordinary torque-free propagation continues between stipulated maps.
                    state['y']=integrate(y,np.zeros(3),np.zeros(3),mass,I,h,
                                         float(experiment.get('gravity_mu_m3_s2',0)))
                    if config['law']=='experimental_coordinate_shift':
                        direction=unit(vec(phase.get('direction_inertial',[1,0,0])))
                        state['y'][7:10]+=direction*ds
                    else:
                        # A declared rotating-coordinate map, not a physical torque/impulse law.
                        da=math.radians(config['rotation_deg'])*ds/(v*(T-ramp))
                        axis_map=unit(vec(config.get('rotation_axis',[0,0,1])))
                        rr=Rotation.from_rotvec(axis_map*da)
                        pivot=vec(config.get('pivot_m',[0,0,0]))
                        state['y'][7:10]=pivot+rr.apply(state['y'][7:10]-pivot)
                        state['y'][10:13]=rr.apply(state['y'][10:13])
                        qr=rr.as_quat();state['y'][:4]=qmul(np.r_[qr[3],qr[:3]],state['y'][:4])
                else:raise ValueError('unsupported metric law: '+str(config['law']))
                state['t']+=h
            else:
                # All installed torch actuators retain command/output state across phases.
                for engine in ship.get('torch',[]):
                    mode=phase.get('mode',state['torch_mode'][engine['id']]) if kind=='torch' else state['torch_mode'][engine['id']]
                    state['torch_mode'][engine['id']]=mode
                    if mode not in engine['modes']:raise ValueError('unknown torch mode: '+mode)
                    requested=float(phase.get('engine_throttles',{}).get(engine['id'],phase.get('throttle',1.))) if kind=='torch' and engine.get('enabled',True) else 0.
                    clipped=float(np.clip(requested,0,1));throttle_limits+=int(requested!=clipped)
                    oldcmd=state['torch_cmd'][engine['id']]
                    cap=float(engine.get('command_slew_fullscale_s',1e30))*h
                    cmd=float(np.clip(clipped,oldcmd-cap,oldcmd+cap));slew_limits+=int(abs(cmd-clipped)>1e-12)
                    avg_t,act=actuator_average(state['torch_act'][engine['id']],cmd,h,float(engine.get('lag_s',0)))
                    state['torch_act'][engine['id']]=act;state['torch_cmd'][engine['id']]=cmd
                    peak_cmd_slew=max(peak_cmd_slew,abs(cmd-oldcmd)/h);peak_throttle=max(peak_throttle,avg_t)
                    f,ve,d,trim=torch_force(engine,mode,mass,avg_t,cg)
                    if engine.get('tvc_rate_deg_s') is not None:
                        proxy=dict(direction=engine['direction'],gimbal_target_direction=d.tolist(),
                                   gimbal_limit_deg=engine.get('gimbal_limit_deg',0),
                                   gimbal_slew_deg_s=engine['tvc_rate_deg_s'])
                        olddir=state['torch_dir'][engine['id']]
                        d=gimbal_update(proxy,olddir,h);state['torch_dir'][engine['id']]=d
                        peak_gimbal_rate=max(peak_gimbal_rate,math.degrees(math.acos(float(np.clip(olddir@d,-1,1))))/h)
                    maxtrim=max(maxtrim,trim)
                    thrust_limits+=int(f<engine['modes'][mode]['max_N']*avg_t-1e-8)
                    extra['torch'].append((engine,f,ve,d))
                if kind=='rcs_turn':
                    rel,wd,ad=reference(t,T,axis,math.radians(angle))
                    qd=qmul(qstart,rel)
                    alpha=ad+9*qerror(q,qd)+6*(wd-w)
                    wanted=I@alpha+np.cross(w,I@w)
                elif kind=='rcs_translate':
                    z=np.clip(t/T,0,1)
                    smooth=10*z**3-15*z**4+6*z**5
                    smoothdot=(30*z*z-60*z**3+30*z**4)/T
                    desired_vel=velstart+dvtarget*smooth
                    desired_accel=dvtarget*smoothdot+2*(desired_vel-y[10:13])
                    force_request=mass*rotation(q).inv().apply(desired_accel)
                    wanted=I@(9*qerror(q,qstart)-6*w)+np.cross(w,I@w)
                elif kind in ('torch','coast') and phase.get('hold_attitude',False):
                    wanted=I@(9*qerror(q,qstart)-6*w)+np.cross(w,I@w)
                elif kind in ('coast','torch'):
                    wanted=np.zeros(3)
                else:raise ValueError('unknown phase: '+kind)
                if extra['torch']:
                    torch_torque=np.zeros(3)
                    for engine,f,ve,d in extra['torch']:torch_torque+=np.cross(vec(engine['pos_m'])-cg,f*d)
                    wanted-=torch_torque
                engines,_=rcs_wrench(ship,cg,state['gdir'])
                request=np.r_[force_request if kind=='rcs_translate' else np.zeros(3),wanted]
                gr,ga,gl=dynamic_gimbals(engines,state,request,t,T,h)
                peak_gimbal_rate=max(peak_gimbal_rate,gr);peak_gimbal_angle=max(peak_gimbal_angle,ga);gimbal_limits+=gl
                engines,A=rcs_wrench(ship,cg,state['gdir'])
                enabled_rcs=kind in ('rcs_turn','rcs_translate') or (kind in ('torch','coast') and phase.get('hold_attitude',False))
                if kind=='rcs_translate':
                    u,fraction=allocation_wrench(A,np.r_[force_request,wanted])
                else:
                    u,fraction=allocation(A,wanted) if enabled_rcs else (np.zeros(len(engines)),1.0)
                minfraction=min(minfraction,fraction)
                allocation_limits+=int(fraction<1.-1e-9)
                # Same fractional slew for the full command vector, preserving paired thruster balance.
                if engines:
                    # Command and realized actuator output are different states.
                    # Slew applies to the command; first-order lag applies to actual thrust.
                    # The original study.py tracks prev_cmd and actual independently.
                    old_cmd=np.array([state['cmd'][e['id']] for e in engines])
                    old_actual=np.array([state['act'][e['id']] for e in engines])
                    delta=u-old_cmd
                    maxslew=min(float(e.get('command_slew_fullscale_s',10.)) for e in engines)
                    scale=min(1.,maxslew*h/max(np.max(abs(delta)),1e-30))
                    cmd=old_cmd+scale*delta
                    slew_limits+=int(scale<1.-1e-12)
                    peak_cmd_slew=max(peak_cmd_slew,float(np.max(abs(cmd-old_cmd)))/h)
                    avg=np.zeros(len(engines))
                    for k,e in enumerate(engines):
                        tau=float(e.get('lag_s',.05))
                        if tau>0:
                            ee=math.exp(-h/tau)
                            avg[k]=cmd[k]+(old_actual[k]-cmd[k])*tau/h*(1-ee)
                            state['act'][e['id']]=float(cmd[k]+(old_actual[k]-cmd[k])*ee)
                        else:
                            avg[k]=cmd[k]
                            state['act'][e['id']]=float(cmd[k])
                        state['cmd'][e['id']]=float(cmd[k])
                        if 'gimbal' not in e and e.get('gimbal_limit_deg',0)>0:
                            olddir=state['gdir'][e['id']]
                            state['gdir'][e['id']]=gimbal_update(e,olddir,h)
                            peak_gimbal_rate=max(peak_gimbal_rate,math.degrees(math.acos(float(np.clip(olddir@state['gdir'][e['id']],-1,1))))/h)
                    peak_throttle=max(peak_throttle,float(np.max(avg)))
                    thrust_limits+=int(np.any(avg>=1.-1e-9))
                    # Recalculate actual wrench after gimbals physically move.
                    _,Aactual=rcs_wrench(ship,cg,state['gdir'])
                    # Build independent engine contributions before tank availability scaling.
                    contributions=[]
                    for k,e in enumerate(engines):
                        f=avg[k]*e['max_N'];ve=exhaust_velocity(e);tank=e.get('tank')
                        contributions.append((e,Aactual[:3,k]*avg[k],Aactual[3:,k]*avg[k],f,ve,'rcs'))
                        if f>0 and (tank is None or ve is None):
                            state['rcs_propellant_unresolved']=True;phase_rcs_unresolved=True
                            if 'RCS propellant model unspecified' not in state['warnings']:
                                state['warnings'].append('RCS propellant model unspecified')
                else:contributions=[]
                for engine,f,ve,d in extra['torch']:
                    contributions.append((engine,f*d,np.cross(vec(engine['pos_m'])-cg,f*d),f,ve,'torch'))
                for e,ff,tt,f,ve,source in contributions:
                    if f>0 and (e.get('tank') is None or ve is None):
                        state['propellant_unresolved']=True;phase_prop_unresolved=True
                        warning=source.upper()+' propellant model unspecified'
                        if warning not in state['warnings']:state['warnings'].append(warning)
                    if e.get('tank') is not None and ve is not None:mdots[e['tank']]+=f/ve
                # Empty tank shuts down only engines fed by that tank.
                factors={tank:min(1.,state['tanks'][tank]/(dot*h)) if dot*h>0 else 1.
                         for tank,dot in mdots.items()}
                if any(v<1.-1e-12 for v in factors.values()):
                    state['depletion_steps']+=1
                    if 'propellant depleted within step: thrust curtailed' not in state['warnings']:
                        state['warnings'].append('propellant depleted within step: thrust curtailed')
                actual_levels=[];engine_samples=[]
                for e,ff,tt,f,ve,source in contributions:
                    factor=factors.get(e.get('tank'),1.) if ve is not None else 1.
                    F+=ff*factor;torque+=tt*factor
                    # Evidence only: expose the already realized contributions, never
                    # change allocation, actuator state, fuel accounting or integration.
                    if source=='rcs':
                        command_N=state['cmd'][e['id']]*e['max_N']
                        end_N=state['act'][e['id']]*e['max_N']
                        direction=state['gdir'][e['id']]
                        mode=None
                    else:
                        mode=state['torch_mode'][e['id']]
                        command_N=state['torch_cmd'][e['id']]*e['modes'][mode]['max_N']
                        end_N=torch_force(e,mode,mass,state['torch_act'][e['id']],cg)[0]
                        direction=ff/f if f>0 else unit(vec(e['direction']))
                    if max(command_N,f,end_N)>0:
                        engine_samples.append({'id':e['id'],'kind':source,'mode':mode,
                            'command_N':float(command_N),'actual_N':float(f*factor),
                            'actuator_end_N':float(end_N*factor),
                            'before_tank_N':float(f),'tank_factor':float(factor),
                            've_m_s':ve,'direction':direction.tolist(),
                            'force_body_N':(ff*factor).tolist(),'torque_body_Nm':(tt*factor).tolist()})
                    if source=='rcs':
                        scalar_rcs_step+=f*factor*h;actual_levels.append(f/e['max_N']*factor)
                    else:scalar_torch_step+=f*factor*h
                for tank,dot in mdots.items():
                    dot*=factors[tank];mdots[tank]=dot
                    used=dot*h;state['tanks'][tank]=max(0.,state['tanks'][tank]-used)
                    state['fuel_used_kg'][tank]=state['fuel_used_kg'].get(tank,0.)+used
                    phasefuel+=used
                if enabled_rcs:
                    desired=np.r_[force_request if kind=='rcs_translate' else np.zeros(3),wanted]
                    realized=Aactual@np.array(actual_levels) if engines else np.zeros(6)
                    peak_force_residual=max(peak_force_residual,float(np.linalg.norm(realized[:3]-desired[:3])))
                    peak_wrench_residual=max(peak_wrench_residual,float(np.linalg.norm(realized[3:]-desired[3:])))
                peak_phase_rate=max(peak_phase_rate,math.degrees(float(np.linalg.norm(state['y'][4:7]))))
                state['rcs_impulse_Ns']+=scalar_rcs_step
                state['torch_impulse_Ns']+=scalar_torch_step
                if engines or extra['torch']:
                    rcs_trace.append({'t_s':state['t'],'q':y[:4].tolist(),
                                      'step_s':h,'mass_kg':mass,'cg_m':cg.tolist(),
                                      'engine_samples':engine_samples,
                                      'omega_rad_s':y[4:7].tolist(),
                                      'thrust_levels':actual_levels,
                                      'directions':[state['gdir'][e['id']].tolist() for e in engines],
                                      'gimbal_angles_deg':{k:np.degrees(v).tolist() for k,v in state['gangle'].items()},
                                      'force_body_N':F.tolist(),'torque_body_Nm':torque.tolist(),
                                      'engine_ids':[e['id'] for e in engines]})
                maxforce=max(maxforce,float(np.linalg.norm(F)))
                other_torque=np.delete(torque,axis) if isinstance(axis,(int,np.integer)) else torque-np.dot(torque,axis)*axis
                maxother=max(maxother,float(np.linalg.norm(other_torque)))
                midmass=mass-.5*sum(mdots.values())*h
                gravity=float(experiment.get('gravity_mu_m3_s2',0))
                state['y']=integrate(y,F,torque,midmass,I,h,gravity)
                state['t']+=h
                peak_phase_rate=max(peak_phase_rate,math.degrees(float(np.linalg.norm(state['y'][4:7]))))
                if kind=='rcs_turn':
                    elapsed=t+h
                    err_now=math.degrees(np.linalg.norm(qerror(state['y'][:4],target)))
                    rate_now=math.degrees(np.linalg.norm(state['y'][4:7]))
                    if at_target is None and elapsed>=T-1e-9:
                        at_target={'t_s':elapsed,'attitude_error_deg':err_now,
                                   'rate_deg_s':rate_now}
                    if elapsed>=T-1e-9:
                        if (err_now<=float(phase.get('gate_attitude_deg',.25)) and
                            rate_now<=float(phase.get('gate_rate_deg_s',.05))):
                            gate_hold+=h
                            if gate_entry is None:gate_entry=elapsed
                        else:
                            gate_entry=None;gate_hold=0.
            if state['t']+1e-8>=nextsample:
                mnow,cnow,inow=mass_properties(ship,state['tanks'])
                hist.append({'time_s':round(state['t'],7),'phase':kind,'position_m':None if state['metric_unresolved'] else state['y'][7:10].tolist(),
                             'velocity_m_s':None if state['metric_unresolved'] else state['y'][10:13].tolist(),
                           'q_body_to_inertial':None if state['metric_unresolved'] else state['y'][:4].tolist(),
                             'omega_rad_s':None if state['metric_unresolved'] else state['y'][4:7].tolist(),
                             'mass_kg':None if state['metric_unresolved'] else mnow,'cg_m':None if state['metric_unresolved'] else cnow.tolist(),
                             'propellant_kg':None if state['metric_unresolved'] else dict(state['tanks']),
                             'inertia_kg_m2':None if state['metric_unresolved'] else inow.tolist(),
                             'gimbal_angles_deg':{k:np.degrees(v).tolist() for k,v in state['gangle'].items()},
                             'force_body_N':None if kind=='metric' else F.tolist(),
                             'torque_body_Nm':None if kind=='metric' else torque.tolist(),'metric_path_m':state['metric_path_m']})
                nextsample+=sample_s
        mass,cg,I=mass_properties(ship,state['tanks'])
        result={'actuators_start':actuators_start,
                'actuators_end':{'rcs_cmd':dict(state['cmd']),'rcs_act':dict(state['act']),
                                 'torch_cmd':dict(state['torch_cmd']),'torch_act':dict(state['torch_act']),
                                 'gimbal_angles_deg':{k:np.degrees(v).tolist() for k,v in state['gangle'].items()}},
                't_start_s':t0,'mass_start_kg':None if start_unresolved else mass_start,'tanks_start_kg':None if start_unresolved else tanks_start,
                'state_start':None if start_unresolved else ystart.tolist(),'state_end':None if unresolved else state['y'].tolist(),
                'metric_law':ship['metric'][phase['model']]['law'] if kind=='metric' else None,
                'kind':kind,'duration_s':T,'t_end_s':state['t'],'mass_end_kg':None if unresolved else mass,
                'cg_end_m':None if unresolved else cg.tolist(),'inertia_end_kg_m2':None if unresolved else I.tolist(),
                'propellant_used_kg':None if unresolved or phase_prop_unresolved else phasefuel,
                'known_propellant_used_kg':phasefuel,
                'rcs_propellant_unresolved':phase_rcs_unresolved,'propellant_unresolved':phase_prop_unresolved,
                'peak_force_N':maxforce,'peak_offaxis_torque_Nm':maxother,
                'minimum_allocated_fraction':minfraction,'max_ideal_tvc_trim_deg':maxtrim,
                'peak_angular_rate_deg_s':peak_phase_rate,
                'phase_attitude_drift_deg':math.degrees(np.linalg.norm(qerror(qstart,state['y'][:4]))),
                'peak_gimbal_rate_deg_s':peak_gimbal_rate,'peak_gimbal_angle_deg':peak_gimbal_angle,
                'gimbal_limit_steps':gimbal_limits,'slew_limit_steps':slew_limits,
                'throttle_clamp_steps':throttle_limits,'thrust_limit_steps':thrust_limits,
                'allocation_limit_steps':allocation_limits,'peak_command_slew_fullscale_s':peak_cmd_slew,
                'peak_throttle':peak_throttle,'peak_force_residual_N':peak_force_residual,
                'peak_torque_residual_Nm':peak_wrench_residual,
                'propellant_depletion_steps':state['depletion_steps']-depletion_start,
                'propellant_available':None if phase_prop_unresolved or unresolved else int(state['depletion_steps']==depletion_start),
                'residual_velocity_m_s':float(np.linalg.norm(state['y'][10:13]-ystart[10:13])),
                'residual_displacement_m':float(np.linalg.norm(state['y'][7:10]-ystart[7:10]-ystart[10:13]*(state['t']-t0))),
                'metric_unresolved':unresolved}
        if canonical is not None:
            result['canonical_operation']=canonical
            result['known_propellant_used_kg']=None
        if kind=='torch':
            metrics['torch_attitude_drift_deg']=result['phase_attitude_drift_deg']
            metrics['torch_final_angular_rate_deg_s']=math.degrees(np.linalg.norm(state['y'][4:7]))
            metrics['torch_peak_angular_rate_deg_s']=peak_phase_rate
        if kind=='rcs_translate':
            result['translation_delta_v_achieved_m_s']=(state['y'][10:13]-velstart).tolist()
            result['translation_velocity_error_m_s']=float(np.linalg.norm(state['y'][10:13]-velstart-dvtarget))
            result['attitude_hold_error_deg']=math.degrees(np.linalg.norm(qerror(qstart,state['y'][:4])))
            metrics['translation_velocity_error_m_s']=result['translation_velocity_error_m_s']
            metrics['attitude_hold_error_deg']=result['attitude_hold_error_deg']
        if kind=='rcs_turn':
            result['at_target_time']=at_target
            result['attitude_error_deg']=at_target['attitude_error_deg']
            result['rate_deg_s']=at_target['rate_deg_s']
            result['gate_entry_s']=None if gate_entry is None else t0+gate_entry
            result['gate_hold_s']=gate_hold
            result['sustained_gate_duration_s']=0. if gate_entry is None else max(0.,state['t']-t0-gate_entry)
            result['post_hold_s']=post_hold
            result['at_end']={'attitude_error_deg':math.degrees(np.linalg.norm(qerror(state['y'][:4],target))),
                              'rate_deg_s':math.degrees(np.linalg.norm(state['y'][4:7]))}
            metrics['attitude_error_deg']=result['attitude_error_deg']
            metrics['rate_deg_s']=result['rate_deg_s']
            metrics['gate_entry_s']=result['gate_entry_s']
        if unresolved:
            for key in ('actuators_end','phase_attitude_drift_deg','peak_angular_rate_deg_s',
                        'residual_velocity_m_s','residual_displacement_m','peak_force_N',
                        'peak_offaxis_torque_Nm','minimum_allocated_fraction','max_ideal_tvc_trim_deg',
                        'peak_gimbal_rate_deg_s','peak_gimbal_angle_deg','gimbal_limit_steps',
                        'slew_limit_steps','throttle_clamp_steps','thrust_limit_steps',
                        'allocation_limit_steps','peak_command_slew_fullscale_s','peak_throttle',
                        'peak_force_residual_N','peak_torque_residual_Nm','propellant_depletion_steps'):
                result[key]=None
        result['qualification']=evaluate(phase.get('checks',{}),result,unresolved)
        for key in ('peak_gimbal_rate_deg_s','peak_gimbal_angle_deg','gimbal_limit_steps','slew_limit_steps',
                    'throttle_clamp_steps','thrust_limit_steps','allocation_limit_steps','peak_command_slew_fullscale_s','peak_throttle','peak_force_residual_N',
                    'peak_torque_residual_Nm','propellant_depletion_steps','peak_angular_rate_deg_s'):
            metrics[key]=max(metrics.get(key,0.),result[key] or 0.)
        metrics['propellant_available']=None if state['propellant_unresolved'] or unresolved else int(state['depletion_steps']==0)
        metrics['residual_velocity_m_s']=result['residual_velocity_m_s']
        metrics['residual_displacement_m']=result['residual_displacement_m']
        if kind=='rcs_turn':
            metrics['gate_hold_s']=gate_hold
            metrics['sustained_gate_duration_s']=result['sustained_gate_duration_s']
        phases.append(result)
    mass,cg,I=mass_properties(ship,state['tanks'])
    known_propellant_used=sum(state['fuel_used_kg'].values())
    metrics.update(mass_end_kg=None if state['metric_unresolved'] else mass,
                   known_propellant_used_kg=known_propellant_used,
                   total_propellant_used_kg=None if state['propellant_unresolved'] or state['metric_unresolved'] else known_propellant_used,
                   metric_path_m=state['metric_path_m'],final_speed_m_s=None if state['metric_unresolved'] else float(np.linalg.norm(state['y'][10:13])),
                   final_angular_rate_deg_s=None if state['metric_unresolved'] else math.degrees(np.linalg.norm(state['y'][4:7])))
    if state['metric_unresolved']:
        for key in list(metrics):
            if key.startswith('peak_') or key.endswith('_steps'):
                metrics[key]=None
    qualification=evaluate(experiment.get('checks',{}),metrics,state['metric_unresolved'])
    statuses=[qualification['status']]+[p['qualification']['status'] for p in phases]
    qualification['status']='fail' if 'fail' in statuses else ('indeterminate' if 'indeterminate' in statuses else 'pass')
    qualification['scope']='Only the configured numerical criteria; no hardware certification'
    qualification['conditional_on_unknown_propellant']=state['propellant_unresolved']
    physical=evaluate({'propellant_available':{'min':1}},metrics,state['metric_unresolved'])
    physical['scope']='Declared propellant availability only; excludes hardware feasibility'
    system_status='fail' if 'fail' in (qualification['status'],physical['status']) else ('indeterminate' if 'indeterminate' in (qualification['status'],physical['status']) else 'pass')
    return {'ship':ship['name'],'experiment':experiment.get('name','unnamed'),
            'ship_sha256':source_hash(ship),'experiment_sha256':source_hash(experiment),
            'dt_s':dt,'phases':phases,'metrics':metrics,'qualification':qualification,
            'physical_qualification':physical,'system_status':system_status,
            'mass_accounting':('canonical terminal mass/remass UNKNOWN; pre-metric inventory preserved' if state['metric_unresolved'] else
                               ('frozen for unspecified consumption; known tanks deplete' if state['propellant_unresolved'] else 'declared tank depletion and installed masses')),
            'gimbal_initialization':{e['id']:e['gimbal'].get('initialization_note','declared angles; no reset between phases')
                                     for e in ship.get('rcs',[]) if 'gimbal' in e},
            'final_state':{'time_s':state['t'],'position_m':None if state['metric_unresolved'] else state['y'][7:10].tolist(),
                           'velocity_m_s':None if state['metric_unresolved'] else state['y'][10:13].tolist(),
                           'q_body_to_inertial':None if state['metric_unresolved'] else state['y'][:4].tolist(),
                           'omega_rad_s':None if state['metric_unresolved'] else state['y'][4:7].tolist(),
                           'mass_kg':None if state['metric_unresolved'] else mass,
                           'cg_m':None if state['metric_unresolved'] else cg.tolist(),
                           'inertia_kg_m2':None if state['metric_unresolved'] else I.tolist(),
                           'tanks_kg':None if state['metric_unresolved'] else state['tanks'],
                           'metric_path_m':state['metric_path_m'],'metric_unresolved':state['metric_unresolved'],
                           **({'remass_kg':None,'matching_delta_v_m_s':None} if state['metric_unresolved'] else {})},
            'rcs_impulse_Ns':state['rcs_impulse_Ns'],'torch_impulse_Ns':state['torch_impulse_Ns'],
            'warnings':state['warnings'],
            'rcs_propellant_unresolved':state['rcs_propellant_unresolved'],'propellant_unresolved':state['propellant_unresolved'],
            'evidence_class':'non-governing numerical experiment; experimental metric laws not physical validation',
            'model_limits':['canonical metric requests execute transition/hold checks; U^M_gamma and finite ledgers absent',
                            'canonical metric arrival mass, position, velocity, attitude, and remass ledger unresolved',
                            'rigid body; fuel centroids and intrinsic inertia scale linearly with fill',
                            'no slosh, plume, thermal, flex, sensor, valve, or tank feed network',
                            'torch auto-trim instantaneous unless tvc_rate_deg_s declared; no structural TVC model',
                            'no full variable-inertia angular-momentum flux law',
                            'conditional metric path estimates do not establish physical arrival state'],
            'history':hist,'rcs_trace':rcs_trace}
