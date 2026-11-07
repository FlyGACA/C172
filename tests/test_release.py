"""Offline structural smoke checks for the FlyGACA C172 release."""
from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReleaseSmokeTests(unittest.TestCase):
    def test_all_phases_present(self):
        for folder in ("01_initial", "02_classic_analog_v2", "02b_refined_airframe", "03_education", "04_digital_twin", "04b_poh_reference", "05_systems_lab", "06_interactive_twin"):
            with self.subTest(folder=folder):
                self.assertTrue((ROOT / folder).is_dir(), folder)

    def test_phase6_assets_and_import_map(self):
        folder = ROOT / "06_interactive_twin"
        model = folder / "C172N_Phase6_Animated_Parts.glb"
        html = (folder / "FlyGACA_C172N_Phase6_Viewer.html").read_text(encoding="utf-8")
        self.assertGreater(model.stat().st_size, 10000)
        with model.open("rb") as stream:
            self.assertEqual(stream.read(4), b"glTF")
        self.assertIn('type="importmap"', html)
        self.assertIn('"three/addons/"', html)
        self.assertIn("./C172N_Phase6_Animated_Parts.glb", html)

    def test_sha256_manifest(self):
        manifest = ROOT / "SHA256SUMS.txt"
        self.assertTrue(manifest.exists())
        entries = 0
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, relpath = line.split("  ", 1)
            # The release manifest came from the original upload package. Its README is
            # preserved verbatim while the repository root README documents later phases.
            target = ROOT / ("docs/archive/UPLOAD_PACKAGE_README.md" if relpath == "README.md" else relpath)
            with self.subTest(path=relpath):
                self.assertTrue(target.is_file(), relpath)
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), digest)
            entries += 1
        self.assertGreaterEqual(entries, 50)

    def test_phase7_and_phase8_use_shared_learning_modules(self):
        for module in ("sim", "scenarios", "gauges"):
            canonical = ROOT / "shared" / "js" / f"{module}.js"
            self.assertTrue(canonical.is_file(), canonical)
            self.assertGreater(canonical.stat().st_size, 1000, canonical)
            for phase in ("07_kinematic_twin", "08_realistic_digital_twin"):
                wrapper = ROOT / phase / "js" / f"{module}.js"
                source = wrapper.read_text(encoding="utf-8")
                self.assertIn(f"../../shared/js/{module}.js", source)
                self.assertLess(len(source), 300, f"{wrapper} should remain a compatibility wrapper")

if __name__ == "__main__":
    unittest.main()
