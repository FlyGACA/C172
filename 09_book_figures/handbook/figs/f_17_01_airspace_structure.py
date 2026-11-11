"""Figure 17-1. Airspace blocks in a flight information region, seen from the side. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-17-01-airspace-structure",
        "replaces": "fig-17-01-airspace-structure.svg",
        "book_file": "plate-17-01-airspace-structure.jpg",
        "caption": "Figure 17-1. Airspace blocks in a flight information region, seen from the side",
        "desc": "Figure 17-1. Airspace blocks in a flight information region, seen from the side",
        "legend": [
            "The FIR: flight information and alerting service throughout.",
            "FL 150: at and above it, every flight is IFR [[§91.77]].",
            "A control zone, from the surface, around the controlled aerodrome (9).",
            "A terminal control area, its floors stepping up away from the aerodrome.",
            "An airway, with an IFR aircraft in it; its floor is above the ground.",
            "Uncontrolled airspace (grey).",
            "A VFR aeroplane under the airway's floor, outside every controlled block.",
            "An aerodrome without a control zone.",
            "A controlled aerodrome with a tower.",
            "A control area over the higher levels; its floor is the dashed line.",
        ],
        "canvas": [640, 372],
        "background": "pale",
        "reskin": {"svg": "fig-17-01-airspace-structure.svg"},
    }
