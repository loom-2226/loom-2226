#!/usr/bin/env node
/**
 * LOOM shuttle sizing v1. Stage-selected input JSON is the sole engineering parameter authority.
 * Numerical physical inputs, screen thresholds and sampling counts are sourced from JSON.
 * Formulas use only mathematical identities. Never promotes an assumption into certification.
 */
function number(o){return typeof o?.value==="number"?o.value:null;}
function bounds(o){return typeof o?.min==="number"&&typeof o?.max==="number"?[o.min,o.max]:null;}
function readPath(d,k){return k.split(".").reduce((o,part)=>o?.[part],d);}
function val(d,k,s){const row=readPath(d,k);return s&&Object.prototype.hasOwnProperty.call(s,k)?s[k]:(number(row)??(bounds(row)?.[0]===bounds(row)?.[1]?bounds(row)?.[0]:null));}
function vals(d,k,s){const v=val(d,k,s),b=bounds(readPath(d,k));return v!==null?v:(b?(b[0]+b[1])/2:null);}
function fmt(v,p){return v===null||v===undefined||!Number.isFinite(v)?"OPEN":v.toFixed(p);}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function fkeys(d,path){return Object.keys(readPath(d,path)||{}).filter(k=>bounds(readPath(d,path+"."+k)));}
function sampleDirections(count,digits,levels){
 const directions=[];
 for(let x=1;directions.length<count && x<levels**digits;x++){
  let q=x,v=[];for(let j=0;j<digits;j++){v.push(q%levels);q=Math.floor(q/levels);}
  if(v.some(z=>z!==0))directions.push(v);
 }
 if(directions.length<count)throw Error("Not enough distinct coordinate-balanced directions");
 return directions;
}
function samples(d,stage,limit){
 const fields=fkeys(d,"mass").filter(k=>!["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t"].includes(k)).map(k=>"mass."+k);
 fields.push("kit.packed_effective_density_t_per_m3");
 if(stage===2)fields.push(...[
  ...fkeys(d,"power").filter(k=>["rotor_figure_of_merit","tipjet_thermal_to_useful_rotor","rotor_usable_input_heat_limit_MW","rotor_safe_tip_speed_mps","rotor_hot_duty_limit_h","rotor_climb_rate_mps","torch_low_ve_kmps","torch_high_ve_kmps","torch_jet_power_GW"].includes(k)).map(k=>"power."+k),
  ...fkeys(d,"water").filter(k=>["reaction_water_entry_debit_t","crew_water_cold_mass_t","crew_water_heating_delta_T_K"].includes(k)).map(k=>"water."+k),
  ...fkeys(d,"thermal").filter(k=>["insulation_k_W_per_mK","insulation_thickness_m","crew_heat_W_each","cabin_electronics_kW","venus_external_surface_K","active_cooler_power_available_kW","reactor_aux_electric_power_available_kW","hot_side_rejection_capacity_kW","hot_loop_reject_temperature_K","cooler_coefficient_of_performance"].includes(k)).map(k=>"thermal."+k),
  ...fkeys(d,"venus").filter(k=>["handover_altitude_km","torch_ascent_dv_kmps"].includes(k)).map(k=>"venus."+k),
  ...fkeys(d,"capsule").filter(k=>k==="content_mass_t").map(k=>"capsule."+k)
 ]);
 const N=limit,levels=number(d.sweep.sample_levels),digits=Math.round(Math.log(N)/Math.log(levels));
 if(levels**digits!==N)throw Error("sample count must be exact power of sample levels");
 const directions=sampleDirections(fields.length,digits,levels);
 const levelsFor=i=>{let n=i,r=[];for(let j=0;j<digits;j++){r.push(n%levels);n=Math.floor(n/levels)}return r};
 const get=(i)=>{let out={},code=levelsFor(i);for(let j=0;j<fields.length;j++){
   const k=fields[j],line=readPath(d,k),ds=directions[j];
   const level=code.reduce((sum,bit,idx)=>sum+bit*ds[idx],0)%levels;
   out[k]=line.min+(line.max-line.min)*level/(levels-1);
 }return out};
 return {fields,rows:N,get};
}
function gate(needed,test){
 const missing=needed.filter(([k,v])=>v===null||v===undefined||!Number.isFinite(v)).map(([k])=>k);
 return missing.length?{status:"OPEN",missing}: {status:test()?"PASS":"FAIL",missing:[]};
}
function geometry(d){
 const g=d.geometry,p=d.sweep,availD=2*(number(g.bay_bore_radius_m)-number(g.g8_min_radial_clearance_m)),
 availL=number(g.bay_x_end_m)-number(g.bay_x_start_m)-2*number(g.g8_min_axial_clearance_m),
 hullD=number(g.hull_diameter_m),hullL=number(g.hull_length_m),rotorD=number(g.rotor_diameter_m);
 const eps=Number.EPSILON*Math.max(availD,availL,hullD,hullL)*2;
 const necessary=hullD<=availD+eps && hullL<=availL+eps && rotorD<=hullL+eps &&
   number(g.rotor_blades_fwd)+number(g.rotor_blades_aft)===number(g.rotor_blades);
 const req=["mast_stowed_extra_diameter_m","hub_axial_length_m","mast_retracted_height_m","crew_pod_x_m","rotor_mast_x_m","rotor_retracted_cg_m","pod_door_ramp_external_excursion_m"];
 const gB= !necessary?{status:"FAIL",missing:[]}:
 gate(req.map(k=>["geometry."+k,number(g[k])]),()=> {
    // Necessary but not sufficient simple extents, positions and CG alignment.
    const extra=number(g.mast_stowed_extra_diameter_m);
    const hub=number(g.hub_axial_length_m);
    const mast=number(g.mast_retracted_height_m);
    const px=number(g.crew_pod_x_m),cx=number(g.rotor_mast_x_m),cg=number(g.rotor_retracted_cg_m);
    return extra<=availD-hullD+eps && mast<=hullD+eps &&
      rotorD+hub<=hullL+eps && px>=0&&px<=hullL&&cx>=0&&cx<=hullL&&cg>=0&&cg<=hullL&&
      number(g.pod_door_ramp_external_excursion_m)<=availD-hullD+eps;
 });
 return {availD,availL,hullD,hullL,rotorD,necessary,gateB:gB,
   radialClearance:Math.abs(availD-hullD)<=eps?0:availD-hullD,
   axialClearance:Math.abs(availL-hullL)<=eps?0:availL-hullL,
   nominalFoldSpan:rotorD,freeLength:hullL-rotorD};
}
function dry(d,s){
 const excluded=new Set(["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t"]);
 const keys=Object.keys(d.mass).filter(x=>!excluded.has(x));
 const parts=keys.map(k=>({key:k,value:val(d,"mass."+k,s)}));
 const missing=parts.filter(x=>x.value===null).map(x=>"mass."+x.key);
 const sum=missing.length?null:parts.reduce((a,b)=>a+b.value,0);
 const kitKeys=d.kit.mass_component_keys;
 const kitMissing=kitKeys.filter(k=>val(d,"mass."+k,s)===null).map(k=>"mass."+k);
 const kitT=kitMissing.length?null:kitKeys.reduce((x,k)=>x+val(d,"mass."+k,s),0);
 const coreT=sum===null||kitT===null?null:sum-kitT;
 const limit=number(d.mass.max_docked_dry_t);
 const a=gate(parts.map(x=>["mass."+x.key,x.value]),()=>sum<=limit);
 const a2=gate([["mass.dry_without_venus_kit",coreT]],()=>coreT<=limit);
 return {status:a.status,missing:a.missing,sum,margin:sum===null?null:limit-sum,
   a2:a2.status,a2Missing:a2.missing,a2Margin:coreT===null?null:limit-coreT,coreT,kitT,parts};
}
function kitFit(d,s,dryResult){
 const mass=dryResult.kitT,density=val(d,"kit.packed_effective_density_t_per_m3",s);
 const free=number(d.kit.holds_free_m3),payload=number(d.kit.payload_allowance_t);
 const bladeM=number(d.geometry.rotor_diameter_m)/2;
 const segmentLength=bladeM/number(d.kit.rotor_blade_segments_per_blade);
 const serviceLength=number(d.kit.service_x_end_m)-number(d.kit.service_x_start_m);
 const volume=mass===null||density===null?null:mass/density;
 const volumeGate=gate([["mass.venus_kit_t",mass],["kit.packed_effective_density_t_per_m3",density]],
    ()=>volume<=free && mass<=payload && segmentLength<=serviceLength);
 const required=["kit.individual_hold_aperture_m","kit.individual_hold_cross_section_m2",
   "kit.rotor_blade_joint_qualified","kit.hot_shuttle_kit_fit_qualified"];
 const g=volumeGate.status==="FAIL"?{status:"FAIL",missing:[]}:
    gate(required.map(k=>[k,number(readPath(d,k))]),()=>volumeGate.status==="PASS" && required.every(k=>number(readPath(d,k))>0));
 return {mass_t:mass,density,packedVolume_m3:volume,payloadLimit_t:payload,freeVolume_m3:free,
     segmentLength_m:segmentLength,holdLength_m:serviceLength,volumeGate:volumeGate.status,
     volumeMissing:volumeGate.missing,fit:g.status,fitMissing:g.missing};
}
function atmosphere(d,h){
 const rows=d.venus.atmosphere_profile;
 if(h<rows[0].altitude_km||h>rows[rows.length-1].altitude_km)return null;
 for(let i=1;i<rows.length;i++)if(h<=rows[i].altitude_km){
  const a=rows[i-1],b=rows[i],w=(h-a.altitude_km)/(b.altitude_km-a.altitude_km);
  // VIRA table: density and pressure interpolated log-linearly; temperature linearly.
  return {rho:Math.exp(Math.log(a.density_kg_m3)*(1-w)+Math.log(b.density_kg_m3)*w),
    temperature:a.temperature_K+(b.temperature_K-a.temperature_K)*w,
    pressure:Math.exp(Math.log(a.pressure_bar)*(1-w)+Math.log(b.pressure_bar)*w)};
 }
 return null;
}
function rotorAt(d,s,mass,h){
 const a=atmosphere(d,h);if(!a)return null;
 const g=number(d.venus.gravity_mps2),m=mass*number(d.si.kg_per_t),
 area=Math.PI*(number(d.geometry.rotor_diameter_m)/2)**2,force=m*g;
 const induced=Math.sqrt(force/(2*a.rho*area));
 const powerMW=force*induced/(number(d.si.W_per_MW)*val(d,"power.rotor_figure_of_merit",s));
 const sourceMW=powerMW/val(d,"power.tipjet_thermal_to_useful_rotor",s);
 return {alt:h,air:a,induced,shaftMW:powerMW,sourceMW};
}
function stage2(d,s,dryResult){
 const missing=[];const requirePath=k=>{const v=val(d,k,s);if(v===null)missing.push(k);return v};
 const dryT=dryResult.sum; if(dryT===null)missing.push(...dryResult.missing);
 const reactionStart=requirePath("water.reaction_water_initial_t"),thermalT=requirePath("water.crew_water_cold_mass_t"),
 cargoT=requirePath("capsule.content_mass_t"),entryT=requirePath("water.reaction_water_entry_debit_t");
 const km=requirePath("si.m_per_km"),kg=requirePath("si.kg_per_t"),seconds=requirePath("si.seconds_per_hour");
 const altitudeLimit=requirePath("venus.handover_altitude_km"),minimumAltitude=d.venus.handover_altitude_km.min;
 const climb=requirePath("power.rotor_climb_rate_mps"),maxHotH=requirePath("power.rotor_hot_duty_limit_h"),
 maxTip=requirePath("power.rotor_safe_tip_speed_mps"),heatMax=requirePath("power.rotor_usable_input_heat_limit_MW");
 const step=requirePath("sweep.handover_step_km"),requiredDV=requirePath("venus.torch_ascent_dv_kmps");
 const jetGW=requirePath("power.torch_jet_power_GW");
 let rotorGate={status:"OPEN",missing:[...new Set(missing)]},handover=null,altProfile=[],flightTimeH=null;
 const baseMass=dryT===null||reactionStart===null||thermalT===null||cargoT===null?null:dryT+reactionStart+thermalT+cargoT;
 if(!rotorGate.missing.length){
   // Sampled rotor climb boundary, not an aerodynamic/structural rotor qualification.
   let accepted=null;
   for(let h=0;h<=altitudeLimit+Number.EPSILON;h+=step){
     const x=rotorAt(d,s,baseMass,h);
     if(!x||x.sourceMW>heatMax||x.induced>maxTip||h*km/climb/seconds>maxHotH)break;
     accepted=x;altProfile.push(x);
   }
   handover=accepted?.alt??null; flightTimeH=handover===null?null:handover*km/climb/seconds;
   rotorGate={status:handover!==null&&handover>=minimumAltitude?"PASS":"FAIL",missing:[]};
 }
 const modes={};
 for(const mode of ["low","high"]){
  const ve=requirePath("power.torch_"+mode+"_ve_kmps");
  const required=[["mass.dry_total_t",dryT],["water.reaction_water_initial_t",reactionStart],
   ["water.crew_water_cold_mass_t",thermalT],["capsule.content_mass_t",cargoT],
   ["water.reaction_water_entry_debit_t",entryT],
   ["venus.torch_ascent_dv_kmps",requiredDV],["power.torch_"+mode+"_ve_kmps",ve],
   ["power.torch_jet_power_GW",jetGW],["power.rotor_usable_input_heat_limit_MW",heatMax],
   ["venus.handover_altitude_km",altitudeLimit],["power.rotor_climb_rate_mps",climb],
   ["power.rotor_hot_duty_limit_h",maxHotH],["power.rotor_safe_tip_speed_mps",maxTip]];
  const q=gate(required,()=>true);
  if(q.status==="OPEN"){modes[mode]={status:"OPEN",missing:q.missing,waterAtOrbit:null,delta_v_orbit:null};continue;}
  const afterEntry=reactionStart-entryT;
  const massStart=dryT+thermalT+cargoT+afterEntry;
  const waterDemand=massStart*(1-Math.exp(-requiredDV/ve));
  const waterPass=afterEntry>=0&&waterDemand<=afterEntry+Number.EPSILON*massStart;
  const actualWaterUsed=Math.max(0,Math.min(Math.max(0,afterEntry),waterDemand));
  const waterEnd=Math.max(0,afterEntry-actualWaterUsed);
  const waterShortfall=Math.max(0,waterDemand-afterEntry);
  const P=jetGW*number(d.si.W_per_GW),vel=ve*km,thrustN=2*P/vel,mdot=thrustN/vel;
  const burnSeconds=actualWaterUsed*kg/mdot;
  const theoreticalDV=ve*Math.log(massStart/(dryT+thermalT+cargoT));
  const status=rotorGate.status==="OPEN"?"OPEN":waterPass&&rotorGate.status==="PASS"?"PASS":"FAIL";
  modes[mode]={status,waterPass,waterAtOrbit:waterEnd,waterDemandT:waterDemand,waterShortfallT:waterShortfall,waterUsedTorchT:actualWaterUsed,
    delta_v_orbit:waterPass?requiredDV:Math.max(0,theoreticalDV),
    delta_v_required:requiredDV,thrustN,mdot,burnSeconds,
    timeH:burnSeconds/seconds,missing:rotorGate.missing,
    afterEntryWaterT:afterEntry,initialMassT:massStart};
 }
 const thermal={};
 const needed=["thermal.venus_external_surface_K","thermal.insulation_k_W_per_mK","thermal.insulation_thickness_m",
  "thermal.crew_heat_W_each","thermal.cabin_electronics_kW","thermal.cooler_coefficient_of_performance",
  "thermal.active_cooler_power_available_kW","thermal.reactor_aux_electric_power_available_kW",
  "thermal.hot_side_rejection_capacity_kW","thermal.hot_loop_reject_temperature_K",
  "water.crew_water_cold_mass_t","water.crew_water_heating_delta_T_K",
  "water.crew_water_heat_capacity_J_per_kg_K","geometry.crew_pod_outer_diameter_m",
  "thermal.cabin_target_K","thermal.stay_requested_h"];
 const q=gate(needed.map(k=>[k,val(d,k,s)]),()=>true);
 for(const crewCount of d.thermal.crew_cases.map(number)){
   if(q.status==="OPEN"){thermal[crewCount]={status:"OPEN",missing:q.missing,podHours:null};continue;}
   const r=val(d,"geometry.crew_pod_outer_diameter_m")/2,area=4*Math.PI*r*r;
   const surface=val(d,"thermal.venus_external_surface_K",s);
   const leak=val(d,"thermal.insulation_k_W_per_mK",s)*area*
      (surface-val(d,"thermal.cabin_target_K"))/val(d,"thermal.insulation_thickness_m",s);
   const electronics=val(d,"thermal.cabin_electronics_kW",s)*number(d.si.W_per_kW);
   const coldLoadW=leak+electronics+crewCount*val(d,"thermal.crew_heat_W_each",s);
   const sensibleJ=thermalT*kg*val(d,"water.crew_water_heat_capacity_J_per_kg_K")*
      val(d,"water.crew_water_heating_delta_T_K",s);
   const podHours=sensibleJ/coldLoadW/seconds;
   const coolerKW=coldLoadW/number(d.si.W_per_kW)/val(d,"thermal.cooler_coefficient_of_performance",s);
   const rejectKW=coldLoadW/number(d.si.W_per_kW)+coolerKW;
   const electricalMax=Math.min(val(d,"thermal.active_cooler_power_available_kW",s),
      val(d,"thermal.reactor_aux_electric_power_available_kW",s));
   const rejectMax=val(d,"thermal.hot_side_rejection_capacity_kW",s);
   const temperatureOK=val(d,"thermal.hot_loop_reject_temperature_K",s)>surface;
   const massOK=dryResult.a2==="PASS" && dryResult.kitT<=number(d.kit.payload_allowance_t);
   const activeOK=temperatureOK&&massOK&&coolerKW<=electricalMax&&rejectKW<=rejectMax;
   thermal[crewCount]={status:activeOK?"PASS":"FAIL",missing:[],podHours,
     maxHours:null,loadW:coldLoadW,leakW:leak,capacityJ:sensibleJ,
     coolerElectricalKW:coolerKW,reactorBusLimitKW:electricalMax,
     rejectKW,rejectLimitKW:rejectMax,temperatureOK,massOK,coldWaterPreservedForPod:true};
 }
 const gateC=rotorGate.status==="OPEN"?"OPEN":
  modes.low.status==="PASS"||modes.high.status==="PASS"?"PASS":
  modes.low.status==="OPEN"||modes.high.status==="OPEN"?"OPEN":"FAIL";
 const waterOpen=[...new Set([...rotorGate.missing,...(modes.low.missing||[]),...(modes.high.missing||[])])];
 return {rotor:rotorGate,gateC,waterMissing:waterOpen,handover,flightTimeH,baseMass,mode:modes,thermal,
  phaseLedger:phaseLedger(d,s,entryT,rotorGate,modes,thermalT,thermal),altProfile};
}
function phaseLedger(d,s,entry,rotor,modes,thermalT,thermal) {
 const initial=val(d,"water.reaction_water_initial_t",s),stages=["entry","rotor deploy","rotor descent","touchdown","surface stay","rotor climb","rotor-to-torch handover","torch ascent to orbit"];
 const active=Object.fromEntries(["low","high"].map(mode=>{
  let reaction=initial;
  const coldState=Object.fromEntries(d.thermal.crew_cases.map(q=>{const crew=number(q);return [crew,thermal[crew]?.capacityJ??null]}));
  const rows=stages.map(phase=>{
   const before=reaction;let debit=null;
   if(phase==="entry")debit=entry;
   else if(["rotor deploy","rotor descent","touchdown","surface stay","rotor climb","rotor-to-torch handover"].includes(phase))
       debit=val(d,"water.reaction_water_rotor_debit_t",s);
   else if(phase==="torch ascent to orbit")debit=modes[mode]?.waterUsedTorchT??null;
   if(debit!==null&&reaction!==null)reaction=Math.max(0,reaction-debit);else reaction=null;
   const cold={};for(const q of d.thermal.crew_cases){const crew=number(q),stored=coldState[crew];
      const request=phase==="surface stay"&&stored!==null?0 /* powered shuttle cooler, no cold-water heat debit */:0;
      const removed=stored===null?null:Math.min(stored,request);
      cold[crew]={energy_before_J:stored,energy_removed_J:removed,energy_shortfall_J:stored===null?null:Math.max(0,request-stored),energy_after_J:stored===null?null:stored-removed};
      coldState[crew]=cold[crew].energy_after_J;
   }
   return {phase,water_before_t:before,water_debit_t:debit,water_after_t:reaction,
       thermal_water_mass_t:thermalT,thermal_energy_by_crew:cold,
       torch_jet_power_GW:phase==="torch ascent to orbit"?val(d,"power.torch_jet_power_GW",s):null,
       reactor_waste_heat_MW:null,reactor_waste_heat_missing:"power.reactor_waste_heat_MW",
        cooler_electric_by_crew_kW:phase==="surface stay"?Object.fromEntries(d.thermal.crew_cases.map(q=>[number(q),thermal[number(q)]?.coolerElectricalKW??null])):null,
        hot_loop_rejection_by_crew_kW:phase==="surface stay"?Object.fromEntries(d.thermal.crew_cases.map(q=>[number(q),thermal[number(q)]?.rejectKW??null])):null,
       custody:"ONBOARD",custody_content_t:val(d,"capsule.content_mass_t",s)};
  });return [mode,rows];
 }));return active;
}
function census(rows,key){
 const counts={PASS:0,FAIL:0,OPEN:0};for(const x of rows)counts[x[key]]++;
 const resolved=counts.PASS+counts.FAIL;
 return {...counts,resolved,pass_fraction:resolved?counts.PASS/resolved:null,total:rows.length};
}
function evaluate(d,stage,s,geo){
 const dryResult=dry(d,s),kit=kitFit(d,s,dryResult);const v=stage===2?stage2(d,s,dryResult):null;
 return {A:dryResult.status,A2:dryResult.a2,KV:kit.volumeGate,KF:kit.fit,B:geo.gateB.status,R:v?.rotor.status??null,
   C:v?.gateC??null,C_low:v?.mode.low.status??null,C_high:v?.mode.high.status??null,
   DS2:v?.thermal[2].status??null,DS4:v?.thermal[4].status??null,
   dry:dryResult,kit,venus:v};
}
function sensitivity(d,stage,design,geo,gateKey){
 const chosen=design.fields;
 const N=number(d.sweep.sensitivity_count),picks=number(d.sweep.report_top_inputs),baseDesign=samples(d,stage,N),out=[];
 for(const field of chosen){
  const x=readPath(d,field);
  const level=[x.min,(x.min+x.max)/2,x.max],pass=[],margins=[];
  for(const v of level){
   let ok=0,n=0,marginTotal=0;
   for(let i=0;i<baseDesign.rows;i++){
    const base=baseDesign.get(i);base[field]=v;
    const e=evaluate(d,stage,base,geo),state=e[gateKey];
    if(state==="PASS")ok++;
    if(state!=="OPEN")n++;
    let margin=null;
    if(gateKey==="A")margin=e.dry.margin;
    else if(gateKey==="A2")margin=e.dry.a2Margin;
    else if(gateKey==="KV")margin=e.kit.freeVolume_m3-e.kit.packedVolume_m3;
    else if(gateKey==="DS2"||gateKey==="DS4"){const z=e.venus?.thermal[gateKey==="DS2"?2:4];margin=z?Math.min(z.reactorBusLimitKW-z.coolerElectricalKW,z.rejectLimitKW-z.rejectKW,e.dry.a2Margin):null;}
    else if(gateKey==="C")margin=Math.max(e.venus?.mode.low.waterAtOrbit??-Infinity,e.venus?.mode.high.waterAtOrbit??-Infinity);
    else if(gateKey==="R")margin=(e.venus?.handover??0)-d.venus.handover_altitude_km.min;
    if(margin!==null&&Number.isFinite(margin))marginTotal+=margin;
   }
   pass.push(n?ok/n:null);margins.push(marginTotal/baseDesign.rows);
  }
  const valid=pass.filter(v=>v!==null);const spread=valid.length?Math.max(...valid)-Math.min(...valid):null;
  const marginShift=Math.max(...margins)-Math.min(...margins);
  out.push({field,passRates:pass,flipSpread:spread,marginShift});
 }
 out.sort((a,b)=>(b.flipSpread??-1)-(a.flipSpread??-1)||b.marginShift-a.marginShift||a.field.localeCompare(b.field));
 return out.slice(0,picks);
}
function analyze(d,stage){
 const geo=geometry(d),limit=number(d.sweep.sample_count),design=samples(d,stage,limit),rows=[];
 const exemplars=[];
 const podRanges=Object.fromEntries(d.thermal.crew_cases.map(q=>[number(q),{min:Infinity,max:-Infinity}]));
 const extensions=stage===2?Object.fromEntries(d.venus.rotor_extension_levels_km.map(q=>[number(q),{rotorMin:Infinity,rotorMax:-Infinity,heatMin:Infinity,heatMax:-Infinity,pressure_bar:null}])):{};
 for(let i=0;i<design.rows;i++){
  const s=design.get(i),e=evaluate(d,stage,s,geo);
  rows.push({A:e.A,A2:e.A2,KV:e.KV,KF:e.KF,B:e.B,R:e.R,C:e.C,C_low:e.C_low,C_high:e.C_high,DS2:e.DS2,DS4:e.DS4});
  if(stage===2){for(const q of d.thermal.crew_cases){const crew=number(q),hours=e.venus.thermal[crew]?.podHours; if(Number.isFinite(hours)){podRanges[crew].min=Math.min(podRanges[crew].min,hours);podRanges[crew].max=Math.max(podRanges[crew].max,hours);}}
   for(const q of d.venus.rotor_extension_levels_km){const alt=number(q),p=extensions[alt],rot=rotorAt(d,s,e.venus.baseMass,alt);
     if(rot){p.rotorMin=Math.min(p.rotorMin,rot.shaftMW);p.rotorMax=Math.max(p.rotorMax,rot.shaftMW);
       p.heatMin=Math.min(p.heatMin,rot.sourceMW);p.heatMax=Math.max(p.heatMax,rot.sourceMW);p.pressure_bar=rot.air.pressure;}}
  }
  if(i<number(d.sweep.report_preview_samples))exemplars.push({sample:i,inputs:s,gates:rows.at(-1),dry:e.dry.sum,coreDry:e.dry.coreT,kit:e.kit,venus:stage===2?{
    handover:e.venus.handover,lowWater:e.venus.mode.low.waterAtOrbit,highWater:e.venus.mode.high.waterAtOrbit,
    lowThrust:e.venus.mode.low.thrustN,highThrust:e.venus.mode.high.thrustN,
    lowDV:e.venus.mode.low.delta_v_orbit,highDV:e.venus.mode.high.delta_v_orbit,
    twoCrewPodHours:e.venus.thermal[2].podHours,fourCrewPodHours:e.venus.thermal[4].podHours,
    twoCrewCoolingKW:e.venus.thermal[2].coolerElectricalKW,fourCrewCoolingKW:e.venus.thermal[4].coolerElectricalKW}:null});
 }
 const gates=Object.fromEntries(["A","A2","KV","KF","B",...(stage===2?["R","C","C_low","C_high","DS2","DS4"]:[])].map(k=>[k,census(rows,k)]));
 const jointStatus=states=>states.includes("FAIL")?"FAIL":states.includes("OPEN")?"OPEN":"PASS";
 const joint=stage===2?Object.fromEntries([
  ["A2_and_C",["A2","C"]],["A2_C_DS2",["A2","C","DS2"]],["A2_C_DS4",["A2","C","DS4"]],["A2_KF_C_DS2",["A2","KF","C","DS2"]],["A2_KF_C_DS4",["A2","KF","C","DS4"]]
 ].map(([k,ks])=>[k,census(rows.map(r=>({[k]:jointStatus(ks.map(x=>r[x]))})),k)])):{};
 const scores=Object.fromEntries(["A","A2","KV",...(stage===2?["R","C","DS2","DS4"]:[])].map(k=>[k,sensitivity(d,stage,design,geo,k)]));
 const components=Object.keys(d.mass).filter(x=>!["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t"].includes(x));
 const sums=[0,0,0];const partRows=components.map(k=>{
  const x=d.mass[k],levels=bounds(x)??[number(x),number(x)];
  const triplet=[levels[0],(levels[0]+levels[1])/2,levels[1]];
  triplet.forEach((v,i)=>sums[i]+=v);
  return {name:k,values:triplet,provenance:x.provenance};
 });
 const kitRows=partRows.filter(x=>d.kit.mass_component_keys.includes(x.name));
 const kitSums=[0,1,2].map(i=>kitRows.reduce((z,x)=>z+x.values[i],0));
 return {geometry:geo,gates,joint,scores,examples:exemplars,partRows,sums,kitRows,kitSums,podRanges,extensions,design:{rows:design.rows,fields:design.fields}};
}
function report(d,stage,hash,a,graphics){
 const p=number(d.sweep.round_decimals),f=x=>fmt(x,p);
 const lines=["# LOOM Shuttle Sizer v1 — Stage "+stage,"ALL bodies. ALL sponsors. 2026–2226.","",
  "**CLASS: Engineering sensitivity / ASSUMPTION / NON-CANON / NOT QUALIFICATION.**",
  "**Run identity:** Git blob SHA-1 of full UTF-8 input JSON incl. stage: \`"+hash+"\`.",
  "**Run:** \`node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage "+stage+"\`.",
  "**Graphics:** "+graphics.map(x=>"\`"+x+"\`").join(", ")+".","",
  "## Computed gates: per-sample status and sample PASS fractions",
  "Design: "+a.design.rows+" balanced, coordinate-stratified min/mid/max samples over "+a.design.fields.length+
   " independent swept inputs. This is **not** full Cartesian probability; PASS fractions are empirical design fractions, not calibrated probabilities.",
  "| Gate | PASS | FAIL | OPEN | PASS / resolved | Missing required inputs |",
  "|---|---:|---:|---:|---:|---|"];
 const requiredB=a.geometry.gateB.missing.length?a.geometry.gateB.missing.join(", "):"none";
 for(const [k,g] of Object.entries(a.gates))lines.push("| "+k+" | "+g.PASS+" | "+g.FAIL+" | "+g.OPEN+" | "+(g.pass_fraction===null?"n/a":(g.pass_fraction*100).toFixed(2)+"%")+" | "+(k==="B"?requiredB:"none in numeric screen; physical qualification holds separate")+" |");
 lines.push("");
 if(stage===2){lines.push("### Joint closure (same sampled configurations)","| Combined gates | PASS | FAIL | OPEN | PASS / resolved |","|---|---:|---:|---:|---:|");for(const [k,g] of Object.entries(a.joint))lines.push("| "+k+" | "+g.PASS+" | "+g.FAIL+" | "+g.OPEN+" | "+(g.pass_fraction===null?"n/a":(100*g.pass_fraction).toFixed(2)+"%")+" |");lines.push("A conditional water PASS is not an overall mission PASS: Bay fit still has required nulls, and passive 18h thermal survival must also pass.","");}
 lines.push("### Gate A mass envelope and historical comparison");
 lines.push("Component sums min / midpoint / max: **"+a.sums.map(f).join(" / ")+" t**. Gate A limit "+f(number(d.mass.max_docked_dry_t))+" t.");
 lines.push("Historical LOST-sizer empty mass "+f(number(d.mass.v1_comparison_dry_t))+" t is the **v1 comparison** while LOST historical output is **"+f(number(d.mass.historical_lost_sizer_dry_t))+"t** in PR #453; neither is an equality target or an input mass offset.");
 lines.push("Actual midpoint versus **"+f(number(d.mass.historical_lost_sizer_dry_t))+"t** historical output: **"+f(a.sums[1]-number(d.mass.historical_lost_sizer_dry_t))+" t** difference ("+f(number(d.mass.historical_lost_sizer_dry_t))+"t historical anchored in #453 and should not be mistaken for a constraint).");
 lines.push("| Distinct dry component | min | mid | max | provenance |","|---|---:|---:|---:|---|");
 for(const row of a.partRows)lines.push("| "+row.name+" | "+row.values.map(f).join(" | ")+" | "+row.provenance+" |");
 lines.push("");
 lines.push("### Gate B G8 stowed fit");
 lines.push("Necessary-dimensional result: **"+(a.geometry.necessary?"PASS":"FAIL")+"**. G8 allowable L "+f(a.geometry.availL)+" m, diameter "+f(a.geometry.availD)+" m; hull "+f(a.geometry.hullL)+" × "+f(a.geometry.hullD)+" m, folded theoretical blade span "+f(a.geometry.nominalFoldSpan)+"m. Real margins: L "+f(a.geometry.axialClearance)+"m, D "+f(a.geometry.radialClearance)+"m.");
 lines.push("Full fit verdict "+a.geometry.gateB.status+"; explicit REQUIRED nulls: "+requiredB+". No arbitrary hub or mast geometry credited.");
 lines.push("");
 lines.push("## Three most influential inputs per gate (one-at-a-time)");
 lines.push("Each factor is set to **min / mid / max** while "+number(d.sweep.sensitivity_count)+" balanced baselines hold all other inputs. Rank by change in PASS fraction; if no boundary crosses, rank by change in physical margin.");
 for(const [k,v] of Object.entries(a.scores)){
   lines.push("**Gate "+k+"**");
   lines.push("| Input | PASS % at min/mid/max | Δ PASS | Δ margin if no flip |","|---|---|---:|---:|");
   for(const x of v)lines.push("| "+x.field+" | "+x.passRates.map(y=>y===null?"OPEN":(y*100).toFixed(1)).join(" / ")+" | "+(x.flipSpread===null?"OPEN":(100*x.flipSpread).toFixed(1)+" pp")+" | "+f(x.marginShift)+" |");
   lines.push("");
 }
 if(stage===2){
 lines.push("## Stage 2: Venus rotor-to-torch, reaction water and thermal ledger");
 lines.push("The single "+f(number(d.geometry.rotor_diameter_m))+"m rotor uses VIRA tabulation, log-linear density interpolation, momentum theory and assumed FM & hot-gas effectiveness. **Handover altitude is computed for each sample**, limited by delivered tipjet heat, hot duty, tip-speed necessary bound and editable requested upper handover altitude. Required low bound "+f(d.venus.handover_altitude_km.min)+"km. No propulsive effect of rotor exhaust is credited to orbital speed.");
 lines.push("**Rotor Gate R:** hover/climb heat/duty arithmetic only, **not** structural rotor/blade-stall qualification. **C:** water-to-orbit from required post-handover Δv using independent low-only and high-only modes and \`thrust=2Pjet/ve\`, \`mdot=2Pjet/ve²\`. C passes if at least one mode returns nonnegative reaction water AND R passes. Crew thermal water and custody payload remain onboard mass, not reaction water.");
 lines.push("**Venus physical mission remains OPEN even where conditional C PASS:** at "+f(d.venus.handover_altitude_km.min)+"–"+f(d.venus.handover_altitude_km.max)+"km Venus atmosphere is still dense; missing torch atmosphere/plume viability, complete entry aerothermal qualification, and detailed ascent path are explicit nulls in input, not silently certified.");
 lines.push("**Thermal Gate D2/D4:** PASS if passive separate cold-water sensible-energy store lasts at least "+f(number(d.thermal.stay_requested_h))+"h after conduction through ideal spherical insulation, cabin electronics and 2/4 crew heat; no active cooling or hot-side power credited. Physical life-support and seals remain separate OPEN.");
 lines.push("**Phase ledger:** sampled for every scenario; representative detailed case below. Reaction water starts with "+f(vals(d,"water.reaction_water_initial_t"))+"t. Crew cold-water mass is a **different inventory**. Custody dry is counted ONCE; custody contents add wet mass ONCE.");
 const ex=a.examples[0],e=evaluate(d,stage,ex.inputs,a.geometry);
 for(const m of ["low","high"]){
 lines.push("**First sampled "+m+" exhaust mode: reaction-water phases**");
 lines.push("| Phase | before t | debit t | after t | Cold water t | Cold energy 2/4 crew remaining kWh | Jet GW | Custody |","|---|---:|---:|---:|---:|---|---:|---|");
 for(const row of e.venus.phaseLedger[m])lines.push("| "+row.phase+" | "+f(row.water_before_t)+" | "+f(row.water_debit_t)+" | "+f(row.water_after_t)+" | "+f(row.thermal_water_mass_t)+" | "+d.thermal.crew_cases.map(q=>f(row.thermal_energy_by_crew[number(q)].energy_after_J/number(d.si.joules_per_kWh))).join(" / ")+" | "+f(row.torch_jet_power_GW)+" | "+row.custody+" |");
 lines.push("Torch "+m+" at first sample: thrust "+f(e.venus.mode[m].thrustN)+"N, delta-v deliverable "+f(e.venus.mode[m].delta_v_orbit)+"km/s, orbit water "+f(e.venus.mode[m].waterAtOrbit)+"t, torch firing "+f(e.venus.mode[m].timeH)+"h.");
 }
 lines.push("**Nominal v1 comparator** (NOT a new debit): "+f(number(d.water.v1_venus_touchdown_belly_debit_t))+"t former belly touchdown already included in its "+f(number(d.water.v1_after_all_burns_remaining_t))+"t post-all-burn remaining figure; new rotor architecture never double subtracts it.");
 lines.push("**Thermal output first sample:** 2 crew max "+f(e.venus.thermal[2].maxHours)+"h, 4 crew max "+f(e.venus.thermal[4].maxHours)+"h; ambient table valid at surface; thermal bridge/radiation, active cooler, and heat-rejector design not qualified.");
 lines.push("**Reactor waste heat remains explicitly OPEN in every phase: `power.reactor_waste_heat_MW`; missing conversion and heat-rejection closure are not assigned zero. Required-but-OPEN physical interfaces**: "+["venus.torch_atmosphere_viability","venus.entry_vehicle_thermal_qualification","thermal.active_cooler_power_available_kW","thermal.hot_side_rejection_capacity_kW"].join(", ")+".");
 }
 lines.push("## Representative sample outcomes");
 lines.push("| # | Dry t | A | B | "+(stage===2?"Rotor | C | C low | C high | D2 | D4":"") +" |");
 lines.push("|---:|---:|---|---|"+(stage===2?"---|---|---|---|---|---|":"")+"|");
 for(const row of a.examples)lines.push("| "+row.sample+" | "+f(row.dry)+" | "+row.gates.A+" | "+row.gates.B+" | "+(stage===2?[row.gates.R,row.gates.C,row.gates.C_low,row.gates.C_high,row.gates.D2,row.gates.D4].join(" | ")+" | ":"")+"");
 lines.push("");
 lines.push("## Full input JSON: exact bytes determine run identity");
 lines.push("\`\`\`json",JSON.stringify(d,null,2),"\`\`\`");
 return lines.join("\n")+"\n";
}
function sideSVG(d,a){
 const g=a.geometry,p=number(d.sweep.svg_pixels_per_meter),pad=number(d.sweep.svg_margin_px),W=Math.ceil(g.hullL*p+2*pad),H=Math.ceil(g.hullD*p+3*pad),
 mid=pad+g.hullL*p/2,y=pad+g.hullD*p/2;
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'"><rect width="100%" height="100%" fill="#121b29"/>'+
 '<text x="'+pad+'" y="25" fill="#fff" font-size="16">SHUTTLE STOWED SCALE ENVELOPE — G8 FIT '+esc(a.geometry.gateB.status)+'</text>'+
 '<rect x="'+pad+'" y="'+(y-g.hullD*p/2)+'" width="'+(g.hullL*p)+'" height="'+(g.hullD*p)+'" rx="'+(g.hullD*p/4)+'" fill="#324b64" stroke="#80c7ee" stroke-width="2"/>'+
 '<line x1="'+(mid-g.rotorD*p/2)+'" y1="'+y+'" x2="'+(mid+g.rotorD*p/2)+'" y2="'+y+'" stroke="#ffcb83" stroke-width="5"/>'+
 '<circle cx="'+mid+'" cy="'+y+'" r="7" fill="#ffd18a"/>'+
 '<text x="'+pad+'" y="'+(H-50)+'" fill="#fff" font-size="13">'+esc(g.hullL+'m hull / '+g.availL.toFixed(2)+'m allowable bay; rotor '+g.rotorD+'m folded theoretical span')+'</text>'+
 '<text x="'+pad+'" y="'+(H-29)+'" fill="#ffcb83" font-size="13">Actual mast/hub/CG positions OPEN; this line is NOT a fit proof</text></svg>';
}
function waterfallSVG(d,a){
 const parts=a.partRows,limit=number(d.mass.max_docked_dry_t),W=1000,H=90+parts.length*27,scale=(W-350)/a.sums[2],barX=300;
 const rects=parts.map((r,i)=>{const x=barX+parts.slice(0,i).reduce((sum,v)=>sum+v.values[1],0)*scale,w=r.values[1]*scale,y=65+i*27;
 return '<text x="20" y="'+(y+13)+'" fill="#cde6ff" font-size="12">'+esc(r.name)+'</text>'+
 '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="19" fill="'+(i%2?"#ffcb82":"#70c9c4")+'"/>';
 }).join("");
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'"><rect width="100%" height="100%" fill="#121b29"/>'+
 '<text x="20" y="25" fill="#fff" font-size="18">DRY-MASS WATERFALL: MIDPOINT STACK (t)</text>'+
 '<text x="20" y="44" fill="#cde6ff" font-size="13">min '+a.sums[0].toFixed(2)+' | midpoint '+a.sums[1].toFixed(2)+' | max '+a.sums[2].toFixed(2)+' | GATE A '+esc(a.gates.A.pass_fraction===null?"OPEN":(100*a.gates.A.pass_fraction).toFixed(1)+"% PASS")+'</text>'+
 rects+'<line x1="'+(barX+limit*scale)+'" x2="'+(barX+limit*scale)+'" y1="48" y2="'+(H-22)+'" stroke="#ff6b76" stroke-dasharray="5 4" stroke-width="2"/>'+
 '<text x="'+(barX+limit*scale+5)+'" y="'+(H-10)+'" fill="#ff9fa5" font-size="12">'+limit+'t dry limit</text></svg>';
}

import {readFileSync,writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
const url=new URL("./shuttle_inputs.json",import.meta.url),raw=readFileSync(url,"utf8"),input=JSON.parse(raw);
const stage=number(input.run_stage),arg=process.argv.indexOf("--stage");
if(![1,2].includes(stage))throw Error("run_stage must be 1 or 2; Stage 3 held");
if(arg>=0&&Number(process.argv[arg+1])!==stage)throw Error("CLI stage mismatches JSON run_stage");
const identity=createHash("sha1").update("blob "+Buffer.byteLength(raw)+"\0"+raw).digest("hex");
const output=analyze(input,stage),fileRoot=new URL("./",import.meta.url);
for(const [name,content] of Object.entries({
 "SHUTTLE_SIZER_REPORT.md":report(input,stage,identity,output,["SHUTTLE_SIDE_VIEW.svg","SHUTTLE_MASS_WATERFALL.svg"]),
 "SHUTTLE_SIDE_VIEW.svg":sideSVG(input,output),
 "SHUTTLE_MASS_WATERFALL.svg":waterfallSVG(input,output)}))writeFileSync(new URL(name,fileRoot),content);
process.stdout.write(JSON.stringify({run_id:identity,stage,gates:output.gates},null,2)+"\n");
