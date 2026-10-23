"""Snapshot existing LOOM world authority; never invent missing physical parameters."""
import csv,hashlib,json,sqlite3
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3];DB=ROOT/'data/LOOM_2226.sqlite3';OUT=P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv';REPORT=P/'RENDEZVOUS_WORLD_AUTHORITY_REPORT_TEST_ONLY.json'
# Explicit source-authority mapping, not invented physical data.
NAMES={'MERCURY':'ME','VENUS':'VE','MARS':'MA','CERES':'CER','PLUTO':'PL','PALLAS':'PAL','VESTA':'VST','PSYCHE':'PSY','HYGIEA':'HYG','KLEOPATRA':'KLE','DAVIDA':'DAV','INTERAMNIA':'INT','JUNO':'JUN','LUTETIA':'LUT','THEMIS':'THE','MOON':'LU','PHOBOS':'PH','DEIMOS':'DE','IO':'IO','EUROPA':'EU','GANYMEDE':'GA','CALLISTO':'CA','MIMAS':'MIM','ENCELADUS':'EN','TETHYS':'TE','DIONE':'DI','RHEA':'RH','TITAN':'TI','IAPETUS':'IA','PHOEBE':'PB','MIRANDA':'MI','ARIEL':'AR','UMBRIEL':'UM','TITANIA':'TT','OBERON':'OB','PROTEUS':'PR','TRITON':'TR','NEREID':'NR','CHARON':'CH','STYX':'ST','NIX':'NI','KERBEROS':'KE','HYDRA':'HY'}
PARENT={'EA':'EARTH','MA':'MARS','JU':'JUPITER','SA':'SATURN','UR':'URANUS','NE':'NEPTUNE','PL':'PLUTO'}
EXTRA={'DACTYL':'IDA','SELAM':'DINKINESH'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import ALL_BODIES
 c=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 vals={r['entity_id']:dict(r) for r in c.execute('select * from celestial_dynamics')}
 fields=['body','authority_entity_id','parent','parent_entity_id','gm_km3_s2','mean_radius_km','orbit_radius_km','parent_gm_km3_s2','parent_radius_km','missing','source_file','source_line','source_sha256']
 assert not OUT.exists() and not REPORT.exists()
 rows=[]
 for body in ALL_BODIES:
  id=NAMES.get(body);v=vals.get(id,{}) if id else {};pid=v.get('primary_gravity_parent_id');parent=PARENT.get(pid,EXTRA.get(body,'')) if pid and pid!='SOL' else EXTRA.get(body,'')
  pv=vals.get(pid,{}) if pid else {};moon=bool(parent);missing=[]
  if v.get('gm_km3_s2') is None:missing.append('BODY_GM')
  if v.get('mean_radius_km') is None:missing.append('BODY_RADIUS')
  if moon and v.get('reference_orbit_radius_km') is None:missing.append('MOON_ORBIT_RADIUS')
  if moon and pv.get('gm_km3_s2') is None:missing.append('PARENT_GM')
  if moon and pv.get('mean_radius_km') is None:missing.append('PARENT_RADIUS')
  rows.append(dict(body=body,authority_entity_id=id or '',parent=parent,parent_entity_id=pid or '',gm_km3_s2=v.get('gm_km3_s2') if v.get('gm_km3_s2') is not None else '',mean_radius_km=v.get('mean_radius_km') if v.get('mean_radius_km') is not None else '',orbit_radius_km=v.get('reference_orbit_radius_km') if v.get('reference_orbit_radius_km') is not None else '',parent_gm_km3_s2=pv.get('gm_km3_s2') if pv.get('gm_km3_s2') is not None else '',parent_radius_km=pv.get('mean_radius_km') if pv.get('mean_radius_km') is not None else '',missing=';'.join(missing),source_file='data/LOOM_2226.sqlite3:celestial_dynamics',source_line='src/loom_solar_gis.py:1191,1402',source_sha256=sha(DB)))
 with OUT.open('x',newline='') as f:w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
 ea=vals['EA'];report={'world_database_sha256':sha(DB),'world_schema_source_sha256':sha(ROOT/'src/loom_solar_gis.py'),'source':'data/LOOM_2226.sqlite3:celestial_dynamics; src/loom_solar_gis.py:1191,1402','world_earth_gm':ea['gm_km3_s2'],'world_earth_radius':ea['mean_radius_km'],'previous_authorized_earth_gm':'398600.4355','earth_gm_differs':ea['gm_km3_s2']!=398600.4355,'rows':len(rows),'missing':{r['body']:r['missing'] for r in rows if r['missing']},'csv_sha256':sha(OUT),'moon_parent_source':'celestial_dynamics.primary_gravity_parent_id; two asteroid satellites mapped to parent for trajectory only; no authored orbit radius'}
 REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print('WORLD_AUTHORITY_COMPLETE',len(rows),'MISSING',len(report['missing']),'EARTH',ea['gm_km3_s2'],ea['mean_radius_km'],'CSV_SHA',sha(OUT),flush=True)
if __name__=='__main__':main()
