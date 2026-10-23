"""Correct Sun authority and represent unbounded mass without floating overflow."""
from pathlib import Path
from simulation.offworld_mvp.build7.compile_solar_accessibility import SUN_GM_KM3_S2
P=Path(__file__).resolve().parent;f=P/'PR427_ASSIST_2035_PILOT_FIXED_TEST_ONLY.py';s=f.read_text()
old='mu_sun=float(con.execute("select gm_km3_s2 from celestial_dynamics where entity_id=\'SU\'").fetchone()[0])';assert s.count(old)==1;s=s.replace(old,'mu_sun=SUN_GM_KM3_S2')
old='return m*(q*(1-eps)/(1-eps*q))**n,n';assert s.count(old)==1;s=s.replace(old,'return math.exp(math.log(m)+n*math.log(q*(1-eps)/(1-eps*q))) if math.log(m)+n*math.log(q*(1-eps)/(1-eps*q))<709 else math.inf,n')
print('FIXES SUN_GM_FROM_BUILD7, EXEC_NAMESPACE, OVERFLOW_TO_INFINITY',flush=True)
exec(compile(s,str(f),'exec'),{'__name__':'__main__','__file__':str(f),'SUN_GM_KM3_S2':SUN_GM_KM3_S2})
