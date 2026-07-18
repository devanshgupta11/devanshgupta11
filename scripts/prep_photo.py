#!/usr/bin/env python3
"""
Prep a source photo for the ASCII-art converter.

A flatly-lit face converts to a dark, unreadable blob if you skip this.
Three steps fix that:
  1. Remove the background with rembg so only the subject remains.
  2. Boost local contrast with OpenCV's CLAHE (contrast-limited adaptive
     histogram equalization) -- gives a flat face real highlights/shadows.
  3. Composite onto pure white so the background maps to the blank end
     of the ASCII ramp (white -> space character).

Output: source-prepped.png (grayscale). Run once per photo:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

try:
    from rembg import remove as rembg_remove
    HAVE_REMBG = True
except Exception:
    HAVE_REMBG = False


def remove_background(img: Image.Image) -> Image.Image:
    if not HAVE_REMBG:
        print("WARNING: rembg not available, skipping background removal.", file=sys.stderr)
        return img.convert("RGBA")
    return rembg_remove(img.convert("RGBA"))


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def composite_on_white(rgba: Image.Image) -> Image.Image:
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(white_bg, rgba)


def prep(src_path: Path, out_path: Path):
    img = Image.open(src_path)
    print(f"Loaded {src_path} ({img.size[0]}x{img.size[1]})")

    no_bg = remove_background(img)
    composited = composite_on_white(no_bg).convert("RGB")

    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    contrasted = apply_clahe(gray)

    Image.fromarray(contrasted).save(out_path)
    print(f"Wrote {out_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    if not src_path.exists():
        print(f"ERROR: {src_path} not found", file=sys.stderr)
        sys.exit(1)

    out_path = Path(__file__).resolve().parent.parent / "source-prepped.png"
    prep(src_path, out_path)


if __name__ == "__main__":
    main()
