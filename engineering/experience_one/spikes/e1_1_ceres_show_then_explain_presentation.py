#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 bounded SHOW-THEN-EXPLAIN presentation diagnostic.

This is an additive, standalone Pixel/browser presentation experiment. It does NOT
replace HUD/GIS/Atlas presentation, does not call a model, does not query SQLite,
and does not mutate campaign or canon state.

Input: an already-qualified LOOM_CANON_CONTEXT_PROJECTION_V1 JSON artifact.
Output: a self-contained offline HTML page built only from deterministic ORIENT and
INTERESTING query packets.

Purpose: test the PRESENTATION seam after DATA, PROJECTION, and bounded SYNTHESIS
have each been separately exercised. A passing technical render does not establish
zero-instruction usability; it only gives us a concrete surface to inspect on Pixel.
"""

import argparse
import html
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
DEFAULT_PROJECTION = Path("/storage/emulated/0/Download/E1_1_CERES_CONTEXT_V1.json")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_CERES_SHOW_THEN_EXPLAIN.html")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


query_mod = _load(SRC / "loom_canon_context_query.py", "loom_canon_context_query")


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def build_view_model(projection: dict[str, Any]) -> dict[str, Any]:
    orient = query_mod.query_projection(projection, "ORIENT")
    interesting = query_mod.query_projection(projection, "INTERESTING", max_items=3)

    entity = orient.get("context_entity") or {}
    facts = orient.get("facts") or {}
    identity = ((facts.get("identity") or {}).get("value") or {})
    political = (facts.get("political_context") or {}).get("value")
    transport = (facts.get("transport_role") or {}).get("value")
    items = interesting.get("items") or []

    if entity.get("entity_id") != "CER":
        raise ValueError("presentation diagnostic is bounded to Ceres/CER")
    if not identity.get("summary"):
        raise ValueError("Ceres identity summary missing")
    if not items:
        raise ValueError("Ceres interesting-place packet is empty")

    cards = []
    for item in items:
        cards.append(
            {
                "entity_id": item.get("entity_id"),
                "name": item.get("name"),
                "role": item.get("role"),
                "traffic_class": item.get("traffic_class"),
                "strategic_importance": item.get("strategic_importance"),
                "commercial_openness": item.get("commercial_openness"),
                "governance_style": item.get("governance_style"),
                "epistemic_status": item.get("epistemic_status"),
                "why_selected": item.get("why_selected"),
                "provenance_by_field": item.get("provenance_by_field"),
            }
        )

    return {
        "schema": "LOOM_E1_1_CERES_PRESENTATION_VIEW_V1",
        "entity": {
            "entity_id": entity.get("entity_id"),
            "name": entity.get("name"),
            "summary": identity.get("summary"),
            "political_context": political,
            "transport_role": transport,
        },
        "notice_cards": cards,
        "ask_next": [
            "What is this place?",
            "What is interesting here?",
            "Why is the Metric & Loom Anchorage restricted?",
        ],
        "authority": {
            "source": "DETERMINISTIC_ORIENT_AND_INTERESTING_PACKETS",
            "selection_authority": "PRESENTATION_DERIVED_NON_AUTHORITY",
            "model_called": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "campaign_mutation": False,
            "canon_mutation": False,
            "network_required": False,
        },
    }


def render_html(view: dict[str, Any]) -> str:
    entity = view["entity"]
    cards = view["notice_cards"]
    prompts = view["ask_next"]

    card_html = []
    for card in cards:
        strategic = card.get("strategic_importance")
        openness = card.get("commercial_openness")
        strategic_text = "—" if strategic is None else f"{float(strategic):.3f}"
        openness_text = "—" if openness is None else f"{float(openness):.3f}"
        prov = json.dumps(card.get("provenance_by_field") or {}, indent=2, sort_keys=True)
        card_html.append(
            f"""
            <article class="notice-card">
              <div class="eyebrow">{_e(card.get('role') or 'PLACE')} · {_e(card.get('traffic_class') or 'UNKNOWN')}</div>
              <h3>{_e(card.get('name') or card.get('entity_id'))}</h3>
              <div class="stats">
                <span>Strategic <b>{_e(strategic_text)}</b></span>
                <span>Openness <b>{_e(openness_text)}</b></span>
                <span>{_e(card.get('governance_style') or 'UNKNOWN')}</span>
              </div>
              <details>
                <summary>Why am I seeing this?</summary>
                <p>Shown by a deterministic presentation ranking over the qualified Canon Context packet. This is not a canon claim about subjective importance.</p>
              </details>
              <details>
                <summary>Provenance</summary>
                <pre>{_e(prov)}</pre>
              </details>
            </article>
            """
        )

    prompt_html = "".join(
        f'<button class="prompt" type="button" data-prompt="{_e(p)}">{_e(p)}</button>'
        for p in prompts
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LOOM — {_e(entity['name'])}</title>
<style>
:root {{ color-scheme: dark; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#080b10; color:#e8edf3; }}
main {{ max-width:900px; margin:0 auto; padding:20px 16px 48px; }}
.topline {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#8b98a7; }}
h1 {{ font-size:40px; margin:8px 0 10px; }}
.lede {{ font-size:18px; line-height:1.5; color:#c9d2dc; margin-bottom:20px; }}
.context-grid {{ display:grid; grid-template-columns:1fr; gap:10px; margin:18px 0 28px; }}
.context {{ padding:14px; border:1px solid #27313d; border-radius:14px; background:#10151d; }}
.context b {{ display:block; margin-bottom:4px; }}
h2 {{ margin-top:30px; font-size:22px; }}
.notice-grid {{ display:grid; grid-template-columns:1fr; gap:12px; }}
.notice-card {{ border:1px solid #293441; border-radius:16px; padding:16px; background:#0f141b; }}
.notice-card h3 {{ margin:6px 0 12px; font-size:20px; }}
.eyebrow {{ font-size:12px; color:#95a5b7; letter-spacing:.06em; }}
.stats {{ display:flex; flex-wrap:wrap; gap:8px; font-size:13px; color:#c4ced8; }}
.stats span {{ border:1px solid #2d3947; border-radius:999px; padding:6px 9px; }}
details {{ margin-top:12px; color:#aeb9c5; }}
summary {{ cursor:pointer; color:#d7dee6; }}
pre {{ overflow:auto; white-space:pre-wrap; font-size:11px; line-height:1.35; background:#080b10; padding:10px; border-radius:10px; }}
.ask {{ margin-top:30px; padding:16px; border:1px solid #334253; border-radius:16px; background:#111923; }}
.prompt-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
.prompt {{ border:1px solid #3a4a5d; background:#172230; color:#e8edf3; border-radius:999px; padding:10px 12px; font:inherit; }}
.prompt:active {{ transform:scale(.99); }}
#selected {{ margin:14px 0 0; color:#b9c7d5; min-height:1.4em; }}
.foot {{ margin-top:28px; color:#708092; font-size:12px; }}
@media (min-width:720px) {{ .context-grid {{ grid-template-columns:1fr 1fr; }} .notice-grid {{ grid-template-columns:repeat(3,1fr); }} }}
</style>
</head>
<body>
<main>
  <div class="topline">LOOM · SHOW THEN EXPLAIN · 2226 CANON CONTEXT</div>
  <h1>{_e(entity['name'])}</h1>
  <div class="lede">{_e(entity['summary'])}</div>

  <section class="context-grid" aria-label="Ceres context">
    <div class="context"><b>Political context</b>{_e(entity.get('political_context') or 'Not established')}</div>
    <div class="context"><b>Transport role</b>{_e(entity.get('transport_role') or 'Not established')}</div>
  </section>

  <h2>What to notice</h2>
  <section class="notice-grid">
    {''.join(card_html)}
  </section>

  <section class="ask">
    <div class="topline">Ask next</div>
    <h2 style="margin-top:6px">You should not need to know the database to explore the world.</h2>
    <div class="prompt-row">{prompt_html}</div>
    <p id="selected" aria-live="polite"></p>
  </section>

  <div class="foot">Standalone E1.1 presentation diagnostic. Read-only. Offline. No model call. No campaign or canon mutation.</div>
</main>
<script>
for (const button of document.querySelectorAll('.prompt')) {{
  button.addEventListener('click', async () => {{
    const text = button.dataset.prompt;
    document.getElementById('selected').textContent = 'Ask Mara: “' + text + '”';
    try {{ await navigator.clipboard.writeText(text); }} catch (_) {{}}
  }});
}}
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projection", type=Path, default=DEFAULT_PROJECTION)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    projection = json.loads(args.projection.expanduser().read_text(encoding="utf-8"))
    view = build_view_model(projection)
    rendered = render_html(view)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")

    print("schema:", view["schema"])
    print("place:", view["entity"]["name"])
    print("notice_count:", len(view["notice_cards"]))
    for i, card in enumerate(view["notice_cards"], 1):
        print(f"notice_{i}: {card['entity_id']} | {card['name']} | {card['role']} | {card['traffic_class']}")
    print("ask_next:")
    for prompt in view["ask_next"]:
        print(" -", prompt)
    print("model_called:", view["authority"]["model_called"])
    print("network_required:", view["authority"]["network_required"])
    print("campaign_mutation:", view["authority"]["campaign_mutation"])
    print("canon_mutation:", view["authority"]["canon_mutation"])
    print("out:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
