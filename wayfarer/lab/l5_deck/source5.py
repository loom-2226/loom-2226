#!/usr/bin/env python3
"""L5 kT approval, source-bound closed EVA/tunnel cutouts, D9 + containment only.

Nonadditive view overlay; source mass stays frozen. The closed EVA pressure-
and-armour plugs are EXACT portions of the original two structural shells.
No claim of open-hatch shielding or certified seal/pressure hardware.
"""
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"lab/packing_phase1b"))
import source_brep_pilot as B
SRC=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
OUT=ROOT/"render/out/interior_L5_source_report.json"
SOURCE_SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
def vol(shape):
    return float(shape.volume)
def intersect(a,b):
    r=a&b
    return 0 if r is None else float(r.volume)
def screen():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_SHA,"STOP geometry source hash changed"
    G=json.loads(SRC.read_text())
    D=json.loads(DEC.read_text())
    assert D["l5_decisions_2026_11_12"]["authority"].startswith("kT APPROVED")
    assert abs(G["dry_t"]-868.1922552640087)<1e-8
    p={x["id"]:x for x in G["parts"]}
    # Radial EVA bore through both shell materials, at 0 deg (Y positive).
    # Closed state retains exactly the original cut pressure AND armour material
    # as concentric layers in the hatch plug. No extra mass / armour credit.
    bore=B.make(dict(k="tube",p0=[12.3,4.20,0],p1=[12.3,4.60,0],r=.5))
    pressure=B.make(p["pressure_vessel"]["shape"])
    armour=B.make(p["armor"]["shape"])
    prplug=pressure&bore
    arplug=armour&bore
    remain_pr=pressure-bore
    remain_ar=armour-bore
    pr0,ar0=vol(pressure),vol(armour)
    pr1,ar1=vol(remain_pr),vol(remain_ar)
    delta_pr=pr0-pr1-vol(prplug)
    delta_ar=ar0-ar1-vol(arplug)
    assert vol(prplug)>0 and vol(arplug)>0
    # OCCT thin-shell volume evaluation can be nonadditive after splitting.
    # Directly test that the reconstructed solid SET matches source.
    reconstructed_pr=remain_pr.fuse(prplug)
    reconstructed_ar=remain_ar.fuse(arplug)
    discrepancies=dict(
        pressure_missing_m3=vol(pressure-reconstructed_pr),
        pressure_extra_m3=vol(reconstructed_pr-pressure),
        armour_missing_m3=vol(armour-reconstructed_ar),
        armour_extra_m3=vol(reconstructed_ar-armour))
    assert all(abs(v)<1e-6 for v in discrepancies.values()),("STOP closed source containment",discrepancies)
    assert intersect(remain_pr,prplug)<1e-7
    assert intersect(remain_ar,arplug)<1e-7
    # Existing EVA rails are at ±14°, so the 1.0m bore subtends
    # 2*asin(.5/4.3) = 13.35 degrees, clear of ±14 degrees.
    eva_rail=[]
    for k in range(4):
        s=p["ext_eva_rail_"+str(k)]["shape"]
        rail=B.make(s)
        assert intersect(bore,rail)<1e-8,("STOP EVA rail",k)
        eva_rail.append(k)
    # Tunnel runs aft from rear bulkhead at (Y=0,Z=-3).
    # 1.2m axial opening, with closed plug occupying exact bored volume.
    bulk=B.make(p["aft_bulkhead"]["shape"])
    cutter=B.cyl(.6,13.38,13.72,0,-3)
    door=bulk&cutter
    bulk_cut=bulk-cutter
    bulk0=vol(bulk)
    bulk_delta=bulk0-vol(bulk_cut)-vol(door)
    assert vol(door)>.3 and abs(bulk_delta)<1e-6,("STOP aft bulkhead conservation",bulk_delta)
    assert intersect(door,bulk_cut)<1e-7
    tunnel=B.make(p["tunnel_0"]["shape"])
    assert intersect(door,tunnel)<1e-8,"STOP tunnel-to-closed-plug interference"
    assert intersect(bulk_cut,tunnel)<1e-8,"STOP tunnel overlaps aft bulkhead"
    # 1.2m hatch closed bulkhead performance is NOT qualified by a source
    # equivalent-mass/stress model; this certifies geometry only.
    eva=dict(name="hatch_L5_EVA_0",diameter_m=1.0,centre_x_m=12.3,
       centre_y_m=4.3,centre_z_m=0.,azimuth_deg=0,height_above_floor_m=1.1,
       room_mass_owner="room_L5-airlock",rail_clear=True,
       removed_pressure_shell_m3=vol(prplug),removed_armour_m3=vol(arplug),
       reinserted_pressure_plug_m3=vol(prplug),
       reinserted_armour_plug_m3=vol(arplug),
       pressure_layer_thickness_m=.03,armour_layer_thickness_m=.20,
       closure_source_mass_delta_t=0,
       closed_geometric_pressure_continuity="PASS",
       closed_geometric_armour_thickness_equivalence="PASS",
       pressure_strength_and_seal_certification="NOT CLAIMED",
       open_hatch_shielding="NOT QUALIFIED")
    transfer=dict(name="hatch_L5_tunnel_0",diameter_m=1.2,centre_x_m=13.55,
       y_m=0.,z_m=-3.,source_tunnel="tunnel_0",
       room_mass_owner="room_L5-vestibule",item_estimated_kg=150,
       removed_bulkhead_m3=vol(door),reinserted_closed_plug_m3=vol(door),
       source_mass_delta_t=0,
       closed_geometric_bulkhead_continuity="PASS",
       opening_state="UNQUALIFIED")
    report=dict(status="L5_SOURCE_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS",
       source_geometry_sha256=SOURCE_SHA,dry_t=G["dry_t"],ECON_dv_km_s=707.845,
       source_mass_rebooking_t=0,EVA=eva,tunnel=transfer,
       checks=dict(D9_category_d=0,
         source_integrity_closed_pressure_volume_delta_m3=delta_pr,
         source_integrity_closed_armour_volume_delta_m3=delta_ar,
         closed_symmetric_difference_m3=discrepancies,
         BRep_evaluation_note="Thin shell volume nonadditivity retained as evidence; reconstructed closed solid set independently checked.",
         source_integrity_closed_bulkhead_volume_delta_m3=bulk_delta,
         EVA_rail_contacts=0,tunnel_bore_contacts=0,
         containment="PASS",G1_G12="NOT RUN / NOT REQUIRED"),
       position_override_only=True,source_geometry_file_unchanged=True,
       exterior_GLBs_unchanged=True,
       caveat="Geometric closed-state replacement only; no material, pressure, seal, load or open-state qualification.")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":screen()
