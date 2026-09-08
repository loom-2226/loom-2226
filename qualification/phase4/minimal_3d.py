from __future__ import annotations
import json, math, hashlib, sqlite3
from pathlib import Path
from typing import Dict, Tuple, List

Vector3=Tuple[float,float,float]
Quat=Tuple[float,float,float,float]

class Minimal3DError(ValueError): pass

def _qnorm(q:Quat)->Quat:
    n=math.sqrt(sum(v*v for v in q))
    if not math.isfinite(n) or n<=0: raise Minimal3DError("invalid quaternion")
    return tuple(v/n for v in q)

def _qmul(a:Quat,b:Quat)->Quat:
    aw,ax,ay,az=a; bw,bx,by,bz=b
    return (aw*bw-ax*bx-ay*by-az*bz,
            aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx,
            aw*bz+ax*by-ay*bx+az*bw)

def _qconj(q): return (q[0],-q[1],-q[2],-q[3])

def rotate(q:Quat,v:Vector3)->Vector3:
    q=_qnorm(q); p=(0.0,*v); r=_qmul(_qmul(q,p),_qconj(q))
    return (r[1],r[2],r[3])

def compose(pt:Vector3,pq:Quat,lt:Vector3,lq:Quat):
    r=rotate(pq,lt)
    return tuple(pt[i]+r[i] for i in range(3)), _qnorm(_qmul(_qnorm(pq),_qnorm(lq)))

def resolve_component_poses(conn:sqlite3.Connection):
    conn.row_factory=sqlite3.Row
    parents={r["component_id"]:r["parent_component_id"] for r in conn.execute(
        "SELECT component_id,parent_component_id FROM physical_component")}
    tf={}
    for r in conn.execute("SELECT component_id,tx_m,ty_m,tz_m,qw,qx,qy,qz FROM component_transform"):
        tf[r["component_id"]]=((float(r["tx_m"]),float(r["ty_m"]),float(r["tz_m"])),
                               (float(r["qw"]),float(r["qx"]),float(r["qy"]),float(r["qz"])))
    out={}; visiting=set()
    def one(cid):
        if cid in out: return out[cid]
        if cid in visiting: raise Minimal3DError(f"transform cycle: {cid}")
        if cid not in tf: raise Minimal3DError(f"missing transform: {cid}")
        visiting.add(cid); lt,lq=tf[cid]; parent=parents[cid]
        pose=(lt,_qnorm(lq)) if parent is None else compose(*one(parent),lt,lq)
        visiting.remove(cid); out[cid]=pose; return pose
    for cid in sorted(parents): one(cid)
    return out

def _active_components(conn, instance_state=None):
    conn.row_factory=sqlite3.Row
    state=dict(instance_state or {})
    domains={}
    for r in conn.execute("SELECT configuration_domain_id,initial_state FROM configuration_domain"):
        domains[r["configuration_domain_id"]]=state.get(r["configuration_domain_id"],r["initial_state"])
    valid={(r["configuration_domain_id"],r["state_code"]) for r in conn.execute(
        "SELECT configuration_domain_id,state_code FROM configuration_state")}
    for d,s in domains.items():
        if (d,s) not in valid: raise Minimal3DError(f"illegal state {d}={s}")
    active={r[0]:True for r in conn.execute("SELECT component_id FROM physical_component")}
    for r in conn.execute("SELECT component_id,configuration_domain_id,state_code,active FROM component_state_rule"):
        if domains.get(r[1])==r[2]: active[r[0]]=bool(r[3])
    return active,domains

def build_scene(conn:sqlite3.Connection, instance_state=None):
    conn.row_factory=sqlite3.Row
    poses=resolve_component_poses(conn); active,domains=_active_components(conn,instance_state)
    prims=[]
    for r in conn.execute("""SELECT g.primitive_id,g.component_id,g.primitive_type,g.dimensions_json,
                             g.local_pose_json,g.physical_roles_json,g.authority_status,g.provenance_id,
                             p.source_path,p.source_version
                             FROM geometry_primitive g
                             JOIN provenance_source p ON p.provenance_id=g.provenance_id
                             ORDER BY g.primitive_id"""):
        if not active.get(r["component_id"],False): continue
        lp=json.loads(r["local_pose_json"] or "{}")
        lt=tuple(float(v) for v in lp.get("translation_m",[0,0,0]))
        lq=tuple(float(v) for v in lp.get("quaternion_wxyz",[1,0,0,0]))
        t,q=compose(*poses[r["component_id"]],lt,lq)
        prims.append({
            "primitive_id":r["primitive_id"], "component_id":r["component_id"],
            "primitive_type":r["primitive_type"], "dimensions":json.loads(r["dimensions_json"]),
            "pose_B":{"translation_m":list(t),"quaternion_wxyz":list(q)},
            "physical_roles":json.loads(r["physical_roles_json"]),
            "authority_status":r["authority_status"],
            "provenance":{"id":r["provenance_id"],"source_path":r["source_path"],"source_version":r["source_version"]},
        })
    return {"schema":"loom.phase4.minimal3d.v0.1","configuration":domains,"primitives":prims}

def _transform_point(pose, p):
    t=tuple(pose["translation_m"]); q=tuple(pose["quaternion_wxyz"])
    r=rotate(q,p); return tuple(t[i]+r[i] for i in range(3))

def _box_mesh(d):
    x,y,z=float(d["x_m"])/2,float(d["y_m"])/2,float(d["z_m"])/2
    v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    f=[(1,2,4,3),(5,7,8,6),(1,5,6,2),(3,4,8,7),(1,3,7,5),(2,6,8,4)]
    return v,f

def _cyl_mesh(d,segments=12):
    L=float(d["length_m"]); D=float(d["diameter_m"]); r=D/2
    v=[]
    for x in (-L/2,L/2):
        for i in range(segments):
            a=2*math.pi*i/segments; v.append((x,r*math.cos(a),r*math.sin(a)))
    f=[]
    for i in range(segments):
        j=(i+1)%segments
        f.append((i+1,j+1,segments+j+1,segments+i+1))
    f.append(tuple(range(1,segments+1)))
    f.append(tuple(range(segments+1,2*segments+1)))
    return v,f

def scene_to_obj(scene)->str:
    lines=["# LOOM Phase 4 deterministic minimal 3D","o Wayfarer"]
    offset=0
    for p in scene["primitives"]:
        roles=set(p["physical_roles"])
        if "RENDER" not in roles: continue
        typ=p["primitive_type"]; d=p["dimensions"]
        if typ=="BOX": verts,faces=_box_mesh(d)
        elif typ=="CYLINDER_X": verts,faces=_cyl_mesh(d)
        else: continue
        lines.append(f"g {p['primitive_id']}")
        for v in verts:
            w=_transform_point(p["pose_B"],v); lines.append("v %.9f %.9f %.9f"%w)
        for face in faces:
            lines.append("f "+" ".join(str(offset+i) for i in face))
        offset+=len(verts)
    return "\n".join(lines)+"\n"

def scene_bounds(scene):
    pts=[]
    for p in scene["primitives"]:
        if "RENDER" not in set(p["physical_roles"]): continue
        d=p["dimensions"]; typ=p["primitive_type"]
        if typ=="BOX": verts,_=_box_mesh(d)
        elif typ=="CYLINDER_X": verts,_=_cyl_mesh(d)
        else: continue
        pts.extend(_transform_point(p["pose_B"],v) for v in verts)
    if not pts: raise Minimal3DError("scene has no rendered geometry")
    return {"min_m":[min(p[i] for p in pts) for i in range(3)],
            "max_m":[max(p[i] for p in pts) for i in range(3)]}

def write_outputs(conn, output_dir:Path, instance_state=None):
    scene=build_scene(conn,instance_state); scene["bounds"]=scene_bounds(scene)
    output_dir.mkdir(parents=True,exist_ok=True)
    js=(json.dumps(scene,sort_keys=True,indent=2)+"\n").encode()
    obj=scene_to_obj(scene).encode()
    (output_dir/"wayfarer_minimal3d.json").write_bytes(js)
    (output_dir/"wayfarer_minimal3d.obj").write_bytes(obj)
    return {"scene_sha256":hashlib.sha256(js).hexdigest(),
            "obj_sha256":hashlib.sha256(obj).hexdigest(),"scene":scene}
