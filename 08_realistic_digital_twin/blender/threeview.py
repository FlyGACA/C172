"""Orthographic line drawings of the built model at a known scale (run inside Blender).

    blender -b models/C172N_realistic.blend --python blender/threeview.py -- --out /tmp/threeview

Writes model_side.png, model_top.png and model_front.png (black lines on transparent) and
threeview.json, which gives for every picture the scale in pixels per inch and the pixel that
corresponds to a reference point of the aircraft. With those two numbers a picture can be laid over
any drawing of the aircraft: the POH three-view (Figure 1-1) and the cabin drawing (Figure 6-4) are
how the outline of this model is checked, see docs/05_shape_reference.md.

The views follow the handbook: side view of the left side with the nose to the left, top view with
the nose down, front view as seen from ahead (the aircraft's left wing on the right).
The drawing code is the one the book figures use (09_book_figures/blender: exact part, depth and
normal data, lines found in numpy).
"""
import argparse
import json
import os
import sys
import tempfile

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "09_book_figures", "blender"))
import render_figure as RF          # noqa: E402
from ink import find_lines, halve   # noqa: E402
from c172 import units as U         # noqa: E402

IN = 0.0254
# name: camera direction, picture window in inches (horizontal a0..a1, vertical b0..b1) and what the axes mean
VIEWS = {
    "side":  dict(h=("fs", -60.0, 300.0), v=("wl", -8.0, 118.0)),
    "top":   dict(h=("bl", -222.0, 222.0), v=("fs", -60.0, 300.0)),       # image up = aft
    "front": dict(h=("bl", -222.0, 222.0), v=("wl", -8.0, 118.0)),
}


def camera_spec(view):
    h, v = VIEWS[view]["h"], VIEWS[view]["v"]
    hc, vc = (h[1] + h[2]) / 2, (v[1] + v[2]) / 2
    width = (h[2] - h[1]) * IN
    if view == "side":       # from the left (+x) looking right: picture right = aft (+y)
        y, z = U.fs(hc), vc * IN
        return dict(type="ortho", pos=[60, y, z], target=[0, y, z], ortho_scale=width)
    if view == "top":        # from above: picture right = +x (left wing), picture up = aft
        y = U.fs(vc)
        return dict(type="ortho", pos=[hc * IN, y, 60], target=[hc * IN, y, 0], ortho_scale=width)
    z = vc * IN              # from ahead looking aft: picture right = +x
    return dict(type="ortho", pos=[hc * IN, -60, z], target=[hc * IN, 0, z], ortho_scale=width)


def render_view(view, px_per_in, hide, work):
    h, v = VIEWS[view]["h"], VIEWS[view]["v"]
    size = [int(round((h[2] - h[1]) * px_per_in)), int(round((v[2] - v[1]) * px_per_in))]
    spec = dict(resolution=size, samples=1, ground_shadow=False, hide=hide, camera=camera_spec(view))
    sc = RF.setup_scene(spec, quick=False)
    cam = RF.setup_camera(sc, spec)
    cam.data.sensor_fit = "HORIZONTAL"
    part, depth, facing, inside, names = RF.render_drawing_data(sc, work)
    outline, boundary, fine = find_lines(part, depth, facing, inside, names, dict(crease_deg=40))
    lines = np.clip(halve(outline | boundary) * 1.0 + halve(fine) * 0.55, 0, 1)
    bpy.data.objects.remove(cam, do_unlink=True)
    for name in ("figure_key",):
        ob = bpy.data.objects.get(name)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
    # reference pixel: (h = 0, v = 0) of the picture window, i.e. FS 0 / BL 0 / ground line
    origin = [(-h[1]) * px_per_in, (v[2]) * px_per_in]          # row counted from the top
    return lines, halve(inside), dict(px_per_in=px_per_in, size=size, horizontal=h[0], vertical=v[0],
                                      origin_px=origin, window_in=dict(h=[h[1], h[2]], v=[v[1], v[2]]))


def save_rgba(path, coverage, rgb=(0, 0, 0)):
    height, width = coverage.shape
    rgba = np.zeros((height, width, 4), dtype=np.float32)
    rgba[..., 0], rgba[..., 1], rgba[..., 2], rgba[..., 3] = rgb[0], rgb[1], rgb[2], coverage
    image = bpy.data.images.new("threeview_out", width, height, alpha=True)
    image.pixels.foreach_set(rgba[::-1].ravel())
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--views", default="side,top,front")
    ap.add_argument("--px-per-in", type=float, default=6.0)
    ap.add_argument("--hide", default="ELECTRICAL.adf_sense_wire", help="comma-separated part or group ids to leave out")
    ap.add_argument("--silhouette", action="store_true", help="also write the filled silhouette of each view")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    hide = [name for name in args.hide.split(",") if name]
    info = {}
    with tempfile.TemporaryDirectory() as work:
        for view in args.views.split(","):
            lines, inside, meta = render_view(view, args.px_per_in, hide, work)
            save_rgba(os.path.join(args.out, f"model_{view}.png"), lines)
            if args.silhouette:
                save_rgba(os.path.join(args.out, f"model_{view}_fill.png"), inside)
            info[view] = meta
            print("view", view, meta["size"])
    with open(os.path.join(args.out, "threeview.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)


if __name__ == "__main__":
    main()
