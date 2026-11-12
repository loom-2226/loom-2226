"""D9 screen kT's flipped L2/L3 hatch leaves against actual committed L2 GLB."""
import hashlib
import json
import math
import struct
from pathlib import Path
import numpy as np

EXPECTED_SHA="50028743262fddc747236f3d5efedbfcd9dc0a84c7a802f93ab01de5491ebeba"

def clipped_inside(tri,lo,hi):
    """Positive area triangle clipping within six OPEN planes of leaf box."""
    poly=list(tri)
    for axis in range(3):
        for bound,sign in ((lo[axis],1),(hi[axis],-1)):
            if not poly:
                return False
            old=poly;poly=[]
            for j,p in enumerate(old):
                q=old[(j+1)%len(old)]
                dp=(p[axis]-bound)*sign
                dq=(q[axis]-bound)*sign
                if dp>=0:
                    poly.append(p)
                if (dp>=0)!=(dq>=0):
                    poly.append(p+(q-p)*(dp/(dp-dq)))
    if len(poly)<3:
        return False
    return any(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0]))>1e-11
               for i in range(1,len(poly)-1))

def screen(glb_path,flipped):
    """All 29 instanced GLB mesh nodes, with glTF transforms applied.

    Source convention: ship (x,y,z) maps to glTF (x,z,-y).
    Distance bounds: mesh triangle AABB is a LOWER bound on clearance,
    vertex-to-box closest point is an UPPER bound. No fabricated exact gap.
    """
    raw=Path(glb_path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==EXPECTED_SHA,"STOP: L2 furniture GLB changed"
    n,typ=struct.unpack_from("<II",raw,12)
    assert typ==0x4e4f534a
    doc=json.loads(raw[20:20+n])
    binlen,bintype=struct.unpack_from("<II",raw,20+n)
    assert bintype==0x004e4942
    buf=raw[20+n+8:20+n+8+binlen]
    nodes=[v for v in doc["nodes"] if "mesh" in v]
    assert len(nodes)==29,("unexpected L2 GLB instances",len(nodes))
    assert all(not any(k in node for k in ("translation","rotation","scale","matrix"))
               for node in doc["nodes"] if "mesh" not in node),"STOP: unhandled L2 hierarchy transform"
    def accessor(index):
        a=doc["accessors"][index]
        view=doc["bufferViews"][a["bufferView"]]
        t={5126:"<f4",5125:"<u4",5123:"<u2"}[a["componentType"]]
        dtype=np.dtype(t)
        factor=3 if a["type"]=="VEC3" else 1
        assert "byteStride" not in view
        ofs=view.get("byteOffset",0)+a.get("byteOffset",0)
        v=np.frombuffer(buf,dtype=dtype,count=a["count"]*factor,offset=ofs)
        return v.reshape((-1,3)) if factor==3 else v
    boxes={}
    for name,item in flipped.items():
        sh=item["shape"]
        boxes[name]=(np.array([sh["x0"],sh["z0"],-sh["y1"]])+1e-5,
                     np.array([sh["x1"],sh["z1"],-sh["y0"]])-1e-5)
    hits=[]
    distances=[]
    total=0
    for node in nodes:
        q=node.get("rotation",[0.,0.,0.,1.])
        assert abs(q[1])+abs(q[2])<1e-7,"STOP L2 mesh rotation not around ship X"
        th=2*math.atan2(q[0],q[3])
        c,si=math.cos(th),math.sin(th)
        move=np.array(node.get("translation",[0.,0.,0.]))
        for prim in doc["meshes"][node["mesh"]]["primitives"]:
            vertices=accessor(prim["attributes"]["POSITION"]).astype(np.float64)
            if th:
                v=vertices.copy()
                vertices[:,1]=c*v[:,1]-si*v[:,2]
                vertices[:,2]=si*v[:,1]+c*v[:,2]
            vertices+=move
            faces=accessor(prim["indices"]).reshape((-1,3))
            triangles=vertices[faces]
            total+=len(triangles)
            mi=triangles.min(axis=1)
            ma=triangles.max(axis=1)
            for name,(lo,hi) in boxes.items():
                sep=np.maximum(np.maximum(lo-ma,mi-hi),0)
                lower=float(np.min(np.linalg.norm(sep,axis=1)))
                vd=np.maximum(np.maximum(lo-vertices,vertices-hi),0)
                upper=float(np.min(np.linalg.norm(vd,axis=1)))
                distances.append(dict(hatch=name,mesh=node["name"],
                                      triangle_AABB_lower_bound_m=round(lower,6),
                                      vertex_upper_bound_m=round(upper,6)))
                ids=np.where(np.all(ma>lo,axis=1)&np.all(mi<hi,axis=1))[0]
                for idx in ids:
                    if clipped_inside(triangles[idx],lo,hi):
                        hits.append(dict(hatch=name,mesh=node["name"],
                                         triangle=int(idx),category="d"))
                        break
    distances.sort(key=lambda r:(r["triangle_AABB_lower_bound_m"],r["vertex_upper_bound_m"]))
    return dict(glb_sha256=digest,mesh_nodes=len(nodes),triangle_count=total,
                D9_hatch_mesh_hits=hits,
                closest_mesh_candidates=distances[:12],
                G2_water_run=[x for x in distances if "G2_water_run" in x["mesh"]],
                clearance_lower_bound_m=min(x["triangle_AABB_lower_bound_m"] for x in distances))
