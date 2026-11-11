"""Figure 15-2. Flying an approach through a microburst. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


from reskin import LOOK        # noqa: E402


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
            # the aeroplane on the approach, a cartoon in the old figure, is the model seen from the right, at the same place and the same descent angle
            "drop": [['<g transform="translate(60 155.6) rotate(17) scale(1.0)"', '<line x1="199.7" y1="170.4"', {"sprites": [{"name": "sprite-side", "at": [61, 155], "width": 96, "angle": 17, **LOOK}]}]],
        },
    }
