// What each control of the cockpit does when the pilot's hand works it (cockpit.js is the hand and the eye).
// Plain logic, no drawing, so the tests can work every control without a browser.
//
// A control is named by its part in the Phase 8 model. It acts on the systems state (s, shared/js/sim.js) and,
// for what the systems state does not hold (flaps, trim, the wheel, the brakes, the doors), on a host (h) that
// the application supplies: on the apron the host moves the model, in flight it flies the aircraft.
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const pct = (x) => `${Math.round(x * 100)} %`;
const onOff = (x) => (x ? 'ON' : 'OFF');
const IGNITION = ['OFF', 'R', 'L', 'BOTH'], FUEL = ['LEFT', 'BOTH', 'RIGHT', 'OFF'];
const SWITCHES = { 'PANEL.master_bat': 'masterBat', 'PANEL.master_alt': 'masterAlt', 'PANEL.switch_avionics_master': 'avionics', 'PANEL.switch_beacon': 'beacon', 'PANEL.switch_nav_lights': 'navLights',
  'PANEL.switch_landing_light': 'landingLight', 'PANEL.switch_pitot_heat': 'pitotHeat', 'PANEL.switch_strobe': 'strobe' };

/**
 * The controls a hand can work, by the name of their part. For each: what it shows (state), and what a press,
 * a click, a drag or the mouse wheel does to it. s: the systems state; h: the host (see FirstPerson);
 * at: { upper, right } — which half of the control the pointer is on.
 */
export function cockpitControls() {
  const push = (key, sign) => ({      // a push-pull control: pulled toward the pilot is down the picture
    state: (s) => pct(s.controls[key]),
    drag: (s, h, d) => { s.controls[key] = clamp(s.controls[key] + (sign * d.dy) / 170, 0, 1); },
    wheel: (s, h, step) => { s.controls[key] = clamp(s.controls[key] + sign * step * 0.04, 0, 1); },
  });
  const t = {
    'PANEL.throttle': push('throttle', -1),
    'PANEL.mixture': push('mixture', -1),
    'PANEL.carb_heat': { ...push('carbHeat', 1), state: (s) => onOff(s.controls.carbHeat > 0.5), click: (s) => { s.controls.carbHeat = s.controls.carbHeat > 0.5 ? 0 : 1; } },
    'PANEL.ignition_switch': {      // the key turns one position at a time; START is sprung, held only while pressed
      state: (s) => s.controls.ignition,
      press: (s, h, at) => { if (!at.right || s.controls.ignition !== 'BOTH') return null; s.controls.ignition = 'START'; return () => { if (s.controls.ignition === 'START') s.controls.ignition = 'BOTH'; }; },
      click: (s, h, at) => { s.controls.ignition = IGNITION[clamp(IGNITION.indexOf(s.controls.ignition) + (at.right ? 1 : -1), 0, 3)]; },
      wheel: (s, h, step) => { s.controls.ignition = IGNITION[clamp(IGNITION.indexOf(s.controls.ignition) - step, 0, 3)]; },
    },
    'FUEL.selector_handle': {       // LEFT, BOTH, RIGHT, OFF round the dial, clockwise
      state: (s) => s.controls.fuelSelector,
      click: (s, h, at) => { s.controls.fuelSelector = FUEL[(FUEL.indexOf(s.controls.fuelSelector) + (at.right ? 1 : 3)) % 4]; },
      wheel: (s, h, step) => { s.controls.fuelSelector = FUEL[(FUEL.indexOf(s.controls.fuelSelector) + (step < 0 ? 1 : 3)) % 4]; },
    },
    'PANEL.flap_switch': {          // the lever selects a position, the motor follows: up is flaps up
      state: (s, h) => `${Math.round(h.flaps.get())}°`,
      click: (s, h, at) => h.flaps.set(clamp(Math.round(h.flaps.get() / 10) * 10 + (at.upper ? -10 : 10), 0, 40)),
      wheel: (s, h, step) => h.flaps.set(clamp(Math.round(h.flaps.get() / 10) * 10 + step * 10, 0, 40)),
    },
    'INTERIOR.trim_wheel': {        // the rim rolled down is nose up
      state: (s, h) => (h.trim.get() >= 0 ? '+' : '−') + Math.abs(h.trim.get()).toFixed(2),
      drag: (s, h, d) => h.trim.set(clamp(h.trim.get() + d.dy / 600, -1, 1)),
      wheel: (s, h, step) => h.trim.set(clamp(h.trim.get() + step * 0.01, -1, 1)),
    },
    'INTERIOR.yoke_L': {            // the hand holds the wheel: across turns it, down the picture pulls it back
      state: () => '',
      grab: (s, h) => h.yoke.get(),
      drag: (s, h, d) => h.yoke.set(clamp(d.from.x + d.tx / 150, -1, 1), clamp(d.from.y + d.ty / 150, -1, 1)),
      release: (s, h) => h.yoke.release(),
    },
    'PANEL.primer': { state: (s, h) => String(h.primes()), click: (s, h) => h.prime() },
    'INTERIOR.parking_brake': { state: (s, h) => onOff(h.parking.get()), click: (s, h) => h.parking.toggle() },
    'PANEL.cabin_heat': { state: (s, h) => onOff(h.cabin.get('cabinHeat')), click: (s, h) => h.cabin.toggle('cabinHeat') },
    'PANEL.cabin_air': { state: (s, h) => onOff(h.cabin.get('cabinAir')), click: (s, h) => h.cabin.toggle('cabinAir') },
    'INTERIOR.door_inner_handle_L': { fixed: true, state: (s, h) => h.door.state('L'), click: (s, h) => h.door.toggle('L') },
    'INTERIOR.door_inner_handle_R': { fixed: true, state: (s, h) => h.door.state('R'), click: (s, h) => h.door.toggle('R') },
  };
  for (const [part, key] of Object.entries(SWITCHES)) t[part] = { state: (s) => onOff(s.controls[key]), click: (s) => { s.controls[key] = !s.controls[key]; } };
  return t;
}
