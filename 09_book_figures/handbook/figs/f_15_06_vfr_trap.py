"""Figure 15-6 (new). The trap of deteriorating weather, from Chapter 15 ("The trap of deteriorating weather"): weather rarely turns bad all at once; the cloud
lowers, the visibility shrinks, and a pilot who wants to get home flies a little lower and a little further, until there is no horizon and no way back; the best escape is the 180°
turn, made early, while the horizon and the ground are still in sight, back to where the weather is better.

One profile scene, read from left to right: a clear sky over the desert that greys towards the right; a cloud deck whose base comes down across the picture (a textured grey
layer cut by a soft noise edge) and a veil of murk below it that thickens to the right until the ground and the hills fade; the path that presses on (red), stepping lower under the
base and ending in the murk; and the path that turns back (green), a half turn drawn as a loop seen from the side, with the model heading back towards the clear sky. The cloud base
and the heights are not to scale; the words are in the legend."""
from figs import h_a1 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 330
BOX = (8, 8, 624, 314)
GY = 266.0
GREEN, RED, INK = "#047857", "#B91C1C", "#1E293B"
BASE = [(8, 58), (120, 62), (230, 82), (330, 112), (430, 150), (530, 186), (632, 210)]            # the cloud base, lowering to the right


def deck():
    """The cloud deck above the lowering base: grey, darker towards the right, with a soft ragged lower edge."""
    top = [(632, 8), (8, 8)]
    poly = BASE + top
    edge = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in BASE)
    return (f'<defs>{S.gradient("vt15d", [(0, "#DCE3EC", 0.92), (0.45, "#AEB8C6", 0.96), (1, "#7C8796", 0.98)], 0, 0, 1, 0)}'
            '<filter id="vt15n" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.02 0.06" numOctaves="4" seed="15" result="t"/>'
            '<feDisplacementMap in="SourceGraphic" in2="t" scale="26" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="2.2"/></filter>'
            '<filter id="vt15m" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.014 0.045" numOctaves="4" seed="4"/>'
            '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.1 -0.42"/><feGaussianBlur stdDeviation="1.2"/></filter>'
            f'<clipPath id="vt15c"><polygon points="{S.pts(poly)}"/></clipPath></defs>'
            f'<polygon points="{S.pts(poly)}" fill="url(#vt15d)" filter="url(#vt15n)"/>'
            f'<g clip-path="url(#vt15c)"><rect x="8" y="8" width="624" height="210" filter="url(#vt15m)" opacity="0.5"/></g>'
            f'<path d="{edge}" fill="none" stroke="#5F6B7B" stroke-opacity="0.5" stroke-width="5" filter="url(#vt15n)"/>')


def murk():
    """The visibility shrinking to the right: a veil below the base that thickens until the ground and the hills fade into it."""
    return (f'<defs>{S.gradient("vt15v", [(0, "#C9D1DB", 0.0), (0.3, "#C9D1DB", 0.0), (0.62, "#C2CAD4", 0.55), (0.82, "#B6BEC9", 0.9), (1, "#AEB6C1", 0.97)], 0, 0, 1, 0)}</defs>'
            '<rect x="8" y="8" width="624" height="314" fill="url(#vt15v)"/>')


def layers():
    out = [H.page("vt15p", W, HT), H.defs()]
    out += H.profile("vt15", BOX, GY, seed=157, sun=(90, 60), clouds=[H.cloud("cloud-cumulus-a", 64, 206, 44, 0.85)], palms=[(60, GY - 5, 0.5)], acacias=[(190, GY - 4, 0.5)], far=30.0, mid=14.0)
    out.append(S.card_front("vt15f", *BOX, deck() + murk()))
    # the path that presses on: a little lower and a little further, into the murk
    press = "M 200 142 C 250 142 262 168 300 168 L 356 168 C 396 168 404 204 440 204 L 486 204 C 520 204 528 232 556 232 L 596 232"
    out.append(H.path_line("M 24 142 L 200 142", INK, 2.6, casing=2.4))
    out.append(H.path_line(press, RED, 2.6, casing=2.4))
    out.append(H.arrow_head(602, 232, 0, 8.5, RED))
    # the path that turns back early: a half turn seen from the side, back towards the clear sky
    back = "M 200 142 C 262 142 286 132 286 118 C 286 104 250 98 196 98 L 60 98"
    out.append(H.path_line(back, GREEN, 2.8, casing=2.4))
    out.append(H.arrow_head(54, 98, 180, 9, GREEN))
    out.append(f'<circle cx="200" cy="142" r="4.6" fill="#FFFFFF" stroke="{GREEN}" stroke-width="2.4"/>')
    # the model: before the decision, turned back (heading left), and pressing on lower and lower, fading
    out.append(H.plane_mid(96, 147, 0, 46))
    out.append(H.plane_mid(130, 103, 0, 46, flip=True, tint="#0E9F6E", tint_strength=0.4))
    out.append(H.plane_mid(330, 173, 2, 42, opacity=0.9))
    out.append(H.plane_mid(462, 209, 3, 40, opacity=0.6))
    out.append(H.plane_mid(578, 237, 4, 38, opacity=0.32))
    out.append(M.chip(292, 96, "180°", GREEN, size=10.0) + M.chip(520, 246, "10 MIN", RED, size=8.6, kind="clock"))
    out.append(H.foreground("vt15", BOX, GY, seed=157, scrub=9, scale=1.2))
    c = S.callout
    out.append(c(1, 384, 96, 372, 128) + c(2, 322, 204, 330, 178) + c(3, 606, 196, 590, 226) + c(4, 236, 176, 204, 146) + c(5, 34, 66, 52, 92))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-15-06-vfr-trap",
        "replaces": "fig-15-06-vfr-trap.svg",                   # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-15-06-vfr-trap.jpg",
        "caption": "Figure 15-6. The trap of deteriorating weather: press on, or turn back early",
        "desc": ("Figure 15-6. A profile from clear weather on the left to low cloud and poor visibility on the right. One aeroplane presses on, a little lower and a little further "
                 "under the lowering cloud base, until it is in the murk with no horizon; the other makes a 180° turn early and flies back to the better weather."),
        "legend": [
            "The cloud lowers and the visibility shrinks, little by little.",
            "Pressing on: a little lower and a little further, to keep the ground in sight.",
            "No horizon and no way back: a pilot without instrument training loses control in about 10 minutes.",
            "The 180° turn, made early, while you can still see the horizon and the ground.",
            "Back to where the weather is better, to land there.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
