"""Tests for the POH-cited study-visual pack (content/study-visuals).

Every figure number must trace to shared/js/sim.js and to a page in
08_realistic_digital_twin/data/poh_references.json; the SVG output must be deterministic, bilingual
and carry the non-affiliation statement in both languages.
"""

import importlib.util
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "content" / "study-visuals"
POH_REFS = ROOT / "08_realistic_digital_twin" / "data" / "poh_references.json"
INSTRUMENTS = ROOT / "08_realistic_digital_twin" / "data" / "instruments.json"

sys.path.insert(0, str(STUDY))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load_module("study_visuals_build", STUDY / "build.py")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


MANIFEST = read_json(STUDY / "manifest.json")
POH = {entry["key"]: entry for entry in read_json(POH_REFS)["values"]}
INSTR = read_json(INSTRUMENTS)["instruments"]


def figure_data(figure):
    return read_json(STUDY / "visuals" / figure["data"])


def arabic_chars(text):
    return len(re.findall(r"[\u0600-\u06FF]", text))


class ManifestTests(unittest.TestCase):
    def test_manifest_shape_and_tiers(self):
        self.assertEqual(MANIFEST["languages"], ["en", "ar"])
        ids = [figure["id"] for figure in MANIFEST["visuals"]]
        self.assertEqual(len(ids), len(set(ids)))
        tiers = [figure["tier"] for figure in MANIFEST["visuals"]]
        self.assertTrue(set(tiers) <= {"free", "premium"})
        # The funnel needs at least one free C172 visual and premium study content behind it.
        self.assertGreaterEqual(tiers.count("free"), 1)
        self.assertGreaterEqual(tiers.count("premium"), 3)
        for figure in MANIFEST["visuals"]:
            self.assertGreaterEqual(len(figure["sources"]), 1)
            for lang in MANIFEST["languages"]:
                self.assertTrue(figure["title"][lang].strip())

    def test_every_source_cites_a_poh_page_with_a_known_key(self):
        for figure in MANIFEST["visuals"]:
            pages = []
            for source in figure["sources"]:
                self.assertIn("POH", source["doc"])
                for field in ("page", "what_en", "what_ar"):
                    self.assertTrue(source[field].strip())
                self.assertTrue(source["keys"])
                for key in source["keys"]:
                    self.assertIn(key, POH, "%s cites missing key %s" % (figure["id"], key))
                    entry_pages = [page.strip() for page in str(POH[key]["page"]).split(",")]
                    self.assertIn(source["page"], entry_pages, "%s: %s is not on p.%s" % (figure["id"], key, source["page"]))
                pages.append(source["page"])
            self.assertEqual(pages, list(dict.fromkeys(pages)))

    def test_facts_appear_in_the_cited_poh_value(self):
        for figure in MANIFEST["visuals"]:
            data = figure_data(figure)
            self.assertTrue(data["poh_keys"])
            for fact in data["facts"]:
                self.assertIn(fact["key"], POH)
                self.assertIn(fact["text"], str(POH[fact["key"]]["value"]), "%s: %r" % (figure["id"], fact["text"]))
            for key in data["poh_keys"]:
                self.assertIn(key, POH)

    def test_bilingual_string_sets_have_identical_keys(self):
        base = MANIFEST["strings"]
        self.assertEqual(set(base["en"]), set(base["ar"]))
        for figure in MANIFEST["visuals"]:
            strings = figure_data(figure)["strings"]
            self.assertEqual(set(strings["en"]), set(strings["ar"]), figure["id"])
            for key, value in strings["ar"].items():
                if key == "unit":  # KIAS stays Latin in both editions
                    continue
                self.assertGreater(arabic_chars(value), 0, "%s: %s is not Arabic" % (figure["id"], key))
            for key, value in MANIFEST["strings"]["ar"].items():
                self.assertGreater(arabic_chars(value), 0, key)
        self.assertGreater(arabic_chars(MANIFEST["non_affiliation"]["ar"]), 80)
        self.assertGreater(len(MANIFEST["non_affiliation"]["en"]), 120)


class DataAgreementTests(unittest.TestCase):
    def setUp(self):
        self.sim = build.load_sim()

    def test_v_speeds_and_arcs_agree_with_sim_and_instruments(self):
        data = figure_data(next(figure for figure in MANIFEST["visuals"] if figure["id"] == "v-speeds"))
        arcs = {arc["id"]: [arc["from"], arc["to"]] for arc in data["arcs"]}
        self.assertEqual(arcs["white"], self.sim["asiWhite"])
        self.assertEqual(arcs["green"], self.sim["asiGreen"])
        self.assertEqual(arcs["yellow"], self.sim["asiYellow"])
        self.assertEqual(data["redline"]["value"], self.sim["vne"])
        values = {entry["code"]: entry["value"] for entry in data["v_speeds"]}
        self.assertEqual(values["VNE"], "%d" % self.sim["vne"])
        self.assertEqual(values["VNO"], "%d" % self.sim["vno"])
        self.assertEqual(values["VA"], "%d" % self.sim["va2300"])
        # 110 KIAS at 10 deg and 85 KIAS at 10-40 deg are printed on POH p.2-4 Fig 2-1; sim.js holds
        # the full-flap limit (85) as vfe.
        limits = POH["airspeed.limits_KIAS"]["value"]
        match = re.search(r"VFE (\d+) \(10 deg\) / (\d+)", limits)
        self.assertIsNotNone(match, limits)
        self.assertEqual(values["VFE"], "%s / %s" % (match.group(1), match.group(2)))
        self.assertEqual(int(match.group(2)), int(self.sim["vfe"]))

        instrument_arcs = {arc["color"]: [arc["from"], arc["to"]] for arc in INSTR["ASI"]["arcs"]}
        self.assertEqual(instrument_arcs, arcs)
        self.assertEqual(INSTR["ASI"]["redlines"][0]["value"], data["redline"]["value"])

    def test_fuel_capacity_agrees_with_sim(self):
        data = figure_data(next(figure for figure in MANIFEST["visuals"] if figure["id"] == "fuel-capacity"))
        standard = next(tank for tank in data["tanks"] if tank["id"] == "standard")
        self.assertEqual(standard["total_per_tank_gal"], self.sim["fuelPerTankTotal"])
        self.assertEqual(standard["usable_per_tank_gal"], self.sim["fuelPerTankUsable"])
        self.assertEqual(standard["unusable_per_tank_gal"], self.sim["fuelUnusablePerTank"])
        self.assertEqual(standard["total_gal"], 2 * self.sim["fuelPerTankTotal"])
        self.assertEqual(standard["usable_gal"], 2 * self.sim["fuelPerTankUsable"])
        long_range = next(tank for tank in data["tanks"] if tank["id"] == "long_range")
        self.assertEqual(long_range["usable_gal"], 2 * long_range["usable_per_tank_gal"])
        self.assertEqual(long_range["total_gal"], 2 * long_range["total_per_tank_gal"])

    def test_alternate_static_labels_agree_with_sim_table(self):
        data = figure_data(next(figure for figure in MANIFEST["visuals"] if figure["id"] == "alternate-static"))
        table = {int(indicated): int(corrected) for indicated, corrected in self.sim["altStatic"]}
        for fact in data["facts"]:
            match = re.fullmatch(r"(\d+)->(\d+)", fact["text"])
            if match:
                self.assertEqual(table[int(match.group(1))], int(match.group(2)))

    def test_engine_bands_agree_with_sim_and_instruments(self):
        data = figure_data(next(figure for figure in MANIFEST["visuals"] if figure["id"] == "engine-propeller"))
        bands = [[band["from"], band["to"]] for band in data["tach_bands"]]
        self.assertEqual(bands[0], [2100, int(self.sim["maxRpm"]) - 250])
        self.assertLessEqual(bands[0][1], self.sim["maxRpm"])
        for band in bands:
            self.assertGreaterEqual(band[0], 0)
            self.assertLessEqual(band[1], self.sim["maxRpm"])
        tach_arcs = [[arc["from"], arc["to"]] for arc in INSTR["TACH"]["arcs"]]
        self.assertEqual(tach_arcs[0], bands[0])
        self.assertEqual(tach_arcs[-1][1], bands[-1][1])
        self.assertEqual(INSTR["TACH"]["redlines"][0]["value"], self.sim["maxRpm"])


class OutputTests(unittest.TestCase):
    def test_build_is_deterministic_and_matches_committed_output(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            build.build(Path(first))
            build.build(Path(second))
            first_files = sorted(path for path in Path(first).rglob("*.svg"))
            second_files = sorted(path for path in Path(second).rglob("*.svg"))
            self.assertEqual([path.relative_to(first) for path in first_files], [path.relative_to(second) for path in second_files])
            for left, right in zip(first_files, second_files):
                self.assertEqual(left.read_bytes(), right.read_bytes(), "%s is not deterministic" % left.name)
            committed = STUDY / "out"
            for path in first_files:
                target = committed / path.relative_to(first)
                self.assertTrue(target.exists(), "committed output missing: %s" % target)
                self.assertEqual(path.read_bytes(), target.read_bytes(), "committed output is stale: %s" % target)

    def test_every_visual_exists_in_both_languages_with_the_svg_contract(self):
        en = MANIFEST["non_affiliation"]["en"].split(".")[0]
        for figure in MANIFEST["visuals"]:
            for lang, direction in (("en", "ltr"), ("ar", "rtl")):
                path = STUDY / "out" / lang / ("%s.svg" % figure["id"])
                self.assertTrue(path.exists(), path)
                root = ET.parse(str(path)).getroot()
                self.assertEqual(root.get("lang"), lang)
                self.assertEqual(root.get("direction"), direction)
                text = path.read_text(encoding="utf-8")
                self.assertIn(en, text, "%s/%s lacks the English disclaimer" % (lang, figure["id"]))
                # Single words so a line wrap inside the footer cannot split the probe.
                self.assertIn("فلاي", text, "%s/%s lacks the Arabic disclaimer" % (lang, figure["id"]))
                if lang == "en":
                    self.assertIn("Training and reference only", text)
                else:
                    self.assertIn("للتدريب والمرجع فقط", text)
                self.assertIn(figure["title"][lang], ET.parse(str(path)).getroot().find("{http://www.w3.org/2000/svg}title").text)
                for banned in ("FAA", "14 CFR"):
                    self.assertNotIn(banned, text)
                self.assertIn("POH p.", text)

    def test_arabic_edition_isolates_numeric_runs(self):
        text = (STUDY / "out" / "ar" / "v-speeds.svg").read_text(encoding="utf-8")
        self.assertIn("\u206641\u201385\u2069", text)
        self.assertIn("\u2066110 / 85\u2069", text)
        self.assertNotIn("\u2066C172N\u2069", text)


class DisclosureAndBindingTests(unittest.TestCase):
    def test_disclosure_band_precedes_the_plot(self):
        for figure in MANIFEST["visuals"]:
            for lang in ("en", "ar"):
                path = STUDY / "out" / lang / ("%s.svg" % figure["id"])
                text = path.read_text(encoding="utf-8")
                band = MANIFEST["strings"][lang]["band"]
                self.assertIn(band, text, "%s/%s is missing the %s band" % (lang, figure["id"], lang))
                # the band is drawn in the header, before the first drawing group
                self.assertLess(text.index(band), text.index("<g>"), "%s/%s draws the band below the plot" % (lang, figure["id"]))

    def test_builder_refuses_values_that_drift_from_the_poh(self):
        sim = build.load_sim()
        build.verify_poh(sim)  # the values currently drawn bind to the printed POH text
        with self.assertRaises(SystemExit):
            build.verify_poh(dict(sim, vne=sim["vne"] + 1))
        with self.assertRaises(SystemExit):
            build.verify_poh(dict(sim, asiYellow=[sim["asiYellow"][0], sim["asiYellow"][1] - 2]))
        with self.assertRaises(SystemExit):
            build.verify_poh(dict(sim, fuelPerTankUsable=sim["fuelPerTankUsable"] + 1))


class HelperTests(unittest.TestCase):
    def test_align_maps_visual_alignment_to_logical_anchor(self):
        self.assertEqual(build.align("ltr", "left"), "start")
        self.assertEqual(build.align("ltr", "right"), "end")
        self.assertEqual(build.align("rtl", "left"), "end")
        self.assertEqual(build.align("rtl", "right"), "start")
        self.assertEqual(build.align("rtl", "center"), "middle")

    def test_isolate_numbers_keeps_ranges_together(self):
        self.assertEqual(build.isolate_numbers("41–85"), "\u206641–85\u2069")
        self.assertEqual(build.isolate_numbers("85 / 110"), "\u206685 / 110\u2069")
        self.assertEqual(build.isolate_numbers("2100–2450 RPM"), "\u20662100–2450 RPM\u2069")
        self.assertEqual(build.isolate_numbers("10° / 10–40°"), "\u206610° / 10–40°\u2069")
        self.assertEqual(build.isolate_numbers("C172N"), "C172N")
        self.assertEqual(build.isolate_numbers("O-320-H2AD"), "O-320-H2AD")
        self.assertEqual(build.isolate_numbers("POH p.2-4"), "POH p.2-4")


if __name__ == "__main__":
    unittest.main()
