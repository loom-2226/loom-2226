#!/usr/bin/env python3
"""kT-approved B3 merge into ONE independent Wayfarer L1 interior GLB.

Source shape authority: PR #517 B3 Python generator; PR #516 only for booked
fixture detailing, mass partition, role nomenclature and 4g limitations.
D9: triangle surface intersection in exact source world coordinates, via FCL;
both centre-down/wing-closed and centre-lifted/wing-open states. No G1-G12.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib, importlib.util, json, math, struct
import numpy as np
import fcl
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"packing_phase1b"))
import source_brep_pilot as P

GLB=ROOT/"render/out/interior_L1.glb"
REPORT=ROOT/"render/out/interior_L1_report.json"
DIAG=ROOT/"render/out/interior_L1_B3_D9_STOP.svg"
DEC=ROOT/"config/kt_decisions.json"
GEOM=ROOT/"results/out/wayfarer_v05_geometry.json"
CONFIG=ROOT/"config/wayfarer_v05_inputs.json"
PR517=ROOT/"lab/l1_station_b3_generator.py"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
DRY=868.1922552640087
DV=707.845
SEAT_BOOKING_KG=51.18518656421065
COMMON_KG=46.
ADDON_KG=SEAT_BOOKING_KG-COMMON_KG
# Explicit conservative conceptual mass partition. B3 arch mesh is a *surface
# envelope*, NOT a homogeneous 35mm solid bar. Assume 2mm-walled composite
# with hinges within the 2.80kg frame allowance.
BUDGET={"hollow_composite_arch_hinges_kg":2.80,
        "thin_film_3kg_per_m2_kg":.55,
        "role_controls_kg":1.50,
        "harness_wiring_connectors_kg":.25}
MASS_EST=sum(BUDGET.values())
if MASS_EST>ADDON_KG+1e-9:
    raise RuntimeError("STOP HALO MASS: estimated B3+controls over "+str(ADDON_KG)+" kg")

def load_glb(path):
    data=path.read_bytes()
    if data[:4]!=b"glTF" or struct.unpack_from("<I",data,8)[0]!=len(data):
        raise RuntimeError("STOP: non-GLB input "+str(path))
    jlen,jtyp=struct.unpack_from("<II",data,12)
    assert jtyp==0x4e4f534a
    doc=json.loads(data[20:20+jlen])
    boff=20+jlen
    blen,btyp=struct.unpack_from("<II",data,boff)
    assert btyp==0x004e4942
    return doc,bytearray(data[boff+8:boff+8+blen])

def read_accessor(doc,binary,idx):
    ac=doc["accessors"][idx];vw=doc["bufferViews"][ac["bufferView"]]
    typ=ac["componentType"]; size={"SCALAR":1,"VEC3":3,"VEC4":4}[ac["type"]]
    dt={5126:np.dtype("<f4"),5125:np.dtype("<u4"),5123:np.dtype("<u2")}[typ]
    offset=vw.get("byteOffset",0)+ac.get("byteOffset",0)
    stride=vw.get("byteStride",size*dt.itemsize)
    if stride==size*dt.itemsize:
        out=np.frombuffer(binary,dtype=dt,count=ac["count"]*size,offset=offset).copy()
        return out.reshape(ac["count"],size)
    return np.array([np.frombuffer(binary,dtype=dt,count=size,offset=offset+i*stride)
                     for i in range(ac["count"])],dtype=dt)

def trimeshes(doc,binary,idx):
    out=[]
    for pr in doc["meshes"][idx]["primitives"]:
        if "POSITION" not in pr["attributes"]:continue
        pos=read_accessor(doc,binary,pr["attributes"]["POSITION"]).astype(float)
        faces=read_accessor(doc,binary,pr["indices"]).astype(np.int64).reshape(-1,3)
        out.append((pos,faces))
    return out

def view(doc,binary,bytes_,target=None):
    while len(binary)%4:binary.append(0)
    o=len(binary);binary.extend(bytes_)
    item=dict(buffer=0,byteOffset=o,byteLength=len(bytes_))
    if target is not None:item["target"]=target
    i=len(doc["bufferViews"]);doc["bufferViews"].append(item);return i

def accessor(doc,binary,arr,component,typ,target=None):
    arr=np.ascontiguousarray(arr)
    v=view(doc,binary,arr.tobytes(),target)
    idx=len(doc["accessors"])
    item=dict(bufferView=v,byteOffset=0,componentType=component,
              count=len(arr),type=typ)
    if typ=="VEC3":
        item["min"]=arr.min(axis=0).tolist()
        item["max"]=arr.max(axis=0).tolist()
    doc["accessors"].append(item)
    return idx

def append_mesh(doc,binary,name,pieces,material_ids,origin=None):
    """B3 source Mesh.P/T pieces; no design geometry invented in this builder."""
    primitives=[];local=[]
    for role,group in pieces.items():
        pp=[];ff=[];cursor=0
        for src_mesh,ids in group:
            off=0
            for i,P0 in enumerate(src_mesh.P):
                if i in ids:
                    P0=np.asarray(P0,dtype=float)
                    faces=np.asarray(src_mesh.T[i],dtype=np.int64)-off
                    pp.append(P0);ff.append(faces+cursor);cursor+=len(P0)
                off+=len(P0)
        if not pp:continue
        xyz=np.concatenate(pp)
        triangles=np.concatenate(ff)
        # Convert the exact B3 u/v/h source vertices into L1 couch mesh axes.
        xyz=np.c_[-xyz[:,2],-xyz[:,1],-xyz[:,0]]
        if origin is not None:xyz-=np.asarray(origin)
        # Nonindexed flat mesh allows accurate per-triangle normals.
        p=xyz[triangles].reshape(-1,3)
        edge1=p.reshape(-1,3,3)[:,1]-p.reshape(-1,3,3)[:,0]
        edge2=p.reshape(-1,3,3)[:,2]-p.reshape(-1,3,3)[:,0]
        no=np.cross(edge1,edge2)
        length=np.linalg.norm(no,axis=1)
        good=length>1e-12
        if not good.any():continue
        face_pos=p.reshape(-1,3,3)[good].reshape(-1,3).astype("<f4")
        normals=np.repeat((no[good]/length[good,None]),3,axis=0).astype("<f4")
        faces=np.arange(len(face_pos),dtype="<u4").reshape(-1,3)
        vp=accessor(doc,binary,face_pos,5126,"VEC3",34962)
        vn=accessor(doc,binary,normals,5126,"VEC3",34962)
        vi=accessor(doc,binary,faces.ravel(),5125,"SCALAR",34963)
        primitives.append(dict(attributes=dict(POSITION=vp,NORMAL=vn),
                               indices=vi,material=material_ids[role]))
        local.append((face_pos.astype(float),faces))
    if not primitives:raise RuntimeError("STOP export: empty B3 mesh "+name)
    mi=len(doc["meshes"]);doc["meshes"].append(dict(name=name,primitives=primitives))
    return mi,local

def fcl_obj(segments):
    verts=[];faces=[];offset=0
    for p,f in segments:
        verts.append(np.asarray(p,dtype=np.float64))
        faces.append(np.asarray(f,dtype=np.int32)+offset)
        offset+=len(p)
    vv=np.concatenate(verts);ff=np.concatenate(faces)
    model=fcl.BVHModel();model.beginModel(len(vv),len(ff))
    model.addSubModel(vv,ff);model.endModel()
    return fcl.CollisionObject(model)

def quat_apply(pts,q):
    q=np.asarray(q,dtype=float);v=q[:3];w=q[3]
    pts=np.asarray(pts,dtype=float)
    tv=2*np.cross(v[None,:],pts)
    return pts + w*tv + np.cross(v[None,:],tv)

def quat_axis(axis,angle_deg):
    axis=np.asarray(axis,dtype=float);axis/=np.linalg.norm(axis)
    a=math.radians(angle_deg)*.5
    return [*(axis*math.sin(a)),math.cos(a)]

def world(segments,base,shift=None,rotation=None):
    out=[]
    for p,f in segments:
        pts=p.copy()
        if rotation is not None:pts=quat_apply(pts,rotation)
        if shift is not None:pts+=np.asarray(shift)
        pts=quat_apply(pts,base["rotation"])+np.asarray(base["translation"])
        out.append((pts,f))
    return out

def failed_picture(reason,records,seats):
    def px(y,z):return (480+78*y,460-78*z)
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="1050" viewBox="0 0 1240 1050">',
       '<rect width="1240" height="1050" fill="#fff"/>',
       '<text x="30" y="48" font-family="Arial" font-size="25">WAYFARER L1 B3 STOP: '+reason+'</text>',
       '<circle cx="480" cy="460" r="324" fill="none" stroke="#54616e" stroke-width="3"/>']
    for st in seats:
        h,f=st["head"],st["feet"]
        a=px(*h);b=px(*f)
        lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#819ba3" stroke-width="48" opacity=".75"/>'%(a[0],a[1],b[0],b[1]))
        cx,cy=px(*st["center_yz"])
        lines.append('<text x="%s" y="%s" font-family="Arial" font-size="18">%s</text>'%(cx,cy,st["id"]))
    for i,detail in enumerate(records[:12]):
        lines.append('<text x="45" y="%s" font-family="Arial" font-size="16">%s</text>'%(790+i*20,detail))
    lines.append('</svg>')
    DIAG.write_text("\n".join(lines))

def shapes_for_fixture(name,sh):
    """#516 proposal: shaped geometry INSIDE unchanged, source-booked box."""
    if sh["k"]!="box":raise RuntimeError("Fixture shape unexpectedly not box "+name)
    x0,x1,y0,y1,z0,z1=[sh[k] for k in ("x0","x1","y0","y1","z0","z1")]
    dx,dy,dz=x1-x0,y1-y0,z1-z0
    if name in ("i4_shared_map_table","i4_equipment_workbench"):
        rim=.025;depth=min(.027,dx*.22)
        outer=P.box(x0,x0+depth,y0,y1,z0,z1)
        inner=P.box(x0-.002,x0+depth+.002,y0+rim,y1-rim,z0+rim,z1-rim)
        shapes=[outer-inner,P.box(x0+depth,x0+min(dx,depth+.027),
                      y0+rim,y1-rim,z0+rim,z1-rim)]
        for y in (y0+rim/2,y1-rim/2):
            for z in (z0+rim/2,z1-rim/2):
                shapes.append(P.box(x0+depth,x1,y-.011,y+.011,z-.011,z+.011))
        return shapes
    if name in ("i4_mission_table","i4_workbench"):
        # Already booked inner cassette, not a separate second worktop.
        lip=min(.022,dx*.22)
        outer=P.box(x0,x1,y0,y1,z0,z1)
        return [outer-P.box(x0+lip,x1+.002,y0+lip,y1-lip,z0+lip,z1-lip)]
    if name in ("i4_engineering_cabinet","i4_sensors_cabinet"):
        wall=.024
        outer=P.box(x0,x1,y0,y1,z0,z1)
        hollow=outer-P.box(x0+wall,x1-wall,y0+wall,y1-wall,z0+wall,z1-wall)
        front=[P.box(x0-.0000,x0+.024,y0+.028,(y0+y1)/2-.010,z0+.035,z1-.035),
               P.box(x0-.0000,x0+.024,(y0+y1)/2+.010,y1-.028,z0+.035,z1-.035)]
        return [hollow,*front]
    if name=="i4_cabinetry":
        wall=min(.023,dx*.2,dy*.2,dz*.2)
        return [P.box(x0,x1,y0,y1,z0,z1)-
                P.box(x0+wall,x1+.001,y0+wall,y1-wall,z0+wall,z1-wall)]
    if name in ("i4_workbench_display","i4_map_console"):
        wall=min(.017,dx*.2,dy*.2,dz*.2)
        return [P.box(x0,x1,y0,y1,z0,z1)-
                P.box(x0-.001,x1+.001,y0+wall,y1-wall,z0+wall,z1-wall),
                P.box(x0+wall,x1-wall,y0+wall,y1-wall,z0+wall,z1-wall)]
    raise RuntimeError("Unmapped fixture "+name)

def mesh_from_brep(doc,binary,name,shapes,matidx):
    vertices=[];faces=[];offset=0
    for shape in shapes:
        vv,ff=shape.tessellate(.016)
        vert=np.array([[p.X,p.Z,-p.Y] for p in vv],dtype=float)
        tri=np.asarray(ff,dtype=np.int64)
        vertices.append(vert);faces.append(tri+offset);offset+=len(vert)
    pts=np.concatenate(vertices);tri=np.concatenate(faces)
    p=pts[tri].reshape(-1,3,3)
    no=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0])
    lens=np.linalg.norm(no,axis=1);good=lens>1e-12
    ps=p[good].reshape(-1,3).astype("<f4")
    nn=np.repeat(no[good]/lens[good,None],3,axis=0).astype("<f4")
    ix=np.arange(len(ps),dtype="<u4")
    a=accessor(doc,binary,ps,5126,"VEC3",34962)
    b=accessor(doc,binary,nn,5126,"VEC3",34962)
    c=accessor(doc,binary,ix,5125,"SCALAR",34963)
    mi=len(doc["meshes"])
    doc["meshes"].append(dict(name=name,primitives=[
        dict(attributes=dict(POSITION=a,NORMAL=b),indices=c,material=matidx)]))
    return mi

def save(doc,binary,path):
    while len(binary)%4:binary.append(0)
    doc["buffers"][0]["byteLength"]=len(binary)
    js=json.dumps(doc,separators=(",",":")).encode()
    while len(js)%4:js+=b" "
    chunks=struct.pack("<II",len(js),0x4e4f534a)+js
    chunks+=struct.pack("<II",len(binary),0x004e4942)+bytes(binary)
    raw=struct.pack("<4sII",b"glTF",2,12+len(chunks))+chunks
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()

def main():
    if hashlib.sha256(GEOM.read_bytes()).hexdigest()!=SHA:raise RuntimeError("source geometry changed")
    D=json.loads(DEC.read_text());approved=D["l1_station_b3_merge_2026_11_12"]
    assert approved["authority"]=="kT APPROVED B3 PR #517"
    G=json.loads(GEOM.read_text());rows={r["id"]:r for r in G["parts"]}
    I=json.loads(CONFIG.read_text())
    seats=I["habitat"]["decks"][0]["command_layout"]["i4_lock"]["stations"]
    assert len(seats)==6 and next(s for s in seats if s["id"]=="S4")["center_yz"]==[2.4,-1.7]
    assert abs(G["dry_t"]-DRY)<1e-8
    assert abs(approved["halo_and_controls_budget_kg"]-ADDON_KG)<1e-9
    # Import the actual #517 generator; its standalone proposal output remains
    # separate and is not promoted into exterior files.
    spec=importlib.util.spec_from_file_location("l1_station_b3_generator",PR517)
    B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
    source_doc,source_bin=load_glb(GLB)
    doc=deepcopy(source_doc);binary=source_bin
    original_positions={n["name"]:(tuple(n.get("translation",[])),tuple(n.get("rotation",[])))
                        for n in doc["nodes"] if n.get("name","").startswith("dry:i4_seat_")}
    old_mass=[(n["name"],n["extras"]["mass"],n["extras"]["source_mass_owner_id"])
              for n in doc["nodes"] if "mesh" in n]
    orig_exterior=doc["asset"]["extras"].get("exterior_state_meshes_copied")
    assert orig_exterior==0
    palette={}
    for name,(color,metal,rough,emission) in B.MAT.items():
        palette[name]=len(doc["materials"])
        m=dict(name="CANON_FINISH/L1/B3/"+name,doubleSided=True,
               pbrMetallicRoughness=dict(baseColorFactor=list(color)+[1.],
                   metallicFactor=metal,roughnessFactor=rough))
        if emission is not None:m["emissiveFactor"]=emission
        doc["materials"].append(m)
    def groups(ids):
        return {k:[(B.M[k],ids.get(k,set()))] for k in B.M}
    common={k:[(B.M[k],set(range(len(B.M[k].P))))] for k in B.M}
    for k in ("surround","screen"):
        if len(B.M[k].P)!=10:raise RuntimeError("B3 source changed screen split")
        common[k]=[(B.M[k],set())]
    if len(B.M["metal"].P)!=15:raise RuntimeError("B3 source changed halo subparts")
    common["metal"]=[(B.M["metal"],set(range(11)))]
    cm,geo_common=append_mesh(doc,binary,"B3_shared_46kg_couch",common,palette)
    centre={k:[(B.M[k],set())] for k in B.M}
    centre["screen"]=[(B.M["screen"],set(range(8)))]
    centre["surround"]=[(B.M["surround"],set(range(8)))]
    centre["metal"]=[(B.M["metal"],{11,12})]
    cp=np.array([-.98,0.,-.02])
    cem,geo_centre=append_mesh(doc,binary,"B3_halo_centre_lift_back",centre,palette,cp)
    wingmeshes={};wgeos={};wpiv={}
    for s,screen_idx,metal_idx in [(-1,8,13),(1,9,14)]:
        wing={k:[(B.M[k],set())] for k in B.M}
        wing["screen"]=[(B.M["screen"],{screen_idx})]
        wing["surround"]=[(B.M["surround"],{screen_idx})]
        wing["metal"]=[(B.M["metal"],{metal_idx})]
        # glTF y=-v, original hinge at u=.02, v=s*.31, h=.84.
        pivot=np.array([-.84,-s*.31,-.02])
        wingmeshes[s],wgeos[s]=append_mesh(doc,binary,"B3_wing_"+str(s),wing,palette,pivot)
        wpiv[s]=pivot
    roles={}
    for rid in B.ROLES:
        add=B.addon(rid)
        all_roles={k:[(add[k],set(range(len(add[k].P))))] for k in B.M}
        roles[rid]=append_mesh(doc,binary,"B3_controls_"+rid,all_roles,palette)
    map_of={n["name"]:n for n in doc["nodes"]}
    station_instances={}
    for seat in seats:
        rid=seat["id"];n=map_of["dry:i4_seat_"+rid]
        assert abs(n["extras"]["mass"]*1000-SEAT_BOOKING_KG)<1e-7
        n["mesh"]=cm
        n["extras"].update(station_design="B3_split_halo",common_couch_budget_kg=COMMON_KG,
          halo_and_controls_budget_kg=ADDON_KG,
          role_variants_source="#517 generator and #516 role names",
          source_mass_rebooking_t=0,source_mass_owner_id="i4_seat_"+rid)
        old_children=list(n.get("children",[]));n["children"]=old_children
        station_instances[rid]=dict(base=n,shapes={"common":geo_common,"controls":roles[rid][1]})
        def attach(name,mesh,kind,shift=None,origin=None):
            e=deepcopy(n["extras"]);e["b3_component"]=kind;e["node_mass_rebooking_t"]=0
            e["source_booking_repeated_nonadditive"]=True
            entry=dict(name="dry:B3_"+rid+"_"+name,mesh=mesh,extras=e)
            if shift is not None:entry["translation"]=list(map(float,shift))
            idx=len(doc["nodes"]);doc["nodes"].append(entry);n["children"].append(idx)
            return idx
        station_instances[rid]["controls_id"]=attach("controls",roles[rid][0],"role_controls")
        station_instances[rid]["centre_id"]=attach("centre",cem,"halo_centre",cp)
        station_instances[rid]["wing_ids"]={}
        for s in (-1,1):
            station_instances[rid]["wing_ids"][s]=attach("wing_"+str(s),
                     wingmeshes[s],"halo_wing",wpiv[s])
    # glTF open/closed animation, ONE L1 GLB. The initial pose is closed.
    times=accessor(doc,binary,np.array([0.,1.],dtype="<f4"),5126,"SCALAR")
    anim=dict(name="B3_centre_lifts_back_wings_swing_aside",
              samplers=[],channels=[])
    for rid,inst in station_instances.items():
        for kind,nodeid,openrot in [
           ("centre",inst["centre_id"],quat_axis([0,1,0],70)),
           ("wing_neg",inst["wing_ids"][-1],quat_axis([1,0,0],80)),
           ("wing_pos",inst["wing_ids"][1],quat_axis([1,0,0],-80))]:
            sample=np.array([[0,0,0,1],openrot],dtype="<f4")
            a=accessor(doc,binary,sample,5126,"VEC4")
            idx=len(anim["samplers"])
            anim["samplers"].append(dict(input=times,output=a,interpolation="LINEAR"))
            anim["channels"].append(dict(sampler=idx,
                    target=dict(node=nodeid,path="rotation")))
    doc.setdefault("animations",[]).append(anim)
    # #516 fixture shaping: all BRep solids are subsets of the fixed source
    # fixture box, and preserve each exact distinct existing source owner.
    fixture_ids=("i4_shared_map_table","i4_mission_table",
      "i4_equipment_workbench","i4_workbench",
      "i4_engineering_cabinet","i4_sensors_cabinet","i4_cabinetry",
      "i4_workbench_display","i4_map_console")
    fxtures=[]
    for fid in fixture_ids:
        s=rows[fid]["shape"]
        solids=shapes_for_fixture(fid,s)
        mi=mesh_from_brep(doc,binary,"B3_shaped_"+fid,solids,palette["shell"] if "cabinet" in fid else palette["surround"])
        name="dry:"+fid
        if name not in map_of:
            # PR #514 drew the parent tables/workbench/cabinets, but left
            # these three *already booked* nested mass-only proxies hidden.
            # Add representations only as contained parts of their parents;
            # every ID is from the source ledger, with ZERO new mass.
            assert fid in ("i4_mission_table","i4_workbench","i4_cabinetry")
            extras=deepcopy(map_of["dry:i4_shared_map_table"]["extras"])
            extras.update(source_mass_owner_id=fid,
                mass=rows[fid]["mass_t"],material=rows[fid]["mat"],
                source_booking_repeated_nonadditive=True,node_mass_rebooking_t=0,
                nested_source_owner_no_new_mass=True,
                l1_part_kind="nested_original_source_mass_proxy")
            node=dict(name=name,mesh=mi,extras=extras)
            sub=next(n for n in doc["nodes"] if n.get("name")=="subsystem:HABITAT/L1")
            sub.setdefault("children",[]).append(len(doc["nodes"]))
            doc["nodes"].append(node);map_of[name]=node
        else:
            node=map_of[name];node["mesh"]=mi
        old_mass_kg=node["extras"]["mass"]*1000
        assert abs(old_mass_kg-rows[fid]["mass_t"]*1000)<1e-6
        node["extras"]["shape_refinement"]="PR516 within source booked AABB"
        fxtures.append(dict(owner=fid,booked_mass_kg=old_mass_kg,mesh=mi))
    # Re-read every source mesh in world glTF coordinate system. No actual
    # source stations moved and no hull/other deck/exterior node changes.
    assert all((tuple(map_of[name].get("translation",[])),
                tuple(map_of[name].get("rotation",[])))==t
                for name,t in original_positions.items())
    fixtures={}
    for n in doc["nodes"]:
        if "mesh" not in n:continue
        name=n.get("name","")
        if name.startswith("dry:i4_seat_") or name.startswith("dry:B3_"):continue
        fixtures[name]=trimeshes(doc,binary,n["mesh"])
    report_states={}
    anybad=[]
    for pose in ("halo_closed","wings_open_centre_back"):
        pieces={}
        for rid,inst in station_instances.items():
            b=inst["base"]
            p=[("common",world(inst["shapes"]["common"],b))]
            p.append(("controls",world(inst["shapes"]["controls"],b)))
            p.append(("centre",world(geo_centre,b,cp,
                  None if pose=="halo_closed" else quat_axis([0,1,0],70))))
            for side in (-1,1):
                turn=(None if pose=="halo_closed" else
                      quat_axis([1,0,0],80 if side<0 else -80))
                p.append(("wing_"+str(side),world(wgeos[side],b,wpiv[side],turn)))
            pieces[rid]=p
        # Analytical pressure vessel containment for all moving panel
        # vertices, not just screen centroids.
        pressure=rows["pressure_vessel"]["shape"]
        xa,xb,R,t=[pressure[k] for k in ("xa","xb","R","t")]
        inner_r=R-t;xa+=t
        gaps=[]
        for rid,models in pieces.items():
            for kind,segs in models:
                pts=np.concatenate([a for a,_ in segs])
                radii=np.linalg.norm(pts[:,[1,2]],axis=1)
                rad_gap=inner_r-radii
                xmin=xb-(xb-xa)*np.sqrt(np.clip(1-(radii/inner_r)**2,0,1))
                allgap=np.minimum(rad_gap,pts[:,0]-xmin)
                gaps.append(dict(station=rid,component=kind,min_shell_m=float(allgap.min())))
                if float(allgap.min())<-.00001:
                    anybad.append(pose+" "+rid+"/"+kind+" pressure shell margin "+str(float(allgap.min())))
        # FCL triangle collision with ALL fixtures and all other stations,
        # using correctly transformed B3 mesh components.
        # Internal co-located parts of ONE authored seat are attachment
        # contacts, not clashes with external objects.
        fixture_models={}
        for name,segs in fixtures.items():
            pts=np.concatenate([a for a,_ in segs])
            fmin=pts.min(axis=0);fmax=pts.max(axis=0)
            fixture_models[name]=(fcl_obj(segs),fmin,fmax)
        built={}
        for rid,models in pieces.items():
            for kind,segs in models:
                pts=np.concatenate([a for a,_ in segs])
                built[(rid,kind)]=(fcl_obj(segs),pts.min(axis=0),pts.max(axis=0))
        contacts=[]
        def intersects(a,b):
            x,x0,x1=a;y,y0,y1=b
            if np.any(x1<y0-1e-7) or np.any(y1<x0-1e-7):return False
            return fcl.collide(x,y,fcl.CollisionRequest(num_max_contacts=1),
                               fcl.CollisionResult())>0
        for (rid,kind),m in built.items():
            for fid,f in fixture_models.items():
                if intersects(m,f):contacts.append(dict(station=rid,component=kind,other=fid))
            for (oid,okind),other in built.items():
                if oid<=rid:continue
                if intersects(m,other):contacts.append(dict(station=rid,component=kind,other=oid+"/"+okind))
        if contacts:anybad.extend(pose+" "+str(c) for c in contacts)
        report_states[pose]=dict(D9_category_d=len(contacts),contacts=contacts,
           pressure_containment="PASS" if all(z["min_shell_m"]>=-1e-5 for z in gaps) else "FAIL",
           min_pressure_shell_clearance_m=round(min(z["min_shell_m"] for z in gaps),6),
           tested_component_nodes=len(built),source_fixture_nodes=len(fixtures))
    if anybad:
        DIAG.parent.mkdir(parents=True,exist_ok=True)
        failed_picture("D9 OR CONTAINMENT",anybad,seats)
        REPORT.write_text(json.dumps(dict(status="STOP_D9_OR_CONTAINMENT",
          pose_checks=report_states,failures=anybad,picture=DIAG.name),indent=2)+"\n")
        raise RuntimeError("STOP B3 D9/containment: see "+str(DIAG))
    if MASS_EST>ADDON_KG:
        failed_picture("HALO + CONTROLS MASS",["exceeds booked allocation"],seats)
        raise RuntimeError("STOP B3 mass")
    # Source booking invariants and PBR extras unchanged.
    assert all(x["extras"]["node_mass_rebooking_t"]==0 for x in doc["nodes"] if "mesh" in x)
    assert len([x for x in doc["nodes"] if x["name"].startswith("dry:i4_seat_")])==6
    assert len({x["mesh"] for x in doc["nodes"] if x["name"].startswith("dry:i4_seat_")})==1
    assert len(anim["channels"])==18
    assert not any(x["name"].startswith("dry:room_") and "mesh" in x for x in doc["nodes"])
    assert not any(x["name"].startswith("dry:outfit_") and "mesh" in x for x in doc["nodes"])
    # Original exact source booking fields for non-couch items unchanged.
    after_mass={x["name"]:(x["extras"]["mass"],x["extras"]["source_mass_owner_id"])
                for x in doc["nodes"] if "mesh" in x}
    assert all(after_mass[name]==(m,owner) for name,m,owner in old_mass)
    doc["asset"].setdefault("extras",{}).update(
      L1_station_design="B3_kT_approved",centre_lifts_back=True,
      wings_swing_aside=True,source_mass_rebooking_t=0,exterior_state_meshes_copied=0)
    glbhash=save(doc,binary,GLB)
    rpt=dict(status="L1_B3_SPLIT_HALO_D9_CONTAINMENT_PASS",
      source_geometry_sha256=SHA,glb_path="render/out/interior_L1.glb",
      glb_sha256=glbhash,source_PR517="#517 generator",keepers_PR516="#516",
      dry_t=DRY,ECON_dv_km_s=DV,source_mass_rebooking_t=0,
      station_locations_unchanged=True,S4_final_yz=[2.4,-1.7],
      budget_per_station_kg=dict(source_owner=SEAT_BOOKING_KG,common_couch=COMMON_KG,
        halo_plus_role_controls_allocation=ADDON_KG,estimated_total=MASS_EST,
        unspent_estimated_margin=ADDON_KG-MASS_EST,
        detailed_halo_controls_mass_estimates=BUDGET,
        mass_status="PASSES CONCEPTUAL ESTIMATE; NOT STRUCTURAL/MATERIAL CERTIFICATION"),
      gltf=dict(common_couch_mesh=cm,instanced_couches=6,
        animation_name=anim["name"],animation_channels=len(anim["channels"]),
        exterior_states_modified=0),
      pose_checks=report_states,
      fixture_source_booked_shapes=fxtures,
      checks=dict(D9="PASS category-d zero in both halo states",
        containment="PASS both states",G1_G12="NOT RUN / NOT REQUESTED"),
      outstanding=["4g hardpoint structural loads","suit/occupant fit",
        "mechanism actuation and cycling","optical screen readability and human reach"])
    REPORT.write_text(json.dumps(rpt,indent=2)+"\n")
    note=ROOT/"docs/L1_INTERIOR_PRINT_1_25_2026_11_12.md"
    contents=note.read_text()
    contents+="""
## kT-approved B3 halo and #516 refinements
- One 1.58 × 0.70m source couch mesh reused at six unchanged source positions. B3 split halo: centre display lifts backward and two wings swing to the sides. One L1 GLB has both poses as a glTF animation, NOT embedded in exterior states.
- Geometry: broad headrests, contoured ivory cushion, light blue-grey shell, 2 halo posts, hinge arms, restrained seat base, armrest control bodies, shaped table/bench/cabinet cases, 1.10 × 0.63m map table (44 × 25.2mm), 1.38 × 0.54m equipment bench (55.2 × 21.6mm), 0.54 × 0.35 × 0.70m cabinet (21.6 × 14 × 28mm). The screen faces are geometry, not screens that actually work.
- Decal / paint: screen contents, lettering, button markings, buckles, thin harness weave, hairline seams and indicator dots. Nothing under 0.6mm at 1:25 is independently printable; some B3 visual faces are under this threshold and must be flattened to decal in STL derivation.
- Role controls: Pilot attitude/translation; Captain backup flight/command-transfer; NAV trajectory/waypoint; Engineering power/thermal; Sensors/EW track-slew/modality; Mission Operations sequence/asset selection. Hardware from B3 #517, terminology from #516.
- Palette (already encoded in B3): #ACBBBD pale blue-grey shell, #D8D8CD ivory upholstery, #607A84 slate frame, muted teal and pale surround. Optional 10–20% brighter printed paint only.
- Mass: 46.000kg common couch and 5.185186564kg halo/control budget inside each 51.185186564kg existing i4_seat booking, no double-booked screen; conceptual 5.100kg halo/control estimate is NOT certified hardware mass. Ship mass/ECON unchanged.
- 4g: illustrative 100kg body imposes ~3.92kN acceleration load. Actual mount strength, occupant support, harness proof, suited egress, motion/mechanism loads remain OPEN.
"""
    note.write_text(contents)
    print(json.dumps(dict(status=rpt["status"],glb_sha256=glbhash,
      closed=report_states["halo_closed"],open=report_states["wings_open_centre_back"],
      estimated_halo_controls_kg=MASS_EST,booked_kg=ADDON_KG),indent=2))

if __name__=="__main__":main()
