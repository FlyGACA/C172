// FlyGACA C172N — a scripted pilot for the flight model.
//
// It holds what a pilot holds: a pitch attitude, an airspeed, a rate of climb or an altitude with the
// elevator; a bank angle or a heading with the ailerons; the ball in the middle with the rudder. The tests
// fly the handbook's figures with it and the lessons use it to demonstrate an exercise. It reads only what
// the instruments show (flight.out) and returns wheel and pedal positions.

import { FM, stepFlight, setInFlight, engineAt, chargeAt, propellerBalance } from './flight.js';

const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const D2R = Math.PI / 180;
const wrap = (deg) => ((deg + 540) % 360) - 180;

/**
 * The pitch attitude (degrees) that holds a rate of climb or descent at the present airspeed and flap setting
 * without load: the angle of attack that carries the weight, plus the angle of the flight path. This is the
 * picture a pilot learns for the round-out, the hold-off and the rotation.
 */
export function pitchFor(f, vsFpm = 0) {
  const o = f.out;
  const v = Math.max(15, o.kcas) * 0.514444;
  const need = (f.weightLb * 0.45359237 * 9.80665) / (0.5 * 1.225 * v * v * FM.wingArea.v);
  const angles = FM.flapAngles.v, add = FM.dCL0Flap.v;
  let i = 1; while (i < angles.length - 1 && angles[i] < f.flapDeg) i++;
  const flaps = add[i - 1] + ((add[i] - add[i - 1]) * (clamp(f.flapDeg, angles[i - 1], angles[i]) - angles[i - 1])) / (angles[i] - angles[i - 1]);
  const alpha = (need - FM.CL0.v - flaps) / FM.CLalpha.v;
  const path = Math.asin(clamp((vsFpm * 0.00508) / Math.max(10, o.ktas * 0.514444), -0.5, 0.5));
  return (alpha + path) / D2R;
}

export function createPilot() {
  return { iPitch: 0, iRoll: 0, iBall: 0, thetaCmd: null, vsInt: 0, speedInt: 0, lastKias: null, accel: 0 };
}

/**
 * One step of the pilot.
 * target: elevator axis  { pitchDeg } | { kias } | { vsFpm } | { altFt } | { elevator } (a fixed wheel position)
 *         aileron axis   { bankDeg } | { headingDeg } | { aileron }
 *         rudder axis    { rudder } | coordinate (default): ball in the middle in the air, the heading on the ground
 *         limits         { maxPitchDeg, minPitchDeg, maxBankDeg }
 * Returns { elevator, aileron, rudder }.
 */
export function pilotStep(p, f, target, dt) {
  const o = f.out;
  const out = { elevator: 0, aileron: 0, rudder: 0 };
  const hold = o.onGround ? { aileron: 0, rudder: 0 } : propellerBalance(f);      // what the propeller asks of the hand and the foot
  // ---------------- elevator
  if (target.elevator != null) { out.elevator = target.elevator; p.thetaCmd = null; p.iPitch = 0; }
  else {
    const hi = target.maxPitchDeg ?? 20, lo = target.minPitchDeg ?? -15;
    if (p.thetaCmd == null) { p.thetaCmd = o.pitchDeg; p.vsInt = 0; p.speedInt = 0; }
    let cmd;
    if (target.pitchDeg != null) cmd = target.pitchDeg;
    else if (target.kias != null) {
      // too fast: raise the nose. The rate of change of speed damps the long exchange of speed and height.
      if (p.lastKias != null && dt > 0) p.accel += ((o.kias - p.lastKias) / dt - p.accel) * Math.min(1, dt / 0.5);
      p.lastKias = o.kias;
      const err = o.kias - target.kias;
      p.speedInt = clamp(p.speedInt + 0.4 * err * dt, -30, 30);
      cmd = p.thetaCmd + 1.0 * err + 1.2 * p.accel + p.speedInt;
      cmd = clamp(cmd, lo, hi);
      out.thetaCmd = cmd;
    } else {
      const vsTarget = target.vsFpm != null ? target.vsFpm : clamp(6 * (target.altFt - o.altFt), -700, 700);
      const err = vsTarget - o.vsFpm;
      p.vsInt = clamp(p.vsInt + 0.0035 * err * dt, -15, 15);
      cmd = clamp(p.thetaCmd + 0.0045 * err + p.vsInt, lo, hi);
    }
    const e = cmd - o.pitchDeg;
    p.iPitch = clamp(p.iPitch + 0.035 * e * dt, -0.9, 0.9);
    out.elevator = clamp(0.045 * e - 0.55 * f.q + p.iPitch, -1, 1);
    if (Math.abs(out.elevator) >= 1) p.iPitch -= 0.035 * e * dt;          // on the stop: do not wind up
  }
  // ---------------- ailerons
  if (target.aileron != null) { out.aileron = target.aileron; p.iRoll = 0; }
  else if (o.onGround && o.wheels >= 2) { out.aileron = 0; p.iRoll = 0; }
  else {
    const limit = target.maxBankDeg ?? 25;
    const bank = target.headingDeg != null ? clamp(1.2 * wrap(target.headingDeg - o.headingDeg), -limit, limit) : (target.bankDeg ?? 0);
    const e = bank - o.bankDeg;
    p.iRoll = clamp(p.iRoll + 0.012 * e * dt, -0.5, 0.5);
    out.aileron = clamp(hold.aileron + 0.03 * e - 0.28 * f.p + p.iRoll, -1, 1);
  }
  // ---------------- rudder
  if (target.rudder != null) { out.rudder = target.rudder; p.iBall = 0; }
  else if (o.onGround) {
    const e = wrap((target.headingDeg ?? target.runwayDeg ?? o.headingDeg) - o.headingDeg);
    out.rudder = clamp(0.12 * e - 1.2 * f.r, -1, 1);
    p.iBall = 0;
  } else {
    // step on the ball, slowly; and damp the yaw the turn does not ask for. The rudder bites with the square of the speed.
    const v = Math.max(20, o.ktas * 0.514444);
    const gain = clamp((70 / Math.max(40, o.kias)) ** 2, 0.25, 2.5);
    const turning = (9.80665 * Math.sin(o.bankDeg * D2R)) / v;
    p.iBall = clamp(p.iBall + 4 * gain * o.slip * dt, -0.9, 0.9);
    out.rudder = clamp(hold.rudder + p.iBall + 0.8 * gain * o.slip - 1.5 * gain * (f.r - turning), -1, 1);
  }
  return out;
}

// ---------------------------------------------------------------------------------- handbook procedures
const FT = 0.3048;

/**
 * The handbook's short-field takeoff (POH p.5-12): flaps up, full throttle before brake release, lift-off at
 * `liftOffKias`, `v50` at 50 ft. `f` stands on the runway. Returns the ground roll and the distance to 50 ft (ft).
 */
export function flyTakeoff(f, { rotateKias = 46, liftOffPitchDeg = 12, v50 = 59, dt = 1 / 120, onStep = null } = {}) {
  const p = createPilot();
  const engine = engineAt(1, chargeAt(f.fieldElevFt, f.isaDevC));
  const heading = f.out.headingDeg;
  let released = null, start = [0, 0], phase = 'run', roll = null, liftOffKias = null;
  const along = () => ((f.north - start[0]) * Math.cos(heading * D2R) + (f.east - start[1]) * Math.sin(heading * D2R)) / FT;
  for (let i = 0; i < 180 / dt; i++) {
    const o = f.out;
    let c = { elevator: 0, aileron: 0, rudder: 0 }, brake = 1;
    if (f.t >= 3) {                                    // three seconds for the engine to reach its static RPM
      brake = 0;
      if (released == null) { released = f.t; start = [f.north, f.east]; }
      if (phase === 'run' && o.kias >= rotateKias) phase = 'rotate';
      if (phase === 'rotate' && o.wheels === 0 && o.aglFt > 1.5) phase = 'climb';
      const target = phase === 'run' ? { elevator: 0, headingDeg: heading }
        : phase === 'rotate' ? { pitchDeg: liftOffPitchDeg, headingDeg: heading }
          : { pitchDeg: clamp(16 + 1.5 * (o.kias - v50), liftOffPitchDeg - 0.5, 19), headingDeg: heading };
      c = pilotStep(p, f, target, dt);
    }
    stepFlight(f, { ...c, trim: 0, brake, engineOn: true, engine, flapCommandDeg: 0 }, dt);
    if (released != null && roll == null && f.out.wheels === 0) { roll = along(); liftOffKias = f.out.kias; }
    if (roll != null && f.out.wheels > 0 && f.out.aglFt < 1) roll = null;          // touched again: not off yet
    if (onStep) onStep(f, phase);
    if (f.out.aglFt >= 50) return { groundRollFt: roll, totalFt: along(), liftOffKias, kiasAt50: f.out.kias, seconds: f.t - released };
  }
  return { groundRollFt: roll, totalFt: null, liftOffKias, kiasAt50: null, seconds: null };
}

/**
 * The handbook's short-field landing (POH p.5-21): flaps 40, power off, 60 KIAS at 50 ft, maximum braking; the
 * flaps are raised on the ground for the brakes to bite (POH p.4-9). `f` is put on the approach above the field.
 * Returns the ground roll, the distance from 50 ft (ft) and how it touched down.
 */
export function flyLanding(f, { approachKias = 60, touchdownKias = 47, flareFt = 35, dt = 1 / 120, onStep = null } = {}) {
  const idle = engineAt(0, chargeAt(f.fieldElevFt, f.isaDevC));
  const tr = setInFlight(f, { kias: approachKias, altFt: f.fieldElevFt + 115, flapDeg: 40, engine: idle, headingDeg: f.out.headingDeg ?? 0 });
  const p = createPilot();
  const heading = f.out.headingDeg;
  let at50 = null, touch = null, phase = 'approach', flap = 40, touchKias = null, touchFpm = null, tTouch = 0;
  const pos = () => f.north * Math.cos(heading * D2R) + f.east * Math.sin(heading * D2R);
  for (let i = 0; i < 180 / dt; i++) {
    const o = f.out;
    if (at50 == null && o.aglFt <= 50) at50 = pos();
    let target, brake = 0;
    if (phase === 'approach') { target = { kias: approachKias, bankDeg: 0 }; if (o.aglFt <= flareFt) phase = 'flare'; }
    if (phase === 'flare') {
      // round out: the sink is taken off as the ground comes near; then the aircraft is held off a foot up while the speed goes
      const sink = o.kias > touchdownKias ? -Math.min(700, 22 * Math.max(0, o.aglFt - 1)) : -90;
      target = { pitchDeg: Math.min(12, pitchFor(f, sink) + 0.004 * (sink - o.vsFpm)), bankDeg: 0 };
      if (o.wheels > 0) { phase = 'roll'; touch = pos(); touchKias = o.kias; touchFpm = o.vsFpm; tTouch = f.t; }
    }
    if (phase === 'roll') {
      target = { elevator: o.wheels >= 3 ? 1 : -0.15, headingDeg: heading };      // nose wheel down, then the wheel fully back
      brake = f.t - tTouch > 1 ? 1 : 0;
      flap = 0;
      if (o.groundSpeedKt < 0.5) break;
    }
    const c = pilotStep(p, f, target, dt);
    stepFlight(f, { ...c, trim: tr.trim, brake, engineOn: true, engine: idle, flapCommandDeg: flap }, dt);
    if (onStep) onStep(f, phase);
  }
  return { groundRollFt: touch == null ? null : (pos() - touch) / FT, totalFt: at50 == null ? null : (pos() - at50) / FT, touchdownKias: touchKias, touchdownFpm: touchFpm };
}

/**
 * A power-off stall as it is taught: throttle closed, the altitude held until the wing stalls, the wheel held back
 * for `holdSeconds`, then the recovery (wheel forward, full throttle, back to a climb). `f` is put in level flight.
 * Returns the speeds of the warning and of the stall, the load factor at the stall and the height the recovery lost.
 */
export function flyStall(f, { flapDeg = 0, holdSeconds = 6, altFt = 3000, entryKias = flapDeg ? 65 : 70, dt = 1 / 60, onStep = null } = {}) {
  const tr = setInFlight(f, { kias: entryKias, altFt, flapDeg });
  const p = createPilot(), charge = chargeAt(altFt, f.isaDevC);
  const r = { maxAlphaDeg: 0 };
  let phase = 'entry', tStall = 0, tRecover = 0, lowest = Infinity;
  for (let i = 0; i < 150 / dt; i++) {
    let target, engine = engineAt(0, charge);
    if (phase === 'entry') target = { altFt, bankDeg: 0, maxPitchDeg: 30 };
    else if (phase === 'hold') target = { elevator: 1, bankDeg: 0 };
    else { engine = engineAt(1, charge); target = f.out.kias < 58 ? { pitchDeg: -3, bankDeg: 0 } : { pitchDeg: 6, bankDeg: 0 }; }
    stepFlight(f, { ...pilotStep(p, f, target, dt), trim: tr.trim, engineOn: true, engine, flapCommandDeg: flapDeg }, dt);
    const o = f.out;
    if (r.warningKcas == null && o.stallWarning) r.warningKcas = o.kcas;
    if (phase === 'entry' && o.stalled) { phase = 'hold'; tStall = f.t; Object.assign(r, { stallKcas: o.kcas, stallKias: o.kias, loadFactor: o.loadFactor, pitchAtStallDeg: o.pitchDeg, altAtStallFt: o.altFt }); }
    if (phase === 'hold') {
      r.maxAlphaDeg = Math.max(r.maxAlphaDeg, o.alphaDeg);
      r.lowestPitchDeg = Math.min(r.lowestPitchDeg ?? 99, o.pitchDeg);
      if (f.t - tStall > holdSeconds) { phase = 'recover'; tRecover = f.t; Object.assign(r, { heldLossFt: r.altAtStallFt - o.altFt, altAtRecoveryFt: o.altFt, alphaHeldDeg: o.alphaDeg, sinkHeldFpm: o.vsFpm }); }
    }
    if (phase === 'recover') {
      lowest = Math.min(lowest, o.altFt);
      if (f.t - tRecover > 2 && o.vsFpm > 0 && !o.stalled) { r.recoveryLossFt = r.altAtRecoveryFt - lowest; r.recoverySeconds = f.t - tRecover; r.alphaStallDeg = o.alphaStallDeg; return r; }
    }
    if (onStep) onStep(f, phase);
  }
  return r;
}
