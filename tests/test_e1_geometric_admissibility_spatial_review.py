import unittest

from engineering.pixel.spatial_review import build_geometric_admissibility_relevance_review


class GeometricAdmissibilitySpatialReviewTests(unittest.TestCase):
    def test_review_explains_parent_problem_in_plain_language(self):
        html = build_geometric_admissibility_relevance_review()
        self.assertIn("Problem statement", html)
        self.assertIn("Why we care", html)
        self.assertIn("How we are trying to solve it", html)
        self.assertIn("where Wayfarer can safely return to ordinary-space flight near Neptune", html)

    def test_review_contains_legend_and_definitions(self):
        html = build_geometric_admissibility_relevance_review()
        self.assertIn("Legend", html)
        self.assertIn("Definitions", html)
        self.assertIn("Geometric Admissibility", html)
        self.assertIn("tidal shear", html)
        self.assertIn("stress-energy", html)
        self.assertIn("fail closed", html)

    def test_review_makes_priority_and_hold_state_visible(self):
        html = build_geometric_admissibility_relevance_review()
        self.assertIn("NEXT ENGINEERING", html)
        self.assertIn("HOLD — COUPLING NOT EARNED", html)
        self.assertIn("PHYSICS BLOCKED", html)
        self.assertIn("Hill radius / SOI are context, not collapse boundaries", html)

    def test_review_does_not_claim_a_numeric_admissibility_score(self):
        html = build_geometric_admissibility_relevance_review()
        self.assertIn("NO NUMERIC IMPORTANCE SCORE", html)
        self.assertNotIn("admissibility score =", html.lower())


if __name__ == "__main__":
    unittest.main()
