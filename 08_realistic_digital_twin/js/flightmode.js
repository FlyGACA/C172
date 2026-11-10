// Flight mode of the Phase 8 viewer: the flight model flies the aircraft of the 3D scene.
//
// The flight deck (shared/js/flightdeck.js) steps the flight model and the systems simulation together. This
// module gives it a world to fly in (ground, runway, haze), places the model where the flight is, follows it
// with the camera, reads the pilot's hands and feet (keys, the on-screen yoke) and shows the numbers.
import * as THREE from 'three';
import { createDeck, stepDeck, deckInFlight, deckOnGround } from './flightdeck.js';
import { createFlight, setWind, FM, gearGeometry, cgStation, coefficientTable, trim as trimFor, kcasFromKias, fullThrottleTorque, chargeAt } from './flight.js';
import { createPilot, pilotStep } from './pilot.js';
import { propellerBalance } from './flight.js';
import { createState } from './sim.js';

const D2R = Math.PI / 180, FT = 0.3048, NM = 1852;
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const Y = new THREE.Vector3(0, 1, 0);

/** Where a flight can begin. */
export const PRESETS = {
  runway: { kind: 'ground' },
  cruise: { kind: 'air', kias: 100, aglFt: 3000, flapDeg: 0, north: 0 },
  approach: { kind: 'air', kias: 70, aglFt: 600, flapDeg: 20, climbFpm: -450, north: -1.25 * NM },
};
export const RUNWAY = { length: 1500, width: 23, start: -40 };     // metres; the aircraft starts at the origin, heading north along it

/** The systems as they are just before takeoff: engine warm and running, electrics on. */
export function readySystems() {
  return createState({
    controls: { masterBat: true, masterAlt: true, avionics: true, ignition: 'BOTH', mixture: 1, throttle: 0, fuelSelector: 'BOTH', beacon: true, navLights: true },
    engine: { running: true, rpm: 700, oilTempF: 170, oilPress: 60 },
    vac: { suction: 4.9, gyro: 1 },
  });
}

// ---------------------------------------------------------------------------------------------- the world
function seeded(seed) { let s = seed >>> 0; return () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }; }

function fieldsTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 1024;
  const g = c.getContext('2d'), rnd = seeded(172);
  const tones = ['#6f8450', '#7b8c57', '#8a8f5c', '#5f7748', '#9a956a', '#667d4c', '#84895a', '#74834f'];
  g.fillStyle = '#70824f'; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 8; i++) for (let j = 0; j < 8; j++) {          // fields
    g.fillStyle = tones[Math.floor(rnd() * tones.length)];
    g.fillRect(i * 128 + 2, j * 128 + 2, 124, 124);
    if (rnd() > 0.55) { g.fillStyle = 'rgba(40,60,30,0.10)'; for (let k = 0; k < 14; k++) g.fillRect(i * 128 + 2, j * 128 + 6 + k * 9, 124, 3); }      // furrows
  }
  g.strokeStyle = 'rgba(58,66,44,0.55)'; g.lineWidth = 3;             // hedges and tracks: they wrap, so the tiles join
  for (let i = 0; i <= 8; i++) { g.beginPath(); g.moveTo(i * 128, 0); g.lineTo(i * 128, 1024); g.moveTo(0, i * 128); g.lineTo(1024, i * 128); g.stroke(); }
  g.strokeStyle = 'rgba(190,182,160,0.8)'; g.lineWidth = 5; g.beginPath(); g.moveTo(0, 384); g.lineTo(1024, 384); g.moveTo(640, 0); g.lineTo(640, 1024); g.stroke();   // roads
  for (let k = 0; k < 9000; k++) { g.fillStyle = rnd() > 0.5 ? 'rgba(255,255,255,0.035)' : 'rgba(0,0,0,0.05)'; g.fillRect(rnd() * 1024, rnd() * 1024, 2 + rnd() * 5, 2 + rnd() * 5); }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}

function runwayTexture() {
  const c = document.createElement('canvas'); c.width = 128; c.height = 4096;
  const g = c.getContext('2d'), rnd = seeded(36);
  const m = c.height / RUNWAY.length;                                 // pixels a metre along the runway
  g.fillStyle = '#3b3d40'; g.fillRect(0, 0, 128, 4096);
  for (let k = 0; k < 5000; k++) { g.fillStyle = rnd() > 0.5 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.10)'; g.fillRect(rnd() * 128, rnd() * 4096, 1 + rnd() * 3, 2 + rnd() * 9); }
  g.fillStyle = '#e8e8e2';
  g.fillRect(3, 0, 3, 4096); g.fillRect(122, 0, 3, 4096);              // edge lines
  for (let y = 120; y < RUNWAY.length - 120; y += 50) g.fillRect(62, y * m, 4, 30 * m);     // centre line
  for (const y of [6, RUNWAY.length - 36]) for (let i = 0; i < 8; i++) g.fillRect(12 + i * 13.5 + (i > 3 ? 4 : 0), y * m, 8, 30 * m);     // thresholds
  g.font = 'bold 44px sans-serif'; g.textAlign = 'center';
  // the canvas is seen upright by a pilot at the bottom of it heading north: his number (36) reads upright, the far one (18) is for the other way
  g.save(); g.translate(64, 60 * m); g.rotate(Math.PI); g.scale(1, m * 0.55); g.fillText('18', 0, 0); g.restore();
  g.save(); g.translate(64, (RUNWAY.length - 60) * m); g.scale(1, m * 0.55); g.fillText('36', 0, 0); g.restore();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}

// ---------------------------------------------------------------------------------------------- the mode
export class FlightMode {
  constructor({ viewer, rig, hud, pad }) {
    this.viewer = viewer; this.rig = rig; this.hud = hud; this.pad = pad;
    this.active = false; this.deck = null; this.preset = 'runway';
    this.camera = 'chase';
    this.assist = { rudder: true, level: false };
    this.conditions = { weightLb: 2300, cgFrac: 0.5, windFromDeg: 0, windKt: 0, isaDevC: 0 };
    this.keys = new Set();
    this.stick = { x: 0, y: 0, rudder: 0, dragging: false };
    this.trim = 0; this.flapCommand = 0; this.parking = true; this.brakeHeld = false;
    this.head = { yaw: 0, pitch: -11 * D2R };
    this.pilot = createPilot();
    this.crashed = null;
    this.onChange = () => {};
    this._lastHeading = 0; this._lastPos = new THREE.Vector3();
    this._q = new THREE.Quaternion(); this._v = new THREE.Vector3();
    this._bindKeys();
    if (pad) this._bindPad(pad);
  }

  // ---- world
  _buildWorld() {
    const scene = this.viewer.scene;
    const world = new THREE.Group(); world.name = '_flightWorld';
    const fields = fieldsTexture(); fields.repeat.set(25, 25);          // a tile of fields is 2.4 km wide
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(60000, 60000), new THREE.MeshStandardMaterial({ map: fields, roughness: 1, metalness: 0, depthWrite: false }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -0.02; ground.receiveShadow = true; ground.renderOrder = -3;
    const runway = new THREE.Mesh(new THREE.PlaneGeometry(RUNWAY.width, RUNWAY.length), new THREE.MeshStandardMaterial({ map: runwayTexture(), roughness: 0.95, metalness: 0, depthWrite: false }));
    runway.rotation.x = -Math.PI / 2; runway.rotation.z = Math.PI;      // the texture's start at the aircraft's end
    runway.position.set(0, 0, RUNWAY.start + RUNWAY.length / 2); runway.receiveShadow = true; runway.renderOrder = -2;
    world.add(ground, runway);
    scene.add(world);
    this.world = world; this.ground = ground;
  }

  // ---- entering and leaving
  /** Begin a flight. sim: the systems state to fly with (the caller keeps using it). */
  start(preset, sim) {
    const v = this.viewer, c = this.conditions;
    if (!this.world) this._buildWorld();
    if (!this.pivot) {
      // the model turns about its centre of gravity: find that point in the model, from the main wheels
      const wheel = this.rig.part('GEAR.main_wheel_L.tyre');
      const centre = new THREE.Box3().setFromObject(wheel).getCenter(new THREE.Vector3());
      const station = cgStation(c.weightLb, c.cgFrac);
      this.cgModel = new THREE.Vector3(0, FM.cgHeight.v, centre.z + gearGeometry(station, c.weightLb * 0.45359237).mainBehindCg);
      this.pivot = new THREE.Group(); this.pivot.name = '_aircraftPivot';
      const rest = (FM.groundPitchDeg.v * D2R) / 2;
      this.restInverse = new THREE.Quaternion(Math.sin(rest), 0, 0, Math.cos(rest));      // the model is drawn standing on its wheels, nose up
    }
    if (!this.active) {
      v.scene.add(this.pivot); this.pivot.add(v.model); v.model.position.copy(this.cgModel).multiplyScalar(-1);
      this.saved = { far: v.camera.far, near: v.camera.near, fov: v.camera.fov, fog: v.scene.fog, maxPolar: v.controls.maxPolarAngle, maxDistance: v.controls.maxDistance, groundVisible: v.ground ? v.ground.visible : true };
      v.camera.far = 45000; v.camera.updateProjectionMatrix();
      v.scene.fog = new THREE.Fog(0xc3d2e2, 3500, 32000);
      v.controls.maxPolarAngle = Math.PI * 0.97; v.controls.maxDistance = 400;
      if (v.ground) v.ground.visible = false;
      this.world.visible = true;
    }
    this.active = true; this.preset = preset; this.crashed = null;
    const p = PRESETS[preset] || PRESETS.runway;
    const flight = createFlight({ weightLb: c.weightLb, cgFrac: c.cgFrac, isaDevC: c.isaDevC, windFromDeg: c.windFromDeg, windKt: c.windKt, flapDeg: p.flapDeg ?? 0 });
    this.deck = createDeck(sim, flight);
    this.pilot = createPilot();
    this.stick.x = this.stick.y = this.stick.rudder = 0;
    if (p.kind === 'air') {
      flight.north = p.north ?? 0;
      const tr = deckInFlight(this.deck, { kias: p.kias, altFt: flight.fieldElevFt + p.aglFt, flapDeg: p.flapDeg ?? 0, climbFpm: p.climbFpm ?? 0, headingDeg: 0 });
      this.trim = tr.trim; this.flapCommand = p.flapDeg ?? 0; this.parking = false;
    } else {
      deckOnGround(this.deck, 0);
      // takeoff trim: where the trim holds the climb at 73 KIAS with full throttle (the TAKEOFF mark of the trim wheel)
      const charge = chargeAt(flight.fieldElevFt, c.isaDevC);
      this.trim = trimFor({ kcas: kcasFromKias(73), altFt: flight.fieldElevFt, isaDevC: c.isaDevC, weightLb: c.weightLb, cgFrac: c.cgFrac, torque: fullThrottleTorque(charge) }).trim;
      this.flapCommand = 0; this.parking = true;
    }
    this.place();
    this._lastHeading = this.deck.flight.out.headingDeg || 0; this._lastPos.copy(this.pivot.position);
    this.setCamera(this.camera, true);
    this.onChange();
    return this.deck;
  }

  stop() {
    if (!this.active) return;
    const v = this.viewer;
    this.active = false;
    v.scene.add(v.model); v.model.position.set(0, 0, 0); v.model.quaternion.identity();
    v.scene.remove(this.pivot);
    v.camera.far = this.saved.far; v.camera.near = this.saved.near; v.camera.fov = this.saved.fov; v.camera.updateProjectionMatrix();
    v.scene.fog = this.saved.fog; v.controls.maxPolarAngle = this.saved.maxPolar; v.controls.maxDistance = this.saved.maxDistance;
    if (v.ground) v.ground.visible = this.saved.groundVisible;
    this.world.visible = false;
    v.manualCamera = false; v.controls.enabled = true;
    v.sun.position.sub(v.sun.target.position); v.sun.target.position.set(0, 0, 0);
    if (this.deck) { delete this.deck.sim.flight.dynamic; this.deck.sim.flight.onGround = true; this.deck.sim.flight.bank = 0; this.deck.sim.flight.pitch = 0; this.deck.sim.flight.iasTarget = 0; this.deck.sim.flight.altTarget = 0; }
    const st = this.rig.state; st.aileron = st.elevator = st.rudder = st.trim = 0; st.flaps = 0;
    this.deck = null;
    this.keys.clear();
    this.onChange();
  }

  /** The systems state was replaced (reset, a scenario): fly on with the new one. */
  bindSim(sim) { if (this.deck) { this.deck.sim = sim; stepDeck(this.deck, {}, 0); } }

  // ---- the pilot's hands and feet
  _bindKeys() {
    const flightKeys = new Set(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'KeyZ', 'KeyX', 'KeyB', 'Space', 'KeyF', 'KeyV', 'PageUp', 'PageDown', 'Equal', 'Minus', 'BracketLeft', 'BracketRight', 'KeyP', 'KeyC']);
    addEventListener('keydown', (e) => {
      if (!this.active || !flightKeys.has(e.code) || e.ctrlKey || e.metaKey || e.altKey) return;
      const t = e.target;
      if (t && (t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'range'))) return;
      if (t && t.tagName === 'INPUT') t.blur();                         // a slider would take the arrow keys for itself
      e.preventDefault();
      if (e.repeat) return;
      this.keys.add(e.code);
      if (e.code === 'KeyF') this.setFlaps(Math.min(40, this.flapCommand + 10));
      if (e.code === 'KeyV') this.setFlaps(Math.max(0, this.flapCommand - 10));
      if (e.code === 'KeyP') { this.parking = !this.parking; this.onChange(); }
      if (e.code === 'KeyC') this.setCamera(this.camera === 'chase' ? 'cockpit' : 'chase');
    });
    addEventListener('keyup', (e) => this.keys.delete(e.code));
    addEventListener('blur', () => this.keys.clear());
  }

  _bindPad(pad) {
    const knob = pad.querySelector('i');
    const set = (e) => {
      const r = pad.getBoundingClientRect();
      this.stick.x = clamp(((e.clientX - r.left) / r.width) * 2 - 1, -1, 1);
      this.stick.y = clamp(((e.clientY - r.top) / r.height) * 2 - 1, -1, 1);     // down on the pad is back on the wheel
    };
    pad.addEventListener('pointerdown', (e) => { pad.setPointerCapture(e.pointerId); this.stick.dragging = true; set(e); e.preventDefault(); });
    pad.addEventListener('pointermove', (e) => { if (this.stick.dragging) set(e); });
    const up = () => { this.stick.dragging = false; };
    pad.addEventListener('pointerup', up); pad.addEventListener('pointercancel', up);
    this._knob = knob;
  }

  setFlaps(deg) { this.flapCommand = clamp(deg, 0, 40); this.onChange(); }
  setTrim(t) { this.trim = clamp(t, -1, 1); }

  _controls(dt) {
    const k = this.keys, s = this.stick, f = this.deck.flight, o = f.out;
    const sim = this.deck.sim;
    // the wheel: the keys push it toward a position, it springs back; the pad holds it where the finger is
    if (!s.dragging) {
      // a held key moves the wheel steadily, up to less than half its travel; released, the wheel comes back faster
      const tx = (k.has('ArrowRight') ? 0.5 : 0) - (k.has('ArrowLeft') ? 0.5 : 0), ty = (k.has('ArrowDown') ? 0.4 : 0) - (k.has('ArrowUp') ? 0.4 : 0);
      s.x += clamp(tx - s.x, -(tx === 0 ? 3 : 1.4) * dt, (tx === 0 ? 3 : 1.4) * dt);
      s.y += clamp(ty - s.y, -(ty === 0 ? 2 : 0.45) * dt, (ty === 0 ? 2 : 0.45) * dt);
    }
    const tr = (k.has('KeyX') ? 0.7 : 0) - (k.has('KeyZ') ? 0.7 : 0);
    s.rudder += clamp(tr - s.rudder, -3 * dt, 3 * dt);
    if (k.has('BracketRight')) this.trim = clamp(this.trim + 0.12 * dt, -1, 1);
    if (k.has('BracketLeft')) this.trim = clamp(this.trim - 0.12 * dt, -1, 1);
    const more = k.has('PageUp') || k.has('Equal'), less = k.has('PageDown') || k.has('Minus');
    if (more || less) { sim.controls.throttle = clamp(sim.controls.throttle + (more ? 0.45 : -0.45) * dt, 0, 1); this.onChange(); }
    // the feet: the pedals, and the assistant that keeps the ball in the middle (on the ground it steers with the wheel)
    let aileron = s.x, rudder = s.rudder;
    if (this.assist.rudder) {
      if (o.onGround) {
        // on the ground the feet keep the aircraft straight: they hold the heading it was last steered to
        const steer = s.rudder + s.x;
        if (Math.abs(steer) > 0.05 || o.groundSpeedKt < 3 || this._heading == null) this._heading = o.headingDeg;
        const off = ((this._heading - o.headingDeg + 540) % 360) - 180;
        rudder = clamp(steer + 0.12 * off - 1.2 * f.r, -1, 1);
      } else {
        // in the air hand and foot hold what the propeller asks, and the feet keep the nose into the wind and damp the yaw
        this._heading = null;
        const hold = propellerBalance(f), v = Math.max(20, o.ktas * 0.514444), gain = clamp((70 / Math.max(40, o.kias)) ** 2, 0.25, 2.5);
        const turning = (9.80665 * Math.sin(o.bankDeg * D2R)) / v;
        rudder = clamp(hold.rudder + 1.5 * gain * o.betaDeg * D2R - 1.5 * gain * (f.r - turning) + s.rudder, -1, 1);
        aileron += hold.aileron;
      }
    }
    if (this.assist.level && !o.onGround && Math.abs(s.x) < 0.02) aileron = pilotStep(this._leveller || (this._leveller = createPilot()), f, { elevator: 0, bankDeg: 0, rudder: 0 }, dt).aileron;
    const brake = this.parking || this.brakeHeld || k.has('KeyB') || k.has('Space') ? 1 : 0;
    return { aileron: clamp(aileron, -1, 1), elevator: clamp(s.y, -1, 1), rudder, trim: this.trim, flapCommandDeg: this.flapCommand, brake };
  }

  // ---- each frame
  /** Advance the flight and the systems by dt seconds. */
  step(dt) {
    if (!this.active || this.crashed) return;
    const f = this.deck.flight;
    const before = { vs: f.out.vsFpm, onGround: f.out.onGround };
    stepDeck(this.deck, this._controls(dt), dt);
    const o = f.out;
    // what the landing gear of the model cannot take is the end of the flight
    if (o.onGround && !before.onGround && before.vs < -900) this.crashed = 'hard';
    else if (o.onGround && (Math.abs(o.bankDeg) > 30 || o.pitchDeg < -10 || o.pitchDeg > 22)) this.crashed = 'attitude';
    else if (o.aglFt < -3) this.crashed = 'ground';
    if (this.crashed) this.onChange();
  }

  /** Put the model where the flight is, move the surfaces, follow with the camera, show the numbers. */
  place() {
    if (!this.active) return;
    const f = this.deck.flight, o = f.out, v = this.viewer, st = this.rig.state;
    this.pivot.position.set(-f.east, f.alt - f.fieldElevFt * FT, f.north);
    this._q.set(-f.quat[2], -f.quat[3], f.quat[1], f.quat[0]);
    this.pivot.quaternion.copy(this._q).multiply(this.restInverse);
    this.pivot.updateMatrixWorld(true);
    // the surfaces and the cockpit controls follow the flight
    const c = this.deck.controls;
    st.aileron = c.aileron; st.rudder = c.rudder; st.trim = c.trim; st.flaps = f.flapDeg;
    const e = o.elevatorDeg ?? 0;
    st.elevator = e < 0 ? -e / FM.elevatorUpDeg.v : -e / FM.elevatorDownDeg.v;
    // the sun's shadow stays under the aircraft; the ground stays under the camera
    const pos = this.pivot.position;
    v.sun.position.sub(v.sun.target.position).add(pos); v.sun.target.position.copy(pos);
    this.ground.position.x = Math.round(pos.x / 2400) * 2400; this.ground.position.z = Math.round(pos.z / 2400) * 2400;
    this._follow();
    if (this.hud) this._hud();
    if (this._knob) { this._knob.style.left = `${50 + this.stick.x * 42}%`; this._knob.style.top = `${50 + this.stick.y * 42}%`; }
  }

  setCamera(kind, reset = false) {
    const v = this.viewer;
    const changed = kind !== this.camera;
    this.camera = kind;
    if (!this.active) return;
    if (kind === 'cockpit') {
      v.manualCamera = true; v.controls.enabled = false; v.camAnim = null;
      v.camera.near = 0.03; v.camera.fov = 68; v.camera.updateProjectionMatrix();      // an eye takes in more than the viewer's lens
      if (changed || reset) { this.head.yaw = 0; this.head.pitch = -11 * D2R; }
    } else {
      v.manualCamera = false; v.controls.enabled = true; v.camAnim = null;
      v.camera.near = 0.4; v.camera.fov = this.saved.fov; v.camera.updateProjectionMatrix();
      if (changed || reset) {
        // behind the tail, a little to the left and above
        const psi = (this.deck.flight.out.headingDeg || 0) * D2R;
        const back = new THREE.Vector3(11 * Math.sin(psi) + 3.5 * Math.cos(psi), 3.2, -11 * Math.cos(psi) + 3.5 * Math.sin(psi));
        v.controls.target.copy(this.pivot.position);
        v.camera.position.copy(this.pivot.position).add(back);
      }
    }
    this.onChange();
  }

  _follow() {
    const v = this.viewer, pos = this.pivot.position, o = this.deck.flight.out;
    if (this.camera === 'cockpit') {
      // the pilot's eye, carried by the aircraft; the head turns within what a neck allows
      this._v.set(0.28, 1.55, 0.015).sub(this.cgModel);
      v.camera.position.copy(this._v).applyQuaternion(this.pivot.quaternion).add(pos);
      const look = new THREE.Quaternion().setFromEuler(new THREE.Euler(FM.groundPitchDeg.v * D2R + this.head.pitch, Math.PI + this.head.yaw, 0, 'YXZ'));
      v.camera.quaternion.copy(this.pivot.quaternion).multiply(look);
    } else {
      // the camera keeps its place relative to the aircraft's heading; the mouse still orbits it
      let d = ((o.headingDeg || 0) - this._lastHeading) * D2R;
      if (d > Math.PI) d -= 2 * Math.PI; else if (d < -Math.PI) d += 2 * Math.PI;
      const off = this._v.copy(v.camera.position).sub(v.controls.target).applyAxisAngle(Y, -d);
      v.controls.target.copy(pos);
      v.camera.position.copy(pos).add(off);
      if (v.camera.position.y < 0.35) v.camera.position.y = 0.35;
    }
    this._lastHeading = o.headingDeg || 0; this._lastPos.copy(pos);
  }

  /** Turn the head (cockpit camera): degrees to the left and up. */
  look(dYawDeg, dPitchDeg) {
    this.head.yaw = clamp(this.head.yaw + dYawDeg * D2R, -110 * D2R, 110 * D2R);
    this.head.pitch = clamp(this.head.pitch + dPitchDeg * D2R, -55 * D2R, 40 * D2R);
  }

  _hud() {
    const o = this.deck.flight.out, s = this.deck.sim, h = this.hud;
    const set = (k, t) => { const el = h.querySelector(`[data-k=${k}]`); if (el && el.textContent !== t) el.textContent = t; };
    set('ias', String(Math.round(s.ind.ias)));
    set('alt', String(Math.round(s.ind.alt / 10) * 10));
    set('vs', String(Math.round(s.ind.vsi / 10) * 10));
    set('hdg', String(Math.round(o.headingDeg) % 360 || 360).padStart(3, '0'));
    set('rpm', String(Math.round(s.ind.rpm / 10) * 10));
    set('flap', `${Math.round(o.flapDeg)}°`);
    set('trim', (this.trim >= 0 ? '+' : '') + this.trim.toFixed(2));
    set('g', o.loadFactor.toFixed(1));
    h.classList.toggle('stall', !!s.ind.stallWarning);
    h.classList.toggle('brake', this.parking || this.brakeHeld || this.keys.has('KeyB') || this.keys.has('Space'));
    h.classList.toggle('ground', !!o.onGround);
  }

  /** The numbers of the model for a table: name, value, source, note, handbook page. */
  static coefficients() {
    const show = (v) => (Array.isArray(v) ? v.map((x) => +x.toPrecision(4)).join(', ') : String(+Number(v).toPrecision(5)));
    return coefficientTable().map((r) => ({ ...r, text: show(r.value) }));
  }

  /** Apply the wind of the conditions to a flight in progress. */
  applyWind() { if (this.deck) setWind(this.deck.flight, this.conditions.windFromDeg, this.conditions.windKt); }
}
