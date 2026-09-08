from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Mapping, Tuple

from model_permutation_experiment import execute_designer_response
from physical_design_core import BoxGeometry, CandidateDesign, CylinderXGeometry, PhysicalDesignError
from wayfarer_s1_solver import solve

BROWSER_3D_VERSION = "LOOM_WAYFARER_BROWSER_3D_v0.1"
BROWSER_3D_AUTHORITY = "REVIEW_EVIDENCE_ONLY"
STATUS = ("ENGINEERING_RESEARCH", "NON_CANON", "NON_PRODUCTION")


@dataclass(frozen=True)
class Browser3DPackage:
    version: str
    parent_candidate_id: str
    child_candidate_id: str
    html_sha256: str
    source_response_sha256: str
    html: str
    authority_status: str = BROWSER_3D_AUTHORITY
    flight_dynamics_authority: bool = False
    canon_changed: bool = False
    production_shipclasses_changed: bool = False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _primitive_records(candidate: CandidateDesign) -> Tuple[dict, ...]:
    type_map = {row.type_id: row for row in candidate.component_types}
    out = []
    for instance in sorted(candidate.component_instances, key=lambda row: row.instance_id):
        if not instance.active:
            continue
        ctype = type_map.get(instance.component_type_id)
        if ctype is None or ctype.admitted_geometry is None:
            continue
        q = tuple(float(v) for v in instance.transform.quaternion_wxyz)
        if q != (1.0, 0.0, 0.0, 0.0):
            raise PhysicalDesignError("browser 3D v0.1 only admits identity body orientation")
        geom = ctype.admitted_geometry
        if isinstance(geom, BoxGeometry):
            kind = "BOX"
            dims = {"x_m": geom.x_m, "y_m": geom.y_m, "z_m": geom.z_m}
        elif isinstance(geom, CylinderXGeometry):
            kind = "CYLINDER_X"
            dims = {"length_m": geom.length_m, "diameter_m": geom.diameter_m}
        else:
            raise PhysicalDesignError(f"unsupported admitted geometry {type(geom).__name__}")
        out.append({
            "id": instance.instance_id,
            "component_type_id": instance.component_type_id,
            "kind": kind,
            "dimensions": dims,
            "translation_m": [float(v) for v in instance.transform.translation_m],
            "authority_status": BROWSER_3D_AUTHORITY,
        })
    for point in sorted(candidate.point_masses, key=lambda row: row.source_id):
        out.append({
            "id": point.source_id,
            "component_type_id": "POINT_MASS",
            "kind": "POINT",
            "dimensions": {"radius_m": 0.22},
            "translation_m": [float(v) for v in point.centroid_m],
            "authority_status": BROWSER_3D_AUTHORITY,
        })
    return tuple(out)


def _scene(candidate: CandidateDesign) -> dict:
    return {
        "candidate_id": candidate.candidate_id,
        "authority_status": BROWSER_3D_AUTHORITY,
        "primitives": _primitive_records(candidate),
    }


def _html(parent: CandidateDesign, child: CandidateDesign, source_response_sha256: str) -> str:
    payload = {
        "version": BROWSER_3D_VERSION,
        "status": STATUS,
        "authority_status": BROWSER_3D_AUTHORITY,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
        "source_response_sha256": source_response_sha256,
        "parent": _scene(parent),
        "child": _scene(child),
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<title>LOOM Wayfarer Shipyard 3D</title><style>
html,body{{margin:0;height:100%;background:#090b0e;color:#e8edf3;font-family:system-ui,sans-serif;overflow:hidden}}#app{{height:100%;display:grid;grid-template-rows:auto 1fr}}header{{display:flex;gap:.4rem;align-items:center;flex-wrap:wrap;padding:.45rem;background:#12161c;border-bottom:1px solid #2a313c}}button{{background:#1c232d;color:#e8edf3;border:1px solid #465265;border-radius:.35rem;padding:.4rem .55rem}}button.on{{border-color:#dbe7f7;background:#2b3746}}#stage{{position:relative;min-height:0}}canvas{{width:100%;height:100%;display:block;touch-action:none}}#hud{{position:absolute;left:.5rem;bottom:.5rem;max-width:92vw;background:#0b0f15dd;border:1px solid #384353;border-radius:.4rem;padding:.45rem;font:12px ui-monospace,monospace;white-space:pre-wrap}}#badge{{font-size:.72rem;border:1px solid #465265;border-radius:99px;padding:.18rem .4rem}}@media(max-width:640px){{header{{padding:.35rem;gap:.25rem}}button{{font-size:.72rem;padding:.34rem .42rem}}#hud{{font-size:10px}}}}
</style></head><body><div id="app"><header><strong>WAYFARER SHIPYARD 3D v0.1</strong><span id="badge">REVIEW EVIDENCE ONLY</span><button id="parent" class="on">PARENT</button><button id="child">CHILD</button><button id="overlay">OVERLAY</button><button data-view="iso">3/4</button><button data-view="side">SIDE</button><button data-view="top">TOP</button></header><div id="stage"><canvas id="gl"></canvas><div id="hud"></div></div></div>
<script id="loom-data" type="application/json">{data}</script><script>
(()=>{{'use strict';const D=JSON.parse(document.getElementById('loom-data').textContent),c=document.getElementById('gl'),gl=c.getContext('webgl',{{antialias:true,alpha:false}});if(!gl){{document.getElementById('hud').textContent='WebGL unavailable on this browser';return;}}
const VS='attribute vec3 p;uniform mat4 mvp;uniform vec3 col;varying vec3 vcol;void main(){{gl_Position=mvp*vec4(p,1.);vcol=col;}}',FS='precision mediump float;varying vec3 vcol;void main(){{gl_FragColor=vec4(vcol,1.);}}';function sh(t,s){{let x=gl.createShader(t);gl.shaderSource(x,s);gl.compileShader(x);if(!gl.getShaderParameter(x,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(x));return x}}const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,VS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,FS));gl.linkProgram(pr);gl.useProgram(pr);const ap=gl.getAttribLocation(pr,'p'),um=gl.getUniformLocation(pr,'mvp'),uc=gl.getUniformLocation(pr,'col');gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);
function box(d){{let x=d.x_m/2,y=d.y_m/2,z=d.z_m/2,v=[-x,-y,-z, x,-y,-z, x,y,-z,-x,y,-z,-x,-y,z, x,-y,z, x,y,z,-x,y,z],f=[0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,3,2,6,3,6,7,1,5,6,1,6,2,0,3,7,0,7,4];return [v,f]}}function cyl(d,n=20){{let v=[],f=[],L=d.length_m/2,r=d.diameter_m/2;for(let s of [-L,L])for(let i=0;i<n;i++){{let a=2*Math.PI*i/n;v.push(s,r*Math.cos(a),r*Math.sin(a))}}for(let i=0;i<n;i++){{let j=(i+1)%n,a=i,b=j,c=n+j,e=n+i;f.push(a,c,b,a,e,c)}}return [v,f]}}function point(d){{let r=d.radius_m,v=[r,0,0,-r,0,0,0,r,0,0,-r,0,0,0,r,0,0,-r],f=[0,2,4,0,4,3,0,3,5,0,5,2,1,4,2,1,3,4,1,5,3,1,2,5];return [v,f]}}
function mesh(o){{let q=o.kind==='BOX'?box(o.dimensions):o.kind==='CYLINDER_X'?cyl(o.dimensions):point(o.dimensions),v=q[0],t=o.translation_m;for(let i=0;i<v.length;i+=3){{v[i]+=t[0];v[i+1]+=t[1];v[i+2]+=t[2]}}return {{id:o.id,v:new Float32Array(v),i:new Uint16Array(q[1])}}}}const scenes={{parent:D.parent.primitives.map(mesh),child:D.child.primitives.map(mesh)}};
function mm(a,b){{let r=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++)r[i*4+j]+=a[i*4+k]*b[k*4+j];return r}}function persp(f,a,n,fa){{let t=1/Math.tan(f/2),r=new Float32Array(16);r[0]=t/a;r[5]=t;r[10]=(fa+n)/(n-fa);r[11]=-1;r[14]=2*fa*n/(n-fa);return r}}function norm(v){{let n=Math.hypot(...v);return v.map(x=>x/n)}}function cross(a,b){{return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}}function look(e,t,u){{let z=norm([e[0]-t[0],e[1]-t[1],e[2]-t[2]]),x=norm(cross(u,z)),y=cross(z,x),r=new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,0,0,0,1]);r[12]=-(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]);r[13]=-(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]);r[14]=-(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]);return r}}
let mode='parent',theta=.55,phi=.55,dist=72,target=[27,0,0],drag=false,lx=0,ly=0;function camera(){{let cp=Math.cos(phi),e=[target[0]+dist*cp*Math.cos(theta),target[1]+dist*Math.sin(phi),target[2]+dist*cp*Math.sin(theta)];return mm(persp(.72,c.width/c.height,.1,300),look(e,target,[0,1,0]))}}function drawScene(rows,col){{for(let o of rows){{let b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,o.v,gl.STATIC_DRAW);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(ap);let ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,o.i,gl.STATIC_DRAW);gl.uniform3fv(uc,col);gl.drawElements(gl.TRIANGLES,o.i.length,gl.UNSIGNED_SHORT,0);gl.deleteBuffer(b);gl.deleteBuffer(ib)}}}}
function render(){{resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.035,.045,.06,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(um,false,camera());if(mode==='overlay'){{drawScene(scenes.parent,[.35,.55,.8]);gl.disable(gl.CULL_FACE);drawScene(scenes.child,[.9,.55,.25]);gl.enable(gl.CULL_FACE)}}else drawScene(scenes[mode],[.72,.78,.84]);document.getElementById('hud').textContent=(mode==='overlay'?'PARENT + CHILD':D[mode].candidate_id)+'\nTouch/drag: orbit • pinch/wheel: zoom\n'+D.authority_status+' • NON-CANON • NON-PRODUCTION';requestAnimationFrame(render)}}function resize(){{let d=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.floor(c.clientWidth*d)),h=Math.max(1,Math.floor(c.clientHeight*d));if(c.width!==w||c.height!==h){{c.width=w;c.height=h}}}}
function setMode(m){{mode=m;['parent','child','overlay'].forEach(x=>document.getElementById(x).classList.toggle('on',x===m))}}['parent','child','overlay'].forEach(x=>document.getElementById(x).onclick=()=>setMode(x));document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{{let v=b.dataset.view;if(v==='side'){{theta=0;phi=.03;dist=72}}else if(v==='top'){{theta=0;phi=1.45;dist=72}}else{{theta=.55;phi=.55;dist=72}}}});
c.addEventListener('pointerdown',e=>{{drag=true;lx=e.clientX;ly=e.clientY;c.setPointerCapture&&c.setPointerCapture(e.pointerId)}});c.addEventListener('pointermove',e=>{{if(!drag)return;theta-=(e.clientX-lx)*.008;phi=Math.max(-1.45,Math.min(1.45,phi+(e.clientY-ly)*.008));lx=e.clientX;ly=e.clientY}});c.addEventListener('pointerup',()=>drag=false);c.addEventListener('wheel',e=>{{dist=Math.max(15,Math.min(160,dist+e.deltaY*.04));e.preventDefault()}},{{passive:false}});let pinch=null;c.addEventListener('touchmove',e=>{{if(e.touches.length===2){{let dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY,n=Math.hypot(dx,dy);if(pinch)dist=Math.max(15,Math.min(160,dist+(pinch-n)*.08));pinch=n;e.preventDefault()}}}},{{passive:false}});c.addEventListener('touchend',()=>pinch=null);render();}})();
</script></body></html>'''


def build_browser_3d(parent: CandidateDesign, child: CandidateDesign, *, source_response_sha256: str) -> Browser3DPackage:
    html = _html(parent, child, source_response_sha256)
    return Browser3DPackage(
        version=BROWSER_3D_VERSION,
        parent_candidate_id=parent.candidate_id,
        child_candidate_id=child.candidate_id,
        html_sha256=_sha(html),
        source_response_sha256=source_response_sha256,
        html=html,
    )


def build_run001_browser_3d(raw_designer_response: str, seed: int = 2226) -> Browser3DPackage:
    parent = solve(seed).candidate
    _, _, child, _, _, _ = execute_designer_response(raw_designer_response, seed=seed)
    return build_browser_3d(parent, child, source_response_sha256=_sha(raw_designer_response))


def write_browser_3d(package: Browser3DPackage, output_dir: Path) -> Mapping[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "wayfarer_shipyard_3d.html"
    html_path.write_text(package.html, encoding="utf-8")
    manifest = {
        k: v for k, v in asdict(package).items() if k != "html"
    }
    manifest["status"] = STATUS
    manifest_text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    (output_dir / "browser_3d_manifest.json").write_text(manifest_text, encoding="utf-8")
    return {
        "wayfarer_shipyard_3d.html": package.html_sha256,
        "browser_3d_manifest.json": _sha(manifest_text),
    }
