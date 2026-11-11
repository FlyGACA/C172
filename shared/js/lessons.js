// FlyGACA C172N — flight lessons: scripted exercises flown on the flight deck (flight model + systems).
//
// A lesson has the shape of a Phase 7 scenario (briefing, steps checked live, debrief, review question) and
// adds a place to begin the flight, a record of how it was flown (report) and a demonstration: the scripted
// pilot flies the exercise with the handbook's procedure. Faults come through the same fault panel as in the
// scenarios (the engine failure is `faults.engineFailure`).
// Checklist wording follows the Cessna 172N handbook; pages are given. The flight model has no certified fidelity.
import { evaluateSteps } from './scenarios.js';
import { readySystems, beginFlight, stepDeck } from './flightdeck.js';
import { createPilot, pilotStep, pitchFor } from './pilot.js';
import { STALL_KCAS, STALL_WARNING, SPEEDS } from './poh_tables.js';

const out = (s) => (s.flight.dynamic ? s.flight.dynamic.out : null);
const wrap = (deg) => ((deg + 540) % 360) - 180;
/** True once `ok` has held for `seconds`. */
function held(c, key, ok, dt, seconds) { c[key] = ok ? (c[key] || 0) + dt : 0; return c[key] >= seconds; }
const r0 = (x) => Math.round(x);

export const LESSONS = [
  // ------------------------------------------------------------------------------------------ stall and recovery
  {
    id: 'stall_recovery', lesson: true, focus: 'FLIGHT', poh: 'POH 4-17, 5-11',
    title: { en: 'Flight lesson: stall and recovery (power off)', ar: 'درس طيران: الانهيار والخروج منه (بلا قدرة)' },
    brief: {
      en: 'Level at 3000 ft, 80 KIAS, flaps up. Close the throttle and hold the altitude: the speed falls, the horn sounds 5 to 10 knots before the stall, then the wing stalls and the nose drops. Recover by lowering the nose first, then full throttle. The handbook says a recovery may lose as much as 180 ft.',
      ar: 'طيران مستوٍ على 3000 قدم بسرعة 80 عقدة والقلابات مرفوعة. أغلق الخانق وحافظ على الارتفاع: تهبط السرعة، ويصفر البوق قبل الانهيار بـ5 إلى 10 عقد، ثم ينهار الجناح وتهبط المقدمة. اخرج من الانهيار بإنزال المقدمة أولًا ثم الخانق الكامل. يذكر الدليل أن الخروج قد يفقد حتى 180 قدمًا.',
    },
    flight: { kind: 'air', kias: 80, aglFt: 3000 },
    steps: [
      { en: 'Carburetor heat — ON (before the throttle is closed)', ar: 'تسخين المكربن — تشغيل (قبل إغلاق الخانق)', done: (s) => s.controls.carbHeat >= 0.95 },
      { en: 'Throttle — IDLE', ar: 'الخانق — خامل', done: (s) => s.controls.throttle <= 0.05 },
      { en: 'Hold the altitude: bring the wheel back as the speed falls, until the horn sounds', ar: 'حافظ على الارتفاع: اسحب عجلة القيادة مع هبوط السرعة حتى يصفر البوق', done: (s, c) => c.hornKias != null },
      { en: 'Keep the wheel coming back until the stall', ar: 'واصل السحب حتى الانهيار', done: (s, c) => c.stallKias != null },
      { en: 'Recover: wheel forward, lower the nose', ar: 'الخروج: ادفع عجلة القيادة وأنزل المقدمة', done: (s, c) => !!c.unstalled },
      { en: 'Throttle — FULL OPEN; carburetor heat — COLD', ar: 'الخانق — مفتوح بالكامل؛ تسخين المكربن — بارد', done: (s, c) => !!c.unstalled && s.controls.throttle >= 0.95 && s.controls.carbHeat <= 0.05 },
      { en: 'Wings level, ball in the middle; climb away', ar: 'سوِّ الجناحين والكرة في الوسط؛ ثم تسلّق', done: (s, c) => !!c.recovered },
    ],
    tick(s, c, dt) {
      const o = out(s); if (!o) return;
      if (c.entryAlt == null) c.entryAlt = o.altFt;
      if (o.stallWarning && c.hornKias == null) { c.hornKias = o.kias; c.hornKcas = o.kcas; }
      if (c.stallKias == null) c.entryError = Math.max(c.entryError || 0, Math.abs(o.altFt - c.entryAlt));
      if (o.stalled && c.stallKias == null) { c.stallKias = o.kias; c.stallKcas = o.kcas; c.stallAlt = o.altFt; }
      if (c.stallKias == null) return;
      c.lowest = Math.min(c.lowest ?? o.altFt, o.altFt);
      c.maxBank = Math.max(c.maxBank || 0, Math.abs(o.bankDeg));
      if (!o.stalled && o.alphaDeg < o.alphaStallDeg - 3) c.unstalled = true;
      if (c.unstalled && o.stalled) c.secondary = true;
      if (c.unstalled && !c.recovered) c.recovered = held(c, '_climb', o.vsFpm > 100 && o.kias > 60 && Math.abs(o.bankDeg) < 10 && !o.stalled, dt, 2);
    },
    report(c) {
      if (c.stallKias == null) return [];
      const lost = r0(c.stallAlt - c.lowest);
      return [
        { en: `Horn at ${r0(c.hornKias)} KIAS, stall at ${r0(c.stallKias)} KIAS: ${r0(c.hornKcas - c.stallKcas)} knots of calibrated airspeed between them (handbook: ${STALL_WARNING.knotsBefore.join(' to ')}).`, ar: `البوق عند ${r0(c.hornKias)} عقدة والانهيار عند ${r0(c.stallKias)} عقدة: بينهما ${r0(c.hornKcas - c.stallKcas)} عقد من السرعة المعايرة (الدليل: ${STALL_WARNING.knotsBefore.join(' إلى ')}).` },
        { en: `Height lost from the stall to the lowest point: ${lost} ft (handbook: as much as ${STALL_KCAS.recoveryLossFt} ft).`, ar: `الارتفاع المفقود من الانهيار إلى أدنى نقطة: ${lost} قدمًا (الدليل: حتى ${STALL_KCAS.recoveryLossFt} قدمًا).` },
        { en: `Altitude held within ${r0(c.entryError)} ft before the stall; steepest bank ${r0(c.maxBank)}°${c.secondary ? '; the wing stalled a second time in the pull-out' : ''}.`, ar: `ثبات الارتفاع قبل الانهيار ضمن ${r0(c.entryError)} قدمًا؛ أقصى ميلان ${r0(c.maxBank)}°${c.secondary ? '؛ وانهار الجناح مرة ثانية عند رفع المقدمة' : ''}.` },
      ];
    },
    debrief: {
      en: 'A wing stalls at an angle of attack, not at a speed: the recovery is to reduce the angle of attack, so the wheel goes forward before anything else. Power then limits the height lost. Pulling up too soon or too hard stalls the wing again. The stall speeds of the handbook (Figure 5-3) are for 2300 lb, power off; the horn gives 5 to 10 knots of warning in every configuration (p.4-17). The model shows a stall and its recovery; it does not show a spin.',
      ar: 'ينهار الجناح عند زاوية هجوم لا عند سرعة: والخروج هو تقليل زاوية الهجوم، فتُدفع عجلة القيادة إلى الأمام قبل أي شيء آخر. ثم تحدّ القدرة من الارتفاع المفقود. رفع المقدمة مبكرًا أو بقوة يعيد الجناح إلى الانهيار. سرعات الانهيار في الدليل (الشكل 5-3) لوزن 2300 رطل وبلا قدرة؛ والبوق ينذر قبل الانهيار بـ5 إلى 10 عقد في كل الأوضاع (ص 4-17). النموذج يُظهر الانهيار والخروج منه، ولا يُظهر الدوران الحلزوني (spin).',
    },
    quiz: {
      q: { en: 'What is the first action of the recovery?', ar: 'ما أول عمل في الخروج من الانهيار؟' },
      options: [{ en: 'Wheel forward: reduce the angle of attack', ar: 'دفع عجلة القيادة: تقليل زاوية الهجوم' }, { en: 'Full throttle', ar: 'الخانق الكامل' }, { en: 'Level the wings with aileron', ar: 'تسوية الجناحين بالجنيحات' }],
      answer: 0, ref: 'POH 4-17',
    },
    demo(deck, c, dt) {
      const s = deck.sim, f = deck.flight, o = f.out, d = (c.demo ??= { t: 0, pilot: createPilot(), phase: 'entry', alt: o.altFt });
      d.t += dt;
      let target = { altFt: d.alt, bankDeg: 0, maxPitchDeg: 30 };
      if (d.phase === 'entry') {
        if (d.t > 1) s.controls.carbHeat = 1;
        if (d.t > 2.5) s.controls.throttle = 0;
        if (o.stalled && d.t > 2.5) { d.phase = 'recover'; d.t0 = d.t; }
      }
      if (d.phase === 'recover') {
        target = { pitchDeg: -3, bankDeg: 0 };                                   // nose down first
        if (d.t - d.t0 > 0.6) s.controls.throttle = 1;
        if (d.t - d.t0 > 1.2) s.controls.carbHeat = 0;
        if (!o.stalled && o.kias > 58 && d.t - d.t0 > 1.2) d.phase = 'climb';
      }
      if (d.phase === 'climb') target = { pitchDeg: 7, bankDeg: 0 };
      return { ...pilotStep(d.pilot, f, target, dt), flapCommandDeg: 0 };
    },
  },
  // ------------------------------------------------------------------------------------------ go-around
  {
    id: 'go_around', lesson: true, focus: 'FLIGHT', poh: 'POH 4-9, 4-20',
    title: { en: 'Flight lesson: go-around (balked landing)', ar: 'درس طيران: إعادة الإقلاع (إلغاء الهبوط)' },
    brief: {
      en: 'Short final at 150 ft: 60 KIAS, flaps 40°, carburetor heat on. The runway is not clear: go around. Follow the balked landing checklist. Full throttle pitches the nose up hard with the flaps down: hold it and keep 55 KIAS.',
      ar: 'اقتراب نهائي على 150 قدمًا: 60 عقدة، القلابات 40°، وتسخين المكربن يعمل. المدرج غير خالٍ: أعد الإقلاع. اتبع قائمة إلغاء الهبوط. الخانق الكامل يرفع المقدمة بقوة والقلابات منزلة: أمسكها وحافظ على 55 عقدة.',
    },
    flight: { kind: 'air', kias: 60, aglFt: 150, flapDeg: 40, climbFpm: -450, north: -640 },
    setup: { controls: { carbHeat: 1 } },
    steps: [
      { en: 'Throttle — FULL OPEN', ar: 'الخانق — مفتوح بالكامل', done: (s) => s.controls.throttle >= 0.95 },
      { en: 'Carburetor heat — COLD', ar: 'تسخين المكربن — بارد', done: (s) => s.controls.carbHeat <= 0.05 },
      { en: 'Wing flaps — 20° (immediately)', ar: 'القلابات — 20° (فورًا)', done: (s) => s.flight.dynamic.flapCommandDeg === 20 },
      { en: `Climb speed — ${SPEEDS.balkedLanding.kias} KIAS`, ar: `سرعة التسلق — ${SPEEDS.balkedLanding.kias} عقدة`, done: (s, c) => !!c.climbing },
      { en: 'Wing flaps — 10° (until obstacles are cleared)', ar: 'القلابات — 10° (حتى تجاوز العوائق)', done: (s, c) => s.flight.dynamic.flapCommandDeg === 10 && c.climbed >= 50 },
      { en: 'Wing flaps — RETRACT (after a safe altitude and 60 KIAS)', ar: 'القلابات — ارفعها (بعد ارتفاع آمن و60 عقدة)', done: (s, c) => s.flight.dynamic.flapCommandDeg === 0 && out(s).kias >= 58 && c.climbed >= 200 },
    ],
    tick(s, c, dt) {
      const o = out(s); if (!o) return;
      c.t = (c.t || 0) + dt;
      if (c.startAgl == null) c.startAgl = o.aglFt;
      c.minAgl = Math.min(c.minAgl ?? o.aglFt, o.aglFt);
      c.climbed = o.aglFt - c.minAgl;
      c.minKias = Math.min(c.minKias ?? o.kias, o.kias);
      c.maxPitch = Math.max(c.maxPitch ?? o.pitchDeg, o.pitchDeg);
      if (o.stallWarning) c.horn = true;
      if (s.controls.throttle >= 0.95 && c.fullAt == null) c.fullAt = c.t;
      if (s.flight.dynamic.flapCommandDeg === 20 && c.fullAt != null && c.flap20At == null) c.flap20At = c.t;
      if (!c.climbing) c.climbing = held(c, '_climb', o.vsFpm > 100 && o.kias >= 50 && o.kias <= 64, dt, 2);
    },
    report(c) {
      if (c.fullAt == null) return [];
      return [
        { en: `Lowest height above the runway: ${r0(c.minAgl)} ft (the go-around began at ${r0(c.startAgl)} ft).`, ar: `أدنى ارتفاع فوق المدرج: ${r0(c.minAgl)} قدمًا (بدأت إعادة الإقلاع عند ${r0(c.startAgl)} قدمًا).` },
        { en: `Lowest speed ${r0(c.minKias)} KIAS; highest nose attitude ${r0(c.maxPitch)}°; the stall warning ${c.horn ? 'sounded' : 'did not sound'}.`, ar: `أدنى سرعة ${r0(c.minKias)} عقدة؛ أعلى وضع للمقدمة ${r0(c.maxPitch)}°؛ بوق الانهيار ${c.horn ? 'صفر' : 'لم يصفر'}.` },
        ...(c.flap20At != null ? [{ en: `Flaps to 20° ${(c.flap20At - c.fullAt).toFixed(1)} s after full throttle.`, ar: `القلابات إلى 20° بعد ${(c.flap20At - c.fullAt).toFixed(1)} ثانية من الخانق الكامل.` }] : []),
      ];
    },
    debrief: {
      en: 'With 40° of flap the aircraft hardly climbs: the flaps come to 20° immediately after full throttle, to 10° until the obstacles are cleared, and up only at a safe altitude and 60 KIAS (p.4-9, 4-20). Each notch raised costs lift for a moment, which is why they come up in stages. The trim was set for the approach, so full throttle pitches the nose up: hold the attitude that gives 55 KIAS, then trim.',
      ar: 'مع 40° من القلابات تكاد الطائرة لا تتسلق: تُرفع القلابات إلى 20° فور الخانق الكامل، ثم إلى 10° حتى تجاوز العوائق، ولا تُرفع كليًا إلا عند ارتفاع آمن و60 عقدة (ص 4-9، 4-20). كل درجة تُرفع تُنقص الرفع لحظة، ولذلك تُرفع على مراحل. الموازنة مضبوطة للاقتراب، فالخانق الكامل يرفع المقدمة: أمسك الوضع الذي يعطي 55 عقدة ثم اضبط الموازنة.',
    },
    quiz: {
      q: { en: 'Full throttle is applied with the flaps at 40°. What comes next?', ar: 'فُتح الخانق كاملًا والقلابات عند 40°. ما التالي؟' },
      options: [{ en: 'Flaps to 20° immediately', ar: 'القلابات إلى 20° فورًا' }, { en: 'Flaps up at once', ar: 'رفع القلابات كليًا مباشرة' }, { en: 'Leave the flaps until 500 ft', ar: 'ترك القلابات حتى 500 قدم' }],
      answer: 0, ref: 'POH 4-9',
    },
    demo(deck, c, dt) {
      const s = deck.sim, f = deck.flight, o = f.out, d = (c.demo ??= { t: 0, pilot: createPilot(), flaps: 40, low: o.aglFt });
      d.t += dt; d.low = Math.min(d.low, o.aglFt);
      let target = { kias: 60, bankDeg: 0 };
      if (d.t > 1.5) s.controls.throttle = 1;
      if (d.t > 2.2) s.controls.carbHeat = 0;
      if (d.t > 2.8 && d.flaps === 40) d.flaps = 20;
      if (d.t > 1.5) target = { kias: d.flaps === 0 ? 70 : d.flaps === 10 ? 62 : SPEEDS.balkedLanding.kias, bankDeg: 0, maxPitchDeg: 20 };
      if (d.flaps === 20 && o.aglFt - d.low > 60 && o.kias > 53) d.flaps = 10;
      if (d.flaps === 10 && o.aglFt - d.low > 210 && o.kias >= 60) d.flaps = 0;
      return { ...pilotStep(d.pilot, f, target, dt), flapCommandDeg: d.flaps };
    },
  },
  // ------------------------------------------------------------------------------------------ engine failure after takeoff
  {
    id: 'engine_failure_after_takeoff', lesson: true, focus: 'FLIGHT', poh: 'POH 3-4, 3-11',
    title: { en: 'Flight lesson: engine failure after takeoff', ar: 'درس طيران: تعطل المحرك بعد الإقلاع' },
    brief: {
      en: 'Climbing out at 70 KIAS, full throttle, the runway still under the nose. The engine will fail. Lower the nose at once to hold 65 KIAS, land straight ahead with only small changes of direction, and secure the fuel and the ignition if there is time. Do not turn back.',
      ar: 'تسلّق بعد الإقلاع بسرعة 70 عقدة والخانق كامل والمدرج ما زال أمام المقدمة. سيتعطل المحرك. أنزل المقدمة فورًا للحفاظ على 65 عقدة، واهبط إلى الأمام مباشرة بتغييرات صغيرة في الاتجاه فقط، وأمّن الوقود والإشعال إن اتسع الوقت. لا تعد إلى المدرج.',
    },
    flight: { kind: 'air', kias: 70, aglFt: 100, fullThrottle: true, north: 420 },      // where a takeoff from the start of the runway has reached 100 ft
    steps: [
      { en: 'The engine fails — recognise it', ar: 'تعطل المحرك — تعرّف عليه', done: (s) => !s.engine.running },
      { en: 'Lower the nose: airspeed — 65 KIAS (flaps up), 60 KIAS (flaps down)', ar: 'أنزل المقدمة: السرعة — 65 عقدة (القلابات مرفوعة)، 60 عقدة (القلابات منزلة)', done: (s, c) => !!c.gliding },
      { en: 'Mixture — IDLE CUT-OFF', ar: 'الخليط — قطع', done: (s) => s.controls.mixture <= 0.05 },
      { en: 'Fuel selector valve — OFF', ar: 'صمام اختيار الوقود — OFF', done: (s) => s.controls.fuelSelector === 'OFF' },
      { en: 'Ignition switch — OFF', ar: 'مفتاح الإشعال — OFF', done: (s) => s.controls.ignition === 'OFF' },
      { en: 'Wing flaps — AS REQUIRED (they are electric: before the master switch)', ar: 'القلابات — حسب الحاجة (كهربائية: قبل المفتاح الرئيسي)', done: (s, c) => s.flight.dynamic.flapCommandDeg > 0 || !s.controls.masterBat || !!c.landed },
      { en: 'Master switch — OFF', ar: 'المفتاح الرئيسي — إيقاف', done: (s) => !s.controls.masterBat },
      { en: 'Land straight ahead, slightly tail low', ar: 'اهبط إلى الأمام مباشرة والذيل منخفض قليلًا', done: (s, c) => !!c.landed },
    ],
    tick(s, c, dt) {
      const o = out(s); if (!o) return;
      c.t = (c.t || 0) + dt;
      if (!c.failed && (o.aglFt >= 250 || c.t > 14)) { s.faults.engineFailure = true; c.failed = true; c.failT = c.t; c.failHeading = o.headingDeg; c.failAgl = o.aglFt; }
      if (!c.failed || s.engine.running) return;
      if (!c.landed) {
        if (!o.onGround) {
          if (o.aglFt > 50) {      // the glide; below this the round-out takes the speed off
            c.minKias = Math.min(c.minKias ?? o.kias, o.kias); c.maxKias = Math.max(c.maxKias ?? o.kias, o.kias);
            if (o.stallWarning) c.horn = true;
          }
          c.maxTurn = Math.max(c.maxTurn || 0, Math.abs(wrap(o.headingDeg - c.failHeading)));
          c.lastFpm = o.vsFpm; c.lastKias = o.kias; c.lastBank = o.bankDeg;
          if (!c.gliding && held(c, '_glide', o.kias >= 57 && o.kias <= 72, dt, 2)) { c.gliding = true; c.glideAfter = c.t - c.failT; }
        } else if (c.lastFpm != null) { c.landed = true; c.touchFpm = c.lastFpm; c.touchKias = c.lastKias; c.touchBank = c.lastBank; c.touchNorth = s.flight.dynamic.north; c.touchEast = s.flight.dynamic.east; }
      }
    },
    report(c) {
      if (!c.failed || c.minKias == null) return [];
      const lines = [
        { en: `The engine failed at ${r0(c.failAgl)} ft. In the glide the speed stayed between ${r0(c.minKias)} and ${r0(c.maxKias)} KIAS${c.glideAfter != null ? `; it was at the glide speed ${c.glideAfter.toFixed(0)} s after the failure` : ''}${c.horn ? '; the stall warning sounded in the glide' : ''}.`, ar: `تعطل المحرك على ${r0(c.failAgl)} قدمًا. في الانحدار بقيت السرعة بين ${r0(c.minKias)} و${r0(c.maxKias)} عقدة${c.glideAfter != null ? `؛ وبلغت سرعة الانحدار بعد ${c.glideAfter.toFixed(0)} ثوانٍ من التعطل` : ''}${c.horn ? '؛ وصفر بوق الانهيار أثناء الانحدار' : ''}.` },
        { en: `Largest change of heading: ${r0(c.maxTurn)}° (the handbook: only small changes in direction).`, ar: `أكبر تغيير في الاتجاه: ${r0(c.maxTurn)}° (الدليل: تغييرات صغيرة في الاتجاه فقط).` },
      ];
      if (c.landed) {
        const onRunway = Math.abs(c.touchEast ?? 0) < 11.5 && (c.touchNorth ?? 0) < 1460;
        lines.push({ en: `Touchdown at ${r0(-c.touchFpm)} ft/min and ${r0(c.touchKias)} KIAS, ${onRunway ? 'on the runway' : 'in the field beyond the runway'}.`, ar: `الملامسة بمعدل ${r0(-c.touchFpm)} قدم/دقيقة وسرعة ${r0(c.touchKias)} عقدة، ${onRunway ? 'على المدرج' : 'في الحقل بعد نهاية المدرج'}.` });
      }
      return lines;
    },
    debrief: {
      en: 'Prompt lowering of the nose to maintain airspeed and establish a glide is the first response (p.3-11). In most cases the landing is planned straight ahead with only small changes in direction to avoid obstructions: altitude and airspeed are seldom sufficient for the 180° gliding turn back to the runway. The checklist (p.3-4) secures the fuel and the ignition before touchdown if time allows; the flaps are electric, so they are set before the master switch goes off.',
      ar: 'أول استجابة هي إنزال المقدمة فورًا للحفاظ على السرعة والدخول في انحدار شراعي (ص 3-11). في معظم الحالات يُخطَّط للهبوط إلى الأمام مباشرة بتغييرات صغيرة في الاتجاه لتفادي العوائق: فالارتفاع والسرعة قلّما يكفيان لدوران شراعي 180° عودةً إلى المدرج. وقائمة الدليل (ص 3-4) تؤمّن الوقود والإشعال قبل الملامسة إن اتسع الوقت؛ والقلابات كهربائية، فتُضبط قبل إيقاف المفتاح الرئيسي.',
    },
    quiz: {
      q: { en: 'Why not turn back to the runway?', ar: 'لماذا لا تعود إلى المدرج؟' },
      options: [{ en: 'Altitude and airspeed are seldom sufficient for a 180° gliding turn', ar: 'الارتفاع والسرعة قلّما يكفيان لدوران شراعي 180°' }, { en: 'The engine might restart', ar: 'قد يعود المحرك للعمل' }, { en: 'The flaps would not come down', ar: 'القلابات لن تنزل' }],
      answer: 0, ref: 'POH 3-11',
    },
    demo(deck, c, dt) {
      const s = deck.sim, f = deck.flight, o = f.out, d = (c.demo ??= { t: 0, pilot: createPilot(), flaps: 0, heading: o.headingDeg });
      d.t += dt;
      let target = { kias: 70, headingDeg: d.heading, maxBankDeg: 15 }, brake = 0;
      if (!s.engine.running) {
        if (d.failT == null) d.failT = d.t;
        const since = d.t - d.failT;
        // the nose goes down at once to the attitude of the glide; then the speed is held
        target = since < 0.6 ? { kias: 70, headingDeg: d.heading } : since < 3 ? { pitchDeg: pitchFor(f, -750) - Math.max(0, 65 - o.kias) * 0.6, headingDeg: d.heading, maxBankDeg: 15 }
          : { kias: d.flaps > 0 ? 60 : 65, headingDeg: d.heading, maxBankDeg: 15, minPitchDeg: -14 };
        if (since > 2.5) s.controls.mixture = 0;
        if (since > 3.5) s.controls.fuelSelector = 'OFF';
        if (since > 4.5) s.controls.ignition = 'OFF';
        if (since > 5.5 && o.aglFt > 60 && d.flaps === 0) d.flaps = 20;      // as required: with this height, 20 degrees are down before the round-out
        if (since > 5.5 && (Math.abs(f.flapDeg - d.flaps) < 0.5 || o.aglFt < 30)) { s.controls.masterBat = false; s.controls.masterAlt = false; }
        if (o.aglFt < 35 && !o.onGround) {      // round out and hold off, as in a landing
          const sink = o.kias > 46 ? -Math.min(700, 22 * Math.max(0, o.aglFt - 1)) : -90;
          target = { pitchDeg: Math.min(12, pitchFor(f, sink) + 0.004 * (sink - o.vsFpm)), headingDeg: d.heading, maxBankDeg: 8 };
        }
        if (o.onGround) { target = { elevator: o.wheels >= 3 ? 1 : -0.1, headingDeg: d.heading }; brake = 1; }
      }
      return { ...pilotStep(d.pilot, f, target, dt), flapCommandDeg: d.flaps, brake };
    },
  },
];

/** Begin a lesson: the systems ready for flight with the lesson's setup, the flight at the lesson's start. Returns { sim, deck, trim, ctx }. */
export function startLesson(lesson, conditions = {}, sim = readySystems()) {
  const begun = beginFlight(sim, lesson.flight, conditions);
  for (const [group, values] of Object.entries(lesson.setup || {})) Object.assign(sim[group], values);
  return { sim, deck: begun.deck, trim: begun.trim, ctx: {} };
}

/** One step of a lesson's bookkeeping: its record of the flight, then its steps. Returns the index of the first step not yet done. */
export function tickLesson(lesson, sim, ctx, dt) {
  if (lesson.tick) lesson.tick(sim, ctx, dt);
  return evaluateSteps(lesson, sim, ctx);
}

/**
 * Fly a lesson with its demonstration, without a screen: the scripted pilot flies it to the end (or for `seconds`).
 * Returns { completed, ctx, deck, sim, seconds }.
 */
export function demonstrate(lesson, { seconds = 180, dt = 1 / 60, conditions = {} } = {}) {
  const { sim, deck, trim, ctx } = startLesson(lesson, conditions);
  let t = 0, completed = false;
  while (t < seconds) {
    const c = lesson.demo(deck, ctx, dt);
    stepDeck(deck, { aileron: c.aileron, elevator: c.elevator, rudder: c.rudder, trim, flapCommandDeg: c.flapCommandDeg ?? deck.controls.flapCommandDeg, brake: c.brake ?? 0 }, dt);
    t += dt;
    if (tickLesson(lesson, sim, ctx, dt) >= lesson.steps.length) { completed = true; if (ctx.endAt == null) ctx.endAt = t; if (t - ctx.endAt > 3) break; }
  }
  return { completed, ctx, deck, sim, seconds: t };
}
