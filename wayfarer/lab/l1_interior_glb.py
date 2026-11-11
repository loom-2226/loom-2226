#!/usr/bin/env python3
"""kT-approved L1 only. One independent GLB; BRep couch D9 + analytic hull containment.
No six-state files, source mass, FQ/G1-G12, or exterior geometry are touched.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

from build123d import Axis

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"packing_phase1b"))
import source_brep_pilot as P

GFILE=ROOT/"results/out/wayfarer_v05_geometry.json"
IFILE=ROOT/"config/wayfarer_v05_inputs.json"
DEC=ROOT/"config/kt_decisions.json"
OUT=ROOT/"render/out"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
DRY=868.1922552640087
DV=707.845
PANELS=[
  (-.26,-.13,0.,.35,-.35,.35),        # tall shoulder / upper contour
  (-.20,-.11,.35,1.12,-.35,.35),       # shallow lumbar / seat pan
  (-.25,-.14,1.12,1.58,-.35,.35),      # contoured knee / foot end
  (-.30,-.16,.15,1.05,-.33,-.28),      # left wing
  (-.30,-.16,.15,1.05,.28,.33),        # right wing
  (-.34,-.20,0.,.24,-.19,-.14),       # head restraint
  (-.34,-.20,0.,.24,.14,.19),
  (-.24,-.06,1.52,1.58,-.23,.23),      # foot retainer
  (-.13,0.,.65,.92,-.10,.10),         # contact mount, zero added mass
]
PRINT_NOTE=ROOT/"docs/L1_INTERIOR_PRINT_1_25_2026_11_12.md"
OUTPUT=OUT/"interior_L1.glb"
REPORT=OUT/"interior_L1_report.json"
CLASH=OUT/"interior_L1_COUCH_CLASH.svg"

def bound(shape):
    b=shape.bounding_box()
    return ((b.min.X,b.max.X),(b.min.Y,b.max.Y),(b.min.Z,b.max.Z))

def separated(a,b,eps=1e-6):
    return any(x[1]<=y[0]+eps or y[1]<=x[0]+eps for x,y in zip(a,b))

def pose(part,seat):
    h,f=seat["head"],seat["feet"]
    angle=math.degrees(math.atan2(f[1]-h[1],f[0]-h[0]))
    return part.rotate(Axis.X,angle).translate((seat["base_x"],h[0],h[1]))

def glpose(seat):
    h,f=seat["head"],seat["feet"]
    theta=math.atan2(f[1]-h[1],f[0]-h[0])
    return dict(translation=[seat["base_x"],h[1],-h[0]],
        rotation=[math.sin(theta/2),0,0,math.cos(theta/2)])

def collider_picture(station,bad,stations):
    # Diagnostic only: the sole extra output if a couch proves impossible.
    def to_px(y,z):return (420+y*66,425-z*66)
    items=['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="890" viewBox="0 0 940 890">',
      '<rect width="940" height="890" fill="#fff"/>',
      '<text x="26" y="42" font-size="23" font-family="Arial">L1 COUCH CLASH: STOP, STATION NOT MOVED</text>',
      '<circle cx="420" cy="425" r="274" fill="none" stroke="#778899" stroke-width="2"/>']
    for seat in stations:
        a,b=to_px(*seat["head"]),to_px(*seat["feet"])
        col="#dc3545" if seat["id"]==station else "#789bb1"
        items.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{col}" stroke-width="43" opacity=".68"/>')
        items.append(f'<text x="{(a[0]+b[0])/2:.1f}" y="{(a[1]+b[1])/2:.1f}" font-family="Arial" font-size="17">{seat["id"]}</text>')
    for i,x in enumerate(bad[:15]):
        items.append(f'<text x="32" y="{660+i*18}" font-family="Arial" font-size="14">{x["other"]}: intersection {x["volume_m3"]:.6f} m3</text>')
    items.append("</svg>")
    CLASH.write_text("\n".join(items))

class GLB:
    def __init__(self):
        self.data=bytearray();self.views=[];self.access=[];self.meshes=[];self.materials=[]
        self.nodes=[];self.mats={}
        self.sizes={}
    def view(self,blob,target):
        while len(self.data)%4:self.data.append(0)
        offset=len(self.data);self.data.extend(blob)
        i=len(self.views)
        self.views.append(dict(buffer=0,byteOffset=offset,byteLength=len(blob),target=target))
        return i
    def material(self,name,color,alpha=1.):
        key=(name,tuple(color),alpha)
        if key not in self.mats:
            self.mats[key]=len(self.materials)
            self.materials.append(dict(name="CANON_FINISH/L1/"+name,
                doubleSided=True,
                alphaMode="BLEND" if alpha<1 else "OPAQUE",
                pbrMetallicRoughness=dict(baseColorFactor=[*color,alpha],
                    metallicFactor=.12,roughnessFactor=.72)))
        return self.mats[key]
    def mesh(self,name,solids,material):
        if not isinstance(solids,(list,tuple)):solids=[solids]
        pos=[];norm=[];idx=[]
        # Retain exact BRep triangulation. No rescale, change of station or print exaggeration.
        for sh in solids:
            vv,ff=sh.tessellate(.017)
            for face in ff:
                pts=[[vv[k].X,vv[k].Y,vv[k].Z] for k in face]
                u=[pts[1][k]-pts[0][k] for k in range(3)]
                v=[pts[2][k]-pts[0][k] for k in range(3)]
                cr=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                n=math.sqrt(sum(t*t for t in cr))
                if n<1e-15:continue
                no=[t/n for t in cr]
                for pt in pts:
                    # Ship [x,y,z] -> glTF [x,z,-y].
                    pos.extend([pt[0],pt[2],-pt[1]])
                    norm.extend([no[0],no[2],-no[1]])
                    idx.append(len(idx))
        if len(idx)<3:raise RuntimeError("STOP export: empty mesh "+name)
        vb=self.view(struct.pack("<"+"f"*len(pos),*pos),34962)
        nb=self.view(struct.pack("<"+"f"*len(norm),*norm),34962)
        ib=self.view(struct.pack("<"+"I"*len(idx),*idx),34963)
        axes=[[pos[j] for j in range(k,len(pos),3)] for k in range(3)]
        vi=len(self.access);self.access.extend([
           dict(bufferView=vb,componentType=5126,count=len(pos)//3,type="VEC3",
                min=[min(a) for a in axes],max=[max(a) for a in axes]),
           dict(bufferView=nb,componentType=5126,count=len(norm)//3,type="VEC3"),
           dict(bufferView=ib,componentType=5125,count=len(idx),type="SCALAR")])
        mi=len(self.meshes)
        self.meshes.append(dict(name=name,primitives=[
            dict(attributes=dict(POSITION=vi,NORMAL=vi+1),indices=vi+2,material=material)]))
        self.sizes[name]=len(idx)//3
        return mi
    def finish(self,root_index,source_sha):
        while len(self.data)%4:self.data.append(0)
        doc=dict(asset=dict(version="2.0",generator="LOOM L1 kT-approved interior single-deck builder",
            extras=dict(source_geometry_sha256=source_sha,exterior_state_meshes_copied=0,
                source_mass_rebooking_t=0)),
            scene=0,scenes=[dict(name="WAYFARER L1 (independent from exterior six states)",
                nodes=[root_index])],nodes=self.nodes,meshes=self.meshes,
            materials=self.materials,accessors=self.access,bufferViews=self.views,
            buffers=[dict(byteLength=len(self.data))])
        js=json.dumps(doc,separators=(",",":")).encode()
        while len(js)%4:js+=b" "
        binary=struct.pack("<II",len(js),0x4e4f534a)+js
        binary+=struct.pack("<II",len(self.data),0x004e4942)+bytes(self.data)
        return struct.pack("<4sII",b"glTF",2,12+len(binary))+binary

def main():
    source=GFILE.read_bytes()
    digest=hashlib.sha256(source).hexdigest()
    if digest!=SHA:raise RuntimeError("STOP export: original source geometry changed")
    G=json.loads(source);I=json.loads(IFILE.read_text());D=json.loads(DEC.read_text())
    decision=D["wayfarer_l1_layout_approval_2026_11_12"]
    assert decision["decision"]=="kT APPROVED L1 LAYOUT; INTERIOR DRAW AUTHORIZED"
    assert I["habitat"]["core_note"].startswith("Central trunk: utilities, avionics racks and a goods lift; not an egress path.")
    assert abs(G["dry_t"]-DRY)<1e-8
    assert abs(decision["ECON_dv_km_s"]-DV)<1e-12
    seats=I["habitat"]["decks"][0]["command_layout"]["i4_lock"]["stations"]
    assert len(seats)==6 and {s["id"] for s in seats}=={"PILOT","NAV","S1","S2","S3","S4"}
    s4=next(s for s in seats if s["id"]=="S4")
    assert s4["center_yz"]==[2.4,-1.7] and decision["S4_final_ship_YZ_m"]==[2.4,-1.7]
    for s in seats:
        assert abs(math.dist(s["head"],s["feet"])-1.58)<.002
        assert abs(s["width"]-.7)<1e-8

    rows={v["id"]:v for v in G["parts"]}
    source_objs={}
    # Only physically authored L1 parts; omit old small duplicate booking proxies
    # and 1:1 seat-box surrogates replaced by actual couch instanced mesh.
    authored=("floor_L1","command_terrace","navigator_platform",
       "hatch_L1L2_0","hatch_L1L2_1",
       "i4_engineering_cabinet","i4_sensors_cabinet","i4_shared_map_table",
       "i4_equipment_workbench","i4_workbench_display","i4_low_g_command_point","i4_map_console")
    for name in authored:
        source_objs[name]=P.make(rows[name]["shape"])
    for prefix in ("i4_terrace_column_","i4_rails_","i4_lights_",
                   "i4_transfer_","i4_observation_rail_"):
        for name in sorted(k for k in rows if k.startswith(prefix)):
            source_objs[name]=P.make(rows[name]["shape"])
    # Ladder tubes and rungs are derived visual parts of booked distributed L1
    # outfitting. No ladder is a new mass-booked item.
    derived={}
    for i,yy in enumerate((-1.4,1.4)):
        for k,zz in enumerate((-.22,.22)):
            derived[f"ladder_L1_{i}_rail_{k}"]=(P.tube(dict(p0=[1.95,yy,zz],p1=[3.05,yy,zz],r=.019)),"outfit_L1")
        for k in range(5):
            x=2.00+.24*k
            derived[f"ladder_L1_{i}_rung_{k}"]=(P.tube(dict(p0=[x,yy,-.22],p1=[x,yy,.22],r=.014)),"outfit_L1")
    # Source r=0.90m core preserved; this is a short L1 visual cut of a
    # UTILITY / GOODS-LIFT trunk, not a new room, habitable crew route or berth.
    derived["core_trunk_L1_wall"]=(P.sector(dict(k="sector",x0=2.56,x1=3.3,
                     r0=.84,r1=.90,a0=0,a1=360)),"core_trunk")
    derived["core_trunk_L1_goods_lift"]=(P.box(2.56,3.25,-.20,.20,-.20,.20),"core_trunk")
    for idx,(y,z) in enumerate(((.54,0),(-.54,0),(0,.54),(0,-.54))):
        derived[f"core_trunk_L1_avionics_rack_{idx}"]=(
            P.box(2.62,3.20,y-.12,y+.12,z-.12,z+.12),"core_trunk")

    common=[P.box(*v) for v in PANELS]
    # Every couch instance uses exactly this ONE source-1.58m BRep component set.
    couches={s["id"]:[pose(x,s) for x in common] for s in seats}
    d9=[];contain=[];collisions=[]
    # Conservative full station clash: exact BRep intersections between all
    # couch elements and each other station, plus all pre-booked L1 parts
    # (excluding semantic room/outfit mass envelopes).
    solid_catalogue=dict(source_objs)
    solid_catalogue.update({k:obj for k,(obj,_) in derived.items()})
    for s in seats:
        station=s["id"]; components=couches[station]
        for n,other in solid_catalogue.items():
            bb=bound(other)
            for piece in components:
                if separated(bound(piece),bb):continue
                cut=piece & other
                v=float(cut.volume) if cut is not None else 0.
                if v>1e-6:
                    collisions.append(dict(station=station,other=n,volume_m3=v))
        for other_st,comps in couches.items():
            if other_st<=station:continue
            for part in components:
                for obj in comps:
                    if separated(bound(part),bound(obj)):continue
                    overlap=part & obj
                    v=float(overlap.volume) if overlap is not None else 0.
                    if v>1e-6:
                        collisions.append(dict(station=station,other="COUCH_"+other_st,volume_m3=v))
    # True x/r profile of source *inner* pressure ellipsoid (convex) plus
    # 4.27m cylindrical section, tested on ALL couch solid tessellation
    # vertices. Convexity ensures all triangle interiors are inside too.
    pv=rows["pressure_vessel"]["shape"]
    inner_xa=pv["xa"]+pv["t"];inner_xb=pv["xb"];inner_R=pv["R"]-pv["t"]
    min_gap=float("inf")
    for s in seats:
        min_station=float("inf")
        for piece in couches[s["id"]]:
            verts,_=piece.tessellate(.012)
            for pt in verts:
                r=math.hypot(pt.Y,pt.Z)
                if r>=inner_R:gap=inner_R-r
                else:
                    sx=inner_xb-(inner_xb-inner_xa)*math.sqrt(1-(r/inner_R)**2)
                    gap=min(pt.X-sx,inner_R-r)
                min_station=min(min_station,gap)
        contain.append(dict(station=s["id"],source_pressure_inner_shell_clearance_min_m=round(min_station,6),
            inside_pressure_hull=min_station>=-1e-5))
        min_gap=min(min_gap,min_station)
    d9_count=sum(c["volume_m3"]>0.01 for c in collisions)
    if collisions or any(not z["inside_pressure_hull"] for z in contain):
        bad=collisions or [dict(station=z["station"],other="PRESSURE_HULL",volume_m3=max(0,-z["source_pressure_inner_shell_clearance_min_m"])) for z in contain if not z["inside_pressure_hull"]]
        collider_picture(bad[0]["station"],bad,seats)
        REPORT.write_text(json.dumps(dict(status="STOP_COUCH_CLASH",clashes=collisions,
            containment=contain,picture=str(CLASH.relative_to(ROOT))),indent=2)+"\n")
        raise RuntimeError("STOP: L1 couch cannot fit without clash/containment failure. See "+str(CLASH))

    gl=GLB()
    pal={"couch":([.17,.22,.27],1.0),"floor":([.27,.30,.33],1.0),
         "fixtures":([.29,.33,.37],1.0),"rail":([.51,.55,.58],1.0),
         "display":([.08,.24,.30],1.0),"hatch":([.42,.45,.48],1.0),
         "utility":([.26,.31,.36],1.0),"volume":([.18,.46,.45],.10),
         "outfit":([.30,.31,.36],.16)}
    couch_mat=gl.material("contoured_couch",*pal["couch"])
    couch_mesh=gl.mesh("i4_contoured_couch_1p58m_SHARED",common,couch_mat)
    metadata={}
    root=len(gl.nodes)
    gl.nodes.append(dict(name="LOOM_WAYFARER_L1_INTERIOR",children=[],
        extras=dict(source_geometry_sha256=SHA,mass_neutral=True,exterior_six_state_untouched=True)))
    systems={}
    def group(name,sub):
        key=(name,sub)
        if key not in systems:
            sn="system:"+name
            root_sys=next((i for i,node in enumerate(gl.nodes) if node.get("name")==sn),None)
            if root_sys is None:
                root_sys=len(gl.nodes)
                gl.nodes.append(dict(name=sn,children=[]))
                gl.nodes[root]["children"].append(root_sys)
            systems[key]=len(gl.nodes)
            gl.nodes.append(dict(name="subsystem:"+name+"/"+sub,children=[]))
            gl.nodes[root_sys]["children"].append(systems[key])
        return systems[key]
    def node(name,mesh,owner,kind,pose_kwargs=None,system="HABITAT",subsystem="L1",extra=None):
        src=rows[owner]
        mass=src["mass_t"]
        assert math.isfinite(mass) and mass>=0
        e=dict(zone="FORE",deck="L1",material=src["mat"],
            print_group=system+"/"+subsystem,mass=mass,mass_unit="t",
            mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=owner,
            semantic_system=system,semantic_subsystem=subsystem,node_mass_rebooking_t=0,
            finish_role="interior_pressure_structure",source_booking_repeated_nonadditive=True,
            l1_part_kind=kind,source_geometry_sha256=SHA)
        if extra:e.update(extra)
        entry=dict(name=name,mesh=mesh,extras=e)
        if pose_kwargs:entry.update(pose_kwargs)
        idx=len(gl.nodes);gl.nodes.append(entry)
        gl.nodes[group(system,subsystem)]["children"].append(idx)
        metadata[name]=e
    for seat in seats:
        name="dry:i4_seat_"+seat["id"]
        node(name,couch_mesh,"i4_seat_"+seat["id"],"1.58m_contoured_couch",
             glpose(seat),extra=dict(couch_local_mesh_instanced=True,
               contoured_nominal_length_m=1.58,seat_role=seat["role"],
               station_source_yz_m=seat["center_yz"]))
    for name,obj in sorted(source_objs.items()):
        if name in ("floor_L1","command_terrace","navigator_platform"):mt="floor"
        elif name.startswith("hatch_"):mt="hatch"
        elif name.startswith("i4_lights") or "display" in name or name=="i4_map_console":mt="display"
        elif name.startswith(("i4_rails_","i4_transfer_","i4_observation_rail_","i4_terrace_column_")):mt="rail"
        else:mt="fixtures"
        color,alpha=pal[mt]
        m=gl.mesh(name,[obj],gl.material(mt,color,alpha))
        node("dry:"+name,m,name,mt)
    for name,(obj,owner) in sorted(derived.items()):
        typ="utility" if name.startswith("core_trunk") else "rail"
        color,alpha=pal[typ]
        m=gl.mesh(name,[obj],gl.material(typ,color,alpha))
        node("dry:"+name,m,owner,typ,system="HABITAT",
            subsystem="shared_access" if typ=="utility" else "L1",
            extra=dict(derived_from_source_booking=True,
                       not_crew_egress=typ=="utility",
                       no_new_mass=True))
    # Semantic source volumes only. No inferred furniture, no solid-collision role.
    for name,typ in (("room_L1-command","room_semantic_volume"),
                     ("outfit_L1","outfit_distributed_mass_volume")):
        src=rows[name]
        idx=len(gl.nodes)
        system,sub="HABITAT","L1"
        gl.nodes.append(dict(name="dry:"+name,
            extras=dict(zone="FORE",deck="L1",material=src["mat"],
               print_group="HABITAT/L1",mass=src["mass_t"],mass_unit="t",
               mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=name,
               semantic_system=system,semantic_subsystem=sub,node_mass_rebooking_t=0,
               semantic_volume_only=True,no_furnishings_implied=True,
               shape_source=src["shape"],l1_part_kind=typ)))
        gl.nodes[group("HABITAT","L1")]["children"].append(idx)
    output=gl.finish(root,SHA)
    OUT.mkdir(exist_ok=True,parents=True)
    OUTPUT.write_bytes(output)
    raw=OUTPUT.read_bytes()
    n,t=struct.unpack_from("<II",raw,12)
    doc=json.loads(raw[20:20+n])
    seatnodes=[v for v in doc["nodes"] if v.get("name","").startswith("dry:i4_seat_")]
    assert len(seatnodes)==6 and {v["mesh"] for v in seatnodes}=={couch_mesh}
    assert len({v["extras"]["source_mass_owner_id"] for v in seatnodes})==6
    assert sum(1 for v in doc["nodes"] if v.get("name","").startswith("dry:core_trunk_L1_goods_lift"))==1
    assert all(v["extras"]["node_mass_rebooking_t"]==0 for v in doc["nodes"] if "mesh" in v)
    assert all("mesh" not in v for v in doc["nodes"] if v.get("name") in ("dry:room_L1-command","dry:outfit_L1"))
    status="L1_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS"
    report=dict(status=status,classification="INTERIOR_L1_ONLY",source_geometry_sha256=SHA,
       glb_path=str(OUTPUT.relative_to(ROOT)),glb_sha256=hashlib.sha256(output).hexdigest(),
       dry_t=DRY,ECON_dv_km_s=DV,source_mass_delta_t=0,exterior_six_state_changes=0,
       checks=dict(D9_category_d=0,couch_collisions_any_volume=0,
          containment="PASS",source_pressure_containment_min_clearance_m=round(min_gap,6),
          G1_G12="NOT RUN / NOT REQUIRED"),
       couch_instances=[dict(id=s["id"],centre_yz_m=s["center_yz"],base_x_m=s["base_x"],
                       common_mesh_index=couch_mesh,booked_mass_t=rows["i4_seat_"+s["id"]]["mass_t"])
                        for s in seats],
       couch_local_panels_m=PANELS,
       couch_brep_component_count=len(common),
       source_visible_parts=len(source_objs),source_derived_utilities_ladders=len(derived),
       mesh_nodes=len([x for x in doc["nodes"] if "mesh" in x]),
       semantic_volume_nodes=["room_L1-command","outfit_L1"],
       source_core_note=I["habitat"]["core_note"],
       ladderway_egress_only=True,
       metadata_source_bookings_nonadditive=True,
       original_station_positions_unmoved=True,
       source_qualifications_held=["occupant body 4g egress","hatch pressure seal and actuation",
          "couch hardpoint/occupant fit","optical sightline occlusion"],
       print_note_path=str(PRINT_NOTE.relative_to(ROOT)))
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    PRINT_NOTE.write_text("""# Wayfarer L1 independent interior: 1:25 print interpretation
**kT-approved L1; original ship model remains true scale. This is a derived print guide, not a mass booking.**

| Element | At 1:25 | Print interpretation |
|---|---:|---|
| L1 annulus outside diameter 8.30 m | 332 mm | Actual deck geometry, two ladder holes left open |
| Utility trunk 1.80 m outside diameter | 72 mm | Goods lift, 4 rack proxies, central utilities; NOT crew egress |
| Ladderways 0.80 m diameter each | 32 mm | Two and ONLY two crew egress routes |
| Six 1.58 x 0.70 m contoured couches | 63.2 x 28.0 mm each | Single shared contour, six repeated positions; physical geometry |
| Command terrace 3.40 x 2.10 m | 136 x 84 mm | Physical deck/platform |
| NAV platform 2.65 x 2.20 m | 106 x 88 mm | Physical deck/platform |
| Open hatch leaf 0.92 m | 36.8 mm | Source-booked leaf, display open |
| Existing rails 22–25 mm tube | 0.88–1.00 mm | Fine geometry, fragile at print size |
| Display surface, screen panels | varies | Draw existing booked outlines; interior screen graphics are DECALS |
| Station designators, NO STEP, hazard, interface labels, indicators and bolt dots | sub-mm | DECALS and paint guide, not additional geometry |

Render \`interior_L1.glb\` once, separately from the six exterior states. Do not convert semantic \`room_*\` / distributed \`outfit_*\` into furniture. No mass, source BRep or exterior envelope credit. Detailed material and clearance hardware remain unqualified.
""")
    print(json.dumps(dict(status=status,glb=OUTPUT.name,bytes=len(output),
        mesh_instances=6,mesh_nodes=report["mesh_nodes"],source_dry_t=DRY,
        ECON_dv_km_s=DV,clearance_min_m=min_gap),indent=2))

if __name__=="__main__":main()
