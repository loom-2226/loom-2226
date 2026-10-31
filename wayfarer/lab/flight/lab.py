"""Scratch-only LOOM spacecraft flight lab runner."""
import argparse,csv,json
from pathlib import Path
from flightlab import run
from cards import resolve
ROOT=Path(__file__).resolve().parent
def load(path):return json.loads(Path(path).read_text())
def save_run(shipfile,expfile,dest,dt,sample_s):
    ship,cards_used=resolve(load(shipfile));exp=load(expfile)
    result=run(ship,exp,dt=dt,sample_s=sample_s)
    result['cards']=cards_used
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    tag=Path(shipfile).stem+'__'+Path(expfile).stem
    hist=result.pop('history')
    trace=result.pop('rcs_trace')
    (dest/(tag+'.telemetry.json')).write_text(json.dumps(hist,allow_nan=False)+'\n')
    if trace:
        (dest/(tag+'.rcs_trace.json')).write_text(json.dumps(trace,allow_nan=False)+'\n')
    (dest/(tag+'.json')).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (dest/(tag+'.csv')).open('w',newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['t_s','phase','x_m','y_m','z_m','vx_m_s','vy_m_s','vz_m_s',
                         'qw','qx','qy','qz','wx_rad_s','wy_rad_s','wz_rad_s','mass_kg',
                         'cg_x_m','cg_y_m','cg_z_m','metric_path_m','tanks_kg_json','gimbal_angles_deg_json',
                         'Fx_body_N','Fy_body_N','Fz_body_N','Tx_body_Nm','Ty_body_Nm','Tz_body_Nm'])
        for h in hist:
            writer.writerow([h['time_s'],h['phase'],*(h['position_m'] or [None]*3),*(h['velocity_m_s'] or [None]*3),
                             *(h['q_body_to_inertial'] or [None]*4),*(h['omega_rad_s'] or [None]*3),
                             h['mass_kg'],*(h['cg_m'] or [None]*3),h['metric_path_m'],
                             json.dumps(h['propellant_kg']),json.dumps(h['gimbal_angles_deg']),
                             *(h['force_body_N'] or [None]*3),*(h['torque_body_Nm'] or [None]*3)])
    print(tag,'status=',result['qualification']['status'],
          'system=',result['system_status'],
          'mass=',round(result['final_state']['mass_kg'],3) if result['final_state']['mass_kg'] is not None else 'unresolved',
          'used_kg=',('unresolved' if result['metrics']['total_propellant_used_kg'] is None else round(result['metrics']['total_propellant_used_kg'],5)),
          'rcs_error=',result['metrics'].get('attitude_error_deg'),
          'warnings=',result['warnings'],flush=True)
    return result

def main():
    p=argparse.ArgumentParser(description='Scratch experimental spacecraft laboratory')
    sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('run');r.add_argument('ship');r.add_argument('experiment')
    r.add_argument('--dt',type=float,default=.1);r.add_argument('--sample',type=float,default=1.)
    r.add_argument('--out',default='lab_results')
    d=sub.add_parser('demo');d.add_argument('--dt',type=float,default=.1)
    d.add_argument('--manifest',default='demo_manifest.json');d.add_argument('--sample',type=float,default=1.);d.add_argument('--out',default='lab_results')
    args=p.parse_args()
    if args.cmd=='run':
        save_run(args.ship,args.experiment,args.out,args.dt,args.sample)
    else:
        out=ROOT/args.out
        summary=[]
        for ship,exp in load(ROOT/args.manifest):
            result=save_run(ROOT/'configs'/(ship+'.json'),ROOT/'experiments'/(exp+'.json'),out,args.dt,args.sample)
            summary.append({'ship_config':ship,'experiment':exp,
                            'status':result['qualification']['status'],'system_status':result['system_status'],
                            'metrics':result['metrics'],'warnings':result['warnings'],
                            'ship_sha256':result['ship_sha256'],
                            'experiment_sha256':result['experiment_sha256']})
        (out/'comparison.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
        keys=['attitude_error_deg','rate_deg_s','gate_entry_s','gate_hold_s','residual_velocity_m_s',
              'peak_gimbal_rate_deg_s','peak_force_residual_N','known_propellant_used_kg','total_propellant_used_kg']
        with (out/'comparison.csv').open('w',newline='') as file:
            writer=csv.writer(file);writer.writerow(['ship','experiment','status','system_status']+keys)
            for row in summary:writer.writerow([row['ship_config'],row['experiment'],row['status'],row['system_status']]+[row['metrics'].get(k) for k in keys])
        print('DEMO FINISHED',len(summary),'runs',out/'comparison.json',flush=True)
if __name__=='__main__':main()
