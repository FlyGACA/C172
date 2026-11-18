"""Figure 3-2 (new). What the pilot in command must do after an accident or serious incident, from that section of Chapter 3: four tiles.

1 notify straight away (a telephone and two arrows to two offices, the President of GACA and the AIB), 2 give the minimum information (a form of eleven lines with ticks), 3 report the details within 48 hours (a clock face with 48 H and three statements, one for each crew member),
4 preserve the evidence (an aeroplane behind barrier tape, a box of records kept). Shapes, colours and the numbers of the callouts; the only text is 48 H, from the chapter. The drawings are generic."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 344
U = "ar0302"
INK, BLUE, GREEN, AMBER, RED, SLATE = "#1E293B", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#475569"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
CELLS = ((10.0, 10.0, 305.0, 157.0, "blue"), (325.0, 10.0, 305.0, 157.0, "slate"), (10.0, 177.0, 305.0, 157.0, "sand"), (325.0, 177.0, 305.0, 157.0, "red"))


def pill(cx, cy, text, fill, size=10.0):
    g = H._GLYPHS
    w = sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * size / g["cap_height"]) + 0.4 for c in text) + 14.0
    h = size + 7.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def office(cx, base, col):
    out = f'<rect x="{n(cx - 30)}" y="{n(base - 46)}" width="60" height="46" rx="3" fill="{col}" stroke="#FFFFFF" stroke-width="1.6"/><path d="M{n(cx - 36)} {n(base - 46)} L{n(cx)} {n(base - 62)} L{n(cx + 36)} {n(base - 46)} Z" fill="{SLATE}"/>'
    out += "".join(f'<rect x="{n(cx - 22 + c * 16)}" y="{n(base - 38 + r * 16)}" width="11" height="9" rx="1.5" fill="#E0F2FE"/>' for r in range(2) for c in range(3))
    return out


def arrow(x1, y1, x2, y2, col=BLUE):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 9 * math.cos(a), y2 - 9 * math.sin(a)
    px, py = -math.sin(a) * 5, math.cos(a) * 5
    return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="3.2" stroke-linecap="round"/><path d="M{n(x2)} {n(y2)} L{n(hx + px)} {n(hy + py)} L{n(hx - px)} {n(hy - py)} Z" fill="{col}"/>'


def tile1():
    x, y = CELLS[0][:2]
    phone = (f'<rect x="{n(x + 50)}" y="{n(y + 46)}" width="42" height="74" rx="8" fill="{INK}" stroke="#FFFFFF" stroke-width="1.6"/><rect x="{n(x + 55)}" y="{n(y + 54)}" width="32" height="50" rx="3" fill="#7DD3FC"/>'
             f'<circle cx="{n(x + 71)}" cy="{n(y + 112)}" r="3.4" fill="#94A3B8"/>')
    return phone + arrow(x + 98, y + 72, x + 182, y + 58) + arrow(x + 98, y + 90, x + 182, y + 116) + office(x + 222, y + 80, "#93C5FD") + office(x + 222, y + 146, "#FCA5A5")


def tile2():
    x, y = CELLS[1][:2]
    out = f'<rect x="{n(x + 96)}" y="{n(y + 18)}" width="116" height="128" rx="6" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2"/><rect x="{n(x + 136)}" y="{n(y + 12)}" width="36" height="12" rx="4" fill="{SLATE}"/>'
    for k in range(11):
        yy = y + 32 + k * 10.4
        out += f'<path d="M{n(x + 106)} {n(yy)} l2.6 2.8 l4.8 -5.6" fill="none" stroke="{GREEN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="{n(x + 120)}" y1="{n(yy)}" x2="{n(x + 200 - (k * 7) % 30)}" y2="{n(yy)}" stroke="#94A3B8" stroke-width="2.4" stroke-linecap="round"/>'
    return out


def tile3():
    x, y = CELLS[2][:2]
    clock = f'<circle cx="{n(x + 92)}" cy="{n(y + 82)}" r="44" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>' + "".join(
        f'<line x1="{n(x + 92)}" y1="{n(y + 82 - 38)}" x2="{n(x + 92)}" y2="{n(y + 82 - 32)}" stroke="{INK}" stroke-width="2.4" transform="rotate({k * 30} {n(x + 92)} {n(y + 82)})"/>' for k in range(12))
    clock += f'<path d="M{n(x + 92)} {n(y + 82)} L{n(x + 92)} {n(y + 52)} M{n(x + 92)} {n(y + 82)} L{n(x + 114)} {n(y + 92)}" stroke="{AMBER}" stroke-width="4" stroke-linecap="round"/><circle cx="{n(x + 92)}" cy="{n(y + 82)}" r="4" fill="{AMBER}"/>'
    sheets = "".join(f'<rect x="{n(x + 172 + k * 26)}" y="{n(y + 46 + k * 10)}" width="58" height="74" rx="4" fill="#FFFFFF" stroke="{SLATE}" stroke-width="1.8"/>'
                     + "".join(f'<line x1="{n(x + 180 + k * 26)}" y1="{n(y + 60 + k * 10 + r * 10)}" x2="{n(x + 222 + k * 26)}" y2="{n(y + 60 + k * 10 + r * 10)}" stroke="#94A3B8" stroke-width="2"/>' for r in range(5)) for k in range(3))
    return clock + sheets + pill(x + 92, y + 142, "48 H", AMBER)


def tile4():
    x, y = CELLS[3][:2]
    ground = f'<path d="M{n(x)} {n(y + 118)} H{n(x + 305)} V{n(y + 148)} q0 9 -9 9 H{n(x + 9)} q-9 0 -9 -9 Z" fill="#D6C39C" fill-opacity="0.8"/>'
    tape = "".join(f'<rect x="{n(x + 12 + k * 24)}" y="{n(y + 112)}" width="12" height="9" fill="{RED if k % 2 == 0 else "#FFFFFF"}"/>' for k in range(12))
    posts = "".join(f'<rect x="{n(x + px)}" y="{n(y + 104)}" width="4" height="32" fill="{SLATE}"/>' for px in (10, 150, 288))
    box = f'<rect x="{n(x + 228)}" y="{n(y + 40)}" width="58" height="40" rx="3" fill="#A16207" stroke="#FFFFFF" stroke-width="1.6"/><rect x="{n(x + 236)}" y="{n(y + 30)}" width="42" height="14" rx="2" fill="#FEF3C7" stroke="{SLATE}" stroke-width="1.2"/><path d="M{n(x + 232)} {n(y + 58)} h50" stroke="#FFFFFF" stroke-width="1.4"/>'
    return ground + posts + box


def layers():
    out = [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>']
    out += [R.tile(f"{U}t{i}", x, y, w, h, tone) for i, (x, y, w, h, tone) in enumerate(CELLS)]
    out += [tile1(), tile2(), tile3(), tile4()]
    out.append({"name": "sprite-side", "at": [CELLS[3][0] + 120, CELLS[3][1] + 100], "width": 108, "angle": 8.0, "outline": OUT, "shadow": SHADOW})
    out.append(tape_front())
    out.append("".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(4)))
    return out


def tape_front():
    x, y = CELLS[3][:2]
    return "".join(f'<rect x="{n(x + 12 + k * 24)}" y="{n(y + 116)}" width="12" height="8" fill="{RED if k % 2 == 0 else "#FFFFFF"}" stroke="#94A3B8" stroke-width="0.4"/>' for k in range(12))


def plate():
    return {
        "id": "fig-03-02-after-an-accident",
        "replaces": "fig-03-02-after-an-accident.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-03-02-after-an-accident.jpg",
        "caption": "Figure 3-2. After an accident or serious incident: notify, give the minimum information, report within 48 hours, preserve the evidence",
        "desc": ("Figure 3-2. What the pilot in command must do after an accident or serious incident, four tiles: notify both the President (GACA) and the AIB as soon as practicable; give the minimum information in the initial notification; "
                 "report the details within 48 hours, with a statement from each flight crew member; and preserve the aircraft, its contents, records and other evidence."),
        "legend": [
            "Notify straight away: the PIC of an aircraft involved in an accident or serious incident notifies both the President (GACA) and the AIB as soon as practicable.",
            "Give the minimum information in the initial notification, where it applies and can be found out.",
            "Report the details within 48 hours of the occurrence, including a statement from each flight crew member.",
            "Preserve the evidence: do not move wreckage, wipe data or discard documents except to save life or prevent further harm, and follow the instructions of the authorities.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
