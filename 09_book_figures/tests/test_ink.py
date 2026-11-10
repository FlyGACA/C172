"""Tests for the ink-line rules of the book illustrations (numpy only, no Blender).
Run: python3 09_book_figures/tests/test_ink.py"""
import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blender"))
import ink  # noqa: E402


def scene(height=80, width=120):
    """An empty picture at double size: no parts, flat depth, every surface facing the camera."""
    part = np.zeros((height, width), dtype=np.int32)
    depth = np.full((height, width), 10.0, dtype=np.float32)
    facing = np.zeros((height, width, 3), dtype=np.float32)
    facing[..., 2] = 1.0
    return part, depth, facing


def lines(part, depth, facing, names, **settings):
    return ink.find_lines(part, depth, facing, part > 0, names, settings)


class LineRules(unittest.TestCase):
    def test_outline_follows_the_rim_and_nothing_else(self):
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        outline, boundary, fine = lines(part, depth, facing, ["body"])
        self.assertFalse(boundary.any()); self.assertFalse(fine.any())
        self.assertTrue(outline[20, 30:90].all() and outline[59, 30:90].all() and outline[20:60, 30].all() and outline[20:60, 89].all())
        self.assertFalse(outline[22:58, 32:88].any(), "no outline inside the part")
        self.assertFalse(outline[part == 0].any(), "the outline is drawn on the part, not on the background")

    def test_two_parts_meet_in_a_boundary_line(self):
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        part[30:50, 50:70] = 2                                  # a door in a fuselage
        outline, boundary, fine = lines(part, depth, facing, ["body", "door"])
        self.assertTrue(boundary[30:50, 49].all() and boundary[30:50, 50].all(), "both sides of the joint are marked")
        self.assertTrue(boundary[29, 50:70].all() and boundary[30, 50:70].all())
        self.assertFalse(boundary[35:45, 55:65].any())
        self.assertFalse((boundary & outline).any())
        self.assertFalse(fine.any())

    def test_slender_parts_are_drawn_with_fine_lines_only(self):
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        part[5:20, 60:62] = 2                                   # an aerial standing on the body, two pixels wide
        outline, boundary, fine = lines(part, depth, facing, ["body", "aerial"])
        aerial = part == 2
        self.assertTrue(fine[aerial].any())
        self.assertFalse(outline[aerial].any(), "a slender part must not get the heavy outline")
        self.assertFalse(boundary[aerial].any())
        self.assertFalse(boundary[20, 55:67].any(), "and no heavy line on the body where the aerial stands")
        self.assertTrue(outline[20, 30:55].all(), "the body keeps its own outline")

    def test_a_fold_is_a_fine_line_and_a_gentle_curve_is_not(self):
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        facing[:, 60:, :] = (1.0, 0.0, 0.0)                     # the surface turns through 90 degrees at column 60
        _, _, fine = lines(part, depth, facing, ["box"])
        self.assertTrue(fine[25:55, 59].all())
        self.assertFalse(fine[25:55, 40:58].any())
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        angle = np.linspace(0, np.pi / 2, 60)                   # the same 90 degrees spread over the whole part
        facing[:, 30:90, 0] = np.sin(angle); facing[:, 30:90, 2] = np.cos(angle)
        _, _, fine = lines(part, depth, facing, ["barrel"])
        self.assertFalse(fine.any())

    def test_a_part_hiding_part_of_itself_is_a_fine_line_but_a_slope_is_not(self):
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        depth[:, 60:] = 10.5                                    # half a metre further away from column 60 on
        _, _, fine = lines(part, depth, facing, ["fairing"])
        self.assertTrue(fine[25:55, 59].all())
        part, depth, facing = scene()
        part[20:60, 30:90] = 1
        depth[:, :] = 10.0 + 0.08 * np.arange(120, dtype=np.float32)[None, :]      # a surface seen at a grazing angle
        _, _, fine = lines(part, depth, facing, ["wing"])
        self.assertFalse(fine.any())

    def test_parts_named_in_no_lines_meet_without_a_line(self):
        part, depth, facing = scene()
        part[20:60, 30:60] = 1
        part[20:60, 60:90] = 2
        _, boundary, _ = lines(part, depth, facing, ["ENGINE.case_L", "ENGINE.case_R"], no_lines=["ENGINE."])
        self.assertFalse(boundary.any())
        _, boundary, _ = lines(part, depth, facing, ["ENGINE.case_L", "ENGINE.case_R"])
        self.assertTrue(boundary[25:55, 59:61].all())


class Strokes(unittest.TestCase):
    def test_grow_and_halve(self):
        dot = np.zeros((21, 21), dtype=bool); dot[10, 10] = True
        self.assertTrue((ink.grow(dot, 0) == dot).all())
        grown = ink.grow(dot, 4)
        self.assertTrue(grown[10, 6] and grown[10, 14] and grown[6, 10] and grown[14, 10])
        self.assertFalse(grown[10, 5] or grown[5, 10])
        self.assertFalse(grown[6, 6], "an octagon, not a square")
        block = np.zeros((4, 4), dtype=bool); block[0:2, 0:2] = True; block[2, 2] = True
        self.assertEqual(ink.halve(block).tolist(), [[1.0, 0.0], [0.0, 0.25]])

    def test_line_weights_are_ordered_and_scale_with_the_picture(self):
        part, depth, facing = scene(200, 400)
        part[40:160, 60:340] = 1
        part[80:120, 150:250] = 2
        facing[:, 300:, :] = (1.0, 0.0, 0.0)
        coverage = ink.draw_ink(part, depth, facing, part > 0, ["body", "door"], {"outer_px": 4.6, "part_px": 2.4, "fine_px": 1.5}, width=2400)
        self.assertEqual(coverage.shape, (100, 200))
        self.assertTrue(0.0 <= coverage.min() and coverage.max() <= 1.0)
        outline = coverage[50, 20:40].sum()        # across the left rim, clear of everything else
        joint = coverage[50, 65:85].sum()          # across the left edge of the door
        fold = coverage[30, 140:160].sum()         # across the fold, above the door
        self.assertAlmostEqual(outline, 4.6, delta=0.8)
        self.assertAlmostEqual(joint, 2.4, delta=0.8)
        self.assertLess(fold, joint); self.assertLess(joint, outline)
        self.assertGreater(fold, 0.5)
        half = ink.draw_ink(part, depth, facing, part > 0, ["body", "door"], {"outer_px": 4.6, "part_px": 2.4, "fine_px": 1.5}, width=1200)
        self.assertLess(half[50, 20:40].sum(), outline, "a smaller picture gets proportionally thinner lines")


class Framing(unittest.TestCase):
    """The automatic camera has to fit a subject into the shorter side of the picture."""

    def setUp(self):
        import framing
        self.f = framing

    def fits(self, radius, fov, aspect, distance):
        """Does a sphere at `distance` fit both sides of a perspective picture?"""
        long_half = math.radians(fov) / 2
        short_half = math.atan(math.tan(long_half) * min(aspect, 1 / aspect))
        return distance * math.sin(long_half) >= radius - 1e-9 and distance * math.sin(short_half) >= radius - 1e-9

    def test_square_picture_uses_the_field_of_view_as_given(self):
        self.assertAlmostEqual(self.f.perspective_distance(1.0, 24, 1.0), 1 / math.sin(math.radians(12)), places=9)

    def test_tall_subject_fits_a_wide_picture_and_a_wide_subject_a_tall_one(self):
        for aspect in (4.0, 16 / 9, 4 / 3, 1.0, 3 / 4, 0.25):
            distance = self.f.perspective_distance(1.0, 24, aspect)
            self.assertTrue(self.fits(1.0, 24, aspect, distance), aspect)
            self.assertFalse(self.fits(1.0, 24, aspect, distance * 0.98), aspect)      # and no further away than needed

    def test_margin_moves_the_camera_back_in_proportion(self):
        self.assertAlmostEqual(self.f.perspective_distance(2.0, 30, 1.5, 1.2), 1.2 * self.f.perspective_distance(2.0, 30, 1.5), places=9)

    def test_orthographic_scale_covers_the_sphere_on_the_short_side(self):
        for aspect in (4.0, 1.5, 1.0, 0.5):
            scale = self.f.orthographic_scale(1.0, aspect)
            self.assertAlmostEqual(scale * min(aspect, 1 / aspect), 2.0, places=9)     # the short side is exactly the diameter


if __name__ == "__main__":
    unittest.main()
