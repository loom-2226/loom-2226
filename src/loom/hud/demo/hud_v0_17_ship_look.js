(()=>{'use strict';
const canvas=document.getElementById('world'),cameraSel=document.getElementById('camera'),resetView=document.getElementById('resetView'),cameraState=document.getElementById('cameraState');
if(!canvas||!cameraSel)return;
const pointers=new Map();
let shipLook=false,lookDir=null,upBase=null,pinchDistance=null,shipFov=60;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function activeCamera(){return window.__loomActiveCamera||null}
function beginShipLook(){
  const camera=activeCamera(); if(!camera)return false;
  if(!lookDir){lookDir=new THREE.Vector3();camera.getWorldDirection(lookDir);lookDir.normalize();upBase=camera.up.clone().normalize();shipFov=Number(camera.fov)||60}
  shipLook=true; if(cameraState)cameraState.textContent='CAM USER / SHIP LOOK'; return true;
}
function rotateShipLook(dx,dy){
  const camera=activeCamera(); if(!camera||!beginShipLook())return;
  const yawAxis=(upBase||new THREE.Vector3(0,1,0)).clone().normalize();
  const yaw=new THREE.Quaternion().setFromAxisAngle(yawAxis,-dx*.006);
  let candidate=lookDir.clone().applyQuaternion(yaw).normalize();
  let right=new THREE.Vector3().crossVectors(candidate,yawAxis);
  if(right.lengthSq()<1e-10)right.set(1,0,0); else right.normalize();
  const pitch=new THREE.Quaternion().setFromAxisAngle(right,-dy*.006);
  const pitched=candidate.clone().applyQuaternion(pitch).normalize();
  if(Math.abs(pitched.dot(yawAxis))<.995)candidate=pitched;
  lookDir.copy(candidate);
}
function zoomShipLook(factor){
  const camera=activeCamera(); if(!camera||!beginShipLook())return;
  shipFov=clamp(shipFov*factor,18,100);
}
function resetShipLook(){shipLook=false;lookDir=null;upBase=null;pinchDistance=null;shipFov=60}
window.__loomBeforeRender=(scene,camera)=>{
  if(cameraSel.value!=='SHIP'||!shipLook)return;
  camera.position.set(0,0,0);
  camera.up.copy(upBase||new THREE.Vector3(0,1,0));
  camera.fov=shipFov; camera.updateProjectionMatrix();
  camera.lookAt(lookDir.clone().multiplyScalar(100000));
  if(cameraState)cameraState.textContent='CAM USER / SHIP LOOK';
};
canvas.addEventListener('pointerdown',e=>{
  if(cameraSel.value!=='SHIP')return;
  e.preventDefault();e.stopImmediatePropagation();
  try{canvas.setPointerCapture(e.pointerId)}catch(_e){}
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});beginShipLook();
},true);
canvas.addEventListener('pointermove',e=>{
  if(cameraSel.value!=='SHIP'||!pointers.has(e.pointerId))return;
  e.preventDefault();e.stopImmediatePropagation();
  const prev=pointers.get(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size===1)rotateShipLook(e.clientX-prev.x,e.clientY-prev.y);
  else if(pointers.size===2){const ps=[...pointers.values()],d=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);if(pinchDistance&&d>0)zoomShipLook(pinchDistance/d);pinchDistance=d}
},true);
const end=e=>{if(cameraSel.value==='SHIP'){e.stopImmediatePropagation();pointers.delete(e.pointerId);pinchDistance=null}};
canvas.addEventListener('pointerup',end,true);canvas.addEventListener('pointercancel',end,true);
canvas.addEventListener('wheel',e=>{if(cameraSel.value!=='SHIP')return;e.preventDefault();e.stopImmediatePropagation();zoomShipLook(Math.exp(e.deltaY*.001))},{capture:true,passive:false});
cameraSel.addEventListener('change',()=>resetShipLook(),true);
if(resetView)resetView.addEventListener('click',()=>resetShipLook(),true);
})();
