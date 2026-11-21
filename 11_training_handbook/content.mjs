// FlyGACA C172N training handbook: the words, in English and Arabic, written for FlyGACA.
//
// The numbers come from the twin's records of the Pilot's Operating Handbook. Each block names the records it
// rests on in `refs`, and the build prints their POH pages beside it. A test fails when a number in a block's
// text is not in one of those records, so a value cannot be typed in here without its source:
//   poh:<key>   08_realistic_digital_twin/data/poh_references.json
//   y79:<key>   04b_poh_reference/poh_1979_reference_data.json
//   tab:<NAME>  shared/js/poh_tables.js (the tables are drawn from it directly)
//   inst:<ID>   08_realistic_digital_twin/data/instruments.json
//   src         the edition of the handbook the records were read from

const p = (en, ar, refs = []) => ({ type: 'p', en, ar, refs });
const note = (kind, en, ar, refs = []) => ({ type: 'note', kind, en, ar, refs });
const facts = (rows) => ({ type: 'facts', rows });
const row = (label, en, ar, refs) => ({ label, en, ar, refs });
const steps = (title, items, refs, after = null) => ({ type: 'steps', title, items, refs, after });
const list = (items, refs) => ({ type: 'list', items, refs });
const figure = (id, caption) => ({ type: 'figure', id, caption });
const table = (name, caption) => ({ type: 'table', name, caption });
const L = (en, ar) => ({ en, ar });

export const TITLE = L('C172N Training Handbook', 'دليل التدريب لطائرة سيسنا C172N');
export const SUBTITLE = L(
  "FlyGACA's own reference for the Cessna 172N of its digital twin, with the page of the Pilot's Operating Handbook behind every value",
  'مرجع FlyGACA الخاص لطائرة سيسنا 172N في توأمها الرقمي، وبجانب كل قيمة صفحتها في دليل تشغيل الطيار (POH)');

export const NOTICE = {
  title: L('Read this first', 'اقرأ هذا أولًا'),
  en: [
    'This is not a Pilot\'s Operating Handbook or an Airplane Flight Manual. No authority and no manufacturer has approved it. It is a study reference written by FlyGACA for the aeroplane of its digital twin.',
    'Its values were read from the Cessna Model 172N Pilot\'s Operating Handbook, 1979 model, and each one shows the page it came from. A particular aircraft can differ from them: its equipment, its weight and balance record and the revisions of its own handbook decide.',
    'Never fly from it. In the aeroplane, use the approved handbook and checklist of the aeroplane you fly.',
  ],
  ar: [
    'هذا ليس دليل تشغيل الطيار (POH) ولا دليل طيران الطائرة (AFM)، ولم تعتمده أي جهة تنظيمية ولا أي جهة مصنّعة. إنه مرجع دراسي كتبته FlyGACA للطائرة التي يمثلها توأمها الرقمي.',
    'قُرئت قيمه من دليل تشغيل الطيار لطائرة Cessna Model 172N موديل 1979، وتظهر بجانب كل قيمة الصفحة التي أُخذت منها. وقد تختلف طائرة بعينها عنها، فالحكم لتجهيزاتها ولسجل وزنها واتزانها ولمراجعات دليلها هي.',
    'لا تطِر به أبدًا. في الطائرة استخدم الدليل المعتمد وقائمة التحقق للطائرة التي تطير بها.',
  ],
  refs: ['src'],
};

// The approved notice, word for word (FlyGACA/UFUQ identity/brand.json), as the site's footer prints it, and the two
// other names a reader of a handbook about this aeroplane might assume FlyGACA speaks for.
export const BRAND_NOTICE = L(
  'Not affiliated with GACA. Always verify against the latest official GACA publication.',
  'غير تابعة لـ GACA. تحقّق دائمًا من أحدث منشور رسمي صادر عن GACA.');
export const MAKER_NOTICE = L(
  'FlyGACA is not affiliated with Cessna or Textron Aviation either. Study material: not a training device and not for flight.',
  'وFlyGACA غير تابعة كذلك لشركة Cessna ولا لشركة Textron Aviation. مادة دراسية: ليست جهاز تدريب وليست للطيران الفعلي.');

export const SECTIONS = [
  {
    id: 'general', title: L('General', 'عام'),
    blocks: [
      p('The aeroplane described here is the one FlyGACA\'s digital twin models: a Cessna 172N of the 1979 model year in its factory-standard form. The configuration of a particular serial number has not been checked against it.',
        'الطائرة الموصوفة هنا هي التي يمثلها التوأم الرقمي لـ FlyGACA: طائرة Cessna 172N من موديل 1979 في هيئتها القياسية كما خرجت من المصنع، ولم تُطابَق عليها هيئة طائرة بعينها برقمها التسلسلي.',
        ['src']),
      facts([
        row(L('Engine', 'المحرك'),
          'Lycoming O-320-H2AD: four cylinders, horizontally opposed, air cooled, normally aspirated, carburettor equipped, direct drive, 320 cu in',
          'Lycoming O-320-H2AD: أربع أسطوانات متقابلة أفقيًا، مبرَّد بالهواء، ذو سحب طبيعي، مزوَّد بمكربن، يدير المروحة مباشرة، سعته 320 cu in',
          ['poh:engine.model', 'poh:engine.type']),
        row(L('Rated power', 'القدرة المقدَّرة'), '160 BHP at 2700 RPM', '160 BHP عند 2700 RPM', ['poh:engine.rating']),
        row(L('Propeller', 'المروحة'),
          'McCauley 1C160/DTM7557, fixed pitch, two blades; diameter 75 in maximum, 74 in minimum',
          'McCauley 1C160/DTM7557، ثابتة الخطوة، بشفرتين؛ قطرها 75 in حدًّا أقصى و74 in حدًّا أدنى',
          ['poh:propeller']),
        row(L('Fuel grade', 'درجة الوقود'), '100LL (blue) or 100 (green)', '100LL (أزرق) أو 100 (أخضر)', ['poh:fuel.grade']),
        row(L('Fuel, standard tanks', 'الوقود، الخزانات القياسية'),
          '21.5 gal each; 43 gal in all, of which 40 gal usable', '21.5 gal في كل خزان؛ 43 gal في المجموع، منها 40 gal قابلة للاستخدام',
          ['poh:fuel.standard_tanks']),
        row(L('Fuel, long-range tanks', 'الوقود، خزانات المدى الطويل'),
          '27 gal each; 54 gal in all, of which 50 gal usable', '27 gal في كل خزان؛ 54 gal في المجموع، منها 50 gal قابلة للاستخدام',
          ['poh:fuel.long_range_tanks']),
        row(L('Oil', 'الزيت'), '6 qt in the sump; 7 qt in all with the oil filter', '6 qt في حوض الزيت؛ و7 qt في المجموع مع مرشّح الزيت', ['poh:oil.sump_qt']),
        row(L('Maximum takeoff weight', 'الوزن الأقصى للإقلاع'), '2300 lb, normal category', '2300 lb، في الفئة العادية', ['y79:weight.max_takeoff_lb']),
        row(L('Dimensions', 'الأبعاد'),
          'wing span 36 ft (with strobe lights); length 26 ft 11 in; height 8 ft 9½ in maximum; horizontal tail span 11 ft 4 in; main wheel track 8 ft 4½ in; wheel base 65 in; propeller ground clearance 11¾ in; wing area 174 sq ft',
          'امتداد الجناح 36 ft (مع أضواء الوميض)؛ الطول 26 ft 11 in؛ الارتفاع 8 ft 9½ in حدًّا أقصى؛ امتداد الذيل الأفقي 11 ft 4 in؛ المسافة بين العجلتين الرئيسيتين 8 ft 4½ in؛ قاعدة العجلات 65 in؛ خلوص المروحة عن الأرض 11¾ in؛ مساحة الجناح 174 sq ft',
          ['poh:geometry.three_view']),
        row(L('Turning radius', 'نصف قطر الدوران'),
          '27 ft 5½ in at least, from the pivot point to the outboard wing tip',
          '27 ft 5½ in على الأقل، من نقطة الارتكاز إلى طرف الجناح الخارجي',
          ['poh:geometry.three_view']),
      ]),
      figure('aircraft-exterior', L('The five major components of the aircraft, drawn from the three-dimensional twin.', 'المكونات الرئيسية الخمسة للطائرة، مرسومة من التوأم ثلاثي الأبعاد.')),
    ],
  },
  {
    id: 'limitations', title: L('Limitations', 'الحدود'),
    blocks: [
      p('The limits below are those the 1979 handbook gives. Speeds are indicated airspeeds in knots (KIAS).',
        'الحدود الآتية هي التي يعطيها دليل موديل 1979. السرعات سرعات مبيَّنة بالعقدة (KIAS).', ['src']),
      facts([
        row(L('Never exceed speed, VNE', 'السرعة التي لا تُتجاوز، VNE'), '160 KIAS', '160 KIAS', ['poh:airspeed.limits_KIAS']),
        row(L('Maximum structural cruising speed, VNO', 'السرعة القصوى للطيران الهيكلي، VNO'), '128 KIAS', '128 KIAS', ['poh:airspeed.limits_KIAS']),
        row(L('Manoeuvring speed, VA', 'سرعة المناورة، VA'), '97 KIAS at 2300 lb', '97 KIAS عند 2300 lb', ['poh:airspeed.limits_KIAS']),
        row(L('Maximum flap extended speed, VFE', 'السرعة القصوى مع القلابات ممدودة، VFE'),
          '110 KIAS with flaps 10°; 85 KIAS with flaps 10° to 40°', '110 KIAS مع القلابات 10°؛ و85 KIAS مع القلابات من 10° إلى 40°',
          ['poh:airspeed.limits_KIAS']),
      ]),
      table('asi', L('Airspeed indicator markings', 'علامات مؤشر السرعة الجوية')),
      figure('asi-markings', L('The airspeed indicator, its arcs and red line drawn from the same records.', 'مؤشر السرعة الجوية، وأقواسه وخطه الأحمر مرسومة من السجلات نفسها.')),
      table('engine', L('Engine instrument markings', 'علامات عدادات المحرك')),
      facts([
        row(L('Maximum engine speed', 'أقصى سرعة للمحرك'), '2700 RPM', '2700 RPM', ['poh:engine.max_rpm']),
        row(L('Static RPM at full throttle', 'الدورات الثابتة بالخانق الكامل'),
          '2280 to 2400 RPM, carburettor heat off, mixture full rich', 'من 2280 إلى 2400 RPM، وتسخين المكربن مغلق والخليط غني كاملًا',
          ['poh:engine.static_rpm_full_throttle']),
        row(L('Unusable fuel', 'الوقود غير القابل للاستخدام'),
          'E red line on the gauges; 1.5 gal unusable in each standard tank, 2.0 gal in each long-range tank',
          'خط أحمر عند E على المقياسين؛ و1.5 gal غير قابلة للاستخدام في كل خزان قياسي، و2.0 gal في كل خزان مدى طويل',
          ['poh:fuel.unusable_marking']),
        row(L('Maximum takeoff weight', 'الوزن الأقصى للإقلاع'), '2300 lb, normal category', '2300 lb، في الفئة العادية', ['y79:weight.max_takeoff_lb']),
      ]),
    ],
  },
  {
    id: 'emergency', title: L('Emergency procedures', 'إجراءات الطوارئ'),
    blocks: [
      note('warning',
        'These are the actions the handbook\'s emergency checklists give, in FlyGACA\'s words and for study. The handbook has more emergency procedures than the twin records; read all of them, and fly with the approved checklist of your aeroplane.',
        'هذه هي الإجراءات التي تعطيها قوائم الطوارئ في دليل الطائرة، بصياغة FlyGACA ولغرض الدراسة. وفي الدليل إجراءات طوارئ أكثر مما سجّله التوأم، فاقرأها كلها، وطِر بقائمة التحقق المعتمدة لطائرتك.'),
      steps(L('Engine failure in flight: restart', 'توقف المحرك في الجو: إعادة التشغيل'), [
        L('Airspeed 65 KIAS.', 'السرعة 65 KIAS.'),
        L('Carburettor heat ON.', 'تسخين المكربن مفتوح (ON).'),
        L('Fuel selector BOTH.', 'صمام اختيار الوقود على BOTH.'),
        L('Mixture RICH.', 'الخليط غني (RICH).'),
        L('Ignition switch BOTH, or START if the propeller has stopped.', 'مفتاح الإشعال على BOTH، أو على START إن توقفت المروحة.'),
        L('Primer IN and LOCKED.', 'مضخة التحضير (primer) مدفوعة ومقفلة (IN and LOCKED).'),
      ], ['poh:checklist.engine_failure_in_flight']),
      p('The best glide, flaps up and the propeller windmilling, is at 65 KIAS, with a glide ratio of 9.1.',
        'أفضل انزلاق دون قدرة، والقلابات مرفوعة والمروحة تدور بفعل الهواء، عند 65 KIAS، بنسبة انزلاق 9.1.', ['tab:GLIDE']),
      steps(L('LOW VOLTAGE light in flight', 'ضوء LOW VOLTAGE في الجو'), [
        L('Avionics OFF.', 'أجهزة الإلكترونيات الجوية مغلقة (OFF).'),
        L('Master switch OFF, both halves.', 'المفتاح الرئيسي مغلق (OFF) بنصفيه.'),
        L('Master switch ON.', 'المفتاح الرئيسي مفتوح (ON).'),
        L('Check that the light is OFF.', 'تحقق من أن الضوء انطفأ.'),
        L('Avionics ON.', 'أجهزة الإلكترونيات الجوية مفتوحة (ON).'),
      ], ['poh:checklist.low_voltage_in_flight'],
      L('If the light comes on again: alternator OFF, non-essential electrical equipment OFF, and end the flight.',
        'وإن عاد الضوء: المولّد المتناوب مغلق (OFF)، والأجهزة الكهربائية غير الضرورية مغلقة، وأنهِ الرحلة.')),
      p('The light can also come on at low RPM with an electrical load. On an over-voltage the alternator control unit removes the alternator field; recycling the master switch resets it.',
        'وقد يضيء الضوء أيضًا عند دورات منخفضة مع حمل كهربائي. وعند ارتفاع الجهد يقطع جهاز التحكم بالمولّد مجاله، ويُعاد ضبطه بإطفاء المفتاح الرئيسي وتشغيله من جديد.',
        ['poh:electrical.low_voltage']),
      steps(L('Static source blocked', 'انسداد مصدر الضغط الساكن'), [
        L('Alternate static source valve: PULL ON.', 'صمام مصدر الضغط الساكن البديل: اسحبه (PULL ON).'),
        L('Correct the airspeed with the calibration table for the alternate source.', 'صحّح السرعة بجدول المعايرة الخاص بالمصدر البديل.'),
      ], ['poh:checklist.static_blockage']),
      p('With flaps up and the heater, vents and windows closed, the rows of that table the twin records pair 40 with 39, 50 with 51, 100 with 101 and 140 with 141 KIAS; the full table is in the aircraft\'s handbook.',
        'والقلابات مرفوعة والمدفأة وفتحات التهوية والنوافذ مغلقة، تقابل صفوف ذلك الجدول التي سجّلها التوأم 40 بـ39، و50 بـ51، و100 بـ101، و140 بـ141 KIAS؛ والجدول كاملًا في دليل الطائرة.',
        ['poh:alternate_static.calibration']),
      steps(L('Carburettor ice', 'جليد المكربن'), [
        L('The sign: a gradual loss of RPM.', 'العلامة: انخفاض تدريجي في الدورات.'),
        L('Full throttle and full carburettor heat until the engine runs smoothly.', 'الخانق كاملًا وتسخين المكربن كاملًا حتى يعمل المحرك بانتظام.'),
        L('Then remove the heat.', 'ثم أزل التسخين.'),
      ], ['poh:carb_icing']),
    ],
  },
  {
    id: 'normal', title: L('Normal procedures', 'الإجراءات العادية'),
    blocks: [
      table('speeds', L('Speeds for normal operation, 2300 lb', 'سرعات التشغيل العادي، 2300 lb')),
      list([
        L('Control wheel lock: remove.', 'قفل عجلة التحكم: أزِله.'),
        L('Rudder gust lock: remove.', 'قفل دفة الاتجاه من الرياح: أزِله.'),
        L('Tail, wing and nose tie-downs: disconnect.', 'أربطة الذيل والجناحين والمقدمة: فُكّها.'),
        L('Pitot tube cover: remove.', 'غطاء أنبوب البيتوت: أزِله.'),
        L('Fuel: take a sample in the sampler cup at the quick-drain valve of each tank sump, and pull the strainer drain knob for about four seconds.', 'الوقود: خذ عيّنة في كوب العيّنات من صمام التصريف السريع في حوض كل خزان، واسحب مقبض تصريف المصفاة نحو أربع ثوانٍ.'),
        L('Oil: not less than four quarts.', 'الزيت: لا يقل عن أربعة كوارتات.'),
      ], ['poh:preflight.ground_equipment']),
      steps(L('Starting the engine', 'تشغيل المحرك'), [
        L('Mixture RICH.', 'الخليط غني (RICH).'),
        L('Carburettor heat COLD.', 'تسخين المكربن بارد (COLD).'),
        L('Master switch ON.', 'المفتاح الرئيسي مفتوح (ON).'),
        L('Prime 2 to 6 strokes; none if the engine is warm.', 'حضّر بمضخة التحضير من 2 إلى 6 ضربات، ولا شيء إن كان المحرك دافئًا.'),
        L('Throttle open 1/8 in.', 'الخانق مفتوح 1/8 in.'),
        L('Ignition switch START.', 'مفتاح الإشعال على START.'),
        L('Oil pressure: check.', 'ضغط الزيت: تحقق منه.'),
      ], ['poh:starting_engine']),
      p('If the engine is flooded: mixture full lean, throttle full open, and crank; then repeat the start without priming.',
        'إن غمر الوقود المحرك: الخليط فقير كاملًا، والخانق مفتوح كاملًا، ثم أدِر المحرك بالمشغّل؛ وبعدها أعد التشغيل دون تحضير.',
        ['poh:flooded_engine']),
      p('Magneto check in the run-up: at 1700 RPM, the drop on either magneto should not exceed 125 RPM, nor the difference between them 50 RPM.',
        'فحص الماغنيتو في فحص المحرك قبل الإقلاع: عند 1700 RPM لا ينبغي أن يتجاوز الانخفاض على أي ماغنيتو 125 RPM، ولا الفرق بينهما 50 RPM.',
        ['poh:runup.magneto_check']),
      p('Leaning: lean until the RPM peaks and then drops by 25 to 50 RPM. Above 75% power, do not lean beyond peak RPM.',
        'الإفقار: أفقِر الخليط حتى تبلغ الدورات ذروتها ثم تنخفض بمقدار 25 إلى 50 RPM. وفوق 75% من القدرة لا تُفقِر إلى ما بعد ذروة الدورات.',
        ['poh:leaning']),
    ],
  },
  {
    id: 'performance', title: L('Performance', 'الأداء'),
    blocks: [
      note('note',
        'The twin records selected rows of the handbook\'s performance figures. To plan a flight, use the complete figure in the aircraft\'s own handbook, with its notes and conditions.',
        'يسجّل التوأم صفوفًا مختارة من أشكال الأداء في دليل الطائرة. ولتخطيط رحلة استخدم الشكل الكامل في دليل الطائرة نفسها، مع ملاحظاته وشروطه.'),
      table('stall', L('Stall speeds, power off, 2300 lb (KCAS)', 'سرعات الانهيار دون قدرة، 2300 lb (KCAS)')),
      p('A stall recovery can lose as much as 180 ft of altitude. The stall warning horn sounds 5 to 10 knots before the stall in all configurations.',
        'قد يفقد التعافي من الانهيار ما يصل إلى 180 ft من الارتفاع. ويرنّ بوق الإنذار بالانهيار قبل الانهيار بـ5 إلى 10 عقد في جميع التهيئات.',
        ['tab:STALL_KCAS', 'tab:STALL_WARNING']),
      table('takeoff', L('Short-field takeoff, flaps up, paved level dry runway, zero wind', 'الإقلاع من مدرج قصير، والقلابات مرفوعة، على مدرج معبّد مستوٍ جاف، دون رياح')),
      table('climb', L('Rate of climb at standard temperature, flaps up, full throttle, 2300 lb', 'معدل الصعود في درجة الحرارة القياسية، والقلابات مرفوعة والخانق كامل، 2300 lb')),
      table('climbTemp', L('Maximum rate of climb by temperature (ft/min)', 'أقصى معدل صعود حسب درجة الحرارة (ft/min)')),
      table('cruise', L('Cruise at standard temperature, 2300 lb, recommended lean mixture', 'الطيران الأفقي في درجة الحرارة القياسية، 2300 lb، بالخليط الفقير الموصى به')),
      table('landing', L('Short-field landing, flaps 40°, power off, maximum braking, 60 KIAS at 50 ft, 2300 lb', 'الهبوط على مدرج قصير، والقلابات 40° ودون قدرة وبأقصى كبح، و60 KIAS عند 50 ft، 2300 lb')),
    ],
  },
  {
    id: 'weight', title: L('Weight and balance', 'الوزن والاتزان'),
    blocks: [
      p('The maximum takeoff weight is 2300 lb in the normal category. The empty weight and its centre of gravity belong to each aeroplane: take them from its own weight and balance record, never from this page.',
        'الوزن الأقصى للإقلاع 2300 lb في الفئة العادية. أما الوزن الفارغ ومركز ثقله فلكل طائرة بعينها: خذهما من سجل الوزن والاتزان الخاص بها، لا من هذه الصفحة.',
        ['y79:weight.max_takeoff_lb']),
      facts([
        row(L('Datum', 'نقطة المرجع'), 'station 0, the front face of the firewall', 'المحطة 0، وهي الوجه الأمامي لجدار الحماية من النار', ['poh:loading.arrangements']),
        row(L('Pilot and front passenger', 'الطيار والراكب الأمامي'),
          'station 37 with the seat set for an average occupant (range 34 to 46)', 'المحطة 37 والمقعد مضبوط لراكب متوسط (المدى من 34 إلى 46)',
          ['poh:loading.arrangements']),
        row(L('Rear passengers', 'الركاب الخلفيون'), 'station 73', 'المحطة 73', ['poh:loading.arrangements']),
        row(L('Baggage area 1', 'منطقة الأمتعة 1'), 'stations 82 to 108, arm 95', 'من المحطة 82 إلى 108، والذراع 95', ['poh:loading.arrangements']),
        row(L('Baggage area 2', 'منطقة الأمتعة 2'), 'stations 108 to 142, arm 123', 'من المحطة 108 إلى 142، والذراع 123', ['poh:loading.arrangements']),
      ]),
      facts([
        row(L('Cabin heights (in)', 'ارتفاعات المقصورة (in)'),
          '41 ahead of the front seats, 48 at the front seats, 43 at the rear seat, 33 in the baggage area, 10¼ at the aft baggage area',
          '41 أمام المقعدين الأماميين، و48 عند المقعدين الأماميين، و43 عند المقعد الخلفي، و33 في منطقة الأمتعة، و10¼ في منطقة الأمتعة الخلفية',
          ['poh:geometry.cabin_heights_in']),
        row(L('Cabin door (in)', 'باب المقصورة (in)'),
          '32 wide at the top, 37 at the bottom, 40 high in front, 41 at the rear', 'عرضه 32 في الأعلى و37 في الأسفل، وارتفاعه 40 في الأمام و41 في الخلف',
          ['poh:geometry.door_openings_in']),
        row(L('Baggage door (in)', 'باب الأمتعة (in)'),
          '15¼ wide at top and bottom, 22 high in front, 21 at the rear', 'عرضه 15¼ في الأعلى والأسفل، وارتفاعه 22 في الأمام و21 في الخلف',
          ['poh:geometry.door_openings_in']),
      ]),
    ],
  },
  {
    id: 'systems', title: L('The aeroplane and its systems', 'الطائرة وأنظمتها'),
    blocks: [
      facts([
        row(L('Flaps', 'القلابات'),
          'single-slot, electrically driven; a switch lever in a slotted panel with mechanical stops at 10° and 20°, a scale and pointer beside it showing the flap travel, and a 15-ampere FLAP circuit breaker',
          'قلابات بشقّ واحد تُدار كهربائيًا؛ ذراع مفتاح في لوحة مشقوقة بمصدّات ميكانيكية عند 10° و20°، وبجانبه تدريج ومؤشر يبيّنان مقدار امتداد القلابات، وقاطع دائرة FLAP بقدرة 15 أمبير',
          ['poh:flaps.system']),
        row(L('Landing gear', 'جهاز الهبوط'),
          'tricycle: a steerable nose wheel with an air/oil shock strut, two main wheels on tubular spring-steel struts, wheel fairings, and a hydraulic disc brake on the inboard side of each main wheel',
          'ثلاثي العجلات: عجلة أمامية قابلة للتوجيه بممتص صدمات هوائي زيتي، وعجلتان رئيسيتان على دعامتين أنبوبيتين من فولاذ نابضي، وأغطية انسيابية للعجلات، ومكابح قرصية هيدروليكية على الجانب الداخلي لكل عجلة رئيسية',
          ['poh:landing_gear.system']),
        row(L('Doors and windows', 'الأبواب والنوافذ'),
          'two entry doors, the left one with a key lock; an openable window in the left door (the right is optional), which may be opened up to 160 knots',
          'بابا دخول، للأيسر منهما قفل بمفتاح؛ ونافذة قابلة للفتح في الباب الأيسر (والأيمن اختياري)، ويجوز فتحها حتى 160 عقدة',
          ['poh:doors_and_windows']),
        row(L('Control lock', 'قفل أدوات التحكم'),
          'a shaped steel rod with a red flag, through the pilot\'s control wheel shaft and the collar on the instrument panel; the flag covers the ignition switch',
          'قضيب فولاذي مشكَّل بعلم أحمر، يمر عبر عمود عجلة التحكم للطيار والطوق على لوحة العدادات؛ ويغطي العلم مفتاح الإشعال',
          ['poh:control_lock']),
        row(L('Baggage', 'الأمتعة'),
          'two areas, behind the rear seats and aft of the cabin bulkhead; a lockable door on the left side, and a net with tie-down straps',
          'منطقتان، خلف المقعد الخلفي وخلف الحاجز الخلفي للمقصورة؛ وباب يُقفل على الجانب الأيسر، وشبكة بأحزمة تثبيت',
          ['poh:baggage.compartment']),
      ]),
      figure('flight-controls', L('The flight controls, seen from above.', 'أدوات التحكم في الطيران، من أعلى.')),
      facts([
        row(L('Ignition', 'الإشعال'),
          'two engine-driven magnetos and two spark plugs per cylinder: the right magneto fires the lower right and upper left plugs, the left magneto the lower left and upper right; a rotary switch OFF, R, L, BOTH, START, spring-loaded back to BOTH',
          'ماغنيتوان يديرهما المحرك وشمعتا إشعال لكل أسطوانة: يشعل الماغنيتو الأيمن الشمعتين السفلية اليمنى والعلوية اليسرى، والأيسر السفلية اليسرى والعلوية اليمنى؛ ومفتاح دوّار OFF وR وL وBOTH وSTART، يعود بنابض إلى BOTH',
          ['poh:ignition.system', 'poh:ignition.plug_map', 'poh:ignition.switch']),
        row(L('Carburettor', 'المكربن'),
          'up-draft, float type, fixed jet, with an accelerator pump, idle cut-off and manual mixture control; full carburettor heat at full throttle costs about 100 to 225 RPM',
          'سحب صاعد، من نوع العوّامة، بفتحة ثابتة، مع مضخة تسارع وقطع على الخمول وتحكم يدوي بالخليط؛ وتسخين المكربن كاملًا بالخانق الكامل يُفقد نحو 100 إلى 225 RPM',
          ['poh:carburetor', 'poh:carb_heat.rpm_loss']),
        row(L('Oil cooler', 'مبرّد الزيت'), 'on the lower right side of the firewall', 'على الجانب الأيمن السفلي من جدار الحماية من النار', ['poh:oil.cooler_location']),
        row(L('Fuel system', 'نظام الوقود'),
          'gravity feed from the tanks through a selector valve (BOTH, RIGHT, LEFT, OFF) and a strainer to the carburettor, with a manual primer',
          'تغذية بالجاذبية من الخزانات عبر صمام اختيار (BOTH وRIGHT وLEFT وOFF) ومصفاة إلى المكربن، مع مضخة تحضير يدوية',
          ['poh:fuel.system']),
      ]),
      figure('fuel-system', L('The fuel system.', 'نظام الوقود.')),
      facts([
        row(L('Electrical system', 'النظام الكهربائي'),
          '28-volt DC, a 60-amp alternator and a 24-volt battery on the left forward side of the firewall',
          'تيار مستمر 28 فولت، ومولّد متناوب 60 أمبير، وبطارية 24 فولت على الجانب الأيسر الأمامي من جدار الحماية من النار',
          ['poh:electrical.system']),
        row(L('Master switch', 'المفتاح الرئيسي'),
          'a split rocker: the right half, BAT, switches all electrical power; the left half, ALT, the alternator',
          'مفتاح متأرجح بنصفين: النصف الأيمن BAT يتحكم في كل الطاقة الكهربائية، والنصف الأيسر ALT في المولّد المتناوب',
          ['poh:electrical.master']),
        row(L('Ammeter', 'مقياس التيار'), 'shows the rate at which the battery is charging or discharging', 'يبيّن معدل شحن البطارية أو تفريغها', ['poh:electrical.ammeter']),
        row(L('Vacuum system', 'نظام التفريغ'),
          'an engine-driven pump powers the attitude and heading indicators; below 4.5 inHg they are not reliable, and the suction gauge green arc is 4.5 to 5.4 inHg',
          'مضخة يديرها المحرك تشغّل الأفق الاصطناعي ومؤشر الاتجاه؛ ودون 4.5 inHg لا يُعتمد عليهما، والقوس الأخضر لمقياس التفريغ من 4.5 إلى 5.4 inHg',
          ['poh:vacuum', 'poh:suction.green_inHg']),
        row(L('Pitot-static system', 'نظام البيتوت والضغط الساكن'),
          'the pitot tube under the left wing and the static port on the lower left side of the forward fuselage; a heated pitot and an alternate static valve below the throttle are optional',
          'أنبوب البيتوت تحت الجناح الأيسر، وفتحة الضغط الساكن على الجانب الأيسر السفلي من مقدمة جسم الطائرة؛ والبيتوت المسخّن وصمام مصدر الضغط الساكن البديل تحت الخانق اختياريان',
          ['poh:pitot_static']),
        row(L('Ventilation', 'التهوية'),
          'adjustable ventilators near each upper corner of the windshield, and two for the rear cabin',
          'فتحات تهوية قابلة للضبط قرب كل زاوية علوية من الزجاج الأمامي، واثنتان للمقصورة الخلفية',
          ['poh:cabin_ventilators']),
      ]),
      p('On the ground the aeroplane is most easily moved by hand with a tow bar on the nose gear strut. When a vehicle tows it, never turn the nose wheel more than 30 degrees either side of centre.',
        'على الأرض تُحرَّك الطائرة بأسهل طريقة يدويًا بقضيب سحب يُثبَّت في دعامة العجلة الأمامية. وإذا سحبتها مركبة فلا تُدِر العجلة الأمامية أبدًا أكثر من 30 درجة إلى أي من الجانبين.',
        ['poh:ground_handling.tow_bar']),
    ],
  },
];

// Column headings of the tables drawn from shared/js/poh_tables.js and instruments.json.
export const TABLE_TEXT = {
  colour: L('Marking', 'العلامة'), range: L('Range', 'المدى'), meaning: L('Meaning', 'المعنى'),
  instrument: L('Instrument', 'العداد'),
  white: L('White arc', 'القوس الأبيض'), green: L('Green arc', 'القوس الأخضر'), yellow: L('Yellow arc', 'القوس الأصفر'), red: L('Red line', 'الخط الأحمر'),
  whiteMeaning: L('Full-flap operating range', 'مدى التشغيل بالقلابات كاملة'),
  greenMeaning: L('Normal operating range', 'مدى التشغيل العادي'),
  yellowMeaning: L('Caution range', 'مدى الحذر'),
  redMeaning: L('Never exceed', 'لا تتجاوزها'),
  min: L('Minimum', 'الحد الأدنى'), max: L('Maximum', 'الحد الأقصى'),
  tach: L('Tachometer', 'عداد الدورات'), oilP: L('Oil pressure', 'ضغط الزيت'), oilT: L('Oil temperature', 'درجة حرارة الزيت'), suction: L('Suction', 'مقياس التفريغ'),
  tachAlt: L('at sea level; the green arc extends to 2575 RPM at 5000 ft and 2700 RPM at 10000 ft', 'عند مستوى سطح البحر؛ ويمتد القوس الأخضر إلى 2575 RPM عند 5000 ft وإلى 2700 RPM عند 10000 ft'),
  speed: L('Speed', 'السرعة'), kias: L('KIAS', 'KIAS'),
  normalClimbOut: L('Normal climb out', 'الصعود العادي بعد الإقلاع'),
  bestRate: L('Best rate of climb', 'أفضل معدل صعود'), bestAngle: L('Best angle of climb', 'أفضل زاوية صعود'),
  atSea: L('at sea level', 'عند مستوى سطح البحر'), at10k: L('at 10000 ft', 'عند 10000 ft'),
  shortField50: L('Short-field takeoff, at 50 ft', 'الإقلاع من مدرج قصير، عند 50 ft'),
  approachUp: L('Approach, flaps up', 'الاقتراب، والقلابات مرفوعة'), approach40: L('Approach, flaps 40°', 'الاقتراب، والقلابات 40°'),
  shortFieldApproach: L('Short-field approach', 'الاقتراب إلى مدرج قصير'),
  balked: L('Balked landing, flaps 20°', 'الهبوط المُجهَض، والقلابات 20°'),
  crosswind: L('Maximum demonstrated crosswind', 'أقصى رياح مستعرضة مُختبرة'), knots: L('kt', 'kt'),
  flaps: L('Flaps', 'القلابات'), cg: L('Centre of gravity', 'مركز الثقل'), aft: L('most rearward', 'الأقصى خلفًا'), fwd: L('most forward', 'الأقصى أمامًا'),
  bank: L('Bank', 'الميلان'),
  elevation: L('Field elevation (ft)', 'منسوب المطار (ft)'), temp: L('°C', '°C'), weight: L('Weight (lb)', 'الوزن (lb)'),
  roll: L('Ground roll (ft)', 'مسافة الدحرجة (ft)'), over50: L('Total to clear 50 ft (ft)', 'المسافة الكلية لتجاوز 50 ft (ft)'),
  liftOff: L('Lift-off KIAS', 'KIAS عند الارتفاع عن الأرض'), at50: L('KIAS at 50 ft', 'KIAS عند 50 ft'),
  altitude: L('Pressure altitude (ft)', 'الارتفاع الضغطي (ft)'), climbKias: L('Climb KIAS', 'KIAS الصعود'), fpm: L('Rate of climb (ft/min)', 'معدل الصعود (ft/min)'),
  rpm: L('RPM', 'RPM'), bhp: L('% BHP', '% BHP'), ktas: L('KTAS', 'KTAS'),
  landRoll: L('Ground roll (ft)', 'مسافة الدحرجة (ft)'), landOver50: L('Total from 50 ft (ft)', 'المسافة الكلية من 50 ft (ft)'),
};

export const SOURCES = {
  title: L('Sources', 'المصادر'),
  en: 'The values come from the twin\'s records of the Cessna Model 172N Pilot\'s Operating Handbook, 1979 model (issued 1 July 1978), each with its page: the POH reference values, the 1979 reference data, the instrument markings and the performance tables. The repository\'s handbook README names the files and says how each value was read. The text is FlyGACA\'s; no page or figure of the handbook is reproduced.',
  ar: 'القيم مأخوذة من سجلات التوأم لدليل تشغيل الطيار لطائرة Cessna Model 172N موديل 1979 (الصادر في 1 يوليو 1978)، مع صفحة كل قيمة: قيم مرجع الدليل، وبيانات المرجع لموديل 1979، وعلامات الأجهزة، وجداول الأداء. ويسمّي ملف README الخاص بالدليل في المستودع الملفات ويبيّن كيف قُرئت كل قيمة. والنص من كتابة FlyGACA، ولا تُستنسخ فيه أي صفحة أو شكل من الدليل.',
};
