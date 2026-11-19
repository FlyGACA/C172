"""Rewrite the gradients of the book's vector figures so that they print the same in every PDF viewer.

A gradient given in bounding-box units (the SVG default) reaches the book's PDF (WeasyPrint) as a shading in a unit square under a large matrix. PDFium (Chrome) draws it;
Poppler (Evince, Okular, the CUPS filters) leaves many of those shapes unfilled: in Figure 19-8 the coloured lights went missing, in Figure 24-6 some of the numbered callouts.
A gradient given in the drawing's own coordinates is drawn by both. This tool gives every shape that uses a bounding-box gradient a gradient of its own in user space:
the same stops (by href to the original), the same vector worked out from the shape's bounding box, so the drawing looks the same on the web page.

    PLAYWRIGHT_MODULE=/opt/node-tools/node_modules/playwright/index.js python3 print_safe_gradients.py <book>/handbook/ppl/figures [name.svg ...]

The bounding boxes are measured in Chromium (getBBox), which also covers paths. Exact for every case found in the book: linear gradients, radial gradients on circles, and radial
gradients on other shapes (a circle in user space squeezed by a gradientTransform to the box's proportions). A gradient that already has a gradientTransform or an href is left
alone and reported. Safe to run again: a shape already on a user-space gradient is not touched. Keeps to the book's rules for an SVG (tools/handbook/render.py)."""
import json
import os
import re
import subprocess
import sys
import tempfile

JS = r"""
const m = await import(process.env.PLAYWRIGHT_MODULE); const chromium = m.chromium || m.default.chromium;
const b = await chromium.launch(); const p = await b.newPage();
const out = {};
for (const f of process.argv.slice(2)) {
  await p.goto('file://' + f);
  out[f] = await p.evaluate(() => {
    const rows = [];
    for (const el of document.querySelectorAll('svg *')) {
      for (const attr of ['fill', 'stroke']) {
        const v = el.getAttribute(attr); const mm = v && v.match(/^url\(#([^)]+)\)$/);
        if (!mm) continue;
        let box = null;
        try { const r = el.getBBox(); box = [r.x, r.y, r.width, r.height]; } catch (e) {}
        rows.push({ tag: el.tagName, attr, id: mm[1], box });
      }
    }
    return rows;
  });
}
console.log(JSON.stringify(out));
await b.close();
"""


def num(v, default):
    if v is None:
        return default
    v = v.strip()
    return float(v[:-1]) / 100 if v.endswith("%") else float(v)


def fmt(v):
    return f"{round(v, 2):g}"


def attr(tag, name):
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def convert(svg, uses):
    """uses: the shapes of this file that reference a paint server, in document order (from Chromium)."""
    grads = {}
    for m in re.finditer(r"<(linearGradient|radialGradient)\b([^>]*)>", svg):
        a = m.group(2)
        gid = attr(a, "id")
        if gid and "userSpaceOnUse" not in a:
            grads[gid] = (m.group(1), a)
    made, order, skipped, changed = {}, {}, [], 0
    it = iter(uses)

    def one(m):
        nonlocal changed
        tag = m.group(0)
        name = re.match(r"<(\w+)", tag).group(1)
        for which in ("fill", "stroke"):
            ref = re.search(rf'\s{which}="url\(#([^)]+)\)"', tag)
            if not ref:
                continue
            use = next(it)
            assert use["tag"] == name and use["attr"] == which and use["id"] == ref.group(1), (use, tag[:80])
            gid = ref.group(1)
            if gid not in grads:
                continue
            kind, a = grads[gid]
            box = use["box"]
            if "gradientTransform" in a or "href" in a or not box or box[2] <= 0 or box[3] <= 0:
                skipped.append((gid, name))
                continue
            bx, by, bw, bh = box
            if kind == "linearGradient":
                x1, y1, x2, y2 = num(attr(a, "x1"), 0), num(attr(a, "y1"), 0), num(attr(a, "x2"), 1), num(attr(a, "y2"), 0)
                if not (x1 == x2 or y1 == y2 or abs(bw - bh) < 0.01):
                    skipped.append((gid, name))                 # a slanted gradient on a box that is not square would change its look
                    continue
                geo = f'x1="{fmt(bx + x1 * bw)}" y1="{fmt(by + y1 * bh)}" x2="{fmt(bx + x2 * bw)}" y2="{fmt(by + y2 * bh)}"'
            else:
                cx, cy, r = num(attr(a, "cx"), 0.5), num(attr(a, "cy"), 0.5), num(attr(a, "r"), 0.5)
                fx, fy = num(attr(a, "fx"), cx), num(attr(a, "fy"), cy)
                k = bh / bw
                cyu = by + cy * bh
                geo = f'cx="{fmt(bx + cx * bw)}" cy="{fmt(cyu)}" r="{fmt(r * bw)}"'
                if attr(a, "fx") is not None or attr(a, "fy") is not None:
                    geo += f' fx="{fmt(bx + fx * bw)}" fy="{fmt(cyu + (fy - cy) * bw)}"'
                if abs(k - 1) > 0.002:                          # squeeze the circle about its centre line to the box's proportions
                    geo += f' gradientTransform="matrix(1 0 0 {round(k, 4):g} 0 {fmt(cyu * (1 - k))})"'
            key = (gid, geo)
            if key not in made:
                order[gid] = order.get(gid, 0) + 1
                made[key] = f"{gid}-u{order[gid]}"
            tag = tag.replace(f'{which}="url(#{gid})"', f'{which}="url(#{made[key]})"')
            changed += 1
        return tag

    body = re.sub(r"<(?!/|linearGradient|radialGradient|stop\b)\w+\b[^>]*>", one, svg)
    assert next(it, None) is None, "the file and the browser disagree on the shapes"
    if not changed:
        return svg, 0, skipped
    for gid, (kind, _) in grads.items():
        new = "".join(f'<{kind} id="{nid}" href="#{gid}" gradientUnits="userSpaceOnUse" {geo}/>' for (g, geo), nid in made.items() if g == gid)
        if new:
            close = f"</{kind}>"
            start = re.search(rf'<{kind}\b[^>]*\sid="{re.escape(gid)}"[^>]*>', body)
            end = body.index(close, start.end()) + len(close)
            body = body[:end] + new + body[end:]
    return body, changed, skipped


def main():
    folder = os.path.abspath(sys.argv[1])
    names = sys.argv[2:] or sorted(f for f in os.listdir(folder) if f.endswith(".svg"))
    paths = [os.path.join(folder, n) for n in names]
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as fh:
        fh.write(JS)
    try:
        found = json.loads(subprocess.run(["node", fh.name] + paths, check=True, capture_output=True, text=True).stdout)
    finally:
        os.unlink(fh.name)
    for name, path in zip(names, paths):
        svg = open(path, encoding="utf-8").read()
        out, changed, skipped = convert(svg, found[path])
        note = f"; left: {sorted(set(skipped))}" if skipped else ""
        if changed:
            assert len(out.encode()) < 40 * 1024, (name, len(out.encode()))
            open(path, "w", encoding="utf-8").write(out)
            print(f"{name}: {changed} shapes on user-space gradients, {len(out.encode())} bytes{note}")
        else:
            print(f"{name}: left as it is{note}")


main()
