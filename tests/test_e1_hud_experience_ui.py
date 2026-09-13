import unittest

from engineering.experience_one.e1_hud_experience_ui import render_experience_html


class E1HUDExperienceUITests(unittest.TestCase):
    def test_zero_instruction_surface_leads_with_world_not_engineering(self):
        diagnostic = """<html><body><main>
<header><div class='eyebrow'>LOOM · EXPERIENCE ONE · 2226</div><h1>WAYFARER</h1><div class='guard'>PRESENTATION ONLY · Navigator authority</div></header>
<div class='grid'><section class='panel orientation'><div class='eyebrow'>Current orientation</div><div class='value'>Wayfarer is at CERES at campaign epoch 2226-08-22T01:32:00Z.</div></section>
<section class='panel'><div class='eyebrow'>Location</div><div class='value'>CERES</div></section>
<section class='panel'><div class='eyebrow'>Campaign epoch</div><div class='value'>2226-08-22T01:32:00Z</div></section>
<section class='panel'><div class='eyebrow'>Remass</div><div class='value'>250.000 t</div></section>
<section class='panel'><div class='eyebrow'>Wet mass</div><div class='value'>1,158.500 t</div></section>
<section class='panel interaction'><div class='eyebrow'>Tell Mara where you want to go</div><form id='flight-intent-form'></form></section></div>
<footer>Browser calculation authority: ZERO</footer></main></body></html>"""
        html = render_experience_html(diagnostic, location="CERES", ship_name="WAYFARER")
        self.assertIn("You’re aboard Wayfarer.", html)
        self.assertIn("What do you want to do?", html)
        self.assertIn("Ask Mara", html)
        self.assertIn("Ship &amp; system details", html)
        self.assertIn("flight-intent-form", html)
        self.assertIn("Browser calculation authority: ZERO", html)
        self.assertLess(html.index("You’re aboard Wayfarer."), html.index("Campaign epoch"))

    def test_neptune_arrival_reads_as_world_state(self):
        html = render_experience_html("<html><body><main><header></header><div class='grid'></div><footer>x</footer></main></body></html>", location="NEPTUNE_SYSTEM", ship_name="WAYFARER")
        self.assertIn("Neptune system", html)
        self.assertNotIn("NEPTUNE_SYSTEM</strong>", html)

    def test_mobile_navigator_review_is_cardified_without_dropping_fields(self):
        diagnostic = """<html><head></head><body><main><header></header><div class='grid'></div>
<section class='panel review'><table><thead><tr><th>PLAN</th><th>METRIC</th><th>TORCH</th><th>TIME</th><th>REMASS USED</th><th>ARRIVAL REMASS</th><th>THERMAL</th><th></th></tr></thead>
<tbody><tr><td>1</td><td>HARD</td><td>CRUISE</td><td>8.222 h</td><td>13.397 t</td><td>236.603 t</td><td>SUSTAINABLE</td><td><button>SELECT</button></td></tr></tbody></table></section>
<footer>x</footer></main></body></html>"""
        html = render_experience_html(diagnostic, location="CERES", ship_name="WAYFARER")
        self.assertIn(".review thead{display:none}", html)
        self.assertIn(".review td:nth-child(1)::before{content:'Plan'}", html)
        self.assertIn(".review td:nth-child(6)::before{content:'Arrival remass'}", html)
        self.assertIn("8.222 h", html)
        self.assertIn("236.603 t", html)
        self.assertIn("SELECT", html)


if __name__ == "__main__":
    unittest.main()
