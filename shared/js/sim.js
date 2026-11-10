// FlyGACA C172N — shared documented educational systems simulation.
//
// DOM-free ES module: the viewer and the Node unit tests import the same code.
// Values tagged POH come from the Cessna Model 172N Pilot's Operating Handbook
// (1 July 1978, 1979 model) with page numbers. Everything else is an
// ILLUSTRATIVE model chosen to reproduce the POH behaviour qualitatively; it is
// not certified, not calibrated against a real aircraft, and must not be used
// for flight or maintenance decisions.

export const POH = {
  vne: 160, vno: 128, vfe: 85, va2300: 97,                // KIAS, p.2-4
  asiWhite: [41, 85], asiGreen: [47, 128], asiYellow: [128, 160], // p.2-5 Fig 2-2
  maxRpm: 2700,                                          // p.2-5
  staticRpm: [2280, 2400],                               // p.2-5 note (full throttle, carb heat off, full rich)
  tachGreenSL: [2100, 2450],                             // p.2-6 Fig 2-3
  oilTempMaxF: 245, oilTempGreen: [100, 245],            // p.2-5 / 2-6
  oilPressMin: 25, oilPressMax: 100, oilPressGreen: [60, 90], // p.2-5 / 2-6
  suctionGreen: [4.5, 5.4],                              // p.2-6, p.7-34
  magDropMax: 125, magDiffMax: 50, magCheckRpm: 1700,    // p.4-7, p.4-13
  carbHeatFullThrottleDrop: [100, 225],                  // p.7-19
  leanPeakDrop: [25, 50],                                // p.4-16
  fuelPerTankTotal: 21.5, fuelPerTankUsable: 20, fuelUnusablePerTank: 1.5, // p.7-21, p.2-6
  systemVolts: 28, batteryVolts: 24, alternatorAmps: 60, // p.7-23, p.7-25
};

// ------------------------------------------------------------ atmosphere / pitot-static
export const P0_INHG = 29.92;
const A0_KT = 661.4788;
export function staticPressure(altFt) {          // ISA, inHg
  return P0_INHG * Math.pow(1 - 6.8755856e-6 * altFt, 5.255876);
}
export function densityRatio(altFt) {             // ISA sigma
  return Math.pow(1 - 6.8755856e-6 * altFt, 4.255876);
}
export function altitudeFromPressure(p, setting = P0_INHG) {
  return (1 - Math.pow(p / setting, 1 / 5.255876)) / 6.8755856e-6;
}
export function impactPressure(kcas) {           // subsonic compressible, inHg
  const v = Math.max(0, kcas) / A0_KT;
  return P0_INHG * (Math.pow(1 + 0.2 * v * v, 3.5) - 1);
}
export function casFromImpact(qc) {
  if (qc <= 0) return 0;
  return A0_KT * Math.sqrt(5 * (Math.pow(qc / P0_INHG + 1, 2 / 7) - 1));
}

// POH p.5-9 Fig 5-1 (sheet 2): alternate static source, flaps UP, heater/vents and windows CLOSED.
export const ALT_STATIC_TABLE = [[40, 39], [50, 51], [60, 61], [70, 71], [80, 82], [90, 91], [100, 101], [110, 111], [120, 121], [130, 131], [140, 141]];
export function alternateStaticKias(kias) {
  const t = ALT_STATIC_TABLE;
  if (kias <= t[0][0]) return kias * (t[0][1] / t[0][0]);
  for (let i = 1; i < t.length; i++) {
    if (kias <= t[i][0]) {
      const [x0, y0] = t[i - 1], [x1, y1] = t[i];
      return y0 + ((y1 - y0) * (kias - x0)) / (x1 - x0);
    }
  }
  return kias + (t[t.length - 1][1] - t[t.length - 1][0]);
}

// ------------------------------------------------------------ engine helpers (illustrative)
export const ENGINE_MODEL = {
  propK: 1.522,          // power absorbed by the fixed-pitch prop at 2700 RPM, static (calibrated to ~2340 static RPM)
  propUnload: 0.0028,    // per knot: prop absorbs less power as airspeed rises (advance ratio)
  idleAir: 0.027,        // closed-throttle airflow fraction (~700 RPM static idle)
  throttleExp: 1.6,
  richAtFullSL: 1.10,    // full-rich at sea level is ~10% rich of best power
  leanMisfire: 0.62,     // mixture ratio below which combustion fails (idle cut-off is ~0)
  richMisfire: 1.85,
  singleMag: { L: 0.875, R: 0.865 }, // power factor running on one magneto (gives ~70-80 RPM drop at 1700)
  weakMag: 0.62,         // a weak magneto/plug set: drop well beyond 125 RPM
  carbHeatDensity: 0.12, // full carb heat reduces charge density ~12%
};

/** Relative fuel-air ratio (1.0 = best power). */
export function mixtureRatio(mixture, altFt, carbHeat = 0, ice = 0) {
  const sigma = densityRatio(altFt) * (1 - ENGINE_MODEL.carbHeatDensity * carbHeat);
  const m = Math.max(0, Math.min(1, mixture));
  return (ENGINE_MODEL.richAtFullSL * Math.pow(m, 0.7)) / Math.sqrt(sigma) * (1 + 0.45 * ice);
}
export function mixturePower(phi) {
  if (phi < ENGINE_MODEL.leanMisfire || phi > ENGINE_MODEL.richMisfire) return 0;
  return phi >= 1 ? 1 - 0.9 * (phi - 1) ** 2 : 1 - 2.2 * (1 - phi) ** 2;
}
export function throttleAirflow(t) {
  return ENGINE_MODEL.idleAir + (1 - ENGINE_MODEL.idleAir) * Math.pow(Math.max(0, Math.min(1, t)), ENGINE_MODEL.throttleExp);
}
export function equilibriumRpm(powerFrac, kias) {
  const k = ENGINE_MODEL.propK * Math.max(0.35, 1 - ENGINE_MODEL.propUnload * Math.max(0, kias));
  return 2700 * Math.cbrt(Math.max(0, powerFrac) / k);
}

/** Evaluate a POH magneto check (p.4-7 / p.4-13). */
export function evaluateMagCheck({ both, right, left }) {
  const dropR = both - right, dropL = both - left;
  const diff = Math.abs(dropR - dropL);
  const issues = [];
  if (dropR > POH.magDropMax) issues.push('drop_right_exceeds_125');
  if (dropL > POH.magDropMax) issues.push('drop_left_exceeds_125');
  if (diff > POH.magDiffMax) issues.push('differential_exceeds_50');
  if (dropR <= 5 || dropL <= 5) issues.push('no_drop_suspect_grounding');
  return { dropR, dropL, diff, pass: issues.length === 0, issues };
}

// ------------------------------------------------------------ state
export function createState(overrides = {}) {
  const s = {
    t: 0,
    controls: {
      masterBat: false, masterAlt: false, avionics: false,
      ignition: 'OFF',           // OFF | R | L | BOTH | START   (POH p.7-19)
      throttle: 0.0, mixture: 1.0, carbHeat: 0,
      fuelSelector: 'BOTH',      // BOTH | LEFT | RIGHT | OFF    (POH p.7-20)
      altStatic: false, pitotHeat: false,
      beacon: false, navLights: false, landingLight: false,
      altimeterSetting: 29.92,
      primeStrokes: 0,
    },
    flight: { onGround: true, iasTarget: 0, altTarget: 0, bank: 0, pitch: 0, oatF: 59 },
    faults: {
      pitot: 'none',             // none | ram | ram_and_drain
      staticBlocked: false,
      alternator: 'none',        // none | failed | overvoltage
      vacuum: false,
      carbIce: false,            // icing conditions present
      magneto: { L: 'ok', R: 'ok' }, // ok | weak | dead | ungrounded
    },
    truth: { ias: 0, alt: 0, vs: 0, heading: 360, turnRate: 0 },
    engine: { running: false, rpm: 0, oilTempF: 59, oilPress: 0, ice: 0, cranking: false, startTimer: 0,
      flooded: false, prime: 0, power: 0, phi: 1.1, roughness: 0, fuelFlowGph: 0, carbBowl: 1, magsFiring: [] },
    fuel: { left: 21.5, right: 21.5 },
    elec: { soc: 0.95, busVolts: 0, ammeter: 0, lowVoltage: false, acuTripped: false, altOnline: false, load: 0, ovTimer: 0, prevMaster: false },
    vac: { suction: 0, gyro: 0, aiBank: 0, aiPitch: 0, hiHeading: 360 },
    lines: { pitot: P0_INHG, static: P0_INHG },
    ind: { ias: 0, alt: 0, vsi: 0, rpm: 0, suction: 0, ammeter: 0, oilT: 59, oilP: 0, fuelL: 20, fuelR: 20, aiBank: 0, aiPitch: 0, hi: 360, tc: 0, tcFlag: true },
    events: [],
  };
  deepMerge(s, overrides);
  s.truth.alt = overrides.truth?.alt ?? s.flight.altTarget;
  s.truth.ias = overrides.truth?.ias ?? (s.flight.onGround ? 0 : s.flight.iasTarget);
  const ps = staticPressure(s.truth.alt);
  s.lines.static = ps;
  s.lines.pitot = ps + impactPressure(s.truth.ias);
  s.vac.hiHeading = s.truth.heading;
  computeIndications(s, 0);
  return s;
}

function deepMerge(a, b) {
  for (const [k, v] of Object.entries(b || {})) {
    if (v && typeof v === 'object' && !Array.isArray(v) && a[k] && typeof a[k] === 'object') deepMerge(a[k], v);
    else a[k] = v;
  }
  return a;
}

const lag = (x, target, dt, tau) => x + (target - x) * (1 - Math.exp(-dt / Math.max(1e-6, tau)));
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

/** Advance the simulation by dt seconds (sub-stepped for stability). */
export function step(s, dt) {
  let left = Math.max(0, dt);
  while (left > 1e-9) {
    const h = Math.min(0.05, left);
    stepOnce(s, h);
    left -= h;
  }
  return s;
}

function emit(s, type) {
  s.events.push({ t: Math.round(s.t * 10) / 10, type });
  if (s.events.length > 50) s.events.shift();
}

function stepOnce(s, dt) {
  const c = s.controls, f = s.flight, e = s.engine, el = s.elec, fl = s.fuel;
  s.t += dt;

  // ---------------- flight "truth"
  // Scenario driven: speed and height follow their targets (this is not a flight model). When a flight model
  // flies the aircraft (flight.dynamic, set by shared/js/flightdeck.js), it writes the truth and this is skipped.
  const tr = s.truth;
  if (!f.dynamic) {
    const iasT = f.onGround ? 0 : f.iasTarget;
    tr.ias = lag(tr.ias, iasT, dt, 2.5);
    const vsCmd = f.onGround ? 0 : clamp((f.altTarget - tr.alt) * 1.2, -800, 800);
    tr.vs = lag(tr.vs, vsCmd, dt, 2.0);
    tr.alt += (tr.vs / 60) * dt;
    if (f.onGround) { tr.alt = f.altTarget; tr.vs = 0; }
    const tas = tr.ias * (1 + 0.02 * tr.alt / 1000);
    tr.turnRate = f.onGround || tas < 20 ? 0 : (1091 * Math.tan((f.bank * Math.PI) / 180)) / tas; // deg/s
    tr.heading = ((tr.heading + tr.turnRate * dt) % 360 + 360) % 360 || 360;
  }

  // ---------------- electrical: master, loads, alternator, battery (POH p.7-23..7-26)
  const masterNow = c.masterBat;
  if (masterNow && !el.prevMaster) {           // recycling the master resets the ACU (POH p.7-26)
    if (el.acuTripped) emit(s, 'acu_reset');
    el.acuTripped = false;
    el.ovTimer = 0;
  }
  el.prevMaster = masterNow;
  // 24 V battery open-circuit voltage (illustrative curve; collapses when nearly flat so the contactor opens, POH p.7-25)
  const batOcv = 24.0 + 1.2 * el.soc - (el.soc < 0.15 ? (0.15 - el.soc) * 40 : 0);
  const contactorClosed = c.masterBat && batOcv > 18.5;
  const starterEngaged = contactorClosed && c.ignition === 'START';
  let load = 0;
  if (contactorClosed) {
    load = 3.0 + (c.avionics ? 8 : 0) + (c.beacon ? 2.5 : 0) + (c.navLights ? 3 : 0) + (c.landingLight ? 9 : 0) + (c.pitotHeat ? 4 : 0);
    if (starterEngaged) load += 150;
  }
  el.load = load;
  const altFail = s.faults.alternator === 'failed';
  const altCapable = contactorClosed && c.masterAlt && !el.acuTripped && !altFail;
  const altMax = altCapable ? 60 * clamp((e.rpm - 600) / 900, 0, 1) : 0; // 60-amp alternator (p.7-25); output vs RPM illustrative
  if (altCapable && s.faults.alternator === 'overvoltage' && altMax > 5) {
    el.ovTimer += dt;
    if (el.ovTimer > 2.0) { el.acuTripped = true; emit(s, 'acu_overvoltage_trip'); }
  }
  let batCurrent; // + = charging
  if (!contactorClosed) { batCurrent = 0; el.busVolts = 0; el.altOnline = false; }
  else if (altMax > 0) {
    const ovBoost = s.faults.alternator === 'overvoltage' && !el.acuTripped ? 1.6 : 0;
    const want = ovBoost ? 45 : clamp(40 * (1 - el.soc) + 1, 0, 60); // tapering charge rate (illustrative)
    const avail = altMax - load;
    batCurrent = Math.min(want, avail);
    el.busVolts = batCurrent >= 0 ? 28.0 + ovBoost * 2 : Math.max(0, batOcv + 0.05 * batCurrent);
    el.altOnline = true;
  } else {
    batCurrent = -load;
    el.busVolts = Math.max(0, batOcv - 0.05 * load);
    el.altOnline = false;
  }
  el.ammeter = lag(el.ammeter, batCurrent, dt, 0.4);
  el.soc = clamp(el.soc + (batCurrent * dt) / (3600 * 13) * (batCurrent > 0 ? 0.85 : 1), 0, 1); // 13 Ah, illustrative
  el.lowVoltage = contactorClosed && el.busVolts < 24.8; // illustrative threshold

  // ---------------- fuel supply (POH p.7-20/7-21)
  const usable = (q) => q > POH.fuelUnusablePerTank + 1e-6;
  const sel = c.fuelSelector;
  const feeds = sel === 'BOTH' ? ['left', 'right'] : sel === 'LEFT' ? ['left'] : sel === 'RIGHT' ? ['right'] : [];
  const live = feeds.filter((k) => usable(fl[k]));
  const supply = live.length > 0;

  // ---------------- ignition (POH p.7-18/7-19): dual magneto, switch OFF-R-L-BOTH-START
  const mf = s.faults.magneto;
  const selected = { OFF: [], R: ['R'], L: ['L'], BOTH: ['L', 'R'], START: ['L', 'R'] }[c.ignition] || [];
  const firing = new Set(selected);
  for (const m of ['L', 'R']) if (mf[m] === 'ungrounded') firing.add(m); // P-lead open: magneto stays "hot"
  for (const m of ['L', 'R']) if (mf[m] === 'dead') firing.delete(m);
  e.magsFiring = [...firing].sort();
  let ignitionFactor = 0;
  if (firing.size === 2) ignitionFactor = (mf.L === 'weak' || mf.R === 'weak') ? 0.97 : 1;
  else if (firing.size === 1) {
    const m = [...firing][0];
    ignitionFactor = mf[m] === 'weak' ? ENGINE_MODEL.weakMag : ENGINE_MODEL.singleMag[m];
  }

  // ---------------- carburetor ice (POH p.3-16, p.4-16)
  const heatLevel = clamp(c.carbHeat, 0, 1);
  if (s.faults.carbIce && e.rpm > 300) e.ice = clamp(e.ice + dt * 0.006 * (1 - heatLevel) * (1.2 - c.throttle * 0.5), 0, 1);
  if (heatLevel > 0) e.ice = clamp(e.ice - dt * 0.05 * heatLevel, 0, 1);
  if (!s.faults.carbIce && heatLevel === 0) e.ice = clamp(e.ice - dt * 0.002, 0, 1);
  const melting = heatLevel > 0.5 && e.ice > 0.05;

  // ---------------- combustion and RPM
  e.phi = mixtureRatio(c.mixture, tr.alt, heatLevel, e.ice) * (e.flooded ? 2.5 : 1);
  const sigma = densityRatio(tr.alt) * (1 - ENGINE_MODEL.carbHeatDensity * heatLevel);
  const iceFactor = 1 - 0.65 * e.ice;
  // carb bowl keeps the engine running a few seconds after supply stops
  const ffDemand = e.running ? 0.6 + 11.0 * throttleAirflow(c.throttle) * sigma * Math.min(e.phi, 1.6) / 1.1 * iceFactor : 0;
  if (supply) e.carbBowl = clamp(e.carbBowl + dt / 2, 0, 1);
  else e.carbBowl = clamp(e.carbBowl - (ffDemand / 3600) * dt / 0.02 - (e.cranking ? dt / 20 : 0), 0, 1);
  const fuelOk = e.carbBowl > 0.02;
  const mixP = mixturePower(e.phi);
  const canFire = fuelOk && mixP > 0 && ignitionFactor > 0;

  // starter, priming and flooding (POH p.4-7, p.4-11)
  e.cranking = starterEngaged && el.busVolts > 16.8; // a flat battery cannot crank
  if (c.primeStrokes > 0) {
    e.prime += c.primeStrokes; c.primeStrokes = 0;
    if (e.prime > 8) { e.flooded = true; emit(s, 'flooded'); }
  }
  if (e.cranking && c.mixture < 0.05 && c.throttle > 0.9 && e.flooded) { // clearing procedure: mixture idle cut-off, full throttle, crank
    e.prime = Math.max(0, e.prime - dt * 2.5);
    if (e.prime <= 3) { e.flooded = false; emit(s, 'flood_cleared'); }
  }
  if (!e.running && e.cranking && canFire && !e.flooded) {
    const cold = e.oilTempF < 100;
    const rate = cold ? (e.prime >= 2 ? 1 : 0.12) : 1;
    e.startTimer += dt * rate;
    if (e.startTimer > 1.2) { e.running = true; e.startTimer = 0; e.prime = 0; emit(s, 'engine_started'); }
  } else if (!e.cranking) e.startTimer = 0;

  if (e.running && !canFire) {
    e.running = false;
    emit(s, !fuelOk ? 'engine_stopped_fuel' : ignitionFactor === 0 ? 'engine_stopped_ignition' : 'engine_stopped_mixture');
  }
  // windmilling restart in flight when fuel returns
  if (!e.running && canFire && !e.flooded && e.rpm > 350 && tr.ias > 50) { e.running = true; emit(s, 'engine_restarted'); }

  e.roughness = e.running ? clamp((firing.size === 1 && mf[[...firing][0]] === 'weak' ? 0.6 : 0) + (e.ice > 0.5 ? (e.ice - 0.5) * 1.6 : 0) + (melting ? 0.35 : 0) + (e.phi < 0.75 ? (0.75 - e.phi) * 4 : 0), 0, 1) : 0;
  e.power = e.running ? throttleAirflow(c.throttle) * sigma * mixP * ignitionFactor * iceFactor : 0;
  if (f.dynamic && !e.cranking) e.rpm = Math.max(0, f.dynamic.rpm);   // the flight model's propeller turns the engine, running or windmilling
  else {
    let rpmTarget;
    if (e.running) rpmTarget = equilibriumRpm(e.power, tr.ias);
    else if (e.cranking) rpmTarget = 160;
    else rpmTarget = tr.ias > 40 ? (tr.ias - 40) * 20 : 0; // windmilling propeller (illustrative)
    const tau = e.running ? 0.7 : e.cranking ? 0.4 : 1.6;
    e.rpm = Math.max(0, lag(e.rpm, rpmTarget, dt, tau));
  }
  if (e.rpm < 2) e.rpm = 0;
  e.fuelFlowGph = e.running ? ffDemand : 0;

  // fuel burn
  if (e.fuelFlowGph > 0 && live.length) {
    const burn = (e.fuelFlowGph / 3600) * dt;
    for (const k of live) fl[k] = Math.max(POH.fuelUnusablePerTank, fl[k] - burn / live.length);
  }

  // oil temperature and pressure (illustrative, POH limits p.2-5)
  const oilTarget = e.running ? s.flight.oatF + 30 + 120 * Math.pow(e.rpm / 2700, 1.5) - (tr.ias > 60 ? 0.15 * (tr.ias - 60) : 0) : s.flight.oatF;
  e.oilTempF = lag(e.oilTempF, oilTarget, dt, e.running ? 240 : 900);
  const coldBonus = clamp((120 - e.oilTempF) * 0.25, 0, 20);
  const oilPTarget = e.rpm > 300 ? clamp(18 + 55 * (e.rpm / 2400) + coldBonus, 0, 115) : 0;
  e.oilPress = lag(e.oilPress, oilPTarget, dt, 0.8);

  // ---------------- vacuum system and gyros (POH p.7-32..7-34)
  const vac = s.vac;
  const suctionTarget = s.faults.vacuum ? 0 : clamp(((e.rpm - 300) / 1300) * 5.0, 0, 5.0);
  vac.suction = lag(vac.suction, suctionTarget, dt, 0.6);
  const spinTarget = clamp(vac.suction / 4.5, 0, 1);
  vac.gyro = lag(vac.gyro, spinTarget, dt, spinTarget > vac.gyro ? 40 : 120);
  if (vac.gyro > 0.8) {
    vac.aiBank = lag(vac.aiBank, f.bank, dt, 0.3);
    vac.aiPitch = lag(vac.aiPitch, f.pitch, dt, 0.3);
    vac.hiHeading = ((vac.hiHeading + tr.turnRate * dt) % 360 + 360) % 360 || 360;
  } else {
    // spinning down: slow precession / tumble (illustrative); a stopped gyro just stays where it is
    const k = vac.gyro > 0.05 ? (0.8 - vac.gyro) / 0.8 : 0;
    vac.aiBank = clamp(vac.aiBank + dt * k * 1.5, -35, 35);
    vac.aiPitch = clamp(vac.aiPitch - dt * k * 0.4, -15, 15);
    vac.hiHeading = ((vac.hiHeading + tr.turnRate * dt * (1 - k) + dt * k * 0.8) % 360 + 360) % 360 || 360;
  }

  // ---------------- pitot-static lines (POH p.3-8, p.5-9, p.7-31)
  const ps = staticPressure(tr.alt);
  const qc = impactPressure(tr.ias);
  const ln = s.lines;
  if (s.faults.pitot === 'none') ln.pitot = lag(ln.pitot, ps + qc, dt, 0.15);
  else if (s.faults.pitot === 'ram') ln.pitot = lag(ln.pitot, ps, dt, 4.0); // drain hole bleeds the line to ambient
  // 'ram_and_drain': trapped pressure, no update
  let staticSource = null;
  if (c.altStatic) {
    const kias = tr.ias;
    staticSource = ps - (impactPressure(alternateStaticKias(kias)) - impactPressure(kias));
  } else if (!s.faults.staticBlocked) staticSource = ps;
  if (staticSource !== null) ln.static = lag(ln.static, staticSource, dt, 0.15);

  computeIndications(s, dt);
}

export function computeIndications(s, dt) {
  const ind = s.ind, el = s.elec, e = s.engine, ln = s.lines, vac = s.vac;
  const prevPa = ind.pressureAlt ?? altitudeFromPressure(ln.static);
  ind.ias = Math.max(0, casFromImpact(ln.pitot - ln.static));
  ind.pressureAlt = altitudeFromPressure(ln.static);
  ind.alt = altitudeFromPressure(ln.static, s.controls.altimeterSetting);
  if (dt > 0) {
    // VSI senses the rate of change of static pressure (independent of the Kollsman setting), with a ~3 s lag
    const raw = ((ind.pressureAlt - prevPa) / dt) * 60;
    ind.vsi = lag(ind.vsi, clamp(raw, -2500, 2500), dt, 3.0);
  }
  ind.rpm = e.rpm;                       // mechanical tachometer
  ind.oilP = e.oilPress;                 // direct-reading
  const powered = el.busVolts > 18;
  ind.oilT = powered ? e.oilTempF : 50;  // electric gauges drop to the stop without power
  ind.fuelL = powered ? Math.max(0, s.fuel.left - POH.fuelUnusablePerTank) : 0;
  ind.fuelR = powered ? Math.max(0, s.fuel.right - POH.fuelUnusablePerTank) : 0;
  ind.ammeter = el.ammeter;
  ind.suction = vac.suction;
  ind.aiBank = vac.aiBank;
  ind.aiPitch = vac.aiPitch;
  ind.hi = vac.hiHeading;
  ind.tcFlag = !powered;                 // electric turn coordinator
  ind.tc = powered ? clamp(s.truth.turnRate / 3, -1.6, 1.6) : 0; // 1.0 = standard-rate mark
  const dyn = s.flight.dynamic;
  ind.slip = dyn ? dyn.slip : 0;                       // the ball: + to the right (needs no power)
  ind.stallWarning = !!(dyn && dyn.stallWarning);      // pneumatic horn: independent of the electrical system (POH p.7-34)
  ind.lowVoltage = el.lowVoltage;
}

/** Plain-language status codes the UI translates; also handy for tests. */
export function annunciations(s) {
  const out = [];
  const ind = s.ind, e = s.engine;
  if (s.elec.lowVoltage) out.push('low_voltage');
  if (e.running && ind.oilP < POH.oilPressMin) out.push('oil_pressure_low');
  if (ind.oilT > POH.oilTempMaxF) out.push('oil_temp_high');
  if (ind.rpm > POH.maxRpm + 5) out.push('overspeed');
  if (e.running && e.rpm > 1500 && ind.suction < POH.suctionGreen[0]) out.push('suction_low'); // checked at run-up/cruise RPM
  if (e.roughness > 0.3) out.push('engine_rough');
  if (e.flooded) out.push('flooded');
  if (e.running && ind.ias > POH.vne) out.push('vne_exceeded');
  if ((s.engine.magsFiring || []).length && s.controls.ignition === 'OFF') out.push('hot_magneto');
  return out;
}
