"""Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart. Drawn again on an aerial view of the country (figs/terrain.py) seen through a framed map window: the wadi
and the road, the planned track a blue ribbon with its two-mile ticks, the station a hexagonal white building with a dome, the planned 300 radial and the 290 radial as light rays, the
10 NM DME arc, the aeroplane of the model at the fix with the GNSS diamond beside it, the new track dashed; beside the map the VOR indicator and the DME readout as lit instruments and
the scale as a ruler. The geometry, numbers and callouts of the old figure are kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-21-08", size=(2560, 1600), seed=218, kind="plain", features=("scrub", "tracks"), veil=0.3, soft=2.6)

FRAME = (18.0, 26.8, 396.0, 355.2)
STN = (364.3, 286.4)
WADI = [(22.8, 225.8), (34.2, 216.5), (45.5, 214.9), (56.9, 217.6), (68.3, 215.2), (79.6, 206.2), (91.0, 199.2), (102.4, 200.1), (113.7, 203.8), (125.1, 201.4), (136.4, 193.3), (147.8, 188.8),
        (159.2, 192.1), (170.5, 196.6), (181.9, 194.2), (193.3, 187.3), (204.6, 185.4), (216.0, 190.9), (227.4, 195.9), (238.7, 193.5), (250.1, 188.1), (261.5, 188.9), (272.8, 196.4),
        (284.2, 201.7), (295.6, 199.5), (306.9, 195.9), (318.3, 199.4), (329.6, 208.5), (341.0, 213.9), (352.4, 212.1), (363.7, 210.6), (375.1, 216.8), (386.5, 227.2), (397.8, 232.6), (409.2, 231.5)]


def poly_d(points):
    return "M " + " L ".join(f"{S.n(x)},{S.n(y)}" for x, y in points)


def plan():
    out = ['<defs><clipPath id="f8c"><rect x="18" y="26.8" width="396" height="355.2" rx="6"/></clipPath><filter id="f8b" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>', '<g clip-path="url(#f8c)">']
    # the wadi: a dry bed between darker banks, bushes along it
    smooth = S.catmull(WADI, 6)
    d = poly_d(smooth)
    out.append(f'<path d="{d}" fill="none" stroke="#6E4B26" stroke-opacity="0.45" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" filter="url(#f8b)"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#A9814F" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#EFE0B8" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFF7DE" stroke-opacity="0.8" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" transform="translate(-0.6 -1)"/>')
    out.append(S.scrub(8, 22, 410, 176, 246, 34, scale=0.8))
    # the road: asphalt with a pale shoulder and a broken centre line
    out.append('<line x1="198" y1="382" x2="198" y2="26.8" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="10.4"/>'
               '<line x1="198" y1="382" x2="198" y2="26.8" stroke="#4C5463" stroke-width="7.2"/>'
               '<line x1="198" y1="382" x2="198" y2="26.8" stroke="#F4EBC9" stroke-width="1.0" stroke-dasharray="6 5"/>')
    out.append("</g>")
    return "".join(out)


def track():
    """The planned track: a ribbon through (88.7, 379.6) to (291.1, 29.2) with ticks every 2 NM and the labels 18 and 30."""
    out = ['<g clip-path="url(#f8c)">']
    out.append(H.ribbon("f8t", [(80.0, 394.6), (296.0, 20.7)], width=5.0, colours=H.BLUE, head=1.0, arrow=False, casing=1.8))
    u, v = (0.5, -0.866), (0.866, 0.5)
    for k in (0, 1, 2, 3, 5, 6, 7):
        cx, cy = 88.7 + u[0] * (26.6 + 47.9 * k), 379.6 + u[1] * (26.6 + 47.9 * k)
        x0, y0, x1, y1 = cx - 6.2 * v[0], cy - 6.2 * v[1], cx + 6.2 * v[0], cy + 6.2 * v[1]
        out.append(f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#FFFFFF" stroke-width="4.4" stroke-linecap="round" stroke-opacity="0.9"/>'
                   f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#1B4FD0" stroke-width="2" stroke-linecap="round"/>')
    out.append(H.text(148, 327.0, "18", 12.5, "#1B4FD0", "bold", "middle", halo="#FFFFFF"))
    out.append(H.text(292, 77.6, "30", 12.5, "#1B4FD0", "bold", "middle", halo="#FFFFFF"))
    out.append("</g>")
    return "".join(out)


def rays_and_arc():
    out = ['<g clip-path="url(#f8c)">']
    # the planned 300 radial (dashed) and the 290 radial (solid), as light rays
    out.append(H.link("f8a", (STN[0] - 8, STN[1] - 4.6), (198.0, 190.4), "#FFFFFF", "#FFFFFF", 2.2, "7 5", 6.0, 1.0))
    out.append(H.link("f8b2", (STN[0] - 12, STN[1] - 4.4), (89.1, 186.2), "#FFFFFF", "#FFFFFF", 2.6, None, 7.0, 1.0))
    # the DME arc, 10 NM about the station, dashed dark with a pale casing
    out.append(H.halo_path("M126.6,253.0 A240.0,240.0 0 0,1 163.0,155.7", "#1B2A47", 2.4, 3.8, 0.85, "8 5"))
    out.append("</g>")
    return "".join(out)


def marks():
    out = []
    # the planned fix on the road and the wadi: a ring
    out.append('<circle cx="198" cy="190.4" r="10" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-opacity="0.9"/><circle cx="198" cy="190.4" r="10" fill="none" stroke="#1B4FD0" stroke-width="2.8"/>')
    out.append(H.text(222, 218.4, "24", 12.5, "#1B4FD0", "bold", "middle", halo="#FFFFFF"))
    # the GNSS position: a diamond a few tenths of a mile from the fix
    dia = [(144.8, 185.7), (159.8, 200.7), (144.8, 215.7), (129.8, 200.7)]
    out.append(f'<defs><filter id="f8g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
               f'<polygon points="{S.pts(dia)}" fill="none" stroke="#35E6A0" stroke-width="5" filter="url(#f8g)" opacity="0.9"/>'
               f'<polygon points="{S.pts(dia)}" fill="none" stroke="#FFFFFF" stroke-width="5.8" stroke-opacity="0.9" stroke-linejoin="round"/>'
               f'<polygon points="{S.pts(dia)}" fill="none" stroke="#0B8A66" stroke-width="2.6" stroke-linejoin="round"/>')
    return "".join(out)


def vor_indicator():
    cx, cy = 531.0, 104.0
    out = [f'<defs><radialGradient id="f8bz" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#4A5468"/><stop offset="1" stop-color="#0B101C"/></radialGradient>'
           f'<radialGradient id="f8fc" cx="0.4" cy="0.35" r="0.85"><stop offset="0" stop-color="#262F42"/><stop offset="1" stop-color="#0E1424"/></radialGradient>'
           f'<radialGradient id="f8kn" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#F4F6FA"/><stop offset="0.6" stop-color="#9AA5B8"/><stop offset="1" stop-color="#4A5468"/></radialGradient>'
           f'<filter id="f8n" x="-300%" y="-30%" width="700%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>']
    out.append(f'<circle cx="{cx}" cy="{cy}" r="68" fill="url(#f8bz)" stroke="#8FA0BC" stroke-opacity="0.55" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="63" fill="url(#f8fc)" stroke="#05080F" stroke-width="1.4"/>')
    out.append(f'<path d="M {cx - 56},{cy - 24} A 61,61 0 0 1 {cx - 12},{cy - 59}" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.6" stroke-linecap="round"/>')
    # the OBS window and its index
    out.append(f'<rect x="513" y="46" width="36" height="17" rx="3" fill="#F4F6FA" stroke="#05080F" stroke-width="1"/>' + H.text(531, 58.8, "290", 12.5, "#111827", "bold", "middle")
               + f'<polygon points="531,71 526.6,63.6 535.4,63.6" fill="#F4F6FA"/>')
    # the deviation dots and the centre ring, the needle (centred)
    for i in range(-5, 6):
        if i == 0:
            out.append(f'<circle cx="{cx}" cy="111.7" r="4.4" fill="none" stroke="#FFFFFF" stroke-width="1.3"/>')
        else:
            out.append(f'<circle cx="{S.n(cx + i * 8.3)}" cy="111.7" r="1.9" fill="#CBD5E6"/>')
    out.append(f'<rect x="{cx - 2.2}" y="73" width="4.4" height="54" rx="2.2" fill="#FFA43A" opacity="0.85" filter="url(#f8n)"/>'
               f'<rect x="{cx - 1.7}" y="73" width="3.4" height="54" rx="1.7" fill="#FFB347" stroke="#FFF1CF" stroke-opacity="0.8" stroke-width="0.5"/>')
    # the TO/FROM window showing FROM
    out.append('<rect x="514" y="133" width="34" height="24" rx="3" fill="#F4F6FA" stroke="#05080F" stroke-width="1"/><polygon points="525,151 520,142 530,142" fill="#111827"/>' + H.text(538, 149, "FR", 11, "#111827", "bold", "middle", mono=True))
    # the OBS knob
    out.append(f'<circle cx="482.5" cy="147.7" r="10.6" fill="#05080F" opacity="0.5"/><circle cx="482.5" cy="147.7" r="9.6" fill="url(#f8kn)" stroke="#2A3448" stroke-width="0.8"/>'
               + "".join(f'<line x1="{S.n(482.5 + 6.2 * math.cos(math.radians(a)))}" y1="{S.n(147.7 + 6.2 * math.sin(math.radians(a)))}" x2="{S.n(482.5 + 9.2 * math.cos(math.radians(a)))}" y2="{S.n(147.7 + 9.2 * math.sin(math.radians(a)))}" stroke="#3A4458" stroke-width="0.8"/>' for a in range(0, 360, 30)))
    return "".join(out)


def dme_readout():
    out = [H.glass("f8d", 471, 198, 120, 48, r=6, top="#101828", bottom="#05080F", opacity=1.0, shadow=False)]
    out.append('<defs><filter id="f8dg" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="3"/></filter></defs>'
               + f'<text x="531" y="233" font-family="monospace" font-size="26" font-weight="bold" fill="#FFB52E" text-anchor="middle" filter="url(#f8dg)" opacity="0.8">10.0</text>'
               + H.text(531, 233, "10.0", 26, "#FFCF63", "bold", "middle", mono=True)
               + H.text(531, 266, "DME", 12, "#8DBBFF", "bold", "middle", mono=True))
    return "".join(out)


def ruler():
    out = ['<defs>' + S.gradient("f8r", [(0, "#FDFEFF"), (1, "#D6DEEA")]) + '</defs>',
           '<rect x="458" y="313" width="148" height="34" rx="5" fill="#10233F" opacity="0.28" transform="translate(0 2.6)" filter="url(#f8b)"/>',
           '<rect x="458" y="313" width="148" height="34" rx="5" fill="url(#f8r)" stroke="#9AA6BA" stroke-width="0.8"/>',
           '<rect x="459" y="314" width="146" height="1.8" rx="0.9" fill="#FFFFFF" opacity="0.9"/>']
    for i in range(6):
        x = 470 + i * 24
        long = i in (0, 5)
        out.append(f'<line x1="{x}" y1="{S.n(323.5 if long else 325.5)}" x2="{x}" y2="334.5" stroke="#1F2937" stroke-width="{2 if long else 1.2}" stroke-linecap="round"/>')
    out.append(H.text(470, 344.6, "0", 10.5, "#1F2937", "bold", "middle") + H.text(590, 344.6, "5", 10.5, "#1F2937", "bold", "middle"))
    out.append('<line x1="470" y1="334.5" x2="590" y2="334.5" stroke="#1F2937" stroke-width="1.6"/>')
    return "".join(out)


def plate():
    st = H.vor_top("f8s", STN[0], STN[1], 1.1)
    frame_hole = f'M 0,0 H 640 V 400 H 0 Z M {FRAME[0] + 6},{FRAME[1]} H {FRAME[0] + FRAME[2] - 6} A 6,6 0 0 1 {FRAME[0] + FRAME[2]},{FRAME[1] + 6} V {FRAME[1] + FRAME[3] - 6} A 6,6 0 0 1 {FRAME[0] + FRAME[2] - 6},{FRAME[1] + FRAME[3]} H {FRAME[0] + 6} A 6,6 0 0 1 {FRAME[0]},{FRAME[1] + FRAME[3] - 6} V {FRAME[1] + 6} A 6,6 0 0 1 {FRAME[0] + 6},{FRAME[1]} Z'
    dim = (f'<defs><filter id="f8fs" x="-5%" y="-5%" width="110%" height="112%"><feDropShadow dx="0" dy="3" stdDeviation="3.2" flood-color="#10233F" flood-opacity="0.45"/></filter></defs>'
           f'<path d="{frame_hole}" fill="#1B2740" fill-opacity="0.36" fill-rule="evenodd"/>'
           f'<rect x="{FRAME[0]}" y="{FRAME[1]}" width="{FRAME[2]}" height="{FRAME[3]}" rx="6" fill="none" stroke="#FFFFFF" stroke-width="2" filter="url(#f8fs)"/>')
    new_track = H.dashed_arrow([(144.8, 196.3), (256.5, 30.4)], "#1B4FD0", 2.8, "8 5", 9.0, casing=1.6)
    card = H.glass("f8k", 436, 18, 190, 262, r=12, top="#1F2E4B", bottom="#0C1527", opacity=0.97)
    layers = [
        {"name": "terrain-21-08", "at": [320, 200], "width": 640},
        dim, plan(), track(), rays_and_arc(), st,
        H.text(364.3, 320.6, "NKL", 13, "#1B4FD0", "bold", "middle", mono=True, halo="#FFFFFF"),
        marks(), new_track,
        H.plane(141.2, 205.2, 56, 34),
        card, vor_indicator(), dme_readout(), ruler(),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 62, 360, 96, 351), c(2, 232, 176, 206, 186), c(3, 396, 262, 372, 280), c(4, 100, 236, 128, 214), c(5, 178, 160, 154, 190), c(6, 52, 246, 70, 217),
        c(7, 172, 100, 212.3, 96), c(8, 322, 44, 296, 36), c(9, 456, 36, 484, 62), c(10, 456, 222, 472, 222), c(11, 624, 330, 600, 330),
    ]))
    return {
        "id": "fig-21-08-cross-check-fix",
        "replaces": "fig-21-08-cross-check-fix.svg",
        "book_file": "plate-21-08-cross-check-fix.jpg",
        "caption": "Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart",
        "desc": "Figure 21-8. Checking a route checkpoint with VOR/DME, GNSS and the chart",
        "legend": [
            "Planned track 030° from aerodrome A; distances from A in NM.",
            "WADI, planned for 0615 UTC: radial 300, 8.0 NM from `NKL`.",
            "The fictional VOR/DME `NKL`; dashed grey, the planned 300 radial.",
            "The fix at 0614 UTC: the 290 radial and the 10 NM DME arc.",
            "The GNSS position, a few tenths of a mile from the fix.",
            "The wadi and the road crossing at WADI.",
            "New track to B, 034°, on heading 043.",
            "The track continues to aerodrome B, 48 NM from A.",
            "VOR indicator: OBS 290, needle centred, `FR`.",
            "DME 10.0 NM; slant range is negligible here.",
            "Scale in NM.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-21-08-cross-check-fix.svg", "blank": True, "layers": layers},
    }
