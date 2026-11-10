"""Ink lines for the book illustrations, found in exact per-pixel data (numpy only).

render_figure.py renders, at twice the size of the picture and without any filtering, which part
covers each pixel, how far away it is and which way the surface faces. This module turns that into
three kinds of line and then into smooth ink coverage at the final size:

    outline   round the whole aircraft (heavy)
    boundary  where two parts meet: door, control surfaces, cowl, windows (medium)
    fine      folds in a surface, and edges where a part hides part of itself (light)

Nothing here needs Blender, so the rules are tested in tests/test_ink.py.
"""
import math

import numpy as np


def grow(mask, radius):
    """Dilate a boolean image by about `radius` pixels (alternating cross and square steps: an octagon)."""
    out = mask.copy()
    for step in range(int(round(radius))):
        grown = out.copy()
        grown[1:, :] |= out[:-1, :]; grown[:-1, :] |= out[1:, :]
        grown[:, 1:] |= out[:, :-1]; grown[:, :-1] |= out[:, 1:]
        if step % 2:
            grown[1:, 1:] |= out[:-1, :-1]; grown[:-1, :-1] |= out[1:, 1:]
            grown[1:, :-1] |= out[:-1, 1:]; grown[:-1, 1:] |= out[1:, :-1]
        out = grown
    return out


def halve(mask):
    """Coverage (0..1) of a double-size boolean image at the final size."""
    h, w = mask.shape[0] // 2 * 2, mask.shape[1] // 2 * 2
    m = mask[:h, :w].astype(np.float32)
    return (m[0::2, 0::2] + m[1::2, 0::2] + m[0::2, 1::2] + m[1::2, 1::2]) / 4


def find_lines(part, depth, facing, inside, names, ink):
    """Three boolean line images at double size: outline, part boundaries, fine lines.

    Slender parts (aerials, wires, vent and pitot tubes) would turn into black bars if they were
    outlined like everything else, so a part whose picture is only a few pixels across is drawn
    with fine lines only. Which parts are slender is measured in the picture, not listed."""
    count = len(names) + 1
    quiet = np.zeros(count, dtype=bool)                               # parts that get no interior lines
    for number, name in enumerate(names, 1):
        quiet[number] = name.startswith(tuple(ink.get("no_lines", ())))
    crease_cos = math.cos(math.radians(ink.get("crease_deg", 50)))
    jump = ink.get("depth_jump_m", 0.03)

    def neighbours(axis):
        """For every pixel a and the next pixel b along the axis: a, b masks and part numbers."""
        valid = np.ones_like(inside)
        last = [slice(None), slice(None)]
        last[axis] = slice(-1, None)
        valid[tuple(last)] = False                                    # np.roll wraps: ignore the last row/column
        b_in = np.roll(inside, -1, axis=axis)
        b_part = np.roll(part, -1, axis=axis)
        return valid, b_in, b_part

    def back(mask, axis):                                             # the same flags placed on pixel b
        return np.roll(mask, 1, axis=axis)

    # ---- pass 1: how slender is each part? (pixels on its rim compared with its area)
    rim = np.zeros_like(inside)
    for axis in (0, 1):
        valid, b_in, b_part = neighbours(axis)
        edge = valid & ((inside != b_in) | (inside & b_in & (part != b_part)))
        rim |= edge & inside
        rim |= back(edge, axis) & inside
    area = np.bincount(part.ravel(), minlength=count)
    rim_count = np.bincount(part[rim], minlength=count)
    slender = area < ink.get("slender_ratio", 5.0) * np.maximum(rim_count, 1)
    slender[0] = False

    # ---- pass 2: classify every edge
    outline = np.zeros_like(inside)
    boundary = np.zeros_like(inside)
    fine = np.zeros_like(inside)
    for axis in (0, 1):
        valid, b_in, b_part = neighbours(axis)
        a_slender, b_slender = slender[part], slender[b_part]
        # the silhouette: inside next to outside
        a_edge = valid & inside & ~b_in
        b_edge = valid & b_in & ~inside
        outline |= a_edge & ~a_slender
        outline |= back(b_edge & ~b_slender, axis)
        fine |= a_edge & a_slender
        fine |= back(b_edge & b_slender, axis)
        # two different parts side by side
        both = valid & inside & b_in
        differ = both & (part != b_part) & ~(quiet[part] & quiet[b_part])
        sturdy = differ & ~a_slender & ~b_slender
        boundary |= sturdy
        boundary |= back(sturdy, axis)
        fine |= differ & a_slender
        fine |= back(differ & b_slender, axis)
        same = both & (part == b_part) & ~quiet[part] & ~a_slender        # slender parts get their rim only
        # a part hiding part of itself: a step in depth much larger than the slope on either side
        step = np.abs(np.roll(depth, -1, axis=axis) - depth)
        before = np.abs(depth - np.roll(depth, 1, axis=axis))
        after = np.abs(np.roll(depth, -2, axis=axis) - np.roll(depth, -1, axis=axis))
        hidden = same & (step > jump + 3.0 * np.maximum(before, after))
        # a fold: the surface direction turns sharply between neighbours
        turn = (facing * np.roll(facing, -1, axis=axis)).sum(axis=-1)
        fold = same & (turn < crease_cos) & ~hidden
        fine |= hidden | fold
    return outline, boundary, fine & ~boundary & ~outline


def draw_ink(part, depth, facing, inside, names, ink, width):
    """Ink coverage (0..1) at the final size. Widths are in pixels of a 2400-pixel-wide picture."""
    scale = width / 2400
    outline, boundary, fine = find_lines(part, depth, facing, inside, names, ink)

    def stroke(mask, px, found):
        # `found` is the width in which find_lines marks the line at double size: a boundary is
        # marked on both sides (2 pixels), the outline and the fine lines on one (1 pixel)
        target = 2 * px * scale
        return halve(grow(mask, max(0.0, (target - found) / 2)))

    outer = stroke(outline, ink.get("outer_px", 4.6), 1)
    middle = stroke(boundary, ink.get("part_px", 2.4), 2)
    thin = stroke(fine, ink.get("fine_px", 1.5), 1) * ink.get("fine_strength", 0.75)
    return 1 - (1 - outer) * (1 - middle) * (1 - thin)
