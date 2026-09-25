#!/usr/bin/env python3
"""Build, import, and verify the immutable Earth 2026-2226 PostgreSQL projection."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_SHA = "d6372ece50976fecfaf76b382d9b682560b70273"
PROMOTION_MANIFEST_SHA = "9934d0ac9f6cbb43d1da91a777ef462a6ae63c9a262bf10592685a8830d20aa2"
MODEL = "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24"
SCENARIO = "MED_CENTRAL__SYNTH_CENTRAL"
SNAPSHOT_ID = "earth-v0-1-9934d0ac-20260925"
V4_MODEL = "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24"
LAB_SHA = "cb4e63554f8ecfaf35a8c3b70275fea479959fbd"
PROMOTION_MERGE = "c27b81b850212c530e61a87f7bf2a4b9a5802af7"

DEFAULTS = {
    "wpp_age": Path("/home/ubuntu/LOOM_Earth2026/raw/WPP2024_PopulationByAge5GroupSex_Percentage_Medium.csv.gz"),
    "wpp_total": Path("/home/ubuntu/LOOM_Earth2026/raw/WPP2024_Demographic_Indicators_Medium.csv.gz"),
    "v4": Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24"),
    "demography": Path("/home/ubuntu/loom_earth_lean_biosynthetic_v0_1_20260924/demography/MED_CENTRAL"),
    "replay": Path("/home/ubuntu/LOOM_ARCHIVE/EARTH_TEMPORAL/2026-09-25/MED_CENTRAL__SYNTH_CENTRAL_detailed_replay"),
    "stage": Path("/home/ubuntu/LOOM_ARCHIVE/EARTH_TEMPORAL/2026-09-25/postgres_import_stage"),
}

TABLE_FILES = {
    "earth_area": ["snapshot_id","iso3","display_name","wpp_location_id","wpp_location_type","economic_qualified"],
    "earth_demographic_year": ["snapshot_id","iso3","year","biological_population","births","deaths","median_age","age_under_20","age_20_64","age_65_plus","age_80_plus","age_100_plus","age_120_plus","age_150_plus","derivation_id"],
    "earth_biological_cohort_year": ["snapshot_id","iso3","year","sex","age_start","age_span","persons","open_ended","derivation_id"],
    "earth_economic_year": ["snapshot_id","iso3","year","value_added","gross_output","investment","capital","population","derivation_id"],
    "earth_sector_year": ["snapshot_id","iso3","sector","year","value_added","gross_output","investment","capital","employment","effective_labor","derivation_id"],
    "earth_sector_asset_year": ["snapshot_id","iso3","sector","asset_class","year","capital","investment","depreciation_rate","replacement_need","replacement_funded","expansion_investment","derivation_id"],
    "earth_legacy_labor_year": ["snapshot_id","iso3","year","legacy_employment","legacy_labor_force","labor_market_working_age_population","derivation_id"],
    "earth_labor_composition_year": ["snapshot_id","iso3","year","biological_population","labor_capable_biological_population","biological_effective_labor","synthetic_population","synthetic_effective_labor","machine_task_capacity","total_effective_labor","recognized_person_population","derivation_id"],
}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def read_ndjson(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def sqlq(value) -> str:
    if value is None: return "NULL"
    return "'"+str(value).replace("'","''")+"'"

def psql(database: str, sql: str, *, file: Path|None=None) -> str:
    cmd=["psql","-X","-qAt","-v","ON_ERROR_STOP=1","-d",database]
    if file: cmd += ["-f",str(file)]
    cmd += ["-c",sql]
    r=subprocess.run(cmd,text=True,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def writer(stage: Path, name: str):
    f=(stage/f"{name}.csv").open("w",encoding="utf-8",newline="")
    return f,csv.writer(f,lineterminator="\n")

def row_values(columns, row):
    return [row.get(k) for k in columns]

def validate_v4(v4: Path, files: list[Path]):
    manifest=json.loads((v4/"RUN_MANIFEST.json").read_text())
    records={**manifest["candidate_local_artifacts"],**manifest["selected_outputs"]}
    expected={str(Path(v["path"]).resolve()):(v["sha256"],v["bytes"]) for v in records.values()}
    for path in files:
        key=str(path.resolve())
        if key not in expected: raise ValueError(f"v4 artifact absent from promoted run manifest: {path}")
        if (sha256(path),path.stat().st_size)!=expected[key]: raise ValueError(f"v4 artifact mismatch: {path}")

def source_paths(v4: Path, replay: Path):
    paths=[]
    for stem in ("countries","country_sectors","country_sector_assets"):
        paths += [v4/f"stage_2026_2031/{stem}_2026_2031.ndjson",
                  v4/f"stage_2031_2060/{stem}_2031_2060.ndjson",
                  v4/f"successor_80_2226/results/{stem}_2060_2226.ndjson",
                  replay/f"{stem}_2100_2226.ndjson"]
    return paths

def cohort_metrics(cohorts):
    by_age={age:cohorts["M"].get(age,0.0)+cohorts["F"].get(age,0.0) for age in sorted(cohorts["M"])}
    pop=sum(by_age.values())
    def total(lo,hi=None): return sum(v for a,v in by_age.items() if a>=lo and (hi is None or a<=hi))
    cumulative=0.0; median=max(by_age)+2.5
    for age,value in by_age.items():
        if cumulative+value>=pop/2:
            median=age+5*max(0,min(1,(pop/2-cumulative)/max(value,1e-30))); break
        cumulative+=value
    return {"population":pop,"median_age":median,"age_under_20":total(0,15),"age_20_64":total(20,60),
            "age_65_plus":total(65),"age_80_plus":total(80),"age_100_plus":total(100),
            "age_120_plus":total(120),"age_150_plus":total(150)}

def prepare(args):
    stage=args.stage
    if stage.exists(): raise ValueError(f"immutable staging directory already exists: {stage}")
    stage.mkdir(parents=True)
    v4_files=source_paths(args.v4,args.replay)[:]
    validate_v4(args.v4,[p for i,p in enumerate(v4_files) if i%4!=3])
    for p in v4_files:
        if not p.exists() or p.stat().st_size==0: raise ValueError(f"missing/empty source: {p}")
    wpp_sha={"age":sha256(args.wpp_age),"total":sha256(args.wpp_total)}
    if wpp_sha!={"age":"c2a7b248c01399688a3461d4a2303c93aabc7d36e5dbf6b378429ed4bf40b012",
                 "total":"286ac36bb1415e2e1ade03acfef0a29f0e4c087e2f78e38c48f50c5df89082bc"}:
        raise ValueError(f"WPP source hash mismatch: {wpp_sha}")

    economic_isos=set(json.loads((args.v4/"PROMOTION_SCOPE.json").read_text())["economic_qualification"]["iso3"])
    totals={}; names={}; locids={}; vital={}
    with gzip.open(args.wpp_total,"rt",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r["Variant"]=="Medium" and r["LocTypeName"]=="Country/Area" and 2026<=int(r["Time"])<=2100:
                iso=r["ISO3_code"].strip(); year=int(r["Time"])
                totals[(iso,year)]=float(r["TPopulation1Jan"])*1000
                names[iso]=r["Location"]; locids[iso]=int(r["LocID"])
                vital[(iso,year)]=(float(r["Births"])*1000,float(r["Deaths"])*1000)
    if len(names)!=237 or len(totals)!=237*75: raise ValueError("WPP annual Country/Area coverage mismatch")

    handles={}; writers={}; counts=defaultdict(int)
    for table,cols in TABLE_FILES.items(): handles[table],writers[table]=writer(stage,table)
    def emit(table,row): writers[table].writerow(row_values(TABLE_FILES[table],row)); counts[table]+=1
    for iso in sorted(names): emit("earth_area",{"snapshot_id":SNAPSHOT_ID,"iso3":iso,"display_name":names[iso],"wpp_location_id":locids[iso],"wpp_location_type":"Country/Area","economic_qualified":iso in economic_isos})

    pct=defaultdict(lambda:defaultdict(dict))
    with gzip.open(args.wpp_age,"rt",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r["Variant"]=="Medium" and r["LocTypeName"]=="Country/Area" and 2026<=int(r["Time"])<=2100:
                pct[(r["ISO3_code"].strip(),int(r["Time"]))][int(r["AgeGrpStart"])]= {"M":float(r["PopMale"]),"F":float(r["PopFemale"]),"span":int(r["AgeGrpSpan"])}
    if len(pct)!=237*75: raise ValueError("WPP age-sex annual coverage mismatch")
    for (iso,year),ages in sorted(pct.items()):
        norm=sum(v[s] for v in ages.values() for s in ("M","F")); cohorts={"M":{},"F":{}}
        for age,v in ages.items():
            for sex in ("M","F"):
                persons=totals[(iso,year)]*v[sex]/norm; cohorts[sex][age]=persons
                emit("earth_biological_cohort_year",{"snapshot_id":SNAPSHOT_ID,"iso3":iso,"year":year,"sex":sex,"age_start":age,"age_span":None if age>=100 else v["span"],"persons":persons,"open_ended":age>=100,"derivation_id":"WPP_2024_MEDIUM_2026_2100"})
        m=cohort_metrics(cohorts); births,deaths=vital[(iso,year)]
        emit("earth_demographic_year",{"snapshot_id":SNAPSHOT_ID,"iso3":iso,"year":year,"biological_population":m.pop("population"),"births":births,"deaths":deaths,**m,"derivation_id":"WPP_2024_MEDIUM_2026_2100"})

    successor_country={}
    for r in read_ndjson(args.demography/"biological_country_2100_2226.ndjson"):
        if r["year"]>=2101: successor_country[(r["iso3"],r["year"])]=r
    for r in read_ndjson(args.demography/"biological_cohorts_2100_2226.ndjson"):
        if r["year"]<2101: continue
        for sex,ages in r["cohorts"].items():
            for age,persons in ages.items(): emit("earth_biological_cohort_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":r["year"],"sex":sex,"age_start":int(age),"age_span":5,"persons":persons,"open_ended":int(age)==155,"derivation_id":"MED_CENTRAL_COHORT_2101_2226"})
        c=successor_country[(r["iso3"],r["year"])]
        emit("earth_demographic_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":r["year"],"biological_population":c["population"],"births":c["births"],"deaths":c["deaths"],"median_age":c["median_age_approx"],"age_under_20":c["under_20"],"age_20_64":c["age_20_64"],"age_65_plus":c["age_65_plus"],"age_80_plus":c["age_80_plus"],"age_100_plus":c["age_100_plus"],"age_120_plus":c["age_120_plus"],"age_150_plus":c["age_150_plus"],"derivation_id":"MED_CENTRAL_COHORT_2101_2226"})

    def ranges(kind):
        return [(args.v4/f"stage_2026_2031/{kind}_2026_2031.ndjson",2026,2030,"V4_2026_2030"),
                (args.v4/f"stage_2031_2060/{kind}_2031_2060.ndjson",2031,2059,"V4_2031_2059"),
                (args.v4/f"successor_80_2226/results/{kind}_2060_2226.ndjson",2060,2100,"V4_2060_2100"),
                (args.replay/f"{kind}_2100_2226.ndjson",2101,2226,"BIOSYNTHETIC_2101_2226")]
    for path,start,end,deriv in ranges("countries"):
        for r in read_ndjson(path):
            if not start<=r["year"]<=end: continue
            emit("earth_economic_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":r["year"],"value_added":r["value_added"],"gross_output":r["gross_output"],"investment":r["investment"],"capital":r["capital"],"population":r.get("population",r.get("biological_population")),"derivation_id":deriv})
            if r["year"]<=2100: emit("earth_legacy_labor_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":r["year"],"legacy_employment":r["employment"],"legacy_labor_force":r.get("labor_force"),"labor_market_working_age_population":r.get("labor_market_working_age_population"),"derivation_id":deriv})
            if deriv=="BIOSYNTHETIC_2101_2226": emit("earth_labor_composition_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":r["year"],"biological_population":r["biological_population"],"labor_capable_biological_population":r["labor_capable_biological_population"],"biological_effective_labor":r["biological_labor"],"synthetic_population":r["synthetic_population"],"synthetic_effective_labor":r["synthetic_labor"],"machine_task_capacity":r["machine_task_capacity"],"total_effective_labor":r["effective_labor_input"],"recognized_person_population":r["recognized_person_population"],"derivation_id":deriv})
    # The explicit 2100 selected labor boundary is preserved alongside legacy employment.
    for r in read_ndjson(args.replay/"countries_2100_2226.ndjson"):
        if r["year"]==2100: emit("earth_labor_composition_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"year":2100,"biological_population":r["biological_population"],"labor_capable_biological_population":r["labor_capable_biological_population"],"biological_effective_labor":r["biological_labor"],"synthetic_population":r["synthetic_population"],"synthetic_effective_labor":r["synthetic_labor"],"machine_task_capacity":r["machine_task_capacity"],"total_effective_labor":r["effective_labor_input"],"recognized_person_population":r["recognized_person_population"],"derivation_id":"BIOSYNTHETIC_BOUNDARY_2100"})
    for path,start,end,deriv in ranges("country_sectors"):
        for r in read_ndjson(path):
            if start<=r["year"]<=end: emit("earth_sector_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"sector":r["sector"],"year":r["year"],"value_added":r["value_added"],"gross_output":r["gross_output"],"investment":r["investment"],"capital":r["capital"],"employment":r.get("employment",r.get("biological_labor")),"effective_labor":r.get("effective_labor"),"derivation_id":deriv})
    for path,start,end,deriv in ranges("country_sector_assets"):
        for r in read_ndjson(path):
            if start<=r["year"]<=end: emit("earth_sector_asset_year",{"snapshot_id":SNAPSHOT_ID,"iso3":r["iso3"],"sector":r["sector"],"asset_class":r["asset_class"],"year":r["year"],"capital":r["capital"],"investment":r.get("investment"),"depreciation_rate":r.get("asset_depreciation_rate"),"replacement_need":r.get("replacement_need"),"replacement_funded":r.get("replacement_funded"),"expansion_investment":r.get("expansion_investment"),"derivation_id":deriv})
    for f in handles.values(): f.close()
    artifacts={str(p):{"sha256":sha256(p),"bytes":p.stat().st_size} for p in [args.wpp_age,args.wpp_total,*source_paths(args.v4,args.replay),args.demography/"biological_country_2100_2226.ndjson",args.demography/"biological_cohorts_2100_2226.ndjson"]}
    manifest={"schema":"loom-earth-postgres-temporal-import-v1","snapshot_id":SNAPSHOT_ID,"authority_main_sha":AUTHORITY_SHA,"promotion_manifest_sha256":PROMOTION_MANIFEST_SHA,"model":MODEL,"scenario":SCENARIO,"artifacts":artifacts,"table_counts":dict(counts),"stage_files":{p.name:{"sha256":sha256(p),"bytes":p.stat().st_size} for p in sorted(stage.glob("*.csv"))}}
    (stage/"IMPORT_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"snapshot_id":SNAPSHOT_ID,"counts":counts,"manifest":str(stage/"IMPORT_MANIFEST.json")},sort_keys=True))

def migrate(database):
    for path in sorted((ROOT/"data/postgres/migrations").glob("[0-9][0-9][0-9]_*.sql")):
        revision=path.stem; digest=sha256(path)
        exists=psql(database,"SELECT to_regclass('loom_control.schema_migration') IS NOT NULL")
        prior=psql(database,f"SELECT script_sha256 FROM loom_control.schema_migration WHERE revision={sqlq(revision)}") if exists=="t" else ""
        if prior:
            if prior!=digest: raise ValueError(f"applied migration changed: {revision}")
            continue
        psql(database,f"INSERT INTO loom_control.schema_migration(revision,script_sha256) VALUES ({sqlq(revision)},{sqlq(digest)})",file=path)

def semantics():
    base="NULL / unavailable before a modeled boundary does not mean zero."
    rows=[
      ("DEM.BIO_POP","Biological population","Biological human persons alive at Jan-1/model boundary.","persons","area-year","biological humans","SELECTED_AUTHORITY",base,2026,2226,"WPP through 2100; selected cohort successor after 2100"),
      ("DEM.SYNTH_POP","Synthetic-person population","Recognized synthetic persons; excludes biological humans and machine tasks.","persons","economic-area-year","recognized synthetic persons","SELECTED_MODEL","Synthetic-person headcount is not synthetic effective labor. "+base,2100,2226,"selected successor only"),
      ("DEM.RECOGNIZED_POP","Recognized-person population","Biological population plus recognized synthetic-person population.","persons","economic-area-year","recognized persons","DERIVED","Machine task capacity is not a population. "+base,2100,2226,"economic 80 only"),
      ("DEM.MEDIAN_AGE","Approximate biological median age","Median derived from five-year biological cohorts.","years","area-year","biological humans","DERIVED","Grouped-cohort approximation; not synthetic age. "+base,2026,2226,"237 WPP areas"),
    ]
    for key,label,definition in [("DEM.AGE_UNDER_20","Biological persons under 20","Biological persons in age groups 0-19."),("DEM.AGE_20_64","Biological persons age 20-64","Biological persons in age groups 20-64."),("DEM.AGE_65_PLUS","Biological persons age 65+","Biological persons age 65 or older."),("DEM.AGE_80_PLUS","Biological persons age 80+","Biological persons age 80 or older."),("DEM.AGE_100_PLUS","Biological persons age 100+","Biological persons age 100 or older."),("DEM.AGE_120_PLUS","Biological persons age 120+","Biological persons age 120 or older."),("DEM.AGE_150_PLUS","Biological persons age 150+","Biological persons age 150 or older.")]:
        rows.append((key,label,definition,"persons","area-year","biological humans","DERIVED",base,2026,2226,"237 WPP areas"))
    rows += [
      ("WORK.LEGACY_EMPLOYMENT","Legacy employment","Employment under predecessor v4 labor-market semantics.","persons/FTE proxy","economic-area-year","legacy v4 employment","QUALIFIED_MODEL","Legacy employment is not automatically comparable to post-2100 biological effective labor. "+base,2026,2100,"economic 80"),
      ("WORK.LABOR_CAPABLE_BIO","Labor-capable biological population","Health and age eligible biological population under the selected cohort labor interface.","persons","economic-area-year","biological humans","SELECTED_MODEL",base,2100,2226,"economic 80"),
      ("WORK.BIO_EFFECTIVE_LABOR","Biological effective labor","Cohort population weighted by functional health, participation and paid-hours factors.","effective-labor equivalents","economic-area-year","biological labor input","SELECTED_MODEL","Biological effective labor is not worker headcount. "+base,2100,2226,"economic 80"),
      ("WORK.SYNTH_EFFECTIVE_LABOR","Synthetic effective labor","Synthetic-person stock weighted by participation and capacity.","effective-labor equivalents","economic-area-year","synthetic-person labor input","SELECTED_MODEL","Synthetic effective labor is not synthetic-person headcount. "+base,2100,2226,"economic 80"),
      ("WORK.MACHINE_TASK_CAPACITY","Non-person machine task capacity","Non-person automation contribution to production.","effective-labor equivalents","economic-area-year","non-person automation","SELECTED_MODEL","Machine task capacity is not a population. "+base,2100,2226,"economic 80"),
      ("WORK.TOTAL_EFFECTIVE_LABOR","Total effective labor","Biological effective labor plus synthetic effective labor plus non-person machine-task capacity.","effective-labor equivalents","economic-area-year","production labor input","DERIVED",base,2100,2226,"economic 80"),
    ]
    for key,label,definition in [("ECON.VALUE_ADDED","Value added","Modeled economic value added in baseline proxy units."),("ECON.GROSS_OUTPUT","Gross output","Modeled gross output in baseline proxy units."),("ECON.CAPITAL","Productive capital","Modeled productive capital stock in baseline proxy units."),("ECON.INVESTMENT","Investment","Modeled annual investment in baseline proxy units.")]:
        rows.append((key,label,definition,"model proxy monetary units","economic-area-year","economic accounts","QUALIFIED_MODEL","Value added per person is production intensity, not household income. "+base,2026,2226,"economic 80"))
    return rows

def import_stage(args):
    manifest=json.loads((args.stage/"IMPORT_MANIFEST.json").read_text())
    for name,record in manifest["stage_files"].items():
        p=args.stage/name
        if (sha256(p),p.stat().st_size)!=(record["sha256"],record["bytes"]): raise ValueError(f"stage mismatch: {name}")
    migrate(args.database)
    existing=psql(args.database,f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")
    if existing:
        verify(args); print(json.dumps({"status":"IDEMPOTENT_EXISTING_SNAPSHOT","snapshot_id":SNAPSHOT_ID})); return
    artifacts=manifest["artifacts"]
    semantic_hash=hashlib.sha256(json.dumps(semantics(),sort_keys=True).encode()).hexdigest()
    contract_hash=hashlib.sha256(json.dumps({"model":MODEL,"scenario":SCENARIO,"manifest":PROMOTION_MANIFEST_SHA},sort_keys=True).encode()).hexdigest()
    sql=["BEGIN;",
         f"INSERT INTO loom_control.semantic_version(semantic_sha256,source_path,source_git_commit) VALUES ({sqlq(semantic_hash)},{sqlq('tools/earth_temporal_pg.py')},{sqlq(AUTHORITY_SHA)});",
         f"INSERT INTO loom_control.snapshot(snapshot_id,consumer_git_commit,consumer_query_sha256,contract_sha256,semantic_sha256,state) VALUES ({sqlq(SNAPSHOT_ID)},{sqlq(AUTHORITY_SHA)},{sqlq(sha256(ROOT/'tools/earth_temporal_pg.py'))},{sqlq(contract_hash)},{sqlq(semantic_hash)},'CANDIDATE');"]
    for path,record in artifacts.items():
        role=("WPP_2024_MEDIUM" if "WPP2024" in path else "SELECTED_DETAILED_REPLAY" if str(args.replay) in path else "PROMOTED_V4_OR_SUCCESSOR_SOURCE")
        sql.append(f"INSERT INTO loom_control.source_artifact(artifact_sha256,source_role,source_path,byte_count,source_git_commit,retained_location) VALUES ({sqlq(record['sha256'])},{sqlq(role)},{sqlq(path)},{record['bytes']},{sqlq(AUTHORITY_SHA)},{sqlq(path)}) ON CONFLICT (artifact_sha256) DO NOTHING;")
        sql.append(f"INSERT INTO loom_control.snapshot_source VALUES ({sqlq(SNAPSHOT_ID)},{sqlq(record['sha256'])},{sqlq(role)});")
    derivs=[
      ("WPP_2024_MEDIUM_2026_2100","UN_WPP_2024_MEDIUM","Jan-1 total normalized age-sex percentage source","EMPIRICAL_PROJECTION_SOURCE",None,str(args.wpp_age)),
      ("MED_CENTRAL_COHORT_2101_2226",MODEL,"Annual five-year cohort propagation with MED_CENTRAL mortality and health semantics","SELECTED_MODEL",SCENARIO,str(args.demography/"biological_cohorts_2100_2226.ndjson")),
      ("BIOSYNTHETIC_BOUNDARY_2100",MODEL,"Explicit labor reinterpretation and production-A rebase with economic levels preserved","SELECTED_MODEL",SCENARIO,str(args.replay/"countries_2100_2226.ndjson")),
      ("BIOSYNTHETIC_2101_2226",MODEL,"Deterministic full-row replay of promoted selected coupled successor","SELECTED_MODEL",SCENARIO,str(args.replay/"countries_2100_2226.ndjson")),
    ]
    # V4 ranges use their first country artifact as family pin; exact all-file pins remain snapshot sources.
    for did,method,artifact in [("V4_2026_2030","promoted v4 stage 2026-2031",args.v4/"stage_2026_2031/countries_2026_2031.ndjson"),("V4_2031_2059","promoted v4 stage 2031-2060",args.v4/"stage_2031_2060/countries_2031_2060.ndjson"),("V4_2060_2100","promoted v4 successor_80 trajectory",args.v4/"successor_80_2226/results/countries_2060_2226.ndjson")]: derivs.append((did,V4_MODEL,method,"QUALIFIED_MODEL",None,str(artifact)))
    for did,model,method,status,scenario,path in derivs:
        digest=artifacts[path]["sha256"]
        sql.append(f"INSERT INTO loom_earth.earth_derivation VALUES ({sqlq(SNAPSHOT_ID)},{sqlq(did)},{sqlq(model)},{sqlq(method)},{sqlq(status)},{sqlq(scenario)},{sqlq(digest)},{sqlq('Source bytes remain outside PostgreSQL and are hash pinned.')});")
    contexts={
      "model_designation":MODEL,"selected_scenario":SCENARIO,"authority_main_sha":AUTHORITY_SHA,"promotion_merge_sha":PROMOTION_MERGE,"promotion_manifest_sha256":PROMOTION_MANIFEST_SHA,"research_lab_source_sha":LAB_SHA,"v4_predecessor":V4_MODEL,
      "fertility_path":{"status":"setting calibration","anchors":{"2100":1.838,"2125":1.802,"2150":1.790,"2175":1.815,"2200":1.846,"2226":1.880}},
      "medical_longevity":{"mechanism":"age-specific mortality and functional health; never a population multiplier","broad":"near-universal mature-Earth infrastructure","high_end":"material but unequal","extreme":"rare","immortality":False},
      "synthetic_stock":{"equation":"S(t+1)=S(t)+additions-losses+net migration","net_migration":0,"persons_distinct_from_machine_tasks":True},
      "allocation_repair":{"formula":"normalized(absolute_capacity_share^0.75 * intensity_share^0.25)","country_specific_exceptions":False},
      "sensitivity":{"grid":"3x3 preserved in promoted authority","medical_biological_population_range_2226":"approximately 6.991B-7.465B"},
      "handoff_2100":{"demography":"WPP Jan-1 state represented once in consumer demographic timeline; selected propagation starts 2101","economics":"v4 levels through 2100; coupled successor starts 2101","labor":"legacy employment and selected effective labor are separate semantic families"},
      "workforce_invariant":{"rule":"biological_effective_labor <= labor_capable_biological_population <= biological_population","expected_2226":"80/80 PASS"},
      "limitations":["No selected synthetic population before 2100","No economics for 157 demographic-only areas","No off-Earth coupling","Five-year cohort resolution","Model proxy monetary units are not household income"],
    }
    for k,v in contexts.items(): sql.append(f"INSERT INTO loom_control.model_context_record VALUES ({sqlq(SNAPSHOT_ID)},{sqlq(k)},{sqlq(json.dumps(v))}::jsonb,{sqlq('Embedded selected authority context; Git remains release authority.')});")
    for row in semantics():
        key,label,definition,unit,grain,basis,status,warning,start,end,coverage=row
        hashes=[PROMOTION_MANIFEST_SHA]
        sql.append("INSERT INTO loom_control.variable_semantics VALUES ("+",".join([sqlq(SNAPSHOT_ID),sqlq(key),sqlq(label),sqlq(definition),sqlq(unit),sqlq(grain),sqlq(basis),sqlq(status),sqlq(definition),sqlq(warning),str(start),str(end),sqlq("ANNUAL"),sqlq(coverage),sqlq(MODEL if end>2100 else V4_MODEL),sqlq(SCENARIO if start>=2100 else None),sqlq("See earth_derivation and import_batch"),sqlq(json.dumps(hashes))+"::jsonb",sqlq(V4_MODEL if start>=2100 else None),sqlq(coverage)])+");")
    coverage=[("demography","DEM.BIO_POP","237_WPP_COUNTRY_AREA",2026,2226,"WPP_2024_MEDIUM_THEN_MED_CENTRAL","SELECTED_AUTHORITY",[]),("cohorts",None,"237_WPP_COUNTRY_AREA",2026,2226,"WPP_AGE_SEX_THEN_MED_CENTRAL","SELECTED_AUTHORITY",[]),("economics","ECON.VALUE_ADDED","80_QUALIFIED_ECONOMIES",2026,2226,"V4_THEN_COUPLED_SUCCESSOR","SELECTED_AUTHORITY",[]),("legacy_labor","WORK.LEGACY_EMPLOYMENT","80_QUALIFIED_ECONOMIES",2026,2100,"V4","QUALIFIED_MODEL",[[2101,2226,"SUPERSEDED_SEMANTIC"]]),("biosynthetic_labor","WORK.TOTAL_EFFECTIVE_LABOR","80_QUALIFIED_ECONOMIES",2100,2226,MODEL,"SELECTED_MODEL",[[2026,2099,"NOT_MODELED_BY_THIS_AUTHORITY"]]),("synthetic_persons","DEM.SYNTH_POP","80_QUALIFIED_ECONOMIES",2100,2226,MODEL,"SELECTED_MODEL",[[2026,2099,"NOT_MODELED_BY_THIS_AUTHORITY"]])]
    for fam,var,scope,start,end,model,status,unavailable in coverage: sql.append(f"INSERT INTO loom_control.temporal_coverage VALUES ({sqlq(SNAPSHOT_ID)},{sqlq(fam)},{sqlq(var)},{sqlq(scope)},{start},{end},'ANNUAL',{sqlq(scope)},{sqlq(model)},{sqlq(status)},{sqlq(V4_MODEL if start>=2100 else None)},{sqlq(json.dumps(unavailable))}::jsonb);")
    sql.append("COMMIT;")
    psql(args.database,"\n".join(sql))
    for table,cols in TABLE_FILES.items():
        path=(args.stage/f"{table}.csv").resolve()
        psql(args.database,f"\\copy loom_civ.{table}({','.join(cols)}) FROM {sqlq(path)} WITH (FORMAT csv, NULL '')")
    # Range-level batch lineage pins every exact source in snapshot_source; record counts pin resulting families.
    primary=next(iter(artifacts.values()))["sha256"]
    for table,count in manifest["table_counts"].items():
        psql(args.database,f"INSERT INTO loom_control.import_batch VALUES ({sqlq(SNAPSHOT_ID)},{sqlq('batch-'+table)},{sqlq(table)},{sqlq(primary)},{sqlq(MODEL)},{sqlq('MULTI_SOURCE_SEE_SNAPSHOT_SOURCE')},{count},2026,2226,{sqlq('Primary key columns in migration 004; exact source hashes in snapshot_source')},now())")
    verify(args,validate=True)
    print(json.dumps({"status":"IMPORTED_AND_VALIDATED","snapshot_id":SNAPSHOT_ID},sort_keys=True))

def verify(args,validate=False):
    q=lambda s: psql(args.database,s)
    state=q(f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")
    if not state: raise ValueError("snapshot missing")
    checks={
      "areas":int(q(f"SELECT count(*) FROM loom_earth.earth_area WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "demography":int(q(f"SELECT count(*) FROM loom_earth.earth_demographic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "cohorts":int(q(f"SELECT count(*) FROM loom_earth.earth_biological_cohort_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "economics":int(q(f"SELECT count(*) FROM loom_earth.earth_economic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "sectors":int(q(f"SELECT count(*) FROM loom_earth.earth_sector_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "assets":int(q(f"SELECT count(*) FROM loom_earth.earth_sector_asset_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "legacy_labor":int(q(f"SELECT count(*) FROM loom_earth.earth_legacy_labor_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
      "labor":int(q(f"SELECT count(*) FROM loom_earth.earth_labor_composition_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)}")),
    }
    expected=json.loads((args.stage/"IMPORT_MANIFEST.json").read_text())["table_counts"]
    mapping={"areas":"earth_area","demography":"earth_demographic_year","cohorts":"earth_biological_cohort_year","economics":"earth_economic_year","sectors":"earth_sector_year","assets":"earth_sector_asset_year","legacy_labor":"earth_legacy_labor_year","labor":"earth_labor_composition_year"}
    if any(checks[k]!=expected[v] for k,v in mapping.items()): raise ValueError(f"row count mismatch {checks} vs {expected}")
    if q(f"SELECT count(*) FROM loom_earth.earth_demographic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} GROUP BY year HAVING count(*)<>237 LIMIT 1"): raise ValueError("demographic annual coverage failure")
    if q(f"SELECT count(*) FROM loom_earth.earth_economic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} GROUP BY year HAVING count(*)<>80 LIMIT 1"): raise ValueError("economic annual coverage failure")
    workforce=int(q(f"SELECT count(*) FROM loom_earth.earth_labor_composition_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND year=2226 AND biological_effective_labor<=labor_capable_biological_population+1e-6 AND labor_capable_biological_population<=biological_population+1e-6"))
    if workforce!=80: raise ValueError(f"workforce invariant {workforce}/80")
    bad=int(q(f"SELECT count(*) FROM loom_earth.earth_labor_composition_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND (abs(recognized_person_population-biological_population-synthetic_population)>1e-5 OR abs(total_effective_labor-biological_effective_labor-synthetic_effective_labor-machine_task_capacity)>1e-5)"))
    if bad: raise ValueError(f"category identity failures: {bad}")
    endpoint=[float(x) for x in q(f"SELECT d.biological_population,l.synthetic_population,d.biological_population+l.synthetic_population,l.biological_effective_labor,l.synthetic_effective_labor,l.machine_task_capacity,l.total_effective_labor FROM (SELECT sum(biological_population) biological_population FROM loom_earth.earth_demographic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND year=2226) d CROSS JOIN (SELECT sum(synthetic_population) synthetic_population,sum(biological_effective_labor) biological_effective_labor,sum(synthetic_effective_labor) synthetic_effective_labor,sum(machine_task_capacity) machine_task_capacity,sum(total_effective_labor) total_effective_labor FROM loom_earth.earth_labor_composition_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND year=2226) l").split("|")]
    target=[7163281708.265873,9672505.78986048,7172954214.055734,1455527766.770138,10881569.013593039,52627339.05102448,1519036674.8347554]
    if any(not math.isclose(a,b,rel_tol=2e-12,abs_tol=1e-5) for a,b in zip(endpoint,target)): raise ValueError(f"endpoint mismatch {endpoint}")
    va=float(q(f"SELECT sum(value_added) FROM loom_earth.earth_economic_year WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND year=2226"))
    if not math.isclose(va,241453886085432.44,rel_tol=2e-12): raise ValueError(f"VA endpoint mismatch {va}")
    ceres=q("SELECT coalesce((SELECT state FROM loom_control.snapshot WHERE snapshot_id='ceres-v1-0231e5f7da744728ab5021268b6f239b'),'RETIRED_FORENSIC_BASELINE')")
    if ceres not in ("VALIDATED", "RETIRED_FORENSIC_BASELINE"): raise ValueError("unexpected Ceres disposition")
    if validate and state=="CANDIDATE": q(f"UPDATE loom_control.snapshot SET state='VALIDATED' WHERE snapshot_id={sqlq(SNAPSHOT_ID)} AND state='CANDIDATE'")
    print(json.dumps({"snapshot_id":SNAPSHOT_ID,"state":q(f'SELECT state FROM loom_control.snapshot WHERE snapshot_id={sqlq(SNAPSHOT_ID)}'),"counts":checks,"workforce_2226":f"{workforce}/80","endpoint":endpoint,"value_added_2226":va,"ceres_disposition":ceres},sort_keys=True))

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    for name in ("prepare","import","verify"):
        q=sub.add_parser(name); q.add_argument("--database",default="loom_dev"); q.add_argument("--wpp-age",type=Path,default=DEFAULTS["wpp_age"]); q.add_argument("--wpp-total",type=Path,default=DEFAULTS["wpp_total"]); q.add_argument("--v4",type=Path,default=DEFAULTS["v4"]); q.add_argument("--demography",type=Path,default=DEFAULTS["demography"]); q.add_argument("--replay",type=Path,default=DEFAULTS["replay"]); q.add_argument("--stage",type=Path,default=DEFAULTS["stage"]); q.add_argument("--validate",action="store_true")
    args=p.parse_args()
    if args.command=="prepare": prepare(args)
    elif args.command=="import": import_stage(args)
    else: verify(args,validate=args.validate)

if __name__=="__main__": main()
