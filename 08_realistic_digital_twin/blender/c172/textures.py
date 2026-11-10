"""Procedural texture generation for the Phase 8 model (numpy + PIL, no bpy).

All textures are original, generated from parametric descriptions. UV conventions match the
lofts in airframe.py: for lofted skins u runs around the section and v along the loft.
Images are written with v = 1 at the top row, which is how Blender reads a UV of (u, 1).
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .profiles import naca4, airfoil_u_of_x, smoothstep

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Original FlyGACA-style scheme (not a Cessna factory scheme)
WHITE = (0.93, 0.93, 0.92)
NAVY = (0.09, 0.19, 0.40)
GOLD = (0.83, 0.65, 0.22)
SKY_BLUE = (0.35, 0.60, 0.85)

# ----------------------------------------------------------------------------- utilities

def _rng(seed):
    return np.random.default_rng(seed)

def fractal_noise(h, w, seed=1, octaves=5, base=8, persistence=0.55):
    """Tileable-ish value noise in [0, 1]."""
    rng = _rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = 1.0; total = 0.0
    for o in range(octaves):
        n = base * (2 ** o)
        grid = rng.random((n, n)).astype(np.float32)
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(img, np.float32) / 255.0)
        total += amp; amp *= persistence
    return out / total

def height_to_normal(height, strength=4.0):
    """Tangent-space normal map (OpenGL / glTF convention, +Y up) from a height field.
    Height increases outward; row 0 is v = 1 (top of image)."""
    h = height.astype(np.float32)
    dx = np.zeros_like(h); dy = np.zeros_like(h)
    dx[:, 1:-1] = (h[:, 2:] - h[:, :-2]) * 0.5
    dy[1:-1, :] = (h[:-2, :] - h[2:, :]) * 0.5     # +v is up the image
    nx = -dx * strength; ny = -dy * strength; nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / l, ny / l, nz / l], -1)
    return ((n * 0.5 + 0.5) * 255).astype(np.uint8)

def stamp_rivet_rows(height, rows, pitch_px, radius_px=2.2, depth=1.0, axis="h", size=None):
    """Add dome rivets along rows. rows: list of (pos_px, start_px, end_px); axis 'h' means
    the row runs horizontally at y = pos."""
    H, W = height.shape
    r = int(math.ceil(radius_px * 2))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    dome = np.clip(1 - (xx**2 + yy**2) / (radius_px**2), 0, 1) ** 0.6 * depth
    for pos, a, b in rows:
        pos = int(round(pos))
        for t in np.arange(a, b, pitch_px):
            t = int(round(t))
            y, x = (pos, t) if axis == "h" else (t, pos)
            if y - r < 0 or y + r + 1 > H or x - r < 0 or x + r + 1 > W:
                continue
            region = height[y - r:y + r + 1, x - r:x + r + 1]
            np.maximum(region, dome, out=region)
    return height

def stamp_seam(height, pos, a, b, axis="h", width_px=2, depth=-0.9):
    H, W = height.shape
    pos = int(round(pos)); a = int(max(0, a)); b = int(min(W if axis == "h" else H, b))
    w0 = max(0, pos - width_px // 2); w1 = min((H if axis == "h" else W), pos + (width_px + 1) // 2)
    if axis == "h":
        height[w0:w1, a:b] = np.minimum(height[w0:w1, a:b], depth)
    else:
        height[a:b, w0:w1] = np.minimum(height[a:b, w0:w1], depth)
    return height

def save_rgb(path, arr01, quality=92):
    img = Image.fromarray((np.clip(arr01, 0, 1) * 255).astype(np.uint8))
    if path.lower().endswith(".jpg"):
        img.save(path, quality=quality, subsampling=0)
    else:
        img.save(path)

def save_orm(path, ao, rough, metal):
    arr = np.stack([ao, rough, metal], -1)
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(path)

def text_mask(h, w, text, cx, cy, size_px, font=FONT_BOLD, angle=0.0, italic_shear=0.0, mirror=False):
    img = Image.new("L", (w, h), 0)
    f = ImageFont.truetype(font, size_px)
    tw, th = f.getbbox(text)[2:]
    tile = Image.new("L", (tw + 20, th + 20), 0)
    ImageDraw.Draw(tile).text((10, 10 - f.getbbox(text)[1]), text, 255, font=f)
    if italic_shear:
        tile = tile.transform(tile.size, Image.AFFINE, (1, italic_shear, -italic_shear * tile.size[1] / 2, 0, 1, 0), Image.BICUBIC)
    if mirror:
        tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
    if angle:
        tile = tile.rotate(angle, Image.BICUBIC, expand=True)
    img.paste(tile, (int(cx - tile.size[0] / 2), int(cy - tile.size[1] / 2)))
    return np.asarray(img, np.float32) / 255.0

def blend(base, color, mask):
    m = mask[..., None]
    return base * (1 - m) + np.asarray(color, np.float32)[None, None, :] * m

# ----------------------------------------------------------------------------- skins

def paint_base(h, w, seed, tint=WHITE, grain=0.03):
    n = fractal_noise(h, w, seed, octaves=4, base=16)
    base = np.ones((h, w, 3), np.float32) * np.asarray(tint, np.float32)
    base *= (1 - grain + grain * 2 * n)[..., None]
    rough = 0.32 + 0.10 * (fractal_noise(h, w, seed + 7, octaves=5, base=12) - 0.5)
    return base, rough

def fuselage_set(out_dir, size=2048, length_m=7.2, circ_m=3.6, wordmark="FlyGACA", registration=""):
    """Fuselage skin. u: 0 bottom, 0.25 right side, 0.5 top, 0.75 left side. v: 0 firewall → 1 tail."""
    H = W = size
    base, rough = paint_base(H, W, 11)
    vv = 1 - (np.arange(H) + 0.5) / H          # v per row
    uu = (np.arange(W) + 0.5) / W              # u per column
    V, U = np.meshgrid(vv, uu, indexing="ij")
    # ---- livery stripe (belt line under the windows, sweeping up into the tail)
    sweep = 0.16 * np.vectorize(smoothstep)(0.62, 0.97, V)
    def band(uc, hw):
        return np.clip(1 - np.abs(U - uc) / hw, 0, 1) ** 0.25
    right_c = 0.205 + sweep; left_c = 0.795 - sweep
    navy = np.maximum(band(right_c, 0.022), band(left_c, 0.022))
    gold = np.maximum(band(right_c + 0.030, 0.004), band(left_c - 0.030, 0.004))
    skyb = np.maximum(band(right_c - 0.032, 0.006), band(left_c + 0.032, 0.006))
    base = blend(base, NAVY, navy); base = blend(base, GOLD, gold); base = blend(base, SKY_BLUE, skyb)
    # wordmark on both sides, aft of the rear window (v ≈ 0.55), between stripe and roof
    # right side: reads tail->nose (decreasing v) with 'up' toward the roof (increasing u)
    # left side: reads nose->tail (increasing v) with 'up' toward decreasing u
    for uc, ang in ((0.345, -90), (0.655, 90)):
        m = text_mask(H, W, wordmark, cx=int(W * uc), cy=int(H * (1 - 0.50)), size_px=int(size * 0.045), angle=ang, italic_shear=0.18, mirror=True)
        base = blend(base, NAVY, m)
    if registration:
        for uc in (0.27, 0.73):
            m = text_mask(H, W, registration, cx=int(W * uc), cy=int(H * (1 - 0.70)), size_px=int(size * 0.035), angle=(-90 if uc < 0.5 else 90), mirror=True)
            base = blend(base, NAVY, m)
    # ---- wear: belly dirt, exhaust soot aft of the stack (right-hand belly, forward)
    dirt = fractal_noise(H, W, 23, octaves=5, base=6)
    belly = np.clip(1 - np.minimum(U, 1 - U) / 0.10, 0, 1)
    base *= (1 - 0.10 * belly * dirt)[..., None]
    soot = np.exp(-((U - 0.11) / 0.05) ** 2) * np.exp(-((V - 0.10) / 0.12) ** 2) * (V > 0.02)
    base *= (1 - 0.35 * soot * (0.5 + dirt))[..., None]
    rough = np.clip(rough + 0.25 * soot + 0.12 * belly * dirt, 0, 1)
    # ---- rivets and seams in UV space
    px_per_m_v = H / length_m; px_per_m_u = W / circ_m
    height = np.zeros((H, W), np.float32)
    frames_m = [0.0, 0.45, 0.95, 1.55, 2.05, 2.55, 2.9, 3.35, 3.9, 4.5, 5.1, 5.7, 6.3, 6.85, 7.15]
    rows = []
    for fm in frames_m:
        y = H - fm * px_per_m_v
        if 4 < y < H - 4:
            rows.append((y, 0, W))
            stamp_seam(height, y + 5, 0, W, axis="h", width_px=2, depth=-0.6)
    stamp_rivet_rows(height, rows, pitch_px=0.028 * px_per_m_u, radius_px=size / 1024 * 1.4, axis="h")
    cols = [(W * k / 20, 0, H) for k in range(20)]
    stamp_rivet_rows(height, cols, pitch_px=0.030 * px_per_m_v, radius_px=size / 1024 * 1.3, axis="v")
    # doubler plates / inspection panels on the belly and sides (subtle grooves)
    for (u0, u1, v0, v1) in [(0.02, 0.07, 0.30, 0.36), (0.93, 0.98, 0.30, 0.36), (0.47, 0.53, 0.75, 0.80), (0.04, 0.09, 0.60, 0.66)]:
        x0, x1 = int(u0 * W), int(u1 * W); y0, y1 = int((1 - v1) * H), int((1 - v0) * H)
        stamp_seam(height, y0, x0, x1, "h"); stamp_seam(height, y1, x0, x1, "h")
        stamp_seam(height, x0, y0, y1, "v"); stamp_seam(height, x1, y0, y1, "v")
    normal = height_to_normal(height, strength=3.0 * size / 2048)
    ao = 1 - 0.25 * np.clip(-height, 0, 1) - 0.06 * belly
    save_rgb(os.path.join(out_dir, "fuselage_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "fuselage_orm.png"), ao, rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "fuselage_normal.png"))

def wing_set(out_dir, size=2048, semispan_m=5.46, chord_m=1.64, tip_color=NAVY, name="wing"):
    """Wing skin: u around the airfoil (TE→upper→LE→lower→TE), v root→tip."""
    H = W = size
    base, rough = paint_base(H, W, 31)
    vv = 1 - (np.arange(H) + 0.5) / H
    uu = (np.arange(W) + 0.5) / W
    V, U = np.meshgrid(vv, uu, indexing="ij")
    tip = np.vectorize(smoothstep)(0.955, 0.965, V)
    base = blend(base, tip_color, tip)
    stripe = np.clip(1 - np.abs(V - 0.945) / 0.006, 0, 1)
    base = blend(base, GOLD, stripe)
    # grime along the lower surface near the root (u > 0.5 is the lower surface)
    dirt = fractal_noise(H, W, 37, octaves=5, base=6)
    lower = (U > 0.52).astype(np.float32)
    base *= (1 - 0.08 * lower * dirt * (1 - V))[..., None]
    rough = np.clip(rough + 0.08 * lower * dirt, 0, 1)
    # rivets: ribs (constant v), spar caps (constant u at x/c 0.25 & 0.68 top and bottom)
    af = naca4("2412", 40)
    px_v = H / semispan_m; px_u = W / (2 * chord_m)
    height = np.zeros((H, W), np.float32)
    rib_pitch = 0.40
    rows = []
    s = 0.12
    while s < semispan_m - 0.05:
        y = H - s * px_v
        rows.append((y, int(W * 0.02), int(W * 0.98)))
        s += rib_pitch
    stamp_rivet_rows(height, rows, pitch_px=0.03 * px_u, radius_px=size / 1024 * 1.3, axis="h")
    cols = []
    for xc in (0.25, 0.68):
        for up in (True, False):
            cols.append((W * airfoil_u_of_x(af, xc, up), 0, H))
    stamp_rivet_rows(height, cols, pitch_px=0.03 * px_v, radius_px=size / 1024 * 1.3, axis="v")
    # tank bay access panels on the upper surface, inboard
    for (xa, xb, sa, sb) in [(0.30, 0.50, 0.55, 0.85), (0.30, 0.50, 1.20, 1.50)]:
        ua, ub = airfoil_u_of_x(af, xb, True), airfoil_u_of_x(af, xa, True)
        x0, x1 = int(ua * W), int(ub * W); y0, y1 = int(H - sb * px_v), int(H - sa * px_v)
        stamp_seam(height, y0, x0, x1, "h"); stamp_seam(height, y1, x0, x1, "h")
        stamp_seam(height, x0, y0, y1, "v"); stamp_seam(height, x1, y0, y1, "v")
    normal = height_to_normal(height, strength=3.0 * size / 2048)
    ao = 1 - 0.25 * np.clip(-height, 0, 1)
    save_rgb(os.path.join(out_dir, f"{name}_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, f"{name}_orm.png"), ao, rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, f"{name}_normal.png"))

def fin_set(out_dir, size=1024, wordmark="FlyGACA"):
    """Vertical fin skin: u around the section (TE→right side→LE→left side), v root→tip.
    Carries the livery sweep and the wordmark on both sides."""
    H = W = size
    base, rough = paint_base(H, W, 41)
    vv = 1 - (np.arange(H) + 0.5) / H; uu = (np.arange(W) + 0.5) / W
    V, U = np.meshgrid(vv, uu, indexing="ij")
    # diagonal navy sweep: low at the leading edge, high at the trailing edge
    side_pos = np.where(U < 0.5, U / 0.5, (1 - U) / 0.5)   # 0 at TE, 1 at LE
    center = 0.25 + 0.35 * (1 - side_pos)
    band = np.clip(1 - np.abs(V - center) / 0.10, 0, 1) ** 0.3
    base = blend(base, NAVY, band)
    base = blend(base, GOLD, np.clip(1 - np.abs(V - center - 0.125) / 0.012, 0, 1))
    base = blend(base, SKY_BLUE, np.clip(1 - np.abs(V - center + 0.125) / 0.015, 0, 1))
    for uc, ang in ((0.25, -22), (0.75, 22)):
        m = text_mask(H, W, wordmark, cx=int(W * uc), cy=int(H * (1 - 0.70)), size_px=int(size * 0.07), angle=ang, italic_shear=0.15, mirror=True)
        base = blend(base, NAVY, m)
    height = np.zeros((H, W), np.float32)
    rows = [(H - H * (0.1 + 0.15 * i), 0, W) for i in range(6)]
    stamp_rivet_rows(height, rows, pitch_px=size / 1024 * 14, radius_px=size / 1024 * 1.5, axis="h")
    stamp_rivet_rows(height, [(W * 0.33, 0, H), (W * 0.67, 0, H)], pitch_px=size / 1024 * 14, radius_px=size / 1024 * 1.5, axis="v")
    normal = height_to_normal(height, strength=3.0 * size / 2048)
    save_rgb(os.path.join(out_dir, "fin_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "fin_orm.png"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "fin_normal.png"))

def plain_skin_set(out_dir, name, size=1024, seed=51, rib_count=8, tint=WHITE):
    """Generic riveted painted skin for stabiliser, control surfaces, cowl, fairings."""
    H = W = size
    base, rough = paint_base(H, W, seed, tint=tint)
    height = np.zeros((H, W), np.float32)
    rows = [(H * (0.06 + 0.88 * i / max(1, rib_count - 1)), int(W * 0.03), int(W * 0.97)) for i in range(rib_count)]
    stamp_rivet_rows(height, rows, pitch_px=size / 1024 * 13, radius_px=size / 1024 * 1.4, axis="h")
    stamp_rivet_rows(height, [(W * 0.30, 0, H), (W * 0.70, 0, H)], pitch_px=size / 1024 * 13, radius_px=size / 1024 * 1.4, axis="v")
    normal = height_to_normal(height, strength=3.0 * size / 2048)
    save_rgb(os.path.join(out_dir, f"{name}_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, f"{name}_orm.png"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, f"{name}_normal.png"))

def cowl_set(out_dir, size=1024):
    """Cowl skin: u around, v nose→firewall. Camloc fasteners along the split line and the
    aft edge, louvre-free (172N has no cowl flaps)."""
    H = W = size
    base, rough = paint_base(H, W, 61)
    vv = 1 - (np.arange(H) + 0.5) / H; uu = (np.arange(W) + 0.5) / W
    V, U = np.meshgrid(vv, uu, indexing="ij")
    # the fuselage stripe continues forward on the cowl sides and fades at the nose bowl
    band = np.maximum(np.clip(1 - np.abs(U - 0.205) / 0.022, 0, 1), np.clip(1 - np.abs(U - 0.795) / 0.022, 0, 1)) ** 0.25
    band *= np.vectorize(smoothstep)(0.25, 0.45, V)
    base = blend(base, NAVY, band)
    gold = np.maximum(np.clip(1 - np.abs(U - 0.235) / 0.004, 0, 1), np.clip(1 - np.abs(U - 0.765) / 0.004, 0, 1)) * np.vectorize(smoothstep)(0.25, 0.45, V)
    base = blend(base, GOLD, gold)
    skyb = np.maximum(np.clip(1 - np.abs(U - 0.173) / 0.006, 0, 1), np.clip(1 - np.abs(U - 0.827) / 0.006, 0, 1)) * np.vectorize(smoothstep)(0.25, 0.45, V)
    base = blend(base, SKY_BLUE, skyb)
    height = np.zeros((H, W), np.float32)
    # split line (u = 0.25 and 0.75), fastener dots along it and around the aft edge
    for uc in (0.25, 0.75):
        stamp_seam(height, W * uc, int(H * 0.05), int(H * 0.95), "v", width_px=2, depth=-0.8)
    stamp_rivet_rows(height, [(W * 0.25 + 10, int(H * 0.05), int(H * 0.95)), (W * 0.75 - 10, int(H * 0.05), int(H * 0.95))], pitch_px=size / 1024 * 48, radius_px=size / 1024 * 3.2, depth=0.7, axis="v")
    stamp_rivet_rows(height, [(H * 0.06, 0, W)], pitch_px=size / 1024 * 48, radius_px=size / 1024 * 3.2, depth=0.7, axis="h")
    # oil access door on top (u ≈ 0.5), aft third
    x0, x1 = int(W * 0.46), int(W * 0.54); y0, y1 = int(H * 0.15), int(H * 0.30)
    for y in (y0, y1): stamp_seam(height, y, x0, x1, "h")
    for x in (x0, x1): stamp_seam(height, x, y0, y1, "v")
    normal = height_to_normal(height, strength=3.0 * size / 2048)
    ao = 1 - 0.2 * np.clip(-height, 0, 1)
    save_rgb(os.path.join(out_dir, "cowl_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "cowl_orm.png"), ao, rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "cowl_normal.png"))

def metal_set(out_dir, size=1024):
    """Brushed/cast aluminium tile for gear legs, engine parts, fittings."""
    H = W = size
    n = fractal_noise(H, W, 71, octaves=5, base=10)
    streak = fractal_noise(H, 8, 72, octaves=4, base=4)
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    base = np.ones((H, W, 3), np.float32) * np.asarray((0.78, 0.79, 0.80), np.float32)
    base *= (0.88 + 0.18 * (0.6 * n + 0.4 * streak))[..., None]
    rough = np.clip(0.42 + 0.18 * (streak - 0.5) + 0.1 * (n - 0.5), 0, 1)
    height = (n - 0.5) * 0.3
    normal = height_to_normal(height, strength=1.0)
    save_rgb(os.path.join(out_dir, "metal_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "metal_orm.png"), np.ones_like(rough), rough, np.ones_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "metal_normal.png"))

def rubber_set(out_dir, size=512):
    H = W = size
    n = fractal_noise(H, W, 81, octaves=5, base=12)
    base = np.ones((H, W, 3), np.float32) * np.asarray((0.05, 0.05, 0.055), np.float32) * (0.8 + 0.5 * n)[..., None]
    # tread: circumferential ribs (u direction)
    uu = (np.arange(W) + 0.5) / W
    ribs = (np.abs(((uu * 18) % 1) - 0.5) < 0.18).astype(np.float32)[None, :].repeat(H, 0)
    height = ribs * 0.8 + (n - 0.5) * 0.2
    normal = height_to_normal(height, strength=2.0)
    rough = np.clip(0.75 + 0.15 * (n - 0.5), 0, 1)
    save_rgb(os.path.join(out_dir, "rubber_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "rubber_orm.png"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "rubber_normal.png"))

def apron_set(out_dir, size=1024):
    H = W = size
    n = fractal_noise(H, W, 91, octaves=6, base=8)
    base = np.ones((H, W, 3), np.float32) * np.asarray((0.36, 0.36, 0.35), np.float32) * (0.75 + 0.5 * n)[..., None]
    rough = np.clip(0.85 + 0.1 * (n - 0.5), 0, 1)
    normal = height_to_normal((n - 0.5) * 0.6, strength=1.5)
    save_rgb(os.path.join(out_dir, "apron_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "apron_orm.png"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "apron_normal.png"))

# ----------------------------------------------------------------------------- sky HDR

def write_hdr(path, rgb):
    """Write a float32 (H, W, 3) image as Radiance RGBE (.hdr)."""
    H, W, _ = rgb.shape
    maxc = np.max(rgb, axis=-1)
    e = np.zeros((H, W), np.int32)
    m = np.zeros((H, W), np.float32)
    nz = maxc > 1e-32
    m[nz], e[nz] = np.frexp(maxc[nz])
    scale = np.where(nz, m * 256.0 / np.maximum(maxc, 1e-32), 0)
    rgbe = np.zeros((H, W, 4), np.uint8)
    rgbe[..., :3] = np.clip(rgb * scale[..., None], 0, 255).astype(np.uint8)
    rgbe[..., 3] = np.where(nz, e + 128, 0).astype(np.uint8)
    with open(path, "wb") as f:
        f.write(b"#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n")
        f.write(f"-Y {H} +X {W}\n".encode())
        f.write(rgbe.tobytes())

def sky_hdr(path, w=1024, h=512, sun_elev_deg=42, sun_az_deg=35):
    """Clear-sky gradient with a sun, over a neutral apron. Original, procedural."""
    v = (np.arange(h) + 0.5) / h                       # 0 top -> 1 bottom
    u = (np.arange(w) + 0.5) / w
    el = np.pi / 2 - v * np.pi                         # elevation per row
    az = (u * 2 * np.pi)[None, :]
    EL = el[:, None].repeat(w, 1); AZ = az.repeat(h, 0)
    zen = np.asarray((0.18, 0.36, 0.80)); hor = np.asarray((0.78, 0.86, 0.96))
    t = np.clip(EL / (np.pi / 2), 0, 1) ** 0.55
    sky = hor[None, None, :] * (1 - t[..., None]) + zen[None, None, :] * t[..., None]
    sky *= 1.1
    se, sa = math.radians(sun_elev_deg), math.radians(sun_az_deg)
    cosang = np.sin(EL) * math.sin(se) + np.cos(EL) * math.cos(se) * np.cos(AZ - sa)
    ang = np.arccos(np.clip(cosang, -1, 1))
    glow = np.exp(-(ang / 0.35) ** 2) * 1.5 + np.exp(-(ang / 0.08) ** 2) * 6
    sun = (ang < 0.012).astype(np.float32) * 2500.0
    img = sky + (glow[..., None] * np.asarray((1.0, 0.95, 0.85))) + sun[..., None] * np.asarray((1.0, 0.97, 0.9))
    ground = np.asarray((0.30, 0.29, 0.28))[None, None, :] * (0.9 + 0.3 * np.clip(-EL / (np.pi / 2), 0, 1))[..., None]
    below = (EL < 0)
    img = np.where(below[..., None], ground * (0.8 + 0.2 * np.cos(AZ - sa)[..., None] * 0.3), img)
    write_hdr(path, img.astype(np.float32))

# ----------------------------------------------------------------------------- driver

def generate_all(tex_dir, hdri_dir, size=2048, wordmark="FlyGACA", registration=""):
    os.makedirs(tex_dir, exist_ok=True); os.makedirs(hdri_dir, exist_ok=True)
    fuselage_set(tex_dir, size=size, wordmark=wordmark, registration=registration)
    from .dials import dials_atlas, panel_misc_atlas
    dials_atlas(os.path.join(tex_dir, "dials.png"))
    panel_misc_atlas(os.path.join(tex_dir, "panel_misc.png"))
    wing_set(tex_dir, size=size)
    fin_set(tex_dir, size=size // 2, wordmark=wordmark)
    plain_skin_set(tex_dir, "stab", size=size // 2, seed=52, rib_count=7)
    plain_skin_set(tex_dir, "control", size=size // 2, seed=53, rib_count=6)
    cowl_set(tex_dir, size=size // 2)
    metal_set(tex_dir, size=size // 2)
    rubber_set(tex_dir, size=512)
    apron_set(tex_dir, size=1024)
    sky_hdr(os.path.join(hdri_dir, "sky.hdr"))

def downscale_sets(tex_dir, sizes=(1024, 512)):
    """Write <tex_dir>/<size>/<name> copies of every texture for the lower quality levels."""
    for size in sizes:
        d = os.path.join(tex_dir, str(size)); os.makedirs(d, exist_ok=True)
        for fn in os.listdir(tex_dir):
            src = os.path.join(tex_dir, fn)
            if not os.path.isfile(src):
                continue
            im = Image.open(src)
            if max(im.size) <= size:
                im.save(os.path.join(d, fn), quality=88) if fn.endswith(".jpg") else im.save(os.path.join(d, fn))
                continue
            sc = size / max(im.size)
            im2 = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.LANCZOS)
            im2.save(os.path.join(d, fn), quality=88) if fn.endswith(".jpg") else im2.save(os.path.join(d, fn))

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    generate_all(os.path.join(out, "textures"), os.path.join(out, "hdri"))
    downscale_sets(os.path.join(out, "textures"))      # the medium and low quality levels use these copies
