(()=>{'use strict';
const toggle=document.getElementById('predictedPathToggle'),stateLabel=document.getElementById('predictedPathState'),cameraSel=document.getElementById('camera');
if(!toggle||!window.THREE||window.__loomPredictedPathInstalled)return;
window.__loomPredictedPathInstalled=true;
let enabled=false,busy=false,lastFetch=0,pathGroup=null,payload=null,lastError='';
const previousBeforeRender=window.__loomBeforeRender;
const v3=a=>new THREE.Vector3(Number(a[0]),Number(a[1]),Number(a[2]));
function clearPath(){if(pathGroup&&pathGroup.parent)pathGroup.parent.remove(pathGroup);pathGroup=null;}
function label(){
  if(!enabled)return 'PATH OFF';
  if(lastError)return `PREDICTED PATH UNAVAILABLE • ${lastError}`;
  if(!payload)return 'PREDICTED PATH • LOADING';
  const h=Number(payload.horizon_s),mins=Number.isFinite(h)?Math.round(h/60):null;
  const ignored=payload.active_propulsion_ignored===true?' • BALLISTIC / ACTIVE THRUST NOT CONTINUED':'';
  return `PREDICTED PATH • ${mins!==null?mins+' min':'BOUNDED'} • BALLISTIC${ignored}`;
}
function renderLabel(){toggle.textContent=enabled?'PREDICTED PATH ON':'PREDICTED PATH OFF';toggle.classList.toggle('active',enabled);if(stateLabel)stateLabel.textContent=label();}
function rebuild(scene){
  if(!enabled||!payload||!scene){clearPath();return;}
  const pts=payload.points||[];
  if(pts.length<2){clearPath();return;}
  const start=pts[0].position_earth_centered_km;
  if(!Array.isArray(start)){clearPath();return;}
  const rel=pts.map(p=>v3(p.position_earth_centered_km).sub(v3(start)));
  clearPath();pathGroup=new THREE.Group();pathGroup.name='LOOM_PREDICTED_PATH_PRESENTATION';
  const glow=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rel),new THREE.LineBasicMaterial({color:0xf0c36a,transparent:true,opacity:.18}));glow.scale.setScalar(1.00005);pathGroup.add(glow);
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rel),new THREE.LineBasicMaterial({color:0xf0c36a,transparent:true,opacity:.86}));pathGroup.add(line);
  const end=rel[rel.length-1];const marker=new THREE.Mesh(new THREE.SphereGeometry(28,10,7),new THREE.MeshBasicMaterial({color:0xf0c36a,transparent:true,opacity:.9}));marker.position.copy(end);marker.name='PREDICTED_PATH_HORIZON';pathGroup.add(marker);
  scene.add(pathGroup);
}
async function refresh(force=false){
  if(!enabled||busy)return;
  const now=Date.now();if(!force&&now-lastFetch<2500)return;
  busy=true;lastFetch=now;lastError='';renderLabel();
  try{
    const r=await fetch('/qualification-flight/predicted-path.json?horizon_s=7200&sample_s=60',{cache:'no-store'}),d=await r.json();
    if(!r.ok||d.contract!=='LOOM_PREDICTED_PATH_V1')throw new Error(d.reason||`HTTP ${r.status}`);
    payload=d;lastError='';
  }catch(e){payload=null;lastError=String(e&&e.message||e);}
  finally{busy=false;renderLabel();}
}
toggle.addEventListener('click',()=>{enabled=!enabled;if(!enabled){payload=null;lastError='';clearPath();}renderLabel();if(enabled)refresh(true);});
window.addEventListener('loom-live-qualification',()=>{if(enabled)refresh(false);});
window.__loomBeforeRender=(scene,camera)=>{
  if(typeof previousBeforeRender==='function')previousBeforeRender(scene,camera);
  if(enabled&&payload&&(!pathGroup||!pathGroup.parent))rebuild(scene);
  if(pathGroup)pathGroup.visible=enabled&&(!cameraSel||cameraSel.value!=='TRAJECTORY');
};
renderLabel();
})();
