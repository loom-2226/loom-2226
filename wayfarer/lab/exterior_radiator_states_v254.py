#!/usr/bin/env python3
"""Step 1 exterior: full-size, non-print radiator state BReps.

From canon-v2.5.3 source positions and booked masses ONLY. Three alternative
poses; not three simultaneous hardware sets. This is a component-stage
candidate, not a whole-ship D9 release. The in-repo G3/canon model is unchanged.
No invented hinge, stowage mechanics, hardware thickness or material credit.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path
from build123d import Color, Compound, Unit, export_gltf, export_step

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from packing_phase1b import source_brep_pilot as P

EXPECTED="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
OUT=ROOT/"render/out"
PREFIX="wayfarer_radiators_step1_88ce19fc"
ANGLES=(40,140,220,320)
STATES=("stowed","metric_hard","torch")

def make(name,spec,colour):
    obj=P.make(spec)
    assert obj is not None and obj.is_valid and obj.volume>0,name
    obj.label=name
    obj.color=Color(colour)
    return obj

def build(g,cfg,mode):
    p={x["id"]:x for x in g["parts"]}
    rad=cfg["radiators"]
    fins=cfg["hot_fins"]
    assert rad["azimuths_deg"]==fins["azimuths_deg"]==list(ANGLES)
    assert rad["x_m"]==[14,32.3] and fins["x_m"]==[34.3,53.3]
    assert rad["pleat_m"]==fins["pleat_m"]==2
    assert rad["torch_span_m"]==4 and rad["span_by_mode_m"]["HARD"]==2
    assert rad["span_by_mode_m"]["LOOM"]==0
    assert fins["pleats"]==14 and fins["deployed_panel_thickness_m"]==.005
    assert fins["root_r_m"]==4.75 and fins["stowed_stack_thickness_m"]==.6
    assert mode in STATES
    parts={}
    mapping={}
    def add(label,shape,mass_source,col):
        assert label not in parts
        parts[label]=make(label,shape,col)
        mapping[label]=mass_source
    for a in ANGLES:
        strake=p["strake_"+str(a)]
        fin=p["hotfin_"+str(a)]
        root=p["hotfin_root_"+str(a)]
        ss=strake["shape"]
        fs=fin["shape"]
        assert ss["k"]=="panel" and ss["a"]==a and ss["x0"]==14 and ss["x1"]==32.3
        assert ss["r0"]==4 and ss["span"]==.5 and ss["t"]==2
        assert fs["k"]=="panel" and fs["a"]==a and fs["x0"]==34.3 and fs["x1"]==53.3
        assert fs["r0"]==4.75 and fs["span"]==2 and fs["t"]==.6
        # Nominal stowed radiating stack and root remain source true solids.
        add(f"dry:strake_{a}:stowed_stack",ss,strake["id"],"#555E65")
        add(f"dry:hotfin_root_{a}:root",root["shape"],root["id"],"#666A73")
        # Strake's 0.06m outward membrane thickness is the existing
        # loomgl.js renderer equivalent, not qualified hardware thickness.
        count={"stowed":0,"metric_hard":1,"torch":2}[mode]
        for n in range(count):
            ext=dict(k="panel",x0=ss["x0"],x1=ss["x1"],a=a,
                     r0=4.5+n*rad["pleat_m"],span=rad["pleat_m"],t=.06)
            add(f"dry:strake_{a}:extended_pleat_{n:02d}",ext,strake["id"],"#66676A")
        if mode!="torch":
            add(f"dry:hotfin_{a}:folded_envelope",fs,fin["id"],"#665C52")
        else:
            # Exactly 14 distinct 2m pleats; physical 5mm declared panel.
            for n in range(fins["pleats"]):
                ex=dict(k="panel",x0=fs["x0"],x1=fs["x1"],a=a,
                        r0=fins["root_r_m"]+n*fins["pleat_m"],
                        span=fins["pleat_m"],t=fins["deployed_panel_thickness_m"])
                add(f"dry:hotfin_{a}:pleat_{n:02d}",ex,fin["id"],"#6A584D")
        # The source 4.256t per fin is consistent with 14*2m*19m,
        # two radiating faces and the source 4kg/m2/face assumption.
        implied=fins["pleats"]*fins["pleat_m"]*(fs["x1"]-fs["x0"])*2*fins["kg_per_m2_face"]/1000
        assert abs(implied-fin["mass_t"])<1e-8
    expected={"stowed":12,"metric_hard":16,"torch":72}[mode]
    assert len(parts)==expected,(mode,len(parts))
    assert len(set(mapping.values()))==12
    return parts,mapping

def component_intersections(parts,cutoff=.01):
    # This checks component self-intersection only; full ship D9 will be
    # required before integration. Two adjacent edges touching are not hits.
    names=sorted(parts)
    hits=[]
    for aa,bb in itertools.combinations(names,2):
        a,b=parts[aa],parts[bb]
        x=P.bounds(a);y=P.bounds(b)
        if any(min(x[2*k+1],y[2*k+1])<=max(x[2*k],y[2*k])
               for k in range(3)):continue
        shared=a&b
        v=0 if shared is None else float(shared.volume)
        if v>cutoff:hits.append(dict(a=aa,b=bb,volume_m3=v))
    return hits

def main():
    raw=GEO.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert sha==EXPECTED,(sha,EXPECTED)
    g=json.loads(raw)
    cfg=json.loads(INPUT.read_text())
    OUT.mkdir(exist_ok=True,parents=True)
    rpt=dict(status="STEP1_EXTERIOR_COMPONENT_DRAWING_CANDIDATE",
             governing_release="canon-v2.5.3",
             source_geometry_sha256=sha,source_mass_changed_t=0,
             three_states_are_mutually_exclusive=True,
             full_ship_D9="PENDING before integration",
             containment="no new internal bodies; original v2.5.3 containment unchanged",
             print_only_geometry_changes=0,
             unfolded_pleat_declared_thickness_m=.005,
             strake_ext_membrane_renderer_equivalent_m=.06,
             stowed_pleat_hinge_and_fold_geometry="OPEN (no sourced hinge dimensions)",
             metric_arrival_qualification="HOLD, viewer operating pose only",
             states={})
    for mode in STATES:
        parts,mapping=build(g,cfg,mode)
        hits=component_intersections(parts)
        assert not hits,(mode,hits)
        geom=Compound(children=list(parts.values()))
        glb=OUT/(PREFIX+"_"+mode+".glb")
        step=OUT/(PREFIX+"_"+mode+".step")
        export_gltf(geom,glb,unit=Unit.M,binary=True,
                    linear_deflection=.03,angular_deflection=.25)
        export_step(geom,step,unit=Unit.M,timestamp="2026-11-09T00:00:00")
        assert glb.stat().st_size>100 and step.stat().st_size>100
        rpt["states"][mode]=dict(nodes=len(parts),hotfin_deployed_pleats=56 if mode=="torch" else 0,
                                 strake_extended_pleats={"stowed":0,"metric_hard":4,"torch":8}[mode],
                                 component_self_intersections_over_0p01m3=hits,
                                 glb=str(glb.relative_to(ROOT)),
                                 step=str(step.relative_to(ROOT)),
                                 source_allocation_ids=sorted(set(mapping.values())),
                                 source_node_to_booked_part=mapping)
        print("STEP1_RADIATOR",mode,len(parts),"NODES","PASS",flush=True)
    path=OUT/(PREFIX+"_report.json")
    path.write_text(json.dumps(rpt,indent=2)+"\n")
    print("STEP1_RADIATORS_READY",path,flush=True)

if __name__=="__main__":
    main()
