#!/usr/bin/env python3
"""Text-layer gate for the handbook PDFs: no private-use characters, no Type 3 fonts, no NUL bytes, bookmarks present.

    python3 11_training_handbook/check_pdf.py [--allow-nul] [pdf ...]

Defaults to both PDFs in 11_training_handbook/out/. Needs pypdf. Exits 1 on any failure.
--allow-nul reports NUL bytes without failing (fix_tounicode.py, run by the build, removes them).
"""
import re, sys
from pathlib import Path
import pypdf

args = [a for a in sys.argv[1:] if not a.startswith('--')]
allow_nul = '--allow-nul' in sys.argv
out = Path(__file__).resolve().parent / 'out'
files = [Path(a) for a in args] or sorted(out.glob('*.pdf'))
failed = False
for f in files:
    r = pypdf.PdfReader(str(f))
    text = ''.join(p.extract_text() or '' for p in r.pages)
    type3 = 0
    for p in r.pages:
        fonts = (p.get('/Resources') or {}).get('/Font') or {}
        type3 += sum(1 for k in fonts if fonts[k].get_object().get('/Subtype') == '/Type3')
    res = {
        'private-use characters': len(re.findall('[-]', text)),
        'Type 3 font uses': type3,
        'NUL bytes': text.count('\x00'),
        'missing bookmarks': 0 if r.outline else 1,
    }
    bad = {k: v for k, v in res.items() if v and not (allow_nul and k == 'NUL bytes')}
    print(f'{f.name}: {len(r.pages)} pages, ' + ', '.join(f'{k} {v}' for k, v in res.items()) + (' FAIL' if bad else ' ok'))
    failed |= bool(bad)
sys.exit(1 if failed else 0)
