from __future__ import annotations

import hashlib
from dataclasses import replace

from wayfarer_browser_3d import Browser3DPackage
from wayfarer_browser_3d_pixel_fix import build_run001_browser_3d_pixel_fix

JS_SYNTAX_FIX_VERSION = "LOOM_WAYFARER_BROWSER_3D_JS_SYNTAX_FIX_v0.1"

_BAD_HUD = "document.getElementById('hud').textContent=(mode==='overlay'?'PARENT + CHILD':D[mode].candidate_id)+'\nTouch/drag: orbit • pinch/wheel: zoom\n'+D.authority_status+' • NON-CANON • NON-PRODUCTION';requestAnimationFrame(render)}"
_GOOD_HUD = "document.getElementById('hud').textContent=(mode==='overlay'?'PARENT + CHILD':D[mode].candidate_id)+'\\nTouch/drag: orbit • pinch/wheel: zoom\\n'+D.authority_status+' • NON-CANON • NON-PRODUCTION';requestAnimationFrame(render)}"


def patch_js_string_escapes(package: Browser3DPackage) -> Browser3DPackage:
    html = package.html
    if _BAD_HUD not in html:
        raise ValueError("browser 3D JavaScript newline anchor missing")
    html = html.replace(_BAD_HUD, _GOOD_HUD, 1)
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    return replace(package, version=JS_SYNTAX_FIX_VERSION, html=html, html_sha256=digest)


def build_run001_browser_3d_js_syntax_fix(raw_designer_response: str, seed: int = 2226) -> Browser3DPackage:
    return patch_js_string_escapes(build_run001_browser_3d_pixel_fix(raw_designer_response, seed=seed))
