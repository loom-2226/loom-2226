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
 const fields=fkeys(d,"mass").filter(k=>!["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t","kit_house_reactor_t"].includes(k)).map(k=>"mass."+k);
 fields.push("power.kit_house_reactor_thermal_MW");
 fields.push("kit.packed_effective_density_t_per_m3");
 if(stage===2)fields.push(...[
  ...fkeys(d,"power").filter(k=>["rotor_figure_of_merit","tipjet_thermal_to_useful_rotor","rotor_safe_tip_speed_mps","rotor_hot_duty_limit_h","rotor_climb_rate_mps","torch_low_ve_kmps","torch_high_ve_kmps","torch_jet_power_GW"].includes(k)).map(k=>"power."+k),
  ...fkeys(d,"water").filter(k=>["reaction_water_entry_debit_t","crew_water_cold_mass_t","crew_water_heating_delta_T_K"].includes(k)).map(k=>"water."+k),
  ...fkeys(d,"thermal").filter(k=>["insulation_k_W_per_mK","insulation_thickness_m","crew_heat_W_each","cabin_electronics_kW","venus_external_surface_K","active_cooler_power_available_kW","reactor_aux_electric_power_available_kW","hot_side_rejection_capacity_kW","hot_loop_reject_temperature_K","cooler_coefficient_of_performance"].includes(k)).map(k=>"thermal."+k),
  ...fkeys(d,"venus").filter(k=>["torch_ascent_dv_kmps"].includes(k)).map(k=>"venus."+k),
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
function reactorMass(d,s){
 const power=val(d,"power.kit_house_reactor_thermal_MW",s),
  specific=number(d.power.kit_house_reactor_net_specific_kW_per_kg),
  eta=number(d.power.kit_house_reactor_direct_conversion_efficiency),
  units=number(d.si.kW_per_MW);
 if([power,specific,eta,units].some(x=>x===null))return null;
 // kg = raw thermal MW * 1000 kW/MW / (net specific power / electrical fraction)
 return power*units/(specific/eta)/number(d.si.kg_per_t);
}
function componentMass(d,k,s){
 return k==="kit_house_reactor_t"?reactorMass(d,s):val(d,"mass."+k,s);
}
function surfaceCooling(d,s,crewCount){
 const needed=["thermal.venus_external_surface_K","thermal.insulation_k_W_per_mK",
  "thermal.insulation_thickness_m","thermal.cabin_electronics_kW","thermal.crew_heat_W_each",
  "geometry.crew_pod_outer_diameter_m","thermal.cabin_target_K","thermal.cooler_coefficient_of_performance"];
 const miss=needed.filter(k=>val(d,k,s)===null);
 if(miss.length)return {missing:miss};
 const r=val(d,"geometry.crew_pod_outer_diameter_m")/2,area=4*Math.PI*r*r;
 const leak=val(d,"thermal.insulation_k_W_per_mK",s)*area*
  (val(d,"thermal.venus_external_surface_K",s)-val(d,"thermal.cabin_target_K"))/
   val(d,"thermal.insulation_thickness_m",s);
 const loadW=leak+val(d,"thermal.cabin_electronics_kW",s)*number(d.si.W_per_kW)+
   crewCount*val(d,"thermal.crew_heat_W_each",s);
 const electricKW=loadW/number(d.si.W_per_kW)/val(d,"thermal.cooler_coefficient_of_performance",s);
 const conversion=number(d.power.kit_house_reactor_direct_conversion_efficiency);
 const thermalKW=electricKW/conversion;
 return {missing:[],loadW,leakW:leak,electricKW,thermalKW};
}
function dry(d,s){
 const excluded=new Set(["max_docked_dry_t","v1_comparison_dry_t","historical_lost_sizer_dry_t"]);
 const keys=Object.keys(d.mass).filter(x=>!excluded.has(x));
 const parts=keys.map(k=>({key:k,value:componentMass(d,k,s)}));
 const missing=parts.filter(x=>x.value===null).map(x=>"mass."+x.key);
 const sum=missing.length?null:parts.reduce((a,b)=>a+b.value,0);
 const kitKeys=d.kit.mass_component_keys;
 const kitMissing=kitKeys.filter(k=>componentMass(d,k,s)===null).map(k=>"mass."+k);
 const kitT=kitMissing.length?null:kitKeys.reduce((x,k)=>x+componentMass(d,k,s),0);
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
 const minimumAltitude=requirePath("venus.minimum_rotor_handover_screen_km");
 const climb=requirePath("power.rotor_climb_rate_mps"),maxHotH=requirePath("power.rotor_hot_duty_limit_h"),
 maxTip=requirePath("power.rotor_safe_tip_speed_mps");
 const rawThermal=requirePath("power.kit_house_reactor_thermal_MW");
 const cooling4=surfaceCooling(d,s,number(d.geometry.crew_pod_seats));
 missing.push(...cooling4.missing);
 const heatMax=rawThermal===null||cooling4.thermalKW===undefined?null:
   Math.max(0,rawThermal-cooling4.thermalKW/number(d.si.kW_per_MW));
 if(heatMax===null)missing.push("power.rotor_usable_input_heat_limit_MW");
 const rotorUpper=d.venus.atmosphere_profile[d.venus.atmosphere_profile.length-1].altitude_km;
 const step=requirePath("sweep.handover_step_km"),requiredDV=requirePath("venus.torch_ascent_dv_kmps");
 const jetGW=requirePath("power.torch_jet_power_GW");
 let rotorGate={status:"OPEN",missing:[...new Set(missing)]},handover=null,altProfile=[],flightTimeH=null;
 const baseMass=dryT===null||reactionStart===null||thermalT===null||cargoT===null?null:dryT+reactionStart+thermalT+cargoT;
 if(!rotorGate.missing.length){
   // Sampled rotor climb boundary, not an aerodynamic/structural rotor qualification.
   let accepted=null;
   for(let h=0;h<=rotorUpper+Number.EPSILON;h+=step){
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
   ["power.torch_jet_power_GW",jetGW],["power.kit_house_reactor_thermal_MW",rawThermal],
   ["power.rotor_usable_input_heat_limit_MW",heatMax],
   ["venus.minimum_rotor_handover_screen_km",minimumAltitude],["power.rotor_climb_rate_mps",climb],
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
   const rawHouseKW=rawThermal*number(d.si.kW_per_MW);
   const directEfficiency=number(d.power.kit_house_reactor_direct_conversion_efficiency);
   const houseNetKW=rawHouseKW*directEfficiency;
   const electricalMax=Math.min(houseNetKW,val(d,"thermal.active_cooler_power_available_kW",s),
      val(d,"thermal.reactor_aux_electric_power_available_kW",s));
   const minStableRawKW=rawHouseKW*number(d.power.kit_house_reactor_min_stable_fraction);
   const allocatedRawKW=coolerKW/directEfficiency;
   // Surface rotor OFF: 10% minimum house-reactor gross thermal output must go somewhere.
   // No unqualified exterior torch exhaust, flywheel, dump-to-cloud heat sink or stored heat credited.
   const minimumWasteKW=Math.max(0,minStableRawKW-allocatedRawKW);
   const netRejectionKW=coldLoadW/number(d.si.W_per_kW)+allocatedRawKW+minimumWasteKW;
   const rejectMax=val(d,"thermal.hot_side_rejection_capacity_kW",s);
   const temperatureOK=val(d,"thermal.hot_loop_reject_temperature_K",s)>surface;
   const massOK=dryResult.a2==="PASS" && dryResult.kitT<=number(d.kit.payload_allowance_t);
   const activeOK=temperatureOK&&massOK&&coolerKW<=electricalMax&&netRejectionKW<=rejectMax;
   thermal[crewCount]={status:activeOK?"PASS":"FAIL",missing:[],podHours,
     maxHours:null,loadW:coldLoadW,leakW:leak,capacityJ:sensibleJ,
     coolerElectricalKW:coolerKW,reactorBusLimitKW:electricalMax,
     rejectKW:netRejectionKW,rejectLimitKW:rejectMax,minimumReactorWasteKW:minimumWasteKW,reactorMinStableRawKW:minStableRawKW,
     reactorThermalMW:rawThermal,rotorHeatBudgetMW:heatMax,
     temperatureOK,massOK,coldWaterPreservedForPod:true};
 }
 const gateC=rotorGate.status==="OPEN"?"OPEN":
  modes.low.status==="PASS"||modes.high.status==="PASS"?"PASS":
  modes.low.status==="OPEN"||modes.high.status==="OPEN"?"OPEN":"FAIL";
 const waterOpen=[...new Set([...rotorGate.missing,...(modes.low.missing||[]),...(modes.high.missing||[])])];
 return {rotor:rotorGate,gateC,waterMissing:waterOpen,handover,flightTimeH,baseMass,mode:modes,thermal,reactorThermalMW:rawThermal,rotorHeatBudgetMW:heatMax,reactorCoolerRawKW:cooling4.thermalKW,
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
       reactor_waste_heat_MW:phase==="surface stay"&&thermal[2]?.minimumReactorWasteKW!==undefined?thermal[2].minimumReactorWasteKW/number(d.si.kW_per_MW):null,
        reactor_waste_heat_missing:"power.reactor_waste_heat_MW (main torch waste still OPEN; kit-house minimum surplus computed for surface)",
        kit_house_reactor_thermal_MW:val(d,"power.kit_house_reactor_thermal_MW",s),
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
    else if(gateKey==="R")margin=(e.venus?.handover??0)-number(d.venus.minimum_rotor_handover_screen_km);
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
 const handovers=[];
 const podRanges=Object.fromEntries(d.thermal.crew_cases.map(q=>[number(q),{min:Infinity,max:-Infinity}]));
 const extensions=stage===2?Object.fromEntries(d.venus.rotor_extension_levels_km.map(q=>[number(q),{rotorMin:Infinity,rotorMax:-Infinity,heatMin:Infinity,heatMax:-Infinity,pressure_bar:null}])):{};
 for(let i=0;i<design.rows;i++){
  const s=design.get(i),e=evaluate(d,stage,s,geo);
  rows.push({A:e.A,A2:e.A2,KV:e.KV,KF:e.KF,B:e.B,R:e.R,C:e.C,C_low:e.C_low,C_high:e.C_high,DS2:e.DS2,DS4:e.DS4});
  if(stage===2){if(e.venus.handover!==null)handovers.push(e.venus.handover);
   for(const q of d.thermal.crew_cases){const crew=number(q),hours=e.venus.thermal[crew]?.podHours; if(Number.isFinite(hours)){podRanges[crew].min=Math.min(podRanges[crew].min,hours);podRanges[crew].max=Math.max(podRanges[crew].max,hours);}}
   for(const q of d.venus.rotor_extension_levels_km){const alt=number(q),p=extensions[alt],rot=rotorAt(d,s,e.venus.baseMass,alt);
     if(rot){p.rotorMin=Math.min(p.rotorMin,rot.shaftMW);p.rotorMax=Math.max(p.rotorMax,rot.shaftMW);
       p.heatMin=Math.min(p.heatMin,rot.sourceMW);p.heatMax=Math.max(p.heatMax,rot.sourceMW);p.pressure_bar=rot.air.pressure;}}
  }
  if(i<number(d.sweep.report_preview_samples))exemplars.push({sample:i,inputs:s,gates:rows.at(-1),dry:e.dry.sum,coreDry:e.dry.coreT,kit:e.kit,venus:stage===2?{
    handover:e.venus.handover,reactorThermal:e.venus.reactorThermalMW,rotorHeatBudget:e.venus.rotorHeatBudgetMW,
    lowWater:e.venus.mode.low.waterAtOrbit,highWater:e.venus.mode.high.waterAtOrbit,
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
 const sortedHandovers=handovers.sort((x,y)=>x-y);
 const clouds=d.research.idle_tipjet_heat;
 const handoverStats={resolved:sortedHandovers.length,failed:stage===2?design.rows-sortedHandovers.length:null,
  min:sortedHandovers[0]??null,max:sortedHandovers.at(-1)??null,
  median:sortedHandovers.length?sortedHandovers[Math.floor((sortedHandovers.length-1)/2)]:null,
  atCloudBase:sortedHandovers.filter(v=>v>=number(clouds.venus_cloud_base_km)).length,
  aboveCloudTop:sortedHandovers.filter(v=>v>=number(clouds.venus_cloud_top_km)).length};
 const kitRows=partRows.filter(x=>d.kit.mass_component_keys.includes(x.name));
 const kitSums=[0,1,2].map(i=>kitRows.reduce((z,x)=>z+x.values[i],0));
 return {geometry:geo,gates,joint,scores,examples:exemplars,partRows,sums,kitRows,kitSums,podRanges,extensions,handoverStats,design:{rows:design.rows,fields:design.fields}};
}
function idleTipjetSensitivity(d,a){
 // RESEARCH ONLY: never invoked by evaluate(), samples(), dry(), gate(), or sensitivity().
 // All numeric boundaries are sourced from non-gate JSON and current VIRA altitude table.
 const spec=d.research.idle_tipjet_heat;
 const levels=number(d.sweep.sample_levels),heightStep=number(d.sweep.handover_step_km);
 const heat=Array.from({length:levels},(_,i)=>spec.hypothetical_delivered_tipjet_heat_MW.min+
    (spec.hypothetical_delivered_tipjet_heat_MW.max-spec.hypothetical_delivered_tipjet_heat_MW.min)*i/(levels-1));
 const modes=["OPTIMISTIC","MIDPOINT","PESSIMISTIC"];
 const massT=[
  a.sums[0]+val(d,"water.reaction_water_initial_t")+d.water.crew_water_cold_mass_t.min+d.capsule.content_mass_t.min,
  a.sums[1]+val(d,"water.reaction_water_initial_t")+
     (d.water.crew_water_cold_mass_t.min+d.water.crew_water_cold_mass_t.max)/2+
     (d.capsule.content_mass_t.min+d.capsule.content_mass_t.max)/2,
  a.sums[2]+val(d,"water.reaction_water_initial_t")+d.water.crew_water_cold_mass_t.max+d.capsule.content_mass_t.max
 ];
 const fms=[d.power.rotor_figure_of_merit.max,
    (d.power.rotor_figure_of_merit.min+d.power.rotor_figure_of_merit.max)/2,d.power.rotor_figure_of_merit.min];
 const effs=[d.power.tipjet_thermal_to_useful_rotor.max,
    (d.power.tipjet_thermal_to_useful_rotor.min+d.power.tipjet_thermal_to_useful_rotor.max)/2,d.power.tipjet_thermal_to_useful_rotor.min];
 const top=d.venus.atmosphere_profile[d.venus.atmosphere_profile.length-1].altitude_km;
 const demands=[],ceilings=[];
 for(let k=0;k<modes.length;k++){
  const sample={"power.rotor_figure_of_merit":fms[k],"power.tipjet_thermal_to_useful_rotor":effs[k]};
  const rows=d.venus.rotor_extension_levels_km.map(o=>{
   const z=rotorAt(d,sample,massT[k],number(o));
   return {case:modes[k],massT:massT[k],fm:fms[k],efficiency:effs[k],alt_km:number(o),
     pressure_bar:z.air.pressure,shaftMW:z.shaftMW,required_tipjet_MW:z.sourceMW};
  });
  demands.push(...rows);
  for(const budget of heat){
   let ceiling=null;
   for(let h=0;h<=top;h+=heightStep){
     const v=rotorAt(d,sample,massT[k],h);
     if(!v||v.sourceMW>budget)break;
     ceiling=h;
   }
   ceilings.push({case:modes[k],budgetMW:budget,ceiling_km:ceiling,
     reaches_cloud_base:ceiling!==null&&ceiling>=d.research.idle_tipjet_heat.venus_cloud_base_km.value,
     above_cloud_top:ceiling!==null&&ceiling>=d.research.idle_tipjet_heat.venus_cloud_top_km.value,
     upper_profile_limit:top});
  }
 }
 return {modes,heat,demands,ceilings,scope:spec.case_scope};
}
function report(d,stage,hash,a,graphics){
 const p=number(d.sweep.round_decimals),f=x=>fmt(x,p),v=(path)=>vals(d,path),first=a.examples[0],rows=[];
 const add=(...line)=>rows.push(...line);
 add("# LOOM Shuttle Sizer v1 — Stage "+stage+" (round 5)","ALL bodies. ALL sponsors. 2026–2226.","",
 "**Authority:** NON-CANON engineering screen, all ranges/provenance from the attached input JSON; numerical PASS is not hardware certification.",
 "**Run identity:** Git-blob SHA-1 of exact input JSON (includes stage): \`"+hash+"\`.",
 "**Reproduce:** \`node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage "+stage+"\`.",
 "**CLI validation record:** "+d.origin.cli_validation.status+" for previous round-2 Stage 2 commit, confirmed by Claude as reported by kT; this round-5 executable was evaluated in JS against hashed inputs; a new independent Node CLI execution is not claimed.",
 "**Graphics:** "+graphics.join(", ")+".","",
 "## Computed gates, same scenario samples",
 "Deterministic coordinate-balanced min/mid/max design: "+a.design.rows+" samples, "+a.design.fields.length+" independent swept inputs. PASS fraction is a **design fraction**, NOT a probability of a flight-ready vehicle.",
 "| Gate | PASS | FAIL | OPEN | PASS / resolved |",
 "|---|---:|---:|---:|---:|");
 for(const [name,g] of Object.entries(a.gates))add("| "+name+" | "+g.PASS+" | "+g.FAIL+" | "+g.OPEN+" | "+(g.pass_fraction===null?"n/a":f(100*g.pass_fraction)+"%")+" |");
 if(stage===2){
  add("","### Joint closure, same samples","| Combined gates | PASS | FAIL | OPEN | PASS / resolved |","|---|---:|---:|---:|---:|");
  for(const [name,g] of Object.entries(a.joint))add("| "+name+" | "+g.PASS+" | "+g.FAIL+" | "+g.OPEN+" | "+(g.pass_fraction===null?"n/a":f(100*g.pass_fraction)+"%")+" |");
 }
 add("","### A vs A2 dry mass (kit separated from shuttle)",
 "Original fully-equipped dry min / mid / max: **"+a.sums.map(f).join(" / ")+" t**.",
 "Detachable Venus/Titan kit min / mid / max: **"+a.kitSums.map(f).join(" / ")+" t**.",
 "Docked shuttle core dry WITHOUT Venus kit min / mid / max: **"+a.sums.map((x,i)=>f(x-a.kitSums[i])).join(" / ")+" t**. A2 applies the "+f(number(d.mass.max_docked_dry_t))+"t G8 docked dry limit to CORE only. A applies the same bound to the fully equipped vehicle as a comparator.",
 "Historical lost-sizer dry "+f(number(d.mass.historical_lost_sizer_dry_t))+"t (not a fit target), current mid minus history "+f(a.sums[1]-number(d.mass.historical_lost_sizer_dry_t))+"t. Earlier v1 comparison "+f(number(d.mass.v1_comparison_dry_t))+"t.");
 
 add("| Dry component | min t | mid t | max t | Kit? | provenance |","|---|---:|---:|---:|---|---|");
 for(const part of a.partRows)add("| "+part.name+" | "+part.values.map(f).join(" | ")+" | "+(d.kit.mass_component_keys.includes(part.name)?"VENUS/TITAN payload":"CORE")+
     " | "+part.provenance+" |");
 add("","### B stowed shuttle and Wayfarer G8 clearance",
 "Necessary hull fit "+(a.geometry.necessary?"PASS":"FAIL")+". Hull length "+f(a.geometry.hullL)+"m vs allowed "+f(a.geometry.availL)+"m, hull diameter "+f(a.geometry.hullD)+"m vs allowed "+f(a.geometry.availD)+"m. Remaining allocated axial and radial margins: "+f(a.geometry.axialClearance)+"m / "+f(a.geometry.radialClearance)+"m. Ideal folded span "+f(a.geometry.nominalFoldSpan)+"m.",
 "Full B remains "+a.geometry.gateB.status+" owing to explicit nulls: "+a.geometry.gateB.missing.join(", ")+".",
 "### Detachable kit and service holds",
 "Kit components: "+d.kit.mass_component_keys.join(", ")+". Thermal pod core insulation/habitat remains in shuttle; detachable hot-loop and active cooler are kit mass and must not be added again.",
 "Kit mass min/mid/max "+a.kitSums.map(f).join(" / ")+" t against total Wayfarer payload allowance "+f(number(d.kit.payload_allowance_t))+"t. Thus remaining allowance for other cargo at those three cases: "+a.kitSums.map(x=>f(number(d.kit.payload_allowance_t)-x)).join(" / ")+" t.",
 "G8 certified hold inventory: two service holds "+f(number(d.kit.holds_total_m3))+"m³ gross; "+f(number(d.kit.holds_free_m3))+"m³ free after drones. Service x "+f(number(d.kit.service_x_start_m))+"–"+f(number(d.kit.service_x_end_m))+"m. Packed effective density "+d.kit.packed_effective_density_t_per_m3.min+"–"+d.kit.packed_effective_density_t_per_m3.max+" t/m³ is ASSUMPTION, not a container design.",
 "Four "+f(number(d.geometry.rotor_diameter_m)/2)+"m blades hypothetically split into "+f(number(d.kit.rotor_blade_segments_per_blade))+" segments per blade; segment length "+
 f((number(d.geometry.rotor_diameter_m)/2)/number(d.kit.rotor_blade_segments_per_blade))+"m versus "+f(number(d.kit.service_x_end_m)-number(d.kit.service_x_start_m))+"m service length, necessary-only PASS. Full blade connector integrity and stow/reassemble geometry still OPEN.",
 "Kit packed-volume gate KV is computed PASS/FAIL per sample. Full kit physical fit KF is OPEN if total volume passes but **kit.individual_hold_aperture_m, kit.individual_hold_cross_section_m2, kit.rotor_blade_joint_qualified, kit.hot_shuttle_kit_fit_qualified** remain null; a sample exceeding total volume is a determinate FAIL. Free volume does not prove two separate holds can accept the pieces.",
 "First sample: kit mass "+f(first.kit.mass_t)+"t, estimated packed volume "+f(first.kit.packedVolume_m3)+"m³, KV="+first.kit.volumeGate+", KF="+first.kit.fit+".",
 "","## Three strongest input sensitivities per computable gate",
 "Each input is set to min / mid / max across "+number(d.sweep.sensitivity_count)+" deterministic OAT baselines; rank by change in PASS fraction, then physical margin if PASS never changes.",
 "B and full KF have no honest min/mid/max influence ranking until required individual geometry/qualification inputs exist.");
 for(const [k,list]of Object.entries(a.scores)){
  add("**"+k+"**","| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |","|---|---|---:|---:|");
  for(const item of list)add("| "+item.field+" | "+item.passRates.map(x=>x===null?"OPEN":f(100*x)).join(" / ")+" | "+
   (item.flipSpread===null?"OPEN":f(100*item.flipSpread))+" | "+f(item.marginShift)+" |");
  add("");
 }
 add("## Three mass-driver research checks (not automatic certification)",
 "### Torch 7.7 GW-class source and approved 2226 lineage",
 "**KT DECISION — DECLARED_2226:** Shuttle 4–10 t engine minimum-size floor is unchanged. Wayfarer working ledger total "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_propulsion_allocation_t))+" t = "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_reactor_t))+" reactor + "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_shadow_shield_t))+" shield + "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_magnetic_nozzle_t))+" nozzle, for "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_jet_power_TW))+" TW jet. The derived specific jet-power per aggregate propulsion kilogram is "+
 f(number(d.research.torch_source.lineage_mass_basis.wayfarer_jet_power_TW)*number(d.si.W_per_TW)/
 (number(d.research.torch_source.lineage_mass_basis.wayfarer_propulsion_allocation_t)*number(d.si.kg_per_t)*number(d.si.W_per_kW)))+
 " kW/kg, so a "+f(number(d.research.torch_source.lineage_mass_basis.shuttle_jet_power_class_GW))+" GW-class ideal proportional engine would be "+
 f(number(d.research.torch_source.lineage_mass_basis.shuttle_jet_power_class_GW)*number(d.si.W_per_GW)/
 (number(d.research.torch_source.lineage_mass_basis.wayfarer_jet_power_TW)*number(d.si.W_per_TW)/
 number(d.research.torch_source.lineage_mass_basis.wayfarer_propulsion_allocation_t)))+
 " t. This is **not** physical miniaturization proof; kT declares a larger 4–10t minimum-size floor. No canon changed.",
 "**RESEARCH NOTE — 2026 DFD gap is real and applies equally to Wayfarer.** Repo [torch energy partition / specific power](https://github.com/loom-2226/loom-2226/blob/main/src/wayfarer_torch_energy_partition_mass_feasibility.py) leaves directed fraction and source specific power OPEN. [Jain and Kakade 2023](https://doi.org/10.1016/j.actaastro.2023.02.011) and [Princeton DFD](https://psatellite.com/technology/fusion/) discuss MW-class conceptual systems, not compact GW hardware. The 2026 research bands below diagnose the 200-year technological extrapolation, not an override of DECLARED_2226.",
 "At "+f(number(d.research.torch_source.targeted_shuttle_torch_jet_power_GW))+" GW ideal jet power, even optimistic study source specific power "+
 d.research.torch_source.dfd_ambitious_specific_power_kW_per_kg.min+"–"+d.research.torch_source.dfd_ambitious_specific_power_kW_per_kg.max+" kW/kg implies **"+
 f(number(d.research.torch_source.targeted_shuttle_torch_jet_power_GW)*number(d.si.W_per_GW)/(d.research.torch_source.dfd_ambitious_specific_power_kW_per_kg.max*number(d.si.W_per_kW)*number(d.si.kg_per_t)))+"–"+
 f(number(d.research.torch_source.targeted_shuttle_torch_jet_power_GW)*number(d.si.W_per_GW)/(d.research.torch_source.dfd_ambitious_specific_power_kW_per_kg.min*number(d.si.W_per_kW)*number(d.si.kg_per_t)))+" t** SOURCE-ONLY, before power partition and shielding. Consequently "+f(d.mass.torch_low_high_engine_t.min)+"–"+f(d.mass.torch_low_high_engine_t.max)+"t torch engine remains DECLARED_2226 at the approved 4–10 t floor. The `>=77t` 2026 research comparison is a technology-gap diagnostic, not a constraint on the fictional 2226 assumption; 2026 scaling limitations apply to Wayfarer as well.",
 "### Biconic hull and thermal structure",
 "NASA [Venus aeroshell](https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf) models "+f(number(d.research.hull.venus_aeroshell_reference_diameter_m))+"m expendable entry body, "+f(number(d.research.hull.venus_aeroshell_reference_structure_t))+"t Ti-composite structure and "+f(number(d.research.hull.venus_aeroshell_reference_TPS_t))+"t HEEET, excluding the "+f(number(d.geometry.hull_diameter_m))+"m × "+f(number(d.geometry.hull_length_m))+"m reusable shuttle with hot rotor mount, keel and rover loads. The "+f(d.mass.hull_thermal_structure_t.min)+"–"+f(d.mass.hull_thermal_structure_t.max)+"t kT range cannot be credibly narrowed from that analog. It stays ASSUMPTION.",
 "### 2.8m OD titanium pressure sphere",
 "[Alvin classification comparison](https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en): "+f(number(d.research.sphere.alvin_wall_mm))+"mm wall for "+f(number(d.research.sphere.alvin_reference_depth_m))+"m ocean depth; [Limiting Factor](https://caladanoceanic.com/home/technology/sub/): "+f(number(d.research.sphere.limiting_factor_wall_mm))+"mm at "+f(number(d.research.sphere.limiting_factor_depth_m))+"m, smaller "+f(number(d.research.sphere.limiting_factor_pressure_hull_inner_diameter_m))+"m inside diameter. [Elastic-plastic buckling](https://doi.org/10.1016/j.marstruc.2017.09.007) flags shape imperfections. Neither qualifies a hot 4-crew Venus vessel; hatch reinforcement remains "+d.research.sphere.hatch_penetration_reinforcement_mass_t.provenance+".");
 const sphere=d.research.sphere,r=number(d.geometry.crew_pod_outer_diameter_m)/2,rho=number(sphere.material_density_kg_per_m3),
   po=(number(d.geometry.crew_pod_pressure_ext_bar)-number(d.geometry.crew_pod_pressure_int_bar))*number(d.si.Pa_per_bar),
   sample=[0,1,2].map(i=>{
      const shell=a.partRows.find(x=>x.name==="pressure_pod_titanium_shell_t").values[i],
       innerR=Math.cbrt(r*r*r-3*shell*number(d.si.kg_per_t)/(4*Math.PI*rho)),
       thickness=r-innerR;
      const e=[sphere.titanium_hot_modulus_GPa.min,(sphere.titanium_hot_modulus_GPa.min+sphere.titanium_hot_modulus_GPa.max)/2,sphere.titanium_hot_modulus_GPa.max][i]*number(d.si.Pa_per_GPa),
       kd=[sphere.knockdown.min,(sphere.knockdown.min+sphere.knockdown.max)/2,sphere.knockdown.max][i],
       sf=[sphere.safety_factor.max,(sphere.safety_factor.min+sphere.safety_factor.max)/2,sphere.safety_factor.min][i],
       allow=[sphere.titanium_allowable_stress_MPa.min,(sphere.titanium_allowable_stress_MPa.min+sphere.titanium_allowable_stress_MPa.max)/2,sphere.titanium_allowable_stress_MPa.max][i]*number(d.si.Pa_per_MPa);
      const pcr=2*e/Math.sqrt(3*(1-number(sphere.poisson_ratio)**2))*(thickness/r)**2;
      const stress=2*allow*thickness/r;
      return {shell,thickness_mm:thickness*number(d.si.millimeters_per_meter),p_allow_bar:Math.min(pcr*kd,stress)/sf/number(d.si.Pa_per_bar),p_req_bar:po/number(d.si.Pa_per_bar)};
   });
 add("Analytic perfect-sphere elastic buckling with independent **assumed knockdown and safety factor**, plus simple membrane compression, against "+f(po/number(d.si.Pa_per_bar))+" bar differential. This is a screen, **not** real-hatch, penetration or thermal-cycle buckling qualification.",
 "| Shell mass t | Nominal wall thickness mm | allowable differential pressure bar | required bar | screen |","|---:|---:|---:|---:|---|");
 for(const q of sample)add("| "+f(q.shell)+" | "+f(q.thickness_mm)+" | "+f(q.p_allow_bar)+" | "+f(q.p_req_bar)+" | "+(q.p_allow_bar>=q.p_req_bar?"PASS ANALYTIC ONLY":"FAIL ANALYTIC")+" |");
 add("Knockdown "+f(sphere.knockdown.min)+"–"+f(sphere.knockdown.max)+", SF "+f(sphere.safety_factor.min)+"–"+f(sphere.safety_factor.max)+
 ", modulus "+f(sphere.titanium_hot_modulus_GPa.min)+"–"+f(sphere.titanium_hot_modulus_GPa.max)+"GPa, allowable compressive stress "+
 f(sphere.titanium_allowable_stress_MPa.min)+"–"+f(sphere.titanium_allowable_stress_MPa.max)+"MPa are all ASSUMPTION; hatch/penetration stress concentrations and Venus hot material strength OPEN. Do not narrow the shell mass until these are resolved.");
 // Round-4 idle heat research sensitivity, always non-gate (both stages).
 const idle=idleTipjetSensitivity(d,a),ref=d.research.idle_tipjet_heat;
 add("","## Round 4 research sensitivity: torch IDLE, heated CO2 tip jets (NEVER credited to gates)",
 "**kT hypothesis:** reactor no-thrust idle at "+f(100*ref.idle_fraction_of_nominal_jet.min)+"–"+f(100*ref.idle_fraction_of_nominal_jet.max)+
 "% of "+f(number(d.research.torch_source.lineage_mass_basis.shuttle_jet_power_class_GW))+"GW working jet reference = "+
 f(ref.idle_fraction_of_nominal_jet.min*number(d.research.torch_source.lineage_mass_basis.shuttle_jet_power_class_GW)*number(d.si.MW_per_GW))+
 "–"+f(ref.idle_fraction_of_nominal_jet.max*number(d.research.torch_source.lineage_mass_basis.shuttle_jet_power_class_GW)*number(d.si.MW_per_GW))+
 "MW numerical comparison. The independently **ASSUMED delivered** thermal budgets "+idle.heat.map(f).join("/")+
 "MW are **NOT** a derived heat-transfer efficiency, guaranteed fusion output, or actual reactor availability. No physical model maps 7.7GW jet to idle thermal power; that mapping is "+ref.heat_transfer_efficiency.provenance+".",
 "**Wayfarer authority is NOT idle:** raw "+f(number(ref.wayfarer_torch_tap_raw_MW))+"MW × "+
 f(number(ref.wayfarer_torch_tap_conversion))+" during the BURN ONLY gives "+
 f(number(ref.wayfarer_torch_tap_net_MWe))+"MWe magnet supply and "+
 f(number(ref.wayfarer_torch_tap_waste_MW))+"MW conversion waste. A burn-only energy tap does not establish a stationary reactor heater.",
 "**Minimum stable fusion / turndown:** [PSS Starfire/PFRC](https://psatellite.com/technology/fusion/) projects MW-scale steady-power capability; [PPPL PFRC](https://www.pppl.gov/Princeton-Field-Reversed-Configuration) studies RF-driven FRCs; [Jain & Kakade](https://doi.org/10.1016/j.actaastro.2023.02.011) identify RF recirculation and sustained-plasma challenges; [Nature FRC demonstration](https://www.nature.com/articles/s41467-025-58849-5) validates limited experimental FRC formation, not a GW fusion powerplant. **No published qualified minimum stable fusion power, 0.5–3% turndown, or exhaustless operation for this reactor lineage was found.** These are OPEN, not failed gate inputs.",
 "**Heat path:** a 2226 source-to-hot-loop exchanger → high-temperature duct manifold → retracted mast/rotating union → four hollow rotor blades → CO₂ tip jets. The source must transfer charged-particle/radiative energy without a main plume, hold the FRC operating point, avoid net reaction exhaust, and dissipate unrecovered thermal power. [NASA exchanger material-interface research](https://ntrs.nasa.gov/citations/20230005988) and [NEP heat-pipe sizing](https://ntrs.nasa.gov/citations/20220013111) establish substantial temperature, fatigue, duct-pressure and exchanger-mass concerns but no validated GW-specific 2226 mass range. Exchanger mass, flow, insulation, rotating union and hot-mast heat leak remain OPEN; no credits or new dry-mass guesses.",
 "**Conditional rotor demand at 30/40/50 km**, using original VIRA table and min/mid/max total wet mass, figure of merit and tip-jet efficiency. The *mass and aerodynamic assumptions are the sizer's existing ranges*, not invented reactor performance.",
 "| Rotor case | Wet t | FM | source→rotor | altitude km | ambient bar | shaft MW | required hot-gas input MW |",
 "|---|---:|---:|---:|---:|---:|---:|---:|");
 for(const z of idle.demands)add("| "+z.case+" | "+f(z.massT)+" | "+f(z.fm)+" | "+f(z.efficiency)+" | "+f(z.alt_km)+" | "+
 f(z.pressure_bar)+" | "+f(z.shaftMW)+" | "+f(z.required_tipjet_MW)+" |");
 add("","**Heat-only ceiling, VIRA profile, no atmospheric/nozzle qualification.** At each independently assumed delivered heat level, climb only while required tip-jet input is no larger than budget. This ignores rotor safe-tip-speed, hot duty, mast/exchanger loss and reactor start/restart, so reported ceilings are optimistic *heat-only* bounds, NOT Gate R or C.",
 "| Rotor case | hypothetical delivered heat MW | thermal rotor ceiling km | cloud-base reached? | **above cloud TOP?** |",
 "|---|---:|---:|---|---|");
 for(const z of idle.ceilings)add("| "+z.case+" | "+f(z.budgetMW)+" | "+f(z.ceiling_km)+" | "+
 (z.reaches_cloud_base?"yes":"no")+" | "+(z.above_cloud_top?"yes":"no")+" |");
 add("","Cloud-base "+f(number(ref.venus_cloud_base_km))+"km; cloud-top "+f(number(ref.venus_cloud_top_km))+
 "km, screen references only. **Entering the clouds is NOT lighting the torch above the clouds.** An ABOVE-CLOUD-TOP result would still not certify magnetic-nozzle plume operation at local density or guarantee reactor idle mode. Jet-power throttling and thermal routing are not demonstrated.",
 "**STOP / HOLDS:** idle fusion power stability, extraction efficiency, exhaust-free containment, rotating joint, heat exchanger/duct mass, and heat transfer to tipjets are all OPEN. Existing A/A2/B/C/D and existing statistical sensitivity ranking are not altered by this isolated calculation.");

 if(stage===2){
 add("","## Stage 2: Venus rotor and torch, D-shuttle vs D-pod",
 "**Rotor:** one "+f(number(d.geometry.rotor_diameter_m))+"m disk, VIRA atmosphere, sampled rotor FM and hot-gas conversion, kT-approved 100–230MW independent kit house reactor plus active cabin electrical debits and rotor hot-duty/tip-speed screens. Handover is an OUTPUT (no imposed 25km ceiling) with "+f(number(d.venus.minimum_rotor_handover_screen_km))+"km necessary minimum screening height; actual aerodynamic climb not certified.",
 "**Torch:** thrust per mode = 2 × Pjet / ve and propellant rate = 2 × Pjet / ve². Required Δv and resulting water-at-orbit are calculated per sample, with separate reaction/crew water and custody payload; never negative reaction-water stock. C is conditional on the rotor arithmetic gate, not dense-CO₂ plume viability.",
 "**D-shuttle:** "+f(number(d.thermal.stay_requested_h))+"h on Venus with pod docked and cold-water store preserved. The kit D–He3 house reactor (NOT the torch) provides electrical source. Cooler draws cabin load/COP, converted at "+f(number(d.power.kit_house_reactor_direct_conversion_efficiency))+" fraction; the reactor must also run above "+f(number(d.power.kit_house_reactor_min_stable_fraction))+" of rated gross thermal power. Minimum unconsumed thermal power is **charged to the hot-side rejection ledger**, not deleted. PASS needs cooler, bus, reactor net, hot-loop sink and A2/kit payload mass to close. Cycling, batteries, hot-gas purge and reactor shutdown are NOT credited without named inputs.",
 "**D-pod:** detached pod, cold-water sensible storage only; **maximum passive hours are OUTPUT** without an invented survival-duration target. No D-pod PASS/FAIL criterion. Passive pod heat load includes electronics and actual crew count.",
 "| Crew | minimum detached pod hours | maximum detached pod hours |","|---:|---:|---:|");
 for(const q of d.thermal.crew_cases){const count=number(q),b=a.podRanges[count];add("| "+count+" | "+f(b.min)+" | "+f(b.max)+" |");}
 add("","**Independent best/worst parameter corners (not contained in every balanced sample):**");
 for(const q of d.thermal.crew_cases){
   const crew=number(q),r=number(d.geometry.crew_pod_outer_diameter_m)/2,area=4*Math.PI*r*r;
   const hot=d.thermal.venus_external_surface_K,cold=number(d.thermal.cabin_target_K),K=d.thermal.insulation_k_W_per_mK,T=d.thermal.insulation_thickness_m;
   const el=d.thermal.cabin_electronics_kW,heat=d.thermal.crew_heat_W_each;
   const water=d.water.crew_water_cold_mass_t,window=d.water.crew_water_heating_delta_T_K,cp=number(d.water.crew_water_heat_capacity_J_per_kg_K);
   const bestLoad=K.min*area*(hot.min-cold)/T.max+el.min*number(d.si.W_per_kW)+crew*heat.min;
   const worstLoad=K.max*area*(hot.max-cold)/T.min+el.max*number(d.si.W_per_kW)+crew*heat.max;
   const best=water.max*number(d.si.kg_per_t)*cp*window.max/bestLoad/number(d.si.seconds_per_hour);
   const worst=water.min*number(d.si.kg_per_t)*cp*window.min/worstLoad/number(d.si.seconds_per_hour);
   add("- "+crew+" crew passive pod: mathematical parameter corner **"+f(worst)+"–"+f(best)+" hours**. Balanced-sample observed maximum "+f(a.podRanges[crew].max)+" hours. No minimum required stay time.");
 }
 add("","### Kit house-reactor power and computed handover",
 "Wayfarer-lineage kit reactor thermal output "+f(d.power.kit_house_reactor_thermal_MW.min)+"–"+f(d.power.kit_house_reactor_thermal_MW.max)+" MW; derived net specific power "+f(number(d.power.kit_house_reactor_net_specific_kW_per_kg))+"kW/kg @ "+f(100*number(d.power.kit_house_reactor_direct_conversion_efficiency))+"% conversion, reactor mass "+f(d.mass.kit_house_reactor_t.min)+"–"+f(d.mass.kit_house_reactor_t.max)+"t plus "+
 f(d.mass.kit_house_exchanger_ducts_t.min)+"–"+f(d.mass.kit_house_exchanger_ducts_t.max)+"t additional exchanger/ducts. BOTH included once in kit payload and wet-ascent mass, never A2 core mass.",
 "Simultaneous rotor+cooler budget per scenario: **rotor raw heat max = reactor gross thermal − (four-crew cooler electrical / 0.75)**. This is a raw heat upper bound with a DECLARED_2226 perfect heat-transfer interface, NOT independently qualified CO2 exchanger or mast. At 18h surface stay, rotor OFF; 10% min-stable thermal reactor power must be transferred/rejected, producing large heat-disposal demand.",
 "Computed rotor handover (not supplied input): **min "+f(a.handoverStats.min)+"km / median "+f(a.handoverStats.median)+"km / max "+f(a.handoverStats.max)+"km** across "+a.handoverStats.resolved+" resolved samples. Reach approximate cloud base "+
 f(number(d.research.idle_tipjet_heat.venus_cloud_base_km))+"km: "+a.handoverStats.atCloudBase+"; reach approximate cloud top "+f(number(d.research.idle_tipjet_heat.venus_cloud_top_km))+"km: "+a.handoverStats.aboveCloudTop+". These are the *joint hot-duty + induced-speed + heat* screens, not the earlier torch-idle research-only heat ceilings.",
 "**Conditional D-shuttle surface cooling can fail all samples because the 10% minimum reactor thermal output "+
 f(d.power.kit_house_reactor_thermal_MW.min*number(d.power.kit_house_reactor_min_stable_fraction))+"–"+
 f(d.power.kit_house_reactor_thermal_MW.max*number(d.power.kit_house_reactor_min_stable_fraction))+"MW exceeds the currently assumed "+
 f(d.thermal.hot_side_rejection_capacity_kW.min)+"–"+f(d.thermal.hot_side_rejection_capacity_kW.max)+"kW hot-loop rejection capacity. Physical independent heat dump, charge storage or short duty cycling is OPEN and NOT fabricated.",
 "### Representative reactor and cooling power","| Crew | Load W | cooler electric kW | aux bus allowance kW | hot-loop reject kW | available reject kW | D-shuttle | D-pod hours |",
 "|---:|---:|---:|---:|---:|---:|---|---:|");
 const ev=evaluate(d,stage,first.inputs,a.geometry);
 for(const q of d.thermal.crew_cases){const crew=number(q),t=ev.venus.thermal[crew];add("| "+crew+" | "+f(t.loadW)+" | "+f(t.coolerElectricalKW)+" | "+f(t.reactorBusLimitKW)+" | "+f(t.rejectKW)+" | "+f(t.rejectLimitKW)+" | "+t.status+" | "+f(t.podHours)+" |");}
 add("","### Phase-by-phase conserved inventories (first scenario, mode comparisons)");
 for(const mode of ["low","high"]){
  add("**Mode "+mode+"**","| Phase | reaction water before → after t | reaction debit t | reserved pod water t | pod cold energy 2/4 crew kWh | cooler input 2/4 crew kW | hot-loop rejection 2/4 crew kW | custody |",
 "|---|---|---:|---:|---|---|---|---|");
  for(const ph of ev.venus.phaseLedger[mode])add("| "+ph.phase+" | "+f(ph.water_before_t)+" → "+f(ph.water_after_t)+" | "+f(ph.water_debit_t)+" | "+f(ph.thermal_water_mass_t)+" | "+
   d.thermal.crew_cases.map(q=>f(ph.thermal_energy_by_crew[number(q)].energy_after_J/number(d.si.joules_per_kWh))).join("/")+" | "+
   (ph.cooler_electric_by_crew_kW?d.thermal.crew_cases.map(q=>f(ph.cooler_electric_by_crew_kW[number(q)])).join("/"):"—")+" | "+
   (ph.hot_loop_rejection_by_crew_kW?d.thermal.crew_cases.map(q=>f(ph.hot_loop_rejection_by_crew_kW[number(q)])).join("/"):"—")+" | "+ph.custody+" |");
  add("Water to orbit "+f(ev.venus.mode[mode].waterAtOrbit)+"t; unmet demand "+f(ev.venus.mode[mode].waterShortfallT)+"t; achievable ideal Δv "+f(ev.venus.mode[mode].delta_v_orbit)+"km/s; thrust "+f(ev.venus.mode[mode].thrustN)+"N.");
 }
 add("","### Dense-CO₂ torch light-up research and rotor extension",
 "A [magnetic nozzle PIC study](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2022.876684/full) operates under near-vacuum backgrounds, not Venus 1–70bar CO₂. [NASA rocket base heating](https://ntrs.nasa.gov/citations/20010116591) and [plume recirculation work](https://link.springer.com/article/10.1007/s12567-020-00306-8) show atmosphere/exhaust shear, entrainment and structural heating matter even for conventional jets. There is **no source** validating a multi-GW magnetically driven plume at Venus pressure; plasma neutralization, CO₂ ingestion, magnetic field confinement, base recirculation, induced hot-loop/hull loads, nozzle erosion and restart remain OPEN.",
 "The **5–25km prescribed handover interval has been removed**. For each sample the sizer computes the highest feasible altitude within the VIRA table and declared rotor duty/thermal/speed bounds. Rotor-only flight to 30–50km increases MW demand; these values are **demand**, not reactor-specific output or blade certification.",
 "| Altitude km | ambient bar | rotor shaft MW min–max | tip-jet heat MW min–max |","|---:|---:|---:|---:|");
 for(const [alt,x]of Object.entries(a.extensions))add("| "+f(Number(alt))+" | "+f(x.pressure_bar)+" | "+f(x.rotorMin)+"–"+f(x.rotorMax)+" | "+f(x.heatMin)+"–"+f(x.heatMax)+" |");
 add("At 30–50km the new reactor 100–230MW raw thermal is drawn from the kit. Its actual gas-side delivered heat is a DECLARED_2226 model assumption; exchanger efficiency, ducting, rotor life, and light-up physics remain unqualified. Moving handover upward helps ambient backpressure but does NOT certify a fusion plasma nozzle even near 1bar. Torch dense-atmosphere viability remains "+d.venus.torch_atmosphere_viability.provenance+".",
 "### Physical holds after conditional gate results",
 "The following declared required physics is still OPEN: venus.torch_atmosphere_viability, venus.entry_vehicle_thermal_qualification, kit individual hold geometry and hot blade joints, research.sphere hot pressurization and actual hatch/seal, power.reactor_waste_heat_MW. No PASS from this sizer overrides those holds.");
 }
 add("","## Representative sampled outcomes","| Sample | Dry with kit t | A | Docked core t | A2 | packed kit m³ | KV | KF | B | "+(stage===2?"Rotor | Water C | D-shuttle 2 | D-shuttle 4":"")+" |",
 "|---:|---:|---|---:|---|---:|---|---|---|"+(stage===2?"---|---|---|---|":"")+"|");
 for(const e of a.examples)add("| "+e.sample+" | "+f(e.dry)+" | "+e.gates.A+" | "+f(e.coreDry)+" | "+e.gates.A2+" | "+f(e.kit.packedVolume_m3)+" | "+e.gates.KV+" | "+e.gates.KF+" | "+e.gates.B+" | "+(stage===2?[e.gates.R,e.gates.C,e.gates.DS2,e.gates.DS4].join(" | ")+" | ":""));
 add("","## Full hashed input JSON (verbatim fields and provenance)","\`\`\`json",JSON.stringify(d,null,2),"\`\`\`");
 return rows.join("\n")+"\n";
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
 const parts=[...a.partRows.filter(x=>!d.kit.mass_component_keys.includes(x.name)),
              ...a.partRows.filter(x=>d.kit.mass_component_keys.includes(x.name))];
 const limit=number(d.mass.max_docked_dry_t),W=1100,H=115+parts.length*27,scale=(W-350)/a.sums[2],barX=300;
 const coreMid=a.sums[1]-a.kitSums[1],kitMid=a.kitSums[1];
 const rects=parts.map((r,i)=>{
   const x=barX+parts.slice(0,i).reduce((sum,v)=>sum+v.values[1],0)*scale;
   const w=r.values[1]*scale,y=85+i*27,kit=d.kit.mass_component_keys.includes(r.name);
   return '<text x="20" y="'+(y+13)+'" fill="#cde6ff" font-size="12">'+esc(r.name)+'</text>'+
     '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="19" fill="'+(kit?"#ffbc76":"#70c9c4")+'"/>';
 }).join("");
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+
 '<rect width="100%" height="100%" fill="#121b29"/>'+
 '<text x="20" y="25" fill="#fff" font-size="18">SHUTTLE DRY-MASS WATERFALL — MIDPOINT STACK (t)</text>'+
 '<text x="20" y="44" fill="#cde6ff" font-size="13">Core '+coreMid.toFixed(2)+'t (cyan), detachable Venus kit '+kitMid.toFixed(2)+'t (amber), full '+a.sums[1].toFixed(2)+'t</text>'+
 '<text x="20" y="63" fill="#cde6ff" font-size="13">A2 core PASS '+(100*a.gates.A2.pass_fraction).toFixed(1)+'%; A full PASS '+(100*a.gates.A.pass_fraction).toFixed(1)+'%; assumed payload capacity '+number(d.kit.payload_allowance_t)+'t</text>'+
 rects+
 '<line x1="'+(barX+coreMid*scale)+'" x2="'+(barX+coreMid*scale)+'" y1="65" y2="'+(H-25)+'" stroke="#83e0c8" stroke-dasharray="3 3" stroke-width="2"/>'+
 '<line x1="'+(barX+limit*scale)+'" x2="'+(barX+limit*scale)+'" y1="65" y2="'+(H-25)+'" stroke="#ff6b76" stroke-dasharray="6 4" stroke-width="2"/>'+
 '<text x="'+(barX+limit*scale+8)+'" y="'+(H-10)+'" fill="#ff9fa5" font-size="12">'+limit+'t docked limit</text></svg>';
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
