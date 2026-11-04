#!/usr/bin/env python3
"""OG-3 nominal crown-conformal shell bands, computed from pinned parent meridian.
Known: total cavity 3.023 m³, min normal gap 59.73 mm, primary 4.3m parent,
backed by two shells. Backup MERIDIAN NOT independently supplied: interpolated
gap g(r)=g_min+a*(1-(r/rmax)^exponent) and fit a to known cavity volume.
Never call interpolation an actual measured surface. Standard-library only.
"""
import json,math,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"wayfarer/config/og3_hydra.json"
I_P=ROOT/"wayfarer/config/wayfarer_v05_inputs.json"
O=json.loads(P.read_text());I=json.loads(I_P.read_text())
C=I["habitat"]["decks"][0]["command_layout"]["crown_dome"]
D=C["shell_option_c"]["deep_pressure_domes"]
A=C["adaptive_optogel"]
G=O["crown_conformal"]
rmax=C["panes"]["inner_radius_m"]
rparent=D["parent_radius_m"]
depth=D["parent_depth_m"]
bound=C["panes"]["ring_boundaries_m"]
min_gap=A["min_local_free_normal_thickness_m"]
volume=A["volume_m3"]
old_mass=G["original_crown_interlayer_mass_t"]
skin=O["skin"]
bulk=O["bulk"]
rho_skin=skin["assumed_density_kg_m3"]
rho_bulk=bulk["assumed_density_kg_m3"]
skin_t=skin["thickness_m"]
n=int(G["integration_steps_per_zone"])
exp=G["normal_gap_profile_exponent"]
# Source area of true normal dome surface from its meridian.
def dpdr(r):
    return depth*r/(rparent*rparent*math.sqrt(1-(r/rparent)**2))
def dist_factor(r):return 1-(r/rmax)**exp
def integration(a,b):
    h=(b-a)/n
    # uniform midpoint integration avoids endpoint r≈0 and numerical derivative instability
    area=weighted=0.
    for i in range(n):
        r=a+(i+.5)*h
        dA=2*math.pi*r*math.sqrt(1+dpdr(r)**2)*h
        area+=dA
        weighted+=dA*dist_factor(r)
    return area,weighted
zones_base=[integration(a,b) for a,b in zip(bound,bound[1:])]
area=sum(x[0] for x in zones_base)
W=sum(x[1] for x in zones_base)
central_excess=(volume-min_gap*area)/W
assert central_excess>=0, "cavity volume too small to preserve minimum gap"
zones=[]
for k,((ra,rb),(ar,wm)) in enumerate(zip(zip(bound,bound[1:]),zones_base)):
    vol=min_gap*ar+central_excess*wm
    skin_vol=ar*skin_t
    gel_vol=vol-skin_vol
    assert gel_vol>0
    t_skin=skin_vol*rho_skin/1000
    t_bulk=gel_vol*rho_bulk/1000
    mass=t_skin+t_bulk
    zones.append({"id":f"crown_ring_{k}","radial_bounds_m":[ra,rb],
     "surface_area_m2":round(ar,9),
     "normal_gap_min_m":round(min_gap+central_excess*dist_factor(rb),9),
     "normal_gap_max_m":round(min_gap+central_excess*dist_factor(ra),9),
     "normal_gap_area_mean_m":round(vol/ar,9),
     "total_interspace_volume_m3":round(vol,9),
     "gel_bulk_volume_m3":round(gel_vol,9),
     "aoi_skin_mass_t":round(t_skin,9),
     "bulk_mass_t":round(t_bulk,9),
     "total_hydra_mass_t":round(mass,9),
     "hydra_areal_kg_m2":round(mass*1000/ar,9),
     "open_total_wws_g_cm2":round((O["shield_areal"]["outer_bumper_kg_m2"]+
        O["shield_areal"]["primary_pressure_pane_kg_m2"]+
        O["shield_areal"]["backup_pressure_pane_kg_m2"]+mass*1000/ar)/
        O["shield_areal"]["areal_kg_m2_per_g_cm2"],9),
     "closed_total_wws_g_cm2":round((O["shield_areal"]["outer_bumper_kg_m2"]+
        O["shield_areal"]["primary_pressure_pane_kg_m2"]+
        O["shield_areal"]["backup_pressure_pane_kg_m2"]+
        O["shield_areal"]["shutter_closed_kg_m2"]+mass*1000/ar)/
        O["shield_areal"]["areal_kg_m2_per_g_cm2"],9)})
new_mass=sum(z["total_hydra_mass_t"] for z in zones)
delta=new_mass-old_mass
if G.get("zones"):
    # Repeatable verification; the initial capture already debited the reserve.
    assert abs(A["mass_t"]-new_mass)<1e-7
    assert abs(G["crown_mass_delta_t"]-delta)<1e-7
    assert abs(I["ledger"]["engineering_reserve_t"]-(G["original_engineering_reserve_t"]-delta))<1e-7
    assert I["og3_hydra"]["sha256"]==hashlib.sha256(P.read_bytes()).hexdigest()
    assert all(abs(a["hydra_areal_kg_m2"]-b["hydra_areal_kg_m2"])<1e-8 for a,b in zip(zones,G["zones"]))
    print(json.dumps({"mode":"VERIFY_EXISTING_CONFORMAL_PROFILE","status":"PASS","crown_mass_t":new_mass,"source_geometry":"INTERPOLATED, backup exact profile OPEN","reserve_after_t":I["ledger"]["engineering_reserve_t"]},indent=2))
    sys.exit(0)
# O(1e-5) base volume accuracy and min true source.
assert abs(sum(z["total_interspace_volume_m3"] for z in zones)-volume)<1e-7
assert abs(area-C["panes"]["inner_area_m2"])<2e-5
assert min(z["normal_gap_min_m"] for z in zones)>=min_gap-1e-8
assert I["ledger"]["engineering_reserve_t"]>=G["original_engineering_reserve_t"]-1e-7
assert abs(A["mass_t"]-old_mass)<1e-7
assert abs(I["ledger"]["aoi_crown_t"]-G["original_aoi_crown_ledger_t"])<1e-7
# Treat the source's 120mm axial offset as inconsistent metadata, not profile derivation.
G.update({
"radial_boundaries_m":bound,
"parent_radius_m":rparent,"parent_depth_m":depth,"radius_m":rmax,
"cavity_volume_m3":volume,"min_normal_gap_m":min_gap,
"normal_gap_profile_exponent":exp,
"fitted_centre_gap_excess_m":round(central_excess,12),
"fitted_centre_normal_gap_m":round(min_gap+central_excess,12),
"surface_area_model_m2":round(area,9),
"skin_total_mass_t":round(sum(z["aoi_skin_mass_t"] for z in zones),9),
"bulk_total_mass_t":round(sum(z["bulk_mass_t"] for z in zones),9),
"conformal_total_mass_t":round(new_mass,9),
"crown_mass_delta_t":round(delta,9),
"zones":zones,
"geometry_status":"INTERPOLATED CONFORMAL DESIGN APPROXIMATION, not measured backup pressure surface; canonical 120mm axial offset conflicts with declared volume and normal minimum; physical fit remains OPEN",
"crown_axial_offset_metadata_m":A["backup_dome_forward_axial_offset_m"],
"uncommitted_1p04t_option_preserved":True,
"not_an_historical_full_hull_validation":True
})
# Recompute pin, update exactly one existing crown physical mass and both ledger
# debit and source reporting. No new extra or speculative armour credit.
A["mass_t"]=round(new_mass,9)
A["volume_m3"]=volume
A["density_kg_m3"]=round(new_mass*1000/volume,9) # EFFECTIVE source bulk+skin, not homogeneous material
A["density_note"]="EFFECTIVE total of OG3 bulk + 2mm skin divided by source cavity volume. True bulk density remains in og3_hydra.json"
A["conformal_profile_note"]="Source-pinned og3_hydra.json, zones; 120mm axial offset versus observed min and volume underconstrained: profile is declared design interpolation, not measured surface."
L=I["ledger"]
L["engineering_reserve_t"]=round(G["original_engineering_reserve_t"]-delta,9)
L["aoi_crown_t"]=round(G["original_aoi_crown_ledger_t"]+delta,9)
L["og3_crown_conformal_bookkeeping"]={"old_booked_interlayer_mass_t":old_mass,"new_booked_interlayer_mass_t":round(new_mass,9),"physical_mass_delta_t":round(delta,9),
"engineering_reserve_before_t":G["original_engineering_reserve_t"],"engineering_reserve_after_t":L["engineering_reserve_t"],
"released_structure_after_t":L["structure_split"]["released_to_reserve"],
"combined_uncommitted_after_t":round(L["engineering_reserve_t"]+L["structure_split"]["released_to_reserve"],9),
"protected_uncommitted_deep_gel_option_t":O["crown_fit"]["unspent_deep_gel_option_t"],
"no_deep_gel":True,"mass_total_invariant":"new physical gel mass displaces exact same amount of preexisting engineering reserve; dry mass unchanged"}
O["crown_fit"]["conformal_fit_report"]="crown_conformal zones: interpolated surface fitting known min and known cavity volume; actual backup shell surface not independently defined"
O["crown_fit"]["bulk_plus_skin_equivalent_column_m"]=round(volume/area,9)
O["crown_fit"]["minimum_local_gap_m"]=min_gap
O["crown_fit"]["original_uniform_column_assumption"]="RETIRED for crown; side WWS panes remain nominal 66.611712004 kg/m2"
O["crown_fit"]["material_budget_status"]="mass delta source-booked to engineering reserve; no deep gel 1.04t touched"
O["shield_areal"]["crown_zone_open_g_cm2"]=[z["open_total_wws_g_cm2"] for z in zones]
O["shield_areal"]["crown_zone_closed_g_cm2"]=[z["closed_total_wws_g_cm2"] for z in zones]
O["shield_areal"]["crown_gcr_dose_credit"]=0
O["shield_areal"]["crown_spe_dose_credit"]=0
O["scope"]="WWS-1 side windows fixed nominal AOI; crown OG-3 conformal zonal mass with interpolated backup geometry; physical qualification OPEN"
O["status"]="DRAFT/NON-CANON/UNQUALIFIED; kT decides merge"
P.write_text(json.dumps(O,indent=2,ensure_ascii=False)+"\n")
I["og3_hydra"]["sha256"]=hashlib.sha256(P.read_bytes()).hexdigest()
I_P.write_text(json.dumps(I,indent=1,ensure_ascii=False)+"\n")
print(json.dumps({"source_area_m2":area,"vol_m3":volume,"min_gap_m":min_gap,"centre_gap_m":min_gap+central_excess,"new_mass_t":new_mass,"delta_t":delta,
"reserve_after_t":L["engineering_reserve_t"],"combined_after_t":L["engineering_reserve_t"]+L["structure_split"]["released_to_reserve"],
"zone_areal_kg_m2":[z["hydra_areal_kg_m2"] for z in zones],"OG3_PIN":I["og3_hydra"]["sha256"]},indent=2))
