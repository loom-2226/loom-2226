"""Body-neutral truthful narrative adapter: reads predicates, never invents them."""
import sqlite3

def narrate(db, body_id):
    c = sqlite3.connect(db)
    name = c.execute('select canonical_name from body where body_id=?',(body_id,)).fetchone()[0]
    lines = [f'{name} has candidate factual records:']
    for prop, value, lo, hi, unit, evidence in c.execute('select property_code,value_numeric,value_min,value_max,canonical_unit,evidence_class from fact where body_id=? order by fact_id',(body_id,)):
        value_text = str(value) if value is not None else f'range {lo}–{hi}'
        lines.append(f'- {prop}: {value_text} {unit or ""} [{evidence}].')
    lines.append('Model products and observations retain their original class and scope; no preferred fact is selected.')
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys
    print(narrate(sys.argv[1], sys.argv[2]))
