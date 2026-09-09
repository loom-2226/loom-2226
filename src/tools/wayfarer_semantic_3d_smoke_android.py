from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import wayfarer_semantic_3d_smoke as base


def build_html() -> str:
    html = base.build_html()
    # The research builder embeds JavaScript inside a Python triple-quoted string.
    # Convert accidental literal newlines inside JS single-quoted strings back
    # into explicit JS escape sequences for Android/Chrome and browser parity.
    html = html.replace("+'\n'+", "+'\\n'+")
    html = html.replace("+'\nobjects=", "+'\\nobjects=")
    html = html.replace("zoom\nblue=", "zoom\\nblue=")
    return html


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "wayfarer_semantic_3d_smoke.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
