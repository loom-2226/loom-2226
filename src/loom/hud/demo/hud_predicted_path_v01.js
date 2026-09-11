(()=>{'use strict';
const toggle=document.getElementById('predictedPathToggle'),stateLabel=document.getElementById('predictedPathState'),cameraSel=document.getElementById('camera'),stage=document.getElementById('stage');
if(!toggle||!window.THREE||window.__loomPredictedPathInstalled)return;
window.__loomPredictedPathInstalled=true;
let enabled=false,busy=false,lastFetch=0,pathGroup=null,payload=null,lastError='',dirty=false;
const previousBeforeRender=window.__loomBeforeRender;
const v3=a=>new THREE.Vector3(Number(a[0]),Number(a[1]),Number(a[2]));
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const CUE_PIXELS={nose:24,velocity:34,future:28};
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
function arrow(name,origin,direction,color){
  if(!direction||direction.lengthSq()<=1e-18)return null;
  const a=new THREE.ArrowHelper(direction.clone().normalize(),origin,1,color,.32,.18);
  a.name=name;
  if(a.line&&a.line.material){a.line.material.transparent=true;a.line.material.opacity=.88;a.line.material.depthTest=false;}
  if(a.cone&&a.cone.material){a.cone.material.transparent=true;a.cone.material.opacity=.92;a.cone.material.depthTest=false;}
  a.renderOrder=30;
  return a;
}
function cueWorldLengthForPixels(camera,point,pixels){
  if(!camera||!point)return .001;
  const height=Math.max(1,stage&&stage.clientHeight||window.innerHeight||600);
  const dist=Math.max(Number(camera.near||.001)*4,camera.position.distanceTo(point));
  const fov=Number(camera.fov||60)*Math.PI/180;
  const visibleHeight=2*dist*Math.tan(fov/2);
  return Math.max(Number(camera.near||.001)*4,visibleHeight*(pixels/height));
}
function setCueLength(cue,camera,pixels){
  if(!cue)return;
  const world=cueWorldLengthForPixels(camera,cue.position,pixels);
  cue.setLength(world,world*.32,world*.18);
}
function updateCueScale(camera){
  if(!pathGroup||!pathGroup.userData||!pathGroup.userData.cues)return;
  const cues=pathGroup.userData.cues;
  const shipView=cameraSel&&cameraSel.value==='SHIP';
  if(cues.nose){cues.nose.visible=!shipView;setCueLength(cues.nose,camera,CUE_PIXELS.nose);}
  if(cues.velocity){cues.velocity.visible=!shipView;setCueLength(cues.velocity,camera,CUE_PIXELS.velocity);}
  if(cues.future){cues.future.visible=!shipView;setCueLength(cues.future,camera,CUE_PIXELS.future);}
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

  const cues={nose:null,velocity:null,future:null};
  const nose=Array.isArray(payload.start_nose_direction_inertial)?v3(payload.start_nose_direction_inertial):null;
  if(payload.show_body_axis_cue===true&&nose){cues.nose=arrow('PREDICTED_PATH_BODY_NOSE',new THREE.Vector3(0,0,0),nose,0xb8c3c7);if(cues.nose)pathGroup.add(cues.nose);}

  const startVelocity=Array.isArray(pts[0].velocity_earth_centered_km_s)?v3(pts[0].velocity_earth_centered_km_s):null;
  if(payload.motion_cue!=='GRAVITY_DOMINATED_NEAR_ZERO_SPEED'&&startVelocity&&startVelocity.lengthSq()>1e-18){
    cues.velocity=arrow('PREDICTED_PATH_START_VELOCITY',new THREE.Vector3(0,0,0),startVelocity,0x7fd7d0);if(cues.velocity)pathGroup.add(cues.velocity);
  }

  const idx=clamp(Math.floor(rel.length*.22),1,Math.max(1,rel.length-2));
  const futureDir=rel[Math.min(idx+1,rel.length-1)].clone().sub(rel[idx]);
  cues.future=arrow('PREDICTED_PATH_FUTURE_DIRECTION',rel[idx].clone(),futureDir,0xf0c36a);if(cues.future)pathGroup.add(cues.future);
  pathGroup.userData.cues=cues;

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
  if(pathGroup){pathGroup.visible=enabled&&(!cameraSel||cameraSel.value!=='TRAJECTORY');if(pathGroup.visible)updateCueScale(camera);}
};
renderLabel();
})();
