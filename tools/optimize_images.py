#!/usr/bin/env python3
"""Skapar optimerade WebP-versioner av bilderna i assets/img.

Kör från projektroten:  python3 tools/optimize_images.py
Varje källbild sparas som <namn>-<bredd>.webp i de bredder som anges nedan.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# källfil -> bredder (px)
JOBS = {
    "hem.jpg": [480, 800, 1200, 1400],
    "stor.jpg": [480, 800, 1200, 1400],
    "flytt.jpg": [480, 800, 1200, 1400],
    "kontor.jpg": [480, 800, 1200, 1400],
    "tradgard.jpg": [480, 800, 1200, 1400],
    "hero-fonster-poster.jpg": [480, 800, 1280],
    "hero-torka-poster.jpg": [1280],
    "logo.png": [300],
    "logo-light.png": [300],
    "guldsigill-2024.png": [440],
}


def main():
    for name, widths in JOBS.items():
        src = Image.open(IMG / name)
        stem = Path(name).stem
        for w in widths:
            im = src.copy()
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            out = IMG / f"{stem}-{w}.webp"
            lossless = im.mode == "RGBA"
            im.save(out, "WEBP", quality=74, method=6, lossless=False, alpha_quality=90) if lossless else im.convert("RGB").save(out, "WEBP", quality=72, method=6)
            print(out.relative_to(ROOT), im.size, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
