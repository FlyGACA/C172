"""Figure 30-3. Choosing a surface in Saudi terrain, and the area within gliding reach. The diagram of the book's figure with the aeroplane of the model (reskin.py), laid on an aerial view of
the country (figs/terrain.py): each of the six framed squares of the old drawing is a piece of ground of its own kind (a gravel plain, soft sand, dunes with their crescents, a salt flat
cracked into plates, irrigated circles one of which lies fallow, a village), the wadi is a dry bed with its boulders and bushes between darker banks, and the road runs under its power
line with the two cars of the old drawing on it. The frames keep the colours that rate them (green, amber, red), the numbered callouts, the circle of gliding reach and the wind are the
old drawing's."""
import os
import re

from figs import h_plan, terrain

OLD = open(os.path.join(h_plan.HERE, "old", "fig-30-03-choosing-a-surface.svg"), encoding="utf-8").read()

# the six framed squares of the old drawing: (the old tag, x, y, w, h)
TILES = {
    "gravel": ('<rect x="220" y="160" width="210" height="110" rx="10" fill="#eceae6" stroke="#047857" stroke-width="3"/>', 220, 160, 210, 110),
    "sand": ('<rect x="450" y="170" width="170" height="100" rx="10" fill="#f7e6cc" stroke="#b45309" stroke-width="3"/>', 450, 170, 170, 100),
    "dunes": ('<rect x="20" y="20" width="190" height="120" rx="10" fill="#f7e6cc" stroke="#b91c1c" stroke-width="3"/>', 20, 20, 190, 120),
    "sabkha": ('<rect x="20" y="160" width="180" height="110" rx="10" fill="#f6f6f4" stroke="#b91c1c" stroke-width="3"/>', 20, 160, 180, 110),
    "farm": ('<rect x="440" y="20" width="180" height="130" rx="10" fill="#fbf7f0" stroke="#b45309" stroke-width="3"/>', 440, 20, 180, 130),
    "village": ('<rect x="230" y="20" width="190" height="120" rx="10" fill="#fbf7f0" stroke="#b91c1c" stroke-width="3"/>', 230, 20, 190, 120),
}


def rect_shape(key):
    _, x, y, w, h = TILES[key]
    return ("rect", x, y, w, h, 10)


def local(shape, x, y, r=None):
    """A place on the canvas as a fraction of the piece cut for the shape."""
    x0, y0, x1, y1 = terrain.box_of(shape)
    return ((x - x0) / (x1 - x0), (y - y0) / (y1 - y0)) if r is None else ((x - x0) / (x1 - x0), (y - y0) / (y1 - y0), r / (x1 - x0))


FARM = rect_shape("farm")
GROUND = {
    "gravel": terrain.piece("terrain-30-03-gravel", rect_shape("gravel"), seed=31, kind="gravel", features=("stones",), soft=1.0, feather=0.5),
    "sand": terrain.piece("terrain-30-03-sand", rect_shape("sand"), seed=32, kind="sand", soft=1.0, feather=0.5),
    "dunes": terrain.piece("terrain-30-03-dunes", rect_shape("dunes"), seed=33, kind="dunes", features=(), veil=0.08, soft=1.6, feather=0.5),
    "sabkha": terrain.piece("terrain-30-03-sabkha", rect_shape("sabkha"), seed=34, kind="sabkha", soft=0.8, feather=0.5),
    "farm": terrain.piece("terrain-30-03-farm", FARM, seed=35, kind="farm", features=("tracks",), veil=0.2, soft=1.8, feather=0.5,
                          fields=[local(FARM, 492, 64, 36), local(FARM, 530, 120, 24), local(FARM, 574, 64, 36) + ("fallow",)]),
    "village": terrain.piece("terrain-30-03-village", rect_shape("village"), seed=36, kind="plain", features=("tracks",), veil=0.26, soft=1.8, feather=0.5),
}

# the wadi: the old drawing's wavy path, 34 wide with its banks and a pale bed 24 wide
WADI_PATH = [(-30, 358), (0, 352), (30, 338), (60, 330), (90, 332), (120, 346), (150, 362), (190, 366), (250, 352), (300, 338), (350, 332), (395, 350), (440, 376), (490, 372), (520, 360), (570, 350), (610, 346), (640, 340), (670, 334)]
WADI = terrain.piece("terrain-30-03-wadi", ("stroke", WADI_PATH, 36), seed=37, kind="plain", features=(), veil=0.1, soft=1.4, feather=0.9, darken=0.8,
                     strokes=[((236, 222, 190, 255), 24, WADI_PATH)])

BOULDERS = [(float(x), float(y), float(r)) for x, y, r in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="#6b7280"/>', OLD) if float(r) < 8]
BUSHES = [(float(x), float(y), float(r)) for x, y, r in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="#047857" opacity="0.8"/>', OLD)]


def stones_and_bushes():
    out = ['<defs><radialGradient id="hpBoulder" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#D4CFC2"/><stop offset="0.6" stop-color="#9B9684"/><stop offset="1" stop-color="#6F6A5B"/></radialGradient>'
           '<radialGradient id="hpBush" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#8DB668"/><stop offset="0.65" stop-color="#4F7C3B"/><stop offset="1" stop-color="#34592B"/></radialGradient></defs>']
    for x, y, r in BOULDERS:
        out.append(f'<ellipse cx="{x + 1.3:g}" cy="{y + 1.8:g}" rx="{r * 1.05:g}" ry="{r * 0.85:g}" fill="#2B2418" fill-opacity="0.3"/><circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="url(#hpBoulder)"/>')
    for x, y, r in BUSHES:
        out.append(f'<ellipse cx="{x + 2:g}" cy="{y + 2.6:g}" rx="{r * 1.1:g}" ry="{r * 0.9:g}" fill="#2B2418" fill-opacity="0.3"/><circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="url(#hpBush)"/>'
                   f'<circle cx="{x - r * 0.25:g}" cy="{y - r * 0.3:g}" r="{r * 0.38:g}" fill="#A9CC83" fill-opacity="0.55"/>')
    return "".join(out)


BARCHAN = ('<defs><linearGradient id="hpBarchan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8E7BF"/><stop offset="0.55" stop-color="#E3BF84"/><stop offset="1" stop-color="#B98A4C"/></linearGradient></defs>')
ROAD = '<line x1="230" y1="300" x2="640" y2="230" stroke="#6b7280" stroke-width="9"/>'

OLD_FARM_FROM = '<circle cx="492" cy="64" r="36"'                      # the old circles, spokes and wheels of the farm square: from here up to the road (the ground picture has its own)
OLD_FARM_TO = '<line x1="230" y1="300" x2="640" y2="230" stroke="#B3A688"'


def plate():
    replace = [[tag, re.sub(r'fill="#[0-9a-fA-F]{6}"', 'fill="none"', tag, count=1)] for tag, *_ in TILES.values()]
    replace += [['<rect x="28" y="398" width="120" height="34" fill="#fbf7f0"/>', '<rect x="28" y="398" width="120" height="34" rx="9" fill="#FFFFFF" fill-opacity="0.82"/>'],
                [ROAD, '<line x1="230" y1="300" x2="640" y2="230" stroke="#B3A688" stroke-opacity="0.6" stroke-width="13"/>' + ROAD.replace("#6b7280", "#555C69")]]
    replace += [['fill="#e9c48f" stroke="#b45309" stroke-width="1.4"/>', 'fill="url(#hpBarchan)" stroke="#8A5A28" stroke-width="0.5"/>']]
    return {
        "id": "fig-30-03-choosing-a-surface",
        "replaces": "fig-30-03-choosing-a-surface.svg",
        "book_file": "plate-30-03-choosing-a-surface.jpg",
        "caption": "Figure 30-3. Choosing a surface in Saudi terrain, and the area within gliding reach",
        "desc": "Figure 30-3. Choosing a surface in Saudi terrain, and the area within gliding reach",
        "legend": [
            "Gravel plain, landing into wind.",
            "Soft sand.",
            "Dunes.",
            "Sabkha.",
            "Wadi.",
            "Farm circles, one fallow.",
            "Road with a power line.",
            "Village.",
            "The aeroplane and its gliding reach, shifted downwind.",
            "The wind.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": h_plan.layer({
            "svg": "fig-30-03-choosing-a-surface.svg",
            "remove": [r'<rect x="0" y="0" width="640" height="440" fill="#fbf7f0"/>',                                       # the page's cream ground: the country shows
                       r'<circle cx="[\d.]+" cy="[\d.]+" r="[12](?:\.\d)?" fill="#9ca3af"/>',                                # the dots of the gravel square
                       r'<path d="M 462 \d+ Q[^"]*" fill="none" stroke="#d6b98d" stroke-width="1.6"/>',                      # the ripples of the sand square
                       r'<line x1="[\d.]+" y1="[\d.]+" x2="[\d.]+" y2="[\d.]+" stroke="#c7c9cc" stroke-width="1.4"/>',       # the cracks of the salt flat
                       r'<ellipse cx="(?:60|150)" cy="(?:210|214)" rx="\d+" ry="\d+" fill="#9ca3af" opacity="0.45"/>',
                       r'<path d="M 0 352 C 90 320 150 380 250 352 C 350 324 420 392 520 360 C 570 344 610 352 640 340" fill="none" stroke="#(?:cbb894|e3d5b8|b91c1c)"[^>]*/>',   # the wadi
                       r'<circle cx="[\d.]+" cy="[\d.]+" r="[\d.]+" fill="#6b7280"/>', r'<circle cx="[\d.]+" cy="[\d.]+" r="7" fill="#047857" opacity="0.8"/>'],
            "replace": replace,
            "drop": [[OLD_FARM_FROM, OLD_FARM_TO, {"markup": ""}]],
        }, "terrain-30-03", seed=303, kind="plain", veil=0.30, markup=BARCHAN + stones_and_bushes(),
            extra_sprites=[GROUND["village"], GROUND["dunes"], GROUND["farm"], GROUND["sabkha"], GROUND["gravel"], GROUND["sand"], WADI]),
    }
