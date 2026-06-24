#!/usr/bin/env python3
"""Rasterize the mark — hermetic, via Pillow (no system rsvg/sips/iconutil).

Draws the shapely layer polygons directly (exterior filled, holes punched),
composites bg / tint / arrow / mark, and renders the arrow as a vertical
gradient when the spec sets accent2. Emits per-size PNGs for both modes (dark =
mono-amber, light = amber-slate) plus .icns / .ico for the dark variants.

CLI: raster.py <out-dir>
"""
import dataclasses
import os
import sys
from PIL import Image, ImageColor, ImageDraw
from gen_mark import Mark, Spec, VARIANTS, MODES

PNG_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 32, 48, 64, 128, 256]

def _polys(g):                                   # -> [(exterior_pts, [hole_pts, ...]), ...]
    if g is None:
        return []
    geoms = g.geoms if g.geom_type in ("MultiPolygon", "GeometryCollection") else [g]
    return [(list(p.exterior.coords), [list(r.coords) for r in p.interiors])
            for p in geoms if p.geom_type == "Polygon"]

def _mask(size, tf, polys):                       # L mask: exterior=255, holes=0
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    for ext, holes in polys:
        d.polygon([tf(x, y) for x, y in ext], fill=255)
        for h in holes:
            d.polygon([tf(x, y) for x, y in h], fill=0)
    return m

def _vgrad(size, top, bot, y0, y1):               # vertical gradient image (top@y0 -> bot@y1 px)
    t, b = ImageColor.getrgb(top), ImageColor.getrgb(bot)
    span = max(1.0, y1 - y0)
    col = Image.new("RGBA", (1, size))
    for y in range(size):
        f = min(1.0, max(0.0, (y - y0) / span))
        col.putpixel((0, y), tuple(int(t[i] + (b[i] - t[i]) * f) for i in range(3)) + (255,))
    return col.resize((size, size))

def raster(spec, size):
    s = Spec(**{**spec.__dict__, "canvas": size})
    m = Mark(s); tf = m._tf()
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(s.bg_round * size), fill=s.bg)
    if (tr := m.tertiary_region()) is not None:
        img.paste(s.tertiary, (0, 0), _mask(size, tf, _polys(tr)))
    if (ar := m.arrow()) is not None:
        amask = _mask(size, tf, _polys(ar))
        if s.accent2:                             # vertical gradient over the arrow's bbox
            _, miny, _, maxy = ar.bounds
            img.paste(_vgrad(size, s.accent, s.accent2, tf(0, maxy)[1], tf(0, miny)[1]), (0, 0), amask)
        else:
            img.paste(s.accent, (0, 0), amask)
    img.paste(s.fg, (0, 0), _mask(size, tf, _polys(m.mark())))
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
