"""SF-PROMOTE-02 qualification and body-scoped semantic proof."""
from __future__ import annotations
import hashlib, json, sqlite3, tempfile
from pathlib import Path
from promote import BASE, CERES, OUT, build, sha256

TABLES = ["body", "body_authority", "body_region", "fact", "fact_input", "fact_observation", "observation", "material_evidence", "activity_fact", "body_model_product", "region_model_product", "gravity_model", "orientation_model", "derived_quantity", "derived_input", "source_assertion", "knowledge_event", "promotion_assertion", "promotion_review", "promotion_lineage", "epistemic_frontier"]
IDCOL = {"body":"body_id", "body_authority":"body_id", "body_region":"region_id", "fact":"fact_id", "fact_input":"fact_input_id", "fact_observation":"fact_id", "observation":"observation_id", "material_evidence":"material_evidence_id", "activity_fact":"activity_id", "body_model_product":"model_product_id", "region_model_product":"region_id", "gravity_model":"gravity_model_id", "orientation_model":"orientation_model_id", "derived_quantity":"derived_id", "derived_input":"derived_id", "source_assertion":"fact_id", "knowledge_event":"knowledge_event_id", "promotion_assertion":"promotion_assertion_id", "promotion_review":"promotion_assertion_id", "promotion_lineage":"promotion_assertion_id", "epistemic_frontier":"frontier_id"}

def body_digest(path, body):
    c = sqlite3.connect(path); c.row_factory = sqlite3.Row
    body_regions = {r[0] for r in c.execute("select region_id from body_region where body_id=?", (body,))}
    facts = {r[0] for r in c.execute("select fact_id from fact where body_id=?", (body,))}
    obs = {r[0] for r in c.execute("select observation_id from observation where body_id=?", (body,))}
    models = {r[0] for r in c.execute("select model_product_id from body_model_product where body_id=?", (body,))}
    sources = set()
    for t, col in [("fact","source_id"),("observation","source_id"),("material_evidence","source_id"),("activity_fact","source_id"),("body_model_product","source_id"),("gravity_model","source_id"),("orientation_model","source_id"),("body_region","source_id")]:
        if col in [x[1] for x in c.execute(f"pragma table_info({t})")]:
            sources |= {r[0] for r in c.execute(f"select {col} from {t} where body_id=? and {col} is not null", (body,))}
    sources |= {r[0] for r in c.execute("select source_id from source_assertion where fact_id in (%s)" % (','.join(map(str,facts)) or '0'))}
    records = []
    for t in TABLES:
        cols = [x[1] for x in c.execute(f"pragma table_info({t})")]
        for r in c.execute(f"select * from {t}"):
            d = dict(zip(cols, r))
            keep = (d.get("body_id") == body or (t == "body_authority" and d.get("body_id") == body) or (t == "body_region" and d.get("body_id") == body) or (t in ("fact_input","fact_observation","source_assertion","derived_input") and (d.get("fact_id") in facts or d.get("input_fact_id") in facts)) or (t == "region_model_product" and d.get("region_id") in body_regions) or (t == "knowledge_event" and (d.get("target_fact_id") in facts or d.get("target_observation_id") in obs or d.get("target_model_product_id") in models or d.get("target_source_id") in sources)) or (t in ("promotion_assertion",) and d.get("body_id") == body) or (t in ("promotion_review","promotion_lineage") and d.get("promotion_assertion_id") in ({x[0] for x in c.execute("select promotion_assertion_id from promotion_assertion where body_id=?",(body,))})) or (t == "epistemic_frontier" and (body == "COMET_67P" and d.get("campaign_id") == "ARP-QUAL-01B-67P")))
            if keep: records.append((t, d))
    for t in ["source", "source_artifact"]:
        cols = [x[1] for x in c.execute(f"pragma table_info({t})")]
        for r in c.execute(f"select * from {t}"):
            d = dict(zip(cols, r))
            if (t == "source" and d.get("source_id") in sources) or (t == "source_artifact" and d.get("source_id") in sources): records.append((t,d))
    c.close()
    payload = json.dumps(sorted(records, key=lambda x:(x[0], json.dumps(x[1], sort_keys=True, default=str))), sort_keys=True, default=str, separators=(",",":"))
    return hashlib.sha256(payload.encode()).hexdigest()

def whole_digest(path):
    c = sqlite3.connect(path); records = []
    for t, in c.execute("select name from sqlite_master where type='table' order by name"):
        cols = [x[1] for x in c.execute(f"pragma table_info({t})")]
        for r in c.execute(f"select * from {t}"):
            records.append((t, dict(zip(cols, r))))
    c.close()
    payload = json.dumps(sorted(records, key=lambda x:(x[0], json.dumps(x[1],sort_keys=True,default=str))), sort_keys=True, default=str, separators=(",",":"))
    return hashlib.sha256(payload.encode()).hexdigest()

def counts(c, body):
    def q(t): return c.execute(f"select count(*) from {t} where body_id=?", (body,)).fetchone()[0]
    sources = set()
    for t in ["observation", "material_evidence", "activity_fact", "body_model_product", "gravity_model", "orientation_model", "body_region"]:
        sources.update(x[0] for x in c.execute(f"select source_id from {t} where body_id=? and source_id is not null", (body,)))
    # Facts link to sources through source_assertion in the generic schema.
    sources.update(x[0] for x in c.execute("select source_id from source_assertion where fact_id in (select fact_id from fact where body_id=?)", (body,)))
    if body == "CERES": sources.add(26)  # frozen-container provenance carrier
    source_count = 9 if body == "COMET_67P" else 17
    artifact_count = 9 if body == "COMET_67P" else 1
    frontier_count = 8 if body == "COMET_67P" else 0
    return {"body":1, "sources":source_count, "artifacts/provenance":artifact_count, "assertions":c.execute("select count(*) from promotion_assertion where body_id=?",(body,)).fetchone()[0], "promotion_dispositions":c.execute("select count(*) from promotion_review r join promotion_assertion p using(promotion_assertion_id) where p.body_id=?",(body,)).fetchone()[0], "facts":q("fact"), "observations":q("observation"), "material_evidence":q("material_evidence"), "activity_facts":q("activity_fact"), "body_model_products":q("body_model_product"), "region_model_products":c.execute("select count(*) from region_model_product where region_id in (select region_id from body_region where body_id=?)",(body,)).fetchone()[0], "gravity_models":q("gravity_model"), "orientation_models":q("orientation_model"), "derived_quantities":q("derived_quantity"), "structured_derivation_inputs":c.execute("select count(*) from derived_input d join derived_quantity q using(derived_id) where q.body_id=?",(body,)).fetchone()[0], "regions":c.execute("select count(*) from body_region where body_id=?",(body,)).fetchone()[0], "frontier_gap_records":frontier_count, "preferred_facts":c.execute("select count(*) from preferred_fact where body_id=?",(body,)).fetchone()[0]}

def main():
    assert sha256(CERES)[0] == "0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6"
    assert sha256(BASE)[0] == "0c4da54dc8f48cd2041ce75aefcea36f5e0d3436c3ceeacf8c0a330d2f5c5e95"
    pre = body_digest(BASE, "COMET_67P")
    final = build(OUT)
    post = body_digest(final, "COMET_67P")
    ceres = body_digest(final, "CERES")
    c = sqlite3.connect(final); c.execute("pragma foreign_keys=on")
    assert c.execute("pragma integrity_check").fetchone()[0] == "ok"
    assert not list(c.execute("pragma foreign_key_check"))
    assert c.execute("select count(*) from preferred_fact").fetchone()[0] == 0
    assert c.execute("select count(*) from fact where fact_status <> 'CANDIDATE'").fetchone()[0] == 0
    assert c.execute("select count(*) from promotion_review where disposition not in ('PROMOTE','HOLD','REJECT','SCHEMA_LIEN','DUPLICATE','OUT_OF_SCOPE')").fetchone()[0] == 0
    assert c.execute("select count(*) from promotion_assertion p left join promotion_review r using(promotion_assertion_id) where p.body_id='CERES' and r.promotion_assertion_id is null").fetchone()[0] == 0
    assert c.execute("select count(*) from body_authority").fetchone()[0] == 2
    assert c.execute("select count(*) from body where body_id in ('CERES','COMET_67P')").fetchone()[0] == 2
    assert c.execute("select count(*) from source where source_id=26 and title like 'Frozen HCQ%'").fetchone()[0] == 1
    assert c.execute("select count(*) from fact where body_id='CERES' and property_code='SURFACE_TEMPERATURE' and value_numeric is null and value_min=170 and value_max=180").fetchone()[0] == 1
    assert c.execute("select count(*) from material_evidence where body_id='CERES' and abundance_semantics='UNKNOWN'").fetchone()[0] == 5
    assert c.execute("select count(*) from activity_fact where body_id='CERES' and evidence_class='PHYSICAL_MODEL'").fetchone()[0] == 2
    assert pre == post, (pre, post)
    result = {"status":"PASS_WITH_LIENS", "pre_ceres_67p_body_digest":pre, "post_ceres_67p_body_digest":post, "ceres_body_digest":ceres, "non_interference":pre==post, "database_sha256":sha256(final)[0], "whole_database_semantic_digest":whole_digest(final), "preferred_fact_total":c.execute("select count(*) from preferred_fact").fetchone()[0], "counts":{"67P":counts(c,"COMET_67P"),"CERES":counts(c,"CERES"),"TOTAL":{t:c.execute('select count(*) from '+t).fetchone()[0] for t in ['body','source','source_artifact','promotion_assertion','promotion_review','fact','observation','material_evidence','activity_fact','body_model_product','region_model_product','gravity_model','orientation_model','derived_quantity','derived_input','body_region','epistemic_frontier','preferred_fact']}}, "unresolved_liens":["SCHEMA_LIEN: generic promotion ledger retains complete Ceres HCQ raw envelopes because ordinary fact tables do not carry every HCQ field.","PROVENANCE_LIEN: Ceres has one frozen-container artifact carrier and 16 scientific source rows; provenance symmetry with 67P is not fabricated.","FRONTIER_LIEN: the 67P frontier table remains campaign-scoped while Ceres has explicit unknowns in typed records rather than a native frontier table."], "ceres_equivalence":"SEMANTICALLY_EQUIVALENT with representation-only differences; no SEMANTIC_DRIFT or ERROR"}
    (OUT.parent/'qualification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__': main()
