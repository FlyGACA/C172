"""Figure 15-2. Flying an approach through a microburst. The diagram of the book's figure with the aeroplane of the model (reskin.py), the dark base of a thunderstorm in place
of the drawn cloud, billows of dust in place of the tan ovals on the ground, and a plain of sand under it (figs/clouds.py, figs/scene.py)."""
from figs import scene as S


from reskin import LOOK        # noqa: E402


GROUND = ('<defs>' + S.gradient("f1502sand", [(0, "#E7D5AA"), (1, "#C9AD7A")]) + '</defs><rect x="0" y="316" width="640" height="44" fill="url(#f1502sand)"/>'
          + S.scrub(5, 0, 640, 320, 358, 26, colour=("#8A8A55", "#5E603E"), scale=0.7))
TAN = {"tint": "#C9A06B", "tint_strength": 0.8}
DUST = [{"name": "cloud-cumulus-b", "at": [198, 302], "width": 98, "height": 30, **TAN}, {"name": "cloud-cumulus-b", "at": [152, 309], "width": 54, "height": 16, **TAN},
        {"name": "cloud-cumulus-b", "at": [446, 302], "width": 98, "height": 30, **TAN}, {"name": "cloud-cumulus-b", "at": [492, 309], "width": 54, "height": 16, **TAN}]


def plate():
    return {
        "id": "fig-15-02-microburst",
        "replaces": "fig-15-02-microburst.svg",
        "book_file": "plate-15-02-microburst.jpg",
        "caption": "Figure 15-2. Flying an approach through a microburst",
        "desc": "Figure 15-2. Flying an approach through a microburst",
        "legend": [
            "Increasing headwind: airspeed and lift rise, and the aeroplane floats above the glide path.",
            "Downdraft: the aeroplane is pushed down.",
            "Increasing tailwind: airspeed falls and the aeroplane sinks fast.",
            "Ground contact short of the runway.",
            "Intended glide path.",
            "Outflow raising a ring of dust.",
            "Runway.",
            "Virga and the rain shaft.",
        ],
        "canvas": [640, 396],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-02-microburst.svg",
            "replace": [['<rect x="0" y="316" width="640" height="44" fill="url(#f1502-gr)"/>', GROUND]],
            # the aeroplane on the approach, a cartoon in the old figure, is the model seen from the right, at the same place and the same descent angle
            "drop": [['<g transform="translate(60 155.6) rotate(17) scale(1.0)"', '<line x1="199.7" y1="170.4"', {"sprites": [{"name": "sprite-side", "at": [61, 155], "width": 96, "angle": 17, **LOOK}]}],
                     ['<circle cx="196" cy="36" r="34" fill="#94a3b8" stroke="#94a3b8" stroke-width="3"/>', '<line x1="214" y1="92" x2="211" y2="132"', {"sprites": [{"name": "cloud-stormbase", "at": [322, 44], "width": 304}]}],
                     ['<ellipse cx="196" cy="309" rx="30" ry="9"', '<line x1="130" y1="236" x2="70" y2="236"', {"sprites": DUST}]],
        },
    }
