// Flat-four (Lycoming O-320 style) slider-crank kinematics shared by the viewer and tests.
// Engine frame = the ENGINE node of the GLB: +Z forward, +Y up, +X toward the LEFT wing.
// Must stay in sync with blender/c172/engine.py (CYL_Z, CRANK_R, ROD_L).

export const CRANK_R = 0.0492; // m, half the 3.875 in stroke (O-320 type data; verify against TCDS E-274)
export const ROD_L = 0.162;    // m, illustrative connecting-rod centre distance

// side: -1 = right bank (-X), +1 = left bank (+X). Lycoming numbering: odd right, even left, No.1 right-front.
// z = cylinder centre ahead of the ENGINE node origin (crank centre). Bank spacing 0.235 m and the
// 0.044 m left-bank stagger are estimated (Phase 8 model, blender/c172/engine.py keeps the same values).
export const CYLINDERS = {
  1: { side: -1, z: 0.140, pinDeg: 180 },
  2: { side: 1, z: 0.096, pinDeg: 0 },
  3: { side: -1, z: -0.095, pinDeg: 0 },
  4: { side: 1, z: -0.139, pinDeg: 180 },
};

export const FIRING_ORDER = [1, 3, 2, 4];
// Crank angle (deg, within the 720 deg four-stroke cycle) at which each cylinder is at TDC on compression.
export const FIRE_DEG = { 1: 0, 3: 180, 2: 360, 4: 540 };

// Illustrative valve events (typical light-aircraft values, NOT O-320-H2AD cam data).
export const VALVE_EVENTS = {
  intake: { open: 340, close: 600 },   // opens 20 deg BTDC (overlap), closes 60 deg ABDC
  exhaust: { open: 120, close: 380 },  // opens 60 deg BBDC, closes 20 deg ATDC
};
export const SPARK_BTDC = 25; // illustrative ignition timing, deg before TDC
export const VALVE_LIFT = 0.012; // m (visual)

const D2R = Math.PI / 180;
const mod = (a, n) => ((a % n) + n) % n;

/** Crank-pin position in the engine frame for crank angle theta (radians). */
export function pinPosition(theta, cyl) {
  const c = CYLINDERS[cyl];
  const a = theta + c.pinDeg * D2R;
  return [CRANK_R * Math.cos(a), CRANK_R * Math.sin(a), c.z];
}

/** Distance from crank axis to piston pin along the bank axis. */
export function pistonPinDistance(theta, cyl) {
  const c = CYLINDERS[cyl];
  const [x, y] = pinPosition(theta, cyl);
  const u = x * c.side;
  return u + Math.sqrt(ROD_L * ROD_L - y * y);
}

export function pistonPosition(theta, cyl) {
  const c = CYLINDERS[cyl];
  return [c.side * pistonPinDistance(theta, cyl), 0, c.z];
}

/** Rotation about +Z for a rod authored along +X from big end to small end. */
export function rodAngle(theta, cyl) {
  const p = pinPosition(theta, cyl);
  const q = pistonPosition(theta, cyl);
  return Math.atan2(q[1] - p[1], q[0] - p[0]);
}

/** Position in this cylinder's own four-stroke cycle, degrees 0..720 (0 = TDC firing). */
export function cycleDeg(thetaDeg, cyl) {
  return mod(thetaDeg - FIRE_DEG[cyl], 720);
}

export const STROKES = ['power', 'exhaust', 'intake', 'compression'];
export function strokeOf(thetaDeg, cyl) {
  return STROKES[Math.floor(cycleDeg(thetaDeg, cyl) / 180)];
}

function lift(c, ev) {
  let span = ev.close - ev.open;
  let x = mod(c - ev.open, 720);
  if (x > span) return 0;
  return Math.sin((Math.PI * x) / span);
}

/** Valve lift fraction 0..1 for 'intake' | 'exhaust'. */
export function valveLift(thetaDeg, cyl, kind) {
  return lift(cycleDeg(thetaDeg, cyl), VALVE_EVENTS[kind]);
}

/** True while the plug would fire (a short window around the spark advance). */
export function sparkActive(thetaDeg, cyl, windowDeg = 18) {
  const c = cycleDeg(thetaDeg + SPARK_BTDC, cyl);
  return c < windowDeg || c > 720 - 2;
}

/** Order in which cylinders reach TDC-compression starting from theta = 0. */
export function firingSequence() {
  return Object.entries(FIRE_DEG).sort((a, b) => a[1] - b[1]).map(([c]) => Number(c));
}
