"""Small, dependency-light mesh primitives for the Phase 7 model (numpy only).

Every primitive returns a ``Geom`` (positions, normals, triangle indices) in the
caller's local frame. Conventions follow glTF: right-handed, +Y up, +Z forward
(toward the propeller) and +X toward the aircraft's LEFT wing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class Geom:
    v: np.ndarray  # (n, 3) float64 positions
    n: np.ndarray  # (n, 3) float64 unit normals
    f: np.ndarray  # (m, 3) int64 triangle indices

    def transformed(self, m: np.ndarray | None = None, t=(0.0, 0.0, 0.0)) -> "Geom":
        v, n = self.v, self.n
        if m is not None:
            v = v @ m.T
            n = n @ m.T
            n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        return Geom(v + np.asarray(t, float), n, self.f)

    def moved(self, t) -> "Geom":
        return self.transformed(None, t)


def merge(*geoms: Geom) -> Geom:
    geoms = [g for g in geoms if g is not None and len(g.f)]
    vs, ns, fs, off = [], [], [], 0
    for g in geoms:
        vs.append(g.v)
        ns.append(g.n)
        fs.append(g.f + off)
        off += len(g.v)
    return Geom(np.concatenate(vs), np.concatenate(ns), np.concatenate(fs))


# ----------------------------------------------------------------- rotations
def rot(axis, deg: float) -> np.ndarray:
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    return np.array([
        [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
    ])


def align(src, dst) -> np.ndarray:
    """Rotation matrix taking unit vector ``src`` onto ``dst``."""
    a = np.asarray(src, float) / np.linalg.norm(src)
    b = np.asarray(dst, float) / np.linalg.norm(dst)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9:
        if c > 0:
            return np.eye(3)
        perp = np.cross(a, [1, 0, 0])
        if np.linalg.norm(perp) < 1e-6:
            perp = np.cross(a, [0, 1, 0])
        return rot(perp, 180)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * (1 / (1 + c))


def quat_from_matrix(m: np.ndarray):
    t = m[0, 0] + m[1, 1] + m[2, 2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w, x, y, z = (m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w, x, y, z = (m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w, x, y, z = (m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s
    return [x, y, z, w]


# ---------------------------------------------------------------- primitives
def box(sx, sy, sz, c=(0, 0, 0)) -> Geom:
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    faces = [
        ((1, 0, 0), [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)]),
        ((-1, 0, 0), [(-hx, -hy, hz), (-hx, hy, hz), (-hx, hy, -hz), (-hx, -hy, -hz)]),
        ((0, 1, 0), [(-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz)]),
        ((0, -1, 0), [(-hx, -hy, hz), (-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)]),
        ((0, 0, 1), [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
        ((0, 0, -1), [(hx, -hy, -hz), (-hx, -hy, -hz), (-hx, hy, -hz), (hx, hy, -hz)]),
    ]
    v, n, f = [], [], []
    for normal, quad in faces:
        b = len(v)
        v += quad
        n += [normal] * 4
        f += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    return Geom(np.array(v, float) + np.asarray(c, float), np.array(n, float), np.array(f))


def cylinder(r, h, seg=24, r_top=None, caps=True) -> Geom:
    """Cylinder/frustum along +Y from y=0 to y=h."""
    r_top = r if r_top is None else r_top
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ca, sa = np.cos(ang), np.sin(ang)
    slope = (r - r_top) / h if h else 0.0
    side_n = np.stack([ca, np.full(seg, slope), sa], 1)
    side_n /= np.linalg.norm(side_n, axis=1, keepdims=True)
    v = np.concatenate([np.stack([r * ca, np.zeros(seg), r * sa], 1), np.stack([r_top * ca, np.full(seg, h), r_top * sa], 1)])
    n = np.concatenate([side_n, side_n])
    f = []
    for i in range(seg):
        j = (i + 1) % seg
        f += [(i, seg + i, seg + j), (i, seg + j, j)]
    g = Geom(v, n, np.array(f))
    if not caps:
        return g
    parts = [g]
    for y, rr, sgn in ((0.0, r, -1), (h, r_top, 1)):
        if rr <= 0:
            continue
        cv = np.concatenate([[[0, y, 0]], np.stack([rr * ca, np.full(seg, y), rr * sa], 1)])
        cn = np.tile([0, sgn, 0], (seg + 1, 1)).astype(float)
        cf = []
        for i in range(seg):
            j = (i + 1) % seg
            cf.append((0, j + 1, i + 1) if sgn > 0 else (0, i + 1, j + 1))
        parts.append(Geom(cv, cn, np.array(cf)))
    return merge(*parts)


def cyl_between(p, q, r, seg=16, r_q=None, caps=True) -> Geom:
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p
    h = float(np.linalg.norm(d))
    return cylinder(r, h, seg, r_q, caps).transformed(align((0, 1, 0), d), p)


def sphere(r, seg=16, rings=10, scale=(1, 1, 1)) -> Geom:
    v, n = [], []
    for i in range(rings + 1):
        phi = math.pi * i / rings
        for j in range(seg + 1):
            th = 2 * math.pi * j / seg
            d = (math.sin(phi) * math.cos(th), math.cos(phi), math.sin(phi) * math.sin(th))
            v.append((d[0] * r * scale[0], d[1] * r * scale[1], d[2] * r * scale[2]))
            nn = np.array((d[0] / scale[0], d[1] / scale[1], d[2] / scale[2]))
            n.append(nn / max(np.linalg.norm(nn), 1e-12))
    f = []
    for i in range(rings):
        for j in range(seg):
            a = i * (seg + 1) + j
            b = a + seg + 1
            f += [(a, a + 1, b), (a + 1, b + 1, b)]
    return Geom(np.array(v, float), np.array(n, float), np.array(f))


def tube(points, r, seg=10) -> Geom:
    """Polyline pipe with spherical joints (fuel, oil, vacuum, pitot-static lines)."""
    pts = [np.asarray(p, float) for p in points]
    parts = [cyl_between(a, b, r, seg, caps=False) for a, b in zip(pts, pts[1:])]
    parts += [sphere(r, seg, max(4, seg // 2)).moved(p) for p in pts]
    return merge(*parts)


def disc(r, thick=0.002, seg=32) -> Geom:
    """Thin disc facing -Z (the pilot side of the instrument panel)."""
    return cylinder(r, thick, seg).transformed(rot((1, 0, 0), -90), (0, 0, 0))


def arc_band(r_in, r_out, a0, a1, thick=0.0015, steps=None) -> Geom:
    """Annular sector on an instrument face (XY plane, facing -Z).

    Angles are in degrees measured clockwise from 12 o'clock as seen by the
    pilot (looking toward +Z), matching the viewer's needle convention.
    """
    steps = steps or max(2, int(abs(a1 - a0) / 4) + 1)
    angs = np.radians(np.linspace(a0, a1, steps))
    dirs = np.stack([-np.sin(angs), np.cos(angs)], 1)
    v, f = [], []
    for zf in (-thick, 0.0):
        for d in dirs:
            v.append((d[0] * r_in, d[1] * r_in, zf))
            v.append((d[0] * r_out, d[1] * r_out, zf))
    v = np.array(v, float)
    m = 2 * steps
    for k in range(steps - 1):
        a, b, c, d = 2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 3
        f += [(a, c, b), (b, c, d)]  # front (-Z)
        f += [(m + a, m + b, m + c), (m + b, m + d, m + c)]  # back
    n = np.tile([0.0, 0.0, -1.0], (len(v), 1))
    n[m:] = (0, 0, 1)
    return Geom(v, n, np.array(f))


def tick(angle, r0, r1, width) -> Geom:
    """Radial tick mark on an instrument face (angle clockwise from 12 o'clock)."""
    a = math.radians(angle)
    d = np.array([-math.sin(a), math.cos(a), 0.0])
    return box(width, r1 - r0, 0.0015).transformed(align((0, 1, 0), d), d * (r0 + r1) / 2)


def smooth_normals(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    n = np.zeros_like(v)
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


def loft(sections, cap_start=True, cap_end=True) -> Geom:
    """Skin a list of equal-length closed rings (each (k,3)) into a closed surface.

    Triangles are oriented so normals point away from each ring's centre, which
    is robust for star-shaped sections (fuselage stations, airfoils, tanks).
    """
    rings = [np.asarray(s, float) for s in sections]
    k = len(rings[0])
    centers = [r.mean(0) for r in rings]
    v = np.concatenate(rings)
    f = []
    for j in range(len(rings) - 1):
        for i in range(k):
            a, b = j * k + i, j * k + (i + 1) % k
            c, d = a + k, b + k
            f += [(a, b, d), (a, d, c)]
    f = np.array(f)
    tri_n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    ring_of = f[:, 0] // k
    ctr = np.array([(centers[j] + centers[min(j + 1, len(rings) - 1)]) / 2 for j in ring_of])
    if ((v[f].mean(1) - ctr) * tri_n).sum() < 0:
        f = f[:, ::-1]
    parts = [Geom(v, smooth_normals(v, f), f)]
    for idx, other, use in ((0, -1, cap_start), (-1, 0, cap_end)):
        if not use:
            continue
        ring = rings[idx]
        c = centers[idx]
        out = c - centers[other]
        out = out / max(np.linalg.norm(out), 1e-12)
        cv = np.concatenate([[c], ring])
        cf = np.array([(0, i + 1, (i + 1) % k + 1) for i in range(k)])
        tn = np.cross(cv[cf[0, 1]] - cv[0], cv[cf[0, 2]] - cv[0])
        if np.dot(tn, out) < 0:
            cf = cf[:, ::-1]
        parts.append(Geom(cv, np.tile(out, (len(cv), 1)), cf))
    return merge(*parts)


def superellipse_ring(cx, cy, z, hw, hh, n=2.6, k=40):
    t = np.linspace(0, 2 * math.pi, k, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    x = hw * np.sign(c) * np.abs(c) ** (2 / n)
    y = hh * np.sign(s) * np.abs(s) ** (2 / n)
    return np.stack([cx + x, cy + y, np.full(k, z)], 1)


def naca4(code: str, u0=0.0, u1=1.0, k=18):
    """Closed NACA 4-digit outline as (chord_fraction, thickness_fraction) pairs.

    Returns points from u1 along the upper surface to u0 and back along the
    lower surface, so partial-chord slices (flaps, ailerons) are closed shapes.
    """
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    xs = u0 + (u1 - u0) * (0.5 - 0.5 * np.cos(np.linspace(0, math.pi, k)))

    def surf(x, upper):
        yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)
        if m and p:
            yc = np.where(x < p, m / p ** 2 * (2 * p * x - x ** 2), m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x ** 2))
        else:
            yc = 0 * x
        return yc + (yt if upper else -yt)

    up = np.stack([xs[::-1], surf(xs[::-1], True)], 1)
    lo = np.stack([xs[1:-1], surf(xs[1:-1], False)], 1)
    return np.concatenate([up, lo])


def wing_panel(code, stations, u0=0.0, u1=1.0, k=18) -> Geom:
    """Loft an airfoil along a span.

    ``stations`` are (leading_edge_point, chord, chord_dir, up_dir); the section
    is the NACA ``code`` profile between chord fractions u0..u1.
    """
    prof = naca4(code, u0, u1, k)
    rings = []
    for le, chord, cdir, udir in stations:
        le, cdir, udir = (np.asarray(a, float) for a in (le, cdir, udir))
        rings.append(np.array([le + cdir * chord * x + udir * chord * y for x, y in prof]))
    return loft(rings)
