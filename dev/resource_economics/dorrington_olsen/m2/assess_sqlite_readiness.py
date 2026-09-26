#!/usr/bin/env python3
import json, sqlite3, sys
from pathlib import Path
db=Path(sys.argv[1])
con=sqlite3.connect(db)
props={r[0]:{"assertions":r[1],"candidate":r[2]} for r in con.execute(
 "select property_code,count(*),sum(disposition='CANDIDATE') from candidate_assertion group by property_code")}
bodies=con.execute("select count(*) from authority_body_ref").fetchone()[0]
def n(*names): return sum(props.get(x,{}).get("candidate",0) or 0 for x in names)
out={
 "database":str(db),"bodies":bodies,
 "empirical_object_lanes":{
  "mass":{"candidate_assertions":n("MASS"),"assessment":"SPARSE"},
  "size_shape":{"candidate_assertions":n("EFFECTIVE_DIAMETER","MEAN_RADIUS","TRIAXIAL_DIMENSIONS","TRIAXIAL_RADII"),"assessment":"PARTIAL"},
  "bulk_density":{"candidate_assertions":n("BULK_DENSITY"),"assessment":"PARTIAL"},
  "taxonomy":{"candidate_assertions":n("SPECTRAL_CLASS_SMASSII","SPECTRAL_CLASS_THOLEN"),"assessment":"PARTIAL"},
  "rotation":{"candidate_assertions":n("ROTATION_PERIOD"),"assessment":"PARTIAL"},
  "resource_presence_abundance":{"candidate_assertions":0,"assessment":"BLOCKING_FOR_RESOURCE_SPECIFIC_CIVPROP"},
  "surface_geotechnical":{"candidate_assertions":0,"assessment":"UNKNOWN_IN_BULK_BASELINE"}
 },
 "conclusion":"Current bulk Solar Facts is enough to identify and physically screen some objects, but not enough to drive resource-specific CIVPROP. The principal missing empirical bridge is target-specific material/resource evidence (presence, abundance, scope, uncertainty), followed by mining-relevant surface/geotechnical evidence. Delta-v and flight time belong to Navigator, not Solar Facts."
}
print(json.dumps(out,indent=2))
