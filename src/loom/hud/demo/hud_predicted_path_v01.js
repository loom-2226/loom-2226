(()=>{'use strict';
const toggle=document.getElementById('predictedPathToggle'),stateLabel=document.getElementById('predictedPathState'),cameraSel=document.getElementById('camera');
if(!toggle||!window.THREE||window.__loomPredictedPathInstalled)return;
window.__loomPredictedPathInstalled=true;
let enabled=false,busy=false,lastFetch=0,pathGroup=null,payload=null,lastError='',dirty=false;
const previousBeforeRender=window.__loomBeforeRender;
const v3=a=>new THREE.Vector3(Number(a[0]),Number(a[1]),Number(a[2]));
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function clearPath(){if(pathGroup&&pathGroup.parent)pathGroup.parent.remove(pathGroup);pathGroup=null;}
function label(){
  if(!enabled)return 'PATH OFF';
  if(lastError)return `PREDICTED PATH UNAVAILABLE • ${lastError}`;
  if(!payload)return 'PREDICTED PATH • LOADING';
  const h=Number(payload.horizon_s),mins=Number.isFinite(h)?Math.round(h/60):null;
  const ignored=payload.active_propulsion_ignored===true?' • ACTIVE THRUST NOT CONTINUED':'';
  const motion=payload.motion_cue==='GRAVITY_DOMINATED_NEAR_ZERO_SPEED'?' • V≈0 • GRAVITY-DOMINATED PATH':'';
  return `PREDICTED PATH • ${mins!==null?mins+' min':'BOUNDED'} • BALLISTIC${motion}${ignored}`;
}
function renderLabel(){toggle.textContent=enabled?'PREDICTED PATH ON':'PREDICTED PATH OFF';toggle.classList.toggle('active',enabled);if(stateLabel)stateLabel.textContent=label();}
function arrow(name,origin,direction,length,color,headScale=.18){
  if(!direction||direction.lengthSq()<=1e-18)return null;
  const a=new THREE.ArrowHelper(direction.clone().normalize(),origin,length,color,Math.max(6,length*headScale),Math.max(3,length*headScale*.45));
  a.name=name;return a;
}
function rebuild(scene){
  dirty=false;
  if(!enabled||!payload||!scene){clearPath();return;}
  const pts=payload.points||[];
  if(pts.length<2){clearPath();return;}
  const start=pts[0].position_earth_centered_km;
  if(!Array.isArray(start)){clearPath();return;}
  const origin=v3(start),rel=pts.map(p=>v3(p.position_earth_centered_km).sub(origin));
  clearPath();pathGroup=new THREE.Group();pathGroup.name='LOOM_PREDICTED_PATH_PRESENTATION';
  const glow=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rel),new THREE.LineBasicMaterial({color:0xf0c36a,transparent:true,opacity:.18}));glow.scale.setScalar(1.00005);pathGroup.add(glow);
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rel),new THREE.LineBasicMaterial({color:0xf0c36a,transparent:true,opacity:.86}));line.name='PREDICTED_PATH_LINE';pathGroup.add(line);
  const end=rel[rel.length-1],marker=new THREE.Mesh(new THREE.SphereGeometry(28,10,7),new THREE.MeshBasicMaterial({color:0xf0c36a,transparent:true,opacity:.9}));marker.position.copy(end);marker.name='PREDICTED_PATH_HORIZON';pathGroup.add(marker);

  let extent=0;for(const p of rel)extent=Math.max(extent,p.length());
  const cueLength=clamp(extent*.08,60,5000);
  const nose=Array.isArray(payload.start_nose_direction_inertial)?v3(payload.start_nose_direction_inertial):null;
  const noseCue=nose&&arrow('PREDICTED_PATH_BODY_NOSE',new THREE.Vector3(0,0,0),nose,cueLength*.65,0xb8c3c7,.14);if(noseCue)pathGroup.add(noseCue);

  const startVelocity=Array.isArray(pts[0].velocity_earth_centered_km_s)?v3(pts[0].velocity_earth_centered_km_s):null;
  if(payload.motion_cue!=='GRAVITY_DOMINATED_NEAR_ZERO_SPEED'&&startVelocity&&startVelocity.lengthSq()>1e-18){
    const velCue=arrow('PREDICTED_PATH_START_VELOCITY',new THREE.Vector3(0,0,0),startVelocity,cueLength,0x7fd7d0,.16);if(velCue)pathGroup.add(velCue);
  }

  const idx=clamp(Math.floor(rel.length*.22),1,Math.max(1,rel.length-2));
  const futureDir=rel[Math.min(idx+1,rel.length-1)].clone().sub(rel[idx]);
  const futureCue=arrow('PREDICTED_PATH_FUTURE_DIRECTION',rel[idx].clone(),futureDir,cueLength*.8,0xf0c36a,.20);if(futureCue)pathGroup.add(futureCue);

  scene.add(pathGroup);
}
async function refresh(force=false){
  if(!enabled||busy)return;
  const now=Date.now();if(!force&&now-lastFetch<2500)return;
  busy=true;lastFetch=now;lastError='';renderLabel();
  try{
    const r=await fetch('/qualification-flight/predicted-path.json?horizon_s=7200&sample_s=60',{cache:'no-store'}),d=await r.json();
    if(!r.ok||d.contract!=='LOOM_PREDICTED_PATH_V1')throw new Error(d.reason||`HTTP ${r.status}`);
    payload=d;lastError='';dirty=true;
  }catch(e){payload=null;lastError=String(e&&e.message||e);dirty=true;}
  finally{busy=false;renderLabel();}
}
toggle.addEventListener('click',()=>{enabled=!enabled;if(!enabled){payload=null;lastError='';dirty=false;clearPath();}renderLabel();if(enabled)refresh(true);});
window.addEventListener('loom-live-qualification',()=>{if(enabled)refresh(false);});
window.__loomBeforeRender=(scene,camera)=>{
  if(typeof previousBeforeRender==='function')previousBeforeRender(scene,camera);
  if(enabled&&payload&&(dirty||!pathGroup||!pathGroup.parent))rebuild(scene);
  if(dirty&&!payload)rebuild(scene);
  if(pathGroup)pathGroup.visible=enabled&&(!cameraSel||cameraSel.value!=='TRAJECTORY');
};
renderLabel();
})();
