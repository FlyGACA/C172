"""Figure 26-1 (new; redrawn in the upgrade round with renders of the model). The flight manual, the school and the speed card, from the first section of Chapter 26.

1 the model's operating-limitations placard (its last two lines: operate in compliance with the operating limitations); 2 the model's airspeed indicator, the needle on 65 kt, with the chapter's example speeds tagged
where they fall on its own scale (VS0 45, VS1 52, VR 55, final 60 and 65, VX 62, VY 75, VFE 90); 3 the maximum demonstrated crosswind, 15 kt, across a runway seen from above; 4 the model's flap switch and its scale.
The model's flap scale reads to 40 degrees and the book's trainer stops at 30, so the 40 degree mark is covered. The speeds are those of the handbook's fictional trainer, indicated, at maximum mass, for learning only."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 400
U = "sc2601"
INK, SLATE, BLUE, GREEN, AMBER, RED, TEAL, VIOLET = "#1E293B", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#0F766E", "#7C3AED"
TX, TY0, TY1 = 300.0, 300.0, 40.0                         # the tape: x of the scale, y at 40 kt and at 95 kt


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.4, anchor="middle"):
    w = gwidth(text, size) + 14.0
    h = size + 8.0
    if anchor == "start":
        cx += w / 2
    elif anchor == "end":
        cx -= w / 2
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def ky(kt):
    return TY0 + (kt - 40.0) * (TY1 - TY0) / 55.0


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def anchors(name):
    with open(os.path.join(HERE, "renders", name + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    return d["size"], d["anchors"]


def placed(name, cx, cy, width):
    """A render laid on the canvas, its middle at (cx, cy), `width` canvas units across: the layer, and a function from its anchors to canvas points."""
    (pw, ph), a = anchors(name)
    h = width * ph / pw
    x0, y0 = cx - width / 2, cy - h / 2
    return {"name": name, "at": [cx, cy], "width": width}, (lambda k: (x0 + a[k][0] * width, y0 + a[k][1] * h)), (x0, y0, width, h)


def card_bg(uid, x, y, w, h, fill="#FFFFFF"):
    return (f'<defs><filter id="{uid}" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.26"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10" fill="{fill}" filter="url(#{uid})"/>')


def clip_open(uid, x, y, w, h, rx=10):
    return f'<defs><clipPath id="{uid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}"/></clipPath></defs><g clip-path="url(#{uid})">'


def rim(x, y, w, h, rx=10):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'


def leader(p, q, col):
    return (f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round"/>'
            f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{col}" stroke-width="2" stroke-linecap="round"/>'
            f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.4" fill="{col}" stroke="#FFFFFF" stroke-width="1.4"/>')


SPEEDS = [(45, "45 VS0", RED), (52, "52 VS1", RED), (55, "55 VR", BLUE), (60, "60 FINAL", TEAL), (62, "62 VX", GREEN), (65, "65 FINAL", TEAL), (75, "75 VY", GREEN), (90, "90 VFE", AMBER)]


def asi():
    """The model's own airspeed indicator, the needle on 65 kt, with the example speeds tagged where they fall on its scale."""
    x, y, w, h = 12.0, 12.0, 352.0, 376.0
    out = [card_bg(f"{U}c1", x, y, w, h, "#EEF2F7")]
    lay, at, _ = placed("dial-26-01-asi", 150, 200, 300)
    out.append(lay)
    ys, last = [], -99.0
    pts = [(at(f"v{v}"), lab, col) for v, lab, col in SPEEDS]
    for (px, py), lab, col in sorted(pts, key=lambda t: t[0][1]):     # a column of tags at the right, in the order the speeds fall down the dial
        ty = max(py, last + 24.0)
        last = ty
        ys.append(((px, py), ty, lab, col))
    shift = max(0.0, ys[-1][1] - (y + h - 18))                          # keep the column inside the card
    marks = ""
    for (px, py), ty, lab, col in ys:
        ty -= shift
        marks += leader((px, py), (x + w - 82, ty), col) + pill(x + w - 80, ty, lab, col, size=7.6, anchor="start")
    out.append(marks)
    return out


def placard():
    x, y, w = 376.0, 12.0, 252.0
    lay, _, (bx, by, bw, bh) = placed("panel-26-01-placard", x + w / 2, 0, w)
    lay["at"][1] = y + bh / 2
    return [card_bg(f"{U}c2", x, y, w, bh), clip_open(f"{U}k2", x, y, w, bh), lay, "</g>", rim(x, y, w, bh)], bh


def flaps(top):
    """The flap switch and its scale on the model's lower panel. The book's trainer has flap settings to 30 degrees: the model's 40 degree mark is covered."""
    x, y, w, h = 376.0, top, 128.0, 388.0 - top
    (pw, ph), a = anchors("panel-26-01-flaps")
    sw = w / 0.21                                                       # the window shows about a quarter of the picture's width
    sh = sw * ph / pw
    ind = a["ind"]
    cx = x + w * 0.42 + (0.5 - ind[0]) * sw
    cy = y + h * 0.42 + (0.5 - ind[1]) * sh
    lay = {"name": "panel-26-01-flaps", "at": [cx, cy], "width": sw}
    return [card_bg(f"{U}c3", x, y, w, h), clip_open(f"{U}k3", x, y, w, h), lay, "@@FLAPMASK@@", "</g>", rim(x, y, w, h)], (cx, cy, sw, sh)


def crosswind(top):
    x, y, w, h = 512.0, top, 116.0, 388.0 - top
    uid = f"{U}x"
    o = card_bg(f"{U}c4", x, y, w, h) + clip_open(f"{uid}k", x, y, w, h)
    o += f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="#E7D9B6"/>'
    cx = x + w / 2 + 8
    o += (f'<rect x="{n(cx - 15)}" y="{n(y - 4)}" width="30" height="{n(h + 8)}" fill="#5E6672"/>'
          + "".join(f'<rect x="{n(cx - 1.4)}" y="{n(y + 10 + k * 26)}" width="2.8" height="14" fill="#F1F5F9"/>' for k in range(int(h / 26)))
          + f'<rect x="{n(cx - 15)}" y="{n(y - 4)}" width="30" height="{n(h + 8)}" fill="none" stroke="#F1F5F9" stroke-width="1.2"/>')
    px, py = x + 18, y + 120                              # a windsock beside the runway, blowing across it
    o += (f'<line x1="{n(px)}" y1="{n(py - 6)}" x2="{n(px)}" y2="{n(py + 42)}" stroke="{INK}" stroke-width="2.2"/>'
          f'<path d="M{n(px)} {n(py - 6)} L{n(px + 30)} {n(py - 2)} L{n(px + 30)} {n(py + 6)} L{n(px)} {n(py + 10)} Z" fill="#F97316" stroke="#9A3412" stroke-width="1.2"/>'
          + "".join(f'<rect x="{n(px + 7 + k * 9.5)}" y="{n(py - 4 + k * 1.2)}" width="4.4" height="{n(12.6 - k * 2.4)}" fill="#FFFFFF"/>' for k in range(3)))
    o += S.ribbon(f"{uid}r", [(x + 6, y + 70), (cx, y + 68), (x + w - 6, y + 66)], 4.4, BLUE, "#7FA6E8", opacity=0.94, head=2.2, tail=0.4, per=6)
    o += pill(cx, y + 46, "15 KT", BLUE) + "</g>" + rim(x, y, w, h)
    return o, (cx, y + h - 70)


def callouts(ph, top):
    c = S.callout
    return c(1, 376 + 14, 12 + ph / 2, r=10) + c(2, 28, 28, r=10) + c(3, 512 + 14, top + 14, r=10) + c(4, 376 + 14, top + 14, r=10)


def layers():
    pl, ph = placard()
    top = 12 + ph + 10
    fl, (fx, fy, fw, fh) = flaps(top)
    (pw, pph), a = anchors("panel-26-01-flaps")
    x40 = fx - fw / 2 + 0.396 * fw
    y40 = fy - fh / 2 + 0.640 * fh
    mask = f'<rect x="{n(x40)}" y="{n(y40)}" width="{n(0.062 * fw)}" height="{n(0.045 * fh)}" fill="#3D3C3B"/>'
    fl = [mask if s_ == "@@FLAPMASK@@" else s_ for s_ in fl]
    cw, (sx, sy) = crosswind(top)
    return ([H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#FFFFFF"/>'] + asi() + pl + fl + [cw]
            + [{"name": "sprite-top", "at": [sx, sy], "width": 64, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.3}}]
            + [callouts(ph, top)])


def plate():
    return {
        "id": "fig-26-01-speed-card",
        "replaces": "fig-26-01-speed-card.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-26-01-speed-card.jpg",
        "caption": "Figure 26-1. The flight manual first, then the example speeds on the airspeed indicator, the crosswind and the flap settings",
        "desc": ("Figure 26-1. The flight manual and the school's procedures first; then the example speeds of the fictional trainer on the model's airspeed indicator, VS0 45, VS1 52, VR 55, final approach 60 (short and soft field) and 65 (normal), VX 62, VY 75 and VFE 90 kt; "
                 "the maximum demonstrated crosswind, 15 kt; and the flap settings 0, 10, 20 and 30 degrees. Indicated speeds at maximum mass, for learning only and never for real flight."),
        "legend": [
            "The flight manual comes first: comply with the operating limitations in the approved AFM, markings and placards (section 91.13(a)), and follow your school's procedures. The checklists in this handbook are illustrative.",
            "The example speeds, indicated, at maximum mass: VS0 45 kt, VS1 52 kt, VR 55 kt, VX 62 kt, VY 75 kt, VFE 90 kt; final approach with full flap 65 kt (normal) and 60 kt (short-field and soft-field). For learning only, never for real flight.",
            "Maximum demonstrated crosswind: 15 kt.",
            "Flap settings: 0°, 10°, 20° and 30° (full).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
