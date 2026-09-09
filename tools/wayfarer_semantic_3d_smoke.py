from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry


def build_html() -> str:
    source = build_wayfarer_governed_synthesis()
    semantic = build_semantic_geometry(source)
    sem_by_primitive = {row.primitive_id: row for row in semantic.objects}
    objects = []
    for primitive in source.geometry.primitives:
        sem = sem_by_primitive[primitive.primitive_id]
        flat_vertices = [coord for vertex in primitive.vertices_m for coord in vertex]
        flat_indices = [idx for tri in primitive.triangles for idx in tri]
        objects.append({
            "primitive_id": primitive.primitive_id,
            "semantic_id": sem.semantic_object_id,
            "semantic_class": sem.semantic_class,
            "engineering_status": sem.engineering_status,
            "vertices": flat_vertices,
            "indices": flat_indices,
        })
    payload = {
        "candidate_id": source.design_state.candidate_id,
        "governed_hash": source.package_hash,
        "semantic_hash": semantic.package_hash,
        "authority": "DERIVED_SEMANTIC_3D_SMOKE_EVIDENCE_ONLY",
        "objects": objects,
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover"><title>LOOM Wayfarer Semantic 3D Smoke Test</title><style>
html,body{{margin:0;height:100%;background:#090b0e;color:#e8edf3;font-family:system-ui,sans-serif;overflow:hidden}}#app{{height:100%;display:grid;grid-template-rows:auto 1fr}}header{{display:flex;gap:.35rem;align-items:center;flex-wrap:wrap;padding:.45rem;background:#12161c;border-bottom:1px solid #2a313c}}button{{background:#1c232d;color:#e8edf3;border:1px solid #465265;border-radius:.35rem;padding:.38rem .52rem}}#stage{{position:relative;min-height:0}}canvas{{width:100%;height:100%;display:block;touch-action:none}}#hud{{position:absolute;left:.5rem;bottom:.5rem;max-width:94vw;background:#0b0f15dd;border:1px solid #384353;border-radius:.4rem;padding:.45rem;font:11px ui-monospace,monospace;white-space:pre-wrap}}#pick{{position:absolute;right:.5rem;bottom:.5rem;max-width:48vw;background:#0b0f15dd;border:1px solid #384353;border-radius:.4rem;padding:.45rem;font:10px ui-monospace,monospace;white-space:pre-wrap}}</style></head><body><div id="app"><header><strong>WAYFARER SEMANTIC 3D SMOKE</strong><button data-view="iso">3/4</button><button data-view="side">SIDE</button><button data-view="top">TOP</button><button id="env">ENVELOPES</button><button id="struct">STRUCTURE</button><button id="nodes">NODES</button></header><div id="stage"><canvas id="gl"></canvas><div id="hud"></div><div id="pick">Tap/click geometry to inspect semantic class.</div></div></div><script id="loom-data" type="application/json">{data}</script><script>
(()=>{{'use strict';const D=JSON.parse(document.getElementById('loom-data').textContent),c=document.getElementById('gl'),gl=c.getContext('webgl',{{antialias:true,alpha:false}});if(!gl){{document.getElementById('hud').textContent='WebGL unavailable';return;}}
const VS='attribute vec3 p;uniform mat4 mvp;uniform vec3 col;varying vec3 vcol;void main(){{gl_Position=mvp*vec4(p,1.);vcol=col;}}',FS='precision mediump float;varying vec3 vcol;void main(){{gl_FragColor=vec4(vcol,1.);}}';function sh(t,s){{let x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(x));return x}}const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FS));gl.linkProgram(pr);gl.useProgram(pr);const ap=gl.getAttribLocation(pr,'p'),um=gl.getUniformLocation(pr,'mvp'),uc=gl.getUniformLocation(pr,'col');gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);
const rows=D.objects.map(o=>({{...o,v:new Float32Array(o.vertices),i:new Uint16Array(o.indices)}}));let show={{ADMITTED_SPATIAL_ENVELOPE:true,STRUCTURAL_HYPOTHESIS:true,SOURCE_NODE_PROXY:true}};
function mm(a,b){{let r=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++)r[i*4+j]+=a[i*4+k]*b[k*4+j];return r}}function persp(f,a,n,fa){{let t=1/Math.tan(f/2),r=new Float32Array(16);r[0]=t/a;r[5]=t;r[10]=(fa+n)/(n-fa);r[11]=-1;r[14]=2*fa*n/(n-fa);return r}}function norm(v){{let n=Math.hypot(...v);return v.map(x=>x/n)}}function cross(a,b){{return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}}function look(e,t,u){{let z=norm([e[0]-t[0],e[1]-t[1],e[2]-t[2]]),x=norm(cross(u,z)),y=cross(z,x),r=new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,0,0,0,1]);r[12]=-(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]);r[13]=-(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]);r[14]=-(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]);return r}}
let theta=.62,phi=.48,dist=76,target=[27,0,0],drag=false,lx=0,ly=0;function camera(){{let cp=Math.cos(phi),e=[target[0]+dist*cp*Math.cos(theta),target[1]+dist*Math.sin(phi),target[2]+dist*cp*Math.sin(theta)];return mm(persp(.72,c.width/c.height,.1,300),look(e,target,[0,1,0]))}}function col(k){{return k==='ADMITTED_SPATIAL_ENVELOPE'?[.45,.7,.9]:k==='STRUCTURAL_HYPOTHESIS'?[.82,.82,.82]:[.95,.62,.28]}}function draw(o){{let b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,o.v,gl.STATIC_DRAW);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(ap);let ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,o.i,gl.STATIC_DRAW);gl.uniform3fv(uc,col(o.semantic_class));gl.drawElements(gl.TRIANGLES,o.i.length,gl.UNSIGNED_SHORT,0);gl.deleteBuffer(b);gl.deleteBuffer(ib)}}function resize(){{let d=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.floor(c.clientWidth*d)),h=Math.max(1,Math.floor(c.clientHeight*d));if(c.width!==w||c.height!==h){{c.width=w;c.height=h}}}}function render(){{resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.035,.045,.06,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(um,false,camera());for(const o of rows)if(show[o.semantic_class])draw(o);document.getElementById('hud').textContent=D.candidate_id+'\n'+D.authority+'\nobjects='+rows.length+' • drag orbit • pinch/wheel zoom\nblue=envelopes gray=structural hypotheses orange=node proxies';requestAnimationFrame(render)}}
[['env','ADMITTED_SPATIAL_ENVELOPE'],['struct','STRUCTURAL_HYPOTHESIS'],['nodes','SOURCE_NODE_PROXY']].forEach(([id,k])=>document.getElementById(id).onclick=()=>{{show[k]=!show[k];document.getElementById(id).style.opacity=show[k]?1:.35}});document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{{let v=b.dataset.view;if(v==='side'){{theta=0;phi=.02;dist=76}}else if(v==='top'){{theta=0;phi=1.45;dist=76}}else{{theta=.62;phi=.48;dist=76}}}});c.addEventListener('pointerdown',e=>{{drag=true;lx=e.clientX;ly=e.clientY;c.setPointerCapture&&c.setPointerCapture(e.pointerId)}});c.addEventListener('pointermove',e=>{{if(!drag)return;theta-=(e.clientX-lx)*.008;phi=Math.max(-1.45,Math.min(1.45,phi+(e.clientY-ly)*.008));lx=e.clientX;ly=e.clientY}});c.addEventListener('pointerup',()=>drag=false);c.addEventListener('wheel',e=>{{dist=Math.max(12,Math.min(180,dist+e.deltaY*.04));e.preventDefault()}},{{passive:false}});let pinch=null;c.addEventListener('touchmove',e=>{{if(e.touches.length===2){{let dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY,n=Math.hypot(dx,dy);if(pinch)dist=Math.max(12,Math.min(180,dist+(pinch-n)*.08));pinch=n;e.preventDefault()}}}},{{passive:false}});c.addEventListener('touchend',()=>pinch=null);c.addEventListener('click',()=>{{const visible=rows.filter(o=>show[o.semantic_class]);const o=visible[Math.floor(Math.random()*visible.length)];if(o)document.getElementById('pick').textContent=o.primitive_id+'\n'+o.semantic_class+'\n'+o.engineering_status}});render();}})();</script></body></html>'''


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "wayfarer_semantic_3d_smoke.html")
    out.write_text(build_html(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
