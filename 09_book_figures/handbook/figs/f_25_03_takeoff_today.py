"""Figure 25-3. Today's takeoff from aerodrome A, morning and afternoon, against the runway. Drawn again as two scenes (the old figure was a strip and two bars): the
runway of 1 200 m seen edge-on at the scale of the old figure (504 units for 1 200 m), rising 1% towards its end (exaggerated), with the takeoff over it twice: at 07:30 and 25° under
a clear morning sky, at 13:00 and 40° under the pale, hazy sky of a hot afternoon. In each: the ground roll as a dark line on the runway, the climb to 15 m (50 ft) as a path in the
air (heights exaggerated), the 50% margin as a pale band along the runway, and what is left of the runway written at its end. The numbers are those of the old figure."""
from figs import h_a1 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 336
X0, X1 = 76.0, 580.0
K = (X1 - X0) / 1200.0                                     # units per metre
SLOPE = 7.0                                                 # the rise over the runway, exaggerated
BLUE, INK, GREEN, RED, AMBER = "#1D4ED8", "#1E293B", "#047857", "#B91C1C", "#B45309"
HAZE = [(0.0, "#9DB7D6"), (0.55, "#D3DEEA"), (1.0, "#F4EBD8")]
ROWS = [(8.0, "07:30", "25°", 368, 672, H.SKY, "192", GREEN), (172.0, "13:00", "40°", 436, 798, HAZE, "3", RED)]


def gy_at(gy, x):
    return gy - (x - X0) / (X1 - X0) * SLOPE


def runway(gy):
    a, b = (X0, gy), (X1, gy - SLOPE)
    out = [f'<polygon points="{n(X0 - 2)},{n(gy + 3.2)} {n(X1 + 2)},{n(gy - SLOPE + 3.2)} {n(X1 + 2)},{n(gy - SLOPE - 3.2)} {n(X0 - 2)},{n(gy - 3.2)}" fill="#C9B48A" opacity="0.8"/>',
           f'<polygon points="{n(X0)},{n(gy + 2.4)} {n(X1)},{n(gy - SLOPE + 2.4)} {n(X1)},{n(gy - SLOPE - 2.4)} {n(X0)},{n(gy - 2.4)}" fill="#3F4756"/>']
    for i in range(8, 100, 6):
        x = X0 + (X1 - X0) * i / 100
        out.append(f'<line x1="{n(x)}" y1="{n(gy_at(gy, x))}" x2="{n(x + 9)}" y2="{n(gy_at(gy, x + 9))}" stroke="#FFFFFF" stroke-width="0.9"/>')
    out.append(f'<line x1="{n(X1)}" y1="{n(gy - SLOPE - 3)}" x2="{n(X1)}" y2="{n(gy - SLOPE + 3)}" stroke="#FFFFFF" stroke-width="2"/>')
    return "".join(out)


def row(y, time, temp, roll, fifty, sky, left, col):
    box = (8.0, y, 624.0, 156.0)
    gy = y + 116.0
    xr, xf, xm = X0 + roll * K, X0 + fifty * K, X0 + fifty * 1.5 * K
    out = H.profile(f"t25{int(y)}", box, gy + 2, seed=25 + int(y), sun=(560 if y < 100 else 300, 40), clouds=[], objects=runway(gy), sky=sky, scrub_count=10)
    # the margin: a pale band along the runway to 1.5 times the distance to 50 ft; the end of the margin
    out.append(f'<polygon points="{n(xf)},{n(gy_at(gy, xf) - 4)} {n(xm)},{n(gy_at(gy, xm) - 4)} {n(xm)},{n(gy_at(gy, xm) + 4)} {n(xf)},{n(gy_at(gy, xf) + 4)}" fill="#F6B36B" opacity="0.75"/>'
               f'<line x1="{n(xm)}" y1="{n(gy_at(gy, xm) - 14)}" x2="{n(xm)}" y2="{n(gy_at(gy, xm) + 6)}" stroke="{AMBER}" stroke-width="2"/>')
    # the ground roll and the climb to 50 ft
    out.append(f'<line x1="{n(X0)}" y1="{n(gy - 1)}" x2="{n(xr)}" y2="{n(gy_at(gy, xr) - 1)}" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.8"/>'
               f'<line x1="{n(X0)}" y1="{n(gy - 1)}" x2="{n(xr)}" y2="{n(gy_at(gy, xr) - 1)}" stroke="{BLUE}" stroke-width="3"/>')
    top = gy_at(gy, xf) - 34
    out.append(H.path_line(f"M {n(xr)} {n(gy_at(gy, xr) - 1)} Q {n((xr + xf) / 2)} {n(gy_at(gy, xr) - 2)} {n(xf)} {n(top)}", BLUE, 2.4, dash="6 4", casing=2.2))
    out.append(f'<line x1="{n(xf)}" y1="{n(top)}" x2="{n(xf)}" y2="{n(gy_at(gy, xf))}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="2 2"/>')
    out.append(H.plane_mid(xf + 6, top + 4, -8, 40))
    # the numbers
    out.append(M.chip(36, y + 24, time, INK, size=8.6, kind="clock") + M.chip(36, y + 42, temp, INK, size=8.6))
    out.append(M.chip((X0 + xr) / 2, gy + 20, str(roll), BLUE, size=8.4) + M.chip(xf, gy + 20, str(fifty), INK, size=8.4)
               + M.chip(xm, gy + 20, f"{fifty * 3 // 2:,}".replace(",", " "), AMBER, size=8.4) + M.chip(608, gy - SLOPE - 18, left, col, size=10.0))
    return out


def layers():
    out = [H.page("t25p", W, HT), H.defs()]
    for r in ROWS:
        out += row(*r)
    gy = ROWS[0][0] + 116.0
    out.append(M.chip(X1, gy - SLOPE + 20, "1 200", INK, size=8.0))
    # the takeoff direction, and the wedge of the upslope at the end of the runway
    out.append(M.arrow(X0 + 8, gy - 16, X0 + 70, gy - 17.5, INK, width=2.2))
    out.append(f'<polygon points="{n(X1 - 70)},{n(gy_at(gy, X1 - 70) + 3)} {n(X1)},{n(gy_at(gy, X1) + 3)} {n(X1)},{n(gy + 3)}" fill="#B45309" opacity="0.55" stroke="#FFFFFF" stroke-width="0.8"/>')
    c = S.callout
    out.append(c(1, 50, 96, X0 + 10, 107) + c(2, 196, 96, 172, 122) + c(3, 300, 64, 358, 84) + c(4, 470, 100, 480, 117) + c(5, 612, 316, X1, 286))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-25-03-takeoff-today",
        "replaces": "fig-25-03-takeoff-today.svg",
        "book_file": "plate-25-03-takeoff-today.jpg",
        "caption": "Figure 25-3. Today's takeoff from aerodrome A, morning and afternoon, against the runway",
        "desc": "Figure 25-3. Today's takeoff from aerodrome A, morning and afternoon, against the runway",
        "legend": [
            "Runway, 1 200 m. The arrow shows the takeoff direction; the wedge, the 1% upslope (exaggerated).",
            "Ground roll.",
            "Distance to clear 15 m (50 ft).",
            "The 50% margin.",
            "End of the runway.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-25-03-takeoff-today.svg", "blank": True, "layers": layers()},
    }
