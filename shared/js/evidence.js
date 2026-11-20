// Evidence records for the C172N values the twin publishes, and the gate that hands a value out only
// when its record is complete and applies to the aircraft and conditions asked for.
//
// The rule: a value without a document, an edition, a page and a matching model is not a value — the
// gate returns null and says why. The records below are transcribed from the Cessna Model 172N
// Pilot's Operating Handbook (1 July 1978, 1979 model) and from the extracts committed in this
// repository (07_kinematic_twin/data/poh_references.json, 08_realistic_digital_twin/data/poh_references.json,
// 04b_poh_reference/poh_1979_reference_data.json). See docs/value-audit.md.

export const POH_SOURCE = Object.freeze({
  document: "Cessna Model 172N Pilot's Operating Handbook",
  edition: '1 July 1978',
  publisher: 'Cessna Aircraft Company',
  aircraft: 'Cessna 172N',
  modelYear: 1979,
  note: '1979-model handbook; a public scan, not a serial-number-specific approved flight manual.',
});

const rec = (id, value, unit, page, conditions = {}, note = '') => Object.freeze({
  id,
  value: Array.isArray(value) ? Object.freeze(value) : value,
  unit,
  page,
  conditions: Object.freeze(conditions),
  source: POH_SOURCE,
  status: 'verified',
  verifiedOn: '2026-11-20',
  ...(note ? { note } : {}),
});

export const EVIDENCE = Object.freeze([
  // Airspeed limitations, p.2-4 Figure 2-1.
  rec('c172n.vne', 160, 'KIAS', '2-4 Fig 2-1'),
  rec('c172n.vno', 128, 'KIAS', '2-4 Fig 2-1'),
  // The handbook prints both a 10 deg row (110 KIAS) and a 10-40 deg row (85 KIAS); at 10 deg the
  // two ranges overlap, so the gate refuses to choose and the caller must read the page.
  rec('c172n.vfe', 110, 'KIAS', '2-4 Fig 2-1', { flapsDeg: 10 }, 'printed 10 deg row'),
  rec('c172n.vfe', 85, 'KIAS', '2-4 Fig 2-1', { flapsDeg: '10-40' }, 'printed 10-40 deg row'),
  rec('c172n.va', 97, 'KIAS', '2-4 Fig 2-1', { weightLb: 2300 }),

  // Airspeed indicator markings, p.2-5 Figure 2-2.
  rec('c172n.asiWhite', [41, 85], 'KIAS', '2-5 Fig 2-2'),
  rec('c172n.asiGreen', [47, 128], 'KIAS', '2-5 Fig 2-2'),
  rec('c172n.asiYellow', [128, 160], 'KIAS', '2-5 Fig 2-2'),

  // Power plant limits, p.2-5; instrument markings, p.2-6 Figure 2-3.
  rec('c172n.maxRpm', 2700, 'rpm', '2-5'),
  rec('c172n.staticRpm', [2280, 2400], 'rpm', '2-5', { throttle: 'full', carbHeat: 'off', mixture: 'full rich' }),
  rec('c172n.tachGreen', [2100, 2450], 'rpm', '2-6 Fig 2-3', { altitudeFt: 0 }, 'sea level; 2100-2575 at 5000 ft, 2100-2700 at 10000 ft'),
  rec('c172n.oilTempMax', 245, 'degF', '2-5'),
  rec('c172n.oilTempGreen', [100, 245], 'degF', '2-6 Fig 2-3'),
  rec('c172n.oilPressMin', 25, 'psi', '2-5'),
  rec('c172n.oilPressMax', 100, 'psi', '2-5'),
  rec('c172n.oilPressGreen', [60, 90], 'psi', '2-6 Fig 2-3'),
  rec('c172n.suctionGreen', [4.5, 5.4], 'inHg', '2-6 Fig 2-3, 7-34'),

  // Run-up and leaning, p.4-7 / 4-13 / 4-16; carburettor heat, p.7-19.
  rec('c172n.magCheckRpm', 1700, 'rpm', '4-7, 4-13'),
  rec('c172n.magDropMax', 125, 'rpm', '4-7, 4-13', { rpm: 1700 }),
  rec('c172n.magDiffMax', 50, 'rpm', '4-7, 4-13', { rpm: 1700 }),
  rec('c172n.carbHeatDrop', [100, 225], 'rpm', '7-19', { throttle: 'full', carbHeat: 'full' }),
  rec('c172n.leanPeakDrop', [25, 50], 'rpm', '4-16'),

  // Fuel, p.1-4 and p.7-21; unusable fuel, p.2-6 Figure 2-3.
  rec('c172n.fuelPerTankTotal', 21.5, 'gal', '1-4, 7-21', { tanks: 'standard' }),
  rec('c172n.fuelPerTankUsable', 20, 'gal', '1-4, 7-21', { tanks: 'standard' }),
  rec('c172n.fuelUnusablePerTank', 1.5, 'gal', '2-6 Fig 2-3', { tanks: 'standard' }),

  // Electrical system, p.7-23 and p.7-25.
  rec('c172n.systemVolts', 28, 'V', '7-23, 7-25'),
  rec('c172n.batteryVolts', 24, 'V', '7-23, 7-25'),
  rec('c172n.alternatorAmps', 60, 'A', '7-25'),

  // Maximum glide, p.3-11 Figure 3-1. Speed is also printed on p.3-3. The figure's weight is not
  // recorded in the committed extract: flagged Needs source in docs/value-audit.md.
  rec('c172n.glideSpeed', 65, 'KIAS', '3-11 Fig 3-1; 3-3', { flaps: 'up', propeller: 'windmilling' }),
  rec('c172n.glideRatio', 9.1, 'ratio', '3-11 Fig 3-1', { flaps: 'up', propeller: 'windmilling' }),

  // Alternate static calibration, p.5-9 Figure 5-1 sheet 2 (flaps up; heater, vents and windows closed).
  rec('c172n.altStaticTable', [[40, 39], [50, 51], [60, 61], [70, 71], [80, 82], [90, 91], [100, 101], [110, 111], [120, 121], [130, 131], [140, 141]], 'KIAS', '5-9 Fig 5-1 sheet 2', { flaps: 'up', vents: 'closed', windows: 'closed' }),
]);

const RANGE = /^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$/;

function conditionMet(want, got) {
  if (got === undefined || got === null) return false;
  if (typeof want === 'number') return got === want;
  const range = typeof want === 'string' ? want.match(RANGE) : null;
  if (range) {
    const lo = Number(range[1]);
    const hi = Number(range[2]);
    return typeof got === 'number' && got >= lo && got <= hi;
  }
  return String(got).toLowerCase() === String(want).toLowerCase();
}

export function conditionsMet(record, request = {}) {
  return Object.entries(record.conditions || {}).every(([key, want]) => conditionMet(want, request[key]));
}

/** Source, edition, page and model checks; conditions are checked separately. */
export function checkEvidence(record, request = {}) {
  const reasons = [];
  const source = record.source || {};
  if (!source.document) reasons.push('missing_source');
  if (!source.edition) reasons.push('missing_edition');
  if (!record.page) reasons.push('missing_page');
  const model = request.model ?? POH_SOURCE.aircraft;
  if (model !== (source.aircraft ?? POH_SOURCE.aircraft)) reasons.push('model_mismatch');
  const year = request.modelYear ?? POH_SOURCE.modelYear;
  if (year !== (source.modelYear ?? POH_SOURCE.modelYear)) reasons.push('model_mismatch');
  if (record.status !== 'verified') reasons.push(record.status || 'needs_source');
  return { ok: reasons.length === 0, reasons };
}

/** The full gate: evidence completeness plus the conditions the record was read under. */
export function gateRecord(record, request = {}) {
  const evidence = checkEvidence(record, request);
  const reasons = [...new Set([...evidence.reasons, ...(conditionsMet(record, request) ? [] : ['missing_conditions'])])];
  return { ok: reasons.length === 0, reasons };
}

export function citation(record) {
  const source = record.source || {};
  return `${source.document} (${source.edition}), p.${record.page}`;
}

/**
 * The only way a published value should reach the viewer. Returns the value and its citation, or
 * null with the reasons it was withheld: unknown_value, missing_source, missing_edition, missing_page,
 * model_mismatch, needs-source, missing_conditions, ambiguous_conditions.
 */
export function useValue(id, request = {}) {
  const records = EVIDENCE.filter((r) => r.id === id);
  if (records.length === 0) return withheld(['unknown_value']);
  const checked = records.map((r) => ({ r, g: checkEvidence(r, request) }));
  const eligible = checked.filter((x) => x.g.ok && conditionsMet(x.r, request));
  if (eligible.length === 1) {
    const r = eligible[0].r;
    return { value: r.value, unit: r.unit, citation: citation(r), conditions: { ...r.conditions }, record: r, reasons: [] };
  }
  if (eligible.length > 1) return withheld(['ambiguous_conditions']);
  const failed = checked.filter((x) => !x.g.ok);
  if (failed.length === records.length) return withheld([...new Set(failed.flatMap((x) => x.g.reasons))]);
  return withheld(['missing_conditions']);
}

function withheld(reasons) {
  return { value: null, unit: null, citation: null, conditions: null, record: null, reasons };
}
