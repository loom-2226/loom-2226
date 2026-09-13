from __future__ import annotations

"""Small presentation-only convergence layer for the Experience One HUD.

This module deliberately does not parse requests, calculate, plan, authorize,
execute, or read/write campaign state. It only rearranges already-rendered HUD
HTML so first contact reads like a world rather than a qualification console.
"""

from html import escape


def _human_location(token: str) -> str:
    token = str(token or "").strip().upper()
    if token == "NEPTUNE_SYSTEM":
        return "Neptune system"
    if token == "CERES":
        return "Ceres"
    return token.replace("_", " ").title() or "your current location"


def render_experience_html(diagnostic_html: str, *, location: str, ship_name: str) -> str:
    """Progressively disclose diagnostics while preserving all existing controls.

    The underlying presenter remains the contract/diagnostic rendering authority.
    This function adds no browser authority and does not alter endpoint behavior.
    """
    html = str(diagnostic_html)
    ship = escape(str(ship_name or "Wayfarer").title())
    place = escape(_human_location(location))

    hero = (
        "<section class='e1-world-hero'>"
        "<div class='eyebrow'>LOOM · 2226</div>"
        f"<h1>You’re aboard {ship}.</h1>"
        f"<p class='e1-place'>You are at <strong>{place}</strong>.</p>"
        "<p class='e1-prompt'>What do you want to do?</p>"
        "</section>"
    )
    html = html.replace("<header>", "<header class='e1-engineering-header'>", 1)
    marker = "</header>"
    if marker in html:
        html = html.replace(marker, marker + hero, 1)

    # Keep the interaction visible and conversational; qualification/state cards
    # become progressive disclosure without deleting any evidence or authority copy.
    html = html.replace("Tell Mara where you want to go", "Ask Mara", 1)
    html = html.replace("INTERPRET INTENT", "ASK MARA", 1)

    grid_start = "<div class='grid'>"
    start = html.find(grid_start)
    if start >= 0:
        interaction_close = "</section></div>"
        real_end = html.find(interaction_close, start)
        if real_end >= 0:
            real_end += len(interaction_close)
            body = html[start:real_end]
            html = html[:start] + "<details class='e1-details'><summary>Ship &amp; system details</summary>" + body + "</details>" + html[real_end:]

    css = """<style id='e1-experience-css'>
.e1-engineering-header{display:none}
.e1-world-hero{padding:18px 2px 8px;margin-bottom:10px}
.e1-world-hero h1{font-size:clamp(38px,10vw,68px);line-height:1.02;letter-spacing:-.025em;margin:12px 0 18px;text-transform:none}
.e1-place{font-size:clamp(20px,5.5vw,30px);margin:0 0 8px;color:var(--text)}
.e1-prompt{font-size:clamp(18px,5vw,26px);margin:26px 0 8px;color:var(--text)}
.e1-details{margin-top:18px;border-top:1px solid var(--line);padding-top:14px}
.e1-details>summary{cursor:pointer;color:var(--muted);font-size:12px;letter-spacing:.08em;text-transform:uppercase;padding:10px 0}
.e1-details>.grid{margin-top:8px}
.e1-details .interaction{display:block}
.e1-details:not([open]) .grid{display:none}
.intent-result,.navigator-request,.review,.final-plan,.authorization,.execution-request,.execution{margin-top:14px}
@media(max-width:640px){
main{padding-top:18px}
.e1-world-hero{padding-top:8px}
.review{overflow:visible}
.review table{min-width:0;width:100%;display:block}
.review thead{display:none}
.review tbody{display:block}
.review tr{display:block;border:1px solid var(--line);margin:10px 0;padding:8px 10px;background:#0c1118}
.review td{display:grid;grid-template-columns:7.3rem minmax(0,1fr);gap:10px;align-items:center;border-top:1px solid var(--line);padding:8px 0;white-space:normal}
.review td:first-child{border-top:0}
.review td::before{color:var(--muted);font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.review td:nth-child(1)::before{content:'Plan'}
.review td:nth-child(2)::before{content:'Metric'}
.review td:nth-child(3)::before{content:'Torch'}
.review td:nth-child(4)::before{content:'Time'}
.review td:nth-child(5)::before{content:'Remass used'}
.review td:nth-child(6)::before{content:'Arrival remass'}
.review td:nth-child(7)::before{content:'Thermal'}
.review td:nth-child(8)::before{content:'Action'}
.review td:nth-child(8) button{width:100%;margin-top:0}
}
</style>"""
    html = html.replace("</head>", css + "</head>", 1)

    # Mara is the obvious first action even while engineering cards are collapsed.
    interaction_marker = "<section class='panel interaction'>"
    interaction_start = html.find(interaction_marker)
    if interaction_start >= 0:
        interaction_end = html.find("</section>", interaction_start)
        if interaction_end >= 0:
            interaction_end += len("</section>")
            interaction = html[interaction_start:interaction_end]
            # Avoid duplicate DOM ids: move, don't copy, the existing interaction.
            html = html[:interaction_start] + html[interaction_end:]
            hero_end = html.find("</section>", html.find("e1-world-hero"))
            if hero_end >= 0:
                hero_end += len("</section>")
                html = html[:hero_end] + interaction + html[hero_end:]

    return html
