"""Figure 2-1 (new). Documents on board: the eight items of GACAR 91.9(a) as eight tiles, each with a small drawing of the document and its number (the same order as the chapter's list).

1 certificate of registration (page with a seal), 2 airworthiness certificate (page with a tick), 3 aircraft radio station licence (page with a mast and waves), 4 list of passengers with origin and destination (people and an arrow),
5 manifest and declaration of cargo (a box on a page), 6 flight logbook (a book), 7 agreement under Article 83 bis (two pages joined by a double arrow), 8 essential search and rescue information (a map with search rings).
No words but SAR: shapes and the numbers of the callouts. The drawings are generic, not copies of any form."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 236
U = "dc2"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
TW, TH = 142.0, 98.0
GX = (20.0, 175.0, 330.0, 485.0)
GY = (16.0, 126.0)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def tile(i):
    x, y = GX[i % 4], GY[i // 4]
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="#EEF2F7" stroke="#CBD5E1" stroke-width="1.2"/>'


def page(x, y, w=44.0, h=58.0, lines=3, fill="#FFFFFF"):
    out = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="3" fill="{fill}" stroke="{SLATE}" stroke-width="1.4" filter="url(#{U}ds)"/>'
    for k in range(lines):
        out += f'<line x1="{n(x + 6)}" y1="{n(y + h - 10 - k * 7)}" x2="{n(x + w - 6)}" y2="{n(y + h - 10 - k * 7)}" stroke="#94A3B8" stroke-width="1.6" stroke-linecap="round"/>'
    return out


def person(x, y, c=SLATE, r=3.6):
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{c}"/><path d="M{n(x - r * 1.5)} {n(y + r * 3.2)} Q{n(x)} {n(y + r * 0.6)} {n(x + r * 1.5)} {n(y + r * 3.2)} Z" fill="{c}"/>'


def icon(i):
    cx = GX[i % 4] + TW / 2
    cy = GY[i // 4] + TH / 2 + 4
    o = []
    if i == 0:                                           # certificate of registration: page, seal and ribbon
        o.append(page(cx - 24, cy - 32, 48, 62, 2))
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="9" fill="{AMBER}" stroke="#FFFFFF" stroke-width="1.4"/><path d="M{n(cx - 5)} {n(cy)} L{n(cx - 8)} {n(cy + 11)} L{n(cx)} {n(cy + 7)} L{n(cx + 8)} {n(cy + 11)} L{n(cx + 5)} {n(cy)} Z" fill="{AMBER}"/>')
    elif i == 1:                                         # airworthiness certificate: page with a tick
        o.append(page(cx - 24, cy - 32, 48, 62, 2))
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="11" fill="{GREEN}" stroke="#FFFFFF" stroke-width="1.4"/><path d="M{n(cx - 5.5)} {n(cy - 7.5)} L{n(cx - 1.5)} {n(cy - 3.5)} L{n(cx + 6)} {n(cy - 12)}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    elif i == 2:                                         # radio station licence: page, mast and waves
        o.append(page(cx - 24, cy - 32, 48, 62, 1))
        o.append(f'<line x1="{n(cx)}" y1="{n(cy - 2)}" x2="{n(cx)}" y2="{n(cy - 20)}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy - 22)}" r="2.6" fill="{BLUE}"/>')
        for r in (7, 12):
            o.append(f'<path d="M{n(cx - r)} {n(cy - 22 - r * 0.7)} A{n(r)} {n(r)} 0 0 0 {n(cx - r)} {n(cy - 22 + r * 0.7)}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-linecap="round"/>'
                     f'<path d="M{n(cx + r)} {n(cy - 22 - r * 0.7)} A{n(r)} {n(r)} 0 0 1 {n(cx + r)} {n(cy - 22 + r * 0.7)}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-linecap="round"/>')
    elif i == 3:                                         # passenger list: page with people and an arrow from origin to destination
        o.append(page(cx - 28, cy - 32, 56, 62, 0))
        for k in range(3):
            o.append(person(cx - 16 + k * 16, cy - 22))
        o.append(f'<circle cx="{n(cx - 17)}" cy="{n(cy + 6)}" r="3.2" fill="{GREEN}"/><circle cx="{n(cx + 17)}" cy="{n(cy + 6)}" r="3.2" fill="{RED}"/><line x1="{n(cx - 12)}" y1="{n(cy + 6)}" x2="{n(cx + 8)}" y2="{n(cy + 6)}" stroke="{SLATE}" stroke-width="1.8"/><path d="M{n(cx + 12)} {n(cy + 6)} L{n(cx + 6)} {n(cy + 2.4)} L{n(cx + 6)} {n(cy + 9.6)} Z" fill="{SLATE}"/>')
        o.append(f'<line x1="{n(cx - 20)}" y1="{n(cy + 18)}" x2="{n(cx + 20)}" y2="{n(cy + 18)}" stroke="#94A3B8" stroke-width="1.6" stroke-linecap="round"/>')
    elif i == 4:                                         # cargo manifest: a box and a page
        o.append(page(cx - 38, cy - 32, 40, 54, 3))
        o.append(f'<path d="M{n(cx - 4)} {n(cy - 6)} L{n(cx + 12)} {n(cy - 14)} L{n(cx + 34)} {n(cy - 6)} L{n(cx + 34)} {n(cy + 18)} L{n(cx + 12)} {n(cy + 26)} L{n(cx - 4)} {n(cy + 18)} Z" fill="#C8A26B" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 4)} {n(cy - 6)} L{n(cx + 12)} {n(cy + 2)} L{n(cx + 34)} {n(cy - 6)} M{n(cx + 12)} {n(cy + 2)} L{n(cx + 12)} {n(cy + 26)}" fill="none" stroke="{SLATE}" stroke-width="1.2"/>')
    elif i == 5:                                         # flight logbook: a closed book with a ribbon and a table
        o.append(f'<rect x="{n(cx - 30)}" y="{n(cy - 30)}" width="60" height="58" rx="4" fill="#1E3A8A" stroke="#0F172A" stroke-width="1.4" filter="url(#{U}ds)"/>'
                 f'<rect x="{n(cx - 30)}" y="{n(cy - 30)}" width="9" height="58" rx="3" fill="#172554"/>'
                 f'<rect x="{n(cx - 15)}" y="{n(cy - 20)}" width="38" height="26" rx="2" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>'
                 f'<line x1="{n(cx - 15)}" y1="{n(cy - 11)}" x2="{n(cx + 23)}" y2="{n(cy - 11)}" stroke="#94A3B8" stroke-width="1"/><line x1="{n(cx - 15)}" y1="{n(cy - 2)}" x2="{n(cx + 23)}" y2="{n(cy - 2)}" stroke="#94A3B8" stroke-width="1"/><line x1="{n(cx + 4)}" y1="{n(cy - 20)}" x2="{n(cx + 4)}" y2="{n(cy + 6)}" stroke="#94A3B8" stroke-width="1"/>')
    elif i == 6:                                         # agreement under Article 83 bis: two pages joined by a double arrow
        o.append(page(cx - 50, cy - 26, 34, 48, 2))
        o.append(page(cx + 16, cy - 26, 34, 48, 2))
        o.append(f'<line x1="{n(cx - 12)}" y1="{n(cy - 2)}" x2="{n(cx + 12)}" y2="{n(cy - 2)}" stroke="{BLUE}" stroke-width="2.6"/>'
                 f'<path d="M{n(cx - 16)} {n(cy - 2)} L{n(cx - 9)} {n(cy - 7)} L{n(cx - 9)} {n(cy + 3)} Z M{n(cx + 16)} {n(cy - 2)} L{n(cx + 9)} {n(cy - 7)} L{n(cx + 9)} {n(cy + 3)} Z" fill="{BLUE}"/>')
    else:                                                # search and rescue information: a map with search rings
        o.append(f'<path d="M{n(cx - 40)} {n(cy - 24)} L{n(cx - 14)} {n(cy - 30)} L{n(cx + 14)} {n(cy - 24)} L{n(cx + 40)} {n(cy - 30)} L{n(cx + 40)} {n(cy + 24)} L{n(cx + 14)} {n(cy + 30)} L{n(cx - 14)} {n(cy + 24)} L{n(cx - 40)} {n(cy + 30)} Z" fill="#E2E8D0" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round" filter="url(#{U}ds)"/>'
                 f'<line x1="{n(cx - 14)}" y1="{n(cy - 30)}" x2="{n(cx - 14)}" y2="{n(cy + 24)}" stroke="#94A3B8" stroke-width="1"/><line x1="{n(cx + 14)}" y1="{n(cy - 24)}" x2="{n(cx + 14)}" y2="{n(cy + 30)}" stroke="#94A3B8" stroke-width="1"/>')
        for r in (7, 14, 21):
            o.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 2.4"/>')
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="3" fill="{RED}"/>')
        o.append(H.glyph_text("SAR", cx, cy - 36, 6.0, RED, spacing=0.4))
    return "".join(o)


def callouts():
    c = S.callout
    out = []
    for i in range(8):
        x, y = GX[i % 4], GY[i // 4]
        out.append(c(i + 1, x + 14, y + 14, r=9.0))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), *[tile(i) for i in range(8)], *[icon(i) for i in range(8)], callouts()]


def plate():
    return {
        "id": "fig-02-01-documents-on-board",
        "replaces": "fig-02-01-documents-on-board.svg",     # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-01-documents-on-board.jpg",
        "caption": "Figure 2-1. Documents on board a Saudi-registered aircraft: the eight items of GACAR 91.9(a)",
        "desc": ("Figure 2-1. Documents on board a Saudi-registered aircraft: the eight items of GACAR 91.9(a), as eight tiles in the order of the chapter's list: certificate of registration, airworthiness certificate, "
                 "radio station licence, passenger list, cargo manifest, flight logbook, Article 83 bis agreement and search and rescue information."),
        "legend": [
            "The certificate of registration (original or true copy).",
            "The airworthiness certificate, including the noise characteristics and certifications.",
            "The aircraft radio station licence.",
            "A list of passengers with their places of origin and destination.",
            "A manifest and declaration of any cargo.",
            "The flight logbook.",
            "For an aircraft under an Article 83 bis agreement, a copy or approved summary of that agreement.",
            "The essential search and rescue information for the area to be flown.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
