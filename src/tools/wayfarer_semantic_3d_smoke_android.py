from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import wayfarer_semantic_3d_smoke as base


COLUMN_MAJOR_MM = r"""function mm(a,b){let o=new Float32Array(16),a00=a[0],a01=a[1],a02=a[2],a03=a[3],a10=a[4],a11=a[5],a12=a[6],a13=a[7],a20=a[8],a21=a[9],a22=a[10],a23=a[11],a30=a[12],a31=a[13],a32=a[14],a33=a[15],b0,b1,b2,b3;b0=b[0];b1=b[1];b2=b[2];b3=b[3];o[0]=b0*a00+b1*a10+b2*a20+b3*a30;o[1]=b0*a01+b1*a11+b2*a21+b3*a31;o[2]=b0*a02+b1*a12+b2*a22+b3*a32;o[3]=b0*a03+b1*a13+b2*a23+b3*a33;b0=b[4];b1=b[5];b2=b[6];b3=b[7];o[4]=b0*a00+b1*a10+b2*a20+b3*a30;o[5]=b0*a01+b1*a11+b2*a21+b3*a31;o[6]=b0*a02+b1*a12+b2*a22+b3*a32;o[7]=b0*a03+b1*a13+b2*a23+b3*a33;b0=b[8];b1=b[9];b2=b[10];b3=b[11];o[8]=b0*a00+b1*a10+b2*a20+b3*a30;o[9]=b0*a01+b1*a11+b2*a21+b3*a31;o[10]=b0*a02+b1*a12+b2*a22+b3*a32;o[11]=b0*a03+b1*a13+b2*a23+b3*a33;b0=b[12];b1=b[13];b2=b[14];b3=b[15];o[12]=b0*a00+b1*a10+b2*a20+b3*a30;o[13]=b0*a01+b1*a11+b2*a21+b3*a31;o[14]=b0*a02+b1*a12+b2*a22+b3*a32;o[15]=b0*a03+b1*a13+b2*a23+b3*a33;return o}"""


def build_html() -> str:
    html = base.build_html()
    # Keep JavaScript strings syntactically valid after Python triple-quoted rendering.
    html = html.replace("+'\n'+", "+'\\n'+")
    html = html.replace("+'\nobjects=", "+'\\nobjects=")
    html = html.replace("zoom\nblue=", "zoom\\nblue=")

    # The research smoke viewer mixed row-major multiplication with WebGL's
    # column-major matrices. Correct only the Android runtime realization;
    # engineering geometry remains untouched.
    html, count = re.subn(
        r"function mm\(a,b\)\{let r=new Float32Array\(16\);.*?return r\}",
        COLUMN_MAJOR_MM,
        html,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Could not patch WebGL matrix multiplication")

    # Do not cull coarse research triangles: winding is not an engineering claim.
    html = html.replace("gl.enable(gl.CULL_FACE);", "gl.disable(gl.CULL_FACE);")

    # Surface runtime failures on the Pixel instead of leaving a blank canvas.
    html = html.replace(
        "(()=>{'use strict';const D=",
        "(()=>{'use strict';const __hud=document.getElementById('hud');try{__hud.textContent='WEBGL_BOOTSTRAP_STARTED';const D=",
        1,
    )
    html = html.replace(
        "render();})();</script>",
        "render();}catch(e){__hud.textContent='WEBGL_RUNTIME_ERROR\\n'+(e&&e.stack?e.stack:String(e));console.error(e);}})();</script>",
        1,
    )
    if "WEBGL_BOOTSTRAP_STARTED" not in html or "WEBGL_RUNTIME_ERROR" not in html:
        raise RuntimeError("Could not install Pixel WebGL runtime diagnostics")
    return html


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "wayfarer_semantic_3d_smoke.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
