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
    definition=schema.removeprefix("loom.solar-basemap.").split("/",1)[0]
    if kind and definition != kind:
        raise ValueError(f"expected {kind} record")
    if schema.endswith("manifest/0.1"):
        if document.get("frame") != "ECLIPJ2000" or document.get("center") != "SUN" or document.get("units") != "km":
            raise ValueError("manifest frame/center/units mismatch")
        if document.get("epoch_et") != 7131844800.0:
            raise ValueError("prototype epoch mismatch")
        expected={"catalog":110,"resolved":103,"unresolved":7}
        counts=document.get("counts",{})
        if any(counts.get(k)!=v for k,v in expected.items()) or counts.get("requested_curves",-1)<8 or counts.get("available_curves",-1)>counts.get("requested_curves",-1):
            raise ValueError("manifest counts do not match qualified authority snapshot or curve bounds")
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
    _schema_validate(document,{"$ref":"#/$defs/"+definition})
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


def validate_audit_record(audit, *, body, anchor, semantic, epoch):
    """Require the physical and derived-reference metadata beside exact states."""
    expected={"schema":"loom.solar-basemap.audit/0.1","body_id":body,"anchor_id":anchor,
              "epoch_et":epoch,"frame":"ECLIPJ2000","units":"km","aberration":"NONE",
              "physical_state_center":"SUN","cartographic_semantic":semantic}
    if any(audit.get(key)!=value for key,value in expected.items()):
        raise ValueError(f"audit identity/frame/units/semantics mismatch for {body}")
    if not isinstance(audit.get("samples"),list) or audit.get("sample_count")!=len(audit["samples"]):
        raise ValueError(f"audit sample inventory mismatch for {body}")
    return True


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
    if manifest["authority"]["sample_source_dictionary"] != manifest["provenance"]:
        raise ValueError("authority source dictionary pointer mismatch")
    for desc in (manifest["root"], manifest["provenance"], manifest["generation"]["spec"]):
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
    if manifest["authority"]["ledger_sha256"] != baseline["authority"]["ledger_sha256"] or manifest["authority"]["manifest_sha256"] != baseline["authority"]["manifest_sha256"]:
        raise ValueError("manifest authority identity differs from qualified baseline")
    expected_counts={"catalog":baseline["counts"]["catalog"],"resolved":baseline["counts"]["resolved"],
                     "unresolved":baseline["counts"]["unresolved"]}
    if any(manifest["counts"].get(k)!=v for k,v in expected_counts.items()):
        raise ValueError("manifest counts resolution differs from qualified baseline")
    baseline_rows={f["body_id"]:f for f in baseline["objects"]}
    spec = json.loads((root / manifest["generation"]["spec"]["uri"]).read_bytes())
    policy=spec["reference_curve_policy"]
    explicit=policy.get("explicit_relationships",{})
    local_families={}
    unresolved_relationships=[]
    for body,row in sorted(baseline_rows.items()):
        if row["body_class"] not in policy["local_member_body_classes"]:continue
        anchor=(explicit.get(body) or {}).get("anchor_id") or row.get("parent_body_id")
        if anchor not in baseline_rows or anchor==body or anchor=="SUN":
            unresolved_relationships.append(body);continue
        local_families.setdefault(anchor,[]).append(body)
    required={body:"SUN" for body,row in baseline_rows.items() if row["body_class"] in policy["heliocentric_body_classes"]}
    for anchor,members in local_families.items():
        if baseline_rows[anchor]["resolution"]=="RESOLVED":
            supported_members=[]
            for body in members:
                if baseline_rows[body]["resolution"]=="RESOLVED":
                    required[body]=anchor
                    supported_members.append(body)
            if supported_members:required.setdefault(anchor,"SUN")
    coverage_ext=product_root.get("extensions",{}).get("org.loom.solar-basemap.local-system-coverage/0.1")
    if not isinstance(coverage_ext,dict) or coverage_ext.get("classification_values")!=[
            "QUALIFIED_SOURCE_AVAILABLE","GOVERNED_POSITION_ONLY","MISSING_REQUIRED_SOURCE","UNRESOLVED_IDENTITY","OUT_OF_SCOPE_BY_CONTRACT"]:
        raise ValueError("generic local-system classification inventory is missing or malformed")
    systems=coverage_ext.get("systems")
    if not isinstance(systems,list):raise ValueError("local-system inventory must be an array")
    system_by_anchor={x.get("anchor_id"):x for x in systems if x.get("anchor_id") is not None}
    if len(system_by_anchor)!=sum(x.get("anchor_id") is not None for x in systems):raise ValueError("duplicate local-system anchor")
    if set(system_by_anchor)!=set(local_families):raise ValueError("local-system inventory differs from governed parent relationships")
    expected_parent_curves=sorted(anchor for anchor,members in local_families.items()
        if baseline_rows[anchor]["resolution"]=="RESOLVED"
        and any(baseline_rows[b]["resolution"]=="RESOLVED" for b in members)
        and baseline_rows[anchor]["body_class"] not in policy["heliocentric_body_classes"])
    if coverage_ext.get("solar_parent_context_curve_ids")!=expected_parent_curves:
        raise ValueError("Solar parent-context curve inventory differs from supported governed local anchors")
    for anchor,members in local_families.items():
        system=system_by_anchor[anchor]
        if sorted(system.get("member_ids",[]))!=sorted(members):raise ValueError(f"local-system member inventory mismatch: {anchor}")
        expected_generated=sorted(body for body in members if body in required)
        if sorted(system.get("generated_curve_ids",[]))!=expected_generated:raise ValueError(f"local-system curve inventory mismatch: {anchor}")
        expected_class=("QUALIFIED_SOURCE_AVAILABLE" if expected_generated else
            "UNRESOLVED_IDENTITY" if members and all("exactly one active governed identifier" in (baseline_rows[b].get("reason") or "") for b in members) else
            "MISSING_REQUIRED_SOURCE" if any(baseline_rows[b]["resolution"]!="RESOLVED" for b in members) or baseline_rows[anchor]["resolution"]!="RESOLVED" else
            "GOVERNED_POSITION_ONLY")
        if system.get("classification")!=expected_class:raise ValueError(f"local-system classification mismatch: {anchor}")
    for body in unresolved_relationships:
        if body not in {x.get("body_id") for x in coverage_ext.get("unanchored_member_omissions",[])}:
            raise ValueError(f"unresolved local identity relationship was hidden: {body}")
    expected_available=sum(c.get("geometry_status") in ("AVAILABLE","PARTIAL") for c in product_root["curves"])
    expected_manifest_counts={**expected_counts,"requested_curves":len(required),"available_curves":expected_available}
    if manifest["counts"]!=expected_manifest_counts:raise ValueError("manifest curve counts differ from generic product inventory")
    omission_reasons={o["body_id"]:o for system in systems for o in system.get("omissions",[])}
    omission_reasons.update({o["body_id"]:o for o in coverage_ext.get("unanchored_member_omissions",[])})
    for body,feature in features.items():
        expected=baseline_rows.get(body)
        expected_reason=omission_reasons.get(body,{}).get("reason",expected.get("reason") if expected else None)
        if not expected or feature["resolution"]!=expected["resolution"] or feature["catalog_parent_id"]!=expected["parent_body_id"] or feature["reason"]!=expected_reason:
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
        semantic="HELIOCENTRIC_REFERENCE_ORBIT" if anchor=="SUN" else "PARENT_RELATIVE_REFERENCE_ORBIT"
        validate_audit_record(audit,body=body,anchor=anchor,semantic=semantic,epoch=manifest["epoch_et"])
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
    client_ext=product_root.get("extensions",{}).get("org.loom.solar-basemap.client/0.1",{})
    embedded=client_ext.get("solar_embedded_curves",{})
    sun_bodies={body for body,anchor in required.items() if anchor=="SUN"}
    coverage_ext=product_root.get("extensions",{}).get("org.loom.solar-basemap.local-system-coverage/0.1",{})
    parent_context=set(coverage_ext.get("solar_parent_context_curve_ids",[]))
    if not parent_context <= sun_bodies:
        raise ValueError("Solar parent-context inventory contains a non-Sun-anchored curve")
    if set(embedded)!=sun_bodies-parent_context:
        raise ValueError("initial Solar LOD inventory differs from Sun anchored curves")
    root_basis=client_ext.get("root_error_basis",{})
    if root_basis.get("max_sse_css_px")!=.75:
        raise ValueError("initial Solar screen error limit differs from specification")
    root_scale=root_basis.get("viewport_css_height",0)/(2*math.tan(math.radians(root_basis.get("vertical_fov_degrees",0)/2))*root_basis.get("camera_distance_km",0))
    if not math.isfinite(root_scale) or root_scale<=0:
        raise ValueError("invalid initial Solar projection basis")
    if product_root.get("nodes"):
        solar_node=next((n for n in product_root["nodes"] if n["node_id"]=="solar"),None)
    else: solar_node=None
    if solar_node is None:raise ValueError("missing Solar hierarchy root")
    root_curves={c["feature_id"]:c for c in product_root["curves"]}
    max_embedded_level=0
    for body,info in embedded.items():
        level=info.get("level"); error=info.get("measured_error_km")
        if not isinstance(level,int) or not 0<=level<len(solar_node["levels"]) or not isinstance(error,(int,float)):
            raise ValueError(f"invalid initial Solar LOD declaration for {body}")
        if info.get("measured_error_css_px")!=error*root_scale or error*root_scale>.75:
            raise ValueError(f"initial Solar LOD exceeds or misstates its screen error for {body}")
        max_embedded_level=max(max_embedded_level,level)
        compiled=json.loads((root/solar_node["levels"][level]["resource"]["uri"]).read_bytes())
        chunk_curve=next((c for c in compiled["curves"] if c["feature_id"]==body),None)
        root_curve=root_curves.get(body)
        if chunk_curve is None or root_curve is None or chunk_curve["segments"]!=root_curve["segments"]:
            raise ValueError(f"initial Solar geometry differs from selected compiled LOD for {body}")
        audit=audits[body]["samples"]
        for segment in root_curve["segments"]:
            if len(segment["sample_indices"])!=len(segment["points"]):raise ValueError("initial Solar point/sample inventory mismatch")
            for index,point in zip(segment["sample_indices"],segment["points"]):
                if index>=len(audit) or point!=[audit[index]["et"],*audit[index]["relative_position_km"]]:
                    raise ValueError(f"initial Solar geometry is not an archived governed sample: {body}")
    if client_ext.get("solar_embedded_level")!=max_embedded_level:
        raise ValueError("aggregate Solar embedded level differs from per-curve levels")
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
