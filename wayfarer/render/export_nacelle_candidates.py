#!/usr/bin/env python3
"""Non-canon whole-ship candidate GLBs. Existing released GLB bytes are read-only.

The 20 appended meshes per state come from EXACT source BReps, including
the ring-lock receiver cut (not a display-only cylinder). Base references
remain the released torch and Metric GLBs. No canon_glb pointer writes.
"""
import hashlib,json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab/metric_nodes"))
from nacelle_source_brep import make
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
G=json.loads(GEO.read_text())
GEOSHA=hashlib.sha256(GEO.read_bytes()).hexdigest()
BASE=ROOT/"render/out"
OUT=ROOT/"render/candidates"
OUT.mkdir(exist_ok=True)
METALS={
 "metric_nacelle":([.66,.71,.78,1],.53,.45),
 "metric_link":([.87,.64,.32,1],.56,.38),
 "metric_arm":([.22,.65,.73,1],.59,.33),
}
def read_glb(p):
 data=p.read_bytes()
 magic,version,length=struct.unpack_from("<III",data,0)
 assert magic==0x46546c67 and version==2 and length==len(data)
 jl,jt=struct.unpack_from("<II",data,12)
 assert jt==0x4e4f534a
 doc=json.loads(data[20:20+jl])
 at=20+jl
 bl,bt=struct.unpack_from("<II",data,at)
 assert bt==0x004e4942
 return doc,bytearray(data[at+8:at+8+bl])
def add_buffer(buf,views,values,target):
 while len(buf)%4:buf.append(0)
 b=values.tobytes()
 start=len(buf)
 buf.extend(b)
 idx=len(views)
 views.append(dict(buffer=0,byteOffset=start,byteLength=len(b),target=target))
 return idx
def append_mesh(doc,buf,name,solid,mat):
 verts,tri=solid.tessellate(.045,.12)
 p=np.asarray([[v.X,v.Y,v.Z] for v in verts],dtype=np.float32)
 faces=np.asarray(tri,dtype=np.uint32)
 assert len(p)>8 and len(faces)>4
 n=np.zeros(p.shape,dtype=np.float64)
 a=p[faces[:,1]]-p[faces[:,0]]
 b=p[faces[:,2]]-p[faces[:,0]]
 fn=np.cross(a,b)
 for j in range(3):
     np.add.at(n,faces[:,j],fn)
 sz=np.linalg.norm(n,axis=1)
 n=np.divide(n,np.maximum(sz[:,None],1e-15)).astype(np.float32)
 pv=add_buffer(buf,doc["bufferViews"],p,34962)
 nv=add_buffer(buf,doc["bufferViews"],n,34962)
 iv=add_buffer(buf,doc["bufferViews"],faces.reshape(-1),34963)
 a0=len(doc["accessors"])
 doc["accessors"].extend([
  dict(bufferView=pv,componentType=5126,count=len(p),type="VEC3",
       min=p.min(axis=0).tolist(),max=p.max(axis=0).tolist()),
  dict(bufferView=nv,componentType=5126,count=len(n),type="VEC3"),
  dict(bufferView=iv,componentType=5125,count=faces.size,type="SCALAR")])
 m=len(doc["meshes"])
 doc["meshes"].append(dict(name=name,primitives=[
  dict(attributes=dict(POSITION=a0,NORMAL=a0+1),indices=a0+2,material=mat)]))
 return m,len(p),len(faces)
def write_glb(path,doc,bin_data):
 def pad(b,fill):return b+bytes([fill])*((-len(b))%4)
 doc["buffers"][0]["byteLength"]=len(bin_data)
 j=pad(json.dumps(doc,separators=(",",":")).encode(),0x20)
 b=pad(bytes(bin_data),0)
 hdr=struct.pack("<III",0x46546c67,2,28+len(j)+len(b))
 path.write_bytes(hdr+struct.pack("<II",len(j),0x4e4f534a)+j+
                  struct.pack("<II",len(b),0x004e4942)+b)
for state,old in [
 ("torch","wayfarer_exterior_detail_88ce19fc_torch_closed.glb"),
 ("Metric","wayfarer_exterior_detail_88ce19fc_metric_hard_closed.glb")
]:
 base=BASE/old
 old_bytes=base.read_bytes()
 oldhash=hashlib.sha256(old_bytes).hexdigest()
 doc,buf=read_glb(base)
 assert doc["scene"]==0 and len(doc["scenes"])==1
 assert doc["scenes"][0]["nodes"]==[0]
 # Parent of original exterior assemblies rotates source (x,y,z) into GL.
 # Append all new source-coordinate meshes under that same parent.
 matids={}
 for k,(rgba,metal,rough) in METALS.items():
  matids[k]=len(doc["materials"])
  doc["materials"].append(dict(name="CANDIDATE_"+k,doubleSided=True,
    pbrMetallicRoughness=dict(baseColorFactor=rgba,metallicFactor=metal,roughnessFactor=rough)))
 count=0
 meshes={}
 for row in G["metric_states"][state]["parts"]:
  id=row["id"]
  kind=next(k for k in METALS if id.startswith(k))
  shape=make(row["shape"])
  assert shape.is_valid and shape.volume>0,id
  mesh,nv,ntri=append_mesh(doc,buf,"candidate:dry:"+id,shape,matids[kind])
  mass=next(p["mass_t"] for p in G["parts"] if p["id"]==id)
  node=len(doc["nodes"])
  doc["nodes"].append(dict(mesh=mesh,name="candidate:dry:"+id,
    extras=dict(node_id="candidate:dry:"+id,semantic_system="METRIC",semantic_subsystem=kind,
                source_allocation_id=id,source_allocation_total_t=mass,
                source_allocation_reused_by_multiple_geometry_nodes=False,
                node_mass_rebooking_t=0,epistemic_status="kT approved installed source CANDIDATE; D9 qualification separate",
                candidate_state=state,source_geometry_sha256=GEOSHA)))
  doc["nodes"][0]["children"].append(node)
  meshes[id]=dict(vertices=nv,triangles=ntri)
  count+=1
 doc.setdefault("extras",{}).update(candidate=True,noncanon=True,
    source_geometry_sha256=GEOSHA,original_released_GLBSHA256=oldhash,
    candidate_state=state,source_dry_t=G["dry_t"],delta_v_ECON_km_s=707.845,
    D9_status="PENDING; do not claim qualification from visualization",
    source_parts_added=count,swing_envelope="OPEN; not D9 qualified")
 assert count==20
 dest=OUT/f"wayfarer_nacelle_{state}_{GEOSHA[:8]}.glb"
 write_glb(dest,doc,buf)
 print("CANDIDATE_GLB",state,dest,dest.stat().st_size,
       hashlib.sha256(dest.read_bytes()).hexdigest(),"NEW",meshes,flush=True)
 assert hashlib.sha256(base.read_bytes()).hexdigest()==oldhash, "RELEASED GLB CHANGED"
