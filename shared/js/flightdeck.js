// FlyGACA C172N — the flight deck: the systems simulation and the flight model flown together.
//
// The systems simulation (sim.js) knows the engine, the electrics, the fuel, the vacuum and pitot-static
// systems and their faults; the flight model (flight.js) knows how the aircraft moves. Each step the engine
// of the one drives the propeller of the other, and the motion of the second is what the instruments of the
// first indicate. A fault set on the fault panel therefore acts on the flight: an engine that stops no
// longer pulls, a blocked pitot tube still misleads the airspeed indicator.

import { step } from './sim.js';
import { createFlight, stepFlight, setInFlight, setOnGround, engineFromSim } from './flight.js';

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
  s.flight.dynamic = { rpm: deck.flight.rpm, slip: o.slip ?? 0, stallWarning: !!o.stallWarning, stalled: !!o.stalled };
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
  stepFlight(f, { ...deck.controls, engineOn, engine }, dt);
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
