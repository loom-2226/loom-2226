#!/usr/bin/env node
/**
 * LOOM shuttle v1 Stage 3, minimal planetary sensitivity model.
 * RESEARCH / NON-CANON / NOT A FLIGHT QUALIFICATION.
 * Reuses the merged Stage 2 mass, water and rotor component ranges without changing them.
 * Ideal circular velocity and mass conservation are physical identities. Required ascent
 * trajectories, propulsion duty and thermal qualification remain explicit OPEN inputs.
 */
function num(x){return typeof x?.value==="number"?x.value:null;}
function range(x){return typeof x?.min==="number"&&typeof x?.max==="number"?[x.min,x.max]:null;}
function path(o,k){return k.split(".").reduce((z,q)=>z?.[q],o);}
function get(b,w,k,s){const row=k.startsWith("world.")?path(w,k.slice(6)):path(b,k);return s&&Object.hasOwn(s,k)?s[k]:(num(row)??(range(row)?.[0]===range(row)?.[1]?range(row)?.[0]:null));}
function f(v){return v===null||v===undefined||!Number.isFinite(v)?"OPEN":v.toFixed(3);}
function directions(n){const out=[];for(let i=1;out.length<n&&i<6561;i++){let x=i,d=[];for(let j=0;j<8;j++){d.push(x%3);x=Math.floor(x/3);}out.push(d);}if(out.length<n)throw Error("too many dimensions");return out;}
function design(b,w){
 const keys=Object.entries(b.mass).filter(([k,x])=>range(x)&&!["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t","kit_house_reactor_t"].includes(k)).map(([k])=>"mass."+k);
 keys.push("power.kit_house_reactor_thermal_MW","kit.packed_effective_density_t_per_m3");
 for(const k of ["rotor_figure_of_merit","tipjet_thermal_to_useful_rotor","rotor_safe_tip_speed_mps","rotor_hot_duty_limit_h","rotor_climb_rate_mps","torch_high_ve_kmps"])keys.push("power."+k);
 keys.push("water.crew_water_cold_mass_t","capsule.content_mass_t");
 for(const k of ["thrust_to_weight","sortie_dv_kmps"])keys.push("world.belly."+k);
 for(const k of ["ve_kmps","jet_efficiency"])keys.push("world.belly.electric."+k);
 for(const k of ["ve_kmps","cryo_tank_t","boiloff_fraction_per_day","storage_days","electrolysis_kWh_per_kg_water"])keys.push("world.belly.chemical."+k);
 const dirs=directions(keys.length),max=3**8;
 const sample=i=>{let q=i,c=[];for(let j=0;j<8;j++){c.push(q%3);q=Math.floor(q/3);}const s={};
  for(let j=0;j<keys.length;j++){const k=keys[j],p=k.startsWith("world.")?path(w,k.slice(6)):path(b,k),v=range(p);if(!v)throw Error("unswept "+k);
   const lev=c.reduce((acc,t,z)=>acc+t*dirs[j][z],0)%3;s[k]=v[0]+(v[1]-v[0])*lev/2;}return s;};
 const n=num(w.pilot.sweep_count);if(n!==max)throw Error("Stage3 expects 3^8 deterministic samples");
 return {keys,count:n,sample};
}
function dry(b,s){
 const exclude=new Set(["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t"]);
 const raw=get(b,null,"power.kit_house_reactor_thermal_MW",s);
 const house=raw*num(b.power.kit_house_reactor_direct_conversion_efficiency)/num(b.power.kit_house_reactor_net_specific_kW_per_kg);
 const parts=Object.entries(b.mass).filter(([k])=>!exclude.has(k)).map(([k,x])=>[k,k==="kit_house_reactor_t"?house:(range(x)?get(b,null,"mass."+k,s):num(x))]);
 if(parts.some(([,v])=>v===null||!Number.isFinite(v)))throw Error("non-numeric dry mass");
 const total=parts.reduce((a,[,v])=>a+v,0),kit=parts.filter(([k])=>b.kit.mass_component_keys.includes(k)).reduce((a,[,v])=>a+v,0);
 return {total,kit,core:total-kit,house,parts};
}
function rotor(b,world,s,mass,h){
 const r=num(b.geometry.rotor_diameter_m)/2,area=Math.PI*r*r,g=num(world.surface_gravity_mps2);
 const rho=num(world.surface_density_kg_m3)*Math.exp(-h/num(world.density_scale_height_km));
 const force=mass*num(b.si.kg_per_t)*g,induced=Math.sqrt(force/(2*rho*area));
 const shaftMW=force*induced/(num(b.si.W_per_MW)*get(b,null,"power.rotor_figure_of_merit",s));
 return {induced,shaftMW,rawMW:shaftMW/get(b,null,"power.tipjet_thermal_to_useful_rotor",s),density:rho};
}
function bellyCase(b,w,world,m,s,kind){
 // Same water is either stored as liquid reaction mass or converted aboard Wayfarer to H2+O2.
 // The cryogenic tank is extra dry mass once (chemical only), with boil-off charged before burn.
 const chem=kind==="chemical",source=w.belly[kind],tank=chem?get(b,w,"world.belly.chemical.cryo_tank_t",s):0;
 const water=get(b,w,"water.reaction_water_initial_t",s);
 const cold=get(b,w,"water.crew_water_cold_mass_t",s),custody=get(b,w,"capsule.content_mass_t",s);
 const initialWet=m.core+tank+water+cold+custody,g=num(world.surface_gravity_mps2);
 const tw=get(b,w,"world.belly.thrust_to_weight",s);
 const thrustN=tw*initialWet*num(b.si.kg_per_t)*g;
 const dv=get(b,w,"world.belly.sortie_dv_kmps",s);
 const ve=get(b,w,"world.belly."+kind+".ve_kmps",s);
 const alpha=1-Math.exp(-dv/ve);
 let loadedT,boiloffT,bellyBurnT,reactorEnergyKWh=null,productionHours=null,jetGW=null,inputGW=null,retention=1;
 if(chem){
   const perDay=get(b,w,"world.belly.chemical.boiloff_fraction_per_day",s);
   const days=get(b,w,"world.belly.chemical.storage_days",s);
   retention=(1-perDay)**days;
   const fLost=1-retention;
   // M0 at initial loaded inventory includes the cryo propellant and stowed ordinary water;
   // prior storage loss changes launch mass. Solve cryo load and loss consistently:
   // L=(M0 - f*L)*alpha/(1-f) -> L = alpha*M0 / (1-f*(1-alpha)).
   loadedT=initialWet*alpha/(1-fLost*(1-alpha));
   boiloffT=loadedT*fLost;
   bellyBurnT=loadedT-boiloffT;
   const kWhKg=get(b,w,"world.belly.chemical.electrolysis_kWh_per_kg_water",s);
   reactorEnergyKWh=loadedT*num(b.si.kg_per_t)*kWhKg;
   productionHours=reactorEnergyKWh/(num(w.belly.chemical.house_reactors_net_MW)*num(b.si.kW_per_MW));
 }else{
   loadedT=initialWet*alpha;boiloffT=0;bellyBurnT=loadedT;
   const eta=get(b,w,"world.belly.electric.jet_efficiency",s);
   jetGW=thrustN*(ve*num(b.si.m_per_km))/2/num(b.si.W_per_GW);
   inputGW=jetGW/eta;
 }
 // Water consumed for belly is loaded cryogenic H2+O2 in chemical mode and
 // direct mass-flow water in electric mode; no double water stock.
 const afterBellyWater=water-loadedT;
 const finalBellyMass=initialWet-loadedT;
 const idealOrbitKmps=Math.sqrt(g*num(world.mean_radius_km)*num(b.si.m_per_km))/num(b.si.m_per_km);
 const torchVe=get(b,w,"power.torch_high_ve_kmps",s);
 const torchWaterNeed=finalBellyMass*(1-Math.exp(-idealOrbitKmps/torchVe));
 const margin=afterBellyWater-torchWaterNeed;
 const afterTorchWater=Math.max(0,afterBellyWater-Math.min(afterBellyWater,torchWaterNeed));
 const coreMargin=num(b.mass.max_docked_dry_t)-(m.core+tank);
 const flags={
   dockedDry:coreMargin>=0?"PASS":"FAIL",
   thrustSizing:tw>=get(b,w,"world.belly.thrust_to_weight",s)?"PASS":"FAIL",
   water:margin>=-1e-10?"PASS":"FAIL",
   physicalSource:chem?"OPEN":"OPEN"
 };
 return {kind,cryoTankT:tank,initialWetT:initialWet,tw,thrustN,thrustkN:thrustN/num(w.si.N_per_kN),
   bellyDvKmps:dv,veKmps:ve,jetGW,inputGW,loadedT,boiloffT,bellyBurnT,
   storedWaterT:water,afterBellyWaterT:afterBellyWater,torchWaterNeedT:torchWaterNeed,
   afterTorchWaterT:afterTorchWater,idealOrbitKmps,margin,coreMargin,flags,
   productionEnergyKWh:reactorEnergyKWh,productionHours,retention,
   waterPhases:[
    {phase:"Wayfarer load before sortie",waterT:water,chargedT:0,cryoT:chem?loadedT:null,coldT:cold,custodyT:custody},
    {phase:chem?"Cryogenic boil-off and belly burn":"Thermal/electric water belly burn",waterT:afterBellyWater,
     chargedT:loadedT,cryoT:chem?bellyBurnT:null,boiloffT,coldT:cold,custodyT:custody},
    {phase:"Main torch ideal-circular-speed floor (NOT full ascent)",waterT:afterTorchWater,
     chargedT:Math.min(Math.max(0,afterBellyWater),torchWaterNeed),cryoT:0,coldT:cold,custodyT:custody}
   ]};
}
function assess(b,w,name,s){
 const world=w.worlds[name],m=dry(b,s),titan=world.mode==="ROTOR_KIT_HOUSE_REACTOR";
 const stored=get(b,w,"water.reaction_water_initial_t",s),cold=get(b,w,"water.crew_water_cold_mass_t",s),cargo=get(b,w,"capsule.content_mass_t",s);
 const launchMass=(titan?m.total:m.core)+stored+cold+cargo;
 const g=num(world.surface_gravity_mps2),R=num(world.mean_radius_km)*num(b.si.m_per_km);
 const idealOrbitKmps=Math.sqrt(g*R)/num(b.si.m_per_km);
 const ve=get(b,null,"power.torch_high_ve_kmps",s);
 const idealBurnT=launchMass*(1-Math.exp(-idealOrbitKmps/ve));
 const afterBurn=Math.max(0,stored-Math.min(stored,idealBurnT));
 const coreMargin=num(b.mass.max_docked_dry_t)-m.core;
 const kitVolume=m.kit/get(b,null,"kit.packed_effective_density_t_per_m3",s);
 const kitMargin=num(b.kit.holds_free_m3)-kitVolume;
 const flags={A2:coreMargin>=0?"PASS":"FAIL",
  KIT_VOLUME:titan?(kitMargin>=0&&m.kit<=num(b.kit.payload_allowance_t)?"PASS":"FAIL"):"N/A",
  LIFT_SCREEN:titan?"PASS":"N/A",ROTOR_MODEL_TOP:titan?"FAIL":"N/A",
  WATER_IDEAL_FLOOR:titan?(stored>=idealBurnT?"PASS":"FAIL"):"N/A",
  ORBIT_FULL:"OPEN",SURFACE_THERMAL:"OPEN",BAY_FULL:"OPEN",FLIGHT_TOTAL:"OPEN"};
 const margins={A2:coreMargin,KIT_VOLUME:kitMargin,LIFT_SCREEN:0,
  ROTOR_MODEL_TOP:0,WATER_IDEAL_FLOOR:stored-idealBurnT};
 let modelTop=null,tipOrBelly=null,architectures=null;
 if(titan){
   const budget=get(b,null,"power.kit_house_reactor_thermal_MW",s);
   const horizon=num(world.atmosphere_model_ceiling_km),step=num(b.sweep.handover_step_km);
   for(let h=0;h<=horizon;h+=step){const z=rotor(b,world,s,launchMass,h);
     if(z.rawMW>budget||z.induced>get(b,null,"power.rotor_safe_tip_speed_mps",s)||
       h*num(b.si.m_per_km)/get(b,null,"power.rotor_climb_rate_mps",s)/num(b.si.seconds_per_hour)>get(b,null,"power.rotor_hot_duty_limit_h",s))break;
     modelTop=h;}
   const z=rotor(b,world,s,launchMass,0);
   margins.LIFT_SCREEN=budget-z.rawMW;
   flags.LIFT_SCREEN=margins.LIFT_SCREEN>=0?"PASS":"FAIL";
   margins.ROTOR_MODEL_TOP=modelTop===null?-horizon:modelTop-horizon;
   flags.ROTOR_MODEL_TOP=modelTop!==null&&modelTop>=horizon?"PASS":"FAIL";
   tipOrBelly={rawHoverMW:z.rawMW,shaftHoverMW:z.shaftMW,induced:z.induced,reactorMW:budget,
     observedEnvelopeKm:modelTop,envelopeLimitKm:horizon};
 }else{
   const electric=bellyCase(b,w,world,m,s,"electric");
   const chemical=bellyCase(b,w,world,m,s,"chemical");
   architectures={electric,chemical};
   flags.A2_CHEM=chemical.flags.dockedDry;
   flags.BELLY_TW_E=electric.flags.thrustSizing;
   flags.BELLY_TW_C=chemical.flags.thrustSizing;
   flags.BELLY_WATER_E=electric.flags.water;
   flags.BELLY_WATER_C=chemical.flags.water;
   flags.GW_TAP_E="OPEN"; // explicit no physical feeder
   flags.WAYFARER_ELECTROLYSIS="OPEN"; // 100MW source declared but production plant unqualified
   flags.CRYO_PHYSICAL="OPEN";
   flags.LIFT_SCREEN="N/A";
   flags.WATER_IDEAL_FLOOR="N/A";
   margins.A2_CHEM=chemical.coreMargin;
   margins.BELLY_TW_E=electric.thrustkN; // sized requirement driver ranking, not hardware pass margin
   margins.BELLY_TW_C=chemical.thrustkN;
   margins.BELLY_WATER_E=electric.margin;
   margins.BELLY_WATER_C=chemical.margin;
   tipOrBelly={worldSized:true,thrustElectrickN:electric.thrustkN,thrustChemicalkN:chemical.thrustkN};
 }
 if(["A2",...(titan?["KIT_VOLUME","LIFT_SCREEN","WATER_IDEAL_FLOOR"]:[])].some(k=>flags[k]==="FAIL"))flags.FLIGHT_TOTAL="FAIL";
 if(!titan){
   flags.FLIGHT_E=flags.A2==="FAIL"||flags.BELLY_WATER_E==="FAIL"?"FAIL":"OPEN";
   flags.FLIGHT_C=flags.A2_CHEM==="FAIL"||flags.BELLY_WATER_C==="FAIL"?"FAIL":"OPEN";
   flags.FLIGHT_TOTAL=flags.FLIGHT_E==="FAIL"&&flags.FLIGHT_C==="FAIL"?"FAIL":"OPEN";
 }
 const waterPhases=titan?[
  {phase:"entry/rotor (no reaction-water debit)",reactionWaterT:stored,coldCrewWaterT:cold,custodyT:cargo,chargedRemassT:0},
  {phase:"ideal circular-speed torch floor",reactionWaterT:afterBurn,coldCrewWaterT:cold,custodyT:cargo,
   chargedRemassT:Math.min(stored,idealBurnT)}
 ]:[];
 return {name,flags,margins,mass:m,launchMass,idealOrbitKmps,idealBurnT,afterBurn,waterPhases,lift:tipOrBelly,
  architectures,physicalHolds:[
   "worlds."+name+".required_ascent_dv_kmps","worlds."+name+".surface_thermal_qualification",
   ...(titan?["worlds.Titan.real_handover_altitude_km","Titan upper-atmosphere model, hot N2/CH4 rotor, torch plume"]:[
    "belly.electric.torch_reactor_GW_tap","belly.chemical.electrolysis_plant_and_liquefaction_qualified",
    "belly.chemical.cryo_joint_storage_qualified","worlds."+name+".belly_sustained_burn_and_ramp"]),
   "G8 stowed geometry"]};
}
function counts(rows,key){
 const x={PASS:0,FAIL:0,OPEN:0,"N/A":0};for(const r of rows)x[r.flags[key]]++;
 return { ...x,pass_fraction:(x.PASS+x.FAIL)?x.PASS/(x.PASS+x.FAIL):null,total:rows.length};
}
function topDrivers(b,w,name,k,fields){
 const baseline=design(b,w),N=num(w.pilot.oat_count),out=[];
 for(const field of fields){
   const line=field.startsWith("world.")?path(w,field.slice(6)):path(b,field),bb=range(line);if(!bb)continue;
   const pass=[],margin=[];
   for(const v of [bb[0],(bb[0]+bb[1])/2,bb[1]]){
     let good=0,valid=0,mm=0;
     for(let i=0;i<N;i++){const s=baseline.sample(i);s[field]=v;const z=assess(b,w,name,s);
       if(z.flags[k]!=="OPEN"&&z.flags[k]!=="N/A"){valid++;if(z.flags[k]==="PASS")good++;}
       mm+=z.margins[k]??0;
     }
     pass.push(valid?good/valid:null);margin.push(mm/N);
   }
   const spread=Math.max(...pass.filter(v=>v!==null))-Math.min(...pass.filter(v=>v!==null));
   out.push({field,passRates:pass,flipFraction:spread,marginShift:Math.max(...margin)-Math.min(...margin)});
 }
 out.sort((a,b)=>b.flipFraction-a.flipFraction||b.marginShift-a.marginShift||a.field.localeCompare(b.field));
 return out.slice(0,num(w.pilot.top));
}
function analyze(b,w){
 const sampling=design(b,w),worlds={};
 for(const name of Object.keys(w.worlds)){
   const rows=[],ranges={};
   let minTop=Infinity,maxTop=-Infinity,topFound=0;
   for(let i=0;i<sampling.count;i++){
     const r=assess(b,w,name,sampling.sample(i));rows.push(r);
     if(r.lift.observedEnvelopeKm!==undefined&&r.lift.observedEnvelopeKm!==null){
       minTop=Math.min(minTop,r.lift.observedEnvelopeKm);maxTop=Math.max(maxTop,r.lift.observedEnvelopeKm);topFound++;}
     if(r.architectures)for(const kind of ["electric","chemical"]){
       for(const k of ["thrustkN","initialWetT","veKmps","bellyDvKmps","jetGW","inputGW",
         "loadedT","bellyBurnT","boiloffT","cryoTankT","afterBellyWaterT","torchWaterNeedT",
         "afterTorchWaterT","productionEnergyKWh","productionHours"]){
         const v=r.architectures[kind][k];if(!Number.isFinite(v))continue;
         const id=kind+"."+k,t=ranges[id]??(ranges[id]={min:Infinity,max:-Infinity,sum:0,count:0});
         t.min=Math.min(t.min,v);t.max=Math.max(t.max,v);t.sum+=v;t.count++;
       }
     }
   }
   const keys=["A2",...(name!=="Titan"?["A2_CHEM"]:[]),
     "KIT_VOLUME","LIFT_SCREEN","ROTOR_MODEL_TOP","WATER_IDEAL_FLOOR",
     ...(name!=="Titan"?["BELLY_TW_E","BELLY_TW_C","BELLY_WATER_E","BELLY_WATER_C",
       "GW_TAP_E","WAYFARER_ELECTROLYSIS","CRYO_PHYSICAL","FLIGHT_E","FLIGHT_C"]:[]),
     "ORBIT_FULL","SURFACE_THERMAL","BAY_FULL","FLIGHT_TOTAL"];
   const gates=Object.fromEntries(keys.map(k=>[k,counts(rows,k)]));
   const ranking=Object.fromEntries(keys.filter(k=>!["FLIGHT_TOTAL","FLIGHT_E","FLIGHT_C"].includes(k)
     &&gates[k].PASS+gates[k].FAIL>0&&gates[k]["N/A"]===0)
       .map(k=>[k,topDrivers(b,w,name,k,sampling.keys)]));
   const outputRanges=Object.fromEntries(Object.entries(ranges).map(([k,v])=>
       [k,{min:v.min,mean:v.sum/v.count,max:v.max}]));
   worlds[name]={gates,ranking,outputRanges,example:rows[0],
     altitude:{min:topFound?minTop:null,max:topFound?maxTop:null,
       censoredAtModelCeiling:num(w.worlds[name].atmosphere_model_ceiling_km)},
     sampled:sampling.count};
 }
 return {sampling:{rows:sampling.count,fields:sampling.keys},worlds};
}
function report(b,w,baseSha,worldSha,a){
 const rows=[],add=(...x)=>rows.push(...x),p=n=>f(n);
 add("# LOOM Shuttle v1 Stage 3 — Titan, Moon, Mars, Mercury",
 "ALL bodies. ALL sponsors. 2026–2226.",
 "",
 "**Status: RESEARCH / NON-CANON / NON-QUALIFICATION.** This is a deliberately small next-world experiment, not certified flight closure.",
 "Upstream: merged noncanon Stage 2 shuttle JSON, Git blob "+baseSha+". Stage 3 source inputs Git blob "+worldSha+".",
 "Deterministic 3-level 3^8 scenario design, "+a.sampling.rows+" per world, "+a.sampling.fields.length+" swept fields. PASS fractions are balanced-design fractions, NOT probabilities.",
 "",
 "## World gate counts",
 "| World | Gate | PASS | FAIL | OPEN | N/A | PASS among resolved |",
 "|---|---|---:|---:|---:|---:|---:|");
 for(const [name,z] of Object.entries(a.worlds))for(const [key,v]of Object.entries(z.gates))
  add("| "+name+" | "+key+" | "+v.PASS+" | "+v.FAIL+" | "+v.OPEN+" | "+v["N/A"]+" | "+(v.pass_fraction===null?"n/a":p(100*v.pass_fraction)+"%")+" |");
 add("","## Physical meaning of the gates",
 "**A2:** Same 34.2t docked core dry without detachable kit. Installed Titan mass includes the entire kit; Moon/Mars/Mercury do not carry it.",
 "**KIT_VOLUME:** Titan-only 56.1m3 aggregate hold and 50t total payload necessary check; individual hold openings and hot blade joints remain OPEN.",
 "**LIFT_SCREEN:** Titan conditional near-surface rotor thermal/induced-velocity screen; light worlds peak T/W of #453 Venus belly 760kN array ANALOGUE only, NOT approved small-thruster hardware or sustained lift.",
 "**ROTOR_MODEL_TOP:** Titan-only threshold of reaching the stated 60km ANALYTICAL ATMOSPHERE DOMAIN EDGE. An artificial model-boundary screen, NOT kT required handover altitude. Model altitude censored at 60km.",
 "**WATER_IDEAL_FLOOR:** high-ve torch and finite 23.1t reaction water compared to ideal circular velocity sqrt(g*radius) using rocket equation, with 0–0.84t unqualified belly touchdown debit on light worlds; actual torch burn, gravity losses, guidance, atmospheric drag and continuous thrust NOT credited.",
 "**ORBIT_FULL:** OPEN for ALL because required site/trajectory Δv is not known. A PASS lower-bound is NOT orbital approval.",
 "**SURFACE_THERMAL:** OPEN for all, including Titan heater/cold operations, Mercury day-night, lunar cycles and Mars entry/dust.",
 "**BAY_FULL:** OPEN from G8 stowed geometry. **FLIGHT_TOTAL:** FAIL on demonstrated necessary-gate failure; otherwise OPEN; no certified PASS.",
 "",
 "## Per-world vehicle and water comparisons");
 for(const [name,z]of Object.entries(a.worlds)){
   const e=z.example,wd=w.worlds[name];add("### "+name,
     "Mode "+wd.mode+", gravity "+p(num(wd.surface_gravity_mps2))+"m/s², mean radius "+p(num(wd.mean_radius_km))+"km, necessary ideal orbital speed "+p(e.idealOrbitKmps)+"km/s.",
     "First sampled vehicle core "+p(e.mass.core)+"t, installed dry "+p(e.mass.total-(wd.mode==="BELLY_NO_KIT"?e.mass.kit:0))+"t, Titan/Venus kit "+p(e.mass.kit)+"t (carried on Wayfarer payload only when deployed). First sampled wet lift mass "+p(e.launchMass)+"t.",
     name==="Titan"?"Projected Titan atmosphere: rho0 "+p(num(wd.surface_density_kg_m3))+" kg/m³ × exp(-h/"+p(num(wd.density_scale_height_km))+"km), only to "+p(num(wd.atmosphere_model_ceiling_km))+"km. Observed rotor computed range "+p(z.altitude.min)+"–"+p(z.altitude.max)+"km; 60km results are CENSORED at model edge, NOT true handover.":"Unqualified 760kN #453 belly array used as hypothetical upper-bound peak; sustained duty and real small belly-nozzle installation OPEN.",
     "Reaction water, cabin cold-water and custody inventories are disjoint. Sampled ledger:",
     "| Phase | Reaction water remaining t | phase debit t | cold crew water t | custody content t |",
     "|---|---:|---:|---:|---:|");
   for(const ph of e.waterPhases)add("| "+ph.phase+" | "+p(ph.reactionWaterT)+" | "+p(ph.chargedRemassT)+" | "+p(ph.coldCrewWaterT)+" | "+p(ph.custodyT)+" |");
   add("Initial reaction water "+p(get(b,w,"water.reaction_water_initial_t"))+"t; ideal circular floor torch water "+p(e.idealBurnT)+"t, remaining "+p(e.afterBurn)+"t; REQUIRED full orbit Δv OPEN; separate belly liftoff burn OPEN.",
     "**Top three one-at-a-time sensitivity drivers per computed gate (including margin ranking if no PASS flips):**");
   for(const [key,items]of Object.entries(z.ranking)){
     add("**"+key+"**","| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |","|---|---|---:|---:|");
     for(const x of items)add("| "+x.field+" | "+x.passRates.map(v=>v===null?"OPEN":p(100*v)).join(" / ")+" | "+p(100*x.flipFraction)+" | "+p(x.marginShift)+" |");}
   add("All OPEN blockers: "+e.physicalHolds.join("; ")+".","");
 }
 add("## Research notes and explicit non-transfer",
 "Source facts: NASA Planetary Fact Sheets, JPL planetary physical parameters, NASA Titan thermal/environment and the merged #453 shuttle research. Each data field retains a URL and ONLINE/PROJECTION/ASSUMPTION/OPEN status in the attached JSON.",
 "Do not apply Venus atmospheric temperature, Venus entry TPS performance, Venus ascent Δv, reactor-to-rotor coupling qualification or any Torch dense atmosphere ignition assumption to Titan or the light worlds. No new propellant is created or shared between thermal water and reaction water.",
 "The 2226 kT lineage declarations, unresolved M1/M2/M3, physical validity and all canon remain untouched.",
 "",
 "## Full Stage 3 input JSON (source and provenance)", "~~~json",JSON.stringify(w,null,2),"~~~");
 return rows.join("\n")+"\n";
}
// CLI only; preceding functions are independently evaluable without filesystem effects.
import {readFileSync,writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
const root=new URL("./",import.meta.url);
const rawBase=readFileSync(new URL("./shuttle_inputs.json",root),"utf8");
const rawWorld=readFileSync(new URL("./shuttle_stage3_inputs.json",root),"utf8");
const sha=t=>createHash("sha1").update("blob "+Buffer.byteLength(t)+"\0"+t).digest("hex");
const b=JSON.parse(rawBase),w=JSON.parse(rawWorld),a=analyze(b,w);
const output=report(b,w,sha(rawBase),sha(rawWorld),a);
writeFileSync(new URL("./SHUTTLE_STAGE3_WORLDS_REPORT.md",root),output);
console.log("LOOM STAGE 3 WORLD SIZER NONCANON: "+a.sampling.rows+" samples per world.");
for(const [name,z]of Object.entries(a.worlds))console.log(name+": "+Object.entries(z.gates).map(([k,v])=>k+"="+v.PASS+"/"+v.FAIL+"/"+v.OPEN).join(" "));
console.log("SOURCE HASHES: "+sha(rawBase)+" / "+sha(rawWorld));
