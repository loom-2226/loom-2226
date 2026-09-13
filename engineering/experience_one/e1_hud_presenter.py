from __future__ import annotations

"""Experience One HUD presentation model with zero browser authority."""

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
    boundary = state.get("kinematic_boundary")
    return {
        "state_id": state_id, "epoch_utc": epoch, "location_token": location,
        "ship_name": str(ship.get("name") or "WAYFARER").strip() or "WAYFARER",
        "remass_t": ship.get("remass_t"), "wet_mass_t": ship.get("wet_mass_t"),
        "kinematic_boundary_status": boundary.get("status") if isinstance(boundary, Mapping) else None,
        "state_authority": "NAVIGATOR_CAMPAIGN_READ_ONLY",
    }


def _orientation(campaign: Mapping[str, Any]) -> dict[str, Any]:
    location, epoch = str(campaign["location_token"]), str(campaign["epoch_utc"])
    return {"grounded": True, "location_token": location, "epoch_utc": epoch,
            "local_geometry_status": "NOT_CLAIMED",
            "summary": f"Wayfarer is at {location} at campaign epoch {epoch}.",
            "provenance": "AUTHORITATIVE_CAMPAIGN_STATE_ONLY"}


def _validate_intent_payload(intent: Mapping[str, Any]) -> dict[str, Any]:
    for field in ("calculation_authority", "state_authority", "execution_authority"):
        if str(intent.get(field)) != "ZERO":
            raise ValueError(f"flight intent {field} must remain ZERO")
    return dict(intent)


def _review_payload(review: FlightReview | Mapping[str, Any]) -> dict[str, Any]:
    payload = review.payload() if isinstance(review, FlightReview) else dict(review)
    if str(payload.get("planner_authority")) != "NAVIGATOR" or str(payload.get("execution_authority")) != "NONE_REVIEW_ONLY":
        raise ValueError("flight review crossed authority boundary")
    return payload


def build_hud_payload(state: Mapping[str, Any], *, intent: Mapping[str, Any] | None = None,
                      review: FlightReview | Mapping[str, Any] | None = None,
                      candidate_details: list[Mapping[str, Any]] | None = None,
                      finalization: Mapping[str, Any] | None = None,
                      authorization: Mapping[str, Any] | None = None) -> dict[str, Any]:
    campaign = _campaign_projection(state)
    payload: dict[str, Any] = {
        "schema": HUD_SCHEMA, "campaign": campaign, "orientation": _orientation(campaign),
        "browser_authority": "PRESENTATION_ONLY", "calculation_authority": "ZERO",
        "state_authority": "ZERO", "execution_authority": "ZERO",
        "flight_intent": None, "flight_review": None, "navigator_candidate_details": [],
        "navigator_finalization": None, "flight_authorization": None,
    }
    if intent is not None: payload["flight_intent"] = _validate_intent_payload(intent)
    if review is not None: payload["flight_review"] = _review_payload(review)
    if candidate_details is not None: payload["navigator_candidate_details"] = [dict(row) for row in candidate_details]
    if finalization is not None:
        if str(finalization.get("execution_authority")) != "NONE_FINALIZED_NOT_AUTHORIZED":
            raise ValueError("finalization crossed execution boundary")
        payload["navigator_finalization"] = dict(finalization)
    if authorization is not None:
        if str(authorization.get("execution_authority")) != "REQUEST_ONLY_NAVIGATOR_MUST_REVALIDATE":
            raise ValueError("authorization contract invalid")
        payload["flight_authorization"] = dict(authorization)
    return payload


def _num(value: Any, digits: int = 3) -> str:
    if value is None: return "—"
    try: return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError): return escape(str(value))


def render_hud_html(payload: Mapping[str, Any]) -> str:
    campaign, orientation = payload["campaign"], payload["orientation"]
    intent, review = payload.get("flight_intent"), payload.get("flight_review")
    finalization, authorization = payload.get("navigator_finalization"), payload.get("flight_authorization")
    detail_rows = payload.get("navigator_candidate_details") or []
    detail_by_plan = {int(r.get("plan_number")): r for r in detail_rows if r.get("plan_number") is not None}

    intent_card = ""
    if isinstance(intent, Mapping):
        intent_card = ("<section class='panel intent-result'><div class='eyebrow'>Mara typed intent</div>"
            f"<div class='value compact'>{escape(str(intent.get('destination','—')))}</div>"
            f"<div class='small'>Priority {escape(str(intent.get('priority','—')))} · Origin {escape(str(intent.get('origin','—')))}</div>"
            "<div class='small'>Calculation ZERO · State ZERO · Execution ZERO</div></section>")

    navigator_request = ""
    if isinstance(intent, Mapping) and not isinstance(review, Mapping):
        navigator_request = ("<section class='panel navigator-request'><div class='eyebrow'>Navigator planning request</div>"
            "<div class='small'>Navigator calculates deterministic options against a temporary campaign copy. No campaign state changes.</div>"
            "<button id='navigator-options-submit' type='button'>ASK NAVIGATOR FOR OPTIONS</button>"
            "<div class='small status' id='navigator-options-status'></div></section>")

    review_card = ""
    if isinstance(review, Mapping):
        rows=[]
        for candidate in review.get("candidates",[]) or []:
            plan=int(candidate.get("plan_number")); detail=detail_by_plan.get(plan,{})
            total_h=None if detail.get("total_s") is None else float(detail["total_s"])/3600.0
            select = "" if isinstance(finalization, Mapping) else f"<button class='select-plan' data-plan='{plan}' type='button'>SELECT</button>"
            rows.append("<tr>"+f"<td>{plan}</td><td>{escape(str(candidate.get('metric','—')))}</td><td>{escape(str(candidate.get('torch','—')))}</td>"
                        +f"<td>{'—' if total_h is None else f'{total_h:.3f} h'}</td><td>{_num(detail.get('remass_used_t'))} t</td>"
                        +f"<td>{_num(detail.get('arrival_remass_t'))} t</td><td>{escape(str(detail.get('thermal','—')))}</td><td>{select}</td></tr>")
        review_card=("<section class='panel review'><div class='eyebrow'>Navigator flight review</div>"
            "<div class='guard'>REVIEW ONLY · EXECUTION AUTHORITY: NONE</div>"
            "<table><thead><tr><th>PLAN</th><th>METRIC</th><th>TORCH</th><th>TIME</th><th>REMASS USED</th><th>ARRIVAL REMASS</th><th>THERMAL</th><th></th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table><div class='small status' id='plan-select-status'></div></section>")

    final_card=""
    if isinstance(finalization, Mapping):
        plan=finalization.get("finalized_plan") or {}; sha=escape(str(finalization.get("finalized_plan_sha256","—")))
        auth_button="" if isinstance(authorization, Mapping) else "<button id='authorize-flight' type='button'>AUTHORIZE FLIGHT</button><div class='small status' id='authorize-status'></div>"
        final_card=("<section class='panel final-plan'><div class='eyebrow'>Navigator finalized plan</div>"
            "<div class='guard'>FINALIZED · NOT EXECUTED</div>"
            f"<div class='value compact'>PLAN {escape(str(finalization.get('selected_plan_number','—')))}</div>"
            f"<div class='small'>Metric {escape(str(plan.get('metric','—')))} · Torch {escape(str(plan.get('torch','—')))}</div>"
            f"<div class='small'>Final plan SHA <code>{sha}</code></div>"
            "<div class='small'>Campaign mutation: NONE · Execution authority: NONE until explicit authorization.</div>"+auth_button+"</section>")

    auth_card=""
    if isinstance(authorization, Mapping):
        auth_card=("<section class='panel authorization'><div class='eyebrow'>Human flight authorization</div>"
            "<div class='guard'>EXPLICIT AUTHORIZATION RECORDED · EXECUTION NOT REQUESTED</div>"
            f"<div class='value compact'>PLAN {escape(str(authorization.get('selected_plan_number','—')))} AUTHORIZED</div>"
            f"<div class='small'>Authorized by {escape(str(authorization.get('authorized_by','—')))} · Navigator must revalidate before any execution.</div>"
            "<div class='small'>There is deliberately no execute control in this qualification slice.</div></section>")

    location,epoch,ship_name,state_id=[escape(str(x)) for x in (campaign["location_token"],campaign["epoch_utc"],campaign["ship_name"],campaign["state_id"])]
    boundary=escape(str(campaign.get("kinematic_boundary_status") or "—")); summary=escape(str(orientation["summary"]))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'><title>LOOM · {ship_name}</title>
<style>:root{{color-scheme:dark;--bg:#07090d;--panel:#10151d;--line:#293241;--text:#e7edf4;--muted:#8f9bab}}*{{box-sizing:border-box}}body{{margin:0;background:#07090d;color:var(--text);font-family:Inter,system-ui,sans-serif}}main{{max-width:980px;margin:auto;padding:22px 16px 44px}}header{{margin-bottom:18px}}h1{{font-size:clamp(28px,8vw,58px);letter-spacing:.08em}}.eyebrow{{color:var(--muted);letter-spacing:.14em;font-size:11px;font-weight:700;text-transform:uppercase}}.guard{{border:1px solid var(--line);padding:8px 10px;color:var(--muted);font-size:11px;display:inline-block}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.panel{{background:#10151d;border:1px solid var(--line);padding:16px;min-height:126px;margin-top:12px}}.value{{font-size:clamp(23px,7vw,42px);margin-top:7px;overflow-wrap:anywhere}}.compact{{font-size:clamp(22px,6vw,34px)}}.small{{color:var(--muted);font-size:13px;margin-top:8px;line-height:1.45}}.orientation,.interaction{{grid-column:1/-1}}textarea{{width:100%;min-height:86px;background:#090d13;color:var(--text);border:1px solid var(--line);padding:12px;font:inherit}}button{{border:1px solid #536174;background:#17202b;color:var(--text);padding:11px 15px;margin-top:12px;font:inherit;font-weight:650}}button:disabled{{opacity:.55}}.review{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:820px}}th,td{{padding:9px 7px;border-top:1px solid var(--line);white-space:nowrap;text-align:left}}th{{color:var(--muted);font-size:10px}}code{{overflow-wrap:anywhere}}footer{{margin-top:14px;color:var(--muted);font-size:11px}}@media(max-width:640px){{.grid{{grid-template-columns:1fr}}.orientation,.interaction{{grid-column:auto}}}}</style></head><body><main>
<header><div class='eyebrow'>LOOM · EXPERIENCE ONE · 2226</div><h1>{ship_name}</h1><div class='guard'>PRESENTATION ONLY · Navigator authority</div></header>
<div class='grid'><section class='panel orientation'><div class='eyebrow'>Current orientation</div><div class='value'>{summary}</div></section><section class='panel'><div class='eyebrow'>Location</div><div class='value'>{location}</div><div class='small'>Boundary: {boundary}</div></section><section class='panel'><div class='eyebrow'>Campaign epoch</div><div class='value'>{epoch}</div><div class='small'>State {state_id}</div></section><section class='panel'><div class='eyebrow'>Remass</div><div class='value'>{_num(campaign.get('remass_t'))} t</div></section><section class='panel'><div class='eyebrow'>Wet mass</div><div class='value'>{_num(campaign.get('wet_mass_t'))} t</div></section><section class='panel interaction'><div class='eyebrow'>Tell Mara where you want to go</div><form id='flight-intent-form'><textarea id='flight-intent-text' placeholder='Take us to Neptune, balanced profile.' required></textarea><button id='flight-intent-submit'>INTERPRET INTENT</button><div class='small status' id='flight-intent-status'></div></form></section></div>
{intent_card}{navigator_request}{review_card}{final_card}{auth_card}
<footer>Browser calculation authority: ZERO · browser state authority: ZERO · browser execution authority: ZERO</footer>
<script>
const form=document.getElementById('flight-intent-form');form.addEventListener('submit',async e=>{{e.preventDefault();const t=document.getElementById('flight-intent-text').value.trim();if(!t)return;const r=await fetch('/intent.json',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{text:t}})}});const d=await r.json();if(!r.ok){{document.getElementById('flight-intent-status').textContent='Intent failed: '+(d.message||'error');return}}location.reload()}});
const nb=document.getElementById('navigator-options-submit');if(nb)nb.addEventListener('click',async()=>{{nb.disabled=true;document.getElementById('navigator-options-status').textContent='Navigator is calculating deterministic options…';const r=await fetch('/navigator-review.json',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:'{{}}'}});const d=await r.json();if(!r.ok){{document.getElementById('navigator-options-status').textContent=d.message||'review failed';nb.disabled=false;return}}location.reload()}});
document.querySelectorAll('.select-plan').forEach(b=>b.addEventListener('click',async()=>{{document.querySelectorAll('.select-plan').forEach(x=>x.disabled=true);document.getElementById('plan-select-status').textContent='Navigator is finalizing selected plan…';const r=await fetch('/navigator-finalize.json',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_number:Number(b.dataset.plan)}})}});const d=await r.json();if(!r.ok){{document.getElementById('plan-select-status').textContent=d.message||'finalization failed';document.querySelectorAll('.select-plan').forEach(x=>x.disabled=false);return}}location.reload()}}));
const ab=document.getElementById('authorize-flight');if(ab)ab.addEventListener('click',async()=>{{ab.disabled=true;document.getElementById('authorize-status').textContent='Recording explicit authorization…';const r=await fetch('/authorize.json',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{authorized:true}})}});const d=await r.json();if(!r.ok){{document.getElementById('authorize-status').textContent=d.message||'authorization failed';ab.disabled=false;return}}location.reload()}});
</script></main></body></html>"""
