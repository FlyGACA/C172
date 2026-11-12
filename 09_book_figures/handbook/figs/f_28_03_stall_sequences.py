"""Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery. Two scenes in cards: the sky over the desert horizon, the model seen from the right
in the six phases of each stall at the attitudes of the old figure (read from it: the nose-high entry, the break, the recovery), the flight path as a dashed line with a casing, the
buffet as red zigzags, the nose dropping as a red arrow and the angle of attack reduced as a blue one, the power as a small gauge under each phase; the twelve numbered callouts of the
old figure kept (figs/h_a1.py and figs/scene.py make the pieces)."""
import math
import os
import re

from figs import h_a1 as H
from figs import scene as S
from reskin import LINE_SIDE

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R1 = (8, 6, 624, 192)
R2 = (8, 210, 624, 192)
PATH1 = ("M 18 82 C 26.7 83.7 43.8 88.3 70 92 C 96.2 95.7 140 101.3 175 104 C 210 106.7 253.3 105.3 280 108 C 306.7 110.7 317.5 115.7 335 120 C 352.5 124.3 367.5 130.2 385 134 "
         "C 402.5 137.8 422.5 141.7 440 143 C 457.5 144.3 465 146.2 490 142 C 515 137.8 566 124 590 118 C 614 112 626.7 108 632 106.6")
PATH2 = ("M 18 331 C 26.7 330.8 53 331 70 330 C 87 329 102.5 327.7 120 325 C 137.5 322.3 156.7 317.8 175 314 C 193.3 310.2 212.5 304.3 230 302 C 247.5 299.7 263.3 299.7 280 300 "
         "C 296.7 300.3 312.5 302 330 304 C 347.5 306 366.7 309.5 385 312 C 403.3 314.5 422.5 318.3 440 319 C 457.5 319.7 465 319.8 490 316 C 515 312.2 566 300.8 590 296 C 614 291.2 626.7 288.5 632 287.4")
XS = [70, 175, 280, 385, 490, 590]


def old_planes():
    """The twelve aeroplanes of the old figure, line drawings in whatever attitude: where each stood, how long it was and how far its nose was down (as reskin.py reads them)."""
    with open(os.path.join(HERE, "old", "fig-28-03-stall-sequences.svg"), encoding="utf-8") as f:
        svg = f.read()
    out = []
    for m in LINE_SIDE.finditer(svg):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", m.group(1))]
        xs, ys = nums[0::2], nums[1::2]
        x1, y1, x2, y2 = (float(m.group(i)) for i in (2, 3, 4, 5))
        pitch_down = math.degrees(math.atan2(y2 - y1, x2 - x1))
        left, right = min(xs), max(xs)
        top, bottom = min(ys), max(y2, y1) + 3
        out.append({"at": [round((left + right) / 2 + 2, 1), round((top + bottom) / 2, 1)], "width": round((right - left) * 1.12, 1), "angle": round(pitch_down, 2)})
    return out


PLANES = old_planes()


def gauge(cx, y, fill):
    """The power set under a phase: a small white case and a grey column rising from the foot to `fill` units (27.6 is full)."""
    out = (f'<rect x="{S.n(cx - 6.5)}" y="{y}" width="13" height="30" rx="3" fill="#FFFFFF" fill-opacity="0.96" stroke="#1F2937" stroke-width="1.2" filter="url(#a1ds)"/>')
    if fill > 0:
        out += (f'<defs>{S.gradient("a1g" + str(int(cx)) + str(int(y)), [(0, "#8A95A8"), (1, "#5B6578")], 0, 0, 1, 0)}</defs>'
                f'<rect x="{S.n(cx - 5)}" y="{S.n(y + 28.8 - fill)}" width="10" height="{S.n(fill)}" rx="1.5" fill="url(#a1g{int(cx)}{int(y)})"/>')
    return out


def pill(x, y, label):
    return (f'<rect x="{x - 4}" y="{y - 12}" width="{6 + 7.5 * len(label)}" height="16" rx="8" fill="#FFFFFF" fill-opacity="0.92"/>'
            f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#5B6578" text-anchor="start">{label}</text>')


def world(uid, box, hz, seed, clouds):
    x, y, w, h = box
    return H.profile(uid, box, hz + 13, seed=seed, sun=(80, 50), far=18, mid=8, base=13, sky=H.horizon_sky((hz - y) / h), clouds=clouds, scrub_count=6, grain=False)


def annotations(dy, red_arrow, blue_arrow, buffet_y):
    out = []
    for x in (266, 276, 286):
        out.append(H.path_line(f"M {x} {buffet_y} l 3 -5 l 3 5 l 3 -5", "#B91C1C", 1.7, casing=1.6, glow=False))
    d, head = red_arrow
    out.append(H.path_line(d, "#B91C1C", 2.3, casing=2.0, glow=False))
    out.append(f'<polygon points="{head}" fill="#B91C1C" stroke="#FFFFFF" stroke-width="1.3" stroke-linejoin="round" paint-order="stroke"/>')
    d, head = blue_arrow
    out.append(H.path_line(d, "#1D4ED8", 3.0, casing=2.0, glow=False))
    out.append(f'<polygon points="{head}" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="1.3" stroke-linejoin="round" paint-order="stroke"/>')
    return "".join(out)


def layers():
    out = [H.page("a1page", 640, 420), H.defs()]
    out += world("a1r1", R1, 172, 71, [H.cloud("cloud-cumulus-b", 332, 44, 48, 0.9), H.cloud("cloud-cumulus-a", 540, 56, 52, 0.85)])
    out += world("a1r2", R2, 376, 73, [H.cloud("cloud-cumulus-b", 226, 250, 44, 0.9), H.cloud("cloud-cumulus-a", 438, 246, 48, 0.9), H.cloud("cloud-cumulus-b", 560, 252, 40, 0.8)])
    out += H.clipped("a1p1", R1, 10, [H.path_line(PATH1, "#6B7A91", 1.7, dash="5 4", casing=2.0, glow=False)])
    out += H.clipped("a1p2", R2, 10, [H.path_line(PATH2, "#6B7A91", 1.7, dash="5 4", casing=2.0, glow=False)])
    out.append(annotations(0, ("M 312 92 C 313.7 93.3 320 97.7 322 100 C 324 102.3 323.6 104.9 324 105.9", "326,112 319.3,105.8 327.6,103"),
                           ("M 408 112 C 409.7 113.3 416.2 117.9 418 120 C 419.8 122.1 418.7 124.1 418.8 124.9", "420,132 413.6,123.9 423.4,122.3"), 80))
    out.append(annotations(0, ("M 310 280 C 312 281.3 319.6 285.7 322 288 C 324.4 290.3 324.1 293.1 324.5 294.1", "327,300 319.9,294.3 328,290.9"),
                           ("M 408 290 C 409.7 291.3 416.2 295.9 418 298 C 419.8 300.1 418.7 302.1 418.8 302.9", "420,310 413.6,301.9 423.4,300.3"), 268))
    for p in PLANES:
        out.append({"name": "sprite-side", **H.LOOK, **p})
    for x, fill in zip(XS, (3.0, 0, 0, 0, 27.6, 27.6)):
        out.append(gauge(x if x != 70 else 70, 158, fill))
    for x, fill in zip(XS, (6.6, 27.6, 27.6, 27.6, 27.6, 27.6)):
        out.append(gauge(x, 362, fill))
    out.append(pill(94, 27, "65") + pill(304, 27, "45") + pill(608, 27, "75") + pill(94, 231, "55") + pill(608, 231, "75"))
    c = S.callout
    out.append("".join(c(k + 1, x, 22) for k, x in enumerate(XS)) + "".join(c(k + 1, x, 226) for k, x in enumerate(XS)))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-28-03-stall-sequences",
        "replaces": "fig-28-03-stall-sequences.svg",
        "book_file": "plate-28-03-stall-sequences.jpg",
        "caption": "Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery",
        "desc": "Figure 28-3. The power-off stall (top) and the power-on stall (bottom), from set-up to recovery",
        "legend": [
            "Set-up. Top: descending at 65 kt, full flap. Bottom: 55 kt (`VR`), takeoff configuration, drawn clean.",
            "Entry. Top: throttle closed, nose raised. Bottom: takeoff power, nose raised past the climb attitude.",
            "The stall: buffet (red), the nose drops. Top: about 45 kt.",
            "Angle of attack reduced first (blue).",
            "Wings level, full power.",
            "Climb at `VY`, 75 kt.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-28-03-stall-sequences.svg", "blank": True, "layers": layers()},
    }
