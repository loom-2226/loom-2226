#!/usr/bin/env python3
"""kT 2026-11-13 non-canon exterior B + three true WWS-1 medical BRep holes.

One visual six-state candidate, not a canon release. The source geometry,
mass inventory, released six GLBs and canon_glb.json pointer are untouched.
Full six-state D9 and containment are the standard source-aware exporter checks.
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"))
import exterior_detail_f3_20261110 as F

PREFIX="wayfarer_exterior_B_medical_88ce19fc"
P=ROOT/"render/out"
SOURCE=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
EVA=ROOT/"render/out/interior_L5_source_report.json"
SOURCE_SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
DRY=868.1922552640087
DV=707.845
def mark_visual_glb(path,mode,pose):
    raw=path.read_bytes()
    assert raw[:4]==b"glTF" and struct.unpack_from("<I",raw,8)[0]==len(raw)
    size,kind=struct.unpack_from("<II",raw,12)
    assert kind==0x4e4f534a
    doc=json.loads(raw[20:20+size])
    tail=raw[20+size:]
    doc.setdefault("extras",{}).update(
        source_geometry_sha256=SOURCE_SHA,
        geometry_status="NON_CANON_WWS1_VISUAL_EXTERIOR_OVERLAY",
        canon_released_assets_untouched=True,
        medical_port_overlay_x_m=[9.10,9.30],
        medical_port_azimuth_deg=[180,210,240],
        actual_hull_and_armour_BRep_holes=True,
        material_or_pressure_qualification="NOT CLAIMED",
        mass_rebooking_t=0,
        six_state_mode=mode,crown_pose=pose)
    for node in doc["nodes"]:
        ex=node.setdefault("extras",{})
        ex["geometry_status"]="NON_CANON_WWS1_VISUAL_EXTERIOR_OVERLAY"
        ex["WWS1_pressure_shielding_qualification"]="NOT CLAIMED"
        ex["mass_rebooking_t"]=0
        # Existing source canonical tags are provenance, NOT this asset's
        # release status; explicitly keep the two separate.
        ex["canon_provenance_only"]=True
    j=json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode()
    j+=b" "*((-len(j))%4)
    cooked=struct.pack("<III",0x46546c67,2,20+len(j)+len(tail))+struct.pack("<II",len(j),0x4e4f534a)+j+tail
    path.write_bytes(cooked)
    assert struct.unpack_from("<I",cooked,8)[0]==len(cooked)
    return dict(path=str(path.relative_to(ROOT)),
        sha256=hashlib.sha256(cooked).hexdigest(),bytes=len(cooked),
        mesh_count=sum("mesh" in n for n in doc["nodes"]),
        original_mass_source_reference_only=True)
def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    src=json.loads(SOURCE.read_text())
    d=json.loads(DEC.read_text())
    assert d["exterior_surface_2026_11_13"]["canon_change"] is False
    assert abs(src["dry_t"]-DRY)<1e-9
    assert d["exterior_surface_2026_11_13"]["mass_rebooking_t"]==0
    feature=next(f for f in src["features"] if f["kind"]=="hatch" and f["room"]=="L5-airlock")
    assert feature["pos"]==[12.25,4.5,0] and feature["d_m"]==1.1
    interior=json.loads(EVA.read_text())["EVA"]
    assert interior["centre_x_m"]==12.3 and interior["diameter_m"]==1.
    x_offset_m=interior["centre_x_m"]-feature["pos"][0]
    assert abs(x_offset_m-.05)<1e-10
    # Caller saves under a NEW prefix, intentionally not the released
    # wayfarer_exterior_detail_88ce19fc_* six-state names.
    F.PREFIX=PREFIX
    F.main(medical_port_visual_overlay=True)
    path=P/(PREFIX+"_report.json")
    report=json.loads(path.read_text())
    assert report["status"]=="F3_EXTERIOR_DETAIL_SIX_STATE_D9_CONTAINMENT_PASS"
    assert report["all_six_state_D9_and_containment"]=="PASS"
    assert abs(report["source_dry_t"]-DRY)<1e-9 and abs(report["ECON_dv_km_s"]-DV)<1e-10,(
         "STOP: source dry or Δv changed",report["source_dry_t"],report["ECON_dv_km_s"])
    assert report["medical_ports_visual_integration"]["actual_PV_armour_BRep_cuts"]
    states={}
    for mode,poses in report["six_states"].items():
        for pose,details in poses.items():
            assert details["category_d_count"]==0
            assert details["boolean_errors"]==0
            assert details["pressure_containment_pass"]
            file=P/(PREFIX+"_"+mode+"_"+pose+".glb")
            assert file.exists() and file.stat().st_size>40000
            states[mode+"/"+pose]=mark_visual_glb(file,mode,pose)
    assert len(states)==6
    result=dict(status="VISUAL_EXTERIOR_B_MEDICAL_3X2_D9_CONTAINMENT_PASS",
        release_class="NON_CANON_WWS1_VISUAL_ONLY",
        authority="exterior_surface_2026_11_13",
        source_sha256=SOURCE_SHA,source_dry_t=DRY,ECON_dv_km_s=DV,
        mass_rebooking_t=0,G1_G12="NOT RUN / NOT REQUIRED",
        authored_seam_render="wayfarer/render/loomgl.js, shaded demarcations; no BRep gaps",
        medical_ports=dict(original_x_m=9.10,visual_x_m=9.30,
          diameter_m=1.55,azimuths_deg=[180,210,240],
          BRep_pressure_and_armour_cuts=True,
          source_position_modified=False,
          design_status="WWS-1 NON-CANON; pressure/shielding UNQUALIFIED"),
        EVA=dict(source_frame_x_m=12.25,source_frame_d_m=1.1,
          interior_clear_x_m=interior["centre_x_m"],interior_clear_d_m=1.,
          interior_mismatch_axial_m=x_offset_m,unchanged=True),
        D9_category_d_total=0,containment="PASS",
        six_states=states,source_F3_report=PREFIX+"_report.json",
        published_canon_glb_pointer_untouched=True,
        published_six_exterior_GLBS_untouched=True,
        no_canon_tag_or_release=True)
    (P/(PREFIX+"_visual_report.json")).write_text(json.dumps(result,indent=2)+"\n")
    print("NONCANON_VISUAL_SIX_STATE_MEDICAL_HOLES_PASS",json.dumps(
        {k:result[k] for k in ("status","medical_ports","EVA","source_dry_t","ECON_dv_km_s","D9_category_d_total","containment")}),flush=True)
if __name__=="__main__":main()
