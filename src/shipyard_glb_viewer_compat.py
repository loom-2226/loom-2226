from __future__ import annotations

from shipyard_glb_viewer import viewer_html as _viewer_html_v01

COMPAT_VERSION = "LOOM_SHIPYARD_GLB_VIEWER_COMPAT_v0.1"


def viewer_html() -> str:
    """Return the offline GLB viewer with WebGL1/WebGL2 uint32-index compatibility.

    Legacy Wayfarer visual-reference GLBs use UNSIGNED_INT index accessors. The
    governed semantic GLB normally emits UNSIGNED_SHORT where possible. WebGL1
    requires OES_element_index_uint before UNSIGNED_INT drawElements calls;
    WebGL2 supports them natively. This wrapper preserves the existing viewer
    while enabling that compatibility path and failing visibly if unavailable.
    """
    html = _viewer_html_v01()
    context_old = "const gl=c.getContext('webgl',{antialias:true,alpha:false});if(!gl){hud.textContent='WEBGL UNAVAILABLE';return}"
    context_new = (
        "const gl=c.getContext('webgl2',{antialias:true,alpha:false})||"
        "c.getContext('webgl',{antialias:true,alpha:false});"
        "if(!gl){hud.textContent='WEBGL UNAVAILABLE';return}"
        "const isWebGL2=(typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext);"
        "const uint32IndexOK=isWebGL2||!!gl.getExtension('OES_element_index_uint');"
    )
    draw_old = "gl.drawElements(gl.TRIANGLES,r.i.length,r.i instanceof Uint32Array?gl.UNSIGNED_INT:gl.UNSIGNED_SHORT,0);"
    draw_new = (
        "if(r.i instanceof Uint32Array&&!uint32IndexOK)throw Error('UNSIGNED_INT indices require WebGL2 or OES_element_index_uint');"
        "gl.drawElements(gl.TRIANGLES,r.i.length,r.i instanceof Uint32Array?gl.UNSIGNED_INT:gl.UNSIGNED_SHORT,0);"
    )
    if context_old not in html or draw_old not in html:
        raise RuntimeError("base GLB viewer changed; compatibility patch no longer matches")
    html = html.replace(context_old, context_new, 1).replace(draw_old, draw_new, 1)
    return html
