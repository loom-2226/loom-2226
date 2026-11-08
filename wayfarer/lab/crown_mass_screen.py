#!/usr/bin/env python3
"""Crown material inventory and six-mode reach, from actual source-dimension BReps.

Source G remains untouched. Candidate material densities and remaining
render-derived track/gore thickness assumptions are stated, not disguised.
"""
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"))
from crown_geom_v25 import make_pane,domes_and_aoi
from packing_phase1b import source_brep_pilot as P

GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
INPUT=ROOT/"config/wayfarer_v05_inputs.json"
SPARES=ROOT/"results/out/crown_seven_spares_bay_options.json"
OUT=ROOT/"results/out/crown_solid_mass_modes_screen.json"
SHA="88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1"
RHO_CERAMIC=3.75    # source density for the panes and both monolithic domes
RHO_TITANIUM=4.43   # nominal Ti alloy; source says Osteon titanium, 2226 alloy density OPEN
RHO_STRATA=2.7      # render/crown_section.py, explicit illustrative coverage density
GORE_T=0.10         # render/crown_section.py, 27g/cm2 at 2700kg/m3
TRACK_WIDTH=.04     # render/research/* 0.04m blade width
TRACK_DEPTH=.10     # render/research/* 0.10m depth

def center(part):
    c=part.center()
    return [float(c.X),float(c.Y),float(c.Z)]
def mod_moment(moment,mass,center,sgn=1):
    for i in range(3):moment[i]+=sgn*mass*center[i]
def record(p,desc,mat,rho):
    v=float(p.volume)
    return dict(id=desc,material=mat,volume_m3=v,density_t_m3=rho,
        mass_t=v*rho,centroid_m=center(p),method="BRep physical volume x named density")

def main():
    assert hashlib.sha256(GEO.read_bytes()).hexdigest()==SHA
    g=json.loads(GEO.read_text())
    i=json.loads(INPUT.read_text())
    s=json.loads(SPARES.read_text())
    cfg=i["habitat"]["decks"][0]["command_layout"]["crown_dome"]
    tiles=cfg["shell_option_c"]["outer_tile_layer"]
    by={p["id"]:p for p in g["parts"]}
    old_dry=float(g["dry_t"])
    oldmoment=[sum(p["mass_t"]*p["centroid_m"][j] for p in g["parts"]) for j in range(3)]
    removed=[]
    def retire(part_id):
        p=by[part_id]
        removed.append(dict(id=part_id,mass_t=p["mass_t"],centroid_m=p["centroid_m"],
           reason="old physical proxy retired" if "no_render" in p["tags"] else "old cut source material retired"))
    for key in ("crown_dome","crown_c_additional_strata_gore","crown_backup_pressure_dome","crown_c_seven_spare_panes","armor","pressure_vessel"):
        retire(key)
    # Retainer 0.120t and AOI 3.041t are intentionally not retired: kT
    # requires conservative gel booked and hardware-not-modelled retainer.
    original={name:P.make(by[name]["shape"]) for name in ("armor","pressure_vessel")}
    opt=cfg["shell_option_c"]["deep_pressure_domes"]
    base=opt["parent_base_x_m"]
    rr=cfg["r_m"]
    outside_rim=base-(base-opt["backup_apex_x_m"])*math.sqrt(1-(rr/opt["parent_radius_m"])**2)
    seat=P.sector(dict(k="sector",x0=outside_rim,
      x1=outside_rim+cfg["brow_ring"]["height_m"],r0=rr,
      r1=rr+cfg["brow_ring"]["width_m"],a0=0,a1=360))
    aperture=P.cyl(rr,-2.0,base+.001)
    cut={}
    for name in original:
        cut[name]=(original[name]-aperture)-seat
    # Source booked density is the only current material-density basis for
    # the mixed legacy armor/PV materials; it is explicit, never 3750kg/m3.
    newparts=[]
    for name in ("armor","pressure_vessel"):
        dens=by[name]["mass_t"]/float(original[name].volume)
        newparts.append(record(cut[name],"dry:"+name,"source booked effective "+name,dens))
    newparts.append(record(seat,"dry:crown_osteon_brow_seat",
                           "Osteon titanium, nominal Ti alloy assumption",RHO_TITANIUM))
    outer,inner,gel=domes_and_aoi(cfg)
    newparts.append(record(outer,"dry:crown_outer_pressure_dome","transparent ceramic",RHO_CERAMIC))
    newparts.append(record(inner,"dry:crown_inner_pressure_dome","transparent ceramic",RHO_CERAMIC))
    # Installed panes: one central, twelve per three annular bands.
    for j in range(37):
        if j==0:pane=make_pane(0,.75,0,360,.01,math.tan(math.radians(50)),center=True)
        else:
            k=j-1;b=1+k//12;az=k%12
            start=30*az+(15 if b==3 else 0)
            pane=make_pane(tiles["radii_m"][b],tiles["radii_m"][b+1],
                start,start+30,.01,math.tan(math.radians(50)))
        newparts.append(record(pane,f"dry:crown_pane_{j+1:02d}",
                               "nonpressure ceramic",RHO_CERAMIC))
    # The closed 27g/cm2 Strata sheet is a separate OPERATING STATE.
    # Render file supplies 0.1m / 2700kg/m3 illustrative equivalent.
    gorearea=cfg["shell_option_c"]["gores"]["full_closed_outer_area_m2"]
    gore_m=gorearea*GORE_T*RHO_STRATA
    # Surface-weighted centre on flat-to-2m and 50deg annulus, not
    # fabrication-grade seam geometry.
    flat=math.pi*2**2
    slope=(math.pi*(rr**2-2**2))/math.cos(math.radians(50))
    avg_r=2/3*(rr**3-2**3)/(rr**2-2**2)
    gore_x=(flat*(-1.2)+slope*(-1.2+(avg_r-2)*math.tan(math.radians(50))))/(flat+slope)
    newparts.append(dict(id="dry:crown_gore_closed_coverage",
      material="Strata 2700kg/m3, render-equivalent closed 0.10m",
      volume_m3=gorearea*GORE_T,density_t_m3=RHO_STRATA,
      mass_t=gore_m,centroid_m=[gore_x,0,0],
      method="rendered exterior coverage equivalent, NOT 16 physical shutter BReps",
      modeling_hold=True))
    # Render layer: simple envelope for 16 tambour meridian tracks.
    # Equivalent-area round section = 0.04m width × 0.10m depth.
    start=1.15
    def xp(r):
        return base-(base-opt["backup_apex_x_m"])*math.sqrt(1-(r/4.3)**2)
    def xo(r):return -1.2+max(0,r-2)*math.tan(math.radians(50))
    rad=math.sqrt(TRACK_WIDTH*TRACK_DEPTH/math.pi)
    for j in range(16):
        th=j*math.pi/8
        p0=[(xp(start)+xo(start))/2,start*math.cos(th),start*math.sin(th)]
        p1=[(xp(rr)+xo(rr))/2,rr*math.cos(th),rr*math.sin(th)]
        shape=P.tube(dict(k="tube",p0=p0,p1=p1,r=rad))
        newparts.append(record(shape,f"dry:crown_tambour_track_{j+1:02d}",
             "Osteon titanium envelope, not proven track hardware",RHO_TITANIUM))
    # Two inspected spare rack options. New mass from BRep type volumes,
    # not larger clearance envelope volume.
    options=[]
    for option in s["options"]:
        sp=[dict(id=q["id"],mass_t=q["mass_t"],centroid_m=q["centroid_m"]) for q in option["pane_envelopes"]]
        moment=oldmoment[:]
        for old in removed:mod_moment(moment,old["mass_t"],old["centroid_m"],-1)
        for p in newparts:mod_moment(moment,p["mass_t"],p["centroid_m"],1)
        for p in sp:mod_moment(moment,p["mass_t"],p["centroid_m"],1)
        mass=old_dry-sum(p["mass_t"] for p in removed)+sum(p["mass_t"] for p in newparts)+sum(p["mass_t"] for p in sp)
        cg=[k/mass for k in moment]
        six=[]
        for name,ve in i["canon"]["torch_ve_km_s"].items():
            oldM=g["states"]["S1"]["mass_t"]
            newM=oldM+(mass-old_dry)
            remass=i["states"]["S1"]["remass_t"]
            oldDv=ve*math.log(oldM/(oldM-remass))
            newDv=ve*math.log(newM/(newM-remass))
            six.append(dict(mode=name,ve_km_s=ve,old_dv_km_s=oldDv,new_dv_km_s=newDv,
                            delta_dv_km_s=newDv-oldDv))
        states=[]
        for name,state in g["states"].items():
            states.append(dict(state=name,old_mass_t=state["mass_t"],
               new_mass_t=state["mass_t"]+mass-old_dry,
               old_cg_m=state["cg_m"],
               new_cg_m=[(state["mass_t"]*state["cg_m"][k]+moment[k]-oldmoment[k]) /
                    (state["mass_t"]+mass-old_dry) for k in range(3)]))
        options.append(dict(label=option["label"],spare_rack=option["x_m"],
         new_total_dry_t=mass,net_dry_mass_delta_t=mass-old_dry,
         dry_cg_before_m=[v/old_dry for v in oldmoment],dry_cg_after_m=cg,
         dry_cg_delta_m=[cg[k]-oldmoment[k]/old_dry for k in range(3)],
         six_mode_dv=six,state_mass_cg=states,
         seven_spares_total_t=sum(p["mass_t"] for p in sp),
         seven_spares_zero_clashes=option["zero_clashes"]))
    out=dict(source_sha256=SHA,authorization="kT SOLIDS GOVERN",
       result_class="PHYSICAL_MASS_SCREEN_NOT_GOVERNING_SOURCE",
       old_dry_t=old_dry,retired=removed,
       physical_new_parts=newparts,existing_conservative_AOI_t=cfg["adaptive_optogel"]["mass_t"],
       AOI_declared_volume_m3=cfg["adaptive_optogel"]["volume_m3"],
       AOI_true_cavity_m3=float(gel.volume),
       unchanged_retainer_booked_t=by["crown_c_outward_retainers"]["mass_t"],
       titanium_density_assumption_t_m3=RHO_TITANIUM,
       strata_render_density_t_m3=RHO_STRATA,
       full_coverage_gore_state="closed only; density/mass is source area-times-render-thickness, physically detailed BRep OPEN",
       options=options)
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    for q in options:
        print("CROWN_SOLID_MASS",json.dumps({k:q[k] for k in
         ("label","new_total_dry_t","net_dry_mass_delta_t","dry_cg_before_m","dry_cg_after_m","dry_cg_delta_m")}),flush=True)
        print("CROWN_SIX_MODE_DV",json.dumps(q["six_mode_dv"]),flush=True)
if __name__=="__main__":main()
