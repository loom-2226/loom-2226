#!/usr/bin/env node
/**
 * LOOM shuttle sizer v1. One input JSON, one report, two SVGs; no runtime or canon edits.
 * Geometry and physical inputs are read from JSON. Numeric literals below are
 * mathematical identities (0, 1, 2, pi), not hardcoded vehicle data.
 * Run: node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage 1
 *      node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage 2
 */
function val(o) { return o && typeof o.value === "number" ? o.value : null; }
function band(o) { return o && typeof o.min === "number" && typeof o.max === "number" ? [o.min,o.max] : null; }
function endpoints(o) { const b=band(o); return b?[b[0],(b[0]+b[1])/2,b[1]]:null; }
function formatted(n,p) { return n===null||!Number.isFinite(n)?"OPEN":n.toFixed(p); }
function get(obj,path) { return path.split(".").reduce((a,k)=>a&&a[k],obj); }
function xml(s) { return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
function hover(massT,density,g,diameter,fm,thermalEfficiency,kgPerT) {
  const area=Math.PI*(diameter/2)**2;
  const force=massT*kgPerT*g;
  const ideal=force*Math.sqrt(force/(2*density*area));
  return {disk:area,force,idealMW:ideal/(kgPerT*kgPerT),rotorMW:ideal/fm/(kgPerT*kgPerT),sourceMW:ideal/fm/thermalEfficiency/(kgPerT*kgPerT)};
}
function limits(d) {
  const g=d.geometry, si=d.si, m=d.mass, rotorDiameter=val(g.rotor_diameter_m);
  const length=val(g.bay_x_end_m)-val(g.bay_x_start_m);
  const vesselLength=val(g.hull_length_m), vesselDiameter=val(g.hull_diameter_m);
  const allowableLength=length-2*val(g.g8_min_axial_clearance_m);
  const allowableDiameter=2*(val(g.bay_bore_radius_m)-val(g.g8_min_radial_clearance_m));
  const fwd=val(g.rotor_blades_fwd),aft=val(g.rotor_blades_aft),count=val(g.rotor_blades);
  const foldedSpan=rotorDiameter/2+rotorDiameter/2;
  const shell=band(m.pressure_pod_titanium_shell_t);
  const dryMax=val(m.max_docked_dry_t);
  const components=Object.entries(m).filter(([k])=>k!=="max_docked_dry_t"&&k!=="v1_comparison_dry_t");
  const unresolved=components.filter(([,q])=>val(q)===null&&!band(q)).map(([k])=>k);
  const tolerance=Number.EPSILON*Math.max(allowableLength,vesselLength)*2;
  const fittedDimensional=(vesselLength<=allowableLength+tolerance && vesselDiameter<=allowableDiameter+tolerance && foldedSpan<=vesselLength+tolerance && fwd+aft===count);
  return {length,allowableLength,allowableDiameter,vesselLength,vesselDiameter,
   foldedSpan,remainingRotorSpan:vesselLength-foldedSpan,
   radialMargin:Math.abs(allowableDiameter-vesselDiameter)<=tolerance?0:allowableDiameter-vesselDiameter,axialMargin:Math.abs(allowableLength-vesselLength)<=tolerance?0:allowableLength-vesselLength,
   shell,shellMid:(shell[0]+shell[1])/2,dryMax,
   massOtherBudget:[dryMax-shell[1],dryMax-shell[0]],unresolved,
   dimensionalNecessaryGate:fittedDimensional?"PASS_NECESSARY_ONLY":"FAIL",
   gateA:"OPEN", gateB:fittedDimensional?"OPEN":"FAIL",
   packOpen:["mast_stowed_extra_diameter_m","hub_axial_length_m","mast_retracted_height_m","rotor_mast_x_m","crew_pod_x_m"].filter(k=>val(g[k])===null),
   constraints:{
     mass:"sum(all unique dry components) <= max_docked_dry_t",
     fit:"outer stowed hardware <= allowable diameter and length including hub, blade roots, mast, ramp, doors; no overlap"
   }};
}
function stage2(d) {
  const si=d.si, g=d.geometry, v=d.venus, p=d.power, t=d.thermal, w=d.water;
  const kgPerT=val(si.kg_per_t),points=[];
  const masses=endpoints(v.rotor_mass_screen_t),fms=endpoints(p.rotor_figure_of_merit),etas=endpoints(p.tipjet_thermal_to_useful_rotor);
  const combos=[];
  for(const m of masses) for(const fm of fms) for(const e of etas) combos.push({mass_t:m,figure_of_merit:fm,tip_eff:e});
  for(const a of v.atmosphere_profile) {
    const q=combos.map(s=>({...s,...hover(s.mass_t,a.density_kg_m3,val(v.gravity_mps2),val(g.rotor_diameter_m),s.figure_of_merit,s.tip_eff,kgPerT)}));
    const min=k=>Math.min(...q.map(x=>x[k])),max=k=>Math.max(...q.map(x=>x[k]));
    points.push({altitude_km:a.altitude_km,temperature_K:a.temperature_K,pressure_bar:a.pressure_bar,density_kg_m3:a.density_kg_m3,
       rotor_MW:[min("rotorMW"),max("rotorMW")],tipjet_thermal_MW:[min("sourceMW"),max("sourceMW")]});
  }
  const podR=val(g.crew_pod_outer_diameter_m)/2;
  const hot=band(t.venus_external_surface_K),k=band(t.insulation_k_W_per_mK),th=band(t.insulation_thickness_m);
  const cold=val(t.cabin_target_K),A=4*Math.PI*podR*podR;
  const leakMin=k[0]*A*(hot[0]-cold)/th[1],leakMax=k[1]*A*(hot[1]-cold)/th[0];
  const secs=val(si.seconds_per_hour), target=val(t.stay_requested_h);
  const kWhFactor=val(si.joules_per_kWh);
  const energyKWh=[leakMin,leakMax].map(z=>z*target*secs/kWhFactor);
  const phaseNames=["entry","rotor deploy","rotor descent","touchdown","surface stay","rotor climb","rotor-to-torch handover","torch ascent to orbit"];
  const phases=phaseNames.map(name=>({phase:name,water_start:"OPEN",water_reaction_delta:"OPEN",thermal_water_delta:"OPEN",reactor_heat:"OPEN",capsule:"ONBOARD/OPEN",post_state:"OPEN"}));
  // Conditional claim ONLY: ambient-gas lift may avoid tank-water use in rotor phase;
  // ZERO from the #453 PROJECTION is not upgraded to physical qualification.
  for (const ph of phases) if(["rotor descent","rotor climb"].includes(ph.phase))
    ph.water_reaction_delta="0 CONDITIONAL tipjet ambient CO2; source/engine not closed";
  return {combinations:combos.length,profile:points,phases,leak_W:[leakMin,leakMax],leak_energy_kWh:energyKWh,
    entry:"OPEN",handover_altitude_km:null,handover_reason:"rotor thermal power limit, safe blade tip speed and climb performance are OPEN",
    torch:"OPEN: engine thrust, ascent trajectory, burn time and actual remass manifest",
    gateC:"OPEN", gateD2:"OPEN",gateD4:"OPEN",
    reasonC:"No phase-complete propellant accounting, thermal powerplant, altitude handover, aero forces or delta-v trajectory.",
    reasonD:"Cold-water mass, temperature span, heat capacity, crew heat, cooling power and hot-side sink OPEN.",
    historicalV1TouchdownDebit_t:val(w.v1_venus_touchdown_belly_debit_t),
    historicalV1PostBurnRemaining_t:val(w.v1_after_all_burns_remaining_t)};
}
function sideSVG(d,r) {
 const px=val(d.sweep.svg_pixels_per_meter),pad=val(d.sweep.svg_margin_px),
  len=r.vesselLength, dia=r.vesselDiameter,barH=dia*px,w=len*px+pad*2,h=barH+pad*3,
  x=pad,y=pad+barH/2,rot=val(d.geometry.rotor_diameter_m),hub=x+len*px/2,top=y-dia*px/2;
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+Math.ceil(w)+'" height="'+Math.ceil(h)+'" viewBox="0 0 '+Math.ceil(w)+' '+Math.ceil(h)+'">'+
 '<rect width="100%" height="100%" fill="#111927"/><text x="'+pad+'" y="27" font-size="15" fill="#f8fafc">SHUTTLE · SCALE SIDE ENVELOPE · NOT A PACKAGING CERTIFICATE</text>'+
 '<rect x="'+x+'" y="'+top+'" width="'+(len*px)+'" height="'+barH+'" rx="'+(dia*px/3)+'" fill="#25364a" stroke="#9fd5ff" stroke-width="2"/>'+
 '<line x1="'+(hub-rot*px/2)+'" y1="'+y+'" x2="'+(hub+rot*px/2)+'" y2="'+y+'" stroke="#ffc875" stroke-width="5"/>'+
 '<circle cx="'+hub+'" cy="'+y+'" r="8" fill="#ffc875"/>'+
 '<text x="'+(hub+14)+'" y="'+(y-12)+'" fill="#ffc875" font-size="12">12m folded blade span; hub at CG OPEN</text>'+
 '<line x1="'+x+'" y1="'+(top+barH+24)+'" x2="'+(x+len*px)+'" y2="'+(top+barH+24)+'" stroke="#b8dfeb"/>'+
 '<text x="'+hub+'" y="'+(top+barH+44)+'" text-anchor="middle" fill="#f8fafc" font-size="14">'+xml(len+'m hull / G8 allowable '+r.allowableLength+'m')+'</text>'+
 '<line x1="'+(x-20)+'" y1="'+top+'" x2="'+(x-20)+'" y2="'+(top+barH)+'" stroke="#b8dfeb"/>'+
 '<text x="'+(x+10)+'" y="'+(top+17)+'" fill="#f8fafc" font-size="13">'+xml(dia+'m OD / G8 allowable '+r.allowableDiameter+'m')+'</text>'+
 '<text x="'+pad+'" y="'+(h-20)+'" fill="#ffce85" font-size="12">Pod 2.8m OD; exact longitudinal location, mast recess, hub and CG remain OPEN</text></svg>';
}
function waterfallSVG(d,r) {
 const dry=r.dryMax,lo=r.shell[0],hi=r.shell[1],p=val(d.sweep.round_decimals),W=900,H=330,pad=56,
   sx=x=>pad+x/dry*(W-2*pad), y0=110,y1=190;
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+
 '<rect width="100%" height="100%" fill="#111927"/>'+
 '<text x="50" y="34" fill="#f8fafc" font-size="18">DRY-MASS WATERFALL · KNOWN Ti SHELL ONLY</text>'+
 '<text x="50" y="60" fill="#b8cfdf" font-size="13">All other component masses OPEN: no total, no Gate A pass</text>'+
 '<rect x="'+pad+'" y="'+y0+'" width="'+(sx(dry)-pad)+'" height="25" fill="#334454"/>'+
 '<rect x="'+pad+'" y="'+y0+'" width="'+(sx(lo)-pad)+'" height="25" fill="#56a89f"/>'+
 '<rect x="'+sx(lo)+'" y="'+y0+'" width="'+(sx(hi)-sx(lo))+'" height="25" fill="#e8b85b"/>'+
 '<text x="'+pad+'" y="'+(y0-12)+'" fill="#f8fafc" font-size="14">Ti geometric shell: '+formatted(lo,p)+'–'+formatted(hi,p)+' t (PROJECTION)</text>'+
 '<rect x="'+pad+'" y="'+y1+'" width="'+(sx(dry)-pad)+'" height="25" fill="#324353"/>'+
 '<rect x="'+pad+'" y="'+y1+'" width="'+(sx(dry-hi)-pad)+'" height="25" fill="#447ac4"/>'+
 '<text x="'+pad+'" y="'+(y1-12)+'" fill="#f8fafc" font-size="14">Budget for all OTHER dry parts: '+formatted(dry-hi,p)+'–'+formatted(dry-lo,p)+' t</text>'+
 '<line x1="'+sx(dry)+'" y1="80" x2="'+sx(dry)+'" y2="254" stroke="#ef8e8e" stroke-width="2" stroke-dasharray="5 4"/>'+
 '<text x="'+sx(dry)+'" y="271" fill="#ef8e8e" font-size="14" text-anchor="end">Gate A max '+dry+' t</text>'+
 '<text x="50" y="300" fill="#b8cfdf" font-size="12">Not a component-mass total. Missing rover, torch, rotor, reactor, custody and structure.</text></svg>';
}
function report(d,stage,hash,r,v,svgNames) {
 const p=val(d.sweep.round_decimals),format=x=>formatted(x,p),lines=[];
 lines.push("# LOOM shuttle sizer v1 — Stage "+stage+" result");
 lines.push("ALL bodies. ALL sponsors. 2026-2226.");
 lines.push("");
 lines.push("**Status:** NON-CANON / NON-RUNTIME / UNQUALIFIED ENGINEERING SENSITIVITY. No machine constants promoted.");
 lines.push("**Input hash / run identity (Git blob SHA-1):** \`"+hash+"\`. Raw UTF-8 input identity is SHA-1 of \`blob <byte-length>\\\\0\` plus JSON bytes.");
 lines.push("**Single source input:** \`wayfarer/lab/shuttle/shuttle_inputs.json\` (all inputs printed at end).");
 lines.push("**Files generated:** \`"+svgNames[0]+"\`, \`"+svgNames[1]+"\`.");
 lines.push("");
 lines.push("## Gate summary");
 lines.push("| Gate | Verdict | Finding |");
 lines.push("|---|---|---|");
 lines.push("| A docked dry ≤ "+format(r.dryMax)+" t | **"+r.gateA+"** | Only Ti geometric shell range "+r.shell.map(format).join("–")+" t; "+r.unresolved.length+" other dry mass entries OPEN; no admissible total. |");
 lines.push("| B G8 bay fully fitted | **"+r.gateB+"** | Necessary hull length "+format(r.vesselLength)+" / available "+format(r.allowableLength)+"m, diameter "+format(r.vesselDiameter)+" / available "+format(r.allowableDiameter)+"m, folded span "+format(r.foldedSpan)+"m; mast/hub/hinge and actual positioning OPEN. |");
 if(stage===2) {
 lines.push("| C water ≥ 0 at Venus orbit | **"+v.gateC+"** | Reaction/thermal water and ascent trajectory incomplete. Historical v1 1.6t after burns must not be counted as newly earned. |");
 lines.push("| D 2-crew surface stay | **"+v.gateD2+"** | Thermal reservoir, crew heat and cooling hardware OPEN. |");
 lines.push("| D 4-crew surface stay | **"+v.gateD4+"** | Same omissions plus distinct 4-crew metabolism/embodiment. |");
 }
 lines.push("");
 lines.push("## Stage 1 — mass and fit");
 lines.push("**Necessary geometry:** G8 bay inner length "+format(r.length)+"m, axial clearance each end "+format(val(d.geometry.g8_min_axial_clearance_m))+"m; bore radius "+format(val(d.geometry.bay_bore_radius_m))+"m, radial clearance "+format(val(d.geometry.g8_min_radial_clearance_m))+"m. Remaining *allowable* diameter and length margins are exactly "+format(r.radialMargin)+"m and "+format(r.axialMargin)+"m. Any mast or hub exterior to the existing hull is a fit FAILURE.");
 lines.push("**Folded rotor:** four blades on one "+format(val(d.geometry.rotor_diameter_m))+"m tip-jet rotor; two fold forward and two aft. The ideal collinear span is "+format(r.foldedSpan)+"m, leaving "+format(r.remainingRotorSpan)+"m for true hinge/root/end geometry. Rotor mount over CG and crew pod station are OPEN; the side view locates neither as engineering authority.");
 lines.push("**Dry-mass components (independently conserved):**");
 lines.push("| Component | Range / value (t) | Provenance |");
 lines.push("|---|---:|---|");
 for(const [k,x] of Object.entries(d.mass)) {if(k==="max_docked_dry_t"||k==="v1_comparison_dry_t")continue;lines.push("| "+k+" | "+(band(x)?band(x).map(format).join("–"):x.value===null?"OPEN":format(val(x)))+" | "+x.provenance+" |");}
 lines.push("");
 lines.push("**Feasibility map:** 3 shell-projection samples; other masses cannot be assigned without evidence.");
 lines.push("| Ti shell assumed (t) | Remaining total budget for ALL other dry components (t) | Gate A | Gate B |");
 lines.push("|---:|---:|---|---|");
 for(const x of endpoints(d.mass.pressure_pod_titanium_shell_t))lines.push("| "+format(x)+" | "+format(r.dryMax-x)+" | OPEN | "+r.gateB+" |");
 lines.push("");
 lines.push("Necessary but insufficient condition: **sum(other component dry masses) ≤ remaining budget**; this is not an earned PASS. Capsule has ONE dry-mass row and may not be counted a second time in the custody ledger.");
 if(stage===2) {
 lines.push("");
 lines.push("## Stage 2 — Venus atmospheric and phase screen");
 lines.push("**Atmosphere:** VIRA-derived IPPW-6 table (source in JSON), tabulated rather than made-up atmosphere fit. Table points are not a continuous flight-dynamics model. **Single rotor** deployed diameter "+format(val(d.geometry.rotor_diameter_m))+"m, area "+format(Math.PI*(val(d.geometry.rotor_diameter_m)/2)**2)+"m². Values below are momentum-theory hover plus assumed rotor FM and tip-jet thermal effectiveness at representative **"+band(d.venus.rotor_mass_screen_t).map(format).join("–")+" t**; they do NOT establish max available thermal power.");
 lines.push("| Alt km | rho kg/m³ | Temperature K | Rotor useful power MW | Tip-jet reactor heat MW |");
 lines.push("|---:|---:|---:|---:|---:|");
 for(const x of v.profile)lines.push("| "+x.altitude_km+" | "+format(x.density_kg_m3)+" | "+format(x.temperature_K)+" | "+x.rotor_MW.map(format).join("–")+" | "+x.tipjet_thermal_MW.map(format).join("–")+" |");
 lines.push("");
 lines.push("**Handover altitude = OPEN output**. A physically defensible handover requires available delivered hot-gas power, tip-jet compression/nozzle model, allowed blade rpm/Mach, bearing lifetime and net climb performance. Those inputs are OPEN, so none can be manufactured by selecting a cloud height. Even unlimited near-surface hover does NOT reach orbit.");
 lines.push("");
 lines.push("**Conserved phase ledger:**");
 lines.push("| Phase | Reaction water | Crew thermal water | Reactor heat/power | Custody capsule |");
 lines.push("|---|---|---|---|---|");
 for(const x of v.phases)lines.push("| "+x.phase+" | "+x.water_reaction_delta+" | "+x.thermal_water_delta+" | "+x.reactor_heat+" | "+x.capsule+" |");
 lines.push("");
 lines.push("The v1 pre-rotor sortie debited **"+format(v.historicalV1TouchdownDebit_t)+"t belly touchdown** and reported **"+format(v.historicalV1PostBurnRemaining_t)+"t AFTER all its planned burns**. These are assumed *historical scenario comparators*, not independent debits or a credited stage-2 water result. Atmospheric tipjets may use **zero onboard reaction water for rotor phases** only conditionally; heat/compressor power and reactor supply remain OPEN.");
 lines.push("");
 lines.push("**Thermal lower-bound envelope:** ideal spherical 2.8m shell conduction without joints, doors, penetration or convection: "+v.leak_W.map(x=>format(x/val(d.si.kW_per_MW))).join("–")+" kW at 300K interior; for 18h "+v.leak_energy_kWh.map(format).join("–")+" kWh **before any crew/equipment heat**. This alone cannot give 2-crew or 4-crew survival duration: cold thermal mass, ΔT, actual heat capacity, compressor/power/rejection hardware, and crew waste heat all OPEN.");
 lines.push("");
 lines.push("**Feasibility map:** "+v.combinations+" sampled mass/FM/tipjet-efficiency combinations × "+v.profile.length+" atmospheric levels. Power **DEMAND** is bounded in the table; **no configuration earns C or D PASS** because supply ceiling, ascent physics, and crew thermal-water ledger are OPEN. C=OPEN, D2=OPEN, D4=OPEN for every sample; no silent failures and no invented positive reserve.");
 }
 lines.push("");
 lines.push("## Inputs driving the result and provenance boundaries");
 lines.push("- A: Ti shell is the only interval-backed dry mass. Single 12m rotor mass is OPEN; #453's 1–10t *four 6m rotor* assumption is **not transferred**.");
 lines.push("- B: no dimensional clearance beyond the stated hull; hub thickness, CG, wing/mast stowage geometry unresolved.");
 if(stage===2)lines.push("- C/D: heat supply and rotor operating ceiling; rotor-to-torch handover; ascent vehicle aerodynamics, Δv, torch thrust and reaction-water load; cold-water partition; hot bearing and thermal lifetime.");
 lines.push("- Light-body access and Titan are Stage 3, not evaluated here. No modification to canon/Wayfarer geometry/Navigator.");
 lines.push("");
 lines.push("## Full hashed input JSON (verbatim)");
 lines.push("\`\`\`json");
 lines.push(JSON.stringify(d,null,2));
 lines.push("\`\`\`");
 return lines.join("\n")+"\n";
}
// CLI
import {readFileSync,writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
const path=new URL("./shuttle_inputs.json",import.meta.url);
const raw=readFileSync(path,"utf8"),data=JSON.parse(raw);
const stageArg=process.argv.indexOf("--stage");
const stage=stageArg<0?1:Number(process.argv[stageArg+1]);
if(![1,2].includes(stage))throw Error("--stage must be 1 or 2 (stage 3 requires kT review)");
const gitBlobId=createHash("sha1").update("blob "+Buffer.byteLength(raw)+"\0"+raw).digest("hex");
const geometry=limits(data),ven=stage===2?stage2(data):null;
const pReport=new URL("./SHUTTLE_SIZER_REPORT.md",import.meta.url),
 pSide=new URL("./SHUTTLE_SIDE_VIEW.svg",import.meta.url),
 pFall=new URL("./SHUTTLE_MASS_WATERFALL.svg",import.meta.url);
writeFileSync(pReport,report(data,stage,gitBlobId,geometry,ven,["SHUTTLE_SIDE_VIEW.svg","SHUTTLE_MASS_WATERFALL.svg"]));
writeFileSync(pSide,sideSVG(data,geometry));
writeFileSync(pFall,waterfallSVG(data,geometry));
process.stdout.write(JSON.stringify({run_id:gitBlobId,stage,gates:{A:geometry.gateA,B:geometry.gateB,C:ven?.gateC||"NOT_RUN",D2:ven?.gateD2||"NOT_RUN",D4:ven?.gateD4||"NOT_RUN"},report:"SHUTTLE_SIZER_REPORT.md"},null,2)+"\n");
