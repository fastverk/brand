#!/usr/bin/env python3
"""Emit fastverk Icon Composer `.icon` bundles (Liquid Glass) from the mark.

Builds each variant's marklib Canvas and emits it as an Icon Composer bundle via
@brando//marklib:iconcomposer — a background fill, the Liquid Glass material on
the layer group, and per-layer blend-mode / fill (the arrow gets a vertical
linear-gradient). Open in Icon Composer (macOS 26) to preview/export.

fastverk CONTENT: which layers/blend-modes/gradient; the bundle schema + writer
is brando's.

CLI: iconcomposer.py <out-dir> [solid|auto]
"""
import os
import sys

from gen_mark import Mark, VARIANTS
from marklib import iconcomposer as ic

# Arrow gets the mono-amber gradient + an "overlay" mark blend (on-brand).
ARROW_GRADIENT = ("#F2C46A", "#C9852B")
BLEND_MODES = {"mark": "overlay", "arrow": "normal", "tint": "normal"}

def emit(out_dir, name, spec, fill="auto"):
    m = Mark(spec)
    canvas = m.canvas()
    # Override the arrow layer's gradient to the canonical Icon Composer stops.
    for layer in canvas.layers:
        if layer.name == "arrow":
            layer.gradient = ARROW_GRADIENT
    ic.emit_icon_bundle(out_dir, "fastverk_%s" % name, canvas,
                        fill=fill, glass=True, blend_modes=BLEND_MODES)

def main(out_dir, fill="auto"):
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in VARIANTS.items():
        emit(out_dir, name, spec, fill)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else "auto")
