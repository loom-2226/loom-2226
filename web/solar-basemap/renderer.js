/* Minimal Three.js adapter. Camera-relative coordinates are formed in JS doubles. */
(function(){
  const canvas=document.getElementById('scene');
  let renderer,scene,camera,handle,featureById={},geometryGroup;
  const state={eye:[0,0,0],target:[0,0,0],distance:50*149597870.7,travel:0,zoom:0,rotation:[0,0],draws:[],frameCount:0,lastTime:0,raf:[],isolatedFeature:null};
  const AU=149597870.7;
  const PLANETS=new Set(['MERCURY','VENUS','EARTH','MARS','JUPITER','SATURN','URANUS','NEPTUNE']);
  const SUN_LABEL_MIN_DIAMETER_CSS_PX=5,PLANET_LABEL_MIN_SEPARATION_CSS_PX=22,MINOR_LABEL_MIN_SEPARATION_CSS_PX=20;
  const MARS_PARENT_CONTEXT_RADIUS_KM=5_000_000,MARS_CONTEXT_ARC_RADIUS_KM=5_000_000;
  function tokenColor(name,fallback){return getComputedStyle(document.documentElement).getPropertyValue(name).trim()||fallback}
  function basis(){const [yaw,pitch]=state.rotation;return {right:[Math.cos(yaw),0,-Math.sin(yaw)],up:[-Math.sin(yaw)*Math.sin(pitch),Math.cos(pitch),-Math.cos(yaw)*Math.sin(pitch)]}}
  function screenOffset(x,y,d){const t=Math.tan(Math.PI/8),nx=2*x/innerWidth-1,ny=1-2*y/innerHeight,{right,up}=basis();return right.map((v,i)=>v*nx*d*t*camera.aspect+up[i]*ny*d*t)}
  function zoomAnchor(x,y){const [yaw,pitch]=state.rotation,dir=[Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)],{right,up}=basis(),nx=2*x/innerWidth-1,ny=1-2*y/innerHeight,tan=Math.tan(Math.PI/8),ray=dir.map((v,i)=>-v+right[i]*nx*tan*camera.aspect+up[i]*ny*tan),mag=Math.hypot(...ray),unit=ray.map(v=>v/mag),eye=eyePosition();let best=null;
    for(const f of Object.values(featureById)){if(!f.position_km)continue;const rel=f.position_km.map((v,i)=>v-eye[i]),along=rel.reduce((sum,v,i)=>sum+v*unit[i],0);if(along<=0)continue;const miss=Math.sqrt(Math.max(0,rel.reduce((sum,v)=>sum+v*v,0)-along*along)),missCss=miss*innerHeight/(2*tan*along);if(missCss<=8&&(!best||along<best.along))best={world:f.position_km,along};}
    if(best)return {...best,ray:unit,distance:state.distance,view:dir};const world=worldAtScreen(x,y),along=state.distance*mag;return {world,along,ray:unit,distance:state.distance,view:dir};
  }
  function worldAtScreen(x,y,d=state.distance){const o=screenOffset(x,y,d);return state.target.map((v,i)=>v+o[i])}
  function keepAnchorAtScreen(anchor,d){const nextEye=anchor.world.map((v,i)=>v-anchor.ray[i]*anchor.along*d/anchor.distance);state.target=nextEye.map((v,i)=>v-anchor.view[i]*d);state.distance=d;state.zoom=distanceToZoom(d)}
  function zoomAt(factor,x,y){const anchor=zoomAnchor(x,y),d=Math.max(500,Math.min(8e9,state.distance*factor));keepAnchorAtScreen(anchor,d);refresh()}
  function panBy(dx,dy){const {right,up}=basis(),kmPerCss=state.distance/(innerHeight/(2*Math.tan(Math.PI/8)));state.target=state.target.map((v,i)=>v-right[i]*dx*kmPerCss+up[i]*dy*kmPerCss);refresh()}
  function scaleLabel(km){if(km>=AU*.1)return `${(km/AU).toPrecision(3)} AU`;return `${Math.round(km).toLocaleString('en-US')} km`}
  function updateScaleAndLabels(){
    const pxPerKm=innerHeight/(2*Math.tan(Math.PI/8)*state.distance),rawKm=88/pxPerKm,power=10**Math.floor(Math.log10(rawKm)),scaled=rawKm/power,unit=(scaled>=5?5:scaled>=2?2:1)*power,bar=document.getElementById('scaleBar');
    const mars=featureById.MARS?.position_km||[0,0,0],marsOffset=Math.hypot(...mars.map((v,i)=>v-state.target[i]));document.getElementById('sceneContext').textContent=`SUN-CENTERED · MARS Δ ${scaleLabel(marsOffset)}`;
    document.getElementById('scaleText').textContent=`1 px ≈ ${scaleLabel(1/pxPerKm)} @ center`;
    bar.style.width=`${Math.max(24,unit*pxPerKm)}px`;bar.dataset.distanceKm=String(unit);bar.dataset.label=scaleLabel(unit);bar.setAttribute('aria-label',`${scaleLabel(unit)} at scene center`);bar.textContent='';
    const layer=document.getElementById('labels'),wanted=new Set();const sun=featureById.SUN?.position_km||[0,0,0],sunDiameter=1392700*pxPerKm;
    for(const f of Object.values(featureById)){if(!f.position_km)continue;const p=f.position_km.map((v,i)=>(v-eyePosition()[i])/(state.distance/100)),clip=new THREE.Vector3(...p).project(camera);if(clip.z < -1||clip.z>1||Math.abs(clip.x)>1.2||Math.abs(clip.y)>1.2)continue;
      let kind='minor',show=false;if(f.body_id==='SUN'){kind='sun';show=sunDiameter>=SUN_LABEL_MIN_DIAMETER_CSS_PX}else if(PLANETS.has(f.body_id)){kind='planet';const q=f.position_km.map((v,i)=>(v-sun[i])*pxPerKm),sep=Math.hypot(...q);show=sep>=PLANET_LABEL_MIN_SEPARATION_CSS_PX}else{const node=handle.root.nodes.find(n=>n.node_id===f.node_id&&n.node_id!=='solar');if(node){const parent=featureById[node.anchor_id]?.position_km||sun,sep=Math.hypot(...f.position_km.map((v,i)=>(v-parent[i])*pxPerKm));show=sep>=MINOR_LABEL_MIN_SEPARATION_CSS_PX}}
      if(!show)continue;wanted.add(f.body_id);let el=document.getElementById(`body-label-${f.body_id}`);if(!el){el=document.createElement('span');el.id=`body-label-${f.body_id}`;el.className=`body-label ${kind}`;el.textContent=f.name||f.body_id;layer.appendChild(el)}el.style.left=`${(clip.x+1)*innerWidth/2+7}px`;el.style.top=`${(1-clip.y)*innerHeight/2-9}px`;el.dataset.kind=kind;
    }for(const el of [...layer.children])if(!wanted.has(el.id.slice('body-label-'.length)))el.remove();
  }
  function init(){
    if(!window.THREE)throw Error('Three.js r149 unavailable');
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,logarithmicDepthBuffer:true,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight,false);renderer.setClearColor(0x05070b,1);
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.001,1e7);camera.position.set(0,0,0);geometryGroup=new THREE.Group();scene.add(geometryGroup);
    addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();draw();});
    canvas.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(e.deltaY*.001),e.clientX,e.clientY)},{passive:false});
    const pointers=new Map();canvas.addEventListener('contextmenu',e=>e.preventDefault());canvas.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,button:e.button,shift:e.shiftKey});canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointerup',e=>pointers.delete(e.pointerId));canvas.addEventListener('pointercancel',e=>pointers.delete(e.pointerId));
    canvas.addEventListener('pointermove',e=>{const previous=pointers.get(e.pointerId);if(!previous)return;const others=[...pointers.entries()].filter(([id])=>id!==e.pointerId).map(([,p])=>p);pointers.set(e.pointerId,{...previous,x:e.clientX,y:e.clientY});const dx=e.clientX-previous.x,dy=e.clientY-previous.y;
      if(others.length){const other=others[0],oldCenter={x:(previous.x+other.x)/2,y:(previous.y+other.y)/2},newCenter={x:(e.clientX+other.x)/2,y:(e.clientY+other.y)/2},oldDistance=Math.hypot(previous.x-other.x,previous.y-other.y),newDistance=Math.hypot(e.clientX-other.x,e.clientY-other.y),oldAngle=Math.atan2(previous.y-other.y,previous.x-other.x),newAngle=Math.atan2(e.clientY-other.y,e.clientX-other.x);let turn=newAngle-oldAngle;while(turn>Math.PI)turn-=2*Math.PI;while(turn< -Math.PI)turn+=2*Math.PI;
        if(Math.abs(turn)>.12){state.rotation[0]-=turn;refresh()}else if(oldDistance>1&&newDistance>1)zoomAt(oldDistance/newDistance,newCenter.x,newCenter.y);
        if(Math.abs(newCenter.x-oldCenter.x)+Math.abs(newCenter.y-oldCenter.y)>0)panBy(newCenter.x-oldCenter.x,newCenter.y-oldCenter.y);
      }else if(e.buttons===2||e.shiftKey||previous.button===2||previous.shift){state.rotation[0]-=dx*.005;state.rotation[1]=Math.max(-1.5,Math.min(1.5,state.rotation[1]-dy*.005));refresh()}
      else panBy(dx,dy);});
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
      const radial=Math.sqrt(Math.max(0,rel.reduce((s,x)=>s+x*x,0)-depth*depth)),zmin=depth-radius;
      // A bound wholly behind the camera cannot contribute pixels. Do not turn
      // its negative depth into infinite SSE and enqueue unrelated system LODs.
      if(depth+radius<=0){errors[n.node_id]=0;continue;}
      const near=zmin<=0;
      const K=near?Infinity:scale/zmin*Math.sqrt(1+Math.pow((radial+radius)/zmin,2));const diameter=2*radius*K;
      if(n.node_id==='solar'||diameter>=12)visibleNodes.add(n.node_id);
      errors[n.node_id]=(n.node_id==='solar'&&diameter>=16*diagonal)?0:K;
    }
    // The Solar node spans the full system, so its bounding sphere can contain
    // the camera and collapse zmin to zero. Measure the projected error scale
    // against the actual governed heliocentric samples instead of suppressing
    // Solar refinement or assigning infinite SSE to the whole-system bound.
    let solarCurveScale=0;for(const c of handle.root.curves){if(c.semantic!=='HELIOCENTRIC_REFERENCE_ORBIT'||c.anchor_id!=='SUN')continue;const anchor=featureById.SUN?.position_km||[0,0,0];for(const segment of c.segments||[])for(const p of segment.points||[]){const world=p.slice(1).map((v,i)=>anchor[i]+v),rel=world.map((v,i)=>v-eye[i]),depth=-rel.reduce((sum,v,i)=>sum+v*dir[i],0);if(depth<=0)continue;const radial=Math.sqrt(Math.max(0,rel.reduce((sum,v)=>sum+v*v,0)-depth*depth));solarCurveScale=Math.max(solarCurveScale,scale/depth*Math.sqrt(1+Math.pow(radial/depth,2)));}}
    errors.solar=solarCurveScale||scale/state.distance;
    return {visibleNodes,errorScaleByNode:errors,eyeKm64:eye,orientation:state.rotation,verticalFov:45,widthCss:innerWidth,heightCss:innerHeight,dpr:devicePixelRatio||1};
  }
  function curveExtentKm(curve){let extent=0;for(const segment of curve.segments||[])for(const point of segment.points||[])extent=Math.max(extent,Math.hypot(point[1],point[2],point[3]));return extent;}
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
      const symbolKind=f.body_id==='SUN'?'sun':PLANETS.has(f.body_id)?'planet':'minor',symbolSizeCssPx=symbolKind==='sun'?9:symbolKind==='planet'?6:4,symbolColor=symbolKind==='sun'?tokenColor('--loom-brand-color-accent-amber','#FF8703'):symbolKind==='planet'?tokenColor('--loom-brand-color-accent-ion-blue','#00D1FF'):tokenColor('--loom-brand-color-secondary-mint','#7EE7D1');
      featureStates.push({body_id:f.body_id,resolution:f.resolution,renderer_status:!markerAdmitted?'LOD_SUPPRESSED':inFrustum?'SUBMITTED_VISIBLE':'FRUSTUM_CLIPPED',separation_css_px:separationPx,clip:[clip.x,clip.y,clip.z],submitted:markerAdmitted,visible:markerAdmitted&&inFrustum,symbol_kind:symbolKind,symbol_size_css_px:symbolSizeCssPx,symbol_color:symbolColor});
      if(!markerAdmitted||state.isolatedFeature&&state.isolatedFeature!==f.body_id)continue;
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));const m=new THREE.PointsMaterial({color:symbolColor,size:symbolSizeCssPx,sizeAttenuation:false});geometryGroup.add(new THREE.Points(g,m));markers++;
    }
    for(const d of state.draws){if(state.isolatedFeature&&state.isolatedFeature!==d.curve.feature_id)continue;let opacity=d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'?.28:.44;
      const marsPosition=featureById.MARS?.position_km||[0,0,0],marsParentContext=d.curve.feature_id==='MARS'&&d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'&&Math.hypot(...state.target.map((v,i)=>v-marsPosition[i]))<=MARS_PARENT_CONTEXT_RADIUS_KM;
      if(d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'){const dia=2*curveExtentKm(d.curve)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);const diagonal=Math.hypot(innerWidth,innerHeight);if(!marsParentContext&&dia>=16*diagonal)continue;if(!marsParentContext&&dia>8*diagonal)opacity*=1-(dia-8*diagonal)/(8*diagonal);if(marsParentContext)opacity=.12;}
      else if(d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'){const node=handle.root.nodes.find(n=>n.anchor_id===d.curve.anchor_id&&n.node_id!=='solar');const dia=2*(node?.content_bound?.radius_km||0)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);if(dia<16)continue;const fade=Math.min(1,(dia-16)/8);opacity*=d.node_id==='system:MARS'?Math.max(.35,fade):fade;}
      const anchor=featureById[d.curve.anchor_id]?.position_km||[0,0,0];let sourcePoints=d.segment.points;if(marsParentContext){let nearest={distance:Infinity,index:0};for(let i=0;i<sourcePoints.length;i++){const w=sourcePoints[i].slice(1).map((v,k)=>anchor[k]+v),distance=Math.hypot(...w.map((v,k)=>v-marsPosition[k]));if(distance<nearest.distance)nearest={distance,index:i};}let lo=nearest.index,hi=nearest.index;while(lo>0&&Math.hypot(...sourcePoints[lo-1].slice(1).map((v,k)=>anchor[k]+v-marsPosition[k]))<=MARS_CONTEXT_ARC_RADIUS_KM)lo--;while(hi+1<sourcePoints.length&&Math.hypot(...sourcePoints[hi+1].slice(1).map((v,k)=>anchor[k]+v-marsPosition[k]))<=MARS_CONTEXT_ARC_RADIUS_KM)hi++;sourcePoints=sourcePoints.slice(lo,hi+1);}
      const pts=sourcePoints.map(p=>p.slice(1).map((v,i)=>(anchor[i]+v-eye[i])/unit));if(pts.length<2){lines.push({feature_id:d.curve.feature_id,semantic:d.curve.semantic,status:'SINGLE_POINT_NOT_DRAWN',vertices:pts.length});continue;}
      const clipPts=pts.map(p=>new THREE.Vector3(...p).project(camera));const inClip=clipPts.filter(p=>Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&p.z>=-1&&p.z<=1).length;
      const arr=new Float32Array(pts.flat());const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(arr,3));const color=d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'?tokenColor('--loom-brand-color-secondary-mint','#7EE7D1'):tokenColor('--loom-brand-color-accent-amber','#FF8703'),m=new THREE.LineBasicMaterial({color,transparent:true,opacity});geometryGroup.add(new THREE.Line(g,m));const visibleIndices=clipPts.map((p,i)=>({p,i})).filter(x=>Math.abs(x.p.x)<=1&&Math.abs(x.p.y)<=1&&x.p.z>=-1&&x.p.z<=1).map(x=>x.i);let gpuError=0,gpuErrorCss=0;for(const i of visibleIndices){const cam=new THREE.Vector3(...pts[i]).applyMatrix4(camera.matrixWorldInverse),depth=-cam.z,K=depth>0?focal/(depth*unit)*Math.sqrt(1+Math.pow(Math.hypot(cam.x,cam.y)/depth,2)):Infinity;for(const v of pts[i]){const error=Math.abs(Math.fround(v)-v)*unit;gpuError=Math.max(gpuError,error);gpuErrorCss=Math.max(gpuErrorCss,error*K);}}lines.push({feature_id:d.curve.feature_id,node_id:d.node_id,level:d.level,semantic:d.curve.semantic,anchor_id:d.curve.anchor_id,presentation_context:marsParentContext?'MARS_HELIOCENTRIC_LOCAL_ARC':null,context_radius_km:marsParentContext?MARS_CONTEXT_ARC_RADIUS_KM:null,opacity,status:inClip?'SUBMITTED_WITH_PROJECTED_VERTICES':'SUBMITTED_TO_GPU_CLIPPING',vertices:pts.length,clip_vertices:inClip,segment_id:d.segment.body_source_ref+'|'+d.segment.anchor_source_ref,float32Input:Array.from(arr),cameraRelativeKm:pts.map(p=>p.map(x=>Math.fround(x)*unit)),gpuConversionMaxKm:gpuError,gpuConversionMaxCssPx:gpuErrorCss});}
    camera.near=.0001;camera.far=10000;camera.updateProjectionMatrix();renderer.render(scene,camera);
    const intervals=state.raf.slice(-200).sort((a,b)=>a-b);const vertices=renderer.info.render.points+renderer.info.render.lines;const report={eyeKm64:eye,targetKm64:state.target,cameraDistanceKm:state.distance,unitKmPerRenderUnit:unit,projectionPixelsPerKm:innerHeight/(2*Math.tan(Math.PI/8))/state.distance,markers,markerGpuErrorKm,markerGpuErrorCssPx,features:featureStates,lines,drawCalls:renderer.info.render.calls,vertices,gpu_geometry_count:renderer.info.memory.geometries,gpu_buffer_bytes_estimate:vertices*3*4,frameCount:state.frameCount,frame_interval_ms:intervals,max_frame_interval_ms:intervals.at(-1)||0,frames_over_33ms:state.raf.filter(x=>x>33.4).length,near:camera.near,far:camera.far};
    window.__solarBasemapScene=report;updateScaleAndLabels();return report;
  }
  let scheduled=false;async function refresh(){state.zoom=distanceToZoom(state.distance);if(!scheduled){scheduled=true;requestAnimationFrame(async()=>{scheduled=false;const view=currentView();await handle.updateView(view);state.draws=handle.drawList();draw();window.__solarBasemapView=view;});}}
  function moveToward(id, distance){const f=featureById[id];if(!f?.position_km)throw Error(`${id} has no governed epoch position`);state.target=[...f.position_km];state.distance=distance;refresh();}
  async function replayApproach(id,startDistance,endDistance,steps=80){
    const f=featureById[id];if(!f?.position_km)throw Error(`${id} has no governed epoch position`);
    const initial=[0,0,0],initialFrame=state.frameCount;
    for(let i=0;i<=steps;i++){
      const u=i/steps,s=u*u*(3-2*u);
      await new Promise(resolve=>requestAnimationFrame(()=>{
        state.target=initial.map((x,k)=>x+(f.position_km[k]-x)*s);
        state.distance=startDistance*Math.pow(endDistance/startDistance,s);
        state.zoom=distanceToZoom(state.distance);
        refresh();
        draw();
        resolve();
      }));
    }
    await refresh();
    return {id,steps,startDistance,endDistance,target:[...state.target],draw_frames:state.frameCount-initialFrame};
  }
  function setZoom(value){const z=Number(value);state.zoom=z;state.distance=50*AU/Math.exp((z/1000)*Math.log(50*AU/10000));refresh();}
  function isolate(id){state.isolatedFeature=id||null;draw();}
  function fit(){state.target=[0,0,0];state.distance=50*AU;state.rotation=[0,0];refresh()}
  window.__solarBasemapReadPixels=()=>{const gl=renderer.getContext(),w=renderer.domElement.width,h=renderer.domElement.height,ratio=renderer.getPixelRatio(),p=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,p);const rects=[...document.querySelectorAll('header,.hud,.catalog.open,.report.open')].map(x=>x.getBoundingClientRect());let mint=0,amber=0,lit=0,excluded=0;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const top=(h-1-y)/ratio,left=x/ratio;if(rects.some(r=>left>=r.left&&left<r.right&&top>=r.top&&top<r.bottom)){excluded++;continue;}const i=(y*w+x)*4,r=p[i],g=p[i+1],b=p[i+2];if(r>20||g>20||b>20)lit++;if(r>35&&g>r*1.2&&b>r*1.1)mint++;if(r>g*1.3&&g>b*1.05)amber++;}return {width:w,height:h,render_dpr:ratio,mint_line_pixels:mint,amber_line_pixels:amber,lit_pixels:lit,excluded_overlay_pixels:excluded};};
  window.LoomRenderer={init,configure,moveToward,setZoom,fit,draw,refresh,replayApproach,isolate,state};
})();
