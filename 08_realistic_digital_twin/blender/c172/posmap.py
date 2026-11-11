"""Where each texel of a painted skin lies on the aircraft.

The paint scheme is a drawing of the aircraft seen from the side. To lay it on a skin, the painter has to know,
for each texel of that skin's texture, which point of the aircraft it covers. Working that out from the tables
the skins are lofted from is only roughly right: the mesh runs straight between its rings and the subdivision
rounds it, so a stripe drawn that way wavers where the section changes quickly and steps at every joint. Here
the answer is read off the finished surface: the triangles of the subdivided skin are drawn into its texture,
carrying their positions.

The maps are written by Blender (blender/posmaps.py) and read by the texture generator, which runs outside it.
"""
import os
import numpy as np
import bpy

SIZE = 1024          # texels each way: the surface is smooth, so the painter may enlarge the map
LEVELS = 2           # the subdivision the maps are read at, whatever quality level is being built


def _bare_surface(ob):
    """Corner positions (T, 3, 3) and texture coordinates (T, 3, 2) of the skin's triangles: subdivided, but before
    it is given a thickness and cut open, so each texel has one point."""
    saved = [(m, m.show_viewport, getattr(m, "levels", None)) for m in ob.modifiers]
    for m in ob.modifiers:
        if m.type == "SUBSURF":
            m.show_viewport = True; m.levels = LEVELS
        else:
            m.show_viewport = False
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    co = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    uv = np.empty(len(me.loops) * 2, np.float64); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    tv = np.empty(n * 3, np.int64); me.loop_triangles.foreach_get("vertices", tv)
    tl = np.empty(n * 3, np.int64); me.loop_triangles.foreach_get("loops", tl)
    M = np.array(ob.matrix_world)
    world = co @ M[:3, :3].T + M[:3, 3]
    P, UV = world[tv].reshape(n, 3, 3), uv[tl].reshape(n, 3, 2)
    ev.to_mesh_clear()
    for m, shown, levels in saved:
        m.show_viewport = shown
        if levels is not None:
            m.levels = levels
    bpy.context.view_layer.update()
    return P, UV


def rasterize(P, UV, size=SIZE):
    """Draw the triangles into the texture: (size, size, 3) positions, row 0 at v = 1, NaN where no triangle lies.
    The texture repeats round the section, so u is taken modulo 1 (the lower cowl runs from u = 0.75 to 1.25).
    Triangles above v = 1 or below v = 0 (the end caps of a loft, see shapes.loft) are left out."""
    out = np.full((size, size, 3), np.nan, np.float32)
    inside = (UV[..., 1].min(axis=1) > -1e-6) & (UV[..., 1].max(axis=1) < 1 + 1e-6)
    P, UV = P[inside], UV[inside].copy()
    UV[..., 0] -= np.floor(UV[..., 0].min(axis=1) + 1e-9)[:, None]
    over = UV[..., 0].max(axis=1) > 1 + 1e-9                    # a triangle across the seam is drawn on both sides of it
    if over.any():
        again = UV[over].copy(); again[..., 0] -= 1.0
        P, UV = np.concatenate([P, P[over]]), np.concatenate([UV, again])
    X = UV[..., 0] * size - 0.5; Y = (1.0 - UV[..., 1]) * size - 0.5          # in texel centres
    area = (X[:, 1] - X[:, 0]) * (Y[:, 2] - Y[:, 0]) - (X[:, 2] - X[:, 0]) * (Y[:, 1] - Y[:, 0])
    x0 = np.clip(np.floor(X.min(1)).astype(int), 0, size - 1); x1 = np.clip(np.ceil(X.max(1)).astype(int), 0, size - 1)
    y0 = np.clip(np.floor(Y.min(1)).astype(int), 0, size - 1); y1 = np.clip(np.ceil(Y.max(1)).astype(int), 0, size - 1)
    eps = 1e-4
    for t in np.nonzero(np.abs(area) > 1e-10)[0]:
        gx, gy = np.meshgrid(np.arange(x0[t], x1[t] + 1), np.arange(y0[t], y1[t] + 1))
        dx, dy = gx - X[t, 0], gy - Y[t, 0]
        w1 = (dx * (Y[t, 2] - Y[t, 0]) - (X[t, 2] - X[t, 0]) * dy) / area[t]
        w2 = ((X[t, 1] - X[t, 0]) * dy - dx * (Y[t, 1] - Y[t, 0])) / area[t]
        w0 = 1.0 - w1 - w2
        m = (w0 >= -eps) & (w1 >= -eps) & (w2 >= -eps)
        if m.any():
            out[gy[m], gx[m]] = w0[m, None] * P[t, 0] + w1[m, None] * P[t, 1] + w2[m, None] * P[t, 2]
    return out


def spread(pos, steps=24):
    """Carry the positions a few texels past the edge of what was drawn, so that the painter's enlarging and the
    filtering of the finished texture never mix in a texel that lies nowhere."""
    for _ in range(steps):
        hole = np.isnan(pos[..., 0])
        if not hole.any():
            break
        total = np.zeros_like(pos); count = np.zeros(pos.shape[:2], np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            src = np.full_like(pos, np.nan)
            ys = slice(max(dy, 0), pos.shape[0] + min(dy, 0)); yd = slice(max(-dy, 0), pos.shape[0] + min(-dy, 0))
            xs = slice(max(dx, 0), pos.shape[1] + min(dx, 0)); xd = slice(max(-dx, 0), pos.shape[1] + min(-dx, 0))
            src[yd, xd] = pos[ys, xs]
            ok = ~np.isnan(src[..., 0])
            total[ok] += src[ok]; count[ok] += 1
        fill = hole & (count > 0)
        pos[fill] = total[fill] / count[fill][:, None]
    return pos


def write(out_dir, skins, size=SIZE):
    """skins: texture name -> names of the objects that wear it (their texture layouts must not overlap)."""
    os.makedirs(out_dir, exist_ok=True)
    for name, objects in skins.items():
        parts = [_bare_surface(bpy.data.objects[o]) for o in objects]
        P = np.concatenate([p for p, _ in parts]); UV = np.concatenate([u for _, u in parts])
        pos = rasterize(P, UV, size)
        drawn = float(np.mean(~np.isnan(pos[..., 0])))
        pos = spread(pos)
        np.save(os.path.join(out_dir, name + ".npy"), pos)
        print(f"position map {name}: {len(P)} triangles, {drawn:.1%} of the texture drawn")


_skins = {}


def wear_skin(ob, skin, assets, material):
    """Give a plate that lies in a painted skin the paint of that skin, so that a stripe runs across it unbroken:
    each of its corners takes the texture coordinates of the point of the skin nearest to it (from the skin's
    position map), and the plate takes the skin's material. The plate must stand in the build frame."""
    if skin not in _skins:
        path = os.path.join(assets, "posmaps", skin + ".npy")
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} is missing: write the position maps first (blender -b --python blender/posmaps.py)")
        grid = np.load(path)
        ok = ~np.isnan(grid[..., 0])
        rows, cols = np.nonzero(ok)
        _skins[skin] = (grid, grid[ok], rows, cols)
    grid, P, rows, cols = _skins[skin]
    size = grid.shape[0]
    me = ob.data; M = ob.matrix_world
    uvs = {}
    for v in me.vertices:
        p = np.asarray(M @ v.co, np.float32)
        i = int(np.argmin(((P - p) ** 2).sum(axis=1)))
        r, c = int(rows[i]), int(cols[i])
        du = dv = 0.0
        if 0 < r < size - 1 and 0 < c < size - 1:
            a = (grid[r, c + 1] - grid[r, c - 1]) / 2; b = (grid[r + 1, c] - grid[r - 1, c]) / 2
            if not (np.isnan(a).any() or np.isnan(b).any()):          # within the texel: its neighbours say how the surface runs there
                sol = np.linalg.lstsq(np.stack([a, b], axis=1), p - grid[r, c], rcond=None)[0]
                du, dv = float(np.clip(sol[0], -1, 1)), float(np.clip(sol[1], -1, 1))
        uvs[v.index] = ((c + 0.5 + du) / size, 1.0 - (r + 0.5 + dv) / size)
    layer = me.uv_layers.active or me.uv_layers.new()
    for loop in me.loops:
        layer.data[loop.index].uv = uvs[loop.vertex_index]
    me.materials.clear(); me.materials.append(material)
