#!/usr/bin/env python3
"""Four kT-approved source-copy hatch leaves; no new booked mass or exterior changes."""
import json, math, hashlib, struct, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"))
from packing_phase1b import source_brep_pilot as P
from l1_interior_glb import GLB
SRC=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
OUT=ROOT/"render/out"
PIC=ROOT/"docs/WAYFARER_DECK_HATCHES_2026_11_12.png"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
BOUNDARIES=(("L2L3",2.6,"floor_L2","outfit_L2"),
            ("L3L4",5.2,"floor_L3","outfit_L4"))
def vol(a,b):
    v=a&b
    return 0.0 if v is None else float(v.volume)
def main():
    src=SRC.read_bytes()
    assert hashlib.sha256(src).hexdigest()==SHA,"STOP source geometry moved"
    geom=json.loads(src)
    assert abs(geom["dry_t"]-868.1922552640087)<1e-8
    rows={p["id"]:p for p in geom["parts"]}
    decisions=json.loads(DEC.read_text())
    assert "deck_hatches_2026_11_12" in decisions
    assert decisions["l2_common_deck_japandi_2026_11_12"]["estimated_drawn_mass_kg"]["outfit_L2"]==145
    budgets={}
    for tag,dx,floor,owner in BOUNDARIES:
        booked=1000*rows[owner]["mass_t"]
        previous=145 if owner=="outfit_L2" else 0
        balance=booked-previous-300
        if balance<0:raise RuntimeError("STOP outfit allowance "+owner)
        budgets[owner]=dict(booked_kg=booked,previous_drawn_kg=previous,hatches_kg=300,remaining_kg=balance)
    floors={}
    baseline=P.make(rows["floor_L1"]["shape"])
    for y in (-1.4,1.4):
        baseline=baseline-P.cyl(.4,2.98,3.32,y,0.)
    for tag,dx,which,owner in BOUNDARIES:
        floor_shape=rows[which]["shape"]
        solid=P.make(floor_shape)
        initial=float(solid.volume)
        for y in (-1.4,1.4):
            solid=solid-P.cyl(.4,floor_shape["x0"]-.02,floor_shape["x1"]+.02,y,0.)
        removed=initial-float(solid.volume)
        assert abs(removed-2*math.pi*.4**2*.3)<.005,(which,removed)
        floors[which]=dict(solid=solid,source=floor_shape,removed=removed)
    leaves={}
    for tag,dx,floor,owner in BOUNDARIES:
        for n in (0,1):
            template=rows["hatch_L1L2_"+str(n)]["shape"]
            shape={**template,"x0":template["x0"]+dx,"x1":template["x1"]+dx}
            assert abs(shape["x0"]-rows[floor]["shape"]["x0"])<1e-9
            assert abs(shape["x1"]-shape["x0"]-.92)<1e-9
            solid=P.make(shape)
            mount=vol(solid,floors[floor]["solid"])
            template_mount=vol(P.make(template),baseline)
            assert abs(mount-template_mount)<1e-6,(tag,n,mount,template_mount)
            leaves["hatch_"+tag+"_"+str(n)]=dict(shape=shape,solid=solid,owner=owner,
                    source="hatch_L1L2_"+str(n),floor_mount_m3=mount)
    # Physically authored source fixtures, not room/outfit accounting envelopes.
    contacts=[]
    scanned=[]
    for name,item in leaves.items():
        bb=P.bounds(item["solid"])
        for p in geom["parts"]:
            rid=p["id"]
            if rid.startswith(("room_","outfit_","floor_","hatch_L1L2_")) or rid in ("pressure_vessel","armor"):
                continue
            s=p["shape"]
            if "x0" in s and "x1" in s and (s["x1"]<=bb[0] or s["x0"]>=bb[1]):
                continue
            solid=P.make(s)
            if P.bbox_intersection_upper(bb,P.bounds(solid))<1e-10:
                continue
            v=vol(item["solid"],solid)
            scanned.append([name,rid,v])
            if v>1e-7:contacts.append(dict(hatch=name,other=rid,volume_m3=v,category="d"))
    names=list(leaves)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if P.bbox_intersection_upper(P.bounds(leaves[a]["solid"]),P.bounds(leaves[b]["solid"]))>1e-10:
                v=vol(leaves[a]["solid"],leaves[b]["solid"])
                if v>1e-7:contacts.append(dict(hatch=a,other=b,volume_m3=v,category="d"))
    door=rows["doors_L4-medical"]["shape"]
    port=leaves["hatch_L3L4_0"]["shape"] # copied L1 id 0: negative Y (180 degrees)
    z_gap=port["z0"]-door["z1"]
    assert abs(z_gap-.1517525274902328)<1e-6
    pressure=rows["pressure_vessel"]["shape"]
    inner_radius=pressure["R"]-pressure["t"]
    clearance=min(inner_radius-math.hypot(max(abs(d["shape"]["y0"]),abs(d["shape"]["y1"])),
                     max(abs(d["shape"]["z0"]),abs(d["shape"]["z1"]))) for d in leaves.values())
    containment=clearance>0 and all(pressure["xb"]<=v["shape"]["x0"] and v["shape"]["x1"]<=pressure["xc"] for v in leaves.values())
    report=dict(status="DECK_HATCHES_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS" if not contacts and containment else "STOP_D9_OR_CONTAINMENT",
       source_geometry_sha256=SHA,source_dry_t=868.1922552640087,ECON_dv_km_s=707.845,
       source_mass_rebooking_t=0,leaf_count=4,source_copy="hatch_L1L2_0/1 translated in X",
       bookings=budgets,
       hatches={name:dict(shape=x["shape"],mass_owner=x["owner"],source=x["source"],
                         floor_mount_m3=x["floor_mount_m3"],mass_estimate_kg=150) for name,x in leaves.items()},
       floors={k:dict(bore_count=2,bore_diameter_m=.8,visual_removed_m3=v["removed"],
                      floor_mass_credit_t=0) for k,v in floors.items()},
       checks=dict(D9_category_d=len(contacts),D9_contacts=contacts,
           physical_source_pairs_screened=len(scanned),
           floor_mount_category="c: identical to L1L2 source leaf/floor mount",
           medical_door_port_z_clearance_m=z_gap,
           L3_semantic_room_zone_corner_intrusion_m=max(0,math.hypot(1.89,.46)-1.9),
           L3_berths_and_partitions="NOT PHYSICALLY DRAWN; no independent clearance qualified",
           min_inner_pressure_radius_clearance_m=clearance,
           containment="PASS" if containment else "FAIL",
           G1_G12="NOT RUN / NOT REQUIRED"),
       exterior_six_state_changes=0,previous_L1_L2_glb_changes=0,viewer_source_changed=False)
    OUT.mkdir(parents=True,exist_ok=True)
    filename=OUT/"interior_deck_hatches_report.json"
    if contacts or not containment:
        filename.write_text(json.dumps(report,indent=2)+"\n")
        raise RuntimeError(report["status"]+"; see saved report")
    # Same GLB writer and extras schema as the L1 interior; independent overlay.
    gl=GLB()
    gl.nodes.append(dict(name="LOOM_WAYFARER_DECK_HATCHES",children=[1],
        extras=dict(source_geometry_sha256=SHA,mass_neutral=True,exterior_six_state_untouched=True)))
    gl.nodes.append(dict(name="system:HABITAT",children=[]))
    subs={}
    def add(name,obj,owner,deck,kind):
        if deck not in subs:
            idx=len(gl.nodes)
            gl.nodes.append(dict(name="subsystem:HABITAT/DECK_ACCESS_"+deck,children=[]))
            gl.nodes[1]["children"].append(idx)
            subs[deck]=idx
        mat=gl.material(kind,[.58,.66,.67] if kind=="hatch" else [.50,.54,.58],1.)
        mesh=gl.mesh(name,[obj],mat)
        ex=dict(zone="FORE",deck=deck,material="source-copy interior pressure fixture",
             print_group="HABITAT/DECK_ACCESS_"+deck,mass=rows[owner]["mass_t"],mass_unit="t",
             mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=owner,
             semantic_system="HABITAT",semantic_subsystem="DECK_ACCESS_"+deck,
             node_mass_rebooking_t=0,source_booking_repeated_nonadditive=True,
             source_geometry_sha256=SHA,finish_role="interior_pressure_structure",
             estimated_item_kg=150 if kind=="hatch" else 0)
        idx=len(gl.nodes)
        gl.nodes.append(dict(name="dry:"+name,mesh=mesh,extras=ex))
        gl.nodes[subs[deck]]["children"].append(idx)
    for name,item in floors.items():add(name,item["solid"],name,name[-2:],"floor")
    for name,item in leaves.items():add(name,item["solid"],item["owner"],"L2" if "L2L3" in name else "L4","hatch")
    raw=gl.finish(0,SHA)
    n,k=struct.unpack_from("<II",raw,12)
    assert k==0x4e4f534a
    doc=json.loads(raw[20:20+n])
    doc["asset"]["generator"]="LOOM Wayfarer kT-approved deck hatch assembly"
    doc["scenes"][0]["name"]="Wayfarer L2L3 L3L4 pressure hatch interior"
    for mat in doc["materials"]:
        mat["name"]=mat["name"].replace("CANON_FINISH/L1/","CANON_FINISH/DECK_ACCESS/")
    j=json.dumps(doc,separators=(",",":")).encode()
    j+=b" "*(-len(j)%4)
    tail=raw[20+n+8:]
    data=struct.pack("<4sII",b"glTF",2,12+8+len(j)+8+len(tail))+struct.pack("<II",len(j),0x4e4f534a)+j+struct.pack("<II",len(tail),0x004e4942)+tail
    dest=OUT/"interior_deck_hatches.glb"
    dest.write_bytes(data)
    report.update(glb=str(dest.relative_to(ROOT)),glb_sha256=hashlib.sha256(data).hexdigest(),
                  glb_bytes=len(data),mesh_nodes=6,picture=str(PIC.relative_to(ROOT)))
    # Evidence image: topological floor bores, leaf positions, and medical door gap.
    fig,(a,b)=plt.subplots(1,2,figsize=(13,6))
    for tag,dx,floor,owner in BOUNDARIES:
        fs=floors[floor]["source"]
        a.axhspan(fs["x0"],fs["x1"],color="#abb2b8",alpha=.4)
        for y in (-1.4,1.4):
            a.add_patch(Rectangle((y-.4,fs["x0"]),.8,.3,color="white",zorder=2))
        for number in (0,1):
            s=leaves["hatch_"+tag+"_"+str(number)]["shape"]
            a.add_patch(Rectangle((s["y0"],s["x0"]),s["y1"]-s["y0"],
                     s["x1"]-s["x0"],facecolor="#4a8990" if tag=="L2L3" else "#45755f",zorder=3))
        a.text(0,fs["x0"]+.15,floor,ha="center",va="center")
    a.set(xlim=(-2.5,2.5),ylim=(9.35,5.3),xlabel="Y (m): 0° and 180° ladderways",
          ylabel="Ship X (m), aft downward",title="Four parked-open leaves and two 0.8 m floor bores")
    s=port
    b.add_patch(Rectangle((s["x0"],s["z0"]),s["x1"]-s["x0"],s["z1"]-s["z0"],
                 color="#45755f",alpha=.85,label="L3/L4 leaf 180°"))
    b.add_patch(Rectangle((door["x0"],door["z0"]),door["x1"]-door["x0"],door["z1"]-door["z0"],
                 color="#ca9258",alpha=.85,label="L4 medical door"))
    b.annotate("",xy=(8.88,s["z0"]),xytext=(8.88,door["z1"]),arrowprops=dict(arrowstyle="<->",color="#9e3c32"))
    b.text(9.01,(s["z0"]+door["z1"])/2,"151.8 mm",color="#9e3c32",va="center")
    b.set(xlim=(8,11),ylim=(-1.1,.65),xlabel="Ship X (m)",ylabel="Ship Z (m)",title="Medical-door clearance (Z)")
    b.legend(loc="upper right")
    fig.suptitle("WAYFARER 2226  |  DECK PRESSURE HATCHES  |  D9=0 / CONTAINMENT PASS")
    fig.text(.5,.03,"L1/L2 source leaf geometry unchanged; four copied leaves. Mass-neutral; 0.30 t from each existing outfit booking.",ha="center")
    fig.tight_layout(rect=[0,.06,1,.93])
    fig.savefig(PIC,dpi=160)
    plt.close(fig)
    filename.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","bookings","checks","glb_sha256","picture")},indent=2))
if __name__=="__main__":
    main()
