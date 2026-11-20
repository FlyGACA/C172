# المرحلة 11 — دليل التدريب لطائرة C172N

دليل FlyGACA الخاص لطائرة سيسنا 172N في التوأم، بالعربية والإنجليزية: [الصفحة](index.html)، وملفات PDF بمقاس A4 في
[`out/`](out/). [English version](README.md)

يتبع الترتيب الذي يعرفه الطيار من دليل تشغيل الطيار (عام، الحدود، إجراءات الطوارئ، الإجراءات العادية، الأداء، الوزن
والاتزان، الأنظمة)، لكن نصه من كتابة FlyGACA، وهو **ليس** دليل تشغيل الطيار (POH) ولا دليل طيران الطائرة (AFM). لم
تعتمده أي جهة تنظيمية ولا أي جهة مصنّعة، ولا يجوز أبدًا استخدامه للطيران. وكل صفحة منه تقول ذلك باللغتين، مع الإشعار الذي
تحمله الصفحة الرئيسية.

## من أين تأتي القيم

لا يُكتب رقم في النص دون مصدره. فالقيم هي سجلات التوأم لدليل تشغيل الطيار لطائرة Cessna Model 172N (موديل 1979، الصادر
في 1 يوليو 1978)، مع صفحة كل قيمة:

| السجل | ما يُستخدم له |
|---|---|
| [`08_realistic_digital_twin/data/poh_references.json`](../08_realistic_digital_twin/data/poh_references.json) | المحرك والمروحة والوقود والزيت والحدود وقوائم التحقق والأنظمة ومحطات التحميل والأبعاد |
| [`04b_poh_reference/poh_1979_reference_data.json`](../04b_poh_reference/poh_1979_reference_data.json) | الوزن الأقصى للإقلاع |
| [`08_realistic_digital_twin/data/instruments.json`](../08_realistic_digital_twin/data/instruments.json) | أقواس العدادات وخطوطها الحمراء |
| [`shared/js/poh_tables.js`](../shared/js/poh_tables.js) | جداول السرعات وسرعات الانهيار والإقلاع والصعود والطيران الأفقي والهبوط والانزلاق |

والأشكال الأربعة من المرحلة 9 ([`09_book_figures/`](../09_book_figures/README_AR.md))، مستخدمة كما هي.

في [`content.mjs`](content.mjs) يسمّي كل جزء من النص السجلات التي يستند إليها، وتطبع الصفحة بجانبه صفحاتها في الدليل.
وتفشل الاختبارات إذا ورد في جزء رقم ليس في أحد تلك السجلات، أو إذا لم يكن لسجل صفحة، أو إذا غابت إحدى اللغتين، أو إذا لم
يكن `index.html` محدَّثًا.

## البناء

```bash
node 11_training_handbook/build.mjs          # يكتب index.html
node 11_training_handbook/build.mjs --pdf    # ويطبع أيضًا out/flygaca-c172n-training-handbook-{en,ar}.pdf (Playwright)
node 11_training_handbook/build.mjs --check  # يفشل إذا لم يكن index.html محدَّثًا
node --test 11_training_handbook/tests/handbook.test.mjs
```

أوامر npm هي `handbook` و`handbook:pdf` و`handbook:check`، ويشغّل `npm test` الاختبارات. غيّر القيمة في سجلها لا في
الصفحة، وغيّر الصياغة في `content.mjs`، ثم أعد البناء.

## ما لم يُنجز بعد

- لم يراجع النص طيار ولا مدرب، ولم يراجع العربية قارئ عربي متخصص في الطيران.
- يسجّل التوأم بعض إجراءات الطوارئ في الدليل وبعض صفوف أشكال الأداء فقط، وتقول الصفحة ذلك حيث ينطبق.
