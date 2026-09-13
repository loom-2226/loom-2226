from __future__ import annotations

"""Read-only Experience One HUD presentation model.

This module presents authoritative campaign state, bounded Mara intent, and typed
Navigator review data. It performs no trajectory calculation, no state mutation,
no authorization and no execution. Browser controls only submit natural-language
intent to the server-side audited Mara adapter.
"""

from html import escape
from typing import Any, Mapping

from engineering.experience_one.e1_flight_interaction_contract import FlightReview

HUD_SCHEMA = "LOOM_E1_HUD_PRESENTATION_V1"


def _require_text(state: Mapping[str, Any], key: str) -> str:
    value = str(state.get(key) or "").strip()
    if not value:
        raise ValueError(f"campaign state missing {key}")
    return value


def _campaign_projection(state: Mapping[str, Any]) -> dict[str, Any]:
    state_id = _require_text(state, "state_id")
    epoch = _require_text(state, "epoch_utc")
    location = _require_text(state, "location_token").upper()
    ship = state.get("ship")
    if not isinstance(ship, Mapping):
        raise ValueError("campaign state missing ship mapping")
    ship_name = str(ship.get("name") or "WAYFARER").strip() or "WAYFARER"
    remass = ship.get("remass_t")
    wet_mass = ship.get("wet_mass_t")
    boundary = state.get("kinematic_boundary")
    boundary_status = None
    if isinstance(boundary, Mapping):
        boundary_status = boundary.get("status")
    return {
        "state_id": state_id,
        "epoch_utc": epoch,
        "location_token": location,
        "ship_name": ship_name,
        "remass_t": remass,
        "wet_mass_t": wet_mass,
        "kinematic_boundary_status": boundary_status,
        "state_authority": "NAVIGATOR_CAMPAIGN_READ_ONLY",
    }


def _orientation(campaign: Mapping[str, Any]) -> dict[str, Any]:
    location = str(campaign["location_token"])
    epoch = str(campaign["epoch_utc"])
    return {
        "grounded": True,
        "location_token": location,
        "epoch_utc": epoch,
        "local_geometry_status": "NOT_CLAIMED",
        "summary": f"Wayfarer is at {location} at campaign epoch {epoch}.",
        "provenance": "AUTHORITATIVE_CAMPAIGN_STATE_ONLY",
    }


def _validate_intent_payload(intent: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "contract",
        "destination",
        "priority",
        "origin",
        "calculation_authority",
        "state_authority",
        "execution_authority",
    }
    missing = sorted(required - set(intent))
    if missing:
        raise ValueError(f"flight intent presentation missing fields: {missing}")
    if str(intent["calculation_authority"]) != "ZERO":
        raise ValueError("flight intent calculation authority must remain ZERO")
    if str(intent["state_authority"]) != "ZERO":
        raise ValueError("flight intent state authority must remain ZERO")
    if str(intent["execution_authority"]) != "ZERO":
        raise ValueError("flight intent execution authority must remain ZERO")
    return dict(intent)


def build_hud_payload(
    state: Mapping[str, Any],
    *,
    intent: Mapping[str, Any] | None = None,
    review: FlightReview | None = None,
) -> dict[str, Any]:
    campaign = _campaign_projection(state)
    payload: dict[str, Any] = {
        "schema": HUD_SCHEMA,
        "campaign": campaign,
        "orientation": _orientation(campaign),
        "browser_authority": "PRESENTATION_ONLY",
        "calculation_authority": "ZERO",
        "state_authority": "ZERO",
        "execution_authority": "ZERO",
        "flight_intent": None,
        "flight_review": None,
    }
    if intent is not None:
        payload["flight_intent"] = _validate_intent_payload(intent)
    if review is not None:
        payload["flight_review"] = review.payload()
    return payload


def _num(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return escape(str(value))


def render_hud_html(payload: Mapping[str, Any]) -> str:
    campaign = payload["campaign"]
    orientation = payload["orientation"]
    intent = payload.get("flight_intent")
    review = payload.get("flight_review")

    intent_card = ""
    if isinstance(intent, Mapping):
        intent_card = (
            "<section class='panel intent-result'><div class='eyebrow'>Mara typed intent</div>"
            f"<div class='value compact'>{escape(str(intent.get('destination', '—')))}</div>"
            f"<div class='small'>Priority {escape(str(intent.get('priority', '—')))} · Origin {escape(str(intent.get('origin', '—')))}</div>"
            "<div class='small'>Calculation ZERO · State ZERO · Execution ZERO</div></section>"
        )

    review_card = ""
    if isinstance(review, Mapping):
        rows = []
        for candidate in review.get("candidates", []) or []:
            rows.append(
                "<tr>"
                f"<td>{escape(str(candidate.get('plan_number', '—')))}</td>"
                f"<td>{escape(str(candidate.get('metric', '—')))}</td>"
                f"<td>{escape(str(candidate.get('torch', '—')))}</td>"
                "</tr>"
            )
        review_card = (
            "<section class='panel review'><div class='eyebrow'>Navigator flight review</div>"
            "<div class='guard'>REVIEW ONLY · EXECUTION AUTHORITY: NONE</div>"
            "<table><thead><tr><th>PLAN</th><th>METRIC</th><th>TORCH</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></section>"
        )

    location = escape(str(campaign["location_token"]))
    epoch = escape(str(campaign["epoch_utc"]))
    ship_name = escape(str(campaign["ship_name"]))
    state_id = escape(str(campaign["state_id"]))
    boundary = escape(str(campaign.get("kinematic_boundary_status") or "—"))
    summary = escape(str(orientation["summary"]))

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'>
<title>LOOM · {ship_name}</title>
<style>
:root {{ color-scheme: dark; --bg:#07090d; --panel:#10151d; --line:#293241; --text:#e7edf4; --muted:#8f9bab; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:radial-gradient(circle at 50% -10%,#17202b 0,#07090d 44%); color:var(--text); font-family:Inter,ui-sans-serif,system-ui,sans-serif; }}
main {{ max-width:980px; margin:auto; padding:22px 16px 44px; }}
header {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; margin-bottom:18px; }}
h1 {{ margin:3px 0 0; font-size:clamp(28px,8vw,58px); letter-spacing:.08em; font-weight:650; }}
.eyebrow {{ color:var(--muted); letter-spacing:.14em; font-size:11px; font-weight:700; text-transform:uppercase; }}
.guard {{ border:1px solid var(--line); padding:8px 10px; color:var(--muted); font-size:11px; letter-spacing:.06em; white-space:nowrap; }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
.panel {{ background:rgba(16,21,29,.86); border:1px solid var(--line); padding:16px; min-height:126px; }}
.value {{ font-size:clamp(23px,7vw,42px); margin-top:7px; overflow-wrap:anywhere; }}
.value.compact {{ font-size:clamp(22px,6vw,34px); }}
.small {{ color:var(--muted); font-size:13px; margin-top:8px; line-height:1.45; }}
.orientation {{ grid-column:1/-1; min-height:150px; }}
.orientation .value {{ font-size:clamp(22px,5vw,36px); line-height:1.2; }}
.interaction {{ grid-column:1/-1; }}
form {{ display:grid; gap:10px; margin-top:12px; }}
textarea {{ width:100%; min-height:86px; resize:vertical; background:#090d13; color:var(--text); border:1px solid var(--line); padding:12px; font:inherit; }}
button {{ justify-self:start; border:1px solid #536174; background:#17202b; color:var(--text); padding:11px 15px; font:inherit; font-weight:650; }}
button:disabled {{ opacity:.55; }}
.status {{ min-height:20px; }}
.review,.intent-result {{ margin-top:12px; }}
table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
th,td {{ text-align:left; padding:9px 7px; border-top:1px solid var(--line); font-size:13px; }}
th {{ color:var(--muted); font-size:10px; letter-spacing:.14em; }}
footer {{ margin-top:14px; color:var(--muted); font-size:11px; letter-spacing:.05em; }}
@media(max-width:640px) {{ .grid {{ grid-template-columns:1fr; }} .orientation,.interaction {{ grid-column:auto; }} header {{ display:block; }} header .guard {{ display:inline-block; margin-top:12px; }} }}
</style>
</head>
<body><main>
<header><div><div class='eyebrow'>LOOM · EXPERIENCE ONE · 2226</div><h1>{ship_name}</h1></div><div class='guard'>PRESENTATION ONLY · Navigator authority</div></header>
<div class='grid'>
<section class='panel orientation'><div class='eyebrow'>Current orientation</div><div class='value'>{summary}</div><div class='small'>Local geometric placement is deliberately not claimed until a qualified Neptune spatial resolver supplies it.</div></section>
<section class='panel'><div class='eyebrow'>Location</div><div class='value'>{location}</div><div class='small'>Boundary: {boundary}</div></section>
<section class='panel'><div class='eyebrow'>Campaign epoch</div><div class='value'>{epoch}</div><div class='small'>State {state_id}</div></section>
<section class='panel'><div class='eyebrow'>Remass</div><div class='value'>{_num(campaign.get('remass_t'))} t</div><div class='small'>Read directly from campaign state.</div></section>
<section class='panel'><div class='eyebrow'>Wet mass</div><div class='value'>{_num(campaign.get('wet_mass_t'))} t</div><div class='small'>Read directly from campaign state.</div></section>
<section class='panel interaction'><div class='eyebrow'>Tell Mara where you want to go</div><div class='small'>Mara may translate your words into a typed destination and priority. Mara cannot calculate a route, change campaign state, authorize, or execute.</div><form id='flight-intent-form'><textarea id='flight-intent-text' maxlength='1000' placeholder='Take us to Neptune, balanced profile.' required></textarea><button id='flight-intent-submit' type='submit'>INTERPRET INTENT</button><div class='small status' id='flight-intent-status'></div></form></section>
</div>
{intent_card}
{review_card}
<footer>Browser calculation authority: ZERO · browser state authority: ZERO · browser execution authority: ZERO</footer>
<script>
const form=document.getElementById('flight-intent-form');
const text=document.getElementById('flight-intent-text');
const button=document.getElementById('flight-intent-submit');
const status=document.getElementById('flight-intent-status');
form.addEventListener('submit', async (event) => {{
  event.preventDefault();
  const value=text.value.trim();
  if(!value) return;
  button.disabled=true;
  status.textContent='Mara is translating intent…';
  try {{
    const response=await fetch('/intent.json', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{text:value}})}});
    const data=await response.json();
    if(!response.ok) throw new Error(data.message || data.reason || 'intent request failed');
    status.textContent='Typed intent received. Reloading…';
    location.reload();
  }} catch(error) {{
    status.textContent='Intent failed: '+error.message;
    button.disabled=false;
  }}
}});
</script>
</main></body></html>"""
