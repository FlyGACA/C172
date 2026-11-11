"""The handbook plates (09_book_figures/handbook): the rules the book sets for its artwork, checked on plates.json and on
the finished SVGs in handbook/out/.

    python3 09_book_figures/tests/test_plates.py

The book's two editions share one file for each figure, so the artwork carries no words: parts are marked with numbered
callouts and each edition explains the numbers in a list under the figure. These checks keep that: every plate has exactly
as many callouts as its legend has items, numbered 1 to n, and its SVG holds no text. Standard library only.
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(os.path.dirname(HERE), "handbook")
OUT = os.path.join(PLATES, "out")
with open(os.path.join(PLATES, "plates.json"), encoding="utf-8") as f:
    SPEC = json.load(f)
with open(os.path.join(PLATES, "glyphs.json"), encoding="utf-8") as f:
    GLYPHS = json.load(f)
MARKER = SPEC["palette"]["marker"]


class PlateSpec(unittest.TestCase):
    def test_ids_are_the_books_file_names(self):
        ids = [p["id"] for p in SPEC["plates"]]
        self.assertEqual(len(ids), len(set(ids)), "an id is used twice")
        for p in SPEC["plates"]:
            self.assertRegex(p["id"], r"^(fig|plate)-\d\d-\d\d-[a-z0-9-]+$", p["id"])
            self.assertTrue(p["replaces"].startswith(p["id"]), p["id"])
            self.assertIn(p["background"], SPEC["backgrounds"], p["id"])
            self.assertEqual(len(p["canvas"]), 2)

    def test_every_plate_has_a_legend_and_a_picture(self):
        for p in SPEC["plates"]:
            self.assertTrue(p["legend"], p["id"])
            self.assertTrue(p["caption"] and p["desc"], p["id"])
            self.assertTrue("render" in p or "source" in p or "drawing" in p, f"{p['id']}: nothing to draw")

    def test_callouts_are_numbered_one_to_the_length_of_the_legend(self):
        for p in SPEC["plates"]:
            numbers = [o["n"] for o in p.get("overlays", []) if o["type"] == "marker"]
            if numbers:
                self.assertEqual(sorted(numbers), list(range(1, len(p["legend"]) + 1)), f"{p['id']}: callouts {sorted(numbers)} against {len(p['legend'])} legend items")

    def test_overlays_use_anchors_the_recipe_defines(self):
        for p in SPEC["plates"]:
            if "render" not in p:
                continue
            anchors = set(p["render"].get("anchors", {}))
            for o in p.get("overlays", []):
                for key in ("at", "from", "to"):
                    if key in o:
                        self.assertIn(o[key], anchors, f"{p['id']}: overlay {o} names the anchor {o[key]!r}, which the recipe does not define")
                for name in o.get("points", []):
                    self.assertIn(name, anchors, p["id"])
                if "polar" in o:
                    self.assertIn(o["polar"][0], anchors, p["id"])

    def test_glyphs_cover_the_digits_and_alpha(self):
        for ch in "0123456789α":
            self.assertIn(ch, GLYPHS["glyphs"])
            self.assertTrue(GLYPHS["glyphs"][ch]["d"].startswith("M"))


class FinishedPlates(unittest.TestCase):
    def finished(self):
        if not os.path.isdir(OUT):
            self.skipTest("no finished plates yet (python3 09_book_figures/handbook/build_plates.py)")
        return [(p, os.path.join(OUT, p["id"] + ".svg")) for p in SPEC["plates"] if os.path.exists(os.path.join(OUT, p["id"] + ".svg"))]

    def test_no_words_in_the_artwork(self):
        for p, path in self.finished():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("<text", text, f"{p['id']}: the artwork must carry no words")
            self.assertNotIn("<tspan", text, p["id"])

    def test_the_svg_declares_its_size_and_describes_itself(self):
        for p, path in self.finished():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            cw, ch = p["canvas"]
            self.assertIn(f'viewBox="0 0 {cw} {ch}"', text, p["id"])
            self.assertRegex(text, r"<title>[^<]+</title>", p["id"])
            self.assertRegex(text, r"<desc>[^<]+</desc>", p["id"])
            self.assertLess(os.path.getsize(path), 2_500_000, f"{p['id']} is heavier than a figure of a book should be")

    def test_as_many_callouts_drawn_as_the_legend_has_items(self):
        for p, path in self.finished():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            drawn = len(re.findall(rf'<circle cx="[\d.]+" cy="[\d.]+" r="13" fill="{re.escape(MARKER)}"/>', text))
            expected = 0 if p.get("colour_coded") else len(p["legend"])          # a plate explained by its colours alone has no callouts
            self.assertEqual(drawn, expected, f"{p['id']}: {drawn} callouts drawn, {expected} expected")

    def test_a_render_is_embedded_where_the_plate_is_one(self):
        for p, path in self.finished():
            if "render" in p or "source" in p:
                with open(path, encoding="utf-8") as f:
                    self.assertIn("data:image/jpeg;base64,", f.read(), p["id"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
