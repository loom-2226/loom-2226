#!/usr/bin/env python3
"""kT-approved exact seven-unit PR520 wallfit into independent L1 GLB, D9 and containment only."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, math, struct, subprocess, sys
import numpy as np
import fcl
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"))
import l1_b3_integrate as B
GEN=ROOT/"lab/l1_wallfit_generator.py"
PROPOSAL=ROOT/"render/out/proposal_L1_wallfit.glb"
GLB=ROOT/"render/out/interior_L1.glb"
RPT=ROOT/"render/out/interior_L1_report.json"
STOP=ROOT/"render/out/interior_L1_wallfit_STOP_report.json"
PICTURE=ROOT/"render/out/interior_L1_wallfit_D9_STOP.svg"
PRINT=ROOT/"docs/L1_INTERIOR_PRINT_1_25_2026_11_12.md"
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
UNITS=["u1_spares_tools","u2_watch_galley","u3_courier_strongbox","u4_emergency_left",
       "u5_backup_panel","u6_emergency_right","u7_wall_lining"]
KG=[96,52,60,40,30,40,40]
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
def localmatrix(node,override=None):
    if "matrix" in node:
        assert override is None
        return np.array(node["matrix"],dtype=float).reshape(4,4).T
    x,y,z,w=np.array(override if override is not None else node.get("rotation",[0,0,0,1]),dtype=float)
    m=np.eye(4)
    m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
              [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
              [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
    if "scale" in node:m[:3,:3]@=np.diag(node["scale"])
    m[:3,3]=node.get("translation",[0,0,0])
    return m
def rendered(doc,buf,opened):
    overrides={}
    if opened:
        anim=doc["animations"][0]
        assert len(anim["channels"])==18
        for channel in anim["channels"]:
            sampler=anim["samplers"][channel["sampler"]]
            overrides[channel["target"]["node"]]=B.read_accessor(doc,buf,sampler["output"])[-1]
    rendered={}
    def visit(i,parent):
        n=doc["nodes"][i];m=parent@localmatrix(n,overrides.get(i))
        if "mesh" in n:
            rendered[n["name"]]=[(xyz@m[:3,:3].T+m[:3,3],faces)
                for xyz,faces in B.trimeshes(doc,buf,n["mesh"])]
        for child in n.get("children",[]):visit(child,m)
    for root in doc["scenes"][doc.get("scene",0)]["nodes"]:visit(root,np.eye(4))
    return rendered
def overlap(a,b):
    x=np.concatenate([p for p,_ in a]);y=np.concatenate([p for p,_ in b])
    if np.any(np.minimum(x.max(0),y.max(0))-np.maximum(x.min(0),y.min(0))<=1e-6):
        return False
    return fcl.collide(B.fcl_obj(a),B.fcl_obj(b),fcl.CollisionRequest(num_max_contacts=1),
        fcl.CollisionResult())>0
def exact_shared_242_sector(a_name,a_parts,b_name,b_parts):
    # U3 [234,242] and U4 [242,250] share ONLY the 242-degree radial
    # end face. FCL detects the two touching sheets; D9 category-d
    # requires a positive-volume intersection. A wedge narrower than
    # 180 deg is convex, so all triangles whose vertices stay in its
    # respective angular interval stay on its side of the boundary.
    ends={"dry:L1_wallfit_u3_courier_strongbox":(234.,242.),
          "dry:L1_wallfit_u4_emergency_left":(242.,250.)}
    if {a_name,b_name}!=set(ends):return False
    for name,parts in ((a_name,a_parts),(b_name,b_parts)):
        vertices=np.concatenate([p for p,_ in parts])
        angles=np.degrees(np.arctan2(vertices[:,1],vertices[:,2]))%360
        lo,hi=ends[name]
        if angles.min()<lo-1e-5 or angles.max()>hi+1e-5:
            return False
    return True
def shellmargin(points,sh):
    r=np.linalg.norm(points[:,1:3],axis=1)
    R=sh["R"]-sh["t"];xa=sh["xa"]+sh["t"];xb=sh["xb"]
    xmin=xb-(xb-xa)*np.sqrt(np.maximum(0,1-np.minimum(r/R,1)**2))
    return np.minimum(R-r,points[:,0]-xmin)
def picture(fails):
    cx,cy=400,440
    def xy(r,a):
        t=math.radians(a);return cx-77*r*math.cos(t),cy-77*r*math.sin(t)
    arcs=[(27,66),(113,126),(234,242),(242,250),(295,305),(354,370)]
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="910" viewBox="0 0 1200 910">',
           '<rect width="1200" height="910" fill="white"/>',
           '<text x="25" y="41" font-family="Arial" font-size="23">L1 WALLFIT STOP / REAL D9 OR CONTAINMENT</text>',
           '<circle cx="400" cy="440" r="326" fill="none" stroke="#657788" stroke-width="3"/>']
    for i,(a,b) in enumerate(arcs):
        ps=[xy(3.755,a),xy(4,a),xy(4,b),xy(3.755,b)]
        lines.append('<polygon points="'+ " ".join("%.1f,%.1f"%p for p in ps) +
                     '" fill="#edb799" stroke="#bd4d43" stroke-width="2"/>')
        tx,ty=xy(3.45,(a+b)/2)
        lines.append('<text x="%.1f" y="%.1f" font-family="Arial" font-size="16">U%d</text>'%(tx,ty,i+1))
    lines.append('<text x="25" y="810" font-family="Arial" font-size="14">U7 occupies the arcs between low cabinets</text>')
    for i,msg in enumerate(fails[:4]):
        lines.append('<text x="25" y="%d" font-family="Arial" font-size="12">%s</text>'%
                     (832+18*i,str(msg).replace("&","&amp;").replace("<","&lt;")[:165]))
    PICTURE.write_text("\n".join(lines))
def main():
    assert hashlib.sha256(GEO.read_bytes()).hexdigest()==SHA
    g=json.loads(GEO.read_text())
    rows={v["id"]:v for v in g["parts"]}
    dec=json.loads(DEC.read_text())["l1_wallfit_2026_11_12"]
    assert dec["authority"].startswith("kT APPROVED Claude PR #520")
    outfit=rows["outfit_L1"]["mass_t"]
    room=rows["room_L1-command"]["mass_t"]
    assert abs(outfit-.8189629850273704)<1e-10 and abs(room-2.1497778356968475)<1e-10
    assert sum(KG)==358 and sum(KG)*.001<outfit
    assert abs(g["dry_t"]-868.1922552640087)<1e-8
    prior=json.loads(RPT.read_text())
    assert prior["status"]=="L1_B3_SPLIT_HALO_D9_CONTAINMENT_PASS"
    assert prior["dry_t"]==868.1922552640087 and prior["ECON_dv_km_s"]==707.845
    doc,binary=B.load_glb(GLB)
    assert hashlib.sha256(GLB.read_bytes()).hexdigest()==prior["glb_sha256"]
    original_nodes=deepcopy(doc["nodes"]);original_anim=deepcopy(doc["animations"])
    original_scene=deepcopy(doc["scenes"]);original_meshes=len(doc["meshes"])
    subprocess.run([sys.executable,str(GEN)],check=True,cwd=ROOT.parent)
    source,sbin=B.load_glb(PROPOSAL)
    nodes=[n for n in source["nodes"] if n["name"].startswith("proposal:u")]
    assert len(nodes)==7 and [n["name"] for n in nodes]==["proposal:"+n for n in UNITS]
    matmap={}
    for i,mat in enumerate(source["materials"]):
        mat=deepcopy(mat);mat["name"]=mat["name"].replace("PROPOSAL/L1_wall/","CANON_FINISH/L1/wallfit/")
        matmap[i]=len(doc["materials"]);doc["materials"].append(mat)
    subsystem=next(i for i,n in enumerate(doc["nodes"]) if n.get("name")=="subsystem:HABITAT/L1")
    original_outfit=next(n for n in doc["nodes"] if n["name"]=="dry:outfit_L1")
    assert "mesh" not in original_outfit
    new=[]
    for unit,kg,node in zip(UNITS,KG,nodes):
        srcmesh=source["meshes"][node["mesh"]]
        prims=[]
        for p in srcmesh["primitives"]:
            xyz=B.read_accessor(source,sbin,p["attributes"]["POSITION"]).astype("<f4")
            normals=B.read_accessor(source,sbin,p["attributes"]["NORMAL"]).astype("<f4")
            idx=(B.read_accessor(source,sbin,p["indices"]).ravel().astype("<u4")
                 if "indices" in p else np.arange(len(xyz),dtype="<u4"))
            assert len(idx)%3==0 and len(normals)==len(xyz)
            ia=B.accessor(doc,binary,xyz,5126,"VEC3",34962)
            ib=B.accessor(doc,binary,normals,5126,"VEC3",34962)
            ic=B.accessor(doc,binary,idx,5125,"SCALAR",34963)
            prims.append(dict(attributes=dict(POSITION=ia,NORMAL=ib),
                              indices=ic,material=matmap[p["material"]]))
        mi=len(doc["meshes"]);doc["meshes"].append(dict(name="wallfit_"+unit,primitives=prims))
        e=deepcopy(original_outfit["extras"])
        e.update(zone="FORE",deck="L1",material="outfit",mass=outfit,mass_unit="t",
            mass_basis="source_booking_reference_nonadditive",source_mass_owner_id="outfit_L1",
            semantic_system="HABITAT",semantic_subsystem="L1",print_group="HABITAT/L1",
            source_booking_repeated_nonadditive=True,node_mass_rebooking_t=0,mass_rebooking_t=0,
            estimated_source_allocation_kg=kg,source_allocation_nonadditive=True,
            source_design_pr=520,approved_wallfit_unit=unit,l1_part_kind="wallfit_outfit_refinement")
        name="dry:L1_wallfit_"+unit
        ni=len(doc["nodes"]);doc["nodes"].append(dict(name=name,mesh=mi,extras=e))
        doc["nodes"][subsystem].setdefault("children",[]).append(ni)
        new.append(name)
    assert len(doc["meshes"])==original_meshes+7 and doc["scenes"]==original_scene
    assert doc["animations"]==original_anim
    assert all(doc["nodes"][i]==old for i,old in enumerate(original_nodes) if i!=subsystem)
    pressure=rows["pressure_vessel"]["shape"]
    states={};failures=[]
    for state,openhalo in (("halo_closed",False),("wings_open_centre_back",True)):
        parts=rendered(doc,binary,openhalo)
        contacts=[];shared_boundary=[]
        for name in new:
            for other,pieces in parts.items():
                if other==name or (other in new and other<name):continue
                if exact_shared_242_sector(name,parts[name],other,pieces):
                    # No positive volume possible; this is a geometrically
                    # proven face-sharing contact at the approved 242 deg ray.
                    shared_boundary.append({"unit":name,"other":other,
                        "angular_contact_deg":242.,"penetrating_volume_m3":0})
                    continue
                if overlap(parts[name],pieces):contacts.append({"unit":name,"other":other})
        shell=[]
        for name in new:
            v=np.concatenate([x for x,_ in parts[name]])
            m=float(shellmargin(v,pressure).min())
            shell.append({"unit":name,"inner_shell_margin_m":round(m,6),"PASS":m>=-1e-5})
        states[state]={"D9_category_d":len(contacts),"contacts":contacts,
            "zero_volume_authorized_shared_sector_contact":shared_boundary,
            "containment":"PASS" if all(x["PASS"] for x in shell) else "FAIL",
            "per_unit":shell,"minimum_inner_shell_margin_m":min(x["inner_shell_margin_m"] for x in shell),
            "existing_L1_rendered_nodes_checked":len(parts)-7,"new_units":7}
        failures.extend(state+": "+x["unit"]+" clashes "+x["other"] for x in contacts)
        failures.extend(state+": "+x["unit"]+" shell "+str(x["inner_shell_margin_m"])
                        for x in shell if not x["PASS"])
    if failures:
        picture(failures)
        result={"status":"STOP_WALLFIT_D9_OR_CONTAINMENT","failures":failures,
                "states":states,"diagnostic_picture":str(PICTURE.relative_to(ROOT)),
                "old_glb_preserved":True,"rebooking_t":0}
        STOP.write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2),flush=True)
        raise RuntimeError("STOP L1 wall-fit D9 / containment")
    doc["asset"]["extras"].update(L1_wallfit="kT_approved_PR520_7units",
        wallfit_mass_owner="outfit_L1",wallfit_estimated_kg=358,
        source_mass_rebooking_t=0,exterior_state_meshes_copied=0)
    newsha=B.save(doc,binary,GLB)
    prior["status"]="L1_B3_WALLFIT_SEVEN_D9_CONTAINMENT_PASS"
    prior["glb_sha256"]=newsha
    prior["wallfit"]={"source_pr":520,"units":new,"mass_owner":"outfit_L1",
        "outfit_L1_booked_t":outfit,"estimated_wallfit_t":.358,
        "outfit_L1_undrawn_t":outfit-.358,"room_L1_command_unchanged_t":room,
        "room_L1_command_purpose":"Source ENGINEERING_ASSUMPTION whole command/navigation room allowance, "
             "not a furniture itemised ledger. Exact component-level distribution unspecified; none charged here.",
        "source_mass_rebooking_t":0,"exterior_modified":0,"stations_and_halo_unchanged":True,
        "source_unit_estimated_mass_kg":dict(zip(UNITS,KG)),"pose_checks":states,
        "generator":"wayfarer/lab/l1_wallfit_generator.py","proposal_GLb_deleted":True,
        "G1_G12":"NOT RUN"}
    RPT.write_text(json.dumps(prior,indent=2)+"\n")
    with PRINT.open("a") as f:
        f.write("\n## L1 wall fit-out: kT approved PR #520\n"
            "Seven units under dome: cabinets h0..0.95m at r3.755..4.00m; U7 dome-following lining h0.30..1.30m. "
            "Book all estimated 358kg within outfit_L1 818.963kg, leaving ~460.963kg undrawn. "
            "The command/navigation room 2.150t booking remains untouched.\n"
            "At 1:25 cabinets up to 38mm tall and 9mm deep; door seams ~1.3mm and handles 4.8×1mm. "
            "0.015m lining is 0.6mm: separate skin or paint. Screen labels, controls, "
            "keypad marks, nozzles and warnings are DECALS.\n"
            "Use original #520 palette: light blue-grey #ACBBBD, slate #607A84, teal #3FA79A, "
            "ivory #D8D8CD, emergency red #B5473F, panel yellow #E3B23C, vault grey.\n")
    PROPOSAL.unlink(missing_ok=True)
    print(json.dumps({"status":prior["status"],"glb_sha256":newsha,"pose_checks":states,
        "mass_kg":358,"outfit_available_kg":outfit*1000,
        "proposal_deleted":not PROPOSAL.exists()},indent=2),flush=True)
if __name__=="__main__":main()
