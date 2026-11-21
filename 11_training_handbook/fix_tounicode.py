#!/usr/bin/env python3
"""Repair the text layer of a handbook PDF: give every glyph that Chromium mapped to U+0000 its real character.

Chromium writes <gid> <0000> in the ToUnicode map for glyphs it cannot trace back to a character: the font's alternate
forms (Arabic-script digits, short letter forms, shadda ligatures). The subset keeps the original glyph ids, so each
one is looked up in the vendored font and mapped from its glyph name (zero.loclARAB -> 0, uni0631.short -> U+0631).

    python3 fix_tounicode.py file.pdf            rewrite in place
Needs pypdf and fontTools. Exits 1 if a NUL glyph cannot be resolved.
"""
import re, sys
from pathlib import Path
import pypdf
from pypdf.generic import NameObject
from fontTools.ttLib import TTFont

FONTS = Path(__file__).resolve().parent.parent / '09_book_figures' / 'vendor' / 'fonts'
DIGITS = {n: str(i) for i, n in enumerate('zero one two three four five six seven eight nine'.split())}

def char_for(glyph_name, cmap_by_name):
    base = glyph_name.split('.')[0]
    if m := re.fullmatch(r'uni((?:[0-9A-F]{4})+)', base): return m.group(1)  # one or several code points (shadda + vowel)
    if base in DIGITS: return f'{ord(DIGITS[base]):04X}'
    c = cmap_by_name.get(base)
    return None if c is None else f'{c:04X}'

def main(path):
    r = pypdf.PdfReader(path); w = pypdf.PdfWriter(clone_from=r)
    fixed = bad = 0; done = set()
    for page in w.pages:
        for ref in [page['/Resources']['/Font'].raw_get(k) for k in page['/Resources']['/Font']]:
            if ref.idnum in done: continue
            done.add(ref.idnum); font = ref.get_object()
            name = str(font.get('/BaseFont', ''))
            style = 'SemiBold' if 'SemiBold' in name else 'Regular' if 'Plex' in name else None
            if not style or '/ToUnicode' not in font: continue
            tt = TTFont(FONTS / f'IBMPlexSansArabic-{style}.ttf'); order = tt.getGlyphOrder()
            by_name = {g: c for c, g in tt.getBestCmap().items()}
            stream = font['/ToUnicode'].get_object()
            text = stream.get_data().decode('latin1')
            def sub(m):
                nonlocal fixed, bad
                c = char_for(order[int(m.group(1), 16)], by_name)
                if c is None or int(c[:4], 16) == 0: bad += 1; return m.group(0)
                fixed += 1; return f'<{m.group(1)}> <{c}>'
            stream.set_data(re.sub(r'<([0-9A-Fa-f]{4})>\s*<0000>', sub, text).encode('latin1'))
    w.write(path)
    print(f'{Path(path).name}: {fixed} NUL glyph mappings repaired, {bad} unresolved')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(max(main(p) for p in sys.argv[1:]) if len(sys.argv) > 1 else 2)
