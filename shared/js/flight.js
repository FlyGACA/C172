// FlyGACA C172N — a small six-degree-of-freedom flight model for teaching.
//
// DOM-free ES module: the viewer and the Node unit tests import the same code.
//
// What it is: rigid-body equations of motion with a coefficient model of the wing, tail, propeller and
// landing gear, small enough to read in one sitting. Its numbers come from two places, and every one of
// them says which (FM below):
//   poh        read from the Cessna Model 172N Pilot's Operating Handbook, page given;
//   derived    worked out from handbook numbers by the rule stated in the note (a stall speed gives a
//              maximum lift coefficient, the cruise table gives the propeller's power coefficient, ...);
//   estimated  a representative value for an aircraft of this type. Not from the handbook, not measured.
// What it is not: it has no certified fidelity. It reproduces the handbook's published performance within
// the tolerances its tests state, and behaves plausibly between those points. It does not model spins,
// icing, turbulence or structural limits. It must not be used to plan or judge a real flight.

import { densityRatio, throttleAirflow } from './sim.js';

const D2R = Math.PI / 180, R2D = 180 / Math.PI;
const G = 9.80665, FT = 0.3048, KT = 0.514444, LB = 0.45359237, HP = 745.69987, IN = 0.0254;
const RHO0 = 1.225;
const SLUG_FT2 = 1.3558179;
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const lerp = (a, b, t) => a + (b - a) * t;

const c = (v, src, note, ref = '') => ({ v, src, note, ref });

/** Every number of the model with its provenance. Code reads K (the plain values, below). */
export const FM = {
  // ---- size and mass
  wingArea: c(174 * FT * FT, 'derived', 'maximum weight 2300 lb divided by the wing loading 13.2 lb/sq ft = 174 sq ft', 'p.1-5'),
  wingSpan: c(36 * FT, 'poh', 'wing span 36 ft (with strobe lights)', 'p.1-2 Fig 1-1'),
  propDiameter: c(75 * IN, 'poh', 'propeller diameter 75 in (maximum)', 'p.1-3, 2-5'),
  ratedPower: c(160 * HP, 'poh', '160 BHP at 2700 RPM', 'p.1-3, 2-5'),
  ratedRpm: c(2700, 'poh', 'maximum engine speed 2700 RPM', 'p.2-5'),
  maxWeightLb: c(2300, 'poh', 'maximum takeoff and landing weight, normal category', 'p.1-5, 2-6'),
  wheelBase: c(65 * IN, 'poh', 'wheel base 65 in', 'p.1-2 Fig 1-1'),
  wheelTrack: c((8 * 12 + 4.5) * IN, 'poh', 'main wheel track 8 ft 4½ in', 'p.1-2 Fig 1-1'),
  Ixx: c(948 * SLUG_FT2, 'estimated', 'roll inertia at maximum weight; a textbook value for the type'),
  Iyy: c(1346 * SLUG_FT2, 'estimated', 'pitch inertia at maximum weight; a textbook value for the type'),
  Izz: c(1967 * SLUG_FT2, 'estimated', 'yaw inertia at maximum weight; a textbook value for the type'),
  cgHeight: c(1.15, 'estimated', 'height of the centre of gravity above the ground at rest (m)'),
  wingAboveCg: c(1.1, 'estimated', 'height of the wing above the centre of gravity (m): for the ground effect'),
  groundPitchDeg: c(4.7, 'derived', 'attitude of the fuselage reference line at rest, from the three-view', 'p.1-2 Fig 1-1'),
  mainGearStation: c(58.0, 'estimated', 'fuselage station of the main wheel axle (in), from the three-view'),
  cgStationFwd: c(38.5, 'poh', 'forward centre of gravity limit at 2300 lb: 38.5 in aft of datum', 'p.2-7, p.6-12 Fig 6-8'),
  cgStationFwdLight: c(35.0, 'poh', 'forward centre of gravity limit at 1950 lb or less: 35.0 in aft of datum, with a straight line to the limit at 2300 lb', 'p.2-7, p.6-12 Fig 6-8'),
  cgStationAft: c(47.3, 'poh', 'aft centre of gravity limit at all weights: 47.3 in aft of datum', 'p.2-7, p.6-12 Fig 6-8'),
  macLeadingEdge: c(25.9, 'estimated', 'station of the leading edge of the mean aerodynamic chord (in); a value for the type'),
  // ---- lift
  CLalpha: c(4.6, 'estimated', 'lift curve slope per radian, from the aspect ratio 7.4'),
  CL0: c(0.20, 'estimated', 'lift coefficient with the fuselage reference line along the flight path, flaps up'),
  flapAngles: c([0, 10, 20, 30, 40], 'poh', 'flap settings 0 to 40 degrees', 'p.7-10'),
  dCL0Flap: c([0, 0.25, 0.45, 0.60, 0.70], 'estimated', 'lift added by the flaps at a given angle of attack'),
  CLmaxAft: c([1.562, 1.768, 1.851, 1.934, 2.017], 'derived', 'from the stall speeds 50, 47 and 44 KCAS at 2300 lb, most rearward centre of gravity, flaps up, 10 and 40 degrees; 20 and 30 degrees interpolated', 'p.5-11 Fig 5-3'),
  CLmaxFwd: c([1.390, 1.501, 1.590, 1.679, 1.768], 'derived', 'from the stall speeds 53, 51 and 47 KCAS at 2300 lb, most forward centre of gravity; 20 and 30 degrees interpolated', 'p.5-11 Fig 5-3'),
  stallWarningMargin: c(0.80, 'derived', 'the stall warning horn sounds 5 to 10 knots above the stall: at about 0.80 of the maximum lift coefficient', 'p.7-34'),
  stallBreakDeg: c(3.0, 'estimated', 'the lift curve bends over this many degrees before the stall'),
  // ---- drag
  CD0: c(0.0303, 'derived', 'with the induced drag factor: from two lines of the cruise table at 8000 ft (75 % and 47 % power), taking the propeller efficiency as 0.78', 'p.5-16 Fig 5-7'),
  K: c(0.0536, 'derived', 'induced drag factor (Oswald efficiency 0.80), from the same two lines', 'p.5-16 Fig 5-7'),
  CDnearStall: c(1.0, 'estimated', 'extra drag close to the stall: above 0.8 of the maximum lift coefficient, per square of the excess fraction'),
  propEfficiencyCruise: c(0.78, 'estimated', 'propeller efficiency in cruise, the assumption behind CD0 and K'),
  dCDFlap: c([0, 0.010, 0.026, 0.044, 0.062], 'estimated', 'drag added by the flaps'),
  CDwindmill: c(0.0251, 'derived', 'drag of the windmilling propeller: what the drag polar lacks to give the maximum glide of 9.1 to 1 at 65 KIAS', 'p.3-11 Fig 3-1'),
  CDstopped: c(0.008, 'estimated', 'drag of a stopped propeller'),
  kStallDrag: c(6.0, 'estimated', 'drag rise beyond the stall, per radian squared'),
  // ---- pitching moment
  neutralPoint: c(0.46, 'estimated', 'neutral point as a fraction of the mean aerodynamic chord'),
  Cm0: c(0.030, 'estimated', 'pitching moment at zero angle of attack: sets the trim speed with the elevator and trim neutral'),
  Cmq: c(-14.0, 'estimated', 'pitch damping'),
  Cmde: c(-1.28, 'estimated', 'elevator power per radian, before the two factors below'),
  tailWake: c(0.80, 'estimated', 'what is left of the elevator and rudder power in the wake of the wing and fuselage, propeller windmilling'),
  kSlipstream: c(1.5, 'estimated', 'gain of elevator and rudder power in the slipstream, per unit of thrust coefficient'),
  elevatorUpDeg: c(28, 'estimated', 'elevator travel up; a value for the type'),
  elevatorDownDeg: c(23, 'estimated', 'elevator travel down; a value for the type'),
  elevatorSaturationDeg: c(21, 'estimated', 'the elevator loses effect at large angles: full travel up is worth about 18 degrees'),
  trimAuthorityDeg: c(10, 'estimated', 'what full trim is worth in degrees of elevator'),
  dCmFlap: c([0, -0.028, -0.049, -0.062, -0.069], 'estimated', 'pitching moment of the flaps at the middle of the centre of gravity range: with the lift they add, lowering them at a fixed trim and throttle slows the aircraft from 80 KIAS to about 73, 68, 64 and 61 KIAS'),
  kCmThrust: c(0.30, 'estimated', 'nose-up moment with power, per unit of thrust coefficient'),
  kDownwash: c(0.18, 'estimated', 'nose-down break of the stall: a stalled wing sends less downwash to the tail; per unit of lift coefficient lost'),
  // ---- lateral and directional
  CYbeta: c(-0.31, 'estimated', 'side force due to sideslip'),
  Clbeta: c(-0.089, 'estimated', 'dihedral effect'),
  Clp: c(-0.47, 'estimated', 'roll damping'),
  Clr0: c(0.02, 'estimated', 'roll due to yaw rate at zero lift'),
  ClrCL: c(0.25, 'estimated', 'roll due to yaw rate, per unit lift coefficient'),
  ClAileron: c(0.054, 'estimated', 'rolling moment of full aileron'),
  CnAileron0: c(-0.0010, 'estimated', 'adverse yaw of full aileron at zero lift'),
  CnAileronCL: c(-0.0020, 'estimated', 'adverse yaw of full aileron, per unit lift coefficient'),
  Cnbeta: c(0.065, 'estimated', 'weathercock stability'),
  Cnr: c(-0.099, 'estimated', 'yaw damping'),
  CnpCL: c(-0.10, 'estimated', 'yaw due to roll rate (adverse), per unit lift coefficient'),
  CnRudder: c(0.0215, 'estimated', 'yawing moment of full rudder, before the wake and slipstream factors'),
  CYRudder: c(-0.052, 'estimated', 'side force of full rudder'),
  ClRudder: c(-0.004, 'estimated', 'rolling moment of full rudder'),
  kCnThrust: c(-0.035, 'estimated', 'left-turning tendency with power and low airspeed, per unit of thrust coefficient'),
  tailArm: c(0.40, 'estimated', 'distance of the fin behind the centre of gravity as a fraction of the wing span'),
  slipstreamShare: c(0.5, 'estimated', 'share of the left-turning tendency that is a side force of the slipstream on the fin; the rest is the propeller disc itself'),
  rigKcas: c(100, 'estimated', 'the airframe is rigged to fly straight, hands off, in level flight at this speed at 3000 ft: there the roll of the propeller torque and the yaw of the slipstream are balanced'),
  // ---- propeller and engine
  Cp0: c(0.0567, 'derived', 'power coefficient of the propeller standing still: full throttle gives 2280 to 2400 RPM static (2340 taken)', 'p.2-5'),
  CpJ0: c(0.976, 'derived', 'advance ratio at which the propeller would absorb no power, with the exponent below: from the cruise table (2100 to 2650 RPM, 2000 to 8000 ft)', 'p.5-16 Fig 5-7'),
  CpExp: c(5.36, 'derived', 'exponent of the fall of the power coefficient with advance ratio, from the cruise table', 'p.5-16 Fig 5-7'),
  Ct0: c(0.0978, 'derived', 'thrust coefficient standing still (about 540 lb of static thrust): from the takeoff ground roll', 'p.5-12 Fig 5-4'),
  Ct1: c(-0.02516, 'derived', 'fall of the thrust coefficient with the advance ratio; with Ct3 it gives the rate of climb at sea level and the assumed efficiency of 0.78 in cruise', 'p.5-14 Fig 5-5, p.5-16 Fig 5-7'),
  Ct3: c(-0.08136, 'derived', 'fall of the thrust coefficient with the cube of the advance ratio (see Ct1)', 'p.5-14 Fig 5-5, p.5-16 Fig 5-7'),
  torqueLapse: c(0.165, 'derived', 'full-throttle torque goes as (pressure ratio over the root of the temperature ratio) to the power 1.165: fits the rate of climb with altitude and with temperature. The fastest lines of the cruise table above 8000 ft then ask 3 to 7 % more power than the model has', 'p.5-14, 5-15, 5-16'),
  windmillJ: c(0.95, 'estimated', 'advance ratio of the windmilling propeller'),
  // ---- landing gear
  kMain: c(60000, 'estimated', 'stiffness of a main gear leg (N/m)'),
  cMain: c(4500, 'estimated', 'damping of a main gear leg (N s/m)'),
  kNose: c(32000, 'estimated', 'stiffness of the nose strut (N/m)'),
  cNose: c(3000, 'estimated', 'damping of the nose strut (N s/m)'),
  muRolling: c(0.02, 'estimated', 'rolling friction on a paved, level, dry runway'),
  muBraking: c(0.43, 'derived', 'braking friction with maximum braking: from the landing ground roll', 'p.5-21 Fig 5-10'),
  muSide: c(0.65, 'estimated', 'side friction of the tyres'),
  noseSteerDeg: c(10, 'poh', 'the rudder pedals turn the nose wheel about 10 degrees each side of centre', 'p.7-9'),
  flapRateDegS: c(5, 'estimated', 'speed of the electric flaps (degrees per second): about eight seconds from up to full down'),
};
const K = Object.fromEntries(Object.entries(FM).map(([k, e]) => [k, e.v]));
const CHORD = K.wingArea / K.wingSpan;
const H_MID = (((K.cgStationFwd + K.cgStationAft) / 2 - K.macLeadingEdge) * IN) / CHORD;      // middle of the centre of gravity range at 2300 lb, in chords

/** Airspeed calibration, normal static source (POH p.5-8, Figure 5-1): [KIAS, KCAS]. */
export const AIRSPEED_CALIBRATION = {
  0: [[40, 49], [50, 55], [60, 62], [70, 70], [80, 80], [90, 89], [100, 99], [110, 108], [120, 118], [130, 128], [140, 138]],
  10: [[40, 49], [50, 55], [60, 62], [70, 71], [80, 80], [85, 85]],
  40: [[40, 47], [50, 54], [60, 62], [70, 71], [80, 81], [85, 86]],
};

function fromTable(table, x, ix, iy) {
  const n = table.length;
  let i = 1;
  while (i < n - 1 && table[i][ix] < x) i++;
  const a = table[i - 1], b = table[i];
  return a[iy] + ((b[iy] - a[iy]) * (x - a[ix])) / (b[ix] - a[ix]);     // extrapolates beyond both ends
}
function calibration(flapDeg, x, ix, iy) {
  if (flapDeg <= 10) return lerp(fromTable(AIRSPEED_CALIBRATION[0], x, ix, iy), fromTable(AIRSPEED_CALIBRATION[10], x, ix, iy), clamp(flapDeg / 10, 0, 1));
  return lerp(fromTable(AIRSPEED_CALIBRATION[10], x, ix, iy), fromTable(AIRSPEED_CALIBRATION[40], x, ix, iy), clamp((flapDeg - 10) / 30, 0, 1));
}
/** Indicated airspeed for a calibrated airspeed (what the pitot-static system shows), and back. */
export function kiasFromKcas(kcas, flapDeg = 0) { return kcas <= 0 ? 0 : Math.max(0, calibration(flapDeg, kcas, 1, 0)); }
export function kcasFromKias(kias, flapDeg = 0) { return kias <= 0 ? 0 : Math.max(0, calibration(flapDeg, kias, 0, 1)); }

function flapTable(values, flapDeg) {
  const a = K.flapAngles;
  const f = clamp(flapDeg, a[0], a[a.length - 1]);
  let i = 1;
  while (i < a.length - 1 && a[i] < f) i++;
  return lerp(values[i - 1], values[i], (f - a[i - 1]) / (a[i] - a[i - 1]));
}

/** Maximum lift coefficient for a flap setting and a centre of gravity (0 = most forward, 1 = most rearward). */
export function clMax(flapDeg, cgFrac = 0.5) {
  return lerp(flapTable(K.CLmaxFwd, flapDeg), flapTable(K.CLmaxAft, flapDeg), clamp(cgFrac, 0, 1));
}

/** Lift coefficient against angle of attack (radians): straight, bent over to the maximum, then falling. */
export function liftCurve(alpha, flapDeg = 0, cgFrac = 0.5) {
  const cl0 = K.CL0 + flapTable(K.dCL0Flap, flapDeg);
  const top = clMax(flapDeg, cgFrac);
  const bend = K.stallBreakDeg * D2R;
  // the straight line would reach `top` at alphaLine; the rounded curve reaches it half a bend later
  const alphaLine = (top - cl0) / K.CLalpha;
  const alphaStall = alphaLine + bend / 2;
  const alphaWarn = (K.stallWarningMargin * top - cl0) / K.CLalpha;
  const line = cl0 + K.CLalpha * alpha;
  let CL;
  if (alpha <= alphaLine - bend / 2) CL = line;
  else if (alpha <= alphaStall) { const x = alphaStall - alpha; CL = top - (K.CLalpha / (2 * bend)) * x * x; }
  else CL = top * (0.62 + 0.38 * Math.exp(-(alpha - alphaStall) / (6 * D2R)));
  const bottom = -0.75 * clMax(0, cgFrac);                       // inverted stall, flaps or not
  if (CL < bottom) CL = bottom * (0.62 + 0.38 * Math.exp((alpha - (bottom - cl0) / K.CLalpha) / (6 * D2R)));
  // `lost`: the lift a stalled wing no longer gives, against the straight line
  return { CL, top, alphaStall, alphaWarn, stalled: alpha > alphaStall, warning: alpha >= alphaWarn, lost: Math.max(0, line - CL) };
}

/**
 * Drag coefficient. lift: what liftCurve() returned for this angle of attack (radians) and flap setting;
 * `ground` (0..1) is what is left of the induced drag near the ground.
 */
export function dragPolar(lift, alpha, flapDeg = 0, ground = 1) {
  const near = Math.max(0, Math.abs(lift.CL) / lift.top - 0.8);
  const beyond = Math.max(0, alpha - lift.alphaStall);
  return K.CD0 + K.K * lift.CL * lift.CL * ground + K.CDnearStall * near * near + flapTable(K.dCDFlap, flapDeg) + K.kStallDrag * beyond * beyond;
}

/** Induced drag left near the ground, for a height of the wing above it (m). */
export function groundEffect(wingHeight) {
  const x = (16 * Math.max(0, wingHeight)) / K.wingSpan;
  return (x * x) / (1 + x * x);
}

// ---------------------------------------------------------------------------------- propeller and engine
export function propCp(J) { return K.Cp0 * (1 - Math.pow(Math.max(0, J) / K.CpJ0, K.CpExp)); }
export function propCt(J) { const j = Math.max(0, J); return K.Ct0 + K.Ct1 * j + K.Ct3 * j * j * j; }

/** Density ratio at an altitude (ft) with a deviation from the standard temperature (°C). */
export function densityAt(altFt, isaDevC = 0) {
  const tStd = 288.15 - 0.0019812 * altFt;
  return densityRatio(altFt) * tStd / (tStd + isaDevC);
}

/**
 * What the engine breathes at a pressure altitude (ft) and a deviation from the standard temperature (°C): the
 * pressure ratio over the root of the temperature ratio (1 at sea level on a standard day).
 */
export function chargeAt(altFt, isaDevC = 0) {
  const tStd = 288.15 - 0.0019812 * altFt;
  const pressure = (densityRatio(altFt) * tStd) / 288.15;
  return pressure / Math.sqrt((tStd + isaDevC) / 288.15);
}

/** Torque the engine gives at full throttle, as a fraction of rated torque, for what it breathes (see chargeAt). */
export function fullThrottleTorque(charge, mixtureFactor = 1) { return Math.pow(charge, 1 + K.torqueLapse) * mixtureFactor; }

/**
 * What the engine can give at a throttle position (0..1): { torque, power }, fractions of the rated torque and of the
 * rated power. Wide open, the torque is what the air density allows; throttled, the engine gives a power that
 * does not depend on its speed (the throttle meters the air), which is the law of the systems simulation.
 */
export function engineAt(throttle, charge, mixtureFactor = 1) {
  const full = fullThrottleTorque(charge, mixtureFactor);
  return { torque: full, power: full * throttleAirflow(throttle) };
}

/**
 * The same from the systems simulation's power figure, which is throttle air x standard density x mixture x
 * ignition x carburetor heat and ice: its density factor is replaced by this model's law for the altitude.
 */
export function engineFromSim(simPower, throttle, altFt, isaDevC = 0) {
  const air = throttleAirflow(throttle);
  const torque = (simPower / (air * densityRatio(altFt))) * fullThrottleTorque(chargeAt(altFt, isaDevC));
  return { torque, power: torque * air };
}

const asEngine = (e) => (typeof e === 'number' ? { torque: e, power: Infinity } : { torque: e.torque, power: e.power ?? Infinity });

/** Shaft power (W) the engine gives at an RPM. engine: a torque fraction, or { torque, power }. */
export function enginePower(engine, rpm) {
  const e = asEngine(engine);
  return K.ratedPower * Math.min((e.torque * rpm) / K.ratedRpm, e.power);
}

/** RPM at which the propeller absorbs what the engine gives, at a true airspeed (m/s). engine: as enginePower(). */
export function equilibriumRpm(engine, tas, sigma) {
  const e = asEngine(engine);
  if (e.torque <= 0 || e.power <= 0) return 0;
  // below `lo` the airflow drives the propeller; the engine speed is above it, where the propeller absorbs power
  let lo = (Math.max(0, tas) / (K.CpJ0 * K.propDiameter)) * 60, hi = K.ratedRpm * 1.6;
  for (let i = 0; i < 40; i++) {
    const mid = (lo + hi) / 2;
    if (propPower(mid, tas, sigma) < enginePower(e, mid)) lo = mid; else hi = mid;
  }
  return (lo + hi) / 2;
}

/** Shaft power (W) the propeller absorbs at an RPM, true airspeed (m/s) and density ratio. */
export function propPower(rpm, tas, sigma) {
  const n = rpm / 60;
  return n > 0 ? propCp(tas / (n * K.propDiameter)) * RHO0 * sigma * n * n * n * Math.pow(K.propDiameter, 5) : 0;
}

/** Thrust (N) of the turning propeller. */
export function propThrust(rpm, tas, sigma) {
  const n = rpm / 60;
  if (n < 1) return 0;
  return Math.max(-0.06, propCt(tas / (n * K.propDiameter))) * RHO0 * sigma * n * n * Math.pow(K.propDiameter, 4);
}

// ---------------------------------------------------------------------------------- moments
/** Elevator and rudder power in the wake of the wing and in the slipstream. */
function tailFactor(Tc) { return K.tailWake * (1 + K.kSlipstream * Math.max(0, Tc)); }

/** What an elevator angle (radians) is worth: the elevator loses effect at large angles. */
function elevatorEffect(de) { const sat = K.elevatorSaturationDeg * D2R; return sat * Math.tanh(de / sat); }

/** Pitching moment coefficient about the centre of gravity. de: elevator angle (radians, trailing edge down positive). */
function pitchCoefficient(alpha, flapDeg, hCg, de, Tc, lift, qHat = 0) {
  // the flaps: their moment at the middle of the centre of gravity range, and their lift moved with the centre of gravity
  const flaps = flapTable(K.dCmFlap, flapDeg) + flapTable(K.dCL0Flap, flapDeg) * (hCg - H_MID);
  return K.Cm0 + flaps - K.CLalpha * (K.neutralPoint - hCg) * alpha + K.Cmq * qHat + K.Cmde * elevatorEffect(de) * tailFactor(Tc) + K.kCmThrust * Tc - K.kDownwash * lift.lost;
}

// The condition the airframe is rigged for (see rigKcas): there the propeller needs neither aileron nor rudder. Filled below.
const RIG = { Cl: 0, Tc: 0 };

/** Rolling and yawing moment coefficients that do not depend on the controls or the motion: the rigging and the power. */
function powerMoments(Tc, torqueCoefficient) {
  const Cn = K.kCnThrust * (Math.max(0, Tc) - RIG.Tc);
  return { Cl: RIG.Cl - torqueCoefficient, Cn, CY: (-K.slipstreamShare * Cn) / K.tailArm };       // the slipstream pushes the fin sideways
}

// ---------------------------------------------------------------------------------- state
const qMul = (a, b) => [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3], a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
  a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1], a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]];
const qFromEuler = (phi, theta, psi) => {
  const c1 = Math.cos(psi / 2), s1 = Math.sin(psi / 2), c2 = Math.cos(theta / 2), s2 = Math.sin(theta / 2), c3 = Math.cos(phi / 2), s3 = Math.sin(phi / 2);
  return [c1 * c2 * c3 + s1 * s2 * s3, c1 * c2 * s3 - s1 * s2 * c3, c1 * s2 * c3 + s1 * c2 * s3, s1 * c2 * c3 - c1 * s2 * s3];
};
/** Rows of the matrix that turns a body vector into an earth (north, east, down) vector. */
function rotation(q) {
  const [w, x, y, z] = q;
  return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
    [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]];
}
const toEarth = (R, v) => [R[0][0] * v[0] + R[0][1] * v[1] + R[0][2] * v[2], R[1][0] * v[0] + R[1][1] * v[1] + R[1][2] * v[2], R[2][0] * v[0] + R[2][1] * v[1] + R[2][2] * v[2]];
const toBody = (R, v) => [R[0][0] * v[0] + R[1][0] * v[1] + R[2][0] * v[2], R[0][1] * v[0] + R[1][1] * v[1] + R[2][1] * v[2], R[0][2] * v[0] + R[1][2] * v[1] + R[2][2] * v[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

export function eulerAngles(q) {
  const [w, x, y, z] = q;
  return { phi: Math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y)), theta: Math.asin(clamp(2 * (w * y - z * x), -1, 1)), psi: Math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z)) };
}

/** Station of the centre of gravity (in aft of datum) for a weight and a position between the limits (0 forward, 1 aft). */
export function cgStation(weightLb, cgFrac) {
  const fwd = lerp(K.cgStationFwdLight, K.cgStationFwd, clamp((weightLb - 1950) / (K.maxWeightLb - 1950), 0, 1));
  return lerp(fwd, K.cgStationAft, clamp(cgFrac, 0, 1));
}

function massProperties(f) {
  const m = f.weightLb * LB;
  const scale = m / (K.maxWeightLb * LB);
  const station = cgStation(f.weightLb, f.cgFrac);
  return { m, Ixx: K.Ixx * scale, Iyy: K.Iyy * scale, Izz: K.Izz * scale, cgStation: station, hCg: ((station - K.macLeadingEdge) * IN) / CHORD };
}

/**
 * Where the three wheels touch, in body axes (x forward, y right, z down), for a centre of gravity; and how far
 * the main wheels are behind it along the ground at rest (m), which places the model in a scene.
 */
export function gearGeometry(station, mass) {
  const theta = K.groundPitchDeg * D2R;
  const xMain = -(K.mainGearStation - station) * IN;
  const xNose = xMain + K.wheelBase;
  // loaded wheel positions at rest: centre of gravity at its height, fuselage at the ground attitude
  const zMainRest = (K.cgHeight + xMain * Math.sin(theta)) / Math.cos(theta);
  const zNoseRest = zMainRest + (xNose - xMain) * Math.tan(theta);
  // share of the weight on the nose wheel, from the horizontal distances of the wheels from the centre of gravity
  const armMain = -(xMain * Math.cos(theta) + zMainRest * Math.sin(theta)), armNose = xNose * Math.cos(theta) + zNoseRest * Math.sin(theta);
  const share = armMain / (armMain + armNose);
  // unloaded positions: lower by what each spring gives under its share
  const zMain = zMainRest + (mass * G * (1 - share)) / (2 * K.kMain) / Math.cos(theta);
  const zNose = zNoseRest + (mass * G * share) / K.kNose / Math.cos(theta);
  return {
    mainBehindCg: armMain, noseShare: share,
    wheels: [
      { name: 'nose', p: [xNose, 0, zNose], k: K.kNose, c: K.cNose, steer: true, brake: false },
      { name: 'left', p: [xMain, -K.wheelTrack / 2, zMain], k: K.kMain, c: K.cMain, steer: false, brake: true },
      { name: 'right', p: [xMain, K.wheelTrack / 2, zMain], k: K.kMain, c: K.cMain, steer: false, brake: true },
    ],
  };
}

/**
 * A flight state. Positions in metres (north, east, altitude above mean sea level), velocities in body axes
 * (m/s), attitude as a quaternion (body to earth), rates in rad/s. wind: the air's velocity (north, east; m/s).
 */
export function createFlight(o = {}) {
  const f = {
    t: 0,
    weightLb: o.weightLb ?? K.maxWeightLb,
    cgFrac: o.cgFrac ?? 0.5,                   // 0 most forward, 1 most rearward centre of gravity
    isaDevC: o.isaDevC ?? 0,
    fieldElevFt: o.fieldElevFt ?? 0,
    wind: [0, 0],
    north: 0, east: 0, alt: 0,
    u: 0, v: 0, w: 0, p: 0, q: 0, r: 0,
    quat: [1, 0, 0, 0],
    flapDeg: o.flapDeg ?? 0,
    rpm: 0,
    out: {},
  };
  setWind(f, o.windFromDeg ?? 0, o.windKt ?? 0);
  if (o.inFlight) setInFlight(f, o.inFlight);
  else setOnGround(f, o.headingDeg ?? 0);
  return f;
}

/** A steady wind: the direction it blows from (degrees true) and its speed (knots). */
export function setWind(f, fromDeg, kt) {
  f.wind = [-Math.cos(fromDeg * D2R) * kt * KT, -Math.sin(fromDeg * D2R) * kt * KT];
  return f;
}

/** Stand the aircraft on its wheels at rest on the field, at a heading (degrees). */
export function setOnGround(f, headingDeg = 0) {
  const theta = K.groundPitchDeg * D2R;
  const wind = f.wind;
  f.wind = [0, 0];
  f.quat = qFromEuler(0, theta, headingDeg * D2R);
  f.u = f.v = f.w = f.p = f.q = f.r = 0;
  f.rpm = 0;
  f.alt = f.fieldElevFt * FT + K.cgHeight;
  for (let i = 0; i < 240; i++) stepFlight(f, { settle: true }, 1 / 120);    // settle on the springs
  f.u = f.v = f.w = f.p = f.q = f.r = 0;
  f.wind = wind;
  stepFlight(f, { settle: true, brake: 1 }, 1e-4);                           // fill `out`
  f.t = 0;
  return f;
}

/**
 * Put the aircraft in steady straight flight: { kias, altFt, headingDeg, climbFpm | torque, flapDeg, engineOn }.
 * Returns the trim (see trim()), which is also kept as f.trimmed.
 */
export function setInFlight(f, o = {}) {
  f.flapDeg = o.flapDeg ?? f.flapDeg;
  const altFt = o.altFt ?? 3000;
  const engineOn = o.engineOn ?? true;
  const tr = trim({ kcas: kcasFromKias(o.kias ?? 90, f.flapDeg), altFt, climbFpm: o.climbFpm ?? 0, torque: o.torque ?? null, engine: o.engine ?? null, engineOn, flapDeg: f.flapDeg,
    weightLb: f.weightLb, cgFrac: f.cgFrac, isaDevC: f.isaDevC });
  f.alt = altFt * FT;
  f.quat = qFromEuler(0, tr.theta, (o.headingDeg ?? 0) * D2R);
  // the trim is in still air: add the wind so that the airspeed is the one asked for
  const windBody = toBody(rotation(f.quat), [f.wind[0], f.wind[1], 0]);
  f.u = tr.tas * Math.cos(tr.alpha) + windBody[0]; f.v = windBody[1]; f.w = tr.tas * Math.sin(tr.alpha) + windBody[2];
  f.p = f.q = f.r = 0;
  f.rpm = tr.rpm;
  f.trimmed = tr;
  stepFlight(f, { elevator: 0, trim: tr.trim, aileron: tr.aileron, rudder: tr.rudder, engine: o.engine ?? tr.torque, engineOn }, 1e-4);     // fill `out`
  f.t = 0;
  return tr;
}

// ---------------------------------------------------------------------------------- forces
function controlsOf(input) {
  return {
    aileron: clamp(input.aileron ?? 0, -1, 1),      // + rolls right
    elevator: clamp(input.elevator ?? 0, -1, 1),    // + pulls the nose up; 0 is where the trim holds the elevator
    rudder: clamp(input.rudder ?? 0, -1, 1),        // + nose right
    trim: clamp(input.trim ?? 0, -1, 1),            // + nose up
    brake: clamp(input.brake ?? 0, 0, 1),
    brakeLeft: clamp(input.brakeLeft ?? 0, 0, 1), brakeRight: clamp(input.brakeRight ?? 0, 0, 1),
  };
}
/** Elevator angle (radians, trailing edge down positive): where the trim holds it, moved by the wheel, within the stops. */
export function elevatorAngle(ctl) {
  const wheel = ctl.elevator > 0 ? ctl.elevator * K.elevatorUpDeg : ctl.elevator * K.elevatorDownDeg;
  return clamp(-wheel - (ctl.trim ?? 0) * K.trimAuthorityDeg, -K.elevatorUpDeg, K.elevatorDownDeg) * D2R;
}

/** Aerodynamic and propeller forces and moments in body axes, and what an observer would want to know. */
function airLoads(f, ctl, thrust, engineOn, mp, R) {
  const altFt = f.alt / FT;
  const sigma = densityAt(altFt, f.isaDevC);
  const rho = RHO0 * sigma;
  const wind = toBody(R, [f.wind[0], f.wind[1], 0]);
  const ua = f.u - wind[0], va = f.v - wind[1], wa = f.w - wind[2];            // velocity through the air
  const V = Math.hypot(ua, va, wa);
  const alpha = V > 0.5 ? Math.atan2(wa, Math.max(0.01, ua)) : 0;
  const beta = V > 0.5 ? Math.asin(clamp(va / V, -1, 1)) : 0;
  const qbar = 0.5 * rho * V * V;
  const qS = qbar * K.wingArea;
  const lift = liftCurve(alpha, f.flapDeg, f.cgFrac);
  const CL = lift.CL;
  const ground = groundEffect(f.alt - f.fieldElevFt * FT + K.wingAboveCg);
  const propDrag = engineOn ? 0 : (f.rpm > 150 ? K.CDwindmill : K.CDstopped);
  const CD = dragPolar(lift, alpha, f.flapDeg, ground) + propDrag + 0.6 * Math.abs(K.CYbeta) * beta * beta;
  const span = V > 1 ? K.wingSpan / (2 * V) : 0, chord = V > 1 ? CHORD / (2 * V) : 0;
  const Tc = qS > 50 ? clamp(thrust / qS, -0.2, 0.6) : 0;
  const tail = tailFactor(Tc);
  const de = elevatorAngle(ctl);
  const torque = engineOn && f.rpm > 100 ? propPower(f.rpm, V, sigma) / ((f.rpm * Math.PI) / 30) : 0;      // the airframe rolls against the propeller
  const power = powerMoments(Tc, qS > 50 ? torque / (qS * K.wingSpan) : 0);
  const CY = K.CYbeta * beta + K.CYRudder * ctl.rudder + power.CY;
  const damp = lift.stalled ? 0.35 : 1;                              // a stalled wing damps roll poorly
  const Cl = K.Clbeta * beta + damp * K.Clp * f.p * span + (K.Clr0 + K.ClrCL * CL) * f.r * span + K.ClAileron * ctl.aileron * (lift.stalled ? 0.5 : 1) + K.ClRudder * ctl.rudder + power.Cl;
  const Cm = pitchCoefficient(alpha, f.flapDeg, mp.hCg, de, Tc, lift, f.q * chord);
  const Cn = K.Cnbeta * beta + K.Cnr * f.r * span + K.CnpCL * CL * f.p * span + K.CnRudder * tail * ctl.rudder + (K.CnAileron0 + K.CnAileronCL * CL) * ctl.aileron + power.Cn;
  const ca = Math.cos(alpha), sa = Math.sin(alpha);
  const L = qS * CL, D = qS * CD;
  return {
    force: [-D * ca + L * sa + thrust, qS * CY, -D * sa - L * ca],
    moment: [qS * K.wingSpan * Cl, qS * CHORD * Cm, qS * K.wingSpan * Cn],
    V, alpha, beta, qbar, sigma, rho, CL, CD, lift, L, D, Tc, de,
  };
}

/** Forces of the three wheels on the ground, in body axes. */
function gearLoads(f, ctl, R, mp) {
  const force = [0, 0, 0], moment = [0, 0, 0];
  const ground = f.fieldElevFt * FT;
  const omega = [f.p, f.q, f.r], vel = [f.u, f.v, f.w];
  let onGround = 0, weightOnWheels = 0;
  const wheels = [];
  for (const wheel of gearGeometry(mp.cgStation, mp.m).wheels) {
    const arm = toEarth(R, wheel.p);
    const depth = arm[2] - (f.alt - ground);                         // how far the wheel is pressed into the ground
    if (depth <= 0) { wheels.push(0); continue; }
    const vPoint = toEarth(R, [vel[0] + omega[1] * wheel.p[2] - omega[2] * wheel.p[1], vel[1] + omega[2] * wheel.p[0] - omega[0] * wheel.p[2], vel[2] + omega[0] * wheel.p[1] - omega[1] * wheel.p[0]]);
    const N = Math.max(0, wheel.k * depth + wheel.c * vPoint[2]);
    if (N <= 0) { wheels.push(0); continue; }
    onGround++; weightOnWheels += N; wheels.push(N);
    const steer = wheel.steer ? ctl.rudder * K.noseSteerDeg * D2R : 0;
    const ahead = toEarth(R, [Math.cos(steer), Math.sin(steer), 0]);
    const len = Math.hypot(ahead[0], ahead[1]) || 1;
    const t = [ahead[0] / len, ahead[1] / len], s = [-t[1], t[0]];
    const vLong = vPoint[0] * t[0] + vPoint[1] * t[1], vSide = vPoint[0] * s[0] + vPoint[1] * s[1];
    const braking = wheel.brake ? Math.max(ctl.brake, wheel.name === 'left' ? ctl.brakeLeft : ctl.brakeRight) : 0;
    const mu = K.muRolling + K.muBraking * braking;
    const fLong = -mu * N * Math.tanh(vLong / 0.25);
    const fSide = -K.muSide * N * Math.tanh((2.5 * vSide) / Math.max(1.5, Math.abs(vLong)));
    const fb = toBody(R, [t[0] * fLong + s[0] * fSide, t[1] * fLong + s[1] * fSide, -N]);
    const mo = cross(wheel.p, fb);
    for (let i = 0; i < 3; i++) { force[i] += fb[i]; moment[i] += mo[i]; }
  }
  return { force, moment, onGround, weightOnWheels, wheels };
}

/**
 * Advance the flight by dt seconds.
 * input: { aileron, elevator, rudder, trim (each -1..1), flapCommandDeg, brake, brakeLeft, brakeRight (0..1),
 *          engineOn, engine: { torque, power } (see engineAt) or torque (a fraction of the rated torque) }
 */
export function stepFlight(f, input = {}, dt = 1 / 60) {
  const mp = massProperties(f);
  const ctl = controlsOf(input);
  let left = Math.max(0, dt);
  while (left > 1e-9) {
    const h = Math.min(1 / 120, left);
    left -= h;
    stepOnce(f, input, ctl, mp, h);
  }
  return f;
}

function stepOnce(f, input, ctl, mp, h) {
  f.t += h;
  // ---- flaps travel at the speed of their motor
  if (input.flapCommandDeg != null && !input.settle) {
    const move = clamp(input.flapCommandDeg - f.flapDeg, -K.flapRateDegS * h, K.flapRateDegS * h);
    f.flapDeg = clamp(f.flapDeg + move, 0, 40);
  }
  const R = rotation(f.quat);
  const sigma = densityAt(f.alt / FT, f.isaDevC);
  const windBody = toBody(R, [f.wind[0], f.wind[1], 0]);
  const V = Math.hypot(f.u - windBody[0], f.v - windBody[1], f.w - windBody[2]);
  // ---- engine and propeller: the RPM goes to where the propeller absorbs what the engine gives
  const engine = input.engine ?? input.torque ?? 0;
  const engineOn = !!input.engineOn && asEngine(engine).torque > 0 && asEngine(engine).power > 0;
  let target;
  if (engineOn) target = equilibriumRpm(engine, V, sigma);
  else target = V > 20 ? (V / (K.windmillJ * K.propDiameter)) * 60 : 0;          // windmilling, or stopped below about 40 knots
  f.rpm += (target - f.rpm) * (1 - Math.exp(-h / (engineOn ? 0.6 : 1.5)));
  if (f.rpm < 5) f.rpm = 0;
  const thrust = engineOn ? propThrust(f.rpm, V, sigma) : 0;
  // ---- forces
  const air = airLoads(f, ctl, thrust, engineOn, mp, R);
  const gear = gearLoads(f, ctl, R, mp);
  const gBody = toBody(R, [0, 0, mp.m * G]);
  const F = [air.force[0] + gear.force[0] + gBody[0], air.force[1] + gear.force[1] + gBody[1], air.force[2] + gear.force[2] + gBody[2]];
  const M = [air.moment[0] + gear.moment[0], air.moment[1] + gear.moment[1], air.moment[2] + gear.moment[2]];
  // ---- rigid-body equations in body axes
  const du = F[0] / mp.m - f.q * f.w + f.r * f.v, dv = F[1] / mp.m - f.r * f.u + f.p * f.w, dw = F[2] / mp.m - f.p * f.v + f.q * f.u;
  const dp = (M[0] + (mp.Iyy - mp.Izz) * f.q * f.r) / mp.Ixx, dq = (M[1] + (mp.Izz - mp.Ixx) * f.r * f.p) / mp.Iyy, dr = (M[2] + (mp.Ixx - mp.Iyy) * f.p * f.q) / mp.Izz;
  f.u += du * h; f.v += dv * h; f.w += dw * h; f.p += dp * h; f.q += dq * h; f.r += dr * h;
  // at rest on the wheels with the brakes holding: stand still rather than creep
  if (gear.onGround >= 3 && Math.hypot(f.u, f.v) < 0.03 && Math.abs(thrust) < K.muRolling * gear.weightOnWheels + K.muBraking * ctl.brake * gear.weightOnWheels * 0.7) { f.u = 0; f.v = 0; }
  // ---- position and attitude
  const vE = toEarth(R, [f.u, f.v, f.w]);
  f.north += vE[0] * h; f.east += vE[1] * h; f.alt -= vE[2] * h;
  const dq4 = qMul(f.quat, [0, f.p, f.q, f.r]);
  f.quat = [f.quat[0] + 0.5 * dq4[0] * h, f.quat[1] + 0.5 * dq4[1] * h, f.quat[2] + 0.5 * dq4[2] * h, f.quat[3] + 0.5 * dq4[3] * h];
  const norm = Math.hypot(...f.quat); f.quat = f.quat.map((x) => x / norm);
  // ---- what the instruments and the lesson want to know
  const e = eulerAngles(f.quat);
  const kcas = (air.V * Math.sqrt(air.sigma)) / KT;
  const o = f.out;
  o.kcas = kcas; o.kias = kiasFromKcas(kcas, f.flapDeg); o.ktas = air.V / KT;
  o.altFt = f.alt / FT;
  o.vsFpm = (-vE[2] / FT) * 60;
  o.aglFt = (f.alt - f.fieldElevFt * FT - K.cgHeight) / FT;      // height of the wheels above the field
  o.headingDeg = ((e.psi * R2D) % 360 + 360) % 360; o.pitchDeg = e.theta * R2D; o.bankDeg = e.phi * R2D;
  o.trackDeg = ((Math.atan2(vE[1], vE[0]) * R2D) % 360 + 360) % 360;
  o.turnRateDps = ((f.q * Math.sin(e.phi) + f.r * Math.cos(e.phi)) / Math.max(0.2, Math.cos(e.theta))) * R2D;
  o.alphaDeg = air.alpha * R2D; o.betaDeg = air.beta * R2D; o.alphaStallDeg = air.lift.alphaStall * R2D;
  o.stalled = air.lift.stalled && air.V > 5;
  o.stallWarning = air.lift.warning && air.V > 15 && gear.onGround === 0;
  o.loadFactor = -(air.force[2] + gear.force[2]) / (mp.m * G);
  // the ball of the turn coordinator: + to the right. It goes where the sideways force on the airframe does not hold it.
  o.slip = clamp(-(air.force[1] + gear.force[1]) / Math.max(0.2 * mp.m * G, Math.abs(air.force[2] + gear.force[2])), -1, 1);
  o.rpm = f.rpm; o.thrustN = thrust; o.CL = air.CL; o.CD = air.CD;
  o.elevatorDeg = air.de * R2D; o.flapDeg = f.flapDeg;
  o.onGround = gear.onGround > 0; o.wheels = gear.onGround; o.weightOnWheels = gear.weightOnWheels;
  o.groundSpeedKt = Math.hypot(vE[0], vE[1]) / KT;
}

// ---------------------------------------------------------------------------------- steady flight
/**
 * Steady straight flight at a calibrated airspeed, in still air: finds the angle of attack, the thrust, the engine
 * torque and the controls that hold it. Give climbFpm, or give `torque` (then the rate of climb is found instead).
 * Returns among others: trim (the trim setting that holds the elevator there, hands off; -1..1), elevator (the
 * wheel position that does it with the trim neutral), aileron and rudder (what balances the propeller).
 */
export function trim({ kcas, altFt = 0, climbFpm = 0, torque = null, engine = null, flapDeg = 0, weightLb = K.maxWeightLb, cgFrac = 0.5, isaDevC = 0, engineOn = true }) {
  const given = engine ?? torque;                                               // what the engine gives, if it is given
  const sigma = densityAt(altFt, isaDevC), rho = RHO0 * sigma;
  const tas = (kcas * KT) / Math.sqrt(sigma);
  const W = weightLb * LB * G, qS = 0.5 * rho * tas * tas * K.wingArea;
  const mp = massProperties({ weightLb, cgFrac });
  const top = liftCurve(1, flapDeg, cgFrac).alphaStall;
  let alpha = 0.05, thrust = 0, gamma = given == null ? Math.asin(clamp((climbFpm * FT) / 60 / tas, -0.9, 0.9)) : 0, rpm = 0, tq = 0, CL = 0, CD = 0, lift = null;
  for (let i = 0; i < 60; i++) {
    const need = (W * Math.cos(gamma) - thrust * Math.sin(alpha)) / qS;        // lift coefficient needed
    let lo = -0.2, hi = top;
    for (let j = 0; j < 40; j++) { const mid = (lo + hi) / 2; if (liftCurve(mid, flapDeg, cgFrac).CL < need) lo = mid; else hi = mid; }
    alpha = (lo + hi) / 2;
    lift = liftCurve(alpha, flapDeg, cgFrac);
    CL = lift.CL;
    CD = dragPolar(lift, alpha, flapDeg) + (engineOn ? 0 : K.CDwindmill);
    const drag = qS * CD;
    if (given == null && engineOn) {
      thrust = (drag + W * Math.sin(gamma)) / Math.cos(alpha);
      let a = 0, b = 1.3;                                                       // the torque that gives this thrust
      for (let j = 0; j < 40; j++) { tq = (a + b) / 2; rpm = equilibriumRpm(tq, tas, sigma); if (propThrust(rpm, tas, sigma) < thrust) a = tq; else b = tq; }
    } else {
      rpm = engineOn ? equilibriumRpm(given, tas, sigma) : (tas / (K.windmillJ * K.propDiameter)) * 60;
      thrust = engineOn ? propThrust(rpm, tas, sigma) : 0;
      gamma = Math.asin(clamp((thrust * Math.cos(alpha) - drag) / W, -0.9, 0.9));
    }
  }
  const shaft = engineOn ? propPower(rpm, tas, sigma) : 0;
  if (engineOn) tq = (shaft / K.ratedPower) * (K.ratedRpm / Math.max(1, rpm));                     // the torque fraction at this RPM
  // the throttle position that gives this power at this density, full rich or leaned as the caller's engine says
  const full = fullThrottleTorque(chargeAt(altFt, isaDevC));
  const air = full > 0 ? shaft / K.ratedPower / full : 0;
  const idle = throttleAirflow(0);
  const throttle = engineOn ? clamp(Math.pow(Math.max(0, air - idle) / (1 - idle), 1 / 1.6), 0, 1) : 0;
  const Tc = thrust / qS;
  // ---- elevator for no pitching moment
  const rest = pitchCoefficient(alpha, flapDeg, mp.hCg, 0, Tc, lift);
  const sat = K.elevatorSaturationDeg * D2R;
  const worth = clamp(-rest / (K.Cmde * tailFactor(Tc)) / sat, -0.999, 0.999);
  const de = clamp(sat * Math.atanh(worth), -K.elevatorUpDeg * D2R, K.elevatorDownDeg * D2R);     // radians, trailing edge down positive
  const elevator = de < 0 ? -de / (K.elevatorUpDeg * D2R) : -de / (K.elevatorDownDeg * D2R);
  // ---- aileron and rudder against the propeller: no rolling and no yawing moment without sideslip
  const power = powerMoments(Tc, engineOn && rpm > 100 ? shaft / ((rpm * Math.PI) / 30) / (qS * K.wingSpan) : 0);
  const a11 = K.ClAileron, a12 = K.ClRudder, a21 = K.CnAileron0 + K.CnAileronCL * CL, a22 = K.CnRudder * tailFactor(Tc);
  const det = a11 * a22 - a12 * a21;
  const aileron = clamp((-power.Cl * a22 + power.Cn * a12) / det, -1, 1), rudder = clamp((-power.Cn * a11 + power.Cl * a21) / det, -1, 1);
  const needCL = (W * Math.cos(gamma) - thrust * Math.sin(alpha)) / qS;
  return { alpha, theta: alpha + gamma, gamma, tas, kcas, thrust, torque: tq, throttle, rpm, CL, CD, Tc, elevator, elevatorDeg: de * R2D, trim: clamp(-(de * R2D) / K.trimAuthorityDeg, -1, 1), aileron, rudder,
    climbFpm: ((tas * Math.sin(gamma)) / FT) * 60, sigma, power: shaft, stalled: CL < needCL - 1e-3 };
}

{
  const t = trim({ kcas: K.rigKcas, altFt: 3000 });
  const qS = 0.5 * RHO0 * t.sigma * t.tas * t.tas * K.wingArea;
  RIG.Tc = t.Tc;
  RIG.Cl = t.power / ((t.rpm * Math.PI) / 30) / (qS * K.wingSpan);
}

/** Power-off stalling speed (KCAS) in level flight at a bank angle: what the maximum lift coefficient gives. */
export function stallSpeedKcas({ flapDeg = 0, weightLb = K.maxWeightLb, cgFrac = 0.5, bankDeg = 0 }) {
  const W = (weightLb * LB * G) / Math.cos(bankDeg * D2R);
  return Math.sqrt((2 * W) / (RHO0 * K.wingArea * clMax(flapDeg, cgFrac))) / KT;
}

/** The coefficients as rows for a table: name, value, where it comes from. */
export function coefficientTable() {
  return Object.entries(FM).map(([name, e]) => ({ name, value: e.v, source: e.src, note: e.note, ref: e.ref }));
}
