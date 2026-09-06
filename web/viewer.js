(function(){
'use strict';

var stage=document.getElementById('stage'),panel=document.getElementById('panel'),status=document.getElementById('status'),validation=document.getElementById('validation');

function fail(label,err){
  var detail=(err&&err.stack)?err.stack:String(err||'unknown error');
  validation.textContent='STARTUP ERROR';validation.style.borderColor='#a55';
  status.textContent=label+'\n'+detail;
  if(window.__wayfarerShowError)window.__wayfarerShowError(label,detail);
}

try{
  if(typeof THREE==='undefined')throw new Error('THREE global is unavailable; classic Three.js did not load');

  var scene=new THREE.Scene();scene.background=new THREE.Color(0x0b0d10);
  var camera=new THREE.PerspectiveCamera(42,1,0.1,500);
  var renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));stage.prepend(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff,0x333333,2.2));var sun=new THREE.DirectionalLight(0xffffff,2.5);sun.position.set(-25,25,30);scene.add(sun);
  var root=new THREE.Group();scene.add(root);var clickable=[];var payload=null,dragging=false,lastX=0,lastY=0,theta=.55,phi=.9,distance=85,target=new THREE.Vector3(28,0,0);

  function matFor(statusName,group){var base={habitat:0xd8d6c9,tanks:0x9b9b96,structure:0x555b62,launch_bay:0x7b7367,launch:0xd6d0bd,radiators:0x27292b,propulsion:0x68676a,docking:0xb0a893}[group]||0x888888;return new THREE.MeshStandardMaterial({color:base,metalness:.45,roughness:.58,transparent:true,opacity:statusName==='OPEN'?.45:1});}
  function cylinderX(length,diameter,mat){var g=new THREE.CylinderGeometry(diameter/2,diameter/2,length,24);g.rotateZ(Math.PI/2);return new THREE.Mesh(g,mat);}
  function box(x,y,z,mat){return new THREE.Mesh(new THREE.BoxGeometry(x,y,z),mat);}
  function nozzle(length,diameter,mat){var g=new THREE.CylinderGeometry(diameter/2,diameter*.28,length,32,1,true);g.rotateZ(Math.PI/2);return new THREE.Mesh(g,mat);}
  function radiator(c,mat){var deployed=document.getElementById('radiators').value==='DEPLOYED',az=THREE.MathUtils.degToRad(c.dimensions.azimuth_deg),mesh;if(deployed){mesh=box(c.dimensions.root_length_m,c.dimensions.panel_chord_m,.12,mat);mesh.position.y=Math.cos(az)*8;mesh.position.z=Math.sin(az)*8;mesh.rotation.x=az;}else{mesh=box(c.dimensions.root_length_m,.18,6.5,mat);mesh.rotation.x=az;}return mesh;}
  function build(){while(root.children.length)root.remove(root.children[0]);clickable.length=0;var launchState=document.getElementById('launch').value,showOpen=document.getElementById('openGeom').checked;payload.components.forEach(function(c){if(c.status==='OPEN'&&!showOpen&&c.group!=='radiators')return;if(c.id==='planetary_launch'&&launchState==='ABSENT')return;var m=matFor(c.status,c.group),mesh;if(c.kind==='cylinder_x')mesh=cylinderX(c.dimensions.length_m,c.dimensions.diameter_m,m);else if(c.kind==='box')mesh=box(c.dimensions.x_m,c.dimensions.y_m,c.dimensions.z_m,m);else if(c.kind==='nozzle_x')mesh=nozzle(c.dimensions.length_m,c.dimensions.aperture_diameter_m,m);else if(c.kind==='radiator_placeholder')mesh=radiator(c,m);else if(c.kind==='collar_z'){mesh=cylinderX(c.dimensions.depth_m,c.dimensions.diameter_m,m);mesh.rotation.y=Math.PI/2;}else return;mesh.position.add(new THREE.Vector3(c.center_m[0],c.center_m[1],c.center_m[2]));mesh.userData.component=c;root.add(mesh);clickable.push(mesh);});status.textContent=payload.components.length+' components • launch '+launchState+' • radiators '+document.getElementById('radiators').value;}
  function updateCamera(){var cp=Math.cos(phi),sp=Math.sin(phi);camera.position.set(target.x+distance*cp*Math.cos(theta),target.y+distance*sp,target.z+distance*cp*Math.sin(theta));camera.lookAt(target);}
  function resize(){var w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
  function setView(v){target.set(28,0,0);if(v==='side'){theta=0;phi=.04;distance=85;}else if(v==='top'){theta=0;phi=1.45;distance=85;}else if(v==='front'){theta=Math.PI;phi=.04;target.set(0,0,0);distance=70;}else if(v==='aft'){theta=0;phi=.04;target.set(57,0,0);distance=70;}else{theta=.55;phi=.65;distance=85;}updateCamera();}

  renderer.domElement.addEventListener('pointerdown',function(e){dragging=true;lastX=e.clientX;lastY=e.clientY;if(renderer.domElement.setPointerCapture)renderer.domElement.setPointerCapture(e.pointerId);});
  renderer.domElement.addEventListener('pointermove',function(e){if(!dragging)return;theta-=(e.clientX-lastX)*.008;phi=Math.max(-1.45,Math.min(1.45,phi+(e.clientY-lastY)*.008));lastX=e.clientX;lastY=e.clientY;updateCamera();});
  renderer.domElement.addEventListener('pointerup',function(){dragging=false;});
  renderer.domElement.addEventListener('wheel',function(e){distance=Math.max(18,Math.min(180,distance+e.deltaY*.05));updateCamera();e.preventDefault();},{passive:false});
  renderer.domElement.addEventListener('click',function(e){var r=renderer.domElement.getBoundingClientRect(),mouse=new THREE.Vector2(((e.clientX-r.left)/r.width)*2-1,-((e.clientY-r.top)/r.height)*2+1),ray=new THREE.Raycaster();ray.setFromCamera(mouse,camera);var hit=ray.intersectObjects(clickable)[0];if(hit)panel.textContent=JSON.stringify(hit.object.userData.component,null,2);});
  ['launch','radiators','openGeom'].forEach(function(id){document.getElementById(id).addEventListener('change',build);});
  document.getElementById('view').addEventListener('change',function(e){setView(e.target.value);});window.addEventListener('resize',resize);

  fetch('/geometry/wayfarer_geometry.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('geometry HTTP '+r.status);return r.json();}).then(function(data){payload=data;validation.textContent=payload.validation.overall_pass?'VALIDATION PASS':'VALIDATION FAIL';validation.style.borderColor=payload.validation.overall_pass?'#5a5':'#a55';resize();setView('iso');build();(function loop(){renderer.render(scene,camera);window.requestAnimationFrame(loop);})();}).catch(function(err){fail('Geometry startup failed',err);});
}catch(err){fail('Viewer startup failed',err);}
})();
