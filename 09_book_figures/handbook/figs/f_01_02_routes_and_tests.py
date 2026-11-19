"""Figure 1-2 (new). Steps 4 to 6 of Chapter 1: the three training routes, the minimums of the two common routes and the two tests.

Top row: the three routes (a pilot school course, a training centre course, instructor training) as three illustrated tiles. Middle: the minimums, as bars to one scale of hours: the pilot school course (35 h ground training, 35 h flight training,
20 h dual, 10 h solo, up to 5 h in an approved FSTD) and the instructor training route (40 h flight time in aeroplanes). Bottom: the knowledge test on thirteen areas and the practical test on twelve areas of operation, as numbered boxes.
The only text is the numbers of hours and areas (from the chapter). The tiles are generic."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 372
U = "ar0102"
INK, BLUE, GREEN, AMBER, RED, PURPLE, SLATE = "#1E293B", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#7C3AED", "#475569"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
TILES = ((10.0, 10.0, 200.0, 104.0, "blue"), (220.0, 10.0, 200.0, 104.0, "green"), (430.0, 10.0, 200.0, 104.0, "sand"))
PX = 4.0                                                     # pixels per hour


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.5):
    return M.chip(cx, cy, text, fill, size=size, anchor="middle")


def card(uid, x, y, w, h):
    return (f'<defs><filter id="{uid}" x="-5%" y="-8%" width="110%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.24"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#FFFFFF" filter="url(#{uid})"/><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#E2E8F0" stroke-width="1.4"/>')


def building(cx, base, w, h, roof, col, flag=None):
    out = f'<rect x="{n(cx - w / 2)}" y="{n(base - h)}" width="{n(w)}" height="{n(h)}" rx="2" fill="{col}" stroke="#FFFFFF" stroke-width="1.4"/>'
    out += f'<path d="M{n(cx - w / 2 - 6)} {n(base - h)} L{n(cx)} {n(base - h - roof)} L{n(cx + w / 2 + 6)} {n(base - h)} Z" fill="{SLATE}"/>'
    for r in range(2):
        for c in range(3):
            out += f'<rect x="{n(cx - w / 2 + 8 + c * (w - 16) / 3)}" y="{n(base - h + 8 + r * 16)}" width="{n((w - 16) / 3 - 6)}" height="9" rx="1.5" fill="#DBEAFE"/>'
    if flag:
        out += f'<line x1="{n(cx)}" y1="{n(base - h - roof)}" x2="{n(cx)}" y2="{n(base - h - roof - 18)}" stroke="{SLATE}" stroke-width="1.6"/><path d="M{n(cx)} {n(base - h - roof - 18)} l14 4 l-14 4 Z" fill="{flag}"/>'
    return out


def tiles():
    out = []
    for i, (x, y, w, h, tone) in enumerate(TILES):
        out.append(R.tile(f"{U}t{i}", x, y, w, h, tone))
    x, y = TILES[0][:2]
    out.append(building(x + 100, y + 86, 86, 40, 14, "#93C5FD", BLUE))                       # a pilot school
    x, y = TILES[1][:2]
    out.append(building(x + 82, y + 86, 76, 40, 12, "#86EFAC"))                              # a training centre and its simulator
    out.append(f'<rect x="{n(x + 132)}" y="{n(y + 54)}" width="40" height="28" rx="6" fill="{SLATE}"/><path d="M{n(x + 136)} {n(y + 86)} l6 -6 h24 l6 6 Z" fill="#334155"/><rect x="{n(x + 138)}" y="{n(y + 58)}" width="28" height="14" rx="3" fill="#7DD3FC"/>')
    x, y = TILES[2][:2]                                                                         # an instructor and a student
    for cx, col in ((x + 66, "#0F766E"), (x + 100, "#B45309")):
        out.append(f'<circle cx="{n(cx)}" cy="{n(y + 44)}" r="10" fill="#F5D0A9" stroke="#FFFFFF" stroke-width="1.4"/><path d="M{n(cx - 15)} {n(y + 88)} q0 -30 15 -30 q15 0 15 30 Z" fill="{col}"/>')
    return "".join(out)


def bars():
    out = [card(f"{U}c1", 10, 124, 410, 132), card(f"{U}c2", 430, 124, 200, 132)]
    x0 = 74.0
    rows = (("35 H", 35, BLUE), ("35 H", 35, AMBER), ("20 H", 20, PURPLE), ("10 H", 10, GREEN), ("5 H", 5, SLATE))
    icons = ("book", "plane", "dual", "solo", "sim")
    for k, (lab, hrs, col) in enumerate(rows):
        y = 138 + k * 23
        out.append(f'<rect x="{n(x0)}" y="{n(y)}" width="{n(hrs * PX)}" height="14" rx="4" fill="{col}"/>' + pill(x0 + hrs * PX + 26, y + 7, lab, col))
        ic = icons[k]
        cx, cy = 50.0, y + 7
        if ic == "book":
            out.append(f'<path d="M{n(cx - 12)} {n(cy - 7)} h10 q2 0 2 2 v12 q0 -2 -2 -2 h-10 Z M{n(cx + 12)} {n(cy - 7)} h-10 q-2 0 -2 2 v12 q0 -2 2 -2 h10 Z" fill="{BLUE}"/>')
        elif ic == "plane":
            out.append(f'<path d="M{n(cx - 12)} {n(cy)} h24 M{n(cx - 2)} {n(cy - 7)} v14 M{n(cx - 11)} {n(cy - 4)} v8" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>')
        elif ic == "dual":
            out.append("".join(f'<circle cx="{n(cx + dx)}" cy="{n(cy - 2)}" r="4" fill="{PURPLE}"/><path d="M{n(cx + dx - 6)} {n(cy + 8)} q0 -6 6 -6 q6 0 6 6 Z" fill="{PURPLE}"/>' for dx in (-6, 6)))
        elif ic == "solo":
            out.append(f'<circle cx="{n(cx)}" cy="{n(cy - 2)}" r="4" fill="{GREEN}"/><path d="M{n(cx - 6)} {n(cy + 8)} q0 -6 6 -6 q6 0 6 6 Z" fill="{GREEN}"/>')
        else:
            out.append(f'<rect x="{n(cx - 11)}" y="{n(cy - 7)}" width="22" height="13" rx="3" fill="{SLATE}"/><rect x="{n(cx - 8)}" y="{n(cy - 4)}" width="16" height="7" rx="1.5" fill="#7DD3FC"/>')
    # the instructor route: 40 h flight time in aeroplanes, to the same scale
    out.append(f'<rect x="{n(458)}" y="{n(182)}" width="{n(40 * PX)}" height="18" rx="4" fill="{AMBER}"/>' + pill(458 + 40 * PX - 26, 222, "40 H", AMBER))
    out.append(f'<path d="M{n(452)} {n(179)} h-0" /><path d="M{n(526)} {n(160)} h24 M{n(540)} {n(153)} v14 M{n(527)} {n(156)} v8" stroke="{AMBER}" stroke-width="3" stroke-linecap="round"/>')
    return "".join(out)


def tests():
    out = [card(f"{U}c3", 10, 266, 305, 96), card(f"{U}c4", 325, 266, 305, 96)]
    for k in range(13):                                        # thirteen knowledge areas
        out.append(f'<rect x="{n(52 + (k % 7) * 30)}" y="{n(282 + (k // 7) * 30)}" width="24" height="24" rx="4" fill="#DBEAFE" stroke="{BLUE}" stroke-width="1.6"/>')
    out.append(pill(286, 326, "13", BLUE, 10.0))
    for k in range(12):                                        # twelve areas of operation
        out.append(f'<rect x="{n(367 + (k % 6) * 30)}" y="{n(282 + (k // 6) * 30)}" width="24" height="24" rx="4" fill="#DCFCE7" stroke="{GREEN}" stroke-width="1.6"/>')
    out.append(pill(570 + 18, 296, "12", GREEN, 10.0))
    return "".join(out)


def callouts():
    pts = ((27, 27), (27, 141), (447, 141), (27, 283), (342, 283))
    return "".join(S.callout(k + 1, x, y, r=10.5) for k, (x, y) in enumerate(pts))


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', tiles(), bars(), tests(), {"name": "sprite-side", "at": [590, 36], "width": 46, "outline": OUT, "shadow": SHADOW}, callouts()]


def plate():
    return {
        "id": "fig-01-02-routes-and-tests",
        "replaces": "fig-01-02-routes-and-tests.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-01-02-routes-and-tests.jpg",
        "caption": "Figure 1-2. Steps 4 to 6: three training routes, the minimum hours of the two common routes, and the two tests",
        "desc": ("Figure 1-2. Steps 4 to 6 of the route to the certificate: the three training routes (a pilot school course, a training centre course, instructor training); the minimums of the pilot school course (35 h ground training, 35 h flight training, "
                 "20 h dual, 10 h solo, up to 5 h in an approved FSTD) and of the instructor training route (40 h flight time in aeroplanes), to one scale; and the knowledge test on thirteen areas and the practical test on twelve areas of operation."),
        "legend": [
            "Three ways to meet the training requirement: a pilot school course, a training centre course, or instructor training.",
            "Pilot school course: 35 h ground training, 35 h flight training, 20 h dual instruction and 10 h solo, and up to 5 h in an approved FSTD.",
            "Instructor training route: 40 h flight time in aeroplanes. These are minimums; most students need more hours.",
            "The knowledge test covers the thirteen aeronautical knowledge areas of Appendix A to Part 141.",
            "The practical test covers the twelve areas of operation for an aeroplane single-engine course.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
