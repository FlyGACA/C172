"""Figure 27-2. Two 90° clearing turns before a manoeuvre, seen from above. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-27-02-clearing-turns",
        "replaces": "fig-27-02-clearing-turns.svg",
        "book_file": "plate-27-02-clearing-turns.jpg",
        "caption": "Figure 27-2. Two 90° clearing turns before a manoeuvre, seen from above",
        "desc": "Figure 27-2. Two 90° clearing turns before a manoeuvre, seen from above",
        "legend": [
            "Before the first turn, look left, ahead and behind, above and below.",
            "First clearing turn, 90° left.",
            "Look right, into the next turn.",
            "Second clearing turn, 90° right, back to the original heading.",
            "The manoeuvre area, now seen from two directions.",
            "A field for a forced landing.",
            "A mast and its wires: an obstacle.",
            "Checks done and the area clear: start, and keep scanning.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-27-02-clearing-turns.svg"},
    }
