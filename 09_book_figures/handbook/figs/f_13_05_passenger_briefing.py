"""Figure 13-5 (new; redrawn in the upgrade round around a cutaway render of the model's cabin). The passenger briefing of GACAR 91.45(a) and (b).

The cabin of the model from above and behind, the skin, the roof, the left door and the wings taken away, a fire extinguisher (a red cylinder, which the model lacks) on the floor between the seats:
2 the lap belts and shoulder harnesses, 3 a seat back, 4 the fire extinguisher, 5 the door and its handle, 6 the baggage area behind the rear seat where survival equipment is stowed. At the right, four small tiles
for what the cabin cannot show: 1 smoking (a crossed cigarette), 7 ditching (a lifebuoy on waves), 8 oxygen (a cylinder marked O2 and a mask) and 9 the briefing in Arabic and English (two bubbles, AR and EN)."""
import math

from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 400
U = "pb13"
INK, SLATE, BLUE, GREEN, AMBER, RED, ORANGE = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#EA580C"
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
    return R.tile(f"{U}t{i}", x, y, TW, TH, ("red", "blue", "slate", "red", "green", "sand", "blue", "slate")[i])


def icon(i):
    cx = GX[i % 4] + TW / 2 + 6
    cy = GY[i // 4] + TH / 2 + 4
    o = []
    if i == 0:                                           # smoking: a cigarette in a red crossed circle
        o.append(f'<rect x="{n(cx - 26)}" y="{n(cy - 4)}" width="40" height="8" rx="2" fill="#F8FAFC" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(cx + 8)}" y="{n(cy - 4)}" width="6" height="8" fill="#F59E0B"/><rect x="{n(cx - 26)}" y="{n(cy - 4)}" width="8" height="8" rx="2" fill="#C8A26B"/>'
                 f'<path d="M{n(cx + 18)} {n(cy - 4)} q4 -6 0 -10 q-4 -4 0 -8" fill="none" stroke="#94A3B8" stroke-width="1.8" stroke-linecap="round"/>')
        o.append(f'<circle cx="{n(cx - 2)}" cy="{n(cy)}" r="30" fill="none" stroke="{RED}" stroke-width="4.4"/><line x1="{n(cx - 23)}" y1="{n(cy + 21)}" x2="{n(cx + 19)}" y2="{n(cy - 21)}" stroke="{RED}" stroke-width="4.4" stroke-linecap="round"/>')
    elif i == 1:                                         # safety belt and harness: a lap belt with a buckle and a shoulder strap
        o.append(f'<path d="M{n(cx - 38)} {n(cy + 14)} L{n(cx - 6)} {n(cy + 14)} M{n(cx + 6)} {n(cy + 14)} L{n(cx + 38)} {n(cy + 14)}" stroke="{INK}" stroke-width="9" stroke-linecap="butt" fill="none"/>'
                 f'<path d="M{n(cx - 22)} {n(cy - 30)} L{n(cx)} {n(cy + 12)}" stroke="#1E3A8A" stroke-width="8" stroke-linecap="butt" fill="none"/>')
        o.append(f'<rect x="{n(cx - 11)}" y="{n(cy + 5)}" width="22" height="18" rx="3" fill="#E2E8F0" stroke="{SLATE}" stroke-width="1.6" filter="url(#{U}ds)"/><rect x="{n(cx - 4)}" y="{n(cy + 10)}" width="8" height="8" rx="1.5" fill="{RED}"/>')
    elif i == 2:                                         # seat backs: a seat in profile with the back upright and a dashed arc where it was reclined
        o.append(f'<path d="M{n(cx - 30)} {n(cy + 26)} L{n(cx - 30)} {n(cy + 8)} L{n(cx + 18)} {n(cy + 8)} L{n(cx + 18)} {n(cy + 26)} Z" fill="#64748B" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 30)} {n(cy - 30)}" stroke="{SLATE}" stroke-width="12" stroke-linecap="round"/><path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 30)} {n(cy - 30)}" stroke="#94A3B8" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 58)} {n(cy - 22)}" stroke="{SLATE}" stroke-width="2" stroke-dasharray="4 3" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 52)} {n(cy - 6)} Q{n(cx - 44)} {n(cy - 20)} {n(cx - 36)} {n(cy - 22)}" fill="none" stroke="{GREEN}" stroke-width="2.6" stroke-linecap="round"/><path d="M{n(cx - 34)} {n(cy - 22)} L{n(cx - 42)} {n(cy - 25)} L{n(cx - 40)} {n(cy - 16)} Z" fill="{GREEN}"/>')
    elif i == 3:                                         # fire extinguisher
        o.append(f'<rect x="{n(cx - 13)}" y="{n(cy - 12)}" width="26" height="42" rx="8" fill="{RED}" stroke="#7F1D1D" stroke-width="1.4" filter="url(#{U}ds)"/><rect x="{n(cx - 6)}" y="{n(cy - 20)}" width="12" height="10" rx="2" fill="{INK}"/>'
                 f'<path d="M{n(cx + 6)} {n(cy - 16)} L{n(cx + 24)} {n(cy - 16)} L{n(cx + 26)} {n(cy - 4)}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx - 6)} {n(cy - 20)} L{n(cx - 22)} {n(cy - 24)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
                 f'<rect x="{n(cx - 8)}" y="{n(cy + 2)}" width="16" height="12" rx="2" fill="#FFFFFF" fill-opacity="0.9"/>')
    elif i == 4:                                         # doors and emergency exits: a door ajar and an arrow out
        o.append(f'<rect x="{n(cx - 30)}" y="{n(cy - 30)}" width="34" height="56" rx="3" fill="{GREEN}" stroke="#14532D" stroke-width="1.6" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 30)} {n(cy - 30)} L{n(cx - 52)} {n(cy - 22)} L{n(cx - 52)} {n(cy + 32)} L{n(cx - 30)} {n(cy + 26)} Z" fill="#166534" stroke="#14532D" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<line x1="{n(cx - 2)}" y1="{n(cy)}" x2="{n(cx + 36)}" y2="{n(cy)}" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/><path d="M{n(cx + 44)} {n(cy)} L{n(cx + 32)} {n(cy - 9)} L{n(cx + 32)} {n(cy + 9)} Z" fill="{GREEN}"/>')
    elif i == 5:                                         # survival equipment: a box with a cross and a bottle
        o.append(f'<rect x="{n(cx - 34)}" y="{n(cy - 18)}" width="52" height="42" rx="5" fill="{ORANGE}" stroke="#9A3412" stroke-width="1.6" filter="url(#{U}ds)"/><rect x="{n(cx - 20)}" y="{n(cy - 26)}" width="24" height="9" rx="3" fill="none" stroke="#9A3412" stroke-width="2.4"/>'
                 f'<path d="M{n(cx - 8)} {n(cy - 8)} h8 v8 h8 v8 h-8 v8 h-8 v-8 h-8 v-8 h8 Z" fill="#FFFFFF" transform="translate(-2 -2)"/>'
                 f'<rect x="{n(cx + 24)}" y="{n(cy - 2)}" width="14" height="26" rx="4" fill="#38BDF8" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(cx + 27)}" y="{n(cy - 8)}" width="8" height="7" fill="{SLATE}"/>')
    elif i == 6:                                         # ditching: waves and a lifebuoy
        o.append(f'<path d="M{n(cx - 48)} {n(cy + 22)} q8 -9 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="{BLUE}" stroke-width="3.4" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 48)} {n(cy + 32)} q8 -9 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="#60A5FA" stroke-width="3" stroke-linecap="round"/>')
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="22" fill="none" stroke="#FFFFFF" stroke-width="15"/><circle cx="{n(cx)}" cy="{n(cy - 8)}" r="22" fill="none" stroke="{ORANGE}" stroke-width="12" filter="url(#{U}ds)"/>')
        for k in range(4):
            a0 = math.radians(45 + 90 * k - 14)
            a1 = math.radians(45 + 90 * k + 14)
            o.append(f'<path d="M{n(cx + 22 * math.cos(a0))} {n(cy - 8 + 22 * math.sin(a0))} A22 22 0 0 1 {n(cx + 22 * math.cos(a1))} {n(cy - 8 + 22 * math.sin(a1))}" fill="none" stroke="#FFFFFF" stroke-width="12"/>')
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="28" fill="none" stroke="#9A3412" stroke-width="1.2"/><circle cx="{n(cx)}" cy="{n(cy - 8)}" r="16" fill="none" stroke="#9A3412" stroke-width="1.2"/>')
    else:                                                # oxygen equipment: a cylinder marked O2 and a mask
        o.append(f'<rect x="{n(cx - 12)}" y="{n(cy - 18)}" width="24" height="46" rx="9" fill="#16A34A" stroke="#14532D" stroke-width="1.4" filter="url(#{U}ds)"/><rect x="{n(cx - 5)}" y="{n(cy - 26)}" width="10" height="9" rx="2" fill="{INK}"/>')
        o.append(H.glyph_text("O2", cx, cy + 8, 6.0, "#FFFFFF", spacing=0.3))
        o.append(f'<path d="M{n(cx + 12)} {n(cy - 22)} Q{n(cx + 28)} {n(cy - 20)} {n(cx + 30)} {n(cy - 4)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
                 f'<path d="M{n(cx + 22)} {n(cy - 4)} Q{n(cx + 30)} {n(cy - 12)} {n(cx + 40)} {n(cy - 4)} Q{n(cx + 40)} {n(cy + 10)} {n(cx + 30)} {n(cy + 12)} Q{n(cx + 22)} {n(cy + 8)} {n(cx + 22)} {n(cy - 4)} Z" fill="#E2E8F0" stroke="{SLATE}" stroke-width="1.4"/>')
    return "".join(o)


import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CX, CY, CW, CH = 12.0, 12.0, 448.0, 376.0                      # the card of the cabin
SX, SW = 472.0, 156.0                                           # the column of small tiles
SH = (CH - 3 * 10.0) / 4


def cabin():
    with open(os.path.join(HERE, "renders", "cabin-13-05-briefing.anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    (pw, ph), a = d["size"], d["anchors"]
    w = CW * 1.02
    h = w * ph / pw
    x0, y0 = CX + CW / 2 - w / 2, CY + CH / 2 - h / 2 + 6
    at = lambda k: (x0 + a[k][0] * w, y0 + a[k][1] * h)
    card = (f'<defs>{S.gradient(U + "cg", [(0, "#DCE7F3"), (1, "#F4F7FB")])}<clipPath id="{U}cc"><rect x="{n(CX)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" rx="10"/></clipPath>'
            f'<filter id="{U}cf" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.26"/></filter></defs>'
            f'<rect x="{n(CX)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" rx="10" fill="url(#{U}cg)" filter="url(#{U}cf)"/><g clip-path="url(#{U}cc)">')
    lay = {"name": "cabin-13-05-briefing", "at": [x0 + w / 2, y0 + h / 2], "width": w, "shadow": {"dx": 1.5, "dy": 3.0, "blur": 3.0, "opacity": 0.28}}
    end = f'</g><rect x="{n(CX)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    return [card, lay, end], at


def small(k, i):
    """Tile k of the column (0 to 3) with the drawing of subject i of the old figure, moved and scaled into it."""
    x, y = SX, CY + k * (SH + 10.0)
    o = R.tile(f"{U}s{k}", x, y, SW, SH, ("red", "blue", "slate", "sand")[k])
    if i is None:
        return o
    ox, oy = GX[i % 4] + TW / 2 + 6, GY[i // 4] + TH / 2 + 4
    sc = 0.9
    return o + f'<g transform="translate({n(x + SW / 2 + 8 - ox * sc)} {n(y + SH / 2 + 4 - oy * sc)}) scale({sc})">' + icon(i) + "</g>"


def bubbles():
    """The rule of 91.45(b): the oral briefing in Arabic and in English, two speech bubbles side by side."""
    x, y = SX, CY + 3 * (SH + 10.0)
    out = [small(3, None)]
    yc = y + SH / 2 + 2
    for bx, label, col in ((x + 46, "AR", GREEN), (x + 114, "EN", BLUE)):
        out.append(f'<path d="M{n(bx - 22)} {n(yc - 16)} h44 a8 8 0 0 1 8 8 v16 a8 8 0 0 1 -8 8 h-28 l-10 10 v-10 h-6 a8 8 0 0 1 -8 -8 v-16 a8 8 0 0 1 8 -8 Z" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round" filter="url(#{U}ds)"/>')
        out.append(H.glyph_text(label, bx + 4, yc - 1, 10.0, "#FFFFFF", spacing=0.6))
    return "".join(out)


def callouts(at):
    c = S.callout
    out = []
    for k, (num, anchor, pos) in enumerate(((2, "belt", (CX + 40, CY + 252)), (3, "back", (CX + 250, CY + 26)), (4, "ext", (CX + 196, CY + 330)),
                                            (5, "door_in", (CX + 330, CY + 26)), (6, "net", (CX + 410, CY + 330)))):
        tx, ty = at(anchor)
        dx, dy = {"ext": (26.0, 14.0), "door_in": (52.0, -36.0)}.get(anchor, (0.0, 0.0))     # the extinguisher's middle; the frame of the right door
        tx, ty = tx + dx, ty + dy
        out.append(c(num, pos[0], pos[1], tx, ty, r=10.0))
    for k, num in enumerate((1, 7, 8, 9)):
        out.append(c(num, SX + 14, CY + k * (SH + 10.0) + 14, r=9.0))
    return "".join(out)


def layers():
    cab, at = cabin()
    return ([H.defs(U, W, HT), background()] + cab + [small(0, 0), small(1, 6), small(2, 7), bubbles(), callouts(at)])


def plate():
    return {
        "id": "fig-13-05-passenger-briefing",
        "replaces": "fig-13-05-passenger-briefing.svg",   # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-13-05-passenger-briefing.jpg",
        "caption": "Figure 13-5. The passenger briefing of GACAR 91.45: the eight subjects, and the briefing in Arabic and English",
        "desc": ("Figure 13-5. The passenger briefing of GACAR 91.45: the eight subjects as eight tiles (smoking, safety belts and harnesses, seat backs, fire extinguishers, doors and emergency exits, "
                 "survival equipment, ditching, oxygen equipment), and the oral briefing in Arabic and in English."),
        "legend": [
            "Smoking.",
            "Safety belts and harnesses.",
            "Seat backs for takeoff and landing.",
            "The fire extinguishers.",
            "The doors and emergency exits.",
            "The survival equipment.",
            "Ditching, on a flight over water.",
            "Any oxygen equipment.",
            "The oral briefing is given in both Arabic and English, unless the person giving it has established that every passenger understands one language; printed cards may supplement it. It may be omitted when the PIC determines that the passengers already know its contents.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
