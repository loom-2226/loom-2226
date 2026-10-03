#!/usr/bin/env python3
import json,subprocess,sys
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engineering.civprop.contracts.earth_country_opportunity_v0_3 import *
SNAP="earth-v0-1-9934d0ac-20260925"
q=f"""with ac as (
 select iso3,sector,
 max(capital) filter(where asset_class='machinery') machinery,
 max(capital) filter(where asset_class='structures') structures,
 max(capital) filter(where asset_class='transport_equipment') transport,
 max(capital) filter(where asset_class='other_assets') other
 from loom_earth.earth_sector_asset_year where snapshot_id='{SNAP}' and year=2026 group by iso3,sector)
select s.iso3,a.display_name,s.year,s.sector,s.value_added,s.gross_output,s.investment,s.capital,s.employment,
d.biological_population,d.births,d.deaths,d.median_age,d.age_under_20,d.age_20_64,d.age_65_plus,
l.legacy_labor_force,l.legacy_employment,ac.machinery,ac.structures,ac.transport,ac.other
from loom_earth.earth_sector_year s join loom_earth.earth_area a using(snapshot_id,iso3)
join loom_earth.earth_demographic_year d using(snapshot_id,iso3,year)
join loom_earth.earth_legacy_labor_year l using(snapshot_id,iso3,year)
join ac using(iso3,sector)
where s.snapshot_id='{SNAP}' and s.year=2026 and a.economic_qualified order by s.iso3,s.sector"""
raw=subprocess.check_output(["psql","-d","loom_dev","-At","-F","|","-c",q],text=True)
states=[]
for line in raw.splitlines():
 z=line.split("|"); nums=list(map(float,z[4:]))
 states.append(CountrySectorStateV03(z[0],z[1],int(z[2]),z[3],*nums))
rows=derive(states)
doc={"surface_id":"EARTH_COUNTRY_OPPORTUNITY_2026_V0_3","snapshot":SNAP,"country_count":len(set(x.iso3 for x in rows)),
"sector_count":len(set(x.sector for x in rows)),"row_count":len(rows),"digest":digest(rows),"rows":[asdict(x) for x in rows]}
out=Path(__file__).resolve().parents[2]/"engineering/civprop/candidate_inputs/EARTH_COUNTRY_OPPORTUNITY_2026_V0_3.json"
out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
print(doc["country_count"],doc["sector_count"],doc["row_count"],doc["digest"])
