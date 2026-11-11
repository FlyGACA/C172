"""Pure-Python 2D profiles (no bpy) shared by the Blender build and the texture generator."""
import math

def naca4(code="2412", n=40, te_closed=True):
    """NACA 4-digit airfoil as a closed loop of (x, y), chord 1, starting at the trailing
    edge, along the upper surface to the leading edge, back along the lower surface."""
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0
    a4 = -0.1036 if te_closed else -0.1015
    pts_u, pts_l = [], []
    for i in range(n + 1):
        x = 0.5 * (1 - math.cos(math.pi * i / n))
        yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 + a4 * x**4)
        if p > 0 and x < p:
            yc = m / p**2 * (2 * p * x - x**2); dyc = 2 * m / p**2 * (p - x)
        elif p > 0:
            yc = m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2); dyc = 2 * m / (1 - p)**2 * (p - x)
        else:
            yc = 0.0; dyc = 0.0
        th = math.atan(dyc)
        pts_u.append((x - yt * math.sin(th), yc + yt * math.cos(th)))
        pts_l.append((x + yt * math.sin(th), yc - yt * math.cos(th)))
    return list(reversed(pts_u)) + pts_l[1:-1]

def airfoil_interp(a, b, t):
    return [(pa[0] * (1 - t) + pb[0] * t, pa[1] * (1 - t) + pb[1] * t) for pa, pb in zip(a, b)]

def airfoil_u_of_x(loop, xc, upper=True):
    """UV u-parameter (index fraction around the closed loop) of chord fraction xc."""
    n = len(loop)
    half = n // 2
    rng = range(0, half + 1) if upper else range(half, n)
    best = min(rng, key=lambda i: abs(loop[i][0] - xc))
    return best / n

def split_airfoil(loop, xc, gap=0.012):
    """Split a closed airfoil loop at chord fraction xc into (main box, control surface).
    Both are closed loops; the surface has a round nose, the box a concave cove."""
    n = len(loop)
    upper = loop[: n // 2 + 1]                       # TE -> LE
    lower = [loop[0]] + list(reversed(loop[n // 2:]))  # TE -> LE
    def y_at(pts, x):
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return 0.0
    yu, yl = y_at(upper, xc), y_at(lower, xc)
    yc = 0.5 * (yu + yl); r = 0.5 * (yu - yl)
    aft_u = [p for p in upper if p[0] > xc]
    aft_l = [p for p in lower if p[0] > xc]
    nose = [(xc + r * 0.96 * math.cos(math.pi / 2 + i * math.pi / 8), yc + r * 0.96 * math.sin(math.pi / 2 + i * math.pi / 8)) for i in range(1, 8)]
    surf = aft_u + [(xc, yu)] + nose + [(xc, yl)] + list(reversed(aft_l))[0:-1]
    fwd_u = [p for p in upper if p[0] <= xc]
    fwd_l = [p for p in lower if p[0] <= xc]
    cove = [(xc + r * 1.04 * math.cos(math.pi / 2 + i * math.pi / 8), yc + r * 1.04 * math.sin(math.pi / 2 + i * math.pi / 8)) for i in range(1, 8)]
    box = [(xc + gap, yu)] + fwd_u + list(reversed(fwd_l))[0:-1] + [(xc + gap, yl)] + list(reversed(cove))
    return box, surf

def superellipse(w, hb, ht, zc, n_top=2.3, n_bot=2.1, k=32, xc=0.0):
    """Closed ring of (x, z) around (xc, zc): half width w, lower height hb, upper height ht.
    Starts at the bottom and goes anticlockwise seen from the front (+x first)."""
    pts = []
    for i in range(k):
        a = -math.pi / 2 + 2 * math.pi * i / k
        c, s = math.cos(a), math.sin(a)
        n = n_top if s >= 0 else n_bot
        h = ht if s >= 0 else hb
        pts.append((xc + w * math.copysign(abs(c) ** (2 / n), c), zc + h * math.copysign(abs(s) ** (2 / n), s)))
    return pts

def rounded_rect(w, h, r, n=6):
    pts = []
    for cx, cy, a0 in [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def ellipse(a, b, k=24):
    return [(a * math.cos(2 * math.pi * i / k), b * math.sin(2 * math.pi * i / k)) for i in range(k)]

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)

def resample_loop(pts, k):
    """Resample a closed loop to k points, equally spaced by arc length, keeping point 0."""
    n = len(pts)
    seg = []
    total = 0.0
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
        d = math.hypot(x1 - x0, y1 - y0); seg.append(d); total += d
    out = []
    j = 0; acc = 0.0
    for i in range(k):
        target = total * i / k
        while j < n - 1 and acc + seg[j] < target:
            acc += seg[j]; j += 1
        x0, y0 = pts[j]; x1, y1 = pts[(j + 1) % n]
        t = 0.0 if seg[j] == 0 else (target - acc) / seg[j]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out

def interp_table(table, s):
    """Piecewise-linear interpolation in a table of (s, value...) rows."""
    if s <= table[0][0]:
        return table[0][1:]
    if s >= table[-1][0]:
        return table[-1][1:]
    for i in range(len(table) - 1):
        s0, s1 = table[i][0], table[i + 1][0]
        if s0 <= s <= s1:
            t = (s - s0) / (s1 - s0)
            t = t * t * (3 - 2 * t)  # smooth
            return [a + (b - a) * t for a, b in zip(table[i][1:], table[i + 1][1:])]

def interp_linear(table, s):
    """Straight-line interpolation in a table of (s, value...) rows, clamped at both ends."""
    if s <= table[0][0]:
        return list(table[0][1:])
    if s >= table[-1][0]:
        return list(table[-1][1:])
    for i in range(len(table) - 1):
        s0, s1 = table[i][0], table[i + 1][0]
        if s0 <= s <= s1:
            t = (s - s0) / (s1 - s0)
            return [a + (b - a) * t for a, b in zip(table[i][1:], table[i + 1][1:])]

def _pchip_slopes(xs, ys):
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    delta = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    if n == 2:
        return [delta[0], delta[0]]
    d = [0.0] * n
    for k in range(1, n - 1):
        if delta[k - 1] * delta[k] > 0:
            w1 = 2 * h[k] + h[k - 1]; w2 = h[k] + 2 * h[k - 1]
            d[k] = (w1 + w2) / (w1 / delta[k - 1] + w2 / delta[k])
    for end, a, b in ((0, 0, 1), (n - 1, n - 2, n - 3)):
        slope = ((2 * h[a] + h[b]) * delta[a] - h[a] * delta[b]) / (h[a] + h[b])
        if slope * delta[a] <= 0:
            slope = 0.0
        elif delta[a] * delta[b] <= 0 and abs(slope) > 3 * abs(delta[a]):
            slope = 3 * delta[a]
        d[end] = slope
    return d

def interp_pchip(table, s):
    """Shape-preserving cubic interpolation in a table of (s, value...) rows (Fritsch-Carlson).

    The curve passes through every row, is smooth across rows and never overshoots them. Use it
    for outlines: interp_table eases in and out of every row, which puts a flat spot at each one
    and shows as a row of kinks along an edge that should be straight or evenly curved.
    """
    n = len(table)
    if s <= table[0][0]:
        return list(table[0][1:])
    if s >= table[-1][0]:
        return list(table[-1][1:])
    xs = [row[0] for row in table]
    i = max(j for j in range(n - 1) if xs[j] <= s)
    h = xs[i + 1] - xs[i]; t = (s - xs[i]) / h
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t
    h01 = -2 * t ** 3 + 3 * t ** 2; h11 = t ** 3 - t ** 2
    out = []
    for col in range(1, len(table[0])):
        ys = [row[col] for row in table]
        d = _pchip_slopes(xs, ys)
        out.append(h00 * ys[i] + h10 * h * d[i] + h01 * ys[i + 1] + h11 * h * d[i + 1])
    return out
