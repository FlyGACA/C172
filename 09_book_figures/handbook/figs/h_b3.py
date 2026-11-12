"""Helpers of worker b3 (Saudi round: figures 18-2 and 18-7). Plain Python, no Pillow, no Blender.

* `facts()` reads data/saudi_airspace.json (the AIP values as printed, AMDT 11/26) and `Frame` projects latitude and longitude into it on an equirectangular
  frame around a chosen origin (x east, y north, in kilometres, 1 NM = 1852 m): x_nm = (lon - lon0) * 60 * cos(lat0), y_nm = (lat - lat0) * 60.
* `text()` is figs/h_a2.py's glyph_text (outlines of Inter Bold, no font needed) with two more letters (k and m), a squeeze for painted numbers and an option that centres a string on its ink.
* `end_marks()` / `runway()` paint an asphalt bar with its edge lines, its centre line, its threshold bars and the designators at both ends, in the bar's own frame
  (its middle at the origin, y along the bar), as figs/f_18_02_runway_designators.py needs them (figs/f_18_07_crosswind.py takes only the facts).
"""
import json
import math
import os
import re

from figs import h_a2 as H
from figs import scene as S

n = S.n
NM = 1.852                                                    # kilometres in a nautical mile
PAINT = "#F6F3EA"
SQUEEZE = 0.74                                                  # the painted numbers are narrower than the letters of a page

# two lower-case letters that glyphs.json does not have (Inter Bold outlines, y down, 2048 units to the em)
EXTRA = {"k": {"d": "M128 0H428V-359L514 -456L826 0H1179L740 -633L1158 -1118H811L445 -688H428V-1490H128Z", "advance": 1188},
         "m": {"d": "M128 0H428V-676C428 -810 509 -884 615 -884C717 -884 789 -814 789 -705V0H1079V-688C1079 -805 1149 -884 1263 -884C1364 -884 1440 -823 1440 -697V0H1741V-754C1741 -997 1589 -1135 1384 -1135C1230 -1135 1088 -1056 1025 -884C973 -1054 880 -1135 737 -1135C603 -1135 478 -1064 418 -901L406 -1118H128Z", "advance": 1869}}

_FACTS = {}


def facts():
    """The facts file of the Saudi round (data/saudi_airspace.json), read once."""
    if not _FACTS:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "saudi_airspace.json")
        with open(path, encoding="utf-8") as f:
            _FACTS.update(json.load(f))
    return _FACTS


class Frame:
    """An equirectangular frame around (lat0, lon0): `xy(lat, lon)` gives (east, north) in kilometres."""

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.kx = 60.0 * math.cos(math.radians(lat0)) * NM       # km per degree of longitude
        self.ky = 60.0 * NM                                        # km per degree of latitude

    def xy(self, lat, lon):
        return (lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky


_INK = {}


def ink_x(c):
    """The sideways extent (min, max) of the outline of a glyph, in font units, from the points of its path (so that a string can be centred on its ink, not on its advances)."""
    if c not in _INK:
        g = H._glyphs()
        table = {**g["glyphs"], **EXTRA}
        xs, cmd, nums = [], None, []
        for tok in re.findall(r"[MLHVCQZ]|-?\d+(?:\.\d+)?", table[c]["d"]):
            if tok.isalpha():
                cmd, nums = tok, []
                continue
            nums.append(float(tok))
            if cmd in ("M", "L", "C", "Q") and len(nums) % 2 == 0:
                xs.append(nums[-2])
            elif cmd == "H":
                xs.append(nums[-1])
        _INK[c] = (min(xs), max(xs)) if xs else (0.0, 0.0)
    return _INK[c]


def width_of(s, height, spacing=0.0, sx=1.0):
    """The width of a string set by text()."""
    g = H._glyphs()
    table = {**g["glyphs"], **EXTRA}
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else table[c]["advance"] * k * sx) + spacing for c in s) - spacing


def text(s, cx, cy, height, fill="#FFFFFF", rotate=0.0, spacing=0.0, stroke=None, stroke_width=0.0, anchor="middle", opacity=None, sx=1.0, ink=False):
    """H.glyph_text with the extra letters: outlines of Inter Bold, `height` units tall at the capitals, centred (or anchored) on (cx, cy); `sx` squeezes the letters sideways
    (runway numbers are painted tall and narrow)."""
    g = H._glyphs()
    table = {**g["glyphs"], **EXTRA}
    k = height / g["cap_height"]
    advances = [(height * 0.38 if c == " " else table[c]["advance"] * k * sx) + spacing for c in s]
    total = sum(advances) - spacing
    cursor = cx - (total / 2 if anchor == "middle" else total if anchor == "end" else 0.0)
    if ink and anchor == "middle":                                     # centre the ink of the string on cx (a "1" has more room on one side than on the other)
        lo, hi, pos = None, None, cursor
        for c, adv in zip(s, advances):
            if c != " ":
                a, b = ink_x(c)
                lo = pos + a * k * sx if lo is None else min(lo, pos + a * k * sx)
                hi = pos + b * k * sx if hi is None else max(hi, pos + b * k * sx)
            pos += adv
        cursor += cx - (lo + hi) / 2
    out = []
    edge = f' stroke="{stroke}" stroke-width="{n(stroke_width / k)}" stroke-linejoin="round"' if stroke else ""
    for c, adv in zip(s, advances):
        if c != " ":
            out.append(f'<path d="{table[c]["d"]}" transform="translate({n(cursor)} {n(cy + height / 2)}) scale({k * sx:.5f} {k:.5f})" fill="{fill}"{edge}/>')
        cursor += adv
    op = f' opacity="{n(opacity)}"' if opacity is not None else ""
    turn = f' transform="rotate({n(rotate)} {n(cx)} {n(cy)})"' if rotate else ""
    return f"<g{turn}{op}>" + "".join(out) + "</g>"


def label(s, cx, cy, height, colour="#1F2937", anchor="middle", rotate=0.0, halo=3.2):
    """A word or a number laid on a picture: its letters in `colour` over a white casing."""
    return (text(s, cx, cy, height, "#FFFFFF", rotate=rotate, anchor=anchor, stroke="#FFFFFF", stroke_width=halo, spacing=height * 0.04)
            + text(s, cx, cy, height, colour, rotate=rotate, anchor=anchor, stroke=colour, stroke_width=height * 0.03, spacing=height * 0.04))


# ------------------------------------------------------------------------------------------------------------------ a runway as a painted bar
def end_marks(cx, number, letter, y_end, width, num_h):
    """The paint at the end of a bar at y_end (y positive downwards in the bar's frame, the end at the bottom): threshold bars, the number and (if there is one) the letter below
    it, nearer the threshold. For the end at -y the caller turns the whole thing round."""
    bar_h = num_h * 0.85
    gap = width * 0.17
    step = max(1.6, (width - 2 * gap) / 7.0)
    xs = [cx + (i - 3.5) * step for i in range(8)]
    out = "".join(f'<rect x="{n(x - step * 0.2)}" y="{n(y_end - bar_h - 0.6)}" width="{n(step * 0.4)}" height="{n(bar_h)}"/>' for x in xs)
    if letter:
        y_letter = y_end - bar_h - 0.6 - num_h * 1.05
        y_number = y_letter - num_h * 1.35
        out += text(number, cx, y_number, num_h, PAINT, spacing=num_h * 0.09, stroke=PAINT, stroke_width=0.3, sx=SQUEEZE, ink=True)
        out += text(letter, cx, y_letter, num_h, PAINT, stroke=PAINT, stroke_width=0.3, sx=SQUEEZE, ink=True)
    else:
        y_number = y_end - bar_h - 0.6 - num_h * 1.05
        out += text(number, cx, y_number, num_h, PAINT, spacing=num_h * 0.09, stroke=PAINT, stroke_width=0.3, sx=SQUEEZE, ink=True)
    return out


def runway(uid, width, half, bottom_text, top_text, num_h, dashes=True):
    """A bar lying along y in its own frame: a soft sand shoulder, the asphalt (the figure's filter `uid`as), a thin edge line, dashes along the middle and the paint at both ends
    (bottom_text = (number, letter) read from the bottom end; top_text from the top end). The figure's defs must hold the filters uid+"as", uid+"pw" and uid+"bl"."""
    x0 = -width / 2
    out = [f'<rect x="{n(x0 - 3)}" y="{n(-half - 3)}" width="{n(width + 6)}" height="{n(2 * half + 6)}" fill="#BFAD84" opacity="0.5" filter="url(#{uid}bl)"/>',
           f'<rect x="{n(x0)}" y="{n(-half)}" width="{n(width)}" height="{n(2 * half)}" fill="#444" filter="url(#{uid}as)"/>',
           f'<rect x="{n(x0)}" y="{n(-half)}" width="{n(width)}" height="{n(2 * half)}" fill="none" stroke="#10151D" stroke-opacity="0.5" stroke-width="0.5"/>']
    inset = min(1.5, width * 0.09)
    paint = "".join(f'<rect x="{n(sx_ - 0.3)}" y="{n(-half + 1.2)}" width="0.6" height="{n(2 * half - 2.4)}"/>' for sx_ in (-width / 2 + inset, width / 2 - inset))
    if dashes:
        span = half - num_h * 4.6
        count = max(2, int(span * 2 / 14.0))
        pitch = span * 2 / count
        paint += "".join(f'<rect x="-0.7" y="{n(-span + pitch * (i + 0.25))}" width="1.4" height="{n(pitch * 0.5)}"/>' for i in range(count))
    paint += end_marks(0, bottom_text[0], bottom_text[1], half, width, num_h)
    paint += f'<g transform="rotate(180 0 0)">{end_marks(0, top_text[0], top_text[1], half, width, num_h)}</g>'
    out.append(f'<g fill="{PAINT}" filter="url(#{uid}pw)">{paint}</g>')
    return "".join(out)
