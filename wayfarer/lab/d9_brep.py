"""D9: exact source-derived solid intersections, current Wayfarer geometry.

No auto-notching. No inferred installed clearance for excluded no_render
proxies. Retains the pinned #156 build123d/OpenCascade conversion and
classification rules; when a real category-(d) overlap exceeds 0.01m3
the candidate is BLOCKED until kT directs an equipment change.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"packing_phase1b"))
import source_brep_pilot as P
import source_brep_triage as T

GEO=HERE.parent/"results/out/wayfarer_v05_geometry.json"
REPORT=HERE.parent/"results/out/D9_BREP_CLASH_REPORT.json"

def run():
    raw=GEO.read_bytes()
    G=json.loads(raw)
    sha=hashlib.sha256(raw).hexdigest()
    parts=[]
    excluded=[]
    for row in G["parts"]:
        name="dry:"+row["id"]
        if "no_render" in row.get("tags",[]):
            excluded.append({"id":name,"mass_t":row["mass_t"],
                            "why":"authored no_render/unlocated proxy: no installed B-rep clearance claim"})
            continue
        parts.append((name,row))
    for i,row in enumerate(G["fluids_by_state"]["S1"]):
        name=f"S1:{row['id']}:{i:02d}"
        if "no_render" in row.get("tags",[]):
            excluded.append({"id":name,"mass_t":row["mass_t"],"why":"explicit non-physical fluid marker"})
            continue
        parts.append((name,row))

    shapes=[]
    errors=[]
    for name,row in parts:
        try:
            solid=P.make(P.settled(row["shape"]))
            if not solid.is_valid: raise ValueError("invalid B-rep")
            if solid.volume<=0: raise ValueError("nonpositive volume")
            shapes.append((name,solid,P.bounds(solid)))
        except Exception as e:
            errors.append({"id":name,"error":f"{type(e).__name__}: {e}"})
    hits=[]
    counts=Counter()
    potential_pairs=len(parts)*(len(parts)-1)//2
    evaluated_pairs=0
    aabb_rejected=0
    for i,(an,ash,ab) in enumerate(shapes):
        for bn,bsh,bb in shapes[i+1:]:
            evaluated_pairs+=1
            if P.bbox_intersection_upper(ab,bb)<=.01:
                aabb_rejected+=1
                continue
            try:
                common=ash & bsh
                # OpenCascade returns None for a genuinely empty common
                # (including AABBs whose enclosing boxes overlap).
                # That is NO physical collision, not a CAD failure.
                if common is None:continue
                v=float(common.volume)
                if v <= .01:continue
                cat,why=T.classify({"a":an,"b":bn})
                if cat not in ("a","b","c","d"):
                    raise ValueError(f"unknown triage {cat}")
                counts[cat]+=1
                hits.append({"a":an,"b":bn,"m3":round(v,8),
                             "category":cat,"why":why})
            except Exception as e:
                errors.append({"a":an,"b":bn,"error":f"{type(e).__name__}: {e}"})
    d=sorted((row for row in hits if row["category"]=="d"),
             key=lambda x:-x["m3"])
    passed=(not errors and not d and
            len(shapes)==len(parts) and evaluated_pairs==potential_pairs)
    out={
        "authority":"NON-QUALIFICATION Phase 1b D9 numerical installed-solid BRep check",
        "geometry_sha256":sha,
        "builder":"source_brep_pilot.py copied from research #156 exact B-rep converter; build123d 0.13.0/OpenCascade",
        "classifier":"source_brep_triage.py copied from research #156, never auto-resolves clashes",
        "threshold_m3":.01,
        "dry_source_parts":len(G["parts"]),
        "S1_source_fluids":len(G["fluids_by_state"]["S1"]),
        "modelled_solids":len(shapes),
        "excluded_source_no_render_proxy_count":len(excluded),
        "excluded_source_no_render_proxy_mass_t":sum(x["mass_t"] for x in excluded),
        "excluded_source_proxies":excluded,
        "pair_count":evaluated_pairs,
        "expected_pairs":potential_pairs,
        "aabb_rejected":aabb_rejected,
        "intersection_category_counts":dict(counts),
        "category_d_count":len(d),
        "category_d_conflicts":d,
        "all_volumetric_hits_over_0p01_m3":hits,
        "geometry_conversion_or_boolean_errors":errors,
        "pass":passed,
        "limits":"This certifies only represented installed BReps: no_render allocations, unlocated tank webs/baffles, unplaced structural D8 doublers, cryo tank walls and moving sweeps are still OPEN.",
    }
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=1)+"\n")
    print("D9",json.dumps({k:out[k] for k in
          ("geometry_sha256","modelled_solids","pair_count",
           "excluded_source_no_render_proxy_count","category_d_count","pass")}),flush=True)
    print("D9_TOP_10",json.dumps(d[:10]),flush=True)
    if errors:
        print("D9_ERRORS",json.dumps(errors[:10]),flush=True)
    return 0 if passed else 1

if __name__=="__main__":
    raise SystemExit(run())
