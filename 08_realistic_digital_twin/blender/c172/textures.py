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
    """Occlusion, roughness and metalness in the three channels. They vary gently, so a JPEG a sixth the size of a
    PNG shows no difference; the channels are kept at full resolution (no chroma subsampling)."""
    arr = np.stack([ao, rough, metal], -1)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if path.lower().endswith(".jpg"):
        img.save(path, quality=88, subsampling=0)
    else:
        img.save(path)

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

def sstep(a, b, x):
    """Smoothstep on arrays."""
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)

def periodic_noise(h, w, seed, low=2.0, high=24.0):
    """Noise in [0, 1] that tiles exactly: white noise with only a band of wavelengths kept (cycles per image)."""
    rng = _rng(seed)
    f = np.fft.fft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None] * h; fx = np.fft.fftfreq(w)[None, :] * w
    r = np.sqrt(fx * fx + fy * fy)
    f *= np.exp(-((r - (low + high) / 2) / ((high - low) / 2 + 1e-6)) ** 2)
    n = np.real(np.fft.ifft2(f))
    n = (n - n.mean()) / (n.std() + 1e-9)
    return np.clip(0.5 + n * 0.22, 0, 1).astype(np.float32)

def paint_base(h, w, seed, tint=WHITE, grain=0.012):
    """Sprayed paint: an even colour with the faintest mottle, and a gloss that varies a little from panel to panel."""
    n = fractal_noise(h, w, seed, octaves=3, base=6)
    base = np.ones((h, w, 3), np.float32) * np.asarray(tint, np.float32)
    base *= (1 - grain + grain * 2 * n)[..., None]
    rough = 0.30 + 0.06 * (fractal_noise(h, w, seed + 7, octaves=4, base=8) - 0.5)
    return base, rough

def rivet_field(h, w):
    return np.zeros((h, w), np.float32)

def finish_skin(base, height, rivets, strength_px):
    """Darken the paint a little in the seams and round the rivets, and turn the relief into a normal map."""
    base = base * (1 - 0.16 * np.clip(-height, 0, 1) - 0.05 * np.clip(rivets, 0, 1))[..., None]
    return base, height_to_normal(height + rivets * 0.5, strength=strength_px)

# ---- the paint scheme: a drawing of the aircraft seen from the side, in station (inches aft of the firewall) and
# height (m, build frame). Each painted skin is given it through its position map (posmap.py), so a stripe is the
# same line in space on the cowl, the fuselage, a door, the fin and the rudder, and runs across their joints unbroken.
IN = 0.0254
BAND_Z = 1.375            # centre of the main band along the cabin and the tailcone: just under the widest line of the fuselage
BAND_HALF = 0.065         # half its height: a band of 13 cm
NOSE_Z = 1.585            # where the band ends at the nose bowl: a little under the spinner
TAIL_FROM = 186.0         # station where the band leaves the tailcone and sweeps up the fin
TAIL_SLOPE = 0.42         # how steeply it climbs there (height per length)
TAIL_BEND = 12.0          # inches over which it turns from level to that slope

def band_centre(station):
    """Height of the middle of the band at a station: from a point at the nose bowl, level along the cabin and the
    tailcone, then up across the fin and the rudder."""
    nose = NOSE_Z + (BAND_Z - NOSE_Z) * sstep(-33.0, -2.0, station)
    return nose + TAIL_SLOPE * IN * TAIL_BEND * np.logaddexp(0.0, (station - TAIL_FROM) / TAIL_BEND)

def scheme_masks(station, z):
    """Coverage of the navy band, of the gold line under it and of the thin navy line over it at the points of a
    skin (2-D arrays of station and height, one value a texel). Returns three arrays in [0, 1]."""
    f = z - band_centre(station)
    aa = np.maximum(np.abs(np.gradient(f, axis=1)), np.abs(np.gradient(f, axis=0))) + 1e-5      # what one texel covers, for the edges
    grow = sstep(-33.4, -13.0, station)                    # the band grows from a point at the nose bowl
    def bar(offset, half):
        return np.clip((f - (offset - half)) / aa + 0.5, 0, 1) * np.clip(((offset + half) - f) / aa + 0.5, 0, 1) * (half > 1e-4)
    navy = bar(0.0, BAND_HALF * grow)
    gold = bar(-(BAND_HALF + 0.034) * grow, 0.012 * grow)
    line = bar((BAND_HALF + 0.028) * grow, 0.0055 * grow)
    return navy, gold, line

def positions(tex_dir, name, size):
    """Where each texel of a skin lies: (size, size, 3) in the build frame (x to the left, y aft, z up), row 0 at v = 1.
    Read from the position map that Blender wrote (blender/posmaps.py); texels of no surface lie far below."""
    path = os.path.join(os.path.dirname(os.path.abspath(tex_dir)), "posmaps", name + ".npy")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is missing: write the position maps first (blender -b --python blender/posmaps.py)")
    pos = np.load(path)
    pos = np.where(np.isnan(pos), np.float32(-1000.0), pos)
    if pos.shape[0] == size:
        return pos
    return np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(pos[..., i]), "F").resize((size, size), Image.BILINEAR)) for i in range(3)], axis=-1)

def side_view(tex_dir, name, size):
    """Station (inches) and height (m) of each texel of a skin."""
    pos = positions(tex_dir, name, size)
    return pos[..., 1] / IN + 40.0, pos[..., 2]

def paint_scheme(base, station, z):
    """Lay the scheme on a skin whose texels lie at (station, z) in side view."""
    navy, gold, line = scheme_masks(station, z)
    base = blend(base, NAVY, np.maximum(navy, line))
    return blend(base, GOLD, gold)

def fuselage_set(out_dir, size=2048, colour_size=None, length_m=7.2, circ_m=3.6):
    """Fuselage skin. u: 0 bottom, 0.25 right side, 0.5 top, 0.75 left side. v: 0 firewall → 1 tail.
    The paint is larger than the relief (colour_size): edges of the scheme stay sharp close up."""
    C = colour_size or size
    base, _ = paint_base(C, C, 11)
    vv = 1 - (np.arange(C) + 0.5) / C
    U = ((np.arange(C) + 0.5) / C)[None, :].astype(np.float32)
    base = paint_scheme(base, *side_view(out_dir, "fuselage", C))
    # ---- wear: a little road dirt on the belly, exhaust soot aft of the stack (right-hand belly, forward)
    V = vv[:, None].astype(np.float32) * np.ones_like(U); Uf = U * np.ones_like(V)
    dirt = np.asarray(Image.fromarray((fractal_noise(512, 512, 23, octaves=5, base=6) * 255).astype(np.uint8)).resize((C, C), Image.BICUBIC), np.float32) / 255
    belly = np.clip(1 - np.minimum(Uf, 1 - Uf) / 0.09, 0, 1)
    base *= (1 - 0.07 * belly * dirt)[..., None]
    soot = np.exp(-((Uf - 0.11) / 0.045) ** 2) * np.exp(-((V - 0.10) / 0.11) ** 2) * (V > 0.02)
    base *= (1 - 0.30 * soot * (0.5 + dirt))[..., None]
    # ---- relief, at its own size: frames and stringers as fine rivet lines, inspection plates as seams
    H = W = size
    _, rough = paint_base(H, W, 11)
    px_per_m_v = H / length_m; px_per_m_u = W / circ_m
    height = np.zeros((H, W), np.float32); rivets = rivet_field(H, W)
    frames_m = [0.0, 0.45, 0.95, 1.55, 2.05, 2.55, 2.9, 3.35, 3.9, 4.5, 5.1, 5.7, 6.3, 6.85, 7.15]
    rows = []
    for fm in frames_m:
        y = H - fm * px_per_m_v
        if 4 < y < H - 4:
            rows.append((y, 0, W))
            stamp_seam(height, y + 4, 0, W, axis="h", width_px=1, depth=-0.5)
    stamp_rivet_rows(rivets, rows, pitch_px=0.024 * px_per_m_u, radius_px=size / 2048 * 1.5, axis="h")
    cols = [(W * k / 20, 0, H) for k in range(20)]
    stamp_rivet_rows(rivets, cols, pitch_px=0.026 * px_per_m_v, radius_px=size / 2048 * 1.5, axis="v")
    for (u0, u1, v0, v1) in [(0.02, 0.07, 0.30, 0.36), (0.93, 0.98, 0.30, 0.36), (0.47, 0.53, 0.75, 0.80), (0.04, 0.09, 0.60, 0.66)]:
        x0, x1 = int(u0 * W), int(u1 * W); y0, y1 = int((1 - v1) * H), int((1 - v0) * H)
        stamp_seam(height, y0, x0, x1, "h", width_px=1, depth=-0.6); stamp_seam(height, y1, x0, x1, "h", width_px=1, depth=-0.6)
        stamp_seam(height, x0, y0, y1, "v", width_px=1, depth=-0.6); stamp_seam(height, x1, y0, y1, "v", width_px=1, depth=-0.6)
    normal = height_to_normal(height + rivets * 0.5, strength=1.6 * size / 2048)
    # the seams and the rivets show faintly in the paint too
    relief = np.asarray(Image.fromarray(((np.clip(-height, 0, 1) * 0.16 + np.clip(rivets, 0, 1) * 0.05) * 255).astype(np.uint8)).resize((C, C), Image.BILINEAR), np.float32) / 255
    base *= (1 - relief)[..., None]
    soot_r = np.asarray(Image.fromarray((np.clip(soot, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    rough = np.clip(rough + 0.25 * soot_r, 0, 1)
    ao = 1 - 0.25 * np.clip(-height, 0, 1)
    save_rgb(os.path.join(out_dir, "fuselage_albedo.jpg"), base, quality=93)
    save_orm(os.path.join(out_dir, "fuselage_orm.jpg"), ao, rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "fuselage_normal.png"))

def wing_set(out_dir, size=2048, semispan_m=5.46, chord_m=1.64, tip_color=NAVY, name="wing"):
    """Wing skin: u around the airfoil (TE→upper→LE→lower→TE), v root→tip."""
    H = W = size
    base, rough = paint_base(H, W, 31)
    vv = 1 - (np.arange(H) + 0.5) / H
    uu = (np.arange(W) + 0.5) / W
    V, U = np.meshgrid(vv, uu, indexing="ij")
    aa = 1.2 / H
    base = blend(base, tip_color, np.clip((V - 0.958) / aa + 0.5, 0, 1))
    base = blend(base, GOLD, np.clip((V - 0.9455) / aa + 0.5, 0, 1) * np.clip((0.9525 - V) / aa + 0.5, 0, 1))
    # grime along the lower surface near the root (u > 0.5 is the lower surface)
    dirt = fractal_noise(H, W, 37, octaves=5, base=6)
    lower = (U > 0.52).astype(np.float32)
    base *= (1 - 0.06 * lower * dirt * (1 - V))[..., None]
    rough = np.clip(rough + 0.08 * lower * dirt, 0, 1)
    # rivets: ribs (constant v), spar caps (constant u at x/c 0.25 & 0.68 top and bottom)
    af = naca4("2412", 40)
    px_v = H / semispan_m; px_u = W / (2 * chord_m)
    height = np.zeros((H, W), np.float32); rivets = rivet_field(H, W)
    rib_pitch = 0.40
    rows = []
    s_ = 0.12
    while s_ < semispan_m - 0.05:
        rows.append((H - s_ * px_v, int(W * 0.02), int(W * 0.98)))
        s_ += rib_pitch
    stamp_rivet_rows(rivets, rows, pitch_px=0.026 * px_u, radius_px=size / 2048 * 1.5, axis="h")
    cols = []
    for xc in (0.25, 0.68):
        for up in (True, False):
            cols.append((W * airfoil_u_of_x(af, xc, up), 0, H))
    stamp_rivet_rows(rivets, cols, pitch_px=0.026 * px_v, radius_px=size / 2048 * 1.5, axis="v")
    # tank bay access panels on the upper surface, inboard
    for (xa, xb, sa, sb) in [(0.30, 0.50, 0.55, 0.85), (0.30, 0.50, 1.20, 1.50)]:
        ua, ub = airfoil_u_of_x(af, xb, True), airfoil_u_of_x(af, xa, True)
        x0, x1 = int(ua * W), int(ub * W); y0, y1 = int(H - sb * px_v), int(H - sa * px_v)
        for y in (y0, y1): stamp_seam(height, y, x0, x1, "h", width_px=1, depth=-0.7)
        for x in (x0, x1): stamp_seam(height, x, y0, y1, "v", width_px=1, depth=-0.7)
    base, normal = finish_skin(base, height, rivets, 1.6 * size / 2048)
    ao = 1 - 0.25 * np.clip(-height, 0, 1)
    save_rgb(os.path.join(out_dir, f"{name}_albedo.jpg"), base, quality=93)
    save_orm(os.path.join(out_dir, f"{name}_orm.jpg"), ao, rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, f"{name}_normal.png"))

def fin_set(out_dir, size=1024):
    """Vertical fin skin: u around the section (TE→right side→LE→left side), v root→tip.
    The band of the fuselage sweeps up across it and carries on over the rudder."""
    H = W = size
    base, rough = paint_base(H, W, 41)
    base = paint_scheme(base, *side_view(out_dir, "fin", size))
    height = np.zeros((H, W), np.float32); rivets = rivet_field(H, W)
    rows = [(H - H * (0.1 + 0.15 * i), 0, W) for i in range(6)]
    stamp_rivet_rows(rivets, rows, pitch_px=size / 1024 * 12, radius_px=size / 1024 * 1.2, axis="h")
    stamp_rivet_rows(rivets, [(W * 0.33, 0, H), (W * 0.67, 0, H)], pitch_px=size / 1024 * 12, radius_px=size / 1024 * 1.2, axis="v")
    base, normal = finish_skin(base, height, rivets, 1.6 * size / 2048)
    save_rgb(os.path.join(out_dir, "fin_albedo.jpg"), base, quality=93)
    save_orm(os.path.join(out_dir, "fin_orm.jpg"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "fin_normal.png"))

def plain_skin_set(out_dir, name, size=1024, seed=51, rib_count=8, tint=WHITE, scheme_of=None, colour_only=False):
    """Generic riveted painted skin for stabiliser, control surfaces, fairings. scheme_of: the position map to lay
    the paint scheme through; colour_only: write the colour alone (the skin shares the relief of another)."""
    H = W = size
    base, rough = paint_base(H, W, seed, tint=tint)
    if scheme_of:
        base = paint_scheme(base, *side_view(out_dir, scheme_of, size))
    height = np.zeros((H, W), np.float32); rivets = rivet_field(H, W)
    rows = [(H * (0.06 + 0.88 * i / max(1, rib_count - 1)), int(W * 0.03), int(W * 0.97)) for i in range(rib_count)]
    stamp_rivet_rows(rivets, rows, pitch_px=size / 1024 * 11, radius_px=size / 1024 * 1.2, axis="h")
    stamp_rivet_rows(rivets, [(W * 0.30, 0, H), (W * 0.70, 0, H)], pitch_px=size / 1024 * 11, radius_px=size / 1024 * 1.2, axis="v")
    base, normal = finish_skin(base, height, rivets, 1.6 * size / 2048)
    save_rgb(os.path.join(out_dir, f"{name}_albedo.jpg"), base, quality=93 if scheme_of else 90)
    if colour_only:
        return
    save_orm(os.path.join(out_dir, f"{name}_orm.jpg"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, f"{name}_normal.png"))

def cowl_set(out_dir, size=1024, colour_size=None):
    """Cowl skin: u round the section as on the fuselage, v from the nose face to the firewall. The paint scheme of the
    fuselage carries on across the firewall and ends in a point at the nose bowl. Quick-release fasteners along the
    split line and round the rear edge; no louvres (the 172N has no cowl flaps)."""
    H = W = size
    C = colour_size or size                       # the paint is as fine as on the fuselage: the band crosses the firewall joint
    base, _ = paint_base(C, C, 61)
    _, rough = paint_base(H, W, 61)
    base = paint_scheme(base, *side_view(out_dir, "cowl", C))
    height = np.zeros((H, W), np.float32); rivets = rivet_field(H, W)
    # split line (u = 0.25 and 0.75), quarter-turn fasteners along it and round the rear edge
    for uc in (0.25, 0.75):
        stamp_seam(height, W * uc, int(H * 0.05), int(H * 0.95), "v", width_px=2, depth=-0.8)
    stamp_rivet_rows(rivets, [(W * 0.25 + 9, int(H * 0.05), int(H * 0.95)), (W * 0.75 - 9, int(H * 0.05), int(H * 0.95))], pitch_px=size / 1024 * 56, radius_px=size / 1024 * 3.0, depth=0.9, axis="v")
    stamp_rivet_rows(rivets, [(H * 0.055, 0, W)], pitch_px=size / 1024 * 56, radius_px=size / 1024 * 3.0, depth=0.9, axis="h")
    # oil filler door on top (u ≈ 0.5), rear third
    x0, x1 = int(W * 0.46), int(W * 0.54); y0, y1 = int(H * 0.15), int(H * 0.30)
    for y in (y0, y1): stamp_seam(height, y, x0, x1, "h", width_px=1, depth=-0.7)
    for x in (x0, x1): stamp_seam(height, x, y0, y1, "v", width_px=1, depth=-0.7)
    normal = height_to_normal(height + rivets * 0.5, strength=1.6 * size / 2048)
    relief = np.asarray(Image.fromarray(((np.clip(-height, 0, 1) * 0.16 + np.clip(rivets, 0, 1) * 0.05) * 255).astype(np.uint8)).resize((C, C), Image.BILINEAR), np.float32) / 255
    base *= (1 - relief)[..., None]
    ao = 1 - 0.2 * np.clip(-height, 0, 1)
    save_rgb(os.path.join(out_dir, "cowl_albedo.jpg"), base, quality=93)
    save_orm(os.path.join(out_dir, "cowl_orm.jpg"), ao, rough, np.zeros_like(rough))
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
    save_orm(os.path.join(out_dir, "metal_orm.jpg"), np.ones_like(rough), rough, np.ones_like(rough))
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
    save_orm(os.path.join(out_dir, "rubber_orm.jpg"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "rubber_normal.png"))

def apron_set(out_dir, size=1024):
    H = W = size
    n = fractal_noise(H, W, 91, octaves=6, base=8)
    base = np.ones((H, W, 3), np.float32) * np.asarray((0.36, 0.36, 0.35), np.float32) * (0.75 + 0.5 * n)[..., None]
    rough = np.clip(0.85 + 0.1 * (n - 0.5), 0, 1)
    normal = height_to_normal((n - 0.5) * 0.6, strength=1.5)
    save_rgb(os.path.join(out_dir, "apron_albedo.jpg"), base)
    save_orm(os.path.join(out_dir, "apron_orm.jpg"), np.ones_like(rough), rough, np.zeros_like(rough))
    Image.fromarray(normal).save(os.path.join(out_dir, "apron_normal.png"))

# ----------------------------------------------------------------------------- interior

def _tile_normal(height, strength):
    """Normal map of a height field that tiles (the edges wrap)."""
    h = height.astype(np.float32)
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    dy = (np.roll(h, 1, 0) - np.roll(h, -1, 0)) * 0.5
    nx = -dx * strength; ny = -dy * strength; nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return ((np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5) * 255).astype(np.uint8)

def _save_tile(out_dir, name, colour, height, strength, mottle=None):
    base = np.ones(height.shape + (3,), np.float32) * np.asarray(colour, np.float32)
    if mottle is not None:
        base *= mottle[..., None]
    save_rgb(os.path.join(out_dir, f"{name}_albedo.jpg"), base, quality=90)
    Image.fromarray(_tile_normal(height, strength)).save(os.path.join(out_dir, f"{name}_normal.jpg"), quality=84, subsampling=0)

def interior_sets(out_dir, size=512):
    """Tiles for the cabin: vinyl, woven cloth, carpet, the wrinkle finish of the panel, the perforated headliner.
    Each tiles exactly. Colours are those of a late-1970s interior in tan; nothing here is a manufacturer's pattern."""
    S = size
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S
    # vinyl: a leather grain of small cells
    grain = periodic_noise(S, S, 101, low=26, high=70)
    cells = periodic_noise(S, S, 102, low=8, high=22)
    vinyl_h = 0.65 * grain + 0.35 * cells
    mott = 0.97 + 0.06 * periodic_noise(S, S, 103, low=2, high=7)
    _save_tile(out_dir, "vinyl_tan", (0.66, 0.53, 0.37), vinyl_h, 2.6, mott)
    _save_tile(out_dir, "vinyl_cream", (0.80, 0.76, 0.68), vinyl_h, 2.0, 0.96 + 0.08 * periodic_noise(S, S, 104, low=2, high=6))
    _save_tile(out_dir, "vinyl_black", (0.045, 0.045, 0.05), vinyl_h, 3.0, 0.85 + 0.3 * periodic_noise(S, S, 105, low=2, high=7))
    # cloth: a plain weave, warp over weft, with slubs
    n = 48
    warp = 0.5 + 0.5 * np.cos(2 * np.pi * xx * n); weft = 0.5 + 0.5 * np.cos(2 * np.pi * yy * n)
    over = ((np.floor(xx * n) + np.floor(yy * n)) % 2).astype(np.float32)
    weave = over * warp + (1 - over) * weft
    slub = periodic_noise(S, S, 106, low=3, high=14)
    cloth_h = 0.8 * weave + 0.2 * slub
    _save_tile(out_dir, "cloth_brown", (0.37, 0.26, 0.17), cloth_h, 2.6, (0.90 + 0.13 * weave) * (0.93 + 0.14 * slub))
    # carpet: cut pile, speckled
    pile = periodic_noise(S, S, 107, low=40, high=110); tuft = periodic_noise(S, S, 108, low=10, high=30)
    _save_tile(out_dir, "carpet", (0.20, 0.17, 0.14), 0.7 * pile + 0.3 * tuft, 4.0, 0.70 + 0.6 * pile)
    # the panel: black wrinkle finish
    wr = periodic_noise(S, S, 109, low=30, high=80)
    _save_tile(out_dir, "panel_black", (0.060, 0.062, 0.066), wr, 3.4, 0.85 + 0.3 * periodic_noise(S, S, 110, low=3, high=9))
    # headliner: perforated vinyl, a hole every few millimetres
    m = 32
    hole = np.clip(1 - np.hypot((xx * m) % 1 - 0.5, (yy * m) % 1 - 0.5) / 0.20, 0, 1) ** 0.5
    _save_tile(out_dir, "headliner", (0.83, 0.81, 0.75), 0.35 * grain - 0.9 * hole, 2.4, 1 - 0.30 * hole)

def liner_set(out_dir, size=1024):
    """The cabin walls, painted where each texel lies: carpet on the kick panels low down, tan vinyl to the window
    sills with a darker band and a line of stitching, cream above and on the roof. u, v as on the fuselage skin
    (u round the section, v from station 2 to station 116)."""
    H = W = size
    z = positions(out_dir, "liner", size)[..., 2]
    aa = np.maximum(np.maximum(np.abs(np.gradient(z, axis=1)), np.abs(np.gradient(z, axis=0))), 1e-5)
    def above(level):
        return np.clip((z - level) / aa + 0.5, 0, 1)
    carpet = np.asarray((0.20, 0.17, 0.14), np.float32); tan = np.asarray((0.66, 0.53, 0.37), np.float32)
    dark = np.asarray((0.42, 0.31, 0.20), np.float32); cream = np.asarray((0.80, 0.76, 0.68), np.float32)
    base = np.ones((H, W, 3), np.float32) * carpet
    base = blend(base, tan, above(1.14))
    base = blend(base, dark, above(1.335) * (1 - above(1.385)))              # the band at arm-rest height
    base = blend(base, cream, above(1.50))
    stitch = above(1.318) * (1 - above(1.324))
    dash = ((np.arange(H)[:, None] // max(2, H // 256)) % 2).astype(np.float32)
    base = blend(base, np.asarray((0.86, 0.80, 0.66), np.float32), stitch * dash)
    base *= (0.95 + 0.10 * fractal_noise(H, W, 121, octaves=3, base=5))[..., None]
    save_rgb(os.path.join(out_dir, "liner_albedo.jpg"), base, quality=90)

# ----------------------------------------------------------------------------- markings (decals)

from .atlas import DECAL_LAYOUT as _DECAL_LAYOUT, DECAL_SIZE, decal_cells, write_cells      # noqa: E402  (the layout is shared with the builders)

def decal_atlas(path):
    """Markings that are laid on the skin as separate pieces, so that they stay sharp and undistorted at every size:
    the operator's wordmark and the small placards of any light aircraft. Transparent where there is no paint."""
    W, H = DECAL_SIZE
    img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    for name, lines, (x, y, w, h), colour, style in _DECAL_LAYOUT:
        rgb = tuple(int(round(c * 255)) for c in colour)
        tile = Image.new("L", (w * 2, h * 2), 0)              # drawn at twice the size, then reduced: clean edges
        d = ImageDraw.Draw(tile)
        if style == "wordmark":
            f = ImageFont.truetype(FONT_BOLD, int(h * 2 * 0.80))
            bb = f.getbbox(lines[0]); tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.text(((w * 2 - tw) / 2 - bb[0], (h * 2 - th) / 2 - bb[1]), lines[0], 255, font=f)
            tile = tile.transform(tile.size, Image.AFFINE, (1, 0.18, -0.18 * tile.size[1] / 2, 0, 1, 0), Image.BICUBIC)      # a forward slant
        else:
            # the largest letters that fit the box, in width and in height
            size = int(h * 2 * (0.62 if len(lines) == 1 else 0.36))
            while size > 8 and max(ImageFont.truetype(FONT_BOLD, size).getbbox(line)[2] for line in lines) > w * 2 * 0.86:
                size -= 2
            f = ImageFont.truetype(FONT_BOLD, size)
            total = len(lines) * size * 1.18
            for i, line in enumerate(lines):
                bb = f.getbbox(line); tw = bb[2] - bb[0]
                d.text(((w * 2 - tw) / 2 - bb[0], (h * 2 - total) / 2 + i * size * 1.18 - bb[1] + size * 0.08), line, 255, font=f)
            if style == "placard":
                d.rounded_rectangle((6, 6, w * 2 - 7, h * 2 - 7), radius=int(h * 0.22), outline=255, width=max(4, h // 14))
        tile = tile.resize((w, h), Image.LANCZOS)
        layer = Image.new("RGBA", (w, h), rgb + (0,)); layer.putalpha(tile)
        img.paste(layer, (x, y), layer)
    # carry the paint colour into the transparent texels round each marking, so that no white fringe shows when it is filtered
    arr = np.asarray(img, np.float32)
    for name, _l, (x, y, w, h), colour, _s in _DECAL_LAYOUT:
        box = arr[y:y + h, x:x + w]
        box[..., :3] = np.asarray(colour, np.float32) * 255
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(path)

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

def generate_all(tex_dir, hdri_dir, size=2048):
    os.makedirs(tex_dir, exist_ok=True); os.makedirs(hdri_dir, exist_ok=True)
    fuselage_set(tex_dir, size=size, colour_size=size * 2)
    from .dials import dials_atlas, panel_misc_atlas, placard_atlas, wood_panel
    dials_atlas(os.path.join(tex_dir, "dials.png"))
    panel_misc_atlas(os.path.join(tex_dir, "panel_misc.png"))
    placard_atlas(os.path.join(tex_dir, "panel_placards.png"))
    wood_panel(os.path.join(tex_dir, "wood_albedo.jpg"))
    write_cells(os.path.join(tex_dir, "atlas_cells.json"), FONT_BOLD)      # the layout of the lettering, for the builders
    wing_set(tex_dir, size=size)
    fin_set(tex_dir, size=size // 2)
    plain_skin_set(tex_dir, "stab", size=size // 2, seed=52, rib_count=7)
    plain_skin_set(tex_dir, "control", size=size // 2, seed=53, rib_count=6)
    plain_skin_set(tex_dir, "rudder", size=size // 2, seed=53, rib_count=6, scheme_of="rudder", colour_only=True)      # the relief of the control surfaces, with the band
    cowl_set(tex_dir, size=size // 2, colour_size=size)
    metal_set(tex_dir, size=size // 2)
    rubber_set(tex_dir, size=512)
    interior_sets(tex_dir, size=512)
    liner_set(tex_dir, size=2048)
    decal_atlas(os.path.join(tex_dir, "decals.png"))
    apron_set(tex_dir, size=1024)
    sky_hdr(os.path.join(hdri_dir, "sky.hdr"))

def downscale_sets(tex_dir, sizes=(1024,), nominal=2048):
    """Write <tex_dir>/<size>/<name> copies of every texture for the lower quality levels: each is reduced by
    size / nominal, so the large paint of the fuselage stays twice as fine as the rest; small tiles are kept."""
    for size in sizes:
        d = os.path.join(tex_dir, str(size)); os.makedirs(d, exist_ok=True)
        for fn in sorted(os.listdir(tex_dir)):
            src = os.path.join(tex_dir, fn)
            if not os.path.isfile(src) or not fn.endswith((".jpg", ".png")):
                continue
            im = Image.open(src)
            target = max(size, int(round(max(im.size) * size / nominal))) if max(im.size) > size else max(im.size)
            if target >= max(im.size):
                im2 = im
            else:
                sc = target / max(im.size)
                im2 = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.LANCZOS)
            if fn.endswith(".jpg"):
                im2.save(os.path.join(d, fn), quality=90, subsampling=0)
            else:
                im2.save(os.path.join(d, fn))

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    generate_all(os.path.join(out, "textures"), os.path.join(out, "hdri"))
    downscale_sets(os.path.join(out, "textures"))      # the medium and low quality levels use these copies
