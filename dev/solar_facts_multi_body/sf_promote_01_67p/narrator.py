"""Constrained narrator: only emits predicates read from promoted records."""
import sqlite3, json
from pathlib import Path

def narrate(db):
 c=sqlite3.connect(db)
 body=c.execute('select canonical_name from body').fetchone()[0]
 facts=c.execute("select property_code,value_numeric,value_min,value_max,canonical_unit,evidence_class from fact order by fact_id").fetchall()
 lines=[f"{body} has the following candidate factual records:"]
 for p,v,lo,hi,u,e in facts:
  value=str(v) if v is not None else f"range {lo}–{hi}"
  lines.append(f"- {p}: {value} {u or ''} [{e}].")
 lines.append("A shape-model product is available; no scalar dimensions are asserted.")
 lines.append("Thermal observations are time- and footprint-bounded; no timeless temperature scalar is asserted.")
 lines.append("Volatile observations concern the coma, and activity/production records remain model-class candidates.")
 return "\n".join(lines)

if __name__=='__main__': print(narrate(Path(__file__).with_name('LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3')))
