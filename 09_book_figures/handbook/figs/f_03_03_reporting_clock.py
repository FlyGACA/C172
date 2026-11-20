"""Figure 3-3 (new: Chapter 3 had no figure). The clock after an occurrence: what Part 4 of the GACAR and the AIP (GEN 1.6) ask of the pilot in command, in hours from the occurrence.

Everything is the book's own reading of the text of Chapter 3, which cites it (data: none; nothing here is measured):
    GACAR 4.11(a)   accident or serious incident: notify the President (GACA) and the AIB as soon as practicable      (no hour is printed: an open start)
    GACAR 4.13      the details, with a statement from each flight crew member, within 48 hours
    GACAR 4.15      other incidents: notify the President as soon as practicable
    GACAR 4.17      the details and the remedial measures within 96 hours
    AIP GEN 1.6     notify immediately the nearest government aerodrome, the nearest police station and the AIB; a written report to the nearest aerodrome director as soon as
                    possible (no hour is printed: the report is drawn dashed); the aircraft is not touched, nor wreckage removed, without the AIB's permission
    GACAR 4.3(d)    preserve the aircraft, its contents, records and other evidence
One lane for each, hours 0 to 96 along the lane (a little beyond, so that the last mark shows): an icon on the hour of the notification, a hatched bar while the time runs, a paper at the
hour the report is due (48 and 96, in a pill), a dashed paper where the text prints no hour, and an open bar with an arrow where the duty has no end date. No words: the numbers of the
sections, the hours, the units. The occurrence in the chapter's example, a rejected takeoff because a runway was occupied, is a serious incident: lane 1."""
from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 292
U = "rc3"
INK = H.INK
X0, X1 = 134.0, 620.0
HOURS = 100.0
PXH = (X1 - X0) / HOURS
SLATE = "#475569"
RED, RED_HI, RED_PALE = "#B91C1C", "#EF4444", "#F7C9C9"
AMBER, AMBER_HI, AMBER_PALE = "#B45309", "#F59E0B", "#F8E0B0"
TEAL, TEAL_HI, TEAL_PALE = "#0F766E", "#14B8A6", "#BDEAE4"
GREY, GREY_HI, GREY_PALE = "#334155", "#64748B", "#CBD5E1"
LANE = {"serious": 92.0, "other": 142.0, "aip": 192.0, "evidence": 242.0}
BAR = 11.0
BOTTOM = 266.0
AXIS_Y0, AXIS_Y1 = 14.0, 40.0
DEADLINES = (("serious", 48), ("other", 96))             # GACAR 4.13 and 4.17


def X(h):
    return X0 + h * PXH


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=5.4, height=10.0, anchor="middle", solid=True):
    return M.chip(x, y, s, colour, size=size * 1.05, anchor=anchor, light=True, height=height)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            + "".join(f'<pattern id="{U}h{k}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="{pale}" fill-opacity="0.7"/>'
                      f'<rect width="1.6" height="5" fill="{col}" fill-opacity="0.6"/></pattern>' for k, (pale, col) in (("r", (RED_PALE, RED)), ("a", (AMBER_PALE, AMBER)), ("t", (TEAL_PALE, TEAL)), ("g", (GREY_PALE, GREY))))
            + f'<linearGradient id="{U}fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GREY_HI}" stop-opacity="0.9"/><stop offset="1" stop-color="{GREY_HI}" stop-opacity="0.35"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def axis():
    out = [f'<rect x="{n(X0)}" y="{n(AXIS_Y0)}" width="{n(X1 - X0)}" height="{n(AXIS_Y1 - AXIS_Y0)}" fill="{SLATE}" fill-opacity="0.10"/>']
    for h in range(0, 101, 12):
        x = X(h)
        out.append(f'<line x1="{n(x)}" y1="{n(AXIS_Y1 - 5)}" x2="{n(x)}" y2="{n(AXIS_Y1)}" stroke="{SLATE}" stroke-width="0.8"/>')
        out.append(f'<line x1="{n(x)}" y1="{n(AXIS_Y1)}" x2="{n(x)}" y2="{n(BOTTOM)}" stroke="{SLATE}" stroke-opacity="0.12" stroke-width="0.6"/>')
        out.append(H.glyph_text(str(h), x, AXIS_Y0 + 9.0, 5.6, SLATE, spacing=0.4))
    out.append(H.glyph_text("H", X1 - 6, AXIS_Y0 + 20.0, 5.6, SLATE, spacing=0.4))
    for h, col in ((48, RED), (96, AMBER)):                # the two deadlines of the text
        out.append(f'<line x1="{n(X(h))}" y1="{n(AXIS_Y1)}" x2="{n(X(h))}" y2="{n(BOTTOM)}" stroke="{col}" stroke-width="1.3" stroke-dasharray="4 3"/>')
        out.append(pill(str(h) + " H", X(h), AXIS_Y1 + 12.0, col, 5.6))
    return "".join(out)


def lane_labels():
    out = []
    rows = (("serious", "4.11", "4.13", RED), ("other", "4.15", "4.17", AMBER), ("aip", "AIP", "GEN 1.6", TEAL), ("evidence", "4.3", "(D)", GREY))
    for key, a, b, col in rows:
        y = LANE[key]
        out.append(f'<rect x="14" y="{n(y - 17)}" width="104" height="34" rx="6" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.55" stroke-width="0.9"/>')
        out.append(H.glyph_text("GACAR" if key != "aip" else "", 24 + gwidth("GACAR", 5.2) / 2, y - 7.0, 5.2, col, spacing=0.4))
        out.append(H.glyph_text(f"{a}  {b}" if key != "aip" else f"{a} {b}", 24 + gwidth(f"{a}  {b}" if key != "aip" else f"{a} {b}", 6.4) / 2, y + 5.0 if key != "aip" else y - 1.0, 6.4, col, spacing=0.4))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ icons
def megaphone(x, y, col):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="10" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x - 5)} {n(y - 2.4)} L{n(x - 0.5)} {n(y - 2.4)} L{n(x + 5.4)} {n(y - 6)} L{n(x + 5.4)} {n(y + 6)} L{n(x - 0.5)} {n(y + 2.4)} L{n(x - 5)} {n(y + 2.4)} Z" fill="#FFFFFF"/>'
            f'<path d="M{n(x - 3.4)} {n(y + 2.4)} L{n(x - 2.6)} {n(y + 6.6)} L{n(x - 0.2)} {n(y + 6.6)} L{n(x - 0.6)} {n(y + 2.4)} Z" fill="#FFFFFF"/>')


def paper(x, y, col, dashed=False):
    stroke = f'stroke="{col}" stroke-width="1.5"' + (' stroke-dasharray="2.6 2"' if dashed else "")
    return (f'<path d="M{n(x - 7)} {n(y - 9)} L{n(x + 3)} {n(y - 9)} L{n(x + 7)} {n(y - 5)} L{n(x + 7)} {n(y + 9)} L{n(x - 7)} {n(y + 9)} Z" fill="#FFFFFF" {stroke} stroke-linejoin="round" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x + 3)} {n(y - 9)} L{n(x + 3)} {n(y - 5)} L{n(x + 7)} {n(y - 5)}" fill="none" {stroke} stroke-linejoin="round"/>'
            + "".join(f'<line x1="{n(x - 4)}" y1="{n(y + d)}" x2="{n(x + 4)}" y2="{n(y + d)}" stroke="{col}" stroke-width="1" stroke-opacity="0.8"/>' for d in (-1.5, 1.8, 5.0)))


def lock(x, y, col):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="10" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x - 3.2)} {n(y - 1.2)} L{n(x - 3.2)} {n(y - 3.6)} A3.2 3.2 0 0 1 {n(x + 3.2)} {n(y - 3.6)} L{n(x + 3.2)} {n(y - 1.2)}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>'
            f'<rect x="{n(x - 5)}" y="{n(y - 1.4)}" width="10" height="7.6" rx="1.4" fill="#FFFFFF"/>')


def arrow_head(x, y, col):
    return f'<path d="M{n(x)} {n(y - 5.5)} L{n(x + 8)} {n(y)} L{n(x)} {n(y + 5.5)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="0.9" stroke-linejoin="round"/>'


def bar(key, h0, h1, col, hatch, solid_end=True):
    y = LANE[key]
    x0, x1 = X(h0), X(h1)
    out = [f'<rect x="{n(x0)}" y="{n(y - BAR / 2)}" width="{n(x1 - x0)}" height="{n(BAR)}" rx="3" fill="url(#{U}h{hatch})" stroke="{col}" stroke-width="1"/>']
    return "".join(out)


def lanes():
    out = []
    for key, col, hatch in (("serious", RED, "r"), ("other", AMBER, "a")):
        y = LANE[key]
        deadline = dict(DEADLINES)[key]
        out.append(bar(key, 0, deadline, col, hatch))
        out.append(megaphone(X(0) + 1.0, y, col))
        out.append(paper(X(deadline), y, col))
    y = LANE["aip"]
    out.append(f'<line x1="{n(X(0))}" y1="{n(y)}" x2="{n(X(30))}" y2="{n(y)}" stroke="{TEAL}" stroke-width="2" stroke-dasharray="5 4" stroke-linecap="round"/>')
    out.append(megaphone(X(0) + 1.0, y, TEAL))
    out.append(paper(X(30), y, TEAL, dashed=True))
    y = LANE["evidence"]
    out.append(f'<rect x="{n(X(0))}" y="{n(y - BAR / 2)}" width="{n(X1 + 6 - X(0))}" height="{n(BAR)}" rx="3" fill="url(#{U}hg)" stroke="{GREY}" stroke-width="1"/>')
    out.append(arrow_head(X1 + 6, y, GREY))
    out.append(lock(X(0) + 1.0, y, GREY))
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.0
    out = []
    out.append(c(1, X(12), LANE["serious"] - 24, X(0) + 7, LANE["serious"] - 7, r=r))
    out.append(c(2, X(38), LANE["serious"] + 24, X(48) - 1, LANE["serious"] + 8, r=r))
    out.append(c(3, X(12), LANE["other"] - 24, X(0) + 7, LANE["other"] - 7, r=r))
    out.append(c(4, X(86), LANE["other"] + 24, X(96) - 1, LANE["other"] + 8, r=r))
    out.append(c(5, X(12), LANE["aip"] - 24, X(0) + 7, LANE["aip"] - 7, r=r))
    out.append(c(6, X(42), LANE["aip"] - 22, X(30), LANE["aip"] - 8, r=r))
    out.append(c(7, X(50), LANE["evidence"] - 22, X(50), LANE["evidence"] - BAR / 2, r=r))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), axis(), lane_labels(), lanes(), callouts(),
            f'<defs><filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>']


def plate():
    return {
        "id": "fig-03-03-reporting-clock",
        "replaces": "fig-03-03-reporting-clock.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-03-03-reporting-clock.jpg",
        "caption": "Figure 3-3. The clock after an occurrence: what Part 4 and the AIP ask of the pilot in command, in hours",
        "desc": ("Figure 3-3. The clock after an occurrence: what Part 4 and the AIP ask of the pilot in command, in hours from the occurrence. Four lanes: an accident or serious incident (GACAR 4.11 "
                 "and 4.13), another incident (4.15 and 4.17), what the AIP adds (GEN 1.6) and the evidence (4.3). Hours 0 to 100 along each lane; the deadlines of 48 and 96 hours marked."),
        "legend": [
            "An accident or a serious incident: the pilot in command notifies GACA and the AIB as soon as practicable, by the quickest means. No hour is printed for this.",
            "48 hours: the details of the occurrence, with a statement from each flight crew member, in a form the President and the AIB accept.",
            "Another incident: the notification to the President, as soon as practicable, with the organization and contact details, the date, time and place and a brief description.",
            "96 hours: the details and the remedial measures.",
            "What the AIP adds: tell immediately the nearest government aerodrome, the nearest police station and the AIB, by the quickest means.",
            "A written report to the nearest aerodrome director as soon as possible: the AIP prints no hour for it, so it is drawn dashed.",
            "The evidence is preserved from the first minute and has no end date in the figure: the aircraft, its contents and records stay as they are until the authorities say otherwise.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
