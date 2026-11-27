// The control-effect trainer: "move the control that raises the nose". Each challenge names an effect; the reader sets the
// control that causes it and is told what their setting does. The effects follow from the models' hinges (the tests work
// them out again from the hinge axes and signs in the models): +X is toward the left wing, +Y up, +Z forward.
// No DOM here, so it can be tested alone.

/** What a control does on each side of centre. */
export const EFFECTS = {
  elevator: {
    pos: { en: 'The elevator’s trailing edge goes up and pushes the tail down: the nose rises.', ar: 'ينخفض ذيل الطائرة لأن الحافة الخلفية لذيل الارتفاع تصعد: فترتفع المقدمة.' },
    neg: { en: 'The elevator’s trailing edge goes down and lifts the tail: the nose drops.', ar: 'يرتفع الذيل لأن الحافة الخلفية لذيل الارتفاع تنزل: فتنخفض المقدمة.' },
  },
  aileron: {
    pos: { en: 'The left aileron goes up and the right one goes down: the aircraft rolls to the left.', ar: 'يصعد الجنيح الأيسر وينزل الأيمن: فتميل الطائرة إلى اليسار.' },
    neg: { en: 'The right aileron goes up and the left one goes down: the aircraft rolls to the right.', ar: 'يصعد الجنيح الأيمن وينزل الأيسر: فتميل الطائرة إلى اليمين.' },
  },
  rudder: {
    pos: { en: 'The rudder swings to the right: the nose yaws to the right.', ar: 'تنحرف الدفة إلى اليمين: فتدور المقدمة إلى اليمين.' },
    neg: { en: 'The rudder swings to the left: the nose yaws to the left.', ar: 'تنحرف الدفة إلى اليسار: فتدور المقدمة إلى اليسار.' },
  },
  flaps: {
    pos: { en: 'The flaps go down: more lift, and more drag, at low speed.', ar: 'تنزل القلابات: رفع أكبر ومقاومة أكبر عند السرعة المنخفضة.' },
  },
};

/** The challenges. `want` says whether a setting of the control is the answer. */
export const CHALLENGES = [
  { id: 'nose_up', key: 'elevator', want: (v) => v >= 0.3, en: 'Raise the nose', ar: 'ارفع مقدمة الطائرة' },
  { id: 'nose_down', key: 'elevator', want: (v) => v <= -0.3, en: 'Lower the nose', ar: 'اخفض مقدمة الطائرة' },
  { id: 'roll_left', key: 'aileron', want: (v) => v >= 0.3, en: 'Roll the aircraft to the left', ar: 'أمِل الطائرة إلى اليسار' },
  { id: 'roll_right', key: 'aileron', want: (v) => v <= -0.3, en: 'Roll the aircraft to the right', ar: 'أمِل الطائرة إلى اليمين' },
  { id: 'yaw_right', key: 'rudder', want: (v) => v >= 0.3, en: 'Yaw the nose to the right', ar: 'أدِر المقدمة إلى اليمين' },
  { id: 'yaw_left', key: 'rudder', want: (v) => v <= -0.3, en: 'Yaw the nose to the left', ar: 'أدِر المقدمة إلى اليسار' },
  { id: 'lift_slow', key: 'flaps', want: (v) => v >= 20, en: 'Get more lift at low speed', ar: 'احصل على رفع أكبر عند السرعة المنخفضة' },
];

/** What a setting of a control does, or null when it is at or near centre. */
export function effectOf(key, value) {
  const e = EFFECTS[key]; if (!e) return null;
  if (key === 'flaps') return value >= 1 ? e.pos : null;
  if (Math.abs(value) < 0.05) return null;
  return value > 0 ? e.pos : e.neg;
}

/**
 * Judges a setting against a challenge.
 * @returns {{ ok: boolean, now: { en: string, ar: string } | null }} `now` is what the reader's setting does, if anything.
 */
export function judge(challenge, value) {
  return { ok: challenge.want(value), now: effectOf(challenge.key, value) };
}

/** A small seeded random generator, so that a round can be repeated in a test. */
export function seeded(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/** The next challenge: one not asked yet in this round, and the same one never twice running. */
export function nextChallenge(asked, rng = Math.random) {
  const fresh = CHALLENGES.filter((c) => !asked.includes(c.id));
  const pool = fresh.length ? fresh : CHALLENGES.filter((c) => c.id !== asked.at(-1));
  return pool[Math.floor(rng() * pool.length)];
}
