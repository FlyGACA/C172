// The names a reader sees for the catalogue's systems and for how well a part is sourced, in both languages, and the
// order the systems are listed in. A system is named the way the Phase 8 viewer names it (its own strings), so the two
// never differ; the few systems the viewer does not name are named here. The Arabic is a draft until a native reader has
// reviewed it. No DOM here, so it can be tested alone.
import { STRINGS } from '../../08_realistic_digital_twin/js/i18n.js';

/** The viewer's parts tree in its order, then the fasteners, the standard hardware and the ground equipment. */
export const ORDER = ['AIRFRAME', 'WING_L', 'WING_R', 'EMPENNAGE', 'GEAR', 'POWERPLANT', 'ENGINE', 'IGNITION', 'INDUCTION', 'OIL', 'FUEL', 'ELECTRICAL', 'AVIONICS', 'VACUUM',
  'PITOT_STATIC', 'STALL_WARNING', 'CONTROLS', 'BRAKES', 'CABIN_AIR', 'INTERIOR', 'PANEL', 'INSTRUMENTS', 'FASTENERS', 'HARDWARE', 'GROUND_EQUIPMENT'];

const EXTRA = {
  FASTENERS: { en: 'Fasteners', ar: 'المثبّتات' },
  HARDWARE: { en: 'Standard hardware', ar: 'العتاد القياسي' },
  GROUND_EQUIPMENT: { en: 'Ground equipment', ar: 'معدات الأرض' },
};

/** @returns {{ en: string, ar: string }} the name of a system; its id when it has no name. */
export function systemName(id) {
  const pick = (lang) => (STRINGS[lang].groups8 || {})[id] || (STRINGS[lang].systems8 || {})[id] || (EXTRA[id] || {})[lang] || id;
  return { en: pick('en'), ar: pick('ar') };
}

/** How well a part is sourced: a short name and what it means, as the key at the foot of the page says. */
export const SOURCE_NAMES = {
  poh: { en: 'In the POH', ar: 'في دليل POH', note: { en: "The Pilot's Operating Handbook shows or names it", ar: 'يظهر في دليل تشغيل الطيار أو يُذكر فيه' } },
  type_data: { en: 'Type data', ar: 'بيانات الطراز', note: { en: "From the type's published data", ar: 'من البيانات المنشورة للطراز' } },
  estimated: { en: 'Estimated', ar: 'تقديرية', note: { en: 'Representative: the part is known to exist; its position and size are not from a drawing', ar: 'تمثيلية: القطعة موجودة فعلًا، لكن موضعها ومقاسها ليسا من رسم هندسي' } },
};
