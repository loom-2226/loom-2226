"""Fix own pilot's nonexistent Sun DB row using existing Build7 Lambert authority."""
from pathlib import Path
from simulation.offworld_mvp.build7.compile_solar_accessibility import SUN_GM_KM3_S2
P=Path(__file__).resolve().parent
source=(P/'PR427_ASSIST_2035_PILOT_FIXED_TEST_ONLY.py').read_text()
old='mu_sun=float(con.execute("select gm_km3_s2 from celestial_dynamics where entity_id=\'SU\'").fetchone()[0])'
assert source.count(old)==1
source=source.replace(old,'mu_sun=SUN_GM_KM3_S2')
print('FIX_SUN_GM_SOURCE simulation/offworld_mvp/build7/compile_solar_accessibility.py:SUN_GM_KM3_S2',flush=True)
exec(compile(source,str(P/'PR427_ASSIST_2035_PILOT_FIXED_TEST_ONLY.py'),'exec'),{'__name__':'__main__','SUN_GM_KM3_S2':SUN_GM_KM3_S2})
