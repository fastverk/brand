#!/usr/bin/env python3
"""Brandbook guideline diagrams: construction grid, optical center, clear space.

Generated hermetically (Pillow) from the same geometry as the mark.
CLI: diagrams.py <out-dir>
"""
import dataclasses
import math
import os
import sys
from PIL import Image, ImageDraw
from gen_mark import Mark, Spec, spec_for
from raster import raster

R3 = math.sqrt(3)
# ⚠ AMBER WAS #E0A33E — a fifth place the accent was written down, and one that
# already disagreed with the skin before the palette moved. Take it from the
# canonical Spec so the guideline figures cannot annotate the mark in a colour
# the mark is not drawn in.
INK, SLATE = "#15161A", "#4A565A"
AMBER = spec_for("full").accent
AMBER_RGB = tuple(int(AMBER[i:i + 2], 16) for i in (1, 3, 5))
PAPER = "#F4F1EA"
GUIDE = "#CFC8B8"

def _ring(d, tf, poly, color, w):
    d.line([tf(x, y) for x, y in poly.exterior.coords], fill=color, width=w, joint="curve")

def construction(path, S=900):
    """Unit circle + outer/inner triangles + vertices."""
    m = Mark(Spec(center_y=0.0, canvas=S))
    tf = m._tf(); scale = 0.66 * S / R3
    img = Image.new("RGB", (S, S), PAPER); d = ImageDraw.Draw(img)
    cx, cyp = tf(0, 0)
    d.line([(cx, 30), (cx, S - 30)], fill=GUIDE, width=1)
    d.line([(30, cyp), (S - 30, cyp)], fill=GUIDE, width=1)
    r = scale
    d.ellipse([cx - r, cyp - r, cx + r, cyp + r], outline="#B9B2A3", width=3)  # unit circle
    _ring(d, tf, m.t_out, INK, 4)                                              # outer triangle
    _ring(d, tf, m.t_in, AMBER, 4)                                            # inner (xphi)
    for x, y in [(R3/2, 0.5), (-R3/2, 0.5), (0, -1)]:
        px, py = tf(x, y); d.ellipse([px-7, py-7, px+7, py+7], fill=INK)
    d.ellipse([cx-7, cyp-7, cx+7, cyp+7], fill=AMBER)                          # circle center
    img.save(path)

def grid(path, S=900):
    """The icon with the optical-center crosshair."""
    base = Image.new("RGBA", (S, S), PAPER)
    base.alpha_composite(raster(dataclasses.replace(spec_for("full"), canvas=S), S))
    d = ImageDraw.Draw(base)
    d.line([(0, S//2), (S, S//2)], fill=AMBER_RGB + (230,), width=3)
    d.line([(S//2, 0), (S//2, S)], fill=AMBER_RGB + (140,), width=2)
    base.convert("RGB").save(path)

def clearspace(path, S=900):
    """The icon with a dashed clear-space frame (clearance = corner radius)."""
    iconsz = int(S * 0.58)
    off = (S - iconsz) // 2
    clr = int(iconsz * 0.20)                                                   # = corner radius
    img = Image.new("RGBA", (S, S), PAPER)
    img.alpha_composite(raster(dataclasses.replace(spec_for("full"), canvas=iconsz), iconsz), (off, off))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = off - clr, off - clr, off + iconsz + clr, off + iconsz + clr
    dash = 14
    for x in range(x0, x1, dash * 2):                                          # dashed frame
        d.line([(x, y0), (min(x + dash, x1), y0)], fill=SLATE, width=3)
        d.line([(x, y1), (min(x + dash, x1), y1)], fill=SLATE, width=3)
    for y in range(y0, y1, dash * 2):
        d.line([(x0, y), (x0, min(y + dash, y1))], fill=SLATE, width=3)
        d.line([(x1, y), (x1, min(y + dash, y1))], fill=SLATE, width=3)
    d.rectangle([off - clr, off - clr, off, off], outline=AMBER, width=3)      # clearance unit
    img.convert("RGB").save(path)

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    construction(os.path.join(out_dir, "construction.png"))
    grid(os.path.join(out_dir, "grid.png"))
    clearspace(os.path.join(out_dir, "clearspace.png"))
    print("diagrams: construction, grid, clearspace")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
