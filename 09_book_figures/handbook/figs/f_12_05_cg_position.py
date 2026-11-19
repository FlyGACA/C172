"""Figure 12-5 (new). How the position of the CG changes the flying, from the table of Chapter 12 ("How the CG position changes the flying"), on the side view of the training aeroplane (sprite-side).

Two aeroplanes, to one scale: CG near the forward limit (left) and near the aft limit (right). The centre of lift (a blue mark on the wing) is the same in both; the CG (amber mark) lies ahead of it, farther ahead on the left. The horizontal
tail holds the nose up with a downward force (red arrow): large on the left, small on the right, as the chapter says. Under each aeroplane, four rows of arrows say what that means for the pilot, in the order of the legend: 3 stability
in pitch, 4 control forces, 5 stall speed, 6 cruise speed (up arrow: greater/higher/faster, down arrow: less/lower/slower; a short arrow means only slightly, as the chapter says for the aft stall speed and cruise). No words: shapes,
colours and the numbers of the callouts. The positions of the marks are drawn to show the idea and are not those of any aeroplane."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 292
U = "cg12"
PW = 300.0                                                   # width of a plane's sprite box
PL = (16.0, 336.0)                                            # left edges of the two aeroplanes
PTOP = 34.0
BLUE, AMBER, RED, SLATE, GREEN = "#1D4ED8", "#B45309", "#B91C1C", "#475569", "#15803D"
CG_U = (3.7, 4.6)                                            # the CG, in tenths of the sprite box: forward, aft
CL_U = 5.35                                                  # the centre of lift
ROWS = (  # (forward arrow, aft arrow) as signed sizes: + up, - down; magnitude 1 = full, 0.5 = slight
    (+1.0, -1.0),                                            # stability in pitch: greater, less
    (+1.0, -1.0),                                            # control forces: heavy, light
    (+1.0, -0.5),                                            # stall speed: higher, slightly lower
    (-1.0, +0.5),                                            # cruise: slower, slightly faster
)


def sx(i, u, v):
    return PL[i] + u / 10.0 * PW, PTOP + v / 10.0 * PW * 640 / 1536


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<line x1="320" y1="22" x2="320" y2="{HT - 22}" stroke="{SLATE}" stroke-opacity="0.2" stroke-width="1"/>')


def arrow(x0, y0, x1, y1, col, width=3.4, head=8.0, shadow=True):
    return M.arrow(x0, y0, x1, y1, col, width=width * 0.8, head=head, halo=shadow)


def cg_mark(x, y, r=7.5):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#FFFFFF" stroke="{SLATE}" stroke-width="1.6" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x)} {n(y)} L{n(x)} {n(y - r)} A{n(r)} {n(r)} 0 0 1 {n(x + r)} {n(y)} Z M{n(x)} {n(y)} L{n(x)} {n(y + r)} A{n(r)} {n(r)} 0 0 1 {n(x - r)} {n(y)} Z" fill="{AMBER}"/>')


def plane(i):
    out = []
    px, py = PL[i] + PW / 2, PTOP + PW * 640 / 1536 / 2
    cgx, cgy = sx(i, CG_U[i], 4.0)
    clx, cly = sx(i, CL_U, 3.55)
    tx, ty = sx(i, 0.85, 2.5)
    # the centre of lift: a blue mark on the wing, with the lift arrow up
    out.append(arrow(clx, cly - 8, clx, cly - 34, BLUE, 3.4, 8.0))
    out.append(f'<path d="M{n(clx)} {n(cly - 7)} L{n(clx - 6)} {n(cly + 3)} L{n(clx + 6)} {n(cly + 3)} Z" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/>')
    # the CG and the weight, down
    out.append(arrow(cgx, cgy + 8, cgx, cgy + 36, SLATE, 3.4, 8.0))
    out.append(cg_mark(cgx, cgy))
    # the tail force, down: large with the CG forward, small with the CG aft
    length = (34.0, 14.0)[i]
    out.append(arrow(tx, ty - 6, tx, ty + length, RED, 3.6 if i == 0 else 3.0, 8.0))
    return "".join(out)


def rows():
    """Four rows under each aeroplane: an arrow up or down for each effect, bigger for a full change and shorter for slightly."""
    out = []
    y0 = 158.0
    dy = 31.0
    for i in range(2):
        for k, row in enumerate(ROWS):
            v = row[i]
            cx = PL[i] + PW / 2
            cy = y0 + k * dy + 13
            # the pill behind
            out.append(f'<rect x="{n(cx - 40)}" y="{n(cy - 13)}" width="80" height="26" rx="9" fill="#EEF2F7" stroke="#CBD5E1" stroke-width="1"/>')
            h = 11.0 if abs(v) < 1 else 18.0
            col = SLATE
            if v > 0:
                out.append(arrow(cx + 10, cy + h / 2, cx + 10, cy - h / 2 - 2, col, 3.6, 7.5, shadow=False))
            else:
                out.append(arrow(cx + 10, cy - h / 2, cx + 10, cy + h / 2 + 2, col, 3.6, 7.5, shadow=False))
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.0
    out = []
    # 1: the CG (forward), 2: the CG (aft)? the legend numbers the marks once: 1 CG, 2 the tail force; the rows are 3..6
    cgx, cgy = sx(0, CG_U[0], 4.0)
    tx, ty = sx(0, 0.85, 2.5)
    out.append(c(1, cgx - 4, cgy - 44, cgx - 1, cgy - 9, r=r))
    out.append(c(2, tx - 24, ty + 40, tx - 2, ty + 26, r=r))
    for k in range(4):
        cx = PL[0] + PW / 2
        out.append(c(3 + k, cx - 66, 158.0 + k * 31.0 + 13, r=r))
    return "".join(out)


def sprites():
    return [A.plane(PL[i] + PW / 2, PTOP + PW * 640 / 1536 / 2, PW, name="sprite-side") for i in range(2)]


def layers():
    return [H.defs(U, W, HT), background(), *sprites(), plane(0), plane(1), rows(), callouts()]


def plate():
    return {
        "id": "fig-12-05-cg-position",
        "replaces": "fig-12-05-cg-position.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-12-05-cg-position.jpg",
        "caption": "Figure 12-5. How the position of the CG changes the flying: near the forward limit (left) and near the aft limit (right)",
        "desc": ("Figure 12-5. How the position of the CG changes the flying, on the side view of the training aeroplane: near the forward limit (left) and near the aft limit (right). The CG lies ahead of the centre of lift, "
                 "and the horizontal tail holds the nose up with a downward force that is large with the CG forward and small with it aft. Four rows of arrows give the effects on stability in pitch, control forces, stall speed and cruise speed."),
        "legend": [
            "The CG (the amber and white mark), ahead of the centre of lift (the blue mark on the wing). Weight acts down at the CG and lift acts up at the centre of lift. The positions are drawn to show the idea.",
            "The downward force of the horizontal tail that holds the nose up: large with the CG near the forward limit, small with it near the aft limit.",
            "Stability in pitch: greater with the CG forward, so the aeroplane resists disturbance and settles quickly; less with it aft, so it is easily disturbed and slow to settle.",
            "Control forces: heavy with the CG forward, with more elevator and trim needed; light with it aft, so it is easy to over-control and to overstress the structure.",
            "Stall speed: higher with the CG forward, because the larger tail down-force adds to the load the wing carries; slightly lower with it aft.",
            "Cruise: slower with the CG forward, using more fuel, for the same reason; slightly faster with it aft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
