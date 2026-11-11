"""The handbook's rules for its artwork files, as its build (tools/handbook/render.py of the book repository:
validate_figure and validate_plate) enforces them, so that what leaves this folder is known to pass them. Stdlib only.

    problems_of_svg(name, text) / problems_of_jpeg(name, data) -> a list of what is wrong (empty: fine)

If the book's rules change, change this file with them (the book repository's docs/handbook.md, section Figures)."""
import re

SVG_MAX_BYTES = 40_000
JPEG_MAX_BYTES = 800_000
JPEG_MAX_SIDE = 3200
SVG_TEXT = re.compile(r"^[0-9\s°%+\-−–.,:/()×≈<>=α-ω]*$")        # digits, symbols and Greek letters: no word of either edition


def problems_of_svg(name, text):
    where = f"figure {name}"
    errors = []
    if not re.match(r"^fig-\d{2}-\d{2}-[a-z0-9-]+\.svg$", name):
        errors.append(f"{where}: the name must look like fig-05-01-four-forces.svg")
    if len(text.encode("utf-8")) > SVG_MAX_BYTES:
        errors.append(f"{where}: larger than {SVG_MAX_BYTES} bytes")
    if not re.search(r'<svg\b[^>]*\bviewBox="[^"]+"', text):
        errors.append(f"{where}: the <svg> element needs a viewBox")
    if re.search(r"<\s*(script|style|foreignObject|image|iframe|a)\b|\sstyle\s*=|\son[a-z]+\s*=", text, re.I):
        errors.append(f"{where}: no script, style, foreignObject, image, links or event handlers")
    if re.search(r'(?:xlink:)?href\s*=\s*"(?!#)', text):
        errors.append(f"{where}: an href may only point inside the figure (#id)")
    for _attrs, content in re.findall(r"<(?:text|tspan)\b([^>]*)>([^<]*)<", text):
        if not SVG_TEXT.match(content):
            errors.append(f"{where}: the text {content.strip()!r} is not language-neutral")
    return errors


def problems_of_jpeg(name, data):
    """Container, size, dimensions, 8-bit RGB, and no private metadata: what the book checks of a colour plate."""
    where = f"plate {name}"
    errors = []
    if not re.fullmatch(r"plate-\d{2}-\d{2}-[a-z0-9-]+\.jpg", name):
        errors.append(f"{where}: the name must look like plate-07-01-control-surfaces.jpg")
    if len(data) > JPEG_MAX_BYTES:
        errors.append(f"{where}: larger than {JPEG_MAX_BYTES} bytes")
    if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        return errors + [f"{where}: needs a complete JPEG container"]
    pos, dimensions, scan = 2, None, False
    try:
        while pos < len(data) - 2:
            if data[pos] != 0xFF:
                raise ValueError("invalid JPEG segment")
            while data[pos] == 0xFF:
                pos += 1
            marker = data[pos]
            pos += 1
            size = int.from_bytes(data[pos:pos + 2], "big")
            if size < 2 or pos + size > len(data) - 2:
                raise ValueError("truncated JPEG segment")
            payload = data[pos + 2:pos + size]
            if marker in (0xE1, 0xED):
                errors.append(f"{where}: remove EXIF, XMP and IPTC metadata")
            if marker == 0xFE:
                errors.append(f"{where}: remove JPEG comments (the book's build adds its own marker to its copy)")
            if marker in (0xC0, 0xC2):
                if len(payload) < 6 or payload[0] != 8 or payload[5] != 3:
                    raise ValueError("use an 8-bit RGB JPEG")
                dimensions = int.from_bytes(payload[3:5], "big"), int.from_bytes(payload[1:3], "big")
            pos += size
            if marker == 0xDA:
                scan = True
                break
        if not dimensions or not scan:
            raise ValueError("missing JPEG frame or scan")
        if min(dimensions) < 1 or max(dimensions) > JPEG_MAX_SIDE:
            errors.append(f"{where}: the sides must be 1 to {JPEG_MAX_SIDE} pixels")
    except (IndexError, ValueError) as exc:
        errors.append(f"{where}: {exc}")
    return errors
