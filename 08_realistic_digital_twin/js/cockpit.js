// First-person cockpit of the Phase 8 viewer: the pilot's head and hand.
//
// The camera is the pilot's eye in the left seat (seat.js). The head turns and the body leans within limits; a
// hand works a control only if the control is within arm's reach of a shoulder, so the far side of the panel
// needs a lean, as in the aircraft. Controls are worked on the model itself: a click on a switch, a drag on a
// push-pull control, on the trim wheel or on the control wheel.
import * as THREE from 'three';
import { HEAD, REACH, REST, VIEWS, clampHead, eyePosition, reachDistance, leanToReach } from './seat.js';
import { cockpitControls } from './cockpit_controls.js';

export { HEAD, REACH, VIEWS };
const D2R = Math.PI / 180;
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
// the systems whose parts can stand between the eye and a control
const CABIN = new Set(['INTERIOR', 'PANEL', 'INSTRUMENTS', 'AVIONICS', 'CONTROLS', 'CABIN_AIR', 'FUEL', 'BRAKES', 'ELECTRICAL', 'PITOT_STATIC', 'VACUUM', 'AIRFRAME']);
const TINT = { near: 0x3d8bff, lean: 0xf5a524, far: 0xe5484d };

export class FirstPerson {
  /**
   * host: what the controls act on —
   *   sim(): the systems state; flaps, trim: { get, set }; yoke: { get, set(x, y), release }; parking: { get, toggle };
   *   cabin: { get(key), toggle(key) }; door: { state(side), toggle(side) }; prime(), primes(); changed();
   *   select(part), pick(x, y): the part under a point of the picture; label(part); words(): the strings of the language.
   * cabinPitchDeg: how far nose-up the cabin stands in the model's own coordinates.
   */
  constructor({ viewer, rig, host, tip, cabinPitchDeg = 0 }) {
    this.viewer = viewer; this.rig = rig; this.host = host; this.tip = tip;
    this.enabled = false; this.showReach = false;
    this.head = { ...REST }; this.want = { ...REST };       // where the head is, and where it is going
    this.cabin = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -cabinPitchDeg * D2R);
    this.controls = cockpitControls();
    this.targets = [];                                       // the meshes of the controls, for the ray
    this.rest = new Map();                                   // where a control was at rest, in the model's coordinates
    viewer.model.updateWorldMatrix(true, true);
    for (const name of Object.keys(this.controls)) {
      const part = rig.part(name);
      if (!part) { delete this.controls[name]; continue; }
      part.traverse((m) => { if (m.isMesh) { m.userData.fpControl = name; this.targets.push(m); } });
      this.rest.set(name, this._centre(part));
    }
    this.ray = new THREE.Raycaster();
    this.hover = null; this.drag = null; this.keys = new Set(); this.shells = new Map();
    this.mats = {};
    for (const [k, colour] of Object.entries(TINT)) for (const strong of [false, true]) {
      this.mats[k + (strong ? '+' : '')] = new THREE.MeshBasicMaterial({ color: colour, transparent: true, opacity: strong ? 0.6 : 0.34, depthWrite: false, fog: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    }
    this._e = new THREE.Euler(0, 0, 0, 'YXZ'); this._q = new THREE.Quaternion(); this._w = new THREE.Quaternion(); this._v = new THREE.Vector3();
    this._bind();
  }

  // ---- on and off
  enable(view = null) {
    const v = this.viewer;
    if (!this.enabled) this.saved = { fov: v.camera.fov, near: v.camera.near };
    this.enabled = true;
    v.manualCamera = true; v.controls.enabled = false; v.camAnim = null;
    v.camera.near = 0.03; v.camera.updateProjectionMatrix();
    v.setIndoors?.(true);
    if (view) this.lookAt(view, true);
    this.place();
  }

  disable() {
    if (!this.enabled) return;
    const v = this.viewer;
    this._endDrag(); this._setHover(null);
    this.enabled = false; this.keys.clear(); this._paint();
    v.manualCamera = false; v.controls.enabled = true;
    v.camera.fov = this.saved.fov; v.camera.near = this.saved.near; v.camera.updateProjectionMatrix();
    v.setIndoors?.(false);
    v.renderer.domElement.style.cursor = '';
  }

  // ---- the head
  /** Turn the head by degrees (to the left, up), at once. */
  look(dYaw, dPitch) {
    this.want = clampHead({ ...this.want, yaw: this.want.yaw + dYaw, pitch: this.want.pitch + dPitch });
    this.head.yaw = this.want.yaw; this.head.pitch = this.want.pitch;
  }
  /** Lean by metres (forward, to the left). */
  lean(dForward, dSide) { this.want = clampHead({ ...this.want, forward: this.want.forward + dForward, side: this.want.side + dSide }); }
  /** Sit back up: no lean. */
  upright() { this.want = clampHead({ ...this.want, forward: 0, side: 0 }); }
  /** Send the head to a named view, or to [yaw, pitch]; the body sits back up. */
  lookAt(view, instant = false) {
    const [yaw, pitch] = Array.isArray(view) ? view : VIEWS[view] || VIEWS.ahead;
    this.want = clampHead({ ...this.want, yaw, pitch, forward: 0, side: 0, fov: REST.fov });
    if (instant) this.head = { ...this.want };
  }
  zoom(delta) { this.want = clampHead({ ...this.want, fov: this.want.fov + delta }); }
  /** Whether the head has come to rest where it was sent. */
  get settled() { return ['yaw', 'pitch', 'forward', 'side', 'fov'].every((k) => Math.abs(this.head[k] - this.want[k]) < (k === 'forward' || k === 'side' ? 0.002 : 0.2)); }

  // ---- reach
  _centre(part) {
    const c = new THREE.Box3().setFromObject(part).getCenter(new THREE.Vector3());
    this.viewer.model.worldToLocal(c);
    return [c.x, c.y, c.z];
  }
  /** Where the hand takes hold of a control, in the model's coordinates. A door's handle is taken where the closed door has it. */
  point(name) { return this.controls[name].fixed ? this.rest.get(name) : this._centre(this.rig.part(name)); }
  /** Metres from the nearer shoulder to a control. */
  distance(name) { return reachDistance(this.point(name), this.head); }
  /** 'near': within reach now; 'lean': within reach with a lean; 'far': out of reach from this seat. */
  reach(name) { const p = this.point(name); return reachDistance(p, this.head) <= HEAD.reach ? 'near' : leanToReach(p) ? 'lean' : 'far'; }

  // ---- each frame
  /** Move the head: the keys, and the easing toward where it was sent. */
  tick(dt) {
    if (!this.enabled || dt <= 0) return;
    const k = this.keys, turn = 75 * dt, move = 0.3 * dt;
    if (k.size) {
      const w = { ...this.want };
      if (k.has('KeyJ')) w.yaw += turn;
      if (k.has('KeyL')) w.yaw -= turn;
      if (k.has('KeyI')) w.pitch += turn;
      if (k.has('KeyK')) w.pitch -= turn;
      if (k.has('KeyW')) w.forward += move;
      if (k.has('KeyS')) w.forward -= move;
      if (k.has('KeyA')) w.side += move;
      if (k.has('KeyD')) w.side -= move;
      this.want = clampHead(w);
    }
    const ease = 1 - Math.exp(-dt / 0.09);
    for (const key of ['yaw', 'pitch', 'forward', 'side', 'fov']) this.head[key] += (this.want[key] - this.head[key]) * ease;
  }

  /** Put the camera at the pilot's eye, in the model wherever the model is. */
  place() {
    if (!this.enabled) return;
    const v = this.viewer, h = this.head;
    if (Math.abs(v.camera.fov - h.fov) > 0.01) { v.camera.fov = h.fov; v.camera.updateProjectionMatrix(); }
    v.model.updateWorldMatrix(true, false);
    v.camera.position.copy(v.model.localToWorld(this._v.set(...eyePosition(h))));
    // the head turns in the cabin's own axes: straight ahead is along the fuselage, not along the ground it stands on
    this._e.set(h.pitch * D2R, Math.PI + h.yaw * D2R, 0, 'YXZ');
    v.camera.quaternion.copy(v.model.getWorldQuaternion(this._w)).multiply(this.cabin).multiply(this._q.setFromEuler(this._e));
    v.camera.updateMatrixWorld(true);
    if (this.showReach) this._paint();
    if (this.hover && this.tip && !this.tip.hidden) this._showTip();
  }

  // ---- the hand
  /** The control under a point of the picture, if nothing stands in front of it. */
  _control(x, y) {
    const r = this.viewer.renderer.domElement.getBoundingClientRect(), cam = this.viewer.camera;
    this.ray.far = 2;                                                   // nothing farther than that is a control of this seat
    this.ray.setFromCamera(new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1), cam);
    const hit = this.ray.intersectObjects(this.targets, false).find((i) => shown(i.object));
    if (!hit) return null;
    const name = hit.object.userData.fpControl;
    this.ray.far = hit.distance - 0.02;
    if (this.ray.intersectObjects(this._occluders(), false).some((i) => shown(i.object))) return null;
    // which half of the control: about where it sits at rest, so that a key that has turned keeps its two halves
    const centre = this.viewer.model.localToWorld(new THREE.Vector3(...this.rest.get(name))).project(cam), at = hit.point.clone().project(cam);
    return { name, part: this.rig.part(name), at: { upper: at.y > centre.y, right: at.x > centre.x }, reach: this.reach(name) };
  }

  /**
   * A point of the picture where the hand finds a control: { x, y, at, reach }, or null if it cannot be seen from
   * where the head is. half: 'left' | 'right' | 'upper' | 'lower' asks for a point on that half of it.
   */
  locate(name, half = null) {
    const part = this.rig.part(name);
    if (!part || !this.controls[name]) return null;
    const cam = this.viewer.camera, r = this.viewer.renderer.domElement.getBoundingClientRect();
    const box = new THREE.Box3().setFromObject(part), p = new THREE.Vector3(), steps = [0.5, 0.25, 0.75, 0.1, 0.9];
    for (const fx of steps) for (const fy of steps) for (const fz of steps) {
      p.set(box.min.x + (box.max.x - box.min.x) * fx, box.min.y + (box.max.y - box.min.y) * fy, box.min.z + (box.max.z - box.min.z) * fz).project(cam);
      if (p.z > 1 || Math.abs(p.x) > 0.96 || Math.abs(p.y) > 0.96) continue;
      const x = r.left + ((p.x + 1) / 2) * r.width, y = r.top + ((1 - p.y) / 2) * r.height;
      const c = this._control(x, y);
      if (!c || c.name !== name) continue;
      if (half && !{ left: !c.at.right, right: c.at.right, upper: c.at.upper, lower: !c.at.upper }[half]) continue;
      return { x, y, at: c.at, reach: c.reach };
    }
    return null;
  }

  /** The parts of the cabin a control can hide behind: found once, the first time they are needed. */
  _occluders() {
    if (this.occluders) return this.occluders;
    const model = this.viewer.model, eye = new THREE.Vector3(...HEAD.eye), sphere = new THREE.Sphere(), toModel = new THREE.Matrix4();
    model.updateWorldMatrix(true, true);
    toModel.copy(model.matrixWorld).invert();
    this.occluders = [];
    model.traverse((m) => {
      if (!m.isMesh || m.userData.fpControl || m.userData.fpShell || m.userData.kind === 'glass') return;
      let part = m; while (part && !part.userData.system) part = part.parent;
      if (!part || !CABIN.has(part.userData.system) || part.name === 'AIRFRAME.fuselage') return;
      if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
      sphere.copy(m.geometry.boundingSphere).applyMatrix4(m.matrixWorld).applyMatrix4(toModel);
      if (sphere.center.distanceTo(eye) - sphere.radius < 1.3) this.occluders.push(m);
    });
    return this.occluders;
  }

  _setHover(c, x = 0, y = 0) {
    const before = this.hover && this.hover.name;
    this.hover = c ? { ...c, x, y } : null;
    if (before !== (c && c.name)) this._paint();
    const def = c && this.controls[c.name];
    this.viewer.renderer.domElement.style.cursor = !c ? '' : c.reach !== 'near' ? 'not-allowed' : def.drag ? 'grab' : 'pointer';
    if (!this.tip) return;
    if (c) this._showTip(); else this.tip.hidden = true;
  }

  _showTip() {
    const h = this.hover, t = this.tip, words = this.host.words();
    const reach = this.reach(h.name), state = this.controls[h.name].state(this.host.sim(), this.host);
    const text = `${this.host.label(h.part)} · ${reach === 'near' ? state : reach === 'lean' ? words.lean : words.far}`.replace(/ · $/, '');
    if (t.textContent !== text) t.textContent = text;
    t.className = reach;
    const r = this.viewer.container.getBoundingClientRect();
    t.hidden = false;
    t.style.left = `${clamp(h.x - r.left + 14, 4, Math.max(4, r.width - t.offsetWidth - 4))}px`;
    t.style.top = `${clamp(h.y - r.top + 18, 4, Math.max(4, r.height - t.offsetHeight - 4))}px`;
  }

  /** Tint the controls: the one under the pointer, and all of them by reach when that is shown. */
  _paint() {
    const want = new Map();
    if (this.enabled) {
      if (this.showReach) for (const name of Object.keys(this.controls)) want.set(name, this.reach(name));
      if (this.hover) want.set(this.hover.name, `${this.reach(this.hover.name)}+`);
    }
    for (const name of Object.keys(this.controls)) {
      const key = want.get(name) || null;
      if ((this.shells.get(name) || null) === key) continue;
      this.shells.set(name, key);
      this.rig.part(name).traverse((m) => {
        if (!m.isMesh || m.userData.fpShell) return;
        let shell = m.children.find((c) => c.userData.fpShell);
        if (!key) { if (shell) shell.visible = false; return; }
        if (!shell) {      // a skin of colour over the part: its own materials are left alone
          shell = new THREE.Mesh(m.geometry, this.mats[key]);
          shell.userData.fpShell = true; shell.raycast = () => {}; shell.renderOrder = 20; shell.castShadow = false;
          m.add(shell);
        }
        shell.material = this.mats[key]; shell.visible = true;
      });
    }
  }
  setShowReach(on) { this.showReach = !!on; this._paint(); }

  _endDrag() {
    const d = this.drag; if (!d) return;
    this.drag = null;
    if (d.undo) d.undo();
    if (d.control && this.controls[d.control.name].release) this.controls[d.control.name].release(this.host.sim(), this.host);
  }

  _bind() {
    const el = this.viewer.renderer.domElement;
    // before the viewer's own listeners on the picture, and instead of them, while the pilot's eye is the camera
    const on = (type, fn) => el.addEventListener(type, (e) => { if (this.enabled) fn(e); }, { capture: true, passive: false });
    on('pointerdown', (e) => {
      e.stopImmediatePropagation(); e.preventDefault();
      if (this.drag || (e.pointerType === 'mouse' && e.button !== 0)) return;
      const c = this._control(e.clientX, e.clientY), near = c && c.reach === 'near';
      this._setHover(c, e.clientX, e.clientY);
      const d = this.drag = { id: e.pointerId, x: e.clientX, y: e.clientY, lx: e.clientX, ly: e.clientY, moved: 0, control: near ? c : null, far: !!c && !near };
      try { el.setPointerCapture(e.pointerId); } catch { /* an event made by a test has no pointer to capture */ }
      if (!near) return;
      const def = this.controls[c.name], s = this.host.sim();
      if (def.press) { d.undo = def.press(s, this.host, c.at); if (d.undo) this.host.changed(); }
      if (def.grab) d.from = def.grab(s, this.host);
      if (def.drag) el.style.cursor = 'grabbing';
    });
    on('pointermove', (e) => {
      const d = this.drag;
      if (!d) { if (e.pointerType === 'mouse') this._setHover(this._control(e.clientX, e.clientY), e.clientX, e.clientY); return; }
      if (e.pointerId !== d.id) return;
      e.stopImmediatePropagation();
      const dx = e.clientX - d.lx, dy = e.clientY - d.ly;
      d.lx = e.clientX; d.ly = e.clientY; d.moved = Math.max(d.moved, Math.hypot(e.clientX - d.x, e.clientY - d.y));
      const def = d.control && this.controls[d.control.name];
      if (def && def.drag) {
        if (d.moved <= 3) return;
        def.drag(this.host.sim(), this.host, { dx, dy, tx: e.clientX - d.x, ty: e.clientY - d.y, from: d.from });
        this.host.changed();
        this.hover = { ...d.control, x: e.clientX, y: e.clientY }; this._showTip();
      } else if (d.moved > 5) {      // a drag anywhere else turns the head, the way the pointer goes
        const k = this.head.fov / REST.fov;
        this.look(-dx * 0.2 * k, -dy * 0.17 * k);
        if (this.tip) this.tip.hidden = true;
      }
    });
    const up = (e) => {
      const d = this.drag; if (!d || e.pointerId !== d.id) return;
      e.stopImmediatePropagation();
      const click = d.moved <= 5 && e.type === 'pointerup';
      if (click && d.control && !d.undo) { const def = this.controls[d.control.name]; if (def.click) def.click(this.host.sim(), this.host, d.control.at); }
      else if (click && !d.control && !d.far) this.host.select(this.host.pick(e.clientX, e.clientY));      // anything else: what is it?
      this._endDrag();
      this.host.changed();
      const c = this._control(e.clientX, e.clientY);
      this._setHover(c, e.clientX, e.clientY);
      // a finger has no hover: show what was touched for a moment
      if (e.pointerType !== 'mouse' && c) { clearTimeout(this._flash); this._flash = setTimeout(() => { if (!this.drag) this._setHover(null); }, 1800); }
    };
    on('pointerup', up); on('pointercancel', up);
    on('wheel', (e) => {
      e.preventDefault(); e.stopImmediatePropagation();
      const c = this.hover, step = Math.sign(e.deltaY);
      if (c && this.reach(c.name) === 'near' && this.controls[c.name].wheel) { this.controls[c.name].wheel(this.host.sim(), this.host, step); this.host.changed(); this._showTip(); } else this.zoom(step * 4);
    });
    el.addEventListener('pointerleave', () => { if (this.enabled && !this.drag) this._setHover(null); });
    const views = Object.keys(VIEWS);
    const headKeys = new Set(['KeyI', 'KeyJ', 'KeyK', 'KeyL', 'KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyR', ...views.map((_, i) => `Digit${i + 1}`)]);
    addEventListener('keydown', (e) => {
      if (!this.enabled || !headKeys.has(e.code) || e.ctrlKey || e.metaKey || e.altKey) return;
      const t = e.target;
      if (t && (t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'range'))) return;
      e.preventDefault();
      if (e.code === 'KeyR') this.lookAt('ahead');
      else if (e.code.startsWith('Digit')) this.lookAt(views[Number(e.code.slice(5)) - 1]);
      else this.keys.add(e.code);
    });
    addEventListener('keyup', (e) => this.keys.delete(e.code));
    addEventListener('blur', () => this.keys.clear());
  }
}

/** Whether an object is drawn: itself and everything it hangs on. */
function shown(o) { for (let p = o; p; p = p.parent) if (!p.visible) return false; return o.layers.isEnabled(0); }
