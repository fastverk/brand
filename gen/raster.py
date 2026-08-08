#!/usr/bin/env python3
"""Rasterize the fastverk mark — hermetic, via brando's marklib raster helpers.

Builds the mark Canvas per size and composites it with Pillow (Mask + vertical
gradient for the accent arrow). Emits per-size PNGs for both modes (dark =
mono-amber, light = amber-slate) plus .icns / .ico for the dark variants.

fastverk CONTENT: the per-mode palette + the size/format policy. The Pillow
plumbing (masks, gradients, compositing) lives in @brando//marklib:raster.

CLI: raster.py <out-dir> [--prefix P] [--palette NAME] [--variant V]...
(the same flags //gen:gen_mark takes, so a property's SVG set and its raster set
cannot drift apart in prefix or palette).
"""
import os
import sys

from PIL import Image

from gen_mark import Mark, Spec, VARIANTS, MODES, parse_args, spec_for
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

def emit(out_dir, name, spec, packed=True, prefix="fastverk"):
    imgs = {sz: raster(spec, sz) for sz in PNG_SIZES}
    for sz in PNG_SIZES:
        imgs[sz].save(os.path.join(out_dir, f"{prefix}_{name}_{sz}.png"))
    if packed:
        imgs[1024].save(os.path.join(out_dir, f"{prefix}_{name}.icns"), format="ICNS")
        imgs[256].save(os.path.join(out_dir, f"{prefix}_{name}.ico"),
                       format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"icons {prefix}_{name}")

def main(argv=None):
    a = parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    for variant in a.variants:
        # dark (primary) + light, both in the requested palette.
        emit(a.out_dir, variant, spec_for(variant, a.palette, "dark"),
             packed=True, prefix=a.prefix)
        emit(a.out_dir, "light_" + variant, spec_for(variant, a.palette, "light"),
             packed=False, prefix=a.prefix)

if __name__ == "__main__":
    main()
