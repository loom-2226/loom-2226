from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any, Dict, Tuple

VIEWER_VERSION = "LOOM_SHIPYARD_GLB_VIEWER_v0.1"
VIEWER_AUTHORITY = "DERIVED_VISUAL_INSPECTION_ONLY"


class GLBViewerError(ValueError):
    pass


def parse_glb(glb: bytes) -> Tuple[dict, bytes]:
    if len(glb) < 20:
        raise GLBViewerError("GLB too short")
    magic, version, total = struct.unpack_from("<4sII", glb, 0)
    if magic != b"glTF" or version != 2 or total != len(glb):
        raise GLBViewerError("invalid glTF 2.0 binary header")
    off = 12
    doc = None
    binary = b""
    while off < len(glb):
        if off + 8 > len(glb):
            raise GLBViewerError("truncated GLB chunk header")
        length, ctype = struct.unpack_from("<II", glb, off)
        off += 8
        if off + length > len(glb):
            raise GLBViewerError("truncated GLB chunk")
        payload = glb[off:off + length]
        off += length
        if ctype == 0x4E4F534A:
            if doc is not None:
                raise GLBViewerError("multiple JSON chunks")
            doc = json.loads(payload.decode("utf-8").rstrip(" \x00"))
        elif ctype == 0x004E4942:
            binary += payload
    if doc is None:
        raise GLBViewerError("missing JSON chunk")
    if doc.get("asset", {}).get("version") != "2.0":
        raise GLBViewerError("unsupported glTF asset version")
    if not isinstance(doc.get("meshes", []), list) or not isinstance(doc.get("nodes", []), list):
        raise GLBViewerError("invalid glTF mesh/node tables")
    return doc, binary


def inspect_glb(glb: bytes) -> Dict[str, Any]:
    doc, binary = parse_glb(glb)
    asset = doc.get("asset", {})
    nodes = doc.get("nodes", [])
    meshes = doc.get("meshes", [])
    semantic_nodes = sum(1 for n in nodes if isinstance(n.get("extras"), dict) and n["extras"].get("semantic_object_id"))
    return {
        "viewer_version": VIEWER_VERSION,
        "viewer_authority": VIEWER_AUTHORITY,
        "generator": asset.get("generator", "UNKNOWN"),
        "mesh_count": len(meshes),
        "node_count": len(nodes),
        "semantic_node_count": semantic_nodes,
        "binary_byte_length": len(binary),
        "asset_extras": asset.get("extras", {}),
    }


def inspect_glb_file(path: Path) -> Dict[str, Any]:
    return inspect_glb(path.read_bytes())


def viewer_html() -> str:
    # No third-party JavaScript or network dependency. This intentionally implements
    # only the glTF subset needed by LOOM semantic GLBs and the legacy Wayfarer
    # visualization fixture: binary GLB, triangle primitives, POSITION, optional
    # node TRS/matrix, scalar indices, and simple material base colors.
    return r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover"><title>LOOM Shipyard GLB Viewer</title><style>
html,body{margin:0;height:100%;background:#090b0e;color:#e7edf5;font-family:system-ui,sans-serif;overflow:hidden}#app{height:100%;display:grid;grid-template-rows:auto 1fr}header{display:flex;gap:.35rem;align-items:center;flex-wrap:wrap;padding:.45rem;background:#12161c;border-bottom:1px solid #2a313c}button{background:#1c232d;color:#e8edf3;border:1px solid #465265;border-radius:.35rem;padding:.38rem .52rem}#stage{position:relative;min-height:0}canvas{width:100%;height:100%;display:block;touch-action:none}#hud,#pick{position:absolute;bottom:.5rem;background:#0b0f15dd;border:1px solid #384353;border-radius:.4rem;padding:.45rem;font:10px ui-monospace,monospace;white-space:pre-wrap}#hud{left:.5rem;max-width:58vw}#pick{right:.5rem;max-width:36vw}</style></head><body><div id="app"><header><strong>LOOM GLB INSPECTOR</strong><button data-view="iso">3/4</button><button data-view="side">SIDE</button><button data-view="top">TOP</button><button id="all">ALL</button><button id="semantic">SEMANTIC</button></header><div id="stage"><canvas id="gl"></canvas><div id="hud">LOADING /model.glb</div><div id="pick">Tap/click to inspect a visible node.</div></div></div><script>
(()=>{'use strict';const hud=document.getElementById('hud'),pick=document.getElementById('pick'),c=document.getElementById('gl');let rows=[],meta={},showSemanticOnly=false;
function mm(a,b){let o=new Float32Array(16);for(let col=0;col<4;col++)for(let row=0;row<4;row++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+row]*b[col*4+k];o[col*4+row]=s}return o}function ident(){let r=new Float32Array(16);r[0]=r[5]=r[10]=r[15]=1;return r}function trs(n){if(n.matrix)return new Float32Array(n.matrix);let t=n.translation||[0,0,0],s=n.scale||[1,1,1],q=n.rotation||[0,0,0,1],x=q[0],y=q[1],z=q[2],w=q[3],r=ident();r[0]=(1-2*y*y-2*z*z)*s[0];r[1]=(2*x*y+2*w*z)*s[0];r[2]=(2*x*z-2*w*y)*s[0];r[4]=(2*x*y-2*w*z)*s[1];r[5]=(1-2*x*x-2*z*z)*s[1];r[6]=(2*y*z+2*w*x)*s[1];r[8]=(2*x*z+2*w*y)*s[2];r[9]=(2*y*z-2*w*x)*s[2];r[10]=(1-2*x*x-2*y*y)*s[2];r[12]=t[0];r[13]=t[1];r[14]=t[2];return r}function norm(v){let n=Math.hypot(...v)||1;return v.map(x=>x/n)}function cross(a,b){return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}function look(e,t,u){let z=norm([e[0]-t[0],e[1]-t[1],e[2]-t[2]]),x=norm(cross(u,z)),y=cross(z,x),r=ident();r[0]=x[0];r[1]=y[0];r[2]=z[0];r[4]=x[1];r[5]=y[1];r[6]=z[1];r[8]=x[2];r[9]=y[2];r[10]=z[2];r[12]=-(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]);r[13]=-(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]);r[14]=-(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]);return r}function persp(f,a,n,fa){let t=1/Math.tan(f/2),r=new Float32Array(16);r[0]=t/a;r[5]=t;r[10]=(fa+n)/(n-fa);r[11]=-1;r[14]=2*fa*n/(n-fa);return r}
function accView(doc,bin,idx){let a=doc.accessors[idx],bv=doc.bufferViews[a.bufferView],comp=a.componentType,count=a.count,typ=a.type,components=typ==='VEC3'?3:1,bytes=comp===5126||comp===5125?4:2,off=(bv.byteOffset||0)+(a.byteOffset||0),len=count*components;let buf=bin.slice(off,off+len*bytes);if(comp===5126)return new Float32Array(buf);if(comp===5125)return new Uint32Array(buf);if(comp===5123)return new Uint16Array(buf);throw Error('unsupported componentType '+comp)}
function parseGLB(ab){let dv=new DataView(ab);if(dv.getUint32(0,true)!==0x46546c67||dv.getUint32(4,true)!==2)throw Error('invalid GLB');let off=12,doc=null,bin=null;while(off<ab.byteLength){let ln=dv.getUint32(off,true),ty=dv.getUint32(off+4,true);off+=8;let ch=ab.slice(off,off+ln);off+=ln;if(ty===0x4E4F534A)doc=JSON.parse(new TextDecoder().decode(ch).replace(/[\u0000 ]+$/,''));else if(ty===0x004E4942)bin=ch}if(!doc||!bin)throw Error('GLB missing JSON or BIN chunk');return[doc,bin]}
const gl=c.getContext('webgl',{antialias:true,alpha:false});if(!gl){hud.textContent='WEBGL UNAVAILABLE';return}const VS='attribute vec3 p;uniform mat4 mvp;uniform vec3 col;varying vec3 vcol;void main(){gl_Position=mvp*vec4(p,1.);vcol=col;}',FS='precision mediump float;varying vec3 vcol;void main(){gl_FragColor=vec4(vcol,1.);}';function sh(t,s){let x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(x));return x}const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FS));gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(pr));gl.useProgram(pr);const ap=gl.getAttribLocation(pr,'p'),um=gl.getUniformLocation(pr,'mvp'),uc=gl.getUniformLocation(pr,'col');gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);
let theta=.62,phi=.48,dist=85,target=[0,0,0],drag=false,lx=0,ly=0,pinch=null;function camera(){let cp=Math.cos(phi),e=[target[0]+dist*cp*Math.cos(theta),target[1]+dist*Math.sin(phi),target[2]+dist*cp*Math.sin(theta)];return mm(persp(.72,c.width/c.height,.1,500),look(e,target,[0,1,0]))}function matColor(doc,mi){let m=(doc.materials||[])[mi],v=m&&m.pbrMetallicRoughness&&m.pbrMetallicRoughness.baseColorFactor;return v?[v[0],v[1],v[2]]:[.72,.76,.82]}
function build(doc,bin){let out=[],mins=[Infinity,Infinity,Infinity],maxs=[-Infinity,-Infinity,-Infinity];(doc.nodes||[]).forEach((n,ni)=>{if(n.mesh===undefined)return;let mesh=doc.meshes[n.mesh],world=trs(n);(mesh.primitives||[]).forEach((p,pi)=>{if(!p.attributes||p.attributes.POSITION===undefined||p.indices===undefined)return;let v=accView(doc,bin,p.attributes.POSITION),i=accView(doc,bin,p.indices);for(let k=0;k<v.length;k+=3){let x=v[k],y=v[k+1],z=v[k+2],tx=world[0]*x+world[4]*y+world[8]*z+world[12],ty=world[1]*x+world[5]*y+world[9]*z+world[13],tz=world[2]*x+world[6]*y+world[10]*z+world[14];mins[0]=Math.min(mins[0],tx);mins[1]=Math.min(mins[1],ty);mins[2]=Math.min(mins[2],tz);maxs[0]=Math.max(maxs[0],tx);maxs[1]=Math.max(maxs[1],ty);maxs[2]=Math.max(maxs[2],tz)}out.push({name:n.name||mesh.name||('node_'+ni),extras:n.extras||{},v:v,i:i,m:world,col:matColor(doc,p.material)})})});if(!out.length)throw Error('no drawable triangle primitives');target=[(mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,(mins[2]+maxs[2])/2];dist=Math.max(12,Math.hypot(maxs[0]-mins[0],maxs[1]-mins[1],maxs[2]-mins[2])*.95);return out}
function resize(){let d=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.floor(c.clientWidth*d)),h=Math.max(1,Math.floor(c.clientHeight*d));if(c.width!==w||c.height!==h){c.width=w;c.height=h}}function draw(r,vp){let vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,r.v,gl.STATIC_DRAW);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(ap);let ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,r.i,gl.STATIC_DRAW);gl.uniformMatrix4fv(um,false,mm(vp,r.m));gl.uniform3fv(uc,r.col);gl.drawElements(gl.TRIANGLES,r.i.length,r.i instanceof Uint32Array?gl.UNSIGNED_INT:gl.UNSIGNED_SHORT,0);gl.deleteBuffer(vb);gl.deleteBuffer(ib)}function render(){resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.035,.045,.06,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);let vp=camera(),vis=rows.filter(r=>!showSemanticOnly||r.extras.semantic_object_id);for(const r of vis)draw(r,vp);hud.textContent=(meta.generator||'UNKNOWN GLB')+'\nmeshes='+rows.length+' semantic='+rows.filter(r=>r.extras.semantic_object_id).length+'\nGLB-native • drag orbit • pinch/wheel zoom';requestAnimationFrame(render)}
fetch('/model.glb',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.arrayBuffer()}).then(ab=>{let [doc,bin]=parseGLB(ab);meta=doc.asset||{};rows=build(doc,bin);render()}).catch(e=>{hud.textContent='GLB VIEWER ERROR\n'+(e&&e.stack?e.stack:String(e));console.error(e)});
document.getElementById('all').onclick=()=>showSemanticOnly=false;document.getElementById('semantic').onclick=()=>showSemanticOnly=true;document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{let v=b.dataset.view;if(v==='side'){theta=0;phi=.02}else if(v==='top'){theta=0;phi=1.45}else{theta=.62;phi=.48}});c.addEventListener('pointerdown',e=>{drag=true;lx=e.clientX;ly=e.clientY;c.setPointerCapture&&c.setPointerCapture(e.pointerId)});c.addEventListener('pointermove',e=>{if(!drag)return;theta-=(e.clientX-lx)*.008;phi=Math.max(-1.45,Math.min(1.45,phi+(e.clientY-ly)*.008));lx=e.clientX;ly=e.clientY});c.addEventListener('pointerup',()=>drag=false);c.addEventListener('wheel',e=>{dist=Math.max(8,Math.min(500,dist+e.deltaY*.05));e.preventDefault()},{passive:false});c.addEventListener('touchmove',e=>{if(e.touches.length===2){let dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY,n=Math.hypot(dx,dy);if(pinch)dist=Math.max(8,Math.min(500,dist+(pinch-n)*.08));pinch=n;e.preventDefault()}},{passive:false});c.addEventListener('touchend',()=>pinch=null);c.addEventListener('click',()=>{let vis=rows.filter(r=>!showSemanticOnly||r.extras.semantic_object_id);if(!vis.length)return;let r=vis[Math.floor(Math.random()*vis.length)];pick.textContent=r.name+'\n'+(r.extras.semantic_class||'LEGACY / NO SEMANTIC CLASS')+'\n'+(r.extras.engineering_status||'VISUAL FIXTURE / UNSPECIFIED')});})();
</script></body></html>'''
