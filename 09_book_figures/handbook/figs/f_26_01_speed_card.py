"""Figure 26-1 (new). The flight manual, the school and the speed card, from the first section of Chapter 26: the AFM first, then the example speeds on one tape.

Left, the flight manual and the school's procedures (a book with a tick, callout 1). Middle, a kneeboard card with a vertical airspeed tape from 40 to 95 kt and the chapter's example speeds at their places: VS0 45, VS1 52, VR 55, final 60 (short and soft field) and 65 (normal), VX 62, VY 75, VFE 90.
Right, the maximum demonstrated crosswind, 15 kt (a windsock across a runway), and the flap settings 0, 10, 20 and 30 degrees (a flap lever). The speeds are those of the handbook's fictional trainer, indicated, at maximum mass, for learning only."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 340
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


def manual():
    x, y, w, h = 20.0, 20.0, 170.0, 300.0
    o = R.tile(f"{U}t1", x, y, w, h, "blue")
    bx, by = x + 40, y + 70
    o += (f'<rect x="{n(bx + 6)}" y="{n(by + 6)}" width="92" height="120" rx="5" fill="#1E3A8A"/>'
          f'<rect x="{n(bx)}" y="{n(by)}" width="92" height="120" rx="5" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>'
          f'<rect x="{n(bx + 14)}" y="{n(by + 18)}" width="64" height="30" rx="3" fill="#FFFFFF" fill-opacity="0.92"/>' + H.glyph_text("AFM", bx + 46, by + 33, 12, BLUE, spacing=0.6)
          + "".join(f'<line x1="{n(bx + 14)}" y1="{n(by + 64 + k * 10)}" x2="{n(bx + 78)}" y2="{n(by + 64 + k * 10)}" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2.4" stroke-linecap="round"/>' for k in range(4)))
    cx, cy = bx + 86, by + 120
    o += (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="16" fill="#FFFFFF" stroke="{GREEN}" stroke-width="3" filter="url(#{U}ds)"/>'
          f'<path d="M{n(cx - 7)} {n(cy)} l5 5.4 l9 -10.4" fill="none" stroke="{GREEN}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return o


def card():
    x, y, w, h = 202.0, 20.0, 236.0, 300.0
    o = (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.6" filter="url(#{U}ds)"/>'
         f'<rect x="{n(x + w / 2 - 30)}" y="{n(y - 6)}" width="60" height="14" rx="4" fill="#94A3B8"/>')
    # the tape and its ticks
    o += f'<rect x="{n(TX - 10)}" y="{n(TY1 - 8)}" width="20" height="{n(TY0 - TY1 + 16)}" rx="6" fill="#F1F5F9" stroke="#94A3B8" stroke-width="1.4"/>'
    o += f'<rect x="{n(TX - 10)}" y="{n(ky(90))}" width="20" height="{n(ky(45) - ky(90))}" rx="2" fill="#FFFFFF" stroke="#E2E8F0"/>'
    o += f'<rect x="{n(TX - 4)}" y="{n(ky(90))}" width="8" height="{n(ky(45) - ky(90))}" rx="2" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>'
    for kt in range(40, 96, 5):
        yy = ky(kt)
        big = kt % 10 == 0
        o += f'<line x1="{n(TX - 10)}" y1="{n(yy)}" x2="{n(TX - (2 if big else 5))}" y2="{n(yy)}" stroke="{INK}" stroke-width="{1.8 if big else 1.2}"/>'
        if big and kt != 60:
            o += H.glyph_text(str(kt), TX - 26, yy, 7.2, SLATE, spacing=0.3)
    marks = [(45, "45 VS0", RED, "R"), (52, "52 VS1", RED, "R"), (55, "55 VR", BLUE, "L"), (60, "60 FINAL", TEAL, "L"), (65, "65 FINAL", TEAL, "R"),
             (62, "62 VX", GREEN, "R2"), (75, "75 VY", GREEN, "R"), (90, "90 VFE", AMBER, "R")]
    for kt, lab, col, side in marks:
        yy = ky(kt)
        if side.startswith("R"):
            off = 24 if side == "R" else 24
            o += f'<line x1="{n(TX + 10)}" y1="{n(yy)}" x2="{n(TX + off)}" y2="{n(yy)}" stroke="{col}" stroke-width="2.6"/>' + pill(TX + off + 2, yy, lab, col, size=7.6, anchor="start")
        else:
            o += f'<line x1="{n(TX - 10)}" y1="{n(yy)}" x2="{n(TX - 40)}" y2="{n(yy)}" stroke="{col}" stroke-width="2.6"/>' + pill(TX - 42, yy, lab, col, size=7.6, anchor="end")
        o += f'<circle cx="{n(TX)}" cy="{n(yy)}" r="3.6" fill="{col}" stroke="#FFFFFF" stroke-width="1.2"/>'
    return o


def crosswind():
    x, y, w, h = 450.0, 20.0, 170.0, 144.0
    o = R.tile(f"{U}t3", x, y, w, h, "sand")
    cx = x + w / 2 + 6                                    # a runway seen along its length, and the wind straight across it
    o += (f'<path d="M{n(cx - 9)} {n(y + 44)} L{n(cx + 9)} {n(y + 44)} L{n(cx + 34)} {n(y + h - 6)} L{n(cx - 34)} {n(y + h - 6)} Z" fill="#5B6577"/>'
          f'<line x1="{n(cx)}" y1="{n(y + 50)}" x2="{n(cx)}" y2="{n(y + h - 12)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="7 6"/>')
    px, py = x + 30, y + 56                               # a windsock beside it, blowing across
    o += f'<line x1="{n(px)}" y1="{n(py - 6)}" x2="{n(px)}" y2="{n(py + 46)}" stroke="{INK}" stroke-width="2.4"/>'
    o += f'<path d="M{n(px)} {n(py - 6)} L{n(px + 34)} {n(py - 1)} L{n(px + 34)} {n(py + 8)} L{n(px)} {n(py + 13)} Z" fill="#F97316" stroke="#9A3412" stroke-width="1.4"/>'
    o += "".join(f'<rect x="{n(px + 8 + k * 11)}" y="{n(py - 4 + k * 1.4)}" width="5" height="{n(15 - k * 2.8)}" fill="#FFFFFF"/>' for k in range(3))
    o += S.ribbon(f"{U}xw", [(x + 26, y + 112), (cx, y + 108), (x + w - 16, y + 104)], 4.4, BLUE, "#7FA6E8", opacity=0.92, head=2.2, tail=0.4, per=6) + pill(x + w - 44, y + 30, "15 KT", BLUE)
    return o


def flaps():
    x, y, w, h = 450.0, 176.0, 170.0, 144.0
    o = R.tile(f"{U}t4", x, y, w, h, "slate")
    sx, sy = x + 70, y + 30
    o += f'<rect x="{n(sx - 6)}" y="{n(sy)}" width="12" height="96" rx="6" fill="#334155"/>'
    for i, d in enumerate((0, 10, 20, 30)):
        yy = sy + 10 + i * 25
        o += f'<line x1="{n(sx + 10)}" y1="{n(yy)}" x2="{n(sx + 20)}" y2="{n(yy)}" stroke="{INK}" stroke-width="2"/>' + pill(sx + 24, yy, f"{d}°", VIOLET, size=7.6, anchor="start")
    o += f'<rect x="{n(sx - 22)}" y="{n(sy + 30)}" width="44" height="12" rx="4" fill="#E2E8F0" stroke="{INK}" stroke-width="1.6" filter="url(#{U}ds)"/>'
    return o


def callouts():
    c = S.callout
    return c(1, 34, 34, r=10) + c(2, 216, 34, r=10) + c(3, 464, 34, r=10) + c(4, 464, 190, r=10)


def layers():
    return [H.defs(U, W, HT), background(), manual(), card(), crosswind(), flaps(), callouts()]


def plate():
    return {
        "id": "fig-26-01-speed-card",
        "replaces": "fig-26-01-speed-card.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-26-01-speed-card.jpg",
        "caption": "Figure 26-1. The flight manual first, then the example speed card: the speeds on one tape, the crosswind and the flap settings",
        "desc": ("Figure 26-1. The flight manual and the school's procedures first; then the example speed card of the fictional trainer: on one airspeed tape, VS0 45, VS1 52, VR 55, final approach 60 (short and soft field) and 65 (normal), VX 62, VY 75 and VFE 90 kt; "
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
