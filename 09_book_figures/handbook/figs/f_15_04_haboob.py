"""Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow. The diagram of the book's figure (the rain, the cold outflow, the arrows, the aerodrome, the numbered callouts)
on a dusty sky with the clouds of the model of the sky (reskin.py, figs/clouds.py): the base of a thunderstorm above, and the wall of dust, a billowing cloud painted the
colour of the sand."""

SKY = ('<defs><linearGradient id="f1504-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9C4E4"/><stop offset="0.7" stop-color="#E4E4DC"/><stop offset="1" stop-color="#EFE2C8"/></linearGradient></defs>'
       '<rect x="0" y="0" width="640" height="314" fill="url(#f1504-sky)"/>')
BACKGROUND = '<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>'
GROUND = '<rect x="0" y="314" width="640" height="46" fill="#f3f4f6"/>'
FIRST_RAIN = '<line x1="462" y1="128" x2="456" y2="262" stroke="#1d4ed8" stroke-width="1.2" stroke-dasharray="6 5"/>'
REMOVE = [
    r'<(?:circle|rect)[^>]*fill="#(?:9ca3af|b45309)" stroke="#(?:9ca3af|b45309)" stroke-width="(?:3|2\.5)"/>',                 # the outlined thunderstorm and the outlined wall of dust
    r'<circle [^>]*fill="#(?:ffffff|f3dcbc)"/>',                                                                                 # their fills
    r'<rect x="(?:396|146)" y="[\d.]+" width="[\d.]+" height="[\d.]+" fill="#(?:ffffff|f3dcbc)"/>',
]


def plate():
    return {
        "id": "fig-15-04-haboob",
        "replaces": "fig-15-04-haboob.svg",
        "book_file": "plate-15-04-haboob.jpg",
        "caption": "Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow",
        "desc": "Figure 15-4. A haboob: dust lifted by a thunderstorm's outflow",
        "legend": [
            "Thunderstorm.",
            "Cold downdraft with heavy rain.",
            "Cold, dense outflow spreading along the surface.",
            "Gust front: sudden wind shift and strong gusts.",
            "Wall of dust.",
            "Direction of movement.",
            "An aerodrome in its path.",
            "Warmer air forced up at the gust front, carrying dust aloft.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {
            "svg": "fig-15-04-haboob.svg",
            "remove": REMOVE,
            "replace": [[BACKGROUND, BACKGROUND + SKY], [GROUND, GROUND.replace("#f3f4f6", "#E7DCC3")]],
            "drop": [[FIRST_RAIN, FIRST_RAIN, {"sprites": [
                {"name": "cloud-stormbase", "at": [486, 70], "width": 250},
                {"name": "cloud-congestus", "at": [240, 204], "width": 176, "tint": "#C9A06B", "tint_strength": 0.75},
            ]}]],
        },
    }
