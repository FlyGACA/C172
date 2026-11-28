// The naming quiz: a picture and four names, or a name and four pictures. Questions are drawn from the catalogue's own
// parts, so the Arabic and English names are the catalogue's. No DOM here, so it can be tested alone.
import { seeded } from './trainer.js';
export { seeded };

export const MODES = ['name', 'picture', 'mixed'];
export const ROUND = 10;

const shuffle = (list, rng) => { const a = [...list]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const clean = (t) => t.trim().toLowerCase();

/**
 * One round of questions.
 * @param {{ id: string, s: string, en: string, ar: string }[]} parts  every part of the catalogue
 * @param {{ mode?: string, system?: string, n?: number, rng?: () => number }} options
 * @returns {{ mode: 'name'|'picture', answer: object, options: object[], correct: number }[]}
 *   In 'name' mode the reader sees the picture and picks a name; in 'picture' mode they see the name and pick a picture.
 */
export function makeRound(parts, { mode = 'name', system = '', n = ROUND, rng = Math.random } = {}) {
  const pool = system ? parts.filter((p) => p.s === system) : parts;
  const questions = [];
  for (const answer of shuffle(pool, rng)) {
    if (questions.length >= n) break;
    // Distractors that look alike are the point, so those from the same system come first; none may share a name with the answer or each other.
    const taken = new Set([clean(answer.en), clean(answer.ar)]), chosen = [];
    const add = (candidates) => { for (const c of shuffle(candidates, rng)) { if (chosen.length === 3) break; if (c === answer || taken.has(clean(c.en)) || taken.has(clean(c.ar))) continue; taken.add(clean(c.en)); taken.add(clean(c.ar)); chosen.push(c); } };
    add(parts.filter((p) => p.s === answer.s)); add(parts);
    if (chosen.length < 3) continue;
    const options = shuffle([answer, ...chosen], rng);
    const how = mode === 'mixed' ? (rng() < 0.5 ? 'name' : 'picture') : mode;
    questions.push({ mode: how, answer, options, correct: options.indexOf(answer) });
  }
  return questions;
}

/** The result of a round: how many were right, and which parts to look at again. */
export function summarize(results) {
  const right = results.filter((r) => r.ok).length;
  return { right, total: results.length, again: results.filter((r) => !r.ok).map((r) => r.part) };
}
