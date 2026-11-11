#!/usr/bin/env python3
"""Fast, dependency-free quality gate for Phase 8 source and generated assets."""

from __future__ import annotations

import json
import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P8 = ROOT / "08_realistic_digital_twin"
LODS = ("high", "medium", "low")
LOD_DETAIL = {"high": 1, "medium": 0, "low": 0}      # highest detail level each quality level carries (blender/c172/export.py)
# Download size ceilings. High carries the structure and mechanisms under the skin (detail level 1);
# medium and low are the basic model, for tablets and phones. Medium and low share one set of textures
# (1024 px, the paint of the fuselage 2048 px): at 512 px the stripes and the cabin trim were a blur on a phone.
MODEL_BUDGETS = {"high": 9_600_000, "medium": 5_900_000, "low": 5_400_000}
IMAGE_BUDGET = 3_000_000
STATUS = {"measured", "poh", "type_data", "estimated"}


class Gate:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def json(self, relative: str):
        path = P8 / relative
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.errors.append(f"{relative}: {exc}")
            return {}


def validate_catalog(gate: Gate) -> None:
    data = gate.json("data/parts_catalog.json")
    entries = data.get("entries", [])
    gate.check(bool(entries), "parts catalog has no entries")
    patterns: set[str] = set()
    for number, entry in enumerate(entries, 1):
        prefix = f"parts catalog entry {number}"
        pattern = entry.get("match", "")
        gate.check(pattern not in patterns, f"{prefix}: duplicate match {pattern!r}")
        patterns.add(pattern)
        try:
            re.compile(pattern)
        except re.error as exc:
            gate.errors.append(f"{prefix}: invalid regular expression: {exc}")
        for language in ("en", "ar"):
            content = entry.get(language, {})
            gate.check(bool(content.get("t", "").strip()), f"{prefix}: missing {language} title")
            gate.check(bool(content.get("d", "").strip()), f"{prefix}: missing {language} description")


def validate_references(gate: Gate) -> None:
    data = gate.json("data/poh_references.json")
    gate.check(bool(data.get("source", {}).get("title")), "POH references: missing source title")
    keys: set[str] = set()
    for number, value in enumerate(data.get("values", []), 1):
        key = value.get("key", "")
        gate.check(bool(key), f"POH reference {number}: missing key")
        gate.check(key not in keys, f"POH reference {number}: duplicate key {key!r}")
        keys.add(key)
        gate.check("value" in value, f"POH reference {key or number}: missing value")
        gate.check(bool(str(value.get("page", "")).strip()), f"POH reference {key or number}: missing page")


def validate_instruments(gate: Gate) -> None:
    instruments = gate.json("data/instruments.json").get("instruments", {})
    gate.check(bool(instruments), "instrument data is empty")
    for name, instrument in instruments.items():
        label = instrument.get("label", {})
        gate.check(all(label.get(lang, "").strip() for lang in ("en", "ar")), f"{name}: incomplete bilingual label")
        points = instrument.get("map", [])
        gate.check(len(points) >= 2, f"{name}: needle map needs at least two points")
        values = [point[0] for point in points if isinstance(point, list) and len(point) == 2]
        gate.check(len(values) == len(points), f"{name}: invalid needle map point")
        gate.check(values == sorted(values) and len(values) == len(set(values)), f"{name}: needle map values must increase")
        if values:
            gate.check(instrument.get("min") <= values[0], f"{name}: minimum is outside needle map")
            gate.check(instrument.get("max") >= values[-1], f"{name}: maximum is outside needle map")


def validate_models(gate: Gate) -> None:
    part_sets: dict[str, set[str]] = {}
    details: dict[str, dict[str, int]] = {}
    for lod in LODS:
        model = P8 / "models" / f"C172N_realistic_{lod}.glb"
        index = gate.json(f"models/model_index_{lod}.json")
        gate.check(model.is_file(), f"{lod}: model is missing")
        if model.is_file():
            gate.check(model.stat().st_size <= MODEL_BUDGETS[lod], f"{lod}: model exceeds {MODEL_BUDGETS[lod] / 1e6:.1f} MB budget")
            gate.check(index.get("bytes") == model.stat().st_size, f"{lod}: index byte count does not match GLB")
        parts = index.get("parts", [])
        names = [part.get("name", "") for part in parts]
        gate.check(len(names) == len(set(names)), f"{lod}: duplicate part names in model index")
        gate.check(index.get("triangles") == sum(part.get("triangles", 0) for part in parts), f"{lod}: triangle total does not match parts")
        for part in parts:
            gate.check(part.get("status") in STATUS, f"{lod}: {part.get('name')}: invalid status")
            gate.check(part.get("status") != "measured" or bool(part.get("measurement_id")), f"{lod}: {part.get('name')}: measured part lacks measurement_id")
            gate.check(bool(part.get("label_en")), f"{lod}: {part.get('name')}: missing English label")
            gate.check(bool(part.get("label_ar")), f"{lod}: {part.get('name')}: missing Arabic label")
        for part in parts:
            gate.check(part.get("detail", 0) <= LOD_DETAIL[lod], f"{lod}: {part.get('name')}: detail level {part.get('detail')} does not belong in this quality level")
        part_sets[lod] = set(names)
        details[lod] = {part.get("name"): part.get("detail", 0) for part in parts}
    for lod in LODS[1:]:
        expected = {name for name, level in details.get("high", {}).items() if level <= LOD_DETAIL[lod]}
        gate.check(part_sets.get(lod) == expected, f"{lod}: part set differs from the high model's parts of detail level <= {LOD_DETAIL[lod]}")


def validate_parts_list(gate: Gate) -> None:
    """models/parts_all.json lists every part of the editable scene, all detail levels; the parts index is written from it."""
    data = gate.json("models/parts_all.json")
    parts = [part for part in data.get("parts", []) if "detail" in part]
    gate.check(bool(parts), "parts list is empty")
    ids = [part.get("id", "") for part in parts]
    gate.check(len(ids) == len(set(ids)), "parts list: duplicate ids")
    for part in parts:
        gate.check(part.get("status") in STATUS, f"parts list: {part.get('id')}: invalid status")
        gate.check(bool(part.get("en")) and bool(part.get("ar")), f"parts list: {part.get('id')}: incomplete bilingual label")
        gate.check(part.get("detail") in (0, 1, 2), f"parts list: {part.get('id')}: invalid detail level")
        gate.check(part.get("status") != "poh" or bool(part.get("ref")) or part.get("detail") == 0, f"parts list: {part.get('id')}: a part documented from the POH needs its page (ref)")
    high = {part.get("name") for part in gate.json("models/model_index_high.json").get("parts", [])}
    in_web_model = {part["id"] for part in parts if part["detail"] <= LOD_DETAIL["high"]}
    gate.check(in_web_model == high, "parts list: the parts of detail level 0-1 differ from the high web model")
    path = P8 / "scripts" / "parts_index.py"
    spec = importlib.util.spec_from_file_location("quality_parts_index", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    index = P8 / "docs" / "06_parts_index.md"
    gate.check(index.is_file() and bool(data) and index.read_text(encoding="utf-8") == module.render(data),
               "docs/06_parts_index.md is out of date: run python3 08_realistic_digital_twin/scripts/parts_index.py")


def validate_manifest_and_assets(gate: Gate) -> None:
    manifest = gate.json("phase8_manifest.json")
    gate.check(manifest.get("phase") == 8, "manifest phase must be 8")
    gate.check(set(manifest.get("reference", {}).get("status_vocabulary", {})) == STATUS, "manifest status vocabulary is incomplete")
    gate.check((P8 / manifest.get("entry_point", "")).is_file(), "manifest entry point is missing")
    for lod, relative in manifest.get("model", {}).get("quality_levels", {}).items():
        gate.check(lod in LODS, f"manifest has unknown LOD {lod!r}")
        gate.check((P8 / relative).is_file(), f"manifest model is missing: {relative}")
    for folder in (P8 / "docs" / "gallery", P8 / "docs" / "renders"):
        for image in folder.glob("*.png"):
            gate.check(image.stat().st_size <= IMAGE_BUDGET, f"{image.relative_to(ROOT)} exceeds {IMAGE_BUDGET / 1e6:.1f} MB budget")


def validate_measurements(gate: Gate) -> None:
    path = P8 / "scripts" / "measurements.py"
    spec = importlib.util.spec_from_file_location("quality_measurements", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = module.validate_dataset(gate.json("data/aircraft_measurements.json"))
    gate.errors.extend(f"aircraft measurements: {error}" for error in errors)
    gate.check((P8 / "data" / "measurement_schema.json").is_file(), "measurement schema is missing")
    gate.check((P8 / "data" / "measurement_template.csv").is_file(), "measurement CSV template is missing")


def main() -> int:
    gate = Gate()
    validate_catalog(gate)
    validate_references(gate)
    validate_instruments(gate)
    validate_models(gate)
    validate_parts_list(gate)
    validate_manifest_and_assets(gate)
    validate_measurements(gate)
    if gate.errors:
        print(f"Quality gate failed with {len(gate.errors)} problem(s):")
        for error in gate.errors:
            print(f"  - {error}")
        return 1
    print("Quality gate OK: catalog, provenance, instruments, LOD indexes, parts list, manifests and asset budgets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
