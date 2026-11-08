#!/usr/bin/env python3
"""v2.5.1 glazing BReps, visual/geometry only. Booked v2.5 masses are untouched."""
import math
from build123d import Axis, Color, Plane, Solid
from packing_phase1b import source_brep_pilot as P

LAYER_NAMES = ("strata", "backup", "aoi", "primary", "bumper")

def _plane(origin, normal):
    # Tangent around the ship axis is perpendicular to every radial normal.
    return Plane(origin=origin, x_dir=(0., -normal[2], normal[1]), z_dir=normal)

def _translated(origin, normal, distance):
    return tuple(origin[i] + normal[i] * distance for i in range(3))

def _coloured(name, solid, colour):
    if not solid.is_valid or solid.volume <= 0:
        raise ValueError("invalid true glazing solid " + name)
    solid.label = name
    solid.color = Color(colour)
    return solid

def build_glazing(g, inputs, spare_source_pane):
    """21 round apertures, 5 L2 band segments, 7 real crown spares.
    
    Geometry positions are exclusively source features/bands, source WWS-1
    dimensions and the FIRST already screened bay-wall location. The Strata
    geometric thickness is the existing render equivalent 27g/cm2 / 2.7t/m3,
    NOT a new constitutive material claim. AOI nominal thickness is its
    existing areal column divided by its booked crown effective density.
    """
    ww = inputs["windows_wws1"]
    assert ww["port_count"] == 21 and ww["shelter_window_count"] == 0
    assert len(ww["port_list"]) == 21
    features = [f for f in g["features"] if f["kind"] == "window"]
    assert len(features) == 21
    band = inputs["habitat"]["crew_systems"]["viewport_band"]["segments"]
    assert len(band) == 5
    crown = inputs["habitat"]["decks"][0]["command_layout"]["crown_dome"]
    aoi = crown["adaptive_optogel"]
    aoi_rho_kg_m3 = 1000. * aoi["mass_t"] / 3.023
    aoi_t = ww["areal_kg_m2"]["aoi"] / aoi_rho_kg_m3
    stack = (0.1, 0.028, aoi_t, 0.028, 0.01) # inboard to outboard
    assert len(stack) == 5 and abs(sum(stack) - (0.166 + aoi_t)) < 1e-12
    # At exterior 4.5m pressure/armour skin, the WWS closure straddles its
    # thickness. It is NOT a pressure-seal or dynamic shutter qualification.
    r_outer = inputs["hull"]["pressure_r_m"] + 0.2 + 0.005
    parts, apertures, windows = {}, [], []
    colours = ("#667B8D", "#A4CFD5", "#57B7B3", "#85C0CA", "#B7DEDF")
    for idx, feat in enumerate(features):
        entry = ww["port_list"][idx]
        assert entry["room"] == feat["room"]
        assert abs(entry["diameter_m"] - feat["d_m"]) < 1e-8
        assert "shelter" not in entry["room"].lower()
        pos, normal = tuple(feat["pos"]), tuple(feat["normal"])
        radius = entry["diameter_m"] / 2
        inner = 0.005 - sum(stack)
        panes = []
        for name, t, colour in zip(LAYER_NAMES, stack, colours):
            p0 = _translated(pos, normal, inner)
            body = Solid.make_cylinder(radius, t, plane=_plane(p0, normal))
            label = f"dry:window_{feat['room']}_{idx}__{name}"
            parts[label] = _coloured(label, body, colour)
            panes.append(label)
            inner += t
        # Cylindrical clear bore + source 12 degree outward armour splay.
        straight = Solid.make_cylinder(radius + .002, .80,
                     plane=_plane(_translated(pos, normal, -.55), normal))
        splay = Solid.make_cone(radius + .002,
                    radius + .002 + .20 * math.tan(math.radians(12)), .20,
                    plane=_plane(_translated(pos, normal, -.20), normal))
        apertures.append(straight.fuse(splay))
        windows.append(dict(id=f"window_{feat['room']}_{idx}",
                            diameter_m=entry["diameter_m"], centre=pos,
                            layers=panes, booked_mass_t=entry["baseline_t"] +
                            entry["incremental_t"]))
    for idx, seg in enumerate(band):
        x0, x1 = seg["x_m"]
        a0, a1 = seg["theta_deg"]
        inner = r_outer - sum(stack)
        panes = []
        for name, t, colour in zip(LAYER_NAMES, stack, colours):
            label = f"dry:viewport_band_{idx}__{name}"
            body = P.sector(dict(k="sector", x0=x0, x1=x1,
                                 r0=inner, r1=inner+t, a0=a0, a1=a1))
            parts[label] = _coloured(label, body, colour)
            panes.append(label)
            inner += t
        # The cut is the actual prescribed five-sector aperture, not an
        # invented sixth segment across the L2 washroom.
        apertures.append(P.sector(dict(k="sector", x0=x0, x1=x1,
               r0=inputs["hull"]["pressure_r_m"]-.06,
               r1=inputs["hull"]["pressure_r_m"]+.25, a0=a0, a1=a1)))
        windows.append(dict(id=f"viewport_band_{idx}", x_m=[x0,x1],
                            theta_deg=[a0,a1], layers=panes))
    # kT chose first collision-screened rack: forward lower bay wall,
    # x20.00..22.60, y-0.95..+0.95, z-2.16..-2.03.
    spares = [
        (0, .75, 0, 360, False), (.75, 2, 0, 30, False),
        (.75, 2, 0, 30, False), (2, 2.75, 0, 30, True),
        (2, 2.75, 0, 30, True), (2.75, 3.5, 15, 45, True),
        (2.75, 3.5, 15, 45, True)
    ]
    names = []
    slope = math.tan(math.radians(50))
    for idx, (r0, r1, a0, a1, tilted) in enumerate(spares):
        is_centre = (idx == 0)
        solid = spare_source_pane(r0, r1, a0, a1, .01,
                        slope, center=is_centre)
        # Rotate panel normal to lower bay-wall Z; retain true BRep and
        # per-pane contour (not the conservative rectangular rack proxy).
        if not is_centre:
            solid = solid.rotate(Axis.X, -(a0+a1)/2)
        solid = solid.rotate(Axis.Y, 90)
        if tilted:
            solid = solid.rotate(Axis.X, math.degrees(math.atan(slope / math.cos(math.radians((a1-a0)/2)))))
        bounds = P.bounds(solid)
        origin = [(bounds[0]+bounds[1])/2,
                  (bounds[2]+bounds[3])/2,
                  (bounds[4]+bounds[5])/2]
        dest = [21.3, 0., -2.1507 + idx * .0186]
        solid = solid.translate(tuple(dest[j]-origin[j] for j in range(3)))
        bb = P.bounds(solid)
        if not (20 <= bb[0] and bb[1] <= 22.6 and
                -.95 <= bb[2] and bb[3] <= .95 and
                -2.16 <= bb[4] and bb[5] <= -2.03):
            raise ValueError(f"spare {idx+1} outside chosen screened rack: {bb}")
        label = f"dry:crown_spare_{idx+1:02d}"
        parts[label] = _coloured(label, solid, "#9FBAD2")
        names.append(label)
    assert len(windows) == 26 and len(parts) == 137
    assert len(set(parts)) == 137
    source_mass = {p["id"]:p["mass_t"] for p in g["parts"]}
    preserved = [p for p in source_mass if p.startswith("window_") or
                 p.startswith("viewport_band_") or
                 p.startswith("wws1_port_uplift_") or
                 p.startswith("wws1_band_uplift_")]
    report = dict(round_assemblies=21, viewport_band_segments=5,
                  storm_shelter_windows=0, spare_true_solids=7,
                  first_screened_bay_wall_x_m=[20., 22.6],
                  layers_inboard_to_outboard=list(LAYER_NAMES),
                  layers_m=[round(t,12) for t in stack],
                  aoi_thickness_source_derived_m=aoi_t,
                  closed_strata_render_equivalent_m=.1,
                  source_mass_allocations_unchanged=True,
                  sourced_window_booked_mass_t=sum(source_mass[n] for n in preserved),
                  individual_windows=windows, spare_names=names,
                  renderer_only=True, physically_unqualified=["pane retainers",
                      "pressure seals", "independent ceramic failure",
                      "dynamic shutter closure", "local particle-dose transport"])
    return parts, apertures, report
