"""Figure 19-6 (new: the chapter's only circuit on the radio is at an aerodrome with a tower). With no tower: what a flight at Thumamah (OETH) broadcasts, where, and on which frequency.

The map is the one of Figure 18-8 (the same frame and the same open satellite picture: Copernicus Sentinel-2; "Contains modified Copernicus Sentinel data 2026"), true north up,
47 canvas units to the NM, with the ATZ, the runway, the left-hand circuit of runway 35, the departure of runway 35 to the North VRP and the arrival from the East VRP as
figs/f_18_08_local_procedures.py lays them out (the tracks are that figure's reading of the AIP's words; the circuit's size is illustrative).

What is drawn over it is the AIP's (AMDT 11/26), in the order of a flight:
  ENR 1.1.5.2    all pilots: keep a continuous listening watch and broadcast position and intended movements before manoeuvring, as applicable; before departure keep a listening
                 watch for at least five minutes and broadcast taxi movements before manoeuvring; broadcast position and intentions before crossing or entering a runway for
                 take-off and again before the take-off roll; broadcast when airborne, when leaving the traffic circuit and when leaving the ATZ
  AD 2 OETH 2.18 THUMAMAH UNICOM 124.400 MHZ, 0300 - 1500; "FREQ 124.4 is only apply for traffic flying within OETH ATZ"; traffic inbound in Class G airspace applies TIBA
                 122.8 and listens, watches and broadcasts traffic information on 124.4 before entering the ATZ; traffic leaving the ATZ through Class G airspace broadcasts on
                 122.8 before departure; traffic in the Riyadh TMA (Class C) listens and watches Riyadh Approach all the time and complies with its instructions
  AD 2 OETH 2.22.3.2  arrival from the east: monitor 124.400 before approaching any VRP; approaching mid-field, look for the traffic in the pattern, plan the sequence, announce
                 the intention and turn to join downwind for the runway in use
  AD 2 OETH 2.17, ENR 2.1   the ATZ: 5 NM, SFC to 3 000 ft AMSL, Class G, no ATS unit; outside it the Riyadh terminal area, Class C, from 700 ft above the ground
The broadcasts of ENR 1.1 are drawn in the colour of 124.400 MHz inside the ATZ: that is how this book reads the two pages together (ENR 1.1 names 122.8 MHz; AD 2.18 keeps
124.4 for traffic within the ATZ). The arrival from the east is the AIP's, which keeps 3 500 ft AMSL at the East VRP: that is above 700 ft above the ground, so no TIBA broadcast
is drawn on it outside the ATZ, only the listening watch the AIP asks for.

Two cards lie on the country east of the ATZ. The lower one is the aerodrome from above at a larger scale, the runway across the page with north to the left as in Figures 18-7 and
26-1 (the plan of data/oeth_plan.json, without the road): the listening watch and the three broadcasts before a take-off from runway 35. No taxiway runs beside the southern half
of the runway, so the aeroplane is drawn entering it by the southern link and taxiing along it to the turning loop at the threshold of 35; that taxi route is this figure's, read
off the plan, not the AIP's. The upper card is the airspace from the side, not to scale: inside the ATZ the UNICOM frequency, outside it the TIBA frequency in the layer of Class G
under 700 ft above the ground, and Riyadh Approach in Class C above that and above the ATZ. Letters: frequencies, class letters, heights and a time with their units, runway
designators; the rest is numbered."""
import math

from figs import f_18_08_local_procedures as L8
from figs import h_b2 as H
from figs import h_b4 as B
from figs import scene as S

n = S.n
W, HT = L8.W, L8.HT
U = "nt5"
F, P = L8.F, L8.P
OETH = H.DATA["oeth"]
UNICOM_MHZ = f'{OETH["comms"]["unicom"]["mhz"]:.3f}'
TIBA_MHZ = f'{OETH["comms"]["tiba_mhz"]:.1f}'
ATZ_TOP = OETH["atz"]["upper_ft_amsl"]
TMA_FLOOR = H.DATA["areas"]["riyadh_east_tma_part1"]["lower"]
assert (UNICOM_MHZ, TIBA_MHZ, ATZ_TOP, TMA_FLOOR, OETH["atz"]["class"]) == ("124.400", "122.8", 3000, "700 FT AGL", "G")
assert "3500 MSL" in OETH["procedures"]["arrival_east"]                                          # the arrival is drawn without a TIBA broadcast because of this height
IN_ATZ, IN_ATZ_INK = "#A8327A", "#7E1F59"            # 124.400 MHz, the UNICOM frequency, inside the ATZ: magenta (not a class colour)
TIBA, TIBA_INK = H.COL["G"], "#145C39"               # 122.8 MHz, the TIBA frequency, in Class G outside: the green of Class G, as in Figure 17-2
APP = H.COL["C"]                                     # Riyadh Approach, in Class C
TRACK = ("#273449", "#44536E", "#C3CDDD")            # the tracks: a neutral ink, so that the colours stay with the frequencies
ARP = L8.ARP
R_ATZ = L8.ATZ["r"]

# ----------------------------------------------------------------------------------------------------- the flight (canvas points)
DEP = L8.rounded([P(L8.RWY_M - 40.0, 0.0), P(L8.TURN_35, 0.0), L8.NV], L8.units(650.0))            # runway 35: from its threshold along the runway, then the right turn to the North VRP
ARR = L8.ARR_EAST                                                                                  # from the East VRP over mid-field to the downwind leg of runway 35
CIRCUIT = L8.CIRCUIT35
_ux, _uy = (ARR[0][0] - ARR[1][0]) / H.dist(ARR[0], ARR[1]), (ARR[0][1] - ARR[1][1]) / H.dist(ARR[0], ARR[1])
LEAD = [(ARR[0][0] + _ux * 50.0, ARR[0][1] + _uy * 50.0), ARR[0]]                                 # the arrival before it reaches the East VRP (it runs off the map)


def where(points, test):
    """The first point along a polyline at which `test` becomes true, by fine steps."""
    total = L8.length(points)
    for i in range(2001):
        (x, y), _ = L8.at_length(points, total * i / 2000)
        if test(x, y):
            return (x, y), total * i / 2000
    raise ValueError("the track never gets there")


OUT_AT, OUT_D = where(DEP, lambda x, y: math.hypot(x - ARP[0], y - ARP[1]) >= R_ATZ)               # where the departure leaves the ATZ
SPOT = {
    4: P(3450.0, 0.0),                                                                           # airborne: soon after the lift-off, over the runway
    5: L8.at_length(DEP, L8.length(DEP) * 0.5)[0],                                               # leaving the circuit: in the right turn away from it
    6: L8.at_length(DEP, OUT_D - 26.0)[0],                                                       # leaving the ATZ: inside its edge
    7: (LEAD[1][0] + _ux * 27.0, LEAD[1][1] + _uy * 27.0),                                       # arriving: before the East VRP
    8: L8.MIDFIELD,                                                                              # approaching mid-field
    9: P(3050.0, L8.D35),                                                                        # in the circuit: on the downwind leg
}


def ground():
    return {"name": "terrain-18-08-picture", "at": [W / 2, HT / 2], "width": W}


def airspace():
    """The ATZ: its edge in the colour of its class, its inside in a breath of the colour of the frequency used in it."""
    return (f'<circle cx="{n(ARP[0])}" cy="{n(ARP[1])}" r="{n(R_ATZ)}" fill="{IN_ATZ}" fill-opacity="0.09"/>' + H.edge(L8.ATZ, "G", dash="8 4.5", width=1.9, uid=U))


def tracks():
    out = [L8.thin(CIRCUIT, (B.BLUE, B.BLUE_MID, B.BLUE_HI), w=1.9, casing=0.9), L8.heads(CIRCUIT, [L8.length(CIRCUIT) * 0.47, L8.length(CIRCUIT) * 0.86], B.BLUE, 6.4, 6.8),
           L8.thin(DEP, TRACK, w=2.6, casing=1.1), L8.heads(DEP, [L8.length(DEP) * 0.3, L8.length(DEP) * 0.74], TRACK[0], 8.0, 8.4),
           L8.thin(LEAD, TRACK, w=2.6, casing=1.1),
           L8.thin(ARR, TRACK, w=2.6, casing=1.1), L8.heads(ARR, [104.0, L8.length(ARR) * 0.45, L8.length(ARR) * 0.9], TRACK[0], 8.0, 8.4)]
    return "".join(out)


def places():
    out = [H.runway(U, P(0.0, 0.0), P(L8.RWY_M, 0.0), 3.0), H.vrp(U, *L8.NV, 11.0), H.vrp(U, *L8.EV, 11.0)]
    out.append(H.label("17", P(-330.0, -420.0)[0], P(-330.0, -420.0)[1], 5.6, H.INK, spacing=0.3))
    out.append(H.label("35", P(L8.RWY_M + 330.0, -420.0)[0], P(L8.RWY_M + 330.0, -420.0)[1], 5.6, H.INK, spacing=0.3))
    return "".join(out)


def broadcast(x, y, colour=IN_ATZ, r=6.6):
    """A broadcast: a megaphone in a badge, in the colour of the frequency."""
    return H.megaphone(U, x, y, r, colour=colour)


def listening(x, y, colour=IN_ATZ, r=6.6):
    """A listening watch: a headset in a badge, in the colour of the frequency."""
    return H.headset(U, x, y, r, colour=colour)


def broadcasts():
    return "".join(broadcast(*SPOT[k]) for k in (4, 5, 6, 8, 9)) + listening(*SPOT[7])


def plane(points, d, width=21.0):
    (x, y), (dx, dy) = L8.at_length(points, d)
    return {"name": "sprite-top", "at": [round(x, 1), round(y, 1)], "width": width, "angle": round(math.degrees(math.atan2(dx, -dy)), 1),
            "shadow": {"dx": 1.6, "dy": 2.4, "blur": 1.6, "opacity": 0.4}, "outline": {"width": 0.45, "colour": "#2B3648", "opacity": 0.9}}


# ----------------------------------------------------------------------------------------------------- the card of the aerodrome: before the take-off
GX, GY, GW, GH = 392.0, 344.0, 236.0, 79.0
S0, S1 = 2150.0, 4190.0                              # the part of the runway frame it shows: from the south apron to past the threshold of 35
GK = GW / (S1 - S0)
RWY_Y = GY + 25.0                                    # the centre line of the runway on the card: the aprons lie on the west side, below it
T_CUT = 270.0                                        # the plan is cut off here, west of the aprons (the road beyond is left out)
PLAN = B.Plan(GX - S0 * GK, RWY_Y, GK)
G_PLANE = {1: PLAN.xy(2560.0, 175.0), 2: PLAN.xy(2800.0, 57.0), 3: PLAN.xy(B.S_S - 70.0, 0.0)}      # on the south apron; on the southern link, short of the runway; lined up on runway 35
G_HEAD = {1: 52.0, 2: 62.0, 3: 270.0}                                                               # where each points on the card (north is to the left)
G_CALL = {1: (G_PLANE[1][0] - 15.5, G_PLANE[1][1]), 2: (G_PLANE[2][0] + 13.0, G_PLANE[2][1] + 11.5), 3: (G_PLANE[3][0] - 1.0, G_PLANE[3][1] - 11.5)}      # the megaphone of each broadcast
G_LISTEN = (G_CALL[1][0] - 14.0, G_CALL[1][1])                                                     # the headset of the listening watch, before the first broadcast
G_R = 5.6


def ground_card():
    clip = f'<clipPath id="{U}gc"><rect x="{n(GX)}" y="{n(GY)}" width="{n(GW)}" height="{n(PLAN.xy(0.0, T_CUT)[1] - GY)}"/></clipPath>'
    sand = (f'<linearGradient id="{U}sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7D3A6"/><stop offset="1" stop-color="#DCC48F"/></linearGradient>')
    taxi = [G_PLANE[1], PLAN.xy(2650.0, 110.0), PLAN.xy(2720.0, 78.0), G_PLANE[2], PLAN.xy(2900.0, 28.0), PLAN.xy(2975.0, 0.0), PLAN.xy(B.S_S - 20.0, 0.0)]      # from the apron by the link onto the runway and along it to the threshold of 35
    out = [f'<defs>{clip}{sand}</defs>', f'<rect x="{n(GX)}" y="{n(GY)}" width="{n(GW)}" height="{n(GH)}" rx="9" fill="url(#{U}sand)" filter="url(#{U}dl)"/>',
           f'<g clip-path="url(#{U}gc)">', B.aerodrome(PLAN, runway_text=False, markings=True),
           f'<polyline points="{S.pts(taxi)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="1.5" stroke-dasharray="2.6 2.2" stroke-linecap="round" stroke-linejoin="round"/>',
           "</g>", B.frame(GX, GY, GW, GH)]
    d = PLAN.xy(B.S_S, 0.0)
    out.append(H.label("35", d[0] + 11.0, RWY_Y - 12.5, 5.2, H.INK, spacing=0.3))
    out.append(listening(*G_LISTEN, r=G_R) + B.label(G_LISTEN[0] + 4.0, G_LISTEN[1] + 16.5, "≥ 5 min", 7.4, "middle"))
    for k in (1, 2, 3):
        out.append(broadcast(*G_CALL[k], r=G_R))
    # north is to the left on this card
    ax, ay = GX + GW - 30.0, GY + GH - 11.0
    out.append(f'<line x1="{n(ax + 9)}" y1="{n(ay)}" x2="{n(ax - 5)}" y2="{n(ay)}" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/><line x1="{n(ax + 9)}" y1="{n(ay)}" x2="{n(ax - 5)}" y2="{n(ay)}" stroke="{H.INK}" stroke-width="1.3" stroke-linecap="round"/>'
               f'<polygon points="{S.pts([(ax - 9.5, ay), (ax - 3.5, ay - 3.4), (ax - 3.5, ay + 3.4)])}" fill="{H.INK}" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>'
               + H.label("N", ax + 15.5, ay, 5.4, H.INK, spacing=0))
    return "".join(out)


def ground_planes():
    spr = {"outline": {"width": 0.4, "colour": "#2B3648", "opacity": 0.9}}
    return [{"name": "sprite-top", "at": [round(G_PLANE[k][0], 1), round(G_PLANE[k][1], 1)], "width": 10.5, "angle": G_HEAD[k], **spr} for k in (1, 2, 3)]


# ----------------------------------------------------------------------------------------------------- the card of the airspace from the side (not to scale)
VX, VY, VW, VH = 436.0, 56.0, 194.0, 140.0
GROUND_Y = VY + VH - 16.0                            # the ground line of the card
FLOOR_Y = GROUND_Y - 38.0                            # 700 ft above the ground
TOP_Y = GROUND_Y - 62.0                              # 3 000 ft AMSL, the top of the ATZ (about 1 130 ft above the aerodrome)
AX0, AX1 = VX + 84.0, VX + 158.0                     # the ATZ, between these
V_R = 7.4                                            # the icons and the numbers on the card
ZONE = {10: (AX0 + 12.0, TOP_Y + 15.0), 11: (VX + 12.0, FLOOR_Y + 19.0), 12: (VX + 14.0, VY + 20.0)}      # where the number of each part of the air stands: the icon follows it


def side_card():
    clip = f'<clipPath id="{U}vc"><rect x="{n(VX)}" y="{n(VY)}" width="{n(VW)}" height="{n(VH)}" rx="9"/></clipPath>'
    sky = f'<linearGradient id="{U}sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#DCEAF8"/><stop offset="1" stop-color="#F2F7FC"/></linearGradient>'
    out = [f'<defs>{clip}{sky}</defs>', f'<rect x="{n(VX)}" y="{n(VY)}" width="{n(VW)}" height="{n(VH)}" rx="9" fill="url(#{U}sky)" filter="url(#{U}dl)"/>', f'<g clip-path="url(#{U}vc)">']
    c, g = H.COL["C"], H.COL["G"]
    # Class C: above 700 ft above the ground outside the ATZ, and above the ATZ
    cpath = (f"M {n(VX)},{n(VY)} L {n(VX + VW)},{n(VY)} L {n(VX + VW)},{n(FLOOR_Y)} L {n(AX1)},{n(FLOOR_Y)} L {n(AX1)},{n(TOP_Y)} L {n(AX0)},{n(TOP_Y)} L {n(AX0)},{n(FLOOR_Y)} L {n(VX)},{n(FLOOR_Y)} Z")
    out.append(f'<path d="{cpath}" fill="{c}" fill-opacity="0.2"/><path d="M {n(VX)},{n(FLOOR_Y)} L {n(AX0)},{n(FLOOR_Y)} L {n(AX0)},{n(TOP_Y)} L {n(AX1)},{n(TOP_Y)} L {n(AX1)},{n(FLOOR_Y)} L {n(VX + VW)},{n(FLOOR_Y)}" '
               f'fill="none" stroke="{c}" stroke-width="1.5" stroke-dasharray="5 3"/>')
    # Class G: the ATZ (in the colour of its frequency), and the layer under the terminal area
    out.append(f'<rect x="{n(AX0)}" y="{n(TOP_Y)}" width="{n(AX1 - AX0)}" height="{n(GROUND_Y - TOP_Y)}" fill="{IN_ATZ}" fill-opacity="0.16"/>'
               f'<rect x="{n(VX)}" y="{n(FLOOR_Y)}" width="{n(AX0 - VX)}" height="{n(GROUND_Y - FLOOR_Y)}" fill="{g}" fill-opacity="0.22"/>'
               f'<rect x="{n(AX1)}" y="{n(FLOOR_Y)}" width="{n(VX + VW - AX1)}" height="{n(GROUND_Y - FLOOR_Y)}" fill="{g}" fill-opacity="0.22"/>'
               f'<line x1="{n(AX0)}" y1="{n(FLOOR_Y)}" x2="{n(AX0)}" y2="{n(GROUND_Y)}" stroke="{g}" stroke-width="1.5" stroke-dasharray="5 3"/>'
               f'<line x1="{n(AX1)}" y1="{n(FLOOR_Y)}" x2="{n(AX1)}" y2="{n(GROUND_Y)}" stroke="{g}" stroke-width="1.5" stroke-dasharray="5 3"/>')
    # the ground and the runway on it
    mid = (AX0 + AX1) / 2
    out.append(f'<rect x="{n(VX)}" y="{n(GROUND_Y)}" width="{n(VW)}" height="{n(VY + VH - GROUND_Y)}" fill="#D9BE86"/><line x1="{n(VX)}" y1="{n(GROUND_Y)}" x2="{n(VX + VW)}" y2="{n(GROUND_Y)}" stroke="#8C7440" stroke-width="0.9"/>'
               f'<rect x="{n(mid - 13)}" y="{n(GROUND_Y - 1.4)}" width="26" height="2.8" rx="0.8" fill="#2B3340" stroke="#FFFFFF" stroke-width="0.5"/>')
    out.append("</g>" + B.frame(VX, VY, VW, VH))
    # the three parts of the air: the number, the icon after it, the frequency
    step = 2 * V_R + 3.0
    x, y = ZONE[10]
    out.append(broadcast(x + step, y, r=V_R) + H.glyph_text(UNICOM_MHZ, mid, y + 19.0, 6.4, IN_ATZ_INK, spacing=0.4, stroke=IN_ATZ_INK, stroke_width=0.25) + H.class_disc(U, AX1 - 11.0, GROUND_Y - 11.0, "G", 6.0))
    x, y = ZONE[11]
    out.append(broadcast(x + step, y, colour=TIBA, r=V_R) + H.glyph_text(TIBA_MHZ, x + 2 * step - 5.0, y, 6.4, TIBA_INK, spacing=0.4, anchor="start", stroke=TIBA_INK, stroke_width=0.25)
               + H.class_disc(U, (AX1 + VX + VW) / 2, y, "G", 6.0))
    x, y = ZONE[12]
    out.append(H.radar(U, x + step + 1.5, y, V_R + 1.6, colour=APP) + H.class_disc(U, x + 2 * step + 4.5, y, "C", 6.6))
    # the two heights
    lab = lambda text, x, y, anchor: B.label(x, y, text, 7.4, anchor)
    out.append(lab(f"{ATZ_TOP // 1000} {ATZ_TOP % 1000:03d} ft AMSL", mid, TOP_Y - 4.5, "middle"))
    out.append(lab("700 ft AGL", VX + 6.0, FLOOR_Y - 4.5, "start"))
    return "".join(out)


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


CALL_AT = {4: (213.0, 303.0), 5: (124.0, 132.0), 6: (190.0, 62.0), 7: (SPOT[7][0], SPOT[7][1] - 27.0), 8: (207.0, 246.0), 9: (86.0, 300.0)}          # where the number of each broadcast stands
G_CALL_AT = {1: (G_CALL[1][0] + 26.0, G_CALL[1][1] + 21.0), 2: (G_CALL[2][0] + 24.0, G_CALL[2][1] + 10.0), 3: (G_CALL[3][0] - 25.0, G_CALL[3][1] - 1.0)}


def callouts():
    c = S.callout
    out = []
    for k in (1, 2, 3):
        out.append(c(k, *G_CALL_AT[k], *rim(G_CALL[k], G_CALL_AT[k], G_R), r=8.4))
    for k in (4, 5, 6, 7, 8, 9):
        out.append(c(k, *CALL_AT[k], *rim(SPOT[k], CALL_AT[k], 6.6), r=10))
    for k in (10, 11, 12):
        x, y = ZONE[k]
        out.append(c(k, x, y, x + V_R + 2.2, y, r=V_R))
    return "".join(out)


def layers():
    out = [H.defs(U, W, HT), B.defs(), ground(), H.vignette(U, W, HT, 0.12), airspace(), tracks(), places(), plane(DEP, L8.length(DEP) * 0.62), plane(ARR, 52.0), broadcasts(),
           side_card(), ground_card(), *ground_planes(), H.north_arrow(U, 612.0, 30.0, 26.0), H.scale_bar(U, 26.0, 410.0, 2 * L8.SCALE, nm_total=2, segments=2, text="2 NM"), callouts()]
    return out


def plate():
    return {
        "id": "fig-19-06-no-tower-broadcasts",
        "replaces": "fig-19-06-no-tower-broadcasts.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-19-06-no-tower-broadcasts.jpg",
        "caption": "Figure 19-6. With no tower: what a flight at Thumamah broadcasts, where, and on which frequency",
        "desc": ("Figure 19-6. With no tower: what a flight at Thumamah broadcasts, where, and on which frequency. North is up on the map and to the left on the card of the aerodrome; the card of the airspace "
                 "is not to scale. The broadcasts and the frequencies are the AIP's (ENR 1.1 and AD 2 OETH, AMDT 11/26); the tracks and the taxi route are illustrative. The ground is an open satellite "
                 "picture (contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "On the apron: listen for at least five minutes, then broadcast the taxi before moving.",
            "Before entering the runway: position and intentions.",
            "Lined up: once more, before the takeoff roll.",
            "Airborne.",
            "Leaving the circuit.",
            "Leaving the ATZ.",
            "Arriving from the east: listen on 124.400 MHz before reaching the VRP.",
            "Approaching mid-field: look for the traffic in the circuit, plan the sequence, announce the intention, then join the downwind leg.",
            "In the circuit: position and intended movement before each manoeuvre.",
            "Inside the ATZ, which is Class G from the surface to 3 000 ft AMSL and has no ATS unit: 124.400 MHz, the frequency of Thumamah UNICOM.",
            "Outside the ATZ, in Class G airspace: 122.8 MHz, the TIBA frequency. A flight about to leave the ATZ through it broadcasts on 122.8 MHz; one arriving through it also listens and broadcasts on 124.400 MHz before it enters the ATZ.",
            "Outside and above the ATZ from 700 ft above the ground, the Riyadh terminal area, Class C: listen to Riyadh Approach at all times and follow its instructions.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
