#!/usr/bin/env python3
"""Validate, import, normalize, and compare aircraft measurements to model references."""

from __future__ import annotations

import argparse
import csv
from datetime import date
import importlib.util
import json
import math
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
UNITS_PATH = ROOT / "blender" / "c172" / "units.py"
SUPPORTED_UNITS = {"mm", "cm", "m", "in", "ft", "deg", "lb", "gal_us", "ft2"}
STATUS = {"raw", "verified", "rejected"}
PROVENANCE = {"aircraft_measurement", "document_reference", "type_data"}
RECORD_FIELDS = ("id", "parameter", "value", "unit", "tolerance", "provenance", "method", "source", "recorded_at", "recorded_by", "verification_status", "notes")
LENGTH_TO_M = {"mm": 0.001, "cm": 0.01, "m": 1.0, "in": 0.0254, "ft": 0.3048}


class MeasurementError(ValueError):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MeasurementError(f"{path}: {exc}") from exc


def validate_dataset(data):
    errors = []
    if not isinstance(data, dict):
        return ["dataset must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    aircraft = data.get("aircraft")
    required_aircraft = ("manufacturer", "model", "year", "tail_number", "serial_number", "configuration")
    if not isinstance(aircraft, dict):
        errors.append("aircraft must be an object")
    else:
        for key in required_aircraft:
            if key not in aircraft:
                errors.append(f"aircraft.{key} is required")
        unknown_aircraft = sorted(set(aircraft) - set(required_aircraft))
        if unknown_aircraft:
            errors.append(f"aircraft has unknown fields: {', '.join(unknown_aircraft)}")
        if not isinstance(aircraft.get("year"), int) or not 1955 <= aircraft.get("year", 0) <= 2100:
            errors.append("aircraft.year must be an integer from 1955 to 2100")
        for key in ("manufacturer", "model", "configuration"):
            if not isinstance(aircraft.get(key), str) or not aircraft.get(key, "").strip():
                errors.append(f"aircraft.{key} must be a non-empty string")
    records = data.get("records")
    if not isinstance(records, list):
        return errors + ["records must be an array"]
    seen = set()
    for index, record in enumerate(records, 1):
        prefix = f"record {index}"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = [field for field in RECORD_FIELDS if field not in record]
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue
        unknown = sorted(set(record) - set(RECORD_FIELDS))
        if unknown:
            errors.append(f"{prefix} unknown fields: {', '.join(unknown)}")
        identifier = record["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", identifier):
            errors.append(f"{prefix}.id is invalid")
        elif identifier in seen:
            errors.append(f"{prefix}.id duplicates {identifier!r}")
        seen.add(identifier)
        if not isinstance(record["parameter"], str) or not re.fullmatch(r"[a-z][a-z0-9_]*", record["parameter"]):
            errors.append(f"{prefix}.parameter is invalid")
        for field in ("value", "tolerance"):
            value = record[field]
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                errors.append(f"{prefix}.{field} must be a finite number")
        if isinstance(record["tolerance"], (int, float)) and record["tolerance"] < 0:
            errors.append(f"{prefix}.tolerance cannot be negative")
        if record["unit"] not in SUPPORTED_UNITS:
            errors.append(f"{prefix}.unit is unsupported: {record['unit']!r}")
        if record["verification_status"] not in STATUS:
            errors.append(f"{prefix}.verification_status is invalid")
        if record["provenance"] not in PROVENANCE:
            errors.append(f"{prefix}.provenance is invalid")
        for field in ("method", "source", "recorded_by"):
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"{prefix}.{field} must be non-empty")
        try:
            date.fromisoformat(record["recorded_at"])
        except (TypeError, ValueError):
            errors.append(f"{prefix}.recorded_at must be YYYY-MM-DD")
        if not isinstance(record["notes"], str):
            errors.append(f"{prefix}.notes must be a string")
    return errors


def canonical_unit(parameter):
    for suffix, unit in (("_m", "m"), ("_in", "in"), ("_deg", "deg"), ("_lb", "lb"), ("_gal", "gal_us"), ("_ft2", "ft2")):
        if parameter.endswith(suffix):
            return unit
    return None


def convert(value, source, target):
    if source == target:
        return float(value)
    if source in LENGTH_TO_M and target in LENGTH_TO_M:
        return float(value) * LENGTH_TO_M[source] / LENGTH_TO_M[target]
    raise MeasurementError(f"cannot convert {source} to {target}")


def load_model_values():
    spec = importlib.util.spec_from_file_location("c172_measurement_units", UNITS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {key: value["v"] for key, value in module.REF.items() if isinstance(value.get("v"), (int, float))}


def deviation_report(data, include_raw=False):
    errors = validate_dataset(data)
    if errors:
        raise MeasurementError("; ".join(errors))
    model = load_model_values()
    rows = []
    for record in data["records"]:
        if record["verification_status"] == "rejected" or (record["verification_status"] == "raw" and not include_raw):
            continue
        parameter = record["parameter"]
        if parameter not in model:
            rows.append({"id": record["id"], "parameter": parameter, "status": "unmapped"})
            continue
        target_unit = canonical_unit(parameter)
        if not target_unit:
            rows.append({"id": record["id"], "parameter": parameter, "status": "unsupported_model_unit"})
            continue
        measured = convert(record["value"], record["unit"], target_unit)
        tolerance = convert(record["tolerance"], record["unit"], target_unit)
        expected = float(model[parameter])
        delta = measured - expected
        numeric_epsilon = 1e-12 * max(1.0, abs(expected))
        if abs(delta) <= numeric_epsilon:
            delta = 0.0
        comparison_tolerance = max(tolerance, numeric_epsilon)
        rows.append({
            "id": record["id"], "parameter": parameter, "status": "within_tolerance" if abs(delta) <= comparison_tolerance else "outside_tolerance",
            "unit": target_unit, "measured": measured, "model": expected, "tolerance": tolerance,
            "deviation": delta, "deviation_percent": (delta / expected * 100) if expected else None,
            "verification_status": record["verification_status"], "provenance": record["provenance"],
        })
    compared = [row for row in rows if row["status"] in {"within_tolerance", "outside_tolerance"}]
    return {
        "schema_version": 1,
        "aircraft": data["aircraft"],
        "summary": {
            "records_total": len(data["records"]), "records_reported": len(rows), "compared": len(compared),
            "within_tolerance": sum(row["status"] == "within_tolerance" for row in compared),
            "outside_tolerance": sum(row["status"] == "outside_tolerance" for row in compared),
            "unmapped": sum(row["status"] == "unmapped" for row in rows),
        },
        "results": rows,
    }


def markdown_report(report):
    aircraft = report["aircraft"]
    summary = report["summary"]
    identity = " / ".join(str(value) for value in (aircraft.get("year"), aircraft.get("manufacturer"), aircraft.get("model")) if value)
    lines = [
        "# C172 measurement deviation report", "",
        f"Aircraft: **{identity}**  ",
        f"Registration: **{aircraft.get('tail_number') or 'not recorded'}**  ",
        f"Serial number: **{aircraft.get('serial_number') or 'not recorded'}**", "",
        f"Compared: {summary['compared']} · Within tolerance: {summary['within_tolerance']} · "
        f"Outside tolerance: {summary['outside_tolerance']} · Unmapped: {summary['unmapped']}", "",
        "| Record | Provenance | Parameter | Profile value | Model | Tolerance | Deviation | Result |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["results"]:
        if "measured" not in row:
            lines.append(f"| {row['id']} | — | {row['parameter']} | — | — | — | — | {row['status']} |")
            continue
        percent = "—" if row["deviation_percent"] is None else f"{row['deviation_percent']:+.3f}%"
        lines.append(
            f"| {row['id']} | {row['provenance']} | {row['parameter']} | {row['measured']:.6g} {row['unit']} | "
            f"{row['model']:.6g} {row['unit']} | ±{row['tolerance']:.6g} | "
            f"{row['deviation']:+.6g} ({percent}) | {row['status']} |"
        )
    lines.extend(["", "Raw and rejected observations are excluded unless `--include-raw` is used.", ""])
    return "\n".join(lines)


def import_csv(csv_path, aircraft_path):
    aircraft_data = load_json(aircraft_path)
    aircraft = aircraft_data.get("aircraft", aircraft_data)
    records = []
    try:
        with csv_path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(RECORD_FIELDS):
                raise MeasurementError(f"CSV columns must be exactly: {', '.join(RECORD_FIELDS)}")
            for row in reader:
                row["value"] = float(row["value"])
                row["tolerance"] = float(row["tolerance"])
                records.append(row)
    except (OSError, ValueError) as exc:
        raise MeasurementError(f"{csv_path}: {exc}") from exc
    data = {"schema_version": 1, "aircraft": aircraft, "records": records}
    errors = validate_dataset(data)
    if errors:
        raise MeasurementError("; ".join(errors))
    return data


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate"); validate.add_argument("dataset", type=Path)
    ingest = sub.add_parser("import-csv"); ingest.add_argument("csv", type=Path); ingest.add_argument("aircraft", type=Path); ingest.add_argument("output", type=Path)
    report = sub.add_parser("report"); report.add_argument("dataset", type=Path); report.add_argument("output", type=Path); report.add_argument("--include-raw", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            errors = validate_dataset(load_json(args.dataset))
            if errors:
                raise MeasurementError("; ".join(errors))
            print(f"Measurements OK: {args.dataset}")
        elif args.command == "import-csv":
            data = import_csv(args.csv, args.aircraft); write_json(args.output, data)
            print(f"Imported {len(data['records'])} measurements to {args.output}")
        else:
            result = deviation_report(load_json(args.dataset), args.include_raw)
            if args.output.suffix.lower() == ".md":
                args.output.write_text(markdown_report(result), encoding="utf-8")
            else:
                write_json(args.output, result)
            print(json.dumps(result["summary"], indent=2))
    except MeasurementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
