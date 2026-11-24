#!/usr/bin/env python3
"""Draw every part of the model for the parts catalogue, and export each system for its 3D view.

    python3 09_book_figures/parts/render_all.py --out DIR [--jobs 3] [--blender PATH] [--only alone|place|models]

Writes DIR/alone/<name>.png (the part on its own, 1920x1200) with its <name>.json, DIR/place/<name>.png
(the part tinted inside the phantom aircraft, 1200x750) and DIR/models/<SYSTEM>.glb. A picture that is
already there is left alone, so a stopped run carries on where it ended. DIR is working material and is not
committed; build.py packs it into the catalogue. Blender is needed (`08_realistic_digital_twin/scripts/get_blender.sh`).
All 1,198 parts take about 14 hours on four cores: seven for the first set and seven for the second.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLEND = "08_realistic_digital_twin/models/C172N_realistic.blend"
TOOL = "09_book_figures/blender/part.py"
KINDS = {
    "alone": ["--size", "1920x1200", "--samples", "64"],
    "place": ["--context", "--frame", "aircraft", "--tint", "#D9774B", "--grow", "0.03", "--size", "1200x750", "--samples", "16"],
}


def name_of(part_id):
    return re.sub(r"[^A-Za-z0-9]", "_", part_id)


def blender(binary, *arguments):
    return subprocess.run([binary, "-b", BLEND, "--python", TOOL, "--", *arguments], cwd=ROOT, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--blender")
    parser.add_argument("--only", choices=("alone", "place", "models"))
    args = parser.parse_args()
    out = os.path.abspath(args.out)
    binary = args.blender or subprocess.check_output([os.path.join(ROOT, "08_realistic_digital_twin/scripts/get_blender.sh")], text=True).strip()
    with open(os.path.join(ROOT, "08_realistic_digital_twin/models/parts_all.json"), encoding="utf-8") as stream:
        parts = [part for part in json.load(stream)["parts"] if not part.get("group")]
    failed = []

    def draw(job):
        kind, part_id = job
        target = os.path.join(out, kind, name_of(part_id) + ".png")
        if os.path.exists(target) and os.path.getsize(target):
            return
        done = blender(binary, "render", "--part", part_id, "--name", name_of(part_id), *KINDS[kind], "--out", os.path.join(out, kind))
        if not (os.path.exists(target) and os.path.getsize(target)):
            failed.append((kind, part_id, done.stdout[-400:] + done.stderr[-400:]))

    jobs = [(kind, part["id"]) for kind in KINDS if args.only in (None, kind) for part in parts]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(draw, jobs))
    if args.only in (None, "models"):
        systems = collections.defaultdict(list)
        for part in parts:
            systems[part["system"]].append(part["id"])
        for system, ids in sorted(systems.items()):
            target = os.path.join(out, "models", system + ".glb")
            if not os.path.exists(target):
                done = blender(binary, "export", "--part", *ids, "--out", target)
                if not os.path.exists(target):
                    failed.append(("models", system, done.stdout[-400:] + done.stderr[-400:]))
    for kind, what, why in failed:
        print(f"FAILED {kind} {what}: {why}", file=sys.stderr)
    print(f"parts: {len(parts)} parts, {len(jobs)} pictures asked for, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
