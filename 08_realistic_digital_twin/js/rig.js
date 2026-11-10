// Part registry and animation rig for the Phase 8 GLB (reads the extras written by blender/c172).
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import * as K from './kinematics.js';
import { valueToAngle } from './gauges.js';

const D2R = Math.PI / 180;
const AX = { x: new THREE.Vector3(1, 0, 0), y: new THREE.Vector3(0, 1, 0), z: new THREE.Vector3(0, 0, 1) };
const EXPLODE = { AIRFRAME: 0.9, WING_L: 1.0, WING_R: 1.0, EMPENNAGE: 1.0, GEAR: 0.8, POWERPLANT: 1.1, ENGINE: 0.8, INTERIOR: 0.6, PANEL: 0.25, SYSTEMS: 0.5 };

export class Rig {
  constructor(root, instr, lang = 'ar') {
    this.root = root; this.instr = instr; this.lang = lang;
    this.parts = new Map();      // name -> Object3D (has userData.system)
    this.groups = new Map();     // system -> group node
    this.base = new Map();       // obj -> { p: Vector3, q: Quaternion }
    this.explodeOff = new Map(); // obj -> Vector3 (world-space dir * distance)
    this.plugs = []; this.needles = []; this.hinges = new Map(); this.labels = [];
    this.state = { aileron: 0, elevator: 0, rudder: 0, trim: 0, flaps: 0, doorL: 0, doorR: 0, cowlOff: 0, noseSteer: 0,
      theta: 0, propAngle: 0, ind: null, controls: null, truth: null, running: false, cranking: false, magsFiring: [], flying: false };
    this.explode = 0; this.xray = false; this.showLabels = false;
    this.hiddenSystems = new Set();   // systems whose parts are not drawn
    this.tmpQ = new THREE.Quaternion(); this.tmpV = new THREE.Vector3();
    root.traverse((o) => {
      // GLTFLoader sanitises node names (drops '.'), so the build stores the canonical id in extras
      if (o.userData.id) o.name = o.userData.id;
      if (o.userData.group) this.groups.set(o.name, o);
      if (o.userData.system && !o.userData.group) this.parts.set(o.name, o);
      if (o.isMesh) {
        o.castShadow = !(o.userData.kind === 'glass'); o.receiveShadow = true;
        if (o.material) {
          if (o.userData.kind === 'glass' || o.material.transparent) { o.material.depthWrite = false; o.renderOrder = 10; o.material.side = THREE.DoubleSide; }
          if (o.material.map) o.material.map.anisotropy = 8;
        }
      }
    });
    for (const [, o] of this.parts) this.base.set(o, { p: o.position.clone(), q: o.quaternion.clone() });
    for (const [, g] of this.groups) this.base.set(g, { p: g.position.clone(), q: g.quaternion.clone() });
    this.engineNode = this.groups.get('ENGINE');
    this._collect();
    this._propellerDisc();
    this._computeExplode();
  }

  _collect() {
    for (const [name, o] of this.parts) {
      const u = o.userData;
      if (u.animate === 'plug') {
        o.traverse((m) => { if (m.isMesh) { m.material = m.material.clone(); m.material.emissive = new THREE.Color(0x000000); } });
        this.plugs.push({ obj: o, cyl: u.cyl, mag: u.magneto });
      }
      if (u.needle) this.needles.push({ obj: o, key: u.needle, axis: u.spin_axis || 'z', sign: u.spin_sign || 1 });
    }
  }

  /** A translucent disc on the propeller's axis: what a propeller turning fast looks like. Shown instead of the blades above idle. */
  _propellerDisc() {
    const prop = this.parts.get('POWERPLANT.propeller'), spinner = this.parts.get('POWERPLANT.spinner');
    if (!prop || !spinner || typeof document === 'undefined') return;
    const box = new THREE.Box3().setFromObject(prop), centre = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'), grad = g.createRadialGradient(128, 128, 8, 128, 128, 128);
    for (const [at, colour] of [[0, 'rgba(30,30,30,0)'], [0.14, 'rgba(30,30,30,0)'], [0.4, 'rgba(34,34,34,0.5)'], [0.86, 'rgba(34,34,34,0.34)'], [0.93, 'rgba(210,180,60,0.45)'], [0.97, 'rgba(34,34,34,0.25)'], [1, 'rgba(30,30,30,0)']]) grad.addColorStop(at, colour);
    g.fillStyle = grad; g.fillRect(0, 0, 256, 256);
    const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace;
    const disc = new THREE.Mesh(new THREE.CircleGeometry(Math.max(size.x, size.y) / 2, 48), new THREE.MeshBasicMaterial({ map, transparent: true, depthWrite: false, side: THREE.DoubleSide, opacity: 0, fog: false }));
    disc.name = '_propellerDisc'; disc.renderOrder = 12; disc.visible = false;
    spinner.updateWorldMatrix(true, false);
    disc.position.copy(spinner.worldToLocal(centre));
    disc.quaternion.setFromUnitVectors(AX.z, AX[spinner.userData.spin_axis || 'z']);
    spinner.add(disc);
    this.propDisc = disc; this.propBlades = prop;
  }

  part(name) { return this.parts.get(name); }
  label(o) { return (this.lang === 'ar' ? o.userData.label_ar : o.userData.label_en) || o.name; }

  // ---------------------------------------------------------------- explode
  _computeExplode() {
    const gc = new THREE.Vector3(), pc = new THREE.Vector3(), box = new THREE.Box3();
    for (const [sys, g] of this.groups) {
      box.setFromObject(g); if (box.isEmpty()) continue; box.getCenter(gc);
      const dist = EXPLODE[sys] ?? 0.6;
      for (const o of g.children) {
        if (!o.userData.system) continue;
        box.setFromObject(o); if (box.isEmpty()) continue; box.getCenter(pc);
        const dir = pc.clone().sub(gc); if (dir.length() < 1e-3) dir.set(0, 1, 0); dir.normalize();
        dir.y += 0.25; dir.normalize();
        this.explodeOff.set(o, dir.multiplyScalar(dist * (o.userData.internal ? 1.6 : 1)));
      }
    }
  }

  setExplode(f) { this.explode = f; }

  // ---------------------------------------------------------------- hinge/spin helpers
  _hinge(o, deg) {
    const u = o.userData, b = this.base.get(o);
    if (!b || !u.hinge_axis) return;
    this.tmpQ.setFromAxisAngle(AX[u.hinge_axis], deg * (u.hinge_sign || 1) * D2R);
    o.quaternion.copy(b.q).multiply(this.tmpQ);
  }
  _spin(o, rad) {
    const u = o.userData, b = this.base.get(o);
    if (!b || !u.spin_axis) return;
    this.tmpQ.setFromAxisAngle(AX[u.spin_axis], rad * (u.spin_sign || 1));
    o.quaternion.copy(b.q).multiply(this.tmpQ);
  }
  _pull(o, travel) {
    const b = this.base.get(o); if (!b) return;
    o.position.copy(b.p); o.position.z -= travel;   // toward the pilot (-Z = aft)
  }
  hinge(name, deg) { const o = this.parts.get(name); if (o) this._hinge(o, deg); }
  spin(name, rad) { const o = this.parts.get(name); if (o) this._spin(o, rad); }

  // ---------------------------------------------------------------- per-frame update
  update(dt, animSpeed) {
    const s = this.state, ind = s.ind, c = s.controls;
    // reset positions (explode offsets added last)
    for (const [o, b] of this.base) { if (o.userData.group) continue; o.position.copy(b.p); }
    // control surfaces
    const ail = s.aileron * 20;
    this.hinge('WING_L.aileron', -ail * 0.85); this.hinge('WING_R.aileron', ail * 0.85);
    this.hinge('EMPENNAGE.elevator', s.elevator > 0 ? -s.elevator * 28 : -s.elevator * 23);
    this.hinge('EMPENNAGE.rudder', s.rudder * 16);
    this.hinge('EMPENNAGE.trim_tab', -s.trim * 20);
    this.hinge('WING_L.flap', s.flaps); this.hinge('WING_R.flap', s.flaps);
    this.hinge('AIRFRAME.door_L', s.doorL * 62); this.hinge('AIRFRAME.door_R', s.doorR * 62);
    this.hinge('GEAR.nose_strut', s.rudder * 10);
    // cowl removal: lift and slide forward
    const cowl = this.parts.get('POWERPLANT.cowl_upper');
    if (cowl) { const b = this.base.get(cowl); cowl.position.set(b.p.x, b.p.y + 0.9 * s.cowlOff, b.p.z + 0.4 * s.cowlOff); cowl.visible = s.cowlOff < 0.98; }
    // yokes, pedals, trim wheel
    for (const side of ['L', 'R']) {
      const y = this.parts.get(`INTERIOR.yoke_${side}`); if (y) this._spin(y, s.aileron * 80 * D2R);
      const sh = this.parts.get(`INTERIOR.yoke_shaft_${side}`); if (sh) { const b = this.base.get(sh); sh.position.copy(b.p); sh.position.z += s.elevator * 0.05; }
      this.hinge(`INTERIOR.pedal_${side}_L`, -s.rudder * 12); this.hinge(`INTERIOR.pedal_${side}_R`, s.rudder * 12);
    }
    this.spin('INTERIOR.trim_wheel', s.trim * 2.5);
    // engine controls from the sim state
    if (c) {
      const tp = this.parts.get('PANEL.throttle'); if (tp) this._pull(tp, (1 - c.throttle) * 0.085);
      const mp = this.parts.get('PANEL.mixture'); if (mp) this._pull(mp, (1 - c.mixture) * 0.07);
      const cp = this.parts.get('PANEL.carb_heat'); if (cp) this._pull(cp, c.carbHeat * 0.07);
      const ign = this.parts.get('PANEL.ignition_switch'); if (ign) this._spin(ign, ({ OFF: -70, R: -35, L: 0, BOTH: 35, START: 70 }[c.ignition] || 0) * D2R);
      const fsl = this.parts.get('FUEL.selector_handle'); if (fsl) this._spin(fsl, ({ LEFT: -90, BOTH: 0, RIGHT: 90, OFF: 180 }[c.fuelSelector] || 0) * D2R);
      this.hinge('PANEL.master_bat', c.masterBat ? 15 : -15); this.hinge('PANEL.master_alt', c.masterAlt ? 15 : -15);
      this.hinge('PANEL.switch_avionics_master', c.avionics ? 15 : -15); this.hinge('PANEL.switch_beacon', c.beacon ? 15 : -15);
      this.hinge('PANEL.switch_nav_lights', c.navLights ? 15 : -15); this.hinge('PANEL.switch_landing_light', c.landingLight ? 15 : -15);
      this.hinge('PANEL.switch_pitot_heat', c.pitotHeat ? 15 : -15); this.hinge('PANEL.switch_strobe', c.strobe ? 15 : -15);
      this.hinge('PANEL.flap_switch', -s.flaps);
      // lights
      this._lamp('ELECTRICAL.beacon', c.beacon && c.masterBat && (Math.sin(performance.now() / 90) > 0.3), 0xff2020, 6);
      this._lamp('WING_L.nav_light', c.navLights && c.masterBat, 0xff2020, 3);
      this._lamp('WING_R.nav_light', c.navLights && c.masterBat, 0x20ff40, 3);
      this._lamp('ELECTRICAL.tail_nav_light', c.navLights && c.masterBat, 0xffffff, 3);
      this._lamp('ELECTRICAL.landing_light', c.landingLight && c.masterBat, 0xffffff, 8);
      this._lamp('WING_L.strobe', c.strobe && c.masterBat && ((performance.now() % 1400) < 60), 0xffffff, 12);
      this._lamp('WING_R.strobe', c.strobe && c.masterBat && ((performance.now() % 1400) < 60), 0xffffff, 12);
    }
    // propeller / crank
    const rpm = ind ? ind.rpm : 0;
    s.theta += (rpm / 60) * 2 * Math.PI * dt * animSpeed;
    this.spin('POWERPLANT.spinner', s.theta); this.spin('ENGINE.crank_flange_pulley', s.theta);
    if (this.propDisc) {      // above idle the eye sees a disc; the slow-motion display of the engine keeps the blades
      const blur = s.flying || animSpeed >= 0.5 ? THREE.MathUtils.clamp((rpm - 300) / 500, 0, 1) : 0;
      this.propDisc.visible = blur > 0.02; this.propDisc.material.opacity = blur;
      this.propBlades.traverse((m) => { if (m.isMesh) m.visible = blur < 0.6; });
    }
    this._engineInternals(s.theta);
    // instruments
    if (ind) this._instruments(ind, s);
    // explode offsets (world dir -> parent local)
    if (this.explode > 0) {
      for (const [o, off] of this.explodeOff) {
        if (!o.parent) continue;
        this.tmpV.copy(off).multiplyScalar(this.explode);
        o.parent.getWorldQuaternion(this.tmpQ).invert();
        this.tmpV.applyQuaternion(this.tmpQ);
        o.position.add(this.tmpV);
      }
    }
  }

  _lamp(name, on, color, strength) {
    const o = this.parts.get(name); if (!o) return;
    o.traverse((m) => { if (m.isMesh && m.material) { if (!m.material.__own) { m.material = m.material.clone(); m.material.__own = true; } m.material.emissive = m.material.emissive || new THREE.Color(); m.material.emissive.set(on ? color : 0x000000); m.material.emissiveIntensity = on ? strength : 0; } });
  }

  _engineInternals(theta) {
    const crank = this.parts.get('ENGINE.crankshaft'); if (crank) this._spin(crank, theta);
    const cam = this.parts.get('ENGINE.camshaft'); if (cam) this._spin(cam, -theta / 2);
    const deg = (theta / D2R);
    for (const c of [1, 2, 3, 4]) {
      const pis = this.parts.get(`ENGINE.piston_${c}`);
      if (pis) { const b = this.base.get(pis); const [x] = K.pistonPosition(theta, c); pis.position.set(x, b.p.y, b.p.z); }
      const rod = this.parts.get(`ENGINE.rod_${c}`);
      if (rod) { const b = this.base.get(rod); const [x, y] = K.pinPosition(theta, c); rod.position.set(x, y, b.p.z); this.tmpQ.setFromAxisAngle(AX.z, K.rodAngle(theta, c)); rod.quaternion.copy(this.tmpQ); }
      for (const kind of ['intake', 'exhaust']) {
        const v = this.parts.get(`ENGINE.valve_${kind}_${c}`);
        if (v) { const b = this.base.get(v); const side = K.CYLINDERS[c].side; v.position.set(b.p.x - side * K.valveLift(deg, c, kind) * K.VALVE_LIFT, b.p.y, b.p.z); }
      }
    }
    const firing = this.state.running || this.state.cranking;
    for (const p of this.plugs) {
      const on = firing && this.state.magsFiring.includes(p.mag) && K.sparkActive(deg, p.cyl);
      p.obj.traverse((m) => { if (m.isMesh) { m.material.emissive.set(on ? 0x66aaff : 0x000000); m.material.emissiveIntensity = on ? 6 : 0; } });
    }
  }

  _instruments(ind, s) {
    const I = this.instr;
    const now = new Date();
    const val = {
      ASI: ind.ias, VSI: ind.vsi, TACH: ind.rpm, SUCTION: ind.suction, AMMETER: ind.ammeter, OIL_P: ind.oilP, OIL_T: ind.oilT,
      FUEL_L: ind.fuelL, FUEL_R: ind.fuelR, OAT: 3,
    };
    for (const n of this.needles) {
      let ang = 0;
      if (n.key in val && I[n.key]) ang = valueToAngle(I[n.key], val[n.key]);
      else if (n.key === 'ALT_100') ang = (((ind.alt % 1000) + 1000) % 1000) * 0.36;
      else if (n.key === 'ALT_1000') ang = (((ind.alt % 10000) + 10000) % 10000) * 0.036;
      else if (n.key === 'ALT_10000') ang = ind.alt * 0.0036;
      else if (n.key === 'TC') ang = (ind.tcFlag ? 0 : ind.tc) * 20;
      else if (n.key === 'CLOCK_H') ang = ((now.getHours() % 12) + now.getMinutes() / 60) * 30;
      else if (n.key === 'CLOCK_M') ang = (now.getMinutes() + now.getSeconds() / 60) * 6;
      else if (n.key === 'OAT') ang = valueToAngle({ map: [[0, 0], [12, 360]] }, 3.2);
      this._spin(n.obj, ang * D2R);
    }
    const ball = this.parts.get('PANEL.AI.ball');
    if (ball) { const b = this.base.get(ball); this._spin(ball, -ind.aiBank * D2R); ball.position.set(b.p.x, b.p.y - THREE.MathUtils.clamp(ind.aiPitch, -20, 20) * 0.0005, b.p.z); }
    const card = this.parts.get('PANEL.DG.card'); if (card) this._spin(card, -ind.hi * D2R);
    // the ball: one width of the ball for about 2.5 degrees of sideways force (+X of the model is the pilot's left)
    const tcb = this.parts.get('PANEL.TC.ball'); if (tcb) { const b = this.base.get(tcb); tcb.position.set(b.p.x - THREE.MathUtils.clamp((ind.slip || 0) / 0.12, -1, 1) * 0.014, b.p.y, b.p.z); }
    const lv = this.parts.get('PANEL.low_volt'); if (lv) this._lamp('PANEL.low_volt', !!ind.lowVoltage, 0xff3030, 2.5);
  }

  // ---------------------------------------------------------------- visibility, x-ray, labels, highlight
  setXray(on) {
    this.xray = on;
    for (const [, o] of this.parts) {
      if (!o.userData.xray) continue;
      o.traverse((m) => { if (m.isMesh && m.material) { if (!m.material.__own) { m.material = m.material.clone(); m.material.__own = true; } m.material.transparent = on; m.material.opacity = on ? 0.22 : 1; m.material.depthWrite = !on; m.renderOrder = on ? 5 : 0; } });
    }
  }
  setGroupVisible(sys, v) { const g = this.groups.get(sys); if (g) g.visible = v; }
  // A system (FUEL, CONTROLS, ...) has parts in several groups, and a part may hang on a part of another
  // system. So a system is hidden through the render layer of each of its parts, which children do not
  // inherit, and not through the visibility of a group.
  systemVisible(sys) { return !this.hiddenSystems.has(sys); }
  setSystemVisible(sys, v) { if (v) this.hiddenSystems.delete(sys); else this.hiddenSystems.add(sys); this.applySystems(); }
  isolate(sys) {
    this.hiddenSystems.clear();
    if (sys != null) for (const [, o] of this.parts) if (o.userData.system !== sys) this.hiddenSystems.add(o.userData.system);
    this.applySystems();
  }
  applySystems() {
    for (const [, o] of this.parts) {           // parents come before their children, so a child part has the last word on its own meshes
      const on = !this.hiddenSystems.has(o.userData.system);
      o.traverse((m) => { if (m !== o && m.userData.system) return; if (on) m.layers.enable(0); else m.layers.disable(0); });
    }
  }
  drawn(o) { return o.layers.isEnabled(0); }
  showAll() { for (const [, g] of this.groups) g.visible = true; for (const [, o] of this.parts) o.visible = o.name !== 'POWERPLANT.cowl_upper' || this.state.cowlOff < 0.98; }
  hide(o) { o.visible = false; }
  setFairings(on) { for (const [n, o] of this.parts) if (/wheel_fairing|leg_fairing/.test(n)) o.visible = on; }

  setConfidence(on) {
    const colours = { measured: 0x22c55e, poh: 0x3b82f6, type_data: 0xf59e0b, estimated: 0x6b7280 };
    for (const [, o] of this.parts) {
      const colour = colours[o.userData.status] ?? colours.estimated;
      o.traverse((m) => {
        if (!m.isMesh || !m.material) return;
        if (on) {
          if (!m.__confidenceOrig) m.__confidenceOrig = m.material;
          const decorate = (source) => {
            const material = source.clone();
            material.color = new THREE.Color(colour);
            material.emissive = new THREE.Color(colour);
            material.emissiveIntensity = 0.18;
            return material;
          };
          m.material = Array.isArray(m.__confidenceOrig) ? m.__confidenceOrig.map(decorate) : decorate(m.__confidenceOrig);
        } else if (m.__confidenceOrig) {
          m.material = m.__confidenceOrig;
          delete m.__confidenceOrig;
        }
      });
    }
  }

  highlight(o) {
    if (this.sel) this.sel.traverse((m) => { if (m.isMesh && m.__orig) { m.material = m.__orig; delete m.__orig; } });
    this.sel = o;
    if (!o) return;
    o.traverse((m) => { if (m.isMesh) { m.__orig = m.material; const mm = m.material.clone(); mm.emissive = new THREE.Color(0x3366ff); mm.emissiveIntensity = 0.6; m.material = mm; } });
  }

  buildLabels(lang) {
    for (const l of this.labels) l.parent && l.parent.remove(l);
    this.labels = [];
    const box = new THREE.Box3(), c = new THREE.Vector3();
    const key = ['AIRFRAME.fuselage', 'WING_L.wing', 'WING_R.wing', 'EMPENNAGE.fin', 'EMPENNAGE.stabilizer', 'POWERPLANT.propeller', 'POWERPLANT.cowl_upper', 'GEAR.nose_strut', 'GEAR.main_wheel_L.tyre', 'PITOT_STATIC.pitot_tube', 'IGNITION.dual_magneto', 'INDUCTION.carburetor', 'ELECTRICAL.alternator', 'ELECTRICAL.battery', 'ENGINE.cylinder_head_1', 'ENGINE.cylinder_head_2', 'ENGINE.cylinder_head_3', 'ENGINE.cylinder_head_4', 'OIL.sump', 'PANEL.ASI.bezel', 'PANEL.ALT.bezel', 'FUEL.selector_handle'];
    for (const n of key) {
      const o = this.parts.get(n); if (!o) continue;
      const div = document.createElement('div'); div.className = 'label'; div.textContent = (lang === 'ar' ? o.userData.label_ar : o.userData.label_en) || n;
      const l = new CSS2DObject(div);
      box.setFromObject(o); box.getCenter(c); o.worldToLocal(c); l.position.copy(c);
      o.add(l); this.labels.push(l);
    }
    this.setLabels(this.showLabels);
  }
  setLabels(on) { this.showLabels = on; for (const l of this.labels) l.visible = on; }

  partsBySystem() {
    const out = {};
    for (const [n, o] of this.parts) (out[o.userData.system] = out[o.userData.system] || []).push(o);
    return out;
  }
}
