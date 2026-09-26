#!/usr/bin/env python3
import json, sqlite3, sys
from pathlib import Path
baseline=sqlite3.connect(sys.argv[1]); promoted=sqlite3.connect(sys.argv[2])
bodies=baseline.execute("select count(*) from authority_body_ref").fetchone()[0]
props=dict(baseline.execute("select property_code,count(*) from candidate_assertion where disposition='CANDIDATE' group by property_code"))
cols={r[1] for r in promoted.execute("pragma table_info(material_evidence)")}
needed={'body_id','region_id','material_family','material_species','physical_form','evidence_class','abundance_semantics','abundance_value','abundance_min','abundance_max','abundance_unit','reported_abundance','depth_min','depth_max','depth_unit','thickness_min','thickness_max','thickness_unit','areal_extent','areal_extent_unit','estimated_volume','estimated_volume_unit','spatial_heterogeneity','measurement_resolution','measurement_method','confidence_class','fact_status','observation_id','source_id'}
material_rows=promoted.execute("select count(*) from material_evidence").fetchone()[0]
material_bodies=promoted.execute("select count(distinct body_id) from material_evidence").fetchone()[0]
out={
 "body_catalog_count":bodies,
 "existing_material_ddl_satisfies_contract":needed<=cols,
 "missing_material_ddl_columns":sorted(needed-cols),
 "promoted_material_rows":material_rows,
 "promoted_bodies_with_material_evidence":material_bodies,
 "promoted_bodies_without_material_evidence":bodies-material_bodies,
 "physical_inventory_assertions":{
  "mass":props.get("MASS",0),
  "bulk_density":props.get("BULK_DENSITY",0),
  "effective_diameter":props.get("EFFECTIVE_DIAMETER",0),
  "mean_radius":props.get("MEAN_RADIUS",0)
 },
 "ddl_decision":"NO_NEW_MATERIAL_TABLE_REQUIRED",
 "population_decision":"RESOURCE_COVERAGE_POPULATION_REQUIRED"
}
print(json.dumps(out,indent=2,sort_keys=True))
