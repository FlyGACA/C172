"""Figure 12-1. Datum, stations and arms of the example aeroplane. The model's aeroplane (sprite-side-left: nose to the left, as in the old figure) parked on an apron under far hills and
sky, the datum at the firewall as a glowing orange plumb line, the four stations (front seats, fuel tanks in the wing, rear seats, baggage) as blue beads on the aeroplane with dashed drops
to measuring tapes (yellow tapes with their ticks, hooked on the datum and ending at each arm: 2.30, 2.60, 3.25 and 3.90 m, 62 units to the metre as in the old figure), and under them the
scale in metres on a ruler (-1 to 4, plus and minus at its ends). The seven numbered callouts of the old figure are kept."""
from figs import scene as S
from figs import h_a3 as H
from reskin import LOOK

n = S.n
U = "f1201"
DATUM_X = 118.0
PER_M = 62.0
ARMS = [(2.30, 298, 260.6, 150), (2.60, 278, 279.2, 100), (3.25, 258, 319.5, 150), (3.90, 238, 359.8, 158)]       # arm, y of its tape, x of the station, y of its bead
INK = "#334155"


def gradients():
    g = S.gradient
    return ("<defs>"
            + g(U + "tape", [(0, "#FFE690"), (0.45, "#F7C12A"), (1, "#C28A06")])
            + g(U + "rul", [(0, "#FFFFFF"), (0.5, "#E4EAF3"), (1, "#AEB9CC")])
            + g(U + "steel", [(0, "#FFFFFF"), (0.5, "#C3CCDA"), (1, "#6B7890")])
            + g(U + "datum", [(0, "#FFC06A"), (0.5, "#F08A12"), (1, "#C26106")], 0, 0, 1, 0)
            + g(U + "apron", [(0, "#BAC1CD"), (1, "#8E97A8")])
            + g(U + "paper", [(0, "#FBFCFE"), (1, "#E9EFF7")])
            + "</defs>")


def scene():
    x, y, w = 8, 8, 624
    hz = 216
    sky = S.sky(U + "sk", x, y, w, hz - y, [(0.0, "#78A8DC"), (0.6, "#B9D4EE"), (1.0, "#F3F1E2")])
    hills = (S.land_layer(U + "h1", S.ridge(5, x, x + w, hz - 4, 46, peaks=0.6), hz, ("#7F8FB6", "#B4C0D8"), rim=False, haze=0.28)
             + S.land_layer(U + "h2", S.ridge(9, x, x + w, hz - 2, 22, peaks=0.35), hz, ("#9AA7C4", "#C9D2E3"), rim=False, haze=0.18))
    sand = (f'<defs>{S.gradient(U + "sd", [(0, "#EADBB4"), (1, "#D4BC8A")])}</defs><rect x="{x}" y="{hz - 6}" width="{w}" height="14" fill="url(#{U}sd)"/>'
            + S.scrub(3, x, x + w, hz - 4, hz + 6, 10, colour=("#8A8A55", "#5E603E"), scale=0.55)
            + S.palm(34, hz - 2, 30, 0.1, 3) + S.palm(612, hz - 1, 27, -0.1, 5) + S.house(552, hz - 3, 22, 12, 2))
    apron = (f'<rect x="{x}" y="{hz + 2}" width="{w}" height="18" fill="url(#{U}apron)"/><line x1="{x}" y1="{hz + 2.5}" x2="{x + w}" y2="{hz + 2.5}" stroke="#E6EAF0" stroke-opacity="0.8" stroke-width="1"/>'
             f'<ellipse cx="308" cy="{hz + 8}" rx="262" ry="5.4" fill="#2C3548" fill-opacity="0.30" filter="url(#{U}b2)"/>')
    paper = (f'<rect x="{x}" y="{hz + 20}" width="{w}" height="{352 - hz - 20}" fill="url(#{U}paper)"/>'
             + "".join(f'<line x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}" stroke="#B9C6DB" stroke-opacity="0.35" stroke-width="0.6"/>' for yy in range(246, 352, 20))
             + "".join(f'<line x1="{xx}" y1="{hz + 20}" x2="{xx}" y2="352" stroke="#B9C6DB" stroke-opacity="0.35" stroke-width="0.6"/>' for xx in range(26, 632, 62)))
    return S.card(U + "c", 8, 8, 624, 344, [(0, "#F3F1E2"), (1, "#E9EFF7")], sky + hills + sand + apron + paper)


def tape(arm, y, sx):
    """A measuring tape from the datum to a station: a yellow strip with a steel hook on the datum, a tick every 0.1 m (longer at 0.5 and 1 m) and a steel pointer at its end."""
    x0, x1 = DATUM_X, DATUM_X + arm * PER_M
    h = 7.0
    out = [f'<rect x="{n(x0)}" y="{n(y - h / 2 + 1.6)}" width="{n(x1 - x0)}" height="{h}" rx="1.6" fill="#14233F" fill-opacity="0.22" filter="url(#{U}b1)"/>',
           f'<rect x="{n(x0)}" y="{n(y - h / 2)}" width="{n(x1 - x0)}" height="{h}" rx="1.6" fill="url(#{U}tape)" stroke="#8A5E00" stroke-width="0.8"/>',
           f'<rect x="{n(x0 + 1)}" y="{n(y - h / 2 + 0.8)}" width="{n(x1 - x0 - 2)}" height="1.3" rx="0.6" fill="#FFFFFF" fill-opacity="0.65"/>']
    ticks = []
    for k in range(1, int(arm * 10) + 1):
        tx = x0 + k * PER_M / 10.0
        ln = 5.8 if k % 10 == 0 else 4.0 if k % 5 == 0 else 2.4
        ticks.append(f'<line x1="{n(tx)}" y1="{n(y + h / 2)}" x2="{n(tx)}" y2="{n(y + h / 2 - ln)}" stroke="#3B2A00" stroke-opacity="0.75" stroke-width="0.7"/>')
    out.append("".join(ticks))
    out.append(f'<path d="M {n(x0 - 2.6)},{n(y - 5.6)} L {n(x0 + 1.4)},{n(y - 5.6)} L {n(x0 + 1.4)},{n(y + 5.6)} L {n(x0 - 2.6)},{n(y + 5.6)} Z" fill="url(#{U}steel)" stroke="#4B586E" stroke-width="0.8"/>')
    out.append(f'<polygon points="{S.pts([(x1 + 8, y), (x1, y - 4.6), (x1, y + 4.6)])}" fill="url(#{U}steel)" stroke="#4B586E" stroke-width="0.8" stroke-linejoin="round"/>')
    out.append(f'<text x="{n(x1 + 14)}" y="{n(y + 4.2)}" font-family="sans-serif" font-size="12" fill="{INK}" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">{arm:.2f}</text>')
    return "".join(out)


def drop(sx, sy, y):
    """A dashed drop from a bead on the aeroplane to the end of its tape, white-edged so that it reads over the aeroplane, with the bead."""
    return (f'<line x1="{n(sx)}" y1="{n(sy + 5)}" x2="{n(sx)}" y2="{n(y - 5)}" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.85" stroke-linecap="round"/>'
            f'<line x1="{n(sx)}" y1="{n(sy + 5)}" x2="{n(sx)}" y2="{n(y - 5)}" stroke="#46556E" stroke-width="1.2" stroke-dasharray="3 3" stroke-linecap="round"/>')


def bead(i, sx, sy):
    return H.ball(f"{U}bd{i}", sx, sy, 5.6, "#DCE9FF", "#3F78D0", "#183F8C", rim="#FFFFFF", p=U)


def datum():
    return (f'<line x1="{DATUM_X}" y1="44" x2="{DATUM_X}" y2="330" stroke="#FFB45A" stroke-opacity="0.35" stroke-width="9" stroke-linecap="round" filter="url(#{U}b2)"/>'
            f'<rect x="{DATUM_X - 2.2}" y="44" width="4.4" height="286" rx="2.2" fill="url(#{U}datum)" stroke="#8F4300" stroke-width="0.6"/>'
            f'<rect x="{DATUM_X - 1.2}" y="46" width="1.2" height="282" rx="0.6" fill="#FFFFFF" fill-opacity="0.55"/>')


def ruler():
    y = 330.0
    body = [(40, y), (50, y - 5.5), (424.5, y - 5.5), (434.5, y), (424.5, y + 5.5), (50, y + 5.5)]
    out = [f'<polygon points="{S.pts(body)}" fill="#14233F" fill-opacity="0.22" transform="translate(0.8 2)" filter="url(#{U}b1)"/>',
           f'<polygon points="{S.pts(body)}" fill="url(#{U}rul)" stroke="#6B7890" stroke-width="0.9" stroke-linejoin="round"/>']
    for k in range(-10, 41):
        x = DATUM_X + k * PER_M / 10.0
        if x < 52 or x > 424:
            continue
        ln = 5.0 if k % 10 == 0 else 3.2 if k % 5 == 0 else 1.8
        out.append(f'<line x1="{n(x)}" y1="{y - 5.5 + 0.8}" x2="{n(x)}" y2="{n(y - 5.5 + 0.8 + ln)}" stroke="#46556E" stroke-width="0.7"/>')
    for k, (num, yy) in enumerate([(-1, 348), (0, 322), (1, 348), (2, 348), (3, 348), (4, 348)]):
        x = DATUM_X + num * PER_M
        label = "−1" if num < 0 else str(num)
        out.append(f'<line x1="{n(x)}" y1="{y - 5.5}" x2="{n(x)}" y2="{y + 5.5}" stroke="#2B3750" stroke-width="1.3"/>')
        xx = x + (9 if num == 0 else 0)
        out.append(f'<text x="{n(xx)}" y="{n(yy)}" font-family="sans-serif" font-size="11" fill="{INK}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">{label}</text>')
    out.append(f'<text x="444.2" y="335" font-family="sans-serif" font-size="16" font-weight="bold" fill="{INK}">+</text><text x="30.5" y="335" font-family="sans-serif" font-size="16" font-weight="bold" fill="{INK}" text-anchor="end">−</text>')
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 118, 30), c(2, 312.6, 298), c(3, 331.2, 278), c(4, 371.5, 258), c(5, 411.8, 238), c(6, 474.2, 330), c(7, 79.6, 92, 79.6, 123)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', H.common_defs(U), gradients(), scene(),
              {"name": "sprite-side-left", "at": [305.5, 142.8], "width": 536.0, "px": 3.0, "shadow": {"dx": 1.2, "dy": 2.0, "blur": 1.8, "opacity": 0.22}},
              datum(), "".join(drop(sx, sy, y) for arm, y, sx, sy in ARMS), "".join(tape(arm, y, sx) for arm, y, sx, sy in ARMS), "".join(bead(i, sx, sy) for i, (arm, y, sx, sy) in enumerate(ARMS)),
              ruler(), callouts()]
    return {
        "id": "fig-12-01-datum-arm-moment",
        "replaces": "fig-12-01-datum-arm-moment.svg",
        "book_file": "plate-12-01-datum-arm-moment.jpg",
        "caption": "Figure 12-1. Datum, stations and arms of the example aeroplane",
        "desc": "Figure 12-1. Datum, stations and arms of the example aeroplane",
        "legend": [
            "The datum: the front face of the firewall, arm 0.",
            "Front seats, arm 2.30 m.",
            "Fuel tanks in the wing, arm 2.60 m.",
            "Rear seats, arm 3.25 m.",
            "Baggage compartment, arm 3.90 m.",
            "Arms aft of the datum are positive. The scale is in metres.",
            "Items ahead of the datum, such as the engine, have negative arms. Their moments are already counted in the basic empty mass.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-12-01-datum-arm-moment.svg", "blank": True, "layers": layers},
    }
