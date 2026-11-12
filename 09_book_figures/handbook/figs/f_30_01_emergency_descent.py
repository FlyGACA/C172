"""Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery. A scene in a card: the desert seen from the side, pale hills and a plain with
scrub, the descent as a spiral drawn with the front half of every turn as a line with a casing and the back half faint and dashed, the model seen from the right at the three places of the
old figure, the height at which to level off as a dashed line, the look-out lines from the first aeroplane; at the right two small cards: the model from behind banked 30 to 45 degrees
against the horizon with the sector of bank, and the limits as a speed tape (white, green and yellow arcs, the red line, the marks VFE, VA, VNO and VNE with their speeds). The six
numbered callouts of the old figure are kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

A = (8, 8, 424, 384)
TOPC = (445, 22, 180, 160)
BOTC = (445, 196, 180, 196)
GYA = 358.0
BLUE = "#1D4ED8"

# the paths of the old figure: the front half of each loop (solid), the back half (dashed, faint), the last run
P_FRONT1 = 'M 112 70 C 113.7 71.3 119 74.3 122 78 C 125 81.7 128.7 89.7 130 92 C 130.1 92.4 130.1 93.6 130.4 94.4 C 130.6 95.1 130.9 95.9 131.4 96.7 C 131.9 97.5 132.5 98.3 133.2 99 C 133.9 99.8 134.7 100.6 135.6 101.3 C 136.6 102.1 137.6 102.9 138.8 103.6 C 139.9 104.4 141.2 105.1 142.5 105.8 C 143.9 106.6 145.4 107.3 146.9 108 C 148.5 108.7 150.2 109.4 152 110.1 C 153.7 110.8 155.6 111.5 157.6 112.2 C 159.5 112.9 161.6 113.5 163.7 114.2 C 165.8 114.8 168 115.5 170.3 116.1 C 172.6 116.7 175 117.3 177.4 117.9 C 179.8 118.5 182.3 119.1 184.9 119.6 C 187.5 120.2 190.1 120.7 192.8 121.3 C 195.5 121.8 198.2 122.3 201 122.8 C 203.8 123.3 206.6 123.8 209.5 124.2 C 212.3 124.7 215.2 125.1 218.2 125.6 C 221.1 126 224 126.4 227 126.8 C 230 127.2 233 127.5 236 127.9 C 239 128.2 242 128.6 245 128.9 C 248 129.2 251 129.5 254 129.8 C 257 130.1 260 130.3 263 130.6 C 266 130.8 268.9 131 271.8 131.2 C 274.8 131.4 277.7 131.6 280.5 131.8 C 283.4 132 286.2 132.1 289 132.2 C 291.8 132.4 294.5 132.5 297.2 132.6 C 299.9 132.7 302.5 132.8 305.1 132.8 C 307.7 132.9 310.2 133 312.6 133 C 315 133 317.4 133.1 319.7 133.1 C 322 133.1 324.2 133.1 326.3 133.1 C 328.4 133 330.5 133 332.4 133 C 334.4 132.9 336.3 132.9 338 132.8 C 339.8 132.7 341.5 132.7 343.1 132.6 C 344.6 132.5 346.1 132.4 347.5 132.3 C 348.8 132.2 350.1 132.1 351.2 131.9 C 352.4 131.8 353.4 131.7 354.4 131.6 C 355.3 131.4 356.1 131.3 356.8 131.1 C 357.5 131 358.1 130.9 358.6 130.7 C 359.1 130.6 359.4 130.4 359.6 130.2 C 359.9 130.1 360 129.9 360 129.8 C 360 129.6 359.7 129.4 359.6 129.3'
P_BACK1 = 'M 359.6 129.3 C 359.5 129.2 359.1 129 358.6 128.9 C 358.1 128.7 357.5 128.6 356.8 128.4 C 356.1 128.3 355.3 128.1 354.4 128 C 353.4 127.9 352.4 127.7 351.2 127.6 C 350.1 127.5 348.8 127.4 347.5 127.3 C 346.1 127.2 344.6 127.1 343.1 127 C 341.5 126.9 339.8 126.8 338 126.8 C 336.3 126.7 334.4 126.6 332.4 126.6 C 330.5 126.5 328.4 126.5 326.3 126.5 C 324.2 126.5 322 126.5 319.7 126.5 C 317.4 126.5 315 126.5 312.6 126.5 C 310.2 126.6 307.7 126.6 305.1 126.7 C 302.5 126.8 299.9 126.9 297.2 127 C 294.5 127.1 291.8 127.2 289 127.3 C 286.2 127.4 283.4 127.6 280.5 127.8 C 277.7 127.9 274.8 128.1 271.8 128.3 C 268.9 128.5 266 128.8 263 129 C 260 129.2 257 129.5 254 129.8 C 251 130.1 248 130.4 245 130.7 C 242 131 239 131.3 236 131.7 C 233 132 230 132.4 227 132.8 C 224 133.2 221.1 133.6 218.2 134 C 215.2 134.4 212.3 134.9 209.5 135.3 C 206.6 135.8 203.8 136.3 201 136.8 C 198.2 137.3 195.5 137.8 192.8 138.3 C 190.1 138.8 187.5 139.4 184.9 139.9 C 182.3 140.5 179.8 141.1 177.4 141.7 C 175 142.3 172.6 142.9 170.3 143.5 C 168 144.1 165.8 144.7 163.7 145.4 C 161.6 146 159.5 146.7 157.6 147.4 C 155.6 148 153.7 148.7 152 149.4 C 150.2 150.1 148.5 150.8 146.9 151.5 C 145.4 152.3 143.9 153 142.5 153.7 C 141.2 154.5 139.9 155.2 138.8 155.9 C 137.6 156.7 136.6 157.5 135.6 158.2 C 134.7 159 133.9 159.7 133.2 160.5 C 132.5 161.3 131.9 162.1 131.4 162.9 C 130.9 163.6 130.6 164.4 130.4 165.2 C 130.1 166 130.1 167.2 130 167.6'
P_FRONT2 = 'M 130 167.6 C 130.1 167.9 130.1 169.1 130.4 169.9 C 130.6 170.7 130.9 171.5 131.4 172.3 C 131.9 173 132.5 173.8 133.2 174.6 C 133.9 175.4 134.7 176.1 135.6 176.9 C 136.6 177.7 137.6 178.4 138.8 179.2 C 139.9 179.9 141.2 180.7 142.5 181.4 C 143.9 182.1 145.4 182.9 146.9 183.6 C 148.5 184.3 150.2 185 152 185.7 C 153.7 186.4 155.6 187.1 157.6 187.7 C 159.5 188.4 161.6 189.1 163.7 189.7 C 165.8 190.4 168 191 170.3 191.6 C 172.6 192.3 175 192.9 177.4 193.5 C 179.8 194 182.3 194.6 184.9 195.2 C 187.5 195.7 190.1 196.3 192.8 196.8 C 195.5 197.3 198.2 197.9 201 198.4 C 203.8 198.8 206.6 199.3 209.5 199.8 C 212.3 200.2 215.2 200.7 218.2 201.1 C 221.1 201.5 224 201.9 227 202.3 C 230 202.7 233 203.1 236 203.4 C 239 203.8 242 204.1 245 204.4 C 248 204.8 251 205.1 254 205.3 C 257 205.6 260 205.9 263 206.1 C 266 206.4 268.9 206.6 271.8 206.8 C 274.8 207 277.7 207.2 280.5 207.3 C 283.4 207.5 286.2 207.7 289 207.8 C 291.8 207.9 294.5 208 297.2 208.1 C 299.9 208.3 302.5 208.3 305.1 208.4 C 307.7 208.5 310.2 208.5 312.6 208.6 C 315 208.6 317.4 208.6 319.7 208.6 C 322 208.6 324.2 208.6 326.3 208.6 C 328.4 208.6 330.5 208.6 332.4 208.5 C 334.4 208.5 336.3 208.4 338 208.4 C 339.8 208.3 341.5 208.2 343.1 208.1 C 344.6 208 346.1 207.9 347.5 207.8 C 348.8 207.7 350.1 207.6 351.2 207.5 C 352.4 207.4 353.4 207.3 354.4 207.1 C 355.3 207 356.1 206.8 356.8 206.7 C 357.5 206.6 358.1 206.4 358.6 206.3 C 359.1 206.1 359.4 206 359.6 205.8 C 359.9 205.6 360 205.5 360 205.3 C 360 205.2 359.7 204.9 359.6 204.9'
P_BACK2 = 'M 359.6 204.9 C 359.5 204.8 359.1 204.6 358.6 204.4 C 358.1 204.3 357.5 204.1 356.8 204 C 356.1 203.8 355.3 203.7 354.4 203.5 C 353.4 203.4 352.4 203.3 351.2 203.2 C 350.1 203 348.8 202.9 347.5 202.8 C 346.1 202.7 344.6 202.6 343.1 202.5 C 341.5 202.5 339.8 202.4 338 202.3 C 336.3 202.2 334.4 202.2 332.4 202.1 C 330.5 202.1 328.4 202.1 326.3 202 C 324.2 202 322 202 319.7 202 C 317.4 202 315 202.1 312.6 202.1 C 310.2 202.1 307.7 202.2 305.1 202.3 C 302.5 202.3 299.9 202.4 297.2 202.5 C 294.5 202.6 291.8 202.7 289 202.9 C 286.2 203 283.4 203.2 280.5 203.3 C 277.7 203.5 274.8 203.7 271.8 203.9 C 268.9 204.1 266 204.3 263 204.6 C 260 204.8 257 205.1 254 205.3 C 251 205.6 248 205.9 245 206.2 C 242 206.5 239 206.9 236 207.2 C 233 207.6 230 207.9 227 208.3 C 224 208.7 221.1 209.1 218.2 209.6 C 215.2 210 212.3 210.4 209.5 210.9 C 206.6 211.3 203.8 211.8 201 212.3 C 198.2 212.8 195.5 213.3 192.8 213.9 C 190.1 214.4 187.5 214.9 184.9 215.5 C 182.3 216 179.8 216.6 177.4 217.2 C 175 217.8 172.6 218.4 170.3 219 C 168 219.7 165.8 220.3 163.7 220.9 C 161.6 221.6 159.5 222.2 157.6 222.9 C 155.6 223.6 153.7 224.3 152 225 C 150.2 225.7 148.5 226.4 146.9 227.1 C 145.4 227.8 143.9 228.5 142.5 229.3 C 141.2 230 139.9 230.8 138.8 231.5 C 137.6 232.3 136.6 233 135.6 233.8 C 134.7 234.5 133.9 235.3 133.2 236.1 C 132.5 236.8 131.9 237.6 131.4 238.4 C 130.9 239.2 130.6 240 130.4 240.8 C 130.1 241.5 130.1 242.7 130 243.1'
P_LAST = 'M 130 243.1 C 132.1 245.4 134.6 252.6 142.5 256.9 C 150.4 261.3 163.3 265.5 177.4 269 C 191.5 272.5 215.7 276.1 227 277.9 C 238.3 279.7 232 277.6 245 280 C 258 282.4 285 289.3 305 292 C 325 294.7 345 295.3 365 296 C 385 296.7 415 296 425 296'


def world():
    out = H.profile("a1a", A, GYA, seed=53, sun=(70, 60), far=22, mid=10, base=13, scrub_count=16,
                    clouds=[H.cloud("cloud-cumulus-b", 396, 52, 64), H.cloud("cloud-cumulus-a", 250, 34, 70, 0.9), H.cloud("cloud-cumulus-b", 40, 246, 44, 0.85)],
                    palms=[(36, GYA + 8, 0.6), (54, GYA + 12, 0.5)], acacias=[(404, GYA + 10, 0.55)])
    return out


def spiral():
    out = [H.line_cased(70, 74, 123.6, 119, "#4B5870", 1.3, dash="3 4", casing=2.0), H.line_cased(70, 74, 105, 134.6, "#4B5870", 1.3, dash="3 4", casing=2.0),
           H.line_cased(10, 310, 425, 310, "#B45309", 2.0, dash="8 6", casing=2.4)]
    out.append(H.line_cased(20, 70, 112, 70, BLUE, 2.6, casing=2.4))
    out.append(H.path_line(P_BACK1, BLUE, 2.0, dash="6 5", casing=1.6, opacity=0.5, glow=False))
    out.append(H.path_line(P_BACK2, BLUE, 2.0, dash="6 5", casing=1.6, opacity=0.5, glow=False))
    out.append(H.path_line(P_FRONT1, BLUE, 2.6, casing=2.4))
    out.append(H.path_line(P_FRONT2, BLUE, 2.6, casing=2.4))
    out.append(H.path_line(P_LAST, BLUE, 2.6, casing=2.4))
    out.append(H.arrow_head(251, 129.5, 4, 12, BLUE))
    out.append(H.arrow_head(251, 205.1, 4, 12, BLUE))
    return "".join(out)


def top_card():
    x, y, w, h = TOPC
    out = H.profile("a1t", TOPC, 112, seed=59, sun=(40, 40), far=26, mid=10, base=13, radius=8, scrub_count=6, grain=False)
    out.append(H.line_cased(455, 99, 615, 99, "#4B5870", 1.3, dash="5 4", casing=2.0, opacity=0.95))
    wedge = "M 532 99 L 606.5 56 A 86 86 0 0 0 592.8 38.2 Z"
    out.append(f'<path d="{wedge}" fill="#2F63C8" fill-opacity="0.28" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.85" stroke-linejoin="round"/>'
               f'<path d="{wedge}" fill="none" stroke="{BLUE}" stroke-width="1.5" stroke-linejoin="round"/>')
    out.append({"name": "sprite-rear", "at": [537.1, 105.5], "width": 136, "angle": -38, **H.LOOK})
    out.append(f'<text x="597" y="130" font-family="sans-serif" font-size="12" font-weight="bold" fill="{BLUE}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke">30°–45°</text>')
    return out


def tape():
    """The limits as a speed tape: the white arc (VS0 to VFE), the green arc (VS1 to VNO), the yellow arc (VNO to VNE), the red line at VNE, the marks with their speeds."""
    x, y, w, h = BOTC
    out = [S.card("a1bt", x, y, w, h, [(0, "#F7FAFE"), (1, "#E4ECF6")], "", radius=8)]
    g = S.gradient
    out.append(f'<defs>{g("a1tpg", [(0, "#58C799"), (0.5, "#079669"), (1, "#056B4B")], 0, 0, 1, 0)}{g("a1tpy", [(0, "#F6D77A"), (0.5, "#E0B44C"), (1, "#B98A22")], 0, 0, 1, 0)}'
               f'{g("a1tpw", [(0, "#FFFFFF"), (1, "#D7DFEA")], 0, 0, 1, 0)}</defs>')
    out.append('<rect x="508" y="219" width="22" height="162" rx="3" fill="#FFFFFF" opacity="0.0"/>')
    out.append('<line x1="523" y1="380" x2="523" y2="210" stroke="#9AA6B8" stroke-width="1"/>')
    out.append('<rect x="511" y="314.6" width="6" height="58.8" fill="url(#a1tpw)" stroke="#1F2937" stroke-width="1"/>')
    out.append('<rect x="518" y="268.8" width="9" height="95.5" fill="url(#a1tpg)"/>')
    out.append('<rect x="518" y="223.1" width="9" height="45.7" fill="url(#a1tpy)"/>')
    out.append('<rect x="518" y="223.1" width="1.6" height="141.2" fill="#FFFFFF" opacity="0.35"/>')
    out.append('<line x1="508" y1="223.1" x2="531" y2="223.1" stroke="#FFFFFF" stroke-width="6" stroke-opacity="0.8"/><line x1="508" y1="223.1" x2="531" y2="223.1" stroke="#B91C1C" stroke-width="3.5"/>')
    for y_, num_, name_, col in ((314.6, "90", "VFE", "#1F2937"), (301.5, "100", "VA", "#1F2937"), (268.8, "125", "VNO", "#1F2937"), (223.1, "160", "VNE", "#B91C1C")):
        out.append(f'<line x1="528" y1="{y_}" x2="536" y2="{y_}" stroke="#1F2937" stroke-width="1.4"/>'
                   f'<text x="504" y="{y_ + 4}" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="end">{num_}</text>'
                   f'<text x="540" y="{y_ + 4}" font-family="monospace" font-size="12" fill="{col}" text-anchor="start">{name_}</text>')
    out.append('<text x="504" y="377.5" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="end">45</text>')
    return out


def callouts():
    c = S.callout
    return "".join([c(1, 30, 36, 56, 56), c(2, 150, 52, 130, 90), c(3, 400, 150, 356, 172), c(4, 462, 42), c(5, 462, 214), c(6, 300, 340, 290, 311)])


def layers():
    out = [H.page("a1page", 640, 400), H.defs()]
    out += world()
    out.append(spiral())
    out.append(H.plane_c(57.9, 63.4, 0, 72))
    out.append(H.plane_c(317.7, 119.8, 24, 66))
    out.append(H.plane_c(391.9, 289.4, 0, 72))
    out.append(H.foreground("a1a", A, GYA, seed=53, scrub=8, scale=1.1))
    out += top_card()
    out += tape()
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-30-01-emergency-descent",
        "replaces": "fig-30-01-emergency-descent.svg",
        "book_file": "plate-30-01-emergency-descent.jpg",
        "caption": "Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery",
        "desc": "Figure 30-1. An emergency descent: a spiral at idle power within the airspeed limits, with an early recovery",
        "legend": [
            "Clear the area and call.",
            "Throttle closed, bank, nose down.",
            "Descending turns over the checked area.",
            "About 30° to 45° of bank, seen from behind.",
            "The example aeroplane's limits: `VFE` 90 kt with any flap; `VA` 100 kt in turbulence; above `VNO` 125 kt (the yellow arc) only in smooth air; never above `VNE` 160 kt.",
            "Level off above the height your school sets.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-30-01-emergency-descent.svg", "blank": True, "layers": layers()},
    }
