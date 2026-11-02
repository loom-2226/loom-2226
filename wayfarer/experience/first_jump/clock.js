"use strict";
// One requestAnimationFrame mission clock. It interpolates FQ11 DISPLAY VALUES,
// not physical spacecraft dynamics or a Metric trajectory.
const $=id=>document.getElementById(id), put=(id,v)=>{$(id).textContent=v};
const PHASES=["preburn","metric","turn","trim"];
const ART={briefing:"cmd_pov.png",preburn:"ext_burn.png",metric:"ext_metric.png",turn:"cmd_pov.png",trim:"ext_departure.png",debrief:"cmd_pov.png"};
const STORY={
briefing:["Command deck","Departure","Couches lock against the thrust axis. The pilot waits for your word.","Captain, we're ready when you are."],
preburn:["Departure","Torch burn","Hot fins unfold. The ship presses firmly into the couches as Earth recedes behind.","Burn's clean, Captain. Keep an eye on the mass line."],
metric:["The weave","Between worlds","The torch falls quiet. Earth slips away as the weave takes hold. Mars waits at the far end.","We have the weave. Our natural arrival velocity is not a promise of a perfect match."],
turn:["Mars approach","The handoff","Mars fills the approach display. The pilot prepares the attitude change.","Mars is on the board. Turn underway."],
trim:["Mars approach","Correcting the line","The ship steadies and fires its brief final correction.","Trim is running, Captain."],
debrief:["Mars approach","Handoff complete","Holding at Mars approach shell. Mars Traffic has us from here.","Mars Traffic has the approach. Nice work, Captain."]
};
let snapshot=null,atWall=0,display=null,timeline=null,spokenPhase="",viewChoice="auto",busy=false;
let camera={zoom:1,angle:0}, fingers=new Map(),pinch=0,started=false, lastShown=-1;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),lerp=(a,b,p)=>a+(b-a)*clamp(p,0,1);
const mmss=v=>{const s=Math.floor(Math.max(0,v));return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0")};
async function api(path,body){
 const init=body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)};
 const res=await fetch(path,init),data=await res.json();if(!res.ok)throw Error(data.error||"Link unavailable");return data;
}
// Authoritative FQ11 time axis; the only browser interpolation is display pacing.
function advanceClock(t,wall,s){
 for(const phase of PHASES){
  const [begin,end]=s.phase_bounds_s[phase];
  if(t>=end-1e-7)continue;
  t=Math.max(t,begin);
  const rate=(end-begin)/s.presentation_s[phase];
  const step=Math.min(end-t,Math.max(0,wall)*rate);
  t+=step;wall-=step/rate;
  if(wall<=0)break;
 }
 return Math.min(t,s.authorised_until_s,s.mission_end_s);
}
function clockAt(now){
 if(!snapshot)return 0;
 return snapshot.mode==="active"?advanceClock(snapshot.mission_clock_s,(now-atWall)/1000,snapshot):snapshot.mission_clock_s;
}
function phaseAt(t,s){
 if(s.mode==="complete")return "debrief";
 if(s.mode==="quit")return s.phase;
 if(s.phase==="briefing"&&s.authorised_until_s===0)return "briefing";
 const b=s.phase_bounds_s;
 if(t<b.preburn[1]-1e-5||(s.authorised_until_s<=b.preburn[1]+1e-5&&t<=b.preburn[1]+1e-5))return "preburn";
 if(t<b.metric[1]-1e-5)return "metric";
 if(t<b.turn[1]-1e-5||(s.authorised_until_s<=b.turn[1]+1e-5&&t<=b.turn[1]+1e-5))return "turn";
 return "trim";
}
function phaseFrac(t,phase,s){const p=s.phase_bounds_s[phase];return p?clamp((t-p[0])/(p[1]-p[0]),0,1):0}
function row(label,value,field){
 const div=document.createElement("div");div.className="reading";
 const k=document.createElement("span");k.textContent=label;
 const b=document.createElement("button");b.textContent=value;
 if(field){const mark=document.createElement("small");mark.className="earned";mark.textContent="earned";b.append(mark);b.onclick=()=>evidence(field)}
 else b.disabled=true;
 div.append(k,b);return div;
}
function readings(phase,t,s){
 const box=$("readings");box.replaceChildren();
 const f=timeline?.cases[s.source_case];if(!f)return;
 const val=k=>f[k].value,p=phaseFrac(t,phase,s);
 if(phase==="briefing"){box.append(row("DESTINATION","Mars"),row("FLIGHT PLAN","Loaded"));return}
 if(phase==="preburn"){box.append(
  row("WATER USED",(lerp(0,val("preburn_kg"),p)/1000).toFixed(3)+" t","preburn_kg"),
  row("PEAK ACCEL",val("preburn_peak_g").toFixed(3)+" g","preburn_peak_g"),
  row("BURN",Math.round(p*100)+"%"));return}
 if(phase==="metric"){box.append(
  row("TRANSIT",mmss(lerp(0,val("metric_s"),p))+" / "+mmss(val("metric_s")),"metric_s"),
  row("ARRIVAL MISMATCH",val("arrival_mismatch_m_s").toFixed(2)+" m/s","arrival_mismatch_m_s"));return}
 if(phase==="turn"){box.append(
  row("RCS TURN",mmss(lerp(0,val("turn_s"),p))+" / "+mmss(val("turn_s")),"turn_s"),
  row("ATTITUDE",lerp(0,val("turn_deg"),p).toFixed(1)+"°","turn_deg"),
  row("MISMATCH",val("arrival_mismatch_m_s").toFixed(2)+" m/s","arrival_mismatch_m_s"));return}
 if(phase==="trim"){box.append(
  row("TRIM",lerp(0,val("trim_s"),p).toFixed(2)+" s","trim_s"),
  row("MISMATCH",lerp(val("arrival_mismatch_m_s"),val("final_mismatch_m_s"),p).toFixed(3)+" m/s","final_mismatch_m_s"));return}
 box.append(row("FINAL MISMATCH",val("final_mismatch_m_s").toFixed(3)+" m/s","final_mismatch_m_s"),
  row("REMASS REMAINING",(val("remass_remaining_kg")/1000).toFixed(3)+" t","remass_remaining_kg"));
}
function sampleAt(t){
 const list=display.samples;let lo=0,hi=list.length-1;
 while(lo<hi){const m=(lo+hi+1)>>1;if(list[m].elapsed_s<=t)lo=m;else hi=m-1}
 const a=list[lo],b=list[Math.min(lo+1,list.length-1)];
 const frac=(t-a.elapsed_s)/(b.elapsed_s-a.elapsed_s||1);
 return {EA:[lerp(a.EA[0],b.EA[0],frac),lerp(a.EA[1],b.EA[1],frac)],
         MA:[lerp(a.MA[0],b.MA[0],frac),lerp(a.MA[1],b.MA[1],frac)]};
}
function drawMap(phase,t,s){
 if(!display)return;
 const show=viewChoice==="map"||(viewChoice==="auto"&&phase!=="briefing");
 $("deck").hidden=show;$("map").hidden=!show;$("tools").hidden=false;
 $("seekrow").hidden=s.authorised_until_s===0||["complete","quit"].includes(s.mode);
 $("pause").hidden=!["active","held"].includes(s.mode);
 put("view",show?"DECK":"MAP");put("pause",s.mode==="held"?"RESUME":"PAUSE");
 if(document.activeElement!==$("seek")){$("seek").max=s.authorised_until_s;$("seek").value=t;put("seekPct",mmss(t))}
 if(!show)return;
 const close=["turn","trim","debrief"].includes(phase),p=phaseFrac(t,phase,s);
 $("map").classList.toggle("close",close);$("map").classList.toggle("metric",phase==="metric");$("map").classList.toggle("paused",s.mode!=="active");
 put("maplabel",close?"MARS / APPROACH":phase==="metric"?"SOLAR / METRIC":"SOLAR / DEPARTURE");
 const xy=sampleAt(t),earth=xy.EA,mars=xy.MA;
 for(const [id,point] of [["earthMarker",earth],["marsMarker",mars]])$(id).setAttribute("transform","translate("+point[0]+" "+point[1]+")");
 for(const [id,point] of [["departurePulse",earth],["arrivalPulse",mars]]){$(id).setAttribute("cx",point[0]);$(id).setAttribute("cy",point[1])}
 const destination=close||(phase==="metric"&&p>=.9999),ship=destination?mars:earth;
 $("shipMarker").setAttribute("transform","translate("+ship[0]+" "+(ship[1]-18)+")");
 $("burnPlume").setAttribute("opacity",phase==="preburn"&&p<.98?".9":"0");
 $("trimFlare").setAttribute("opacity",phase==="trim"&&p<.99?".9":"0");
 const angle=timeline.cases[s.source_case].turn_deg.value;
 $("closeShip").setAttribute("transform","rotate("+(phase==="turn"?lerp(0,angle,p):close?angle:0)+" -145 37)");
 $("departurePulse").classList.toggle("active",phase==="metric"&&p<.985);
 $("arrivalPulse").classList.toggle("active",phase==="metric"&&p>=.985);
 let zoom=1,center=[0,0];
 if(phase==="briefing"){zoom=2.8;center=earth}
 if(phase==="preburn"){zoom=lerp(2.8,.85,p);center=[lerp(earth[0],0,p),lerp(earth[1],0,p)]}
 if(phase==="metric"){zoom=lerp(.85,1.12,p)}
 if(close){zoom=2.8;center=mars}
 $("solarScene").setAttribute("transform","rotate("+camera.angle+") scale("+(zoom*camera.zoom)+") translate("+(-center[0])+" "+(-center[1])+")");
}
function frame(now){
 if(!snapshot){requestAnimationFrame(frame);return}
 const s=snapshot,t=clockAt(now),phase=phaseAt(t,s),[part,title,description,voice]=STORY[phase];
 if(spokenPhase!==phase){put("chapter",part);put("heading",title);put("story",description);
   put("mara",phase==="turn"&&s.source_case==="UNDERBURN_1_PERCENT"?"Departure burn fell short, Captain. Recovery's on the board.":voice);
   spokenPhase=phase;
 }
 $("deck").dataset.phase=phase;
 const art="/art/"+ART[phase];if($("art").getAttribute("src")!==art)$("art").setAttribute("src",art);
 $("bar").style.width=(100*t/s.mission_end_s)+"%";put("missionTime","MISSION "+mmss(t)+" / "+mmss(s.mission_end_s));
 put("gate",s.mode==="awaiting"?(s.next_gate==="burn"?"Ready to burn":s.next_gate==="jump"?"Awaiting jump authorisation":"Awaiting trim authorisation"):
             s.mode==="held"?"On your hold":s.mode==="complete"?"Mars Traffic standing by":s.mode==="quit"?"Bridge session ended":"Under way");
 const done=["complete","quit"].includes(s.mode);
 $("go").hidden=done||!["awaiting","held"].includes(s.mode);
 $("hold").hidden=true;$("quit").hidden=done;$("replay").hidden=!done;
 put("go",s.mode==="held"?"RESUME":s.next_gate==="burn"?"AUTHORISE BURN":s.next_gate==="jump"?"AUTHORISE JUMP":"AUTHORISE TRIM");
 if(now-lastShown>125||spokenPhase!==phase){readings(phase,t,s);lastShown=now}
 drawMap(phase,t,s);
 requestAnimationFrame(frame);
}
function accept(s){snapshot=s;atWall=performance.now();if(!started){started=true;requestAnimationFrame(frame)}}
async function command(action,args={}){
 if(busy)return;busy=true;
 try{accept(await api("/api/command",{action,...args}))}catch(e){put("mara","The bridge link is down. "+e.message)}finally{busy=false}
}
async function evidence(field){
 try{const e=await api("/api/evidence",{field});$("evidence").hidden=false;
 const box=$("trace");box.replaceChildren();
 for(const [k,v] of [["Reading",e.field],["Value",String(e.value)],["FQ11",e.source]]){
  const p=document.createElement("p");p.textContent=k+": "+v;box.append(p)}
 const note=document.createElement("p");note.textContent="Intermediate numbers are presentation interpolation between accepted FQ11 endpoints.";box.append(note);
 await diagnostics();
 }catch(e){put("mara","Ship's record is unavailable.")}
}
async function diagnostics(){
 try{const d=await api("/api/diagnostics");put("diagnostic",d.narration==="live_available"?"Live Mara configured; individual reply outcomes are in the log.":"Mara uses scripted comms until an API key is configured in Termux.")}catch(e){put("diagnostic","Channel status unavailable")}
}
async function init(){
 try{
  [display,timeline]=await Promise.all([api("/api/map"),api("/api/timeline")]);
  if(display.schema!=="FIRST_JUMP_SOLAR_DISPLAY_v0.3"||display.metric_path!==null||display.mars_approach_range!==null)throw Error("Bad map");
  for(const key of ["EA","MA"]){
   const path=document.createElementNS("http://www.w3.org/2000/svg","path");
   path.setAttribute("class","orbit");path.setAttribute("d",display.orbit_context[key].map((p,i)=>(i?"L":"M")+p[0]+","+p[1]).join(" "));
   $("orbitPaths").append(path);
  }
  accept(await api("/api/state"));
  setInterval(async()=>{if(busy)return;try{accept(await api("/api/state"))}catch(e){put("gate","Connection interrupted")}},1000);
 }catch(e){put("gate","Navigation display unavailable: "+e.message)}
}
$("go").onclick=()=>command("go");$("pause").onclick=()=>command(snapshot.mode==="held"?"go":"hold");
$("quit").onclick=()=>{if(confirm("Leave bridge?"))command("quit")};
$("replay").onclick=async()=>{const choice=$("scenario").value;try{spokenPhase="";accept(await api("/api/new",choice?{case:choice}:{}))}catch(e){put("mara","Bridge unavailable.")}};
$("view").onclick=()=>{viewChoice=$("map").hidden?"map":"deck"};
$("in").onclick=()=>{camera.zoom=Math.min(5,camera.zoom*1.25)};$("out").onclick=()=>{camera.zoom=Math.max(.4,camera.zoom/1.25)};
$("left").onclick=()=>{camera.angle-=15};$("right").onclick=()=>{camera.angle+=15};
$("seek").oninput=()=>put("seekPct",mmss(Number($("seek").value)));
$("seek").onchange=()=>command("scrub",{clock_s:Number($("seek").value)});
$("showEvidence").onclick=async()=>{$("evidence").hidden=!$("evidence").hidden;if(!$("evidence").hidden)await diagnostics()};
$("closeEvidence").onclick=()=>{$("evidence").hidden=true};
const svg=$("svg");
svg.onpointerdown=e=>{svg.setPointerCapture(e.pointerId);fingers.set(e.pointerId,[e.clientX,e.clientY]);
 if(fingers.size===2){const a=[...fingers.values()];pinch=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1])}};
svg.onpointermove=e=>{if(!fingers.has(e.pointerId))return;
 const old=fingers.get(e.pointerId),now=[e.clientX,e.clientY];fingers.set(e.pointerId,now);
 if(fingers.size===1)camera.angle+=(now[0]-old[0])*.28;
 if(fingers.size===2){const a=[...fingers.values()],d=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]);
 if(pinch>0)camera.zoom=clamp(camera.zoom*d/pinch,.4,5);pinch=d}
};
for(const e of ["pointerup","pointercancel","lostpointercapture"])svg.addEventListener(e,evt=>{fingers.delete(evt.pointerId);if(fingers.size<2)pinch=0});
$("ask").onclick=async()=>{const q=$("question").value.trim();if(!q||busy)return;busy=true;$("ask").disabled=true;put("mara","Let me check the board, Captain…");
 try{const a=await api("/api/ask",{question:q});put("mara",a.reply);$("question").value=""}catch(e){put("mara","Can't reach the ship's channel.")}
 finally{busy=false;$("ask").disabled=false}};
$("question").onkeydown=e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();$("ask").click()}};
init();
