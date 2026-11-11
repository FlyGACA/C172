"""Plane geometry for sheet-metal parts (pure Python, tested outside Blender)."""
import math


def area(loop):
    """Signed area of a closed 2D loop: positive when it runs counter-clockwise."""
    return 0.5 * sum(loop[i][0] * loop[(i + 1) % len(loop)][1] - loop[(i + 1) % len(loop)][0] * loop[i][1] for i in range(len(loop)))


def counter_clockwise(loop):
    return list(loop) if area(loop) >= 0 else list(reversed(loop))


def inset(loop, distance):
    """Move a closed loop inward by `distance` (outward if negative). Corners are mitred, with the
    mitre limited so that a sharp trailing edge does not shoot off."""
    pts = counter_clockwise(loop)
    n = len(pts)
    out = []
    for i in range(n):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        ax, ay = x1 - x0, y1 - y0
        bx, by = x2 - x1, y2 - y1
        la, lb = math.hypot(ax, ay) or 1e-12, math.hypot(bx, by) or 1e-12
        # inward normals of the two edges (interior is on the left of a counter-clockwise loop)
        nax, nay = -ay / la, ax / la
        nbx, nby = -by / lb, bx / lb
        mx, my = nax + nbx, nay + nby
        lm = math.hypot(mx, my)
        if lm < 1e-9:
            mx, my, scale = nax, nay, 1.0
        else:
            mx, my = mx / lm, my / lm
            scale = min(3.0, 1.0 / max(1e-6, mx * nax + my * nay))
        out.append((x1 + mx * distance * scale, y1 + my * distance * scale))
    return out


def circle(cx, cy, radius, segments=16):
    return [(cx + radius * math.cos(2 * math.pi * i / segments), cy + radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]


def slot(cx, cy, length, width, segments=8, angle=0.0):
    """Stadium (a slot with round ends), `length` overall along `angle`."""
    r = width / 2
    half = max(0.0, length / 2 - r)
    c, s = math.cos(angle), math.sin(angle)
    pts = []
    for sign, start in ((1, -math.pi / 2), (-1, math.pi / 2)):
        for i in range(segments + 1):
            a = start + math.pi * i / segments
            x, y = sign * half + r * math.cos(a), r * math.sin(a)
            pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def rounded_rectangle(cx, cy, width, height, radius, segments=4):
    radius = min(radius, width / 2, height / 2)
    pts = []
    for qx, qy, start in ((1, 1, 0.0), (-1, 1, math.pi / 2), (-1, -1, math.pi), (1, -1, 1.5 * math.pi)):
        ox, oy = cx + qx * (width / 2 - radius), cy + qy * (height / 2 - radius)
        for i in range(segments + 1):
            a = start + (math.pi / 2) * i / segments
            pts.append((ox + radius * math.cos(a), oy + radius * math.sin(a)))
    return pts


def inside(point, loop):
    """Even-odd test: is the point inside the closed loop?"""
    x, y = point
    hit = False
    n = len(loop)
    for i in range(n):
        x0, y0 = loop[i]; x1, y1 = loop[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            hit = not hit
    return hit


def height_at(loop, x):
    """Lowest and highest y of a closed loop on the vertical line at x (None outside its extent)."""
    ys = []
    n = len(loop)
    for i in range(n):
        x0, y0 = loop[i]; x1, y1 = loop[(i + 1) % n]
        if x0 == x1:
            if x0 == x:
                ys.extend((y0, y1))
            continue
        if min(x0, x1) <= x <= max(x0, x1):
            ys.append(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
    return (min(ys), max(ys)) if ys else None


def lightening_holes(loop, x0, x1, count, margin, max_radius=None, segments=14):
    """Round holes along a web between x0 and x1: `count` holes evenly spaced, each as large as the
    web allows with `margin` of metal above, below and between holes. Holes that would be smaller
    than half the margin are left out."""
    holes = []
    if count <= 0 or x1 <= x0:
        return holes
    pitch = (x1 - x0) / count
    for i in range(count):
        cx = x0 + pitch * (i + 0.5)
        radius = pitch / 2 - margin / 2
        for dx in (-0.6, -0.3, 0.0, 0.3, 0.6):          # the web must clear the hole all the way across it
            extent = height_at(loop, cx + dx * max(radius, 0.0))
            if extent is None:
                radius = 0.0
                break
            lo, hi = extent
            reach = math.sqrt(max(0.0, 1 - dx * dx))    # how much of the radius the hole needs at this offset
            radius = min(radius, ((hi - lo) / 2 - margin) / max(reach, 0.35))
        if max_radius is not None:
            radius = min(radius, max_radius)
        if radius < margin * 0.5:
            continue
        lo, hi = height_at(loop, cx)
        holes.append(circle(cx, (lo + hi) / 2, radius, segments))
    return holes


def resample(points, count, closed=False):
    """`count` points evenly spaced along a polyline (or closed loop)."""
    pts = list(points) + ([points[0]] if closed else [])
    lengths = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(lengths)
    steps = count if closed else count - 1
    out = []
    for k in range(count):
        target = total * k / steps
        i = 0
        while i < len(lengths) - 1 and target > lengths[i]:
            target -= lengths[i]; i += 1
        t = 0.0 if lengths[i] == 0 else min(1.0, target / lengths[i])
        out.append(tuple(a + (b - a) * t for a, b in zip(pts[i], pts[i + 1])))
    return out


def spaced(start, end, pitch, margin=0.0):
    """Positions from start+margin to end-margin, spaced as near to `pitch` as divides evenly."""
    length = (end - start) - 2 * margin
    if length <= 0:
        return [(start + end) / 2]
    count = max(1, int(round(length / pitch)))
    return [start + margin + length * i / count for i in range(count + 1)]


def convex_hull(points):
    """Convex hull of 2D points, counter-clockwise (monotone chain)."""
    pts = sorted(set((round(x, 9), round(y, 9)) for x, y in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def clear_of(holes, others, gap):
    """The round holes of `holes` [(cx, cy, r)] that neither touch nor crowd any of `others`: a hole is
    dropped when it comes within `gap` of another one without containing it."""
    kept = []
    for cx, cy, r in holes:
        ok = True
        for ox, oy, orad in others:
            distance = math.hypot(cx - ox, cy - oy)
            if distance < r + orad + gap and not distance + orad < r - gap * 0.5:
                ok = False
                break
        if ok:
            kept.append((cx, cy, r))
    return kept
