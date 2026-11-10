"""Pure-Python tests for the geometry profiles and texture helpers (no Blender needed).
Run: python3 -m pytest 08_realistic_digital_twin/tests  or  python3 08_realistic_digital_twin/tests/test_profiles.py"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blender"))
from c172 import profiles, units  # noqa: E402


class ProfileTests(unittest.TestCase):
    def test_naca2412_shape(self):
        pts = profiles.naca4("2412", 40)
        self.assertEqual(len(pts), 80)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        self.assertAlmostEqual(min(xs), 0.0, places=6)
        self.assertAlmostEqual(max(xs), 1.0, places=6)
        self.assertAlmostEqual(max(ys) - min(ys), 0.12, delta=0.012)   # 12 % thick
        self.assertGreater(sum(ys) / len(ys), 0.0)                      # cambered upward

    def test_symmetric_airfoil(self):
        pts = profiles.naca4("0012", 40)
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(max(ys), -min(ys), places=6)

    def test_split_airfoil_closed_loops(self):
        box, surf = profiles.split_airfoil(profiles.naca4("2412", 40), 0.75)
        self.assertGreater(len(box), 20); self.assertGreater(len(surf), 10)
        self.assertLess(max(p[0] for p in box), 0.78)
        self.assertGreater(min(p[0] for p in surf), 0.70)

    def test_resample_preserves_perimeter(self):
        loop = profiles.naca4("2412", 60)
        r = profiles.resample_loop(loop, 48)
        def per(p): return sum(math.hypot(p[(i + 1) % len(p)][0] - p[i][0], p[(i + 1) % len(p)][1] - p[i][1]) for i in range(len(p)))
        self.assertAlmostEqual(per(loop), per(r), delta=0.02)

    def test_superellipse_bounds(self):
        ring = profiles.superellipse(0.54, 0.5, 0.7, 1.3, 2.6, 2.4, 40)
        self.assertEqual(len(ring), 40)
        self.assertAlmostEqual(max(p[0] for p in ring), 0.54, places=6)
        self.assertAlmostEqual(min(p[1] for p in ring), 0.8, places=6)
        self.assertAlmostEqual(max(p[1] for p in ring), 2.0, places=6)

    def test_interp_table(self):
        t = [(0, 1.0, 10.0), (10, 2.0, 20.0)]
        self.assertEqual(list(profiles.interp_table(t, -1)), [1.0, 10.0])
        self.assertEqual(list(profiles.interp_table(t, 11)), [2.0, 20.0])
        mid = profiles.interp_table(t, 5)
        self.assertAlmostEqual(mid[0], 1.5); self.assertAlmostEqual(mid[1], 15.0)


    def test_interp_linear(self):
        t = [(0, 0.0), (10, 5.0), (20, 5.0)]
        self.assertEqual(profiles.interp_linear(t, -3), [0.0])
        self.assertEqual(profiles.interp_linear(t, 25), [5.0])
        self.assertAlmostEqual(profiles.interp_linear(t, 4)[0], 2.0)
        self.assertAlmostEqual(profiles.interp_linear(t, 15)[0], 5.0)

    def test_interp_pchip_passes_through_rows_and_never_overshoots(self):
        # an outline with a ramp and a flat: a smoothstep or a natural spline would either flatten at
        # every row or overshoot the flat; the outline of the hull must do neither
        t = [(0, 0.0, 9.0), (10, 10.0, 9.0), (20, 20.0, 7.0), (30, 20.0, 2.0), (40, 20.0, 1.0)]
        for row in t:
            got = profiles.interp_pchip(t, row[0])
            self.assertAlmostEqual(got[0], row[1]); self.assertAlmostEqual(got[1], row[2])
        samples = [profiles.interp_pchip(t, x / 4) for x in range(0, 161)]
        first = [v[0] for v in samples]; second = [v[1] for v in samples]
        self.assertTrue(all(b >= a - 1e-9 for a, b in zip(first, first[1:])), "rising column must stay monotonic")
        self.assertTrue(all(b <= a + 1e-9 for a, b in zip(second, second[1:])), "falling column must stay monotonic")
        self.assertLessEqual(max(first), 20.0 + 1e-9)
        self.assertAlmostEqual(profiles.interp_pchip(t, 5)[0], 5.0, delta=0.05)      # straight where the rows are in line
        self.assertEqual(profiles.interp_pchip(t, -5), [0.0, 9.0])
        self.assertEqual(profiles.interp_pchip(t, 99), [20.0, 1.0])

    def test_interp_pchip_is_smooth_through_a_row(self):
        t = [(0, 0.0), (10, 4.0), (20, 12.0), (30, 14.0)]
        before = (profiles.interp_pchip(t, 10)[0] - profiles.interp_pchip(t, 9.99)[0]) / 0.01
        after = (profiles.interp_pchip(t, 10.01)[0] - profiles.interp_pchip(t, 10)[0]) / 0.01
        self.assertAlmostEqual(before, after, delta=0.02)                          # no kink, unlike straight segments
        self.assertGreater(before, 0.3)                                            # and no flat spot, unlike smoothstep


class UnitsTests(unittest.TestCase):
    def test_poh_dimensions(self):
        self.assertAlmostEqual(units.SPAN, 10.922, places=3)            # 35 ft 10 in
        self.assertAlmostEqual(units.ref("length_m"), 8.204, places=3)  # 26 ft 11 in
        self.assertAlmostEqual(units.PROP_R * 2, 1.905, places=3)       # 75 in
        self.assertAlmostEqual(units.TAIL_END_Y - units.SPINNER_TIP_Y, units.ref("length_m"), places=3)

    def test_stance_and_ground_frame(self):
        self.assertAlmostEqual(units.wl(0), units.GROUND_Z)
        self.assertAlmostEqual(units.wl(10) - units.wl(0), 0.254)
        # the crank axis is one propeller radius plus the published clearance above the ground
        self.assertAlmostEqual((units.PROP_Z - units.GROUND_Z - units.PROP_R) / units.IN, 11.75, places=6)
        # the axle stations reproduce the published wheel base
        self.assertAlmostEqual(units.MAIN_AXLE_Y - units.NOSE_AXLE_Y, units.ref("wheel_base_m"), places=6)
        # at rest the aircraft is lower than the POH maximum height (nose strut depressed)
        self.assertLess(units.ref("static_height_m"), units.ref("height_m"))

    def test_every_reference_has_status(self):
        for k, v in units.REF.items():
            self.assertIn(v["status"], ("measured", "poh", "type_data", "estimated"), k)
            self.assertTrue(v["ref"], k)

    def test_wing_area_from_planform(self):
        # root chord constant to the taper start then linear to the tip: should solve ~174 ft²
        s1 = units.TAPER_START; s2 = units.SEMISPAN
        area = 2 * (units.ROOT_CHORD * s1 + (units.ROOT_CHORD + units.TIP_CHORD) / 2 * (s2 - s1))
        self.assertAlmostEqual(area / 0.09290304, 174, delta=4)


if __name__ == "__main__":
    unittest.main()
