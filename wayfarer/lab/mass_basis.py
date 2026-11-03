#!/usr/bin/env python3
"""Wayfarer mass campaign Track 1 (research-only). Source-locked 292-part ledger.
Usage: python wayfarer/lab/mass_basis.py --capture [--halo-results path]
       python wayfarer/lab/mass_basis.py --verify
No mutation of authoritative ship inputs, G1-G12 criteria, or geometry.
"""
import argparse,collections,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2]
GFILE=R/"wayfarer/results/out/wayfarer_v05_geometry.json"
IFILE=R/"wayfarer/config/wayfarer_v05_inputs.json"
BFILE=R/"wayfarer/config/mass_basis.json"
REPORT=R/"wayfarer/docs/MASS_WATERFALL_2026_11_04.md"
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Each unqualified sizing category is identified explicitly. A material name
# or component allocation is not physical sizing evidence.
GOV={
"propulsion":"torch/flight thrust, thermal, remass, G2/G4/G5","plant":"Mc constitutive, 2GJ bank, cryoplant, G4/G10; physical sizing OPEN",
"thermal":"q=eps sigma A T4 with view factor, hot-loop hydraulic/heat pipe, G4",
"structure":"5g x 1.5, 250MPa stress, buckling, pressure, G5/G8",
"habitat":"habitable volume, pressure/heat, shelter G5/G6/G7",
"shuttle":"3.8m shuttle, mass and G8 clearance, 92bar pod HOLD",
"rcs":"torque, available manoeuvre impulse, one-cluster-out G3/G9/G10",
"service":"pressure-tight transfer and separation, G8/G9",
"drones":"payload/hold fit, G8",
"mission":"payload operations/courier hold, G8",
"avionics":"control/data/redundancy, G7/G9",
"electrical":"house reactor peak stores, electrical allocation, G4/G9",
"external":"clearance vs windows and arm/rails, G5/G9",
}
CANON_PROTECTED={"armor","pressure_vessel","shield","shuttle","crown_backup_pressure_dome","crown_adaptive_optogel","hotfin_40","hotfin_140","hotfin_220","hotfin_320"}
CANON_LEDGER={
"armor":"ledger.armor_fixed_shield_t",
"shield":"ledger.propulsion_split.shield",
"reactor":"ledger.propulsion_split.reactor",
"nozzle":"ledger.propulsion_split.nozzle",
"shuttle":"shuttle.dry_t",
"manifold":"ledger.thermal_radiators_t",
"plant_fore":"ledger.relational_plant_t/2",
"plant_aft":"ledger.relational_plant_t/2",
"crown_adaptive_optogel":"habitat.decks[0].command_layout.crown_dome.adaptive_optogel.mass_t",
}
def categorize(part):
 s=part["system"]; m=part["mat"];id=part["id"]
 if id.startswith("longeron_") and "joint" not in part["tags"]:
  return ("CFRP ρ1.6t/m3, E150GPa, design stress 250MPa (source)", "tube wall physical mass rho*pi*(D²-(D-2t)²)*L/4; G5 stress screen", "PHYSICS_SIZED_INPUT")
 if m=="radiator":
  return ("1300K radiator composite, 5kg/m² assumed", "rho_areal*emitting geometry; G4 Stefan-Boltzmann", "MIXED_SIZED")
 if m=="hotfin":
  return ("1750K high-T fin, 4kg/m² face + common allowance", "2 faces*length*span*4kg/m² + mechanisms; G4", "MIXED_SIZED")
 if id=="crown_adaptive_optogel":
  return ("OG-3 conformal alkane/BNNT-H/10B-carborane +2mm AOI skin", "zone surface integrals of (gap-skin)rho_bulk+skin*rho_skin; source pinned", "DESIGN_INTERPOLATION")
 if m in ("hull_armor","shield"):
  return ("Strata MHL-22 27g/cm² or torch shadow shielding (separate)", "source areal requirement but actual particle dose OPEN", "REQUIRED_NOT_REDESIGNED")
 if m in ("pressure_hull","tank_shell","hull_skin","bulkhead"):
  return ("CFRP/metal/composite source engineering allocation", "pressure/5g structure and leak limit, section-specific FEA unresolved", "ALLOCATION_PENDING_SIZING")
 if m in ("reactor","plant","manifold"):
  return ("Declared 2226 advanced system, actual constituted physical mass UNKNOWN", "booked allocation; NO independent specific power/density/heat-transfer mass closure", "UNSIZED_ALLOCATION")
 if m in ("frame","floor","longeron"):
  return ("CFRP/titanium/2226 joint material per authored source", "source geometry mass allowance; joint+structural FEA partly OPEN", "PARTIAL_GEOMETRY")
 return (part["mat"]+" (per source, no invented alloy)", "source-booked mass: governing case not independently dimensioned", "UNSIZED_OR_ASSUMED")
def direct_screens(I):
 m=I["materials"];l=I["longerons"];r=I["radiators"];h=I["hot_fins"]
 t=l["items"][0];d=t["d_m"];w=t["wall_m"];length=l["x_m"][1]-l["x_m"][0]
 area=math.pi*(d*d-(d-2*w)**2)/4
 longeron=area*length*len(l["items"])*m["cfrp_density_t_m3"]
 panel=len(r["azimuths_deg"])*(r["x_m"][1]-r["x_m"][0])*r["max_span_m"]*r["areal_kg_m2"]/1000
 hotfin=2*len(h["azimuths_deg"])*(h["x_m"][1]-h["x_m"][0])*h["pleat_m"]*h["pleats"]*h["kg_per_m2_face"]/1000+h["allowance_t"]
 return [
 {"screen":"longeron CFRP source tube solids, before spread reserves/joint loads","calculated_t":longeron,"ledger_t":I["ledger"]["structure_split"]["longerons"],"interpretation":"Independent geometric material screen; longeron joints/ring growth are distinct, G5 stress separate"},
 {"screen":"radiator 1300K deployed panel areal basis","calculated_t":panel,"ledger_t":I["ledger"]["radiator_panels_t"],"interpretation":"Matches one-sided kg/m2 panel material, not full 90t thermal manifold"},
 {"screen":"1750K hotfin panel + folding support","calculated_t":hotfin,"ledger_t":I["ledger"]["torch_hot_fins_t"],"interpretation":"Two radiating faces per fin and 4t deployment/support allocation; lifetime unqualified"}]
def build_capture(G,I,halo):
 p=G["parts"];names=[q["id"] for q in p]
 assert len(names)==len(set(names))
 reserve=I["ledger"]["engineering_reserve_t"]+I["ledger"]["structure_split"]["released_to_reserve"]
 non=sum(q["mass_t"] for q in p if "from_reserve" not in q["tags"])
 assert non>reserve
 fac=non/(non-reserve)
 records=[]
 for q in p:
  material,rule,sizing=categorize(q)
  spread=0 if "from_reserve" in q["tags"] else q["mass_t"]*(1-1/fac)
  physical=q["mass_t"]-spread
  records.append({"id":q["id"],"name":q["name"],"system":q["system"],
   "material":material,"mat_source_code":q["mat"],
   "mass_from_geometry_t":round(q["mass_t"],9),
   "physically_allocated_without_spread_reserve_t":round(physical,9),
   "embedded_spread_uncommitted_reserve_t":round(spread,9),
   "sizing_rule":rule,"sizing_status":sizing,
   "governing_case":GOV.get(q["system"],"Check source G1–G12"),
   "source":"wayfarer/results/out/wayfarer_v05_geometry.json::parts["+q["id"]+"]",
   "source_provenance":q["prov"],
   "canon_or_protected":q["id"] in CANON_PROTECTED or q["mat"] in ("hull_armor","shield"),
   "canon_line_if_mapped":CANON_LEDGER.get(q["id"]),
   "tags":q["tags"],"radiation_credit":"ZERO for reserve growth, NO unmeasured GCR/SPE dose credit"})
 free=reserve-16.8
 return {"status":"TRACK1 RESEARCH, source-locked, NO ship/runtime/canon mutation; no speculative saving credited",
  "date":"2026-11-04","input_sha256":sha(IFILE),"geometry_sha256":sha(GFILE),
  "source_dry_t":G["dry_t"],"S1_mass_t":G["states"]["S1"]["mass_t"],
  "S1_remass_t":I["states"]["S1"]["remass_t"],"ECON_ve_km_s":I["canon"]["torch_ve_km_s"]["ECON"],
  "current_engineering_reserve_t":I["ledger"]["engineering_reserve_t"],
  "current_released_structural_t":I["ledger"]["structure_split"]["released_to_reserve"],
  "combined_uncommitted_t":reserve,"combined_uncommitted_floor_t":16.8,
  "free_buffer_above_floor_t":free,"allocated_growth_spread_factor":fac,
  "direct_physics_screens":direct_screens(I),"parts":records,
  "halo_cases_Je1000":[{"BL_Tm":q["BL_Tm"],"mass_t":q["optimistic_mass_t"],"required_verified_stripdown_t":max(0,q["optimistic_mass_t"]-free),
                         "optimistic_reach_penalty_km_s":q["reach_lost_km_s"]} for q in halo["Je_sweep"] if q["baseline"]]}
def report(B,G,I):
 p=B["parts"]
 sum_p=sum(x["mass_from_geometry_t"] for x in p)
 assert abs(sum_p-G["dry_t"])<2e-6
 sum_spread=sum(x["embedded_spread_uncommitted_reserve_t"] for x in p)
 assert abs(sum_spread-B["combined_uncommitted_t"])<1e-6
 cf=I["canon"];M=B["S1_mass_t"];rem=B["S1_remass_t"];ve=B["ECON_ve_km_s"]
 marginal=ve*((M-rem)**-1-M**-1)
 l=["# Wayfarer MASS CAMPAIGN — Track 1, ledger to physics","",
 "ALL bodies. ALL sponsors. 2026–2226.",
 "",
 "**RESEARCH / DRAFT / NON-CANON / NON-RUNTIME / NO MERGE. kT decides.**",
 "",
 f"**Geometry SHA** `{B['geometry_sha256']}`. **Dry mass {G['dry_t']:.6f}t**, {len(p)} individual parts. Ledger-to-parts sum **{sum_p:.6f}t**, discrepancy {sum_p-G['dry_t']:+.9f}t.",
 "",
 f"**Critical distinction:** source builder spreads **{B['combined_uncommitted_t']:.6f}t** of still-uncommitted engineering/released-structure growth mass into the non-`from_reserve` dry parts with factor **{B['allocated_growth_spread_factor']:.6f}**. The booked pre-spread baseline for each line EXCLUDES that spread, but it is NOT a physically qualified mass. **Do not count those tonnes as already earned weight savings and then use them again to fund Halo.**",
 "",
 f"ECON local sensitivity for 1t near S1: **~{marginal:.3f}km/s recovered per tonne truly removed** (exact small-perturbation derivative, not route optimization). The shorthand 0.69km/s/t is sound near the current S1.",
 "",
 "## Three independent source sizing calculations (others remain stated allocations)","",
 "| Governing calculation | Direct mass t | Ledger before spread t | Delta t | Status |","|---|---:|---:|---:|---|"]
 for sc in B["direct_physics_screens"]:
  diff=sc["calculated_t"]-sc["ledger_t"]
  l.append(f"| {sc['screen']} | {sc['calculated_t']:.4f} | {sc['ledger_t']:.4f} | {diff:+.4f} | {sc['interpretation']} |")
 l+=["","These are direct **mass sizing** arithmetic checks, not a substitute for pressure, stress, radiation or heat rejection qualification. Reevaluate all critical G1–G12 physics for any accepted part change.",
 "","## Ranked source allocations before uncommitted reserve spread","","| Rank | Part | Booked pre-spread t | Embedded uncommitted reserve t | Current geometry total t | Sizing status | Protected/canon? |","|---:|---|---:|---:|---:|---|---|"]
 ranked=sorted(p,key=lambda z:-z["physically_allocated_without_spread_reserve_t"])
 for i,q in enumerate(ranked[:32],1):
  l.append(f"| {i} | `{q['id']}` | {q['physically_allocated_without_spread_reserve_t']:.3f} | {q['embedded_spread_uncommitted_reserve_t']:.3f} | {q['mass_from_geometry_t']:.3f} | {q['sizing_status']} | {'YES' if q['canon_or_protected'] else 'review'} |")
 l+=["",f"Full {len(p)}-part record, explicit material classification, governing sizing requirement, provenance/source, identified canon lines and reserve distribution are in [mass_basis.json](../config/mass_basis.json). Rows without a quantitative sizing law are marked as **unsized allocations**, not material facts.",
 "","## How much actual strip-down buys 10–20Tm Halo?","","| Halo case at Je1000 | Optimistic installed mass | Already free above 16.8t floor | **Verified additional mass saving required** | ECON reach cost if simply added |","|---:|---:|---:|---:|---:|"]
 for q in B["halo_cases_Je1000"]:
  l.append(f"| {q['BL_Tm']}Tm | {q['mass_t']:.3f}t | {B['free_buffer_above_floor_t']:.3f}t | **{q['required_verified_stripdown_t']:.3f}t** | {q['optimistic_reach_penalty_km_s']:.2f}km/s |")
 l+=["",
 "### One testable **allocation target**, not an asserted saving",
 "",
 "| Suspect ledger source | Hypothetical requested saving | Fraction of present pre-spread booked allocation | What must be shown |","|---|---:|---:|---|"]
 tests=[("manifold",10.0,"G4: thermal loop/pump/coolant mass from heat transfer and pressure, not bare radiators"),
        ("plant_fore",4.5,"G4/G10: compact Mc/metric hardware constitutive model"),
        ("plant_aft",4.5,"G4/G10: mirrored plant physics and redundancy closure"),
        ("reactor",8.0,"G2/G4/G5: torch reactor actual mass from specific power and shield interfaces"),
        ("tank_shell_out",2.0,"G5: tank/carrying-shell pressure, 5g buckling and double-duty"),
        ("tank_shell_in",2.0,"G5/G6: internal tank shell and radiation-water preservation")]
 for id,target,note in tests:
  q=next(z for z in p if z["id"]==id)
  l.append(f"| `{id}` | {target:.2f}t | {target/q['physically_allocated_without_spread_reserve_t']*100:.1f}% | {note} |")
 total=sum(x[1] for x in tests)
 l+=["",f"This **{total:.2f}t counterfactual package** would cover a 20Tm Halo's ~30.7t funding gap on paper, but **ZERO t is currently verified or credited**. Even one rejected component replacement unbalances the target. It cannot become ship mass until the indicated sizing calculations and G1–G12 checks pass.",
 "",
 "The most valuable first experiment is **manifold ~90t pre-spread:** reconstruct coolant duty, pressure drop, line length/radius, pump and material mass. If it genuinely requires ~90t, eliminate its alleged 10t saving and move on. The Mc plant is not discountable merely because it is futuristic.",
 "",
 "## Hard holds",
 "",
 "- No passive armour removal; no GCR dose discount for OG-3 or Halo; maintain shelter ZERO windows and 208 Metric faces.",
 "- No cuts to habitat volume or 50t protected water; no new pressure-body, thermal, bay clearance or payload loss.",
 "- Engineering reserve >=5t, combined uncommitted >=16.8t after any mass reallocation; WWS 12t NEW draw stays tracked separately.",
 "- **No part has an earned saving yet.** This is an inventory plus first physically testable design question, not a canon redesign.",
 "- Keep historical and proposed materials separate; kT decides merges.",""]
 REPORT.write_text("\n".join(l)+"\n")
 return marginal
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--capture",action="store_true")
 a.add_argument("--verify",action="store_true")
 a.add_argument("--halo-results",type=Path)
 opt=a.parse_args()
 assert opt.capture!=opt.verify,"choose exactly one --capture or --verify"
 G=read(GFILE);I=read(IFILE)
 if opt.capture:
  assert opt.halo_results is not None and opt.halo_results.exists()
  B=build_capture(G,I,read(opt.halo_results))
  BFILE.write_text(json.dumps(B,indent=2)+"\n")
 else:
  B=read(BFILE)
  assert B["input_sha256"]==sha(IFILE) and B["geometry_sha256"]==sha(GFILE),"SOURCE DRIFT - refresh capture before any claims"
  byid={q["id"]:q for q in G["parts"]}
  assert len(B["parts"])==len(byid)
  differences=[(x["id"],x["mass_from_geometry_t"]-byid[x["id"]]["mass_t"]) for x in B["parts"] if x["id"] not in byid or abs(x["mass_from_geometry_t"]-byid[x["id"]]["mass_t"])>2e-8]
  assert not differences,differences[:8]
 marginal=report(B,G,I)
 print(json.dumps({"status":"PASS SOURCE LOCK","dry_t":G["dry_t"],"parts":len(B["parts"]),"spread_uncommitted_t":B["combined_uncommitted_t"],"source_sha":B["geometry_sha256"],"reach_km_s_per_t":marginal,"halo_targets":B["halo_cases_Je1000"]},indent=2))
if __name__=="__main__": main()
