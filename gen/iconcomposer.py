#!/usr/bin/env python3
"""Emit Icon Composer `.icon` bundles (Liquid Glass) from the mark layers.

Schema mirrors what Icon Composer writes on save: a background `fill` (solid or
automatic-gradient), a layer group carrying the glass material (specular +
shadow + translucency), and per-layer blend-mode / fill — the arrow gets a
vertical linear-gradient. Colors are `extended-srgb`. Open in Icon Composer
(macOS 26) to preview Default/Dark/Clear/Tinted and export.

CLI: iconcomposer.py <out-dir> [solid|auto]
"""
import json
import os
import sys
from gen_mark import Mark, VARIANTS

# Arrow linear-gradient stops (top -> bottom) + vertical axis (0..1).
ARROW_GRADIENT = ("#F2C46A", "#C9852B")  # mono-amber: bright top -> deep bottom (on-brand)
GRAD_AXIS = {"start": {"x": 0.5, "y": 0}, "stop": {"x": 0.5, "y": 0.7}}
# The Liquid Glass material (Icon Composer's group-level defaults).
GLASS = {
    "specular": True,
    "shadow": {"kind": "neutral", "opacity": 0.5},
    "translucency": {"enabled": True, "value": 0.5},
}

def _ext(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return "extended-srgb:%.5f,%.5f,%.5f,1.00000" % (r, g, b)

def _bg_fill(spec, mode):
    return {"automatic-gradient": _ext(spec.bg)} if mode == "auto" else {"solid": _ext(spec.bg)}

def emit(out_dir, name, spec, fill="auto", glass=True, arrow_gradient=ARROW_GRADIENT):
    icon = os.path.join(out_dir, "fastverk_%s.icon" % name)
    assets = os.path.join(icon, "Assets")
    os.makedirs(assets, exist_ok=True)
    m = Mark(spec)

    layers = []  # front -> back: mark, arrow, tint
    for img, geom, color, blend in [("mark.svg", m.mark(), spec.fg, "overlay"),
                                    ("arrow.svg", m.arrow(), spec.accent, "normal"),
                                    ("tint.svg", m.tertiary_region(), spec.tertiary, "normal")]:
        if geom is None:
            continue
        m._layer(os.path.join(assets, img), geom, color)
        layer = {"blend-mode": blend, "image-name": img, "name": img.rsplit(".", 1)[0]}
        if arrow_gradient and img == "arrow.svg":
            layer["fill"] = {
                "linear-gradient": [_ext(arrow_gradient[0]), _ext(arrow_gradient[1])],
                "orientation": GRAD_AXIS,
            }
        layers.append(layer)

    group = {"layers": layers}
    if glass:
        group.update(GLASS)
    manifest = {
        "fill": _bg_fill(spec, fill),
        "groups": [group],
        "supported-platforms": {"circles": ["watchOS"], "squares": "shared"},
    }
    with open(os.path.join(icon, "icon.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("icon fastverk_%s.icon" % name)

def main(out_dir, fill="auto"):
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in VARIANTS.items():
        emit(out_dir, name, spec, fill)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else "auto")
