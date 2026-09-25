#!/usr/bin/env python3
"""Project LOOM canon chronology and technology scenario anchors into PostgreSQL."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUTHORITY_SHA = "c0b50afdd792cecf0b32a8752855e5afa8694ddd"
CANON_PATH = ROOT / "canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md"
TECH_PATH = ROOT / "docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md"
MANIFEST_PATH = ROOT / "data/postgres/timeline_projection_manifest.json"
MIGRATION_PATH = ROOT / "data/postgres/migrations/010_timeline_projection.sql"
EXPECTED = {"CANON_HISTORY":19,"MODERATE_SCENARIO_ANCHOR":18,"FICTIONAL_PHYSICS_SCENARIO_ANCHOR":5,"SOCIAL_SCENARIO_ANCHOR":1}

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def sqlq(value):
    if value is None: return "NULL"
    return "'"+str(value).replace("'","''")+"'"

def psql(database, sql="", file=None):
    cmd=["psql","-X","-qAt","-v","ON_ERROR_STOP=1","-d",database]
    if file: cmd += ["-f",str(file)]
    if sql: cmd += ["-c",sql]
    r=subprocess.run(cmd,text=True,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def git_head():
    return subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True,capture_output=True,check=True).stdout.strip()

def section(text,start,end):
    i=text.index(start); j=text.index(end,i+len(start)); return text[i:j]

def md_plain(value): return value.replace("**","").replace("`","").strip()

def table_rows(block):
    rows=[]
    headers={"Period","Milestone ID / family","Original milestone ID","Scenario milestone"}
    for line in block.splitlines():
        if not line.startswith("|"): continue
        cells=[c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or md_plain(cells[0]) in headers: continue
        if all(set(c)<=set("-: ") for c in cells): continue
        rows.append(cells)
    return rows

def source_ids(cell):
    ids=re.findall(r"`([^`]+)`",cell)
    if not ids: raise ValueError(f"missing source milestone id: {cell}")
    return ids

def year_bounds(ref):
    m=re.findall(r"(?<!\d)(\d{4})(s?)",ref)
    if not m: return None,None,"UNDATED"
    start=int(m[0][0]); end=int(m[-1][0])+(9 if m[-1][1] else 0)
    precision="APPROX_YEAR" if "c." in ref and len(m)==1 else "APPROX_RANGE" if "c." in ref else "DECADE_OR_RANGE" if any(d for _,d in m) else "RANGE" if ("–" in ref or "-" in ref) else "EXACT_YEAR"
    return start,end,precision

def make_row(mid,family,kind,authority,epistemic,period,capability,source_section,order,id_origin="SOURCE",gate=None,basis=None,notes=None,aliases=None):
    start,end,precision=year_bounds(period)
    return {"milestone_id":mid,"id_origin":id_origin,"family":family,"timeline_kind":kind,"authority_class":authority,"epistemic_status":epistemic,"reference_period":period,"start_year":start,"end_year":end,"temporal_precision":precision,"capability_change_md":capability,"threshold_gate_md":gate,"basis_uncertainty_md":basis,"source_section":source_section,"sort_order":order,"notes_md":notes,"aliases":aliases or []}

MILESTONE_FIELDS=("milestone_id","id_origin","family","timeline_kind","authority_class","epistemic_status","reference_period","start_year","end_year","temporal_precision","capability_change_md","threshold_gate_md","basis_uncertainty_md","source_section","sort_order","notes_md")

def record_view(row):
    return {key:row[key] for key in MILESTONE_FIELDS}

def parse_milestones():
    canon=CANON_PATH.read_text(encoding="utf-8"); tech=TECH_PATH.read_text(encoding="utf-8")
    cr=table_rows(section(canon,"## 2.1 Technological chronology","## 2.2 Frontier scale"))
    mr=table_rows(section(tech,"## 5. FICTIONAL CANON COMPARATOR — chronology preserved, never a rollout target","### 5.1 SELECTED MODERATE *fictional physics* scenario anchors"))
    if len(cr)!=18 or len(mr)!=EXPECTED["CANON_HISTORY"]: raise ValueError(f"canon/comparator row mismatch: {len(cr)} / {len(mr)}")
    canon_by_period={md_plain(c[0]):c for c in cr}
    rows=[]; order=0; used=set()
    for m in mr:
        order+=1; ids=source_ids(m[0]); mp=md_plain(m[1])
        if mp not in canon_by_period: raise ValueError(f"comparator period absent from CANON I: {mp}")
        c=canon_by_period[mp]; used.add(mp)
        rows.append(make_row(ids[0],ids[0].split("-",1)[0],"CANON_HISTORY","GOVERNING_CANON","CANON_HISTORY",mp,c[1],"CANON I v2.4 §2.1",order,notes=m[2],aliases=ids[1:]))
    if used!=set(canon_by_period): raise ValueError("not every CANON I chronology row received a stable timeline ID")
    moderate=table_rows(section(tech,"## 4. SELECTED MODERATE SCENARIO — dated capability thresholds","### 4.1 Synthetic-person legal recognition: separate social scenario, NOT a technology threshold"))
    if len(moderate)!=EXPECTED["MODERATE_SCENARIO_ANCHOR"]: raise ValueError(f"moderate row mismatch: {len(moderate)}")
    for m in moderate:
        order+=1; ids=source_ids(m[0])
        rows.append(make_row(ids[0],ids[0].split("-",1)[0],"MODERATE_SCENARIO_ANCHOR","PROVISIONAL_SIMULATION_SCAFFOLD","AUTHOR_SCENARIO_MODERATE",md_plain(m[1]),m[2],"Technology Timeline §4",order,gate=m[3],basis=m[4]))

    social=section(tech,"### 4.1 Synthetic-person legal recognition: separate social scenario, NOT a technology threshold","### 4.2 Institutional access and research: deliberately no universal calendar year")
    social_line=next(line for line in social.splitlines() if line.startswith("**2090"))
    order+=1
    rows.append(make_row("SOC-MOD-SYNTH-LEGAL-RECOGNITION","SOC","SOCIAL_SCENARIO_ANCHOR","PROVISIONAL_SIMULATION_SCAFFOLD","AUTHOR_SCENARIO_MODERATE","2090",social_line,"Technology Timeline §4.1",order,id_origin="PROJECTION_GENERATED",notes="Projection-generated stable ID; source defines no milestone ID."))
    physics=table_rows(section(tech,"### 5.1 SELECTED MODERATE *fictional physics* scenario anchors","## 6. Minimal dependency and agent-decision contract"))
    if len(physics)!=EXPECTED["FICTIONAL_PHYSICS_SCENARIO_ANCHOR"]: raise ValueError(f"fictional physics row mismatch: {len(physics)}")
    for p in physics:
        order+=1; ids=source_ids(p[0])
        rows.append(make_row(ids[0],"SPEC","FICTIONAL_PHYSICS_SCENARIO_ANCHOR","PROVISIONAL_SIMULATION_SCAFFOLD","SPECULATIVE_FICTION",md_plain(p[1]),p[2],"Technology Timeline §5.1",order,gate=p[3]))
    return rows

RULES={
 "DATE_DOES_NOT_UNLOCK":"The date alone does **not** unlock a technology, create capacity, give every agent access, establish profitability for another process, cause migration or colonize a location.",
 "FOUR_TECH_STATES":"Keep four separate states: `knowledge_or_demonstration`, `reliable_operational_design`, `installed_local_capacity`, `actor_access_and_adoption`.",
 "CANON_COMPARATOR_NOT_DESTINATION":"Existing canon is a **comparator**, not a destination.",
 "UNKNOWN_NOT_ZERO":"Missing quantities remain `UNKNOWN` / null, not zero.",
 "SITE_SPECIFIC":"Site specificity matters: a proven process at one site creates transferable knowledge, not capacity at other sites.",
}

def build_manifest():
    tech=TECH_PATH.read_text(encoding="utf-8")
    for key,rule in RULES.items():
        if rule not in tech: raise ValueError(f"interpretation rule drift: {key}")
    rows=parse_milestones(); counts={}
    for row in rows: counts[row["timeline_kind"]]=counts.get(row["timeline_kind"],0)+1
    if counts!=EXPECTED: raise ValueError(f"timeline counts drifted: {counts}")
    sources={
      "canon":{"path":str(CANON_PATH.relative_to(ROOT)),"sha256":sha256(CANON_PATH),"bytes":CANON_PATH.stat().st_size},
      "technology":{"path":str(TECH_PATH.relative_to(ROOT)),"sha256":sha256(TECH_PATH),"bytes":TECH_PATH.stat().st_size},
    }
    semantic_payload={"counts":counts,"rules":RULES,"authority_classes":sorted({r["authority_class"] for r in rows})}
    semantic_sha=hashlib.sha256(json.dumps(semantic_payload,sort_keys=True).encode()).hexdigest()
    projection_payload=[record_view(r) for r in rows]
    projection_sha=hashlib.sha256(json.dumps(projection_payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    contract_payload={"schema_revision":MIGRATION_PATH.stem,"migration_sha256":sha256(MIGRATION_PATH),"sources":sources,"milestones":[(r["milestone_id"],r["timeline_kind"],r["authority_class"]) for r in rows]}
    contract_sha=hashlib.sha256(json.dumps(contract_payload,sort_keys=True).encode()).hexdigest()
    manifest={"schema":"loom-timeline-postgres-projection-v1","source_authority_main_sha":SOURCE_AUTHORITY_SHA,"snapshot_id":f"timeline-v0-1-{contract_sha[:12]}-20260925","semantic_sha256":semantic_sha,"contract_sha256":contract_sha,"projection_sha256":projection_sha,"sources":sources,"counts":counts,"total_milestones":len(rows),"interpretation_rule_count":len(RULES)}
    MANIFEST_PATH.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest

def migrate(database):
    for path in sorted((ROOT/"data/postgres/migrations").glob("[0-9][0-9][0-9]_*.sql")):
        revision=path.stem; digest=sha256(path)
        exists=psql(database,"SELECT to_regclass('loom_control.schema_migration') IS NOT NULL")
        prior=psql(database,f"SELECT script_sha256 FROM loom_control.schema_migration WHERE revision={sqlq(revision)}") if exists=="t" else ""
        if prior:
            if prior!=digest: raise ValueError(f"applied migration changed: {revision}")
            continue
        psql(database,f"INSERT INTO loom_control.schema_migration(revision,script_sha256) VALUES ({sqlq(revision)},{sqlq(digest)})",file=path)

def insert_projection(database):
    manifest=build_manifest(); migrate(database); sid=manifest["snapshot_id"]
    existing=psql(database,f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={sqlq(sid)}")
    if existing:
        verify(database,manifest)
        return {"status":"IDEMPOTENT_EXISTING_SNAPSHOT","snapshot_id":sid,"state":existing}
    rows=parse_milestones(); consumer=git_head(); query_sha=sha256(Path(__file__))
    sem=manifest["semantic_sha256"]; contract=manifest["contract_sha256"]
    canon_sha=manifest["sources"]["canon"]["sha256"]; tech_sha=manifest["sources"]["technology"]["sha256"]
    sql=["BEGIN;"]
    sql.append(f"INSERT INTO loom_control.semantic_version(semantic_sha256,source_path,source_git_commit) VALUES ({sqlq(sem)},{sqlq('canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md + docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md')},{sqlq(SOURCE_AUTHORITY_SHA)});")
    sql.append(f"INSERT INTO loom_control.snapshot(snapshot_id,consumer_git_commit,consumer_query_sha256,contract_sha256,semantic_sha256,state) VALUES ({sqlq(sid)},{sqlq(consumer)},{sqlq(query_sha)},{sqlq(contract)},{sqlq(sem)},'CANDIDATE');")
    for key,role in (("canon","GOVERNING_TIMELINE_CANON"),("technology","PROVISIONAL_TIMELINE_SCAFFOLD")):
        src=manifest["sources"][key]
        sql.append(f"INSERT INTO loom_control.source_artifact(artifact_sha256,source_role,source_path,byte_count,source_git_commit,retained_location) VALUES ({sqlq(src['sha256'])},{sqlq(role)},{sqlq(src['path'])},{src['bytes']},{sqlq(SOURCE_AUTHORITY_SHA)},{sqlq(src['path'])}) ON CONFLICT (artifact_sha256) DO NOTHING;")
        sql.append(f"INSERT INTO loom_control.snapshot_source(snapshot_id,artifact_sha256,source_role) VALUES ({sqlq(sid)},{sqlq(src['sha256'])},{sqlq(role)});")
    for row in rows:
        vals=[sid,row["milestone_id"],row["id_origin"],row["family"],row["timeline_kind"],row["authority_class"],row["epistemic_status"],row["reference_period"],row["start_year"],row["end_year"],row["temporal_precision"],row["capability_change_md"],row["threshold_gate_md"],row["basis_uncertainty_md"],row["source_section"],row["sort_order"],row["notes_md"]]
        sql.append("INSERT INTO loom_timeline.milestone VALUES ("+",".join(sqlq(v) for v in vals)+");")
        for alias in row["aliases"]:
            sql.append(f"INSERT INTO loom_timeline.milestone_alias VALUES ({sqlq(sid)},{sqlq(row['milestone_id'])},{sqlq(alias)});")
        if row["timeline_kind"]=="CANON_HISTORY":
            sql.append(f"INSERT INTO loom_timeline.milestone_source VALUES ({sqlq(sid)},{sqlq(row['milestone_id'])},{sqlq(canon_sha)},'GOVERNING_CONTENT',{sqlq(SOURCE_AUTHORITY_SHA)});")
            sql.append(f"INSERT INTO loom_timeline.milestone_source VALUES ({sqlq(sid)},{sqlq(row['milestone_id'])},{sqlq(tech_sha)},'STABLE_ID_MAPPING',{sqlq(SOURCE_AUTHORITY_SHA)});")
        else:
            sql.append(f"INSERT INTO loom_timeline.milestone_source VALUES ({sqlq(sid)},{sqlq(row['milestone_id'])},{sqlq(tech_sha)},'SCENARIO_DEFINITION',{sqlq(SOURCE_AUTHORITY_SHA)});")
    for key,rule in RULES.items():
        sql.append(f"INSERT INTO loom_timeline.interpretation_rule VALUES ({sqlq(sid)},{sqlq(key)},{sqlq(rule)},{sqlq(tech_sha)},{sqlq('Technology Timeline §§1,4')});")
    sql.append("COMMIT;")
    psql(database,"\n".join(sql))
    verify(database,manifest,allow_candidate=True)
    psql(database,f"UPDATE loom_control.snapshot SET state='VALIDATED' WHERE snapshot_id={sqlq(sid)} AND state='CANDIDATE'")
    verify(database,manifest)
    return {"status":"IMPORTED_AND_VALIDATED","snapshot_id":sid,"consumer_git_commit":consumer}

def verify(database,manifest=None,allow_candidate=False):
    manifest=manifest or json.loads(MANIFEST_PATH.read_text(encoding="utf-8")); sid=manifest["snapshot_id"]
    state=psql(database,f"SELECT state FROM loom_control.snapshot WHERE snapshot_id={sqlq(sid)}")
    allowed={"VALIDATED","CANDIDATE"} if allow_candidate else {"VALIDATED"}
    if state not in allowed: raise ValueError(f"unexpected snapshot state: {state!r}")
    counts={kind:int(psql(database,f"SELECT count(*) FROM loom_timeline.milestone WHERE snapshot_id={sqlq(sid)} AND timeline_kind={sqlq(kind)}")) for kind in EXPECTED}
    if counts!=EXPECTED: raise ValueError(f"database timeline counts mismatch: {counts}")
    expected_rows=[record_view(r) for r in parse_milestones()]
    actual_rows=json.loads(psql(database,f"SELECT json_agg(to_jsonb(m)-'snapshot_id' ORDER BY sort_order)::text FROM loom_timeline.milestone m WHERE snapshot_id={sqlq(sid)}"))
    if actual_rows!=expected_rows: raise ValueError("full milestone round-trip mismatch")
    expected_aliases=sorted([{"milestone_id":r["milestone_id"],"alias_id":a} for r in parse_milestones() for a in r["aliases"]],key=lambda x:x["alias_id"])
    actual_aliases=json.loads(psql(database,f"SELECT COALESCE(json_agg(json_build_object('milestone_id',milestone_id,'alias_id',alias_id) ORDER BY alias_id),'[]'::json)::text FROM loom_timeline.milestone_alias WHERE snapshot_id={sqlq(sid)}"))
    if actual_aliases!=expected_aliases: raise ValueError("milestone alias round-trip mismatch")
    actual_rules=json.loads(psql(database,f"SELECT COALESCE(json_object_agg(rule_key,rule_text_md),'{{}}'::json)::text FROM loom_timeline.interpretation_rule WHERE snapshot_id={sqlq(sid)}"))
    if actual_rules!=RULES: raise ValueError("interpretation-rule round-trip mismatch")
    bad=int(psql(database,f"SELECT count(*) FROM loom_timeline.milestone WHERE snapshot_id={sqlq(sid)} AND ((timeline_kind='CANON_HISTORY') <> (authority_class='GOVERNING_CANON'))"))
    if bad: raise ValueError(f"authority-class contamination: {bad}")
    rc=int(psql(database,f"SELECT count(*) FROM loom_timeline.interpretation_rule WHERE snapshot_id={sqlq(sid)}"))
    if rc!=len(RULES): raise ValueError(f"interpretation-rule count mismatch: {rc}")
    torch=psql(database,f"SELECT authority_class FROM loom_timeline.milestone WHERE snapshot_id={sqlq(sid)} AND milestone_id='TRN-2100-TORCH-EMERGE'")
    metric=psql(database,f"SELECT authority_class FROM loom_timeline.milestone WHERE snapshot_id={sqlq(sid)} AND milestone_id='SPEC-MOD-METRIC-SHIP'")
    if torch!="GOVERNING_CANON" or metric!="PROVISIONAL_SIMULATION_SCAFFOLD": raise ValueError(f"authority sentinel failure: torch={torch}, metric={metric}")
    return {"snapshot_id":sid,"state":state,"counts":counts,"rules":rc}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("prepare","migrate","import","verify"))
    parser.add_argument("--database",default="loom_dev")
    args=parser.parse_args()
    if args.command=="prepare": print(json.dumps(build_manifest(),indent=2,sort_keys=True))
    elif args.command=="migrate":
        migrate(args.database); print(json.dumps({"status":"MIGRATED","database":args.database}))
    elif args.command=="import": print(json.dumps(insert_projection(args.database),indent=2,sort_keys=True))
    else: print(json.dumps(verify(args.database),indent=2,sort_keys=True))

if __name__=="__main__": main()
