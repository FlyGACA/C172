"""A panel of a plate that shows a 3D view of Thumamah (a render of blender/render_oeth.py from a recipe of figs/oeth3d.py) above the plate's own drawing:
the render laid in a rounded frame, cropped round the height of the render that holds the subject, with a north arrow projected from the scene and
numbered callouts on the render's anchors. `below` moves the plate's own drawing down under the panel."""
import json
import os

from figs import h_b4 as B4
from figs import scene as S

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def anchors(rid):
    with open(os.path.join(HERE, "renders", rid + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    return d["size"], d["anchors"]


def placer(rid, box, v_mid):
    """The canvas point of an anchor, and the image layer: the render `box[2]` units wide, the height v_mid of it (0 top, 1 bottom) at the middle of the box."""
    px, py, pw, ph = box
    (w, h), a = anchors(rid)
    ih = pw * h / w
    y0 = py + ph / 2 - v_mid * ih
    return (lambda k: (round(px + a[k][0] * pw, 1), round(y0 + a[k][1] * ih, 1))), {"name": rid, "at": [px + pw / 2, y0 + ih / 2], "width": pw}


def panel(rid, box, v_mid, uid, callouts, marks=None, r=9.5):
    """The layers of the panel. callouts: (number, anchor, disc x, disc y); marks(at): more SVG drawn on the render, inside its frame."""
    px, py, pw, ph = box
    at, img = placer(rid, box, v_mid)
    clip = f'<defs><clipPath id="{uid}c3"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10"/></clipPath></defs><g clip-path="url(#{uid}c3)">'
    (x0, y0), (x1, y1) = at("n0"), at("n1")
    north = B4.north_arrow(px + pw - 34, py + 34, (x1 - x0, y1 - y0))
    inner = (marks(at) if marks else "") + north
    frame = f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'
    discs = "".join(S.callout(k, dx, dy, *at(a), r=r) for k, a, dx, dy in callouts)
    return [clip, img, inner + "</g>" + frame + discs]


def below(layers, dy):
    """The plate's own drawing moved down by dy (under the panel): all its layers in one translated group. Pictures (sprite layers) are drawn in place
    in the SVG, so they move with the group; the group is one piece because a drawing may open a group in one layer and close it in another."""
    return [f'<g transform="translate(0 {dy})">', *layers, "</g>"]
