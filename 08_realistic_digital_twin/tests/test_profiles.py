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
        self.assertAlmostEqual(units.ref("wingspan_strobes_m"), 10.973, places=3)   # 36 ft over the strobe lights
        self.assertAlmostEqual(units.TRACK, 2.553, places=3)            # 8 ft 4½ in
        # the overall length is measured with the aircraft on its wheels: spinner tip to the top of the rudder
        nose = units.to_ground((0.0, units.SPINNER_TIP_Y, units.PROP_Z))
        tail = units.to_ground((0.0, units.TAIL_END_Y, units.wl(91.0)))
        self.assertAlmostEqual(tail[1] - nose[1], units.ref("length_m"), delta=0.02)

    def test_stance_and_ground_frame(self):
        self.assertAlmostEqual(units.wl(0), units.GROUND_Z)
        self.assertAlmostEqual(units.wl(10) - units.wl(0), 0.254)
        # the axle stations reproduce the published wheel base
        self.assertAlmostEqual(units.MAIN_AXLE_Y - units.NOSE_AXLE_Y, units.ref("wheel_base_m"), places=6)
        # the ground passes under the main wheels where the tables say, and rises aft in the build frame
        self.assertAlmostEqual(units.ground_wl(units.GROUND_PIVOT_FS), -units.GROUND_DROP_IN)
        self.assertGreater(units.ground_wl(200.0), units.ground_wl(0.0))
        # build frame <-> scene: a round trip, the ground on z = 0, the main wheel station unchanged
        point = (0.7, units.fs(120.0), units.wl(55.0))
        back = units.from_ground(units.to_ground(point))
        for a, b in zip(point, back):
            self.assertAlmostEqual(a, b, places=9)
        for station in (-7.0, 58.0, 230.0):
            self.assertAlmostEqual(units.to_ground((0.0, units.fs(station), units.ground_z(units.fs(station))))[2], 0.0, places=9)
        self.assertAlmostEqual(units.to_ground((0.0, units.MAIN_AXLE_Y, units.ground_z(units.MAIN_AXLE_Y)))[1], units.MAIN_AXLE_Y, places=9)

    def test_published_height_and_propeller_clearance_belong_together(self):
        """POH Fig 1-1 gives the maximum height "with nose gear depressed" and a propeller clearance of
        11¾ in. At rest the model has more clearance and less height; pushing the nose down until the
        clearance is 11¾ in must bring the tail up to the published 8 ft 9½ in."""
        hub = units.to_ground((0.0, units.fs(-36.4), units.PROP_Z))
        top = units.to_ground((0.0, units.fs(253.2), units.wl(95.2) + 0.065))        # top of the beacon
        main = units.MAIN_AXLE_Y
        clearance = hub[2] - units.PROP_R
        self.assertGreater(clearance, units.ref("prop_clearance_m") + 0.08)           # at rest: about 17 in
        self.assertLess(top[2], units.ref("height_m") - 0.15)                         # at rest: about 7 ft 10 in
        lo, hi = 0.0, 0.2
        for _ in range(60):                                                           # nose-down angle that leaves 11¾ in
            phi = (lo + hi) / 2
            z = (hub[1] - main) * math.sin(phi) + hub[2] * math.cos(phi)
            lo, hi = (phi, hi) if z - units.PROP_R > units.ref("prop_clearance_m") else (lo, phi)
        height = (top[1] - main) * math.sin(phi) + top[2] * math.cos(phi)
        self.assertAlmostEqual(height, units.ref("height_m"), delta=0.03)
        drop = units.ref("wheel_base_m") * math.sin(phi)                              # how far the nose wheel has to go down
        self.assertTrue(0.06 < drop < 0.12, drop)

    def test_every_reference_has_status(self):
        for k, v in units.REF.items():
            self.assertIn(v["status"], ("measured", "poh", "type_data", "estimated"), k)
            self.assertTrue(v["ref"], k)

    def test_wing_area_from_planform(self):
        # root chord constant to the taper start then linear to the tip: should solve ~174 ft²
        s1 = units.TAPER_START; s2 = units.SEMISPAN
        area = 2 * (units.ROOT_CHORD * s1 + (units.ROOT_CHORD + units.TIP_CHORD) / 2 * (s2 - s1))
        self.assertAlmostEqual(area / 0.09290304, 174, delta=1)
        # published chords: 64 in at the root, 44.5 in at the tip rib
        self.assertAlmostEqual(units.ROOT_CHORD / units.IN, 64.0, places=6)
        self.assertAlmostEqual((units.ROOT_CHORD - units.TAPER_PER_M * (units.TIP_RIB - units.TAPER_START)) / units.IN, 44.5, places=6)


class SheetGeometryTests(unittest.TestCase):
    """Plane geometry behind the sheet-metal parts of the detail packs (c172/detail/geom2d.py)."""

    def setUp(self):
        from c172.detail import geom2d
        self.g = geom2d
        self.rib = [(0.0, 0.0), (0.4, -0.02), (0.8, 0.0), (0.8, 0.10), (0.4, 0.14), (0.0, 0.10)]

    def test_area_sign_and_orientation(self):
        square = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.assertAlmostEqual(self.g.area(square), 1.0)
        self.assertAlmostEqual(self.g.area(list(reversed(square))), -1.0)
        self.assertGreater(self.g.area(self.g.counter_clockwise(list(reversed(square)))), 0)

    def test_inset_moves_every_edge_inward(self):
        square = [(0, 0), (1, 0), (1, 1), (0, 1)]
        inner = self.g.inset(square, 0.1)
        self.assertAlmostEqual(self.g.area(inner), 0.64, places=6)
        self.assertAlmostEqual(self.g.area(self.g.inset(square, -0.1)), 1.44, places=6)
        self.assertAlmostEqual(self.g.area(self.g.inset(list(reversed(square)), 0.1)), 0.64, places=6)   # either winding

    def test_lightening_holes_stay_inside_the_web(self):
        margin = 0.02
        holes = self.g.lightening_holes(self.rib, 0.05, 0.75, 4, margin)
        self.assertEqual(len(holes), 4)
        for hole in holes:
            for point in hole:
                self.assertTrue(self.g.inside(point, self.rib))
                low, high = self.g.height_at(self.rib, point[0])
                self.assertGreater(point[1] - low, margin * 0.9)
                self.assertGreater(high - point[1], margin * 0.9)
        centres = [sum(p[0] for p in hole) / len(hole) for hole in holes]
        radii = [max(p[0] for p in hole) - c for hole, c in zip(holes, centres)]
        for a, b, ra, rb in zip(centres, centres[1:], radii, radii[1:]):
            self.assertGreater(b - a - ra - rb, margin * 0.9)                    # metal left between two holes

    def test_no_hole_where_the_web_is_too_shallow(self):
        strip = [(0.0, 0.0), (1.0, 0.0), (1.0, 0.03), (0.0, 0.03)]
        self.assertEqual(self.g.lightening_holes(strip, 0.05, 0.95, 5, 0.02), [])

    def test_slot_and_rounded_rectangle_extent(self):
        slot = self.g.slot(0.0, 0.0, 0.10, 0.02)
        self.assertAlmostEqual(max(p[0] for p in slot) - min(p[0] for p in slot), 0.10, places=6)
        self.assertAlmostEqual(max(p[1] for p in slot) - min(p[1] for p in slot), 0.02, places=6)
        box = self.g.rounded_rectangle(1.0, 2.0, 0.3, 0.2, 0.05)
        self.assertAlmostEqual(max(p[0] for p in box) - min(p[0] for p in box), 0.3, places=6)
        self.assertAlmostEqual(max(p[1] for p in box) - min(p[1] for p in box), 0.2, places=6)

    def test_resample_and_spacing(self):
        line = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
        points = self.g.resample(line, 5)
        self.assertEqual(points[0], (0.0, 0.0)); self.assertEqual(points[-1], (1.0, 1.0))
        steps = [math.dist(a, b) for a, b in zip(points, points[1:])]
        self.assertAlmostEqual(max(steps), 0.5, places=6)
        row = self.g.spaced(0.0, 1.0, 0.24, margin=0.02)
        self.assertAlmostEqual(row[0], 0.02); self.assertAlmostEqual(row[-1], 0.98)
        self.assertEqual(len(row), 5)


if __name__ == "__main__":
    unittest.main()
