#!/usr/bin/env python3
"""Approved L3, source-authored Claude furniture; D9 + containment only.

Builds separate interior_L3.glb from l3_quarters/l3geom.py, the exact source
used by export3.py. Draws ten 0.5 m viewports as their original CTX triangles,
separately from 21 approved proposal groups. Their source-booked window
assembly masses are referenced nonadditively. No source fixture edits.
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
from l2_interior_glb import GLTF,rotate,srgb,inside_box_triangle
from l3_quarters import l3geom
import geom
SRC=ROOT/"results/out/wayfarer_v05_geometry.json"
DEC=ROOT/"config/kt_decisions.json"
HATCH=ROOT/"render/out/interior_deck_hatches_report.json"
OUT=ROOT/"render/out"
GLB=OUT/"interior_L3.glb"
REPORT=OUT/"interior_L3_report.json"
PIC=ROOT/"docs/WAYFARER_L3_APPROVED_D9_2026_11_13.png"
FLAG_PIC=ROOT/"docs/WAYFARER_L3_D9_FLAGS_2026_11_13.png"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
# Each original Claude room total, including its share of P0 partitions.
# P0 draws booking references, but no additional proposed mass.
EST={"B_CAPT_15":150,"C1_captain_wardrobe":50,"C2_captain_desk":40,
     "C3_captain_visitor_seat":20,
     "B_CA_75":190,"A1_crewA_lockers":100,"A2_crewA_desk":55,
     "B_GUEST_169":200,"B_GUEST_221":200,"G1_guest_lockers":140,"G2_guest_table":80,
     "B_CB_259":190,"B_CB_311":130,"B1_crewB_lockers":95,"B2_crewB_desk":50,
     "H1_guest_washroom":215,"H2_crew_washroom":215,
     "D3_lining":95,"D1_lighting":25,"D2_overhead_rail":25}
ROOMS=[("CAPT",0,60),("CA",60,120),("HG",120,150),
       ("GUEST",150,240),("CB",240,330),("HC",330,360)]
ROOM_CODES={k:"room_L3-"+k for k,_,_ in ROOMS}
ROOM_TOTAL={"CAPT":260,"CA":345,"HG":215,"GUEST":620,"CB":465,"HC":215}
def itemowner(it):
    if it.startswith("P0_"):
        return "room_L3-"+it.removeprefix("P0_")
    if it.startswith("D"):
        return "outfit_L3"
    if it.startswith("B_"):
        return "room_L3-"+it.split("_")[1]
    return {"C":"room_L3-CAPT","A":"room_L3-CA","G":"room_L3-GUEST",
            "B":"room_L3-CB","H":"room_L3-HG" if it.startswith("H1") else "room_L3-HC"}[it[0]]
def samples(tris):
    tri=np.concatenate([np.asarray(t,float).reshape((-1,3,3)) for t in tris.values()])
    return np.concatenate((tri.reshape(-1,3),
        .5*(tri[:,0]+tri[:,1]),.5*(tri[:,1]+tri[:,2]),
        .5*(tri[:,2]+tri[:,0]),tri.mean(axis=1)),axis=0)
def water_intrusions(it,tris,waters):
    p=samples(tris)
    x=p[:,0];y=-p[:,2];z=p[:,1];r=np.hypot(y,z)
    az=(np.degrees(np.arctan2(z,y))+360)%360
    out=[]
    for w in waters:
        q=w["shape"];eps=1e-5
        if q["a0"]==0 and q["a1"]==360:
            valid=np.ones(len(p),bool)
        else:
            valid=(az>q["a0"]+1e-4)&(az<q["a1"]-1e-4)
        valid &= (x>q["x0"]+eps)&(x<q["x1"]-eps)
        valid &= (r>q["r0"]+eps)&(r<q["r1"]-eps)
        idx=np.where(valid)[0]
        if len(idx):
            out.append(dict(item=it,source_part=w["id"],sample_intrusions=len(idx),
                  first_point_ship_xyz_m=[round(float(x[idx[0]]),6),
                    round(float(y[idx[0]]),6),round(float(z[idx[0]]),6)],
                  sample_min_r_m=float(r[idx].min()),sample_max_r_m=float(r[idx].max()),
                  sample_min_h_m=float((8.2-x[idx]).min()),
                  sample_max_h_m=float((8.2-x[idx]).max())))
    return out
def boxhits(it,tris,shape,name):
    if "x0" not in shape:return []
    e=1e-5
    lo=np.array([shape["x0"],shape["z0"],-shape["y1"]])+e
    hi=np.array([shape["x1"],shape["z1"],-shape["y0"]])-e
    if np.any(lo>=hi):return []
    for material,T in tris.items():
        t=np.asarray(T,float).reshape(-1,3,3)
        mi=t.min(axis=1);ma=t.max(axis=1)
        indices=np.where(np.all(ma>lo,axis=1)&np.all(mi<hi,axis=1))[0]
        for i in indices:
            if inside_box_triangle(t[i],lo,hi):
                return [dict(item=it,physical_fixture=name,material=material,
                              triangle=int(i),category="d")]
    return []
def picture_geometry():
    fig,ax=plt.subplots(figsize=(9.8,8.8))
    fig.patch.set_facecolor("#f6f5f1");ax.set_facecolor("#f6f5f1")
    colors=["#b6c5b8","#d9d2b9","#bad5d6","#c7cdc3","#d5bdaf","#d4cfb4"]
    for i,(r,a,b) in enumerate(ROOMS):
        ax.add_patch(Wedge((0,0),4.07,a,b,width=2.18,
            facecolor=colors[i],edgecolor="#8b928c",lw=1.5))
        mid=math.radians((a+b)/2)
        ax.text(3.05*math.cos(mid),3.05*math.sin(mid),r,
                ha="center",va="center",fontsize=10,weight="bold")
    ax.add_patch(Circle((0,0),1.25,facecolor="#eceae3",
                        edgecolor="#767a76",lw=1.5))
    ax.add_patch(Circle((0,0),4.11,fill=False,edgecolor="#297b93",
                        lw=6,alpha=.38))
    for room,angle,tiers in l3geom.BERTHS:
        a=math.radians(angle)
        ax.plot(3.0*math.cos(a),3.0*math.sin(a),"s",
                color="#8e5b45",markersize=9 if tiers==2 else 7)
    for rid,ang in l3geom.DOORS.items():
        a=math.radians(ang)
        ax.plot(1.9*math.cos(a),1.9*math.sin(a),".",color="#334b4b",markersize=10)
    for ang,hh in l3geom.WIN:
        a=math.radians(ang)
        ax.plot(4.07*math.cos(a),4.07*math.sin(a),"o",
                markerfacecolor="#b5dce8",markeredgecolor="#236481",markersize=6)
    ax.plot([-1.86,-1.86],[-.46,.46],alpha=.0)  # no L2/L3 leaves protrude into L3
    ax.set(xlim=(-4.7,4.7),ylim=(-4.7,4.7),
           xlabel="Ship Y (m)",ylabel="Ship Z (m)",title="L3 deck plan; source positions")
    ax.set_aspect("equal")
    fig.suptitle("WAYFARER 2226  |  L3 QUARTERS  |  D9 + CONTAINMENT")
    fig.text(.5,.035,"21 Claude-approved furniture groups. 10 source Ø0.5 m viewport render meshes; water-ring r4.07–4.15 m. Mass-neutral.",ha="center",fontsize=9)
    fig.tight_layout(rect=[0,.06,1,.93])
    PIC.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(PIC,dpi=155)
    plt.close(fig)
def picture_flags(items,flags,water):
    if not flags:return
    n=len(flags);cols=min(3,n);rows=math.ceil(n/cols)
    fig,axes=plt.subplots(rows,cols,figsize=(5*cols,3.8*rows),squeeze=False,layout="constrained")
    for ax,entry in zip(axes.flat,flags):
        it=entry.get("item")
        w=next((q for q in water if q["id"]==entry.get("source_part")),None)
        if it in items and w:
            pt=samples(items[it]);r=np.hypot(pt[:,1],pt[:,2]);h=8.2-pt[:,0]
            ax.scatter(r,h,s=.4,c="#698b92",alpha=.18,rasterized=True)
            a=w["shape"]
            ax.add_patch(Rectangle((a["r0"],8.2-a["x1"]),a["r1"]-a["r0"],a["x1"]-a["x0"],
                color="#bd6b50",alpha=.3))
            ax.set_xlim(max(1.0,a["r0"]-.25),a["r1"]+.25)
            ax.set_ylim(-.12,2.43)
            ax.set_xlabel("Radius (m)")
            ax.set_ylabel("Height (m)")
        ax.set_title(f"{it}: {entry.get('source_part',entry.get('physical_fixture','source envelope'))}",
            fontsize=10)
        ax.text(.02,.98,f"{entry.get('sample_intrusions','physical')} flag",transform=ax.transAxes,va="top",fontsize=9)
    for ax in list(axes.flat)[n:]:ax.axis("off")
    fig.suptitle("WAYFARER L3  |  D9 FLAG LOCATIONS  |  STOP, DO NOT MOVE GEOMETRY")
    fig.savefig(FLAG_PIC,dpi=150)
    plt.close(fig)
def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA,"STOP source geometry basis changed"
    G=json.loads(SRC.read_text());D=json.loads(DEC.read_text())
    assert abs(G["dry_t"]-868.1922552640087)<1e-8
    assert D["deck_hatches_2026_11_12"]["status"].startswith("BUILT")
    h=json.loads(HATCH.read_text())
    assert h["checks"]["D9_category_d"]==0
    assert h["checks"]["containment"]=="PASS"
    assert h["hatches"]["hatch_L2L3_0"]["shape"]["x1"]==5.60
    assert h["hatches"]["hatch_L2L3_1"]["shape"]["x1"]==5.60
    assert h["hatches"]["hatch_L3L4_0"]["shape"]["x0"]==8.26
    assert h["hatches"]["hatch_L3L4_1"]["shape"]["x0"]==8.2
    parts={p["id"]:p for p in G["parts"]}
    l3geom.build()
    grouped={}
    for (it,mat),tri in geom.T.items():
        if it in ("ARCH","CTX") or not tri:continue
        V=np.asarray(tri,float).reshape(-1,3,3)
        if it=="P0_partitions":
            az=(np.degrees(np.arctan2(V[:,:,1].mean(axis=1),
                                      -V[:,:,2].mean(axis=1)))+360)%360
            room_idx=np.zeros(len(az),int)
            for j,(room,lo,hi) in enumerate(ROOMS):
                room_idx[(az>=lo)&(az<hi)]=j
            for j,(room,lo,hi) in enumerate(ROOMS):
                selection=V[room_idx==j]
                if len(selection):grouped.setdefault("P0_"+room,{})[mat]=selection
        else:grouped.setdefault(it,{})[mat]=V
    proposal={it for it,mat in geom.T if it not in ("ARCH","CTX")}
    assert len(proposal)==21,("STOP unexpected Claude proposal group count",len(proposal))
    assert proposal-{"P0_partitions"}==set(grouped)-{it for it in grouped if it.startswith("P0_")}
    assert set(EST)==proposal-{"P0_partitions"},(set(EST)-proposal,proposal-set(EST))
    assert len([it for it in grouped if it.startswith("P0_")])==6
    # Source window names and their angular/height centres MUST match Claude.
    src_window=[p for p in G["parts"] if p["id"].startswith("window_L3-")]
    assert len(src_window)==10
    windows={}
    for win in src_window:
        a=win["shape"];x=(a["x0"]+a["x1"])*.5
        y=(a["y0"]+a["y1"])*.5;z=(a["z0"]+a["z1"])*.5
        ang=(math.degrees(math.atan2(z,y))+360)%360
        idx=np.argmin([abs(((ang-wa+180)%360)-180)+100*abs((8.2-x)-hh)
                       for wa,hh in l3geom.WIN])
        wa,hh=l3geom.WIN[idx]
        assert abs(((ang-wa+180)%360)-180)<.01 and abs((8.2-x)-hh)<.02,(win["id"],ang,x,wa,hh)
        windows[(wa,hh)]=win["id"]
    assert len(windows)==10
    # Viewport's authored CTX material triangles are kept as 10 distinct source
    # assembly meshes, not treated as a new mass allocation or moved to improve D9.
    ctx={}
    for material in ("space","titanium"):
        t=geom.T.get(("CTX",material))
        assert t,(material,"missing source viewport geometry")
        V=np.asarray(t,float).reshape(-1,3,3)
        cent=V.mean(axis=1)
        az=(np.degrees(np.arctan2(cent[:,1],-cent[:,2]))+360)%360
        hh=8.2-cent[:,0]
        dst=np.array([[abs(((a-wa+180)%360)-180)+100*abs(hh_i-h)
                         for wa,h in l3geom.WIN] for a,hh_i in zip(az,hh)])
        nearest=np.argmin(dst,axis=1)
        for i,(wa,h) in enumerate(l3geom.WIN):
            T=V[nearest==i]
            assert len(T)>0,(material,wa,h)
            ctx.setdefault(windows[(wa,h)],{})[material]=T
    assert len(ctx)==10
    owners={**{k:parts[k]["mass_t"]*1000 for k in
                  ["outfit_L3"]+[f"room_L3-{r}" for r,_,_ in ROOMS]},
            **{w["id"]:w["mass_t"]*1000 for w in src_window}}
    used={k:0 for k in owners}
    for it in grouped:used[itemowner(it)]+=EST.get(it,0)
    assert all(used[f"room_L3-{r}"]==ROOM_TOTAL[r] for r in ROOM_TOTAL)
    assert used["outfit_L3"]==145
    excess={k:dict(used_kg=used[k],booked_kg=owners[k]) for k in used if used[k]>owners[k]+1e-5}
    report=dict(source_geometry_sha256=SHA,source_dry_t=G["dry_t"],
        ECON_dv_km_s=707.845,source_mass_rebooking_t=0,
        approved_proposal_groups=len(proposal),source_proposal_nodes=sorted(proposal),
        L3_source_viewport_diameter_m=.5,L3_source_viewport_count=len(ctx),
        L3_viewport_part_ids=sorted(ctx),source_window_booking_repeated_nonadditive=True,
        partitions_split_by_room=True,
        booking_kg=owners,estimated_drawn_kg=used,booking_exceeded=excess,
        L2L3_hatches_upward_into_L2=True,L3L4_180_hatch_floor_stowed=True,
        exterior_GLBS_changed=0,other_interior_GLBS_changed=0,
        checks=dict(G1_G12="NOT RUN / NOT REQUIRED"))
    OUT.mkdir(parents=True,exist_ok=True)
    picture_geometry()
    if excess:
        report.update(status="STOP_L3_BOOKING_EXCEEDED")
        REPORT.write_text(json.dumps(report,indent=2)+"\n")
        raise RuntimeError(report["status"]+str(excess))
    all_pts=np.concatenate([np.asarray(v).reshape(-1,3) for d in grouped.values() for v in d.values()])
    r=np.hypot(all_pts[:,1],all_pts[:,2]);height=8.2-all_pts[:,0]
    shell=parts["pressure_vessel"]["shape"]["R"]-parts["pressure_vessel"]["shape"]["t"]
    core=parts["core_racks"]["shape"]["r1"]
    # The berth water ring is a source-preserved, separate 0.08 m water solid.
    # The r=4.07 lining and water ring can TOUCH, but cannot intersect into
    # positive-thickness protected water. Never reposition Claude's lining.
    waters=[p for p in G["fluids_by_state"]["S1"] if p["id"] in
            ("jacket_berth_ring","jacket_berth_wall_extended")]
    assert len(waters)==3
    jacket=[]
    for it,tris in grouped.items():jacket.extend(water_intrusions(it,tris,waters))
    clearances=dict(core_racks_m=float(r.min()-core),
        pressure_shell_m=float(shell-r.max()),
        L3_floor_m=float(height.min()),L2_floor_m=float(2.3-height.max()),
        inner_berth_water_ring_m=float(4.07-r.max()))
    # Core enclosure, floors and pressure hull containment; the L3 room
    # envelope is NOT a physical collision volume.
    invalid=[k for k in ("core_racks_m","pressure_shell_m","L3_floor_m","L2_floor_m")
             if clearances[k]<-1e-5]
    fixtures={p["id"]:p["shape"] for p in src_window}
    fixtures["hatch_L3L4_1"]=h["hatches"]["hatch_L3L4_1"]["shape"]
    # L2 leaves have been flipped upward; neither occupies L3.
    physical=[]
    for it,tris in grouped.items():
        for name,sh in fixtures.items():physical.extend(boxhits(it,tris,sh,name))
    d9=len(jacket)+len(physical)+len(invalid)
    contained=not invalid
    checks=dict(D9_category_d=d9,containment="PASS" if contained else "FAIL",
       source_clearances_m={k:round(v,8) for k,v in clearances.items()},
       protected_berth_ring_intrusions=jacket,physical_fixture_contacts=physical,
       source_envelope_violations=invalid,
       water_sampling_basis="all vertices, 3 edge midpoints and triangle centroids",
       viewport_source_qualification="0.5 m drawn from Claude CTX; aperture machining, pressure seal and WWS-1 size change NOT qualified",
       L2L3_upward_guard_not_in_L3=True,
       G1_G12="NOT RUN / NOT REQUIRED")
    report["checks"]=checks
    flags=jacket+physical+[dict(item="L3",physical_fixture=v) for v in invalid]
    if d9 or not contained:
        picture_flags(grouped,flags,waters)
        report.update(status="STOP_L3_D9_OR_CONTAINMENT",
             flag_picture=str(FLAG_PIC.relative_to(ROOT)),
             D9_flag_count=len(flags))
        REPORT.write_text(json.dumps(report,indent=2)+"\n")
        raise RuntimeError("STOP L3 D9: "+json.dumps(flags)[:5500])
    # GLB source-authored triangles; independent from exterior and L1/L2/L4/L5.
    # Repeated B berth pods remain distinct because some are 1 tier, some 2.
    mats=sorted({m for d in list(grouped.values())+list(ctx.values()) for m in d})
    mi={m:i for i,m in enumerate(mats)}
    gl=GLTF()
    gl.nodes.append(dict(name="LOOM_WAYFARER_L3_INTERIOR",children=[1],
        extras=dict(source_geometry_sha256=SHA,mass_neutral=True,
                    L3_source_windows_0_5m=True,other_deck_GLBS_untouched=True)))
    gl.nodes.append(dict(name="system:HABITAT",children=[]))
    sysnodes={}
    def add(it,tri,own,name,propose,additional=None):
        sub=own.removeprefix("room_L3-") if own.startswith("room_L3-") else (
             "deck_services" if own=="outfit_L3" else "source_viewports")
        if sub not in sysnodes:
            n=len(gl.nodes);sysnodes[sub]=n
            gl.nodes.append(dict(name="subsystem:HABITAT/L3_"+sub,children=[]))
            gl.nodes[1]["children"].append(n)
        e=dict(zone="FORE",deck="L3",material="L3 approved organic Japandi",
            print_group="HABITAT/L3_"+sub,mass=parts[own]["mass_t"],mass_unit="t",
            mass_basis="source_booking_reference_nonadditive",
            source_mass_owner_id=own,source_geometry_sha256=SHA,
            node_mass_rebooking_t=0,source_booking_repeated_nonadditive=True,
            semantic_system="HABITAT",semantic_subsystem="L3_"+sub,
            approved_proposal_node=propose,
            estimated_group_drawn_kg=EST.get(it,0))
        if additional:e.update(additional)
        mesh=gl.mesh(it,tri,mi)
        n=len(gl.nodes)
        gl.nodes.append(dict(name=name,mesh=mesh,extras=e))
        gl.nodes[sysnodes[sub]]["children"].append(n)
    for it in sorted(grouped):
        add(it,grouped[it],itemowner(it),"dry:L3_"+it,
            "proposal:L3_"+("P0_partitions" if it.startswith("P0_") else it))
    for win in src_window:
        wid=win["id"]
        add(wid,ctx[wid],wid,"dry:L3_"+wid,"source:L3_0.5m_viewport",
            dict(viewport_diameter_m=.5,source_window_id=wid,
                 clearance_interface="source booked L3 window, independent viewer mesh; no new water-ring cut"))
    materials=[]
    for mat in mats:
        col,em=geom.MAT[mat]
        materials.append(dict(name="CANON_FINISH/L3/"+mat,doubleSided=True,
           pbrMetallicRoughness=dict(baseColorFactor=srgb(col),
             metallicFactor=.6 if mat=="titanium" else 0.,
             roughnessFactor=.35 if mat in ("titanium","glass") else .7),
           **(dict(emissiveFactor=srgb(col)[:3]) if em else {})))
    blob=gl.finish(materials,SHA)
    GLB.write_bytes(blob)
    report.update(status="L3_D9_CATEGORY_D_ZERO_CONTAINMENT_PASS",
       glb="render/out/interior_L3.glb",glb_sha256=hashlib.sha256(blob).hexdigest(),
       glb_bytes=len(blob),
       glb_mesh_nodes=sum("mesh" in n for n in gl.nodes),glb_unique_meshes=len(gl.meshes),
       source_proposal_groups=21,room_partition_split_nodes=6,
       source_viewport_nodes=len(ctx),
       source_geometry_exact=True,repeated_berths="each original berth authored separately",
       smooth_normals=True,palette="Claude approved organic Japandi",
       picture=str(PIC.relative_to(ROOT)),D9_flag_count=0)
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","checks","estimated_drawn_kg",
         "approved_proposal_groups","glb_mesh_nodes","glb_sha256","picture")},indent=2))
if __name__=="__main__":main()
