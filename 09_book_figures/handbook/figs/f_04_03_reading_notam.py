"""Figure 4-3 (new). Reading a NOTAM, on the illustrative notice of Chapter 4 ("Reading a NOTAM (illustrative only; not a real notice)"): the notice as four lines of coded text, each part with a colour and a number, and under it
the validity on a time scale in UTC and in local time (UTC+3).

The notice: A1234/26 NOTAMN / Q) OEJD/QMXLC/IV/M/A/000/999/ / A) OEXX B) 2611051200 C) 2611051600 / E) TWY B CLSD DUE WIP. 1 the series, number and year with N for a new notice, 2 the Q-line (the FIR OEJD, the subject QMX taxiway and LC closed),
3 the placeholder aerodrome of item A, 4 the start and end of validity (the legend's numbers follow the five lines) (B and C: 5 November 2026, 1200 to 1600 UTC), 5 the plain-language text of item E (taxiway B closed, work in progress); under them a time scale with the closure from 12 to 16 UTC (blue) and from 15 to 19 local
time (amber), three hours later. Latin capitals and digits only (they are the notice's own); the words are in the legend. The notice is made up and is not a real one, as the chapter says."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 314
U = "nt4"
INK, SLATE, BLUE, GREEN, AMBER, RED, PURPLE = "#1E293B", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#7C3AED"
LEFT = 40.0
LINES = (
    (76.0, (("A1234/26 NOTAMN", INK),)),
    (102.0, (("Q) OEJD/QMXLC/IV/M/A/000/999/", PURPLE),)),
    (128.0, (("A) OEXX", GREEN),)),
    (154.0, (("B) 2611051200 C) 2611051600", BLUE),)),
    (180.0, (("E) TWY B CLSD DUE WIP", RED),)),
)
SIZE = 11.0


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.0, height=11.0):
    w = gwidth(s, size) + 11.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.1" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<rect x="24" y="52" width="440" height="152" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.4" filter="url(#{U}ds)"/>')


def text_block():
    out = []
    for y, parts in LINES:
        x = LEFT
        for s, col in parts:
            w = gwidth(s, SIZE, 0.6)
            out.append(H.glyph_text(s, x + w / 2, y, SIZE, col, spacing=0.6))
            x += w + 5.0
    return "".join(out)


def marks():
    """Thin coloured underlines of the parts, so that the callouts point at something."""
    out = []
    for y, parts in LINES:
        x = LEFT
        for s, col in parts:
            w = gwidth(s, SIZE, 0.6)
            out.append(f'<line x1="{n(x)}" y1="{n(y + 9)}" x2="{n(x + w)}" y2="{n(y + 9)}" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-opacity="0.8"/>')
            x += w + 5.0
    return "".join(out)


def scale():
    """The validity on a time scale: 10 to 20 hours, UTC above (blue) and local time below (amber)."""
    x0, x1 = 80.0, 560.0
    h0, h1 = 10.0, 20.0
    def hx(h):
        return x0 + (h - h0) / (h1 - h0) * (x1 - x0)
    out = []
    y_utc, y_loc = 244.0, 272.0
    for h in range(10, 21):
        out.append(f'<line x1="{n(hx(h))}" y1="{n(y_utc - 6)}" x2="{n(hx(h))}" y2="{n(y_loc + 6)}" stroke="{SLATE}" stroke-opacity="0.16" stroke-width="1"/>')
        out.append(H.glyph_text(str(h), hx(h), y_loc + 14.0, 4.6, SLATE, spacing=0.3))
    out.append(f'<rect x="{n(hx(12))}" y="{n(y_utc - 7)}" width="{n(hx(16) - hx(12))}" height="14" rx="5" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>')
    out.append(f'<rect x="{n(hx(15))}" y="{n(y_loc - 7)}" width="{n(hx(19) - hx(15))}" height="14" rx="5" fill="{AMBER}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>')
    out.append(pill("UTC", 46.0, y_utc, BLUE, 5.6, 11.0))
    out.append(pill("+3", 46.0, y_loc, AMBER, 5.6, 11.0))
    # the three hours that the local time is ahead
    out.append(f'<path d="M{n(hx(12))} {n(y_utc + 8)} L{n(hx(15))} {n(y_loc - 8)}" stroke="{SLATE}" stroke-width="1.4" stroke-dasharray="3 3" fill="none"/><path d="M{n(hx(16))} {n(y_utc + 8)} L{n(hx(19))} {n(y_loc - 8)}" stroke="{SLATE}" stroke-width="1.4" stroke-dasharray="3 3" fill="none"/>')
    return "".join(out)


def callouts():
    c = S.callout
    out = []
    for k, (y, parts) in enumerate(LINES):
        w = sum(gwidth(t, SIZE, 0.6) for t, _ in parts) + 5.0 * (len(parts) - 1)
        out.append(c(k + 1, 500.0, y, LEFT + w + 8.0, y, r=9.5))
    out.append(c(6, 596.0, 258.0, 518.0, 272.0, r=9.5))                 # the time scale
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), marks(), text_block(), scale(), callouts()]


def plate():
    return {
        "id": "fig-04-03-reading-notam",
        "replaces": "fig-04-03-reading-notam.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-04-03-reading-notam.jpg",
        "caption": "Figure 4-3. Reading a NOTAM: the illustrative notice of this chapter, part by part, and its validity in UTC and in local time",
        "desc": ("Figure 4-3. Reading the illustrative NOTAM of this chapter (made up, not a real notice): its four lines of coded text part by part, and under it the validity, "
                 "1200 to 1600 UTC, on a time scale next to the same closure in local time (UTC+3), 1500 to 1900."),
        "legend": [
            "A1234/26 NOTAMN: the series, number and year. NOTAMN means a new NOTAM (NOTAMR replaces one and NOTAMC cancels one).",
            "The Q-line: the FIR (OEJD, Jeddah) and the subject code, QMX for a taxiway and LC for closed.",
            "A) OEXX: the aerodrome. OEXX is a placeholder; real Saudi aerodrome indicators begin with OE.",
            "B) and C): the validity, from 5 November 2026 at 1200 UTC to 1600 UTC.",
            "E): the text in plain language: taxiway B is closed because of work in progress.",
            "The same closure on a time scale: 1200 to 1600 UTC (blue) is 1500 to 1900 in local time, UTC+3 (amber). Convert every NOTAM time before you decide whether it affects your flight.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
