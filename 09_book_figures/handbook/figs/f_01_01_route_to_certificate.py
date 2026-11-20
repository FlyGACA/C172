"""Figure 1-1 (new: Chapter 1 had no figure). The route to a private pilot certificate, step by step, with the numbers the chapter prints, and what keeps it usable afterwards.

Nothing is measured and nothing is new: every number is one of Chapter 1's, with the section it cites there:
    step 1  medical certificate     Class 2 (61.105, 61.133(h)); valid to the end of the 60th month after the examination under age 40, the 24th month from age 40 (61.9(b))
    step 2  student certificate     at least 16 years old (61.103); the same validity as the medical (61.111(e))
    step 3  solo                    three endorsements before a solo flight (61.109(a)), the instructor's within the preceding 90 days; cross-country thresholds 25 NM and 50 NM (61.113)
    step 4  a training route        three routes (61.133(d)); the minimums of the two common ones: pilot school course, 35 h flight training (141 App A IV(a)), dual 20 h and solo 10 h;
                                    instructor route, 40 h flight time in aeroplanes (61 App C), the same dual and solo content
    step 5  knowledge test          thirteen knowledge areas (141 App A III(b))
    step 6  practical test          twelve areas of operation (141 App A IV(d)(1))
    after   currency                3 takeoffs and 3 landings in the preceding 90 days to carry passengers (61.17(a)); a flight review in the preceding 24 calendar months, 1 h flight and 1 h ground (61.21)
The two bars of hours are drawn to one scale (5.6 units to the hour). Dual 20 h and solo 10 h add to 30 h, so the minimum totals of 35 h and 40 h are not wholly itemised: the rest is hatched
and unlabelled, and the legend says so. No words: digits, units (H, D, M, NM), the codes of the parts and the numbers of the steps."""
from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 330
U = "rt1"
X0 = 42.0
DX = 92.0
Y_PATH = 52.0
BLUE, BLUE_HI, BLUE_PALE = "#1D4ED8", "#3B82F6", "#BFD3FA"
AMBER, AMBER_HI = "#B45309", "#F59E0B"
GREEN, GREEN_HI = "#15803D", "#22C55E"
RED = "#B91C1C"
SLATE, GREY_PALE = "#475569", "#CBD5E1"
STEPS = 6
HOUR = 5.6                                              # canvas units to the hour in the two bars
BAR_X, BAR_H = 78.0, 22.0
BAR_Y = {"school": 232.0, "instructor": 266.0}
TOTALS = {"school": 35, "instructor": 40}              # 141 App A IV(a); 61 App C
DUAL, SOLO = 20, 10                                     # 141 App A IV(b), V
assert DUAL + SOLO == 30 and TOTALS["school"] - DUAL - SOLO == 5 and TOTALS["instructor"] - DUAL - SOLO == 10


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=5.4, height=10.0, solid=True):
    return M.chip(x, y, s, colour, size=size * 1.05, anchor="middle", light=True, height=height)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<pattern id="{U}hh" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="{GREY_PALE}" fill-opacity="0.7"/>'
            f'<rect width="1.6" height="5" fill="{SLATE}" fill-opacity="0.55"/></pattern></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


# ------------------------------------------------------------------------------------------------------------------ icons (each in a 28 unit box centred on x, y)
def cross(x, y):
    return (f'<rect x="{n(x - 3)}" y="{n(y - 9)}" width="6" height="18" rx="1.5" fill="{RED}"/><rect x="{n(x - 9)}" y="{n(y - 3)}" width="18" height="6" rx="1.5" fill="{RED}"/>')


def id_card(x, y):
    return (f'<rect x="{n(x - 11)}" y="{n(y - 8)}" width="22" height="16" rx="2.4" fill="#FFFFFF" stroke="{BLUE}" stroke-width="1.4"/><circle cx="{n(x - 5)}" cy="{n(y - 1.5)}" r="2.8" fill="{BLUE}"/>'
            f'<path d="M{n(x - 9.5)} {n(y + 6)} Q{n(x - 5)} {n(y + 0.4)} {n(x - 0.5)} {n(y + 6)} Z" fill="{BLUE}"/>'
            + "".join(f'<line x1="{n(x + 2.5)}" y1="{n(y + d)}" x2="{n(x + 8.5)}" y2="{n(y + d)}" stroke="{BLUE}" stroke-width="1.2"/>' for d in (-3.5, 0, 3.5)))


def signpost(x, y):
    return (f'<line x1="{n(x)}" y1="{n(y - 10)}" x2="{n(x)}" y2="{n(y + 10)}" stroke="{SLATE}" stroke-width="2"/>'
            + "".join(f'<path d="M{n(x - 9 + 2 * k)} {n(y - 9 + 6.6 * k)} L{n(x + 6 + 2 * k)} {n(y - 9 + 6.6 * k)} L{n(x + 10 + 2 * k)} {n(y - 5.7 + 6.6 * k)} L{n(x + 6 + 2 * k)} {n(y - 2.4 + 6.6 * k)} L{n(x - 9 + 2 * k)} {n(y - 2.4 + 6.6 * k)} Z" '
                      f'fill="{col}" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>' for k, col in enumerate((BLUE, AMBER, GREEN))))


def book(x, y):
    return (f'<path d="M{n(x - 11)} {n(y - 7)} Q{n(x - 5)} {n(y - 10)} {n(x)} {n(y - 6)} Q{n(x + 5)} {n(y - 10)} {n(x + 11)} {n(y - 7)} L{n(x + 11)} {n(y + 8)} Q{n(x + 5)} {n(y + 5)} {n(x)} {n(y + 9)} Q{n(x - 5)} {n(y + 5)} {n(x - 11)} {n(y + 8)} Z" '
            f'fill="#FFFFFF" stroke="{BLUE}" stroke-width="1.4" stroke-linejoin="round"/><line x1="{n(x)}" y1="{n(y - 6)}" x2="{n(x)}" y2="{n(y + 9)}" stroke="{BLUE}" stroke-width="1.1"/>'
            + "".join(f'<line x1="{n(x - 8.5)}" y1="{n(y - 3.5 + d)}" x2="{n(x - 2.5)}" y2="{n(y - 3.5 + d)}" stroke="{BLUE}" stroke-opacity="0.6" stroke-width="0.9"/>' for d in (0, 3.6, 7.2)))


def clipboard(x, y):
    return (f'<rect x="{n(x - 8)}" y="{n(y - 9)}" width="16" height="19" rx="2.2" fill="#FFFFFF" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(x - 4)}" y="{n(y - 11.5)}" width="8" height="5" rx="1.6" fill="{SLATE}"/>'
            f'<path d="M{n(x - 4.6)} {n(y + 1)} L{n(x - 1.4)} {n(y + 4.4)} L{n(x + 5)} {n(y - 3.2)}" fill="none" stroke="{GREEN}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


def scroll(x, y):
    return (f'<rect x="{n(x - 11)}" y="{n(y - 8)}" width="22" height="16" rx="2" fill="#FFF7DC" stroke="{AMBER}" stroke-width="1.4"/>'
            f'<circle cx="{n(x)}" cy="{n(y + 1)}" r="4.6" fill="{AMBER_HI}" stroke="{AMBER}" stroke-width="1"/><path d="M{n(x - 2.6)} {n(y + 4.6)} L{n(x - 3.8)} {n(y + 10)} L{n(x)} {n(y + 8)} L{n(x + 3.8)} {n(y + 10)} L{n(x + 2.6)} {n(y + 4.6)} Z" fill="{AMBER}"/>'
            + "".join(f'<line x1="{n(x - 8)}" y1="{n(y - 4.6)}" x2="{n(x + 8)}" y2="{n(y - 4.6)}" stroke="{AMBER}" stroke-opacity="0.55" stroke-width="0.9"/>' for _ in (0,)))


def plane_icon(x, y):
    return (f'<path d="M{n(x)} {n(y - 10)} L{n(x + 2.2)} {n(y - 3)} L{n(x + 11)} {n(y + 2)} L{n(x + 11)} {n(y + 4)} L{n(x + 2.2)} {n(y + 2)} L{n(x + 1.6)} {n(y + 7)} L{n(x + 5)} {n(y + 9)} L{n(x + 5)} {n(y + 10.6)} L{n(x)} {n(y + 9.4)} '
            f'L{n(x - 5)} {n(y + 10.6)} L{n(x - 5)} {n(y + 9)} L{n(x - 1.6)} {n(y + 7)} L{n(x - 2.2)} {n(y + 2)} L{n(x - 11)} {n(y + 4)} L{n(x - 11)} {n(y + 2)} L{n(x - 2.2)} {n(y - 3)} Z" fill="{BLUE}" stroke="#FFFFFF" stroke-width="0.9" stroke-linejoin="round"/>')


# ------------------------------------------------------------------------------------------------------------------ the path
def sx(i):
    return X0 + DX * i


def path():
    out = [f'<line x1="{n(sx(0))}" y1="{n(Y_PATH)}" x2="{n(sx(STEPS - 1) + DX - 22)}" y2="{n(Y_PATH)}" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>'
           f'<line x1="{n(sx(0))}" y1="{n(Y_PATH)}" x2="{n(sx(STEPS - 1) + DX - 22)}" y2="{n(Y_PATH)}" stroke="{SLATE}" stroke-opacity="0.5" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 8"/>']
    icons = (cross, id_card, plane_icon, signpost, book, clipboard)
    for i, icon in enumerate(icons):
        x = sx(i)
        out.append(f'<circle cx="{n(x)}" cy="{n(Y_PATH + 40)}" r="19" fill="#FFFFFF" stroke="{SLATE}" stroke-opacity="0.45" stroke-width="1.1" filter="url(#{U}ds)"/>')
        out.append(icon(x, Y_PATH + 40))
        out.append(f'<line x1="{n(x)}" y1="{n(Y_PATH + 21)}" x2="{n(x)}" y2="{n(Y_PATH + 8)}" stroke="{SLATE}" stroke-opacity="0.5" stroke-width="1.2"/>')
    out.append(f'<circle cx="{n(sx(STEPS - 1) + DX - 10)}" cy="{n(Y_PATH)}" r="19" fill="#FFFFFF" stroke="{AMBER}" stroke-width="1.4" filter="url(#{U}ds)"/>' + scroll(sx(STEPS - 1) + DX - 10, Y_PATH))
    return "".join(out)


def facts():
    """The numbers under each step."""
    rows = (
        (("2", RED), ("60 M", BLUE), ("24 M", AMBER)),            # class 2; the validity under 40 and from 40
        (("16", BLUE),),                                             # years
        (("3", BLUE), ("90 D", AMBER), ("25 NM", SLATE), ("50 NM", SLATE)),     # endorsements; instructor's within 90 days; the two distances
        (("3", BLUE), ("35 H", GREEN), ("40 H", AMBER)),            # routes; school; instructor
        (("13", BLUE),),
        (("12", BLUE),),
    )
    out = []
    for i, row in enumerate(rows):
        x = sx(i)
        y = Y_PATH + 76
        for label, col in row:
            out.append(pill(label, x, y, col))
            y += 13.0
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the hours
def bars():
    out = []
    for key, label in (("school", "141"), ("instructor", "61 C")):
        y = BAR_Y[key]
        total = TOTALS[key]
        x = BAR_X
        out.append(H.glyph_text(label, BAR_X - 8 - gwidth(label, 5.4) / 2, y, 5.4, SLATE, spacing=0.4))
        out.append(f'<rect x="{n(x)}" y="{n(y - BAR_H / 2)}" width="{n(total * HOUR)}" height="{n(BAR_H)}" rx="4" fill="url(#{U}hh)" stroke="{SLATE}" stroke-width="1"/>')
        out.append(f'<rect x="{n(x)}" y="{n(y - BAR_H / 2)}" width="{n(DUAL * HOUR)}" height="{n(BAR_H)}" rx="4" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.2"/>')
        out.append(f'<rect x="{n(x + DUAL * HOUR)}" y="{n(y - BAR_H / 2)}" width="{n(SOLO * HOUR)}" height="{n(BAR_H)}" fill="{AMBER_HI}" stroke="#FFFFFF" stroke-width="1.2"/>')
        out.append(H.glyph_text("20", x + DUAL * HOUR / 2, y, 6.4, "#FFFFFF", spacing=0.4))
        out.append(H.glyph_text("10", x + (DUAL + SOLO / 2) * HOUR, y, 6.4, "#FFFFFF", spacing=0.4))
        out.append(pill(f"{total} H", x + total * HOUR + 22, y, GREEN if key == "school" else AMBER))
    return "".join(out)


def currency():
    out = []
    x0, y0 = 372.0, 216.0
    cards = ((x0, "90 D", "3", plane_icon), (x0 + 126.0, "24 M", "1", clipboard))
    for x, a, b, icon in cards:
        out.append(f'<rect x="{n(x)}" y="{n(y0)}" width="116" height="74" rx="9" fill="#FFFFFF" stroke="{SLATE}" stroke-opacity="0.35" stroke-width="1" filter="url(#{U}ds)"/>')
        out.append(icon(x + 24, y0 + 24))
        out.append(pill(a, x + 78, y0 + 24, AMBER, 6.2, 12.0))
        if icon is plane_icon:
            out.append(H.glyph_text("3 + 3", x + 58, y0 + 54, 7.2, BLUE, spacing=0.5))
        else:
            out.append(H.glyph_text("1 H + 1 H", x + 58, y0 + 54, 6.4, BLUE, spacing=0.5))
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.0
    out = []
    for i in range(STEPS):
        out.append(c(i + 1, sx(i), Y_PATH, r=r))
    out.append(c(7, 30, 205, r=r))
    out.append(c(8, 360, 205, r=r))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), path(), facts(), bars(), currency(), callouts()]


def plate():
    return {
        "id": "fig-01-01-route-to-certificate",
        "replaces": "fig-01-01-route-to-certificate.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-01-01-route-to-certificate.jpg",
        "caption": "Figure 1-1. The route to a private pilot certificate in six steps, with the numbers of this chapter",
        "desc": ("Figure 1-1. The route to a private pilot certificate in six steps, with the numbers of this chapter: the medical certificate, the student pilot certificate, solo, a training route, "
                 "the knowledge test and the practical test; the hours of the two common routes; and what keeps the certificate usable. The numbers are those of Chapter 1 and the sections it cites."),
        "legend": [
            "The medical certificate: Class 2 at least. Valid to the end of the 60th month after the examination if you were under 40 then, the 24th month if you were 40 or older.",
            "The student pilot certificate: at least 16 years old. It is valid as long as the medical certificate it rests on.",
            "Solo: three endorsements before any solo flight, the instructor's within the preceding 90 days. Cross-country solo is controlled at 25 NM and at 50 NM from the departure aerodrome.",
            "A training route: three are open (a pilot school course, a training centre course, instructor training). The minimums of the two common ones are 35 h of flight training for the school course and 40 h of flight time for the instructor route.",
            "The knowledge test: thirteen knowledge areas, the thirteen of Appendix A to Part 141.",
            "The practical test: twelve areas of operation for an aeroplane single-engine course. Then the certificate.",
            "The hours of the two common routes, to one scale: the pilot school course (Part 141, Appendix A, 35 h) and the instructor route (Part 61, Appendix C, 40 h). Both ask 20 h of dual instruction (blue) and 10 h of solo (amber); those add to 30 h, so the rest of each total is hatched and not itemised here.",
            "Staying current: 3 takeoffs and 3 landings in the preceding 90 days to carry passengers by day, and a flight review (1 h of flight training and 1 h of ground training) in the preceding 24 calendar months.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
