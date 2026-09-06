(() => {
'use strict';
const canvas = document.getElementById('gl');
const info = document.getElementById('info');
const statusEl = document.getElementById('status');
const epochEl = document.getElementById('epoch');
const frameEl = document.getElementById('frame');
const gl = canvas.getContext('webgl', {antialias:true, alpha:false});
if(!gl){statusEl.textContent='WebGL unavailable';return;}

const vs=`attribute vec3 aPos;attribute vec3 aColor;attribute float aSize;uniform mat4 uMVP;varying vec3 vColor;void main(){gl_Position=uMVP*vec4(aPos,1.0);gl_PointSize=aSize;vColor=aColor;}`;
const fs=`precision mediump float;varying vec3 vColor;void main(){vec2 p=gl_PointCoord*2.0-1.0;if(dot(p,p)>1.0)discard;gl_FragColor=vec4(vColor,1.0);}`;
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const loc={pos:gl.getAttribLocation(program,'aPos'),color:gl.getAttribLocation(program,'aColor'),size:gl.getAttribLocation(program,'aSize'),mvp:gl.getUniformLocation(program,'uMVP')};
const buffers={pos:gl.createBuffer(),color:gl.createBuffer(),size:gl.createBuffer()};

let snapshot=null, states=[], center=[0,0,0], yaw=.55, pitch=.38, zoom=2.7, scale=1, positions=[], colors=[], sizes=[];
const byId=new Map();

function resize(){const d=Math.min(devicePixelRatio||1,2);const w=Math.floor(canvas.clientWidth*d),h=Math.floor(canvas.clientHeight*d);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}}
function mul(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)o[c*4+r]=a[r]*b[c*4]+a[4+r]*b[c*4+1]+a[8+r]*b[c*4+2]+a[12+r]*b[c*4+3];return o;}
function perspective(fovy,aspect,n,f){const t=1/Math.tan(fovy/2),nf=1/(n-f);return new Float32Array([t/aspect,0,0,0,0,t,0,0,0,0,(f+n)*nf,-1,0,0,2*f*n*nf,0]);}
function translate(z){return new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,z,1]);}
function rotX(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1]);}
function rotY(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]);}
function currentMVP(){const aspect=canvas.width/canvas.height;return mul(perspective(Math.PI/3,aspect,.05,100),mul(translate(-zoom),mul(rotX(pitch),rotY(yaw))));}
function project(p,m){const x=p[0],y=p[1],z=p[2];const cx=m[0]*x+m[4]*y+m[8]*z+m[12],cy=m[1]*x+m[5]*y+m[9]*z+m[13],cw=m[3]*x+m[7]*y+m[11]*z+m[15];if(cw<=0)return null;return [(cx/cw*.5+.5)*canvas.clientWidth,(1-(cy/cw*.5+.5))*canvas.clientHeight];}
function rebuild(){if(!states.length)return;const rel=states.map(s=>[s.position_km[0]-center[0],s.position_km[1]-center[1],s.position_km[2]-center[2]]);let max=1;for(const p of rel)max=Math.max(max,Math.hypot(...p));scale=1/max;positions=[];colors=[];sizes=[];for(let i=0;i<states.length;i++){const s=states[i],p=rel[i];positions.push(p[0]*scale,p[1]*scale,p[2]*scale);const infra=s.payload?.state_class==='INFRASTRUCTURE';if(s.navigation_grade){colors.push(.70,.86,.77);}else if(infra){colors.push(.62,.72,.88);}else{colors.push(.85,.74,.45);}sizes.push(infra?5:9);}
 bind(buffers.pos,loc.pos,3,new Float32Array(positions));bind(buffers.color,loc.color,3,new Float32Array(colors));bind(buffers.size,loc.size,1,new Float32Array(sizes));statusEl.textContent=`${states.length} states · ${snapshot.counts.navigation_grade} nav-grade\nscale ${max.toExponential(2)} km → 1 unit`;}
function bind(buf,attr,n,data){gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,n,gl.FLOAT,false,0,0);}
function draw(){resize();gl.clearColor(.02,.03,.05,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.useProgram(program);gl.uniformMatrix4fv(loc.mvp,false,currentMVP());gl.drawArrays(gl.POINTS,0,states.length);requestAnimationFrame(draw);}
function setCenter(id){const s=byId.get(id);center=s?s.position_km.slice():[0,0,0];zoom=2.7;rebuild();}
function inspect(index){const s=states[index];if(!s)return;const p=s.position_km,v=s.velocity_km_s,infra=s.payload?.state_class==='INFRASTRUCTURE';info.innerHTML=`<h2>${esc(s.payload?.name||s.entity_id)}</h2><div class="grid"><b>ID</b><span>${esc(s.entity_id)}</span><b>CLASS</b><span>${esc(s.payload?.state_class||'—')}</span><b>NAV</b><span class="${s.navigation_grade?'navgood':'navbad'}">${s.navigation_grade?'NAVIGATION GRADE':'PROVISIONAL / FALLBACK'}</span><b>POSITION km</b><span>${p.map(x=>x.toFixed(1)).join(', ')}</span><b>VELOCITY km/s</b><span>${v.map(x=>x.toFixed(4)).join(', ')}</span><b>SOURCE</b><span>${esc(s.provenance?.state_source||'—')}</span>${infra?`<b>CENTER</b><span>${esc(s.payload?.center_entity_id||'—')}</span><b>VALIDITY</b><span>${esc(s.payload?.validity_status||'—')}</span>`:''}</div>`;}
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

let drag=null,pinch=null;
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);drag={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};});
canvas.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>3)drag.moved=true;yaw+=dx*.008;pitch=Math.max(-1.45,Math.min(1.45,pitch+dy*.008));drag.x=e.clientX;drag.y=e.clientY;});
canvas.addEventListener('pointerup',e=>{if(drag&&drag.id===e.pointerId&&!drag.moved)pick(e.clientX,e.clientY);drag=null;});
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(1.25,Math.min(8,zoom*Math.exp(e.deltaY*.001)));},{passive:false});
canvas.addEventListener('touchstart',e=>{if(e.touches.length===2)pinch=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);},{passive:true});
canvas.addEventListener('touchmove',e=>{if(e.touches.length===2&&pinch){const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);zoom=Math.max(1.25,Math.min(8,zoom*(pinch/d)));pinch=d;}},{passive:true});
function pick(x,y){const m=currentMVP();let best=-1,bd=26;for(let i=0;i<states.length;i++){const p=project([positions[i*3],positions[i*3+1],positions[i*3+2]],m);if(!p)continue;const d=Math.hypot(p[0]-x,p[1]-y);if(d<bd){bd=d;best=i;}}if(best>=0)inspect(best);}

document.getElementById('system').onclick=()=>setCenter('SOL');
document.getElementById('ceres').onclick=()=>setCenter('CER');
document.getElementById('reset').onclick=()=>{yaw=.55;pitch=.38;zoom=2.7;};

fetch('/spatial-state.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();}).then(data=>{snapshot=data;states=data.states||[];for(const s of states)byId.set(s.entity_id,s);epochEl.textContent=data.epoch_utc;frameEl.textContent=data.reference_frame;rebuild();}).catch(err=>{statusEl.textContent='SPATIAL LOAD FAILED\n'+err;});
requestAnimationFrame(draw);
})();
