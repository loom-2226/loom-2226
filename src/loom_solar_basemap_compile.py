"""Read-only compiler from the governed Solar resolver to the basemap product."""
from __future__ import annotations

import gzip
import hashlib
import bisect
import json
import math
import os
import platform
import shutil
import struct
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from src.loom_solar_basemap_contract import canonical_bytes, resource_bytes, validate_product
from src.loom_solar_inspector import Inspector
from src.loom_solar_postgres import load_authority
from src.loom_spice_ephemeris_adapter import SPICE_FRAME, SpiceEphemerisAdapter

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "engineering/solar_basemap/generation-spec.json"
T = 7131844800.0
YEAR = 365.25 * 86400.0
LOCAL_SYSTEM_CLASSES = ("QUALIFIED_SOURCE_AVAILABLE", "GOVERNED_POSITION_ONLY",
                        "MISSING_REQUIRED_SOURCE", "UNRESOLVED_IDENTITY",
                        "OUT_OF_SCOPE_BY_CONTRACT")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ledger_sha(ledger):
    return hashlib.sha256(json.dumps(ledger, sort_keys=True).encode()).hexdigest()


def _vec(state):
    return [float(x) for x in state["state"]["position_km"]]


def _source(service, body, et):
    source, coverage = service.adapter.registry.source_for(body, et)
    return source, coverage


def _rdp(points, tolerance):
    if len(points) <= 2:
        return list(range(len(points)))
    keep = {0, len(points)-1}
    stack = [(0, len(points)-1)]
    while stack:
        first, last = stack.pop()
        a, b = points[first][1:], points[last][1:]
        ab = [b[i]-a[i] for i in range(3)]
        den = sum(x*x for x in ab)
        best, best_i = -1.0, None
        for i in range(first+1, last):
            p = points[i][1:]
            u = min(1.0, max(0.0, sum((p[k]-a[k])*ab[k] for k in range(3))/den)) if den else 0.0
            d = math.dist(p, [a[k]+u*ab[k] for k in range(3)])
            if d > best:
                best, best_i = d, i
        if best > tolerance:
            keep.add(best_i); stack.extend(((first,best_i),(best_i,last)))
    return sorted(keep)


def _initial_curve_level(levels, probe_error_km, projection_scale, max_sse_css_px=.75):
    """Pick each curve's own coarsest level meeting the fixed root-view SSE."""
    for level_id, level in enumerate(levels):
        error_km=probe_error_km+level["error"]
        if error_km*projection_scale<=max_sse_css_px:
            return level_id,error_km
    raise ValueError("curve has no level meeting the initial Solar-view screen error budget")


def _derive_curve_inventory(rows, spec):
    """Derive curve anchors from governed identity relationships and source resolution."""
    policy = spec["reference_curve_policy"]
    by_id = rows
    explicit = policy.get("explicit_relationships", {})
    heliocentric = {
        body: "SUN" for body, row in rows.items()
        if row["body_class"] in policy["heliocentric_body_classes"]
    }
    families = {}
    member_omissions = []
    for body, row in sorted(rows.items()):
        if row["body_class"] not in policy["local_member_body_classes"]:
            continue
        relationship = explicit.get(body)
        anchor = relationship.get("anchor_id") if relationship else None
        parent = row.get("parent_body_id")
        relation_error = None
        if anchor is None and parent in by_id:
            # Preserve the exact governed parent identity. Barycenter-to-primary
            # proximity or familiar naming is not a relationship edge.
            anchor = parent
        elif anchor is None:
            relation_error = "no governed local parent relationship or qualified explicit relationship"
        if anchor is not None and (anchor not in by_id or anchor == body or anchor == "SUN"):
            relation_error = f"local anchor is absent or invalid: {anchor}"
            anchor = None
        if anchor is None:
            unresolved_relation = parent is None or parent not in by_id
            member_omissions.append({
                "body_id": body,
                "parent_body_id": parent,
                "classification": "UNRESOLVED_IDENTITY" if unresolved_relation else "OUT_OF_SCOPE_BY_CONTRACT",
                "reason": relation_error,
            })
            continue
        family = families.setdefault(anchor, {"anchor_id": anchor, "member_ids": [], "explicit_relationships": []})
        family["member_ids"].append(body)
        if relationship:
            family["explicit_relationships"].append({"body_id": body, **relationship})

    requested = dict(heliocentric)
    for anchor, family in sorted(families.items()):
        anchor_row = by_id.get(anchor)
        supported_members = []
        for body in family["member_ids"]:
            row = by_id[body]
            if row["resolution"] != "RESOLVED":
                reason = row.get("reason") or "governed resolver did not resolve member at publication epoch"
                identity_issue = "exactly one active governed identifier" in reason
                member_omissions.append({"body_id": body, "parent_body_id": row.get("parent_body_id"),
                    "anchor_id": anchor, "classification": "UNRESOLVED_IDENTITY" if identity_issue else "MISSING_REQUIRED_SOURCE",
                    "reason": reason})
                continue
            if not anchor_row or anchor_row["resolution"] != "RESOLVED":
                member_omissions.append({"body_id": body, "parent_body_id": row.get("parent_body_id"),
                    "anchor_id": anchor, "classification": "MISSING_REQUIRED_SOURCE",
                    "reason": "governed local anchor has no resolved epoch position"})
                continue
            requested[body] = anchor
            supported_members.append(body)
        # The accepted client presents local context from the Solar curve whose
        # identity matches a local node's governed anchor. When that anchor is
        # a barycenter rather than a planet center, generate its own Sun-relative
        # curve from that exact governed identity and source.
        if supported_members and anchor_row and anchor_row["resolution"] == "RESOLVED":
            requested.setdefault(anchor, "SUN")

    inventory = []
    for anchor, family in sorted(families.items()):
        inventory.append({**family, "member_ids": sorted(family["member_ids"]),
                          "explicit_relationships": sorted(family["explicit_relationships"], key=lambda x: x["body_id"])})
    return requested, inventory, member_omissions


def _curve_sampling(inspector, body, anchor, plan):
    start, end = plan["start_et"], plan["end_et"]
    cache = {}
    def evaluate(et):
        key = struct.pack(">d", et)
        if key not in cache:
            b = inspector.record(body, et)
            a = inspector.record(anchor, et)
            if b["resolution"] != "RESOLVED" or a["resolution"] != "RESOLVED":
                cache[key] = (None, b, a)
            else:
                cache[key] = ([float(x-y) for x,y in zip(b["state"]["position_km"],a["state"]["position_km"])], b, a)
        return cache[key]
    def pair_for(row):
        q,b,a=row
        if q is None:return None
        bp=b["state"]["provenance"]["ephemeris_source_id"]
        ap=a["state"]["provenance"]["ephemeris_source_id"]
        return bp,ap
    seed_n = 65
    times = {start+(end-start)*i/(seed_n-1) for i in range(seed_n)}
    if start<=T<=end: times.add(T)
    times = sorted(times)
    for c in inspector.registry.coverage:
        if c.body_id in (None, body, anchor) and c.coverage_start_et is not None:
            for boundary in (c.coverage_start_et, c.coverage_end_et):
                for candidate in (boundary-1, math.nextafter(boundary,-math.inf), boundary,
                                  math.nextafter(boundary,math.inf), boundary+1):
                    if start <= candidate <= end: times.append(candidate)
    times = sorted(set(times))
    for et in times: evaluate(et)
    max_radius = max((math.dist(v[0],(0,0,0)) for v in cache.values() if v[0]), default=1.0)
    epsilon = max(.01, max_radius*1e-6)
    master=set(times)
    limited = False
    def refine(a,b,depth=0):
        nonlocal limited, max_radius, epsilon
        row_a=evaluate(a); row_b=evaluate(b); pa=row_a[0]; pb=row_b[0]
        split=(b-a) > (end-start)/256.0
        probes=[a+(b-a)*f for f in (.25,.5,.75)]
        probe_rows=[evaluate(t) for t in probes]
        vals=[row[0] for row in probe_rows]
        max_radius=max([max_radius]+[math.dist(v,(0,0,0)) for v in vals if v is not None])
        epsilon=max(.01,max_radius*1e-6)
        # An unresolved probe is a gap boundary; do not recursively chase it as
        # though it were curvature. Maximum temporal step still bounds each side.
        if pa is not None and pb is not None and all(p is not None for p in vals) and not split:
            for t,p in zip(probes, vals):
                u=(t-a)/(b-a); chord=[pa[k]+u*(pb[k]-pa[k]) for k in range(3)]
                if math.dist(p,chord)>epsilon: split=True
        sequence=[pair_for(row_a)]+[pair_for(row) for row in probe_rows]+[pair_for(row_b)]
        seam_probes=[t for i,t in enumerate(probes,1) if sequence[i-1] is not None and sequence[i] is not None and sequence[i-1]!=sequence[i]]
        has_seam=any(x is not None and y is not None and x!=y for x,y in zip(sequence,sequence[1:]))
        if has_seam and (b-a)>(end-start)/256.0: split=True
        elif seam_probes: master.update(seam_probes)
        if any(p is None for p in vals) and not split:
            master.update(t for t,p in zip(probes,vals) if p is None)
        if split:
            if depth >= 20:
                limited=True; return
            m=probes[1]
            if m in (a,b): limited=True; return
            if len(master)>=16385: limited=True; return
            master.add(m)
            refine(a,m,depth+1); refine(m,b,depth+1)
    for a,b in zip(times,times[1:]): refine(a,b)
    master_times=sorted(master)
    # Independent evenly offset validation grid; failed exact queries remain explicit gaps.
    max_residual=0.0; worst=None; failed=[]; seam_probes=[]; previous_grid_pair=None
    for i in range(8192):
        et=start+(end-start)*(i+.5)/8192
        exact,_,_=evaluate(et)
        if exact is None:
            failed.append(et); continue
        hi=min(len(master_times)-1,bisect.bisect_left(master_times,et))
        lo=max(0,hi-1); ta,tb=master_times[lo],master_times[hi]
        va,vb=evaluate(ta)[0],evaluate(tb)[0]
        if va is None or vb is None or tb==ta: failed.append(et); continue
        exact_pair=pair_for(evaluate(et))
        if previous_grid_pair is not None and exact_pair!=previous_grid_pair:seam_probes.append(et)
        previous_grid_pair=exact_pair
        u=(et-ta)/(tb-ta); chord=[va[k]+u*(vb[k]-va[k]) for k in range(3)]
        residual=math.dist(exact,chord)
        if residual>max_residual: max_residual,worst=residual,et
    # One exact reinsertion pass for violating probes.
    if max_residual>epsilon and not failed and len(master)<16385:
        evaluate(worst); master.add(worst); master_times=sorted(master)
        max_residual=0.0
        for i in range(8192):
            et=start+(end-start)*(i+.5)/8192; exact,_,_=evaluate(et)
            if exact is None: continue
            hi=min(len(master_times)-1,bisect.bisect_left(master_times,et)); lo=max(0,hi-1)
            ta,tb=master_times[lo],master_times[hi]; va,vb=evaluate(ta)[0],evaluate(tb)[0]
            if va and vb and tb!=ta:
                u=(et-ta)/(tb-ta); max_residual=max(max_residual,math.dist(exact,[va[k]+u*(vb[k]-va[k]) for k in range(3)]))
    if seam_probes:
        master.update(seam_probes); master_times=sorted(master)
    # Preserve independently observed unavailable probes as gaps, bracketed by
    # exact states. Coalesce only adjacent grid probes, never draw across a group.
    if failed:
        delta=(end-start)/8192
        groups=[]
        for et in failed:
            if groups and et-groups[-1][-1]<=delta*1.1: groups[-1].append(et)
            else: groups.append([et])
        for group in groups:
            before=max(start,group[0]-delta); after=min(end,group[-1]+delta)
            for boundary in (before,group[0],group[-1],after): evaluate(boundary)
            master.update((before,group[0],group[-1],after))
        master_times=sorted(master)
    # Segment at every failed sample and every body/anchor source-pair seam.
    samples=[]; segments=[]; gaps=[]; active=None; previous_sources=None
    for et in master_times:
        q,b,a=evaluate(et)
        if q is None:
            if active:
                segments.append(active); active=None
            gaps.append({"start_et":et,"end_et":et,"reason":b.get("reason") or a.get("reason") or "unresolved state"})
            previous_sources=None; continue
        bs=_source(inspector.service,body,et)[0]; ass=_source(inspector.service,anchor,et)[0]
        pair=(bs.ephemeris_source_id+"::"+body,ass.ephemeris_source_id+"::"+anchor)
        if active is None or pair!=previous_sources:
            if active: segments.append(active)
            active={"body_source_ref":pair[0],"anchor_source_ref":pair[1],"authority_class":b["authority_class"],"_rows":[]}
        active["_rows"].append((et,q)); previous_sources=pair
    if active: segments.append(active)
    max_simplification=0.0
    master_index={t:i for i,t in enumerate(master_times)}
    levels=[]
    radii=[math.dist(q,(0,0,0)) for q,_,_ in cache.values() if q]
    R=max(radii,default=1.0)
    tolerance=R/128
    for level_id in range(16):
        out=[]; retained_count=0; err=0.0
        for seg in segments:
            rows=seg["_rows"]; pts=[[t,*q] for t,q in rows]
            idx=_rdp(pts,tolerance)
            # T is mandatory whenever it belongs to this valid segment.
            if any(t==T for t,_ in rows):
                ix=next(i for i,(t,_) in enumerate(rows) if t==T); idx=sorted(set(idx+[ix]))
            selected=set(idx)
            for j,p in enumerate(pts):
                lo=max((i for i in idx if i<=j),default=idx[0]); hi=min((i for i in idx if i>=j),default=idx[-1])
                a0,b0=p[1:],pts[hi][1:]; a1=pts[lo][1:]; d=[b0[k]-a1[k] for k in range(3)]; den=sum(x*x for x in d)
                u=min(1,max(0,sum((p[k+1]-a1[k])*d[k] for k in range(3))/den)) if den else 0
                err=max(err,math.dist(p[1:],[a1[k]+u*d[k] for k in range(3)]))
            out.append({"body_source_ref":seg["body_source_ref"],"anchor_source_ref":seg["anchor_source_ref"],"authority_class":seg["authority_class"],
                        "sample_indices":[master_index[rows[i][0]] for i in idx],
                        "points":[pts[i] for i in idx]})
            retained_count+=len(idx)
        if levels and retained_count==sum(len(s["points"]) for s in levels[-1]["segments"]): break
        levels.append({"segments":out,"error":err,"vertices":retained_count})
        max_simplification=max(max_simplification,err)
        if tolerance<=epsilon: break
        tolerance=max(epsilon,tolerance/4)
    # Finest is exact master; append if simplification ladder did not reach it.
    if not levels or levels[-1]["vertices"] != sum(len(s["_rows"]) for s in segments):
        levels.append({"segments":[{"body_source_ref":s["body_source_ref"],"anchor_source_ref":s["anchor_source_ref"],"authority_class":s["authority_class"],
                                    "sample_indices":[master_index[t] for t,_ in s["_rows"]],"points":[[t,*q] for t,q in s["_rows"]]} for s in segments],"error":0.0,"vertices":sum(len(s["_rows"]) for s in segments)})
    audit={"body_id":body,"anchor_id":anchor,"frame":SPICE_FRAME,"samples":[{"et":t,"relative_position_km":q,
        "body_resolution":b["resolution"],"anchor_resolution":a["resolution"],"body_reason":b.get("reason"),"anchor_reason":a.get("reason"),
        "body_state":({"position_km":b["state"]["position_km"],"velocity_km_s":b["state"]["velocity_km_s"],"provenance":b["state"]["provenance"]} if "state" in b else None),
        "anchor_state":({"position_km":a["state"]["position_km"],"velocity_km_s":a["state"]["velocity_km_s"],"provenance":a["state"]["provenance"]} if "state" in a else None)}
        for t,(q,b,a) in ((t,cache[struct.pack(">d",t)]) for t in master_times)]}
    status="SAMPLING_LIMIT" if limited or max_residual>epsilon else ("PARTIAL" if gaps or failed else "AVAILABLE")
    return {"levels":levels,"gaps":gaps,"audit":audit,"status":status,"probe_error":max_residual,"worst_et":worst,
            "epsilon":epsilon,"cache_count":len(cache),"failed_probes":len(failed),"horizon":plan,"master_count":len(master_times)}


def _write_resource(root, directory, value):
    data=resource_bytes(value); uri=f"{directory}/{data['sha256']}.json"
    path=root/uri; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(canonical_bytes(value))
    (path.with_suffix(path.suffix+".gz")).write_bytes(data["gzip"])
    return {"uri":uri,"sha256":data["sha256"],"bytes":data["bytes"],"gzip_bytes":len(data["gzip"])}


def compile_product(database, asset_root, output, epoch="2226-01-01T00:00:00 TDB"):
    if epoch != "2226-01-01T00:00:00 TDB": raise ValueError("prototype epoch is fixed by generation spec")
    ledger,registry,manifest_hashes=load_authority(database,asset_root)
    service=SpiceEphemerisAdapter(registry).service()
    inspector=Inspector(ledger,registry,service,manifest_hashes,max_orbit_years=100)
    et=inspector.time.parse(epoch)
    if et != T: raise ValueError("epoch codec did not produce the pinned numeric ET")
    baseline=json.loads((ROOT/"engineering/solar_basemap/evidence/catalog_2226_snapshot.json").read_text())
    if inspector.authority["ledger_sha256"]!=baseline["authority"]["ledger_sha256"] or manifest_hashes!=baseline["authority"]["manifest_sha256"]:
        raise ValueError("live authority identity differs from qualified architecture snapshot; audit diff before build")
    output=Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        if not (output/"current.json").is_file():raise FileExistsError(f"nonempty output has no validated current pointer: {output}")
        validate_product(output)
    output.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix=".basemap-build-",dir=output))
    try:
        snap=inspector.snapshot(et)
        rows={r["body_id"]:r for r in snap["objects"]}
        if len(rows)!=110: raise ValueError("authority catalog changed: expected 110 IDs; audit before proceeding")
        expected_ids={r["body_id"] for r in baseline["objects"]}
        keys=("catalog","resolved","direct","propagated","unresolved")
        expected_counts={k:baseline["counts"][k] for k in keys}
        actual_counts={k:snap["counts"][k] for k in keys}
        if set(rows)!=expected_ids or actual_counts!=expected_counts:
            raise ValueError(f"epoch authority resolution differs from qualification snapshot: expected={expected_counts} actual={actual_counts} ids_same={set(rows)==expected_ids}")
        positions={k:_vec(v) for k,v in rows.items() if v["resolution"]=="RESOLVED"}
        spec=json.loads(SPEC_PATH.read_text())
        spec_bytes=canonical_bytes(spec); spec_desc=_write_resource(stage,"objects",spec)
        build_spec_id=hashlib.sha256(canonical_bytes({"authority":inspector.authority,"generation":spec})).hexdigest()
        requested,local_systems,omissions=_derive_curve_inventory(rows,spec)
        family_anchor={body:family["anchor_id"] for family in local_systems for body in family["member_ids"]}
        curves_by_node={}; compiled_by_body={}; source_rows={}; sample_resources=[]; counts={}
        def add_source_ref(raw_source_id,owner):
            ref=f"{raw_source_id}::{owner}"
            if ref in source_rows:return ref
            src=registry.sources[raw_source_id]
            covered=[c for c in registry.coverage if c.ephemeris_source_id==raw_source_id and c.body_id in (None,owner)
                     and c.status=="QUALIFIED" and c.coverage_start_et is not None and c.coverage_end_et is not None]
            if not covered:raise ValueError(f"source provenance has no qualified numeric ET coverage: {ref}")
            source_rows[ref]={"source_ref":ref,"body_id":owner,"source_id":raw_source_id,"asset_sha256":src.sha256,
                "capability":src.state_capability,"navigation_grade":src.navigation_grade,"uncertainty_km":src.uncertainty_km,
                "coverage_start_et":min(c.coverage_start_et for c in covered),"coverage_end_et":max(c.coverage_end_et for c in covered),
                "lineage":src.source_lineage}
            return ref
        for body,row in rows.items():
            if row["resolution"]=="RESOLVED":
                add_source_ref(row["state"]["provenance"]["ephemeris_source_id"],body)
        for body,anchor in sorted(requested.items()):
            plan=inspector.automatic_plan(body,et)
            compiled=_curve_sampling(inspector,body,anchor,plan)
            semantic="HELIOCENTRIC_REFERENCE_ORBIT" if anchor=="SUN" else "PARENT_RELATIVE_REFERENCE_ORBIT"
            audit_val={"schema":"loom.solar-basemap.audit/0.1","body_id":body,"anchor_id":anchor,"epoch_et":et,
                       "frame":SPICE_FRAME,"units":"km","aberration":"NONE","physical_state_center":"SUN",
                       "cartographic_semantic":semantic,"horizon":plan,"sample_count":compiled["master_count"],
                       "samples":compiled["audit"]["samples"],"extensions":{}}
            audit_desc=_write_resource(stage,"provenance",audit_val); sample_resources.append(audit_desc)
            curve_base={"feature_id":body,"semantic":semantic,"anchor_id":anchor,"horizon_reference_id":plan["orbital_reference_center"],"frame":SPICE_FRAME,
                "start_et":plan["start_et"],"end_et":plan["end_et"],"horizon_status":plan["status"],"closed":False,
                "geometry_status":compiled["status"],"segments":[],"gaps":compiled["gaps"],"source_refs":[],"audit":audit_desc,
                "error":{"sampling_probe_error_km":compiled["probe_error"],"simplification_error_km":max((x["error"] for x in compiled["levels"]),default=0),
                         "sampling_status":"SAMPLING_LIMIT" if compiled["status"]=="SAMPLING_LIMIT" else "VALIDATED_PROBES","gpu_budget_css_px":.25}}
            curve_base["source_refs"]=sorted({ref for segment in compiled["levels"][-1]["segments"] for ref in (segment["body_source_ref"],segment["anchor_source_ref"])})
            node_id=f"system:{anchor}" if anchor!="SUN" else "solar"
            levels=[]
            compiled_by_body[body]={"node_id":node_id,"curve":curve_base,"compiled":compiled}
            curves_by_node.setdefault(node_id,[]).append(curve_base)
            counts[body]=compiled
            for seg in compiled["levels"][-1]["segments"]:
                for source_id in (seg["body_source_ref"],seg["anchor_source_ref"]):
                    raw_source_id,owner=source_id.split("::",1)
                    add_source_ref(raw_source_id,owner)
        # One independently loadable package per semantic node and nested level.
        node_levels={}
        for node_id in sorted(curves_by_node):
            bodies=[b for b,v in compiled_by_body.items() if v["node_id"]==node_id]
            max_count=max((len(compiled_by_body[b]["compiled"]["levels"]) for b in bodies),default=0)
            descriptors=[]
            for level_id in range(max_count):
                curves=[]; errors=[]; vertices=segments=0
                for body in sorted(bodies):
                    record=compiled_by_body[body]; lvls=record["compiled"]["levels"]
                    use=lvls[min(level_id,len(lvls)-1)]
                    curves.append({**record["curve"],"segments":use["segments"]})
                    errors.append(record["compiled"]["probe_error"]+use["error"])
                    vertices+=use["vertices"]; segments+=len(use["segments"])
                chunk={"schema":"loom.solar-basemap.chunk/0.1","build_spec_id":build_spec_id,"node_id":node_id,"level":level_id,"curves":curves,"extensions":{}}
                desc=_write_resource(stage,"objects",chunk)
                descriptors.append({"level":level_id,"resource":desc,"measured_error_km":max(errors,default=0),"vertices":vertices,"segments":segments})
            node_levels[node_id]=descriptors
        root_nodes=[]
        features=[]
        body_to_node={}
        omission_by_body={row["body_id"]:row for row in omissions}
        generated_local_anchors={v["node_id"].removeprefix("system:") for v in compiled_by_body.values() if v["node_id"]!="solar"}
        for body,row in rows.items():
            local_anchor=family_anchor.get(body)
            node_id=f"system:{local_anchor}" if local_anchor in generated_local_anchors else "solar"
            body_to_node[body]=node_id
            geom=("UNRESOLVED" if row["resolution"]!="RESOLVED" or body in omission_by_body else
                  counts[body]["status"] if body in requested else "NOT_REQUESTED")
            reason=row.get("reason") or (omission_by_body.get(body) or {}).get("reason")
            features.append({"body_id":body,"name":row["canonical_name"],"body_class":row["body_class"],"catalog_parent_id":row.get("parent_body_id"),
                "resolution":row["resolution"],"reason":reason,"position_semantic":"PHYSICAL_EPOCH_POSITION",
                "position_km":positions.get(body),"source_ref":(f"{row['state']['provenance']['ephemeris_source_id']}::{body}" if row["resolution"]=="RESOLVED" else None),"geometry_status":geom,"node_id":node_id})
        anchor_ids={"SUN"}|generated_local_anchors
        inventory_by_anchor={x["anchor_id"]:x for x in local_systems}
        for system in local_systems:
            anchor=system["anchor_id"]
            member_compiled=[counts[b] for b in system["member_ids"] if b in counts]
            useful=any(any(len(seg["points"])>=2 for seg in level["segments"])
                       for result in member_compiled for level in result["levels"])
            resolved_member=any(rows[b]["resolution"]=="RESOLVED" for b in system["member_ids"])
            member_omissions=[x for x in omissions if x.get("anchor_id")==anchor or x.get("body_id") in system["member_ids"]]
            if useful:
                system["classification"]="QUALIFIED_SOURCE_AVAILABLE"
            elif any(x["classification"]=="UNRESOLVED_IDENTITY" for x in member_omissions) and not resolved_member:
                system["classification"]="UNRESOLVED_IDENTITY"
            elif any(x["classification"]=="MISSING_REQUIRED_SOURCE" for x in member_omissions):
                system["classification"]="MISSING_REQUIRED_SOURCE"
            elif resolved_member:
                system["classification"]="GOVERNED_POSITION_ONLY"
            else:
                system["classification"]="OUT_OF_SCOPE_BY_CONTRACT"
            system["node_id"]=f"system:{anchor}" if anchor in generated_local_anchors else None
            system["generated_curve_ids"]=sorted(b for b in system["member_ids"] if b in counts)
            system["omissions"]=sorted(member_omissions,key=lambda x:x["body_id"])
        inventory_by_body={x["body_id"]:x for x in omissions}
        for omission in omissions:
            family_anchor_id=omission.get("anchor_id")
            if family_anchor_id in inventory_by_anchor:
                continue
            # Preserve unanchored or ambiguous identities in the product inventory.
            local_systems.append({"anchor_id":None,"candidate_parent_id":omission.get("parent_body_id"),
                "candidate_id":f"unresolved:{omission['body_id']}","node_id":None,"member_ids":[omission["body_id"]],
                "generated_curve_ids":[],"classification":omission["classification"],"omissions":[omission],"explicit_relationships":[]})
        for system in local_systems:
            for omission in system.get("omissions",[]):
                omission.setdefault("anchor_id",system.get("anchor_id"))
        for anchor in sorted(anchor_ids):
            nid="solar" if anchor=="SUN" else f"system:{anchor}"
            if anchor not in positions:
                raise ValueError(f"governed cartographic anchor unresolved at publication epoch: {anchor}")
            anchor_pos=positions[anchor]
            members=sorted(body for body in requested if requested[body]==anchor)
            levels=node_levels.get(nid,[])
            local_position_bodies=[b for b in positions if body_to_node.get(b)==nid]
            curve_points=[point[1:] for b,item in compiled_by_body.items() if item["node_id"]==nid
                          for segment in item["compiled"]["levels"][-1]["segments"] for point in segment["points"]]
            extent=max([math.dist(positions[b],anchor_pos) for b in local_position_bodies]+
                       [math.dist(point,(0,0,0)) for point in curve_points],default=0)
            if anchor=="SUN":
                subtree_extent=max([math.dist(positions[b],anchor_pos) for b in positions]+
                    [math.dist(positions[a],anchor_pos)+max((math.dist(point,(0,0,0)) for point in
                     [p[1:] for b,item in compiled_by_body.items() if item["node_id"]==f"system:{a}"
                      for seg in item["compiled"]["levels"][-1]["segments"] for p in seg["points"]]),default=0)
                     for a in generated_local_anchors],default=0)
                children=sorted(f"system:{a}" for a in generated_local_anchors)
            else:
                subtree_extent=extent
                children=[]
            root_nodes.append({"node_id":nid,"parent_node_id":None if nid=="solar" else "solar","anchor_id":anchor,"anchor_position_km":anchor_pos,
                "content_bound":{"center_km":[0,0,0],"radius_km":extent},
                "subtree_bound":{"center_km":[0,0,0],"radius_km":subtree_extent},
                "members":members,"children":children,"levels":levels})
        # Ship only the heliocentric level useful at Solar overview; finer
        # heliocentric packages remain lazy. Pixel-sized CSS viewport is the
        # conservative root error basis specified by the acceptance plan.
        root_scale=915/(2*math.tan(math.pi/8)*(50*149597870.7))
        planet_ids={body for body,row in rows.items()
                    if row["body_class"] in spec["reference_curve_policy"]["heliocentric_body_classes"]}
        local_parent_context_curve_ids=generated_local_anchors-planet_ids
        embedded_curve_levels={}; embedded_level=0; coarse=[]
        for body in sorted(requested):
            item=compiled_by_body[body]
            if item["node_id"]=="solar":
                if body in local_parent_context_curve_ids:
                    # These exact anchor arcs are parent-context ink for a
                    # local-system approach. Keep them in progressive Solar
                    # chunks, not the initial root payload.
                    coarse.append({**item["curve"],"segments":[]})
                    continue
                curve_level,error_km=_initial_curve_level(item["compiled"]["levels"],item["compiled"]["probe_error"],root_scale,.75)
                embedded_level=max(embedded_level,curve_level)
                embedded_curve_levels[body]={"level":curve_level,"measured_error_km":error_km,"measured_error_css_px":error_km*root_scale}
                level=item["compiled"]["levels"][curve_level]
                coarse.append({**item["curve"],"segments":level["segments"]})
            else:
                coarse.append({**item["curve"],"segments":[]})
        omission_by_body={x["body_id"]:x for x in omissions}
        for system in local_systems:
            for body in system.get("member_ids",[]):
                if body in omission_by_body:
                    omission_by_body[body].setdefault("anchor_id",system.get("anchor_id"))
        root={"schema":"loom.solar-basemap.root/0.1","build_spec_id":build_spec_id,"epoch_et":T,"features":sorted(features,key=lambda f:f["body_id"]),
              "nodes":root_nodes,"curves":coarse,"extensions":{
                "org.loom.solar-basemap.client/0.1":{"solar_embedded_level":embedded_level,
                  "solar_embedded_curves":embedded_curve_levels,
                  "root_error_basis":{"viewport_css_height":915,"vertical_fov_degrees":45,
                    "camera_distance_km":50*149597870.7,"max_sse_css_px":.75}},
                "org.loom.solar-basemap.local-system-coverage/0.1":{"classification_values":list(LOCAL_SYSTEM_CLASSES),
                  "systems":sorted(local_systems,key=lambda x:(x.get("anchor_id") or "",x.get("candidate_id") or "")),
                  "solar_parent_context_curve_ids":sorted(local_parent_context_curve_ids),
                  "unanchored_member_omissions":sorted([x for x in omissions if not x.get("anchor_id")],key=lambda x:x["body_id"])}}}
        source_dict={"schema":"loom.solar-basemap.provenance/0.1","build_spec_id":build_spec_id,"sources":sorted(source_rows.values(),key=lambda x:x["source_ref"]),
                     "sample_resources":sorted(sample_resources,key=lambda x:x["sha256"]),"extensions":{}}
        provenance_desc=_write_resource(stage,"provenance",source_dict)
        root_desc=_write_resource(stage,"objects",root)
        raw_ledger=canonical_bytes(ledger); canonical_ledger_hash=hashlib.sha256(raw_ledger).hexdigest()
        # Kernel identity inventory includes each source actually used.
        used_ids=set(source_rows); assets={}
        for ref in used_ids:
            sid=ref.split("::",1)[0]
            for asset in registry.sources[sid].kernel_assets:
                assets[(ref,asset.sha256)]=(asset.sha256,asset.byte_count or 0,sid)
        import spiceypy
        inputs={"resolver_git_sha":os.popen("git rev-parse HEAD").read().strip(),"resolver_module_hashes":{n:sha(ROOT/n) for n in ("src/loom_solar_postgres.py","src/loom_spice_ephemeris_adapter.py","src/loom_solar_inspector.py","src/loom_solar_time.py")},
            "compiler_git_sha":os.popen("git rev-parse HEAD").read().strip(),"compiler_module_hashes":{"src/loom_solar_basemap_compile.py":sha(__file__)},
            "toolchain":{"python":platform.python_version(),"spiceypy":spiceypy.__version__,"cspice":str(spiceypy.tkvrsn("TOOLKIT")),"platform":platform.platform()},
            "epoch_binary64_hex":struct.pack(">d",T).hex(),"kernel_assets":[{"sha256":x[0],"bytes":x[1],"source_id":x[2]} for x in sorted(assets.values())]}
        # Digest compiler-relevant inputs, semantic generation, and authority identities.
        manifest={"schema":"loom.solar-basemap.manifest/0.1","build_spec_id":build_spec_id,"epoch_et":T,"epoch_tdb":inspector.time.label(T),"frame":SPICE_FRAME,
          "center":"SUN","units":"km","aberration":"NONE","authority":{"ledger_sha256":inspector.authority["ledger_sha256"],"canonical_ledger_sha256":canonical_ledger_hash,
          "manifest_sha256":manifest_hashes,"sample_source_dictionary":provenance_desc},"inputs":inputs,"generation":{"spec_version":spec["spec_version"],"anchor_policy":spec["anchor_policy"],
          "horizon_policy":spec["horizon_policy"],"sampling_policy":spec["sampling_policy"]["id"],"simplification_policy":spec["simplification_policy"]["id"],
          "serialization_policy":spec["serialization_policy"],"client_policy":spec["client_policy"]["id"],"spec":spec_desc},"root":root_desc,"provenance":provenance_desc,
          "counts":{"catalog":len(rows),"resolved":snap["counts"]["resolved"],"unresolved":snap["counts"]["unresolved"],"requested_curves":len(requested),
          "available_curves":sum(c["status"] in ("AVAILABLE","PARTIAL") for c in counts.values())},"extensions":{}}
        manifest["build_id"]=hashlib.sha256(canonical_bytes(manifest)).hexdigest()
        build_dir=stage/f"builds/{manifest['build_id']}"; build_dir.mkdir(parents=True)
        mbytes=canonical_bytes(manifest); (build_dir/"manifest.json").write_bytes(mbytes); (build_dir/"manifest.json.gz").write_bytes(gzip.compress(mbytes,mtime=0))
        staged_pointer={"build_id":manifest["build_id"],"manifest_uri":f"builds/{manifest['build_id']}/manifest.json","manifest_sha256":hashlib.sha256(mbytes).hexdigest()}
        (stage/"current.json").write_bytes(canonical_bytes(staged_pointer))
        validate_product(stage)
        # Preserve all prior output content; atomically promote one validated build and pointer.
        target=output/f"builds/{manifest['build_id']}"; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(build_dir,target,dirs_exist_ok=True)
        for directory in ("objects","provenance"):
            dest=output/directory; dest.mkdir(exist_ok=True)
            shutil.copytree(stage/directory,dest,dirs_exist_ok=True)
        ptr={"build_id":manifest["build_id"],"manifest_uri":f"builds/{manifest['build_id']}/manifest.json","manifest_sha256":hashlib.sha256(mbytes).hexdigest()}
        tmp=output/"current.json.tmp"; tmp.write_bytes(canonical_bytes(ptr)); os.replace(tmp,output/"current.json")
        report={"build_id":manifest["build_id"],"build_spec_id":build_spec_id,"catalog":snap["counts"],"root_gzip_bytes":root_desc["gzip_bytes"],
                "manifest_gzip_bytes":len(gzip.compress(mbytes,mtime=0)),"initial_product_gzip_bytes":root_desc["gzip_bytes"]+len(gzip.compress(mbytes,mtime=0)),
                "curves":{k:{x:v[x] for x in ("status","probe_error","epsilon","cache_count","master_count","failed_probes")} for k,v in counts.items()}}
        (output/"reproducibility-report.json").write_bytes(canonical_bytes(report))
        return manifest,report
    finally:
        shutil.rmtree(stage,ignore_errors=True)
