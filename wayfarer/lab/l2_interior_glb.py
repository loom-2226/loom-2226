#!/usr/bin/env python3
"""Approved Wayfarer L2 furniture only. No exterior, L1, source mass, or G1-G12 changes."""
from pathlib import Path
import sys, json, math, struct, hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"l2_organic_study"))
import geom, raster

OUT=ROOT/"render"/"out"
SOURCE=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
GLB=OUT/"interior_L2.glb"
REPORT=OUT/"interior_L2_report.json"
SOURCE_SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
DRY=868.1922552640087
DV=707.845
EST={"room_L2-galley":345,"room_L2-wardroom":200,
     "room_L2-observation":95,"room_L2-exercise":410,
     "room_L2-hygiene":215,"outfit_L2":60}
CENTERS={"W3_stools":[64,77,90,103,116],
         "O1_loungers":[162,180,198]}

def rotate(V,angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    R=np.array([[1,0,0],[0,c,-s],[0,s,c]])
    return np.asarray(V)@R.T

def owner(item):
    if item.startswith("D") or item=="G0_wall_details":return "outfit_L2"
    return {"G":"room_L2-galley","W":"room_L2-wardroom",
            "O":"room_L2-observation","E":"room_L2-exercise",
            "H":"room_L2-hygiene"}[item[0]]

def split_repeat(parts,angles):
    # Preserve Claude's triangles. Partition by angular centre, never change coordinates.
    result={a:{} for a in angles}
    for mat,tris in parts.items():
        V=np.asarray(tris,dtype=float).reshape(-1,3,3)
        a=(np.degrees(np.arctan2(V[:,:,1].mean(1),-V[:,:,2].mean(1)))+360)%360
        delta=np.abs((a[:,None]-np.asarray(angles)[None,:]+180)%360-180)
        belonging=np.argmin(delta,axis=1)
        for i,at in enumerate(angles):
            result[at][mat]=V[belonging==i]
            assert len(result[at][mat])>0,(mat,at)
    # All copies are the same approved generator geometry, rigidly rotated.
    ref=angles[len(angles)//2]
    for at in angles:
        for mat,V in result[at].items():
            baseline=result[ref][mat]
            rotated=rotate(baseline,at-ref)
            assert rotated.shape==V.shape,(at,mat,rotated.shape,V.shape)
            if not np.allclose(rotated,V,atol=1e-5,rtol=0):
                raise RuntimeError("Repeat is not a rigid instance: %s at %s"%(mat,at))
    return ref,result

def inside_box_triangle(tri,lo,hi):
    # Six exact plane clips against the OPEN box. Surface penetration is a
    # conservative D9 screen; zero-thickness boundary contact is excluded.
    poly=[p for p in tri]
    for axis in range(3):
        for bound,side in ((lo[axis],1),(hi[axis],-1)):
            if not poly:return False
            old=poly;poly=[]
            for j,p in enumerate(old):
                q=old[(j+1)%len(old)]
                d1=(p[axis]-bound)*side; d2=(q[axis]-bound)*side
                if d1>=0:poly.append(p)
                if (d1>=0)!=(d2>=0):
                    poly.append(p+(q-p)*(d1/(d1-d2)))
    return bool(poly)

def srgb(hx):
    c=[int(hx[i:i+2],16)/255 for i in (1,3,5)]
    return [((x+.055)/1.055)**2.4 if x>.04045 else x/12.92 for x in c]+[1.]

class GLTF:
    def __init__(self):
        self.buf=bytearray();self.views=[];self.acc=[];self.meshes=[];self.nodes=[]
    def arr(self,v,target):
        while len(self.buf)%4:self.buf.append(0)
        o=len(self.buf);self.buf.extend(v.tobytes())
        self.views.append(dict(buffer=0,byteOffset=o,byteLength=v.nbytes,target=target))
        return len(self.views)-1
    def mesh(self,name,parts,mi):
        primitives=[]
        for m,t in parts.items():
            if len(t)==0:continue
            V=np.asarray(t,dtype=float).reshape(-1,3,3)
            _,N=raster.smooth_normals(V)
            P=V.reshape(-1,3).astype(np.float32)
            N=N.reshape(-1,3).astype(np.float32)
            key=np.round(np.c_[P*5000,N*100]).astype(np.int64)
            _,first,inv=np.unique(key,axis=0,return_index=True,return_inverse=True)
            Pu=P[first];Nu=N[first]/(np.linalg.norm(N[first],axis=1,keepdims=True)+1e-9)
            I=inv.astype(np.uint32)
            a=len(self.acc)
            self.acc.extend([
                dict(bufferView=self.arr(Pu,34962),componentType=5126,count=len(Pu),
                     type="VEC3",min=Pu.min(0).tolist(),max=Pu.max(0).tolist()),
                dict(bufferView=self.arr(Nu.astype(np.float32),34962),
                     componentType=5126,count=len(Nu),type="VEC3"),
                dict(bufferView=self.arr(I,34963),componentType=5125,count=len(I),type="SCALAR")
            ])
            primitives.append(dict(attributes=dict(POSITION=a,NORMAL=a+1),
                                   indices=a+2,material=mi[m]))
        assert primitives,name
        self.meshes.append(dict(name=name,primitives=primitives))
        return len(self.meshes)-1
    def finish(self,materials,source_sha):
        while len(self.buf)%4:self.buf.append(0)
        gl=dict(asset=dict(version="2.0",generator="LOOM approved L2 organic Japandi",
            extras=dict(source_geometry_sha256=source_sha,
                        exterior_state_meshes_copied=0,source_mass_rebooking_t=0)),
            scene=0,scenes=[dict(name="WAYFARER L2 independent interior",nodes=[0])],
            nodes=self.nodes,meshes=self.meshes,materials=materials,
            accessors=self.acc,bufferViews=self.views,
            buffers=[dict(byteLength=len(self.buf))])
        js=json.dumps(gl,separators=(",",":")).encode()
        js+=b" "*(-len(js)%4)
        return (struct.pack("<4sII",b"glTF",2,12+8+len(js)+8+len(self.buf))
                +struct.pack("<II",len(js),0x4E4F534A)+js
                +struct.pack("<II",len(self.buf),0x004E4942)+bytes(self.buf))

def main():
    source=SOURCE.read_bytes();sha=hashlib.sha256(source).hexdigest()
    assert sha==SOURCE_SHA,"STOP: source geometry changed"
    G=json.loads(source);I=json.loads(INPUT.read_text())
    assert abs(G["dry_t"]-DRY)<1e-8
    parts={p["id"]:p for p in G["parts"]}
    bookings={k:parts[k]["mass_t"] for k in EST}
    assert all(EST[k]<=1000*v+1e-6 for k,v in bookings.items()),"STOP: room booking exceeded"
    assert I["habitat"]["decks"][1]["id"]=="L2"
    geom.build()
    items={}
    for (it,mat),tris in geom.T.items():
        if it in ("ARCH","CTX") or not tris:continue
        items.setdefault(it,{})[mat]=np.asarray(tris,float).reshape(-1,3,3)
    assert len(items)==23,("approved 23 proposal nodes",list(items))
    all_v=np.concatenate([v.reshape(-1,3) for p in items.values() for v in p.values()])
    r=np.hypot(all_v[:,1],all_v[:,2])
    h=geom.X0-all_v[:,0]
    # D9 against source *physical* fixtures, NOT room semantic masses.
    floor=parts["floor_L2"]["shape"];floor1=parts["floor_L1"]["shape"]
    core=parts["core_racks"]["shape"]
    band=[p["shape"] for p in G["parts"] if p["id"].startswith("viewport_band_")]
    inner_r=parts["pressure_vessel"]["shape"]["R"]-parts["pressure_vessel"]["shape"]["t"]
    clearances=dict(floor_L2_m=float(np.min(h)),
        L1_floor_m=float(np.min(all_v[:,0])-floor1["x1"]),
        core_racks_m=float(np.min(r)-core["r1"]),
        viewport_band_m=float(min(p["r0"] for p in band)-np.max(r)),
        pressure_shell_m=float(inner_r-np.max(r)))
    violations=[k for k,v in clearances.items() if v < -1e-5]
    # Both hatch leaves: triangle/solid intersection, not AABB-only "clashes".
    hatch_hits=[]
    all_tri=np.concatenate([v.reshape(-1,3,3) for p in items.values() for v in p.values()])
    for name in ("hatch_L1L2_0","hatch_L1L2_1"):
        box=parts[name]["shape"]
        eps=1e-5
        lo=np.array([box["x0"],box["z0"],-box["y1"]])+eps
        hi=np.array([box["x1"],box["z1"],-box["y0"]])-eps
        cand=np.where(np.all(all_tri.max(axis=1)>lo,axis=1)&
                      np.all(all_tri.min(axis=1)<hi,axis=1))[0]
        if any(inside_box_triangle(all_tri[j],lo,hi) for j in cand):
            hatch_hits.append(name)
    d9=len(violations)+len(hatch_hits)
    containment=(clearances["pressure_shell_m"]>=-1e-5 and
                 clearances["floor_L2_m"]>=-1e-5 and
                 clearances["L1_floor_m"]>=-1e-5)
    result=dict(status="L2_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS" if d9==0 and containment else "STOP_L2_D9_OR_CONTAINMENT",
        source_geometry_sha256=sha,glb_path="render/out/interior_L2.glb",
        dry_t=DRY,ECON_dv_km_s=DV,source_mass_rebooking_t=0,
        booking_kg={k:1000*v for k,v in bookings.items()},
        estimated_items_kg=EST,estimated_total_kg=sum(EST.values()),
        source_proposal_mesh_groups=len(items),instances={"stools":5,"loungers":3},
        checks=dict(D9_category_d=d9,D9_scope="floor_L2, L1 floor, L1L2 hatch leaves, core racks, viewport band",
            source_clearances_m={k:round(v,6) for k,v in clearances.items()},
            source_hatch_leaf_hits=hatch_hits,source_violations=violations,
            containment="PASS" if containment else "FAIL",
            G1_G12="NOT RUN / NOT REQUIRED"),exterior_six_state_changes=0,
        palette="SOURCE L2_ORGANIC_STUDY pass 2",smooth_normals=True)
    OUT.mkdir(parents=True,exist_ok=True)
    if d9 or not containment:
        REPORT.write_text(json.dumps(result,indent=2)+"\n")
        raise RuntimeError(result["status"]+": "+str(result["checks"]))
    # Export unchanged source shapes, but share meshes for the two repeated sets.
    gl=GLTF()
    gl.nodes.append(dict(name="LOOM_WAYFARER_L2_INTERIOR",children=[],
        extras=dict(source_geometry_sha256=sha,mass_neutral=True,
                    exterior_six_state_untouched=True)))
    gl.nodes.append(dict(name="system:HABITAT",children=[]))
    gl.nodes[0]["children"].append(1)
    systems={}
    materials=[]
    mats=sorted({m for p in items.values() for m in p})
    for m in mats:
        col,em=geom.MAT[m]
        materials.append(dict(name="CANON_FINISH/L2/"+m,doubleSided=True,
            pbrMetallicRoughness=dict(baseColorFactor=srgb(col),
              metallicFactor=.6 if m=="titanium" else 0.,
              roughnessFactor=.35 if m in ("titanium","glass") else .7),
            **(dict(emissiveFactor=srgb(col)[:3]) if em else {})))
    mi={m:i for i,m in enumerate(mats)}
    def addnode(item,name,mesh,pose=None,extra=None):
        own=owner(item)
        sub=own.removeprefix("room_L2-") if own!="outfit_L2" else "common_services"
        if sub not in systems:
            idx=len(gl.nodes);gl.nodes.append(dict(name="subsystem:HABITAT/L2_"+sub,children=[]))
            systems[sub]=idx;gl.nodes[1]["children"].append(idx)
        e=dict(zone="FORE",deck="L2",material="L2 organic Japandi mixed",
            print_group="HABITAT/L2_"+sub,mass=bookings[own],mass_unit="t",
            mass_basis="source_booking_reference_nonadditive",source_mass_owner_id=own,
            semantic_system="HABITAT",semantic_subsystem="L2_"+sub,
            node_mass_rebooking_t=0,source_booking_repeated_nonadditive=True,
            l2_part_kind="approved_furniture_or_outfit",source_geometry_sha256=sha,
            approved_proposal_node="proposal:L2_"+item)
        if extra:e.update(extra)
        n=dict(name=name,mesh=mesh,extras=e)
        if pose:n.update(pose)
        idx=len(gl.nodes);gl.nodes.append(n);gl.nodes[systems[sub]]["children"].append(idx)
    for it in sorted(items):
        if it in CENTERS:
            centers=CENTERS[it];ref,split=split_repeat(items[it],centers)
            local={m:rotate(v,-ref) for m,v in split[ref].items()}
            mesh=gl.mesh(it+"_SHARED",local,mi)
            for k,a in enumerate(centers,1):
                rad=math.radians(a)
                addnode(it,"dry:L2_"+it.removesuffix("s")+"_"+str(k),mesh,
                    dict(rotation=[math.sin(rad/2),0,0,math.cos(rad/2)]),
                    dict(shared_mesh_instanced=True,repeat_angle_deg=a,repeat_count=len(centers)))
        else:
            mesh=gl.mesh(it,items[it],mi)
            addnode(it,"dry:L2_"+it,mesh)
    data=gl.finish(materials,sha);GLB.write_bytes(data)
    result.update(glb_sha256=hashlib.sha256(data).hexdigest(),
        glb_bytes=len(data),mesh_nodes=sum("mesh" in n for n in gl.nodes),
        unique_meshes=len(gl.meshes),repeated_mesh_indices={
            it:next(n["mesh"] for n in gl.nodes if n["name"].startswith("dry:L2_"+it.removesuffix("s")+"_"))
            for it in CENTERS})
    REPORT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
