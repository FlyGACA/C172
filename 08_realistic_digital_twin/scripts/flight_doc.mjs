// Writes the two generated tables of docs/08_flight_model.md: the model flown against the handbook's figures,
// and every number of the model with its source. Run: npm run flight:doc   (--check fails if the document is stale)
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as F from '../js/flight.js';
import { flyTakeoff, flyLanding, flyStall } from '../js/pilot.js';
import * as POH from '../js/poh_tables.js';

const DOC = fileURLToPath(new URL('../docs/08_flight_model.md', import.meta.url));
const KT = 0.514444;
const isaDev = (altFt, tempC) => tempC - (15 - 0.0019812 * altFt);
const pct = (model, book) => `${model >= book ? '+' : '−'}${Math.abs((model / book - 1) * 100).toFixed(0)} %`;
const signed = (x, d = 0) => (Number(x.toFixed(d)) === 0 ? '0' : `${x > 0 ? '+' : '−'}${Math.abs(x).toFixed(d)}`);
const climbAt = (kias, altFt, tempC = null) => {
  const dev = tempC == null ? 0 : isaDev(altFt, tempC);
  return F.trim({ kcas: F.kcasFromKias(kias), altFt, isaDevC: dev, torque: F.fullThrottleTorque(F.chargeAt(altFt, dev)) }).climbFpm;
};
/** Level flight that turns a given RPM, and level flight at full throttle, at an altitude. */
function levelAt(altFt, want) {
  let lo = 60, hi = 140;
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (want(F.trim({ kcas: mid, altFt }))) lo = mid; else hi = mid; }
  return F.trim({ kcas: lo, altFt });
}

export function validationMarkdown() {
  const out = [];
  // ---- stall speeds
  out.push(`### Stall speeds, power off, 2300 lb (${POH.STALL_KCAS.ref})`, '', '| Flaps | Centre of gravity | Handbook KCAS | Model KCAS |', '|---|---|---|---|');
  for (const cg of ['aft', 'fwd']) for (const flap of [0, 10, 40]) {
    out.push(`| ${flap}° | most ${cg === 'aft' ? 'rearward' : 'forward'} | ${POH.STALL_KCAS[cg][flap][0]} | ${F.stallSpeedKcas({ flapDeg: flap, cgFrac: cg === 'aft' ? 1 : 0 }).toFixed(1)} |`);
  }
  const flown = [[0, 0.5], [40, 0.5]].map(([flap, cg]) => ({ flap, r: flyStall(F.createFlight({ cgFrac: cg }), { flapDeg: flap, holdSeconds: 0.5 }) }));
  out.push('', `Flown by the scripted pilot (throttle closed, altitude held, centre of gravity in the middle): ${flown.map(({ flap, r }) => `flaps ${flap}°: horn at ${r.warningKcas.toFixed(1)} KCAS, stall at ${r.stallKcas.toFixed(1)} KCAS (${r.loadFactor.toFixed(2)} g), recovery lost ${r.recoveryLossFt.toFixed(0)} ft`).join('; ')}. The handbook: horn ${POH.STALL_WARNING.knotsBefore.join(' to ')} knots before the stall (${POH.STALL_WARNING.ref}); a recovery may lose as much as ${POH.STALL_KCAS.recoveryLossFt} ft.`);
  // ---- engine
  const staticRpm = F.equilibriumRpm(F.engineAt(1, 1), 0, 1);
  out.push('', `### Static RPM (${POH.STATIC_RPM.ref})`, '', `Handbook: ${POH.STATIC_RPM.min} to ${POH.STATIC_RPM.max} RPM at full throttle. Model: ${staticRpm.toFixed(0)} RPM, with ${(F.propThrust(staticRpm, 0, 1) / 4.4482216).toFixed(0)} lb of thrust.`);
  // ---- climb
  out.push('', `### Rate of climb, flaps up, full throttle, standard temperature (${POH.CLIMB_STANDARD.ref})`, '', '| Altitude ft | Climb KIAS | Handbook ft/min | Model ft/min | Difference |', '|---|---|---|---|---|');
  for (const [alt, kias, fpm] of POH.CLIMB_STANDARD.rows) { const m = climbAt(kias, alt); out.push(`| ${alt} | ${kias} | ${fpm} | ${m.toFixed(0)} | ${signed(m - fpm)} |`); }
  let worst = 0, count = 0;
  for (const [alt, row] of Object.entries(POH.CLIMB_TEMPERATURE.rows)) POH.CLIMB_TEMPERATURE.tempC.forEach((tc, i) => { if (row[i + 1] != null) { worst = Math.max(worst, Math.abs(climbAt(row[0], Number(alt), tc) - row[i + 1])); count++; } });
  out.push('', `At ${POH.CLIMB_TEMPERATURE.tempC.map((t) => String(t).replace('-', '−')).join(', ').replace(/, (\d+)$/, ' and $1')} °C (${POH.CLIMB_TEMPERATURE.ref}, ${count} values from sea level to 12,000 ft): the largest difference is ${worst.toFixed(0)} ft/min.`);
  // ---- cruise
  out.push('', `### Cruise, standard temperature (${POH.CRUISE.ref})`, '', '| Altitude ft | Lines within full throttle | Largest difference | Fastest handbook line | Model at full throttle |', '|---|---|---|---|---|');
  for (const [altText, rows] of Object.entries(POH.CRUISE.rows)) {
    const alt = Number(altText), full = F.fullThrottleTorque(F.chargeAt(alt));
    const top = levelAt(alt, (t) => t.torque < full);
    let n = 0, dKt = 0, dPct = 0;
    for (const [rpm, percent, ktas] of rows) {
      const t = levelAt(alt, (x) => x.rpm < rpm);
      if (t.torque > full) continue;
      n++; dKt = Math.max(dKt, Math.abs(t.tas / KT - ktas)); dPct = Math.max(dPct, Math.abs((t.power / F.FM.ratedPower.v) * 100 - percent));
    }
    const [rpm0, pct0, ktas0] = rows[0];
    const reach = n === rows.length ? 'within reach' : `${(top.tas / KT).toFixed(0)} KTAS at ${Math.round(top.rpm / 10) * 10} RPM, ${((top.power / F.FM.ratedPower.v) * 100).toFixed(0)} %`;
    out.push(`| ${alt} | ${n} of ${rows.length} | ${dKt.toFixed(1)} kt, ${dPct.toFixed(1)} points of power | ${ktas0} KTAS at ${rpm0} RPM, ${pct0} % | ${reach} |`);
  }
  // ---- glide
  const g = F.trim({ kcas: F.kcasFromKias(POH.GLIDE.kias), altFt: 6000, engineOn: false });
  out.push('', `### Maximum glide (${POH.GLIDE.ref})`, '', `Handbook: about ${POH.GLIDE.ratio} to 1 at ${POH.GLIDE.kias} KIAS, propeller windmilling. Model: ${(1 / Math.tan(-g.gamma)).toFixed(2)} to 1, sinking ${Math.abs(g.climbFpm).toFixed(0)} ft/min.`);
  // ---- takeoff
  out.push('', `### Short-field takeoff (${POH.TAKEOFF.ref})`, '', '| Field ft | °C | Weight lb | Handbook ground roll / over 50 ft | Model | Difference |', '|---|---|---|---|---|---|');
  for (const [elev, tc, weight, roll, total, liftOff, at50] of POH.TAKEOFF.rows) {
    const r = flyTakeoff(F.createFlight({ fieldElevFt: elev, isaDevC: isaDev(elev, tc), weightLb: weight }), weight === 2300 ? {} : { rotateKias: liftOff - 6, v50: at50 });
    out.push(`| ${elev} | ${tc} | ${weight} | ${roll} / ${total} ft | ${r.groundRollFt.toFixed(0)} / ${r.totalFt.toFixed(0)} ft | ${pct(r.groundRollFt, roll)} / ${pct(r.totalFt, total)} |`);
  }
  // ---- landing
  out.push('', `### Short-field landing (${POH.LANDING.ref})`, '', '| Field ft | °C | Handbook ground roll / over 50 ft | Model | Difference |', '|---|---|---|---|---|');
  for (const [elev, tc, roll, total] of POH.LANDING.rows) {
    const r = flyLanding(F.createFlight({ fieldElevFt: elev, isaDevC: isaDev(elev, tc) }));
    out.push(`| ${elev} | ${tc} | ${roll} / ${total} ft | ${r.groundRollFt.toFixed(0)} / ${r.totalFt.toFixed(0)} ft | ${pct(r.groundRollFt, roll)} / ${pct(r.totalFt, total)} |`);
  }
  return out.join('\n');
}

export function coefficientsMarkdown() {
  const show = (v) => (Array.isArray(v) ? v.map((x) => +x.toPrecision(4)).join(', ') : String(+Number(v).toPrecision(5)));
  const label = { poh: 'POH', derived: 'POH-derived', estimated: 'estimated' };
  const rows = F.coefficientTable();
  const count = (s) => rows.filter((r) => r.source === s).length;
  const out = [`${rows.length} numbers: ${count('poh')} read from the handbook, ${count('derived')} derived from handbook numbers, ${count('estimated')} estimated. Values are in SI units unless the note says otherwise.`, '',
    '| Number | Value | Source | What it is, and the rule | POH page |', '|---|---|---|---|---|'];
  for (const r of rows) out.push(`| \`${r.name}\` | ${show(r.value)} | ${label[r.source]} | ${r.note} | ${r.ref} |`);
  return out.join('\n');
}

/** The document with its two generated blocks filled in. */
export function render(text) {
  const fill = (t, name, body) => {
    const begin = `<!-- ${name}:begin (generated by scripts/flight_doc.mjs) -->`, end = `<!-- ${name}:end -->`;
    const i = t.indexOf(begin), j = t.indexOf(end);
    if (i < 0 || j < 0) throw new Error(`missing ${name} block`);
    return `${t.slice(0, i + begin.length)}\n${body}\n${t.slice(j)}`;
  };
  return fill(fill(text, 'validation', validationMarkdown()), 'coefficients', coefficientsMarkdown());
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const before = readFileSync(DOC, 'utf8'), after = render(before);
  if (process.argv.includes('--check')) {
    if (before !== after) { console.error('docs/08_flight_model.md is stale: run npm run flight:doc'); process.exit(1); }
    console.log('docs/08_flight_model.md is up to date');
  } else { writeFileSync(DOC, after); console.log('wrote', DOC); }
}
