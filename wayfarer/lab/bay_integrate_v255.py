#!/usr/bin/env python3
"""Integrate kT 2026-11-10 fitted Drone/Crawler Bay into six full-ship poses.

Source ledger untouched; v2.5.3 crown, original installed BRep and #480
radiator poses are the base. Replace ONLY 8 existing carrier/drone/dock
representations. Preserve the seven crown spare panes at their approved rack.
"""
from __future__ import annotations
import json,hashlib,sys
from pathlib import Path
from build123d import Color,Compound,Unit,export_gltf,export_step
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from bay_fit_v255 import (screen,COURIER_PARTS,MASS_SPLIT,P,THRESH,overlap,volume)
from crown_geom_v253 import main as canon_model,inside_pressure_hull_check
from v253_extra import check_added_interior
from exterior_radiator_states_v254 import build as radiator_state,STATES,ANGLES
from exterior_integrate_v254 import provenance,glb_extras
import d9_sharded as D

OUT=ROOT/"render/out"
PREFIX="wayfarer_bay_fullship_88ce19fc"
GOVERNING="canon-v2.5.3"
BASE_COMMIT="03479ea035a9207e3f7b91402ec387237b5c66e6"

def evaluate(model,poses,g,cfg,criteria,original_containment,
             original_added_inside,new_parts,source_sha):
    assert source_sha=="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
    assert original_containment["pass_containment"] and original_added_inside["pass_containment"]
    (selected,bay_parts,bay_sources,bay_masses,closed,sweeps),bay_screen=screen()
    assert selected in ("tangential_radial","axial_aft_fallback")
    rows={v["id"]:v for v in g["parts"]}
    fluids={v["id"]:v for v in g["fluids_by_state"]["S1"]}
    assert abs(rows["courier_systems"]["mass_t"]-sum(MASS_SPLIT.values()))<1e-9
    assert bay_screen["variants"][selected]["pass_BRep_fit"]
    assert bay_screen["source_spare_panes_remain_screened_at_x_m"]==[20,22.6]
    source_replace={"dry:"+n for n in COURIER_PARTS}
    radiator_replace={f"dry:{prefix}_{a}" for a in ANGLES
                      for prefix in ("strake","hotfin","hotfin_root")}
    assert len(source_replace)==8 and len(radiator_replace)==12
    assert source_replace|radiator_replace<=set(model)
    for n in source_replace:
        assert n.startswith("dry:")
    for j in range(1,8):
        assert f"dry:crown_spare_{j:02d}" in model
    base={n:s for n,s in model.items() if n not in source_replace|radiator_replace}
    assert len(model)==441 and len(base)==421
    assert not set(bay_parts).intersection(base)
    # Verify the selected closed bay pieces are entirely in their approved
    # angular/radial/axial envelope, including the existing moved drone lines.
    bound=P.make(rows["courier_systems"]["shape"])
    for n,s in bay_parts.items():
        assert volume(s-bound)<=THRESH,(n,"escaped bay",volume(s-bound))
    report=dict(status="BAY_FULL_SHIP_D9_PENDING",
         governing_canon_tag=GOVERNING,
         governing_merge_commit=BASE_COMMIT,
         base_radiator_step1_commit="e3084a06daa25169f080b67ce27b779825429bc5",
         source_geometry_sha256=source_sha,
         chosen_layout=selected,
         primary_failed_and_fallback_used=selected=="axial_aft_fallback",
         primary_BRep_issues=bay_screen["variants"]["tangential_radial"]["all_conflicts_count"],
         chosen_BRep_issues=0,
         spare_panes_remain_original_approved_x_m=[20,22.6],
         spare_pane_nodes_not_moved=[f"dry:crown_spare_{j:02d}" for j in range(1,8)],
         source_original_courier_mass_t=rows["courier_systems"]["mass_t"],
         courier_mass_split_t=MASS_SPLIT,
         named_unlocated_courier_systems_remainder_t=MASS_SPLIT["courier_systems_unallocated"],
         source_dry_mass_t=g["dry_t"],ECON_dv_km_s=707.845,
         source_mass_ledger_changed_t=0,
         source_mass_allocations_represented_by_replaced_BReps=sorted(COURIER_PARTS),
         source_courier_id_retained_as_booked_allocation=True,
         source_mass_rebooking_t=0,
         BRep_bay_parts=len(bay_parts),
         bay_containment=dict(bay_fitted_inside_source_envelope=True,
             service_arm_and_tunnel_unchanged=True,
             collar_radial_corridor_clear=True,
             spare_panes_unchanged=True),
         strake_1300K_view_factor_screen=bay_screen["strake_view_factor_screen"],
         thermal_qualification="OPEN: high unshadowed ~58kW/m2 bay-side strake exposure; no shielding or G4 credit",
         door_motion="aft open swept BRep checked without claiming actuator or thermal closure",
         no_canon_mass_or_geometry_source_edit=True,
         six_modes_are_alternative_poses=True,
         modes={})
    OUT.mkdir(exist_ok=True,parents=True)
    # One editable master STEP for the 25 distinct approved bay components.
    bay_step=OUT/(PREFIX+"_bay_components.step")
    export_step(Compound(children=list(bay_parts.values())),bay_step,
                unit=Unit.M,timestamp="2026-11-10T00:00:00")
    assert bay_step.stat().st_size>100
    report["bay_components_step"]=str(bay_step.relative_to(ROOT))
    for mode in STATES:
        rad,mapping=radiator_state(g,cfg,mode)
        fitted=[]
        for n in sorted(rad):
            if n.endswith((":stowed_stack",":folded_envelope",":root")):
                old="dry:"+mapping[n]
                assert old in radiator_replace and old in model
                rad[n]=model[old]
                rad[n].label=n
                fitted.append(n)
        assert len(fitted)==(8 if mode=="torch" else 12)
        assert not set(base).intersection(rad)
        assert not set(bay_parts).intersection(rad)
        combined={**base,**rad,**bay_parts}
        expected_parts=421+len(rad)+len(bay_parts)
        assert len(combined)==expected_parts
        inside=inside_pressure_hull_check(combined,rows)
        newly=check_added_interior(combined,g,new_parts)
        assert inside["pass_containment"] and newly["pass_containment"]
        # Screen swept-open door volume against every installed ship solid,
        # not only the local collar/arm/tunnel sources from preflight.
        door_clashes=[]
        for door,sweep in sweeps.items():
            for name,part in combined.items():
                if name==door or name.startswith("dry:bay_shell_"):continue
                if P.bbox_intersection_upper(P.bounds(sweep),P.bounds(part))<=THRESH:continue
                v=overlap(sweep,part)
                if v>THRESH:
                    door_clashes.append(dict(open_door=door,against=name,intersection_m3=round(v,9)))
        print("BAY_DOOR_FULL_SHIP_SWEEP",mode,json.dumps(door_clashes[:20]),flush=True)
        if door_clashes:
            (OUT/(PREFIX+"_sweep_blocker.json")).write_text(json.dumps(dict(
                mode=mode,failures=door_clashes),indent=2)+"\n")
            raise RuntimeError("open door swept envelope intersects installed ship "+mode)
        mode_out=dict(bay_component_count=len(bay_parts),
            radiator_component_count=len(rad),
            source_suballocations_unchanged=True,
            original_spare_panes_in_situ=True,
            pressure_containment=dict(
                existing=inside,
                new_interior=newly,
                all_new_bay_outside_pressure_vessel_by_design=True,
                bay_inside_existing_outer_source_envelope=True,
                pass_containment=True),
            door_open_sweep_clashes=door_clashes,
            gores={})
        for pose in ("stowed","closed"):
            ship={**combined,**poses[pose]}
            names=sorted(ship)
            n=len(names);np=n*(n-1)//2
            result=D.pair_scan(ship,names,0,np,criteria["D9"]["min_intersection_m3"])
            print("BAY_FULL_SHIP_D9",mode,pose,json.dumps(dict(
                solids=n,pairs=np,category_d=result["category_d_count"],
                bool_errors=len(result["collision_errors"]),
                conflicts=result["category_d_conflicts"][:20])),flush=True)
            if result["category_d_count"] or result["collision_errors"]:
                (OUT/(PREFIX+"_clash_blocker.json")).write_text(json.dumps(
                    dict(mode=mode,pose=pose,conflicts=result["category_d_conflicts"],
                         bool_errors=result["collision_errors"]),indent=2)+"\n")
                raise RuntimeError("Bay D9 category-d installed solid collision "+mode+" "+pose)
            path=OUT/(PREFIX+"_"+mode+"_"+pose+".glb")
            export_gltf(Compound(children=list(ship.values())),path,
                        unit=Unit.M,binary=True,linear_deflection=.05,angular_deflection=.3)
            metadata={}
            for name in names:
                e=provenance(name,rows,fluids,mapping)
                if name in bay_sources:
                    source=bay_sources[name]
                    e=dict(source_allocation_id=source,
                      source_allocation_total_t=rows[source]["mass_t"],
                      source_allocation_reused_by_multiple_geometry_nodes=(source=="courier_systems"),
                      node_mass_rebooking_t=0,
                      node_booked_suballocation_t=bay_masses[name],
                      epistemic_status="kT 2026-11-10 located BRep; hardware thermal/actuation OPEN")
                elif name.startswith("dry:crown_spare_"):
                    e=dict(source_allocation_id="crown_c_seven_spare_panes",
                      source_allocation_total_t=rows["crown_c_seven_spare_panes"]["mass_t"],
                      node_mass_rebooking_t=0,
                      epoxy_status="unchanged approved x20..22.6 storage rack")
                metadata[name]=dict(canon_tag=GOVERNING,
                    geometry_revision="bay layout x14-17.5 source derived, non-canon",
                    node_id=name,radiator_mode=mode,
                    crown_gore_pose=pose,
                    bay_layout=selected,
                    **e)
            extras=glb_extras(path,metadata)
            assert extras["mesh_nodes_with_extras"]==n
            mode_out["gores"][pose]=dict(
                part_count=n,pair_count=np,category_d_count=0,
                boolean_errors=0,
                containment_pass=True,
                door_open_sweep_pass=True,
                glb=str(path.relative_to(ROOT)),
                gltf_extras=extras,
                category_counts=result["category_counts"],
                )
        report["modes"][mode]=mode_out
    assert set(report["modes"])==set(STATES)
    report["status"]="BAY_FULL_SHIP_3X2_D9_AND_CONTAINMENT_PASS"
    fn=OUT/(PREFIX+"_report.json")
    fn.write_text(json.dumps(report,indent=2)+"\n")
    print("BAY_FULL_SHIP_INTEGRATION_PASS",fn,flush=True)

if __name__=="__main__":
    canon_model(on_model_ready=evaluate)
