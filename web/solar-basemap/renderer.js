/* Minimal Three.js adapter. Camera-relative coordinates are formed in JS doubles. */
(function(){
  const canvas=document.getElementById('scene');
  let renderer,scene,camera,handle,featureById={},geometryGroup;
  const state={eye:[0,0,0],target:[0,0,0],distance:50*149597870.7,travel:0,zoom:0,rotation:[0,0],draws:[],frameCount:0,lastTime:0,raf:[],isolatedFeature:null};
  const AU=149597870.7;
  function init(){
    if(!window.THREE)throw Error('Three.js r149 unavailable');
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,logarithmicDepthBuffer:true,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight,false);renderer.setClearColor(0x05070b,1);
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.001,1e7);camera.position.set(0,0,0);geometryGroup=new THREE.Group();scene.add(geometryGroup);
    addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();draw();});
    canvas.addEventListener('wheel',e=>{e.preventDefault();state.distance=Math.max(500,Math.min(8e9,state.distance*Math.exp(e.deltaY*.001)));state.zoom=distanceToZoom(state.distance);refresh();},{passive:false});
    const pointers=new Map();canvas.addEventListener('contextmenu',e=>e.preventDefault());canvas.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointerup',e=>pointers.delete(e.pointerId));canvas.addEventListener('pointercancel',e=>pointers.delete(e.pointerId));
    canvas.addEventListener('pointermove',e=>{const previous=pointers.get(e.pointerId);if(!previous)return;const others=[...pointers.entries()].filter(([id])=>id!==e.pointerId).map(([,p])=>p);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const dx=e.clientX-previous.x,dy=e.clientY-previous.y;
      if(others.length){const other=others[0],oldDistance=Math.hypot(previous.x-other.x,previous.y-other.y),newDistance=Math.hypot(e.clientX-other.x,e.clientY-other.y);if(oldDistance>1&&newDistance>1)state.distance=Math.max(500,Math.min(8e9,state.distance*oldDistance/newDistance));state.target[0]-=dx*state.distance/innerHeight;state.target[1]+=dy*state.distance/innerHeight;}
      else if(e.buttons===2||e.shiftKey||e.button===1){state.target[0]-=dx*state.distance/innerHeight;state.target[1]+=dy*state.distance/innerHeight;}
      else{state.rotation[0]-=dx*.005;state.rotation[1]=Math.max(-1.5,Math.min(1.5,state.rotation[1]-dy*.005));}refresh();});
    if(!renderer.capabilities.logarithmicDepthBuffer)throw Error('logarithmic depth buffer capability required');
    return renderer.capabilities.logarithmicDepthBuffer;
  }
  function distanceToZoom(d){return Math.max(0,Math.min(1000,1000*(Math.log(50*AU/d)/Math.log(50*AU/10000))))}
  function eyePosition(){const [yaw,pitch]=state.rotation,dir=[Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)];return state.target.map((x,i)=>x+dir[i]*state.distance)}
  function configure(h){handle=h;featureById=Object.fromEntries(h.catalog().map(f=>[f.body_id,f]));h.onChange(()=>{state.draws=h.drawList();draw();});state.target=[0,0,0];state.distance=50*AU;refresh();}
  function point(feature){return feature?.position_km||[0,0,0]}
  function currentView(){
    const scale=innerHeight/(2*Math.tan(Math.PI/8));const eye=eyePosition(),[yaw,pitch]=state.rotation,dir=[Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)],diagonal=Math.hypot(innerWidth,innerHeight);
    const visibleNodes=new Set(['solar']);const errors={},positions={};
    for(const n of handle.root.nodes){const anchor=featureById[n.anchor_id];if(!anchor||!anchor.position_km)continue;positions[n.node_id]=anchor.position_km;
      const center=n.anchor_position_km.map((x,i)=>x+n.content_bound.center_km[i]),rel=center.map((x,i)=>x-eye[i]);const depth=-rel.reduce((s,x,i)=>s+x*dir[i],0),radius=n.content_bound.radius_km;
      const radial=Math.sqrt(Math.max(0,rel.reduce((s,x)=>s+x*x,0)-depth*depth)),zmin=depth-radius;const near=zmin<=0;
      const K=near?Infinity:scale/zmin*Math.sqrt(1+Math.pow((radial+radius)/zmin,2));const diameter=2*radius*K;
      if(n.node_id==='solar'||diameter>=12)visibleNodes.add(n.node_id);
      errors[n.node_id]=(n.node_id==='solar'&&diameter>=16*diagonal)?0:K;
    }
    return {visibleNodes,errorScaleByNode:errors,eyeKm64:eye,orientation:state.rotation,verticalFov:45,widthCss:innerWidth,heightCss:innerHeight,dpr:devicePixelRatio||1};
  }
  function clear(){while(geometryGroup.children.length){const x=geometryGroup.children[geometryGroup.children.length-1];geometryGroup.remove(x);x.geometry?.dispose();x.material?.dispose();}}
  function draw(){
    if(!renderer||!handle)return;const t=performance.now();if(state.lastTime)state.raf.push(t-state.lastTime);state.lastTime=t;state.frameCount++;
    clear();const eye=eyePosition();const targetRel=state.target.map((x,i)=>(x-eye[i])/state.distance);camera.position.set(0,0,0);camera.lookAt(...targetRel);camera.updateMatrixWorld();
    const unit=state.distance/100,focal=innerHeight/(2*Math.tan(Math.PI/8));const lines=[];const featureStates=[];let markers=0,markerGpuErrorKm=0,markerGpuErrorCssPx=0;
    for(const f of handle.catalog()){
      if(!f.position_km){featureStates.push({body_id:f.body_id,resolution:f.resolution,renderer_status:'AUTHORITY_UNRESOLVED',reason:f.reason,submitted:false,visible:false});continue;}
      const localNode=handle.root.nodes.find(n=>n.node_id===f.node_id&&n.node_id!=='solar');
      let separationPx=null,markerAdmitted=true;if(localNode){const parent=featureById[localNode.anchor_id];if(parent?.position_km){const sep=Math.hypot(...f.position_km.map((x,i)=>x-parent.position_km[i]));separationPx=sep*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);markerAdmitted=separationPx>=8;}}
      const p=f.position_km.map((x,i)=>(x-eye[i])/unit);
      const clip=new THREE.Vector3(...p).project(camera),inFrustum=Math.abs(clip.x)<=1&&Math.abs(clip.y)<=1&&clip.z>=-1&&clip.z<=1;
      if(markerAdmitted&&inFrustum){const cam=new THREE.Vector3(...p).applyMatrix4(camera.matrixWorldInverse),depth=-cam.z,K=depth>0?focal/(depth*unit)*Math.sqrt(1+Math.pow(Math.hypot(cam.x,cam.y)/depth,2)):Infinity;for(const x of p){const error=Math.abs(Math.fround(x)-x)*unit;markerGpuErrorKm=Math.max(markerGpuErrorKm,error);markerGpuErrorCssPx=Math.max(markerGpuErrorCssPx,error*K);}}
      featureStates.push({body_id:f.body_id,resolution:f.resolution,renderer_status:!markerAdmitted?'LOD_SUPPRESSED':inFrustum?'SUBMITTED_VISIBLE':'FRUSTUM_CLIPPED',separation_css_px:separationPx,clip:[clip.x,clip.y,clip.z],submitted:markerAdmitted,visible:markerAdmitted&&inFrustum});
      if(!markerAdmitted||state.isolatedFeature&&state.isolatedFeature!==f.body_id)continue;
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));const m=new THREE.PointsMaterial({color:f.body_id==='SUN'?0xff8703:0x00d1ff,size:f.body_id==='SUN'?7:4,sizeAttenuation:false});geometryGroup.add(new THREE.Points(g,m));markers++;
    }
    for(const d of state.draws){if(state.isolatedFeature&&state.isolatedFeature!==d.curve.feature_id)continue;let opacity=.62;
      if(d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'){const rootNode=handle.root.nodes.find(n=>n.node_id==='solar');const dia=2*(rootNode?.content_bound?.radius_km||0)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);const diagonal=Math.hypot(innerWidth,innerHeight);if(dia>=16*diagonal)continue;if(dia>8*diagonal)opacity*=1-(dia-8*diagonal)/(8*diagonal);}
      else if(d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'){const node=handle.root.nodes.find(n=>n.anchor_id===d.curve.anchor_id&&n.node_id!=='solar');const dia=2*(node?.content_bound?.radius_km||0)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);if(dia<16)continue;opacity*=Math.min(1,(dia-16)/8);}
      const anchor=featureById[d.curve.anchor_id]?.position_km||[0,0,0];const pts=d.segment.points.map(p=>p.slice(1).map((v,i)=>(anchor[i]+v-eye[i])/unit));if(pts.length<2){lines.push({feature_id:d.curve.feature_id,semantic:d.curve.semantic,status:'SINGLE_POINT_NOT_DRAWN',vertices:pts.length});continue;}
      const clipPts=pts.map(p=>new THREE.Vector3(...p).project(camera));const inClip=clipPts.filter(p=>Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&p.z>=-1&&p.z<=1).length;
      const arr=new Float32Array(pts.flat());const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(arr,3));const m=new THREE.LineBasicMaterial({color:d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'?0x7ee7d1:0xff8703,transparent:true,opacity});geometryGroup.add(new THREE.Line(g,m));const visibleIndices=clipPts.map((p,i)=>({p,i})).filter(x=>Math.abs(x.p.x)<=1&&Math.abs(x.p.y)<=1&&x.p.z>=-1&&x.p.z<=1).map(x=>x.i);let gpuError=0,gpuErrorCss=0;for(const i of visibleIndices){const cam=new THREE.Vector3(...pts[i]).applyMatrix4(camera.matrixWorldInverse),depth=-cam.z,K=depth>0?focal/(depth*unit)*Math.sqrt(1+Math.pow(Math.hypot(cam.x,cam.y)/depth,2)):Infinity;for(const v of pts[i]){const error=Math.abs(Math.fround(v)-v)*unit;gpuError=Math.max(gpuError,error);gpuErrorCss=Math.max(gpuErrorCss,error*K);}}lines.push({feature_id:d.curve.feature_id,node_id:d.node_id,semantic:d.curve.semantic,anchor_id:d.curve.anchor_id,status:inClip?'SUBMITTED_WITH_PROJECTED_VERTICES':'SUBMITTED_TO_GPU_CLIPPING',vertices:pts.length,clip_vertices:inClip,segment_id:d.segment.body_source_ref+'|'+d.segment.anchor_source_ref,float32Input:Array.from(arr),cameraRelativeKm:pts.map(p=>p.map(x=>Math.fround(x)*unit)),gpuConversionMaxKm:gpuError,gpuConversionMaxCssPx:gpuErrorCss});}
    camera.near=.0001;camera.far=10000;camera.updateProjectionMatrix();renderer.render(scene,camera);
    const intervals=state.raf.slice(-200).sort((a,b)=>a-b);const vertices=renderer.info.render.points+renderer.info.render.lines;const report={eyeKm64:eye,targetKm64:state.target,cameraDistanceKm:state.distance,unitKmPerRenderUnit:unit,projectionPixelsPerKm:innerHeight/(2*Math.tan(Math.PI/8))/state.distance,markerGpuErrorKm,markerGpuErrorCssPx,features:featureStates,lines,drawCalls:renderer.info.render.calls,vertices,gpu_geometry_count:renderer.info.memory.geometries,gpu_buffer_bytes_estimate:vertices*3*4,frameCount:state.frameCount,frame_interval_ms:intervals,max_frame_interval_ms:intervals.at(-1)||0,frames_over_33ms:state.raf.filter(x=>x>33.4).length,near:camera.near,far:camera.far};
    window.__solarBasemapScene=report;return report;
  }
  let scheduled=false;async function refresh(){state.zoom=distanceToZoom(state.distance);document.getElementById('zoom').value=String(state.zoom);if(!scheduled){scheduled=true;requestAnimationFrame(async()=>{scheduled=false;const view=currentView();state.draws=await handle.updateView(view);draw();window.__solarBasemapView=view;});}}
  function moveToward(id, distance){const f=featureById[id];if(!f?.position_km)throw Error(`${id} has no governed epoch position`);state.target=[...f.position_km];state.distance=distance;refresh();}
  async function replayApproach(id,startDistance,endDistance,steps=80){const f=featureById[id];if(!f?.position_km)throw Error(`${id} has no governed epoch position`);const initial=[0,0,0];for(let i=0;i<=steps;i++){const u=i/steps,s=u*u*(3-2*u);state.target=initial.map((x,k)=>x+(f.position_km[k]-x)*s);state.distance=startDistance*Math.pow(endDistance/startDistance,s);await new Promise(resolve=>requestAnimationFrame(resolve));}await refresh();return {id,steps,startDistance,endDistance,target:[...state.target]};}
  function setZoom(value){const z=Number(value);state.zoom=z;state.distance=50*AU/Math.exp((z/1000)*Math.log(50*AU/10000));refresh();}
  function isolate(id){state.isolatedFeature=id||null;draw();}
  function fit(){state.target=[0,0,0];state.distance=50*AU;state.rotation=[0,0];refresh()}
  window.__solarBasemapReadPixels=()=>{const gl=renderer.getContext(),w=renderer.domElement.width,h=renderer.domElement.height,ratio=renderer.getPixelRatio(),p=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,p);const rects=[...document.querySelectorAll('header,.hud,.catalog.open,.report.open')].map(x=>x.getBoundingClientRect());let mint=0,amber=0,lit=0,excluded=0;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const top=(h-1-y)/ratio,left=x/ratio;if(rects.some(r=>left>=r.left&&left<r.right&&top>=r.top&&top<r.bottom)){excluded++;continue;}const i=(y*w+x)*4,r=p[i],g=p[i+1],b=p[i+2];if(r>20||g>20||b>20)lit++;if(r>35&&g>r*1.2&&b>r*1.1)mint++;if(r>g*1.3&&g>b*1.05)amber++;}return {width:w,height:h,render_dpr:ratio,mint_line_pixels:mint,amber_line_pixels:amber,lit_pixels:lit,excluded_overlay_pixels:excluded};};
  window.LoomRenderer={init,configure,moveToward,setZoom,fit,draw,refresh,replayApproach,isolate,state};
})();
