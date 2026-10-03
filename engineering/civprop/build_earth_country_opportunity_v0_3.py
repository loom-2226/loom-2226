#!/usr/bin/env python3
import argparse,json,subprocess,sys
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engineering.civprop.contracts.earth_country_opportunity_v0_3 import *
SNAP="earth-v0-1-9934d0ac-20260925"
def f(x): return None if x=="" else float(x)
def load(db,year):
 q=f"""with ac as (
 select iso3,sector,
 sum(capital) filter(where asset_class='machinery') machinery,
 sum(capital) filter(where asset_class='structures') structures,
 sum(capital) filter(where asset_class='transport_equipment') transport,
 sum(capital) filter(where asset_class='other_assets') other,
 sum(investment) asset_investment,sum(replacement_need) replacement_need,
 sum(replacement_funded) replacement_funded,sum(expansion_investment) expansion_investment
 from loom_earth.earth_sector_asset_year where snapshot_id='{SNAP}' and year={year} group by iso3,sector)
select s.iso3,a.display_name,s.year,s.sector,s.value_added,s.gross_output,s.investment,s.capital,s.employment,
d.biological_population,d.births,d.deaths,d.median_age,d.age_under_20,d.age_20_64,d.age_65_plus,
lg.legacy_labor_force,lg.legacy_employment,ac.machinery,ac.structures,ac.transport,ac.other,
ac.asset_investment,ac.replacement_need,ac.replacement_funded,ac.expansion_investment,
lc.total_effective_labor,lc.synthetic_effective_labor,lc.machine_task_capacity
from loom_earth.earth_sector_year s join loom_earth.earth_area a using(snapshot_id,iso3)
join loom_earth.earth_demographic_year d using(snapshot_id,iso3,year)
join loom_earth.earth_legacy_labor_year lg using(snapshot_id,iso3,year)
join ac using(iso3,sector)
left join loom_earth.earth_labor_composition_year lc using(snapshot_id,iso3,year)
where s.snapshot_id='{SNAP}' and s.year={year} and a.economic_qualified order by s.iso3,s.sector"""
 raw=subprocess.check_output(["psql","-d",db,"-At","-F","|","-c",q],text=True)
 states=[]
 for line in raw.splitlines():
  z=line.split("|")
  states.append(CountrySectorStateV03(z[0],z[1],int(z[2]),z[3],*(f(v) for v in z[4:])))
 return states
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--database",default="loom_dev");ap.add_argument("--year",type=int,default=2026);ap.add_argument("--output")
 a=ap.parse_args();rows=derive(load(a.database,a.year))
 doc={"surface_id":f"EARTH_COUNTRY_OPPORTUNITY_{a.year}_V0_3","snapshot":SNAP,"year":a.year,
 "country_count":len(set(x.iso3 for x in rows)),"sector_count":len(set(x.sector for x in rows)),"row_count":len(rows),
 "digest":digest(rows),"rows":[asdict(x) for x in rows]}
 out=Path(__file__).resolve().parents[2]/(a.output or f"engineering/civprop/candidate_inputs/EARTH_COUNTRY_OPPORTUNITY_{a.year}_V0_3.json")
 out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
 print(doc["country_count"],doc["sector_count"],doc["row_count"],doc["digest"],out)
if __name__=="__main__":main()
