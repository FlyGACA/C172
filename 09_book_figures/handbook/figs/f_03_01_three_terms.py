"""Figure 3-1 (new). The three terms of GACAR Part 1 that Part 4 uses (Chapter 3, "Three words with exact meanings"), as nested regions.

The widest region is the aviation safety occurrence (any safety-related event that endangers, or if not corrected could endanger, an aircraft, its occupants or anyone else). Inside it, on the left, the incident (any occurrence other than an accident that affects
or could affect the safety of operation), and inside the incident the serious incident (an incident whose circumstances show a high probability of an accident). On the right, the accident, outside the incident because an incident is by definition not an accident,
with its three ways to be one, each a small drawing: a person fatally or seriously injured, an aircraft with damage or structural failure that would normally need major repair or replacement, and an aircraft that is missing or completely inaccessible (drawn dashed).
An arrow from the serious incident to the accident says what the definition notes: the difference lies only in the result. No words: shapes, colours and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "tm3"
INK, SLATE, BLUE, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#B45309", "#B91C1C"


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def region(x, y, w, h, fill, stroke, op=0.14, rx=18, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="2.6"{dd}/>'


def person(x, y, col=RED):
    return (f'<circle cx="{n(x)}" cy="{n(y - 14)}" r="7" fill="{INK}"/><path d="M{n(x - 12)} {n(y + 16)} Q{n(x)} {n(y - 8)} {n(x + 12)} {n(y + 16)} Z" fill="{INK}"/>'
            f'<circle cx="{n(x + 12)}" cy="{n(y - 12)}" r="8" fill="{col}" stroke="#FFFFFF" stroke-width="1.4"/><path d="M{n(x + 8)} {n(y - 12)} h8 M{n(x + 12)} {n(y - 16)} v8" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>')


def damaged(x, y):
    """An aeroplane with a wing broken off."""
    return (A.plane(x, y, 44.0, name="sprite-top"), f'<path d="M{n(x - 22)} {n(y - 12)} l8 6 l-6 4 l8 6" fill="none" stroke="{RED}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')


def missing(x, y):
    return (f'<rect x="{n(x - 22)}" y="{n(y - 22)}" width="44" height="44" rx="8" fill="none" stroke="{SLATE}" stroke-width="2.2" stroke-dasharray="5 4"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="3" fill="{SLATE}"/><circle cx="{n(x - 12)}" cy="{n(y + 4)}" r="2" fill="{SLATE}" fill-opacity="0.6"/><circle cx="{n(x + 12)}" cy="{n(y - 4)}" r="2" fill="{SLATE}" fill-opacity="0.6"/>')


def regions():
    out = []
    out.append(region(20, 24, 600, 258, "#94A3B8", SLATE, 0.10, 20))                 # the aviation safety occurrence
    out.append(region(40, 48, 300, 214, "#3B82F6", BLUE, 0.12, 16))                  # the incident
    out.append(region(60, 76, 150, 160, "#EF4444", RED, 0.16, 14))                   # the serious incident
    out.append(region(372, 48, 228, 214, "#F59E0B", AMBER, 0.20, 16))                # the accident
    return "".join(out)


def serious():
    x, y = 135.0, 186.0
    return (f'<path d="M{n(x)} {n(y - 52)} L{n(x + 26)} {n(y - 8)} L{n(x - 26)} {n(y - 8)} Z" fill="#FACC15" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round" transform="translate(0 0)"/>'
            f'<path d="M{n(x)} {n(y - 40)} v16" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/><circle cx="{n(x)}" cy="{n(y - 17)}" r="2.2" fill="{INK}"/>')


def incident_icon():
    """A small warning mark in the incident region, outside the serious incident."""
    x, y = 276.0, 150.0
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="22" fill="#60A5FA" fill-opacity="0.7" stroke="{BLUE}" stroke-width="2.4"/>'
            f'<path d="M{n(x)} {n(y - 11)} v12" stroke="{BLUE}" stroke-width="3.6" stroke-linecap="round"/><circle cx="{n(x)}" cy="{n(y + 10)}" r="2.4" fill="{BLUE}"/>')


def arrow_result():
    """The arrow from the serious incident to the accident: the difference is only in the result."""
    x0, x1, y = 216.0, 372.0, 214.0
    return (f'<path d="M{n(x0)} {n(y)} Q{n((x0 + x1) / 2)} {n(y + 36)} {n(x1 - 6)} {n(y)}" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity="0.9"/>'
            f'<path d="M{n(x0)} {n(y)} Q{n((x0 + x1) / 2)} {n(y + 36)} {n(x1 - 6)} {n(y)}" fill="none" stroke="{INK}" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="1 7"/>'
            f'<path d="M{n(x1)} {n(y)} L{n(x1 - 12)} {n(y - 7)} L{n(x1 - 12)} {n(y + 7)} Z" fill="{INK}"/>')


def accident_icons():
    out = [person(424, 160), missing(556, 150)]
    d = damaged(490, 150)
    out.append(d[1])
    return "".join(out)


def sprites():
    return [A.plane(490, 150, 44.0, name="sprite-top")]


def callouts():
    c = S.callout
    r = 9.5
    out = []
    out.append(c(1, 600.0, 36.0, 580.0, 36.0, r=r))                     # the aviation safety occurrence
    out.append(c(2, 330.0, 62.0, 316.0, 74.0, r=r))                     # the incident
    out.append(c(3, 200.0, 88.0, 186.0, 100.0, r=r))                    # the serious incident
    out.append(c(4, 586.0, 62.0, 566.0, 76.0, r=r))                     # the accident
    out.append(c(5, 292.0, 262.0, 290.0, 234.0, r=r))                   # the result only
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), regions(), serious(), incident_icon(), *sprites(), accident_icons(), arrow_result(), callouts()]


def plate():
    return {
        "id": "fig-03-01-three-terms",
        "replaces": "fig-03-01-three-terms.svg",             # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-03-01-three-terms.jpg",
        "caption": "Figure 3-1. Accident, serious incident and incident: three terms of Part 1, and the wider occurrence that Part 4 reports",
        "desc": ("Figure 3-1. Accident, serious incident and incident as nested regions inside the aviation safety occurrence. The incident, with the serious incident inside it, lies beside the accident, "
                 "which is outside the incident by definition; the accident has three ways to occur: a person seriously or fatally injured, aircraft damage needing major repair, and an aircraft missing or inaccessible."),
        "legend": [
            "The aviation safety occurrence: any safety-related event that endangers, or if not corrected could endanger, an aircraft, its occupants or anyone else (section 4.1). This is the wider term Part 4 uses.",
            "The incident: any occurrence other than an accident, associated with the operation of an aircraft, that affects or could affect the safety of operation.",
            "The serious incident: an incident whose circumstances show that there was a high probability of an accident.",
            "The accident: an occurrence between the time any person boards with the intention of flight and the time all have disembarked, in which (left to right) a person is fatally or seriously injured, the aircraft sustains damage or structural failure that would normally need major repair or replacement (the broken wing), or the aircraft is missing or completely inaccessible (the dashed frame). An accident is not an incident, by definition.",
            "The difference between an accident and a serious incident lies only in the result, as the definition notes.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
