"""Keep feasible body spacing distinct from actual body collision."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from schematic_layout.geometry import Box
from schematic_layout.scene import Scene, Symbol
from schematic_layout.qa import check_scene


def pair(gap):
    bodies = [Box(40, 40, 42, 44), Box(42 + gap, 40, 44 + gap, 44)]
    return Scene(Box(0, 0, 297, 210),
                 symbols=[Symbol(f"X{i}", "Demo:Box", 1, [], body, [], [])
                          for i, body in enumerate(bodies, 1)])


class BodyClearanceReviewTests(unittest.TestCase):
    def test_separated_close_bodies_require_review_without_false_collision(self):
        report = check_scene(pair(0.3))
        self.assertEqual(report["status"], "REVIEW")
        self.assertEqual(report["counts"], {"body_clearance": 1})
        self.assertEqual(report["findings"][0]["severity"], "warning")

    def test_real_overlap_still_fails(self):
        report = check_scene(pair(-0.3))
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["counts"], {"body_overlap": 1})
        self.assertEqual(report["findings"][0]["severity"], "error")

    def test_original_spacing_threshold_is_preserved(self):
        self.assertEqual(check_scene(pair(1.269))["status"], "REVIEW")
        self.assertEqual(check_scene(pair(1.27))["status"], "PASS")

    def test_existing_coverage_gap_is_not_closed_by_spacing_review(self):
        scene = pair(0.3)
        scene.gaps.append("Synthetic unresolved artwork")
        report = check_scene(scene)
        self.assertEqual(report["status"], "INSUFFICIENT")
        self.assertEqual(report["counts"], {"body_clearance": 1})


if __name__ == "__main__":
    unittest.main()
