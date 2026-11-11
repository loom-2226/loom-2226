#!/usr/bin/env python3
"""Wayfarer kT 2026-11-09 hull seam + surface engravings, pre-PBR review.

Drawing-only OCC blind marks. No new installed parts, no mass rebinding,
no changes to silhouette or pressure surfaces. 20mm skins and tank walls
CANNOT take literal 30mm cuts; their OCC marks are <=6mm deep and the
3cm apparent finish profile awaits kT's PBR treatment decision.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from build123d import Axis, Solid
from packing_phase1b import source_brep_pilot as P

ROOT=Path(__file__).resolve().parents[1]
WIDTH_M=.05
VISUAL_DEPTH_M=.03
THIN_SHELL_CUT_DEPTH_M=.006
FINE_WIDTH_M=.02
FINE_DEPTH_M=.003

def ring(x, radius, depth, offset=(0.,0.), width=WIDTH_M):
    y,z=offset
    # kT v2.5.8: nozzle alone gets 150 mm wide band (all other seams 50 mm).
    assert width in (WIDTH_M,.15,FINE_WIDTH_M)
    outer=Solid.make_cylinder(radius+.07,width,P.plane_x(x-width/2,y,z))
    inner=Solid.make_cylinder(radius-depth,width+.02,
                            P.plane_x(x-width/2-.01,y,z))
    return outer-inner

def longitudinal(x0,x1,radius,depth,az,offset=(0.,0.),width=WIDTH_M):
    if x1<=x0:raise ValueError((x0,x1))
    edge=P.box(x0,x1,radius-depth,radius+.07,-width/2,width/2)
    return edge.rotate(Axis.X,az).translate((0,offset[0],offset[1]))

def panel_edges(x0,x1,radius,depth,az,half_width):
    # Four blind grooves; no new hinge, hatch or structural cut.
    edges=[
        P.box(x0,x0+.027,radius-depth,radius+.04,-half_width,half_width),
        P.box(x1-.027,x1,radius-depth,radius+.04,-half_width,half_width),
        P.box(x0,x1,radius-depth,radius+.04,-half_width,-half_width+.027),
        P.box(x0,x1,radius-depth,radius+.04,half_width-.027,half_width),
    ]
    return [s.rotate(Axis.X,az) for s in edges]

def cut_surface(original,tools,name):
    shape=original
    v0=float(shape.volume)
    hits=0
    for tool in tools:
        # Exact OCC intersection avoids subtracting an irrelevant tool.
        common=shape & tool
        if common is None or float(common.volume)<1e-11:
            continue
        nxt=shape-tool
        if nxt is None or not nxt.is_valid or float(nxt.volume)<=0:
            raise RuntimeError("STOP: surface engraving invalid "+name)
        shape=nxt;hits+=1
    if hits:
        a=original.bounding_box();b=shape.bounding_box()
        before=(a.min.X,a.min.Y,a.min.Z,a.max.X,a.max.Y,a.max.Z)
        after=(b.min.X,b.min.Y,b.min.Z,b.max.X,b.max.Y,b.max.Z)
        if any(float(after[i])<float(before[i])-1e-6 for i in range(3)) or any(
               float(after[i])>float(before[i])+1e-6 for i in range(3,6)):
            raise RuntimeError("STOP: engraved solid exceeds source envelope "+name)
        shape.label=name
        shape.color=original.color
    return shape,dict(grooves_intersected=hits,display_only_removed_m3=max(0.,v0-float(shape.volume)))

def apply(installed,rows,mode):
    plan=json.loads((ROOT/"config/kt_decisions.json").read_text())[
        "hull_seam_scheme_2026_11_09"]
    assert plan["decision"]=="ACCEPTED"
    rings=plan["ring_seams_at_frames_x_m"]
    habitat=plan["habitat_ring_seams_x_m"]
    azs=plan["longitudinal_seams_azimuth_deg"]+plan["mid_split_azimuth_deg"]
    assert rings==list(range(14,35,2))
    assert habitat==[3,5.6,8.2,10.8]
    assert azs==[40,140,220,320,0,180,270]
    result=dict(installed)
    evidence={}
    source_targets=("armor","skin_service","skin_midship","skin_aft",
                    "tank_shell_out","tank_shell_in")
    for sid in source_targets:
        name="dry:"+sid
        assert name in result and sid in rows
        q=rows[sid]["shape"]
        outer=q["R"] if sid=="armor" else q["r1"]
        begin=2.35 if sid=="armor" else q["x0"]
        end=q["xc"] if sid=="armor" else q["x1"]
        depth=VISUAL_DEPTH_M if sid=="armor" else THIN_SHELL_CUT_DEPTH_M
        xs=([2.35]+habitat+[14]) if sid=="armor" else [
            x for x in rings if begin<=x<=end]
        cutters=[ring(x,outer,depth) for x in xs]
        # No 22.5-degree visual grid. The existing actual bay-door edges
        # remain the top-quarter panel boundaries.
        cutters += [longitudinal(begin+.06,end-.06,outer,depth,a) for a in azs]
        # True-scale fine blind sub-panels between the existing structural seams.
        fine_map=dict(armor=[4.3,9.5],skin_service=[15.,17.],
            skin_midship=[19.,23.,27.,31.],skin_aft=[33.],
            tank_shell_out=[19.,23.,27.,31.])
        fine_xs=[x for x in fine_map.get(sid,[]) if begin+.2<x<end-.2]
        cutters.extend(ring(x,outer,FINE_DEPTH_M,width=FINE_WIDTH_M) for x in fine_xs)
        fine_lines=dict(skin_service=[(14.4,15.6,20),(16.4,17.4,200)],
            skin_midship=[(18.45,19.45,20),(18.45,19.45,200),
                          (30.8,31.6,20),(30.8,31.6,200)],
            skin_aft=[(32.6,33.7,20),(32.6,33.7,200)]).get(sid,[])
        for x0,x1,a in fine_lines:
            cutters.append(longitudinal(x0,x1,outer,FINE_DEPTH_M,a,width=FINE_WIDTH_M))
        panels=[]
        if sid=="skin_service":panels=[(15.1,15.8,85),(15.1,15.8,255),
                                      (16.1,16.9,20),(16.1,16.9,200)]
        if sid=="skin_midship":panels=[(18.6,19.3,20),(30.8,31.5,200)]
        if sid=="skin_aft":panels=[(32.8,33.4,96),(32.8,33.4,236)]
        for x0,x1,ang in panels:
            cutters.extend(panel_edges(x0,x1,outer,depth,ang,.19))
        old=result[name]
        detailed,ev=cut_surface(old,cutters,name)
        result[name]=detailed
        evidence[name]=dict(source_allocation_id=sid,
            nominal_groove_width_m=WIDTH_M,
            requested_apparent_groove_depth_m=VISUAL_DEPTH_M,
            OCC_display_cut_depth_m=depth,
            thin_shell_nonperforation_guard=(sid!="armor"),
            ring_station_m=xs,
            longitudinal_seam_azimuth_deg=azs,
            maintenance_panel_outlines=len(panels),
            nostromo_subpanel_ring_x_m=fine_xs,
            nostromo_subpanel_longitudinal_count=len(fine_lines),
            print_space_dimensions_applied=False,bolts_paint_only=True,
            pressure_boundary_cuts=0,
            source_mass_rebooking_t=0,**ev)
    # Torch face decoration only; v2.5.8 nozzle bands are 150mm x 30mm,
    # with five unchanged source stations and no extra manufactured solids.
    # Dark gunmetal band faces are assigned at GLB primitive level.
    # Torch face decoration only: blind rings, seams and service-panel
    # outlines. No new separate band parts, no shielding or heat credit.
    torch={
      "shield":(2.75,.008,[34.7,38.9],[0,90,180,270],[]),
      "reactor":(2.125,.03,[39.7,43.2,45.9],[],[(40.2,42.1,a) for a in (0,90,180,270)]),
      "nozzle":(None,.03,[47.2,48.5,49.8,51.1,52.4],[],[]),
    }
    for sid,(radius,depth,xs,angs,panels) in torch.items():
        name="dry:"+sid
        assert name in result and sid in rows
        q=rows[sid]["shape"]
        offset=tuple(q.get("offset_yz",(0,0)))
        def r_at(x):
            if radius is not None:return radius
            return q["r0"]+(x-q["x0"])*(q["r1"]-q["r0"])/(q["x1"]-q["x0"])
        band_width=.15 if sid=="nozzle" else WIDTH_M
        tools=[ring(x,r_at(x),depth,offset,width=band_width) for x in xs]
        tools += [longitudinal(q["x0"]+.15,q["x1"]-.15,r_at(q["x0"]),depth,
                               a,offset) for a in angs]
        for x0,x1,ang in panels:
            tools.extend([v.translate((0,offset[0],offset[1]))
                         for v in panel_edges(x0,x1,r_at(x0),depth,ang,.40)])
        old=result[name]
        detailed,ev=cut_surface(old,tools,name)
        result[name]=detailed
        evidence[name]=dict(role=sid,
            ring_band_station_m=xs,band_width_m=band_width,
            band_depth_m=depth,segment_seams_azimuth_deg=angs,
            access_panel_outlines=len(panels),requested_groove_width_m=WIDTH_M,
            visual_only=True,source_mass_rebooking_t=0,**ev)
    return result,dict(
        mode=mode,approved_seam_scheme="hull_seam_scheme_2026_11_09",
        ring_width_m=WIDTH_M,requested_visual_depth_m=VISUAL_DEPTH_M,
        thin_wall_actual_OCC_depth_m=THIN_SHELL_CUT_DEPTH_M,
        legacy_22p5_degree_skin_grid_removed=True,
        nostromo_true_scale_subpanel_width_m=FINE_WIDTH_M,
        nostromo_true_scale_blind_depth_m=FINE_DEPTH_M,
        nostromo_bolts_paint_only=True,
        print_space_overrides_in_canon=False,
        top_quarter_preserves_bay_door_edges=True,
        no_pressure_boundary_perforation=True,
        source_mass_rebooking_t=0,parts=evidence)
