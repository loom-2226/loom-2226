"""Run the rev7 600 s CRUISE point-Sun benchmark in official GMAT R2026a.
ChemicalThruster is only a constant-thrust/Isp interface surrogate, not torch hardware.
"""
import json,subprocess,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;B=R/'GMAT/R2026a/bin';out=R/'results'
t=json.loads((out/'torch.json').read_text());y=t['heliocentric_initial_SI']
script=f'''% Non-governing rev7 established-physics finite-burn benchmark.
Create CoordinateSystem SunJ2000;
SunJ2000.Origin = Sun;
SunJ2000.Axes = MJ2000Eq;
Create ChemicalTank Water;
Water.FuelMass = 250000;
Water.Volume = 300;
Water.FuelDensity = 1000;
Water.PressureModel = PressureRegulated;
Create ChemicalThruster Torch;
Torch.CoordinateSystem = SunJ2000;
Torch.ThrustDirection1 = 0;
Torch.ThrustDirection2 = 1;
Torch.ThrustDirection3 = 0;
Torch.DecrementMass = true;
Torch.Tank = {{Water}};
Torch.GravitationalAccel = 9.80665;
Torch.C1 = {t['F_N']:.16g};
Torch.K1 = {t['ve_m_s']/9.80665:.16g};
Create Spacecraft Wayfarer;
Wayfarer.DateFormat = TAIModJulian;
Wayfarer.Epoch = '21545';
Wayfarer.CoordinateSystem = SunJ2000;
Wayfarer.DisplayStateType = Cartesian;
Wayfarer.X = {y[0]/1000:.16g};
Wayfarer.Y = 0;
Wayfarer.Z = 0;
Wayfarer.VX = 0;
Wayfarer.VY = {y[4]/1000:.16g};
Wayfarer.VZ = 0;
Wayfarer.DryMass = {y[6]-250000:.16g};
Wayfarer.Tanks = {{Water}};
Wayfarer.Thrusters = {{Torch}};
Create ForceModel SolarForce;
SolarForce.CentralBody = Sun;
SolarForce.PrimaryBodies = {{}};
SolarForce.PointMasses = {{Sun}};
SolarForce.Drag = None;
SolarForce.SRP = Off;
SolarForce.RelativisticCorrection = Off;
Create Propagator Prop;
Prop.FM = SolarForce;
Prop.Type = RungeKutta89;
Prop.InitialStepSize = 1;
Prop.Accuracy = 1e-12;
Prop.MinStep = 0.00001;
Prop.MaxStep = 10;
Prop.StopIfAccuracyIsViolated = true;
Create FiniteBurn Burn;
Burn.Thrusters = {{Torch}};
Create ReportFile Results;
Results.Filename = '{out/'gmat_trajectory.txt'}';
Results.Precision = 16;
Results.ColumnWidth = 25;
Results.WriteHeaders = true;
Results.Add = {{Wayfarer.ElapsedSecs,Wayfarer.SunJ2000.X,Wayfarer.SunJ2000.Y,Wayfarer.SunJ2000.Z,Wayfarer.SunJ2000.VX,Wayfarer.SunJ2000.VY,Wayfarer.SunJ2000.VZ,Wayfarer.TotalMass}};
BeginMissionSequence;
BeginFiniteBurn Burn(Wayfarer);
Propagate Prop(Wayfarer) {{Wayfarer.ElapsedSecs = 600}};
EndFiniteBurn Burn(Wayfarer);
Report Results Wayfarer.ElapsedSecs Wayfarer.SunJ2000.X Wayfarer.SunJ2000.Y Wayfarer.SunJ2000.Z Wayfarer.SunJ2000.VX Wayfarer.SunJ2000.VY Wayfarer.SunJ2000.VZ Wayfarer.TotalMass;
'''
(R/'wayfarer_torch.script').write_text(script)
startup=(B/'gmat_startup_file.txt').read_text()
startup='\n'.join('# study disables unused optional plugin: '+l if l.startswith('PLUGIN') and any(x in l for x in ['MatlabInterface','OpenFramesInterface','OVtoOFI']) else l for l in startup.splitlines())+'\n'
(B/'study_startup.txt').write_text(startup)
with (out/'gmat_run.log').open('w') as f:
    ret=subprocess.run(['./GmatConsole-R2026a','--startup_file','study_startup.txt','--run',str(R/'wayfarer_torch.script')],cwd=B,stdout=f,stderr=subprocess.STDOUT)
assert ret.returncode==0,(ret.returncode,(out/'gmat_run.log').read_text()[-4000:])
# GMAT repeats report headers after Report commands; accept numeric rows only.
rows=[]
for line in (out/'gmat_trajectory.txt').read_text().splitlines():
    try:
        vals=[float(v) for v in line.split()]
    except ValueError:
        continue
    if len(vals)==8: rows.append(vals)
data=np.array(rows,dtype=float)
if not len(data):raise ValueError('no GMAT numeric trajectory samples')
end=data[-1,1:].copy();end[:6]*=1000
ref=np.array(t['heliocentric_final_SI'])
result={'GMAT_release':'R2026a','epoch_TAI_ModJulian':21545.,'frame':'Sun-centered MJ2000Eq',
 'gravity':'Sun point mass only; GMAT default Sun GM, reference 132712440018 km3/s2',
 'duration_s':float(data[-1,0]),'gmat_end_state_SI':end.tolist(),
 'position_difference_m':float(np.linalg.norm(end[:3]-ref[:3])),
 'velocity_difference_m_s':float(np.linalg.norm(end[3:6]-ref[3:6])),
 'mass_difference_kg':float(end[6]-ref[6]),
 'sample_count':len(data),'binary_sha256':hashlib.sha256((B/'GmatConsole-R2026a').read_bytes()).hexdigest(),
 'archive_sha256':hashlib.sha256((R/'gmat-rhel7-x64-R2026a.tar.gz').read_bytes()).hexdigest()}
(out/'gmat_comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
