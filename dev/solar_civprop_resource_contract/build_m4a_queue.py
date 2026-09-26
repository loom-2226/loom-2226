#!/usr/bin/env python3
import csv,json,sqlite3,sys
from pathlib import Path
manifest=json.loads(Path(sys.argv[1]).read_text())
con=sqlite3.connect(sys.argv[2])
included=set(manifest["eligibility"]["included_body_classes"])
families=[q["resource_family"] for q in manifest["required_questions"]]
rows=con.execute("select body_id,canonical_name,body_class from authority_body_ref order by body_id").fetchall()
w=csv.writer(sys.stdout); w.writerow(["body_id","canonical_name","body_class","resource_family","initial_disposition"])
for bid,name,cls in rows:
 if cls in included:
  for fam in families: w.writerow([bid,name,cls,fam,"UNASSESSED"])
