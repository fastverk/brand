#!/usr/bin/env python3
"""Rasterize the mark — hermetic, via Pillow (no system rsvg/sips/iconutil).

Draws the shapely layer polygons directly (exterior filled, interior holes
punched) and composites bg / tint / arrow / mark, then writes per-size PNGs and
macOS .icns / Windows .ico / favicon from the same source.

CLI: `raster.py <out-dir>` emits the full icon set for every VARIANT.
"""
import os
import sys
from PIL import Image, ImageDraw
from gen_mark import Mark, Spec, VARIANTS

PNG_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 32, 48, 64, 128, 256]

def _polys(g):                                   # -> [(exterior_pts, [hole_pts, ...]), ...]
    if g is None:
        return []
    geoms = g.geoms if g.geom_type in ("MultiPolygon", "GeometryCollection") else [g]
    return [(list(p.exterior.coords), [list(r.coords) for r in p.interiors])
            for p in geoms if p.geom_type == "Polygon"]

def _mask(size, tf, polys):                      # L mask: exterior=255, holes=0
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    for ext, holes in polys:
        d.polygon([tf(x, y) for x, y in ext], fill=255)
        for h in holes:
            d.polygon([tf(x, y) for x, y in h], fill=0)
    return m

def raster(spec, size):
    s = Spec(**{**spec.__dict__, "canvas": size})
    m = Mark(s); tf = m._tf()
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(img)
    bd.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(s.bg_round * size), fill=s.bg)
    for g, color in [(m.tertiary_region(), s.tertiary), (m.arrow(), s.accent), (m.mark(), s.fg)]:
        if g is None:
            continue
        img.paste(color, (0, 0), _mask(size, tf, _polys(g)))
    return img

def emit_variant(out_dir, name, spec):
    imgs = {sz: raster(spec, sz) for sz in PNG_SIZES}
    for sz in PNG_SIZES:
        imgs[sz].save(os.path.join(out_dir, f"fastverk_{name}_{sz}.png"))
    imgs[1024].save(os.path.join(out_dir, f"fastverk_{name}.icns"), format="ICNS")
    imgs[256].save(os.path.join(out_dir, f"fastverk_{name}.ico"),
                   format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"icons fastverk_{name} -> {out_dir}")

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in VARIANTS.items():
        emit_variant(out_dir, name, spec)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
