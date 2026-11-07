"""Tests for aircraft measurement ingestion and model deviation reports."""

import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "08_realistic_digital_twin" / "scripts" / "measurements.py"
SPEC = importlib.util.spec_from_file_location("measurements", MODULE)
measurements = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measurements)


AIRCRAFT = {
    "manufacturer": "Cessna", "model": "172N", "year": 1979,
    "tail_number": "TEST", "serial_number": "TEST", "configuration": "test fixture",
}


def record(**overrides):
    value = {
        "id": "span-1", "parameter": "wingspan_m", "value": 10922, "unit": "mm", "tolerance": 10,
        "provenance": "aircraft_measurement", "method": "laser", "source": "test fixture", "recorded_at": "2026-11-07",
        "recorded_by": "tester", "verification_status": "verified", "notes": "",
    }
    value.update(overrides)
    return value


class MeasurementTests(unittest.TestCase):
    def test_valid_dataset_and_unit_conversion(self):
        data = {"schema_version": 1, "aircraft": AIRCRAFT, "records": [record()]}
        self.assertEqual(measurements.validate_dataset(data), [])
        report = measurements.deviation_report(data)
        row = report["results"][0]
        self.assertEqual(row["unit"], "m")
        self.assertAlmostEqual(row["measured"], 10.922)
        self.assertEqual(row["status"], "within_tolerance")
        markdown = measurements.markdown_report(report)
        self.assertIn("wingspan_m", markdown)
        self.assertIn("within_tolerance", markdown)

    def test_outside_tolerance_and_unmapped_parameter(self):
        data = {"schema_version": 1, "aircraft": AIRCRAFT, "records": [
            record(value=11000, tolerance=2),
            record(id="custom-1", parameter="door_width_m", value=1, unit="m"),
        ]}
        report = measurements.deviation_report(data)
        self.assertEqual(report["summary"]["outside_tolerance"], 1)
        self.assertEqual(report["summary"]["unmapped"], 1)

    def test_exact_converted_value_with_zero_tolerance_ignores_float_noise(self):
        data = {"schema_version": 1, "aircraft": AIRCRAFT, "records": [record(value=430, unit="in", tolerance=0)]}
        self.assertEqual(measurements.deviation_report(data)["results"][0]["status"], "within_tolerance")

    def test_raw_records_are_excluded_by_default(self):
        data = {"schema_version": 1, "aircraft": AIRCRAFT, "records": [record(verification_status="raw")]}
        self.assertEqual(measurements.deviation_report(data)["summary"]["records_reported"], 0)
        self.assertEqual(measurements.deviation_report(data, include_raw=True)["summary"]["records_reported"], 1)

    def test_invalid_records_are_rejected(self):
        data = {"schema_version": 1, "aircraft": AIRCRAFT, "records": [record(tolerance=-1, recorded_at="07/11/2026")]}
        errors = measurements.validate_dataset(data)
        self.assertTrue(any("negative" in error for error in errors))
        self.assertTrue(any("YYYY-MM-DD" in error for error in errors))

    def test_csv_import(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            csv_path, aircraft_path = folder / "measurements.csv", folder / "aircraft.json"
            aircraft_path.write_text(json.dumps({"aircraft": AIRCRAFT}), encoding="utf-8")
            with csv_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=measurements.RECORD_FIELDS)
                writer.writeheader(); writer.writerow(record())
            imported = measurements.import_csv(csv_path, aircraft_path)
            self.assertEqual(imported["records"][0]["value"], 10922.0)


if __name__ == "__main__":
    unittest.main()
