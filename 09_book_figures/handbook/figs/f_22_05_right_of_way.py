"""Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-22-05-right-of-way",
        "replaces": "fig-22-05-right-of-way.svg",
        "book_file": "plate-22-05-right-of-way.jpg",
        "caption": "Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing",
        "desc": "Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing",
        "legend": [
            "Converging, same category, about the same altitude: the aircraft on the other's right has the right of way [[§91.61(d)]].",
            "The other gives way, here by turning right to pass behind, not over, under or ahead.",
            "Head-on or nearly so: both alter course to the right [[§91.61(e)]].",
            "Overtaking: the aircraft being overtaken has the right of way.",
            "The overtaking aircraft alters course to the right and passes well clear [[§91.61(f)]].",
            "Landing, side view: of two aircraft approaching to land, the lower has the right of way, though it may not cut in front of one on final approach or overtake it [[§91.61(g)]].",
            "The higher aircraft gives way: it extends or goes around.",
            "An aircraft on final approach has the right of way over aircraft on the surface, such as one waiting to enter the runway.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {"svg": "fig-22-05-right-of-way.svg"},
    }
