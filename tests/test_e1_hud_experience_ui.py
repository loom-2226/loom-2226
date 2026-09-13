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


if __name__ == "__main__":
    unittest.main()
