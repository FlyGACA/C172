// The pilot in the left seat of the Phase 8 model: where the eyes and the shoulders are as the head turns and the
// body leans, and what a hand can reach from there. Plain numbers, no drawing: the first-person camera
// (cockpit.js) and the tests both use it.
//
// Coordinates are the model's: metres, nose +Z, the pilot's left +X, up +Y. Everything here is ESTIMATED from the
// build of a seated adult in a shoulder harness and from the seat as the model draws it; nothing was measured on
// an aircraft or a pilot. The eye is where that adult's eye is on that seat: 0.77 m above the cushion pressed down
// by 3 cm, and 0.2 m ahead of the seat back at shoulder height. (The handbook's station 37, Figure 6-3, is the
// centre of gravity of the front seat occupant, which lies some 6 cm ahead of the eye here; it is not the eye.)

const D2R = Math.PI / 180;
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

/** The head and the body: limits in degrees and metres. Positive yaw is to the left, positive pitch is up. */
export const HEAD = {
  eye: [0.28, 1.63, -0.05],
  yaw: [-135, 135],                    // the neck gives about 80 degrees, the eyes and the shoulders the rest
  pitch: [-70, 55],
  leanForward: [0, 0.20],              // how far the eyes move as the body leans: the seat back behind, the harness and the wheel ahead
  leanSide: [-0.14, 0],                // to the right only: on the left the door post is a hand's width from the head
  fov: [28, 75],                       // degrees, vertical: 68 is the look of the unaided eye in this viewer
  neckBelow: 0.10, neckBehind: 0.085,  // the eyes turn about the neck, not about themselves
  shoulderBelow: 0.25, shoulderAside: 0.19, shoulderBehind: 0.045,
  shoulderShare: 0.7,                  // the shoulders move this much of what the eyes move in a lean
  torso: 0.75,                         // from the hips to the eyes: a lean swings the head about the hips, so it also comes down a little
  reach: 0.72,                         // how far from the shoulder a hand can work a control
};

/** The reach of the arm as estimated (metres). A survey may replace HEAD.reach; this stays what the model was built with. */
export const REACH = 0.72;

/**
 * The cabin of the model about the pilot, for a survey that places the eye from what a tape can reach: the floor
 * panel (its height at Z = 0 and its rise toward the nose, per metre) and the face of the instrument panel.
 */
export const CABIN = { floorY: 0.6466, floorSlope: 0.025, panelFaceZ: 0.498 };

/** Where the head rests, and views it can be sent to: [yaw, pitch] in degrees. */
export const REST = { yaw: 0, pitch: -11, forward: 0, side: 0, fov: 68 };
export const VIEWS = {
  ahead: [0, -11], panel: [0, -27], left: [80, -8], right: [-80, -8], pedestal: [-38, -50], selector: [-80, -66], overhead: [8, 50], behind: [132, -14],
};

/** A head state within the limits (a new object). */
export function clampHead(h) {
  return {
    yaw: clamp(h.yaw ?? 0, ...HEAD.yaw), pitch: clamp(h.pitch ?? 0, ...HEAD.pitch),
    forward: clamp(h.forward ?? 0, ...HEAD.leanForward), side: clamp(h.side ?? 0, ...HEAD.leanSide),
    fov: clamp(h.fov ?? REST.fov, ...HEAD.fov),
  };
}

/** How far a lean brings the head down: it swings about the hips. */
const drop = (h) => ((h.forward ?? 0) ** 2 + (h.side ?? 0) ** 2) / (2 * HEAD.torso);

/** The base of the neck: it moves with the lean. */
export function neckPosition(h) {
  return [HEAD.eye[0] + (h.side ?? 0), HEAD.eye[1] - HEAD.neckBelow - drop(h), HEAD.eye[2] - HEAD.neckBehind + (h.forward ?? 0)];
}

/** The eye: above and ahead of the neck, swinging about it as the head turns. */
export function eyePosition(h) {
  const yaw = (h.yaw ?? 0) * D2R, pitch = (h.pitch ?? 0) * D2R;
  // from the neck to the eye with the head level and straight: up and ahead; then nod (about the ear-to-ear axis), then turn
  const up = HEAD.neckBelow * Math.cos(pitch) + HEAD.neckBehind * Math.sin(pitch);
  const ahead = HEAD.neckBehind * Math.cos(pitch) - HEAD.neckBelow * Math.sin(pitch);
  const n = neckPosition(h);
  return [n[0] + ahead * Math.sin(yaw), n[1] + up, n[2] + ahead * Math.cos(yaw)];
}

/** The direction of the gaze: a unit vector. */
export function gaze(h) {
  const yaw = (h.yaw ?? 0) * D2R, pitch = (h.pitch ?? 0) * D2R;
  return [Math.cos(pitch) * Math.sin(yaw), Math.sin(pitch), Math.cos(pitch) * Math.cos(yaw)];
}

/** The two shoulders, left then right: they follow part of the lean and do not turn with the head. */
export function shoulders(h) {
  const k = HEAD.shoulderShare;
  const x = HEAD.eye[0] + (h.side ?? 0) * k, y = HEAD.eye[1] - HEAD.shoulderBelow - drop(h) * k, z = HEAD.eye[2] - HEAD.shoulderBehind + (h.forward ?? 0) * k;
  return [[x + HEAD.shoulderAside, y, z], [x - HEAD.shoulderAside, y, z]];
}

/** Metres from the nearer shoulder to a point. */
export function reachDistance(point, h = REST) {
  return Math.min(...shoulders(h).map((s) => Math.hypot(point[0] - s[0], point[1] - s[1], point[2] - s[2])));
}

export function canReach(point, h = REST) { return reachDistance(point, h) <= HEAD.reach; }

/**
 * The least lean with which a point comes within reach: { forward, side } in metres (zeros if it already is),
 * or null if no lean the seat allows brings it within reach.
 */
export function leanToReach(point) {
  if (canReach(point, REST)) return { forward: 0, side: 0 };
  let best = null;
  const steps = 12;
  for (let i = 0; i <= steps; i++) for (let j = 0; j <= steps; j++) {
    const forward = HEAD.leanForward[0] + ((HEAD.leanForward[1] - HEAD.leanForward[0]) * i) / steps;
    const side = HEAD.leanSide[0] + ((HEAD.leanSide[1] - HEAD.leanSide[0]) * j) / steps;
    if (!canReach(point, { forward, side })) continue;
    const size = Math.hypot(forward, side);
    if (!best || size < best.size) best = { forward, side, size };
  }
  return best && { forward: best.forward, side: best.side };
}

/** Whether a point is within reach now, within reach with a lean, or out of reach from the seat: 'near' | 'lean' | 'far'. */
export function reachOf(point, h = REST) {
  if (canReach(point, h)) return 'near';
  return leanToReach(point) ? 'lean' : 'far';
}

// ---------------------------------------------------------------------------------------------- a survey of the pilot
const AS_BUILT = { eye: [...HEAD.eye], reach: HEAD.reach, shoulderBelow: HEAD.shoulderBelow, shoulderAside: HEAD.shoulderAside };

/** The height of the model's floor panel at a Z. */
export const floorAt = (z) => CABIN.floorY + CABIN.floorSlope * z;

/**
 * Replace the estimates by measurements of a pilot in the seat: { eye: [x, y, z], reach, shoulderBelow, shoulderAside },
 * any of them, in metres and the model's coordinates. Returns what was replaced. HEAD.measured lists it.
 */
export function applyMeasuredSeat(m = {}) {
  const done = [];
  if (m.eye) { HEAD.eye = m.eye.map((v, i) => (Number.isFinite(v) ? v : HEAD.eye[i])); done.push('eye'); }
  for (const k of ['reach', 'shoulderBelow', 'shoulderAside']) if (Number.isFinite(m[k])) { HEAD[k] = m[k]; done.push(k); }
  if (done.length) HEAD.measured = [...new Set([...(HEAD.measured || []), ...done])];
  return done;
}

/** Put back the estimates. */
export function resetMeasuredSeat() {
  HEAD.eye = [...AS_BUILT.eye]; HEAD.reach = AS_BUILT.reach; HEAD.shoulderBelow = AS_BUILT.shoulderBelow; HEAD.shoulderAside = AS_BUILT.shoulderAside;
  delete HEAD.measured;
}
