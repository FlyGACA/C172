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
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(os.path.dirname(HERE), "handbook")
OUT = os.path.join(PLATES, "out")
sys.path.insert(0, PLATES)
from book_rules import problems_of_jpeg, problems_of_svg      # noqa: E402
import plates_spec                                            # noqa: E402  (the first six plates of plates.json and one module per figure in figs/)
from reskin import sprites_used                               # noqa: E402  (the pictures of the aeroplane a re-skinned plate lays on its old drawing)
SPEC = plates_spec.load()
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
            self.assertTrue("render" in p or "source" in p or "layers" in p or "drawing" in p or "reskin" in p, f"{p['id']}: nothing to draw")

    def test_callouts_are_numbered_one_to_the_length_of_the_legend(self):
        for p in SPEC["plates"]:
            numbers = [o["n"] for o in p.get("overlays", []) if o["type"] == "marker"]
            if numbers:
                self.assertEqual(sorted(numbers), list(range(1, len(p["legend"]) + 1)), f"{p['id']}: callouts {sorted(numbers)} against {len(p['legend'])} legend items")

    def test_overlays_use_anchors_the_recipe_defines(self):
        for p in SPEC["plates"]:
            if "render" in p:
                recipes = {"": p["render"]}
            elif "layers" in p:
                recipes = {layer["name"] + ".": layer["render"] for layer in p["layers"] if "render" in layer}
            else:
                continue
            anchors = {prefix + k for prefix, r in recipes.items() for k in r.get("anchors", {})}
            curves = {prefix + k for prefix, r in recipes.items() for k in r.get("curves", {})}
            for o in p.get("overlays", []):
                for key in ("at", "from", "to"):
                    if key in o and isinstance(o[key], str):                  # (a list is a point of the canvas)
                        self.assertIn(o[key], anchors, f"{p['id']}: overlay {o} names the anchor {o[key]!r}, which the recipe does not define")
                for name in o.get("points", []):
                    if isinstance(name, str) and o["type"] != "outline":
                        self.assertIn(name, anchors, p["id"])
                if "polar" in o:
                    self.assertIn(o["polar"][0], anchors, p["id"])
                if o["type"] == "path":
                    self.assertIn(o["curve"], curves, f"{p['id']}: overlay {o} names a curve the recipe does not define")
                if o["type"] == "marker" and "on" in o:
                    self.assertIn(o["on"]["curve"], curves, f"{p['id']}: marker {o['n']} sits on a curve the recipe does not define")
                if o["type"] in ("glowdot", "icon", "text", "wedge", "sprite") and isinstance(o.get("at"), str):
                    self.assertIn(o["at"], anchors, f"{p['id']}: {o['type']} at the anchor {o['at']!r}, which the recipe does not define")
            for g in p.get("ground", []):
                self.assertIn(g["type"], ("wedge", "dots", "band", "contact"), p["id"])
                if isinstance(g.get("at"), str):
                    self.assertIn(g["at"], anchors, f"{p['id']}: ground item {g} names an anchor the recipe does not define")

    def test_a_reskin_lays_only_sprites_the_catalogue_makes(self):
        """build_plates.py waits for the renders of the sprites a re-skinned plate uses, and for no others (so one picture not rendered yet holds up only the plates that
        lay it); every one of them must be a sprite that figs/sprites.py or a cloud that figs/clouds.py makes, or the plate could never be built."""
        made = {s["id"] for s in SPEC["sprites"]} | {c["id"] for c in SPEC["clouds"]}
        for p in SPEC["plates"]:
            if "reskin" in p:
                used = {name for name in sprites_used(p) if not name.startswith("terrain-")}          # (the ground of figs/terrain.py is made when the plate's module is read)
                self.assertLessEqual(used, made, f"{p['id']}: lays a sprite that figs/sprites.py and figs/clouds.py do not make")
        self.assertIn("sprite-spin", sprites_used(next(p for p in SPEC["plates"] if p["id"] == "fig-06-02-spin-phases")))
        self.assertNotIn("sprite-spin", sprites_used(next(p for p in SPEC["plates"] if p["id"] == "fig-26-02-normal-takeoff-landing")))

    def test_each_plate_names_the_file_the_book_takes(self):
        """A render becomes plate-NN-NN-name.jpg (the book takes no SVG with a picture in it); a drawing stays fig-NN-NN-name.svg."""
        for p in SPEC["plates"]:
            raster = "render" in p or "source" in p or "layers" in p or "reskin" in p
            name = p["book_file"]
            self.assertRegex(name, r"^plate-\d\d-\d\d-[a-z0-9-]+\.jpg$" if raster else r"^fig-\d\d-\d\d-[a-z0-9-]+\.svg$", p["id"])
            self.assertEqual(name.split(".")[0].split("-", 1)[1], p["id"].split("-", 1)[1], f"{p['id']} and {name} number the same figure")

    def test_the_book_numbers_each_plate_in_both_editions(self):
        """The legend of a plate is what the book's list under it says; every plate in the book has numbers to point at (1 to n)."""
        for p in SPEC["plates"]:
            self.assertFalse(p.get("colour_coded"), f"{p['id']}: the book's editions number what the figure shows, so does the plate")

    def test_the_airspeed_indicator_has_the_books_example_aeroplane_speeds(self):
        """Figure 10-3 gives VS0 45, VS1 52, VFE 90, VNO 125 and VNE 160 kt, and chapters 11 to 13 and Part 7 build on them."""
        asi = SPEC["dials"]["ASI"]
        arcs = {a["color"]: (a["from"], a["to"]) for a in asi["arcs"]}
        self.assertEqual(arcs, {"white": (45, 90), "green": (52, 125), "yellow": (125, 160)})
        self.assertEqual([r["value"] for r in asi["redlines"]], [160])

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
            if "render" in p or "source" in p or "layers" in p:
                with open(path, encoding="utf-8") as f:
                    self.assertIn("data:image/jpeg;base64,", f.read(), p["id"])


class BookFiles(unittest.TestCase):
    """What goes into the book's handbook/ppl/figures/: out/book/, by the rules of its build (book_rules.py)."""

    def built(self):
        folder = os.path.join(OUT, "book")
        if not os.path.isdir(folder):
            self.skipTest("no book files yet (python3 09_book_figures/handbook/book_plates.py)")
        return [(p, os.path.join(folder, p["book_file"])) for p in SPEC["plates"] if os.path.exists(os.path.join(folder, p["book_file"]))]

    def test_every_book_file_passes_the_books_rules(self):
        for p, path in self.built():
            if path.endswith(".jpg"):
                with open(path, "rb") as f:
                    problems = problems_of_jpeg(p["book_file"], f.read())
            else:
                with open(path, encoding="utf-8") as f:
                    problems = problems_of_svg(p["book_file"], f.read())
            self.assertEqual(problems, [], p["id"])

    def test_the_checker_catches_what_the_book_rejects(self):
        self.assertTrue(problems_of_svg("fig-05-01-x.svg", '<svg viewBox="0 0 1 1"><image href="data:image/png;base64,AAAA"/></svg>'))
        self.assertTrue(problems_of_svg("fig-05-01-x.svg", '<svg viewBox="0 0 1 1"><text>Lift</text></svg>'))
        self.assertTrue(problems_of_svg("fig-05-01-x.svg", '<svg viewBox="0 0 1 1">' + "<g/>" * 20_000 + "</svg>"))
        self.assertEqual(problems_of_svg("fig-05-01-x.svg", '<svg viewBox="0 0 1 1"><text>105 kt</text></svg>'), ["figure fig-05-01-x.svg: the text '105 kt' is not language-neutral"])
        self.assertTrue(problems_of_jpeg("plate-07-01-x.jpg", b"<svg/>"))
        self.assertTrue(problems_of_jpeg("photo.jpg", b"\xff\xd8\xff\xd9"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
