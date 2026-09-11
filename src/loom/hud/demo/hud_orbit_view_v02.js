(()=>{'use strict';
const cameraSel=document.getElementById('camera'),canvas=document.getElementById('world'),resetView=document.getElementById('resetView'),cameraState=document.getElementById('cameraState');
if(!cameraSel||!canvas||!window.THREE||window.__loomOrbitViewInstalled)return;
window.__loomOrbitViewInstalled=true;
let live=null,orbitGroup=null,userCamera=false,lastKey='';
const previousBeforeRender=window.__loomBeforeRender;
const v3=a=>new THREE.Vector3(Number(a[0]),Number(a[1]),Number(a[2]));
const safeUnit=(a,fallback)=>{const v=v3(a);return v.lengthSq()>1e-12?v.normalize():fallback.clone()};
function removeOrbitGroup(){if(orbitGroup&&orbitGroup.parent)orbitGroup.parent.remove(orbitGroup);orbitGroup=null;}
function rebuildOrbit(scene){
  if(!live||!scene)return;
  const vis=live.orbit_visualization||{},o=live.orbital_state||{},shipState=live.wayfarer||{};
  const points=vis.points_earth_centered_km;
  if(!(vis.available===true&&o.operational_orbit===true&&Array.isArray(points)&&points.length>2&&Array.isArray(shipState.position_earth_centered_km)&&Array.isArray(vis.current_position_earth_centered_km)&&Array.isArray(vis.prograde_unit_earth_centered))){removeOrbitGroup();lastKey='';return;}
  const key=`${live.sim_epoch_utc}|${points.length}|${Number(o.apoapsis_altitude_km).toFixed(3)}|${Number(o.periapsis_altitude_km).toFixed(3)}`;
  if(key===lastKey&&orbitGroup&&orbitGroup.parent===scene)return;
  removeOrbitGroup();lastKey=key;
  const shipPos=v3(shipState.position_earth_centered_km);
  orbitGroup=new THREE.Group();orbitGroup.name='LOOM_ORBIT_OVERVIEW_PRESENTATION';
  const rel=points.map(p=>v3(p).sub(shipPos));
  const pathLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints(rel),new THREE.LineBasicMaterial({color:0x7fd7d0,transparent:true,opacity:.98}));
  pathLine.name='LOOM_ORBIT_PATH_PRESENTATION';orbitGroup.add(pathLine);
  if(rel.length>4){
    const curve=new THREE.CatmullRomCurve3(rel.slice(0,-1),true,'centripetal');
    const tube=new THREE.Mesh(new THREE.TubeGeometry(curve,Math.max(96,rel.length*2),12,6,true),new THREE.MeshBasicMaterial({color:0x4ea5a1,transparent:true,opacity:.28,depthWrite:false}));
    tube.name='LOOM_ORBIT_PATH_PRESENTATION_GLOW';orbitGroup.add(tube);
  }
  function markerAt(p,label,color=0xf0c36a,radius=45){if(!Array.isArray(p))return;const g=new THREE.Group();g.name=label;const m=new THREE.Mesh(new THREE.SphereGeometry(radius,12,8),new THREE.MeshBasicMaterial({color}));m.position.copy(v3(p).sub(shipPos));g.add(m);orbitGroup.add(g);}
  markerAt(vis.periapsis_position_earth_centered_km,'PERIAPSIS_PRESENTATION_MARKER');
  markerAt(vis.apoapsis_position_earth_centered_km,'APOAPSIS_PRESENTATION_MARKER');
  markerAt(vis.current_position_earth_centered_km,'SHIP_POSITION_PRESENTATION_MARKER',0xffffff,60);
  const currentRel=v3(vis.current_position_earth_centered_km).sub(shipPos),prograde=safeUnit(vis.prograde_unit_earth_centered,new THREE.Vector3(0,1,0));
  const cue=new THREE.Group();cue.name='PROGRADE_PRESENTATION_CUE';
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(18,18,180,10),new THREE.MeshBasicMaterial({color:0x7fd7d0}));shaft.position.y=90;cue.add(shaft);
  const head=new THREE.Mesh(new THREE.ConeGeometry(55,120,12),new THREE.MeshBasicMaterial({color:0x7fd7d0}));head.position.y=240;cue.add(head);
  cue.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),prograde);cue.position.copy(currentRel);orbitGroup.add(cue);
  scene.add(orbitGroup);
}
function orbitCamera(camera){
  if(!live||userCamera)return false;
  const o=live.orbital_state||{},vis=live.orbit_visualization||{},w=live.wayfarer||{};
  if(!(o.operational_orbit===true&&vis.available===true&&Array.isArray(w.position_earth_centered_km)&&Array.isArray(w.velocity_earth_centered_km_s)))return false;
  const shipPos=v3(w.position_earth_centered_km),earthRel=shipPos.clone().multiplyScalar(-1),radial=shipPos.clone().normalize(),prograde=safeUnit(w.velocity_earth_centered_km_s,new THREE.Vector3(0,1,0));
  const normal=new THREE.Vector3().crossVectors(radial,prograde);if(normal.lengthSq()<1e-10)normal.set(0,0,1);else normal.normalize();
  if(cameraSel.value==='ORBIT'){
    const ap=Number(o.apoapsis_altitude_km),extent=6378.137+Math.max(Number.isFinite(ap)?ap:0,Number(o.altitude_km)||0,400);
    camera.position.copy(earthRel)
      .add(normal.clone().multiplyScalar(extent*3.25))
      .add(prograde.clone().multiplyScalar(extent*.70))
      .add(radial.clone().multiplyScalar(extent*.22));
    camera.up.copy(radial);camera.near=Math.max(.01,extent/10000);camera.far=Math.max(5000000,extent*20);camera.fov=52;camera.updateProjectionMatrix();camera.lookAt(earthRel);
    if(cameraState)cameraState.textContent='CAM DEFAULT / ORBIT OVERVIEW FIT';
    return true;
  }
  if(cameraSel.value==='CHASE'){
    camera.position.copy(prograde).multiplyScalar(-.24).add(radial.clone().multiplyScalar(.075));
    camera.up.copy(radial);camera.near=.001;camera.far=5000000;camera.fov=60;camera.updateProjectionMatrix();
    camera.lookAt(prograde.clone().multiplyScalar(.12).add(radial.clone().multiplyScalar(-.025)));
    if(cameraState)cameraState.textContent='CAM DEFAULT / ORBIT HORIZON';
    return true;
  }
  return false;
}
window.__loomBeforeRender=(scene,camera)=>{
  if(typeof previousBeforeRender==='function')previousBeforeRender(scene,camera);
  rebuildOrbit(scene);
  if(orbitGroup)orbitGroup.visible=cameraSel.value==='ORBIT';
  orbitCamera(camera);
};
window.addEventListener('loom-live-qualification',e=>{live=e&&e.detail||null;lastKey='';});
if(window.__loomLiveQualification)live=window.__loomLiveQualification;
canvas.addEventListener('pointerdown',()=>{if(cameraSel.value==='ORBIT'||cameraSel.value==='CHASE')userCamera=true;});
cameraSel.addEventListener('change',()=>{userCamera=false;if(cameraSel.value==='ORBIT'&&cameraState)cameraState.textContent='CAM DEFAULT / ORBIT OVERVIEW FIT';});
if(resetView)resetView.addEventListener('click',()=>{userCamera=false;});
})();
