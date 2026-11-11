"""Figure 31-5. A night circuit for runway 27: the lights you use and the traps. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-31-05-night-circuit",
        "replaces": "fig-31-05-night-circuit.svg",
        "book_file": "plate-31-05-night-circuit.jpg",
        "caption": "Figure 31-5. A night circuit for runway 27: the lights you use and the traps",
        "desc": "Figure 31-5. A night circuit for runway 27: the lights you use and the traps",
        "legend": [
            "Aerodrome beacon.",
            "Runway edge lights white, threshold green, end red.",
            "Approach lights.",
            "PAPI, left of the runway seen from final.",
            "Taxiway edge lights, blue.",
            "A highway: a straight line of lights like a runway.",
            "Town lights.",
            "Joining at 45° to downwind, at circuit height.",
            "Downwind: runway lights parallel on your left; checks.",
            "Abeam the threshold: power back, descent, altimeter.",
            "Base, threshold about 45° behind: altimeter and vertical speed.",
            "Final over dark ground: expect the black hole.",
            "Traffic on final, landing light toward the runway.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-31-05-night-circuit.svg", "sprite_top": "sprite-top-night", "outline": False},
    }
