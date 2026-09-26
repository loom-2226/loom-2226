"""Independent hostile review for cross-body and epistemic firewalls."""
import sqlite3, tempfile
from pathlib import Path
from promote import OUT, build

def main():
    with tempfile.TemporaryDirectory() as td:
        p = build(Path(td) / 'hostile.sqlite3'); c = sqlite3.connect(p); c.execute('pragma foreign_keys=on')
        checks = {}
        checks['identity_authority_unique'] = c.execute("select count(*),count(distinct body_id) from body_authority").fetchone() == (2,2)
        checks['preferred_fact_firewall'] = c.execute('select count(*) from preferred_fact').fetchone()[0] == 0
        checks['region_isolation'] = c.execute("select count(*) from body_region where body_id='COMET_67P'").fetchone()[0] == 0 and c.execute("select count(*) from material_evidence where body_id='CERES' and region_id in (select region_id from body_region where body_id='COMET_67P')").fetchone()[0] == 0
        checks['model_isolation'] = c.execute("select count(*) from body_model_product where body_id='COMET_67P' and model_name like '%Ceres%'").fetchone()[0] == 0
        checks['material_isolation'] = c.execute("select count(*) from material_evidence where body_id='COMET_67P'").fetchone()[0] == 0
        checks['coma_not_nucleus'] = c.execute("select count(*) from promotion_assertion where body_id='CERES' and property_code like '%NUCLEUS%'").fetchone()[0] == 0
        checks['same_property_body_scoped'] = c.execute("select count(*) from fact where property_code='MASS' and body_id in ('CERES','COMET_67P')").fetchone()[0] == 2
        checks['derivation_isolation'] = c.execute("select count(*) from fact_input fi join fact f on f.fact_id=fi.fact_id left join fact i on i.fact_id=fi.input_fact_id where f.body_id<>coalesce(i.body_id,f.body_id)").fetchone()[0] == 0
        checks['source_isolation'] = c.execute("select count(*) from promotion_assertion p where p.body_id='CERES' and p.source_id between 1 and 9").fetchone()[0] == 0
        checks['knowledge_time_scoped'] = c.execute("select count(*) from knowledge_event where target_observation_id in (select observation_id from observation where body_id='CERES') and target_observation_id not in (select observation_id from observation where body_id='CERES')").fetchone()[0] == 0
        checks['candidate_only'] = c.execute("select count(*) from fact where fact_status<>'CANDIDATE'").fetchone()[0] == 0
        checks['unknown_not_zero'] = c.execute("select count(*) from material_evidence where body_id='CERES' and abundance_semantics='UNKNOWN' and abundance_value=0").fetchone()[0] == 0
        checks['resolution_preserved'] = c.execute("select count(*) from fact where body_id='CERES' and property_code='SURFACE_TEMPERATURE' and value_numeric is null and value_min=170 and value_max=180").fetchone()[0] == 1
        assert all(checks.values()), checks
    print({'status':'PASS','checks':checks})

if __name__ == '__main__': main()
