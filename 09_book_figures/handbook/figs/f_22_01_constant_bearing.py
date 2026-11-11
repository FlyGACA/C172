"""Figure 22-1. A collision course: constant bearing, no relative motion. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-22-01-constant-bearing",
        "replaces": "fig-22-01-constant-bearing.svg",
        "book_file": "plate-22-01-constant-bearing.jpg",
        "caption": "Figure 22-1. A collision course: constant bearing, no relative motion",
        "desc": "Figure 22-1. A collision course: constant bearing, no relative motion",
        "legend": [
            "First moment.",
            "Second moment, 20 seconds later.",
            "Third moment, 20 seconds before impact. The same moments appear in the plan view (left) and through your windscreen (right).",
            "Collision point.",
            "The angle between your nose and the other aircraft stays the same: a constant bearing.",
            "In the windscreen the other aircraft stays at one spot and only grows.",
            "Traffic that moves across the windscreen is not on a collision course while it keeps moving; keep it in sight.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-22-01-constant-bearing.svg"},
    }
