from __future__ import annotations

from dataclasses import replace

from wayfarer_browser_3d import Browser3DPackage, build_run001_browser_3d

PIXEL_FIX_VERSION = "LOOM_WAYFARER_BROWSER_3D_PIXEL_FIX_v0.2"

_BAD_MM = "function mm(a,b){let r=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++)r[i*4+j]+=a[i*4+k]*b[k*4+j];return r}"
_GOOD_MM = "function mm(a,b){let r=new Float32Array(16);for(let col=0;col<4;col++)for(let row=0;row<4;row++)for(let k=0;k<4;k++)r[col*4+row]+=a[k*4+row]*b[col*4+k];return r}"

_OLD_GL = "const D=JSON.parse(document.getElementById('loom-data').textContent),c=document.getElementById('gl'),gl=c.getContext('webgl',{antialias:true,alpha:false});if(!gl){document.getElementById('hud').textContent='WebGL unavailable on this browser';return;}"
_NEW_GL = "const D=JSON.parse(document.getElementById('loom-data').textContent),c=document.getElementById('gl'),hud=document.getElementById('hud');let gl;try{gl=c.getContext('webgl',{antialias:true,alpha:false})||c.getContext('experimental-webgl',{antialias:true,alpha:false});if(!gl)throw Error('WebGL context unavailable');hud.textContent='WebGL context OK • initializing renderer';}catch(err){hud.textContent='PIXEL STARTUP FAIL\\n'+String(err&&err.stack?err.stack:err);return;}"

_OLD_LINK = "gl.linkProgram(pr);gl.useProgram(pr);const ap=gl.getAttribLocation(pr,'p'),um=gl.getUniformLocation(pr,'mvp'),uc=gl.getUniformLocation(pr,'col');gl.enable(gl.DEPTH_TEST);"
_NEW_LINK = "gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS))throw Error('PROGRAM LINK FAIL: '+gl.getProgramInfoLog(pr));gl.useProgram(pr);const ap=gl.getAttribLocation(pr,'p'),um=gl.getUniformLocation(pr,'mvp'),uc=gl.getUniformLocation(pr,'col');if(ap<0||!um||!uc)throw Error('shader bindings unavailable');gl.enable(gl.DEPTH_TEST);"

_OLD_RENDER = "function render(){resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.035,.045,.06,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(um,false,camera());"
_NEW_RENDER = "let firstFrame=true;function render(){resize();gl.viewport(0,0,c.width,c.height);gl.clearColor(.035,.045,.06,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(um,false,camera());"

_OLD_HUD = "document.getElementById('hud').textContent=(mode==='overlay'?'PARENT + CHILD':D[mode].candidate_id)+'\\nTouch/drag: orbit • pinch/wheel: zoom\\n'+D.authority_status+' • NON-CANON • NON-PRODUCTION';requestAnimationFrame(render)}"
_NEW_HUD = "{let err=gl.getError(),label=(mode==='overlay'?'PARENT + CHILD':D[mode].candidate_id);hud.textContent=label+'\\nTouch/drag: orbit • pinch/wheel: zoom\\nWebGL '+gl.getParameter(gl.VERSION)+' • GLERR '+err+'\\n'+D.authority_status+' • NON-CANON • NON-PRODUCTION';if(firstFrame)firstFrame=false;}requestAnimationFrame(render)}"


def patch_pixel_blank_render(package: Browser3DPackage) -> Browser3DPackage:
    html = package.html
    replacements = (
        (_BAD_MM, _GOOD_MM),
        (_OLD_GL, _NEW_GL),
        (_OLD_LINK, _NEW_LINK),
        (_OLD_RENDER, _NEW_RENDER),
        (_OLD_HUD, _NEW_HUD),
    )
    for old, new in replacements:
        if old not in html:
            raise ValueError(f"Pixel fix anchor missing: {old[:48]}")
        html = html.replace(old, new, 1)
    import hashlib
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    return replace(package, version=PIXEL_FIX_VERSION, html=html, html_sha256=digest)


def build_run001_browser_3d_pixel_fix(raw_designer_response: str, seed: int = 2226) -> Browser3DPackage:
    return patch_pixel_blank_render(build_run001_browser_3d(raw_designer_response, seed=seed))
