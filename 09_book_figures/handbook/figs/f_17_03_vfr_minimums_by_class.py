"""Figure 17-3. VFR visibility and distance from cloud in Classes B to E. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-17-03-vfr-minimums-by-class",
        "replaces": "fig-17-03-vfr-minimums-by-class.svg",
        "book_file": "plate-17-03-vfr-minimums-by-class.jpg",
        "caption": "Figure 17-3. VFR visibility and distance from cloud in Classes B to E",
        "desc": "Figure 17-3. VFR visibility and distance from cloud in Classes B to E",
        "legend": [
            "Class B: clear of clouds.",
            "500 ft below cloud.",
            "1 000 ft above.",
            "2 000 ft horizontally.",
            "Classes C and D, and Class E below 10 000 ft MSL.",
            "1 000 ft below.",
            "1 000 ft above.",
            "1 500 m horizontally (amber: metres).",
            "Class E at or above 10 000 ft MSL.",
        ],
        "canvas": [640, 392],
        "background": "pale",
        "reskin": {"svg": "fig-17-03-vfr-minimums-by-class.svg"},
    }
