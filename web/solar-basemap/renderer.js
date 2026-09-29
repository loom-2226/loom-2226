/* Minimal Three.js adapter. Camera-relative coordinates are formed in JS doubles. */
(function(){
  const canvas=document.getElementById('scene');
  let renderer,scene,camera,handle,featureById={},geometryGroup,symbolTextures={};
  const state={eye:[0,0,0],target:[0,0,0],distance:50*149597870.7,travel:0,zoom:0,rotation:[0,0],draws:[],frameCount:0,lastTime:0,raf:[],isolatedFeature:null,selectedBodyId:null};
  const AU=149597870.7;
  const SUN_LABEL_MIN_DIAMETER_CSS_PX=5,PLANET_LABEL_MIN_SEPARATION_CSS_PX=22,MINOR_LABEL_MIN_SEPARATION_CSS_PX=20;
  const LOCAL_CONTEXT_MIN_RADIUS_KM=5_000_000,LOCAL_CONTEXT_BOUND_MULTIPLIER=160;
  const PINCH_DEADBAND_CSS_PX=6,PINCH_LOG_GAIN=.82,PINCH_MAX_RATIO=3;
  let focusMotion=null;
  function tokenColor(name,fallback){return getComputedStyle(document.documentElement).getPropertyValue(name).trim()||fallback}
  function basis(){const [yaw,pitch]=state.rotation;return {right:[Math.cos(yaw),0,-Math.sin(yaw)],up:[-Math.sin(yaw)*Math.sin(pitch),Math.cos(pitch),-Math.cos(yaw)*Math.sin(pitch)]}}
  function screenOffset(x,y,d){const t=Math.tan(Math.PI/8),nx=2*x/innerWidth-1,ny=1-2*y/innerHeight,{right,up}=basis();return right.map((v,i)=>v*nx*d*t*camera.aspect+up[i]*ny*d*t)}
  function zoomAnchor(x,y){const [yaw,pitch]=state.rotation,dir=[Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)],{right,up}=basis(),nx=2*x/innerWidth-1,ny=1-2*y/innerHeight,tan=Math.tan(Math.PI/8),ray=dir.map((v,i)=>-v+right[i]*nx*tan*camera.aspect+up[i]*ny*tan),mag=Math.hypot(...ray),unit=ray.map(v=>v/mag),eye=eyePosition();let best=null;
    const selected=featureById[state.selectedBodyId],selectedVisible=window.__solarBasemapScene?.features?.some(f=>f.body_id===state.selectedBodyId&&f.visible);
    if(selected?.position_km&&selectedVisible){const rel=selected.position_km.map((v,i)=>v-eye[i]),along=Math.hypot(...rel);return {world:selected.position_km,along,ray:rel.map(v=>v/along),distance:state.distance,view:dir};}
    for(const f of Object.values(featureById)){if(!f.position_km)continue;const rel=f.position_km.map((v,i)=>v-eye[i]),along=rel.reduce((sum,v,i)=>sum+v*unit[i],0);if(along<=0)continue;const miss=Math.sqrt(Math.max(0,rel.reduce((sum,v)=>sum+v*v,0)-along*along)),missCss=miss*innerHeight/(2*tan*along);if(missCss<=8&&(!best||along<best.along))best={world:f.position_km,along};}
    if(best)return {...best,ray:unit,distance:state.distance,view:dir};const world=worldAtScreen(x,y),along=state.distance*mag;return {world,along,ray:unit,distance:state.distance,view:dir};
  }
  function worldAtScreen(x,y,d=state.distance){const o=screenOffset(x,y,d);return state.target.map((v,i)=>v+o[i])}
  function keepAnchorAtScreen(anchor,d){const nextEye=anchor.world.map((v,i)=>v-anchor.ray[i]*anchor.along*d/anchor.distance);state.target=nextEye.map((v,i)=>v-anchor.view[i]*d);state.distance=d;state.zoom=distanceToZoom(d)}
  function zoomAt(factor,x,y){const anchor=zoomAnchor(x,y),d=Math.max(500,Math.min(8e9,state.distance*factor));keepAnchorAtScreen(anchor,d);refresh()}
  function panBy(dx,dy){const {right,up}=basis(),kmPerCss=state.distance/(innerHeight/(2*Math.tan(Math.PI/8)));state.target=state.target.map((v,i)=>v-right[i]*dx*kmPerCss+up[i]*dy*kmPerCss);refresh()}
  function selectBody(id){const f=featureById[id];if(!f?.position_km)return false;state.selectedBodyId=id;const badge=document.getElementById('selectionBadge');badge.hidden=false;badge.textContent=`${f.name||id} · selected · pinch to approach`;
    if(focusMotion)focusMotion.cancelled=true;const motion={from:[...state.target],to:[...f.position_km],start:performance.now(),duration:520,cancelled:false};focusMotion=motion;
    function step(now){if(motion.cancelled)return;const u=Math.min(1,(now-motion.start)/motion.duration),s=u*u*(3-2*u);state.target=motion.from.map((v,i)=>v+(motion.to[i]-v)*s);refresh();if(u<1)requestAnimationFrame(step);else focusMotion=null;}
    draw();requestAnimationFrame(step);return true;
  }
  function selectAt(x,y){const r=window.__solarBasemapScene;if(!r)return false;const labels=[...document.querySelectorAll('.body-label')];for(const label of labels){const box=label.getBoundingClientRect();if(x>=box.left-5&&x<=box.right+5&&y>=box.top-5&&y<=box.bottom+5)return selectBody(label.dataset.bodyId);}
    let best=null;for(const f of r.features){if(!f.visible||!f.clip)continue;const px=(f.clip[0]+1)*innerWidth/2,py=(1-f.clip[1])*innerHeight/2,d=Math.hypot(px-x,py-y),hit=Math.max(18,(f.symbol_size_css_px||4)/2+13),score=d+(f.symbol_kind==='minor'?15:f.symbol_kind==='planet'?2:0);if(d<=hit&&(!best||score<best.score))best={id:f.body_id,score};}return best?selectBody(best.id):false;
  }
  function markerTexture(kind){const surface=document.createElement('canvas');surface.width=surface.height=64;const ctx=surface.getContext('2d');if(kind==='minor'){ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(32,4);ctx.lineTo(60,32);ctx.lineTo(32,60);ctx.lineTo(4,32);ctx.closePath();ctx.fill();}
    else if(kind==='glow'){const gradient=ctx.createRadialGradient(32,32,4,32,32,32);gradient.addColorStop(0,'#fff');gradient.addColorStop(.25,'#ffffffb0');gradient.addColorStop(1,'#ffffff00');ctx.fillStyle=gradient;ctx.fillRect(0,0,64,64);}
    else{ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(32,32,29,0,Math.PI*2);ctx.fill();}
    const texture=new THREE.CanvasTexture(surface);texture.needsUpdate=true;return texture;
  }
  function scaleLabel(km){if(km>=AU*.1)return `${(km/AU).toPrecision(3)} AU`;return `${Math.round(km).toLocaleString('en-US')} km`}
  function updateScaleAndLabels(){
    const pxPerKm=innerHeight/(2*Math.tan(Math.PI/8)*state.distance),rawKm=88/pxPerKm,power=10**Math.floor(Math.log10(rawKm)),scaled=rawKm/power,unit=(scaled>=5?5:scaled>=2?2:1)*power,bar=document.getElementById('scaleBar');
    const selected=featureById[state.selectedBodyId],offset=selected?.position_km?Math.hypot(...selected.position_km.map((v,i)=>v-state.target[i])):null;document.getElementById('sceneContext').textContent=selected?`SUN-CENTERED · ${selected.name||selected.body_id} Δ ${scaleLabel(offset)}`:'SUN-CENTERED · TRUE SCALE';
    document.getElementById('scaleText').textContent=`1 px ≈ ${scaleLabel(1/pxPerKm)} @ center`;
    bar.style.width=`${Math.max(24,unit*pxPerKm)}px`;bar.dataset.distanceKm=String(unit);bar.dataset.label=scaleLabel(unit);bar.setAttribute('aria-label',`${scaleLabel(unit)} at scene center`);bar.textContent='';
    const layer=document.getElementById('labels'),ring=document.getElementById('selectionRing'),sun=featureById.SUN?.position_km||[0,0,0],sunDiameter=1392700*pxPerKm,rendered=window.__solarBasemapScene?.features||[];
    const regions=[...document.querySelectorAll('.pilot-chrome,.hud,#scale,#selectionBadge:not([hidden])')].map(el=>{const r=el.getBoundingClientRect();return {x:r.left-4,y:r.top-4,w:r.width+8,h:r.height+8}}),occupied=[...regions],wanted=new Set();
    const candidates=rendered.filter(x=>x.visible&&x.clip).map(x=>{const f=featureById[x.body_id];if(!f)return null;const kind=x.symbol_kind,selected=x.body_id===state.selectedBodyId,px=(x.clip[0]+1)*innerWidth/2,py=(1-x.clip[1])*innerHeight/2;let show=selected;
      if(kind==='sun')show||=sunDiameter>=SUN_LABEL_MIN_DIAMETER_CSS_PX;
      else if(kind==='planet')show||=Math.hypot(...f.position_km.map((v,i)=>(v-sun[i])*pxPerKm))>=PLANET_LABEL_MIN_SEPARATION_CSS_PX;
      else{const node=handle.root.nodes.find(n=>n.node_id===f.node_id&&n.node_id!=='solar');const parent=featureById[node?.anchor_id]?.position_km||sun;show||=!!node&&Math.hypot(...f.position_km.map((v,i)=>(v-parent[i])*pxPerKm))>=MINOR_LABEL_MIN_SEPARATION_CSS_PX;}
      return show?{f,kind,selected,px,py,priority:selected?1000:kind==='sun'?900:kind==='planet'?500:100}:null}).filter(Boolean).sort((a,b)=>b.priority-a.priority||a.f.body_id.localeCompare(b.f.body_id));
    for(const item of candidates){const {f,kind,selected,px,py}=item,name=f.name||f.body_id,w=Math.max(28,name.length*6.2),h=16,gap=(kind==='sun'?16:11),placements=[[px+gap,py-h/2],[px-gap-w,py-h/2],[px-w/2,py-gap-h],[px-w/2,py+gap]];let box=null;
      for(const [x,y] of placements){const proposed={x,y,w,h};if(x<4||y<35||x+w>innerWidth-4||y+h>innerHeight-4)continue;if(occupied.some(r=>x<r.x+r.w&&x+w>r.x&&y<r.y+r.h&&y+h>r.y))continue;box=proposed;break;}
      if(!box)continue;occupied.push(box);wanted.add(f.body_id);let el=document.getElementById(`body-label-${f.body_id}`);if(!el){el=document.createElement('span');el.id=`body-label-${f.body_id}`;el.textContent=name;el.dataset.bodyId=f.body_id;layer.appendChild(el)}el.className=`body-label ${kind}${selected?' selected':''}`;el.style.left=`${box.x}px`;el.style.top=`${box.y}px`;el.dataset.kind=kind;
    }for(const el of [...layer.children])if(!wanted.has(el.dataset.bodyId))el.remove();
    const marker=rendered.find(x=>x.body_id===state.selectedBodyId&&x.visible);ring.hidden=!marker;if(marker){ring.style.left=`${(marker.clip[0]+1)*innerWidth/2}px`;ring.style.top=`${(1-marker.clip[1])*innerHeight/2}px`;ring.setAttribute('aria-label',`${featureById[state.selectedBodyId]?.name||state.selectedBodyId} selected`);}
  }
  function init(){
    if(!window.THREE)throw Error('Three.js r149 unavailable');
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,logarithmicDepthBuffer:true,preserveDrawingBuffer:true});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight,false);renderer.setClearColor(0x05070b,1);
    scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.001,1e7);camera.position.set(0,0,0);geometryGroup=new THREE.Group();scene.add(geometryGroup);symbolTextures={sun:markerTexture('sun'),planet:markerTexture('planet'),minor:markerTexture('minor'),glow:markerTexture('glow')};
    addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();draw();});
    canvas.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(Math.max(-180,Math.min(180,e.deltaY))*.0008),e.clientX,e.clientY)},{passive:false});
    const pointers=new Map();let gesture=null,tapCandidate=null,singleBlocked=false,suppressClick=null;canvas.addEventListener('contextmenu',e=>e.preventDefault());
    document.addEventListener('click',e=>{if(suppressClick&&performance.now()<suppressClick.until&&Math.hypot(e.clientX-suppressClick.x,e.clientY-suppressClick.y)<24){e.preventDefault();e.stopImmediatePropagation();suppressClick=null;}},true);
    function twoPoints(){const [a,b]=[...pointers.values()];return {center:{x:(a.x+b.x)/2,y:(a.y+b.y)/2},span:Math.hypot(a.x-b.x,a.y-b.y),angle:Math.atan2(b.y-a.y,b.x-a.x)}}
    function startGesture(){if(pointers.size!==2)return;const p=twoPoints();gesture={...p,rotation:[...state.rotation],distance:state.distance,anchor:zoomAnchor(p.center.x,p.center.y),mode:null,movedIds:new Set(),started:performance.now(),decisionTimer:null};tapCandidate=null;singleBlocked=true;}
    function angleDifference(a,b){let d=a-b;while(d>Math.PI)d-=2*Math.PI;while(d< -Math.PI)d+=2*Math.PI;return d;}
    function updateGesture(pointerId){if(!gesture||pointers.size!==2)return;if(pointerId!==null)gesture.movedIds.add(pointerId);if(!gesture.mode&&gesture.movedIds.size<2&&performance.now()-gesture.started<80){if(!gesture.decisionTimer){const pending=gesture;pending.decisionTimer=setTimeout(()=>{if(gesture===pending)updateGesture(null)},80);}return;}
      const p=twoPoints(),centerTravel=Math.hypot(p.center.x-gesture.center.x,p.center.y-gesture.center.y),spanTravel=Math.abs(p.span-gesture.span),turn=angleDifference(p.angle,gesture.angle);
      if(!gesture.mode){if(spanTravel>PINCH_DEADBAND_CSS_PX&&spanTravel>centerTravel*.8)gesture.mode='zoom';else if(centerTravel>9||Math.abs(turn)>.12)gesture.mode='orient';else return;}
      if(gesture.mode==='zoom'){const noise=Math.log(1+PINCH_DEADBAND_CSS_PX/gesture.span),ratio=Math.log(Math.max(1,p.span)/gesture.span),filtered=Math.sign(ratio)*Math.max(0,Math.abs(ratio)-noise),relative=Math.max(1/PINCH_MAX_RATIO,Math.min(PINCH_MAX_RATIO,Math.exp(-PINCH_LOG_GAIN*filtered))),distance=Math.max(500,Math.min(8e9,gesture.distance*relative));keepAnchorAtScreen(gesture.anchor,distance);refresh();}
      else{state.rotation[0]=gesture.rotation[0]-(p.center.x-gesture.center.x)*.005-turn*.75;state.rotation[1]=Math.max(-1.42,Math.min(1.42,gesture.rotation[1]+(p.center.y-gesture.center.y)*.005));refresh();}
    }
    canvas.addEventListener('pointerdown',e=>{if(focusMotion)focusMotion.cancelled=true;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,button:e.button,shift:e.shiftKey});canvas.setPointerCapture(e.pointerId);if(pointers.size===1&&!singleBlocked)tapCandidate={id:e.pointerId,x:e.clientX,y:e.clientY,time:performance.now()};if(pointers.size===2)startGesture();});
    function finishPointer(e,cancelled){if(!cancelled&&tapCandidate?.id===e.pointerId&&pointers.size===1&&Math.hypot(e.clientX-tapCandidate.x,e.clientY-tapCandidate.y)<8&&performance.now()-tapCandidate.time<450&&selectAt(e.clientX,e.clientY))suppressClick={x:e.clientX,y:e.clientY,until:performance.now()+500};pointers.delete(e.pointerId);tapCandidate=null;if(pointers.size<2)gesture=null;if(pointers.size===0)singleBlocked=false;}
    canvas.addEventListener('pointerup',e=>finishPointer(e,false));canvas.addEventListener('pointercancel',e=>finishPointer(e,true));
    canvas.addEventListener('pointermove',e=>{const previous=pointers.get(e.pointerId);if(!previous)return;pointers.set(e.pointerId,{...previous,x:e.clientX,y:e.clientY});if(pointers.size>=2){updateGesture(e.pointerId);return;}if(singleBlocked)return;const dx=e.clientX-previous.x,dy=e.clientY-previous.y;if(tapCandidate&&Math.hypot(e.clientX-tapCandidate.x,e.clientY-tapCandidate.y)>=8)tapCandidate=null;if(!dx&&!dy)return;
      if(e.buttons===2||e.shiftKey||previous.button===2||previous.shift){state.rotation[0]-=dx*.005;state.rotation[1]=Math.max(-1.42,Math.min(1.42,state.rotation[1]-dy*.005));refresh();}else panBy(dx,dy);
    });
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
      let loadedCurveScale=0;if(near&&n.node_id!=='solar')for(const d of handle.drawList())if(d.node_id===n.node_id){const curveAnchor=featureById[d.curve.anchor_id]?.position_km;if(!curveAnchor)continue;for(const point of d.segment.points){const world=point.slice(1).map((v,i)=>curveAnchor[i]+v),pointRel=world.map((v,i)=>v-eye[i]),pointDepth=-pointRel.reduce((s,v,i)=>s+v*dir[i],0);if(pointDepth<=0)continue;const pointRadial=Math.sqrt(Math.max(0,pointRel.reduce((s,v)=>s+v*v,0)-pointDepth*pointDepth));loadedCurveScale=Math.max(loadedCurveScale,scale/pointDepth*Math.sqrt(1+Math.pow(pointRadial/pointDepth,2)));}}
      const K=near?(n.node_id==='solar'?Infinity:loadedCurveScale||scale/state.distance):scale/zmin*Math.sqrt(1+Math.pow((radial+radius)/zmin,2));const diameter=2*radius*K;
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
  function localContextForCurve(curve){if(curve.semantic!=='HELIOCENTRIC_REFERENCE_ORBIT')return null;const node=handle.root.nodes.find(n=>n.node_id!=='solar'&&n.anchor_id===curve.feature_id),position=featureById[node?.anchor_id]?.position_km;if(!node||!position)return null;
    const radius=Math.max(LOCAL_CONTEXT_MIN_RADIUS_KM,(node.content_bound?.radius_km||0)*LOCAL_CONTEXT_BOUND_MULTIPLIER);return Math.hypot(...state.target.map((v,i)=>v-position[i]))<=radius&&state.distance<=radius?{node,position,radius}:null;
  }
  function clear(){while(geometryGroup.children.length){const x=geometryGroup.children[geometryGroup.children.length-1];geometryGroup.remove(x);x.geometry?.dispose();x.material?.dispose();}}
  function draw(){
    if(!renderer||!handle)return;const t=performance.now();if(state.lastTime)state.raf.push(t-state.lastTime);state.lastTime=t;state.frameCount++;
    clear();const eye=eyePosition();const targetRel=state.target.map((x,i)=>(x-eye[i])/state.distance);camera.position.set(0,0,0);camera.lookAt(...targetRel);camera.updateMatrixWorld();
    const unit=state.distance/100,focal=innerHeight/(2*Math.tan(Math.PI/8));const lines=[];const featureStates=[];let markers=0,markerGpuErrorKm=0,markerGpuErrorCssPx=0;
    for(const f of handle.catalog()){
      if(!f.position_km){featureStates.push({body_id:f.body_id,resolution:f.resolution,renderer_status:'AUTHORITY_UNRESOLVED',reason:f.reason,submitted:false,visible:false});continue;}
      const localNode=handle.root.nodes.find(n=>n.node_id===f.node_id&&n.node_id!=='solar'),parent=featureById[localNode?.anchor_id||f.parent_body_id];
      // Barycenters and catalog satellites without a governed local node remain
      // inspectable in the catalog; they do not masquerade as local map detail.
      let separationPx=null,presentationReason=null,markerAdmitted=true;if(f.body_class==='BARYCENTER'){markerAdmitted=false;presentationReason='BARYCENTER_SYMBOL_SUPPRESSED';}else if(f.body_class==='NATURAL_SATELLITE'&&!localNode){markerAdmitted=false;presentationReason=f.geometry_status==='NOT_REQUESTED'?'LOCAL_GEOMETRY_NOT_REQUESTED':'LOCAL_NODE_UNAVAILABLE';}
      if(parent?.position_km&&f.body_id!==parent.body_id){const sep=Math.hypot(...f.position_km.map((x,i)=>x-parent.position_km[i]));separationPx=sep*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);if(markerAdmitted&&separationPx<8){markerAdmitted=false;presentationReason='PARENT_SEPARATION_LOD';}}
      const p=f.position_km.map((x,i)=>(x-eye[i])/unit);
      const clip=new THREE.Vector3(...p).project(camera),inFrustum=Math.abs(clip.x)<=1&&Math.abs(clip.y)<=1&&clip.z>=-1&&clip.z<=1;
      if(markerAdmitted&&inFrustum){const cam=new THREE.Vector3(...p).applyMatrix4(camera.matrixWorldInverse),depth=-cam.z,K=depth>0?focal/(depth*unit)*Math.sqrt(1+Math.pow(Math.hypot(cam.x,cam.y)/depth,2)):Infinity;for(const x of p){const error=Math.abs(Math.fround(x)-x)*unit;markerGpuErrorKm=Math.max(markerGpuErrorKm,error);markerGpuErrorCssPx=Math.max(markerGpuErrorCssPx,error*K);}}
      const symbolKind=f.body_id==='SUN'?'sun':f.body_class==='PLANET'?'planet':'minor',symbolSizeCssPx=symbolKind==='sun'?17:symbolKind==='planet'?10:4,symbolColor=symbolKind==='sun'?tokenColor('--loom-brand-color-accent-amber','#FF8703'):symbolKind==='planet'?tokenColor('--loom-domain-nav-node-color','#C7D3DF'):tokenColor('--loom-brand-color-secondary-steel','#8A97A6');
      featureStates.push({body_id:f.body_id,resolution:f.resolution,renderer_status:!markerAdmitted?'LOD_SUPPRESSED':inFrustum?'SUBMITTED_VISIBLE':'FRUSTUM_CLIPPED',presentation_reason:presentationReason,separation_css_px:separationPx,clip:[clip.x,clip.y,clip.z],submitted:markerAdmitted,visible:markerAdmitted&&inFrustum,symbol_kind:symbolKind,symbol_size_css_px:symbolSizeCssPx,symbol_color:symbolColor});
      if(!markerAdmitted||state.isolatedFeature&&state.isolatedFeature!==f.body_id)continue;
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));if(symbolKind==='sun'){const glow=new THREE.PointsMaterial({color:symbolColor,map:symbolTextures.glow,size:40,sizeAttenuation:false,transparent:true,opacity:.55,depthWrite:false});geometryGroup.add(new THREE.Points(g.clone(),glow));}
      const m=new THREE.PointsMaterial({color:symbolColor,map:symbolTextures[symbolKind],size:symbolSizeCssPx,sizeAttenuation:false,transparent:true,opacity:symbolKind==='minor'?.62:1,alphaTest:.2,depthWrite:false});geometryGroup.add(new THREE.Points(g,m));markers++;
    }
    for(const d of state.draws){if(state.isolatedFeature&&state.isolatedFeature!==d.curve.feature_id)continue;let opacity=d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'?.24:.56;
      const localContext=localContextForCurve(d.curve);
      if(d.curve.semantic==='HELIOCENTRIC_REFERENCE_ORBIT'){const dia=2*curveExtentKm(d.curve)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);const diagonal=Math.hypot(innerWidth,innerHeight);if(!localContext&&dia>=16*diagonal)continue;if(!localContext&&dia>8*diagonal)opacity*=1-(dia-8*diagonal)/(8*diagonal);if(localContext)opacity=.09;}
      else if(d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'){const node=handle.root.nodes.find(n=>n.anchor_id===d.curve.anchor_id&&n.node_id!=='solar');const dia=2*(node?.content_bound?.radius_km||0)*innerHeight/(2*Math.tan(Math.PI/8)*state.distance);if(dia<16)continue;const fade=Math.min(1,(dia-16)/8);opacity*=Math.max(.5,fade);}
      const anchor=featureById[d.curve.anchor_id]?.position_km||[0,0,0];let sourcePoints=d.segment.points;if(localContext){let nearest={distance:Infinity,index:0};for(let i=0;i<sourcePoints.length;i++){const w=sourcePoints[i].slice(1).map((v,k)=>anchor[k]+v),distance=Math.hypot(...w.map((v,k)=>v-localContext.position[k]));if(distance<nearest.distance)nearest={distance,index:i};}let lo=nearest.index,hi=nearest.index;while(lo>0&&Math.hypot(...sourcePoints[lo-1].slice(1).map((v,k)=>anchor[k]+v-localContext.position[k]))<=localContext.radius)lo--;while(hi+1<sourcePoints.length&&Math.hypot(...sourcePoints[hi+1].slice(1).map((v,k)=>anchor[k]+v-localContext.position[k]))<=localContext.radius)hi++;sourcePoints=sourcePoints.slice(lo,hi+1);}
      const pts=sourcePoints.map(p=>p.slice(1).map((v,i)=>(anchor[i]+v-eye[i])/unit));if(pts.length<2){lines.push({feature_id:d.curve.feature_id,semantic:d.curve.semantic,status:'SINGLE_POINT_NOT_DRAWN',vertices:pts.length});continue;}
      const clipPts=pts.map(p=>new THREE.Vector3(...p).project(camera));const inClip=clipPts.filter(p=>Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&p.z>=-1&&p.z<=1).length;
      const arr=new Float32Array(pts.flat());const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(arr,3));const color=d.curve.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'?tokenColor('--loom-brand-color-secondary-ice','#C7D3DF'):tokenColor('--loom-domain-nav-orbit-color','#8A97A6'),m=new THREE.LineBasicMaterial({color,transparent:true,opacity});geometryGroup.add(new THREE.Line(g,m));const visibleIndices=clipPts.map((p,i)=>({p,i})).filter(x=>Math.abs(x.p.x)<=1&&Math.abs(x.p.y)<=1&&x.p.z>=-1&&x.p.z<=1).map(x=>x.i);let gpuError=0,gpuErrorCss=0;for(const i of visibleIndices){const cam=new THREE.Vector3(...pts[i]).applyMatrix4(camera.matrixWorldInverse),depth=-cam.z,K=depth>0?focal/(depth*unit)*Math.sqrt(1+Math.pow(Math.hypot(cam.x,cam.y)/depth,2)):Infinity;for(const v of pts[i]){const error=Math.abs(Math.fround(v)-v)*unit;gpuError=Math.max(gpuError,error);gpuErrorCss=Math.max(gpuErrorCss,error*K);}}lines.push({feature_id:d.curve.feature_id,node_id:d.node_id,level:d.level,semantic:d.curve.semantic,anchor_id:d.curve.anchor_id,presentation_context:localContext?'LOCAL_PARENT_ARC':null,context_radius_km:localContext?.radius??null,opacity,color,status:inClip?'SUBMITTED_WITH_PROJECTED_VERTICES':'SUBMITTED_TO_GPU_CLIPPING',vertices:pts.length,clip_vertices:inClip,segment_id:d.segment.body_source_ref+'|'+d.segment.anchor_source_ref,float32Input:Array.from(arr),cameraRelativeKm:pts.map(p=>p.map(x=>Math.fround(x)*unit)),gpuConversionMaxKm:gpuError,gpuConversionMaxCssPx:gpuErrorCss});}
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
  function fit(){if(focusMotion)focusMotion.cancelled=true;state.selectedBodyId=null;document.getElementById('selectionBadge').hidden=true;state.target=[0,0,0];state.distance=50*AU;state.rotation=[0,0];refresh()}
  window.__solarBasemapReadPixels=()=>{const gl=renderer.getContext(),w=renderer.domElement.width,h=renderer.domElement.height,ratio=renderer.getPixelRatio(),p=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,p);const rects=[...document.querySelectorAll('header,.hud,.catalog.open,.report.open')].map(x=>x.getBoundingClientRect());let mint=0,amber=0,steel=0,lit=0,excluded=0;for(let y=0;y<h;y++)for(let x=0;x<w;x++){const top=(h-1-y)/ratio,left=x/ratio;if(rects.some(r=>left>=r.left&&left<r.right&&top>=r.top&&top<r.bottom)){excluded++;continue;}const i=(y*w+x)*4,r=p[i],g=p[i+1],b=p[i+2];if(r>20||g>20||b>20)lit++;if(r>35&&g>r*1.2&&b>r*1.1)mint++;if(r>g*1.3&&g>b*1.05)amber++;if(r>20&&r<80&&g>=r*1.05&&b>=g*1.03&&b<100)steel++;}return {width:w,height:h,render_dpr:ratio,mint_line_pixels:mint,amber_line_pixels:amber,steel_line_pixels:steel,lit_pixels:lit,excluded_overlay_pixels:excluded};};
  window.LoomRenderer={init,configure,moveToward,setZoom,fit,draw,refresh,replayApproach,isolate,state};
})();
