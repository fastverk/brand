#!/usr/bin/env python3
"""Rasterize the fastverk mark — hermetic, via brando's marklib raster helpers.

Builds the mark Canvas per size and composites it with Pillow (Mask + vertical
gradient for the accent arrow). Emits per-size PNGs for both modes (dark =
mono-amber, light = amber-slate) plus .icns / .ico for the dark variants.

fastverk CONTENT: the per-mode palette + the size/format policy. The Pillow
plumbing (masks, gradients, compositing) lives in @brando//marklib:raster.

CLI: raster.py <out-dir>
"""
import dataclasses
import os
import sys

from PIL import Image

from gen_mark import Mark, Spec, VARIANTS, MODES
from marklib import raster as mraster

PNG_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 32, 48, 64, 128, 256]

def raster(spec, size):
    s = Spec(**{**spec.__dict__, "canvas": size})
    m = Mark(s); tf = m._tf()
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mraster.background_rect(img, size, s.bg, s.bg_round)
    if (tr := m.tertiary_region()) is not None:
        mraster.paste_geom(img, size, tf, tr, s.tertiary)
    if (ar := m.arrow()) is not None:
        if s.accent2:
            mraster.paste_geom(img, size, tf, ar, s.accent, s.accent2, gradient=True)
        else:
            mraster.paste_geom(img, size, tf, ar, s.accent)
    mraster.paste_geom(img, size, tf, m.mark(), s.fg)
    return img

def emit(out_dir, name, spec, packed=True):
    imgs = {sz: raster(spec, sz) for sz in PNG_SIZES}
    for sz in PNG_SIZES:
        imgs[sz].save(os.path.join(out_dir, f"fastverk_{name}_{sz}.png"))
    if packed:
        imgs[1024].save(os.path.join(out_dir, f"fastverk_{name}.icns"), format="ICNS")
        imgs[256].save(os.path.join(out_dir, f"fastverk_{name}.ico"),
                       format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"icons fastverk_{name}")

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for variant, base in VARIANTS.items():
        emit(out_dir, variant, base, packed=True)                              # dark (primary)
        emit(out_dir, "light_" + variant, dataclasses.replace(base, **MODES["light"]), packed=False)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
