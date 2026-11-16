// Deep links: a URL that opens the viewer on one view — a mode, a selected part, a guided scenario or lesson.
// ?mode=engine&part=POWERPLANT.propeller&scenario=runup   (with ?q= and ?lang=, which the viewer already reads)
// Every value is checked before it is used. A value that fails is left out, named in `rejected`, and the rest
// of the link still applies; a bad link never stops the viewer from opening.

/** The viewer's modes, as on the mode buttons of index.html. */
export const MODES = ['exterior', 'cockpit', 'engine', 'systems', 'flight'];

/** A part's name in the model: SYSTEM.part, more dotted levels allowed (GEAR.nose_wheel.tyre, PANEL.ASI.needle_ASI). */
export const PART_NAME = /^[A-Z][A-Z0-9_]*(\.[A-Za-z0-9_]+)+$/;
const MAX_PART = 120;
const SHOWN = 80;                    // how much of a rejected value is repeated back

/**
 * Read and check the deep-link parameters.
 * @param {URLSearchParams} params
 * @param {{ scenarios: { id: string, lesson?: boolean }[] }} known  the guided scenarios and the flight lessons
 * @returns {{ mode: string|null, part: string|null, scenario: string|null, lesson: boolean,
 *             rejected: { key: string, value: string, reason: string }[] }}
 * `part` has passed the name check only: whether the model has that part is known once the model is loaded.
 */
export function parseLink(params, { scenarios = [] } = {}) {
  const link = { mode: null, part: null, scenario: null, lesson: false, rejected: [] };
  const reject = (key, value, reason) => link.rejected.push({ key, value: String(value).slice(0, SHOWN), reason });
  const one = (key) => {
    const all = params.getAll(key);
    if (all.length === 0) return null;
    if (all.length > 1) { reject(key, all.join(','), 'given more than once'); return null; }
    return all[0];
  };

  const scenario = one('scenario');
  if (scenario !== null) {
    const s = scenarios.find((x) => x.id === scenario);
    if (s) { link.scenario = s.id; link.lesson = !!s.lesson; } else reject('scenario', scenario, 'no such scenario or lesson');
  }

  const mode = one('mode');
  if (mode !== null) {
    if (!MODES.includes(mode)) reject('mode', mode, 'no such mode');
    // A lesson is flown: it puts the viewer in flight. A guided scenario sets its own state on the ground,
    // which the flight mode would replace with an aircraft on the runway.
    else if (link.scenario && link.lesson && mode !== 'flight') reject('mode', mode, 'a lesson opens in the flight mode');
    else if (link.scenario && !link.lesson && mode === 'flight') reject('mode', mode, 'a guided scenario does not open in the flight mode');
    else link.mode = mode;
  }

  const part = one('part');
  if (part !== null) {
    if (part.length > MAX_PART || !PART_NAME.test(part)) reject('part', part, 'not a part name');
    else link.part = part;
  }
  return link;
}
