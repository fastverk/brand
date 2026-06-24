#!/usr/bin/env python3
"""Emit Icon Composer `.icon` bundles (Liquid Glass) from the mark layers.

A `.icon` is a bundle: `icon.json` (manifest) + `Assets/` (layer SVGs). The dark
bg becomes the canvas `fill`; tint/arrow/mark become foreground layers (which the
system renders with the Liquid Glass material). Open in Icon Composer to preview
the Default/Dark/Clear/Tinted appearances and export.

CLI: iconcomposer.py <out-dir>
"""
import json
import os
import sys
from gen_mark import Mark, VARIANTS

def _srgb(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return "srgb:%.4f,%.4f,%.4f,1.0" % (r, g, b)

def emit(out_dir, name, spec):
    icon = os.path.join(out_dir, "fastverk_%s.icon" % name)
    assets = os.path.join(icon, "Assets")
    os.makedirs(assets, exist_ok=True)
    m = Mark(spec)

    # Icon Composer orders layers FRONT-first (index 0 = top), so list the
    # mark first (over the arrow over the tint over the bg fill).
    layers = []
    for img, geom, color in [("mark.svg", m.mark(), spec.fg),
                             ("arrow.svg", m.arrow(), spec.accent),
                             ("tint.svg", m.tertiary_region(), spec.tertiary)]:
        if geom is None:
            continue
        m._layer(os.path.join(assets, img), geom, color)
        # glass = the Liquid Glass material (translucency + refraction) per layer.
        layers.append({"image-name": img, "name": img.rsplit(".", 1)[0], "glass": True})

    manifest = {
        "fill": {"solid": _srgb(spec.bg)},
        "groups": [{"layers": layers, "specular": True, "shadow": {"kind": "neutral"}}],
        "supported-platforms": {"circles": ["watchOS"], "squares": "shared"},
    }
    with open(os.path.join(icon, "icon.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("icon fastverk_%s.icon (%d layers)" % (name, len(layers)))

def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in VARIANTS.items():
        emit(out_dir, name, spec)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
