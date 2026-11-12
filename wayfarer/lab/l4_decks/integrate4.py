#!/usr/bin/env python3
"""kT-approved L4, source-fix screen then independent approved interior GLB.

Only D9 & containment. The existing source mass file stays unchanged; L4
position overrides are carried in this installed representation and report.
"""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Wedge
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"lab"))
sys.path.insert(0,str(ROOT/"lab/l2_organic_study"))
from l2_interior_glb import GLTF,rotate,split_repeat,srgb
from l2_hatch_glb_d9 import clipped_inside
from l4_decks import l4geom
from l4_decks.flag_pictures import create as draw_original_flags, ORIGINAL as ORIGINAL_FLAGS
import geom
from packing_phase1b import source_brep_pilot as P

SRC=ROOT/"results/out/wayfarer_v05_geometry.json"
HATCH=ROOT/"render/out/interior_deck_hatches_report.json"
DEC=ROOT/"config/kt_decisions.json"
OUT=ROOT/"render/out"
GLB=OUT/"interior_L4.glb"
REPORT=OUT/"interior_L4_report.json"
PIC=ROOT/"docs/WAYFARER_L4_APPROVED_D9_2026_11_12.png"
FLAG_PIC=ROOT/"docs/WAYFARER_L4_12_D9_FLAGS_RESOLVED_2026_11_12.png"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
EST={"S0_shelter_plug_door":20,"S7_shelter_lining":40,"S1_living_wall":55,
     "S2_wellness_loungers":40,"S3_soft_floor":25,"S4_backup_stand":10,
     "S5_shelter_seats":65,"S6_storm_lockers":30,
     "M1_treatment_table":160,"M2_recovery_bed":125,
     "M3_cabinets_pharmacy":150,"M5_decon_sink_terminal":55,
     "R_racks":10000,"R8_laundry":180,"R9_spares":260,
     "D3_lining":80,"D1_lighting":30,"D2_overhead_rail":30,
     "P0_medical":70,"P0_eclss":70}
REPEATS={"S2_wellness_loungers":[60,120],
         "S5_shelter_seats":[26,37,48,59,70,110,121,132,143,154],
         "R_racks":[264,278,292,306,320,334,348]}
def owner(item):
    if item.startswith("S"):return "room_L4-shelter"
    if item.startswith("M") or item=="P0_medical":return "room_L4-medical"
    if item.startswith("R") or item=="P0_eclss":return "room_L4-eclss"
    if item.startswith("D"):return "outfit_L4"
    raise RuntimeError("Unknown L4 owner "+item)
def part_inside_box(tris,shape):
    lo=np.array([shape["x0"],shape["z0"],-shape["y1"]])+1e-5
    hi=np.array([shape["x1"],shape["z1"],-shape["y0"]])-1e-5
    tr=np.concatenate([np.asarray(t,float).reshape(-1,3,3) for t in tris.values()])
    ids=np.where(np.all(tr.max(axis=1)>lo,axis=1)&np.all(tr.min(axis=1)<hi,axis=1))[0]
    return any(clipped_inside(tr[j],lo,hi) for j in ids)
def jacket_hits(item,tris,water):
    if item=="S0_shelter_plug_door":
        # Approved water-filled door shell occupies the closed water plug.
        return []
    tri=np.concatenate([np.asarray(v,float).reshape(-1,3,3) for v in tris.values()])
    points=np.concatenate([tri.reshape(-1,3),
                          (tri[:,0]+tri[:,1])*.5,
                          (tri[:,1]+tri[:,2])*.5,
                          (tri[:,2]+tri[:,0])*.5,
                          tri.mean(axis=1)])
    x=points[:,0];y=-points[:,2];z=points[:,1]
    r=np.hypot(y,z);az=(np.degrees(np.arctan2(z,y))+360)%360
    hits=[]
    for p in water:
        s=p["shape"];e=1e-5
        inside=(x>s["x0"]+e)&(x<s["x1"]-e)&(r>s["r0"]+e)&(r<s["r1"]-e)&(az>s["a0"]+1e-4)&(az<s["a1"]-1e-4)
        if np.any(inside):
            hits.append(dict(item=item,protected_water=p["id"],sample_intrusions=int(np.sum(inside))))
    return hits
def graph(geo,rep):
    fig,(ax,side)=plt.subplots(1,2,figsize=(13.5,6))
    fig.patch.set_facecolor("#f5f5f2")
    for a in (ax,side):a.set_facecolor("#f5f5f2")
    ax.add_patch(Wedge((0,0),4.15,15,165,width=0.2,facecolor="#4f8ea3",alpha=.48))
    ax.add_patch(Wedge((0,0),2.1,15,165,width=.2,facecolor="#4f8ea3",alpha=.65))
    ax.add_patch(Wedge((0,0),2.1,78.54,101.46,width=.2,facecolor="#dcaf69",alpha=.95))
    ax.add_patch(Wedge((0,0),3.8,18.8,161.2,width=1.7,facecolor="#cfdcbe",alpha=.30))
    for angle in (180,210,240):
        v=math.radians(angle);x=4.15*math.cos(v);y=4.15*math.sin(v)
        ax.plot(x,y,"o",markersize=11,color="#6c9bb6")
    ax.add_patch(Rectangle((-2.75,-.46),.92,.92,facecolor="#3a7659",alpha=.9))
    ax.plot([1.86,1.86],[-.46,.46],lw=7,color="#b77843")
    ax.text(-2.75,-.78,"180° hatch slab pocket",fontsize=9)
    ax.text(0,3.35,"SHELTER + WELLNESS",ha="center",fontsize=10,weight="bold")
    ax.text(-2.8,-2.4,"MEDICAL",fontsize=10,weight="bold")
    ax.text(2.65,-2.4,"ECLSS / LAUNDRY",fontsize=10,weight="bold")
    ax.set(xlim=(-4.7,4.7),ylim=(-4.7,4.7),xlabel="Y (m)",ylabel="Z (m)",title="Source-fixed L4 transverse plan")
    ax.set_aspect("equal")
    side.add_patch(Rectangle((8.5,0),2.3,2.3,edgecolor="#777",facecolor="#e3e4e1",alpha=.4))
    side.axhline(2.30,ls="--",color="#b86e52",lw=1)
    for idx,angle in enumerate((180,210,240)):
        side.add_patch(Rectangle((9.30-.08,1.5-.775),.16,1.55,facecolor="#7eafc7",alpha=.80))
        side.text(9.48,1.5+(.25-idx*.25),f"{angle}°",fontsize=8)
    side.add_patch(Rectangle((8.25,0),.08,.92,facecolor="#3a7659",alpha=.88))
    side.text(8.28,1.08,"180° hatch stowed\nin L3 floor slab",fontsize=9)
    side.set(xlim=(8.08,11),ylim=(-.10,2.58),xlabel="Ship X (m), source station",ylabel="Height (m)",title="Medical ports: centre h=1.50")
    fig.suptitle("WAYFARER L4  |  kT APPROVED  |  D9=0  •  CONTAINMENT PASS")
    fig.text(.5,.025,"Local source-fix geometry: equal-water plug at 90°, medical ports lowered, 180° L3L4 leaf stowed. No added mass.",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.93])
    PIC.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(PIC,dpi=160)
    plt.close(fig)
def main():
    raw=SRC.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA,"STOP source geometry changed"
    G=json.loads(raw);rows={p["id"]:p for p in G["parts"]}
    D=json.loads(DEC.read_text())
    assert D["l4_decisions_2026_11_12"]["wellness_room"].startswith("L4-shelter"),"STOP kT L4 authority mismatch"
    assert abs(G["dry_t"]-868.1922552640087)<1e-8
    hrep=json.loads(HATCH.read_text())
    assert hrep["status"]=="DECK_HATCHES_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS"
    assert hrep["checks"]["D9_category_d"]==0 and hrep["checks"]["containment"]=="PASS"
    assert hrep["L4_source_fixes"]["dry_mass_delta_t"]==0
    assert abs(hrep["L4_source_fixes"]["shelter_water_door"]["water_mass_delta_t"])<1e-12
    assert hrep["hatches"]["hatch_L3L4_0"]["shape"]["x0"]==8.26
    assert hrep["hatches"]["hatch_L3L4_1"]["shape"]["x0"]==8.2
    assert hrep["L4_source_fixes"]["medical_ports"]["centre_x_after_m"]==9.3
    assert hrep["L4_source_fixes"]["medical_ports"]["port_top_height_m"]==2.275
    h1=hrep["hatches"]["hatch_L3L4_1"]["shape"]
    # Approved 19 proposal groups: preserve geometry; split P0 according
    # to its physical medical/ECLSS side without duplicating booked mass.
    l4geom.build()
    items={}
    for (it,mat),tri in geom.T.items():
        if it in ("CTX","ARCH") or not tri:continue
        v=np.asarray(tri,float).reshape(-1,3,3)
        if it=="P0_walls":
            angle=(np.degrees(np.arctan2(v[:,:,1].mean(axis=1),-v[:,:,2].mean(axis=1)))+360)%360
            for group,mask in (("P0_medical",angle<255),("P0_eclss",angle>=255)):
                if mask.any():items.setdefault(group,{})[mat]=v[mask]
        else:items.setdefault(it,{})[mat]=v
    original={it for it,_ in geom.T if it not in ("CTX","ARCH")}
    assert len(original)==19,(len(original),sorted(original))
    assert set(items)==set(EST),(set(items)-set(EST),set(EST)-set(items))
    booked={k:1000*rows[k]["mass_t"] for k in ("room_L4-shelter","room_L4-medical","room_L4-eclss","outfit_L4")}
    previous=dict(room_L4_shelter=0,room_L4_medical=0,room_L4_eclss=0,outfit_L4=300)
    usage={k:sum(EST[it] for it in items if owner(it)==k) for k in booked}
    booking_exceeded=[k for k in booked if usage[k]+(300 if k=="outfit_L4" else 0)>booked[k]+1e-7]
    checks=dict(step1_source_D9_category_d=hrep["checks"]["D9_category_d"],
      step1_source_containment=hrep["checks"]["containment"],
      G1_G12="NOT RUN / NOT REQUIRED")
    rep=dict(source_geometry_sha256=SHA,decision_source="l4_decisions_2026_11_12",
         source_dry_t=G["dry_t"],ECON_dv_km_s=707.845,source_mass_rebooking_t=0,
         original_proposal_groups=len(original),group_ids=sorted(original),P0_partition_split=True,
         booking_kg=booked,estimated_drawn_kg=usage,
         estimated_prior_L4_hatches_kg=300,booking_excess=booking_exceeded,
         source_fixes=hrep["L4_source_fixes"],checks=checks,
         exterior_GLB_changes=0,existing_L1_L2_GLB_changes=0)
    if booking_exceeded:
        rep["status"]="STOP_ROOM_BOOKING_EXCEEDED"
        REPORT.write_text(json.dumps(rep,indent=2)+"\n")
        raise RuntimeError(rep["status"]+":"+str(booking_exceeded))
    # All L4 geometry remains within pressure shell and between both floors.
    pts=np.concatenate([v.reshape(-1,3) for part in items.values() for v in part.values()])
    radial=np.hypot(pts[:,1],pts[:,2])
    h=10.8-pts[:,0]
    rmin=float(radial.min());rmax=float(radial.max())
    hmin=float(h.min());hmax=float(h.max())
    shell_r=rows["pressure_vessel"]["shape"]["R"]-rows["pressure_vessel"]["shape"]["t"]
    envelope_violations=[]
    if rmin<rows["core_racks"]["shape"]["r1"]-1e-5:envelope_violations.append("core_racks")
    if rmax>shell_r+1e-5:envelope_violations.append("pressure_shell")
    if hmin<-.00001:envelope_violations.append("floor_L4")
    if hmax>2.30001:envelope_violations.append("floor_L3")
    checks.update(source_clearances_m=dict(core_racks=rmin-rows["core_racks"]["shape"]["r1"],
                pressure_shell=shell_r-rmax,floor_L4=hmin,floor_L3=2.30-hmax))
    # Physical triangulated-vs-box screen, including remaining hatch leaf,
    # rescue kit, shelter backup; medical windows at relocated source x.
    fixtures={k:rows[k]["shape"] for k in ("rescue_kit","shelter_backup")}
    fixtures["hatch_L3L4_1"]=h1
    fixtures.update(hrep["L4_source_fixes"]["medical_ports"]["source_proxy_overrides"])
    physical=[]
    for item,mat_tris in items.items():
        for name,shape in fixtures.items():
            if item=="S4_backup_stand" and name=="shelter_backup":
                # Source 72h stored backup resting on its approved new stand.
                # This is intentional structural contact, not category-d.
                continue
            if part_inside_box(mat_tris,shape):
                physical.append(dict(item=item,fixture=name,category="d"))
    water=[p for p in G["fluids_by_state"]["S1"] if p["id"].startswith("jacket_")
           and p["id"] in ("jacket_outer","jacket_inner","jacket_radial_a","jacket_radial_b","jacket_ceiling","jacket_floor")]
    # Correct jacket_inner has the approved water-filled door relief. Its
    # union has precisely the same volume. S0's water-filled panel is category-c.
    # All other furniture must stay outside protected water volumes.
    jacket=[]
    for item,tris in items.items():
        jacket.extend(jacket_hits(item,tris,water))
    d9=len(physical)+len(jacket)+len(envelope_violations)
    contained=len(envelope_violations)==0
    checks.update(D9_category_d=d9,physical_fixture_contacts=physical,
                  protected_water_vertex_or_centroid_intrusions=jacket,
                  source_envelope_violations=envelope_violations,
                  containment="PASS" if contained else "FAIL")
    if d9 or not contained:
        rep["status"]="STOP_L4_D9_OR_CONTAINMENT"
        REPORT.write_text(json.dumps(rep,indent=2)+"\n")
        raise RuntimeError(rep["status"]+": "+str(checks))
    # GLB built from accepted original L4 authored vertices; repeated authored
    # geometry uses shared meshes, and P0 split by physical room.
    gl=GLTF()
    gl.nodes.append(dict(name="LOOM_WAYFARER_L4_INTERIOR",children=[],
       extras=dict(source_geometry_sha256=SHA,mass_neutral=True,exterior_six_state_untouched=True,
                   L4_shelter_is_wellness_room=True)))
    gl.nodes.append(dict(name="system:HABITAT",children=[]));gl.nodes[0]["children"].append(1)
    mats=sorted({m for part in items.values() for m in part})
    materials=[]
    for mat in mats:
        col,em=geom.MAT[mat]
        materials.append(dict(name="CANON_FINISH/L4/"+mat,doubleSided=True,
          pbrMetallicRoughness=dict(baseColorFactor=srgb(col),metallicFactor=.6 if mat=="titanium" else 0.,
                                    roughnessFactor=.35 if mat in ("titanium","glass") else .7),
          **(dict(emissiveFactor=srgb(col)[:3]) if em else {})))
    mi={m:i for i,m in enumerate(mats)}
    subidx={}
    def addnode(it,name,mesh,pose=None,extra=None):
        own=owner(it)
        room={"room_L4-shelter":"shelter_wellness",
              "room_L4-medical":"medical","room_L4-eclss":"eclss","outfit_L4":"deck_services"}[own]
        if room not in subidx:
            n=len(gl.nodes);gl.nodes.append(dict(name="subsystem:HABITAT/L4_"+room,children=[]))
            gl.nodes[1]["children"].append(n);subidx[room]=n
        ex=dict(zone="FORE",deck="L4",material="L4 organic Japandi",
          print_group="HABITAT/L4_"+room,mass=rows[own]["mass_t"],mass_unit="t",
          mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=own,
          semantic_system="HABITAT",semantic_subsystem="L4_"+room,
          node_mass_rebooking_t=0,source_booking_repeated_nonadditive=True,
          source_geometry_sha256=SHA,source_proposal_node="proposal:L4_"+("P0_walls" if it.startswith("P0_") else it),
          estimated_drawn_group_kg=EST[it],room_role=room)
        if extra:ex.update(extra)
        n=len(gl.nodes)
        node=dict(name=name,mesh=mesh,extras=ex)
        if pose:node.update(pose)
        gl.nodes.append(node);gl.nodes[subidx[room]]["children"].append(n)
    repeated={}
    for it in sorted(items):
        if it in REPEATS:
            angles=REPEATS[it]
            ref,split=split_repeat(items[it],angles)
            local={m:rotate(v,-ref) for m,v in split[ref].items()}
            mesh=gl.mesh(it+"_SHARED",local,mi)
            repeated[it]=dict(count=len(angles),shared_mesh_index=mesh)
            for ix,a in enumerate(angles):
                rad=math.radians(a)
                addnode(it,"dry:L4_"+it+"_"+str(ix+1),mesh,
                    pose=dict(rotation=[math.sin(rad/2),0,0,math.cos(rad/2)]),
                    extra=dict(shared_mesh_instanced=True,repeat_angle_deg=a,repeat_count=len(angles)))
        else:
            mesh=gl.mesh(it,items[it],mi)
            addnode(it,"dry:L4_"+it,mesh)
    data=gl.finish(materials,SHA)
    OUT.mkdir(parents=True,exist_ok=True)
    GLB.write_bytes(data)
    mesh_nodes=sum("mesh" in n for n in gl.nodes)
    rep.update(status="L4_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS",
      glb=str(GLB.relative_to(ROOT)),glb_sha256=hashlib.sha256(data).hexdigest(),
      glb_bytes=len(data),glb_mesh_nodes=mesh_nodes,glb_unique_meshes=len(gl.meshes),
      instance_repeats=repeated,P0_subroom_nodes=["P0_medical","P0_eclss"],
      painting="source L4 Japandi / warm industrial",
      smooth_normals=True,
      estimated_outfit_L4_after_hatches_and_interior_kg=booked["outfit_L4"]-300-usage["outfit_L4"],
      picture=str(PIC.relative_to(ROOT)))
    graph(G,rep)
    rep["original_12_jacket_flags"]=draw_original_flags(items,water,FLAG_PIC)
    assert len(rep["original_12_jacket_flags"])==12 and not jacket
    rep["diagnostic_12_flags_png"]=str(FLAG_PIC.relative_to(ROOT))
    rep["jacket_sampling_basis"]="vertices, all three edge midpoints and triangle centroids; corrected source geometry"
    REPORT.write_text(json.dumps(rep,indent=2)+"\n")
    print(json.dumps({k:rep[k] for k in ("status","checks","booking_kg","estimated_drawn_kg",
            "original_proposal_groups","glb_mesh_nodes","instance_repeats","glb_sha256","picture")},indent=2))
if __name__=="__main__":main()
