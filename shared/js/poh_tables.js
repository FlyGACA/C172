// FlyGACA C172N — performance figures of the Pilot's Operating Handbook (Cessna Model 172N, 1978), as numbers.
//
// These are the published values the flight model is fitted to and tested against: only figures, each with
// its page. The tests (tests/flight.test.mjs) and the validation table of docs/08_flight_model.md read them here.

/** Stall speeds, power off, 2300 lb (p.5-11, Figure 5-3): KCAS at 0, 30, 45 and 60 degrees of bank. */
export const STALL_KCAS = {
  ref: 'p.5-11 Fig 5-3',
  bankDeg: [0, 30, 45, 60],
  aft: { 0: [50, 54, 59, 71], 10: [47, 51, 56, 66], 40: [44, 47, 52, 62] },      // most rearward centre of gravity; key: flap degrees
  fwd: { 0: [53, 57, 63, 75], 10: [51, 55, 61, 72], 40: [47, 51, 56, 66] },      // most forward centre of gravity
  recoveryLossFt: 180,                                                              // altitude loss during a stall recovery: as much as
};

/** Rate of climb at standard temperature, flaps up, full throttle, 2300 lb (p.5-15, Figure 5-6): [altitude ft, climb KIAS, ft/min]. */
export const CLIMB_STANDARD = {
  ref: 'p.5-15 Fig 5-6',
  rows: [[0, 73, 770], [1000, 73, 725], [2000, 72, 675], [3000, 72, 630], [4000, 71, 580], [5000, 71, 535], [6000, 70, 485], [7000, 69, 440], [8000, 69, 390],
    [9000, 68, 345], [10000, 68, 295], [11000, 67, 250], [12000, 67, 200]],
};

/** Maximum rate of climb at -20, 0, 20 and 40 °C (p.5-14, Figure 5-5): altitude: [climb KIAS, ft/min at each temperature]. */
export const CLIMB_TEMPERATURE = {
  ref: 'p.5-14 Fig 5-5',
  tempC: [-20, 0, 20, 40],
  rows: { 0: [73, 875, 815, 755, 695], 2000: [72, 765, 705, 650, 590], 4000: [71, 655, 600, 545, 485], 6000: [70, 545, 495, 440, 385], 8000: [69, 440, 390, 335, 280],
    10000: [68, 335, 285, 230, null], 12000: [67, 230, 180, null, null] },
};

/** Cruise performance at standard temperature, 2300 lb, recommended lean mixture (p.5-16, Figure 5-7): altitude: [RPM, % BHP, KTAS]. */
export const CRUISE = {
  ref: 'p.5-16 Fig 5-7',
  rows: {
    2000: [[2500, 75, 116], [2400, 67, 111], [2300, 60, 105], [2200, 53, 100], [2100, 47, 94]],
    4000: [[2550, 75, 118], [2500, 71, 115], [2400, 64, 110], [2300, 57, 105], [2200, 51, 99], [2100, 46, 93]],
    6000: [[2600, 75, 120], [2500, 67, 115], [2400, 60, 109], [2300, 54, 104], [2200, 49, 98], [2100, 44, 92]],
    8000: [[2650, 75, 122], [2600, 71, 120], [2500, 64, 114], [2400, 58, 109], [2300, 52, 103], [2200, 47, 97]],
    10000: [[2650, 71, 122], [2600, 68, 119], [2500, 61, 114], [2400, 55, 108], [2300, 50, 102], [2200, 45, 96]],
    12000: [[2600, 64, 118], [2500, 58, 113], [2400, 53, 107], [2300, 48, 101], [2200, 44, 95]],
  },
};

/** Maximum glide, propeller windmilling, flaps up (p.3-11, Figure 3-1). */
export const GLIDE = { ref: 'p.3-11 Fig 3-1', kias: 65, ratio: 9.1 };

/** Static RPM at full throttle (p.2-5). */
export const STATIC_RPM = { ref: 'p.2-5', min: 2280, max: 2400 };

/**
 * Short-field takeoff, flaps up, paved level dry runway, zero wind (p.5-12 and 5-13, Figure 5-4):
 * [field elevation ft, °C, weight lb, ground roll ft, total over 50 ft, lift-off KIAS, KIAS at 50 ft].
 */
export const TAKEOFF = {
  ref: 'p.5-12, 5-13 Fig 5-4',
  rows: [[0, 0, 2300, 720, 1300, 52, 59], [0, 20, 2300, 835, 1490, 52, 59], [0, 40, 2300, 960, 1700, 52, 59], [2000, 20, 2300, 1000, 1790, 52, 59], [4000, 20, 2300, 1210, 2175, 52, 59],
    [8000, 20, 2300, 1805, 3375, 52, 59], [0, 20, 2100, 680, 1220, 50, 56], [0, 20, 1900, 540, 985, 47, 54]],
};

/**
 * Short-field landing, flaps 40, power off, maximum braking, 60 KIAS at 50 ft, 2300 lb (p.5-21, Figure 5-10):
 * [field elevation ft, °C, ground roll ft, total over 50 ft].
 */
export const LANDING = {
  ref: 'p.5-21 Fig 5-10',
  rows: [[0, 0, 495, 1205], [0, 20, 530, 1265], [0, 40, 565, 1330], [4000, 20, 615, 1410], [8000, 20, 710, 1580]],
};

/** Stall warning: the horn sounds this many knots above the stall in all configurations (p.7-34). */
export const STALL_WARNING = { ref: 'p.7-34', knotsBefore: [5, 10] };

/** Speeds for normal operation at 2300 lb (p.4-3), KIAS. */
export const SPEEDS = {
  ref: 'p.4-3',
  bestRate: { 0: 73, 10000: 68 }, bestAngle: { 0: 59, 10000: 61 },
  normalClimbOut: [70, 80], shortFieldAt50Ft: 59,
  approachFlapsUp: [60, 70], approachFlaps40: [55, 65], shortFieldApproach: 60,
  balkedLanding: { kias: 55, flapDeg: 20 },
  maxDemonstratedCrosswindKt: 15,
};
