// FlyGACA C172N — the flight deck: the systems simulation and the flight model flown together.
//
// The systems simulation (sim.js) knows the engine, the electrics, the fuel, the vacuum and pitot-static
// systems and their faults; the flight model (flight.js) knows how the aircraft moves. Each step the engine
// of the one drives the propeller of the other, and the motion of the second is what the instruments of the
// first indicate. A fault set on the fault panel therefore acts on the flight: an engine that stops no
// longer pulls, a blocked pitot tube still misleads the airspeed indicator.

import { step, createState } from './sim.js';
import { createFlight, stepFlight, setInFlight, setOnGround, engineFromSim, engineAt, chargeAt, trim as trimFor, kcasFromKias, fullThrottleTorque } from './flight.js';

const NM = 1852;

/** Where a flight can begin: on the runway, or in the air at a height above the field (north: metres along the runway heading). */
export const STARTS = {
  runway: { kind: 'ground' },
  cruise: { kind: 'air', kias: 100, aglFt: 3000, flapDeg: 0, north: 0 },
  approach: { kind: 'air', kias: 70, aglFt: 600, flapDeg: 20, climbFpm: -450, north: -1.25 * NM },
};

/** The systems as they are just before takeoff: engine warm and running, electrics on. */
export function readySystems() {
  return createState({
    controls: { masterBat: true, masterAlt: true, avionics: true, ignition: 'BOTH', mixture: 1, throttle: 0, fuelSelector: 'BOTH', beacon: true, navLights: true },
    engine: { running: true, rpm: 700, oilTempF: 170, oilPress: 60 },
    vac: { suction: 4.9, gyro: 1 },
  });
}

/** A deck from a systems state and (optionally) a flight state. */
export function createDeck(sim, flight = createFlight()) {
  const deck = { sim, flight, controls: { aileron: 0, elevator: 0, rudder: 0, trim: 0, flapCommandDeg: flight.flapDeg, brake: 0, brakeLeft: 0, brakeRight: 0 } };
  writeTruth(deck);
  return deck;
}

/** What the engine of the systems simulation gives the propeller now: { engineOn, engine }. */
export function engineOf(deck) {
  const s = deck.sim, f = deck.flight;
  if (!s.engine.running || s.engine.power <= 0) return { engineOn: false, engine: null };
  return { engineOn: true, engine: engineFromSim(s.engine.power, s.controls.throttle, f.alt / 0.3048, f.isaDevC) };
}

function writeTruth(deck) {
  const s = deck.sim, o = deck.flight.out;
  // `out` is the flight's own record (speeds, heights, attitude: see flight.js): lessons read it
  s.flight.dynamic = { rpm: deck.flight.rpm, slip: o.slip ?? 0, stallWarning: !!o.stallWarning, stalled: !!o.stalled, out: o, flapCommandDeg: deck.controls.flapCommandDeg, trim: deck.controls.trim,
    north: deck.flight.north, east: deck.flight.east };
  s.flight.onGround = !!o.onGround;
  s.flight.bank = o.bankDeg ?? 0;
  s.flight.pitch = o.pitchDeg ?? 0;
  s.truth.ias = o.kias ?? 0;                       // what the pitot-static system is given: the indicated airspeed of the calibration table
  s.truth.alt = o.altFt ?? 0;
  s.truth.vs = o.vsFpm ?? 0;
  s.truth.heading = o.headingDeg || 360;
  s.truth.turnRate = o.turnRateDps ?? 0;
}

/**
 * Advance both by dt seconds. controls: { aileron, elevator, rudder, trim, flapCommandDeg, brake, brakeLeft, brakeRight };
 * what is left out keeps its last value.
 */
export function stepDeck(deck, controls = {}, dt = 1 / 60) {
  Object.assign(deck.controls, controls);
  const s = deck.sim, f = deck.flight;
  const { engineOn, engine } = engineOf(deck);
  if (engineOn && f.rpm < s.engine.rpm) f.rpm = s.engine.rpm;      // the starter has just handed the engine over
  // the flaps are electric (POH p.7-10): without power on the bus they stay where they are
  const flapCommandDeg = s.elec.busVolts > 18 ? deck.controls.flapCommandDeg : f.flapDeg;
  stepFlight(f, { ...deck.controls, flapCommandDeg, engineOn, engine }, dt);
  writeTruth(deck);
  step(s, dt);
  return deck;
}

/** Stand the aircraft on the runway (heading in degrees). The systems are left as they are. */
export function deckOnGround(deck, headingDeg = 0) {
  setOnGround(deck.flight, headingDeg);
  if (deck.sim.engine.running) deck.flight.rpm = deck.sim.engine.rpm;          // a running engine keeps turning
  deck.controls = { ...deck.controls, aileron: 0, elevator: 0, rudder: 0, trim: 0, flapCommandDeg: deck.flight.flapDeg, brake: 1 };
  writeTruth(deck);
  return deck;
}

/**
 * Put the aircraft in steady flight ({ kias, altFt, headingDeg, climbFpm, flapDeg }) with the engine running,
 * the throttle where that flight needs it and the trim holding it hands off. Returns the trim (see flight.trim()).
 */
export function deckInFlight(deck, o = {}) {
  const s = deck.sim, f = deck.flight;
  const tr = setInFlight(f, o);
  Object.assign(s.controls, { masterBat: true, masterAlt: true, ignition: 'BOTH', fuelSelector: s.controls.fuelSelector === 'OFF' ? 'BOTH' : s.controls.fuelSelector, throttle: tr.throttle });
  Object.assign(s.engine, { running: true, rpm: tr.rpm, oilTempF: Math.max(s.engine.oilTempF, 170), oilPress: 70 });
  Object.assign(s.vac, { suction: 4.9, gyro: 1, aiBank: 0, aiPitch: tr.theta * 57.2958, hiHeading: f.out.headingDeg || 360 });
  deck.controls = { aileron: tr.aileron, elevator: 0, rudder: tr.rudder, trim: tr.trim, flapCommandDeg: f.flapDeg, brake: 0, brakeLeft: 0, brakeRight: 0 };
  writeTruth(deck);
  const ps = s.lines;                                // start the pitot-static lines at the flight's pressures: no needle sweep
  step(s, 0);
  for (let i = 0; i < 40; i++) { writeTruth(deck); step(s, 0.05); }
  ps.pitot = s.lines.pitot; ps.static = s.lines.static;
  s.ind.vsi = tr.climbFpm;
  return tr;
}

/**
 * Begin a flight with a systems state: a deck at one of the STARTS (or a start of the same shape; fullThrottle
 * begins in a full-throttle climb), in given conditions ({ weightLb, cgFrac, isaDevC, windFromDeg, windKt, fieldElevFt }).
 * Returns { deck, trim, parking }: the trim setting that holds the start, and whether the parking brake is set.
 */
export function beginFlight(sim, start = STARTS.runway, conditions = {}) {
  const flight = createFlight({ ...conditions, flapDeg: start.flapDeg ?? 0 });
  const deck = createDeck(sim, flight);
  if (start.kind === 'air') {
    flight.north = start.north ?? 0;
    const altFt = flight.fieldElevFt + start.aglFt;
    const tr = deckInFlight(deck, { kias: start.kias, altFt, flapDeg: start.flapDeg ?? 0, climbFpm: start.climbFpm ?? 0, headingDeg: 0, engine: start.fullThrottle ? engineAt(1, chargeAt(altFt, flight.isaDevC)) : null });
    if (start.fullThrottle) sim.controls.throttle = 1;
    return { deck, trim: tr.trim, parking: false };
  }
  deckOnGround(deck, 0);
  // takeoff trim: where the trim holds the climb at 73 KIAS with full throttle (the TAKEOFF mark of the trim wheel)
  const charge = chargeAt(flight.fieldElevFt, flight.isaDevC);
  const trim = trimFor({ kcas: kcasFromKias(73), altFt: flight.fieldElevFt, isaDevC: flight.isaDevC, weightLb: flight.weightLb, cgFrac: flight.cgFrac, torque: fullThrottleTorque(charge) }).trim;
  deck.controls.trim = trim;
  return { deck, trim, parking: true };
}
