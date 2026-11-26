// What a typed word is compared with. Texts are folded first, so that spellings a reader may use interchangeably compare
// equal: capitals, accents, Arabic vowel marks and the hamza and ya and ta marbuta variants, Arabic-Indic digits, and the
// dots and underscores of a part's name. No DOM here, so it can be tested alone.
const MARKS = /[ً-ٰٟـ]/g; // Arabic vowel marks, the dagger alef and the tatweel

/** @returns {string} the text in the form words are compared in */
export function fold(text) {
  return String(text).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(MARKS, '')
    .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ئ/g, 'ي').replace(/ؤ/g, 'و').replace(/ة/g, 'ه')
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

/** @returns {string[]} the words of a query, folded */
export const words = (query) => fold(query).split(' ').filter(Boolean);

/** The folded text a part is searched in: both names, its id, and the names of what is drawn with it. */
export const haystack = (part) => fold([part.en, part.ar, part.id, ...part.more.flatMap((m) => [m[1], m[2]])].join(' '));

/** Whether every word of a query is in a haystack. No words matches everything. */
export const matches = (hay, ws) => ws.every((w) => hay.includes(w));
