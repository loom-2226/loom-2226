#!/usr/bin/env python3
"""kT-approved L5 23-group interior, BRep source hatch screen + D9, mass-neutral.

The full-source dry and water records are immutable. Material / pressure / 
shielding performance of the real opened hatch is not claimed by a closed
geometric plug test.
"""
import hashlib,json,math,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge,Circle,Rectangle
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"lab"))
sys.path.insert(0,str(ROOT/"lab/l2_organic_study"))
import geom
from l2_interior_glb import GLTF,rotate,split_repeat,srgb,inside_box_triangle
from l5_deck import l5geom
SRC=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
OUT=ROOT/"render/out"
REPORT=OUT/"interior_L5_report.json"
GLB=OUT/"interior_L5.glb"
PNG=ROOT/"docs/WAYFARER_L5_D9_2026_11_12.png"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
# Composite room estimates from the approved Claude proposal, including A4
# and T1. P0 partition estimates are ALREADY included in room composites.
EST={"A0_inner_pressure_hatch":115,"A1_control_panel":55,"A2_tether_tool_board":65,
 "A3_handhold_station":65,"A4_EVA_hatch":280,
 "U1_EVA_suit_stands":690,"U2_IVA_lockers":150,"U3_donning_bench":50,
 "W1_workbench":210,"W2_3D_printer":180,"W3_mill_lathe":195,
 "W4_W5_parts_walls":95,"W6_stools":60,
 "V1_custody_vault":315,"V2_vault_door":95,
 "S1_stores_racks":200,"S2_stores_racks":200,
 "T1_tunnel_floor_hatch":150,"T2_handrails_panel":30,
 "D3_lining":80,"D1_lighting":30,"D2_overhead_rail":35}
REPEATS={"U1_EVA_suit_stands":[32,44,56,68],"W6_stools":[115,135],
         "S1_stores_racks":[210,225,240],"S2_stores_racks":[300,315,330]}
ROOMS=[("room_L5-airlock",-20,20),("room_L5-suits",20,80),
       ("room_L5-workshop",80,170),("room_L5-custody",170,200),
       ("room_L5-stores",200,250),("room_L5-vestibule",250,290),
       ("room_L5-stores2",290,340)]
def owner(it):
    if it.startswith("P0_"):return it[len("P0_"):]
    if it.startswith("S1"):return "room_L5-stores"
    if it.startswith("S2"):return "room_L5-stores2"
    c=it[0]
    return dict(A="room_L5-airlock",U="room_L5-suits",W="room_L5-workshop",
                V="room_L5-custody",T="room_L5-vestibule",
                D="outfit_L5")[c]
def boxed_inside(v,sh):
    """Triangle/box OPEN interior check, glTF positions (x,z,-y)."""
    tri=np.asarray(v).reshape((-1,3,3))
    lo=np.array([sh["x0"],sh["z0"],-sh["y1"]])+1e-5
    hi=np.array([sh["x1"],sh["z1"],-sh["y0"]])-1e-5
    bmin=tri.min(axis=1);bmax=tri.max(axis=1)
    candidates=np.where(np.all(bmax>lo,axis=1)&np.all(bmin<hi,axis=1))[0]
    return any(inside_box_triangle(tri[k],lo,hi) for k in candidates)
def draw(report):
    fig,ax=plt.subplots(figsize=(9.5,8.5))
    fig.patch.set_facecolor("#f4f2ed");ax.set_facecolor("#f4f2ed")
    color=["#c7d3ca","#d7d2c5","#c6c9bf","#d1c6b9","#ccc8b3","#b7cbd0","#d1d4bc"]
    for j,(r,a,b) in enumerate(ROOMS):
        ax.add_patch(Wedge((0,0),4.15,a,b,width=2.25,facecolor=color[j],edgecolor="#727b78",linewidth=1.5))
        mid=math.radians((a+b)/2)
        ax.text(2.9*math.cos(mid),2.9*math.sin(mid),r.removeprefix("room_L5-").upper(),
                rotation=0,fontsize=8,ha="center",va="center",weight="bold")
    ax.add_patch(Circle((0,0),1.25,facecolor="#f2efe9",edgecolor="#8e8b85",linewidth=2))
    ax.add_patch(Circle((4.3,0),.50,facecolor="#678e89",edgecolor="#294d4a",linewidth=2))
    ax.annotate("1.0 m EVA hatch\nx=12.30 / 0°",xy=(4.3,0),xytext=(5.1,.75),fontsize=10,
                arrowprops=dict(arrowstyle="->",color="#284c49"))
    ax.add_patch(Circle((0,-3),.60,facecolor="#c89c64",edgecolor="#725632",linewidth=2))
    ax.annotate("1.2 m tunnel hatch\nbulkhead x=13.40–13.70\nr3.0 / 270°",xy=(0,-3),
                xytext=(1.3,-5),fontsize=10,arrowprops=dict(arrowstyle="->",color="#78572b"))
    ax.set(xlim=(-5.6,6.2),ylim=(-5.65,5.5),xlabel="Ship Y (m)",ylabel="Ship Z (m)")
    ax.set_aspect("equal")
    fig.suptitle("WAYFARER 2226  |  L5 EVA / MISSION / TRANSFER  |  D9 PASS",fontsize=14)
    fig.text(.5,.025,"kT-approved 23-group L5 design; source-copied mass bookings. Hatch closure geometric checks, not pressure certification.",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.93])
    PNG.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(PNG,dpi=155)
    plt.close(fig)
def main():
    data=SRC.read_bytes()
    assert hashlib.sha256(data).hexdigest()==SHA,"STOP source geometry changed"
    g=json.loads(data)
    assert abs(g["dry_t"]-868.1922552640087)<1e-8
    dec=json.loads(DEC.read_text())
    assert dec["l5_decisions_2026_11_12"]["authority"].startswith("kT APPROVED")
    srcfix=json.loads((OUT/"interior_L5_source_report.json").read_text())
    assert srcfix["status"]=="L5_SOURCE_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS"
    assert srcfix["checks"]["D9_category_d"]==0
    parts={p["id"]:p for p in g["parts"]}
    l5geom.build()
    items={}
    orig={it for it,m in geom.T if it not in ("CTX","ARCH")}
    assert len(orig)==23,(len(orig),orig)
    for (it,m),tris in geom.T.items():
        if it in ("CTX","ARCH") or not tris:continue
        vv=np.asarray(tris,float).reshape(-1,3,3)
        if it=="P0_walls":
            # P0 is split by authored room sector, no coordinate changes.
            aa=(np.degrees(np.arctan2(vv[:,:,1].mean(axis=1),-vv[:,:,2].mean(axis=1)))+360)%360
            aa=np.where(aa>=340,aa-360,aa)
            assignment=np.zeros(len(aa),int)
            for j,(room,lo,hi) in enumerate(ROOMS):
                assignment[(aa>=lo)&(aa<hi)]=j
            for j,(room,lo,hi) in enumerate(ROOMS):
                subset=vv[assignment==j]
                if len(subset):
                    items.setdefault("P0_"+room,{})[m]=subset
        else:items.setdefault(it,{})[m]=vv
    assert set(orig)-{"P0_walls"}==set(items)-{k for k in items if k.startswith("P0_")}
    assert set(EST)==set(orig)-{"P0_walls"}
    assert any(k.startswith("P0_") for k in items)
    # Composite estimates already include the drawing of P0 walls, but
    # the wall group still references its physical source mass owner.
    used={}
    booked={}
    for it in items:
        k=owner(it)
        booked[k]=parts[k]["mass_t"]*1000
        used[k]=used.get(k,0)+EST.get(it,0)
    over={k:{"used_kg":used[k],"booked_kg":booked[k]} for k in booked if used[k]>booked[k]+1e-6}
    rep=dict(source_geometry_sha256=SHA,source_dry_t=g["dry_t"],
       ECON_dv_km_s=707.845,source_mass_rebooking_t=0,
       source_groups=23,source_proposal_nodes=sorted(orig),P0_room_split=True,
       booking_kg=booked,estimated_drawn_kg=used,booking_exceeded=over,
       source_hatches=srcfix,checks=dict(G1_G12="NOT RUN / NOT REQUIRED"),
       original_exterior_GLBS_changed=0,other_interior_GLBS_changed=0)
    OUT.mkdir(parents=True,exist_ok=True)
    if over:
        rep["status"]="STOP_L5_BOOKING_EXCEEDED"
        REPORT.write_text(json.dumps(rep,indent=2)+"\n")
        raise RuntimeError(rep["status"]+": "+str(over))
    vs=np.concatenate([v.reshape(-1,3) for part in items.values() for v in part.values()])
    radius=np.hypot(vs[:,1],vs[:,2])
    height=13.4-vs[:,0]
    inner=parts["pressure_vessel"]["shape"]["R"]-parts["pressure_vessel"]["shape"]["t"]
    core=parts["core_racks"]["shape"]["r1"]
    bulk=parts["aft_bulkhead"]["shape"]["x0"]
    limits=dict(core_racks_m=float(radius.min()-core),
        pressure_inner_shell_m=float(inner-radius.max()),
        L4_L5_ceiling_m=float(2.3-height.max()),
        aft_bulkhead_m=float(bulk-vs[:,0].max()))
    bad=[k for k,v in limits.items() if v < -1e-5]
    fixtures={p["id"]:p["shape"] for p in g["parts"] if p["id"].startswith("window_L5-")}
    fixtures.update({k:parts[k]["shape"] for k in ("hatch_L4L5_0","hatch_L4L5_180")})
    # Genuine source physical boxes; don't treat semantic room zones as solids.
    collisions=[]
    for it,mat in items.items():
        for name,sh in fixtures.items():
            if any(boxed_inside(v,sh) for v in mat.values()):
                collisions.append({"item":it,"physical_fixture":name,"category":"d"})
    # No physical authored triangle may penetrate the axial bulkhead, with
    # T1 intentionally attached at that opening (otherwise identical test).
    bulk_hit=[it for it,part in items.items() if it!="T1_tunnel_floor_hatch" and any(
        np.any(v[:,:,0]>bulk+1e-5) for v in part.values())]
    if bulk_hit:collisions+=[dict(item=it,physical_fixture="aft_bulkhead",category="d") for it in bulk_hit]
    # tunnel_0 is aft of x13.70; geometry bound here is x<=13.4, hence no
    # body can hit the tunnel, and the hatch axis is exact by source proof.
    hits=len(collisions)+len(bad)
    checks=dict(D9_category_d=hits,category_d_contacts=collisions,
       envelope_violations=bad,source_clearances_m={k:round(v,6) for k,v in limits.items()},
       tunnel_axis_match=True,EVA_closed_pressure_and_armour_geo=srcfix["EVA"]["closed_geometric_armour_thickness_equivalence"],
       source_stage_D9=0,containment="PASS" if not bad else "FAIL",
       G1_G12="NOT RUN / NOT REQUIRED")
    rep["checks"]=checks
    if hits:
        rep["status"]="STOP_L5_D9_OR_CONTAINMENT"
        REPORT.write_text(json.dumps(rep,indent=2)+"\n")
        raise RuntimeError(rep["status"]+": "+str(checks))
    mats=sorted({m for d in items.values() for m in d})
    mi={m:i for i,m in enumerate(mats)}
    materials=[]
    for m in mats:
        col,em=geom.MAT[m]
        materials.append(dict(name="CANON_FINISH/L5/"+m,doubleSided=True,
          pbrMetallicRoughness=dict(baseColorFactor=srgb(col),
            metallicFactor=.6 if m=="titanium" else 0.,
            roughnessFactor=.35 if m in ("titanium","glass") else .7),
          **(dict(emissiveFactor=srgb(col)[:3]) if em else {})))
    gl=GLTF()
    gl.nodes.append(dict(name="LOOM_WAYFARER_L5_INTERIOR",children=[1],
        extras=dict(source_geometry_sha256=SHA,mass_neutral=True,interior_only=True)))
    gl.nodes.append(dict(name="system:HABITAT",children=[]))
    subs={}
    def add(it,name,mesh,pose=None,extra=None):
        own=owner(it);sub=own.removeprefix("room_L5-").removeprefix("outfit_L5")
        if not sub:sub="deck_services"
        if sub not in subs:
            idx=len(gl.nodes)
            gl.nodes.append(dict(name="subsystem:HABITAT/L5_"+sub,children=[]))
            gl.nodes[1]["children"].append(idx);subs[sub]=idx
        ex=dict(zone="FORE",deck="L5",material="approved L5 organic Japandi",
           print_group="HABITAT/L5_"+sub,mass=parts[own]["mass_t"],mass_unit="t",
           mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=own,
           semantic_system="HABITAT",semantic_subsystem="L5_"+sub,
           node_mass_rebooking_t=0,source_booking_repeated_nonadditive=True,
           approved_proposal_node="proposal:L5_"+("P0_walls" if it.startswith("P0_") else it),
           estimated_group_drawn_kg=EST.get(it,0),
           source_geometry_sha256=SHA)
        if extra:ex.update(extra)
        node=dict(name=name,mesh=mesh,extras=ex)
        if pose:node.update(pose)
        idx=len(gl.nodes);gl.nodes.append(node);gl.nodes[subs[sub]]["children"].append(idx)
    instances={}
    for it in sorted(items):
        if it in REPEATS:
            angles=REPEATS[it]
            # Preserve every authored triangle. Share only genuinely rigid
            # material subsets; tubular tessellation can differ by azimuth.
            partitions={}
            for mat,tri in items[it].items():
                arr=np.asarray(tri,float).reshape(-1,3,3)
                azi=(np.degrees(np.arctan2(arr[:,:,1].mean(axis=1),-arr[:,:,2].mean(axis=1)))+360)%360
                delta=np.abs((azi[:,None]-np.asarray(angles)[None,:]+180)%360-180)
                nearest=np.argmin(delta,axis=1)
                partitions[mat]={a:arr[nearest==j] for j,a in enumerate(angles)}
                assert all(len(partitions[mat][a])>0 for a in angles),(it,mat)
            ref=angles[len(angles)//2]
            shared=[];unique=[]
            for mat in sorted(partitions):
                samples=partitions[mat]
                base=samples[ref]
                rigid=all(rotate(base,a-ref).shape==samples[a].shape and
                          np.allclose(rotate(base,a-ref),samples[a],atol=1e-5,rtol=0)
                          for a in angles)
                if rigid:
                    shared.append(mat)
                    mesh=gl.mesh(it+"_"+mat+"_SHARED",{mat:rotate(base,-ref)},mi)
                    for ix,a in enumerate(angles,1):
                        rad=math.radians(a)
                        add(it,"dry:L5_"+it+"_"+mat+"_"+str(ix),mesh,
                            dict(rotation=[math.sin(rad/2),0,0,math.cos(rad/2)]),
                            dict(shared_mesh_instanced=True,material_subset=mat,
                                 angle_deg=a,repeat_count=len(angles)))
                else:
                    unique.append(mat)
                    for ix,a in enumerate(angles,1):
                        mesh=gl.mesh(it+"_"+mat+"_"+str(ix),{mat:samples[a]},mi)
                        add(it,"dry:L5_"+it+"_"+mat+"_"+str(ix),mesh,
                            extra=dict(shared_mesh_instanced=False,material_subset=mat,
                                       angle_deg=a,repeat_count=len(angles),
                                       distinction="source geometry not rigidly repeated"))
            instances[it]=dict(count=len(angles),shared_materials=shared,
                               unique_source_materials=unique,source_preserved=True)
        else:
            mesh=gl.mesh(it,items[it],mi)
            add(it,"dry:L5_"+it,mesh)
    raw=gl.finish(materials,SHA)
    GLB.write_bytes(raw)
    rep.update(status="L5_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS",
         glb="render/out/interior_L5.glb",glb_sha256=hashlib.sha256(raw).hexdigest(),
         glb_bytes=len(raw),glb_mesh_nodes=sum("mesh" in n for n in gl.nodes),
         glb_unique_meshes=len(gl.meshes),instance_repeats=instances,
         smooth_normals=True,palette="approved Claude L5 organic Japandi",
         P0_room_nodes=sorted(k for k in items if k.startswith("P0_")),
         picture="docs/WAYFARER_L5_D9_2026_11_12.png")
    draw(rep)
    REPORT.write_text(json.dumps(rep,indent=2)+"\n")
    print(json.dumps({k:rep[k] for k in ("status","estimated_drawn_kg","checks",
                  "source_groups","glb_mesh_nodes","glb_unique_meshes","instance_repeats","picture")},indent=2))
if __name__=="__main__":main()
