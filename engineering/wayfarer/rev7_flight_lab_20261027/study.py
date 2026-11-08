"""Isolated rev-7 flight experiments; no LOOM writes or certification claims.
All units SI; quaternion scalar first, active body-to-inertial rotation.
Run: .venv/bin/python study.py
"""
import json, sys, math, hashlib, csv
from pathlib import Path
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'source'; REV=SRC/'design/wayfarer/v0.5.7'; OUT=ROOT/'results'
sys.path[:0]=[str(SRC),str(REV),str(REV/'g10')]
import g10_flight_dynamics as G
OUT.mkdir(exist_ok=True)

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')

def model(state='S1',coarse=25e3,failed=None):
    st=G.CARD['states'][state]
    th=[t for t in G.TH if t['cluster']!=failed]
    pos=np.array([t['pos'] for t in th]); dirs=np.array([t['f'] for t in th])/25000
    caps=np.array([25000 if t['kind']=='axial' else coarse for t in th])
    r=pos-np.array(st['cg_m'])
    A=np.vstack((dirs.T,np.cross(r,dirs).T))*caps
    return st,th,pos,dirs,caps,A

def authority(state,coarse,axis,failed=None):
    st,th,p,d,c,A=model(state,coarse,failed)
    # Six-dimensional wrench; hold all other torque axes and net force at zero.
    ix=axis+3; ids=[j for j in range(6) if j!=ix]
    vals=[]
    for sg in [1,-1]:
        sol=linprog(-sg*A[ix]/1e6,A_eq=A[ids]/1e6,b_eq=np.zeros(5),bounds=[(0,1)]*len(th),method='highs')
        assert sol.success,sol.message
        vals.append(sg*float(A[ix]@sol.x))
    return vals

def allocate(A,torque):
    # Maximize the realizable fraction of the exact requested wrench. A positive
    # LP witness proves feasibility; solver failure is an error, not infeasibility.
    b=np.r_[np.zeros(3),torque]
    scale=np.array([1e6]*3+[2e7]*3)
    eq=np.column_stack((A,-b))/scale[:,None]
    sol=linprog(np.r_[np.zeros(A.shape[1]),-1.],A_eq=eq,b_eq=np.zeros(6),
                bounds=[(0,1)]*(A.shape[1]+1),method='highs')
    assert sol.success,sol.message
    fraction=float(sol.x[-1])
    least=linprog(np.ones(A.shape[1]),A_eq=A/scale[:,None],b_eq=b*fraction/scale,
                  bounds=[(0,1)]*A.shape[1],method='highs')
    assert least.success,least.message
    return least.x,fraction

def qmul(q,p):
    return np.r_[q[0]*p[0]-q[1:]@p[1:],q[0]*p[1:]+p[0]*q[1:]+np.cross(q[1:],p[1:])]
def rot(q):return Rotation.from_quat(np.r_[q[1:],q[0]])
def err(q,qd):return rot(q).inv().__mul__(rot(qd)).as_rotvec()
def reference(t,T,axis):
    u=np.clip(t/T,0,1)
    theta=np.pi*(10*u**3-15*u**4+6*u**5)
    w=np.pi/T*(30*u**2-60*u**3+30*u**4)
    a=np.pi/T**2*(60*u-180*u**2+120*u**3)
    v=np.eye(3)[axis]
    return np.r_[math.cos(theta/2),v*math.sin(theta/2)],w*v,a*v

def fly(label,state='S1',coarse=300e3,axis=1,T=10,dt=.02,lag=.05,failed=None,save=False,override=None,gimballed=False):
    st,th,pos,dirs,caps,A=model(state,coarse,failed)
    mass=st['mass_t']*1000; inertia=np.array(st['inertia_tensor_kg_m2'],float)
    if override:
        mass,inertia,cg=override
        A=np.vstack((dirs.T,np.cross(pos-cg,dirs).T))*caps
    inv=np.linalg.inv(inertia)
    if gimballed:
        assert axis==1 and not override
        gc=json.loads((OUT/'gimbal_static.json').read_text())
        gtargets=[np.radians(np.array(v['gimbal_angles_deg'])) for v in gc]
        angles=gtargets[0].copy();peak_gimbal_rate=0.
        coarse_th=[dict(t,kind='gimballed_coarse') for t in G.TH if t['kind']=='inward']
        nominal=np.array([t['f'] for t in coarse_th])/25000
        tangent=np.cross(np.tile([1,0,0],(8,1)),nominal)
        th=th+coarse_th;pos=np.vstack((pos,[t['pos'] for t in coarse_th]))
        caps=np.r_[caps,np.full(8,300000.)]
        dirs=np.vstack((dirs,nominal))
        A=np.vstack((dirs.T,np.cross(pos-np.array(st['cg_m']),dirs).T))*caps
    # RCS mass/inertia are frozen because current-build RCS ve/tank model is OPEN.
    # Report impulse for conditional propellant calculation, never fake a ve.
    y=np.r_[1.,np.zeros(12)] # q4, w3, position3, velocity3
    actual=np.zeros(len(th)); impulse=0.; min_scale=1.; peak_u=0.; peak_f=0.; peak_other=0.
    rows=[]; commands=[]; atT=None; settle=None; hold=0.
    peak_accel=0.;peak_rate=0.;prev_cmd=np.zeros(len(th));peak_slew=0.
    def deriv(z,force,torque):
        q=z[:4];w=z[4:7]
        return np.r_[.5*qmul(q,np.r_[0,w]), inv@(torque-np.cross(w,inertia@w)),z[10:13],rot(q).apply(force)/mass]
    for k in range(round((T+4)/dt)+1):
        t=k*dt;qd,wd,ad=reference(t,T,axis)
        if gimballed:
            target_angles=gtargets[0 if t<T/2 else 1]
            change=np.clip((target_angles-angles)*(1-math.exp(-dt/.1)),-math.radians(30)*dt,math.radians(30)*dt)
            angles+=change;peak_gimbal_rate=max(peak_gimbal_rate,float(np.max(abs(change)))/dt*180/np.pi)
            ga,gb=angles.T
            dirs[-8:]=np.cos(gb)[:,None]*np.cos(ga)[:,None]*nominal+np.cos(gb)[:,None]*np.sin(ga)[:,None]*tangent+np.sin(gb)[:,None]*np.tile([1,0,0],(8,1))
            A=np.vstack((dirs.T,np.cross(pos-np.array(st['cg_m']),dirs).T))*caps
        error=np.linalg.norm(err(y[:4],qd))*180/np.pi
        target=reference(T,T,axis)[0]
        finalerr=np.linalg.norm(err(y[:4],target))*180/np.pi
        rate=np.linalg.norm(y[4:7])*180/np.pi
        if abs(t-T)<dt/4:atT={'attitude_error_deg':finalerr,'rate_deg_s':rate}
        if t>=T and finalerr<=.25 and rate<=.05:
            hold+=dt
            if settle is None:settle=t
        else:hold=0.;settle=None
        rows.append([t,*y,finalerr,rate])
        if k==round((T+4)/dt):break
        # Reference feed-forward and full-tensor PD tracker; perfect state estimate.
        # Gains declared experimental: wn=3 rad/s, damping=1.
        alpha=ad+9*err(y[:4],qd)+6*(wd-y[4:7])
        torque=inertia@alpha+np.cross(y[4:7],inertia@y[4:7])
        u,s=allocate(A,torque);min_scale=min(min_scale,s)
        # Command slew 10 full-scale/s; first-order rise/fall lag. ZOH command.
        delta=u-prev_cmd
        fraction=min(1.,10*dt/max(float(np.max(abs(delta))),1e-30))
        cmd=prev_cmd+fraction*delta
        peak_slew=max(peak_slew,float(np.max(abs(cmd-prev_cmd))/dt));prev_cmd=cmd
        # Average thrust over step for exact integration of the actuator ODE.
        if lag:
            e=math.exp(-dt/lag); avg=cmd+(actual-cmd)*lag/dt*(1-e);actual=cmd+(actual-cmd)*e
        else:avg=cmd;actual=cmd
        force=A[:3]@avg; applied=A[3:]@avg
        peak_u=max(peak_u,float(np.max(avg)));peak_f=max(peak_f,float(np.linalg.norm(force)))
        peak_other=max(peak_other,float(np.linalg.norm(np.delete(applied,axis))))
        peak_accel=max(peak_accel,float(np.linalg.norm(inv@(applied-np.cross(y[4:7],inertia@y[4:7])))))
        peak_rate=max(peak_rate,rate)
        impulse+=float(caps@avg)*dt
        commands.append([t,*avg])
        k1=deriv(y,force,applied); k2=deriv(y+.5*dt*k1,force,applied)
        k3=deriv(y+.5*dt*k2,force,applied); k4=deriv(y+dt*k3,force,applied)
        y+=dt/6*(k1+2*k2+2*k3+k4);y[:4]/=np.linalg.norm(y[:4])
    result={'label':label,'state':state,'axis':axis,'coarse_N':coarse,'failed_cluster':failed,
            'duration_s':T,'dt_s':dt,'actuator_tau_s':lag,'command_slew_fullscale_s':10,'slew_policy':'common interpolation fraction preserves force balance for fixed directions; changing gimbals need separate residual check',
            'at_target_time':atT,'at_end':{'attitude_error_deg':finalerr,'rate_deg_s':rate},
            'gate_entry_s':settle,'gate_hold_s':hold,'minimum_allocated_fraction':min_scale,
            'peak_actual_fraction':peak_u,'peak_net_force_N':peak_f,'peak_offaxis_torque_Nm':peak_other,
            'peak_angular_accel_rad_s2':peak_accel,'peak_rate_deg_s':peak_rate,
            'total_scalar_impulse_Ns':impulse,'residual_velocity_m_s':y[10:13].tolist(),
            'displacement_m':y[7:10].tolist(),'pass_at_target':atT['attitude_error_deg']<=.25 and atT['rate_deg_s']<=.05,
            'mass_model':'frozen rev7 mass/inertia; propellant not qualified; Isp/tank distribution missing'}
    if gimballed:
        result.update(architecture='8 inward 300 kN two-axis gimbals PLUS all original 32 fixed 25 kN nozzles',peak_gimbal_rate_deg_s=peak_gimbal_rate,gimbal_lag_s=.1,gimbal_limit_deg=25,initial_gimbals='prepositioned; time excluded',extra_hardware_mass='not allocated, conditional trade only')
    if save:
        np.savetxt(OUT/(label+'_state.csv'),rows,delimiter=',',header='t,qw,qx,qy,qz,wx,wy,wz,x,y,z,vx,vy,vz,error_deg,rate_deg_s',comments='')
        np.savetxt(OUT/(label+'_thrust.csv'),commands,delimiter=',',header='t,'+','.join(t['cluster']+':'+t['kind'] for t in th),comments='')
        dump(label+'_mounts.json',[dict(t,max_force_N=float(c)) for t,c in zip(th,caps)])
    print(label,json.dumps(result,default=lambda x:x.item()),flush=True)
    return result

def gimbal_screen():
    # Eight coarse engines, each neutral direction inward at existing cluster.
    # Local direction = cos(b)cos(a)*inward + cos(b)sin(a)*tangent + sin(b)*axial.
    # Mechanical angles a,b individually bounded +/-25 degrees, throttle 0..1.
    th=[t for t in G.TH if t['kind']=='inward'];pos=np.array([t['pos'] for t in th]);r=pos-np.array(G.CARD['states']['S1']['cg_m'])
    inward=np.array([t['f'] for t in th])/25000
    axial=np.tile([1,0,0],(8,1));tangent=np.cross(axial,inward)
    fmax=300e3
    def force(z):
        z=z.reshape(8,3);u,a,b=z.T
        return fmax*u[:,None]*(np.cos(b)[:,None]*np.cos(a)[:,None]*inward+np.cos(b)[:,None]*np.sin(a)[:,None]*tangent+np.sin(b)[:,None]*axial)
    def wrench(z):
        f=force(z);return np.r_[f.sum(0),np.cross(r,f).sum(0)]
    out=[]
    for sg in [1,-1]:
        sols=[]
        for seed in range(4):
            rng=np.random.default_rng(seed);z=np.zeros((8,3));z[:,0]=.5;z[:,1:]=rng.uniform(-.2,.2,(8,2))
            res=minimize(lambda z:-sg*wrench(z)[4]/1e7,z.ravel(),method='SLSQP',
                bounds=[v for _ in range(8) for v in [(0,1),(-math.radians(25),math.radians(25)),(-math.radians(25),math.radians(25))]],
                constraints={'type':'eq','fun':lambda z:wrench(z)[[0,1,2,3,5]]/1e6},options={'ftol':1e-11,'maxiter':700})
            w=wrench(res.x);resid=np.linalg.norm(w[[0,1,2,3,5]])
            if resid<1e-2:sols.append((sg*w[4],res,resid))
        if not sols:out.append({'sign':sg,'status':'no feasible numerical witness; NOT physical infeasibility'});continue
        tq,res,resid=max(sols,key=lambda x:x[0]);z=res.x.reshape(8,3)
        out.append({'sign':sg,'pitch_torque_Nm':tq,'optimizer_success':bool(res.success),'residual_N_or_Nm':resid,
                    'throttle':z[:,0].tolist(),'gimbal_angles_deg':np.degrees(z[:,1:]).tolist(),'forces_N':force(res.x).tolist(),
                    'status':'feasible static witness; no global optimality or dynamic qualification'})
    return out

def torch(m0=None,tag="torch"):
    m0=G.CARD['states']['S1']['mass_t']*1000 if m0 is None else m0;F,ve=G.torch_force('CRUISE',m0);mdot=F/ve;T=600.
    def rhs(t,y):return [y[1],F/y[2],-mdot]
    sol=solve_ivp(rhs,[0,T],[0,0,m0],method='DOP853',rtol=1e-12,atol=1e-10,dense_output=True)
    mf=m0-mdot*T;dv=ve*math.log(m0/mf);x=ve*(T-mf/mdot*math.log(m0/mf))
    # Independent Sun point-mass finite-burn trajectory: start circular at 1 AU,
    # inertial +Y thrust. Separate conventional trajectory from free-space delta-v.
    mu=1.32712440018e20;AU=149597870700.
    y0=np.array([AU,0,0,0,math.sqrt(mu/AU),0,m0])
    def gravrhs(t,y):return np.r_[y[3:6],-mu*y[:3]/np.linalg.norm(y[:3])**3+np.array([0,F/y[6],0]),-mdot]
    gs=solve_ivp(gravrhs,[0,T],y0,method='DOP853',rtol=1e-12,atol=1e-9)
    # One compact fixed-step RK4 implementation, independent of DOP853.
    errors={}
    for h in [10.,5.,1.]:
        y=y0.copy()
        for k in range(round(T/h)):
            a=gravrhs(k*h,y);b=gravrhs(k*h+h/2,y+h*a/2);c=gravrhs(k*h+h/2,y+h*b/2);d=gravrhs(k*h+h,y+h*c)
            y+=h*(a+2*b+2*c+d)/6
        errors[str(h)]={'position_error_m':float(np.linalg.norm(y[:3]-gs.y[:3,-1])), 'velocity_error_m_s':float(np.linalg.norm(y[3:6]-gs.y[3:6,-1])), 'mass_error_kg':float(y[6]-gs.y[6,-1])}
    result={'mode':'CRUISE','T_s':T,'F_N':F,'ve_m_s':ve,'mdot_kg_s':mdot,'initial_mass_kg':m0,'final_mass_kg':mf,
            'propellant_used_kg':m0-mf,'acceleration_initial_m_s2':F/m0,'acceleration_final_m_s2':F/mf,
            'analytic_dv_m_s':dv,'numeric_dv_m_s':sol.y[1,-1],'analytic_position_m':x,'numeric_position_m':sol.y[0,-1],
            'jet_power_W':F*ve/2,'heliocentric_initial_SI':y0.tolist(),'heliocentric_final_SI':gs.y[:,-1].tolist(),
            'sun_mu_m3_s2':mu,'rk4_vs_dop853':errors}
    dump(tag+'.json',result)
    np.savetxt(OUT/(tag+'_free.csv'),np.column_stack((np.arange(601),sol.sol(np.arange(601)).T)),delimiter=',',header='t,x,v,m',comments='')
    return result

def metric():
    card=G.METRIC.build_metric_closure();out=[]
    for name,mode in card['modes'].items():
        v=float(mode['beta'])*299792458.;T=float(mode['ramp_s']);plateau=60.
        # Canon explicitly supplies linear CLEAN metric path ramp approximation.
        distance=v*(T+plateau)
        out.append({'mode':name,'ramp_s':T,'plateau_s':plateau,'collapse_s':T,
                    'one_ramp_km':v*T/2/1000,'coordinate_path_km':distance/1000,
                    'ordinary_arrival_velocity':None,'ordinary_delta_v':None,'remass':None,
                    'cold_load_W':float(mode['cold_load_w']),
                    'scope':'kinematic metric path envelope only; symmetric collapse is an experiment assumption; U^M_gamma absent'})
    seq=['COAST','METRIC_PREP','METRIC_RAMP','METRIC_TRANSPORT','METRIC_COLLAPSE','NRE_RELAXATION','COAST','TORCH','COAST']
    return {'modes':out,'nominal_sequence':G.run_sequence(seq),'illegal_direct_torch':G.run_sequence(['TORCH','METRIC_RAMP']),
            'zero_duration_relaxation_also_accepted':G.run_sequence(['METRIC_COLLAPSE','NRE_RELAXATION','LOOM_FORMATION']),
            'limitation':'sequence checker has no time, load, state, or conservation-ledger integration'}

def main():
    auth=[]
    for s in ['S1','S2','S7']:
        for F in [25000,150000,200000,300000]:
            for ax in [0,1,2]:
                vals=authority(s,F,ax)
                I=G.CARD['states'][s]['inertia_tensor_kg_m2'][ax][ax]
                auth.append({'state':s,'coarse_N':F,'axis':ax,'signed_authority_Nm':vals,
                    'ideal_single_axis_rest_to_rest_s':math.sqrt(2*np.pi*I*(1/vals[0]+1/vals[1])),
                    'ideal_10s_equal_torque_Nm':4*np.pi*I/100})
    dump('authority.json',auth);dump('gimbal_static.json',gimbal_screen())
    runs=[]
    for label,kw in [
        ('baseline25_10s',dict(coarse=25000,T=10)),
        ('baseline25_40s',dict(coarse=25000,T=40,save=True)),
        ('fixed200_10s',dict(coarse=200000)),
        ('fixed300_pitch',dict(save=True)),
        ('fixed300_yaw',dict(axis=2)),
        ('fixed300_loaded',dict(state='S2')),
        ('fixed300_clusterout',dict(failed='F+Z')),
        ('fixed300_slowactuator',dict(lag=.2)),
        ('fixed300_halfstep',dict(dt=.01))]:
        runs.append(fly(label,**kw));dump('rcs_runs.json',runs)
    tr=torch();dump('metric.json',metric())
    # Combined: same free-space state, 600 s torch, shutdown, stipulated 60 s
    # thermal/retraction coast, 40 s original RCS turn. RCS mass frozen as above.
    # Use mass-weighted first moments from S1/S4 as an explicit two-endpoint model;
    # it is not an actual tank drain law (S3 disagrees with linear depletion).
    s1=G.CARD['states']['S1'];s4=G.CARD['states']['S4'];f=tr['propellant_used_kg']/250000
    m=tr['final_mass_kg'];cg=((1-f)*s1['mass_t']*1000*np.array(s1['cg_m'])+f*s4['mass_t']*1000*np.array(s4['cg_m']))/m
    # Interpolate inertia about fixed datum, then shift to current CG.
    def shift(v):return (v@v)*np.eye(3)-np.outer(v,v)
    o1=np.array(s1['inertia_tensor_kg_m2'])+s1['mass_t']*1000*shift(np.array(s1['cg_m']))
    o4=np.array(s4['inertia_tensor_kg_m2'])+s4['mass_t']*1000*shift(np.array(s4['cg_m']))
    inertia=(1-f)*o1+f*o4-m*shift(cg)
    turn=fly('combined_baseline_turn',coarse=25000,T=40,override=(m,inertia,cg),save=True)
    coast=60.;total_after=coast+44
    dump('combined.json',{'torch':tr,'coast_before_turn_s':coast,'turn':turn,'cg_at_turn_m':cg.tolist(),
        'mass_kg_at_turn':m,'position_end_m':[tr['numeric_position_m']+tr['numeric_dv_m_s']*total_after-turn['displacement_m'][0],turn['displacement_m'][1],-turn['displacement_m'][2]],
        'velocity_end_m_s':(np.array([tr['numeric_dv_m_s'],0,0])+np.array(turn['residual_velocity_m_s'])*[-1,1,-1]).tolist(),
        'boundary_position_velocity_mass_jumps':[0,0,0],
        'initial_body_to_inertial_q':[0,0,1,0],'torch_force_body_axis':'minus x','RCS_attitude_history':'relative to initial attitude; final thrust direction reverses',
        'limitations':['folding and cooling time assumed 60 s, not derived','folding at zero angular momentum; no deployment dynamics','mass/inertia two-endpoint approximation, not tank-drain qualification','RCS propellant omitted: current-build Isp absent','torch ideal TVC, perfect state estimate, gravity omitted in combined case']})

if __name__=='__main__':main()
