"""Figure 29-8 (new). The descent to C, from Chapter 29 ("The arrival", the example "Arriving at C"): C is at 2 300 ft and its circuit 1 000 ft above it; from 6 500 ft, 3 200 ft to
lose at 500 ft/min takes 6.4 minutes, about 13 NM at 2 NM a minute; start down 15 NM out, at 09:38, so as to level a few miles before joining.

A profile scene (figs/h_a1.profile: sky, clouds, the plain, C's runway seen edge-on) to scale along the ground and stretched in height: the path in the air as a line with a casing, the
cruise and circuit heights as dashed lines, the model at three places (in the cruise, in the descent, level at circuit height), the two distances and the height to lose as dimension
lines, the digits written on the figure (figs/marks.py); the words are in the legend."""
from figs import h_a1 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 320
BOX = (8, 8, 624, 304)
GY = 262.0                                                  # the ground at C, 2 300 ft
XC, PX_NM = 560.0, 500.0 / 15.0                             # C (its threshold), and the scale along the ground
BLUE, AMBER, INK, GREEN = "#1D4ED8", "#B45309", "#1E293B", "#047857"


def y_ft(ft):
    return GY - (ft - 2300.0) * 180.0 / 4200.0


def x_nm(nm_out):
    return XC - nm_out * PX_NM


X0, X1 = x_nm(15), x_nm(2)                                 # start down 15 NM out; 13 NM later, level about 2 NM out
YC, YL = y_ft(6500), y_ft(3300)


def on_path(x):
    return YC + (x - X0) / (X1 - X0) * (YL - YC)


def layers():
    out = [H.page("v29p", W, HT), H.defs()]
    out += H.profile("v29", BOX, GY, seed=59, sun=(90, 64), runway_args={"x0": 540, "x1": 632, "threshold": True, "half": 4.2, "dash_from": 566},
                     clouds=[H.cloud("cloud-cumulus-a", 420, 92, 70, 0.8), H.cloud("cloud-cumulus-b", 150, 196, 48, 0.75)],
                     acacias=[(250, GY - 4, 0.5), (420, GY - 3, 0.45)])
    # the heights: the cruise and the circuit
    out.append(S.altitude_line(16, 632, YC, "#FFFFFF", 0.85, "5 4", 1.3) + S.altitude_line(X1 - 30, 632, YL, "#FFFFFF", 0.85, "5 4", 1.3))
    # the path: in the cruise, down, level at circuit height
    d = f"M 16 {n(YC)} L {n(X0)} {n(YC)} L {n(X1)} {n(YL)} L 600 {n(YL)}"
    out.append(H.path_line(d, BLUE, 2.6, casing=2.4))
    out.append(H.arrow_head(606, YL, 0, 9, BLUE))
    out.append(f'<circle cx="{n(X0)}" cy="{n(YC)}" r="4.2" fill="#FFFFFF" stroke="{AMBER}" stroke-width="2.2"/><circle cx="{n(X1)}" cy="{n(YL)}" r="4.2" fill="#FFFFFF" stroke="{AMBER}" stroke-width="2.2"/>')
    # the model: in the cruise, in the descent, level at circuit height
    xm = (X0 + X1) / 2
    out.append(H.plane_mid(40, YC + 5, 0, 50))
    out.append(H.plane_mid(xm, on_path(xm) + 5, 4, 50))
    out.append(H.plane_mid(520, YL + 5, 0, 50))
    # the distances, and the height to lose
    out.append(H.dim_line(X0, 26, XC, 26, INK) + H.dim_line(X0, 48, X1, 48, AMBER))
    out.append(f'<line x1="{n(X0)}" y1="18" x2="{n(X0)}" y2="{n(YC - 6)}" stroke="{INK}" stroke-width="1" stroke-dasharray="2 3" stroke-opacity="0.7"/>'
               f'<line x1="{n(XC)}" y1="18" x2="{n(XC)}" y2="{n(GY - 4)}" stroke="{INK}" stroke-width="1" stroke-dasharray="2 3" stroke-opacity="0.7"/>'
               f'<line x1="{n(X1)}" y1="40" x2="{n(X1)}" y2="{n(YL - 6)}" stroke="{AMBER}" stroke-width="1" stroke-dasharray="2 3" stroke-opacity="0.8"/>')
    out.append(H.dim_line(612, YC + 2, 612, YL - 2, INK))
    # the digits
    out.append(M.chip((X0 + XC) / 2, 26, "15 NM", INK, size=9.0)
               + M.chip((X0 + X1) / 2 - 34, 48, "13 NM", AMBER, size=9.0) + M.chip((X0 + X1) / 2 + 34, 48, "6.4 MIN", AMBER, size=9.0, kind="clock")
               + M.chip(X0 + 34, YC - 13, "09:38", AMBER, size=8.8, kind="clock")
               + M.chip(xm + 50, on_path(xm) - 24, "500 FT/MIN", BLUE, size=8.8, kind="down")
               + M.chip(300, YC - 13, "6 500 FT", INK, size=8.8)
               + M.chip(590, (YC + YL) / 2, "3 200 FT", INK, size=8.8)
               + M.chip(462, YL + 16, "3 300 FT", INK, size=8.8)
               + M.chip(586, GY + 22, "2 300 FT", INK, size=8.8))
    out.append(H.foreground("v29", BOX, GY, seed=59, lights=(540, 632), scrub=10, scale=1.2))
    c = S.callout
    out.append(c(1, 30, YC + 34, 38, YC + 10) + c(2, X0 + 42, YC + 30, X0 + 3, YC + 4) + c(3, xm - 46, on_path(xm) + 34, xm - 24, on_path(xm - 24) + 2)
               + c(4, 500, YL - 30, 512, YL - 3) + c(5, 528, GY + 26, 548, GY))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-29-08-arrival-descent",
        "replaces": "fig-29-08-arrival-descent.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-29-08-arrival-descent.jpg",
        "caption": "Figure 29-8. The descent to C: when to start down",
        "desc": ("Figure 29-8. A profile of the arrival at C, to scale along the ground and stretched in height: in the cruise at 6 500 ft, start down 15 NM out at 09:38; "
                 "3 200 ft at 500 ft/min takes 6.4 minutes, about 13 NM at 2 NM a minute; level at the circuit height, 3 300 ft, a few miles before joining. C is at 2 300 ft."),
        "legend": [
            "In the cruise at 6 500 ft.",
            "Start down 15 NM out, at 09:38.",
            "3 200 ft to lose at 500 ft/min: 6.4 minutes; at 2 NM a minute, about 13 NM.",
            "Level at circuit height, 3 300 ft, a few miles before joining.",
            "C: 2 300 ft; the circuit is 1 000 ft above it.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
