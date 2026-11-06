// Guided, POH-referenced training scenarios. Each step's `done(s, ctx)` predicate is
// evaluated live against the simulation; steps latch in order. Steps with `ack`
// need a button press, steps with `choice` need the correct answer.
// Checklist wording follows the 1979 C172N POH; the simulation behind it is illustrative.
import { evaluateMagCheck, POH } from './sim.js';

const warm = { engine: { running: true, rpm: 900, oilTempF: 150, oilPress: 60 }, vac: { suction: 2, gyro: 1 } };
const onAll = { masterBat: true, masterAlt: true, avionics: true, mixture: 1, throttle: 0.12, ignition: 'BOTH', fuelSelector: 'BOTH' };
const cruise = (alt, ias, extra = {}) => ({
  ...warm,
  flight: { onGround: false, altTarget: alt, iasTarget: ias },
  truth: { heading: 90 },
  controls: { ...onAll, throttle: 0.72, navLights: true, beacon: true, ...extra },
});

export const SCENARIOS = [
  {
    id: 'engine_start', focus: 'ENGINE', poh: 'POH 4-7',
    title: { en: 'Engine start (cold)', ar: 'تشغيل المحرك (بارد)' },
    brief: {
      en: 'Cold engine on the ramp. Follow the POH "Starting Engine" checklist. Watch the starter crank the engine in the 3D view, then the pistons fire in 1-3-2-4 order.',
      ar: 'المحرك بارد على الساحة. اتبع قائمة "تشغيل المحرك" في POH، وراقب بادئ الحركة يدير المحرك ثم اشتعال الأسطوانات بالترتيب 1-3-2-4.',
    },
    setup: { controls: { mixture: 0, carbHeat: 1, throttle: 0 } },
    steps: [
      { en: 'Mixture — RICH', ar: 'الخليط — غني (RICH)', done: (s) => s.controls.mixture >= 0.95 },
      { en: 'Carburetor heat — COLD', ar: 'تسخين المكربن — بارد (COLD)', done: (s) => s.controls.carbHeat === 0 },
      { en: 'Master switch — ON (BAT and ALT)', ar: 'المفتاح الرئيسي — تشغيل (BAT وALT)', done: (s) => s.controls.masterBat && s.controls.masterAlt },
      { en: 'Prime — 2 to 6 strokes (cold engine)', ar: 'التحضير (Primer) — من 2 إلى 6 ضخات للمحرك البارد', done: (s, c) => (c.primes || 0) >= 2 && (c.primes || 0) <= 6 && !s.engine.flooded },
      { en: 'Throttle — OPEN 1/8 inch', ar: 'الخانق — مفتوح 1/8 بوصة', done: (s) => s.controls.throttle >= 0.02 && s.controls.throttle <= 0.15 },
      { en: 'Propeller area — CLEAR', ar: 'منطقة المروحة — خالية', ack: true },
      { en: 'Ignition switch — START (release when the engine starts)', ar: 'مفتاح الإشعال — START (حرّره عند دوران المحرك)', done: (s) => s.engine.running && s.controls.ignition === 'BOTH' },
      { en: 'Oil pressure — CHECK (above 25 psi)', ar: 'ضغط الزيت — تحقق (أعلى من 25 psi)', done: (s) => s.engine.running && s.ind.oilP >= POH.oilPressMin },
      { en: 'Avionics power switch — ON', ar: 'مفتاح طاقة الأجهزة الإلكترونية — تشغيل', done: (s) => s.controls.avionics },
    ],
    debrief: {
      en: 'Priming puts fuel directly into the intake ports because a cold carburetor atomises poorly. More than ~6 strokes floods the engine: the POH clearing procedure is mixture idle cut-off, full throttle, crank (POH 4-11). Oil pressure must rise within seconds of the start.',
      ar: 'التحضير يدفع الوقود مباشرة إلى منافذ السحب لأن المكربن البارد لا يذرّي الوقود جيدًا. أكثر من 6 ضخات تقريبًا يُغرق المحرك؛ وإجراء التنظيف في POH: الخليط على القطع، الخانق مفتوح بالكامل، ثم التدوير (POH 4-11). يجب أن يرتفع ضغط الزيت خلال ثوانٍ من التشغيل.',
    },
    quiz: {
      q: { en: 'Weak firing and black smoke during start usually means…', ar: 'الاشتعال الضعيف مع دخان أسود أثناء التشغيل يدل غالبًا على…' },
      options: [{ en: 'Over-priming / flooding', ar: 'الإفراط في التحضير / الإغراق' }, { en: 'A flat battery', ar: 'بطارية فارغة' }, { en: 'Carburetor ice', ar: 'جليد المكربن' }],
      answer: 0, ref: 'POH 4-11',
    },
  },
  {
    id: 'runup', focus: 'IGNITION', poh: 'POH 4-7, 4-13',
    title: { en: 'Before-takeoff run-up & magneto check', ar: 'فحص ما قبل الإقلاع وفحص المغناطيس' },
    brief: {
      en: 'Engine warm, parking brake set. At 1700 RPM check each magneto: the drop must not exceed 125 RPM on either, nor 50 RPM between them. Watch which spark plugs stop firing in the 3D view when you select R or L.',
      ar: 'المحرك دافئ والفرامل مثبتة. عند 1700 RPM افحص كل مغناطيس: يجب ألا يتجاوز الانخفاض 125 RPM لأي منهما ولا الفرق بينهما 50 RPM. راقب في العرض ثلاثي الأبعاد أي شمعات تتوقف عند اختيار R أو L.',
    },
    setup: { ...warm, controls: { ...onAll, fuelSelector: 'LEFT' } },
    steps: [
      { en: 'Fuel selector valve — BOTH', ar: 'صمام اختيار الوقود — BOTH', done: (s) => s.controls.fuelSelector === 'BOTH' },
      { en: 'Mixture — RICH (below 3000 ft)', ar: 'الخليط — غني (تحت 3000 قدم)', done: (s) => s.controls.mixture >= 0.95 },
      { en: 'Throttle — 1700 RPM', ar: 'الخانق — 1700 RPM', done: (s, c) => Math.abs(s.engine.rpm - 1700) <= 40 && (c.bothRef = s.engine.rpm) },
      { en: 'Magnetos — R: note the RPM drop', ar: 'المغناطيس — R: سجّل انخفاض الدورات', done: (s, c) => c.right !== undefined },
      { en: 'Back to BOTH to clear the other plugs', ar: 'عُد إلى BOTH لتنظيف الشمعات الأخرى', done: (s, c) => c.right !== undefined && s.controls.ignition === 'BOTH' },
      { en: 'Magnetos — L: note the RPM drop', ar: 'المغناطيس — L: سجّل انخفاض الدورات', done: (s, c) => c.left !== undefined },
      { en: 'Ignition — BOTH', ar: 'الإشعال — BOTH', done: (s, c) => c.left !== undefined && s.controls.ignition === 'BOTH' && (c.mag = evaluateMagCheck({ both: c.bothRef, right: c.right, left: c.left })) },
      { en: 'Carburetor heat — CHECK for RPM drop, then COLD', ar: 'تسخين المكربن — تحقق من انخفاض الدورات ثم أعده بارداً', done: (s, c) => c.carbChecked && s.controls.carbHeat === 0 },
      { en: 'Suction gage — CHECK (green arc 4.5–5.4 inHg)', ar: 'مقياس الشفط — تحقق (القوس الأخضر 4.5–5.4)', done: (s) => s.ind.suction >= POH.suctionGreen[0] && s.ind.suction <= POH.suctionGreen[1] },
      { en: 'Engine instruments and ammeter — CHECK', ar: 'عدادات المحرك ومقياس التيار — تحقق', ack: true },
      { en: 'Throttle — 1000 RPM or less', ar: 'الخانق — 1000 RPM أو أقل', done: (s) => s.engine.rpm <= 1000 },
    ],
    tick(s, c, dt) {
      const ign = s.controls.ignition;
      c.dwell = c.lastIgn === ign ? (c.dwell || 0) + dt : 0;
      c.lastIgn = ign;
      if (c.bothRef && ign === 'R' && c.dwell > 3) c.right = Math.round(s.engine.rpm);
      if (c.right !== undefined && c.sawBothAfterR && ign === 'L' && c.dwell > 3) c.left = Math.round(s.engine.rpm);
      if (c.right !== undefined && ign === 'BOTH') c.sawBothAfterR = true;
      if (s.controls.carbHeat >= 0.95 && c.left !== undefined) c.carbHot = (c.carbHot || 0) + dt;
      if (c.carbHot > 2) c.carbChecked = true;
    },
    debrief: {
      en: 'Each plug of every cylinder is fired by one side of the dual magneto (right: lower-right + upper-left plugs; left: lower-left + upper-right, POH 7-19). Running on one magneto burns the charge from one plug only, so RPM drops slightly. No drop at all can mean a magneto that is not grounded — treat the propeller as live.',
      ar: 'كل شمعة في كل أسطوانة يشعلها أحد جانبي المغناطيس المزدوج (الأيمن: الشمعات السفلية اليمنى والعلوية اليسرى؛ الأيسر: السفلية اليسرى والعلوية اليمنى، POH 7-19). التشغيل على مغناطيس واحد يعني اشتعالًا من شمعة واحدة فتنخفض الدورات قليلًا. عدم وجود أي انخفاض قد يعني مغناطيسًا غير مؤرَّض — اعتبر المروحة خطرة.',
    },
    quiz: {
      q: { en: 'R drop 70 RPM, L drop 130 RPM. Result?', ar: 'انخفاض R = 70 وانخفاض L = 130 دورة. النتيجة؟' },
      options: [{ en: 'Fail: L exceeds 125 and the differential exceeds 50', ar: 'غير مقبول: L تجاوز 125 والفرق تجاوز 50' }, { en: 'Pass', ar: 'مقبول' }, { en: 'Pass if carb heat is on', ar: 'مقبول إذا كان تسخين المكربن مفعّلًا' }],
      answer: 0, ref: 'POH 4-7',
    },
  },
  {
    id: 'runup_fault', focus: 'IGNITION', poh: 'POH 3-16, 4-13',
    title: { en: 'Run-up: diagnose the ignition', ar: 'فحص المحرك: شخّص عطل الإشعال' },
    brief: {
      en: 'Same run-up, but something is wrong with one magneto. Find it with the R / L check and decide whether the aircraft is airworthy.',
      ar: 'نفس فحص ما قبل الإقلاع، لكن هناك خلل في أحد المغناطيسين. اكتشفه بفحص R / L وقرّر هل الطائرة صالحة للطيران.',
    },
    setup: { ...warm, controls: { ...onAll }, faults: { magneto: { L: 'ok', R: 'weak' } } },
    inherit: 'runup',
    steps: null,
    final: {
      choice: true,
      en: 'Decision — which magneto is faulty?', ar: 'القرار — أي مغناطيس معطوب؟',
      options: [{ en: 'Right (R)', ar: 'الأيمن (R)' }, { en: 'Left (L)', ar: 'الأيسر (L)' }, { en: 'None — go flying', ar: 'لا يوجد — أقلع' }],
      answer: 0,
    },
    debrief: {
      en: 'An excessive drop on R points at the right magneto or the plugs it fires (lower-right and upper-left). The POH suggests leaning to burn off plug fouling and re-checking; if it does not clear, the aircraft is not airworthy (POH 3-16, 4-13).',
      ar: 'الانخفاض الزائد على R يشير إلى المغناطيس الأيمن أو الشمعات التي يشعلها (السفلية اليمنى والعلوية اليسرى). يقترح POH إفقار الخليط لحرق ترسبات الشمعات ثم إعادة الفحص؛ إذا لم يزل الخلل فالطائرة غير صالحة للطيران (POH 3-16، 4-13).',
    },
  },
  {
    id: 'leaning', focus: 'INDUCTION', poh: 'POH 4-16',
    title: { en: 'Cruise leaning by RPM', ar: 'إفقار الخليط في الطيران المستقيم' },
    brief: {
      en: 'Level at 6500 ft with full rich mixture. Lean slowly: RPM rises to a peak, then falls. The POH recommends leaning until RPM peaks and drops 25–50 RPM.',
      ar: 'طيران مستوٍ على 6500 قدم والخليط غني بالكامل. أفقر الخليط ببطء: ترتفع الدورات إلى قمة ثم تنخفض. يوصي POH بالإفقار حتى تبلغ الدورات القمة ثم تنخفض 25–50 دورة.',
    },
    setup: cruise(6500, 105, { throttle: 0.85 }),
    steps: [
      { en: 'Note RPM at full rich', ar: 'سجّل الدورات عند الخليط الغني', done: (s, c) => c.rich !== undefined },
      { en: 'Lean slowly until RPM peaks', ar: 'أفقر الخليط ببطء حتى تبلغ الدورات القمة', done: (s, c) => c.peak > c.rich + 10 && s.engine.rpm < c.peak - 8 },
      { en: 'Continue until RPM is 25–50 below peak', ar: 'تابع حتى تنخفض الدورات 25–50 عن القمة', done: (s, c) => c.peak - s.engine.rpm >= 25 && c.peak - s.engine.rpm <= 50 && s.engine.running },
    ],
    tick(s, c, dt) {
      c.t = (c.t || 0) + dt;
      if (c.rich === undefined && c.t > 4) { c.rich = s.engine.rpm; c.peak = s.engine.rpm; }
      if (c.rich !== undefined && s.engine.rpm > (c.peak || 0)) c.peak = s.engine.rpm;
    },
    debrief: {
      en: 'At altitude the air is less dense but the carburetor meters fuel by pressure drop, so a full-rich mixture gets richer as you climb. Leaning restores the best fuel/air ratio. Above 75% power do not lean beyond peak RPM (POH 4-16).',
      ar: 'في الارتفاع يقل كثافة الهواء بينما يقيس المكربن الوقود بفرق الضغط، فيصبح الخليط الغني أغنى مع الصعود. الإفقار يعيد النسبة المثلى بين الوقود والهواء. فوق 75% من القدرة لا تفقر بعد قمة الدورات (POH 4-16).',
    },
  },
  {
    id: 'carb_ice', focus: 'INDUCTION', poh: 'POH 3-16, 4-16',
    title: { en: 'Carburetor icing', ar: 'تكوّن الجليد في المكربن' },
    brief: {
      en: 'Cruise at 3000 ft in humid air. Fuel evaporation and the venturi cool the carburetor below freezing. Watch for an unexplained, gradual RPM loss.',
      ar: 'طيران على 3000 قدم في هواء رطب. تبخر الوقود والفنتوري يبردان المكربن تحت درجة التجمد. راقب أي انخفاض تدريجي غير مبرر في الدورات.',
    },
    setup: { ...cruise(3000, 95, { throttle: 0.6 }), faults: { carbIce: true }, engine: { ...warm.engine, ice: 0.3 } },
    steps: [
      { en: 'Recognise the unexplained RPM loss', ar: 'لاحظ انخفاض الدورات غير المبرر', done: (s) => s.engine.ice >= 0.42 },
      { en: 'Throttle — FULL', ar: 'الخانق — مفتوح بالكامل', done: (s) => s.controls.throttle >= 0.95 },
      { en: 'Carburetor heat — FULL OUT', ar: 'تسخين المكربن — مسحوب بالكامل', done: (s) => s.controls.carbHeat >= 0.95 },
      { en: 'Wait until the engine runs smoothly', ar: 'انتظر حتى يعمل المحرك بسلاسة', done: (s) => s.engine.ice < 0.05 },
      { en: 'Carburetor heat — OFF, readjust throttle', ar: 'تسخين المكربن — إيقاف، ثم أعد ضبط الخانق', done: (s) => s.controls.carbHeat === 0 && s.controls.throttle < 0.95 },
    ],
    debrief: {
      en: 'Applying heat first makes RPM drop further (hot, less dense air and melt water) before it recovers as the ice clears. Use the minimum heat that prevents ice, and lean for smoothness if heat stays on (POH 3-16).',
      ar: 'عند تطبيق التسخين تنخفض الدورات أولًا (هواء ساخن أقل كثافة وماء ذائب) ثم ترتفع عند زوال الجليد. استخدم أقل تسخين يمنع الجليد، وأفقر الخليط للسلاسة إذا بقي التسخين مفعّلًا (POH 3-16).',
    },
    quiz: {
      q: { en: 'Why does RPM drop when carb heat is first applied?', ar: 'لماذا تنخفض الدورات عند تفعيل تسخين المكربن أولًا؟' },
      options: [{ en: 'Hot air is less dense and melting ice is ingested', ar: 'الهواء الساخن أقل كثافة والجليد الذائب يدخل المحرك' }, { en: 'The magnetos switch off', ar: 'يتوقف المغناطيس' }, { en: 'The fuel selector closes', ar: 'يُغلق صمام الوقود' }],
      answer: 0, ref: 'POH 7-19',
    },
  },
  {
    id: 'static_block', focus: 'PITOT_STATIC', poh: 'POH 3-8, 5-9',
    title: { en: 'Static source blockage', ar: 'انسداد مصدر الضغط الساكن' },
    brief: {
      en: 'Climbing from 3000 to 4500 ft. Water froze in the static line. Cross-check the altimeter, VSI and airspeed against power and attitude.',
      ar: 'صعود من 3000 إلى 4500 قدم. تجمّد ماء في خط الضغط الساكن. قارن مقياس الارتفاع ومؤشر الصعود والسرعة مع القدرة والوضعية.',
    },
    setup: { ...cruise(3000, 85, { throttle: 0.9 }), faults: { staticBlocked: true }, flight: { onGround: false, altTarget: 4500, iasTarget: 80 }, truth: { alt: 3000, ias: 85, heading: 90 } },
    steps: [
      { en: 'Cross-check: altimeter frozen and VSI at zero while climbing', ar: 'المقارنة: مقياس الارتفاع ثابت ومؤشر الصعود صفر رغم الصعود', done: (s) => s.truth.alt - s.ind.alt > 250 },
      { en: 'Alternate static source valve — PULL ON', ar: 'صمام المصدر الساكن البديل — اسحبه (ON)', done: (s) => s.controls.altStatic },
      { en: 'Airspeed — consult the calibration table (Section 5)', ar: 'السرعة — راجع جدول المعايرة (القسم 5)', ack: true },
    ],
    debrief: {
      en: 'With the static port blocked the altimeter freezes, the VSI reads zero and the ASI under-reads in a climb (over-reads in a descent). The alternate source uses cabin pressure, slightly lower than outside: with vents and windows closed the ASI reads about 1–2 kt high (POH Fig 5-1, p.5-9).',
      ar: 'عند انسداد منفذ الضغط الساكن يثبت مقياس الارتفاع ويقرأ مؤشر الصعود صفرًا وتقل قراءة السرعة في الصعود (وتزيد في الهبوط). المصدر البديل يستخدم ضغط المقصورة الأقل قليلًا من الخارج؛ مع إغلاق الفتحات والنوافذ تزيد قراءة السرعة 1–2 عقدة تقريبًا (POH الشكل 5-1، ص 5-9).',
    },
  },
  {
    id: 'pitot_ice', focus: 'PITOT_STATIC', poh: 'POH 7-31',
    title: { en: 'Iced pitot tube', ar: 'تجمّد أنبوب البيتو' },
    brief: {
      en: 'Level at 4000 ft, constant power, in visible moisture near freezing. The pitot inlet ices over while its drain hole stays open.',
      ar: 'طيران مستوٍ على 4000 قدم بقدرة ثابتة في رطوبة قرب التجمد. يتجمد مدخل البيتو بينما تبقى فتحة التصريف مفتوحة.',
    },
    setup: { ...cruise(4000, 100), faults: { pitot: 'ram' } },
    steps: [
      { en: 'Notice the ASI falling with constant power and altitude', ar: 'لاحظ انخفاض مؤشر السرعة رغم ثبات القدرة والارتفاع', done: (s) => s.ind.ias < 70 },
      { en: 'Pitot heat — ON (if installed)', ar: 'تسخين البيتو — تشغيل (إن وُجد)', done: (s) => s.controls.pitotHeat },
      { en: 'Airspeed indication restored', ar: 'عادت قراءة السرعة', done: (s) => Math.abs(s.ind.ias - s.truth.ias) < 4 },
    ],
    tick(s, c, dt) {
      if (s.controls.pitotHeat && s.elec.busVolts > 20) c.heat = (c.heat || 0) + dt;
      if (c.heat > 12) s.faults.pitot = 'none';
    },
    debrief: {
      en: 'Ram inlet blocked + drain open: pressure leaks out and the ASI drops toward zero. Ram inlet and drain both blocked: the trapped pressure makes the ASI behave like an altimeter (higher in a climb). Pitot heat is an electrical load — watch the ammeter.',
      ar: 'انسداد المدخل مع بقاء فتحة التصريف: يتسرب الضغط وتنخفض السرعة نحو الصفر. انسداد المدخل والتصريف معًا: يحبس الضغط فيعمل مؤشر السرعة كمقياس ارتفاع (يزيد مع الصعود). تسخين البيتو حمل كهربائي — راقب مقياس التيار.',
    },
  },
  {
    id: 'low_voltage', focus: 'ELECTRICAL', poh: 'POH 3-9, 7-26',
    title: { en: 'Low-voltage light in flight', ar: 'إضاءة تحذير الجهد المنخفض أثناء الطيران' },
    brief: {
      en: 'Cruise with avionics on. The alternator control unit senses over-voltage and takes the alternator off line. Follow the POH checklist.',
      ar: 'طيران مع تشغيل الأجهزة الإلكترونية. وحدة التحكم في المولد تكتشف جهدًا زائدًا وتفصل المولد. اتبع قائمة POH.',
    },
    setup: { ...cruise(4500, 105), faults: { alternator: 'overvoltage' } },
    steps: [
      { en: 'Low-voltage light ON, ammeter shows discharge', ar: 'ضوء الجهد المنخفض مضاء ومقياس التيار يُظهر تفريغًا', done: (s) => s.elec.lowVoltage && s.ind.ammeter < 0 },
      { en: 'Avionics power switch — OFF', ar: 'مفتاح طاقة الأجهزة الإلكترونية — إيقاف', done: (s) => !s.controls.avionics },
      { en: 'Master switch — OFF (both sides)', ar: 'المفتاح الرئيسي — إيقاف (الجانبان)', done: (s) => !s.controls.masterBat && !s.controls.masterAlt },
      { en: 'Master switch — ON', ar: 'المفتاح الرئيسي — تشغيل', done: (s) => s.controls.masterBat && s.controls.masterAlt },
      { en: 'Low-voltage light — CHECK (it illuminates again)', ar: 'ضوء الجهد المنخفض — تحقق (أضاء مجددًا)', done: (s) => s.elec.acuTripped && s.elec.lowVoltage },
      { en: 'Alternator — OFF', ar: 'المولد — إيقاف', done: (s) => !s.controls.masterAlt && s.controls.masterBat },
      { en: 'Non-essential radio and electrical equipment — OFF', ar: 'إطفاء الأجهزة اللاسلكية والكهربائية غير الضرورية', done: (s) => !s.controls.landingLight && !s.controls.beacon && !s.controls.pitotHeat && !s.controls.avionics },
      { en: 'Flight — TERMINATE as soon as practical', ar: 'الرحلة — أنهِها في أقرب وقت عملي', ack: true },
    ],
    debrief: {
      en: 'Recycling the master resets the alternator control unit. If the light returns there is a real malfunction: the battery now carries the whole load, so shed load and land. A low-voltage light at low RPM taxi with a load is normal and goes out at higher RPM (POH 7-26).',
      ar: 'إعادة تشغيل المفتاح الرئيسي تعيد ضبط وحدة التحكم. إذا عاد الضوء فهناك عطل حقيقي: البطارية تحمل كل الأحمال الآن، فخفّف الأحمال واهبط. إضاءة الضوء عند دورات منخفضة أثناء التدرج مع حمل كهربائي أمر طبيعي وتنطفئ عند رفع الدورات (POH 7-26).',
    },
  },
  {
    id: 'vacuum_fail', focus: 'VACUUM', poh: 'POH 7-34',
    title: { en: 'Vacuum system failure', ar: 'تعطل نظام التفريغ' },
    brief: {
      en: 'Cruise at 4500 ft. The engine-driven vacuum pump will fail. The attitude and heading indicators keep spinning down and slowly become wrong.',
      ar: 'طيران على 4500 قدم. ستتعطل مضخة التفريغ التي يديرها المحرك، فتتباطأ جيروسكوبات مؤشري الوضعية والاتجاه وتصبح قراءاتهما خاطئة تدريجيًا.',
    },
    setup: cruise(4500, 100),
    steps: [
      { en: 'Suction gage — below the green arc', ar: 'مقياس الشفط — تحت القوس الأخضر', done: (s) => s.ind.suction < POH.suctionGreen[0] && s.faults.vacuum },
      { en: 'Treat the attitude and heading indicators as unreliable; cross-check TC, ASI, ALT, VSI', ar: 'اعتبر مؤشري الوضعية والاتجاه غير موثوقين؛ قارن مع منسق الانعطاف والسرعة والارتفاع ومؤشر الصعود', ack: true },
      {
        choice: true, en: 'The turn coordinator now shows a turn. Which way?', ar: 'منسق الانعطاف يُظهر انعطافًا الآن. في أي اتجاه؟',
        options: [{ en: 'Right', ar: 'يمين' }, { en: 'Left', ar: 'يسار' }, { en: 'No turn — trust the attitude indicator', ar: 'لا يوجد انعطاف — صدّق مؤشر الوضعية' }], answer: 0,
      },
    ],
    tick(s, c, dt) {
      c.t = (c.t || 0) + dt;
      if (c.t > 6) s.faults.vacuum = true;
      if (c.t > 60) s.flight.bank = 15;
    },
    debrief: {
      en: 'Below 4.5 inHg the gyros are not considered reliable (POH 7-34). The electric turn coordinator and the pitot-static instruments are independent of vacuum — use them for partial-panel flying.',
      ar: 'تحت 4.5 بوصة زئبق لا تُعدّ الجيروسكوبات موثوقة (POH 7-34). منسق الانعطاف الكهربائي وأجهزة البيتو-الساكن مستقلة عن التفريغ — استخدمها للطيران بلوحة جزئية.',
    },
  },
  {
    id: 'engine_failure', focus: 'FUEL', poh: 'POH 3-4',
    title: { en: 'Engine failure in flight (fuel)', ar: 'توقف المحرك أثناء الطيران (الوقود)' },
    brief: {
      en: 'Cruise at 4500 ft feeding from the LEFT tank only. Watch the fuel gauges. When the engine stops, fly 65 KIAS and run the POH checklist.',
      ar: 'طيران على 4500 قدم مع التغذية من الخزان الأيسر فقط. راقب عدادات الوقود. عند توقف المحرك حافظ على 65 عقدة ونفّذ قائمة POH.',
    },
    setup: { ...cruise(4500, 100, { fuelSelector: 'LEFT' }), fuel: { left: 1.58, right: 15 } },
    steps: [
      { en: 'Engine stops — recognise it', ar: 'توقف المحرك — تعرّف عليه', done: (s) => !s.engine.running },
      { en: 'Airspeed — 65 KIAS', ar: 'السرعة — 65 عقدة', done: (s) => Math.abs(s.flight.iasTarget - 65) <= 3 },
      { en: 'Carburetor heat — ON', ar: 'تسخين المكربن — تشغيل', done: (s) => s.controls.carbHeat >= 0.95 },
      { en: 'Fuel selector valve — BOTH', ar: 'صمام اختيار الوقود — BOTH', done: (s) => s.controls.fuelSelector === 'BOTH' },
      { en: 'Mixture — RICH', ar: 'الخليط — غني', done: (s) => s.controls.mixture >= 0.95 },
      { en: 'Ignition switch — BOTH (or START if the propeller has stopped)', ar: 'مفتاح الإشعال — BOTH (أو START إذا توقفت المروحة)', done: (s) => s.controls.ignition === 'BOTH' || s.controls.ignition === 'START' },
      { en: 'Primer — IN and LOCKED', ar: 'المضخة اليدوية (Primer) — مدفوعة ومقفلة', ack: true },
      { en: 'Engine restarts', ar: 'عاد المحرك للعمل', done: (s) => s.engine.running },
    ],
    debrief: {
      en: 'The left tank still holds its 1.5 gal of unusable fuel — the gauge reads E. 65 KIAS is the POH best-glide speed and also keeps the propeller windmilling for a restart. Selecting BOTH restored gravity feed from the right tank.',
      ar: 'الخزان الأيسر ما زال يحتوي على 1.5 جالون غير قابلة للاستخدام — والعداد يقرأ E. سرعة 65 عقدة هي سرعة الانزلاق الأفضل في POH، وتُبقي المروحة تدور بفعل الهواء لإعادة التشغيل. اختيار BOTH أعاد التغذية بالجاذبية من الخزان الأيمن.',
    },
  },
];

const byId = Object.fromEntries(SCENARIOS.map((x) => [x.id, x]));
for (const sc of SCENARIOS) {
  if (sc.inherit && !sc.steps) {
    const base = byId[sc.inherit];
    sc.steps = [...base.steps, sc.final];
    sc.tick = base.tick;
  }
}

/** Advance step completion. Returns the index of the first incomplete step. */
export function evaluateSteps(sc, s, ctx) {
  ctx.done = ctx.done || [];
  for (let i = 0; i < sc.steps.length; i++) {
    if (ctx.done[i]) continue;
    const st = sc.steps[i];
    if (st.ack || st.choice) return i;            // waits for the user
    if (st.done(s, ctx)) { ctx.done[i] = true; continue; }
    return i;
  }
  return sc.steps.length;
}
