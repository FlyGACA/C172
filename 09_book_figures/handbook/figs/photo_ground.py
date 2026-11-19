"""The ground of style C for the illustrated scenes: a window of a render of the open picture of the desert east of Thumamah on its relief (figs/oeth3d.py,
backdrop-side-desert seen from the side and backdrop-plan-desert from above; "Contains modified Copernicus Sentinel data 2026"), toned for the scene
and laid as an <image> in the drawing's own markup, so that it can sit inside a clipped tile under the drawn things. Pillow only.

    side(x0, x1, horizon, bottom, tone="day", offset=0.0)        the ground from the horizon down, a window `offset` (0 to 1) along the render
    plan(x, y, w, h, tone="day", zoom=1.0, cx=0.5, cy=0.5, flip=False)    the ground from above over a rectangle, centred on (cx, cy) of the render

`tone` is day, storm (darkened under a storm), dusk or night. Every figure that uses it says in its note that the ground is an open satellite picture."""
import base64
import io
import os

from PIL import Image

RENDERS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
K = 4.0                                                     # pixels to a canvas unit
TONES = {"day": ("#E9D6AE", 0.22, 1.0), "storm": ("#5E6A86", 0.38, 0.82), "dusk": ("#E7B58E", 0.26, 0.95), "night": ("#1C2436", 0.78, 0.9)}
_CACHE = {}


def _source(name):
    if name not in _CACHE:
        im = Image.open(os.path.join(RENDERS, name + ".png")).convert("RGBA")
        box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        _CACHE[name] = im.crop(box).convert("RGB")
    return _CACHE[name]


def _tone(im, tone):
    colour, amount, light = TONES[tone]
    rgb = tuple(int(colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if light != 1.0:
        im = im.point(lambda v: round(v * light))
    return Image.blend(im, Image.new("RGB", im.size, rgb), amount)


def _markup(im, x, y, w, h):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")
    return (f'<image x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" preserveAspectRatio="none" '
            f'href="data:image/jpeg;base64,{b64}" xlink:href="data:image/jpeg;base64,{b64}"/>')


def side(x0, x1, horizon, bottom, tone="day", offset=0.0):
    src = _source("backdrop-side-desert")
    w, h = x1 - x0, bottom - horizon + 2.0
    sw = src.width * 0.72
    sh = sw * h / w
    if sh > src.height:
        sh, sw = src.height, src.height * w / h
    ox = (src.width - sw) * max(0.0, min(1.0, offset))
    im = src.crop((round(ox), 0, round(ox + sw), round(sh))).resize((max(2, round(w * K)), max(2, round(h * K))), Image.LANCZOS)
    return _markup(_tone(im, tone), x0, horizon - 1.0, w, h + 1.0)


def plan(x, y, w, h, tone="day", zoom=1.0, cx=0.5, cy=0.5, flip=False):
    src = _source("backdrop-plan-desert")
    sw = min(src.width, src.height * w / h) / zoom
    sh = sw * h / w
    ox = max(0.0, min(src.width - sw, cx * src.width - sw / 2))
    oy = max(0.0, min(src.height - sh, cy * src.height - sh / 2))
    im = src.crop((round(ox), round(oy), round(ox + sw), round(oy + sh))).resize((max(2, round(w * K)), max(2, round(h * K))), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return _markup(_tone(im, tone), x, y, w, h)
