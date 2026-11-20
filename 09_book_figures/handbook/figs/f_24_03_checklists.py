"""Figure 24-3 (new). Checklists for finding hazards, from that section of Chapter 24: IMSAFE (the pilot) as six tiles and PAVE (the whole flight) as four.

The letters are the checklists' own, with a small drawing each: I a thermometer, M a capsule, S a clock pressed by two arrows, A a glass, F a moon and Z, E a cracked heart; P a headset, A the aeroplane from above, V sun, cloud and high ground, E a calendar pushed by two arrows.
Callout 1 is IMSAFE, 2 is PAVE and 3 is its last letter, external pressures. Shapes, letters and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 276
U = "ck24"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
Y1, H1 = 16.0, 116.0
Y2, H2 = 144.0, 116.0
X1 = [16.0 + i * 102.0 for i in range(6)]
W1 = 96.0
X2 = [16.0 + i * 153.0 for i in range(4)]
W2 = 147.0


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def letter(ch, cx, y, col):
    return f'<circle cx="{n(cx)}" cy="{n(y + 22)}" r="15" fill="{col}" stroke="#FFFFFF" stroke-width="1.8" filter="url(#{U}ds)"/>' + H.glyph_text(ch, cx, y + 22, 14, "#FFFFFF", spacing=0.4)


def ds():
    return f' filter="url(#{U}ds)"'


def icon(kind, cx, cy):
    if kind == "thermo":
        o = f'<rect x="{n(cx - 5)}" y="{n(cy - 26)}" width="10" height="38" rx="5" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2"{ds()}/><circle cx="{n(cx)}" cy="{n(cy + 15)}" r="9.5" fill="{RED}" stroke="{SLATE}" stroke-width="2"/><rect x="{n(cx - 2.2)}" y="{n(cy - 10)}" width="4.4" height="26" rx="2.2" fill="{RED}"/>'
        return o + "".join(f'<line x1="{n(cx + 8)}" y1="{n(cy - 20 + k * 8)}" x2="{n(cx + 13)}" y2="{n(cy - 20 + k * 8)}" stroke="{SLATE}" stroke-width="1.4"/>' for k in range(4))
    if kind == "capsule":
        return (f'<g transform="rotate(-35 {n(cx)} {n(cy)})"><rect x="{n(cx - 22)}" y="{n(cy - 10)}" width="44" height="20" rx="10" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2"{ds()}/>'
                f'<path d="M{n(cx)} {n(cy - 10)} h12 a10 10 0 0 1 0 20 h-12 Z" fill="{BLUE}"/></g>')
    if kind == "squeeze":
        o = (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="17" fill="#FFFFFF" stroke="{SLATE}" stroke-width="2.6"{ds()}/>'
             f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - 11)}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/><line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + 8)}" y2="{n(cy + 3)}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
        for sg in (-1, 1):
            o += f'<line x1="{n(cx + sg * 38)}" y1="{n(cy)}" x2="{n(cx + sg * 24)}" y2="{n(cy)}" stroke="{RED}" stroke-width="4" stroke-linecap="round"/><path d="M{n(cx + sg * 20)} {n(cy)} L{n(cx + sg * 28)} {n(cy - 6)} L{n(cx + sg * 28)} {n(cy + 6)} Z" fill="{RED}"/>'
        return o
    if kind == "glass":
        return (f'<path d="M{n(cx - 12)} {n(cy - 20)} L{n(cx + 12)} {n(cy - 20)} L{n(cx + 9)} {n(cy + 20)} L{n(cx - 9)} {n(cy + 20)} Z" fill="#F1F5F9" stroke="{SLATE}" stroke-width="2"{ds()}/>'
                f'<path d="M{n(cx - 10.6)} {n(cy - 3)} L{n(cx + 10.6)} {n(cy - 3)} L{n(cx + 9)} {n(cy + 20)} L{n(cx - 9)} {n(cy + 20)} Z" fill="#D97706" fill-opacity="0.85"/>')
    if kind == "moon":
        o = f'<circle cx="{n(cx - 6)}" cy="{n(cy + 2)}" r="18" fill="#F7EBC2" stroke="#FFFFFF" stroke-width="1.2"{ds()}/><circle cx="{n(cx + 4)}" cy="{n(cy - 5)}" r="15.5" fill="#43558C"/>'
        return o + "".join(H.glyph_text("Z", cx + 18 + k * 4, cy - 4 - k * 10, s, "#F1F5F9", spacing=0.3) for k, s in enumerate((6.5, 5.2, 4.2)))
    if kind == "heart":
        return (f'<path d="M{n(cx)} {n(cy + 18)} C{n(cx - 30)} {n(cy - 2)} {n(cx - 20)} {n(cy - 26)} {n(cx)} {n(cy - 12)} C{n(cx + 20)} {n(cy - 26)} {n(cx + 30)} {n(cy - 2)} {n(cx)} {n(cy + 18)} Z" fill="{RED}" stroke="#7F1D1D" stroke-width="1.8"{ds()}/>'
                f'<path d="M{n(cx)} {n(cy - 12)} l-5 9 l7 6 l-5 8 l3 7" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
    if kind == "headset":
        return (f'<path d="M{n(cx - 20)} {n(cy + 6)} v-6 a20 20 0 0 1 40 0 v6" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"{ds()}/>'
                f'<rect x="{n(cx - 27)}" y="{n(cy)}" width="13" height="22" rx="5" fill="{SLATE}"/><rect x="{n(cx + 14)}" y="{n(cy)}" width="13" height="22" rx="5" fill="{SLATE}"/>'
                f'<path d="M{n(cx - 20)} {n(cy + 20)} q4 12 20 12" fill="none" stroke="{INK}" stroke-width="2.4"/><circle cx="{n(cx + 2)}" cy="{n(cy + 32)}" r="4" fill="{INK}"/>')
    if kind == "env":
        o = (f'<path d="M{n(cx - 40)} {n(cy + 22)} L{n(cx - 14)} {n(cy - 8)} L{n(cx)} {n(cy + 8)} L{n(cx + 12)} {n(cy - 2)} L{n(cx + 40)} {n(cy + 22)} Z" fill="#A8A29E" stroke="#57534E" stroke-width="1.8" stroke-linejoin="round"/>'
             f'<circle cx="{n(cx + 22)}" cy="{n(cy - 18)}" r="10" fill="#FBBF24" stroke="#FFFFFF" stroke-width="1.2"/>')
        o += f'<path d="M{n(cx - 34)} {n(cy - 12)} a8 8 0 0 1 10 -10 a10 10 0 0 1 18 2 a7 7 0 0 1 4 13 h-30 a6 6 0 0 1 -2 -5 Z" fill="#FFFFFF" stroke="#94A3B8" stroke-width="1.4"{ds()}/>'
        return o
    if kind == "calendar":
        o = (f'<rect x="{n(cx - 17)}" y="{n(cy - 16)}" width="34" height="34" rx="4" fill="#FFFFFF" stroke="{SLATE}" stroke-width="2.2"{ds()}/><rect x="{n(cx - 17)}" y="{n(cy - 16)}" width="34" height="9" rx="3" fill="{RED}"/>')
        for r in range(3):
            for c in range(3):
                o += f'<rect x="{n(cx - 11 + c * 8)}" y="{n(cy - 3 + r * 6.5)}" width="5" height="4" fill="{SLATE}" fill-opacity="{0.9 if (r, c) == (1, 1) else 0.35}"/>'
        for sg in (-1, 1):
            o += f'<line x1="{n(cx + sg * 44)}" y1="{n(cy)}" x2="{n(cx + sg * 26)}" y2="{n(cy)}" stroke="{RED}" stroke-width="4" stroke-linecap="round"/><path d="M{n(cx + sg * 21)} {n(cy)} L{n(cx + sg * 29)} {n(cy - 6)} L{n(cx + sg * 29)} {n(cy + 6)} Z" fill="{RED}"/>'
        return o
    return ""


def row1():
    o = ""
    for i, (ch, kind, tone) in enumerate((("I", "thermo", "red"), ("M", "capsule", "blue"), ("S", "squeeze", "slate"), ("A", "glass", "sand"), ("F", "moon", "night"), ("E", "heart", "red"))):
        x = X1[i]
        o += R.tile(f"{U}a{i}", x, Y1, W1, H1, tone) + letter(ch, x + W1 / 2, Y1, BLUE) + icon(kind, x + W1 / 2, Y1 + 76)
    return o


def row2():
    o = ""
    for i, (ch, kind, tone) in enumerate((("P", "headset", "slate"), ("A", "plane", "blue"), ("V", "env", "sand"), ("E", "calendar", "red"))):
        x = X2[i]
        o += R.tile(f"{U}b{i}", x, Y2, W2, H2, tone) + letter(ch, x + W2 / 2, Y2, GREEN) + icon(kind, x + W2 / 2, Y2 + 74)
    return o


def sprites():
    return [A.plane(X2[1] + W2 / 2, Y2 + 76, 50.0, name="sprite-top", angle=0.0)]


def callouts():
    c = S.callout
    return c(1, X1[0] + 14, Y1 + 14, r=9.5) + c(2, X2[0] + 14, Y2 + 14, r=9.5) + c(3, X2[3] + 14, Y2 + 14, r=9.5)


def layers():
    return [H.defs(U, W, HT), background(), row1(), row2(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-24-03-checklists",
        "replaces": "fig-24-03-checklists.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-24-03-checklists.jpg",
        "caption": "Figure 24-3. Checklists for finding hazards: IMSAFE for the pilot, PAVE for the whole flight",
        "desc": ("Figure 24-3. Checklists for finding hazards. IMSAFE, six tiles: Illness, Medication, Stress, Alcohol, Fatigue, Emotion. PAVE, four tiles: Pilot in command, Aircraft, enVironment, External pressures. "
                 "Both are FAA teaching aids, not GACAR requirements."),
        "legend": [
            "IMSAFE, before each flight: Illness, Medication, Stress, Alcohol, Fatigue, Emotion. An FAA teaching aid, not a GACAR requirement; behind it stands the rule of section 91.3(d).",
            "PAVE, the whole flight: Pilot in command, Aircraft, enVironment, External pressures.",
            "External pressures can make you ignore every other risk factor. Decide before the pressure arrives: allow time for a delay, have another way to get there, and tell people in advance that the flight may not go.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
