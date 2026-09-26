#!/usr/bin/env python3
"""Deterministic pairwise comparison for Solar Baseline candidate assertions.

The input database is opened read-only. Results are written to a separate
SQLite ledger; assertions and preference state are never updated.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

ENGINE_VERSION = "solar-baseline-01r-reconcile-v1.0"
CLASSIFICATIONS = (
    "EXACT_EQUIVALENT", "UNIT_EQUIVALENT", "PRECISION_EQUIVALENT",
    "AGREES_WITHIN_UNCERTAINTY", "LIMIT_COMPATIBLE", "RANGE_COMPATIBLE",
    "DISTINCT_BUT_COMPATIBLE", "CONFLICT", "LIMIT_CONFLICT",
    "SEMANTICALLY_DISTINCT", "INSUFFICIENT_INFORMATION",
    "MODEL_SENTINEL_SUSPECTED", "NOT_COMPARABLE",
)

# Factors map source units to one canonical unit, scoped to a property.
# No radius/diameter or GM/mass conversion is admitted.
UNIT_FACTORS = {
    "ROTATION_PERIOD": {"s": Decimal(1), "sec": Decimal(1), "seconds": Decimal(1),
                         "h": Decimal(3600), "hr": Decimal(3600), "hour": Decimal(3600),
                         "d": Decimal(86400), "day": Decimal(86400)},
    "MEAN_RADIUS": {"m": Decimal(1), "km": Decimal(1000)},
    "EQUATORIAL_RADIUS": {"m": Decimal(1), "km": Decimal(1000)},
    "POLAR_RADIUS": {"m": Decimal(1), "km": Decimal(1000)},
    "EFFECTIVE_DIAMETER": {"m": Decimal(1), "km": Decimal(1000)},
    "GM": {"m^3/s^2": Decimal(1), "km^3/s^2": Decimal(10) ** 9},
    "BULK_DENSITY": {"kg/m^3": Decimal(1), "g/cm^3": Decimal(1000)},
    "POLE_ORIENTATION": {"rad": Decimal(1), "radian": Decimal(1), "deg": Decimal("0.017453292519943295769236907684886")},
    "POLE_RIGHT_ASCENSION_MODEL": {"rad": Decimal(1), "radian": Decimal(1), "deg": Decimal("0.017453292519943295769236907684886")},
    "POLE_DECLINATION_MODEL": {"rad": Decimal(1), "radian": Decimal(1), "deg": Decimal("0.017453292519943295769236907684886")},
}
CANONICAL_UNIT = {"ROTATION_PERIOD": "s", "MEAN_RADIUS": "m", "EQUATORIAL_RADIUS": "m",
                  "POLAR_RADIUS": "m", "EFFECTIVE_DIAMETER": "m", "GM": "m^3/s^2",
                  "BULK_DENSITY": "kg/m^3", "POLE_ORIENTATION": "rad",
                  "POLE_RIGHT_ASCENSION_MODEL": "rad", "POLE_DECLINATION_MODEL": "rad"}


@dataclass(frozen=True)
class Numeric:
    kind: str
    lo: Decimal | None
    hi: Decimal | None
    op: str = ""
    quantum: Decimal | None = None
    approx: bool = False
    lo_open: bool = False
    hi_open: bool = False
    vector: tuple[Decimal,...] | None = None
    uncertainty: Decimal | None = None


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_number(text: str | None) -> Numeric | None:
    """Parse scalar, explicit range, or inequality without discarding bounds."""
    if text is None:
        return None
    s = text.strip().replace("D", "E").replace("d", "e")
    inline_uncertainty=None
    if not (s.startswith("[") and s.endswith("]")):
        s=s.replace(",","")
        pm=re.fullmatch(r"\s*(.+?)\s*(?:±|\\pm|\+/-)\s*(.+?)\s*",s)
        if pm:
            s=pm.group(1).strip()
            try:inline_uncertainty=Decimal(pm.group(2).strip().replace("D","E").replace("d","e"))
            except InvalidOperation:return None
            if inline_uncertainty < 0:return None
    if s.startswith("(") and s.endswith(")"):
        s=s[1:-1].strip()
    approx = bool(re.search(r"(?:~|≈|\babout\b|\bapprox(?:imately)?\b)", s, re.I))
    s = re.sub(r"(?:~|≈|\babout\b|\bapprox(?:imately)?\b)", "", s, flags=re.I).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            values=json.loads(s,parse_float=Decimal,parse_int=Decimal)
            if isinstance(values,list) and values and all(isinstance(x,(int,float,Decimal,str)) and re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?",str(x)) for x in values):
                return Numeric("VECTOR",None,None,approx=approx,vector=tuple(Decimal(str(x)) for x in values))
        except (json.JSONDecodeError,InvalidOperation,TypeError):
            return None
    vector_pattern=r"\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?(?:\s+[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)+\s*"
    if re.fullmatch(vector_pattern,s):
        tokens=re.findall(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?",s)
        return Numeric("VECTOR",None,None,approx=approx,vector=tuple(Decimal(x) for x in tokens))
    s=re.sub(r"\s+\[[^\]]+\]\s*$","",s)
    pat = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
    range_match = re.fullmatch(rf"\s*({pat})\s*(?:\.\.|–|—|\bto\b)\s*({pat})\s*", s, re.I)
    if range_match:
        try:
            lo, hi = Decimal(range_match.group(1)), Decimal(range_match.group(2))
        except InvalidOperation:
            return None
        if lo > hi:
            return None
        return Numeric("RANGE", lo, hi, quantum=None, approx=approx)
    limit = re.fullmatch(rf"\s*(<=|>=|<|>|≤|≥)\s*({pat})\s*", s)
    if limit:
        op, raw = limit.groups()
        op = {"≤": "<=", "≥": ">="}.get(op, op)
        value = Decimal(raw)
        return Numeric("LIMIT", None if op in ("<", "<=") else value,
                       value if op in ("<", "<=") else None, op, approx=approx,
                       lo_open=op==">", hi_open=op=="<")
    scalar = re.fullmatch(rf"\s*({pat})\s*", s)
    if not scalar:
        return None
    raw = scalar.group(1)
    try:
        value = Decimal(raw)
    except InvalidOperation:
        return None
    exponent = Decimal(raw).as_tuple().exponent
    quantum = Decimal(1).scaleb(exponent)
    return Numeric("SCALAR", value, value, quantum=quantum, approx=approx, uncertainty=inline_uncertainty)


def normalize_unit(value: Numeric, unit: str | None, prop: str) -> tuple[Numeric | None, str | None, str]:
    if unit is None:
        return value, None, "UNIT_ABSENT"
    norm = unit.strip().replace("³", "^3").replace("^ 3", "^3").replace(" / ", "/")
    factors = UNIT_FACTORS.get(prop, {})
    # Exact identical units need no registry entry; conversions do.
    canonical = CANONICAL_UNIT.get(prop)
    keymap = {k.casefold(): (k, v) for k, v in factors.items()}
    if norm.casefold() in keymap and canonical:
        matched_unit, factor = keymap[norm.casefold()]
        canonical_factor = next((f for k, f in factors.items() if k.casefold() == canonical.casefold()), None)
        if canonical_factor is None:
            return None, None, "UNIT_REGISTRY_INCOMPLETE"
        scale = factor / canonical_factor
        if value.kind=="VECTOR":
            vec=tuple(x*scale for x in value.vector) if value.vector else None
            return Numeric("VECTOR",None,None,value.op,None,value.approx,value.lo_open,value.hi_open,vec),canonical,("UNIT_ALREADY_CANONICAL" if matched_unit.casefold()==canonical.casefold() else "PROPERTY_SCOPED_UNIT_CONVERSION")
        return Numeric(value.kind, value.lo * scale if value.lo is not None else None,
                       value.hi * scale if value.hi is not None else None, value.op,
                       value.quantum * abs(scale) if value.quantum is not None else None, value.approx,
                       value.lo_open, value.hi_open, None,
                       value.uncertainty * abs(scale) if value.uncertainty is not None else None), canonical, ("UNIT_ALREADY_CANONICAL" if matched_unit.casefold() == canonical.casefold() else "PROPERTY_SCOPED_UNIT_CONVERSION")
    if canonical and norm.casefold() != canonical.casefold() and norm.casefold() in {k.casefold() for k in factors}:
        return None, None, "UNIT_REGISTRY_INCOMPLETE"
    return value, norm, "UNIT_UNCHANGED" if canonical is None or norm.casefold() == canonical.casefold() else "UNIT_UNRECOGNIZED_NO_CONVERSION"


def parse_uncertainty(text: str | None, unit: str | None, prop: str) -> Decimal | None:
    if not text:
        return None
    parsed = parse_number(text)
    if not parsed or parsed.kind != "SCALAR" or parsed.lo is None:
        return None
    converted, _, _ = normalize_unit(parsed, unit, prop)
    return converted.lo if converted and converted.kind == "SCALAR" else None


def _overlap(a: Numeric, b: Numeric) -> bool:
    alo, ahi = a.lo, a.hi
    blo, bhi = b.lo, b.hi
    if ahi is not None and blo is not None and (ahi < blo or (ahi == blo and (a.hi_open or b.lo_open))):
        return False
    if bhi is not None and alo is not None and (bhi < alo or (bhi == alo and (b.hi_open or a.lo_open))):
        return False
    return True


def _numeric_values_equal(a: Numeric, b: Numeric) -> bool:
    if a.kind!=b.kind:
        return False
    if a.kind=="VECTOR":
        return a.vector is not None and a.vector==b.vector
    return a.lo==b.lo and a.hi==b.hi and a.op==b.op and a.uncertainty==b.uncertainty


def normalization_mismatch(assertion: dict) -> bool:
    reported=assertion.get("reported_value")
    normalized=assertion.get("normalized_value")
    if reported is None or normalized is None:
        return False
    rv,nv=parse_number(reported),parse_number(normalized)
    if rv is None and nv is None:
        return False
    if rv is None or nv is None:
        return True
    ru=assertion.get("reported_unit")
    nu=assertion.get("normalized_unit") or ru
    rv,_,_=normalize_unit(rv,ru,assertion["property_code"])
    nv,_,_=normalize_unit(nv,nu,assertion["property_code"])
    return rv is None or nv is None or not _numeric_values_equal(rv,nv)


def compare(a: dict, b: dict) -> dict:
    if a["body_id"] != b["body_id"]:
        return result("NOT_COMPARABLE", "CROSS_BODY_COMPARISON_PROHIBITED", a, b)
    if a["property_code"] != b["property_code"]:
        return result("SEMANTICALLY_DISTINCT", "PROPERTY_CODES_DIFFER", a, b)
    if a.get("identity_held") or b.get("identity_held"):
        return result("NOT_COMPARABLE", "IDENTITY_CROSSWALK_REMAINS_HELD", a, b)
    if normalization_mismatch(a) or normalization_mismatch(b):
        return result("NOT_COMPARABLE", "REPORTED_NORMALIZED_VALUE_MISMATCH", a, b)
    if a.get("epistemic_class") == "PHYSICAL_MODEL" or b.get("epistemic_class") == "PHYSICAL_MODEL":
        if a.get("source_value_kind") != b.get("source_value_kind"):
            return result("SEMANTICALLY_DISTINCT", "MODEL_AND_NONMODEL_EPISTEMIC_CLASSES", a, b)
    av = parse_number(a.get("normalized_value") or a.get("reported_value"))
    bv = parse_number(b.get("normalized_value") or b.get("reported_value"))
    if av is None or bv is None:
        if a.get("normalized_value") == b.get("normalized_value") and a.get("normalized_unit") == b.get("normalized_unit"):
            cls = "EXACT_EQUIVALENT"
            reason = "EXACT_OPAQUE_REPRESENTATION"
        else:
            cls, reason = "NOT_COMPARABLE", "NON_NUMERIC_OR_UNPARSEABLE_REPRESENTATION"
        return result(cls, reason, a, b)
    au0, bu0 = a.get("normalized_unit") or a.get("reported_unit"), b.get("normalized_unit") or b.get("reported_unit")
    an, au, am = normalize_unit(av, au0, a["property_code"])
    bn, bu, bm = normalize_unit(bv, bu0, b["property_code"])
    if an is None or bn is None:
        return result("NOT_COMPARABLE", "UNIT_CONVERSION_UNDEFINED", a, b, unit_methods=[am, bm])
    unit_methods = [am, bm]
    if au is not None and bu is not None and au.casefold() != bu.casefold() and ("NO_CONVERSION" in am or "NO_CONVERSION" in bm or "UNRECOGNIZED" in am or "UNRECOGNIZED" in bm):
        return result("NOT_COMPARABLE", "UNITS_DIFFER_WITHOUT_PROPERTY_SCOPED_CONVERSION", a, b, unit_methods=unit_methods)

    if an.kind=="VECTOR" or bn.kind=="VECTOR":
        if an.kind!="VECTOR" or bn.kind!="VECTOR" or an.vector is None or bn.vector is None or len(an.vector)!=len(bn.vector):
            return result("NOT_COMPARABLE", "VECTOR_AND_SCALAR_OR_VECTOR_DIMENSIONS_DIFFER", a,b,unit_methods=unit_methods)
        if an.vector==bn.vector:
            classification="UNIT_EQUIVALENT" if au0 and bu0 and au0.casefold()!=bu0.casefold() else "EXACT_EQUIVALENT"
            return result(classification,"EXACT_COMPONENTWISE_DECIMAL_EQUALITY",a,b,unit_methods=unit_methods)
        if an.approx or bn.approx:
            return result("INSUFFICIENT_INFORMATION","APPROXIMATION_HAS_NO_DETERMINISTIC_ERROR_BOUND",a,b,unit_methods=unit_methods)
        return result("CONFLICT","DISTINCT_COMPONENTWISE_VECTOR_VALUES_PRESERVED",a,b,unit_methods=unit_methods)

    # A scalar/limit comparison uses strict mathematical interval semantics.
    if "LIMIT" in (an.kind, bn.kind):
        if an.kind == "LIMIT" and bn.kind == "LIMIT":
            return result("LIMIT_COMPATIBLE" if _overlap(an, bn) else "LIMIT_CONFLICT", "LIMIT_INTERVAL_INTERSECTION", a, b, unit_methods=unit_methods)
        other = bn if an.kind == "LIMIT" else an
        limit = an if an.kind == "LIMIT" else bn
        if other.kind == "SCALAR":
            ok = _overlap(limit, other)
            return result("LIMIT_COMPATIBLE" if ok else "LIMIT_CONFLICT", "SCALAR_TESTED_AGAINST_OPEN_OR_CLOSED_LIMIT", a, b, unit_methods=unit_methods)
        ok = _overlap(limit, other)
        return result("LIMIT_COMPATIBLE" if ok else "LIMIT_CONFLICT", "RANGE_TESTED_AGAINST_LIMIT", a, b, unit_methods=unit_methods)
    if an.kind == "RANGE" or bn.kind == "RANGE":
        return result("RANGE_COMPATIBLE" if _overlap(an, bn) else "CONFLICT", "RANGE_INTERVAL_INTERSECTION", a, b, unit_methods=unit_methods)
    if av.approx or bv.approx:
        return result("INSUFFICIENT_INFORMATION", "APPROXIMATION_HAS_NO_DETERMINISTIC_ERROR_BOUND", a, b, unit_methods=unit_methods)
    if an.lo == bn.lo:
        if a.get("source_lineage") == b.get("source_lineage") and an.uncertainty==bn.uncertainty:
            return result("EXACT_EQUIVALENT", "SAME_LINEAGE_IDENTICAL_VALUE", a, b, unit_methods=unit_methods)
        if an.uncertainty != bn.uncertainty:
            return result("DISTINCT_BUT_COMPATIBLE", "SAME_SCALAR_DIFFERING_UNCERTAINTY_REPRESENTATION",a,b,unit_methods=unit_methods)
        if au0 and bu0 and au0.casefold() != bu0.casefold():
            return result("UNIT_EQUIVALENT", "EXACT_DECIMAL_AFTER_PROPERTY_SCOPED_UNIT_CONVERSION", a, b, unit_methods=unit_methods)
        return result("EXACT_EQUIVALENT", "EXACT_DECIMAL_VALUE_AND_UNIT", a, b, unit_methods=unit_methods)

    # Display precision permits a deterministic equivalence only when the
    # more precise number rounds exactly to the coarser source quantum.
    if an.quantum is not None and bn.quantum is not None:
        if abs(an.lo-bn.lo) < (abs(an.quantum)+abs(bn.quantum))/Decimal(2):
            return result("PRECISION_EQUIVALENT", "ROUNDS_TO_COARSER_REPORTED_DECIMAL_QUANTUM", a, b, unit_methods=unit_methods,
                          precision_basis={"quantum_a":str(an.quantum),"quantum_b":str(bn.quantum)})
    ua = parse_uncertainty(a.get("normalized_uncertainty") or a.get("reported_uncertainty"), a.get("normalized_unit") or a.get("reported_unit"), a["property_code"]) or an.uncertainty
    ub = parse_uncertainty(b.get("normalized_uncertainty") or b.get("reported_uncertainty"), b.get("normalized_unit") or b.get("reported_unit"), b["property_code"]) or bn.uncertainty
    if ua is not None and ub is not None:
        if abs(an.lo-bn.lo) <= ua+ub:
            return result("AGREES_WITHIN_UNCERTAINTY", "SYMMETRIC_UNCERTAINTY_INTERVALS_OVERLAP", a,b,unit_methods=unit_methods, uncertainty_basis={"uncertainty_a":str(ua),"uncertainty_b":str(ub)})
        return result("CONFLICT", "SYMMETRIC_UNCERTAINTY_INTERVALS_DISJOINT", a,b,unit_methods=unit_methods, uncertainty_basis={"uncertainty_a":str(ua),"uncertainty_b":str(ub)})
    if ua is not None or ub is not None:
        u=ua if ua is not None else ub
        if abs(an.lo-bn.lo) <= u:
            return result("DISTINCT_BUT_COMPATIBLE", "ONE_ASSERTION_HAS_UNCERTAINTY_OTHER_IS_POINT_VALUE", a,b,unit_methods=unit_methods, uncertainty_basis={"available_uncertainty":str(u)})
    if a.get("source_lineage") == b.get("source_lineage"):
        return result("INSUFFICIENT_INFORMATION", "SAME_LINEAGE_DISTINCT_SCALARS_WITHOUT_REPRESENTATION_RELATION", a,b,unit_methods=unit_methods)
    return result("CONFLICT", "UNEQUAL_SCALARS_WITHOUT_SHARED_PRECISION_OR_UNCERTAINTY_BASIS", a,b,unit_methods=unit_methods)


def result(classification: str, reason: str, a: dict, b: dict, **extra) -> dict:
    def detail(x):
        return {k:x.get(k) for k in ("reported_value","reported_unit","reported_uncertainty",
            "normalized_value","normalized_unit","normalized_uncertainty","source_artifact_id",
            "source_lineage","source_reference","epistemic_class","source_value_kind","identity_held")}
    return {"classification":classification,"reason_code":reason,
            "assertion_a":a["assertion_id"],"assertion_b":b["assertion_id"],
            "value_a":detail(a),"value_b":detail(b),**extra}


def load_assertions(conn: sqlite3.Connection, resolved_crosswalks: set[tuple[str,str]]) -> list[dict]:
    conn.row_factory = sqlite3.Row
    artifacts={r["artifact_id"]:dict(r) for r in conn.execute("SELECT artifact_id,authority,product,version,sha256 FROM source_artifact")}
    held={(r["source_artifact_id"],r["body_id"]) for r in conn.execute("SELECT source_artifact_id,body_id FROM identity_crosswalk WHERE disposition='HOLD'")} - resolved_crosswalks
    rows=[dict(r) for r in conn.execute("SELECT * FROM candidate_assertion ORDER BY body_id,property_code,assertion_id")]
    for row in rows:
        art=artifacts.get(row["source_artifact_id"],{})
        row["source_authority"]=art.get("authority")
        row["source_product"]=art.get("product")
        row["source_version"]=art.get("version")
        row["identity_held"]=(row["source_artifact_id"],row["body_id"]) in held
    return rows


def resolve_identities(conn: sqlite3.Connection, identity_doc: Path) -> list[dict]:
    """Resolve aliases only from exact frozen NAIF ID/name rows and LOOM IDs."""
    conn.row_factory = sqlite3.Row
    text=identity_doc.read_text(errors="replace")
    id_names={}
    for m in re.finditer(r"(?m)^\s*(\d+)\s+'([^']+)'",text):
        id_names.setdefault(m.group(1),set()).add(m.group(2).strip())
    def norm_name(x: str) -> str:
        return re.sub(r"[^a-z0-9]+"," ",re.sub(r"^\s*\d+\s+","",x.strip().casefold())).strip()
    def documented_aliases(value: str) -> list[tuple[str,str]]:
        n=int(value); out=[(value,"EXACT_AUTHORITY_ID")]
        if 20_000_001<=n<=49_999_999:
            out.append((str(2_000_000+(n-20_000_000)),"NAIF_EXTENDED_TO_LEGACY_ARITHMETIC_ALIAS"))
        elif 2_000_001<=n<=2_999_999:
            out.append((str(20_000_000+(n-2_000_000)),"NAIF_LEGACY_TO_EXTENDED_ARITHMETIC_ALIAS"))
        return out
    body_rows={r["body_id"]:dict(r) for r in conn.execute("SELECT body_id,canonical_name,body_class FROM authority_body_ref")}
    out=[]
    for r in conn.execute("SELECT * FROM identity_crosswalk ORDER BY crosswalk_id"):
        row=dict(r)
        if row["disposition"] != "HOLD":
            status="UNCHANGED_MATCH"; reason="INPUT_CROSSWALK_ALREADY_MATCHED"
            resolved_id=row["external_id"]; new_disposition=row["disposition"]; released=0
        else:
            body=body_rows.get(row["body_id"] or "",{})
            canonical=norm_name(body.get("canonical_name",""))
            aliases=documented_aliases(row["external_id"])
            exact_matches=[(code,method,name) for code,method in aliases for name in id_names.get(code,set()) if norm_name(name)==canonical]
            if len(exact_matches)==1:
                resolved_id,alias_method,_=exact_matches[0]
                status="VERIFIED_EXISTING_BODY_ID"
                reason="EXACT_NAIF_ID_NAME_MATCHES_CANONICAL_IDENTITY" if alias_method=="EXACT_AUTHORITY_ID" else alias_method
                new_disposition="MATCH"
                released=conn.execute("SELECT count(*) FROM candidate_assertion WHERE body_id=? AND source_artifact_id=? AND disposition='HOLD'",(row["body_id"],row["source_artifact_id"])).fetchone()[0]
            else:
                targets=sorted(code for code,aliases in id_names.items() if any(norm_name(name)==canonical for name in aliases))
                if body.get("body_class") in ("BINARY_ASTEROID_PRIMARY","TROJAN_ASTEROID") and len(targets)==1:
                    status="SUPPLEMENTAL_PRIMARY_IDENTITY_RESOLVED_SOURCE_ID_REMAINS_HELD"
                    reason="EXACT_AUTHORITY_ID_NAME_MATCH_FOUND_BUT_SOURCE_IDENTIFIER_NAMES_OTHER_SYSTEM_OBJECT"
                    resolved_id=targets[0]
                else:
                    status="HOLD"; reason="NO_UNIQUE_EXACT_AUTHORITY_ID_NAME_CLASS_MATCH"; resolved_id=None
                new_disposition="HOLD"; released=0
        out.append({"crosswalk_id":row["crosswalk_id"],"source_artifact_id":row["source_artifact_id"],
                    "external_id_scheme":row["external_id_scheme"],"external_id":row["external_id"],
                    "body_id":row["body_id"],"prior_disposition":row["disposition"],
                    "resolution":status,"reason_code":reason,"evidence_notes":row["notes"],
                    "resolved_external_id":resolved_id,"new_disposition":new_disposition,
                    "assertions_released":released})
    return out


def semantic_digest(ledger: Path) -> str:
    c=sqlite3.connect(ledger)
    records=[]
    for table in ("reconciliation_group","reconciliation_pair","identity_resolution","assertion_disposition_event","effective_coverage"):
        cols=[r[1] for r in c.execute(f"PRAGMA table_info({table})")]
        records.extend((table,dict(zip(cols,row))) for row in c.execute(f"SELECT * FROM {table}"))
    c.close()
    payload=json.dumps(sorted(records,key=lambda x:(x[0],json.dumps(x[1],sort_keys=True,default=str))),sort_keys=True,separators=(",",":"),default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def build(input_db: Path, out_db: Path, report_dir: Path, reverse: bool=False,
          identity_doc: Path | None=None) -> dict:
    started=time.perf_counter()
    if out_db.exists():
        raise FileExistsError(f"refusing to overwrite {out_db}")
    report_dir.mkdir(parents=True,exist_ok=True)
    uri=f"file:{input_db.resolve()}?mode=ro&immutable=1"
    source=sqlite3.connect(uri,uri=True)
    source.execute("PRAGMA query_only=ON")
    identity_doc=identity_doc or Path(__file__).resolve().parent/"raw"/"naif_ids_required_reading.html"
    identity_doc_sha=digest_file(identity_doc)
    id_res=resolve_identities(source,identity_doc)
    resolved_crosswalks={(x["source_artifact_id"],x["body_id"]) for x in id_res
                         if x["prior_disposition"]=="HOLD" and x["new_disposition"]=="MATCH"}
    assertions=load_assertions(source,resolved_crosswalks)
    groups={}
    for row in assertions:
        groups.setdefault((row["body_id"],row["property_code"]),[]).append(row)
    group_rows=[]; pair_rows=[]
    for (body,prop),rows in sorted(groups.items()):
        rows=sorted(rows,key=lambda x:x["assertion_id"],reverse=reverse)
        classifications={}
        lineage_counts={}
        for r in rows:lineage_counts[r["source_lineage"]]=lineage_counts.get(r["source_lineage"],0)+1
        for a,b in itertools.combinations(rows,2):
            if b["assertion_id"] < a["assertion_id"]:
                a,b=b,a
            cmp=compare(a,b)
            same=a["source_lineage"]==b["source_lineage"]
            cmp["same_source_lineage"]=same
            cmp["same_artifact"]=a["source_artifact_id"]==b["source_artifact_id"]
            cmp["same_authority_product_version"]=(a.get("source_authority"),a.get("source_product"),a.get("source_version"))==(b.get("source_authority"),b.get("source_product"),b.get("source_version"))
            cmp["source_lineage_a"]=a["source_lineage"]
            cmp["source_lineage_b"]=b["source_lineage"]
            cmp["independence_status"]="SAME_LINEAGE" if same else "NOT_ESTABLISHED_FROM_FROZEN_METADATA"
            pair_rows.append((body,prop,a["assertion_id"],b["assertion_id"],cmp["classification"],cmp["reason_code"],json.dumps(cmp,sort_keys=True,separators=(",",":"))))
            classifications[cmp["classification"]]=classifications.get(cmp["classification"],0)+1
        group_rows.append((body,prop,len(rows),len(lineage_counts),len(rows)-len(lineage_counts),json.dumps(classifications,sort_keys=True,separators=(",",":"))))
    unique_lineages=source.execute("SELECT count(DISTINCT source_lineage) FROM candidate_assertion").fetchone()[0]
    released=[]
    for item in id_res:
        if item["prior_disposition"]=="HOLD" and item["new_disposition"]=="MATCH":
            released.extend((r[0],item["body_id"],r[1],"HOLD","CANDIDATE",item["crosswalk_id"],item["reason_code"],item["source_artifact_id"])
                            for r in source.execute("SELECT assertion_id,property_code FROM candidate_assertion WHERE body_id=? AND source_artifact_id=? AND disposition='HOLD' ORDER BY assertion_id",(item["body_id"],item["source_artifact_id"])))
    released_ids={x[0] for x in released}
    effective_lineage_count=len({x["source_lineage"] for x in assertions
                                 if x["disposition"]=="CANDIDATE" or x["assertion_id"] in released_ids})
    coverage=[]
    for body,prop,disp,reason,n in source.execute("SELECT body_id,property_code,disposition,reason,assertion_count FROM coverage ORDER BY body_id,property_code"):
        rows=groups.get((body,prop),[])
        lane_released_ids={x[0] for x in released if x[1]==body and x[2]==prop}
        effective=bool(any(x["disposition"]=="CANDIDATE" or x["assertion_id"] in lane_released_ids for x in rows))
        effective_disp="SUPPORTED" if effective else disp
        coverage.append((body,prop,disp,reason,effective_disp,int(effective),len({x['source_lineage'] for x in rows if x['disposition']=='CANDIDATE' or x['assertion_id'] in lane_released_ids})))
    source.close()
    if reverse:
        group_rows.reverse();pair_rows.reverse();id_res.reverse();coverage.reverse()
    c=sqlite3.connect(out_db)
    c.executescript("""
    PRAGMA foreign_keys=ON;
    CREATE TABLE reconciliation_group(body_id TEXT NOT NULL,property_code TEXT NOT NULL,assertion_count INTEGER NOT NULL,source_lineage_count INTEGER NOT NULL,same_lineage_excess INTEGER NOT NULL,classification_counts_json TEXT NOT NULL,PRIMARY KEY(body_id,property_code));
    CREATE TABLE reconciliation_pair(body_id TEXT NOT NULL,property_code TEXT NOT NULL,assertion_a TEXT NOT NULL,assertion_b TEXT NOT NULL,classification TEXT NOT NULL,reason_code TEXT NOT NULL,detail_json TEXT NOT NULL,PRIMARY KEY(body_id,property_code,assertion_a,assertion_b),CHECK(classification IN ("""+",".join(repr(x) for x in CLASSIFICATIONS)+""")));
    CREATE TABLE identity_resolution(crosswalk_id TEXT PRIMARY KEY,source_artifact_id TEXT NOT NULL,external_id_scheme TEXT NOT NULL,external_id TEXT NOT NULL,body_id TEXT,prior_disposition TEXT NOT NULL,resolution TEXT NOT NULL,reason_code TEXT NOT NULL,evidence_notes TEXT NOT NULL,resolved_external_id TEXT,new_disposition TEXT NOT NULL,assertions_released INTEGER NOT NULL);
    CREATE TABLE assertion_disposition_event(assertion_id TEXT PRIMARY KEY,body_id TEXT NOT NULL,property_code TEXT NOT NULL,prior_disposition TEXT NOT NULL,new_disposition TEXT NOT NULL,crosswalk_id TEXT NOT NULL,reason_code TEXT NOT NULL,source_artifact_id TEXT NOT NULL);
    CREATE TABLE effective_coverage(body_id TEXT NOT NULL,property_code TEXT NOT NULL,input_disposition TEXT NOT NULL,input_reason TEXT NOT NULL,effective_disposition TEXT NOT NULL,effectively_supported INTEGER NOT NULL,effective_independent_lineages INTEGER NOT NULL,PRIMARY KEY(body_id,property_code));
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    """)
    c.executemany("INSERT INTO reconciliation_group VALUES(?,?,?,?,?,?)",group_rows)
    c.executemany("INSERT INTO reconciliation_pair VALUES(?,?,?,?,?,?,?)",pair_rows)
    c.executemany("INSERT INTO identity_resolution VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",[(x["crosswalk_id"],x["source_artifact_id"],x["external_id_scheme"],x["external_id"],x["body_id"],x["prior_disposition"],x["resolution"],x["reason_code"],x["evidence_notes"],x["resolved_external_id"],x["new_disposition"],x["assertions_released"]) for x in id_res])
    c.executemany("INSERT INTO assertion_disposition_event VALUES(?,?,?,?,?,?,?,?)",released)
    c.executemany("INSERT INTO effective_coverage VALUES(?,?,?,?,?,?,?)",coverage)
    runtime=time.perf_counter()-started
    c.executemany("INSERT INTO meta VALUES(?,?)",[("engine_version",ENGINE_VERSION),("input_sha256",digest_file(input_db)),("input_mutated","false"),("identity_reference_sha256",identity_doc_sha),("preferred_fact_count","0")])
    c.commit();c.close()
    digest=semantic_digest(out_db)
    c=sqlite3.connect(out_db);c.execute("INSERT INTO meta VALUES(?,?)",("semantic_digest",digest));c.commit();c.close()
    # Aggregate only actual assertion comparisons, keeping assertion and
    # independent-lineage quantities visibly separate.
    rc=sqlite3.connect(out_db);rc.row_factory=sqlite3.Row
    class_counts={r[0]:r[1] for r in rc.execute("SELECT classification,count(*) FROM reconciliation_pair GROUP BY 1 ORDER BY 1")}
    lineage_pairs={
        "same_source_lineage_pairs":rc.execute("SELECT count(*) FROM reconciliation_pair WHERE json_extract(detail_json,'$.same_source_lineage')=1").fetchone()[0],
        "distinct_lineage_pairs_independence_not_established":rc.execute("SELECT count(*) FROM reconciliation_pair WHERE json_extract(detail_json,'$.same_source_lineage')=0").fetchone()[0],
        "independent_confirmed_pairs":0,
        "same_artifact_pairs":rc.execute("SELECT count(*) FROM reconciliation_pair WHERE json_extract(detail_json,'$.same_artifact')=1").fetchone()[0],
        "same_authority_product_version_pairs":rc.execute("SELECT count(*) FROM reconciliation_pair WHERE json_extract(detail_json,'$.same_authority_product_version')=1").fetchone()[0],
        "identity_held_not_comparable_pairs":rc.execute("SELECT count(*) FROM reconciliation_pair WHERE reason_code='IDENTITY_CROSSWALK_REMAINS_HELD'").fetchone()[0],
    }
    multi=rc.execute("SELECT count(*) FROM reconciliation_group WHERE assertion_count>1").fetchone()[0]
    singles=rc.execute("SELECT count(*) FROM reconciliation_group WHERE assertion_count=1").fetchone()[0]
    before_hold=rc.execute("SELECT count(*) FROM identity_resolution WHERE prior_disposition='HOLD'").fetchone()[0]
    after_hold=rc.execute("SELECT count(*) FROM identity_resolution WHERE prior_disposition='HOLD' AND new_disposition='HOLD'").fetchone()[0]
    coverage_counts={r[0]:r[1] for r in rc.execute("SELECT effective_disposition,count(*) FROM effective_coverage GROUP BY 1 ORDER BY 1")}
    support_after=rc.execute("SELECT count(*) FROM effective_coverage WHERE effectively_supported=1").fetchone()[0]
    lineage_count=effective_lineage_count
    conflict_rows=[]
    for r in rc.execute("SELECT body_id,property_code,detail_json FROM reconciliation_pair WHERE classification IN ('CONFLICT','LIMIT_CONFLICT') ORDER BY body_id,property_code,assertion_a,assertion_b"):
        detail=json.loads(r["detail_json"]); conflict_rows.append({"body_id":r["body_id"],"property_code":r["property_code"],**detail})
    rc.close()
    held_families_before=len({x["body_id"] for x in id_res if x["prior_disposition"]=="HOLD"})
    held_families_after=len({x["body_id"] for x in id_res if x["prior_disposition"]=="HOLD" and x["new_disposition"]=="HOLD"})
    resolved_families=len({x["body_id"] for x in id_res if x["prior_disposition"]=="HOLD" and x["resolution"] in ("VERIFIED_EXISTING_BODY_ID","SUPPLEMENTAL_PRIMARY_IDENTITY_RESOLVED_SOURCE_ID_REMAINS_HELD")})
    resolved_rows=sum(1 for x in id_res if x["prior_disposition"]=="HOLD" and x["new_disposition"]=="MATCH")
    report={"mission_id":"SOLAR-BASELINE-01R","engine_version":ENGINE_VERSION,"input_database":str(input_db),"input_sha256":digest_file(input_db),"input_semantic_digest":"eaa76ed502dfd96ab8d6f7eb6c294f0344a4d9abb68678f18d03f3a5af5c9cda","identity_reference_sha256":identity_doc_sha,"input_assertions":len(assertions),"unique_source_lineages":unique_lineages,"reconciliation_groups":len(group_rows),"single_assertion_groups":singles,"multi_assertion_groups":multi,"pairwise_comparisons":len(pair_rows),"classification_counts":class_counts,"lineage_pair_counts":lineage_pairs,"same_lineage_excess_assertions":sum(x[4] for x in group_rows),"effective_coverage":{"lanes":len(coverage),"supported_before":sum(1 for _,_,d,_,_,_,_ in coverage if d=="SUPPORTED"),"supported_after":support_after,"newly_supported_lanes":support_after-sum(1 for _,_,d,_,_,_,_ in coverage if d=="SUPPORTED"),"unsupported_or_non_supported_before":len(coverage)-sum(1 for _,_,d,_,_,_,_ in coverage if d=="SUPPORTED"),"effective_independent_lineages":lineage_count,"dispositions":coverage_counts},"identity":{"holds_before":before_hold,"holds_after":after_hold,"held_identity_families_before":held_families_before,"held_identity_families_after":held_families_after,"primary_identity_families_resolved":resolved_families,"crosswalk_rows_resolved":resolved_rows,"released_assertions":len(released),"records":len(id_res)},"preferred_fact_count":0,"input_mutated":False,"ledger_path":str(out_db),"ledger_sha256":digest_file(out_db),"semantic_digest":digest,"conflict_rows":conflict_rows,"runtime_seconds":runtime,"offline_replay":True}
    (report_dir/"reconciliation_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    (report_dir/"identity_resolution.json").write_text(json.dumps({"engine_version":ENGINE_VERSION,"identity_reference_sha256":identity_doc_sha,"holds_before":before_hold,"holds_after":after_hold,"primary_identity_families_resolved":resolved_families,"crosswalk_rows_resolved":resolved_rows,"released_assertions":len(released),"decisions":id_res},indent=2,sort_keys=True)+"\n")
    (report_dir/"conflict_report.json").write_text(json.dumps({"conflict_pair_count":class_counts.get("CONFLICT",0),"limit_conflict_pair_count":class_counts.get("LIMIT_CONFLICT",0),"conflicts":conflict_rows},indent=2,sort_keys=True)+"\n")
    return report


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--reports",type=Path,required=True)
    parser.add_argument("--reverse",action="store_true")
    args=parser.parse_args()
    print(json.dumps(build(args.input,args.output,args.reports,args.reverse),sort_keys=True))


if __name__ == "__main__":
    main()
