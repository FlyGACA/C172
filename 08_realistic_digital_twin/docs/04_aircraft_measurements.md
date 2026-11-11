# Aircraft measurement and provenance workflow

Phase 8 currently represents a factory-standard 1979 C172N educational baseline. No value may
be labelled `measured` until it has been recorded from the actual aircraft and passes this
workflow.

The named profile is **HZ-C172**. Its initial records are document references and type data,
not a physical survey; the serial number and installed configuration remain unverified.

The flight model and the pilot's seat have their own survey, which does not rebuild the 3D model:
[10_flight_survey.md](10_flight_survey.md).

## Recording a survey

1. Complete the identity fields in `data/aircraft_measurements.json`, including registration and
   serial number. Never infer a serial number from photographs.
2. Copy `data/measurement_template.csv` and add one observation per row. Set `provenance` to
   `aircraft_measurement`, `document_reference`, or `type_data`. Keep repeated
   measurements as separate records with unique IDs; do not average them manually.
3. Use ISO dates (`YYYY-MM-DD`) and record the physical method, instrument, operator, source,
   uncertainty/tolerance, aircraft configuration, and useful notes.
4. Mark new observations `raw`. A second person checks the station/datum, units, transcription,
   and aircraft identity before changing them to `verified`. Use `rejected` rather than deleting
   a bad observation so the audit trail remains visible.

Supported units are `mm`, `cm`, `m`, `in`, `ft`, `deg`, `lb`, `gal_us`, and `ft2`. Parameters
that match keys in `blender/c172/units.py` are compared automatically with the model.

```bash
python3 scripts/measurements.py import-csv data/my_survey.csv data/aircraft_measurements.json /tmp/measurements.json
python3 scripts/measurements.py validate /tmp/measurements.json
python3 scripts/measurements.py report /tmp/measurements.json /tmp/deviation_report.json
```

Use a `.json` output path for machine-readable results or `.md` for a review-friendly table.

The report excludes `raw` and `rejected` observations by default. `--include-raw` is available
for fieldwork previews, but raw data must never change the production model or provenance badge.

## Datum and naming rules

- Fuselage station is inches aft of the firewall datum (`FS 0`).
- Butt line is distance from aircraft centreline; state left/right in the record ID and notes.
- Water-line measurements must describe the chosen vertical datum explicitly.
- Parameters use lowercase snake case. Prefer existing `units.py` names such as `wingspan_m`,
  `gear_track_m`, and `wing_le_fs_in`.
- Photograph and scan sources should use durable filenames or URLs and include scale-control IDs.

## Applying verified measurements

Changing the JSON record alone does not alter geometry. Update the relevant generator constant,
set its status to `measured`, cite the measurement record ID in its reference/note, rebuild all
LODs, and run the complete geometry and visual regression suite. Review unexpected deviations
before accepting new reference renders.
