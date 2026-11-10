#!/usr/bin/env python3
"""Wayfarer F3: retro-industrial exterior engraving, bounded by source BReps.

Every edited part is the ORIGINAL installed true solid MINUS blind pockets or
engraved lines. Zero added/raised solids, zero protrusion, zero rebooking.
This is visual/print-level engineering, not flight/sensor/thermal qualification.
Original six-state D9, containment, G8 and extras remain mandatory via the
#488 six-state integrator. No changes to crown panes or mass ledger.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from collections import Counter
from build123d import Plane,Solid
from packing_phase1b import source_brep_pilot as P
from shuttle import shuttle_v1_fullship_integrate_20261110 as A

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"render/out"
PREFIX="wayfarer_exterior_detail_88ce19fc"
MIN_PRINT_FEATURE_M=.10
records={}
samples={}
ALL_CLASSES=("rcs","sensor_turret","rf_tiles","laser_terminal",
    "star_tracker","bow_ring","docking_camera","grapple_fixture",
    "service_port","vent","docking_target","eva_rail","hold_door",
    "folded_fin","fin_root")

def group_of(name):
    k=name.removeprefix("dry:")
    if k.startswith("rcs_"):return "rcs"
    if k.startswith("ext_sensor_turret_"):return "sensor_turret"
    if k.startswith("ext_rf_array_"):return "rf_tiles"
    if k.startswith("ext_laser_terminal_"):return "laser_terminal"
    if k.startswith("ext_star_tracker_"):return "star_tracker"
    if k=="bow_sensors":return "bow_ring"
    if k.startswith("docking_camera_"):return "docking_camera"
    if k.startswith("ext_grapple_fixture_"):return "grapple_fixture"
    if k.startswith("ext_service_port_"):return "service_port"
    if k.startswith("ext_vent_"):return "vent"
    if k.startswith("ext_docking_target_"):return "docking_target"
    if k.startswith("ext_eva_rail_"):return "eva_rail"
    if k.startswith("hold_existing_door_"):return "hold_door"
    if k.startswith("hotfin_") and k.endswith(":folded_envelope"):return "folded_fin"
    if k.startswith("hotfin_root_") and k.endswith(":root"):return "fin_root"
    return None

def source_id(name,klass):
    n=name[4:].split(":")[0]
    if klass=="hold_door":return "courier_systems"
    return n

def bb(shape):
    b=shape.bounding_box()
    return (float(b.min.X),float(b.max.X),float(b.min.Y),float(b.max.Y),
            float(b.min.Z),float(b.max.Z))

def face(name,source,shape):
    """Outward-facing radial side, plus its tangent and source X span."""
    b=bb(shape);xc=(b[0]+b[1])/2
    cy=(b[2]+b[3])/2;cz=(b[4]+b[5])/2
    k=source["shape"].get("k")
    if name.startswith("dry:hold_existing_door_"):
        ny,nz=(1.,0.) if "starboard" in name else (-1.,0.)
        cy=b[3] if ny>0 else b[2]
    elif name.startswith("dry:rcs_"):
        side=name.split("rcs_",1)[1]
        if side.endswith("+Y"):ny,nz=1.,0.
        elif side.endswith("-Y"):ny,nz=-1.,0.
        elif side.endswith("+Z"):ny,nz=0.,1.
        else:ny,nz=0.,-1.
        cy=b[3] if ny>0 else b[2] if ny<0 else (b[2]+b[3])/2
        cz=b[5] if nz>0 else b[4] if nz<0 else (b[4]+b[5])/2
    elif name.startswith("dry:docking_camera_"):
        ny,nz=0.,-1.
        cz=b[4]
    elif k=="sector":
        q=source["shape"]
        a=math.radians((q["a0"]+q["a1"])/2)
        ny,nz=math.cos(a),math.sin(a)
        cy,cz=q["r1"]*ny,q["r1"]*nz
    else:
        raise ValueError("no exterior face direction "+name)
    ey,ez=nz,-ny    # y_dir of plane with world X as local x
    return (xc,cy,cz,ny,nz,ey,ez,b[0],b[1])

def round_engraving(F,x,offset_t,radius,depth):
    _,cy,cz,ny,nz,ey,ez,_,_=F
    origin=(x,cy+ey*offset_t-ny*depth,cz+ez*offset_t-nz*depth)
    return Solid.make_cylinder(radius,depth+.09,
        Plane(origin=origin,x_dir=(1,0,0),z_dir=(0,ny,nz)))

def panel_engraving(F,x_start,x_len,t_start,t_width,depth):
    _,cy,cz,ny,nz,ey,ez,_,_=F
    origin=(x_start,cy+ey*t_start-ny*depth,
            cz+ez*t_start-nz*depth)
    return Solid.make_box(x_len,t_width,depth+.09,
        Plane(origin=origin,x_dir=(1,0,0),z_dir=(0,ny,nz)))

def ring_engraving(F,x,offset_t,r_outer,r_inner,depth):
    if not 0<r_inner<r_outer:raise ValueError("bad annular engraving")
    return round_engraving(F,x,offset_t,r_outer,depth)-round_engraving(
        F,x,offset_t,r_inner,depth+.002)

def panel_pleats(source,root=False):
    q=source["shape"]
    assert q["k"]=="panel"
    a=math.radians(q["a"])
    n=(0,math.cos(a),math.sin(a))    # radial plane axis
    t=(0,-math.sin(a),math.cos(a))   # tangential external face
    # P.panel places the broad face at local ±t/2. Every line is carved
    # into that existing face, not a raised fin or added printed bracket.
    start=q["x0"];stop=q["x1"]
    stride=2.4 if not root else 2.8
    count=int((stop-start-1)/stride)
    cutters=[]
    for i in range(count):
        x=start+1.2+i*stride
        # The installed v2.5.3 fitted hot-fin BRep can extend much
        # further radially than the dormant `source.shape.span` field.
        # Cut all the way across that EXISTING BRep's radial reach and
        # retain material solely by boolean subtraction. A short 2m
        # cutter at nominal r4.75 missed the actual fitted 140deg fin.
        extent=45.0
        # The installed source BRep for a hot-fin 'folded_envelope'
        # actually spans the deployed radial reach and its thin membrane
        # is the 5mm source deployed_panel_thickness, NOT the nominal
        # 0.6m stowed_stack_thickness drawing field. F3 engraves the
        # existing thin face; it does not thicken, relocate or fold it.
        installed_t=(q["t"] if root else .005)
        depth=min(.055,installed_t*.32)
        for side in (1,-1):
            direction=(0,side*t[1],side*t[2])
            offset_r=0.0 if side==1 else extent
            origin=(x,n[1]*offset_r+side*t[1]*(installed_t/2-depth),
                    n[2]*offset_r+side*t[2]*(installed_t/2-depth))
            cutters.append(Solid.make_box(.13,extent,depth+.012,
                Plane(origin=origin,x_dir=(1,0,0),z_dir=direction)))
    assert len(cutters)>=3
    return cutters

def cutters_for(name,klass,source,shape):
    if klass in ("folded_fin","fin_root"):
        return panel_pleats(source,root=(klass=="fin_root"))
    if klass=="bow_ring":
        # Existing source bow-sensor ring is internal to armour; four
        # small, blind face apertures never cut the pressure vessel.
        tools=[]
        for degrees in (0,90,180,270):
            a=math.radians(degrees);ny,nz=math.cos(a),math.sin(a)
            tools.append(Solid.make_cylinder(.075,.55,
                Plane(origin=(1.56,3.20*ny,3.20*nz),
                      x_dir=(1,0,0),z_dir=(0,ny,nz))))
        return tools
    F=face(name,source,shape)
    x=F[0];x0,x1=F[-2:]
    span=x1-x0
    k=source["shape"].get("k")
    radial_thick=source["shape"].get("r1",0)-source["shape"].get("r0",0) if k=="sector" else .8
    shallow=max(.002,min(.028,radial_thick*.27))
    tools=[]
    if klass=="rcs":
        # Housing recessed inside existing 0.8m cube; three radial
        # sockets plus ONE axial socket canted 10 degrees outward.
        tools.append(panel_engraving(F,x-.29,.58,-.27,.54,.035))
        for dx,offset in ((-.20,-.15),(0.,0.),(.20,.15)):
            tools.append(round_engraving(F,x+dx,offset,.072,.17))
        forward=name.startswith("dry:rcs_F")
        sign=-1 if forward else 1
        a=math.radians(10)
        ny,nz=F[3],F[4]
        normal=(sign*math.cos(a),ny*math.sin(a),nz*math.sin(a))
        b=bb(shape)
        xface=(b[0]+.14 if forward else b[1]-.14)
        tools.append(Solid.make_cylinder(.082,.27,
            Plane(origin=(xface,(b[2]+b[3])/2,(b[4]+b[5])/2),
                  x_dir=(0,F[5],F[6]),z_dir=normal)))
        # Access-panel engraving (rather than a protruding panel).
        tools.append(panel_engraving(F,x-.31,.62,-.30,.60,.008))
    elif klass=="sensor_turret":
        tools.extend((round_engraving(F,x,0,.135,.09),
                     ring_engraving(F,x,0,.26,.23,.012),
                     panel_engraving(F,x-.39,.18,-.32,.13,.012)))
    elif klass=="rf_tiles":
        # Flush, framed RF tiles; only engraved grid lines in 30mm source.
        for dx in (-.34,0.,.34):
            tools.append(panel_engraving(F,x+dx-.012,.024,-.34,.68,.007))
        for t in (-.18,.18):
            tools.append(panel_engraving(F,x-.56,1.12,t-.012,.024,.007))
    elif klass=="laser_terminal":
        # Recessed curved gimbal suggestion, not added dome outside
        # source exterior sector.
        tools.extend((round_engraving(F,x,0,.105,.065),
                     ring_engraving(F,x,0,.19,.166,.014)))
    elif klass=="star_tracker":
        # Baffle inside existing 0.08m-deep device, not a new tube.
        tools.extend((round_engraving(F,x,0,.056,.050),
                     ring_engraving(F,x,0,.087,.075,.009)))
    elif klass=="docking_camera":
        tools.extend((round_engraving(F,x,0,.053,.07),
                     ring_engraving(F,x,0,.080,.069,.015)))
    elif klass=="grapple_fixture":
        tools.extend((panel_engraving(F,x-.13,.26,-.115,.23,.011),
                     round_engraving(F,x,0,.060,.028)))
    elif klass=="service_port":
        tools.extend((round_engraving(F,x,0,.09,.012),
                     ring_engraving(F,x,0,.155,.14,.006)))
    elif klass=="vent":
        # A 0.12m part cannot carry a separate >=0.1m raised grille:
        # shallow below-threshold engraved slits only.
        for dx in (-.027,0.,.027):
            tools.append(panel_engraving(F,x+dx-.007,.014,-.023,.046,.005))
    elif klass=="docking_target":
        tools.extend((ring_engraving(F,x,0,.11,.09,.005),
                     round_engraving(F,x,0,.030,.005)))
    elif klass=="eva_rail":
        # Rail itself is <0.1m in transverse size; engrave bracket marks,
        # never invent raised 0.1m bolted supports outside its envelope.
        for xx in (x0+.36,x1-.36):
            tools.append(panel_engraving(F,xx-.052,.104,-.012,.024,.007))
    elif klass=="hold_door":
        # Existing 2.4x1.8m door is a 10mm sheet. Hatches/bolts are
        # ENGRAVINGS only, not 0.1m protruding hardware.
        tools.append(panel_engraving(F,x-.99,1.98,-.66,1.32,.003))
        for xx in (x-.86,x+.86):
            for t in (-.54,.54):
                tools.append(round_engraving(F,xx,t,.065,.004))
    else:
        raise ValueError("missing cutter style "+klass)
    assert tools
    return tools

def carve(old,tools,name):
    s=old
    before=float(old.volume)
    if not (old.is_valid and before>0):
        raise ValueError("invalid source BRep "+name)
    for cut in tools:
        s=s-cut
        if s is None or not s.is_valid or float(s.volume)<=0:
            raise RuntimeError("detail causes invalid/deleted part "+name)
    after=float(s.volume)
    removal=before-after
    if removal<=max(1e-10,before*1e-8):
        raise RuntimeError("detail did not engrave within source envelope "+name+
            " source_bbox="+str(bb(old))+
            " first_cut_bbox="+str(bb(tools[0])))
    a=bb(old);b=bb(s)
    if any(b[2*i]<a[2*i]-1e-6 or b[2*i+1]>a[2*i+1]+1e-6 for i in range(3)):
        raise RuntimeError("STOP kT F1: detail outside source bounding envelope "+name)
    # Difference from source is always an exact subset by construction.
    # A further OCC difference guards accidental BRep conversion defects.
    extra=s-old
    spill=0 if extra is None else float(extra.volume)
    if spill>1e-8:
        raise RuntimeError("STOP kT F1: added volume outside source "+name+" "+str(spill))
    s.label=name;s.color=old.color
    return s,dict(source_volume_m3=before,edited_volume_m3=after,
                  engraved_m3=removal,external_added_m3=spill,
                  same_source_envelope=True,feature_tools=len(tools))

def detail_ship(installed,rows,mode):
    updated=dict(installed)
    entries={};counts=Counter()
    for name in sorted(installed):
        klass=group_of(name)
        if klass is None:continue
        sid=source_id(name,klass)
        if sid not in rows:
            raise ValueError("detail without existing source booking "+name+" -> "+sid)
        original=installed[name]
        source=rows[sid]
        tools=cutters_for(name,klass,source,original)
        detailed,evidence=carve(original,tools,name)
        updated[name]=detailed
        entries[name]=dict(role=klass,source_allocation_id=sid,
                           booked_mass_t=source["mass_t"],**evidence)
        counts[klass]+=1
        if mode=="stowed" and name in (
            "dry:rcs_F+Y","dry:ext_sensor_turret_0",
            "dry:ext_rf_array_0","dry:hotfin_40:folded_envelope"):
            samples[name]=(original,detailed)
    expected=dict(rcs=8,sensor_turret=2,rf_tiles=4,laser_terminal=2,
        star_tracker=4,bow_ring=1,docking_camera=2,grapple_fixture=4,
        service_port=3,vent=4,docking_target=1,eva_rail=4,
        hold_door=2,folded_fin=0 if mode=="torch" else 4,fin_root=4)
    assert set(counts)=={k for k,v in expected.items() if v>0},(mode,dict(counts))
    assert all(counts[k]==v for k,v in expected.items()),(mode,dict(counts),expected)
    records[mode]=dict(edited_nodes=len(entries),by_role=dict(sorted(counts.items())),
        source_mass_rebooking_t=0,all_detail_subtractions=True,
        source_envelope_violations=0,parts=entries)
    print("F3_EXTERIOR_DETAIL",mode,len(entries),json.dumps(dict(counts)),flush=True)
    return updated

def render_f3():
    """Source/modified BRep tessellation, orthographic paired CAD render."""
    import matplotlib
    matplotlib.use("Agg")
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    names=["dry:rcs_F+Y","dry:ext_sensor_turret_0",
           "dry:ext_rf_array_0","dry:hotfin_40:folded_envelope"]
    assert all(n in samples for n in names),list(samples)
    fig=plt.figure(figsize=(15,15),facecolor="#141820")
    for row,name in enumerate(names):
        shapes=samples[name]
        bounds=[bb(v) for v in shapes]
        ext=[min(b[2*i] for b in bounds) for i in range(3)]
        top=[max(b[2*i+1] for b in bounds) for i in range(3)]
        mid=[(a+b)/2 for a,b in zip(ext,top)]
        radius=max((b-a)/2 for a,b in zip(ext,top)) * 1.3
        for col,obj in enumerate(shapes):
            ax=fig.add_subplot(4,2,row*2+col+1,projection="3d")
            vertices,faces=obj.tessellate(.035)
            verts=np.array([[v.X,v.Y,v.Z] for v in vertices])
            tris=np.array([[verts[k] for k in tri] for tri in faces])
            # Dense BRep tessellation; deliberately reduce display triangles
            # but never alter the exported CAD/GLB solids.
            if len(tris)>6000:tris=tris[::max(1,len(tris)//6000)]
            pc=Poly3DCollection(tris,linewidths=.04,
                    edgecolors="#4c5666",alpha=1)
            pc.set_facecolor("#81929b" if col==0 else "#adb6b3")
            ax.add_collection3d(pc)
            ax.set(xlim=(mid[0]-radius,mid[0]+radius),
                   ylim=(mid[1]-radius,mid[1]+radius),
                   zlim=(mid[2]-radius,mid[2]+radius))
            ax.view_init(elev=23,azim=-63)
            ax.set_proj_type("ortho")
            ax.set_axis_off()
            ax.set_title(name[4:]+("  SOURCE" if col==0 else "  ENGRAVED"),
                         color="white",size=10,pad=4)
    fig.suptitle("WAYFARER / F3  •  SOURCE vs ENVELOPE-CONTAINED DETAIL",
                 color="white",fontsize=17)
    fig.subplots_adjust(top=.94,bottom=.02,hspace=.12,wspace=.03)
    png=OUT/(PREFIX+"_F3_before_after.png")
    fig.savefig(png,dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    assert png.stat().st_size>5000
    return png.name

def main():
    A.PREFIX=PREFIX
    def integrate(*args):
        A.evaluate(*args,detail_pass=detail_ship)
    A.build_canon_v253(on_model_ready=integrate)
    p=OUT/(PREFIX+"_report.json")
    rpt=json.loads(p.read_text())
    assert rpt["status"]=="FULL_SHUTTLE_HOLD_3X2_D9_CONTAINMENT_EXTRAS_HIERARCHY_PASS"
    assert rpt["all_six_state_D9_and_containment"]=="PASS"
    assert set(records)=={"stowed","metric_hard","torch"}
    f3=render_f3()
    rpt.update(status="F3_EXTERIOR_DETAIL_SIX_STATE_D9_CONTAINMENT_PASS",
        exterior_detail=dict(style="retro-industrial; subtractions/engraving only",
        print_minimum_modelled_feature_m=MIN_PRINT_FEATURE_M,
        smaller_marks="ENGRAVINGS not raised printable solids",
        no_hull_protrusion=True,no_crown_change=True,no_performance_claims=True,
        no_new_source_mass=True,
        source_canon="canon-v2.5.3",
        modes=records),
        F3_before_after_png="render/out/"+f3)
    p.write_text(json.dumps(rpt,indent=2)+"\n")
    print("F3_EXTERIOR_SIX_STATE_PASS",f3,flush=True)

if __name__=="__main__":
    main()
