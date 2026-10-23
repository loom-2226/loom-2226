"""Fix execution namespace of own Sun-GM pilot wrapper."""
from pathlib import Path
from simulation.offworld_mvp.build7.compile_solar_accessibility import SUN_GM_KM3_S2
P=Path(__file__).resolve().parent;f=P/'PR427_ASSIST_2035_PILOT_FIXED_TEST_ONLY.py';source=f.read_text()
old='mu_sun=float(con.execute("select gm_km3_s2 from celestial_dynamics where entity_id=\'SU\'").fetchone()[0])'
assert source.count(old)==1
source=source.replace(old,'mu_sun=SUN_GM_KM3_S2')
print('FIXES SUN_GM_SOURCE_BUILD7 AND EXEC_NAMESPACE',flush=True)
exec(compile(source,str(f),'exec'),{'__name__':'__main__','__file__':str(f),'SUN_GM_KM3_S2':SUN_GM_KM3_S2})
