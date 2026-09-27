"""Canonical and semantic checks for derived Solar basemap products.

These checks validate display products only. They do not grant state authority.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath

SCHEMA = Path(__file__).resolve().parents[1] / "engineering/solar_basemap/product.schema.json"
SCHEMA_DOC = json.loads(SCHEMA.read_text())


def _schema_validate(value, schema, path="$", root=SCHEMA_DOC):
    """Small dependency-free evaluator for the JSON Schema subset in product.schema."""
    if "$ref" in schema:
        target=root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target=target[part]
        _schema_validate(value,target,path,root); return
    if "oneOf" in schema:
        matches=0
        for option in schema["oneOf"]:
            try:_schema_validate(value,option,path,root);matches+=1
            except ValueError:pass
        if matches!=1:raise ValueError(f"{path}: expected exactly one schema match, got {matches}")
    for sub in schema.get("allOf",[]):_schema_validate(value,sub,path,root)
    if "if" in schema:
        try:_schema_validate(value,schema["if"],path,root); condition=True
        except ValueError:condition=False
        if condition and "then" in schema:_schema_validate(value,schema["then"],path,root)
    typ=schema.get("type")
    types=typ if isinstance(typ,list) else [typ] if typ else []
    checks={"object":lambda x:isinstance(x,dict),"array":lambda x:isinstance(x,list),"string":lambda x:isinstance(x,str),
            "number":lambda x:isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x),
            "integer":lambda x:isinstance(x,int) and not isinstance(x,bool),"boolean":lambda x:isinstance(x,bool),"null":lambda x:x is None}
    if types and not any(checks[t](value) for t in types):raise ValueError(f"{path}: expected {types}")
    if "const" in schema and value!=schema["const"]:raise ValueError(f"{path}: expected constant {schema['const']}")
    if "enum" in schema and value not in schema["enum"]:raise ValueError(f"{path}: value outside enum")
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if "minimum" in schema and value<schema["minimum"]:raise ValueError(f"{path}: below minimum")
        if "maximum" in schema and value>schema["maximum"]:raise ValueError(f"{path}: above maximum")
    if isinstance(value,str):
        if len(value)<schema.get("minLength",0):raise ValueError(f"{path}: string too short")
        if "pattern" in schema and not __import__('re').search(schema["pattern"],value):raise ValueError(f"{path}: pattern mismatch")
    if isinstance(value,list):
        if len(value)<schema.get("minItems",0) or len(value)>schema.get("maxItems",10**12):raise ValueError(f"{path}: array length mismatch")
        if "items" in schema:
            for i,item in enumerate(value):_schema_validate(item,schema["items"],f"{path}[{i}]",root)
    if isinstance(value,dict):
        missing=set(schema.get("required",()))-value.keys()
        if missing:raise ValueError(f"{path}: missing fields {sorted(missing)}")
        properties=schema.get("properties",{})
        for key,item in value.items():
            if key in properties:_schema_validate(item,properties[key],f"{path}.{key}",root)
            elif schema.get("additionalProperties") is False:raise ValueError(f"{path}: undeclared field {key}")
            elif isinstance(schema.get("additionalProperties"),dict):_schema_validate(item,schema["additionalProperties"],f"{path}.{key}",root)


def _finite(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        return 0 if value == 0 else value
    if isinstance(value, list):
        return [_finite(v) for v in value]
    if isinstance(value, dict):
        return {k: _finite(v) for k, v in value.items()}
    return value


def canonical_bytes(value):
    return json.dumps(_finite(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def resource_bytes(value):
    raw = canonical_bytes(value)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "gzip": gzip.compress(raw, compresslevel=9, mtime=0)}


def validate_semantics(document, *, kind=None):
    if not isinstance(document, dict) or not isinstance(document.get("schema"), str):
        raise ValueError("product record requires schema discriminator")
    schema = document["schema"]
    if schema not in {"loom.solar-basemap.manifest/0.1", "loom.solar-basemap.root/0.1",
                      "loom.solar-basemap.chunk/0.1", "loom.solar-basemap.provenance/0.1"}:
        raise ValueError(f"unsupported product schema {schema}")
    if kind and not schema.endswith("/" + kind + "/0.1"):
        raise ValueError(f"expected {kind} record")
    if schema.endswith("manifest/0.1"):
        if document.get("frame") != "ECLIPJ2000" or document.get("center") != "SUN" or document.get("units") != "km":
            raise ValueError("manifest frame/center/units mismatch")
        if document.get("epoch_et") != 7131844800.0:
            raise ValueError("prototype epoch mismatch")
        if document.get("counts", {}).get("catalog") != 110:
            raise ValueError("catalog count does not match authority snapshot")
    if schema.endswith("root/0.1"):
        ids = [f.get("body_id") for f in document.get("features", [])]
        if len(ids) != len(set(ids)) or len(ids) != 110:
            raise ValueError("root must retain all 110 unique governed identities")
        nodes = {n.get("node_id"): n for n in document.get("nodes", [])}
        if "solar" not in nodes:
            raise ValueError("missing solar root node")
        for node in nodes.values():
            if node.get("parent_node_id") is not None and node["parent_node_id"] not in nodes:
                raise ValueError("broken presentation hierarchy")
        # A well formed parent pointer is insufficient: cycles can make a
        # streamed hierarchy permanently unreachable or recurse forever.
        for node_id in nodes:
            seen=set(); current=node_id
            while current is not None:
                if current in seen:
                    raise ValueError("cyclic presentation hierarchy")
                seen.add(current)
                current=nodes[current].get("parent_node_id")
        for curve in document.get("curves", []):
            if curve.get("closed") is not False:
                raise ValueError("curves must remain open");
            if curve.get("semantic") == "PARENT_RELATIVE_REFERENCE_ORBIT" and curve.get("anchor_id") == "SUN":
                raise ValueError("parent-relative curve cannot use Sun anchor")
            _validate_curve(curve)
    _schema_validate(document,{"$ref":"#/$defs/"+schema.split(".")[-1].split("/")[0]})
    return True


def _validate_curve(curve):
    if curve.get("start_et", 0) > curve.get("end_et", 0):
        raise ValueError("curve interval is reversed")
    for segment in curve.get("segments", []):
        points = segment.get("points", [])
        if [p[0] for p in points] != sorted(p[0] for p in points):
            raise ValueError("segment epochs are not chronological")
        for index in segment.get("sample_indices", []):
            if not isinstance(index, int) or index < 0:
                raise ValueError("invalid retained sample index")
        for point in points:
            if len(point) != 4 or not all(math.isfinite(float(v)) for v in point):
                raise ValueError("invalid segment coordinate")


def validate_product(root):
    """Verify immutable resource hashes, gzip variants and manifest identity."""
    root = Path(root)
    pointer = json.loads((root / "current.json").read_text())
    manifest_path = root / pointer["manifest_uri"]
    manifest_raw = manifest_path.read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != pointer["manifest_sha256"]:
        raise ValueError("manifest pointer hash mismatch")
    manifest = json.loads(manifest_raw)
    validate_semantics(manifest)
    build_claim = manifest.pop("build_id")
    if hashlib.sha256(canonical_bytes(manifest)).hexdigest() != build_claim:
        raise ValueError("manifest build id mismatch")
    manifest["build_id"] = build_claim
    for desc in (manifest["root"], manifest["provenance"]):
        _verify_resource(root, desc)
    product_root = json.loads((root / manifest["root"]["uri"]).read_bytes())
    validate_semantics(product_root)
    if product_root["build_spec_id"] != manifest["build_spec_id"]:
        raise ValueError("root build specification mismatch")
    provenance = json.loads((root / manifest["provenance"]["uri"]).read_bytes())
    if provenance.get("build_spec_id") != manifest["build_spec_id"]:
        raise ValueError("provenance build specification mismatch")
    source_records = {s["source_ref"]:s for s in provenance["sources"]}
    source_refs=set(source_records)
    features = {f["body_id"]: f for f in product_root["features"]}
    baseline = json.loads((Path(__file__).resolve().parents[1]/"engineering/solar_basemap/evidence/catalog_2226_snapshot.json").read_text())
    baseline_rows={f["body_id"]:f for f in baseline["objects"]}
    for body,feature in features.items():
        expected=baseline_rows.get(body)
        if not expected or feature["resolution"]!=expected["resolution"] or feature["catalog_parent_id"]!=expected["parent_body_id"]:
            raise ValueError(f"catalog status/parent changed from qualified baseline: {body}")
        expected_position=expected.get("relative",{}).get("position_km")
        if feature["position_km"]!=expected_position:
            raise ValueError(f"epoch marker differs from qualified authority baseline: {body}")
        if feature["resolution"]=="RESOLVED":
            source=source_records.get(feature["source_ref"])
            if source is None or source["body_id"]!=body:
                raise ValueError(f"epoch marker source provenance missing or misbound: {body}")
            if source["source_id"] not in feature["source_ref"]:
                raise ValueError(f"epoch marker source identity mismatch: {body}")
        elif feature["source_ref"] is not None:
            raise ValueError(f"unresolved identity carries a source reference: {body}")
    curves = {c["feature_id"]: c for c in product_root["curves"]}
    spec = json.loads((root / manifest["generation"]["spec"]["uri"]).read_bytes())
    required = spec["requested_reference_curves"]
    if set(curves) != set(required):
        raise ValueError("requested curve inventory mismatch")
    audits = {}
    for body, anchor in required.items():
        curve = curves[body]
        if curve["anchor_id"] != anchor:
            raise ValueError(f"curve anchor mismatch for {body}")
        _verify_resource(root, curve["audit"])
        audit = json.loads((root / curve["audit"]["uri"]).read_bytes())
        audits[body] = audit
        if audit["body_id"] != body or audit["anchor_id"] != anchor or audit["frame"] != "ECLIPJ2000":
            raise ValueError(f"audit identity/frame mismatch for {body}")
        for sample in audit["samples"]:
            if sample["body_state"] is None or sample["anchor_state"] is None:
                continue
            b, a = sample["body_state"]["position_km"], sample["anchor_state"]["position_km"]
            if sample["relative_position_km"] != [x-y for x,y in zip(b,a)]:
                raise ValueError(f"relative sample differs from governed state subtraction: {body}")
            bp = sample["body_state"]["provenance"].get("ephemeris_source_id")
            ap = sample["anchor_state"]["provenance"].get("ephemeris_source_id")
            if f"{bp}::{body}" not in source_refs or f"{ap}::{anchor}" not in source_refs:
                raise ValueError(f"source provenance missing for {body}")
        marker = next((s for s in audit["samples"] if s["et"] == manifest["epoch_et"] and s["body_state"]), None)
        if marker and features[body]["position_km"] != marker["body_state"]["position_km"]:
            raise ValueError(f"epoch marker differs from exact governed state for {body}")
    expected_by_node = {}
    for node in product_root["nodes"]:
        node_curves = sorted(body for body, anchor in required.items() if ("solar" if anchor == "SUN" else f"system:{anchor}") == node["node_id"])
        expected_by_node[node["node_id"]] = node_curves
        if [level["level"] for level in node["levels"]] != list(range(len(node["levels"]))):
            raise ValueError(f"nonconsecutive LOD levels at {node['node_id']}")
        if [x["measured_error_km"] for x in node["levels"]] != sorted((x["measured_error_km"] for x in node["levels"]),reverse=True):
            raise ValueError(f"LOD errors are not nonincreasing at {node['node_id']}")
        previous = None
        for level in node["levels"]:
            _verify_resource(root, level["resource"])
            chunk = json.loads((root / level["resource"]["uri"]).read_bytes())
            validate_semantics(chunk,kind="chunk")
            if chunk["build_spec_id"] != manifest["build_spec_id"] or chunk["node_id"] != node["node_id"] or chunk["level"] != level["level"]:
                raise ValueError("chunk identity mismatch")
            if sorted(c["feature_id"] for c in chunk["curves"]) != node_curves:
                raise ValueError(f"curve inventory changes across LOD at {node['node_id']}")
            current={}
            for c in chunk["curves"]:
                body=c["feature_id"]; audit=audits[body]["samples"]
                source_pairs=[]; current_indices=[]
                for segment in c["segments"]:
                    pair=(segment["body_source_ref"],segment["anchor_source_ref"]); source_pairs.append(pair)
                    for index,point in zip(segment["sample_indices"],segment["points"]):
                        if index>=len(audit):raise ValueError("curve index outside retained-sample audit")
                        sample=audit[index]
                        expected_point=[sample["et"],*sample["relative_position_km"]]
                        if sample["relative_position_km"] is None or point!=expected_point:
                            raise ValueError(f"render point is not an archived governed sample: {body}")
                        if point[0]==manifest["epoch_et"] and c["semantic"]=="PARENT_RELATIVE_REFERENCE_ORBIT":
                            anchor_position=features[c["anchor_id"]]["position_km"]
                            world=[anchor_position[i]+point[i+1] for i in range(3)]
                            marker=features[body]["position_km"]
                            tolerance=max(1e-9,2*max(math.ulp(float(x)) for x in marker))
                            if math.dist(world,marker)>tolerance:raise ValueError(f"local reference curve misses exact epoch position: {body}")
                        current_indices.append(index)
                    if len(segment["points"])<2:continue
                current[body]=(source_pairs,set(current_indices))
            if previous is not None:
                for body,(pairs,indices) in current.items():
                    old_pairs,old_indices=previous[body]
                    if pairs!=old_pairs or not old_indices.issubset(indices):raise ValueError(f"LOD samples are not nested at {node['node_id']}:{body}")
            previous=current
    # Every declared child/parent remains in one rooted tree. The v0.1
    # generation currently has two levels only, but reject malformed future
    # packages instead of relying on today's shallow layout.
    node_ids={n["node_id"] for n in product_root["nodes"]}
    children={n["node_id"]:[] for n in product_root["nodes"]}
    for n in product_root["nodes"]:
        if n.get("parent_node_id") is not None:
            children[n["parent_node_id"]].append(n["node_id"])
    reached=set(); stack=["solar"]
    while stack:
        current=stack.pop()
        if current in reached:raise ValueError("cyclic presentation hierarchy")
        reached.add(current);stack.extend(children[current])
    if reached!=node_ids:raise ValueError("presentation hierarchy is disconnected")
    for curve in product_root["curves"]:
        _verify_resource(root,curve["audit"])
    for desc in provenance.get("sample_resources",[]):_verify_resource(root,desc)
    return manifest, product_root


def _verify_resource(root, desc):
    uri = PurePosixPath(desc["uri"])
    if uri.is_absolute() or ".." in uri.parts:
        raise ValueError("unsafe product URI")
    raw = (root / uri).read_bytes()
    if len(raw) != desc["bytes"] or hashlib.sha256(raw).hexdigest() != desc["sha256"]:
        raise ValueError(f"resource integrity failure: {uri}")
    gz = (root / (str(uri) + ".gz")).read_bytes()
    if len(gz) != desc["gzip_bytes"] or gzip.decompress(gz) != raw:
        raise ValueError(f"gzip integrity failure: {uri}")
