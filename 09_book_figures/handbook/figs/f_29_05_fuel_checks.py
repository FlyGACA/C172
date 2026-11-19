"""Figure 29-5 (new). The fuel check of Chapter 29, "Fuel checks", on the chapter's own worked example ("Fuel at checkpoint 2"): takeoff with 146 L; the climb of 13 min at 40 L/h uses 8.7 L; the cruise of 15 min at 30 L/h
uses 7.5 L; about 130 L are left (146 - 8.7 - 7.5 = 129.8); B needs 12 L, plus the 15 L final reserve.

Above: a scene of the leg (the runway at A, checkpoint 2 with a flag, the aeroplane in the cruise, the runway at B). Below: the fuel at takeoff as one bar of litres to scale (146 L = 600 units), cut into what was used (16.2 L,
the climb and the cruise), what the flight to B still needs (12 L), the final reserve (15 L) and the margin (103 L, the rest of the 130 L). Digits, L and the plus sign; the words are in the legend. The numbers are those of the chapter."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "ar29f"
INK, BLUE, GREEN, AMBER, RED, GREY = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#94A3B8"
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
PX, PY, PW, PH = 12.0, 12.0, 616.0, 140.0
BX0, BX1, BY, BH = 20.0, 620.0, 214.0, 44.0
K = (BX1 - BX0) / 146.0                                      # units per litre
USED, MARGIN, TOB, RES = 16.2, 103.0, 12.0, 15.0
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def scene():
    uid = f"{U}p"
    hz = PY + 58.0
    strips = (f'<rect x="{n(PX + 18)}" y="{n(hz + 38)}" width="64" height="9" rx="2" fill="#5B6577"/><line x1="{n(PX + 24)}" y1="{n(hz + 42.5)}" x2="{n(PX + 76)}" y2="{n(hz + 42.5)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="7 5"/>'
              f'<rect x="{n(PX + PW - 82)}" y="{n(hz + 38)}" width="64" height="9" rx="2" fill="#5B6577"/><line x1="{n(PX + PW - 76)}" y1="{n(hz + 42.5)}" x2="{n(PX + PW - 24)}" y2="{n(hz + 42.5)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="7 5"/>')
    flag = (f'<line x1="{n(PX + 308)}" y1="{n(hz + 44)}" x2="{n(PX + 308)}" y2="{n(hz + 6)}" stroke="#44403C" stroke-width="2.6"/>'
            f'<path d="M{n(PX + 308)} {n(hz + 6)} L{n(PX + 334)} {n(hz + 14)} L{n(PX + 308)} {n(hz + 22)} Z" fill="{RED}" stroke="#7F1D1D" stroke-width="1"/>')
    route = S.ribbon(f"{U}r", [(PX + 60, hz + 14), (PX + 160, hz + 6), (PX + 300, hz + 2), (PX + 420, hz + 8), (PX + 548, hz + 16)], 4.6, "#2FA35A", "#9BE0B2", opacity=0.6, head=2.0, tail=0.5, per=8)
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-5%" y="-10%" width="110%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", PX, PY, PW, PH, DAY) + S.plain(f"{U}g", PX, PX + PW, hz, PY + PH, seed=5, tone="day", acacias=((PX + 150, hz + 34, 0.8), (PX + 470, hz + 36, 0.8)), photo=True)
            + strips + flag + route + '</g>' + f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def pill(cx, cy, w, text, fill="#1F2937", height=13.0):
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - height / 2 - 3)}" width="{n(w)}" height="{n(height + 6)}" rx="{n((height + 6) / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.4"/>'
            + H.glyph_text(text, cx, cy, height, fill="#FFFFFF"))


def bar():
    x = BX0
    segs = []
    for width_l, col, label in ((USED, GREY, "16.2"), (MARGIN, "#2FA35A", "103"), (TOB, "#2563EB", "12"), (RES, "#F59E0B", "15")):
        w = width_l * K
        segs.append((x, w, col, label))
        x += w
    uid = f"{U}b"
    out = [f'<defs><clipPath id="{uid}c"><rect x="{n(BX0)}" y="{n(BY)}" width="{n(BX1 - BX0)}" height="{n(BH)}" rx="10"/></clipPath>'
           f'<filter id="{uid}s" x="-5%" y="-20%" width="110%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
           f'<rect x="{n(BX0)}" y="{n(BY)}" width="{n(BX1 - BX0)}" height="{n(BH)}" rx="10" fill="#FFFFFF" filter="url(#{uid}s)"/><g clip-path="url(#{uid}c)">']
    for sx, sw, col, label in segs:
        out.append(f'<rect x="{n(sx)}" y="{n(BY)}" width="{n(sw)}" height="{n(BH)}" fill="{col}"/><rect x="{n(sx)}" y="{n(BY)}" width="{n(sw)}" height="{n(BH * 0.38)}" fill="#FFFFFF" fill-opacity="0.22"/>'
                   f'<line x1="{n(sx)}" y1="{n(BY)}" x2="{n(sx)}" y2="{n(BY + BH)}" stroke="#FFFFFF" stroke-width="1.6"/>')
        out.append(H.glyph_text(label, sx + sw / 2, BY + BH / 2 + 0.5, 15.0, fill="#FFFFFF"))
    out.append('</g>')
    out.append(f'<rect x="{n(BX0)}" y="{n(BY)}" width="{n(BX1 - BX0)}" height="{n(BH)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>')
    # the 130 L bracket and the 146 L at takeoff
    bx0 = segs[1][0]
    out.append(f'<path d="M{n(bx0)} {n(BY - 6)} L{n(bx0)} {n(BY - 14)} L{n(BX1)} {n(BY - 14)} L{n(BX1)} {n(BY - 6)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(pill((bx0 + BX1) / 2, BY - 28, 62.0, "130 L"))
    out.append(f'<path d="M{n(BX0)} {n(BY + BH + 6)} L{n(BX0)} {n(BY + BH + 14)} L{n(BX1)} {n(BY + BH + 14)} L{n(BX1)} {n(BY + BH + 6)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(pill((BX0 + BX1) / 2, BY + BH + 28, 62.0, "146 L"))
    return "".join(out), segs


def callouts(segs):
    c = S.callout
    return (c(1, 30.0, 188.0, BX0 + 3.0, BY - 2.0, r=10.5) + c(2, segs[0][0] + segs[0][1] / 2 + 12, BY + BH + 30.0, segs[0][0] + segs[0][1] / 2, BY + BH - 2.0, r=10.5)
            + c(3, segs[1][0] + 40.0, BY - 28.0, segs[1][0] + 8.0, BY - 12.0, r=10.5) + c(4, segs[3][0] + segs[3][1] - 44.0, BY + BH + 30.0, segs[3][0] + segs[3][1] - 40.0, BY + BH - 2.0, r=10.5))


def sprites():
    return [{"name": "sprite-side", "at": [PX + 310, PY + 52], "width": 60, "outline": OUT, "shadow": SHADOW}]


def layers():
    b, segs = bar()
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="300" fill="#ffffff"/>', scene(), *sprites(), b, callouts(segs)]


def plate():
    return {
        "id": "fig-29-05-fuel-checks",
        "replaces": "fig-29-05-fuel-checks.svg",             # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-29-05-fuel-checks.jpg",
        "caption": "Figure 29-5. A fuel check at checkpoint 2: the fuel at takeoff, what has been used, what is left and what the flight to B still needs",
        "desc": ("Figure 29-5. A fuel check at checkpoint 2 on the chapter's worked example, as one bar of litres to scale: 146 L at takeoff, 16.2 L used in the climb and the cruise, about 130 L left, "
                 "of which 12 L are needed to reach B and 15 L are the final reserve, with a margin of about 103 L."),
        "legend": [
            "Fuel at takeoff: 146 L in this example.",
            "Used so far: the climb (13 min at 40 L/h, 8.7 L) and the cruise (15 min at 30 L/h, 7.5 L), 16.2 L in all.",
            "About 130 L are left at checkpoint 2, and the gauges agree. When the gauges and the calculation disagree, plan on the lower figure until you know why.",
            "B needs 12 L, plus the 15 L final reserve: the rest of the 130 L, about 103 L, is a wide margin. The usable fuel must never fall below the fuel to reach an aerodrome where a safe landing can be made with the planned final reserve remaining.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
