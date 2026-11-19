"""Figure 24-7. A personal minimums card: the legal floor and your own minimum for each item. Drawn again as the thing itself (the old figure was a flat table): a
laminated card held on a kneeboard by its clip, the paper slightly warm with a soft sheen across the laminate, its header with the lines for the name and the date of the last review,
nine rows each with a small coloured sign (an eye, a cloud base, a windsock, a runway, a fuel gauge, a setting sun, a calendar, a person), the legal floor printed grey and the blank
boxes for your own minimum outlined in blue, and the six IMSAFE boxes; beside it, the scale of the old figure: the floor, your minimum above it, and the margin between that may narrow
but never below the floor. The layout, the floor values and the twelve callouts of the old figure are kept."""
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 420
INK, GREY, BLUE, AMBER, RED = "#1F2937", "#94A3B8", "#1D4ED8", "#B45309", "#B91C1C"
ROWS = [(124.5, "5"), (161.5, "1 000"), (198.5, "–"), (235.5, "–"), (272.5, "30"), (309.5, "0"), (346.5, "–")]


def defs():
    g = S.gradient
    return (f'<defs>{g("mc24b", [(0, "#5B4632"), (1, "#3E2F21")])}{g("mc24p", [(0, "#FFFDF7"), (1, "#F6F0E2")])}'
            f'{g("mc24s", [(0, "#FFFFFF", 0.0), (0.42, "#FFFFFF", 0.0), (0.5, "#FFFFFF", 0.35), (0.58, "#FFFFFF", 0.0), (1, "#FFFFFF", 0.0)], 0, 0, 1, 1)}'
            f'{g("mc24c", [(0, "#E5E7EB"), (0.5, "#9CA3AF"), (1, "#6B7280")])}'
            '<filter id="mc24d" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="3" stdDeviation="3.5" flood-color="#10233F" flood-opacity="0.35"/></filter></defs>')


def board():
    """The kneeboard (dark leather), the card on it with its shadow, the laminate's sheen, the clip."""
    return ('<rect x="8" y="6" width="466" height="410" rx="16" fill="url(#mc24b)" filter="url(#mc24d)"/>'
            '<rect x="14" y="12" width="454" height="398" rx="12" fill="none" stroke="#7A6248" stroke-width="1.2" stroke-dasharray="3 3"/>'
            '<rect x="20" y="14" width="440" height="392" rx="12" fill="url(#mc24p)" filter="url(#mc24d)"/>'
            '<path d="M 20 64 L 20 26 Q 20 14 32 14 L 448 14 Q 460 14 460 26 L 460 64 Z" fill="#E3EBFA"/>'
            '<line x1="20" y1="64" x2="460" y2="64" stroke="#1F2937" stroke-width="1.2"/>'
            '<rect x="20" y="14" width="440" height="392" rx="12" fill="url(#mc24s)"/>'
            '<rect x="20.5" y="14.5" width="439" height="391" rx="11.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.4"/>'
            '<rect x="190" y="2" width="100" height="22" rx="6" fill="url(#mc24c)" stroke="#4B5563" stroke-width="1"/>'
            '<rect x="200" y="8" width="80" height="6" rx="3" fill="#F3F4F6" opacity="0.7"/>')


def signs():
    out = []
    # 2 an eye
    out.append('<path d="M 96 124.5 Q 110 112.5 124 124.5 Q 110 136.5 96 124.5 Z" fill="#FFFFFF" stroke="#1F2937" stroke-width="2"/><circle cx="110" cy="124.5" r="4.5" fill="#2563EB"/><circle cx="110" cy="124.5" r="2" fill="#0B1224"/>')
    # 3 a cloud and its base
    out.append('<g fill="#E2E8F0" stroke="#475569" stroke-width="1.4"><circle cx="104" cy="163.5" r="7"/><circle cx="113" cy="158.5" r="8"/><circle cx="120" cy="164.5" r="6"/></g>'
               '<rect x="104" y="163" width="16" height="7.5" fill="#E2E8F0"/><line x1="95" y1="174.5" x2="125" y2="174.5" stroke="#1F2937" stroke-width="1.6" stroke-dasharray="3 3"/>')
    # 4 a windsock
    out.append('<line x1="98" y1="186.5" x2="98" y2="212.5" stroke="#1F2937" stroke-width="2"/>'
               '<polygon points="98,186.5 112,188.5 112,198.5 98,200.5" fill="#F97316"/><polygon points="112,188.5 124,190.5 124,196.5 112,198.5" fill="#FFFFFF" stroke="#F97316" stroke-width="1"/>')
    # 5 a runway in perspective
    out.append('<polygon points="103,222.5 117,222.5 122,248.5 98,248.5" fill="#4B5563"/><line x1="110" y1="225.5" x2="110" y2="245.5" stroke="#FFFFFF" stroke-width="1.4" stroke-dasharray="3 3"/>')
    # 6 a fuel gauge
    out.append('<path d="M 98 278.5 A 12 12 0 0 1 122 278.5" fill="#FFFFFF" stroke="#1F2937" stroke-width="2"/><path d="M 98 278.5 A 12 12 0 0 1 101.5 270" fill="none" stroke="#DC2626" stroke-width="3"/>'
               '<line x1="110" y1="278.5" x2="103" y2="269.5" stroke="#1F2937" stroke-width="2.2"/><circle cx="110" cy="278.5" r="2.5" fill="#1F2937"/>')
    # 7 a setting sun
    out.append('<line x1="95" y1="315.5" x2="125" y2="315.5" stroke="#1F2937" stroke-width="2"/><path d="M 102 315.5 A 8 8 0 0 1 118 315.5" fill="#FDBA74" stroke="#EA580C" stroke-width="2"/>'
               + "".join(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#EA580C" stroke-width="1.6"/>' for x1, y1, x2, y2 in
                         ((99.7, 311.7, 95.9, 310.4), (104.5, 306, 102.5, 302.5), (110, 304.5, 110, 300.5), (115.5, 306, 117.5, 302.5), (120.3, 311.7, 124.1, 310.4))))
    # 8 a calendar
    out.append('<rect x="98" y="336.5" width="24" height="22" rx="2" fill="#FFFFFF" stroke="#1F2937" stroke-width="1.8"/><rect x="98" y="336.5" width="24" height="6" fill="#DC2626"/>'
               + "".join(f'<rect x="{x}" y="{y}" width="4" height="3" fill="#94A3B8"/>' for x in (102, 108, 114) for y in (345.5, 351.5)))
    # 9 a person
    out.append('<circle cx="110" cy="377.5" r="6" fill="#334155"/><path d="M 99 396.5 Q 99 384.5 110 384.5 Q 121 384.5 121 396.5 Z" fill="#334155"/>')
    return "".join(out)


def table():
    out = ['<line x1="70" y1="48" x2="250" y2="48" stroke="#94A3B8" stroke-width="1.4"/><line x1="290" y1="48" x2="420" y2="48" stroke="#94A3B8" stroke-width="1.4"/>']
    for y, v in ROWS:
        out.append(f'<rect x="250" y="{n(y - 13)}" width="80" height="26" rx="4" fill="#EEF1F5" stroke="#B6C0CC" stroke-width="1.2"/>'
                   f'<rect x="355" y="{n(y - 13)}" width="80" height="26" rx="4" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2"/>'
                   f'<line x1="34" y1="{n(y + 18.5)}" x2="446" y2="{n(y + 18.5)}" stroke="#E7E2D6" stroke-width="1.2"/>')
        out.append(M.chip(290, y, v, "#64748B", size=8.6))
    for x in (202, 244, 286, 328, 370, 412):
        out.append(f'<rect x="{x}" y="375.5" width="14" height="14" rx="2" fill="#FFFFFF" stroke="#1F2937" stroke-width="1.6"/>')
    for x, c in zip((192, 234, 276, 318, 360, 402), "IMSAFE"):
        out.append(M.chip(x, 382.5, c, INK, size=8.0))
    return "".join(out)


def scale():
    return ('<rect x="510" y="190" width="80" height="140" fill="#E8EEFC" opacity="0.9"/><rect x="510" y="330" width="80" height="16" fill="#CBD5E1"/>'
            f'<line x1="510" y1="190" x2="590" y2="190" stroke="{BLUE}" stroke-width="4"/><line x1="510" y1="330" x2="590" y2="330" stroke="{INK}" stroke-width="4"/>'
            + M.arrow(550, 198, 550, 300, BLUE, width=2.4, dash="6 4", halo=False))


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', defs(), board(), signs(), table(), scale()]
    c = S.callout
    out.append(c(1, 46, 39) + c(10, 290, 84) + c(11, 395, 84) + "".join(c(k, 46, y) for k, (y, _) in zip(range(2, 9), ROWS)) + c(9, 46, 383.5)
               + c(12, 550, 140, 550, 186) + c(10, 612, 330) + c(11, 612, 190))
    return out


def plate():
    return {
        "id": "fig-24-07-minimums-card",
        "replaces": "fig-24-07-minimums-card.svg",
        "book_file": "plate-24-07-minimums-card.jpg",
        "caption": "Figure 24-7. A personal minimums card: the legal floor and your own minimum for each item",
        "desc": "Figure 24-7. A personal minimums card: the legal floor and your own minimum for each item",
        "legend": [
            "Your name, and the date you last reviewed the card.",
            "Flight visibility, km.",
            "Ceiling, ft.",
            "Surface wind, gusts and crosswind, kt.",
            "Runway: the AFM distance for the day, and the margin you add.",
            "Fuel on landing, minutes.",
            "Daylight: minutes before sunset by which you land.",
            "Recent practice: days since your last flight.",
            "Fitness: the six IMSAFE questions, each answered \"fit\".",
            "The legal floor (grey); a dash means the GACAR gives no figure.",
            "Your own minimum, to fill in.",
            "Your margin: it may narrow with training and experience, never below the floor.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-24-07-minimums-card.svg", "blank": True, "layers": layers()},
    }
