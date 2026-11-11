"""Figure 29-3. The checkpoint routine: clock, compass, chart, ground, then the log. The diagram of the book's figure with the aeroplane of the model (reskin.py)."""


def plate():
    return {
        "id": "fig-29-03-checkpoint-routine",
        "replaces": "fig-29-03-checkpoint-routine.svg",
        "book_file": "plate-29-03-checkpoint-routine.jpg",
        "caption": "Figure 29-3. The checkpoint routine: clock, compass, chart, ground, then the log",
        "desc": "Figure 29-3. The checkpoint routine: clock, compass, chart, ground, then the log",
        "legend": [
            "Clock.",
            "Compass.",
            "Chart, read towards the ground.",
            "Ground: the feature, confirmed.",
            "The log: planned minutes, planned time and, in blue, actual or revised time.",
            "Two minutes before the estimate: start.",
            "Over the checkpoint: note the time.",
            "A minute later: correct and revise.",
            "Between checkpoints: look out.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-29-03-checkpoint-routine.svg"},
    }
