"""Body-neutral narrative adapter over typed fact authority only.

Qualitative value_text is rendered verbatim; missing values never become zero.
Observations, models, and ledger liens are not rewritten into fact predicates.
"""
import sqlite3

def narrate(db,body_id):
 c=sqlite3.connect(db)
 row=c.execute('select canonical_name from body where body_id=?',(body_id,)).fetchone()
 if row is None:raise KeyError(f'unknown body_id: {body_id}')
 lines=[f'{row[0]} has candidate factual records:']
 for prop,value,lo,hi,unit,evidence,text in c.execute('select property_code,value_numeric,value_min,value_max,canonical_unit,evidence_class,value_text from fact where body_id=? order by fact_id',(body_id,)):
  if value is not None:value_text=str(value)
  elif lo is not None and hi is not None:value_text=f'range {lo}–{hi}'
  elif text is not None:value_text=text
  else:value_text='unknown (no scalar or range asserted)'
  lines.append(f'- {prop}: {value_text} {unit or ""} [{evidence}].')
 lines.append('Model products and observations retain their original class and scope; no preferred fact is selected.')
 c.close();return '\n'.join(lines)
