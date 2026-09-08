from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from governed_ship_synthesis import (
    GEOMETRY_AUTHORITY,
    GovernedSynthesisPackage,
    build_wayfarer_governed_synthesis,
    validate_package,
)

VIEWER_VERSION = "LOOM_GOVERNED_SHIP_SYNTHESIS_VIEWER_v0.1"
VIEWER_AUTHORITY = "REVIEW_EVIDENCE_ONLY"


@dataclass(frozen=True)
class SynthesisViewerPackage:
    version: str
    synthesis_package_hash: str
    html_sha256: str
    html: str
    authority_status: str = VIEWER_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _viewer_payload(package: GovernedSynthesisPackage) -> dict:
    validate_package(package)
    meshes = []
    for primitive in package.geometry.primitives:
        meshes.append(
            {
                "id": primitive.primitive_id,
                "kind": primitive.primitive_kind,
                "vertices": [list(v) for v in primitive.vertices_m],
                "triangles": [list(t) for t in primitive.triangles],
                "authority_status": primitive.authority_status,
            }
        )
    return {
        "viewer_version": VIEWER_VERSION,
        "authority_status": VIEWER_AUTHORITY,
        "synthesis_package_hash": package.package_hash,
        "candidate_id": package.design_state.candidate_id,
        "dependency_graph_status": package.design_state.dependency_graph_status,
        "structural_qualification": package.structure.qualification_status,
        "open_packaging_items": list(package.packaging.open_items),
        "meshes": meshes,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }


def build_html(package: GovernedSynthesisPackage) -> str:
    data = json.dumps(_viewer_payload(package), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<title>LOOM Governed Ship Synthesis</title><style>
html,body{{margin:0;height:100%;background:#07090c;color:#e8edf3;font-family:system-ui,sans-serif;overflow:hidden}}#app{{height:100%;display:grid;grid-template-rows:auto 1fr}}header{{display:flex;gap:.35rem;align-items:center;flex-wrap:wrap;padding:.42rem;background:#11161d;border-bottom:1px solid #2c3542}}header strong{{margin-right:.25rem}}button{{background:#1b2330;color:#e8edf3;border:1px solid #46556a;border-radius:.38rem;padding:.38rem .52rem}}button.on{{background:#33445a;border-color:#d9e7f8}}#badge{{font-size:.7rem;border:1px solid #526079;border-radius:99px;padding:.18rem .4rem}}#stage{{position:relative;min-height:0}}canvas{{width:100%;height:100%;display:block;touch-action:none}}#hud{{position:absolute;left:.5rem;bottom:.5rem;max-width:93vw;background:#080c12e8;border:1px solid #354154;border-radius:.45rem;padding:.48rem;font:11px ui-monospace,monospace;white-space:pre-wrap}}@media(max-width:640px){{header{{padding:.34rem;gap:.24rem}}header strong{{width:100%;font-size:.84rem}}button{{font-size:.7rem;padding:.32rem .4rem}}#hud{{font-size:9px}}}}
</style></head><body><div id="app"><header><strong>WAYFARER — GOVERNED SYNTHESIS v0.1</strong><span id="badge">RESEARCH / NON-CANON</span><button id="all" class="on">ALL</button><button id="regions">REGIONS</button><button id="structure">STRUCTURE</button><button id="nodes">NODES</button><button data-view="iso">3/4</button><button data-view="side">SIDE</button><button data-view="top">TOP</button></header><div id="stage"><canvas id="gl"></canvas><div id="hud">Starting governed synthesis viewer…</div></div></div>
<script id="loom-data" type="application/json">{data}</script><script>
(()=>{{'use strict';
const D=JSON.parse(document.getElementById('loom-data').textContent),c=document.getElementById('gl'),hud=document.getElementById('hud');let gl;
try{{gl=c.getContext('webgl',{{antialias:true,alpha:false}})||c.getContext('experimental-webgl',{{antialias:true,alpha:false}});if(!gl)throw Error('WebGL context unavailable')}}catch(err){{hud.textContent=`WEBGL STARTUP FAIL
${{String(err&&err.stack?err.stack:err)}}`;return}}
const VS='attribute vec3 p;uniform mat4 mvp;uniform vec3 col;varying vec3 vcol;void main(){{gl_Position=mvp*vec4(p,1.);vcol=col;}}';
const FS='precision mediump float;varying vec3 vcol;void main(){{gl_FragColor=vec4(vcol,1.);}}';
function shader(type,source){{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}}
let program;try{{program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,VS));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,FS));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program)}}catch(err){{hud.textContent=`SHADER STARTUP FAIL
${{String(err&&err.stack?err.stack:err)}}`;return}}
const ap=gl.getAttribLocation(program,'p'),um=gl.getUniformLocation(program,'mvp'),uc=gl.getUniformLocation(program,'col');if(ap<0||!um||!uc){{hud.textContent='SHADER BINDING FAIL';return}}gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);
function mesh(row){{const flat=[];for(const v of row.vertices)flat.push(v[0],v[1],v[2]);const idx=[];for(const t of row.triangles)idx.push(t[0],t[1],t[2]);return {{id:row.id,kind:row.kind,v:new Float32Array(flat),i:new Uint16Array(idx)}}}}
const meshes=D.meshes.map(mesh);
function mm(a,b){{const r=new Float32Array(16);for(let col=0;col<4;col++)for(let row=0;row<4;row++)for(let k=0;k<4;k++)r[col*4+row]+=a[k*4+row]*b[col*4+k];return r}}
function persp(f,a,n,fa){{const t=1/Math.tan(f/2),r=new Float32Array(16);r[0]=t/a;r[5]=t;r[10]=(fa+n)/(n-fa);r[11]=-1;r[14]=2*fa*n/(n-fa);return r}}
function norm(v){{const n=Math.hypot(...v);return v.map(x=>x/n)}}function cross(a,b){{return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}}
function look(e,t,u){{const z=norm([e[0]-t[0],e[1]-t[1],e[2]-t[2]]),x=norm(cross(u,z)),y=cross(z,x),r=new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,0,0,0,1]);r[12]=-(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]);r[13]=-(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]);r[14]=-(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]);return r}}
let mode='all',theta=.55,phi=.52,dist=78,target=[27,0,0],drag=false,lx=0,ly=0,pinch=null;
function camera(){{const cp=Math.cos(phi),e=[target[0]+dist*cp*Math.cos(theta),target[1]+dist*Math.sin(phi),target[2]+dist*cp*Math.sin(theta)];return mm(persp(.72,c.width/c.height,.1,400),look(e,target,[0,1,0]))}}
function visible(row){{if(mode==='all')return true;if(mode==='regions')return row.kind==='REGION_ENVELOPE';if(mode==='structure')return row.kind==='STRUCTURAL_MEMBER';return row.kind==='SOURCE_NODE'}}
function color(kind){{if(kind==='REGION_ENVELOPE')return [.38,.48,.58];if(kind==='STRUCTURAL_MEMBER')return [.72,.76,.79];return [.95,.58,.22]}}
function draw(row){{const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,row.v,gl.STATIC_DRAW);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(ap);const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,row.i,gl.STATIC_DRAW);gl.uniform3fv(uc,color(row.kind));gl.drawElements(gl.TRIANGLES,row.i.length,gl.UNSIGNED_SHORT,0);gl.deleteBuffer(b);gl.deleteBuffer(ib)}}
function resize(){{const d=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.floor(c.clientWidth*d)),h=Math.max(1,Math.floor(c.clientHeight*d));if(c.width!==w||c.height!==h){{c.width=w;c.height=h}}}}
function render(){{resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.025,.032,.044,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(um,false,camera());let count=0;for(const row of meshes)if(visible(row)){{draw(row);count++}}const err=gl.getError();hud.textContent=`${{D.candidate_id}}
mode=${{mode}} meshes=${{count}} total=${{meshes.length}}
structure=${{D.structural_qualification}}
packaging OPEN=${{D.open_packaging_items.length}}
dependency graph=${{D.dependency_graph_status}}
WebGL=${{gl.getParameter(gl.VERSION)}} GLERR=${{err}}
Touch/drag orbit • pinch/wheel zoom`;requestAnimationFrame(render)}}
function setMode(m){{mode=m;['all','regions','structure','nodes'].forEach(x=>document.getElementById(x).classList.toggle('on',x===m))}}['all','regions','structure','nodes'].forEach(x=>document.getElementById(x).onclick=()=>setMode(x));
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{{const v=b.dataset.view;if(v==='side'){{theta=0;phi=.03;dist=78}}else if(v==='top'){{theta=0;phi=1.45;dist=78}}else{{theta=.55;phi=.52;dist=78}}}});
c.addEventListener('pointerdown',e=>{{drag=true;lx=e.clientX;ly=e.clientY;c.setPointerCapture&&c.setPointerCapture(e.pointerId)}});c.addEventListener('pointermove',e=>{{if(!drag)return;theta-=(e.clientX-lx)*.008;phi=Math.max(-1.45,Math.min(1.45,phi+(e.clientY-ly)*.008));lx=e.clientX;ly=e.clientY}});c.addEventListener('pointerup',()=>drag=false);c.addEventListener('pointercancel',()=>drag=false);c.addEventListener('wheel',e=>{{dist=Math.max(12,Math.min(180,dist+e.deltaY*.04));e.preventDefault()}},{{passive:false}});c.addEventListener('touchmove',e=>{{if(e.touches.length===2){{const dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY,n=Math.hypot(dx,dy);if(pinch!==null)dist=Math.max(12,Math.min(180,dist+(pinch-n)*.08));pinch=n;e.preventDefault()}}}},{{passive:false}});c.addEventListener('touchend',()=>pinch=null);render();
}})();
</script></body></html>'''


def build_viewer(package: GovernedSynthesisPackage) -> SynthesisViewerPackage:
    html = build_html(package)
    return SynthesisViewerPackage(
        version=VIEWER_VERSION,
        synthesis_package_hash=package.package_hash,
        html_sha256=_sha(html),
        html=html,
    )


def build_wayfarer_viewer(seed: int = 2226) -> SynthesisViewerPackage:
    return build_viewer(build_wayfarer_governed_synthesis(seed))


def write_viewer(package: SynthesisViewerPackage, output_dir: Path) -> Mapping[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "wayfarer_governed_synthesis.html"
    html_path.write_text(package.html, encoding="utf-8")
    manifest = {k: v for k, v in asdict(package).items() if k != "html"}
    manifest_text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    (output_dir / "viewer_manifest.json").write_text(manifest_text, encoding="utf-8")
    return {
        html_path.name: package.html_sha256,
        "viewer_manifest.json": _sha(manifest_text),
    }
