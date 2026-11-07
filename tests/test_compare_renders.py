"""Unit tests for the perceptual render regression metric."""

import importlib.util
from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "08_realistic_digital_twin" / "scripts" / "compare_renders.py"
SPEC = importlib.util.spec_from_file_location("compare_renders", MODULE)
compare_renders = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare_renders)


class RenderComparisonTests(unittest.TestCase):
    def test_identical_images_have_zero_difference(self):
        image = Image.new("RGB", (64, 32), "white")
        mae, rms, edge_mae, _ = compare_renders.score(image, image.copy())
        self.assertEqual((mae, rms, edge_mae), (0.0, 0.0, 0.0))

    def test_large_visual_change_is_detected(self):
        white = Image.new("RGB", (64, 32), "white")
        black = Image.new("RGB", (64, 32), "black")
        mae, rms, _edge_mae, _ = compare_renders.score(white, black)
        self.assertGreater(mae, 0.9)
        self.assertGreater(rms, 0.9)


if __name__ == "__main__":
    unittest.main()
