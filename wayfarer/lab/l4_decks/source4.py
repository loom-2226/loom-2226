#!/usr/bin/env python3
"""kT L4 source-position fixes, locally applied at interior build boundary.

Returns actual BRep solids for mass-neutral water plug and radially stowed
L3/L4 hatch; corrects source-frame medical window proxies (+0.20 m X).
Never revises booked source inventories or claims fresh G1-G12 qualification.
"""
import math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"packing_phase1b"))
import source_brep_pilot as P

def overlap(a,b):
    c=a & b
    return 0. if c is None else float(c.volume)

def apply(G,hatches):
    rows={p["id"]:p for p in G["parts"]}
    fluids={p["id"]:p for p in G["fluids_by_state"]["S1"]}
    # The water-filled closing plug precisely replaces (not adds to) the
    # 0.8m-width opening in the inner 20cm shelter water jacket at 90 degrees.
    inner=P.make(fluids["jacket_inner"]["shape"])
    a=math.degrees(.4/2.)
    slot=P.make(dict(k="sector",x0=8.7,x1=10.6,r0=1.9,r1=2.1,a0=90-a,a1=90+a))
    plug=inner & slot
    wall=inner-slot
    v=float(inner.volume)
    w=float(wall.volume); q=float(plug.volume)
    assert q>0.15 and abs(w+q-v)<1e-6,("STOP: protected water not conserved",v,w,q)
    assert overlap(wall,plug)<1e-7,("STOP door intersects water")
    # hatch_L3L4_0 (180 degrees, Y negative) slides radially within floor_L3.
    # _1 at 0 degrees (Y positive) remains exactly as in the merged hatch file.
    src=hatches["hatch_L3L4_0"]["shape"]
    assert src["y0"]<0 and hatches["hatch_L3L4_1"]["shape"]["y0"]>0
    stowed=dict(k="box",x0=8.26,x1=8.32,y0=-2.75,y1=-1.83,z0=-.46,z1=.46)
    leaf=P.make(stowed)
    floor=P.make(rows["floor_L3"]["shape"])
    for y in (-1.4,1.4):
        floor=floor-P.cyl(.4,8.18,8.52,y,0.)
    pocket=P.box(8.25,8.33,-2.76,-1.82,-.47,.47)
    floor=floor-pocket
    assert overlap(leaf,floor)<1e-8,("STOP: parked sliding leaf clashes with slab")
    assert leaf.bounding_box().min.X>8.2 and leaf.bounding_box().max.X<8.5
    assert overlap(leaf,P.make(hatches["hatch_L3L4_1"]["shape"]))<1e-8
    # Visual source port centres; keep the same 0.30m proxy extents and mass.
    # Medical port true diameter = 1.55m as already authored by l4geom.
    ports={}
    for number in (4,5,6):
        for prefix in ("window_L4-medical_","wws1_port_uplift_"):
            name=prefix+str(number)
            shape=rows[name]["shape"]
            moved={**shape,"x0":shape["x0"]+.20,"x1":shape["x1"]+.20}
            assert abs((moved["x0"]+moved["x1"])/2-9.3)<1e-8
            ports[name]=moved
    # Top edge 1.50m+0.775m = 2.275m, lower than the L4 ceiling 2.30m.
    assert 1.50+.775<=2.30
    changed=dict(
        shelter_water_door=dict(original_jacket_m3=v,remaining_wall_m3=w,
            plug_volume_m3=q,water_total_after_m3=w+q,water_mass_delta_t=0,
            width_m=.8,at_deg=90,closed_mode_water_thickness_m=.20),
        medical_ports=dict(source_ids=sorted(ports),centre_x_before_m=9.10,
            centre_x_after_m=9.30,centre_height_m=1.50,diameter_m=1.55,
            port_top_height_m=2.275,source_proxy_overrides=ports,
            source_mass_delta_t=0),
        sliding_hatch=dict(name="hatch_L3L4_0",azimuth_deg=180,
            originally_open_x_m=[src["x0"],src["x1"]],
            parked_stowed=stowed,slab_pocket=dict(x_m=[8.25,8.33],
                y_m=[-2.76,-1.82],z_m=[-.47,.47]),
            floor_intersection_m3=0,source_mass_delta_t=0),
        other_hatch=dict(name="hatch_L3L4_1",
            pose=hatches["hatch_L3L4_1"]["shape"],unchanged=True),
        dry_mass_delta_t=0,water_mass_delta_t=0)
    return dict(inner_wall=wall,water_plug=plug,sliding_leaf=leaf,
         floor_L3_cut=floor,source_port_overrides=ports,
         changed=changed,inner_jacket=inner)
