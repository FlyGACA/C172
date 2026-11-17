"""Checks for the versioned Phase 8 release bundle (scripts/release_manifest.py)."""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_manifest as rm  # noqa: E402


class CommittedManifestTests(unittest.TestCase):
    def test_committed_manifest_is_current(self):
        errors, current = rm.check(ROOT)
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertGreater(current["file_count"], 0)

    def test_manifest_lists_required_files_with_real_digests(self):
        manifest = json.loads((ROOT / rm.MANIFEST).read_text(encoding="utf-8"))
        paths = {f["path"]: f for f in manifest["files"]}
        for required in rm.REQUIRED:
            with self.subTest(path=required):
                self.assertIn(required, paths)
                self.assertEqual(paths[required]["sha256"], rm.sha256(ROOT / required))
        self.assertNotIn(rm.MANIFEST, paths, "the manifest must not list itself")
        self.assertEqual(manifest["file_count"], len(manifest["files"]))
        self.assertEqual(manifest["total_bytes"], sum(f["size"] for f in manifest["files"]))

    def test_bundle_excludes_ci_render_baselines(self):
        self.assertFalse([p for p in rm.bundle_paths(ROOT) if "/docs/renders/" in p])


class VersionTests(unittest.TestCase):
    RELEASES = "# Releases\n\n## v8.0.0\n\nText.\n\n## Phase history\n"

    def test_consistent_versions_pass(self):
        self.assertEqual(rm.version_errors("8.0.0", self.RELEASES, "8.0.0", "v8.0.0"), [])

    def test_non_semver_package_version_fails(self):
        self.assertTrue(rm.version_errors("8.0", self.RELEASES))
        self.assertTrue(rm.version_errors(None, self.RELEASES))

    def test_releases_heading_must_match_package(self):
        errors = rm.version_errors("8.1.0", self.RELEASES)
        self.assertTrue(any("RELEASES.md top release is v8.0.0" in e for e in errors), errors)

    def test_missing_or_repeated_heading_fails(self):
        self.assertTrue(rm.version_errors("8.0.0", "# Releases\n"))
        repeated = "## v8.0.0\n\n## v8.0.0\n"
        self.assertTrue(any("repeats" in e for e in rm.version_errors("8.0.0", repeated)))

    def test_manifest_version_must_match_package(self):
        errors = rm.version_errors("8.0.0", self.RELEASES, manifest_version="7.9.0")
        self.assertTrue(any("is for 7.9.0" in e for e in errors), errors)

    def test_tag_must_match_package(self):
        for tag in ("v8.0.1", "8.0.0", "v8.0.0-rc1"):
            with self.subTest(tag=tag):
                self.assertTrue(rm.version_errors("8.0.0", self.RELEASES, tag=tag))


class DiffTests(unittest.TestCase):
    def test_detects_added_removed_and_changed_files(self):
        old = {"files": [
            {"path": "a", "size": 1, "sha256": "x"},
            {"path": "b", "size": 1, "sha256": "y"},
            {"path": "same", "size": 3, "sha256": "z"},
        ]}
        new = {"files": [
            {"path": "a", "size": 1, "sha256": "changed"},
            {"path": "c", "size": 2, "sha256": "w"},
            {"path": "same", "size": 3, "sha256": "z"},
        ]}
        self.assertEqual(rm.manifest_diff(old, new), ["added: c", "removed: b", "changed: a"])

    def test_identical_manifests_have_no_diff(self):
        manifest = {"files": [{"path": "a", "size": 1, "sha256": "x"}]}
        self.assertEqual(rm.manifest_diff(manifest, manifest), [])


if __name__ == "__main__":
    unittest.main()
