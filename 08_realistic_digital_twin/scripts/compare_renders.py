#!/usr/bin/env python3
"""Perceptual regression comparison for deterministic reference renders."""

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat


def prepared(path, size=(256, 144)):
    with Image.open(path) as image:
        image = image.convert("RGBA")
        background = Image.new("RGBA", image.size, "white")
        background.alpha_composite(image)
        return ImageOps.fit(background.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def score(reference, candidate):
    delta = ImageChops.difference(reference, candidate)
    stat = ImageStat.Stat(delta)
    mae = sum(stat.mean) / (3 * 255)
    rms = math.sqrt(sum(value * value for value in stat.rms) / 3) / 255
    ref_edges = reference.convert("L").filter(ImageFilter.FIND_EDGES)
    candidate_edges = candidate.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_mae = ImageStat.Stat(ImageChops.difference(ref_edges, candidate_edges)).mean[0] / 255
    return mae, rms, edge_mae, delta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("names", nargs="+")
    parser.add_argument("--max-mae", type=float, default=0.035)
    parser.add_argument("--max-rms", type=float, default=0.09)
    parser.add_argument("--max-edge-mae", type=float, default=0.05)
    parser.add_argument("--diff-dir", type=Path)
    args = parser.parse_args()
    failed = False
    if args.diff_dir:
        args.diff_dir.mkdir(parents=True, exist_ok=True)
    for name in args.names:
        reference_path = args.reference / name
        candidate_path = args.candidate / name
        if not reference_path.is_file() or not candidate_path.is_file():
            print(f"[{name}] MISSING reference or candidate")
            failed = True
            continue
        mae, rms, edge_mae, delta = score(prepared(reference_path), prepared(candidate_path))
        ok = mae <= args.max_mae and rms <= args.max_rms and edge_mae <= args.max_edge_mae
        print(f"[{name}] {'OK' if ok else 'DIFF'}: MAE={mae:.4f}, RMS={rms:.4f}, edge MAE={edge_mae:.4f}")
        failed = failed or not ok
        if args.diff_dir:
            delta.save(args.diff_dir / name)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
