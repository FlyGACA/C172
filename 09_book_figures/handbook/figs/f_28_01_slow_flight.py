"""Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve. Left, two scenes in cards: the model seen from the right in cruise and in
slow flight with full flap, over a desert horizon (the chord line dashed, the level flight path as a green arrow, the angle of attack between them in amber, the throttle as a small
slider); right, the power-required curve in a card (the region of reversed command as a pale block, the dashed VS0 line, the minimum, the two points with their arrows). The nine
numbered callouts of the old figure are kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

C1 = (8, 12, 318, 160)
C2 = (8, 180, 318, 192)
CH = (336, 12, 296, 356)
H1, H2 = 97.0, 252.0                     # the horizon of each card: the level of the flight path
W = 236.0
BLUE, AMBER, GREEN, RED = "#1D4ED8", "#B45309", "#047857", "#B91C1C"

AOA = 'M 278.5 250.6 C 278.5 250.2 278.5 249.3 278.5 248.6 C 278.5 248 278.5 247.3 278.5 246.7 C 278.4 246.1 278.4 245.4 278.4 244.8 C 278.3 244.1 278.3 243.5 278.2 242.9 C 278.2 242.2 278.1 241.6 278 240.9 C 278 240.3 277.9 239.7 277.8 239 C 277.7 238.4 277.6 237.8 277.6 237.1 C 277.5 236.5 277.4 235.8 277.2 235.2 C 277.1 234.6 277 233.9 276.9 233.3 C 276.8 232.7 276.6 231.7 276.5 231.4'
CURVE = 'M 394.1 205.7 C 395.2 207.9 398.8 214.8 401.1 218.8 C 403.4 222.8 405.8 226.5 408.1 229.9 C 410.5 233.3 412.8 236.4 415.2 239.3 C 417.5 242.2 419.8 244.7 422.2 247.1 C 424.5 249.5 426.9 251.6 429.2 253.5 C 431.6 255.4 433.9 257 436.2 258.5 C 438.6 260 440.9 261.2 443.3 262.3 C 445.6 263.4 448 264.3 450.3 265 C 452.7 265.7 455 266.2 457.3 266.5 C 459.7 266.9 462 267 464.4 267 C 466.7 267 469.1 266.9 471.4 266.5 C 473.8 266.2 476.1 265.7 478.4 265.1 C 480.8 264.4 483.1 263.6 485.5 262.6 C 487.8 261.7 490.2 260.6 492.5 259.3 C 494.8 258 497.2 256.6 499.5 255 C 501.9 253.5 504.2 251.7 506.6 249.9 C 508.9 248 511.2 246 513.6 243.8 C 515.9 241.7 518.3 239.3 520.6 236.9 C 523 234.4 525.3 231.8 527.7 229.1 C 530 226.3 532.3 223.4 534.7 220.3 C 537 217.3 539.4 214.1 541.7 210.8 C 544.1 207.4 546.4 203.9 548.8 200.3 C 551.1 196.6 553.4 192.8 555.8 188.9 C 558.1 185 560.5 180.9 562.8 176.6 C 565.2 172.4 567.5 168 569.8 163.5 C 572.2 158.9 574.5 154.2 576.9 149.4 C 579.2 144.5 581.6 139.5 583.9 134.4 C 586.2 129.2 588.6 123.9 590.9 118.4 C 593.3 113 596.8 104.4 598 101.6'
TOWARDS = 'M 447.5 254 C 445.6 253.1 440 250.9 436.2 248.5 C 432.5 246.1 428.8 243.3 425 239.8 C 421.2 236.3 416.4 230.7 413.8 227.6 C 411.1 224.4 409.8 222 409 220.9'
AWAY = 'M 503.8 242 C 507.5 238.5 518.8 229.3 526.2 220.7 C 533.8 212.1 541.2 201.9 548.8 190.3 C 556.2 178.6 565.6 161.3 571.2 150.7 C 576.9 140.2 580.7 131 582.6 127'


def scene(uid, box, horizon, seed, clouds):
    x, y, w, h = box
    return H.profile(uid, box, horizon + 13, seed=seed, sun=(60, 40), far=22, mid=10, base=13, sky=H.horizon_sky((horizon - y) / h), clouds=clouds, scrub_count=10, grain=False)


def throttle(x, y, fill):
    """The throttle position as a small slider: a white rounded case and a grey column rising to the lever."""
    return (f'<rect x="{x}" y="{y}" width="12" height="48" rx="3" fill="#FFFFFF" fill-opacity="0.95" stroke="#1F2937" stroke-width="1.2" filter="url(#a1ds)"/>'
            f'<defs>{S.gradient("a1thr" + str(int(y)), [(0, "#8A95A8"), (1, "#5B6578")], 0, 0, 1, 0)}</defs>'
            f'<rect x="{x + 1.5}" y="{y + 45 - fill - 1.5}" width="9" height="{fill}" rx="1.5" fill="url(#a1thr{int(y)})"/>'
            f'<rect x="{x + 1.5}" y="{y + 45 - fill - 1.5}" width="9" height="1.6" fill="#1F2937"/>')


def chord_and_path(x0, y0, chord_end, path_end, head):
    out = [H.line_cased(x0, y0, chord_end[0], chord_end[1], "#1F2937", 1.4, dash="4 3", casing=2.2),
           H.line_cased(x0 + 4, y0, path_end - 8, y0, GREEN, 2.6, casing=2.4),
           f'<polygon points="{head}" fill="{GREEN}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" paint-order="stroke"/>']
    return "".join(out)


def chart():
    x, y, w, h = CH
    out = [S.card("a1ch", x, y, w, h, [(0, "#F9FBFE"), (1, "#E6EEF7")], "", radius=10)]
    out.append(f'<defs>{S.gradient("a1rev", [(0, "#FDEBD0"), (1, "#F8D4A0")], 0, 0, 1, 0)}</defs>'
               f'<rect x="394.1" y="62" width="70.3" height="258" fill="url(#a1rev)" opacity="0.85"/>'
               f'<rect x="394.1" y="62" width="70.3" height="258" fill="none" stroke="#FFFFFF" stroke-width="1" stroke-opacity="0.8"/>')
    out.append(H.line_cased(394.1, 62, 394.1, 320, RED, 2.0, dash="5 4", casing=2.2))
    out.append(H.line_cased(464.4, 273, 464.4, 320, "#7B8799", 1.2, dash="3 3", casing=1.8))
    out.append('<line x1="370" y1="320" x2="607.8" y2="320" stroke="#1F2937" stroke-width="1.8" stroke-linecap="round"/><polygon points="615,320 606,324.9 606,315.1" fill="#1F2937"/>'
               '<line x1="370" y1="320" x2="370" y2="62.2" stroke="#1F2937" stroke-width="1.8" stroke-linecap="round"/><polygon points="370,55 374.9,64 365.1,64" fill="#1F2937"/>')
    out.append('<text x="394.1" y="338" font-family="monospace" font-size="12" fill="#1F2937" text-anchor="middle">VS0</text>')
    out.append(H.path_line(CURVE, BLUE, 3.0, casing=2.6))
    out.append(H.path_line(TOWARDS, AMBER, 2.2, casing=2.2, glow=False) + H.arrow_head(405.3, 215.7 - 0.0, -140, 10, AMBER) if False else H.path_line(TOWARDS, AMBER, 2.2, casing=2.2, glow=False))
    out.append('<polygon points="405.3,215.7 413.5,219.7 406.4,224.8" fill="#B45309" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" paint-order="stroke"/>')
    out.append(H.path_line(AWAY, GREEN, 2.2, casing=2.2, glow=False))
    out.append('<polygon points="585.3,121.3 585.8,130.4 577.9,126.6" fill="#047857" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" paint-order="stroke"/>')
    for (cx, cy, col, uid) in ((422.2, 247.1, AMBER, "a1pa"), (562.8, 176.6, GREEN, "a1pg")):
        out.append(f'<defs><radialGradient id="{uid}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.9"/><stop offset="0.35" stop-color="{col}"/><stop offset="1" stop-color="{col}"/></radialGradient></defs>'
                   f'<circle cx="{cx}" cy="{cy}" r="8.5" fill="#10233F" opacity="0.18" transform="translate(0.8 1.8)"/><circle cx="{cx}" cy="{cy}" r="6.6" fill="#FFFFFF"/><circle cx="{cx}" cy="{cy}" r="5.4" fill="url(#{uid})"/>')
    return out


def callouts():
    c = S.callout
    return "".join([c(1, 54, 52, 112, 76), c(2, 54, 212, 112, 236), c(3, 298.5, 210.6, 280.5, 238.6), c(4, 34, 36, 34, 82),
                    c(5, 560, 70, 588.1, 120.9), c(6, 490.4, 300, 466.4, 275), c(7, 427.8, 80), c(8, 412.2, 287.1, 420.2, 254.1), c(9, 372.1, 300, 392.1, 290)])


def layers():
    out = [H.page("a1page", 640, 380), H.defs()]
    out += scene("a1s1", C1, H1, 61, [H.cloud("cloud-cumulus-b", 250, 36, 62), H.cloud("cloud-cumulus-a", 130, 30, 52, 0.85)])
    out += scene("a1s2", C2, H2, 67, [H.cloud("cloud-cumulus-a", 238, 204, 66), H.cloud("cloud-cumulus-b", 112, 202, 50, 0.85)])
    out.append(H.plane_c(196, 95.7, 0.63, W))
    out.append(H.plane_c(193, 250.6, -9.91, W))
    out.append(chord_and_path(196, 95.7, (316, 92.6), 321.6, "321.6,95.7 312.4,100.8 312.4,90.7"))
    out.append(chord_and_path(193, 250.6, (310.4, 225.6), 318.5, "318.5,250.6 309.3,255.6 309.3,245.5"))
    out.append(H.path_line(AOA, AMBER, 2.6, casing=2.2, glow=False))
    out.append(throttle(28, 86, 33.6))
    out.append(throttle(28, 246, 27.4))
    out += chart()
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-28-01-slow-flight",
        "replaces": "fig-28-01-slow-flight.svg",
        "book_file": "plate-28-01-slow-flight.jpg",
        "caption": "Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve",
        "desc": "Figure 28-1. Slow flight: attitude, angle of attack and power, and where slow flight sits on the power curve",
        "legend": [
            "Cruise: nose near the horizon, cruise power.",
            "Slow flight with full flap: nose high, altitude held.",
            "The angle of attack between the chord line (dashed) and the level flight path (green): large.",
            "Throttle position.",
            "Power required for level flight against airspeed; schematic, not the example aeroplane's data.",
            "Minimum power.",
            "The region of reversed command.",
            "Slow flight (amber point); cruise is the green point.",
            "`VS0`, 45 kt.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-28-01-slow-flight.svg", "blank": True, "layers": layers()},
    }
