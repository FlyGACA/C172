"""Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-18-04-taxiway-signs",
        "replaces": "fig-18-04-taxiway-signs.svg",
        "book_file": "plate-18-04-taxiway-signs.jpg",
        "caption": "Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign",
        "desc": "Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign",
        "legend": [
            "Runway-holding position marking: solid lines on your side, dashed lines on the runway side.",
            "Runway-holding position sign `09-27`, with the location sign `B` outboard of it.",
            "Taxiway centreline, curving on to the runway centreline.",
            "Intermediate holding position before taxiway `A`.",
            "Direction signs either side of the location sign `B`: taxiway `A` goes both left and right.",
            "Mandatory instruction sign.",
            "Location sign.",
            "Direction sign.",
            "Destination sign: this way to runway 09.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-18-04-taxiway-signs.svg"},
    }
