import json, pathlib
p=pathlib.Path(__file__).parent
systems={
 'engine':{'ar':'المحرك والإشعال','components':['ENGINE__crankcase','ENGINE__crankshaft','ENGINE__cylinder_1__barrel','ENGINE__alternator','ENGINE__starter'],'reference':'POH Section 1: O-320-H2AD, 160 BHP @ 2700 RPM','status':'manufacturer_reference_for_1979; geometry_illustrative'},
 'fuel':{'ar':'الوقود','components':['FUEL__left_wing_tank','FUEL__right_wing_tank','FUEL__selector','FUEL__strainer'],'reference':'POH Section 1: standard 43 total / 40 usable US gal; long range 54 total / 50 usable','status':'manufacturer_reference_for_1979; routing_illustrative'},
 'electrical':{'ar':'الكهرباء','components':['ELECTRICAL__battery','ELECTRICAL__master_contactor','ELECTRICAL__alternator_bus'],'reference':'POH Section 7; exact installation and supplements require checking','status':'conceptual_only'},
 'instruments':{'ar':'العدادات','components':['PANEL__AIRSPEED__housing','PANEL__ALTIMETER__housing','PANEL__ATTITUDE__housing','PANEL__VSI__housing','PANEL__HEADING__housing','PANEL__TURN_COORDINATOR__housing'],'reference':'POH Section 7; installed instruments are configuration-dependent','status':'conceptual_only'},
 'airframe':{'ar':'الهيكل والتحكم','components':[],'reference':'POH Section 1 figure 1-1; exact CAD requires engineering drawings','status':'illustrative'}
}
(p/'system_manifest.json').write_text(json.dumps({'model':'Cessna 172N','reference_year':1979,'systems':systems,'disclaimer':'Educational prototype only; not approved flight instruction or maintenance data'},ensure_ascii=False,indent=2))
lessons=[
 {'id':'engine','title':'محرك Lycoming O-320-H2AD','fact':'160 BHP عند 2700 RPM','simulation':'مؤشر RPM يحسب علاقة افتراضية مع throttle وmixture، لا يمثل أداء المحرك الفعلي','quiz':{'q':'ما القدرة الاسمية المرجعية للمحرك؟','options':['160 BHP','200 BHP','100 BHP'],'answer':0}},
 {'id':'fuel','title':'الوقود','fact':'خزانات قياسية 43 جالون إجمالي و40 قابلة للاستخدام','simulation':'مستوى الوقود وانقطاع التدفق تعليميان، ولا يطبقان سلوك نظام الوقود الحقيقي','quiz':{'q':'كم الوقود القابل للاستخدام في الخزانات القياسية؟','options':['43 جالون','40 جالون','50 جالون'],'answer':1}},
 {'id':'electrical','title':'الكهرباء','fact':'راجع Section 7 ووثائق الطائرة المحددة للتجهيزات','simulation':'تعطل alternator يوقف الشحن افتراضيا ويقلل مؤشر طاقة بطارية تجريبية','quiz':{'q':'ما وظيفة المولد Alternator؟','options':['شحن البطارية وتغذية الشبكة','قياس الضغط الجوي','تغيير زاوية المروحة'],'answer':0}},
 {'id':'instruments','title':'عدادات الطيران','fact':'أجهزة Six Pack التقليدية تتضمن IAS وALT وVSI وAI وHI وTC','simulation':'تجميد مؤشرات الأعطال تبسيط لا يعكس جميع الحالات الفيزيائية','quiz':{'q':'أي عداد يعتمد على فرق الضغط الكلي والثابت؟','options':['Airspeed Indicator','Heading Indicator','Tachometer'],'answer':0}},
 {'id':'airframe','title':'هيكل الطائرة','fact':'امتداد الجناحين المرجعي 36 قدمًا','simulation':'الهيكل الثلاثي الأبعاد تقريبي ولا يطابق أبعاد جميع الأجزاء','quiz':{'q':'ما امتداد الجناحين المرجعي؟','options':['36 قدمًا','42 قدمًا','29 قدمًا'],'answer':0}}
]
(p/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2))
